import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { problemResponse } from '@/test/fake-api'
import {
  DELETE_CHECKLIST_ITEM,
  GET_SCHEDULE,
  POST_CHECKLIST,
  PUT_CHECKLIST_ITEM,
  PUT_CHECKLIST_ORDER,
  PUT_STATE,
  renderSchedule,
} from '@/test/render-schedule'
import { checklistItem, ID, scheduleWithChecklist } from '@/test/schedule-fixtures'
import { memory } from '@/test/schedule-helpers'

// F-CRN-07: checklist de subtarefas (marcos e avulsas). Aqui, o do marco: o componente é o mesmo.
const ITEMS = [
  checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um', done: true, position: 0 }),
  checklistItem({ id: ID.itemDois, text: 'Item Exemplo Dois', position: 1 }),
  checklistItem({ id: ID.itemTres, text: 'Item Exemplo Três', position: 2 }),
]

function setup(
  items = ITEMS,
  routes: (store: ReturnType<typeof memory>) => Record<string, never> | object = () => ({}),
) {
  const store = memory(scheduleWithChecklist(ID.destravado, items))
  const view = renderSchedule({ [GET_SCHEDULE]: store.get, ...routes(store) } as never, {
    marco: ID.destravado,
  })
  return { store, ...view }
}

async function section() {
  const dialog = await screen.findByRole('dialog', { name: 'Marco Exemplo Destravado' })
  return within(await within(dialog).findByRole('region', { name: 'Checklist' }))
}

const lastBody = (api: ReturnType<typeof renderSchedule>['api'], route: string) =>
  api.callsTo(route).at(-1)?.body

