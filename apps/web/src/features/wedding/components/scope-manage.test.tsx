import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { mapWithCategory, mapWithEmptyGroup, renderScope } from '@/test/render-scope'

const BASE = '/api/v1/wedding/scope'
const GET = `GET ${BASE}`
const PUT_CAT = (id: string) => `PUT ${BASE}/categories/${id}`
const VIS_CAT = (id: string) => `PUT ${BASE}/categories/${id}/visibility`
const DEL_CAT = (id: string) => `DELETE ${BASE}/categories/${id}`
const HISTORY = (id: string) => `GET ${BASE}/categories/${id}/history`
const sheet = (name: string) => screen.findByRole('dialog', { name })

describe('Detalhes da categoria (F-PLN-02 e F-PLN-05)', () => {
  const abre = (handlers = {}, id = 'c-foto') =>
    renderScope({ [HISTORY(id)]: jsonResponse(200, []), ...handlers }, { categoria: id })

  it('edita nome, grupo e estimativa de uma vez, com a versão que a tela mostra', async () => {
    const { api, user } = abre({
      [PUT_CAT('c-foto')]: jsonResponse(
        200,
        mapWithCategory('c-foto', { name: 'Foto Nova', estimate_cents: 200_000, version: 2 }),
      ),
    })
    const dialog = await sheet('Fotografia Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Editar detalhes' }))
    const nome = within(dialog).getByRole('textbox', { name: 'Nome' })
    expect(nome).toHaveValue('Fotografia Exemplo')
    expect(within(dialog).getByRole('textbox', { name: 'Estimativa inicial' })).toHaveValue(
      '1.500,00',
    )
    await user.clear(nome)
    await user.type(nome, 'Foto Nova')
    const estimativa = within(dialog).getByRole('textbox', { name: 'Estimativa inicial' })
    await user.clear(estimativa)
    await user.type(estimativa, '2.000')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar detalhes' }))

    await waitFor(() => expect(api.callsTo(PUT_CAT('c-foto'))).toHaveLength(1))
    expect(api.callsTo(PUT_CAT('c-foto'))[0]?.body).toEqual({
      name: 'Foto Nova',
      group_id: 'g-a',
      estimate_cents: 200_000,
      version: 1,
    })
  })

  it('estimativa vazia vai como nula, nunca como zero', async () => {
    const { api, user } = abre({ [PUT_CAT('c-foto')]: jsonResponse(200, MAPA()) })
    const dialog = await sheet('Fotografia Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Editar detalhes' }))
    await user.clear(within(dialog).getByRole('textbox', { name: 'Estimativa inicial' }))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar detalhes' }))
    await waitFor(() => expect(api.callsTo(PUT_CAT('c-foto'))).toHaveLength(1))
    expect(api.callsTo(PUT_CAT('c-foto'))[0]?.body).toMatchObject({ estimate_cents: null })
  })

  it('nome em branco é bloqueado antes de enviar', async () => {
    const { api, user } = abre()
    const dialog = await sheet('Fotografia Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Editar detalhes' }))
    await user.clear(within(dialog).getByRole('textbox', { name: 'Nome' }))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar detalhes' }))
    expect(await within(dialog).findByText('Informem um nome de até 60 caracteres.')).toBeVisible()
    expect(api.callsTo(PUT_CAT('c-foto'))).toHaveLength(0)
  })

  it('nome já usado mostra a mensagem da API e mantém o que foi digitado', async () => {
    const { user } = abre({
      [PUT_CAT('c-foto')]: problemResponse(409, 'duplicate_scope_name', {
        detail: 'Já existe uma frente ou um grupo com este nome. Escolha outro.',
      }),
    })
    const dialog = await sheet('Fotografia Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Editar detalhes' }))
    const nome = within(dialog).getByRole('textbox', { name: 'Nome' })
    await user.clear(nome)
    await user.type(nome, 'Vídeo Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar detalhes' }))
    expect(await within(dialog).findByText(/Já existe uma frente ou um grupo/)).toBeVisible()
    expect(nome).toHaveValue('Vídeo Exemplo')
  })

  it('enquanto edita os detalhes, o status não muda (uma seção por vez)', async () => {
    const { user } = abre()
    const dialog = await sheet('Fotografia Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Editar detalhes' }))
    expect(within(dialog).getByRole('combobox', { name: 'Status' })).toBeDisabled()
    await user.click(within(dialog).getByRole('button', { name: 'Cancelar' }))
    expect(within(dialog).getByRole('combobox', { name: 'Status' })).toBeEnabled()
  })

  it('oculta e mostra de novo, sem excluir nada', async () => {
    const { api, user } = abre({
      [VIS_CAT('c-foto')]: jsonResponse(
        200,
        mapWithCategory('c-foto', { hidden: true, visible: false, version: 2 }),
      ),
    })
    const dialog = await sheet('Fotografia Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Ocultar da tela' }))
    await waitFor(() => expect(api.callsTo(VIS_CAT('c-foto'))).toHaveLength(1))
    expect(api.callsTo(VIS_CAT('c-foto'))[0]?.body).toEqual({ hidden: true, version: 1 })
    expect(await within(dialog).findByRole('button', { name: 'Mostrar na tela' })).toBeVisible()
  })

  it('categoria do catálogo não tem Excluir e explica por quê', async () => {
    abre()
    const dialog = await sheet('Fotografia Exemplo')
    expect(
      within(dialog).queryByRole('button', { name: 'Excluir categoria' }),
    ).not.toBeInTheDocument()
    expect(
      within(dialog).getByText('Veio com o Altare: só se oculta, não se exclui.'),
    ).toBeVisible()
  })

  it('a do casal exclui só depois de ler a consequência e confirmar', async () => {
    const { api, user } = abre(
      {
        [GET]: jsonResponse(
          200,
          mapWithCategory('c-buffet', { origin: 'casal', can_delete: true }),
        ),
        [DEL_CAT('c-buffet')]: jsonResponse(200, mapWithCategory('c-buffet', {})),
      },
      'c-buffet',
    )
    const dialog = await sheet('Buffet Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Excluir categoria' }))
    const confirmacao = await screen.findByRole('dialog', { name: 'Excluir esta categoria?' })
    expect(
      within(confirmacao).getByText(/O histórico e as avaliações ficam guardados/),
    ).toBeVisible()
    expect(api.callsTo(DEL_CAT('c-buffet'))).toHaveLength(0)
    await user.click(within(confirmacao).getByRole('button', { name: 'Sim, excluir' }))
    await waitFor(() => expect(api.callsTo(DEL_CAT('c-buffet'))).toHaveLength(1))
    expect(
      new URL(api.callsTo(DEL_CAT('c-buffet'))[0]?.request.url ?? '').searchParams.get('version'),
    ).toBe('1')
  })
})

