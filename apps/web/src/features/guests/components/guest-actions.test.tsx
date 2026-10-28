import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { GuestList, GuestStatus } from '@/features/guests/api/guests'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { household, LIST } from '@/test/guest-fixtures'
import { GET_GUESTS, renderGuests } from '@/test/render-guests'

const BASE = '/api/v1/guests'
const STATUS = (id: string) => `PUT ${BASE}/people/${id}/status`
const MOVE = (id: string) => `PUT ${BASE}/people/${id}/household`
const DELETE_GUEST = (id: string) => `DELETE ${BASE}/people/${id}`
const RESTORE_GUEST = (id: string) => `POST ${BASE}/people/${id}/restore`
const DELETE_HOUSEHOLD = (id: string) => `DELETE ${BASE}/households/${id}`
const RESTORE_HOUSEHOLD = (id: string) => `POST ${BASE}/households/${id}/restore`
const HISTORY = (id: string) => `GET ${BASE}/people/${id}/history`

/** A API falsa com memória: a leitura devolve o que a última escrita deixou. */
function memory(initial: GuestList) {
  const state = { list: initial }
  return {
    state,
    get: () => jsonResponse(200, state.list),
    write: (next: (current: GuestList) => GuestList) => () => {
      state.list = next(state.list)
      return jsonResponse(200, state.list)
    },
  }
}

const withStatus = (list: GuestList, id: string, status: GuestStatus): GuestList => ({
  households: list.households.map((h) => {
    const guests = h.guests.map((g) =>
      g.id === id ? { ...g, status, version: g.version + 1, decline_reason: null } : g,
    )
    return { ...h, guests, summary: household({ guests }).summary }
  }),
})

const trigger = (name: string, status: string) =>
  screen.findByRole('button', { name: `Mudar o status de ${name}, hoje ${status}` })

