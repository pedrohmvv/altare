import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, mockApi, problemResponse } from '@/test/fake-api'
import { EVAL, MAP } from '@/test/scope-fixtures'
import type { PlanningSearch } from '../search'
import { ScopeMap } from './scope-map'

const GET = 'GET /api/v1/wedding/scope'
const FOTO = 'c-foto'
const VIDEO = 'c-video'
const BUFFET = 'c-buffet'
const PUT_STATUS = (id: string) => `PUT /api/v1/wedding/scope/categories/${id}/status`
const PUT_EVAL = (id: string) => `PUT /api/v1/wedding/scope/categories/${id}/my-evaluation`
const HISTORY = (id: string) => `GET /api/v1/wedding/scope/categories/${id}/history`

function Harness({
  initial,
  profile = 'Noivo',
}: {
  initial: PlanningSearch
  profile?: 'Noivo' | 'Noiva'
}) {
  const [search, setSearch] = useState<PlanningSearch>(initial)
  return (
    <ScopeMap
      search={search}
      profile={profile}
      onSearchChange={(patch) =>
        setSearch((prev) => {
          const next: Record<string, unknown> = { ...prev, ...patch }
          for (const key of Object.keys(next)) if (next[key] === undefined) delete next[key]
          return next as PlanningSearch
        })
      }
    />
  )
}

function withCategory(id: string, change: Record<string, unknown>) {
  return {
    ...MAP,
    groups: MAP.groups.map((g) => ({
      ...g,
      categories: g.categories.map((c) => (c.id === id ? { ...c, ...change } : c)),
    })),
  }
}

function renderSheet(
  handlers: Parameters<typeof mockApi>[0] = {},
  initial: PlanningSearch = { categoria: FOTO },
  profile: 'Noivo' | 'Noiva' = 'Noivo',
) {
  const api = mockApi({
    [GET]: jsonResponse(200, MAP),
    [HISTORY(FOTO)]: jsonResponse(200, []),
    ...handlers,
  })
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <Harness initial={initial} profile={profile} />
    </QueryClientProvider>,
  )
  return { api, user: userEvent.setup() }
}

const painel = () => screen.findByRole('dialog', { name: 'Fotografia Exemplo' })

