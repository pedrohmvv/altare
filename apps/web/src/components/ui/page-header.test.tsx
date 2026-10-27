import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Button } from './button'
import { PageHeader } from './page-header'

describe('PageHeader', () => {
  it('tem o título da página como o único h1', () => {
    render(<PageHeader title="Possibilidades de espaço" />)

    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1)
    expect(
      screen.getByRole('heading', { level: 1, name: 'Possibilidades de espaço' }),
    ).toBeVisible()
  })

  it('mostra o rótulo acima e a linha de apoio abaixo do título', () => {
    render(
      <PageHeader
        eyebrow="Possibilidades · Espaço"
        title="Possibilidades de espaço"
        description="Comparem os espaços lado a lado."
      />,
    )

    expect(screen.getByText('Possibilidades · Espaço')).toBeVisible()
    expect(screen.getByText('Comparem os espaços lado a lado.')).toBeVisible()
  })

  it('põe as ações ao lado do título', () => {
    render(<PageHeader title="Contatos" actions={<Button>Novo contato</Button>} />)

    expect(screen.getByRole('button', { name: 'Novo contato' })).toBeVisible()
  })

  it('funciona só com o título', () => {
    render(<PageHeader title="Visão geral" />)

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Visão geral' })).toBeVisible()
  })
})
