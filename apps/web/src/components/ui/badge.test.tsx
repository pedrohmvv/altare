import { render, screen } from '@testing-library/react'
import { BadgeCheck, CircleAlert } from 'lucide-react'
import { describe, expect, it } from 'vitest'
import { Badge } from './badge'

describe('Badge', () => {
  it('mostra o texto completo do estado', () => {
    render(<Badge>Aguardando avaliação da Noiva</Badge>)

    expect(screen.getByText('Aguardando avaliação da Noiva')).toBeVisible()
  })

  it('acompanha o texto de um ícone decorativo, que o leitor de tela ignora', () => {
    const { container } = render(
      <Badge variant="consensus" icon={<BadgeCheck />}>
        Consenso favorito
      </Badge>,
    )

    expect(screen.getByText('Consenso favorito')).toBeVisible()
    expect(container.querySelector('svg')).toBeInTheDocument()
    expect(container.querySelector('[aria-hidden="true"] svg')).toBeInTheDocument()
  })

  it('exige ícone nas variantes de consenso e de atenção (verificado pelo tsc)', () => {
    const ok = (
      <Badge variant="attention" icon={<CircleAlert />}>
        1 extra pendente
      </Badge>
    )
    // @ts-expect-error variante semântica sem ícone não compila: cor nunca é o único sinal
    const semIcone = <Badge variant="attention">1 extra pendente</Badge>

    expect([ok, semIcone]).toHaveLength(2)
  })

  it('aceita as variantes neutra, primária e de contorno sem ícone', () => {
    render(
      <>
        <Badge>Neutro</Badge>
        <Badge variant="primary">Primário</Badge>
        <Badge variant="outline">Contorno</Badge>
      </>,
    )

    expect(screen.getAllByText(/Neutro|Primário|Contorno/)).toHaveLength(3)
  })

  it('repassa className e atributos do span', () => {
    render(
      <Badge className="ml-2" title="Selo">
        Selo
      </Badge>,
    )

    expect(screen.getByText('Selo')).toHaveClass('ml-2')
    expect(screen.getByText('Selo')).toHaveAttribute('title', 'Selo')
  })
})