describe('checklist do painel (F-CRN-07)', () => {
  it('sem itens, mostra o estado vazio calmo e o campo de adicionar', async () => {
    setup([])
    const list = await section()
    expect(list.getByText(/Ainda sem itens/)).toBeVisible()
    expect(list.queryByText(/ de /)).toBeNull()
    expect(list.getByRole('textbox', { name: 'Novo item' })).toBeVisible()
  })

  it('mostra o progresso "N de M" em texto e cada item com a caixa nomeada pelo texto', async () => {
    setup()
    const list = await section()
    expect(list.getByText('1 de 3')).toBeVisible()
    expect(list.getByRole('checkbox', { name: 'Item Exemplo Um' })).toBeChecked()
    expect(list.getByRole('checkbox', { name: 'Item Exemplo Dois' })).not.toBeChecked()
  })

  it('tem uma região de alerta vazia desde o início e uma de status', async () => {
    setup()
    const list = await section()
    expect(list.getAllByRole('alert').some((region) => region.textContent === '')).toBe(true)
    expect(list.getByRole('status')).toBeEmptyDOMElement()
  })

  it('marcar envia o item inteiro com a versão dele e atualiza o progresso', async () => {
    const { api, user } = setup(ITEMS, (store) => ({
      [PUT_CHECKLIST_ITEM(ID.itemDois)]: store.writeChecklist(ID.destravado, (items) =>
        items.map((item) => (item.id === ID.itemDois ? { ...item, done: true, version: 2 } : item)),
      ),
    }))
    const list = await section()
    await user.click(list.getByRole('checkbox', { name: 'Item Exemplo Dois' }))
    await waitFor(() => expect(list.getByText('2 de 3')).toBeVisible())
    expect(lastBody(api, PUT_CHECKLIST_ITEM(ID.itemDois))).toEqual({
      text: 'Item Exemplo Dois',
      done: true,
      version: 1,
    })
  })

  it('a caixa do item pendente fica desabilitada e o foco volta a ela depois', async () => {
    let release: () => void = () => {}
    const { user } = setup(ITEMS, (store) => ({
      [PUT_CHECKLIST_ITEM(ID.itemDois)]: () =>
        new Promise<Response>((resolve) => {
          release = () =>
            resolve(
              store.writeChecklist(ID.destravado, (items) =>
                items.map((item) =>
                  item.id === ID.itemDois ? { ...item, done: true, version: 2 } : item,
                ),
              )(),
            )
        }),
    }))
    const list = await section()
    await user.click(list.getByRole('checkbox', { name: 'Item Exemplo Dois' }))
    await waitFor(() =>
      expect(list.getByRole('checkbox', { name: 'Item Exemplo Dois' })).toBeDisabled(),
    )
    release()
    await waitFor(() =>
      expect(list.getByRole('checkbox', { name: 'Item Exemplo Dois' })).toBeEnabled(),
    )
    await waitFor(() =>
      expect(list.getByRole('checkbox', { name: 'Item Exemplo Dois' })).toHaveFocus(),
    )
  })

  it('adicionar envia o texto, limpa o campo, mantém o foco nele e anuncia', async () => {
    const { api, user } = setup(ITEMS, (store) => ({
      [POST_CHECKLIST('milestones', ID.destravado)]: store.writeChecklist(
        ID.destravado,
        (items) => [
          ...items,
          checklistItem({ id: ID.itemNovo, text: 'Item Exemplo Novo', position: 3 }),
        ],
      ),
    }))
    const list = await section()
    const field = list.getByRole('textbox', { name: 'Novo item' })
    await user.type(field, '  Item Exemplo Novo ')
    await user.click(list.getByRole('button', { name: 'Adicionar item' }))

    await waitFor(() => expect(list.getByText('Item adicionado.')).toBeVisible())
    expect(lastBody(api, POST_CHECKLIST('milestones', ID.destravado))).toEqual({
      text: 'Item Exemplo Novo',
    })
    expect(list.getByRole('checkbox', { name: 'Item Exemplo Novo' })).toBeVisible()
    expect(field).toHaveValue('')
    await waitFor(() => expect(field).toHaveFocus())
  })

  it('texto vazio é bloqueado no navegador, com o aviso junto do campo', async () => {
    const { api, user } = setup()
    const list = await section()
    await user.click(list.getByRole('button', { name: 'Adicionar item' }))
    expect(await list.findByText('Informem o texto do item.')).toBeVisible()
    expect(api.callsTo(POST_CHECKLIST('milestones', ID.destravado))).toHaveLength(0)
  })

  it('a lista cheia (50 itens) mostra o limite e não troca nada', async () => {
    const { user } = setup(ITEMS, () => ({
      [POST_CHECKLIST('milestones', ID.destravado)]: problemResponse(422, 'checklist_full', {
        detail: 'Detalhe da API.',
      }),
    }))
    const list = await section()
    await user.type(list.getByRole('textbox', { name: 'Novo item' }), 'Mais um')
    await user.click(list.getByRole('button', { name: 'Adicionar item' }))
    expect(await list.findByText('Cada lista vai até 50 itens.')).toBeVisible()
    expect(list.getByRole('textbox', { name: 'Novo item' })).toHaveValue('Mais um')
  })

  it('editar o texto da linha envia o item inteiro e volta ao botão Editar', async () => {
    const { api, user } = setup(ITEMS, (store) => ({
      [PUT_CHECKLIST_ITEM(ID.itemDois)]: store.writeChecklist(ID.destravado, (items) =>
        items.map((item) =>
          item.id === ID.itemDois ? { ...item, text: 'Item Exemplo Editado', version: 2 } : item,
        ),
      ),
    }))
    const list = await section()
    await user.click(list.getByRole('button', { name: 'Editar o item Item Exemplo Dois' }))
    const field = list.getByRole('textbox', { name: 'Texto do item' })
    expect(field).toHaveFocus()
    await user.clear(field)
    await user.type(field, 'Item Exemplo Editado')
    await user.click(list.getByRole('button', { name: 'Salvar o item Item Exemplo Dois' }))

    await waitFor(() =>
      expect(list.getByRole('checkbox', { name: 'Item Exemplo Editado' })).toBeVisible(),
    )
    expect(lastBody(api, PUT_CHECKLIST_ITEM(ID.itemDois))).toEqual({
      text: 'Item Exemplo Editado',
      done: false,
      version: 1,
    })
    expect(list.getByRole('status')).toHaveTextContent('Item salvo.')
    expect(list.getByRole('button', { name: 'Editar o item Item Exemplo Editado' })).toHaveFocus()
  })

  it('um 409 ao editar oferece a versão mais recente e não sobrescreve', async () => {
    const { api, user, store } = setup(ITEMS, () => ({
      [PUT_CHECKLIST_ITEM(ID.itemDois)]: problemResponse(409, 'version_conflict'),
    }))
    const list = await section()
    await user.click(list.getByRole('button', { name: 'Editar o item Item Exemplo Dois' }))
    const field = list.getByRole('textbox', { name: 'Texto do item' })
    await user.clear(field)
    await user.type(field, 'Meu texto')
    store.state.schedule = scheduleWithChecklist(
      ID.destravado,
      ITEMS.map((item) =>
        item.id === ID.itemDois ? { ...item, text: 'Texto do outro', version: 2 } : item,
      ),
    )
    await user.click(list.getByRole('button', { name: 'Salvar o item Item Exemplo Dois' }))

    const reload = await list.findByRole('button', { name: 'Ver a versão mais recente' })
    expect(list.getByRole('textbox', { name: 'Texto do item' })).toHaveValue('Meu texto')
    await user.click(reload)
    await waitFor(() =>
      expect(list.getByRole('checkbox', { name: 'Texto do outro' })).toBeVisible(),
    )
    expect(api.callsTo(PUT_CHECKLIST_ITEM(ID.itemDois))).toHaveLength(1)
  })

  it('o primeiro item não sobe e o último não desce', async () => {
    setup()
    const list = await section()
    expect(list.getByRole('button', { name: 'Subir o item Item Exemplo Um' })).toBeDisabled()
    expect(list.getByRole('button', { name: 'Descer o item Item Exemplo Três' })).toBeDisabled()
    expect(list.getByRole('button', { name: 'Descer o item Item Exemplo Um' })).toBeEnabled()
  })

  it('descer envia a lista completa de ids e o foco acompanha o botão do item movido', async () => {
    const { api, user } = setup(ITEMS, (store) => ({
      [PUT_CHECKLIST_ORDER('milestones', ID.destravado)]: store.writeChecklist(
        ID.destravado,
        ([um, dois, tres]) => [dois, um, tres].filter((item) => item !== undefined) as never,
      ),
    }))
    const list = await section()
    await user.click(list.getByRole('button', { name: 'Descer o item Item Exemplo Um' }))

    await waitFor(() => expect(list.getByText('Itens reordenados.')).toBeVisible())
    expect(lastBody(api, PUT_CHECKLIST_ORDER('milestones', ID.destravado))).toEqual({
      ids: [ID.itemDois, ID.itemUm, ID.itemTres],
    })
    await waitFor(() =>
      expect(list.getByRole('button', { name: 'Descer o item Item Exemplo Um' })).toHaveFocus(),
    )
  })

  it('uma ordem que já não é a do servidor pede a versão mais recente', async () => {
    const { user } = setup(ITEMS, () => ({
      [PUT_CHECKLIST_ORDER('milestones', ID.destravado)]: problemResponse(
        422,
        'invalid_checklist_order',
      ),
    }))
    const list = await section()
    await user.click(list.getByRole('button', { name: 'Descer o item Item Exemplo Um' }))
    expect(await list.findByRole('button', { name: 'Ver a versão mais recente' })).toBeVisible()
  })

  it('remover é imediato, sem diálogo, com a versão do item, e o foco vai ao título', async () => {
    const { api, user } = setup(ITEMS, (store) => ({
      [DELETE_CHECKLIST_ITEM(ID.itemDois)]: store.writeChecklist(ID.destravado, (items) =>
        items.filter((item) => item.id !== ID.itemDois),
      ),
    }))
    const list = await section()
    await user.click(list.getByRole('button', { name: 'Remover o item Item Exemplo Dois' }))

    await waitFor(() => expect(list.getByText('Item removido.')).toBeVisible())
    expect(list.queryByRole('checkbox', { name: 'Item Exemplo Dois' })).toBeNull()
    expect(screen.getAllByRole('dialog')).toHaveLength(1)
    const call = api.callsTo(DELETE_CHECKLIST_ITEM(ID.itemDois)).at(-1)
    expect(new URL(call?.request.url ?? '').searchParams.get('version')).toBe('1')
    expect(list.getByRole('heading', { name: 'Checklist' })).toHaveFocus()
  })

  it('as escritas do checklist saem uma depois da outra, para as respostas não chegarem fora de ordem', async () => {
    const releases: (() => void)[] = []
    const { api, user } = setup(ITEMS, (store) => {
      const hold = (id: string) => () =>
        new Promise<Response>((resolve) => {
          releases.push(() =>
            resolve(
              store.writeChecklist(ID.destravado, (items) =>
                items.map((item) => (item.id === id ? { ...item, done: !item.done } : item)),
              )(),
            ),
          )
        })
      return {
        [PUT_CHECKLIST_ITEM(ID.itemDois)]: hold(ID.itemDois),
        [PUT_CHECKLIST_ITEM(ID.itemTres)]: hold(ID.itemTres),
      }
    })
    const list = await section()
    await user.click(list.getByRole('checkbox', { name: 'Item Exemplo Dois' }))
    await user.click(list.getByRole('checkbox', { name: 'Item Exemplo Três' }))

    await waitFor(() => expect(api.callsTo(PUT_CHECKLIST_ITEM(ID.itemDois))).toHaveLength(1))
    expect(api.callsTo(PUT_CHECKLIST_ITEM(ID.itemTres))).toHaveLength(0)
    releases[0]?.()
    await waitFor(() => expect(api.callsTo(PUT_CHECKLIST_ITEM(ID.itemTres))).toHaveLength(1))
  })

  it('com a marcação do item pendente, Editar, Subir, Descer e Remover dele ficam desabilitados', async () => {
    let release: () => void = () => {}
    const { api, user } = setup(ITEMS, (store) => ({
      [PUT_CHECKLIST_ITEM(ID.itemDois)]: () =>
        new Promise<Response>((resolve) => {
          release = () =>
            resolve(
              store.writeChecklist(ID.destravado, (items) =>
                items.map((item) =>
                  item.id === ID.itemDois ? { ...item, done: true, version: 2 } : item,
                ),
              )(),
            )
        }),
    }))
    const list = await section()
    await user.click(list.getByRole('checkbox', { name: 'Item Exemplo Dois' }))
    await waitFor(() =>
      expect(list.getByRole('checkbox', { name: 'Item Exemplo Dois' })).toBeDisabled(),
    )
    for (const name of ['Editar', 'Subir', 'Descer', 'Remover']) {
      expect(list.getByRole('button', { name: `${name} o item Item Exemplo Dois` })).toBeDisabled()
    }
    // Remover agora mandaria a versão de antes da marcação e daria 409 provocado pela própria tela.
    expect(api.callsTo(DELETE_CHECKLIST_ITEM(ID.itemDois))).toHaveLength(0)
    release()
    await waitFor(() =>
      expect(list.getByRole('button', { name: 'Remover o item Item Exemplo Dois' })).toBeEnabled(),
    )
  })

  it('com a adição pendente, Subir e Descer de todas as linhas ficam desabilitados', async () => {
    let release: () => void = () => {}
    const { api, user } = setup(ITEMS, (store) => ({
      [POST_CHECKLIST('milestones', ID.destravado)]: () =>
        new Promise<Response>((resolve) => {
          release = () =>
            resolve(
              store.writeChecklist(ID.destravado, (items) => [
                ...items,
                checklistItem({ id: ID.itemNovo, text: 'Item Exemplo Novo', position: 3 }),
              ])(),
            )
        }),
    }))
    const list = await section()
    await user.type(list.getByRole('textbox', { name: 'Novo item' }), 'Item Exemplo Novo')
    await user.click(list.getByRole('button', { name: 'Adicionar item' }))
    await waitFor(() =>
      expect(api.callsTo(POST_CHECKLIST('milestones', ID.destravado))).toHaveLength(1),
    )

    for (const name of ['Item Exemplo Um', 'Item Exemplo Dois', 'Item Exemplo Três']) {
      expect(list.getByRole('button', { name: `Subir o item ${name}` })).toBeDisabled()
      expect(list.getByRole('button', { name: `Descer o item ${name}` })).toBeDisabled()
    }
    release()
    await waitFor(() =>
      expect(list.getByRole('button', { name: 'Descer o item Item Exemplo Dois' })).toBeEnabled(),
    )
  })

  it('a escrita do estado do marco também espera a do checklist (escopo único do cronograma)', async () => {
    let release: () => void = () => {}
    const { api, user } = setup(ITEMS, (store) => ({
      [PUT_CHECKLIST_ITEM(ID.itemDois)]: () =>
        new Promise<Response>((resolve) => {
          release = () =>
            resolve(
              store.writeChecklist(ID.destravado, (items) =>
                items.map((item) =>
                  item.id === ID.itemDois ? { ...item, done: true, version: 2 } : item,
                ),
              )(),
            )
        }),
      [PUT_STATE(ID.destravado)]: store.write(ID.destravado, () => ({
        state: 'Em andamento',
        version: 2,
      })),
    }))
    const dialog = await screen.findByRole('dialog', { name: 'Marco Exemplo Destravado' })
    const list = await section()
    await user.click(list.getByRole('checkbox', { name: 'Item Exemplo Dois' }))
    await waitFor(() => expect(api.callsTo(PUT_CHECKLIST_ITEM(ID.itemDois))).toHaveLength(1))
    await user.click(within(dialog).getByRole('button', { name: 'Marcar em andamento' }))

    expect(api.callsTo(PUT_STATE(ID.destravado))).toHaveLength(0)
    release()
    await waitFor(() => expect(api.callsTo(PUT_STATE(ID.destravado))).toHaveLength(1))
  })

  it('com a remoção de um item pendente, Subir e Descer de todas as linhas e a caixa dele ficam desabilitados', async () => {
    let release: () => void = () => {}
    const { api, user } = setup(ITEMS, (store) => ({
      [DELETE_CHECKLIST_ITEM(ID.itemDois)]: () =>
        new Promise<Response>((resolve) => {
          release = () =>
            resolve(
              store.writeChecklist(ID.destravado, (items) =>
                items.filter((item) => item.id !== ID.itemDois),
              )(),
            )
        }),
    }))
    const list = await section()
    await user.click(list.getByRole('button', { name: 'Remover o item Item Exemplo Dois' }))
    await waitFor(() => expect(api.callsTo(DELETE_CHECKLIST_ITEM(ID.itemDois))).toHaveLength(1))

    // A ordem mandada agora ainda levaria o item removido (ordem inválida, provocada pela tela).
    for (const name of ['Item Exemplo Um', 'Item Exemplo Dois', 'Item Exemplo Três']) {
      expect(list.getByRole('button', { name: `Subir o item ${name}` })).toBeDisabled()
      expect(list.getByRole('button', { name: `Descer o item ${name}` })).toBeDisabled()
    }
    expect(list.getByRole('checkbox', { name: 'Item Exemplo Dois' })).toBeDisabled()
    expect(api.callsTo(PUT_CHECKLIST_ORDER('milestones', ID.destravado))).toHaveLength(0)
    release()
    await waitFor(() =>
      expect(list.queryByRole('checkbox', { name: 'Item Exemplo Dois' })).toBeNull(),
    )
    expect(list.getByRole('button', { name: 'Descer o item Item Exemplo Um' })).toBeEnabled()
  })
})
