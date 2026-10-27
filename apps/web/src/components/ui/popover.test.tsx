import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { Button } from './button'
import { Popover, PopoverContent, PopoverTrigger } from './popover'

const renderPopover = (content: Partial<Parameters<typeof PopoverContent>[0]> = {}) =>
  render(
    <Popover>
      <PopoverTrigger asChild>
        <Button>Abrir</Button>
      </PopoverTrigger>
      <PopoverContent title="Nota do espaço" description="Só para conferência." {...content}>
        <p>Espaço Exemplo A</p>
      </PopoverContent>
    </Popover>,
  )

describe('Popover', () => {
  it('começa fechado, com o gatilho dizendo que não está expandido', () => {
    renderPopover()

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Abrir' })).toHaveAttribute('aria-expanded', 'false')
  })

  it('abre pelo gatilho com o título como nome e a descrição ligada', async () => {
    renderPopover()

    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))

    const popover = await screen.findByRole('dialog', { name: 'Nota do espaço' })
    expect(popover).toHaveAccessibleDescription('Só para conferência.')
    expect(screen.getByText('Espaço Exemplo A')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Abrir' })).toHaveAttribute('aria-expanded', 'true')
  })

  it('sem descrição não liga aria-describedby', async () => {
    renderPopover({ description: undefined })

    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))

    expect(await screen.findByRole('dialog')).not.toHaveAttribute('aria-describedby')
  })

  it('leva o foco para dentro ao abrir e o devolve ao gatilho ao fechar com Esc', async () => {
    renderPopover()
    const trigger = screen.getByRole('button', { name: 'Abrir' })

    await userEvent.click(trigger)
    const popover = await screen.findByRole('dialog')
    expect(popover.contains(document.activeElement)).toBe(true)

    await userEvent.keyboard('{Escape}')
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(trigger).toHaveFocus()
  })

  it('tem o botão Fechar, com nome, que fecha o cartão', async () => {
    renderPopover()
    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))

    await userEvent.click(await screen.findByRole('button', { name: 'Fechar' }))

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('fecha ao clicar fora, sem escurecer nem travar a página', async () => {
    render(
      <>
        <button type="button">Fora</button>
        <Popover>
          <PopoverTrigger asChild>
            <Button>Abrir</Button>
          </PopoverTrigger>
          <PopoverContent title="Nota do espaço" />
        </Popover>
      </>,
    )
    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))
    await screen.findByRole('dialog')

    // Não é modal: o resto da página continua acessível enquanto o cartão está aberto.
    expect(screen.getByRole('button', { name: 'Fora' })).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Fora' }))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })
})
