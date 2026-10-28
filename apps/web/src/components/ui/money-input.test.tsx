import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { MoneyInput } from './money-input'

function Controlled({
  initial = null,
  onChange,
}: {
  initial?: number | null
  onChange?: (c: number | null) => void
}) {
  const [value, setValue] = useState<number | null>(initial)
  return (
    <MoneyInput
      label="Teto macro"
      value={value}
      onValueChange={(cents) => {
        setValue(cents)
        onChange?.(cents)
      }}
    />
  )
}

describe('MoneyInput', () => {
  it('tem rótulo, prefixo R$ e mostra o valor em reais', () => {
    render(<Controlled initial={2_800_000} />)
    const campo = screen.getByLabelText('Teto macro')
    expect(campo).toHaveValue('28.000,00')
    expect(screen.getByText('R$')).toBeInTheDocument()
  })

  it('devolve centavos inteiros enquanto a pessoa digita', async () => {
    const onChange = vi.fn()
    render(<Controlled onChange={onChange} />)
    await userEvent.type(screen.getByLabelText('Teto macro'), '28000')
    expect(onChange).toHaveBeenLastCalledWith(2_800_000)
  })

  it('ao sair do campo, escreve o valor no formato de reais', async () => {
    render(<Controlled />)
    const campo = screen.getByLabelText('Teto macro')
    await userEvent.type(campo, '28000')
    await userEvent.tab()
    expect(campo).toHaveValue('28.000,00')
  })

  it('campo vazio vale nada (null), nunca zero', async () => {
    const onChange = vi.fn()
    render(<Controlled initial={100} onChange={onChange} />)
    await userEvent.clear(screen.getByLabelText('Teto macro'))
    expect(onChange).toHaveBeenLastCalledWith(null)
  })

  it('texto que não é valor mostra um erro acionável e não chuta um número', async () => {
    const onChange = vi.fn()
    render(<Controlled onChange={onChange} />)
    const campo = screen.getByLabelText('Teto macro')
    await userEvent.type(campo, '28.5')
    expect(onChange).toHaveBeenLastCalledWith(null)
    expect(campo).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByText(/como 28\.000,00/)).toBeInTheDocument()
  })

  it('acompanha o valor quando ele muda por fora (restaurar um formulário)', () => {
    const { rerender } = render(
      <MoneyInput label="Teto macro" value={100_00} onValueChange={() => {}} />,
    )
    expect(screen.getByLabelText('Teto macro')).toHaveValue('100,00')
    rerender(<MoneyInput label="Teto macro" value={150_000} onValueChange={() => {}} />)
    expect(screen.getByLabelText('Teto macro')).toHaveValue('1.500,00')
    rerender(<MoneyInput label="Teto macro" value={null} onValueChange={() => {}} />)
    expect(screen.getByLabelText('Teto macro')).toHaveValue('')
  })

  it('o erro de fora vence o do próprio campo', () => {
    render(
      <MoneyInput
        label="Teto macro"
        value={null}
        onValueChange={() => {}}
        error="Informe o teto."
      />,
    )
    expect(screen.getByText('Informe o teto.')).toBeInTheDocument()
  })

  it('usa teclado numérico no celular', () => {
    render(<Controlled />)
    expect(screen.getByLabelText('Teto macro')).toHaveAttribute('inputmode', 'decimal')
  })
})
