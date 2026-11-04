import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import {
  GET_SCHEDULE,
  POST_PHASE,
  PUT_PHASE,
  PUT_PHASE_ORDER,
  renderSchedule,
} from '@/test/render-schedule'
import { ID, SCHEDULE, scheduleWithEmptyPhase } from '@/test/schedule-fixtures'
import { activeAlert, memory } from '@/test/schedule-helpers'
import type { Schedule } from '../api/schedule'

const THREE = scheduleWithEmptyPhase()

function reordered(schedule: Schedule, ids: string[]): Schedule {
  return {
    ...schedule,
    phases: ids.map((id, position) => ({
      ...(schedule.phases.find((phase) => phase.id === id) as Schedule['phases'][number]),
      position,
    })),
  }
}

function renamed(schedule: Schedule, id: string, title: string, version: number): Schedule {
  return {
    ...schedule,
    phases: schedule.phases.map((phase) =>
      phase.id === id ? { ...phase, title, version } : phase,
    ),
  }
}

async function openDialog(user: ReturnType<typeof renderSchedule>['user']) {
  const gatilho = await screen.findByRole('button', { name: 'Fases' })
  await user.click(gatilho)
  const dialog = await screen.findByRole('dialog', { name: 'Fases do cronograma' })
  return { gatilho, dialog }
}

