import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Checkbox } from './checkbox'

describe('Checkbox', () => {
  it('é um checkbox com o nome do rótulo', () => {
    render(<Checkbox label="Incluir bebidas" />)

    expect(screen.getByRole('checkbox', { name: 'Incluir bebidas' })).not.toBeChecked()
  })

  it('alterna ao clicar no controle e avisa o novo estado', async () => {
    const onCheckedChange = vi.fn()
    render(<Checkbox label="Incluir bebidas" onCheckedChange={onCheckedChange} />)

    await userEvent.click(screen.getByRole('checkbox', { name: 'Incluir bebidas' }))

    expect(screen.getByRole('checkbox', { name: 'Incluir bebidas' })).toBeChecked()
    expect(onCheckedChange).toHaveBeenCalledWith(true)
  })

  it('alterna ao clicar no rótulo', async () => {
    render(<Checkbox label="Incluir bebidas" />)

    await userEvent.click(screen.getByText('Incluir bebidas'))

    expect(screen.getByRole('checkbox', { name: 'Incluir bebidas' })).toBeChecked()
  })

  it('alterna com a tecla Espaço', async () => {
    render(<Checkbox label="Incluir bebidas" />)

    await userEvent.tab()
    await userEvent.keyboard(' ')

    expect(screen.getByRole('checkbox', { name: 'Incluir bebidas' })).toBeChecked()
  })

  it('anuncia o estado indeterminado como misto', () => {
    render(<Checkbox label="Todos os convidados" checked="indeterminate" />)

    expect(screen.getByRole('checkbox', { name: 'Todos os convidados' })).toBePartiallyChecked()
  })

  it('não alterna quando desabilitado', async () => {
    const onCheckedChange = vi.fn()
    render(<Checkbox label="Incluir bebidas" disabled onCheckedChange={onCheckedChange} />)

    await userEvent.click(screen.getByText('Incluir bebidas'))

    expect(screen.getByRole('checkbox', { name: 'Incluir bebidas' })).toBeDisabled()
    expect(onCheckedChange).not.toHaveBeenCalled()
  })

  it('respeita o estado inicial marcado', () => {
    render(<Checkbox label="Incluir bebidas" defaultChecked />)

    expect(screen.getByRole('checkbox', { name: 'Incluir bebidas' })).toBeChecked()
  })
})
