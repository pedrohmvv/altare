import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Select } from './select'

const renderSelect = (props: Partial<Parameters<typeof Select>[0]> = {}) =>
  render(
    <Select label="Categoria" {...props}>
      <option value="espaco">Espaço</option>
      <option value="buffet">Buffet</option>
    </Select>,
  )

describe('Select', () => {
  it('tem o rótulo acima e é um combobox nativo', () => {
    renderSelect()

    expect(screen.getByRole('combobox', { name: 'Categoria' })).toBeInTheDocument()
  })

  it('troca de opção pelo teclado e pelo mouse', async () => {
    const onChange = vi.fn()
    renderSelect({ onChange })

    await userEvent.selectOptions(screen.getByLabelText('Categoria'), 'buffet')

    expect(screen.getByLabelText('Categoria')).toHaveValue('buffet')
    expect(onChange).toHaveBeenCalledOnce()
  })

  it('começa no placeholder, que não pode ser escolhido de volta', async () => {
    renderSelect({ placeholder: 'Escolha uma categoria' })

    expect(screen.getByLabelText('Categoria')).toHaveValue('')
    expect(screen.getByRole('option', { name: 'Escolha uma categoria' })).toBeDisabled()
  })

  it('respeita o valor inicial mesmo com placeholder', () => {
    renderSelect({ placeholder: 'Escolha uma categoria', defaultValue: 'buffet' })

    expect(screen.getByLabelText('Categoria')).toHaveValue('buffet')
  })

  it('com erro fica inválido e descreve o motivo', () => {
    renderSelect({ error: 'Escolha uma categoria.' })

    expect(screen.getByLabelText('Categoria')).toBeInvalid()
    expect(screen.getByLabelText('Categoria')).toHaveAccessibleDescription('Escolha uma categoria.')
  })

  it('escreve a obrigatoriedade no rótulo e respeita o desabilitado', () => {
    renderSelect({ required: true, disabled: true })

    expect(screen.getByRole('combobox', { name: 'Categoria (obrigatório)' })).toBeDisabled()
  })
})