describe('status em um toque (F-CNV-04)', () => {
  it('muda o status pelo selo e o resumo do núcleo acompanha', async () => {
    const mem = memory(LIST)
    const { user, api } = renderGuests({
      [GET_GUESTS]: mem.get,
      [STATUS('p-d')]: mem.write((c) => withStatus(c, 'p-d', 'Confirmado')),
    })
    await user.click(await trigger('Convidado Exemplo D', 'Rascunho'))
    const card = await screen.findByRole('dialog', { name: 'Status de Convidado Exemplo D' })

    await user.click(within(card).getByRole('button', { name: 'Confirmado' }))

    await waitFor(() => expect(api.callsTo(STATUS('p-d'))).toHaveLength(1))
    expect(api.callsTo(STATUS('p-d'))[0]?.body).toEqual({
      status: 'Confirmado',
      reason: null,
      version: 1,
    })
    expect(await screen.findByText('1 de 1 confirmado')).toBeVisible()
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('Não irá pergunta o motivo, que é opcional, e o envia', async () => {
    const mem = memory(LIST)
    const { user, api } = renderGuests({
      [GET_GUESTS]: mem.get,
      [STATUS('p-d')]: mem.write((c) => withStatus(c, 'p-d', 'Não irá')),
    })
    await user.click(await trigger('Convidado Exemplo D', 'Rascunho'))
    const card = await screen.findByRole('dialog', { name: 'Status de Convidado Exemplo D' })
    await user.click(within(card).getByRole('button', { name: 'Não irá' }))
    expect(api.callsTo(STATUS('p-d'))).toHaveLength(0)

    await user.type(within(card).getByRole('textbox', { name: 'Motivo de não ir' }), 'Viagem')
    await user.click(within(card).getByRole('button', { name: 'Confirmar' }))

    await waitFor(() => expect(api.callsTo(STATUS('p-d'))).toHaveLength(1))
    expect(api.callsTo(STATUS('p-d'))[0]?.body).toEqual({
      status: 'Não irá',
      reason: 'Viagem',
      version: 1,
    })
  })

  it('Não irá sem motivo salva normalmente', async () => {
    const mem = memory(LIST)
    const { user, api } = renderGuests({
      [GET_GUESTS]: mem.get,
      [STATUS('p-d')]: mem.write((c) => withStatus(c, 'p-d', 'Não irá')),
    })
    await user.click(await trigger('Convidado Exemplo D', 'Rascunho'))
    const card = await screen.findByRole('dialog')
    await user.click(within(card).getByRole('button', { name: 'Não irá' }))

    await user.click(within(card).getByRole('button', { name: 'Confirmar' }))

    await waitFor(() => expect(api.callsTo(STATUS('p-d'))).toHaveLength(1))
    expect(api.callsTo(STATUS('p-d'))[0]?.body).toMatchObject({ reason: null })
  })

  it('conflito de versão avisa e oferece a versão mais recente, sem sobrescrever', async () => {
    const mem = memory(LIST)
    const { user, api } = renderGuests({
      [GET_GUESTS]: mem.get,
      [STATUS('p-d')]: problemResponse(409, 'version_conflict'),
    })
    await user.click(await trigger('Convidado Exemplo D', 'Rascunho'))
    const card = await screen.findByRole('dialog')
    await user.click(within(card).getByRole('button', { name: 'Confirmado' }))

    expect(await within(card).findByText(/foi alterado em outra tela/)).toBeVisible()
    mem.state.list = withStatus(LIST, 'p-d', 'Convidado')
    await user.click(within(card).getByRole('button', { name: 'Ver a versão mais recente' }))

    expect(await trigger('Convidado Exemplo D', 'Convidado')).toBeVisible()
    expect(api.callsTo(STATUS('p-d'))).toHaveLength(1)
  })

  it('escolher o status em que a pessoa já está não envia nada', async () => {
    const mem = memory(LIST)
    const { user, api } = renderGuests({ [GET_GUESTS]: mem.get })
    await user.click(await trigger('Convidado Exemplo D', 'Rascunho'))
    const card = await screen.findByRole('dialog')

    await user.click(within(card).getByRole('button', { name: 'Rascunho' }))

    expect(api.callsTo(STATUS('p-d'))).toHaveLength(0)
  })
})

describe('mover, excluir e desfazer (F-CNV-01 e F-CNV-02)', () => {
  const open = (handlers = {}, id = 'n-a') => renderGuests(handlers, { nucleo: id })

  it('move a pessoa para outro núcleo', async () => {
    const mem = memory(LIST)
    const { user, api } = open({
      [GET_GUESTS]: mem.get,
      [MOVE('p-c')]: mem.write(() => LIST),
    })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    await user.click(
      within(sheet).getByRole('button', { name: 'Mover de núcleo: Convidado Exemplo C' }),
    )
    const dialog = await screen.findByRole('dialog', { name: 'Mover de núcleo' })
    await user.click(within(dialog).getByRole('combobox', { name: 'Núcleo de destino' }))
    await user.click(screen.getByRole('option', { name: 'Outra Família Exemplo' }))

    await user.click(within(dialog).getByRole('button', { name: 'Mover' }))

    await waitFor(() => expect(api.callsTo(MOVE('p-c'))).toHaveLength(1))
    expect(api.callsTo(MOVE('p-c'))[0]?.body).toEqual({ household_id: 'n-b', version: 1 })
  })

  it('exige escolher o destino e mostra a recusa da API quando é a última pessoa', async () => {
    const mem = memory(LIST)
    const { user } = open(
      {
        [GET_GUESTS]: mem.get,
        [MOVE('p-d')]: problemResponse(422, 'last_guest_in_household', {
          detail: 'Este é o último convidado do núcleo. Excluam o núcleo ou deixem alguém nele.',
        }),
      },
      'n-b',
    )
    const sheet = await screen.findByRole('dialog', { name: 'Outra Família Exemplo' })
    await user.click(
      within(sheet).getByRole('button', { name: 'Mover de núcleo: Convidado Exemplo D' }),
    )
    const dialog = await screen.findByRole('dialog', { name: 'Mover de núcleo' })

    await user.click(within(dialog).getByRole('button', { name: 'Mover' }))
    expect(await within(dialog).findByText('Escolham o núcleo de destino.')).toBeVisible()

    await user.click(within(dialog).getByRole('combobox', { name: 'Núcleo de destino' }))
    await user.click(screen.getByRole('option', { name: 'Família Exemplo' }))
    await user.click(within(dialog).getByRole('button', { name: 'Mover' }))
    expect(await within(dialog).findByText(/último convidado do núcleo/)).toBeVisible()
  })

  it('o acompanhante não tem botão de mover: vai junto com o titular', async () => {
    const mem = memory(LIST)
    open({ [GET_GUESTS]: mem.get })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })

    expect(
      within(sheet).getByText('O acompanhante muda de núcleo junto com o titular.'),
    ).toBeVisible()
  })

  it('exclui a pessoa, avisa e o Desfazer a restaura', async () => {
    const mem = memory(LIST)
    const { user, api } = open({
      [GET_GUESTS]: mem.get,
      [DELETE_GUEST('p-c')]: mem.write(() => LIST),
      [RESTORE_GUEST('p-c')]: mem.write(() => LIST),
    })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    await user.click(
      within(sheet).getByRole('button', { name: 'Excluir pessoa: Convidado Exemplo C' }),
    )
    const dialog = await screen.findByRole('dialog', { name: 'Excluir Convidado Exemplo C?' })
    expect(within(dialog).getByText(/fica guardada e pode ser restaurada/)).toBeVisible()

    await user.click(within(dialog).getByRole('button', { name: 'Excluir pessoa' }))

    await waitFor(() => expect(api.callsTo(DELETE_GUEST('p-c'))).toHaveLength(1))
    const url = new URL(api.callsTo(DELETE_GUEST('p-c'))[0]?.request.url ?? '')
    expect(url.searchParams.get('version')).toBe('1')
    expect(url.searchParams.has('companion')).toBe(false)
    // O Desfazer fica dentro do painel: um aviso fora dele ficaria escondido do teclado e do leitor.
    expect(
      await within(sheet).findByText('Convidado Exemplo C foi excluído da lista.'),
    ).toBeVisible()

    await user.click(within(sheet).getByRole('button', { name: 'Desfazer' }))
    await waitFor(() => expect(api.callsTo(RESTORE_GUEST('p-c'))).toHaveLength(1))
    await waitFor(() =>
      expect(
        within(sheet).queryByText('Convidado Exemplo C foi excluído da lista.'),
      ).not.toBeInTheDocument(),
    )
  })

  it('o titular com acompanhante sem nome só pode excluir os dois', async () => {
    const mem = memory(LIST)
    const { user, api } = open({
      [GET_GUESTS]: mem.get,
      [DELETE_GUEST('p-a')]: mem.write(() => LIST),
    })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    await user.click(
      within(sheet).getByRole('button', { name: 'Excluir pessoa: Convidado Exemplo A' }),
    )
    const dialog = await screen.findByRole('dialog', { name: 'Excluir Convidado Exemplo A?' })

    expect(within(dialog).getByRole('radio', { name: 'Manter o acompanhante' })).toBeDisabled()
    expect(
      within(dialog).getByText('Sem nome, o acompanhante sai junto com o titular.'),
    ).toBeVisible()
    await user.click(within(dialog).getByRole('button', { name: 'Excluir pessoa' }))

    await waitFor(() => expect(api.callsTo(DELETE_GUEST('p-a'))).toHaveLength(1))
    expect(
      new URL(api.callsTo(DELETE_GUEST('p-a'))[0]?.request.url ?? '').searchParams.get('companion'),
    ).toBe('delete')
  })

  it('o acompanhante com nome pode ficar na lista quando o titular sai', async () => {
    const named = {
      households: LIST.households.map((h) =>
        h.id === 'n-a'
          ? household({
              ...h,
              guests: h.guests.map((g) =>
                g.id === 'p-b' ? { ...g, name: 'Acompanhante Exemplo' } : g,
              ),
            })
          : h,
      ),
    }
    const mem = memory(named)
    const { user, api } = open({
      [GET_GUESTS]: mem.get,
      [DELETE_GUEST('p-a')]: mem.write(() => named),
    })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    await user.click(
      within(sheet).getByRole('button', { name: 'Excluir pessoa: Convidado Exemplo A' }),
    )
    const dialog = await screen.findByRole('dialog', { name: 'Excluir Convidado Exemplo A?' })

    await user.click(
      within(dialog).getByRole('radio', { name: 'Manter Acompanhante Exemplo na lista' }),
    )
    await user.click(within(dialog).getByRole('button', { name: 'Excluir pessoa' }))

    await waitFor(() => expect(api.callsTo(DELETE_GUEST('p-a'))).toHaveLength(1))
    expect(
      new URL(api.callsTo(DELETE_GUEST('p-a'))[0]?.request.url ?? '').searchParams.get('companion'),
    ).toBe('keep')
  })

  it('a recusa de excluir a última pessoa aparece no diálogo, em português', async () => {
    const mem = memory(LIST)
    const { user } = open(
      {
        [GET_GUESTS]: mem.get,
        [DELETE_GUEST('p-d')]: problemResponse(422, 'last_guest_in_household', {
          detail: 'Este é o último convidado do núcleo. Excluam o núcleo ou deixem alguém nele.',
        }),
      },
      'n-b',
    )
    const sheet = await screen.findByRole('dialog', { name: 'Outra Família Exemplo' })
    await user.click(
      within(sheet).getByRole('button', { name: 'Excluir pessoa: Convidado Exemplo D' }),
    )
    const dialog = await screen.findByRole('dialog', { name: 'Excluir Convidado Exemplo D?' })

    await user.click(within(dialog).getByRole('button', { name: 'Excluir pessoa' }))

    expect(await within(dialog).findByText(/último convidado do núcleo/)).toBeVisible()
  })

  it('exclui o núcleo com confirmação, fecha o painel e o Desfazer o restaura', async () => {
    const mem = memory(LIST)
    const { user, api } = open({
      [GET_GUESTS]: mem.get,
      [DELETE_HOUSEHOLD('n-a')]: mem.write((c) => ({
        households: c.households.filter((h) => h.id !== 'n-a'),
      })),
      [RESTORE_HOUSEHOLD('n-a')]: mem.write(() => LIST),
    })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    await user.click(within(sheet).getByRole('button', { name: 'Excluir núcleo' }))
    const dialog = await screen.findByRole('dialog', { name: 'Excluir Família Exemplo?' })
    expect(within(dialog).getByText(/as 3 pessoas saem da lista e dos contadores/)).toBeVisible()

    await user.click(within(dialog).getByRole('button', { name: 'Excluir núcleo' }))

    await waitFor(() => expect(api.callsTo(DELETE_HOUSEHOLD('n-a'))).toHaveLength(1))
    expect(
      new URL(api.callsTo(DELETE_HOUSEHOLD('n-a'))[0]?.request.url ?? '').searchParams.get(
        'version',
      ),
    ).toBe('1')
    expect(await screen.findByText('Família Exemplo foi excluído da lista.')).toBeVisible()
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(screen.queryByRole('heading', { name: 'Família Exemplo' })).not.toBeInTheDocument()

    await user.click(await screen.findByRole('button', { name: 'Desfazer' }))
    await waitFor(() => expect(api.callsTo(RESTORE_HOUSEHOLD('n-a'))).toHaveLength(1))
    expect(await screen.findByRole('heading', { name: 'Família Exemplo' })).toBeVisible()
  })
})

