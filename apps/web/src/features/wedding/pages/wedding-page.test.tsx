import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { jsonResponse, mockApi, problemResponse } from '@/test/fake-api'
import type { Baseline, BaselineChange } from '../api/baseline'
import type { DateImpact } from '../api/use-date-impact'
import { WeddingPage, type WeddingPageProps } from './wedding-page'

const GET = 'GET /api/v1/wedding/baseline'
const PUT_CITY = 'PUT /api/v1/wedding/baseline/city'
const PUT_DATE = 'PUT /api/v1/wedding/baseline/date'
const PUT_CEILING = 'PUT /api/v1/wedding/baseline/ceiling'
const CHANGES = 'GET /api/v1/wedding/baseline/changes'
const PREVIEW = 'GET /api/v1/schedule/date-preview'
const SCHEDULE = 'GET /api/v1/schedule'

function emptyBaseline(): Baseline {
  return {
    date: { status: 'Em definição', note: null, version: 1, value: { kind: 'nenhuma' } },
    city: { status: 'Em definição', note: null, version: 1, value: null },
    format: { status: 'Em definição', note: null, version: 1, value: null },
    size: {
      status: 'Em definição',
      note: null,
      version: 1,
      value: { minimum: null, maximum: null },
      guest_count: 0,
    },
    ceiling: { status: 'Em definição', note: null, version: 1, value: { cents: null } },
    ceremony: {
      status: 'Em definição',
      note: null,
      version: 1,
      value: { kinds: [], detail: null },
    },
  }
}

function renderPage(
  handlers: Parameters<typeof mockApi>[0] = {},
  props: Partial<WeddingPageProps> = {},
) {
  const api = mockApi({ [GET]: jsonResponse(200, emptyBaseline()), ...handlers })
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <WeddingPage search={{}} onSearchChange={() => {}} profile="Noivo" {...props} />
    </QueryClientProvider>,
  )
  return { api, user: userEvent.setup() }
}

const row = (name: RegExp | string) => screen.findByRole('button', { name })
const dialog = () => screen.findByRole('dialog')

describe('Definições Base: o Porte e a contagem da lista (F-PLN-01, D-073)', () => {
  const withGuests = (count: number) => {
    const baseline = emptyBaseline()
    return { ...baseline, size: { ...baseline.size, guest_count: count } }
  }

  it('mostra, ao lado do Porte, quantas pessoas a lista tem agora', async () => {
    renderPage({ [GET]: jsonResponse(200, withGuests(142)) })

    const porte = await row(/Porte/)

    expect(within(porte).getByText('Na lista agora: 142 pessoas')).toBeVisible()
    // O valor do Porte continua sendo o que o casal definiu: a contagem é só ao lado.
    expect(within(porte).getByText('Ainda sem valor')).toBeVisible()
  })

  it('com uma pessoa, usa o singular', async () => {
    renderPage({ [GET]: jsonResponse(200, withGuests(1)) })

    expect(within(await row(/Porte/)).getByText('Na lista agora: 1 pessoa')).toBeVisible()
  })

  it('sem ninguém na lista, não diz nada', async () => {
    renderPage({ [GET]: jsonResponse(200, withGuests(0)) })

    expect(within(await row(/Porte/)).queryByText(/Na lista agora/)).not.toBeInTheDocument()
  })

  it('só o Porte mostra a contagem', async () => {
    renderPage({ [GET]: jsonResponse(200, withGuests(142)) })
    await row(/Porte/)

    expect(screen.getAllByText(/Na lista agora/)).toHaveLength(1)
  })
})