describe('fases do cronograma (F-CRN-01)', () => {
  it('lista as fases na ordem, cada uma com o nome em um campo e os botões de subir e descer', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: memory(THREE).get })
    const { dialog } = await openDialog(user)

    expect(within(dialog).getByRole('textbox', { name: 'Fase 1 (obrigatório)' })).toHaveValue(
      'Fase Exemplo Um',
    )
    expect(within(dialog).getByRole('textbox', { name: 'Fase 2 (obrigatório)' })).toHaveValue(
      'Fase Exemplo Dois',
    )
    expect(within(dialog).getByRole('textbox', { name: 'Fase 3 (obrigatório)' })).toHaveValue(
      'Fase Exemplo Três',
    )
    expect(within(dialog).queryByRole('button', { name: /Excluir/ })).not.toBeInTheDocument()
  })

  it('os nomes de fase são obrigatórios por escrito e marcados para o leitor de tela', async () => {
    const { user } = renderSchedule()
    const { dialog } = await openDialog(user)

    expect(within(dialog).getByRole('textbox', { name: 'Fase 1 (obrigatório)' })).toHaveAttribute(
      'aria-required',
      'true',
    )
    expect(
      within(dialog).getByRole('textbox', { name: 'Nome da nova fase (obrigatório)' }),
    ).toHaveAttribute('aria-required', 'true')
  })

  it('a hierarquia é diálogo (h2) e seções (h3)', async () => {
    const { user } = renderSchedule()
    const { dialog } = await openDialog(user)

    expect(
      within(dialog).getByRole('heading', { level: 2, name: 'Fases do cronograma' }),
    ).toBeVisible()
    expect(within(dialog).getByRole('heading', { level: 3, name: 'Ordem e nomes' })).toBeVisible()
    expect(within(dialog).getByRole('heading', { level: 3, name: 'Nova fase' })).toBeVisible()
  })

  it('a primeira fase não sobe e a última não desce', async () => {
    const { user } = renderSchedule()
    const { dialog } = await openDialog(user)

    expect(
      within(dialog).getByRole('button', { name: 'Subir a fase Fase Exemplo Um' }),
    ).toBeDisabled()
    expect(
      within(dialog).getByRole('button', { name: 'Descer a fase Fase Exemplo Um' }),
    ).toBeEnabled()
    expect(
      within(dialog).getByRole('button', { name: 'Descer a fase Fase Exemplo Dois' }),
    ).toBeDisabled()
    expect(
      within(dialog).getByRole('button', { name: 'Subir a fase Fase Exemplo Dois' }),
    ).toBeEnabled()
  })

  it('descer envia a lista completa de ids na nova ordem e o foco acompanha o botão da fase', async () => {
    const mem = memory(THREE)
    const order = [ID.faseDois, ID.faseUm, ID.faseVazia]
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_PHASE_ORDER]: mem.set(reordered(THREE, order)),
    })
    const { dialog } = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Descer a fase Fase Exemplo Um' }))

    await waitFor(() => expect(api.callsTo(PUT_PHASE_ORDER)).toHaveLength(1))
    expect(api.callsTo(PUT_PHASE_ORDER)[0]?.body).toEqual({ ids: order })
    await waitFor(() =>
      expect(within(dialog).getByRole('textbox', { name: 'Fase 2 (obrigatório)' })).toHaveValue(
        'Fase Exemplo Um',
      ),
    )
    // A fase agora é a do meio: o foco fica no mesmo botão, que ainda pode descer.
    await waitFor(() =>
      expect(
        within(dialog).getByRole('button', { name: 'Descer a fase Fase Exemplo Um' }),
      ).toHaveFocus(),
    )
    expect(within(dialog).getByText('Ordem das fases salva.')).toBeVisible()
  })

  it('se a fase chega ao fim, o foco vai ao outro botão dela, porque o desabilitado não o recebe', async () => {
    const mem = memory(SCHEDULE)
    const { user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_PHASE_ORDER]: mem.set(reordered(SCHEDULE, [ID.faseDois, ID.faseUm])),
    })
    const { dialog } = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Descer a fase Fase Exemplo Um' }))

    await waitFor(() =>
      expect(
        within(dialog).getByRole('button', { name: 'Subir a fase Fase Exemplo Um' }),
      ).toHaveFocus(),
    )
  })

  it('subir também envia a lista completa', async () => {
    const mem = memory(THREE)
    const order = [ID.faseUm, ID.faseVazia, ID.faseDois]
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_PHASE_ORDER]: mem.set(reordered(THREE, order)),
    })
    const { dialog } = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Subir a fase Fase Exemplo Três' }))

    await waitFor(() => expect(api.callsTo(PUT_PHASE_ORDER)).toHaveLength(1))
    expect(api.callsTo(PUT_PHASE_ORDER)[0]?.body).toEqual({ ids: order })
  })

  it('renomear envia o novo nome com a versão da fase e a lista passa a mostrá-lo', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_PHASE(ID.faseDois)]: mem.set(renamed(SCHEDULE, ID.faseDois, 'Nome Novo da Fase', 7)),
    })
    const { dialog } = await openDialog(user)

    const campo = within(dialog).getByRole('textbox', { name: 'Fase 2 (obrigatório)' })
    await user.clear(campo)
    await user.type(campo, '  Nome Novo da Fase  ')
    await user.click(
      within(dialog).getByRole('button', { name: 'Salvar o nome da fase Fase Exemplo Dois' }),
    )

    await waitFor(() => expect(api.callsTo(PUT_PHASE(ID.faseDois))).toHaveLength(1))
    expect(api.callsTo(PUT_PHASE(ID.faseDois))[0]?.body).toEqual({
      title: 'Nome Novo da Fase',
      version: 2,
    })
    expect(await within(dialog).findByText('Nome da fase salvo.')).toBeVisible()
    expect(within(dialog).getByRole('textbox', { name: 'Fase 2 (obrigatório)' })).toHaveValue(
      'Nome Novo da Fase',
    )
  })

  it('renomear não perde nenhum marco da fase', async () => {
    const mem = memory()
    const { user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_PHASE(ID.faseDois)]: mem.set(renamed(SCHEDULE, ID.faseDois, 'Nome Novo da Fase', 7)),
    })
    const { dialog } = await openDialog(user)
    const campo = within(dialog).getByRole('textbox', { name: 'Fase 2 (obrigatório)' })
    await user.clear(campo)
    await user.type(campo, 'Nome Novo da Fase')
    await user.click(
      within(dialog).getByRole('button', { name: 'Salvar o nome da fase Fase Exemplo Dois' }),
    )
    await within(dialog).findByText('Nome da fase salvo.')
    await user.keyboard('{Escape}')

    const secao = await screen.findByRole('region', { name: 'Nome Novo da Fase' })
    expect(within(secao).getByRole('button', { name: 'Marco Exemplo da Categoria' })).toBeVisible()
    expect(within(secao).getByRole('button', { name: 'Marco Exemplo com Aviso' })).toBeVisible()
  })

  it('sem nome a fase não é salva: erro ao lado do campo e nenhuma chamada', async () => {
    const { api, user } = renderSchedule()
    const { dialog } = await openDialog(user)

    await user.clear(within(dialog).getByRole('textbox', { name: 'Fase 1 (obrigatório)' }))
    await user.click(
      within(dialog).getByRole('button', { name: 'Salvar o nome da fase Fase Exemplo Um' }),
    )

    expect(await within(dialog).findByText('Informem o nome da fase.')).toBeVisible()
    expect(within(dialog).getByRole('textbox', { name: 'Fase 1 (obrigatório)' })).toHaveAttribute(
      'aria-invalid',
      'true',
    )
    expect(api.callsTo(PUT_PHASE(ID.faseUm))).toHaveLength(0)
  })

  it('um nome com mais de 60 caracteres é recusado', async () => {
    const { api, user } = renderSchedule()
    const { dialog } = await openDialog(user)

    const campo = within(dialog).getByRole('textbox', { name: 'Fase 1 (obrigatório)' })
    await user.clear(campo)
    await user.click(campo)
    await user.paste('a'.repeat(61))
    await user.click(
      within(dialog).getByRole('button', { name: 'Salvar o nome da fase Fase Exemplo Um' }),
    )

    expect(await within(dialog).findByText('Usem até 60 caracteres.')).toBeVisible()
    expect(api.callsTo(PUT_PHASE(ID.faseUm))).toHaveLength(0)
  })

  it('uma fase nova vai no fim, com o campo limpo depois', async () => {
    const mem = memory()
    const nova = {
      id: '00000000-0000-4000-8000-0000000000f9',
      title: 'Fase Nova Exemplo',
      position: 2,
      version: 1,
      progress: { done: 0, total: 0 },
      milestones: [],
    }
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [POST_PHASE]: mem.set({ ...SCHEDULE, phases: [...SCHEDULE.phases, nova] }),
    })
    const { dialog } = await openDialog(user)

    const campo = within(dialog).getByRole('textbox', { name: 'Nome da nova fase (obrigatório)' })
    await user.type(campo, '  Fase Nova Exemplo  ')
    await user.click(within(dialog).getByRole('button', { name: 'Adicionar fase' }))

    await waitFor(() => expect(api.callsTo(POST_PHASE)).toHaveLength(1))
    expect(api.callsTo(POST_PHASE)[0]?.body).toEqual({ title: 'Fase Nova Exemplo' })
    expect(
      await within(dialog).findByRole('textbox', { name: 'Fase 3 (obrigatório)' }),
    ).toHaveValue('Fase Nova Exemplo')
    expect(
      within(dialog).getByRole('textbox', { name: 'Nome da nova fase (obrigatório)' }),
    ).toHaveValue('')
    expect(within(dialog).getByText('Fase criada.')).toBeVisible()
  })

  it('uma fase nova sem nome é recusada ao lado do campo', async () => {
    const { api, user } = renderSchedule()
    const { dialog } = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Adicionar fase' }))

    expect(await within(dialog).findByText('Informem o nome da fase.')).toBeVisible()
    expect(api.callsTo(POST_PHASE)).toHaveLength(0)
  })

  it('o 422 de título do servidor aparece no campo da fase nova', async () => {
    const { user } = renderSchedule({
      [POST_PHASE]: problemResponse(422, 'phase_title_required', {
        detail: 'Dê um nome à fase.',
      }),
    })
    const { dialog } = await openDialog(user)

    await user.type(
      within(dialog).getByRole('textbox', { name: 'Nome da nova fase (obrigatório)' }),
      'Algo',
    )
    await user.click(within(dialog).getByRole('button', { name: 'Adicionar fase' }))

    expect(await within(dialog).findByText('Dê um nome à fase.')).toBeVisible()
  })

  it('um conflito de versão avisa, oferece a versão mais recente e não sobrescreve', async () => {
    let lidas = 0
    const newer = renamed(SCHEDULE, ID.faseUm, 'Nome do Outro', 5)
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: () => {
        lidas += 1
        return jsonResponse(200, lidas === 1 ? SCHEDULE : newer)
      },
      [PUT_PHASE(ID.faseUm)]: problemResponse(409, 'version_conflict'),
    })
    const { dialog } = await openDialog(user)

    const campo = within(dialog).getByRole('textbox', { name: 'Fase 1 (obrigatório)' })
    await user.clear(campo)
    await user.type(campo, 'Meu nome')
    await user.click(
      within(dialog).getByRole('button', { name: 'Salvar o nome da fase Fase Exemplo Um' }),
    )

    const alerta = await activeAlert(dialog)
    expect(alerta).toHaveTextContent(/alteradas em outra tela/)
    await user.click(within(alerta).getByRole('button', { name: 'Ver a versão mais recente' }))

    await waitFor(() =>
      expect(within(dialog).getByRole('textbox', { name: 'Fase 1 (obrigatório)' })).toHaveValue(
        'Nome do Outro',
      ),
    )
    expect(api.callsTo(PUT_PHASE(ID.faseUm))).toHaveLength(1)
  })

  it('uma ordem inválida mostra a mensagem do servidor e oferece a versão mais recente', async () => {
    const { user } = renderSchedule({
      [PUT_PHASE_ORDER]: problemResponse(422, 'invalid_phase_order', {
        detail: 'A nova ordem precisa listar todas as fases uma só vez.',
      }),
    })
    const { dialog } = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Descer a fase Fase Exemplo Um' }))

    const alerta = await activeAlert(dialog)
    expect(alerta).toHaveTextContent('A nova ordem precisa listar todas as fases uma só vez.')
    expect(within(alerta).getByRole('button', { name: 'Ver a versão mais recente' })).toBeVisible()
  })

  it('uma falha de rede ao renomear avisa e mantém o nome digitado', async () => {
    const { user } = renderSchedule({
      [PUT_PHASE(ID.faseUm)]: () => {
        throw new TypeError('Failed to fetch')
      },
    })
    const { dialog } = await openDialog(user)

    const campo = within(dialog).getByRole('textbox', { name: 'Fase 1 (obrigatório)' })
    await user.clear(campo)
    await user.type(campo, 'Ainda aqui')
    await user.click(
      within(dialog).getByRole('button', { name: 'Salvar o nome da fase Fase Exemplo Um' }),
    )

    expect(await activeAlert(dialog)).toHaveTextContent(/Não conseguimos salvar as fases/)
    expect(campo).toHaveValue('Ainda aqui')
  })

  it('Esc fecha o diálogo e devolve o foco ao botão Fases', async () => {
    const { user } = renderSchedule()
    const { gatilho } = await openDialog(user)

    await user.keyboard('{Escape}')

    await waitFor(() =>
      expect(screen.queryByRole('dialog', { name: 'Fases do cronograma' })).not.toBeInTheDocument(),
    )
    await waitFor(() => expect(gatilho).toHaveFocus())
  })

  it('o botão Fechar do diálogo também devolve o foco ao botão Fases', async () => {
    const { user } = renderSchedule()
    const { gatilho, dialog } = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Fechar' }))

    await waitFor(() => expect(gatilho).toHaveFocus())
  })
})
