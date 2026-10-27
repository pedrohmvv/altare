import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { Textarea } from './textarea'

describe('Textarea', () => {
  it('tem o rótulo acima e aceita várias linhas', async () => {
    render(<Textarea label="Observações" rows={4} />)

    await userEvent.type(screen.getByLabelText('Observações'), 'Primeira{enter}Segunda')

    expect(screen.getByLabelText('Observações')).toHaveValue('Primeira\nSegunda')
    expect(screen.getByLabelText('Observações')).toHaveAttribute('rows', '4')
  })

  it('descreve a ajuda e o erro juntos', () => {
    render(
      <Textarea
        label="Observações"
        hint="Só vocês veem isto"
        error="Escreva ao menos uma frase."
      />,
    )

    expect(screen.getByLabelText('Observações')).toBeInvalid()
    expect(screen.getByLabelText('Observações')).toHaveAccessibleDescription(
      'Só vocês veem isto Escreva ao menos uma frase.',
    )
  })

  it('escreve a obrigatoriedade no rótulo', () => {
    render(<Textarea label="Observações" required />)

    expect(screen.getByRole('textbox', { name: 'Observações (obrigatório)' })).toBeRequired()
  })

  it('não aceita digitação quando desabilitado', async () => {
    render(<Textarea label="Observações" disabled />)

    await userEvent.type(screen.getByLabelText('Observações'), 'x')

    expect(screen.getByLabelText('Observações')).toHaveValue('')
  })
})