describe('Definições Base: o painel (F-PLN-01)', () => {
  it('traz o título da área como o único h1 e o painel com as seis definições', async () => {
    renderPage()
    expect(screen.getByRole('heading', { level: 1, name: 'O rumo de vocês' })).toBeVisible()
    expect(await screen.findByRole('heading', { level: 2, name: 'Definições base' })).toBeVisible()
    for (const label of [
      'Data ou época',
      'Cidade ou região',
      'Formato',
      'Porte',
      'Teto macro',
      'Tipo de cerimônia',
    ]) {
      expect(await row(new RegExp(label))).toBeVisible()
    }
  })

  it('num casamento novo todas aparecem vazias e Em definição, sem dado inventado', async () => {
    renderPage()
    await row(/Cidade ou região/)
    expect(screen.getAllByText('Em definição')).toHaveLength(6)
    expect(screen.queryByText('Definido')).not.toBeInTheDocument()
    expect(screen.getAllByText('Ainda sem valor')).toHaveLength(6)
  })

  it('enquanto carrega, avisa em texto; falhando, oferece tentar de novo e refaz o pedido', async () => {
    let attempts = 0
    const { user } = renderPage({
      [GET]: () => {
        attempts += 1
        return attempts === 1
          ? problemResponse(500, 'internal_error')
          : jsonResponse(200, emptyBaseline())
      },
    })
    expect(screen.getByText('Carregando as definições')).toBeInTheDocument()
    expect(await screen.findByText('Não conseguimos carregar as definições')).toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Tentar de novo' }))
    expect(await row(/Cidade ou região/)).toBeVisible()
    expect(attempts).toBe(2)
  })

  it('mostra o valor guardado e o selo Definido, com o texto completo', async () => {
    const baseline = emptyBaseline()
    baseline.city = { status: 'Definido', note: null, version: 2, value: 'Cidade Exemplo' }
    baseline.ceiling = { status: 'Definido', note: null, version: 2, value: { cents: 2_800_000 } }
    renderPage({ [GET]: jsonResponse(200, baseline) })
    const cidade = await row(/Cidade ou região/)
    expect(within(cidade).getByText('Cidade Exemplo')).toBeVisible()
    expect(within(cidade).getByText('Definido')).toBeVisible()
    expect(within(await row(/Teto macro/)).getByText(/R\$\s28\.000/)).toBeVisible()
  })
})

