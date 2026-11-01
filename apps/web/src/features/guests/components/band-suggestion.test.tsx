import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { GuestList } from '@/features/guests/api/guests'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { guest, household, listOf } from '@/test/guest-fixtures'
import { GET_GUESTS, renderGuests, stubWideScreen } from '@/test/render-guests'

const PUT_GUEST = (id: string) => `PUT /api/v1/guests/people/${id}`

function withChild(over: Parameters<typeof guest>[0] = {}): GuestList {
  return listOf(
    [
      household({
        id: 'n-a',
        name: 'Família Exemplo',
        guests: [
          guest({ id: 'p-a', name: 'Convidado Exemplo A' }),
          guest({
            id: 'p-k',
            name: 'Criança Exemplo',
            band: 'Criança pagante',
            age: 4,
            suggested_band: 'Criança isenta',
            ...over,
          }),
        ],
      }),
    ],
    { exempt_until_age: 5, paying_until_age: 12 },
  )
}

const sheetOf = () => screen.findByRole('dialog', { name: 'Família Exemplo' })

describe('faixa sugerida pela idade (F-CNV-03)', () => {
  it('mostra a sugestão em texto e nunca muda a faixa sozinha', async () => {
    const { api } = renderGuests(
      { [GET_GUESTS]: jsonResponse(200, withChild()) },
      { nucleo: 'n-a' },
    )
    const sheet = await sheetOf()

    expect(within(sheet).getByText('Pela idade (4 anos): Criança isenta.')).toBeVisible()
    expect(within(sheet).getAllByText(/Criança pagante/).length).toBeGreaterThan(0)
    expect(api.callsTo(PUT_GUEST('p-k'))).toHaveLength(0)
  })

  it('aplicar manda a faixa nova com a versão que a tela viu', async () => {
    const { user, api } = renderGuests(
      {
        [GET_GUESTS]: jsonResponse(200, withChild()),
        [PUT_GUEST('p-k')]: jsonResponse(
          200,
          withChild({ band: 'Criança isenta', suggested_band: null }),
        ),
      },
      { nucleo: 'n-a' },
    )
    const sheet = await sheetOf()

    await user.click(
      within(sheet).getByRole('button', {
        name: 'Aplicar a faixa Criança isenta a Criança Exemplo',
      }),
    )

    await waitFor(() => expect(api.callsTo(PUT_GUEST('p-k'))).toHaveLength(1))
    expect(api.callsTo(PUT_GUEST('p-k'))[0]?.body).toMatchObject({
      band: 'Criança isenta',
      age: 4,
      name: 'Criança Exemplo',
      version: 1,
    })
    await waitFor(() => expect(within(sheet).queryByText(/Pela idade \(/)).not.toBeInTheDocument())
  })

  it('manter a faixa recusa a sugestão sem enviar nada', async () => {
    const { user, api } = renderGuests(
      { [GET_GUESTS]: jsonResponse(200, withChild()) },
      { nucleo: 'n-a' },
    )
    const sheet = await sheetOf()

    await user.click(
      within(sheet).getByRole('button', { name: 'Manter a faixa de Criança Exemplo' }),
    )

    expect(within(sheet).queryByText(/Pela idade \(/)).not.toBeInTheDocument()
    expect(api.callsTo(PUT_GUEST('p-k'))).toHaveLength(0)
  })

  it('aplicar "Adulto" tira a idade, que só vale para criança', async () => {
    const { user, api } = renderGuests(
      {
        [GET_GUESTS]: jsonResponse(200, withChild({ age: 15, suggested_band: 'Adulto' })),
        [PUT_GUEST('p-k')]: jsonResponse(
          200,
          withChild({ band: 'Adulto', age: null, suggested_band: null }),
        ),
      },
      { nucleo: 'n-a' },
    )
    const sheet = await sheetOf()

    await user.click(
      within(sheet).getByRole('button', { name: 'Aplicar a faixa Adulto a Criança Exemplo' }),
    )

    await waitFor(() => expect(api.callsTo(PUT_GUEST('p-k'))).toHaveLength(1))
    expect(api.callsTo(PUT_GUEST('p-k'))[0]?.body).toMatchObject({ band: 'Adulto', age: null })
  })

  it('um conflito de versão aparece no aviso, sem sobrescrever', async () => {
    const { user } = renderGuests(
      {
        [GET_GUESTS]: jsonResponse(200, withChild()),
        [PUT_GUEST('p-k')]: problemResponse(409, 'version_conflict'),
      },
      { nucleo: 'n-a' },
    )
    const sheet = await sheetOf()

    await user.click(within(sheet).getByRole('button', { name: /Aplicar a faixa/ }))

    expect(await within(sheet).findByText(/foi alterado em outra tela/)).toBeVisible()
  })

  it('sem idade ou sem sugestão, nenhum aviso aparece', async () => {
    renderGuests(
      { [GET_GUESTS]: jsonResponse(200, withChild({ suggested_band: null })) },
      { nucleo: 'n-a' },
    )
    const sheet = await sheetOf()

    expect(within(sheet).queryByText(/Pela idade \(/)).not.toBeInTheDocument()
  })

  it('na tabela, a sugestão aparece como uma dica discreta ao lado da faixa', async () => {
    stubWideScreen()
    renderGuests({ [GET_GUESTS]: jsonResponse(200, withChild()) })
    const tabela = await screen.findByRole('table')

    expect(within(tabela).getByText('Pela idade: Criança isenta')).toBeVisible()
  })
})
