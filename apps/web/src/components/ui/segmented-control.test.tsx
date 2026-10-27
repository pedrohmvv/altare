import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { SegmentedControl, type SegmentedControlProps } from './segmented-control'

const OPTIONS = [
  { value: 'casal', label: 'Casal' },
  { value: 'minha', label: 'Minha visão' },
  { value: 'outra', label: 'Outra', disabled: true },
]

const renderControl = (props: Partial<SegmentedControlProps> = {}) =>
  render(<SegmentedControl aria-label="Lente de visão" options={OPTIONS} {...props} />)

describe('SegmentedControl', () => {
  it('é um grupo de opções exclusivas, nomeado, com um item por segmento', () => {
    renderControl({ defaultValue: 'casal' })

    expect(screen.getByRole('radiogroup', { name: 'Lente de visão' })).toBeInTheDocument()
    expect(screen.getAllByRole('radio')).toHaveLength(3)
  })

  it('marca a opção inicial como selecionada', () => {
    renderControl({ defaultValue: 'minha' })

    expect(screen.getByRole('radio', { name: 'Minha visão' })).toBeChecked()
    expect(screen.getByRole('radio', { name: 'Casal' })).not.toBeChecked()
  })

  it('troca de opção ao clicar e avisa o novo valor', async () => {
    const onValueChange = vi.fn()
    renderControl({ defaultValue: 'casal', onValueChange })

    await userEvent.click(screen.getByRole('radio', { name: 'Minha visão' }))

    expect(screen.getByRole('radio', { name: 'Minha visão' })).toBeChecked()
    expect(onValueChange).toHaveBeenCalledWith('minha')
  })

  it('clicar na opção já selecionada não a desmarca', async () => {
    const onValueChange = vi.fn()
    renderControl({ defaultValue: 'casal', onValueChange })

    await userEvent.click(screen.getByRole('radio', { name: 'Casal' }))

    expect(screen.getByRole('radio', { name: 'Casal' })).toBeChecked()
    expect(onValueChange).not.toHaveBeenCalled()
  })

  it('funciona controlado: só muda quando o valor muda', async () => {
    const onValueChange = vi.fn()
    const { rerender } = renderControl({ value: 'casal', onValueChange })

    await userEvent.click(screen.getByRole('radio', { name: 'Minha visão' }))
    expect(onValueChange).toHaveBeenCalledWith('minha')
    expect(screen.getByRole('radio', { name: 'Casal' })).toBeChecked()

    rerender(
      <SegmentedControl
        aria-label="Lente de visão"
        options={OPTIONS}
        value="minha"
        onValueChange={onValueChange}
      />,
    )
    expect(screen.getByRole('radio', { name: 'Minha visão' })).toBeChecked()
  })

  it('navega pelo teclado: Tab entra no selecionado, seta move o foco e Espaço escolhe', async () => {
    const onValueChange = vi.fn()
    renderControl({ defaultValue: 'casal', onValueChange })

    await userEvent.tab()
    expect(screen.getByRole('radio', { name: 'Casal' })).toHaveFocus()

    await userEvent.keyboard('{ArrowRight}')
    expect(screen.getByRole('radio', { name: 'Minha visão' })).toHaveFocus()

    await userEvent.keyboard(' ')
    expect(onValueChange).toHaveBeenCalledWith('minha')
  })

  it('não escolhe uma opção desabilitada', async () => {
    const onValueChange = vi.fn()
    renderControl({ defaultValue: 'casal', onValueChange })

    await userEvent.click(screen.getByRole('radio', { name: 'Outra' }))

    expect(screen.getByRole('radio', { name: 'Outra' })).toBeDisabled()
    expect(onValueChange).not.toHaveBeenCalled()
  })
})
