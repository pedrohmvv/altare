import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { GuestList } from '@/features/guests/api/guests'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { guest, household, LIST, listOf } from '@/test/guest-fixtures'
import { GET_GUESTS, renderGuests } from '@/test/render-guests'

const PUT_INVITE = (id: string) => `PUT /api/v1/guests/households/${id}/invite`
const DELETE_INVITE = (id: string) => `DELETE /api/v1/guests/households/${id}/invite`

const SENT = {
  invite_sent_on: '2026-10-20',
  invite_channel: 'WhatsApp',
} as const

const withInvite = (): GuestList =>
  listOf(LIST.households.map((h) => (h.id === 'n-a' ? { ...h, ...SENT, version: 2 } : h)))

const allConfirmed = (): GuestList =>
  listOf([
    household({
      id: 'n-a',
      name: 'Família Exemplo',
      guests: [guest({ id: 'p-a', status: 'Confirmado' }), guest({ id: 'p-b', status: 'Não irá' })],
    }),
  ])

async function open(user: ReturnType<typeof renderGuests>['user'], label = 'Registrar convite') {
  const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
  await user.click(within(sheet).getByRole('button', { name: label }))
  return { sheet, dialog: await screen.findByRole('dialog', { name: 'Convite do núcleo' }) }
}

async function pickChannel(
  dialog: HTMLElement,
  user: ReturnType<typeof renderGuests>['user'],
  name = 'WhatsApp',
) {
  await user.click(within(dialog).getByRole('combobox', { name: 'Canal' }))
  await user.click(screen.getByRole('option', { name }))
}