describe('Painel da categoria: abrir e fechar', () => {
  it('clicar no nome abre o painel e põe a categoria na URL; o Esc tira', async () => {
    const { user } = renderSheet({}, {})
    await user.click(await screen.findByRole('button', { name: 'Fotografia Exemplo' }))
    const aberto = await painel()
    expect(aberto).toHaveAccessibleDescription(/Grupo Exemplo A/)
    await user.keyboard('{Escape}')
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('abre direto quando a URL já traz a categoria, e some se o id não existe mais', async () => {
    renderSheet()
    expect(await painel()).toBeVisible()
  })

  it('id de categoria desconhecido na URL não abre nada e não quebra a página', async () => {
    renderSheet({}, { categoria: '0190a1b2-c3d4-7e5f-8a9b-0c1d2e3f4a5b' })
    expect(await screen.findByRole('heading', { name: 'Grupo Exemplo A' })).toBeVisible()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })
})

describe('Painel da categoria: status (F-PLN-03)', () => {
  it('mudar para Entra ou Talvez envia na hora, com a versão que a tela mostra', async () => {
    const { api, user } = renderSheet(
      {
        [PUT_STATUS(VIDEO)]: jsonResponse(
          200,
          withCategory(VIDEO, { status: 'Talvez (Se couber)', version: 2 }),
        ),
      },
      { categoria: VIDEO },
    )
    const dialog = await screen.findByRole('dialog', { name: 'Vídeo Exemplo' })
    await user.click(within(dialog).getByRole('combobox', { name: 'Status' }))
    await user.click(screen.getByRole('option', { name: 'Talvez (Se couber)' }))

    await waitFor(() => expect(api.callsTo(PUT_STATUS(VIDEO))).toHaveLength(1))
    expect(api.callsTo(PUT_STATUS(VIDEO))[0]?.body).toEqual({
      status: 'Talvez (Se couber)',
      reason: null,
      version: 1,
    })
    await waitFor(() =>
      expect(within(dialog).getByRole('combobox', { name: 'Status' })).toHaveTextContent(
        'Talvez (Se couber)',
      ),
    )
  })

  it('Fica de fora pede o motivo antes de enviar e bloqueia sem ele', async () => {
    const { api, user } = renderSheet({
      [PUT_STATUS(FOTO)]: jsonResponse(
        200,
        withCategory(FOTO, { status: 'Fica de fora', discard_reason: 'fora do teto', version: 2 }),
      ),
    })
    const dialog = await painel()
    await user.click(within(dialog).getByRole('combobox', { name: 'Status' }))
    await user.click(screen.getByRole('option', { name: 'Fica de fora' }))

    expect(api.callsTo(PUT_STATUS(FOTO))).toHaveLength(0)
    await user.click(within(dialog).getByRole('button', { name: 'Confirmar: fica de fora' }))
    expect(
      await within(dialog).findByText('Escrevam por que esta frente fica de fora.'),
    ).toBeVisible()
    expect(api.callsTo(PUT_STATUS(FOTO))).toHaveLength(0)

    await user.type(
      within(dialog).getByRole('textbox', { name: /Por que fica de fora/ }),
      ' fora do teto ',
    )
    await user.click(within(dialog).getByRole('button', { name: 'Confirmar: fica de fora' }))
    await waitFor(() => expect(api.callsTo(PUT_STATUS(FOTO))).toHaveLength(1))
    expect(api.callsTo(PUT_STATUS(FOTO))[0]?.body).toEqual({
      status: 'Fica de fora',
      reason: 'fora do teto',
      version: 1,
    })
  })

  it('uma categoria reaberta mostra o motivo do descarte anterior', async () => {
    renderSheet({
      [GET]: jsonResponse(
        200,
        withCategory(FOTO, { status: 'Em discussão', discard_reason: 'fora do teto' }),
      ),
    })
    const dialog = await painel()
    expect(within(dialog).getByText('Motivo do descarte anterior: fora do teto')).toBeVisible()
  })

  it('conflito de versão avisa, recarrega o mapa e não sobrescreve', async () => {
    let leituras = 0
    const { api, user } = renderSheet({
      [GET]: () => {
        leituras += 1
        return jsonResponse(
          200,
          leituras === 1 ? MAP : withCategory(FOTO, { status: 'Talvez (Se couber)', version: 2 }),
        )
      },
      [PUT_STATUS(FOTO)]: problemResponse(409, 'version_conflict'),
    })
    const dialog = await painel()
    await user.click(within(dialog).getByRole('combobox', { name: 'Status' }))
    await user.click(screen.getByRole('option', { name: 'Talvez (Se couber)' }))
    expect(await within(dialog).findByText(/Outra pessoa alterou esta frente/)).toBeVisible()
    await waitFor(() => expect(leituras).toBeGreaterThan(1))
    expect(api.callsTo(PUT_STATUS(FOTO))).toHaveLength(1)
  })
})

describe('Painel da categoria: avaliação (F-PLN-04 e F-PLN-05)', () => {
  it('o Noivo salva a própria prioridade e nota com a versão da avaliação dele', async () => {
    const { api, user } = renderSheet(
      {
        [PUT_EVAL(VIDEO)]: jsonResponse(200, MAP),
      },
      { categoria: VIDEO },
    )
    const dialog = await screen.findByRole('dialog', { name: 'Vídeo Exemplo' })
    await user.click(within(dialog).getByRole('button', { name: 'Dispenso' }))
    await user.type(within(dialog).getByRole('textbox', { name: 'Minha nota' }), 'só se sobrar')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar minha avaliação' }))

    await waitFor(() => expect(api.callsTo(PUT_EVAL(VIDEO))).toHaveLength(1))
    expect(api.callsTo(PUT_EVAL(VIDEO))[0]?.body).toEqual({
      priority: 'Dispenso',
      note: 'só se sobrar',
      version: 1,
    })
  })

  it('a prioridade pode ser desmarcada (volta a sem avaliação)', async () => {
    const { api, user } = renderSheet(
      { [PUT_EVAL(VIDEO)]: jsonResponse(200, MAP) },
      { categoria: VIDEO },
    )
    const dialog = await screen.findByRole('dialog', { name: 'Vídeo Exemplo' })
    const atual = within(dialog).getByRole('button', { name: 'Se couber' })
    expect(atual).toHaveAttribute('aria-pressed', 'true')
    await user.click(atual)
    await user.click(within(dialog).getByRole('button', { name: 'Salvar minha avaliação' }))
    await waitFor(() => expect(api.callsTo(PUT_EVAL(VIDEO))).toHaveLength(1))
    expect(api.callsTo(PUT_EVAL(VIDEO))[0]?.body).toMatchObject({ priority: null })
  })

  it('a Noiva edita só a dela; a do Noivo aparece em leitura, sem campo', async () => {
    const { user } = renderSheet({}, { categoria: FOTO }, 'Noiva')
    const dialog = await painel()
    const doOutro = within(dialog).getByRole('region', { name: 'Avaliação do Noivo' })
    expect(within(doOutro).getByText('Quero muito')).toBeVisible()
    expect(within(doOutro).queryByRole('textbox')).not.toBeInTheDocument()
    expect(within(doOutro).queryByRole('button')).not.toBeInTheDocument()
    expect(within(dialog).getByRole('button', { name: 'Dispenso' })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
    expect(user).toBeDefined()
  })

  it('quando o outro ainda não avaliou, diz em texto', async () => {
    renderSheet({}, { categoria: VIDEO }, 'Noivo')
    const dialog = await screen.findByRole('dialog', { name: 'Vídeo Exemplo' })
    const doOutro = within(dialog).getByRole('region', { name: 'Avaliação da Noiva' })
    expect(within(doOutro).getByText('Ainda não avaliou')).toBeVisible()
  })

  it('divergência é um convite a conversar, em texto', async () => {
    renderSheet()
    const dialog = await painel()
    expect(
      within(dialog).getByText(
        'Vocês avaliaram esta frente de forma diferente. Vale conversar antes de decidir.',
      ),
    ).toBeVisible()
  })

  it('conflito na avaliação avisa e oferece a versão mais recente, sem perder o que foi digitado antes de pedir', async () => {
    let leituras = 0
    const nova = withCategory(VIDEO, {
      noivo: { priority: 'Quero muito', note: 'do outro lado', version: 2 },
    })
    const { user } = renderSheet(
      {
        [GET]: () => {
          leituras += 1
          return jsonResponse(200, leituras === 1 ? MAP : nova)
        },
        [PUT_EVAL(VIDEO)]: problemResponse(409, 'version_conflict'),
      },
      { categoria: VIDEO },
    )
    const dialog = await screen.findByRole('dialog', { name: 'Vídeo Exemplo' })
    await user.type(within(dialog).getByRole('textbox', { name: 'Minha nota' }), 'minha edição')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar minha avaliação' }))
    expect(await within(dialog).findByText(/Outra pessoa alterou esta avaliação/)).toBeVisible()
    expect(within(dialog).getByRole('textbox', { name: 'Minha nota' })).toHaveValue('minha edição')

    await user.click(
      await within(dialog).findByRole('button', { name: 'Ver a versão mais recente' }),
    )
    expect(await within(dialog).findByRole('textbox', { name: 'Minha nota' })).toHaveValue(
      'do outro lado',
    )
  })
})

describe('Painel da categoria: histórico', () => {
  it('lista quem mudou o quê e quando, do mais recente ao mais antigo', async () => {
    renderSheet(
      {
        [HISTORY(BUFFET)]: jsonResponse(200, [
          {
            id: 'h2',
            from_status: 'Fica de fora',
            to_status: 'Em discussão',
            reason: null,
            by: 'Noivo',
            at: '2026-10-28T15:30:00Z',
          },
          {
            id: 'h1',
            from_status: 'Em discussão',
            to_status: 'Fica de fora',
            reason: 'fora do teto',
            by: 'Noiva',
            at: '2026-10-27T12:00:00Z',
          },
        ]),
      },
      { categoria: BUFFET },
    )
    const dialog = await screen.findByRole('dialog', { name: 'Buffet Exemplo' })
    const itens = await within(dialog).findAllByRole('listitem')
    expect(itens[0]).toHaveTextContent('Noivo')
    expect(itens[0]).toHaveTextContent('28 out 2026, 12:30')
    expect(itens[0]).toHaveTextContent('Fica de fora → Em discussão')
    expect(itens[1]).toHaveTextContent('Noiva')
    expect(itens[1]).toHaveTextContent('fora do teto')
  })

  it('sem mudanças, diz com calma', async () => {
    renderSheet()
    const dialog = await painel()
    expect(await within(dialog).findByText('Nenhuma mudança de status ainda.')).toBeVisible()
    expect(EVAL).toBeDefined()
  })
})
