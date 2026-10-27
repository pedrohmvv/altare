import { screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { renderRoute } from '@/test/render-route'

const AREAS = [
  ['/', 'O momento de vocês'],
  ['/planejamento', 'O rumo de vocês'],
  ['/cronograma', 'O que pode andar agora'],
  ['/possibilidades', 'Comparar propostas'],
  ['/orcamento', 'O orçamento de vocês'],
  ['/contatos', 'Quem vocês estão consultando'],
  ['/convidados', 'Quem estará com vocês'],
  ['/assistente', 'Conversem com o assistente'],
] as const

describe('rotas das áreas', () => {
  it.each(AREAS)('%s mostra o título editorial da área como o único h1', async (path, title) => {
    await renderRoute(path)

    expect(await screen.findByRole('heading', { level: 1, name: title })).toBeInTheDocument()
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1)
  })

  it.each(AREAS)('%s mostra um estado vazio acolhedor, sem ação morta', async (path) => {
    await renderRoute(path)

    expect(await screen.findByRole('heading', { level: 2 })).toBeVisible()
    expect(within(screen.getByRole('main')).queryByRole('button')).not.toBeInTheDocument()
  })

  it('um caminho desconhecido mostra a página não encontrada com a saída para a Visão Geral', async () => {
    await renderRoute('/nao-existe')

    expect(
      await screen.findByRole('heading', { name: 'Não encontramos esta página' }),
    ).toBeVisible()
    expect(screen.getByRole('link', { name: 'Ir para a Visão Geral' })).toHaveAttribute('href', '/')
  })

  it('em desenvolvimento a rota /design-system abre a vitrine, fora da navegação', async () => {
    await renderRoute('/design-system')

    expect(await screen.findByRole('heading', { level: 1, name: 'Design System' })).toBeVisible()
  })
})

describe('vitrine só em desenvolvimento (D-053, D-057)', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
  })

  it('em produção a rota /design-system não existe: cai na página não encontrada', async () => {
    vi.stubEnv('DEV', false)
    await renderRoute('/design-system')

    expect(
      await screen.findByRole('heading', { name: 'Não encontramos esta página' }),
    ).toBeVisible()
    expect(
      screen.queryByRole('heading', { level: 1, name: 'Design System' }),
    ).not.toBeInTheDocument()
  })
})

describe('lente na URL', () => {
  it('lê ?lente=minha', async () => {
    const router = await renderRoute('/cronograma?lente=minha')

    expect(router.state.matches.at(-1)?.search).toMatchObject({ lente: 'minha' })
  })

  it('sem o parâmetro, a lente é Casal (nenhum valor)', async () => {
    const router = await renderRoute('/cronograma')

    expect(router.state.matches.at(-1)?.search.lente).toBeUndefined()
  })

  it('um valor inválido cai em Casal', async () => {
    const router = await renderRoute('/cronograma?lente=banana')

    expect(router.state.matches.at(-1)?.search.lente).toBeUndefined()
  })
})
