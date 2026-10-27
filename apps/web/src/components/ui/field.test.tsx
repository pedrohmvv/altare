import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Field } from './field'

const renderField = (props: Partial<Parameters<typeof Field>[0]> = {}) =>
  render(
    <Field label="Nome do espaço" {...props}>
      {(control) => <input {...control} />}
    </Field>,
  )

describe('Field', () => {
  it('liga o rótulo visível ao controle', () => {
    renderField()

    expect(screen.getByLabelText('Nome do espaço')).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: 'Nome do espaço' })).toBeInTheDocument()
  })

  it('descreve o controle pela ajuda', () => {
    renderField({ hint: 'Como aparece nas listas' })

    expect(screen.getByRole('textbox')).toHaveAccessibleDescription('Como aparece nas listas')
  })

  it('sem erro não marca o controle como inválido', () => {
    renderField()

    expect(screen.getByRole('textbox')).not.toHaveAttribute('aria-invalid')
  })

  it('com erro marca o controle como inválido e descreve o erro em texto', () => {
    renderField({ error: 'Informe o nome do espaço.' })

    expect(screen.getByRole('textbox')).toBeInvalid()
    expect(screen.getByRole('textbox')).toHaveAccessibleDescription('Informe o nome do espaço.')
    expect(screen.getByText('Informe o nome do espaço.')).toBeVisible()
  })

  it('descreve ajuda e erro juntos, nessa ordem', () => {
    renderField({ hint: 'Como aparece nas listas', error: 'Informe o nome do espaço.' })

    expect(screen.getByRole('textbox')).toHaveAccessibleDescription(
      'Como aparece nas listas Informe o nome do espaço.',
    )
  })

  it('escreve a obrigatoriedade no rótulo em vez de usar asterisco', () => {
    renderField({ required: true })

    expect(screen.getByRole('textbox', { name: 'Nome do espaço (obrigatório)' })).toBeRequired()
  })

  it('usa o id informado quando há um', () => {
    renderField({ id: 'espaco' })

    expect(screen.getByRole('textbox')).toHaveAttribute('id', 'espaco')
  })
})