describe('Definições Base: editar uma definição', () => {
  it('abre o diálogo da definição e o Cancelar fecha devolvendo o foco à linha', async () => {
    const { user } = renderPage()
    const linha = await row(/Cidade ou região/)
    await user.click(linha)
    expect(await dialog()).toHaveAccessibleName('Cidade ou região')
    await user.click(screen.getByRole('button', { name: 'Cancelar' }))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(linha).toHaveFocus()
  })

  it('define a cidade: envia valor, situação e a versão vista, e o painel mostra o resultado', async () => {
    const saved = emptyBaseline()
    saved.city = {
      status: 'Definido',
      note: 'decidimos juntos',
      version: 2,
      value: 'Cidade Exemplo',
    }
    const { api, user } = renderPage({ [PUT_CITY]: jsonResponse(200, saved) })
    await user.click(await row(/Cidade ou região/))
    await user.type(
      await screen.findByRole('textbox', { name: 'Cidade ou região' }),
      'Cidade Exemplo',
    )
    await user.click(screen.getByRole('radio', { name: 'Definido' }))
    await user.type(
      screen.getByRole('textbox', { name: /Por que estamos em dúvida/ }),
      'decidimos juntos',
    )
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(api.callsTo(PUT_CITY)[0]?.body).toEqual({
      status: 'Definido',
      note: 'decidimos juntos',
      version: 1,
      value: 'Cidade Exemplo',
    })
    expect(api.callsTo(PUT_CITY)[0]?.request.headers.get('X-Altare-CSRF')).toBe('1')
    expect(within(await row(/Cidade ou região/)).getByText('Definido')).toBeVisible()
  })

  it('marcar Definido sem valor é bloqueado, com mensagem acionável e foco no campo', async () => {
    const { api, user } = renderPage()
    await user.click(await row(/Cidade ou região/))
    await screen.findByRole('dialog')
    await user.click(screen.getByRole('radio', { name: 'Definido' }))
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    const campo = screen.getByRole('textbox', { name: 'Cidade ou região' })
    expect(await screen.findByText(/Preencham o valor antes de marcar como Definido/)).toBeVisible()
    expect(campo).toHaveAttribute('aria-invalid', 'true')
    expect(campo).toHaveFocus()
    expect(api.callsTo(PUT_CITY)).toHaveLength(0)
  })

  it('o teto aceita R$ 28.000,00 e vai como 2800000 centavos', async () => {
    const { api, user } = renderPage({ [PUT_CEILING]: jsonResponse(200, emptyBaseline()) })
    await user.click(await row(/Teto macro/))
    await user.type(await screen.findByRole('textbox', { name: 'Teto macro' }), '28.000,00')
    await user.click(screen.getByRole('radio', { name: 'Definido' }))
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    await waitFor(() => expect(api.callsTo(PUT_CEILING)).toHaveLength(1))
    expect(api.callsTo(PUT_CEILING)[0]?.body).toMatchObject({ value: { cents: 2_800_000 } })
  })

  it('a data exata vai como exata; sem data envia nenhuma', async () => {
    const { api, user } = renderPage({ [PUT_DATE]: jsonResponse(200, emptyBaseline()) })
    await user.click(await row(/Data ou época/))
    await screen.findByRole('dialog')
    await user.click(screen.getByRole('radio', { name: 'Data exata' }))
    fireEvent.change(screen.getByLabelText('Data'), { target: { value: '2027-05-01' } })
    await user.click(screen.getByRole('radio', { name: 'Definido' }))
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))
    await waitFor(() => expect(api.callsTo(PUT_DATE)).toHaveLength(1))
    expect(api.callsTo(PUT_DATE)[0]?.body).toMatchObject({
      status: 'Definido',
      value: { kind: 'exata', exact: '2027-05-01' },
    })
  })

  it('janela com o fim antes do início é recusada no campo do fim', async () => {
    const { api, user } = renderPage()
    await user.click(await row(/Data ou época/))
    await screen.findByRole('dialog')
    await user.click(screen.getByRole('radio', { name: 'Janela' }))
    await user.click(screen.getByRole('combobox', { name: 'Mês do início' }))
    await user.click(screen.getByRole('option', { name: 'junho' }))
    await user.type(screen.getByRole('textbox', { name: 'Ano do início' }), '2027')
    await user.click(screen.getByRole('combobox', { name: 'Mês do fim' }))
    await user.click(screen.getByRole('option', { name: 'março' }))
    await user.type(screen.getByRole('textbox', { name: 'Ano do fim' }), '2027')
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    expect(await screen.findByText('O fim não pode ser antes do início.')).toBeVisible()
    expect(api.callsTo(PUT_DATE)).toHaveLength(0)
  })
})

/** A prévia do cronograma como a API a devolve: sem mudança, para os testes que não a olham. */
function preview(over: Partial<DateImpact> = {}): DateImpact {
  return {
    mode_before: 'com_data',
    mode_after: 'com_data',
    changes: [],
    manual_kept: 0,
    newly_overdue: 0,
    ...over,
  }
}

const aChange = (n: number, title = `Marco Exemplo ${n}`): DateImpact['changes'][number] => ({
  id: `00000000-0000-4000-8000-00000000000${n}`,
  title,
  window_before: { start: '2026-04-12', end: '2026-08-12' },
  window_after: { start: '2026-05-12', end: '2026-09-12' },
  target_before: '2026-08-12',
  target_after: '2026-09-12',
})

