import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { renderRoute } from '@/test/render-route'

const launcher = () => screen.findByRole('button', { name: 'Assistente' })

describe('ícone flutuante do assistente (D-050, D-054 item 11)', () => {
  it('aparece recolhido nas áreas e nunca abre sozinho', async () => {
    await renderRoute('/orcamento')

    const button = await launcher()
    expect(button).toHaveAttribute('aria-expanded', 'false')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('fica oculto na própria área Assistente', async () => {
    await renderRoute('/assistente')
    await screen.findByRole('heading', { level: 1, name: 'Conversem com o assistente' })

    expect(screen.queryByRole('button', { name: 'Assistente' })).not.toBeInTheDocument()
  })

  it('aparece também na vitrine, que não é uma das 8 áreas', async () => {
    await renderRoute('/design-system')
    expect(await launcher()).toBeInTheDocument()
  })

  it('abre um painel que diz com calma que o assistente ainda não está disponível', async () => {
    await renderRoute('/contatos')

    await userEvent.click(await launcher())

    const panel = await screen.findByRole('dialog', {
      name: 'O assistente ainda não está disponível',
    })
    expect(panel).toHaveAccessibleDescription(/chega com a camada de inteligência/)
    // Sem prometer prazo e sem simular um chat: nada de campo de texto nem de botão de enviar.
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    expect(panel.textContent).not.toMatch(/\d+ (dias|semanas|meses)|em breve|amanhã/i)
  })

  it('fecha com Esc e devolve o foco ao ícone', async () => {
    await renderRoute('/cronograma')
    const button = await launcher()

    await userEvent.click(button)
    await screen.findByRole('dialog')
    await userEvent.keyboard('{Escape}')

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(button).toHaveFocus()
  })

  it('não tira o ícone da ordem de Tab (alcançável pelo teclado) e é um botão', async () => {
    await renderRoute('/planejamento')
    const button = await launcher()

    expect(button.tagName).toBe('BUTTON')
    expect(button).not.toHaveAttribute('tabindex', '-1')
  })

  it('recolhe ao rolar para baixo para não cobrir o que se lê, sem sair da ordem de Tab', async () => {
    await renderRoute('/orcamento')
    const button = await launcher()
    expect(button).not.toHaveAttribute('data-hidden')

    act(() => {
      Object.defineProperty(window, 'scrollY', { value: 300, configurable: true })
      window.dispatchEvent(new Event('scroll'))
    })
    expect(button).toHaveAttribute('data-hidden', 'true')
    // Continua alcançável pelo teclado e pelo leitor de tela: só some da vista.
    expect(button).not.toHaveAttribute('tabindex', '-1')
    expect(button).not.toHaveAttribute('aria-hidden')

    act(() => {
      Object.defineProperty(window, 'scrollY', { value: 0, configurable: true })
      window.dispatchEvent(new Event('scroll'))
    })
    expect(button).not.toHaveAttribute('data-hidden')
  })

  it('mantém a pílula à vista enquanto o cartão está aberto, mesmo rolando para baixo', async () => {
    await renderRoute('/orcamento')
    const button = await launcher()

    await userEvent.click(button)
    await screen.findByRole('dialog')
    act(() => {
      Object.defineProperty(window, 'scrollY', { value: 400, configurable: true })
      window.dispatchEvent(new Event('scroll'))
    })

    expect(button).not.toHaveAttribute('data-hidden')
  })
})
