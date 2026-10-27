import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Money } from './money'

const NBSP = ' '
const MINUS = '−'

const textOf = (ui: React.ReactElement) => render(ui).container.textContent

describe('Money', () => {
  it('mostra o valor em reais a partir dos centavos', () => {
    expect(textOf(<Money cents={2_800_000} />)).toBe(`R$${NBSP}28.000`)
  })

  it('mostra os centavos quando a precisão é always', () => {
    expect(textOf(<Money cents={2_800_000} precision="always" />)).toBe(`R$${NBSP}28.000,00`)
  })

  it('mostra o sinal quando signed, com o menos tipográfico nos negativos', () => {
    expect(textOf(<Money cents={125_000} signed />)).toBe(`+${NBSP}R$${NBSP}1.250`)
    expect(textOf(<Money cents={-125_000} signed />)).toBe(`${MINUS}${NBSP}R$${NBSP}1.250`)
  })

  it('aceita className e atributos do span, como title', () => {
    const { container } = render(<Money cents={100} className="text-right" title="Preço base" />)

    expect(container.firstElementChild).toHaveClass('text-right')
    expect(container.firstElementChild).toHaveAttribute('title', 'Preço base')
  })

  it('não renderiza um valor que não seja inteiro de centavos', () => {
    expect(() => render(<Money cents={10.5} />)).toThrow(RangeError)
  })
})
