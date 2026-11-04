import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import {
  DELETE_TASK,
  GET_SCHEDULE,
  PUT_CHECKLIST_ITEM,
  PUT_TASK,
  PUT_TASK_STATE,
  RESTORE_TASK,
  renderSchedule,
} from '@/test/render-schedule'
import { checklistItem, ID, sampleTasks, scheduleWithTasks, task } from '@/test/schedule-fixtures'
import { memory } from '@/test/schedule-helpers'

// F-CRN-06: o painel da avulsa, aberto pela URL (?avulsa=).
const TITLE = 'Avulsa Exemplo Atrasada'

function setup(
  routes: (store: ReturnType<typeof memory>) => object = () => ({}),
  tasks = sampleTasks(),
) {
  const store = memory(scheduleWithTasks(tasks))
  const view = renderSchedule(
    { [GET_SCHEDULE]: store.get, ...routes(store) } as never,
    { avulsa: tasks[0]?.id },
    { profile: 'Noiva' },
  )
  return { store, ...view }
}

async function panel(name = TITLE) {
  return screen.findByRole('dialog', { name })
}

describe('o painel da avulsa pela URL (F-CRN-06)', () => {
  it('abre procurando nos dados do cronograma, com o estado, o atraso e a contagem em texto', async () => {
    setup()
    const dialog = await panel()
    expect(within(dialog).getByText('A fazer')).toBeVisible()
    expect(within(dialog).getByText('Atrasada')).toBeVisible()
    expect(within(dialog).getByText('venceu há 3 dias')).toBeVisible()
    expect(within(dialog).getByText('15/01/2020')).toBeVisible()
    expect(within(dialog).getByLabelText('Título (obrigatório)')).toHaveValue(TITLE)
    expect(within(dialog).getByRole('combobox', { name: 'Responsável' })).toHaveTextContent('Noiva')
  })

  it('uma avulsa que não existe não abre painel nenhum', async () => {
    renderSchedule(
      { [GET_SCHEDULE]: jsonResponse(200, scheduleWithTasks(sampleTasks())) },
      { avulsa: ID.avulsaNova },
    )
    await screen.findByRole('heading', { name: 'Fase Exemplo Um' })
    expect(screen.queryByRole('dialog')).toBeNull()
  })

  it('abrir o painel de uma avulsa limpa o marco da URL, e o de um marco limpa a avulsa', async () => {
    const store = memory(scheduleWithTasks(sampleTasks()))
    const { user, probe } = renderSchedule({ [GET_SCHEDULE]: store.get }, { marco: ID.destravado })
    await screen.findByRole('dialog', { name: 'Marco Exemplo Destravado' })
    await user.keyboard('{Escape}')
    await user.click(await screen.findByRole('button', { name: TITLE }))
    await panel()
    expect(probe.current).toEqual({ avulsa: ID.avulsaUm })
    await user.keyboard('{Escape}')
    await user.click(await screen.findByRole('button', { name: 'Marco Exemplo Destravado' }))
    await screen.findByRole('dialog', { name: 'Marco Exemplo Destravado' })
    expect(probe.current).toEqual({ marco: ID.destravado })
  })
})

describe('editar a avulsa (F-CRN-06)', () => {
  it('envia a avulsa inteira com a versão e mostra o que o servidor devolveu', async () => {
    const { api, user } = setup((store) => ({
      [PUT_TASK(ID.avulsaUm)]: store.writeTask(ID.avulsaUm, () => ({
        title: 'Avulsa Exemplo Renomeada',
        version: 2,
      })),
    }))
    const dialog = await panel()
    const title = within(dialog).getByLabelText('Título (obrigatório)')
    await user.clear(title)
    await user.type(title, '  Avulsa Exemplo Renomeada ')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.callsTo(PUT_TASK(ID.avulsaUm))).toHaveLength(1))
    expect(api.callsTo(PUT_TASK(ID.avulsaUm))[0]?.body).toEqual({
      title: 'Avulsa Exemplo Renomeada',
      responsible: 'Noiva',
      note: null,
      target_date: '2020-01-15',
      version: 1,
    })
    expect(await screen.findByRole('dialog', { name: 'Avulsa Exemplo Renomeada' })).toBeVisible()
    expect(within(dialog).getByText('Alterações salvas.')).toBeVisible()
  })

  it('"Tirar o prazo" limpa a data e envia nulo', async () => {
    const { api, user } = setup((store) => ({
      [PUT_TASK(ID.avulsaUm)]: store.writeTask(ID.avulsaUm, () => ({
        target_date: null,
        days_left: null,
        overdue: false,
        version: 2,
      })),
    }))
    const dialog = await panel()
    await user.click(within(dialog).getByRole('button', { name: 'Tirar o prazo' }))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.callsTo(PUT_TASK(ID.avulsaUm))).toHaveLength(1))
    expect(api.callsTo(PUT_TASK(ID.avulsaUm))[0]?.body).toMatchObject({ target_date: null })
    await waitFor(() => expect(within(dialog).getByText('Sem prazo')).toBeVisible())
    expect(within(dialog).queryByText('Atrasada')).toBeNull()
  })

  it('título vazio é bloqueado no navegador', async () => {
    const { api, user } = setup()
    const dialog = await panel()
    await user.clear(within(dialog).getByLabelText('Título (obrigatório)'))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))
    expect(await within(dialog).findByText('Informem o título da avulsa.')).toBeVisible()
    expect(api.callsTo(PUT_TASK(ID.avulsaUm))).toHaveLength(0)
  })

  it('um 409 oferece a versão mais recente e não sobrescreve', async () => {
    const { api, user } = setup(() => ({
      [PUT_TASK(ID.avulsaUm)]: problemResponse(409, 'version_conflict'),
    }))
    const dialog = await panel()
    await user.type(within(dialog).getByLabelText('Nota'), 'Minha nota.')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))
    expect(
      await within(dialog).findByRole('button', { name: 'Ver a versão mais recente' }),
    ).toBeVisible()
    expect(within(dialog).getByLabelText('Nota')).toHaveValue('Minha nota.')
    expect(api.callsTo(PUT_TASK(ID.avulsaUm))).toHaveLength(1)
  })
})

