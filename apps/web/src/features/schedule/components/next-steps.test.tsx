import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse } from '@/test/fake-api'
import { GET_SCHEDULE, renderSchedule, stubWideScreen } from '@/test/render-schedule'
import { FID, scheduleForFilters, scheduleWithTasks, task } from '@/test/schedule-fixtures'

/** Uma fase só, com um marco Concluído da Noiva: nada que seja "próximo passo" de ninguém. */
const quietBase = () => {
  const full = scheduleForFilters()
  const [, second] = full.phases
  if (!second) throw new Error('A fixture de filtros tem duas fases')
  return { ...full, tasks: [], phases: [{ ...second, milestones: [] }] }
}

import type { ScheduleSearch } from '../search'

// F-CRN-09: "Meus próximos passos" (só no celular, só com perfil, sempre "eu ou Ambos").
function setup(
  schedule = scheduleForFilters(),
  search: ScheduleSearch = {},
  session: { profile?: 'Noivo' | 'Noiva'; lens?: 'casal' | 'minha' } = { profile: 'Noiva' },
) {
  return renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, schedule) }, search, session)
}

const section = async () =>
  within(await screen.findByRole('region', { name: 'Meus próximos passos' }))

describe('Meus próximos passos no celular (F-CRN-09)', () => {
  it('é uma seção com h2, uma lista e a ordem: atrasados primeiro, depois o prazo', async () => {
    setup()
    const next = await section()
    expect(next.getByRole('heading', { level: 2, name: 'Meus próximos passos' })).toBeVisible()
    const rows = next.getAllByRole('listitem')
    expect(rows).toHaveLength(3)
    expect(
      within(rows[0] as HTMLElement).getByText('Avulsa Exemplo da Noiva Atrasada'),
    ).toBeVisible()
    expect(
      within(rows[1] as HTMLElement).getByText('Marco Exemplo de Ambos Atrasado'),
    ).toBeVisible()
    expect(
      within(rows[2] as HTMLElement).getByText('Avulsa Exemplo da Noiva em Andamento'),
    ).toBeVisible()
  })

  it('cada linha diz o tipo, o atraso com ícone e texto, a contagem e o responsável', async () => {
    setup()
    const next = await section()
    const row = next.getAllByRole('listitem')[0] as HTMLElement
    expect(within(row).getByText('Avulsa')).toBeVisible()
    expect(within(row).getByText('Atrasada')).toBeVisible()
    expect(within(row).getByText('venceu há 9 dias')).toBeVisible()
    expect(within(row).getByText('Noiva')).toBeVisible()
    expect(row.querySelector('svg')).not.toBeNull()
    const marco = next.getAllByRole('listitem')[1] as HTMLElement
    expect(within(marco).getByText('Marco')).toBeVisible()
    expect(within(marco).getByText('Atrasado')).toBeVisible()
    expect(within(marco).getByText('Ambos')).toBeVisible()
  })

  it('fica acima da barra de filtros', async () => {
    setup()
    const next = await screen.findByRole('region', { name: 'Meus próximos passos' })
    const bar = screen.getByRole('region', { name: 'Filtros do cronograma' })
    expect(next.compareDocumentPosition(bar) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })

  it('é sempre "eu ou Ambos", sem seguir a lente nem os filtros', async () => {
    setup(scheduleForFilters(), { responsavel: 'noivo' }, { profile: 'Noiva', lens: 'casal' })
    const next = await section()
    expect(next.getAllByRole('listitem')).toHaveLength(3)
    expect(next.queryByText('Avulsa Exemplo do Noivo')).toBeNull()
  })

  it('sem perfil, não aparece', async () => {
    setup(scheduleForFilters(), {}, {})
    await screen.findByRole('region', { name: 'Filtros do cronograma' })
    expect(screen.queryByRole('region', { name: 'Meus próximos passos' })).toBeNull()
  })

  it('no computador, não aparece (nem escondido por CSS)', async () => {
    stubWideScreen()
    setup()
    await screen.findByRole('table')
    expect(screen.queryByText('Meus próximos passos')).toBeNull()
  })

  it('sem nada seu pendente, diz com calma', async () => {
    setup(quietBase())
    expect(await screen.findByText('Nada seu pendente por agora.')).toBeVisible()
  })

  it('mostra até 8 e "Ver todos (N)" expande no lugar, com aria-expanded', async () => {
    const tasks = Array.from({ length: 10 }, (_, index) =>
      task({
        id: `00000000-0000-4000-8000-00000000f0${String(index).padStart(2, '0')}`,
        title: `Avulsa Exemplo ${String(index).padStart(2, '0')}`,
        responsible: 'Noiva',
      }),
    )
    const { user } = setup(scheduleWithTasks(tasks, quietBase()))
    const next = await section()
    expect(next.getAllByRole('listitem')).toHaveLength(8)
    const more = next.getByRole('button', { name: 'Ver todos (10)' })
    expect(more).toHaveAttribute('aria-expanded', 'false')
    await user.click(more)
    expect(next.getAllByRole('listitem')).toHaveLength(10)
    const less = next.getByRole('button', { name: 'Ver menos' })
    expect(less).toHaveAttribute('aria-expanded', 'true')
    await user.click(less)
    expect(next.getAllByRole('listitem')).toHaveLength(8)
  })

  it('com 8 ou menos, não oferece "Ver todos"', async () => {
    setup()
    const next = await section()
    expect(next.queryByRole('button', { name: /Ver todos/ })).toBeNull()
  })

  it('a linha de um marco abre o painel dele, e fechar devolve o foco à linha', async () => {
    const { user, probe } = setup()
    const next = await section()
    const row = next.getByRole('button', { name: 'Marco: Marco Exemplo de Ambos Atrasado' })
    expect(row).toHaveAttribute('data-next-step-id', FID.mAmbosAtrasado)
    expect(row).not.toHaveAttribute('data-milestone-id')
    await user.click(row)
    expect(
      await screen.findByRole('dialog', { name: 'Marco Exemplo de Ambos Atrasado' }),
    ).toBeVisible()
    expect(probe.current).toEqual({ marco: FID.mAmbosAtrasado })
    await user.keyboard('{Escape}')
    await waitFor(() => expect(row).toHaveFocus())
  })

  it('a linha de uma avulsa abre o painel da avulsa', async () => {
    const { user, probe } = setup()
    const next = await section()
    await user.click(next.getByRole('button', { name: 'Avulsa: Avulsa Exemplo da Noiva Atrasada' }))
    expect(
      await screen.findByRole('dialog', { name: 'Avulsa Exemplo da Noiva Atrasada' }),
    ).toBeVisible()
    expect(probe.current).toEqual({ avulsa: FID.tNoivaAtrasada })
  })
})
