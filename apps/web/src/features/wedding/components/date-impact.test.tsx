import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { DateImpactChange, DateImpact as DateImpactData } from '../api/use-date-impact'
import { DateImpact } from './date-impact'

const change = (n: number, over: Partial<DateImpactChange> = {}): DateImpactChange => ({
  id: `00000000-0000-4000-8000-00000000000${n}`,
  title: `Marco Exemplo ${n}`,
  window_before: { start: '2026-04-12', end: '2026-08-12' },
  window_after: { start: '2026-05-12', end: '2026-09-12' },
  target_before: '2026-08-12',
  target_after: '2026-09-12',
  ...over,
})

const impact = (over: Partial<DateImpactData> = {}): DateImpactData => ({
  mode_before: 'com_data',
  mode_after: 'com_data',
  changes: [change(1), change(2)],
  manual_kept: 0,
  newly_overdue: 0,
  ...over,
})

const FAILED =
  'Não conseguimos calcular agora o que muda no cronograma. Ao confirmar, as janelas são recalculadas.'

function show(data: DateImpactData | undefined, failed = false) {
  render(<DateImpact data={data} failed={failed} />)
}

describe('prévia ao mudar a data: o resumo (F-CRN-05, regra 4)', () => {
  it('carregando, diz o que faz numa região de status', () => {
    show(undefined)

    expect(screen.getByRole('status')).toHaveTextContent('Calculando o que muda no cronograma…')
  })

  it('com erro na prévia, diz com honestidade que não calculou e que a confirmação recalcula', () => {
    show(undefined, true)

    expect(screen.getByText(FAILED)).toBeVisible()
    expect(screen.queryByText('A data recalcula as janelas do cronograma.')).not.toBeInTheDocument()
    expect(screen.queryByText(/Calculando/)).not.toBeInTheDocument()
  })

  it('com data e com data: "N marcos mudam de janela"', () => {
    show(impact({ changes: [change(1), change(2), change(3)] }))

    expect(screen.getByText('3 marcos mudam de janela.')).toBeVisible()
  })

  it('com um só marco, usa o singular', () => {
    show(impact({ changes: [change(1)] }))

    expect(screen.getByText('1 marco muda de janela.')).toBeVisible()
  })

  it('sem data para com data: "N marcos ganham janela calculada"', () => {
    show(impact({ mode_before: 'sem_data', changes: [change(1, { window_before: null })] }))
    expect(screen.getByText('1 marco ganha janela calculada.')).toBeVisible()
  })

  it('sem data para com data, no plural', () => {
    show(
      impact({
        mode_before: 'sem_data',
        changes: [change(1, { window_before: null }), change(2, { window_before: null })],
      }),
    )
    expect(screen.getByText('2 marcos ganham janela calculada.')).toBeVisible()
  })

  it('com data para sem data: perdem a janela e os prazos de vocês ficam', () => {
    show(
      impact({
        mode_after: 'sem_data',
        changes: [change(1, { window_after: null }), change(2, { window_after: null })],
      }),
    )

    expect(screen.getByText('2 marcos perdem a janela calculada.')).toBeVisible()
  })

  it('com data para sem data, com um marco, usa o singular', () => {
    show(impact({ mode_after: 'sem_data', changes: [change(1, { window_after: null })] }))

    expect(screen.getByText('1 marco perde a janela calculada.')).toBeVisible()
  })

  it('nada muda: "Nenhum marco muda de janela."', () => {
    show(impact({ changes: [] }))

    expect(screen.getByText('Nenhum marco muda de janela.')).toBeVisible()
    expect(screen.queryByRole('list')).not.toBeInTheDocument()
  })
})

describe('prévia ao mudar a data: prazos manuais e atrasos', () => {
  it('diz quantos marcos com prazo definido por vocês não mudam, quando há mudanças', () => {
    show(impact({ manual_kept: 3 }))
    expect(screen.getByText('3 marcos com prazo definido por vocês não mudam.')).toBeVisible()
  })

  it('com um marco, usa o singular', () => {
    show(impact({ manual_kept: 1 }))
    expect(screen.getByText('1 marco com prazo definido por vocês não muda.')).toBeVisible()
  })

  it('diz também quando o modo muda, ainda que nenhuma janela mude', () => {
    show(impact({ mode_before: 'sem_data', changes: [], manual_kept: 2 }))
    expect(screen.getByText('2 marcos com prazo definido por vocês não mudam.')).toBeVisible()
  })

  it('com a mesma data e nada a mudar, não repete os prazos manuais', () => {
    show(impact({ changes: [], manual_kept: 4 }))

    expect(screen.getByText('Nenhum marco muda de janela.')).toBeVisible()
    expect(screen.queryByText(/prazo definido por vocês não/)).not.toBeInTheDocument()
  })

  it('sem prazos manuais, não fala deles', () => {
    show(impact({ manual_kept: 0 }))
    expect(screen.queryByText(/prazo definido por vocês/)).not.toBeInTheDocument()
  })

  it('diz quantos marcos passam a aparecer como Atrasado, no plural e no singular', () => {
    const { unmount } = render(<DateImpact data={impact({ newly_overdue: 2 })} failed={false} />)
    expect(screen.getByText('2 marcos passam a aparecer como Atrasado.')).toBeVisible()
    unmount()

    render(<DateImpact data={impact({ newly_overdue: 1 })} failed={false} />)
    expect(screen.getByText('1 marco passa a aparecer como Atrasado.')).toBeVisible()
  })

  it('sem atrasos novos, não fala de atraso', () => {
    show(impact({ newly_overdue: 0 }))
    expect(screen.queryByText(/Atrasado/)).not.toBeInTheDocument()
  })
})

describe('prévia ao mudar a data: a lista dos marcos', () => {
  it('mostra o título e a janela antes e depois em dd/mm/aaaa', () => {
    show(impact({ changes: [change(1)] }))
    const lista = screen.getByRole('list', { name: 'Marcos que mudam de janela' })
    const item = within(within(lista).getByRole('listitem'))

    expect(item.getByText('Marco Exemplo 1')).toBeVisible()
    expect(item.getByText('12/04/2026 a 12/08/2026')).toBeVisible()
    expect(item.getByText('12/05/2026 a 12/09/2026')).toBeVisible()
  })

  it('o marco sem janela antes ou depois diz isso em palavras', () => {
    show(
      impact({
        mode_before: 'sem_data',
        changes: [change(1, { window_before: null })],
      }),
    )
    expect(screen.getByText('sem janela calculada')).toBeVisible()
  })

  it('mostra até 5 marcos e diz quantos mais há', () => {
    show(impact({ changes: [1, 2, 3, 4, 5, 6, 7].map((n) => change(n)) }))

    expect(screen.getAllByRole('listitem')).toHaveLength(5)
    expect(screen.queryByText('Marco Exemplo 6')).not.toBeInTheDocument()
    expect(screen.getByText('e mais 2 marcos')).toBeVisible()
  })

  it('com seis, diz "e mais 1 marco" no singular', () => {
    show(impact({ changes: [1, 2, 3, 4, 5, 6].map((n) => change(n)) }))

    expect(screen.getByText('e mais 1 marco')).toBeVisible()
  })

  it('com exatamente 5, não diz "e mais"', () => {
    show(impact({ changes: [1, 2, 3, 4, 5].map((n) => change(n)) }))

    expect(screen.getAllByRole('listitem')).toHaveLength(5)
    expect(screen.queryByText(/^e mais/)).not.toBeInTheDocument()
  })
})