describe('Definições Base: mudar algo já definido (F-PLN-01, regra 2)', () => {
  function withDefinedDate() {
    const baseline = emptyBaseline()
    baseline.date = {
      status: 'Definido',
      note: null,
      version: 4,
      value: { kind: 'exata', exact: '2027-05-01' },
    }
    return baseline
  }

  async function changeDate(user: ReturnType<typeof userEvent.setup>) {
    await user.click(await row(/Data ou época/))
    await screen.findByRole('dialog')
    fireEvent.change(screen.getByLabelText('Data'), { target: { value: '2027-06-05' } })
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))
  }

  it('pede confirmação, mostra o impacto e o antes e depois, e só envia ao confirmar', async () => {
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withDefinedDate()),
      [PUT_DATE]: jsonResponse(200, withDefinedDate()),
      [PREVIEW]: jsonResponse(200, preview()),
    })
    await changeDate(user)

    const confirmacao = within(await dialog())
    expect(await confirmacao.findByText('Mudar algo que vocês já definiram?')).toBeVisible()
    expect(await confirmacao.findByText('Nenhum marco muda de janela.')).toBeVisible()
    expect(confirmacao.getByText('1 mai 2027')).toBeVisible()
    expect(confirmacao.getByText('5 jun 2027')).toBeVisible()
    expect(api.callsTo(PUT_DATE)).toHaveLength(0)

    await user.click(screen.getByRole('button', { name: 'Confirmar mudança' }))
    await waitFor(() => expect(api.callsTo(PUT_DATE)).toHaveLength(1))
    expect(api.callsTo(PUT_DATE)[0]?.body).toMatchObject({
      version: 4,
      value: { kind: 'exata', exact: '2027-06-05' },
    })
  })

  it('Voltar devolve ao formulário com o que foi digitado, sem enviar nada', async () => {
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withDefinedDate()),
      [PREVIEW]: jsonResponse(200, preview()),
    })
    await changeDate(user)
    await user.click(await screen.findByRole('button', { name: 'Voltar' }))
    expect(screen.getByLabelText('Data')).toHaveValue('2027-06-05')
    expect(api.callsTo(PUT_DATE)).toHaveLength(0)
  })

  it('mudar só a nota não pede confirmação', async () => {
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withDefinedDate()),
      [PUT_DATE]: jsonResponse(200, withDefinedDate()),
    })
    await user.click(await row(/Data ou época/))
    await user.type(
      await screen.findByRole('textbox', { name: /Por que estamos em dúvida/ }),
      'só um lembrete',
    )
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))
    await waitFor(() => expect(api.callsTo(PUT_DATE)).toHaveLength(1))
    expect(screen.queryByText('Mudar algo que vocês já definiram?')).not.toBeInTheDocument()
  })

  it('voltar a Em definição é permitido sem confirmação', async () => {
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withDefinedDate()),
      [PUT_DATE]: jsonResponse(200, withDefinedDate()),
    })
    await user.click(await row(/Data ou época/))
    await screen.findByRole('dialog')
    await user.click(screen.getByRole('radio', { name: 'Em definição' }))
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))
    await waitFor(() => expect(api.callsTo(PUT_DATE)).toHaveLength(1))
    expect(api.callsTo(PUT_DATE)[0]?.body).toMatchObject({ status: 'Em definição' })
  })
})

