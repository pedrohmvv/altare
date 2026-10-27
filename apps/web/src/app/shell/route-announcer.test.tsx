import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { renderRoute } from '@/test/render-route'

const sidebar = () => screen.getByRole('navigation', { name: 'Navegação principal' })

describe('anúncio da troca de rota', () => {
  it('põe o nome da área no título do documento já na primeira página', async () => {
    await renderRoute('/cronograma')
    await screen.findByRole('heading', { level: 1, name: 'Cronograma & Dependências' })

    expect(document.title).toBe('Cronograma & Dependências · Altare')
  })

  it('não rouba o foco na primeira página', async () => {
    await renderRoute('/')
    const title = await screen.findByRole('heading', { level: 1, name: 'Visão Geral' })

    expect(title).not.toHaveFocus()
  })

  it('ao trocar de área muda o título do documento e leva o foco ao novo h1', async () => {
    await renderRoute('/')
    await screen.findByRole('heading', { level: 1, name: 'Visão Geral' })

    await userEvent.click(within(sidebar()).getByRole('link', { name: 'Orçamento & Simulador' }))

    const title = await screen.findByRole('heading', { level: 1, name: 'Orçamento & Simulador' })
    await waitFor(() => expect(title).toHaveFocus())
    expect(document.title).toBe('Orçamento & Simulador · Altare')
  })

  it('o título da página é focável por programa, mas fora da ordem do Tab', async () => {
    await renderRoute('/')
    const title = await screen.findByRole('heading', { level: 1, name: 'Visão Geral' })

    expect(title).toHaveAttribute('tabindex', '-1')
  })

  it('trocar só a lente não move o foco nem muda o título', async () => {
    await renderRoute('/cronograma')
    const title = await screen.findByRole('heading', { level: 1 })
    const lens = screen.getByRole('radio', { name: 'Minha visão' })

    await userEvent.click(lens)

    await waitFor(() => expect(lens).toBeChecked())
    expect(title).not.toHaveFocus()
    expect(document.title).toBe('Cronograma & Dependências · Altare')
  })

  it('em uma página inexistente o título diz que não foi encontrada', async () => {
    await renderRoute('/nao-existe')
    await screen.findByRole('heading', { level: 1, name: 'Não encontramos esta página' })

    expect(document.title).toBe('Página não encontrada · Altare')
  })
})
