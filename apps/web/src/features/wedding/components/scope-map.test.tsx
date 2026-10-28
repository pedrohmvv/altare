import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { jsonResponse, mockApi, problemResponse } from '@/test/fake-api'
import { MAP } from '@/test/scope-fixtures'
import type { PlanningSearch } from '../search'
import { ScopeMap } from './scope-map'

const GET = 'GET /api/v1/wedding/scope'
function Harness({
  initial = {},
  onChange,
  lens,
  profile = 'Noivo',
}: {
  initial?: PlanningSearch
  onChange?: (p: object) => void
  lens?: 'casal' | 'minha'
  profile?: 'Noivo' | 'Noiva'
}) {
  const [search, setSearch] = useState<PlanningSearch>(initial)
  return (
    <ScopeMap
      search={search}
      profile={profile}
      lens={lens}
      onSearchChange={(patch) => {
        onChange?.(patch)
        setSearch((prev) => {
          const next: Record<string, unknown> = { ...prev, ...patch }
          for (const key of Object.keys(next)) if (next[key] === undefined) delete next[key]
          return next as PlanningSearch
        })
      }}
    />
  )
}

function renderMap(handlers = {}, props: Parameters<typeof Harness>[0] = {}) {
  const api = mockApi({ [GET]: jsonResponse(200, MAP), ...handlers })
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <Harness {...props} />
    </QueryClientProvider>,
  )
  return { api, user: userEvent.setup() }
}

describe('Mapa de Escopo: leitura (F-PLN-02, F-PLN-05, F-PLN-08)', () => {
  it('mostra o que carrega, depois os grupos e as categorias visíveis', async () => {
    renderMap()
    expect(screen.getByText('Carregando o Mapa de Escopo')).toBeInTheDocument()
    expect(await screen.findByRole('heading', { level: 3, name: 'Grupo Exemplo A' })).toBeVisible()
    expect(screen.getByRole('heading', { level: 4, name: 'Fotografia Exemplo' })).toBeVisible()
    expect(screen.getByRole('heading', { level: 4, name: 'Buffet Exemplo' })).toBeVisible()
    expect(screen.queryByText('Oculta Exemplo')).not.toBeInTheDocument()
  })

  it('o progresso vem da API, por escrito e como barra', async () => {
    renderMap()
    const barra = await screen.findByRole('progressbar', {
      name: '2 de 3 categorias classificadas',
    })
    expect(barra).toHaveAttribute('aria-valuenow', '2')
    expect(barra).toHaveAttribute('aria-valuemax', '3')
  })

  it('os totais separam Entra e Talvez e dizem quantas estão sem estimativa', async () => {
    renderMap()
    const totais = await screen.findByRole('group', { name: 'Estimativas' })
    expect(within(totais).getByText(/R\$\s1\.500/)).toBeVisible()
    expect(within(totais).getByText('2 sem estimativa')).toBeVisible()
  })

  it('cada categoria mostra status, estimativa (ou "sem estimativa") e alinhamento em texto', async () => {
    renderMap()
    const foto = (await screen.findByRole('heading', { name: 'Fotografia Exemplo' })).closest('li')
    expect(foto).not.toBeNull()
    expect(within(foto as HTMLElement).getByText('Entra (Essencial)')).toBeVisible()
    expect(within(foto as HTMLElement).getByText(/R\$\s1\.500/)).toBeVisible()
    expect(within(foto as HTMLElement).getByText('Divergem')).toBeVisible()
    const video = screen
      .getByRole('heading', { name: 'Vídeo Exemplo' })
      .closest('li') as HTMLElement
    expect(within(video).getByText('sem estimativa')).toBeVisible()
    expect(within(video).getByText('Aguardando avaliação da Noiva')).toBeVisible()
    const buffet = screen
      .getByRole('heading', { name: 'Buffet Exemplo' })
      .closest('li') as HTMLElement
    expect(within(buffet).getByText('Alinhados')).toBeVisible()
    expect(within(buffet).getByText(/fora do teto/)).toBeVisible()
  })

  it('erro de carga oferece tentar de novo', async () => {
    let tentativas = 0
    const { user } = renderMap({
      [GET]: () => {
        tentativas += 1
        return tentativas === 1 ? problemResponse(500, 'internal_error') : jsonResponse(200, MAP)
      },
    })
    expect(await screen.findByText('Não conseguimos carregar o Mapa de Escopo')).toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Tentar de novo' }))
    expect(await screen.findByRole('heading', { name: 'Grupo Exemplo A' })).toBeVisible()
  })

  it('sem nenhuma frente, o estado vazio acolhe', async () => {
    renderMap({
      [GET]: jsonResponse(200, { ...MAP, groups: [], progress: { classified: 0, total: 0 } }),
    })
    expect(await screen.findByText('Nenhuma frente por aqui ainda')).toBeVisible()
  })
})