function MAPA() {
  return mapWithCategory('c-foto', {})
}

describe('Nova categoria (F-PLN-02)', () => {
  it('cria no grupo escolhido, com nome e estimativa opcional', async () => {
    const { api, user } = renderScope({ [`POST ${BASE}/categories`]: jsonResponse(201, MAPA()) })
    await user.click(await screen.findByRole('button', { name: 'Nova categoria' }))
    const dialog = await screen.findByRole('dialog', { name: 'Nova categoria' })
    await user.type(within(dialog).getByRole('textbox', { name: 'Nome' }), '  Cerimonial Exemplo ')
    await user.click(within(dialog).getByRole('combobox', { name: 'Grupo' }))
    await user.click(screen.getByRole('option', { name: 'Grupo Exemplo B' }))
    await user.type(within(dialog).getByRole('textbox', { name: 'Estimativa inicial' }), '3.200,50')
    await user.click(within(dialog).getByRole('button', { name: 'Criar categoria' }))
    await waitFor(() => expect(api.callsTo(`POST ${BASE}/categories`)).toHaveLength(1))
    expect(api.callsTo(`POST ${BASE}/categories`)[0]?.body).toEqual({
      group_id: 'g-b',
      name: 'Cerimonial Exemplo',
      estimate_cents: 320_050,
    })
  })

  it('nome em branco é bloqueado e nome repetido mostra a mensagem da API', async () => {
    const { api, user } = renderScope({
      [`POST ${BASE}/categories`]: problemResponse(409, 'duplicate_scope_name', {
        detail: 'Já existe uma frente ou um grupo com este nome. Escolha outro.',
      }),
    })
    await user.click(await screen.findByRole('button', { name: 'Nova categoria' }))
    const dialog = await screen.findByRole('dialog', { name: 'Nova categoria' })
    await user.click(within(dialog).getByRole('button', { name: 'Criar categoria' }))
    expect(await within(dialog).findByText('Informem um nome de até 60 caracteres.')).toBeVisible()
    expect(api.callsTo(`POST ${BASE}/categories`)).toHaveLength(0)

    await user.type(within(dialog).getByRole('textbox', { name: 'Nome' }), 'Fotografia')
    await user.click(within(dialog).getByRole('button', { name: 'Criar categoria' }))
    expect(await within(dialog).findByText(/Já existe uma frente ou um grupo/)).toBeVisible()
  })
})

