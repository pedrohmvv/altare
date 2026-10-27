import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Button } from './button'
import { EmptyState } from './empty-state'

describe('EmptyState', () => {
  it('tem o título como h2 por padrão e aceita outro nível', () => {
    const { rerender } = render(<EmptyState title="Ainda sem fornecedores" />)
    expect(screen.getByRole('heading', { level: 2, name: 'Ainda sem fornecedores' })).toBeVisible()

    rerender(<EmptyState title="Ainda sem fornecedores" headingLevel={3} />)
    expect(screen.getByRole('heading', { level: 3, name: 'Ainda sem fornecedores' })).toBeVisible()
  })

  it('mostra a descrição acolhedora e a ação', () => {
    render(
      <EmptyState
        title="Ainda sem fornecedores"
        description="Que tal adicionar o primeiro contato?"
        action={<Button>Adicionar contato</Button>}
      />,
    )

    expect(screen.getByText('Que tal adicionar o primeiro contato?')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Adicionar contato' })).toBeVisible()
  })

  it('usa o ramo por padrão e o arco quando pedido, sempre como ornamento decorativo', () => {
    const { container, rerender } = render(<EmptyState title="Nada por aqui" />)
    const ramo = container.querySelector('img')
    expect(ramo).toHaveAttribute('src', '/brand/ornamentos/ramo-pequeno.svg')
    expect(ramo).toHaveAttribute('alt', '')

    rerender(<EmptyState title="Nada por aqui" illustration="arco" />)
    expect(container.querySelector('img')).toHaveAttribute(
      'src',
      '/brand/ornamentos/arco-simples.svg',
    )
  })

  // Guia, pág. 31: o ramo grande é o da tela de login e do 404.
  it('usa o ramo grande quando pedido, para a página não encontrada', () => {
    const { container } = render(<EmptyState title="Nada por aqui" illustration="ramo-grande" />)

    expect(container.querySelector('img')).toHaveAttribute(
      'src',
      '/brand/ornamentos/ramo-grande.svg',
    )
  })

  it('não expõe o ornamento como imagem ao leitor de tela', () => {
    render(<EmptyState title="Nada por aqui" />)

    expect(screen.queryByRole('img')).not.toBeInTheDocument()
  })
})
