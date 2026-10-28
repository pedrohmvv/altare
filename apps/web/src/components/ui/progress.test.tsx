import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Progress } from './progress'

describe('Progress', () => {
  it('é uma barra de progresso com o texto visível como nome e os valores', () => {
    render(<Progress value={3} max={18} label="3 de 18 categorias classificadas" />)

    const barra = screen.getByRole('progressbar', { name: '3 de 18 categorias classificadas' })
    expect(barra).toHaveAttribute('aria-valuenow', '3')
    expect(barra).toHaveAttribute('aria-valuemax', '18')
    expect(screen.getByText('3 de 18 categorias classificadas')).toBeVisible()
  })

  it('preenche a proporção do total', () => {
    render(<Progress value={1} max={4} label="1 de 4" />)
    expect(screen.getByRole('progressbar').firstElementChild).toHaveStyle({ width: '25%' })
  })

  it('sem nada a medir fica vazia, sem divisão por zero', () => {
    render(<Progress value={0} max={0} label="0 de 0" />)
    expect(screen.getByRole('progressbar').firstElementChild).toHaveStyle({ width: '0%' })
  })

  it('nunca passa de 100% nem fica abaixo de 0%', () => {
    const { rerender } = render(<Progress value={9} max={4} label="x" />)
    expect(screen.getByRole('progressbar').firstElementChild).toHaveStyle({ width: '100%' })
    rerender(<Progress value={-3} max={4} label="x" />)
    expect(screen.getByRole('progressbar').firstElementChild).toHaveStyle({ width: '0%' })
  })
})
