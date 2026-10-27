import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { renderRoute } from '@/test/render-route'

const AREA_NAMES = [
  'Visão Geral',
  'Planejamento & Caminhos',
  'Cronograma & Dependências',
  'Possibilidades & Decisões',
  'Orçamento & Simulador',
  'Contatos & Fornecedores',
  'Convidados, Enxoval & Dia D',
  'Assistente',
]

const sidebar = () => screen.getByRole('navigation', { name: 'Navegação principal' })
const bottomBar = () => screen.getByRole('navigation', { name: 'Navegação principal (celular)' })

describe('casca de navegação', () => {
  it('tem os pontos de referência da página, com dois menus de nomes distintos', async () => {
    await renderRoute('/cronograma')
    await screen.findByRole('heading', { level: 1 })

    // O PageHeader também usa <header>, que o jsdom lê como banner; a barra superior vem primeiro.
    expect(screen.getAllByRole('banner')[0]).toBeInTheDocument()
    expect(screen.getByRole('main')).toHaveAttribute('id', 'conteudo')
    expect(sidebar()).toBeInTheDocument()
    expect(bottomBar()).toBeInTheDocument()
  })

  it('lista as 8 áreas na barra lateral, com o Assistente por último', async () => {
    await renderRoute('/')
    await screen.findByRole('heading', { level: 1 })

    const links = within(sidebar())
      .getAllByRole('link')
      .filter((link) => link.getAttribute('aria-label') === null)
    expect(links.map((link) => link.textContent)).toEqual(AREA_NAMES)
  })

  it('marca a área atual com aria-current="page"', async () => {
    await renderRoute('/orcamento')
    await screen.findByRole('heading', { level: 1, name: 'Orçamento & Simulador' })

    expect(within(sidebar()).getByRole('link', { name: 'Orçamento & Simulador' })).toHaveAttribute(
      'aria-current',
      'page',
    )
    expect(within(sidebar()).getByRole('link', { name: 'Visão Geral' })).not.toHaveAttribute(
      'aria-current',
    )
  })

  it('troca de área ao clicar e mantém só a nova como atual', async () => {
    await renderRoute('/')
    await screen.findByRole('heading', { level: 1, name: 'Visão Geral' })

    await userEvent.click(
      within(sidebar()).getByRole('link', { name: 'Cronograma & Dependências' }),
    )

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Cronograma & Dependências' }),
    ).toBeVisible()
    expect(
      within(sidebar()).getByRole('link', { name: 'Cronograma & Dependências' }),
    ).toHaveAttribute('aria-current', 'page')
    expect(within(sidebar()).getByRole('link', { name: 'Visão Geral' })).not.toHaveAttribute(
      'aria-current',
    )
  })

  it('a marca leva à Visão Geral', async () => {
    await renderRoute('/contatos')
    await screen.findByRole('heading', { level: 1 })

    // A marca fica no aside, acima do menu principal.
    expect(
      within(screen.getByRole('complementary')).getByRole('link', {
        name: 'Altare, ir para a Visão Geral',
      }),
    ).toHaveAttribute('href', '/')
  })

  it('o primeiro foco do teclado é o link "Ir para o conteúdo", que aponta para o main', async () => {
    await renderRoute('/')
    await screen.findByRole('heading', { level: 1 })

    await userEvent.tab()

    const skip = screen.getByRole('link', { name: 'Ir para o conteúdo' })
    expect(skip).toHaveFocus()
    expect(skip).toHaveAttribute('href', '#conteudo')
  })
})

describe('seletor de lente', () => {
  it('começa em Casal e tem um grupo nomeado na barra superior', async () => {
    await renderRoute('/')
    await screen.findByRole('heading', { level: 1 })

    const group = within(screen.getAllByRole('banner')[0] as HTMLElement).getByRole('radiogroup', {
      name: 'Lente de visão',
    })
    expect(within(group).getByRole('radio', { name: 'Casal' })).toBeChecked()
    expect(within(group).getByRole('radio', { name: 'Minha visão' })).not.toBeChecked()
  })

  it('lê a lente da URL', async () => {
    await renderRoute('/cronograma?lente=minha')
    await screen.findByRole('heading', { level: 1 })

    expect(screen.getByRole('radio', { name: 'Minha visão' })).toBeChecked()
  })

  it('trocar para Minha visão coloca ?lente=minha na URL e voltar para Casal a tira', async () => {
    const router = await renderRoute('/cronograma')
    await screen.findByRole('heading', { level: 1 })

    await userEvent.click(screen.getByRole('radio', { name: 'Minha visão' }))
    await waitFor(() => expect(router.state.location.search).toMatchObject({ lente: 'minha' }))
    expect(screen.getByRole('radio', { name: 'Minha visão' })).toBeChecked()

    await userEvent.click(screen.getByRole('radio', { name: 'Casal' }))
    await waitFor(() => expect(router.state.location.search.lente).toBeUndefined())
    expect(router.state.location.href).not.toContain('lente')
  })

  it('a lente continua ao navegar entre as áreas', async () => {
    const router = await renderRoute('/?lente=minha')
    await screen.findByRole('heading', { level: 1 })

    await userEvent.click(within(sidebar()).getByRole('link', { name: 'Contatos & Fornecedores' }))

    await screen.findByRole('heading', { level: 1, name: 'Contatos & Fornecedores' })
    expect(router.state.location.search).toMatchObject({ lente: 'minha' })
    expect(screen.getByRole('radio', { name: 'Minha visão' })).toBeChecked()
  })
})

describe('barra inferior do celular', () => {
  it('tem 4 destinos mais o botão Mais', async () => {
    await renderRoute('/')
    await screen.findByRole('heading', { level: 1 })

    const bar = within(bottomBar())
    expect(
      bar
        .getAllByRole('link')
        .map((link) => link.textContent)
        .sort(),
    ).toEqual(['Contatos', 'Início', 'Opções', 'Orçamento'])
    expect(bar.getByRole('button', { name: 'Mais' })).toBeInTheDocument()
  })

  it('o Mais abre uma folha com as demais áreas, inclusive o Assistente', async () => {
    await renderRoute('/')
    await screen.findByRole('heading', { level: 1 })

    await userEvent.click(within(bottomBar()).getByRole('button', { name: 'Mais' }))

    const dialog = await screen.findByRole('dialog', { name: 'Mais áreas' })
    expect(
      within(dialog)
        .getAllByRole('link')
        .map((link) => link.textContent),
    ).toEqual([
      'Planejamento & Caminhos',
      'Cronograma & Dependências',
      'Convidados, Enxoval & Dia D',
      'Assistente',
    ])
  })

  it('escolher uma área na folha fecha a folha e navega', async () => {
    await renderRoute('/')
    await screen.findByRole('heading', { level: 1 })
    await userEvent.click(within(bottomBar()).getByRole('button', { name: 'Mais' }))
    const dialog = await screen.findByRole('dialog', { name: 'Mais áreas' })

    await userEvent.click(within(dialog).getByRole('link', { name: 'Assistente' }))

    expect(await screen.findByRole('heading', { level: 1, name: 'Assistente' })).toBeVisible()
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('marca o destino atual e usa o nome curto Opções para Possibilidades & Decisões', async () => {
    await renderRoute('/possibilidades')
    await screen.findByRole('heading', { level: 1 })

    expect(within(bottomBar()).getByRole('link', { name: 'Opções' })).toHaveAttribute(
      'aria-current',
      'page',
    )
  })
})
