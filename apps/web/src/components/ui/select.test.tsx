import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Select, type SelectProps } from './select'

const OPTIONS = [
  { value: 'espaco', label: 'Espaço' },
  { value: 'buffet', label: 'Buffet' },
  { value: 'foto', label: 'Fotografia', disabled: true },
]

const renderSelect = (props: Partial<SelectProps> = {}) =>
  render(<Select label="Categoria" options={OPTIONS} {...props} />)

describe('Select', () => {
  it('tem o rótulo acima e é um combobox', () => {
    renderSelect()

    expect(screen.getByRole('combobox', { name: 'Categoria' })).toBeInTheDocument()
  })

  it('mostra o placeholder enquanto nada foi escolhido', () => {
    renderSelect({ placeholder: 'Escolha uma categoria' })

    expect(screen.getByRole('combobox', { name: 'Categoria' })).toHaveTextContent(
      'Escolha uma categoria',
    )
  })

  it('abre a lista própria do app com as opções ao clicar', async () => {
    renderSelect()

    await userEvent.click(screen.getByRole('combobox', { name: 'Categoria' }))

    expect(screen.getByRole('listbox')).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Espaço' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Buffet' })).toBeInTheDocument()
  })

  it('escolhe uma opção com o mouse, fecha a lista e avisa o valor', async () => {
    const onValueChange = vi.fn()
    renderSelect({ onValueChange })

    await userEvent.click(screen.getByRole('combobox', { name: 'Categoria' }))
    await userEvent.click(screen.getByRole('option', { name: 'Buffet' }))

    expect(onValueChange).toHaveBeenCalledWith('buffet')
    expect(screen.getByRole('combobox', { name: 'Categoria' })).toHaveTextContent('Buffet')
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })

  it('escolhe pelo teclado: Enter abre, setas navegam, Enter escolhe', async () => {
    const onValueChange = vi.fn()
    renderSelect({ onValueChange })

    await userEvent.tab()
    await userEvent.keyboard('{Enter}')
    await userEvent.keyboard('{ArrowDown}{Enter}')

    expect(onValueChange).toHaveBeenCalledWith('buffet')
  })

  it('fecha a lista com Esc sem mudar o valor', async () => {
    const onValueChange = vi.fn()
    renderSelect({ onValueChange })

    await userEvent.click(screen.getByRole('combobox', { name: 'Categoria' }))
    await userEvent.keyboard('{Escape}')

    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
    expect(onValueChange).not.toHaveBeenCalled()
  })

  it('não deixa escolher uma opção desabilitada', async () => {
    renderSelect()

    await userEvent.click(screen.getByRole('combobox', { name: 'Categoria' }))

    expect(screen.getByRole('option', { name: 'Fotografia' })).toHaveAttribute(
      'aria-disabled',
      'true',
    )
  })

  it('mostra o rótulo da opção do valor inicial', () => {
    renderSelect({ defaultValue: 'buffet' })

    expect(screen.getByRole('combobox', { name: 'Categoria' })).toHaveTextContent('Buffet')
  })

  it('com erro fica inválido e descreve o motivo', () => {
    renderSelect({ error: 'Escolha uma categoria.' })

    expect(screen.getByRole('combobox', { name: 'Categoria' })).toBeInvalid()
    expect(screen.getByRole('combobox', { name: 'Categoria' })).toHaveAccessibleDescription(
      'Escolha uma categoria.',
    )
  })

  it('escreve a obrigatoriedade no rótulo e respeita o desabilitado', () => {
    renderSelect({ required: true, disabled: true })

    expect(screen.getByRole('combobox', { name: 'Categoria (obrigatório)' })).toBeDisabled()
  })
})
