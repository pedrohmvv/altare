import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { guest, household, listOf } from '@/test/guest-fixtures'
import { GET_GUESTS, renderGuests, stubWideScreen } from '@/test/render-guests'

describe('lista de convidados: leitura', () => {
  it('mostra o carregamento e depois os núcleos', async () => {
    renderGuests()

    expect(screen.getByText('Carregando a lista de convidados…')).toBeVisible()
    expect(await screen.findByRole('heading', { name: 'Família Exemplo' })).toBeVisible()
    expect(screen.getByRole('heading', { name: 'Outra Família Exemplo' })).toBeVisible()
  })

  it('a lista vazia acolhe e explica por onde começar', async () => {
    renderGuests({ [GET_GUESTS]: jsonResponse(200, listOf([])) })

    expect(await screen.findByRole('heading', { name: 'Ainda sem convidados' })).toBeVisible()
    expect(screen.getByText(/Comecem por um núcleo/)).toBeVisible()
  })

  it('o erro de leitura é acionável e tenta de novo', async () => {
    let tentativas = 0
    const { user } = renderGuests({
      [GET_GUESTS]: () => {
        tentativas += 1
        return tentativas === 1
          ? problemResponse(500, 'internal_error')
          : jsonResponse(200, listOf([]))
      },
    })

    expect(await screen.findByText('Não conseguimos carregar a lista agora.')).toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Tentar de novo' }))

    expect(await screen.findByRole('heading', { name: 'Ainda sem convidados' })).toBeVisible()
  })

  it('no celular, o cartão mostra o lado, o resumo e cada pessoa com o status em texto', async () => {
    // F-CNV-07
    renderGuests()
    const cartao = (await screen.findByRole('heading', { name: 'Família Exemplo' })).closest(
      'li',
    ) as HTMLElement

    expect(within(cartao).getByText('Noivo')).toBeVisible()
    expect(within(cartao).getByText('1 de 3 confirmados · 1 não irá')).toBeVisible()
    expect(within(cartao).getByText('Convidado Exemplo A')).toBeVisible()
    expect(within(cartao).getByText('Confirmado')).toBeVisible()
    expect(within(cartao).getByText('Não irá')).toBeVisible()
  })

  it('o acompanhante sem nome aparece como "Acompanhante de {titular}"', async () => {
    // F-CNV-02
    renderGuests()

    expect(await screen.findByText('Acompanhante de Convidado Exemplo A')).toBeVisible()
  })

  it('o WhatsApp só aparece para celular válido e abre numa nova aba com rel seguro', async () => {
    // F-CNV-01
    renderGuests()
    await screen.findByRole('heading', { name: 'Família Exemplo' })

    const link = screen.getByRole('link', { name: 'Abrir WhatsApp de Convidado Exemplo A' })

    expect(link).toHaveAttribute('href', 'https://wa.me/5511912345678')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    expect(screen.getAllByRole('link', { name: /Abrir WhatsApp/ })).toHaveLength(1)
  })

  it('um endereço que não é do WhatsApp nunca vira link, mesmo vindo da API', async () => {
    const lista = listOf([
      household({
        id: 'n-b',
        name: 'Outra Família Exemplo',
        guests: [guest({ household_id: 'n-b', whatsapp_url: 'javascript:alert(1)' })],
      }),
    ])
    renderGuests({ [GET_GUESTS]: jsonResponse(200, lista) })

    await screen.findByRole('heading', { name: 'Outra Família Exemplo' })
    expect(screen.queryByRole('link')).not.toBeInTheDocument()
  })

  it('na tela larga, a tabela agrupa as pessoas por núcleo', async () => {
    // F-CNV-07
    stubWideScreen()
    renderGuests()
    const tabela = await screen.findByRole('table')

    expect(
      within(tabela)
        .getAllByRole('columnheader')
        .map((c) => c.textContent),
    ).toEqual(['Nome', 'Faixa', 'Probabilidade', 'Status', 'Contato'])
    expect(within(tabela).getAllByRole('rowgroup').length).toBeGreaterThanOrEqual(3)
    const linha = within(tabela).getByText('Convidado Exemplo C').closest('tr') as HTMLElement
    expect(within(linha).getByText('Criança pagante')).toBeVisible()
    expect(within(linha).getByText('9 anos')).toBeVisible()
    expect(within(linha).getByText('Certeza')).toBeVisible()
    expect(within(linha).getByText('Não irá')).toBeVisible()
  })
})

describe('lista de convidados: painel do núcleo', () => {
  it('abre pelo nome do núcleo e mostra as pessoas, o endereço e a observação', async () => {
    const { user } = renderGuests()
    await user.click(await screen.findByRole('button', { name: 'Família Exemplo' }))

    const painel = await screen.findByRole('dialog', { name: 'Família Exemplo' })
    expect(within(painel).getByText('Convidado Exemplo C')).toBeVisible()
    expect(within(painel).getByText('Sem lactose')).toBeVisible()
    expect(within(painel).getByText('Viagem')).toBeVisible()
    expect(within(painel).getByText('(11) 91234-5678')).toBeVisible()
    expect(within(painel).getByText('Rua Exemplo, 100')).toBeVisible()
    expect(within(painel).getByText('SP · 00000-000')).toBeVisible()
    expect(within(painel).getByText('Convite impresso.')).toBeVisible()
  })

  it('abre direto quando a URL já traz o núcleo', async () => {
    renderGuests({}, { nucleo: 'n-b' })

    expect(await screen.findByRole('dialog', { name: 'Outra Família Exemplo' })).toBeVisible()
    expect(within(screen.getByRole('dialog')).getByText('Ainda sem endereço.')).toBeVisible()
  })

  it('um núcleo desconhecido na URL não abre nada nem quebra a lista', async () => {
    renderGuests({}, { nucleo: 'n-nao-existe' })

    expect(await screen.findByRole('heading', { name: 'Família Exemplo' })).toBeVisible()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('Esc fecha o painel e o foco volta ao botão que o abriu', async () => {
    // D-070
    const { user } = renderGuests()
    const abrir = await screen.findByRole('button', { name: 'Família Exemplo' })
    await user.click(abrir)
    await screen.findByRole('dialog')

    await user.keyboard('{Escape}')

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(abrir).toHaveFocus()
  })
})