describe('o estado da avulsa (F-CRN-06)', () => {
  it('A fazer oferece Marcar em andamento e Concluir, e Marcar em andamento leva a Em andamento sem confirmação', async () => {
    const { api, user } = setup((store) => ({
      [PUT_TASK_STATE(ID.avulsaUm)]: store.writeTask(ID.avulsaUm, () => ({
        state: 'Em andamento',
        version: 2,
      })),
    }))
    const dialog = await panel()
    expect(within(dialog).queryByRole('button', { name: 'Reabrir' })).toBeNull()
    await user.click(within(dialog).getByRole('button', { name: 'Marcar em andamento' }))

    await waitFor(() => expect(api.callsTo(PUT_TASK_STATE(ID.avulsaUm))).toHaveLength(1))
    expect(api.callsTo(PUT_TASK_STATE(ID.avulsaUm))[0]?.body).toEqual({
      state: 'Em andamento',
      ignore_open_items: false,
      version: 1,
    })
    expect(await within(dialog).findByText('Avulsa em andamento.')).toBeVisible()
    expect(within(dialog).getByRole('heading', { name: 'Estado' })).toHaveFocus()
    expect(within(dialog).queryByRole('button', { name: 'Marcar em andamento' })).toBeNull()
    expect(within(dialog).getByRole('button', { name: 'Concluir' })).toBeVisible()
    expect(within(dialog).getByRole('button', { name: 'Reabrir' })).toBeVisible()
  })

  it('Concluída só oferece Reabrir, que volta a A fazer sem confirmação', async () => {
    const tasks = sampleTasks()
    const { api, user } = setup(
      (store) => ({
        [PUT_TASK_STATE(ID.avulsaDois)]: store.writeTask(ID.avulsaDois, () => ({
          state: 'A fazer',
          version: 2,
        })),
      }),
      [tasks[1] as never, tasks[0] as never],
    )
    const dialog = await panel('Avulsa Exemplo Concluída')
    expect(within(dialog).getByText('Concluída')).toBeVisible()
    expect(within(dialog).queryByRole('button', { name: 'Marcar em andamento' })).toBeNull()
    expect(within(dialog).queryByRole('button', { name: 'Concluir' })).toBeNull()
    await user.click(within(dialog).getByRole('button', { name: 'Reabrir' }))

    await waitFor(() => expect(api.callsTo(PUT_TASK_STATE(ID.avulsaDois))).toHaveLength(1))
    expect(api.callsTo(PUT_TASK_STATE(ID.avulsaDois))[0]?.body).toMatchObject({ state: 'A fazer' })
    expect(await within(dialog).findByText('Avulsa reaberta.')).toBeVisible()
    expect(screen.getAllByRole('dialog')).toHaveLength(1)
  })

  it('concluir sem itens em aberto envia na hora, sem confirmação', async () => {
    const tasks = [task({ id: ID.avulsaUm, title: TITLE, state: 'Em andamento' })]
    const { api, user } = setup(
      (store) => ({
        [PUT_TASK_STATE(ID.avulsaUm)]: store.writeTask(ID.avulsaUm, () => ({
          state: 'Concluída',
          version: 2,
        })),
      }),
      tasks,
    )
    const dialog = await panel()
    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

    await waitFor(() => expect(api.callsTo(PUT_TASK_STATE(ID.avulsaUm))).toHaveLength(1))
    expect(api.callsTo(PUT_TASK_STATE(ID.avulsaUm))[0]?.body).toMatchObject({
      state: 'Concluída',
      ignore_open_items: false,
    })
    expect(await within(dialog).findByText('Avulsa concluída.')).toBeVisible()
  })
})

