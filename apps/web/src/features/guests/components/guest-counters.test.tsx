import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { GuestList } from '@/features/guests/api/guests'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { LIST } from '@/test/guest-fixtures'
import { GET_GUESTS, renderGuests } from '@/test/render-guests'

const PUT_SETTINGS = 'PUT /api/v1/guests/settings'

// Os pesos do exemplo da spec: nunca valores do casal.
const WEIGHTS = { certain_pct: 100, probable_pct: 70, phase_2_pct: 30 }

function weighted(list: GuestList, rounded: number, adults: number, children: number): GuestList {
  return {
    ...list,
    headcount: {
      ...list.headcount,
      weighted_adults_hundredths: adults,
      weighted_paying_children_hundredths: children,
      weighted_rounded_up: rounded,
    },
    settings: { ...list.settings, weights: WEIGHTS, version: 2 },
  }
}

const counters = async () =>
  within(await screen.findByRole('region', { name: 'Contadores da lista' }))

describe('contadores (F-CNV-06)', () => {
  it('mostram o total nominal, os confirmados e os que não irão, por faixa', async () => {
    renderGuests()
    const region = await counters()

    // LIST: 3 adultos na lista (1 confirmado), 1 criança pagante que não irá.
    expect(region.getByText('Total nominal').closest('div')).toHaveTextContent('3')
    expect(region.getByText('Total nominal').closest('div')).toHaveTextContent('3 adultos')
    expect(region.getByText('Confirmados').closest('div')).toHaveTextContent('1 adulto')
    expect(region.getByText('Não irão: 1')).toBeVisible()
  })

  it('sem pesos, o ponderado diz "defina os pesos" e não mostra número nenhum', async () => {
    renderGuests()
    const region = await counters()

    const bloco = region.getByText('Estimado ponderado').closest('div') as HTMLElement
    expect(within(bloco).getByText('Defina os pesos')).toBeVisible()
    expect(bloco.textContent).not.toMatch(/\d/)
  })

  it('com pesos, mostra o ponderado já arredondado para cima e o valor exato por faixa', async () => {
    renderGuests({ [GET_GUESTS]: jsonResponse(200, weighted(LIST, 5, 340, 100)) })
    const region = await counters()

    const bloco = region.getByText('Estimado ponderado').closest('div') as HTMLElement
    expect(bloco).toHaveTextContent('5')
    expect(bloco).toHaveTextContent('Adultos 3,4 · crianças pagantes 1')
    expect(bloco).toHaveTextContent('arredondado para cima')
  })
})

describe('pesos e idades (F-CNV-03 e F-CNV-06)', () => {
  async function openSettings(user: ReturnType<typeof renderGuests>['user']) {
    await user.click(await screen.findByRole('button', { name: 'Ajustar pesos e idades' }))
    return screen.findByRole('dialog', { name: 'Pesos e idades das crianças' })
  }

  it('abre vazio, porque os pesos e os limites são decisões de vocês', async () => {
    const { user } = renderGuests()
    const dialog = await openSettings(user)

    for (const name of [
      'Certeza',
      'Provável',
      'Fase 2',
      'Criança isenta até',
      'Criança pagante até',
    ]) {
      expect(within(dialog).getByRole('textbox', { name })).toHaveValue('')
    }
  })

  it('define os pesos e os limites e o ponderado aparece na mesma resposta', async () => {
    const { user, api } = renderGuests({
      [PUT_SETTINGS]: () => jsonResponse(200, weighted(LIST, 5, 340, 100)),
    })
    const dialog = await openSettings(user)

    await user.type(within(dialog).getByRole('textbox', { name: 'Certeza' }), '100')
    await user.type(within(dialog).getByRole('textbox', { name: 'Provável' }), '70')
    await user.type(within(dialog).getByRole('textbox', { name: 'Fase 2' }), '30')
    await user.type(within(dialog).getByRole('textbox', { name: 'Criança isenta até' }), '5')
    await user.type(within(dialog).getByRole('textbox', { name: 'Criança pagante até' }), '12')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar' }))

    await waitFor(() => expect(api.callsTo(PUT_SETTINGS)).toHaveLength(1))
    expect(api.callsTo(PUT_SETTINGS)[0]?.body).toEqual({
      weights: WEIGHTS,
      exempt_until_age: 5,
      paying_until_age: 12,
      version: 1,
    })
    const bloco = (await counters()).getByText('Estimado ponderado').closest('div') as HTMLElement
    await waitFor(() => expect(bloco).toHaveTextContent('Adultos 3,4'))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('os três pesos andam juntos: com um faltando, o erro aponta quem falta e nada é enviado', async () => {
    const { user, api } = renderGuests()
    const dialog = await openSettings(user)
    await user.type(within(dialog).getByRole('textbox', { name: 'Certeza' }), '100')

    await user.click(within(dialog).getByRole('button', { name: 'Salvar' }))

    expect(
      await within(dialog).findAllByText(
        'Definam os três pesos juntos, ou deixem os três em branco.',
      ),
    ).toHaveLength(2)
    expect(api.callsTo(PUT_SETTINGS)).toHaveLength(0)
  })

  it('peso fora de 0 a 100 e idade acima de 17 são recusados na tela', async () => {
    const { user, api } = renderGuests()
    const dialog = await openSettings(user)
    await user.type(within(dialog).getByRole('textbox', { name: 'Certeza' }), '100')
    await user.type(within(dialog).getByRole('textbox', { name: 'Provável' }), '101')
    await user.type(within(dialog).getByRole('textbox', { name: 'Fase 2' }), '30')
    await user.type(within(dialog).getByRole('textbox', { name: 'Criança pagante até' }), '18')

    await user.click(within(dialog).getByRole('button', { name: 'Salvar' }))

    expect(await within(dialog).findByText('Use um número inteiro de 0 a 100.')).toBeVisible()
    expect(within(dialog).getByText('Use uma idade de 0 a 17 anos.')).toBeVisible()
    expect(api.callsTo(PUT_SETTINGS)).toHaveLength(0)
  })

  it('conflito de versão avisa e oferece a versão mais recente', async () => {
    let current: GuestList = LIST
    const { user } = renderGuests({
      [GET_GUESTS]: () => jsonResponse(200, current),
      [PUT_SETTINGS]: problemResponse(409, 'version_conflict'),
    })
    const dialog = await openSettings(user)
    await user.type(within(dialog).getByRole('textbox', { name: 'Certeza' }), '90')
    await user.type(within(dialog).getByRole('textbox', { name: 'Provável' }), '60')
    await user.type(within(dialog).getByRole('textbox', { name: 'Fase 2' }), '20')
    current = weighted(LIST, 5, 340, 100)

    await user.click(within(dialog).getByRole('button', { name: 'Salvar' }))
    expect(await within(dialog).findByText(/foi alterado em outra tela/)).toBeVisible()
    await user.click(within(dialog).getByRole('button', { name: 'Ver a versão mais recente' }))

    await waitFor(() =>
      expect(within(dialog).getByRole('textbox', { name: 'Certeza' })).toHaveValue('100'),
    )
    expect(within(dialog).getByRole('textbox', { name: 'Provável' })).toHaveValue('70')
  })
})