describe('Grupos (F-PLN-02)', () => {
  const abreGrupos = async (handlers = {}) => {
    const r = renderScope({ [GET]: jsonResponse(200, mapWithEmptyGroup()), ...handlers })
    await r.user.click(await screen.findByRole('button', { name: 'Grupos' }))
    return { ...r, dialog: await screen.findByRole('dialog', { name: 'Grupos' }) }
  }

  it('lista os grupos e marca os do catálogo', async () => {
    const { dialog } = await abreGrupos()
    const itens = within(dialog).getAllByRole('listitem')
    expect(itens).toHaveLength(3)
    expect(within(itens[0] as HTMLElement).getByText('Catálogo')).toBeVisible()
  })

  it('só os grupos do casal e vazios têm Excluir', async () => {
    const { dialog } = await abreGrupos()
    expect(
      within(dialog).queryByRole('button', { name: 'Excluir Grupo Exemplo A' }),
    ).not.toBeInTheDocument()
    expect(
      within(dialog).queryByRole('button', { name: 'Excluir Grupo Exemplo B' }),
    ).not.toBeInTheDocument()
    expect(within(dialog).getByRole('button', { name: 'Excluir Vazio Exemplo' })).toBeVisible()
  })

  it('cria um grupo novo', async () => {
    const { api, user, dialog } = await abreGrupos({
      [`POST ${BASE}/groups`]: jsonResponse(201, MAPA()),
    })
    await user.type(
      within(dialog).getByRole('textbox', { name: 'Nome do novo grupo' }),
      ' Lua de mel ',
    )
    await user.click(within(dialog).getByRole('button', { name: 'Criar grupo' }))
    await waitFor(() => expect(api.callsTo(`POST ${BASE}/groups`)).toHaveLength(1))
    expect(api.callsTo(`POST ${BASE}/groups`)[0]?.body).toEqual({ name: 'Lua de mel' })
  })

  it('renomeia com a versão do grupo', async () => {
    const { api, user, dialog } = await abreGrupos({
      [`PUT ${BASE}/groups/g-b`]: jsonResponse(200, MAPA()),
    })
    await user.click(within(dialog).getByRole('button', { name: 'Renomear Grupo Exemplo B' }))
    const campo = within(dialog).getByRole('textbox', { name: 'Novo nome de Grupo Exemplo B' })
    await user.clear(campo)
    await user.type(campo, 'Outro Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar nome' }))
    await waitFor(() => expect(api.callsTo(`PUT ${BASE}/groups/g-b`)).toHaveLength(1))
    expect(api.callsTo(`PUT ${BASE}/groups/g-b`)[0]?.body).toEqual({
      name: 'Outro Exemplo',
      version: 1,
    })
  })

  it('oculta um grupo e exclui o vazio do casal', async () => {
    const { api, user, dialog } = await abreGrupos({
      [`PUT ${BASE}/groups/g-a/visibility`]: jsonResponse(200, mapWithEmptyGroup()),
      [`DELETE ${BASE}/groups/g-vazio`]: jsonResponse(200, MAPA()),
    })
    await user.click(within(dialog).getByRole('button', { name: 'Ocultar Grupo Exemplo A' }))
    await waitFor(() => expect(api.callsTo(`PUT ${BASE}/groups/g-a/visibility`)).toHaveLength(1))
    expect(api.callsTo(`PUT ${BASE}/groups/g-a/visibility`)[0]?.body).toEqual({
      hidden: true,
      version: 1,
    })

    await user.click(within(dialog).getByRole('button', { name: 'Excluir Vazio Exemplo' }))
    await waitFor(() => expect(api.callsTo(`DELETE ${BASE}/groups/g-vazio`)).toHaveLength(1))
    expect(
      new URL(api.callsTo(`DELETE ${BASE}/groups/g-vazio`)[0]?.request.url ?? '').searchParams.get(
        'version',
      ),
    ).toBe('3')
  })

  it('nome de grupo repetido mostra a mensagem da API', async () => {
    const { user, dialog } = await abreGrupos({
      [`POST ${BASE}/groups`]: problemResponse(409, 'duplicate_scope_name', {
        detail: 'Já existe uma frente ou um grupo com este nome. Escolha outro.',
      }),
    })
    await user.type(within(dialog).getByRole('textbox', { name: 'Nome do novo grupo' }), 'Registro')
    await user.click(within(dialog).getByRole('button', { name: 'Criar grupo' }))
    expect(await within(dialog).findByText(/Já existe uma frente ou um grupo/)).toBeVisible()
  })
})

describe('Sem nenhuma frente', () => {
  it('o estado vazio leva a gerenciar grupos', async () => {
    const { user } = renderScope({
      [GET]: jsonResponse(200, { ...mapWithEmptyGroup(), groups: [] }),
    })
    await user.click(await screen.findByRole('button', { name: 'Gerenciar grupos' }))
    expect(await screen.findByRole('dialog', { name: 'Grupos' })).toBeVisible()
  })
})