describe('Definições Base: conflito e falhas', () => {
  it('versão velha: avisa, não sobrescreve e oferece a versão mais recente', async () => {
    const newer = emptyBaseline()
    newer.city = { status: 'Definido', note: null, version: 2, value: 'Outra Cidade Exemplo' }
    let reads = 0
    const { api, user } = renderPage({
      [GET]: () => {
        reads += 1
        return jsonResponse(200, reads === 1 ? emptyBaseline() : newer)
      },
      [PUT_CITY]: problemResponse(409, 'version_conflict', {
        detail: 'Este registro foi alterado por outra pessoa. Recarregue e tente de novo.',
      }),
    })
    await user.click(await row(/Cidade ou região/))
    await user.type(
      await screen.findByRole('textbox', { name: 'Cidade ou região' }),
      'Minha Cidade Exemplo',
    )
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    expect(
      await screen.findByText('Outra pessoa alterou esta definição enquanto vocês editavam.'),
    ).toBeVisible()
    expect(api.callsTo(PUT_CITY)).toHaveLength(1)

    await user.click(await screen.findByRole('button', { name: 'Ver a versão mais recente' }))
    expect(await screen.findByRole('textbox', { name: 'Cidade ou região' })).toHaveValue(
      'Outra Cidade Exemplo',
    )
    expect(api.callsTo(PUT_CITY)).toHaveLength(1)
    expect(
      screen.queryByText('Outra pessoa alterou esta definição enquanto vocês editavam.'),
    ).not.toBeInTheDocument()
  })

  it('falha de rede: avisa com calma e o formulário não perde o que foi digitado', async () => {
    const { user } = renderPage({
      [PUT_CITY]: () => {
        throw new TypeError('Failed to fetch')
      },
    })
    await user.click(await row(/Cidade ou região/))
    await user.type(
      await screen.findByRole('textbox', { name: 'Cidade ou região' }),
      'Cidade Exemplo',
    )
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    expect(await screen.findByText(/Não conseguimos salvar agora/)).toBeVisible()
    expect(screen.getByRole('textbox', { name: 'Cidade ou região' })).toHaveValue('Cidade Exemplo')
  })

  it('erro do servidor mostra a mensagem em português que a API mandou', async () => {
    const { user } = renderPage({
      [PUT_CITY]: problemResponse(422, 'invalid_baseline_value', {
        detail: 'Confira o valor deste campo: o formato ou o limite informado não é aceito.',
      }),
    })
    await user.click(await row(/Cidade ou região/))
    await user.type(
      await screen.findByRole('textbox', { name: 'Cidade ou região' }),
      'Cidade Exemplo',
    )
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))
    expect(await screen.findByText(/Confira o valor deste campo/)).toBeVisible()
  })
})

describe('Definições Base: histórico (F-PLN-01, regra 3)', () => {
  const change = (over: Partial<BaselineChange> = {}): BaselineChange => ({
    id: '00000000-0000-0000-0000-000000000001',
    field: 'date',
    by: 'Noiva',
    at: '2026-10-27T15:30:00Z',
    before: { status: 'Definido', note: null, value: { kind: 'exata', exact: '2027-05-01' } },
    after: { status: 'Definido', note: null, value: { kind: 'exata', exact: '2027-06-05' } },
    ...over,
  })

  it('lista quem mudou, quando e o valor anterior, do mais recente ao mais antigo', async () => {
    const { user } = renderPage({
      [CHANGES]: jsonResponse(200, [
        change(),
        change({
          id: '00000000-0000-0000-0000-000000000002',
          field: 'city',
          by: 'Noivo',
          before: { status: 'Em definição', note: null, value: null },
          after: { status: 'Definido', note: null, value: 'Cidade Exemplo' },
        }),
      ]),
    })
    await user.click(await screen.findByRole('button', { name: 'Ver histórico' }))
    const lista = await within(await dialog()).findByRole('list')
    const itens = within(lista).getAllByRole('listitem')
    expect(itens).toHaveLength(2)
    expect(itens[0]).toHaveTextContent('Noiva')
    expect(itens[0]).toHaveTextContent('27 out 2026, 12:30')
    expect(itens[0]).toHaveTextContent('Data ou época')
    expect(itens[0]).toHaveTextContent('1 mai 2027')
    expect(itens[0]).toHaveTextContent('5 jun 2027')
    expect(itens[1]).toHaveTextContent('Noivo')
    expect(itens[1]).toHaveTextContent('sem valor')
    expect(itens[1]).toHaveTextContent('Cidade Exemplo')
    expect(itens[1]).toHaveTextContent('Em definição')
  })

  it('sem mudanças, diz com calma que ainda não há nenhuma', async () => {
    const { user } = renderPage({ [CHANGES]: jsonResponse(200, []) })
    await user.click(await screen.findByRole('button', { name: 'Ver histórico' }))
    expect(await screen.findByText('Ainda sem mudanças.')).toBeVisible()
  })
})

