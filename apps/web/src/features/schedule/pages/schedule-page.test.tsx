import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { GET_SCHEDULE, renderSchedule, stubWideScreen } from '@/test/render-schedule'
import { ID, SCHEDULE } from '@/test/schedule-fixtures'

const phase = (name: string) => screen.getByRole('region', { name })

describe('cronograma por fase: leitura (F-CRN-09)', () => {
  it('mostra o carregamento e depois uma seção por fase, com o título', async () => {
    renderSchedule()

    expect(screen.getByText('Carregando o cronograma…')).toBeVisible()
    expect(await screen.findByRole('heading', { level: 2, name: 'Fase Exemplo Um' })).toBeVisible()
    expect(screen.getByRole('heading', { level: 2, name: 'Fase Exemplo Dois' })).toBeVisible()
  })

  it('o progresso vem da API, por escrito e como barra, sem contar arquivados', async () => {
    renderSchedule()
    await screen.findByRole('heading', { name: 'Fase Exemplo Um' })

    expect(within(phase('Fase Exemplo Um')).getByText('1 de 3 concluídos')).toBeVisible()
    const barra = within(phase('Fase Exemplo Um')).getByRole('progressbar', {
      name: '1 de 3 concluídos',
    })
    expect(barra).toHaveAttribute('aria-valuenow', '1')
    expect(barra).toHaveAttribute('aria-valuemax', '3')
    expect(within(phase('Fase Exemplo Dois')).getByText('1 de 4 concluídos')).toBeVisible()
  })

  it('o marco arquivado não aparece na lista', async () => {
    renderSchedule()
    await screen.findByRole('heading', { name: 'Fase Exemplo Um' })

    expect(screen.queryByText('Marco Exemplo Arquivado')).not.toBeInTheDocument()
  })

  it('o que está Destravado ganha o selo com texto e ícone, não só cor', async () => {
    renderSchedule()
    const cartao = (
      await screen.findByRole('heading', { name: 'Marco Exemplo Destravado' })
    ).closest('li') as HTMLElement

    expect(within(cartao).getByText('Destravado')).toBeVisible()
    expect(cartao.querySelector('svg')).not.toBeNull()
  })

  it('o Bloqueado diz "Aguardando:" com os nomes do que falta', async () => {
    // F-CRN-03, regra 3
    renderSchedule()
    const cartao = (
      await screen.findByRole('heading', { name: 'Marco Exemplo Bloqueado' })
    ).closest('li') as HTMLElement

    expect(within(cartao).getByText('Bloqueado')).toBeVisible()
    expect(within(cartao).getByText('Aguardando: Marco Exemplo Destravado')).toBeVisible()
  })

  it('a categoria por classificar é o motivo do bloqueio, como a API o escreve', async () => {
    // F-CRN-04
    renderSchedule()
    const cartao = (
      await screen.findByRole('heading', { name: 'Marco Exemplo da Categoria' })
    ).closest('li') as HTMLElement

    expect(
      within(cartao).getByText('Aguardando classificar a categoria no Mapa de Escopo'),
    ).toBeVisible()
    expect(within(cartao).queryByText(/^Aguardando:/)).not.toBeInTheDocument()
  })

  it('o opcional leva a etiqueta "Opcional" e o atrasado leva ícone e "Atrasado"', async () => {
    // F-CRN-04, F-CRN-03
    renderSchedule()
    const cartao = (await screen.findByRole('heading', { name: 'Marco Exemplo Opcional' })).closest(
      'li',
    ) as HTMLElement

    expect(within(cartao).getByText('Opcional')).toBeVisible()
    const atrasado = within(cartao).getByText('Atrasado')
    expect(atrasado).toBeVisible()
    expect(atrasado.parentElement?.querySelector('svg')).not.toBeNull()
    expect(within(cartao).getByText('15 jan 2020')).toBeVisible()
  })

  it('o Concluído com predecessor não resolvido diz antes de quê, em texto e com ícone', async () => {
    // F-CRN-03, regra 5 (aviso depends_on_unresolved)
    renderSchedule()
    const cartao = (
      await screen.findByRole('heading', { name: 'Marco Exemplo com Aviso' })
    ).closest('li') as HTMLElement

    expect(within(cartao).getByText('Concluído')).toBeVisible()
    const aviso = within(cartao).getByText(
      'Concluído antes de: Marco Exemplo Bloqueado, Marco Exemplo da Categoria',
    )
    expect(aviso).toBeVisible()
    const icone = aviso.querySelector('svg')
    expect(icone).not.toBeNull()
    expect(icone).toHaveAttribute('aria-hidden', 'true')
  })

  it('cada fase leva o rótulo "Fase N" na ordem do cronograma', async () => {
    renderSchedule()
    await screen.findByRole('heading', { name: 'Fase Exemplo Um' })

    expect(within(phase('Fase Exemplo Um')).getByText('Fase 1')).toBeVisible()
    expect(within(phase('Fase Exemplo Dois')).getByText('Fase 2')).toBeVisible()
  })

  it('o responsável aparece por extenso em cada marco', async () => {
    renderSchedule()
    const cartao = (
      await screen.findByRole('heading', { name: 'Marco Exemplo Destravado' })
    ).closest('li') as HTMLElement

    expect(within(cartao).getByText('Noiva')).toBeVisible()
  })

  it('sem marcos, acolhe e diz o que virá', async () => {
    renderSchedule({
      [GET_SCHEDULE]: jsonResponse(200, { has_exact_date: false, phases: [] }),
    })

    expect(await screen.findByRole('heading', { name: 'Ainda sem marcos' })).toBeVisible()
  })

  it('o erro de leitura é acionável e tenta de novo', async () => {
    let tentativas = 0
    const { user } = renderSchedule({
      [GET_SCHEDULE]: () => {
        tentativas += 1
        return tentativas === 1
          ? problemResponse(500, 'internal_error')
          : jsonResponse(200, SCHEDULE)
      },
    })

    expect(await screen.findByText('Não conseguimos carregar o cronograma agora.')).toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Tentar de novo' }))

    expect(await screen.findByRole('heading', { name: 'Fase Exemplo Um' })).toBeVisible()
  })
})

