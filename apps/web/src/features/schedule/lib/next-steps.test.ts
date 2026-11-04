import { describe, expect, it } from 'vitest'
import { FID, ID, milestone, SCHEDULE, scheduleForFilters, task } from '@/test/schedule-fixtures'

/** Só avulsas: sem os marcos de exemplo, que também são de Ambos e Destravados. */
const scheduleWithTasks = (tasks: ReturnType<typeof task>[]) => ({
  ...SCHEDULE,
  phases: [],
  tasks,
})

import { nextSteps } from './next-steps'

describe('Meus próximos passos (F-CCD-04, F-CRN-09)', () => {
  it('traz o que é do perfil ou de Ambos, Destravado ou Em andamento, e A fazer ou Em andamento', () => {
    const steps = nextSteps(scheduleForFilters(), 'Noiva')
    expect(steps.map((step) => step.id)).toEqual([
      FID.tNoivaAtrasada,
      FID.mAmbosAtrasado,
      FID.tNoivaAndamento,
    ])
  })

  it('o Noivo vê o dele e o de Ambos, nunca o da Noiva', () => {
    const steps = nextSteps(scheduleForFilters(), 'Noivo')
    expect(steps.map((step) => step.id).sort()).toEqual(
      [FID.mNoivo, FID.mAmbosAtrasado, FID.tNoivo].sort(),
    )
  })

  it('deixa fora o Bloqueado, o Concluído, a Concluída e o arquivado', () => {
    const all = nextSteps(scheduleForFilters(), 'Noiva').map((step) => step.id)
    for (const out of [FID.mNoiva, FID.mNoivaConcluido, FID.mNoivaArquivado, FID.tAmbosConcluida]) {
      expect(all).not.toContain(out)
    }
  })

  it('diz o tipo, o prazo, a contagem e o atraso como o servidor os deu', () => {
    const first = nextSteps(scheduleForFilters(), 'Noiva').find(
      (step) => step.id === FID.mAmbosAtrasado,
    )
    expect(first).toEqual({
      kind: 'milestone',
      id: FID.mAmbosAtrasado,
      title: 'Marco Exemplo de Ambos Atrasado',
      responsible: 'Ambos',
      dueDate: '2020-02-01',
      daysLeft: -5,
      overdue: true,
    })
  })

  it('ordena: atrasados primeiro (o mais atrasado antes), depois o prazo crescente, depois sem prazo', () => {
    const steps = nextSteps(
      scheduleWithTasks([
        task({ id: ID.avulsaUm, title: 'Sem prazo', responsible: 'Noiva' }),
        task({
          id: ID.avulsaDois,
          title: 'Prazo longe',
          responsible: 'Noiva',
          target_date: '2027-09-01',
          days_left: 300,
        }),
        task({
          id: ID.avulsaNova,
          title: 'Prazo perto',
          responsible: 'Noiva',
          target_date: '2027-01-01',
          days_left: 30,
        }),
        task({
          id: FID.tNoivo,
          title: 'Atrasada pouco',
          responsible: 'Noiva',
          target_date: '2026-10-30',
          days_left: -2,
          overdue: true,
        }),
        task({
          id: FID.tNoivaAtrasada,
          title: 'Atrasada muito',
          responsible: 'Noiva',
          target_date: '2026-09-01',
          days_left: -60,
          overdue: true,
        }),
      ]),
      'Noiva',
    )
    expect(steps.map((step) => step.title)).toEqual([
      'Atrasada muito',
      'Atrasada pouco',
      'Prazo perto',
      'Prazo longe',
      'Sem prazo',
    ])
  })

  it('o prazo do marco é o efetivo (a janela), e o da avulsa é o dela', () => {
    const base = scheduleWithTasks([
      task({
        id: ID.avulsaUm,
        title: 'Avulsa com prazo',
        responsible: 'Noiva',
        target_date: '2027-02-01',
        days_left: 10,
      }),
    ])
    const schedule = {
      ...base,
      phases: [
        {
          ...(scheduleForFilters().phases[0] as (typeof SCHEDULE.phases)[number]),
          milestones: [
            milestone({
              id: ID.destravado,
              title: 'Marco com janela',
              responsible: 'Noiva',
              state: 'Destravado',
              effective_target: '2027-01-10',
              days_left: 5,
            }),
          ],
        },
      ],
    }
    expect(nextSteps(schedule, 'Noiva').map((step) => step.title)).toEqual([
      'Marco com janela',
      'Avulsa com prazo',
    ])
  })

  it('desempata por título (pt-BR) e depois por id', () => {
    const steps = nextSteps(
      scheduleWithTasks([
        task({ id: ID.avulsaDois, title: 'Árvore', responsible: 'Ambos' }),
        task({ id: ID.avulsaUm, title: 'Zebra', responsible: 'Ambos' }),
        task({ id: ID.avulsaNova, title: 'Beta', responsible: 'Ambos' }),
        task({ id: FID.tNoivo, title: 'Beta', responsible: 'Ambos' }),
      ]),
      'Noiva',
    )
    expect(steps.map((step) => step.title)).toEqual(['Árvore', 'Beta', 'Beta', 'Zebra'])
    const betas = steps.filter((step) => step.title === 'Beta').map((step) => step.id)
    expect(betas).toEqual([...betas].sort())
  })
})