describe('Planejamento: as abas ficam na URL (F-PLN-08)', () => {
  it('abre na aba das Definições Base quando a URL não diz nada', async () => {
    renderPage()
    expect(screen.getByRole('tab', { name: 'Definições Base' })).toHaveAttribute(
      'aria-selected',
      'true',
    )
    expect(await screen.findByRole('heading', { level: 2, name: 'Definições base' })).toBeVisible()
  })

  it('trocar de aba pede a mudança na URL e fecha a categoria aberta', async () => {
    const changes: object[] = []
    const { user } = renderPage({}, { onSearchChange: (patch) => changes.push(patch) })
    await user.click(screen.getByRole('tab', { name: 'Mapa de Escopo' }))
    expect(changes.at(-1)).toEqual({ aba: 'escopo', categoria: undefined })
  })

  it('com aba=escopo na URL mostra o Mapa de Escopo, sem pedir as Definições Base', async () => {
    const api = mockApi({
      'GET /api/v1/wedding/scope': jsonResponse(200, {
        groups: [],
        progress: { classified: 0, total: 0 },
        totals: {
          essential_cents: 0,
          essential_without_estimate: 0,
          maybe_cents: 0,
          maybe_without_estimate: 0,
        },
      }),
    })
    render(
      <QueryClientProvider client={new QueryClient()}>
        <WeddingPage search={{ aba: 'escopo' }} onSearchChange={() => {}} profile="Noiva" />
      </QueryClientProvider>,
    )
    expect(screen.getByRole('tab', { name: 'Mapa de Escopo' })).toHaveAttribute(
      'aria-selected',
      'true',
    )
    expect(await screen.findByText('Nenhuma frente por aqui ainda')).toBeVisible()
    expect(api.callsTo('GET /api/v1/wedding/baseline')).toHaveLength(0)
  })
})

