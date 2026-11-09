import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { problemResponse } from '@/test/fake-api'
import { GET_SCHEDULE, PUT_STATE, renderSchedule } from '@/test/render-schedule'
import { checklistItem, ID, scheduleWithChecklist } from '@/test/schedule-fixtures'
import { memory, openMilestone } from '@/test/schedule-helpers'

// F-CRN-07, regra 5: concluir o marco com itens em aberto pede confirmação e preserva os itens.
const OPEN = [
  checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um', done: true, position: 0 }),
  checklistItem({ id: ID.itemDois, text: 'Item Exemplo Dois', position: 1 }),
]

function setup(id: string, routes: (store: ReturnType<typeof memory>) => object = () => ({})) {
  const store = memory(scheduleWithChecklist(id, OPEN))
  return {
    store,
    ...renderSchedule({ [GET_SCHEDULE]: store.get, ...routes(store) } as never),
  }
}

describe('concluir o marco com itens em aberto (F-CRN-07)', () => {
  it('no marco destravado, pede confirmação só com os itens e envia ignore_open_items', async () => {
    const { api, user } = setup(ID.destravado, (store) => ({
      [PUT_STATE(ID.destravado)]: store.write(ID.destravado, () => ({
        state: 'Concluído',
        version: 2,
      })),
    }))
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')
    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

    const confirm = await screen.findByRole('dialog', { name: 'Concluir com itens em aberto?' })
    expect(within(confirm).getByText('Há 1 item em aberto no checklist.')).toBeVisible()
    expect(within(confirm).getByText('Os itens continuam como estão.')).toBeVisible()
    expect(within(confirm).queryByText('O que falta')).toBeNull()
    await user.click(within(confirm).getByRole('button', { name: 'Concluir mesmo assim' }))

    await waitFor(() => expect(api.callsTo(PUT_STATE(ID.destravado))).toHaveLength(1))
    expect(api.callsTo(PUT_STATE(ID.destravado))[0]?.body).toEqual({
      state: 'Concluído',
      ignore_block: false,
      ignore_open_items: true,
      version: 1,
    })
    expect(await within(dialog).findByText('Marco concluído.')).toBeVisible()
    expect(within(dialog).getByText('1 de 2')).toBeVisible()
    await waitFor(() =>
      expect(within(dialog).getByRole('heading', { name: 'Estado' })).toHaveFocus(),
    )
  })

  it('no marco bloqueado, um só diálogo com as duas permissões e as duas flags no envio', async () => {
    const { api, user } = setup(ID.bloqueado, (store) => ({
      [PUT_STATE(ID.bloqueado)]: store.write(ID.bloqueado, () => ({
        state: 'Concluído',
        version: 2,
      })),
    }))
    const dialog = await openMilestone(user, 'Marco Exemplo Bloqueado')
    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

    const confirm = await screen.findByRole('dialog', { name: 'Concluir com itens em aberto?' })
    expect(within(confirm).getByText('Há 1 item em aberto no checklist.')).toBeVisible()
    expect(within(confirm).getByText('O que falta')).toBeVisible()
    expect(within(confirm).getByText('Marco Exemplo Destravado')).toBeVisible()
    expect(screen.queryByRole('dialog', { name: 'Ignorar o bloqueio?' })).toBeNull()
    await user.click(within(confirm).getByRole('button', { name: 'Concluir mesmo assim' }))

    await waitFor(() => expect(api.callsTo(PUT_STATE(ID.bloqueado))).toHaveLength(1))
    expect(api.callsTo(PUT_STATE(ID.bloqueado))[0]?.body).toEqual({
      state: 'Concluído',
      ignore_block: true,
      ignore_open_items: true,
      version: 1,
    })
  })

  it('cancelar volta ao botão Concluir e não envia nada', async () => {
    const { api, user } = setup(ID.destravado)
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')
    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))
    const confirm = await screen.findByRole('dialog', { name: 'Concluir com itens em aberto?' })
    await user.click(within(confirm).getByRole('button', { name: 'Cancelar' }))
    await waitFor(() =>
      expect(within(dialog).getByRole('button', { name: 'Concluir' })).toHaveFocus(),
    )
    expect(api.callsTo(PUT_STATE(ID.destravado))).toHaveLength(0)
  })

  it('um 422 de itens em aberto (dado velho) lê de novo e reabre com a contagem nova', async () => {
    const all = [checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um', done: true, position: 0 })]
    const store = memory(scheduleWithChecklist(ID.destravado, all))
    const { user } = renderSchedule({
      [GET_SCHEDULE]: store.get,
      [PUT_STATE(ID.destravado)]: problemResponse(422, 'checklist_open_items'),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')
    store.state.schedule = scheduleWithChecklist(ID.destravado, [
      ...all,
      checklistItem({ id: ID.itemDois, text: 'Item Exemplo Dois', position: 1 }),
      checklistItem({ id: ID.itemTres, text: 'Item Exemplo Três', position: 2 }),
    ])
    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

    const confirm = await screen.findByRole('dialog', { name: 'Concluir com itens em aberto?' })
    expect(within(confirm).getByText('Há 2 itens em aberto no checklist.')).toBeVisible()
  })

  it('se uma releitura zera os itens em aberto, a confirmação se fecha e o foco vai ao título "Estado"', async () => {
    const one = [checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um' })]
    const store = memory(scheduleWithChecklist(ID.destravado, one))
    const { user } = renderSchedule({ [GET_SCHEDULE]: store.get })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')
    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))
    await screen.findByRole('dialog', { name: 'Concluir com itens em aberto?' })

    store.state.schedule = scheduleWithChecklist(
      ID.destravado,
      one.map((item) => ({ ...item, done: true })),
    )
    window.dispatchEvent(new Event('visibilitychange'))

    await waitFor(() =>
      expect(screen.queryByRole('dialog', { name: 'Concluir com itens em aberto?' })).toBeNull(),
    )
    // O diálogo de ignorar o bloqueio não existe para este marco (não está bloqueado).
    expect(screen.queryByRole('dialog', { name: 'Ignorar o bloqueio?' })).toBeNull()
    await waitFor(() =>
      expect(within(dialog).getByRole('heading', { name: 'Estado' })).toHaveFocus(),
    )
  })
})