describe('concluir a avulsa com itens em aberto (F-CRN-07, regra 5)', () => {
  it('pede confirmação com a contagem, diz que os itens ficam e envia ignore_open_items', async () => {
    const { api, user } = setup((store) => ({
      [PUT_TASK_STATE(ID.avulsaUm)]: store.writeTask(ID.avulsaUm, () => ({
        state: 'Concluída',
        version: 2,
      })),
    }))
    const dialog = await panel()
    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

    const confirm = await screen.findByRole('dialog', { name: 'Concluir com itens em aberto?' })
    expect(within(confirm).getByText('Há 2 itens em aberto no checklist.')).toBeVisible()
    expect(within(confirm).getByText('Os itens continuam como estão.')).toBeVisible()
    expect(within(confirm).queryByText('O que falta')).toBeNull()
    expect(api.callsTo(PUT_TASK_STATE(ID.avulsaUm))).toHaveLength(0)
    await user.click(within(confirm).getByRole('button', { name: 'Concluir mesmo assim' }))

    await waitFor(() => expect(api.callsTo(PUT_TASK_STATE(ID.avulsaUm))).toHaveLength(1))
    expect(api.callsTo(PUT_TASK_STATE(ID.avulsaUm))[0]?.body).toEqual({
      state: 'Concluída',
      ignore_open_items: true,
      version: 1,
    })
    expect(await within(dialog).findByText('Avulsa concluída.')).toBeVisible()
    expect(within(dialog).getByText('1 de 3')).toBeVisible()
    await waitFor(() =>
      expect(within(dialog).getByRole('heading', { name: 'Estado' })).toHaveFocus(),
    )
  })

  it('com um item só, usa o singular', async () => {
    const tasks = [
      task({
        id: ID.avulsaUm,
        title: TITLE,
        checklist: [checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um' })],
      }),
    ]
    const { user } = setup(() => ({}), tasks)
    await user.click(within(await panel()).getByRole('button', { name: 'Concluir' }))
    expect(await screen.findByText('Há 1 item em aberto no checklist.')).toBeVisible()
  })

  it('cancelar não envia nada e devolve o foco ao botão Concluir', async () => {
    const { api, user } = setup()
    const dialog = await panel()
    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))
    const confirm = await screen.findByRole('dialog', { name: 'Concluir com itens em aberto?' })
    await user.click(within(confirm).getByRole('button', { name: 'Cancelar' }))

    await waitFor(() =>
      expect(within(dialog).getByRole('button', { name: 'Concluir' })).toHaveFocus(),
    )
    expect(api.callsTo(PUT_TASK_STATE(ID.avulsaUm))).toHaveLength(0)
  })

  it('se o servidor diz que há itens em aberto (dado velho), lê de novo e reabre com a contagem nova', async () => {
    const tasks = [
      task({
        id: ID.avulsaUm,
        title: TITLE,
        checklist: [checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um', done: true })],
      }),
    ]
    const { store, user } = setup(
      () => ({
        [PUT_TASK_STATE(ID.avulsaUm)]: problemResponse(422, 'checklist_open_items'),
      }),
      tasks,
    )
    const dialog = await panel()
    store.state.schedule = scheduleWithTasks([
      task({
        id: ID.avulsaUm,
        title: TITLE,
        version: 1,
        checklist: [
          checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um', done: true }),
          checklistItem({ id: ID.itemDois, text: 'Item Exemplo Dois', position: 1 }),
          checklistItem({ id: ID.itemTres, text: 'Item Exemplo Três', position: 2 }),
        ],
      }),
    ])
    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

    const confirm = await screen.findByRole('dialog', { name: 'Concluir com itens em aberto?' })
    expect(within(confirm).getByText('Há 2 itens em aberto no checklist.')).toBeVisible()
  })
})