describe('histórico de status (F-CNV-04, regra 4)', () => {
  it('mostra quem mudou, quando e de qual status para qual, com o motivo', async () => {
    const mem = memory(LIST)
    const { user } = renderGuests(
      {
        [GET_GUESTS]: mem.get,
        [HISTORY('p-c')]: jsonResponse(200, [
          {
            id: 'h-1',
            from_status: 'Rascunho',
            to_status: 'Não irá',
            reason: 'Viagem',
            profile: 'Noiva',
            changed_at: '2026-10-28T15:30:00Z',
          },
        ]),
      },
      { nucleo: 'n-a' },
    )
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    const person = within(sheet).getByText('Convidado Exemplo C').closest('li') as HTMLElement

    await user.click(within(person).getByRole('button', { name: 'Ver histórico' }))

    expect(await within(person).findByText('De Rascunho para Não irá')).toBeVisible()
    expect(within(person).getByText('Motivo: Viagem')).toBeVisible()
    expect(within(person).getByText(/Noiva ·/)).toBeVisible()
  })

  it('sem mudanças, diz que ainda não há nenhuma', async () => {
    const mem = memory(LIST)
    const { user } = renderGuests(
      { [GET_GUESTS]: mem.get, [HISTORY('p-d')]: jsonResponse(200, []) },
      { nucleo: 'n-b' },
    )
    const sheet = await screen.findByRole('dialog', { name: 'Outra Família Exemplo' })

    await user.click(within(sheet).getByRole('button', { name: 'Ver histórico' }))

    expect(await within(sheet).findByText('Ainda sem mudanças de status.')).toBeVisible()
  })
})
