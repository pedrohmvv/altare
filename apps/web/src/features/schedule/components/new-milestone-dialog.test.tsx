import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import {
  GET_SCHEDULE,
  POST_MILESTONE,
  renderSchedule,
  stubWideScreen,
} from '@/test/render-schedule'
import {
  ID,
  SCHEDULE,
  scheduleWithEmptyPhase,
  scheduleWithNewMilestone,
} from '@/test/schedule-fixtures'
import { memory } from '@/test/schedule-helpers'

const NOVO = { id: ID.novo, title: 'Marco Novo Exemplo' }

async function openDialog(user: ReturnType<typeof renderSchedule>['user']) {
  const gatilho = await screen.findByRole('button', { name: 'Novo marco' })
  await user.click(gatilho)
  const dialog = await screen.findByRole('dialog', { name: 'Novo marco' })
  return { gatilho, dialog }
}

describe('novo marco (F-CRN-01)', () => {
  it('o cabeçalho da página oferece "Novo marco" e "Fases" quando o cronograma carregou', async () => {
    renderSchedule()

    expect(await screen.findByRole('button', { name: 'Novo marco' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Fases' })).toBeVisible()
  })

  it('abre com a primeira fase, responsável Ambos e sem categoria, com o apoio da categoria', async () => {
    const { user } = renderSchedule()
    const { dialog } = await openDialog(user)

    expect(within(dialog).getByRole('combobox', { name: 'Fase' })).toHaveTextContent(
      'Fase Exemplo Um',
    )
    expect(within(dialog).getByRole('combobox', { name: 'Responsável' })).toHaveTextContent('Ambos')
    expect(within(dialog).getByRole('combobox', { name: 'Categoria' })).toHaveTextContent(
      'Sem categoria',
    )
    expect(
      within(dialog).getByText(/decide se o marco fica Bloqueado, Opcional ou arquivado/),
    ).toBeVisible()
    expect(screen.getByRole('heading', { level: 2, name: 'Novo marco' })).toBeVisible()
  })

  it('sem título o formulário bloqueia, mostra o erro ao lado do campo e não chama a API', async () => {
    const { api, user } = renderSchedule()
    const { dialog } = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Criar marco' }))

    expect(await within(dialog).findByText('Informem o título do marco.')).toBeVisible()
    expect(within(dialog).getByLabelText(/^Título/)).toHaveAttribute('aria-invalid', 'true')
    expect(api.callsTo(POST_MILESTONE)).toHaveLength(0)
  })

  it('criar envia título, fase, responsável e categoria, fecha o diálogo e abre o painel do marco criado', async () => {
    const mem = memory()
    const { api, user, probe } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [POST_MILESTONE]: mem.created(scheduleWithNewMilestone(ID.faseUm, NOVO), ID.novo),
    })
    const { dialog } = await openDialog(user)

    await user.type(within(dialog).getByLabelText(/^Título/), '  Marco Novo Exemplo  ')
    await user.click(within(dialog).getByRole('button', { name: 'Criar marco' }))

    await waitFor(() => expect(api.callsTo(POST_MILESTONE)).toHaveLength(1))
    expect(api.callsTo(POST_MILESTONE)[0]?.body).toEqual({
      title: 'Marco Novo Exemplo',
      phase_id: ID.faseUm,
      responsible: 'Ambos',
      category_id: null,
    })
    const painel = await screen.findByRole('dialog', { name: 'Marco Novo Exemplo' })
    expect(screen.queryByRole('dialog', { name: 'Novo marco' })).not.toBeInTheDocument()
    expect(probe.current.marco).toBe(ID.novo)
    expect(within(painel).getByText('Fase: Fase Exemplo Um')).toBeVisible()
    await waitFor(() => expect(painel).toHaveFocus())
    // O cronograma devolvido vai direto para o cache: nenhuma segunda leitura.
    expect(api.callsTo(GET_SCHEDULE)).toHaveLength(1)
  })

  it('a fase, o responsável e a categoria escolhidos vão no corpo', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [POST_MILESTONE]: mem.created(scheduleWithNewMilestone(ID.faseDois, NOVO), ID.novo),
    })
    const { dialog } = await openDialog(user)

    await user.type(within(dialog).getByLabelText(/^Título/), 'Marco Novo Exemplo')
    await user.click(within(dialog).getByRole('combobox', { name: 'Fase' }))
    await user.click(screen.getByRole('option', { name: 'Fase Exemplo Dois' }))
    await user.click(within(dialog).getByRole('combobox', { name: 'Responsável' }))
    await user.click(screen.getByRole('option', { name: 'Noiva' }))
    await user.click(within(dialog).getByRole('combobox', { name: 'Categoria' }))
    await user.click(screen.getByRole('option', { name: 'Buffet Exemplo' }))
    await user.click(within(dialog).getByRole('button', { name: 'Criar marco' }))

    await waitFor(() => expect(api.callsTo(POST_MILESTONE)).toHaveLength(1))
    expect(api.callsTo(POST_MILESTONE)[0]?.body).toEqual({
      title: 'Marco Novo Exemplo',
      phase_id: ID.faseDois,
      responsible: 'Noiva',
      category_id: ID.buffet,
    })
    expect(await screen.findByRole('dialog', { name: 'Marco Novo Exemplo' })).toBeVisible()
  })

  it('partindo de "Novo marco nesta fase", a fase de origem é a padrão', async () => {
    const mem = memory(scheduleWithEmptyPhase())
    const { user } = renderSchedule({ [GET_SCHEDULE]: mem.get })
    const botao = await screen.findByRole('button', {
      name: 'Novo marco nesta fase: Fase Exemplo Três',
    })
    expect(screen.getByText('Nenhum marco ativo nesta fase.')).toBeVisible()

    await user.click(botao)

    const dialog = await screen.findByRole('dialog', { name: 'Novo marco' })
    expect(within(dialog).getByRole('combobox', { name: 'Fase' })).toHaveTextContent(
      'Fase Exemplo Três',
    )
  })

  it('o botão de cada fase vazia leva o nome da fase, mas o rótulo visível começa igual', async () => {
    const vazia = (id: string, title: string, position: number) => ({
      id,
      title,
      position,
      version: 1,
      progress: { done: 0, total: 0 },
      milestones: [],
    })
    const mem = memory({
      ...scheduleWithEmptyPhase(),
      phases: [
        ...scheduleWithEmptyPhase().phases,
        vazia('00000000-0000-4000-8000-0000000000f4', 'Fase Exemplo Quatro', 3),
      ],
    })
    renderSchedule({ [GET_SCHEDULE]: mem.get })

    const tres = await screen.findByRole('button', {
      name: 'Novo marco nesta fase: Fase Exemplo Três',
    })
    const quatro = screen.getByRole('button', {
      name: 'Novo marco nesta fase: Fase Exemplo Quatro',
    })
    expect(tres).toHaveTextContent('Novo marco nesta fase')
    expect(quatro).toHaveTextContent('Novo marco nesta fase')
  })

  it('no computador, a fase vazia também oferece "Novo marco nesta fase"', async () => {
    stubWideScreen()
    const mem = memory(scheduleWithEmptyPhase())
    const { user } = renderSchedule({ [GET_SCHEDULE]: mem.get })
    const tabela = await screen.findByRole('table', {
      name: 'Fases do cronograma e os marcos de cada uma',
    })

    await user.click(
      within(tabela).getByRole('button', { name: 'Novo marco nesta fase: Fase Exemplo Três' }),
    )

    expect(
      within(await screen.findByRole('dialog', { name: 'Novo marco' })).getByRole('combobox', {
        name: 'Fase',
      }),
    ).toHaveTextContent('Fase Exemplo Três')
  })

  it('o 422 de título do servidor aparece no campo Título', async () => {
    const { user } = renderSchedule({
      [POST_MILESTONE]: problemResponse(422, 'milestone_title_required', {
        detail: 'Dê um título ao marco.',
      }),
    })
    const { dialog } = await openDialog(user)

    await user.type(within(dialog).getByLabelText(/^Título/), 'Marco Novo Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Criar marco' }))

    expect(await within(dialog).findByText('Dê um título ao marco.')).toBeVisible()
    expect(within(dialog).getByLabelText(/^Título/)).toHaveAttribute('aria-invalid', 'true')
  })

  it('o 422 de categoria indisponível aparece no campo Categoria', async () => {
    const { user } = renderSchedule({
      [POST_MILESTONE]: problemResponse(422, 'category_not_available', {
        detail: 'Esta categoria não está disponível.',
      }),
    })
    const { dialog } = await openDialog(user)

    await user.type(within(dialog).getByLabelText(/^Título/), 'Marco Novo Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Criar marco' }))

    expect(await within(dialog).findByText('Esta categoria não está disponível.')).toBeVisible()
    expect(within(dialog).getByRole('combobox', { name: 'Categoria' })).toHaveAttribute(
      'aria-invalid',
      'true',
    )
    await waitFor(() =>
      expect(within(dialog).getByRole('combobox', { name: 'Categoria' })).toHaveFocus(),
    )
  })

  it('uma falha de rede avisa e mantém o que foi digitado', async () => {
    const { user } = renderSchedule({
      [POST_MILESTONE]: () => {
        throw new TypeError('Failed to fetch')
      },
    })
    const { dialog } = await openDialog(user)

    await user.type(within(dialog).getByLabelText(/^Título/), 'Ainda aqui')
    await user.click(within(dialog).getByRole('button', { name: 'Criar marco' }))

    expect(await within(dialog).findByText(/Não conseguimos criar o marco agora/)).toBeVisible()
    expect(within(dialog).getByLabelText(/^Título/)).toHaveValue('Ainda aqui')
  })

  it('abre o painel pelo milestone_id devolvido, mesmo se outro marco entrou na mesma fase depois dele', async () => {
    const outro = { id: '00000000-0000-4000-8000-0000000000aa', title: 'Marco de Outra Pessoa' }
    const resposta = scheduleWithNewMilestone(
      ID.faseUm,
      outro,
      scheduleWithNewMilestone(ID.faseUm, NOVO),
    )
    const { user, probe } = renderSchedule({
      [POST_MILESTONE]: jsonResponse(201, { schedule: resposta, milestone_id: ID.novo }),
    })
    const { dialog } = await openDialog(user)

    await user.type(within(dialog).getByLabelText(/^Título/), 'Marco Novo Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Criar marco' }))

    expect(await screen.findByRole('dialog', { name: 'Marco Novo Exemplo' })).toBeVisible()
    expect(probe.current.marco).toBe(ID.novo)
  })

  it('se o id devolvido não está nas listas, não abre painel e só avisa', async () => {
    const { user, probe } = renderSchedule({
      [POST_MILESTONE]: jsonResponse(201, { schedule: SCHEDULE, milestone_id: ID.novo }),
    })
    const { dialog } = await openDialog(user)

    await user.type(within(dialog).getByLabelText(/^Título/), 'Marco Novo Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Criar marco' }))

    await waitFor(() =>
      expect(screen.queryByRole('dialog', { name: 'Novo marco' })).not.toBeInTheDocument(),
    )
    expect(probe.current.marco).toBeUndefined()
    expect(await screen.findByText('Marco criado')).toBeVisible()
  })

  it('um marco criado já arquivado (categoria fora do escopo) não abre painel e o aviso explica', async () => {
    const { user, probe } = renderSchedule({
      [POST_MILESTONE]: jsonResponse(201, {
        schedule: scheduleWithNewMilestone(ID.faseUm, { ...NOVO, archived: true }),
        milestone_id: ID.novo,
      }),
    })
    const { dialog } = await openDialog(user)

    await user.type(within(dialog).getByLabelText(/^Título/), 'Marco Novo Exemplo')
    await user.click(within(dialog).getByRole('button', { name: 'Criar marco' }))

    expect(await screen.findByText(/fica fora das listas/)).toBeVisible()
    expect(probe.current.marco).toBeUndefined()
  })

  it('cancelar não envia nada e devolve o foco ao botão que abriu o diálogo', async () => {
    const { api, user } = renderSchedule()
    const { gatilho, dialog } = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Cancelar' }))

    expect(api.callsTo(POST_MILESTONE)).toHaveLength(0)
    await waitFor(() => expect(gatilho).toHaveFocus())
  })

  it('Esc também cancela e devolve o foco ao botão de origem', async () => {
    const { user } = renderSchedule()
    const { gatilho } = await openDialog(user)

    await user.keyboard('{Escape}')

    await waitFor(() =>
      expect(screen.queryByRole('dialog', { name: 'Novo marco' })).not.toBeInTheDocument(),
    )
    await waitFor(() => expect(gatilho).toHaveFocus())
  })

  it('aberto por "Novo marco nesta fase", cancelar devolve o foco a esse botão', async () => {
    const mem = memory(scheduleWithEmptyPhase())
    const { user } = renderSchedule({ [GET_SCHEDULE]: mem.get })
    const botao = await screen.findByRole('button', {
      name: 'Novo marco nesta fase: Fase Exemplo Três',
    })
    await user.click(botao)
    const dialog = await screen.findByRole('dialog', { name: 'Novo marco' })

    await user.click(within(dialog).getByRole('button', { name: 'Cancelar' }))

    await waitFor(() => expect(botao).toHaveFocus())
  })
})
