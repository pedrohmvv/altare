import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderRoute } from '@/test/render-route'

const AREAS = [
  ['/', 'Visão Geral'],
  ['/planejamento', 'Planejamento & Caminhos'],
  ['/cronograma', 'Cronograma & Dependências'],
  ['/possibilidades', 'Possibilidades & Decisões'],
  ['/orcamento', 'Orçamento & Simulador'],
  ['/contatos', 'Contatos & Fornecedores'],
  ['/convidados', 'Convidados, Enxoval & Dia D'],
  ['/assistente', 'Assistente'],
] as const

describe('rotas das áreas', () => {
  it.each(AREAS)('%s mostra o título da área como o único h1', async (path, title) => {
    await renderRoute(path)

    expect(await screen.findByRole('heading', { level: 1, name: title })).toBeInTheDocument()
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1)
  })

  it.each(AREAS)('%s mostra um estado vazio acolhedor, sem ação morta', async (path) => {
    await renderRoute(path)

    expect(await screen.findByRole('heading', { level: 2 })).toBeVisible()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('um caminho desconhecido mostra a página não encontrada com a saída para a Visão Geral', async () => {
    await renderRoute('/nao-existe')

    expect(
      await screen.findByRole('heading', { name: 'Não encontramos esta página' }),
    ).toBeVisible()
    expect(screen.getByRole('link', { name: 'Ir para a Visão Geral' })).toHaveAttribute('href', '/')
  })

  it('a rota /design-system abre a conferência provisória, fora da navegação', async () => {
    await renderRoute('/design-system')

    expect(await screen.findByRole('heading', { level: 1, name: 'Design System' })).toBeVisible()
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