describe('Definições Base: a prévia do cronograma ao mudar a data (F-CRN-05, regra 4)', () => {
  const definedAs = (value: Baseline['date']['value'], status: 'Definido' | 'Em definição') => {
    const baseline = emptyBaseline()
    baseline.date = { status, note: null, version: 4, value }
    return baseline
  }
  const withExactDate = () => definedAs({ kind: 'exata', exact: '2027-06-12' }, 'Definido')

  async function changeExactDate(user: ReturnType<typeof userEvent.setup>, to = '2027-07-12') {
    await user.click(await row(/Data ou época/))
    await screen.findByRole('dialog')
    fireEvent.change(screen.getByLabelText('Data'), { target: { value: to } })
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))
    return within(await dialog())
  }

  it('só consulta a prévia quando a tela de confirmação abre, com a data do formulário', async () => {
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withExactDate()),
      [PREVIEW]: jsonResponse(200, preview()),
    })
    await user.click(await row(/Data ou época/))
    await screen.findByRole('dialog')
    fireEvent.change(screen.getByLabelText('Data'), { target: { value: '2027-07-12' } })
    expect(api.callsTo(PREVIEW)).toHaveLength(0)

    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    await screen.findByText('Mudar algo que vocês já definiram?')
    await waitFor(() => expect(api.callsTo(PREVIEW)).toHaveLength(1))
    expect(new URL(api.callsTo(PREVIEW)[0]?.request.url as string).searchParams.get('exact')).toBe(
      '2027-07-12',
    )
  })

  it('mudar de data exata para uma janela é o cenário Sem Data: a consulta vai sem `exact`', async () => {
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withExactDate()),
      [PREVIEW]: jsonResponse(
        200,
        preview({
          mode_after: 'sem_data',
          changes: [{ ...aChange(1), window_after: null }],
          manual_kept: 2,
        }),
      ),
    })
    await user.click(await row(/Data ou época/))
    await screen.findByRole('dialog')
    await user.click(screen.getByRole('radio', { name: 'Janela' }))
    await user.click(screen.getByRole('combobox', { name: 'Mês do início' }))
    await user.click(screen.getByRole('option', { name: 'junho' }))
    await user.type(screen.getByRole('textbox', { name: 'Ano do início' }), '2027')
    await user.click(screen.getByRole('combobox', { name: 'Mês do fim' }))
    await user.click(screen.getByRole('option', { name: 'julho' }))
    await user.type(screen.getByRole('textbox', { name: 'Ano do fim' }), '2027')
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    const confirmacao = within(await dialog())
    expect(await confirmacao.findByText('1 marco perde a janela calculada.')).toBeVisible()
    expect(confirmacao.getByText('2 marcos com prazo definido por vocês não mudam.')).toBeVisible()
    expect(new URL(api.callsTo(PREVIEW)[0]?.request.url as string).searchParams.has('exact')).toBe(
      false,
    )
  })

  it('resume o que muda, os prazos de vocês que ficam, os atrasos novos e lista os marcos', async () => {
    const { user } = renderPage({
      [GET]: jsonResponse(200, withExactDate()),
      [PREVIEW]: jsonResponse(
        200,
        preview({
          changes: [aChange(1), aChange(2), aChange(3)],
          manual_kept: 1,
          newly_overdue: 2,
        }),
      ),
    })
    const confirmacao = await changeExactDate(user)

    expect(await confirmacao.findByText('3 marcos mudam de janela.')).toBeVisible()
    expect(confirmacao.getByText('1 marco com prazo definido por vocês não muda.')).toBeVisible()
    expect(confirmacao.getByText('2 marcos passam a aparecer como Atrasado.')).toBeVisible()
    const lista = confirmacao.getByRole('list', { name: 'Marcos que mudam de janela' })
    expect(within(lista).getAllByRole('listitem')).toHaveLength(3)
    expect(within(lista).getAllByText('12/04/2026 a 12/08/2026')).toHaveLength(3)
  })

  it('ao abrir a confirmação, o foco vai ao título dela, e não se perde', async () => {
    const { user } = renderPage({
      [GET]: jsonResponse(200, withExactDate()),
      [PREVIEW]: jsonResponse(200, preview()),
    })
    const confirmacao = await changeExactDate(user)

    expect(
      confirmacao.getByRole('heading', { name: 'Mudar algo que vocês já definiram?' }),
    ).toHaveFocus()
  })

  it('o texto fixo antigo não aparece quando a prévia chega', async () => {
    const { user } = renderPage({
      [GET]: jsonResponse(200, withExactDate()),
      [PREVIEW]: jsonResponse(200, preview({ changes: [aChange(1)] })),
    })
    const confirmacao = await changeExactDate(user)

    await confirmacao.findByText('1 marco muda de janela.')
    expect(confirmacao.queryByText('A data recalcula as janelas do cronograma.')).toBeNull()
  })

  it('enquanto calcula, avisa numa região de status e o confirmar não fica bloqueado', async () => {
    let release: (response: Response) => void = () => {}
    const pending = new Promise<Response>((resolve) => {
      release = resolve
    })
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withExactDate()),
      [PUT_DATE]: jsonResponse(200, withExactDate()),
      [PREVIEW]: () => pending,
    })
    const confirmacao = await changeExactDate(user)

    expect(await confirmacao.findByRole('status')).toHaveTextContent(
      'Calculando o que muda no cronograma…',
    )
    const confirmar = confirmacao.getByRole('button', { name: 'Confirmar mudança' })
    expect(confirmar).toBeEnabled()

    await user.click(confirmar)
    await waitFor(() => expect(api.callsTo(PUT_DATE)).toHaveLength(1))
    release(jsonResponse(200, preview()))
  })

  it('se a prévia falha, diz que não calculou e o confirmar continua valendo', async () => {
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withExactDate()),
      [PUT_DATE]: jsonResponse(200, withExactDate()),
      [PREVIEW]: problemResponse(500, 'internal_error'),
    })
    const confirmacao = await changeExactDate(user)

    expect(
      await confirmacao.findByText(
        'Não conseguimos calcular agora o que muda no cronograma. Ao confirmar, as janelas são recalculadas.',
      ),
    ).toBeVisible()
    expect(confirmacao.queryByText('A data recalcula as janelas do cronograma.')).toBeNull()
    expect(confirmacao.queryByText(/Calculando/)).not.toBeInTheDocument()

    await user.click(confirmacao.getByRole('button', { name: 'Confirmar mudança' }))
    await waitFor(() => expect(api.callsTo(PUT_DATE)).toHaveLength(1))
  })

  it('Voltar e confirmar de novo calcula outra vez, sem aproveitar a prévia antiga', async () => {
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withExactDate()),
      [PREVIEW]: jsonResponse(200, preview({ changes: [aChange(1)] })),
    })
    const primeira = await changeExactDate(user)
    await primeira.findByText('1 marco muda de janela.')

    await user.click(screen.getByRole('button', { name: 'Voltar' }))
    await user.click(await screen.findByRole('button', { name: 'Salvar definição' }))

    await screen.findByText('Mudar algo que vocês já definiram?')
    await waitFor(() => expect(api.callsTo(PREVIEW)).toHaveLength(2))
  })

  it('a primeira definição da data não pede confirmação nem consulta a prévia', async () => {
    const { api, user } = renderPage({
      [PUT_DATE]: jsonResponse(200, withExactDate()),
      [PREVIEW]: jsonResponse(200, preview()),
    })
    await user.click(await row(/Data ou época/))
    await screen.findByRole('dialog')
    await user.click(screen.getByRole('radio', { name: 'Data exata' }))
    fireEvent.change(screen.getByLabelText('Data'), { target: { value: '2027-06-12' } })
    await user.click(screen.getByRole('radio', { name: 'Definido' }))
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    await waitFor(() => expect(api.callsTo(PUT_DATE)).toHaveLength(1))
    expect(screen.queryByText('Mudar algo que vocês já definiram?')).not.toBeInTheDocument()
    expect(api.callsTo(PREVIEW)).toHaveLength(0)
  })

  it('voltar a Em definição não pede confirmação nem consulta a prévia', async () => {
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withExactDate()),
      [PUT_DATE]: jsonResponse(200, withExactDate()),
      [PREVIEW]: jsonResponse(200, preview()),
    })
    await user.click(await row(/Data ou época/))
    await screen.findByRole('dialog')
    await user.click(screen.getByRole('radio', { name: 'Em definição' }))
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    await waitFor(() => expect(api.callsTo(PUT_DATE)).toHaveLength(1))
    expect(api.callsTo(PREVIEW)).toHaveLength(0)
  })

  it('só a data tem prévia: mudar a cidade já definida mantém o texto próprio, sem consulta', async () => {
    const baseline = emptyBaseline()
    baseline.city = { status: 'Definido', note: null, version: 2, value: 'Cidade Exemplo' }
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, baseline),
      [PREVIEW]: jsonResponse(200, preview()),
    })
    await user.click(await row(/Cidade/))
    await screen.findByRole('dialog')
    const campo = screen.getByRole('textbox', { name: /Cidade/ })
    await user.clear(campo)
    await user.type(campo, 'Outra Cidade Exemplo')
    await user.click(screen.getByRole('button', { name: 'Salvar definição' }))

    await screen.findByText('Mudar algo que vocês já definiram?')
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
    expect(api.callsTo(PREVIEW)).toHaveLength(0)
  })

  it('não lê nem invalida o cronograma: ele refaz a leitura sozinho ao montar', async () => {
    const { api, user } = renderPage({
      [GET]: jsonResponse(200, withExactDate()),
      [PUT_DATE]: jsonResponse(200, withExactDate()),
      [PREVIEW]: jsonResponse(200, preview()),
    })
    const confirmacao = await changeExactDate(user)
    await user.click(confirmacao.getByRole('button', { name: 'Confirmar mudança' }))

    await waitFor(() => expect(api.callsTo(PUT_DATE)).toHaveLength(1))
    expect(api.callsTo(SCHEDULE)).toHaveLength(0)
  })
})
