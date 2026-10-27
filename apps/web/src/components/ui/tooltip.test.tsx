import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Trash2 } from 'lucide-react'
import { describe, expect, it } from 'vitest'
import { Button } from './button'
import { Tooltip } from './tooltip'

const renderTooltip = () =>
  render(
    <Tooltip content="Mover para a lixeira" delayDuration={0}>
      <Button size="icon" aria-label="Excluir fornecedor">
        <Trash2 aria-hidden />
      </Button>
    </Tooltip>,
  )

describe('Tooltip', () => {
  it('começa escondido e o gatilho segue com o próprio nome acessível', () => {
    renderTooltip()

    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Excluir fornecedor' })).toBeInTheDocument()
  })

  it('aparece ao passar o mouse e descreve o gatilho', async () => {
    renderTooltip()
    const button = screen.getByRole('button', { name: 'Excluir fornecedor' })

    await userEvent.hover(button)

    expect(await screen.findByRole('tooltip')).toHaveTextContent('Mover para a lixeira')
    expect(button).toHaveAccessibleDescription('Mover para a lixeira')
  })

  it('aparece com o foco do teclado', async () => {
    renderTooltip()

    await userEvent.tab()

    expect(await screen.findByRole('tooltip')).toHaveTextContent('Mover para a lixeira')
  })

  it('some com a tecla Esc', async () => {
    renderTooltip()
    await userEvent.tab()
    await screen.findByRole('tooltip')

    await userEvent.keyboard('{Escape}')

    await waitFor(() => expect(screen.queryByRole('tooltip')).not.toBeInTheDocument())
  })

  it('some ao tirar o mouse', async () => {
    renderTooltip()
    const button = screen.getByRole('button', { name: 'Excluir fornecedor' })
    await userEvent.hover(button)
    await screen.findByRole('tooltip')

    await userEvent.unhover(button)
    // A área de tolerância do Radix é geométrica: afasta o ponteiro para fora dela.
    await userEvent.pointer({ target: document.body, coords: { clientX: 800, clientY: 800 } })

    await waitFor(() => expect(screen.queryByRole('tooltip')).not.toBeInTheDocument())
  })
})