describe('cronograma por fase: desktop e celular (F-CRN-09)', () => {
  it('no celular, uma lista de cartões e nenhuma tabela', async () => {
    renderSchedule()
    await screen.findByRole('heading', { name: 'Fase Exemplo Um' })

    expect(screen.queryByRole('table')).not.toBeInTheDocument()
    expect(screen.getAllByRole('list').length).toBeGreaterThan(0)
  })

  it('no computador, uma tabela com um grupo de linhas por fase', async () => {
    stubWideScreen()
    renderSchedule()
    const tabela = await screen.findByRole('table', {
      name: 'Fases do cronograma e os marcos de cada uma',
    })

    expect(within(tabela).getAllByRole('rowheader')).toHaveLength(2)
    expect(within(tabela).getByRole('rowheader', { name: /Fase Exemplo Um/ })).toHaveAttribute(
      'scope',
      'rowgroup',
    )
    expect(within(tabela).getByText('1 de 3 concluídos')).toBeVisible()
    expect(within(tabela).getByRole('button', { name: 'Marco Exemplo Bloqueado' })).toBeVisible()
    expect(within(tabela).getByText('Aguardando: Marco Exemplo Destravado')).toBeVisible()
    expect(within(tabela).queryByText('Marco Exemplo Arquivado')).not.toBeInTheDocument()
  })

  it('no computador, um título de seção (só para o leitor) fica entre o h1 e a tabela', async () => {
    stubWideScreen()
    renderSchedule()
    await screen.findByRole('table', { name: 'Fases do cronograma e os marcos de cada uma' })

    expect(screen.getByRole('heading', { level: 2, name: 'Marcos por fase' })).toBeInTheDocument()
  })

  it('a tabela tem as colunas de marco, estado, responsável e prazo-alvo', async () => {
    stubWideScreen()
    renderSchedule()
    const tabela = await screen.findByRole('table', {
      name: 'Fases do cronograma e os marcos de cada uma',
    })

    for (const nome of ['Marco', 'Estado', 'Responsável', 'Prazo-alvo']) {
      expect(within(tabela).getByRole('columnheader', { name: nome })).toBeVisible()
    }
    expect(within(tabela).getByText('15/03/2027')).toBeVisible()
  })
})

describe('o painel do marco na URL (F-CRN-09)', () => {
  it('abrir um marco põe o id dele na URL e abre o painel', async () => {
    const { user } = renderSchedule()
    await user.click(await screen.findByRole('button', { name: 'Marco Exemplo Destravado' }))

    const painel = await screen.findByRole('dialog', { name: 'Marco Exemplo Destravado' })
    expect(within(painel).getByText('Fase: Fase Exemplo Um')).toBeVisible()
  })

  it('com ?marco= na URL, o painel já abre (o recarregamento reabre)', async () => {
    renderSchedule({}, { marco: ID.bloqueado })

    expect(await screen.findByRole('dialog', { name: 'Marco Exemplo Bloqueado' })).toBeVisible()
  })

  it('um marco que não existe não abre painel nenhum', async () => {
    renderSchedule({}, { marco: '00000000-0000-4000-8000-0000000000ff' })
    await screen.findByRole('heading', { name: 'Fase Exemplo Um' })

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('o marco arquivado não abre painel, porque não está nas listas', async () => {
    renderSchedule({}, { marco: ID.arquivado })
    await screen.findByRole('heading', { name: 'Fase Exemplo Um' })

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('aberto pela URL, ao fechar o foco cai no botão do próprio marco', async () => {
    const { user } = renderSchedule({}, { marco: ID.bloqueado })
    await screen.findByRole('dialog', { name: 'Marco Exemplo Bloqueado' })

    await user.keyboard('{Escape}')

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(screen.getByRole('button', { name: 'Marco Exemplo Bloqueado' })).toHaveFocus()
  })

  it('ao abrir, o foco vai ao painel, não ao primeiro botão de estado', async () => {
    const { user } = renderSchedule()
    await user.click(await screen.findByRole('button', { name: 'Marco Exemplo Destravado' }))

    const painel = await screen.findByRole('dialog', { name: 'Marco Exemplo Destravado' })
    await waitFor(() => expect(painel).toHaveFocus())
  })

  it('ao fechar, o foco volta ao marco que abriu o painel', async () => {
    const { user } = renderSchedule()
    const gatilho = await screen.findByRole('button', { name: 'Marco Exemplo Destravado' })
    await user.click(gatilho)
    await screen.findByRole('dialog', { name: 'Marco Exemplo Destravado' })

    await user.keyboard('{Escape}')

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(gatilho).toHaveFocus()
  })
})
