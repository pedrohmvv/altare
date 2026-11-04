import { describe, expect, it } from 'vitest'
import { FID, scheduleForFilters } from '@/test/schedule-fixtures'
import {
  applyScheduleFilters,
  filtersFromSearch,
  hasActiveFilters,
  lensApplies,
} from './schedule-filters'

const schedule = scheduleForFilters()
const ids = (result: ReturnType<typeof applyScheduleFilters>) => [
  ...result.milestoneIds,
  ...result.taskIds,
]

describe('filtros do cronograma (F-CRN-09)', () => {
  it('traduz os slugs da URL para os valores da API', () => {
    expect(
      filtersFromSearch({
        responsavel: 'noiva',
        estado: 'em-andamento',
        atrasados: true,
        avulsas: true,
      }),
    ).toEqual({
      responsible: 'Noiva',
      state: 'Em andamento',
      overdueOnly: true,
      tasksOnly: true,
    })
    expect(filtersFromSearch({ estado: 'a-fazer' }).state).toBe('A fazer')
    expect(filtersFromSearch({ estado: 'concluido' }).state).toBe('Concluído')
  })

  it('sem filtro nem lente, mostra tudo o que as listas mostram, sem o arquivado', () => {
    const result = applyScheduleFilters(schedule, { filters: {} })
    expect(result.total).toBe(8)
    expect(result.shown).toBe(8)
    expect(result.narrowed).toBe(false)
    expect(ids(result)).not.toContain(FID.mNoivaArquivado)
  })

  it('o responsável filtra marcos e avulsas', () => {
    const result = applyScheduleFilters(schedule, { filters: { responsible: 'Noivo' } })
    expect(ids(result).sort()).toEqual([FID.mNoivo, FID.tNoivo].sort())
    expect(result.shown).toBe(2)
    expect(result.total).toBe(8)
    expect(result.narrowed).toBe(true)
  })

  it('Bloqueado e Destravado casam só marcos, pelo estado do servidor', () => {
    const blocked = applyScheduleFilters(schedule, { filters: { state: 'Bloqueado' } })
    expect(ids(blocked)).toEqual([FID.mNoiva])
    const unlocked = applyScheduleFilters(schedule, { filters: { state: 'Destravado' } })
    expect(ids(unlocked)).toEqual([FID.mNoivo])
  })

  it('A fazer casa só avulsas', () => {
    const result = applyScheduleFilters(schedule, { filters: { state: 'A fazer' } })
    expect(result.milestoneIds.size).toBe(0)
    expect([...result.taskIds].sort()).toEqual([FID.tNoivo, FID.tNoivaAtrasada].sort())
  })

  it('Em andamento casa marcos e avulsas', () => {
    const result = applyScheduleFilters(schedule, { filters: { state: 'Em andamento' } })
    expect([...result.milestoneIds]).toEqual([FID.mAmbosAtrasado])
    expect([...result.taskIds]).toEqual([FID.tNoivaAndamento])
  })

  it('Concluído casa o Concluído do marco e a Concluída da avulsa', () => {
    const result = applyScheduleFilters(schedule, { filters: { state: 'Concluído' } })
    expect([...result.milestoneIds]).toEqual([FID.mNoivaConcluido])
    expect([...result.taskIds]).toEqual([FID.tAmbosConcluida])
  })

  it('atrasados usa o overdue do servidor, em marcos e avulsas', () => {
    const result = applyScheduleFilters(schedule, { filters: { overdueOnly: true } })
    expect([...result.milestoneIds]).toEqual([FID.mAmbosAtrasado])
    expect([...result.taskIds]).toEqual([FID.tNoivaAtrasada])
  })

  it('só avulsas esconde todos os marcos', () => {
    const result = applyScheduleFilters(schedule, { filters: { tasksOnly: true } })
    expect(result.milestoneIds.size).toBe(0)
    expect(result.taskIds.size).toBe(4)
  })

  it('os grupos se combinam por E', () => {
    const result = applyScheduleFilters(schedule, {
      filters: { responsible: 'Noiva', overdueOnly: true },
    })
    expect(ids(result)).toEqual([FID.tNoivaAtrasada])
  })

  describe('a lente Minha visão', () => {
    it('com perfil, mostra os itens do perfil e os de Ambos', () => {
      const noiva = applyScheduleFilters(schedule, {
        filters: {},
        lens: 'minha',
        profile: 'Noiva',
      })
      expect(ids(noiva)).not.toContain(FID.mNoivo)
      expect(ids(noiva)).not.toContain(FID.tNoivo)
      expect(ids(noiva)).toContain(FID.mNoiva)
      expect(ids(noiva)).toContain(FID.mAmbosAtrasado)
      expect(ids(noiva)).toContain(FID.tAmbosConcluida)
      expect(noiva.shown).toBe(6)
      expect(noiva.total).toBe(8)
      expect(noiva.narrowed).toBe(true)

      const noivo = applyScheduleFilters(schedule, {
        filters: {},
        lens: 'minha',
        profile: 'Noivo',
      })
      expect(ids(noivo).sort()).toEqual(
        [FID.mNoivo, FID.mAmbosAtrasado, FID.tNoivo, FID.tAmbosConcluida].sort(),
      )
    })

    it('o filtro explícito de responsável vence a lente', () => {
      const context = {
        filters: { responsible: 'Noivo' as const },
        lens: 'minha' as const,
        profile: 'Noiva' as const,
      }
      expect(ids(applyScheduleFilters(schedule, context)).sort()).toEqual(
        [FID.mNoivo, FID.tNoivo].sort(),
      )
      expect(lensApplies(context)).toBe(false)
    })

    it('sem perfil, a lente não filtra', () => {
      const result = applyScheduleFilters(schedule, { filters: {}, lens: 'minha' })
      expect(result.shown).toBe(8)
      expect(result.narrowed).toBe(false)
      expect(lensApplies({ filters: {}, lens: 'minha' })).toBe(false)
    })

    it('a lente Casal mostra tudo, mesmo com perfil', () => {
      const result = applyScheduleFilters(schedule, {
        filters: {},
        lens: 'casal',
        profile: 'Noiva',
      })
      expect(result.shown).toBe(8)
      expect(lensApplies({ filters: {}, lens: 'casal', profile: 'Noiva' })).toBe(false)
    })

    it('a lente se soma aos outros filtros por E', () => {
      const result = applyScheduleFilters(schedule, {
        filters: { overdueOnly: true },
        lens: 'minha',
        profile: 'Noivo',
      })
      expect([...result.milestoneIds]).toEqual([FID.mAmbosAtrasado])
      expect(result.taskIds.size).toBe(0)
    })
  })

  it('hasActiveFilters ignora a lente e vê cada filtro', () => {
    expect(hasActiveFilters({})).toBe(false)
    expect(hasActiveFilters({ overdueOnly: false })).toBe(false)
    expect(hasActiveFilters({ tasksOnly: true })).toBe(true)
    expect(hasActiveFilters({ state: 'Bloqueado' })).toBe(true)
  })
})
