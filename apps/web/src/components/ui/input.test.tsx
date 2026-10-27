import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Input } from './input'

describe('Input', () => {
  it('tem o rótulo acima e aceita digitação', async () => {
    const onChange = vi.fn()
    render(<Input label="Preço base" onChange={onChange} />)

    await userEvent.type(screen.getByLabelText('Preço base'), '12500')

    expect(screen.getByLabelText('Preço base')).toHaveValue('12500')
    expect(onChange).toHaveBeenCalled()
  })

  it('mostra o prefixo e o sufixo fora do valor e os lê como descrição', async () => {
    render(<Input label="Preço base" prefix="R$" suffix="por pessoa" />)

    await userEvent.type(screen.getByLabelText('Preço base'), '90')

    expect(screen.getByText('R$')).toBeVisible()
    expect(screen.getByText('por pessoa')).toBeVisible()
    expect(screen.getByLabelText('Preço base')).toHaveValue('90')
    expect(screen.getByLabelText('Preço base')).toHaveAccessibleDescription('R$ por pessoa')
  })

  it('com erro fica inválido e descreve o motivo', () => {
    render(<Input label="Preço base" error="Informe o preço base em reais." />)

    expect(screen.getByLabelText('Preço base')).toBeInvalid()
    expect(screen.getByLabelText('Preço base')).toHaveAccessibleDescription(
      'Informe o preço base em reais.',
    )
  })

  it('não aceita digitação quando desabilitado', async () => {
    render(<Input label="Preço base" disabled />)

    await userEvent.type(screen.getByLabelText('Preço base'), '1')

    expect(screen.getByLabelText('Preço base')).toBeDisabled()
    expect(screen.getByLabelText('Preço base')).toHaveValue('')
  })

  it('repassa o tipo e o placeholder sem trocar o rótulo', () => {
    render(<Input label="Quando" type="date" placeholder="dd/mm/aaaa" />)

    expect(screen.getByLabelText('Quando')).toHaveAttribute('type', 'date')
  })
})
