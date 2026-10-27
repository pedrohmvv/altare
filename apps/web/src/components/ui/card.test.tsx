import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { Card } from './card'

describe('Card', () => {
  it('agrupa o conteúdo sem criar um papel próprio', () => {
    render(
      <Card>
        <h2>Espaço Exemplo A</h2>
      </Card>,
    )

    expect(screen.getByRole('heading', { name: 'Espaço Exemplo A' })).toBeVisible()
    expect(screen.queryByRole('article')).not.toBeInTheDocument()
  })

  it('com asChild entrega o estilo a um link, focável pelo teclado', async () => {
    render(
      <Card variant="interactive" asChild>
        <a href="/possibilidades/espaco-a">Espaço Exemplo A</a>
      </Card>,
    )

    await userEvent.tab()

    expect(screen.getByRole('link', { name: 'Espaço Exemplo A' })).toHaveFocus()
  })

  it('repassa className e atributos do elemento', () => {
    render(
      <Card variant="muted" className="mt-4" data-testid="cartao">
        Resumo
      </Card>,
    )

    expect(screen.getByTestId('cartao')).toHaveClass('mt-4')
  })
})