describe('excluir a avulsa (F-CRN-06, D-072 item 8)', () => {
  it('exclui sem diálogo, fecha o painel, limpa a URL e oferece Desfazer por 4 s', async () => {
    const { api, user, probe } = setup((store) => ({
      [DELETE_TASK(ID.avulsaUm)]: () => {
        store.state.schedule = scheduleWithTasks(sampleTasks().slice(1))
        return jsonResponse(200, store.state.schedule)
      },
      [RESTORE_TASK(ID.avulsaUm)]: store.set(scheduleWithTasks(sampleTasks())),
    }))
    const dialog = await panel()
    await user.click(within(dialog).getByRole('button', { name: 'Excluir avulsa' }))

    expect(await screen.findByText('Avulsa excluída')).toBeVisible()
    const call = api.callsTo(DELETE_TASK(ID.avulsaUm))[0]
    expect(new URL(call?.request.url ?? '').searchParams.get('version')).toBe('1')
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
    expect(probe.current).toEqual({})
    await waitFor(() => expect(screen.getByRole('heading', { level: 1 })).toHaveFocus())

    await user.click(screen.getByRole('button', { name: 'Desfazer' }))
    await waitFor(() => expect(api.callsTo(RESTORE_TASK(ID.avulsaUm))).toHaveLength(1))
    expect(await screen.findByText('Avulsa restaurada')).toBeVisible()
  })

  it('se a restauração falha, oferece Tentar de novo', async () => {
    const { user } = setup((store) => ({
      [DELETE_TASK(ID.avulsaUm)]: store.set(scheduleWithTasks(sampleTasks().slice(1))),
      [RESTORE_TASK(ID.avulsaUm)]: problemResponse(500, 'internal_error'),
    }))
    await user.click(within(await panel()).getByRole('button', { name: 'Excluir avulsa' }))
    await user.click(await screen.findByRole('button', { name: 'Desfazer' }))
    expect(await screen.findByRole('button', { name: 'Tentar de novo' })).toBeVisible()
  })
})

describe('o checklist da avulsa (F-CRN-07)', () => {
  it('mostra o checklist da avulsa, com o progresso por escrito', async () => {
    setup()
    const dialog = await panel()
    const region = within(dialog).getByRole('region', { name: 'Checklist' })
    expect(within(region).getByText('1 de 3')).toBeVisible()
    expect(within(region).getByRole('checkbox', { name: 'Item Exemplo Um' })).toBeChecked()
  })
})

describe('as escritas do cronograma saem em série, de qualquer família (F-CRN-06, F-CRN-07)', () => {
  it('marcar um item e logo mudar o estado da avulsa: a segunda só sai depois da resposta da primeira', async () => {
    let releaseItem: () => void = () => {}
    const { api, user, store } = setup((s) => ({
      [PUT_CHECKLIST_ITEM(ID.itemDois)]: () =>
        new Promise<Response>((resolve) => {
          releaseItem = () =>
            resolve(
              s.writeChecklist(ID.avulsaUm, (items) =>
                items.map((item) =>
                  item.id === ID.itemDois ? { ...item, done: true, version: 2 } : item,
                ),
              )(),
            )
        }),
      [PUT_TASK_STATE(ID.avulsaUm)]: s.writeTask(ID.avulsaUm, () => ({
        state: 'Em andamento',
        version: 2,
      })),
    }))
    const dialog = await panel()
    await user.click(within(dialog).getByRole('checkbox', { name: 'Item Exemplo Dois' }))
    await waitFor(() => expect(api.callsTo(PUT_CHECKLIST_ITEM(ID.itemDois))).toHaveLength(1))
    await user.click(within(dialog).getByRole('button', { name: 'Marcar em andamento' }))

    // A segunda escrita espera: se saísse agora, a resposta dela poderia chegar antes e ser coberta.
    expect(api.callsTo(PUT_TASK_STATE(ID.avulsaUm))).toHaveLength(0)
    releaseItem()
    await waitFor(() => expect(api.callsTo(PUT_TASK_STATE(ID.avulsaUm))).toHaveLength(1))
    expect(await within(dialog).findByText('Avulsa em andamento.')).toBeVisible()
    const region = within(dialog).getByRole('region', { name: 'Checklist' })
    expect(within(region).getByText('2 de 3')).toBeVisible()
    expect(store.state.schedule.tasks[0]).toMatchObject({ state: 'Em andamento' })
  })
})

describe('a confirmação de concluir quando os itens em aberto somem (F-CRN-07)', () => {
  it('se uma releitura zera os itens em aberto, a confirmação se fecha e o foco vai ao título "Estado"', async () => {
    const tasks = [
      task({
        id: ID.avulsaUm,
        title: TITLE,
        checklist: [checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um' })],
      }),
    ]
    const { user, store } = setup(() => ({}), tasks)
    const dialog = await panel()
    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))
    await screen.findByRole('dialog', { name: 'Concluir com itens em aberto?' })

    // O outro marcou o último item: a próxima leitura (ao voltar à janela) traz 0 em aberto.
    store.state.schedule = scheduleWithTasks([
      task({
        id: ID.avulsaUm,
        title: TITLE,
        checklist: [checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um', done: true })],
      }),
    ])
    window.dispatchEvent(new Event('visibilitychange'))

    await waitFor(() =>
      expect(screen.queryByRole('dialog', { name: 'Concluir com itens em aberto?' })).toBeNull(),
    )
    await waitFor(() =>
      expect(within(dialog).getByRole('heading', { name: 'Estado' })).toHaveFocus(),
    )
  })
})