describe('Mapa de Escopo: filtros e vistas na URL (F-PLN-08)', () => {
  it('um chip de status liga o filtro, mostra só o que combina e desliga ao clicar de novo', async () => {
    const onChange = vi.fn()
    const { user } = renderMap({}, { onChange })
    const chip = await screen.findByRole('button', { name: 'Fica de fora' })
    expect(chip).toHaveAttribute('aria-pressed', 'false')

    await user.click(chip)
    expect(onChange).toHaveBeenLastCalledWith({ status: 'fora' })
    expect(chip).toHaveAttribute('aria-pressed', 'true')
    expect(screen.queryByRole('heading', { name: 'Fotografia Exemplo' })).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Buffet Exemplo' })).toBeVisible()

    await user.click(chip)
    expect(onChange).toHaveBeenLastCalledWith({ status: undefined })
    expect(screen.getByRole('heading', { name: 'Fotografia Exemplo' })).toBeVisible()
  })

  it('divergem e falta avaliar filtram pelo alinhamento que a API calculou', async () => {
    const { user } = renderMap()
    await user.click(await screen.findByRole('button', { name: 'Divergem' }))
    expect(screen.getByRole('heading', { name: 'Fotografia Exemplo' })).toBeVisible()
    expect(screen.queryByRole('heading', { name: 'Vídeo Exemplo' })).not.toBeInTheDocument()
  })

  it('"só o que falta eu avaliar" usa a prioridade de quem está na sessão', async () => {
    const { user } = renderMap()
    await user.click(await screen.findByRole('button', { name: 'Só o que falta eu avaliar' }))
    // o Noivo já avaliou Fotografia e Vídeo; falta só Buffet? não: Buffet tem as duas. Nada falta.
    expect(screen.getByText('Nada neste filtro')).toBeVisible()
  })

  it('filtro sem resultado diz com calma e "Limpar filtros" desliga todos', async () => {
    const onChange = vi.fn()
    const { user } = renderMap({}, { initial: { status: 'talvez' }, onChange })
    expect(await screen.findByText('Nada neste filtro')).toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Limpar filtros' }))
    expect(onChange).toHaveBeenLastCalledWith({
      status: undefined,
      alinhamento: undefined,
      pendente: undefined,
    })
    expect(await screen.findByRole('heading', { name: 'Fotografia Exemplo' })).toBeVisible()
  })

  it('mostrar ocultas traz as ocultas, marcadas em texto', async () => {
    const { user } = renderMap()
    await user.click(await screen.findByRole('button', { name: 'Mostrar ocultas' }))
    const oculta = screen
      .getByRole('heading', { name: 'Oculta Exemplo' })
      .closest('li') as HTMLElement
    expect(within(oculta).getByText('Oculta')).toBeVisible()
  })

  it('a vista por status agrupa nas quatro seções, na ordem', async () => {
    const { user } = renderMap()
    await user.click(await screen.findByRole('radio', { name: 'Por status' }))
    const titulos = screen.getAllByRole('heading', { level: 3 }).map((h) => h.textContent)
    expect(titulos).toEqual([
      'Em discussão',
      'Entra (Essencial)',
      'Talvez (Se couber)',
      'Fica de fora',
    ])
    const entra = screen
      .getByRole('heading', { level: 3, name: 'Entra (Essencial)' })
      .closest('section') as HTMLElement
    expect(within(entra).getByRole('heading', { name: 'Fotografia Exemplo' })).toBeVisible()
  })

  it('abre já filtrado quando a URL traz o filtro', async () => {
    renderMap({}, { initial: { status: 'entra', vista: 'status' } })
    expect(await screen.findByRole('button', { name: 'Entra (Essencial)' })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
    expect(screen.getByRole('radio', { name: 'Por status' })).toBeChecked()
  })
})

describe('Mapa de Escopo: lente e quadro (F-PLN-08)', () => {
  it('Minha visão destaca, em texto, o que falta a minha avaliação', async () => {
    renderMap({}, { profile: 'Noiva', lens: 'minha' })
    const video = (await screen.findByRole('heading', { name: 'Vídeo Exemplo' })).closest(
      'li',
    ) as HTMLElement
    expect(within(video).getByText('Falta a sua avaliação')).toBeVisible()
    const foto = screen
      .getByRole('heading', { name: 'Fotografia Exemplo' })
      .closest('li') as HTMLElement
    expect(within(foto).queryByText('Falta a sua avaliação')).not.toBeInTheDocument()
  })

  it('Casal destaca, em texto, o que diverge, e a lente nunca esconde nada', async () => {
    renderMap({}, { lens: 'casal' })
    const foto = (await screen.findByRole('heading', { name: 'Fotografia Exemplo' })).closest(
      'li',
    ) as HTMLElement
    expect(within(foto).getByText('Vale conversar')).toBeVisible()
    expect(screen.getByRole('heading', { name: 'Vídeo Exemplo' })).toBeVisible()
    expect(screen.getByRole('heading', { name: 'Buffet Exemplo' })).toBeVisible()
  })

  it('na tela larga, a vista por status é o quadro de quatro colunas', async () => {
    vi.stubGlobal('matchMedia', (query: string) => ({
      matches: true,
      media: query,
      addEventListener() {},
      removeEventListener() {},
    }))
    renderMap({}, { initial: { vista: 'status' } })
    const quadro = await screen.findByRole('region', { name: 'Quadro por status' })
    const colunas = within(quadro).getAllByRole('heading', { level: 3 })
    expect(colunas.map((c) => c.textContent)).toEqual([
      'Em discussão',
      'Entra (Essencial)',
      'Talvez (Se couber)',
      'Fica de fora',
    ])
    const entra = within(quadro)
      .getByRole('heading', { name: 'Entra (Essencial)' })
      .closest('section') as HTMLElement
    expect(within(entra).getByRole('heading', { name: 'Fotografia Exemplo' })).toBeVisible()
  })

  it('na tela estreita, a vista por status é a lista agrupada, sem o quadro', async () => {
    renderMap({}, { initial: { vista: 'status' } })
    expect(
      await screen.findByRole('heading', { level: 3, name: 'Entra (Essencial)' }),
    ).toBeVisible()
    expect(screen.queryByRole('region', { name: 'Quadro por status' })).not.toBeInTheDocument()
  })
})
