import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { GuestList } from '@/features/guests/api/guests'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { guest, household, LIST } from '@/test/guest-fixtures'
import { GET_GUESTS, renderGuests } from '@/test/render-guests'

const BASE = '/api/v1/guests'
const POST_HOUSEHOLDS = `POST ${BASE}/households`
const POST_GUESTS = (id: string) => `POST ${BASE}/households/${id}/guests`
const PUT_HOUSEHOLD = (id: string) => `PUT ${BASE}/households/${id}`
const PUT_GUEST = (id: string) => `PUT ${BASE}/people/${id}`
const POST_COMPANION = (id: string) => `POST ${BASE}/people/${id}/companion`

/** A API falsa com memória: a leitura devolve o que a última escrita deixou, como o servidor faria. */
function memory(initial: GuestList) {
  const state = { list: initial }
  return {
    state,
    get: () => jsonResponse(200, state.list),
    write: (next: GuestList | ((current: GuestList) => GuestList)) => () => {
      state.list = typeof next === 'function' ? next(state.list) : next
      return jsonResponse(200, state.list)
    },
  }
}

const EMPTY: GuestList = { households: [] }

async function fillNewHousehold(
  user: ReturnType<typeof renderGuests>['user'],
  names = {
    household: 'Família Nova',
    guest: 'Convidado Exemplo A',
  },
) {
  await user.click(await screen.findByRole('button', { name: 'Adicionar núcleo' }))
  const dialog = await screen.findByRole('dialog', { name: 'Novo núcleo' })
  const [householdName, guestName] = within(dialog).getAllByRole('textbox', { name: /^Nome/ })
  await user.type(householdName as HTMLElement, names.household)
  await user.click(within(dialog).getByRole('combobox', { name: 'Lado' }))
  await user.click(screen.getByRole('option', { name: 'Noiva' }))
  await user.type(guestName as HTMLElement, names.guest)
  return dialog
}

