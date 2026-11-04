import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import {
  DELETE_MILESTONE,
  GET_SCHEDULE,
  RESTORE_MILESTONE,
  renderSchedule,
} from '@/test/render-schedule'
import { ID, SCHEDULE } from '@/test/schedule-fixtures'
import { activeAlert, memory, openMilestone } from '@/test/schedule-helpers'
import type { Schedule } from '../api/schedule'

const without = (id: string): Schedule => ({
  ...SCHEDULE,
  phases: SCHEDULE.phases.map((phase) => ({
    ...phase,
    milestones: phase.milestones.filter((item) => item.id !== id),
  })),
})

async function askToDelete(name: string, user: ReturnType<typeof renderSchedule>['user']) {
  const painel = await openMilestone(user, name)
  const gatilho = within(painel).getByRole('button', { name: 'Excluir marco' })
  await user.click(gatilho)
  const confirmacao = await screen.findByRole('dialog', { name: `Excluir “${name}”?` })
  return { painel, gatilho, confirmacao }
}

describe('excluir marco (F-CRN-01, regra 3)', () => {
  it('com dependentes, lista os nomes e diz que deixam de depender', async () => {
    const { user } = renderSchedule()
    const { confirmacao } = await askToDelete('Marco Exemplo Destravado', user)

    expect(
      within(confirmacao).getByRole('heading', { level: 3, name: 'Marcos que dependem dele' }),
    ).toBeVisible()
    expect(within(confirmacao).getByText('Marco Exemplo Bloqueado')).toBeVisible()
    expect(within(confirmacao).getByText(/deixam de depender dele/)).toBeVisible()
    expect(within(confirmacao).getByText(/pode ser restaurado/)).toBeVisible()
  })

  it('sem dependentes, diz que nenhum marco depende dele', async () => {
    const { user } = renderSchedule()
    const { confirmacao } = await askToDelete('Marco Exemplo Opcional', user)

    expect(within(confirmacao).getByText('Nenhum marco depende dele.')).toBeVisible()
    expect(within(confirmacao).queryByRole('list')).not.toBeInTheDocument()
  })

  it('confirmar envia o DELETE com a versão, fecha o painel, limpa o marco da URL e avisa', async () => {
    const mem = memory()
    const { api, user, probe } = renderSchedule(
      {
        [GET_SCHEDULE]: mem.get,
        [DELETE_MILESTONE(ID.opcional)]: mem.set(without(ID.opcional)),
      },
      { marco: ID.opcional },
    )
    const painel = await screen.findByRole('dialog', { name: 'Marco Exemplo Opcional' })
    await user.click(within(painel).getByRole('button', { name: 'Excluir marco' }))
    const confirmacao = await screen.findByRole('dialog', {
      name: 'Excluir “Marco Exemplo Opcional”?',
    })

    await user.click(within(confirmacao).getByRole('button', { name: 'Excluir marco' }))

    await waitFor(() => expect(api.callsTo(DELETE_MILESTONE(ID.opcional))).toHaveLength(1))
    const chamada = api.callsTo(DELETE_MILESTONE(ID.opcional))[0]
    expect(new URL(chamada?.request.url ?? '').searchParams.get('version')).toBe('1')
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(probe.current.marco).toBeUndefined()
    expect(screen.queryByRole('button', { name: 'Marco Exemplo Opcional' })).not.toBeInTheDocument()
    expect(await screen.findByText('Marco excluído')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Desfazer' })).toBeVisible()
    // Sem painel nem marco, o foco vai ao título da página, que fica.
    expect(screen.getByRole('heading', { level: 1 })).toHaveFocus()
  })

  it('Desfazer chama a restauração e o marco volta à lista', async () => {
    const mem = memory()
    const { api, user } = renderSchedule(
      {
        [GET_SCHEDULE]: mem.get,
        [DELETE_MILESTONE(ID.opcional)]: mem.set(without(ID.opcional)),
        [RESTORE_MILESTONE(ID.opcional)]: () => {
          mem.state.schedule = SCHEDULE
          return jsonResponse(200, { schedule: SCHEDULE, left_out: [] })
        },
      },
      { marco: ID.opcional },
    )
    const painel = await screen.findByRole('dialog', { name: 'Marco Exemplo Opcional' })
    await user.click(within(painel).getByRole('button', { name: 'Excluir marco' }))
    const confirmacao = await screen.findByRole('dialog', {
      name: 'Excluir “Marco Exemplo Opcional”?',
    })
    await user.click(within(confirmacao).getByRole('button', { name: 'Excluir marco' }))

    await user.click(await screen.findByRole('button', { name: 'Desfazer' }))

    await waitFor(() => expect(api.callsTo(RESTORE_MILESTONE(ID.opcional))).toHaveLength(1))
    expect(await screen.findByRole('button', { name: 'Marco Exemplo Opcional' })).toBeVisible()
    expect(api.callsTo(GET_SCHEDULE)).toHaveLength(1)
  })

  it('se alguma ligação não voltou, o aviso cita os títulos e o sentido', async () => {
    const mem = memory()
    const { user } = renderSchedule(
      {
        [GET_SCHEDULE]: mem.get,
        [DELETE_MILESTONE(ID.opcional)]: mem.set(without(ID.opcional)),
        [RESTORE_MILESTONE(ID.opcional)]: jsonResponse(200, {
          schedule: SCHEDULE,
          left_out: [
            {
              milestone_id: ID.bloqueado,
              title: 'Marco Exemplo Bloqueado',
              direction: 'depends_on',
            },
            {
              milestone_id: ID.categoria,
              title: 'Marco Exemplo da Categoria',
              direction: 'dependency_of',
            },
          ],
        }),
      },
      { marco: ID.opcional },
    )
    const painel = await screen.findByRole('dialog', { name: 'Marco Exemplo Opcional' })
    await user.click(within(painel).getByRole('button', { name: 'Excluir marco' }))
    const confirmacao = await screen.findByRole('dialog', {
      name: 'Excluir “Marco Exemplo Opcional”?',
    })
    await user.click(within(confirmacao).getByRole('button', { name: 'Excluir marco' }))
    await user.click(await screen.findByRole('button', { name: 'Desfazer' }))

    expect(await screen.findByText('Marco restaurado, com ressalvas')).toBeVisible()
    expect(
      screen.getByText(
        /depende de Marco Exemplo Bloqueado; é dependência de Marco Exemplo da Categoria/,
      ),
    ).toBeVisible()
  })

  it('restaurar sem ressalva só confirma, sem listar nada', async () => {
    const mem = memory()
    const { user } = renderSchedule(
      {
        [GET_SCHEDULE]: mem.get,
        [DELETE_MILESTONE(ID.opcional)]: mem.set(without(ID.opcional)),
        [RESTORE_MILESTONE(ID.opcional)]: jsonResponse(200, { schedule: SCHEDULE, left_out: [] }),
      },
      { marco: ID.opcional },
    )
    const painel = await screen.findByRole('dialog', { name: 'Marco Exemplo Opcional' })
    await user.click(within(painel).getByRole('button', { name: 'Excluir marco' }))
    const confirmacao = await screen.findByRole('dialog', {
      name: 'Excluir “Marco Exemplo Opcional”?',
    })
    await user.click(within(confirmacao).getByRole('button', { name: 'Excluir marco' }))
    await user.click(await screen.findByRole('button', { name: 'Desfazer' }))

    expect(await screen.findByText('Marco restaurado')).toBeVisible()
    expect(screen.queryByText(/ressalvas/)).not.toBeInTheDocument()
  })

  it('se restaurar falha, o aviso diz que o marco segue guardado e oferece Tentar de novo', async () => {
    const mem = memory()
    let tentativas = 0
    const { api, user } = renderSchedule(
      {
        [GET_SCHEDULE]: mem.get,
        [DELETE_MILESTONE(ID.opcional)]: mem.set(without(ID.opcional)),
        [RESTORE_MILESTONE(ID.opcional)]: () => {
          tentativas += 1
          if (tentativas === 1) return problemResponse(500, 'internal_error')
          mem.state.schedule = SCHEDULE
          return jsonResponse(200, { schedule: SCHEDULE, left_out: [] })
        },
      },
      { marco: ID.opcional },
    )
    const painel = await screen.findByRole('dialog', { name: 'Marco Exemplo Opcional' })
    await user.click(within(painel).getByRole('button', { name: 'Excluir marco' }))
    const confirmacao = await screen.findByRole('dialog', {
      name: 'Excluir “Marco Exemplo Opcional”?',
    })
    await user.click(within(confirmacao).getByRole('button', { name: 'Excluir marco' }))
    await user.click(await screen.findByRole('button', { name: 'Desfazer' }))

    expect(await screen.findByText('Não conseguimos restaurar o marco agora.')).toBeVisible()
    expect(screen.getByText(/segue guardado/)).toBeVisible()
    await user.click(screen.getByRole('button', { name: 'Tentar de novo' }))

    await waitFor(() => expect(api.callsTo(RESTORE_MILESTONE(ID.opcional))).toHaveLength(2))
    expect(await screen.findByText('Marco restaurado')).toBeVisible()
    expect(await screen.findByRole('button', { name: 'Marco Exemplo Opcional' })).toBeVisible()
  })

  it('cancelar não envia nada e devolve o foco ao botão Excluir marco', async () => {
    const { api, user } = renderSchedule()
    const { gatilho, confirmacao } = await askToDelete('Marco Exemplo Opcional', user)

    await user.click(within(confirmacao).getByRole('button', { name: 'Cancelar' }))

    expect(api.callsTo(DELETE_MILESTONE(ID.opcional))).toHaveLength(0)
    await waitFor(() => expect(gatilho).toHaveFocus())
    expect(screen.getByRole('dialog', { name: 'Marco Exemplo Opcional' })).toBeVisible()
  })

  it('Esc fecha só a confirmação e devolve o foco ao botão Excluir marco', async () => {
    const { user } = renderSchedule()
    const { gatilho } = await askToDelete('Marco Exemplo Opcional', user)

    await user.keyboard('{Escape}')

    await waitFor(() =>
      expect(
        screen.queryByRole('dialog', { name: 'Excluir “Marco Exemplo Opcional”?' }),
      ).not.toBeInTheDocument(),
    )
    expect(screen.getByRole('dialog', { name: 'Marco Exemplo Opcional' })).toBeVisible()
    await waitFor(() => expect(gatilho).toHaveFocus())
  })

  it('um conflito de versão avisa dentro da confirmação, oferece a versão mais recente e não exclui', async () => {
    const { user } = renderSchedule({
      [DELETE_MILESTONE(ID.opcional)]: problemResponse(409, 'version_conflict'),
    })
    const { confirmacao } = await askToDelete('Marco Exemplo Opcional', user)

    await user.click(within(confirmacao).getByRole('button', { name: 'Excluir marco' }))

    const alerta = await activeAlert(confirmacao)
    expect(alerta).toHaveTextContent(/alterado em outra tela/)
    expect(within(alerta).getByRole('button', { name: 'Ver a versão mais recente' })).toBeVisible()
    expect(screen.queryByText('Marco excluído')).not.toBeInTheDocument()
  })

  it('uma falha de rede avisa dentro da confirmação e deixa tentar de novo', async () => {
    const { user } = renderSchedule({
      [DELETE_MILESTONE(ID.opcional)]: () => {
        throw new TypeError('Failed to fetch')
      },
    })
    const { confirmacao } = await askToDelete('Marco Exemplo Opcional', user)

    await user.click(within(confirmacao).getByRole('button', { name: 'Excluir marco' }))

    expect(await activeAlert(confirmacao)).toHaveTextContent(/Não conseguimos excluir/)
    expect(within(confirmacao).getByRole('button', { name: 'Excluir marco' })).toBeEnabled()
  })
})
