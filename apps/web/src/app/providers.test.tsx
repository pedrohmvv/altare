import { render, screen } from '@testing-library/react'
import { Plus } from 'lucide-react'
import { describe, expect, it } from 'vitest'
import { Providers } from './providers'

// Guia, pág. 33: traço de 1,5 px em qualquer tamanho. Os ícones são dimensionados por classes
// (`size-5`), então só o traço que não escala (`vector-effect`) garante 1,5 px de tela (D-054).
describe('Providers', () => {
  it('desenha todo ícone Lucide com traço de 1,5 px', () => {
    render(
      <Providers>
        <Plus aria-label="Adicionar" />
      </Providers>,
    )
    expect(screen.getByLabelText('Adicionar')).toHaveAttribute('stroke-width', '1.5')
  })

  it('mantém o traço do mesmo tamanho ao redimensionar o ícone', () => {
    render(
      <Providers>
        <Plus aria-label="Adicionar" className="size-5" />
      </Providers>,
    )
    const strokes = [...screen.getByLabelText('Adicionar').querySelectorAll('path')]
    expect(strokes.length).toBeGreaterThan(0)
    for (const stroke of strokes) {
      expect(stroke).toHaveAttribute('vector-effect', 'non-scaling-stroke')
    }
  })
})