describe('novo núcleo (F-CNV-01)', () => {
  it('a lista vazia oferece criar o primeiro núcleo', async () => {
    const mem = memory(EMPTY)
    renderGuests({ [GET_GUESTS]: mem.get })

    expect(await screen.findByRole('button', { name: 'Adicionar núcleo' })).toBeVisible()
  })

  it('recusa nome e lado vazios e leva o foco ao primeiro campo com erro', async () => {
    const mem = memory(EMPTY)
    const { user, api } = renderGuests({ [GET_GUESTS]: mem.get })
    await user.click(await screen.findByRole('button', { name: 'Adicionar núcleo' }))
    const dialog = await screen.findByRole('dialog', { name: 'Novo núcleo' })

    await user.click(within(dialog).getByRole('button', { name: 'Criar núcleo' }))

    expect(await within(dialog).findByText('Informem o nome do núcleo.')).toBeVisible()
    expect(within(dialog).getByText('Escolham o lado do núcleo.')).toBeVisible()
    expect(within(dialog).getByText('Informem o nome da pessoa.')).toBeVisible()
    await waitFor(() =>
      expect(within(dialog).getAllByRole('textbox', { name: /^Nome/ })[0]).toHaveFocus(),
    )
    expect(api.callsTo(POST_HOUSEHOLDS)).toHaveLength(0)
  })

  it('cria o núcleo com a primeira pessoa e continua aberto para as demais', async () => {
    const mem = memory(EMPTY)
    const created = household({
      id: 'n-novo',
      name: 'Família Nova',
      side: 'Noiva',
      guests: [guest({ id: 'p-1', household_id: 'n-novo' })],
    })
    const { user, api } = renderGuests({
      [GET_GUESTS]: mem.get,
      [POST_HOUSEHOLDS]: mem.write({ households: [created] }),
      [POST_GUESTS('n-novo')]: mem.write((current) => ({
        households: [
          {
            ...created,
            guests: [
              ...created.guests,
              guest({ id: 'p-2', household_id: 'n-novo', name: 'Convidado Exemplo B' }),
            ],
          },
          ...current.households.slice(1),
        ],
      })),
    })
    const dialog = await fillNewHousehold(user)

    await user.click(within(dialog).getByRole('button', { name: 'Criar núcleo' }))

    await waitFor(() => expect(api.callsTo(POST_HOUSEHOLDS)).toHaveLength(1))
    expect(api.callsTo(POST_HOUSEHOLDS)[0]?.body).toEqual({
      household: {
        name: 'Família Nova',
        side: 'Noiva',
        street: null,
        number: null,
        complement: null,
        district: null,
        city: null,
        state: null,
        postal_code: null,
        note: null,
      },
      first_guest: {
        name: 'Convidado Exemplo A',
        band: 'Adulto',
        age: null,
        probability: 'Provável',
        dietary_restriction: null,
        note: null,
        phone: null,
        email: null,
      },
    })
    const next = await screen.findByRole('dialog', { name: 'Pessoas de Família Nova' })
    expect(within(next).getByText('Convidado Exemplo A')).toBeVisible()

    await user.type(within(next).getByRole('textbox', { name: 'Nome' }), 'Convidado Exemplo B')
    await user.click(within(next).getByRole('button', { name: 'Adicionar pessoa' }))

    expect(await within(next).findByText('Convidado Exemplo B foi adicionada.')).toBeVisible()
    expect(api.callsTo(POST_GUESTS('n-novo'))[0]?.body).toMatchObject({
      name: 'Convidado Exemplo B',
    })
    // o formulário segue aberto, limpo e com o foco de volta ao nome
    await waitFor(() => expect(within(next).getByRole('textbox', { name: 'Nome' })).toHaveValue(''))
    await waitFor(() => expect(within(next).getByRole('textbox', { name: 'Nome' })).toHaveFocus())

    await user.click(within(next).getByRole('button', { name: 'Concluir' }))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('nome repetido aparece no campo do nome, em português', async () => {
    const mem = memory(LIST)
    const { user } = renderGuests({
      [GET_GUESTS]: mem.get,
      [POST_HOUSEHOLDS]: problemResponse(409, 'duplicate_household_name', {
        detail: 'Já existe um núcleo com este nome. Escolham outro.',
      }),
    })
    const dialog = await fillNewHousehold(user, {
      household: 'Família Exemplo',
      guest: 'Convidado Exemplo Z',
    })

    await user.click(within(dialog).getByRole('button', { name: 'Criar núcleo' }))

    expect(
      await within(dialog).findByText('Já existe um núcleo com este nome. Escolham outro.'),
    ).toBeVisible()
    expect(within(dialog).getAllByRole('textbox', { name: /^Nome/ })[0]).toHaveAttribute(
      'aria-invalid',
      'true',
    )
  })

  it('telefone recusado pela API aparece no campo do telefone', async () => {
    const mem = memory(EMPTY)
    const { user } = renderGuests({
      [GET_GUESTS]: mem.get,
      [POST_HOUSEHOLDS]: problemResponse(422, 'invalid_phone', {
        detail: 'Confira o telefone: informe o DDD e o número.',
      }),
    })
    const dialog = await fillNewHousehold(user)
    await user.type(within(dialog).getByRole('textbox', { name: /^Telefone/ }), '123')

    await user.click(within(dialog).getByRole('button', { name: 'Criar núcleo' }))

    expect(
      await within(dialog).findByText('Confira o telefone: informe o DDD e o número.'),
    ).toBeVisible()
  })

  it('uma falha de rede avisa e mantém tudo o que foi digitado', async () => {
    const mem = memory(EMPTY)
    const { user } = renderGuests({
      [GET_GUESTS]: mem.get,
      [POST_HOUSEHOLDS]: () => {
        throw new TypeError('rede')
      },
    })
    const dialog = await fillNewHousehold(user)

    await user.click(within(dialog).getByRole('button', { name: 'Criar núcleo' }))

    expect(await within(dialog).findByText(/O que vocês escreveram continua aqui/)).toBeVisible()
    expect(within(dialog).getAllByRole('textbox', { name: /^Nome/ })[0]).toHaveValue('Família Nova')
  })
})

describe('editar o núcleo e as pessoas', () => {
  const open = (handlers = {}) => renderGuests({ ...handlers }, { nucleo: 'n-a' })

  it('edita o núcleo com a versão que a tela mostra', async () => {
    const mem = memory(LIST)
    const { user, api } = open({
      [GET_GUESTS]: mem.get,
      [PUT_HOUSEHOLD('n-a')]: mem.write((current) => ({
        households: current.households.map((h) =>
          h.id === 'n-a' ? { ...h, side: 'Noiva', version: 2 } : h,
        ),
      })),
    })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    await user.click(within(sheet).getByRole('button', { name: 'Editar núcleo' }))
    const dialog = await screen.findByRole('dialog', { name: 'Editar núcleo' })
    expect(within(dialog).getByRole('textbox', { name: 'Nome do núcleo' })).toHaveValue(
      'Família Exemplo',
    )
    expect(within(dialog).getByRole('textbox', { name: 'Logradouro' })).toHaveValue('Rua Exemplo')

    await user.click(within(dialog).getByRole('combobox', { name: 'Lado' }))
    await user.click(screen.getByRole('option', { name: 'Noiva' }))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar núcleo' }))

    await waitFor(() => expect(api.callsTo(PUT_HOUSEHOLD('n-a'))).toHaveLength(1))
    expect(api.callsTo(PUT_HOUSEHOLD('n-a'))[0]?.body).toMatchObject({
      name: 'Família Exemplo',
      side: 'Noiva',
      street: 'Rua Exemplo',
      version: 1,
    })
    await waitFor(() =>
      expect(screen.queryByRole('dialog', { name: 'Editar núcleo' })).not.toBeInTheDocument(),
    )
  })

  it('conflito de versão avisa e oferece ver a versão mais recente, sem sobrescrever', async () => {
    const mem = memory(LIST)
    const { user, api } = open({
      [GET_GUESTS]: mem.get,
      [PUT_HOUSEHOLD('n-a')]: problemResponse(409, 'version_conflict'),
    })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    await user.click(within(sheet).getByRole('button', { name: 'Editar núcleo' }))
    const dialog = await screen.findByRole('dialog', { name: 'Editar núcleo' })
    const nome = within(dialog).getByRole('textbox', { name: 'Nome do núcleo' })
    await user.clear(nome)
    await user.type(nome, 'Minha Família Exemplo')
    // enquanto isso, a outra pessoa mudou o nome
    mem.state.list = {
      households: LIST.households.map((h) =>
        h.id === 'n-a' ? { ...h, name: 'Família Exemplo da Outra', version: 2 } : h,
      ),
    }

    await user.click(within(dialog).getByRole('button', { name: 'Salvar núcleo' }))

    expect(await within(dialog).findByText(/foi alterado em outra tela/)).toBeVisible()
    await user.click(within(dialog).getByRole('button', { name: 'Ver a versão mais recente' }))

    await waitFor(() => expect(nome).toHaveValue('Família Exemplo da Outra'))
    expect(api.callsTo(PUT_HOUSEHOLD('n-a'))).toHaveLength(1)
  })

  it('o acompanhante pode ser salvo sem nome; a pessoa comum, não', async () => {
    const mem = memory(LIST)
    const { user, api } = open({
      [GET_GUESTS]: mem.get,
      [PUT_GUEST('p-b')]: mem.write(LIST),
    })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })

    await user.click(
      within(sheet).getByRole('button', { name: 'Editar Acompanhante de Convidado Exemplo A' }),
    )
    const companion = await screen.findByRole('dialog', { name: 'Editar pessoa' })
    await user.click(within(companion).getByRole('button', { name: 'Salvar pessoa' }))
    await waitFor(() => expect(api.callsTo(PUT_GUEST('p-b'))).toHaveLength(1))
    expect(api.callsTo(PUT_GUEST('p-b'))[0]?.body).toMatchObject({ name: null, version: 1 })
  })

  it('a pessoa comum não salva sem nome', async () => {
    const mem = memory(LIST)
    const { user, api } = open({ [GET_GUESTS]: mem.get })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    await user.click(within(sheet).getByRole('button', { name: 'Editar Convidado Exemplo C' }))
    const dialog = await screen.findByRole('dialog', { name: 'Editar pessoa' })
    const nome = within(dialog).getByRole('textbox', { name: 'Nome' })
    await user.clear(nome)

    await user.click(within(dialog).getByRole('button', { name: 'Salvar pessoa' }))

    expect(await within(dialog).findByText('Informem o nome da pessoa.')).toBeVisible()
    expect(api.callsTo(PUT_GUEST('p-c'))).toHaveLength(0)
  })

  it('a pessoa em Não irá mostra o motivo e o salva', async () => {
    const mem = memory(LIST)
    const { user, api } = open({ [GET_GUESTS]: mem.get, [PUT_GUEST('p-c')]: mem.write(LIST) })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    await user.click(within(sheet).getByRole('button', { name: 'Editar Convidado Exemplo C' }))
    const dialog = await screen.findByRole('dialog', { name: 'Editar pessoa' })
    const motivo = within(dialog).getByRole('textbox', { name: 'Motivo de não ir' })
    expect(motivo).toHaveValue('Viagem')
    await user.clear(motivo)
    await user.type(motivo, 'Trabalho')

    await user.click(within(dialog).getByRole('button', { name: 'Salvar pessoa' }))

    await waitFor(() => expect(api.callsTo(PUT_GUEST('p-c'))).toHaveLength(1))
    expect(api.callsTo(PUT_GUEST('p-c'))[0]?.body).toMatchObject({
      decline_reason: 'Trabalho',
      band: 'Criança pagante',
      age: 9,
      version: 1,
    })
  })

  it('acrescentar o acompanhante cria uma linha sem nome e a oferta some', async () => {
    const solo = household({
      id: 'n-s',
      name: 'Núcleo Solo Exemplo',
      guests: [guest({ id: 'p-s', household_id: 'n-s' })],
    })
    const mem = memory({ households: [solo] })
    const { user, api } = renderGuests(
      {
        [GET_GUESTS]: mem.get,
        [POST_COMPANION('p-s')]: mem.write({
          households: [
            household({
              ...solo,
              guests: [
                ...solo.guests,
                guest({
                  id: 'p-n',
                  household_id: 'n-s',
                  name: null,
                  companion_of_id: 'p-s',
                  holder_name: 'Convidado Exemplo A',
                }),
              ],
            }),
          ],
        }),
      },
      { nucleo: 'n-s' },
    )
    const sheet = await screen.findByRole('dialog', { name: 'Núcleo Solo Exemplo' })

    await user.click(within(sheet).getByRole('button', { name: 'Adicionar acompanhante' }))

    await waitFor(() => expect(api.callsTo(POST_COMPANION('p-s'))).toHaveLength(1))
    expect(api.callsTo(POST_COMPANION('p-s'))[0]?.body).toEqual({ name: null })
    expect(
      await within(sheet).findAllByText('Acompanhante de Convidado Exemplo A'),
    ).not.toHaveLength(0)
    expect(
      within(sheet).queryByRole('button', { name: 'Adicionar acompanhante' }),
    ).not.toBeInTheDocument()
  })
})