describe('convite por núcleo (F-CNV-05)', () => {
  it('o núcleo sem envio diz que o convite ainda não foi enviado e oferece registrar', async () => {
    renderGuests({}, { nucleo: 'n-a' })
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })

    expect(within(sheet).getByText('Convite ainda não enviado.')).toBeVisible()
    expect(within(sheet).getByRole('button', { name: 'Registrar convite' })).toBeVisible()
    expect(within(sheet).queryByRole('button', { name: 'Limpar envio' })).not.toBeInTheDocument()
  })

  it('sem ninguém em rascunho, registra direto, sem a oferta', async () => {
    const { user, api } = renderGuests(
      {
        [GET_GUESTS]: jsonResponse(200, allConfirmed()),
        [PUT_INVITE('n-a')]: jsonResponse(200, allConfirmed()),
      },
      { nucleo: 'n-a' },
    )
    const { dialog } = await open(user)
    fireEvent.change(within(dialog).getByLabelText('Data do envio'), {
      target: { value: '2026-10-20' },
    })
    await pickChannel(dialog, user)

    await user.click(within(dialog).getByRole('button', { name: 'Salvar envio' }))

    await waitFor(() => expect(api.callsTo(PUT_INVITE('n-a'))).toHaveLength(1))
    expect(api.callsTo(PUT_INVITE('n-a'))[0]?.body).toEqual({
      sent_on: '2026-10-20',
      channel: 'WhatsApp',
      move_drafts: false,
      version: 1,
    })
    expect(screen.queryByText('Mover os rascunhos para Convidado?')).not.toBeInTheDocument()
  })

  it('com rascunhos, oferece mover; aceitar manda move_drafts true', async () => {
    const { user, api } = renderGuests(
      { [PUT_INVITE('n-a')]: jsonResponse(200, withInvite()) },
      { nucleo: 'n-a' },
    )
    const { dialog } = await open(user)
    fireEvent.change(within(dialog).getByLabelText('Data do envio'), {
      target: { value: '2026-10-20' },
    })
    await pickChannel(dialog, user, 'Impresso')

    await user.click(within(dialog).getByRole('button', { name: 'Salvar envio' }))

    expect(await within(dialog).findByText('Mover os rascunhos para Convidado?')).toBeVisible()
    expect(
      within(dialog).getByText('1 pessoa está em Rascunho. Querem marcá-la como Convidado agora?'),
    ).toBeVisible()
    expect(api.callsTo(PUT_INVITE('n-a'))).toHaveLength(0)

    await user.click(within(dialog).getByRole('button', { name: 'Mover para Convidado' }))

    await waitFor(() => expect(api.callsTo(PUT_INVITE('n-a'))).toHaveLength(1))
    expect(api.callsTo(PUT_INVITE('n-a'))[0]?.body).toMatchObject({
      channel: 'Impresso',
      move_drafts: true,
    })
  })

  it('recusar a oferta registra o envio e mantém os status', async () => {
    const { user, api } = renderGuests(
      { [PUT_INVITE('n-a')]: jsonResponse(200, withInvite()) },
      { nucleo: 'n-a' },
    )
    const { dialog } = await open(user)
    await pickChannel(dialog, user, 'E-mail')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar envio' }))

    await user.click(await within(dialog).findByRole('button', { name: 'Manter como estão' }))

    await waitFor(() => expect(api.callsTo(PUT_INVITE('n-a'))).toHaveLength(1))
    expect(api.callsTo(PUT_INVITE('n-a'))[0]?.body).toMatchObject({
      channel: 'E-mail',
      move_drafts: false,
    })
  })

  it('a data futura e o canal vazio são recusados na tela, sem enviar nada', async () => {
    const { user, api } = renderGuests({}, { nucleo: 'n-a' })
    const { dialog } = await open(user)
    fireEvent.change(within(dialog).getByLabelText('Data do envio'), {
      target: { value: '2999-01-01' },
    })

    await user.click(within(dialog).getByRole('button', { name: 'Salvar envio' }))

    expect(await within(dialog).findByText('A data não pode ser futura.')).toBeVisible()
    expect(within(dialog).getByText('Escolham o canal.')).toBeVisible()
    expect(api.callsTo(PUT_INVITE('n-a'))).toHaveLength(0)
  })

  it('a recusa da API aparece no formulário, em português', async () => {
    const { user } = renderGuests(
      {
        [GET_GUESTS]: jsonResponse(200, allConfirmed()),
        [PUT_INVITE('n-a')]: problemResponse(422, 'invalid_invite', {
          detail:
            'Informem a data e o canal do envio. A data é a de hoje ou de um dia que já passou.',
        }),
      },
      { nucleo: 'n-a' },
    )
    const { dialog } = await open(user)
    await pickChannel(dialog, user)

    await user.click(within(dialog).getByRole('button', { name: 'Salvar envio' }))

    expect(
      await within(dialog).findByText(/A data é a de hoje ou de um dia que já passou/),
    ).toBeVisible()
  })

  it('o núcleo com envio mostra a data e o canal, e limpar manda a versão e não toca em status', async () => {
    const { user, api } = renderGuests(
      {
        [GET_GUESTS]: jsonResponse(200, withInvite()),
        [DELETE_INVITE('n-a')]: jsonResponse(200, LIST),
      },
      { nucleo: 'n-a' },
    )
    const sheet = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    expect(within(sheet).getByText('Enviado em 20 out 2026 por WhatsApp.')).toBeVisible()
    expect(within(sheet).getByRole('button', { name: 'Editar envio' })).toBeVisible()

    await user.click(within(sheet).getByRole('button', { name: 'Limpar envio' }))

    await waitFor(() => expect(api.callsTo(DELETE_INVITE('n-a'))).toHaveLength(1))
    expect(
      new URL(api.callsTo(DELETE_INVITE('n-a'))[0]?.request.url ?? '').searchParams.get('version'),
    ).toBe('2')
  })

  it('conflito de versão avisa e oferece a versão mais recente', async () => {
    let current = LIST
    const { user } = renderGuests(
      {
        [GET_GUESTS]: () => jsonResponse(200, current),
        [PUT_INVITE('n-a')]: problemResponse(409, 'version_conflict'),
      },
      { nucleo: 'n-a' },
    )
    const { dialog } = await open(user)
    await pickChannel(dialog, user)
    current = withInvite()

    await user.click(within(dialog).getByRole('button', { name: 'Salvar envio' }))
    await user.click(await within(dialog).findByRole('button', { name: 'Manter como estão' }))
    expect(await within(dialog).findByText(/foi alterado em outra tela/)).toBeVisible()
    await user.click(within(dialog).getByRole('button', { name: 'Ver a versão mais recente' }))

    await waitFor(() =>
      expect(within(dialog).getByLabelText('Data do envio')).toHaveValue('2026-10-20'),
    )
  })

  it('a lista mostra o envio no cartão, e o núcleo sem envio não diz nada', async () => {
    renderGuests({ [GET_GUESTS]: jsonResponse(200, withInvite()) })
    const enviado = (await screen.findByRole('heading', { name: 'Família Exemplo' })).closest(
      'li',
    ) as HTMLElement
    const semEnvio = screen
      .getByRole('heading', { name: 'Outra Família Exemplo' })
      .closest('li') as HTMLElement

    expect(within(enviado).getByText('Convite enviado em 20 out 2026 · WhatsApp')).toBeVisible()
    expect(within(semEnvio).queryByText(/Convite enviado/)).not.toBeInTheDocument()
  })
})
