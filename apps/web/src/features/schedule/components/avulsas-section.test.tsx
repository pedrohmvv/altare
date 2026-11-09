import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse } from '@/test/fake-api'
import { GET_SCHEDULE, renderSchedule, stubWideScreen } from '@/test/render-schedule'
import {
  checklistItem,
  ID,
  SCHEDULE,
  sampleTasks,
  scheduleWithChecklist,
  scheduleWithTasks,
} from '@/test/schedule-fixtures'

// F-CRN-06 (seção "Avulsas") e F-CRN-07 ("2 de 5" no cartão e na linha).
const EMPTY_TEXT =
  'Ainda não há avulsas. Criem uma para o que não tem ordem, como “pesquisar alianças”.'

const FIVE = [1, 2, 3, 4, 5].map((n) =>
  checklistItem({
    id: `00000000-0000-4000-8000-00000000e00${n}`,
    text: `Item Exemplo ${n}`,
    done: n <= 2,
    position: n,
  }),
)

describe('a seção "Avulsas" no celular (F-CRN-06)', () => {
  it('é uma seção com h2 "Avulsas", depois da última fase, com um cartão por avulsa', async () => {
    renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleWithTasks(sampleTasks())) })
    const section = await screen.findByRole('region', { name: 'Avulsas' })
    expect(within(section).getByRole('heading', { level: 2, name: 'Avulsas' })).toBeVisible()
    const lastPhase = screen.getByRole('region', { name: 'Fase Exemplo Dois' })
    expect(
      lastPhase.compareDocumentPosition(section) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy()

    const card = within(section)
      .getByRole('heading', { level: 3, name: 'Avulsa Exemplo Atrasada' })
      .closest('li') as HTMLElement
    expect(within(card).getByText('A fazer')).toBeVisible()
    expect(within(card).getByText('Atrasada')).toBeVisible()
    expect(within(card).getByText('Noiva')).toBeVisible()
    expect(within(card).getByText('venceu há 3 dias')).toBeVisible()
    expect(within(card).getByText('Checklist: 1 de 3')).toBeVisible()
    expect(within(section).getByText('Concluída')).toBeVisible()
  })

  it('o botão de cada avulsa tem data-task-id e não data-milestone-id', async () => {
    renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleWithTasks(sampleTasks())) })
    const button = await screen.findByRole('button', { name: 'Avulsa Exemplo Atrasada' })
    expect(button).toHaveAttribute('data-task-id', ID.avulsaUm)
    expect(button).not.toHaveAttribute('data-milestone-id')
  })

  it('sem avulsas, diz o que são e oferece "Nova avulsa"', async () => {
    renderSchedule()
    const section = await screen.findByRole('region', { name: 'Avulsas' })
    expect(within(section).getByText(EMPTY_TEXT)).toBeVisible()
    expect(within(section).getByRole('button', { name: 'Nova avulsa' })).toBeVisible()
  })

  it('o cabeçalho da página também tem o botão "Nova avulsa"', async () => {
    renderSchedule()
    await screen.findByRole('region', { name: 'Avulsas' })
    expect(screen.getAllByRole('button', { name: 'Nova avulsa' })).toHaveLength(2)
  })
})

describe('a seção "Avulsas" no computador (F-CRN-06)', () => {
  it('é um grupo de linhas da mesma tabela, depois da última fase, com as colunas do marco', async () => {
    stubWideScreen()
    renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleWithTasks(sampleTasks())) })
    const table = await screen.findByRole('table', {
      name: 'Fases do cronograma com os seus marcos, e as avulsas.',
    })
    const headers = within(table).getAllByRole('rowheader')
    expect(headers).toHaveLength(3)
    const avulsas = within(table).getByRole('rowheader', { name: 'Avulsas' })
    expect(avulsas).toHaveAttribute('scope', 'rowgroup')
    expect(avulsas).toHaveAttribute('colspan', '4')
    expect(headers.at(-1)).toBe(avulsas)

    const row = within(table)
      .getByRole('button', { name: 'Avulsa Exemplo Atrasada' })
      .closest('tr') as HTMLElement
    expect(within(row).getByText('A fazer')).toBeVisible()
    expect(within(row).getByText('Atrasada')).toBeVisible()
    expect(within(row).getByText('Noiva')).toBeVisible()
    expect(within(row).getByText('15/01/2020')).toBeVisible()
    expect(within(row).getByText('venceu há 3 dias')).toBeVisible()
    expect(within(row).getByText('Checklist: 1 de 3')).toBeVisible()
  })

  it('sem avulsas, a tabela diz o que são e oferece "Nova avulsa"', async () => {
    stubWideScreen()
    renderSchedule()
    const table = await screen.findByRole('table', {
      name: 'Fases do cronograma com os seus marcos, e as avulsas.',
    })
    expect(within(table).getByText(EMPTY_TEXT)).toBeVisible()
    expect(within(table).getByRole('button', { name: 'Nova avulsa' })).toBeVisible()
  })
})

describe('as avulsas ficam fora dos bloqueios e do progresso (F-CRN-06)', () => {
  it('não aparecem em "Aguardando", em "Libera" nem no progresso da fase', async () => {
    const { user } = renderSchedule({
      [GET_SCHEDULE]: jsonResponse(200, scheduleWithTasks(sampleTasks())),
    })
    await screen.findByRole('region', { name: 'Avulsas' })
    expect(screen.getByRole('region', { name: 'Fase Exemplo Um' })).toHaveTextContent(
      '1 de 3 concluídos',
    )
    for (const element of screen.getAllByText(/^Aguardando/)) {
      expect(element).not.toHaveTextContent('Avulsa')
    }
    await user.click(screen.getByRole('button', { name: 'Marco Exemplo Concluído' }))
    const dialog = await screen.findByRole('dialog', { name: 'Marco Exemplo Concluído' })
    expect(within(dialog).queryByText(/Avulsa Exemplo/)).toBeNull()
  })
})

describe('"N de M" do checklist no cartão e na linha (F-CRN-07)', () => {
  it('o cartão do marco mostra "Checklist: 2 de 5" e o nome do botão não muda', async () => {
    renderSchedule({
      [GET_SCHEDULE]: jsonResponse(200, scheduleWithChecklist(ID.destravado, FIVE)),
    })
    const button = await screen.findByRole('button', { name: 'Marco Exemplo Destravado' })
    const card = button.closest('li') as HTMLElement
    expect(within(card).getByText('Checklist: 2 de 5')).toBeVisible()
    expect(within(card).getByRole('button')).toHaveAccessibleName('Marco Exemplo Destravado')
  })

  it('a linha da tabela do marco mostra o mesmo texto', async () => {
    stubWideScreen()
    renderSchedule({
      [GET_SCHEDULE]: jsonResponse(200, scheduleWithChecklist(ID.destravado, FIVE)),
    })
    const button = await screen.findByRole('button', { name: 'Marco Exemplo Destravado' })
    const row = button.closest('tr') as HTMLElement
    expect(within(row).getByText('Checklist: 2 de 5')).toBeVisible()
  })

  it('sem itens, não mostra nada', async () => {
    renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, SCHEDULE) })
    await screen.findByRole('button', { name: 'Marco Exemplo Destravado' })
    expect(screen.queryByText(/^Checklist:/)).toBeNull()
  })
})
