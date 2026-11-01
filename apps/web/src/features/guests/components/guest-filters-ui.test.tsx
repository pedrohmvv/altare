import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse } from '@/test/fake-api'
import { guest, household, LIST, listOf } from '@/test/guest-fixtures'
import { GET_GUESTS, renderGuests } from '@/test/render-guests'

const COM_COMUM = listOf([
  ...LIST.households,
  household({
    id: 'n-c',
    name: 'Amigos Exemplo',
    side: 'Comum',
    guests: [guest({ id: 'p-e', household_id: 'n-c', name: 'Pedro Exemplo' })],
  }),
])

const heading = (name: string) => screen.findByRole('heading', { name })
const gone = (name: string) => screen.queryByRole('heading', { name })

describe('busca e filtros (F-CNV-07)', () => {
  it('buscar "silva" mostra só quem tem Silva, sem diferenciar caixa nem acento', async () => {
    const lista = listOf([
      household({
        id: 'n-s',
        name: 'Família Silva Exemplo',
        guests: [guest({ id: 'a', household_id: 'n-s', name: 'Maria da Silva Exemplo' })],
      }),
      household({
        id: 'n-x',
        name: 'Família Outra Exemplo',
        guests: [guest({ id: 'b', household_id: 'n-x', name: 'João Exemplo' })],
      }),
    ])
    const { user } = renderGuests({ [GET_GUESTS]: jsonResponse(200, lista) })
    await heading('Família Silva Exemplo')

    await user.type(screen.getByRole('searchbox', { name: 'Buscar por nome' }), 'SÍLVA')

    expect(await heading('Família Silva Exemplo')).toBeVisible()
    expect(gone('Família Outra Exemplo')).not.toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('1 de 2 pessoas')
  })

  it('um chip filtra, diz "N de M pessoas" e limpar volta à lista inteira', async () => {
    const { user } = renderGuests({ [GET_GUESTS]: jsonResponse(200, COM_COMUM) })
    await heading('Família Exemplo')

    await user.click(screen.getByRole('button', { name: 'Noiva' }))

    expect(await heading('Outra Família Exemplo')).toBeVisible()
    expect(gone('Família Exemplo')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Noiva' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('status')).toHaveTextContent('1 de 5 pessoas')

    await user.click(screen.getByRole('button', { name: 'Limpar filtros' }))

    expect(await heading('Família Exemplo')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Noiva' })).toHaveAttribute('aria-pressed', 'false')
  })

  it('tocar de novo no mesmo chip tira o filtro', async () => {
    const { user } = renderGuests({ [GET_GUESTS]: jsonResponse(200, COM_COMUM) })
    await heading('Família Exemplo')

    await user.click(screen.getByRole('button', { name: 'Convite não enviado' }))
    expect(gone('Família Exemplo')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Convite não enviado' }))

    expect(await heading('Família Exemplo')).toBeVisible()
  })

  it('filtra por status e por restrição alimentar, e some o núcleo sem ninguém', async () => {
    const { user } = renderGuests({ [GET_GUESTS]: jsonResponse(200, COM_COMUM) })
    await heading('Família Exemplo')

    await user.click(screen.getByRole('button', { name: 'Com restrição alimentar' }))

    // só o Convidado Exemplo A (Sem lactose) tem restrição na lista de exemplo
    expect(await heading('Família Exemplo')).toBeVisible()
    expect(gone('Outra Família Exemplo')).not.toBeInTheDocument()
    expect(gone('Amigos Exemplo')).not.toBeInTheDocument()
  })

  it('quando nada corresponde, acolhe e oferece limpar', async () => {
    const { user } = renderGuests({ [GET_GUESTS]: jsonResponse(200, COM_COMUM) })
    await heading('Família Exemplo')

    await user.type(screen.getByRole('searchbox', { name: 'Buscar por nome' }), 'xyz')

    expect(await screen.findByRole('heading', { name: 'Nenhuma pessoa corresponde' })).toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Limpar filtros e busca' }))
    expect(await heading('Família Exemplo')).toBeVisible()
    expect(screen.getByRole('searchbox', { name: 'Buscar por nome' })).toHaveValue('')
  })

  it('os contadores do topo continuam globais mesmo com filtro', async () => {
    const { user } = renderGuests({ [GET_GUESTS]: jsonResponse(200, COM_COMUM) })
    const regiao = await screen.findByRole('region', { name: 'Contadores da lista' })
    const antes = regiao.textContent

    await user.click(screen.getByRole('button', { name: 'Noiva' }))

    expect(screen.getByRole('region', { name: 'Contadores da lista' }).textContent).toBe(antes)
  })

  it('o painel do núcleo abre pela URL mesmo quando o filtro o esconde da lista', async () => {
    renderGuests({ [GET_GUESTS]: jsonResponse(200, COM_COMUM) }, { nucleo: 'n-b', lado: 'noivo' })

    expect(await screen.findByRole('dialog', { name: 'Outra Família Exemplo' })).toBeVisible()
  })
})

describe('lente Minha visão (F-CNV-07)', () => {
  it('com o Noivo, mostra o lado dele e o Comum, e o outro lado fica a um toque', async () => {
    const { user } = renderGuests(
      { [GET_GUESTS]: jsonResponse(200, COM_COMUM) },
      {},
      { profile: 'Noivo', lens: 'minha' },
    )

    expect(await heading('Família Exemplo')).toBeVisible()
    expect(await heading('Amigos Exemplo')).toBeVisible()
    expect(gone('Outra Família Exemplo')).not.toBeInTheDocument()
    expect(screen.getByText('Minha visão: o lado do Noivo e o Comum.')).toBeVisible()
    expect(screen.getByRole('status')).toHaveTextContent('4 de 5 pessoas')

    await user.click(screen.getByRole('button', { name: 'Mostrar também o outro lado' }))

    expect(await heading('Outra Família Exemplo')).toBeVisible()
  })

  it('com a Noiva, mostra o lado dela e o Comum', async () => {
    renderGuests(
      { [GET_GUESTS]: jsonResponse(200, COM_COMUM) },
      {},
      { profile: 'Noiva', lens: 'minha' },
    )

    expect(await heading('Outra Família Exemplo')).toBeVisible()
    expect(await heading('Amigos Exemplo')).toBeVisible()
    expect(gone('Família Exemplo')).not.toBeInTheDocument()
  })

  it('na lente Casal mostra todos e não oferece "o outro lado"', async () => {
    renderGuests({ [GET_GUESTS]: jsonResponse(200, COM_COMUM) })

    expect(await heading('Família Exemplo')).toBeVisible()
    expect(await heading('Outra Família Exemplo')).toBeVisible()
    expect(
      screen.queryByRole('button', { name: 'Mostrar também o outro lado' }),
    ).not.toBeInTheDocument()
  })

  it('um filtro de lado explícito vence a lente', async () => {
    renderGuests(
      { [GET_GUESTS]: jsonResponse(200, COM_COMUM) },
      { lado: 'noiva' },
      { profile: 'Noivo', lens: 'minha' },
    )

    expect(await heading('Outra Família Exemplo')).toBeVisible()
    expect(
      within(document.body).queryByRole('heading', { name: 'Família Exemplo' }),
    ).not.toBeInTheDocument()
  })
})
