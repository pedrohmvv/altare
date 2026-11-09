import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { GET_SCHEDULE, PUT_DEPENDENCIES, renderSchedule } from '@/test/render-schedule'
import { ID, SCHEDULE, scheduleWith } from '@/test/schedule-fixtures'
import { activeAlert, memory, openMilestone } from '@/test/schedule-helpers'

const PUT = PUT_DEPENDENCIES(ID.destravado)
const section = (dialog: HTMLElement) => within(dialog).getByRole('region', { name: 'Depende de' })

describe('"Depende de" editável no painel (F-CRN-03)', () => {
  it('cada predecessor tem o seu botão Remover, com o nome do marco para o leitor de tela', async () => {
    const { user } = renderSchedule()
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    const lista = within(section(dialog)).getByRole('list', { name: 'Depende de' })
    expect(within(lista).getByText('Marco Exemplo Concluído')).toBeVisible()
    expect(
      within(lista).getByRole('button', {
        name: 'Remover a dependência de Marco Exemplo Concluído',
      }),
    ).toBeVisible()
  })

  it('"Libera" continua só leitura: nenhum botão de remover nem de adicionar', async () => {
    const { user } = renderSchedule()
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    const libera = within(dialog).getByRole('list', { name: 'Libera' })
    expect(within(libera).queryByRole('button')).not.toBeInTheDocument()
  })

  it('remover envia o conjunto inteiro sem o removido, com a versão do marco', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT]: mem.write(ID.destravado, () => ({ depends_on: [], version: 2 })),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(
      within(dialog).getByRole('button', {
        name: 'Remover a dependência de Marco Exemplo Concluído',
      }),
    )

    await waitFor(() => expect(api.callsTo(PUT)).toHaveLength(1))
    expect(api.callsTo(PUT)[0]?.body).toEqual({ depends_on: [], version: 1 })
    expect(await within(section(dialog)).findByText('Não depende de nenhum marco.')).toBeVisible()
    expect(within(section(dialog)).getByText('Dependência removida.')).toBeVisible()
  })

  it('depois de remover, o foco vai ao título "Depende de", que fica na tela', async () => {
    const mem = memory()
    const { user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT]: mem.write(ID.destravado, () => ({ depends_on: [], version: 2 })),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(
      within(dialog).getByRole('button', {
        name: 'Remover a dependência de Marco Exemplo Concluído',
      }),
    )

    await within(section(dialog)).findByText('Não depende de nenhum marco.')
    await waitFor(() =>
      expect(within(section(dialog)).getByRole('heading', { name: 'Depende de' })).toHaveFocus(),
    )
  })

  it('depois de adicionar, o foco também vai ao título "Depende de"', async () => {
    const mem = memory()
    const { user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT]: mem.write(ID.destravado, () => ({
        depends_on: [
          { id: ID.concluido, title: 'Marco Exemplo Concluído', resolved: true },
          { id: ID.opcional, title: 'Marco Exemplo Opcional', resolved: false },
        ],
        version: 2,
      })),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('combobox', { name: 'Adicionar dependência' }))
    await user.click(screen.getByRole('option', { name: 'Marco Exemplo Opcional' }))
    await user.click(within(dialog).getByRole('button', { name: 'Adicionar' }))

    await within(section(dialog)).findByText('Dependência adicionada.')
    await waitFor(() =>
      expect(within(section(dialog)).getByRole('heading', { name: 'Depende de' })).toHaveFocus(),
    )
  })

  it('remover a única dependência que faltava destrava o marco, pelo estado que a API devolve', async () => {
    const mem = memory()
    const { user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_DEPENDENCIES(ID.bloqueado)]: mem.write(ID.bloqueado, () => ({
        state: 'Destravado',
        blocked_by: [],
        depends_on: [],
        version: 2,
      })),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Bloqueado')
    expect(within(dialog).getByText('Aguardando: Marco Exemplo Destravado')).toBeVisible()

    await user.click(
      within(dialog).getByRole('button', {
        name: 'Remover a dependência de Marco Exemplo Destravado',
      }),
    )

    await waitFor(() => expect(within(dialog).getByText('Destravado')).toBeVisible())
    expect(within(dialog).queryByText(/^Aguardando:/)).not.toBeInTheDocument()
  })

  it('adicionar oferece os marcos vivos agrupados por fase, sem o próprio, os ligados e os arquivados', async () => {
    const { user } = renderSchedule()
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('combobox', { name: 'Adicionar dependência' }))

    const faseUm = screen.getByRole('group', { name: 'Fase Exemplo Um' })
    expect(
      within(faseUm)
        .getAllByRole('option')
        .map((o) => o.textContent),
    ).toEqual(['Marco Exemplo Bloqueado'])
    const faseDois = screen.getByRole('group', { name: 'Fase Exemplo Dois' })
    expect(
      within(faseDois)
        .getAllByRole('option')
        .map((o) => o.textContent),
    ).toEqual([
      'Marco Exemplo da Categoria',
      'Marco Exemplo Opcional',
      'Marco Exemplo com Aviso',
      'Marco Exemplo em Andamento',
    ])
    expect(
      screen.queryByRole('option', { name: 'Marco Exemplo Destravado' }),
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('option', { name: 'Marco Exemplo Arquivado' }),
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('option', { name: 'Marco Exemplo Concluído' }),
    ).not.toBeInTheDocument()
  })

  it('o botão Adicionar só vale depois de escolher um marco; envia o conjunto inteiro', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT]: mem.write(ID.destravado, () => ({
        depends_on: [
          { id: ID.concluido, title: 'Marco Exemplo Concluído', resolved: true },
          { id: ID.opcional, title: 'Marco Exemplo Opcional', resolved: false },
        ],
        version: 2,
      })),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')
    const adicionar = within(dialog).getByRole('button', { name: 'Adicionar' })
    expect(adicionar).toBeDisabled()

    await user.click(within(dialog).getByRole('combobox', { name: 'Adicionar dependência' }))
    await user.click(screen.getByRole('option', { name: 'Marco Exemplo Opcional' }))
    await user.click(adicionar)

    await waitFor(() => expect(api.callsTo(PUT)).toHaveLength(1))
    expect(api.callsTo(PUT)[0]?.body).toEqual({
      depends_on: [ID.concluido, ID.opcional],
      version: 1,
    })
    const lista = await within(section(dialog)).findByRole('list', { name: 'Depende de' })
    expect(within(lista).getByText('Marco Exemplo Opcional')).toBeVisible()
    expect(within(section(dialog)).getByText('Dependência adicionada.')).toBeVisible()
    expect(within(dialog).getByRole('button', { name: 'Adicionar' })).toBeDisabled()
  })

  it('um ciclo é recusado com a mensagem do servidor e o caminho, sem alterar nada', async () => {
    const { user } = renderSchedule({
      [PUT]: problemResponse(422, 'dependency_cycle', {
        detail:
          'Esta dependência fecharia um ciclo: Marco Exemplo Destravado → Marco Exemplo Bloqueado → Marco Exemplo Destravado. Remova uma dessas dependências ou escolha outro marco.',
      }),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('combobox', { name: 'Adicionar dependência' }))
    await user.click(screen.getByRole('option', { name: 'Marco Exemplo Bloqueado' }))
    await user.click(within(dialog).getByRole('button', { name: 'Adicionar' }))

    const alerta = await activeAlert(section(dialog))
    expect(alerta).toHaveTextContent(
      'Marco Exemplo Destravado → Marco Exemplo Bloqueado → Marco Exemplo Destravado',
    )
    const lista = within(section(dialog)).getByRole('list', { name: 'Depende de' })
    expect(within(lista).getAllByRole('listitem')).toHaveLength(1)
  })

  it('a auto-dependência recusada pelo servidor também aparece no aviso da seção', async () => {
    const { user } = renderSchedule({
      [PUT]: problemResponse(422, 'self_dependency', {
        detail: 'Um marco não pode depender dele mesmo. Escolha outro marco.',
      }),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('combobox', { name: 'Adicionar dependência' }))
    await user.click(screen.getByRole('option', { name: 'Marco Exemplo Bloqueado' }))
    await user.click(within(dialog).getByRole('button', { name: 'Adicionar' }))

    expect(await activeAlert(section(dialog))).toHaveTextContent(
      'Um marco não pode depender dele mesmo.',
    )
  })

  it('a região de aviso da seção existe vazia desde o início, para o leitor de tela anunciar', async () => {
    const { user } = renderSchedule()
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    expect(within(section(dialog)).getByRole('alert')).toBeEmptyDOMElement()
  })

  it('um conflito de versão oferece a versão mais recente, sem sobrescrever', async () => {
    let lidas = 0
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: () => {
        lidas += 1
        return jsonResponse(
          200,
          lidas === 1 ? SCHEDULE : scheduleWith(ID.destravado, { depends_on: [], version: 4 }),
        )
      },
      [PUT]: problemResponse(409, 'version_conflict'),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(
      within(dialog).getByRole('button', {
        name: 'Remover a dependência de Marco Exemplo Concluído',
      }),
    )
    const alerta = await activeAlert(section(dialog))
    await user.click(within(alerta).getByRole('button', { name: 'Ver a versão mais recente' }))

    expect(await within(section(dialog)).findByText('Não depende de nenhum marco.')).toBeVisible()
    expect(api.callsTo(PUT)).toHaveLength(1)
  })

  it('uma falha de rede avisa e não muda a lista', async () => {
    const { user } = renderSchedule({
      [PUT]: () => {
        throw new TypeError('Failed to fetch')
      },
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(
      within(dialog).getByRole('button', {
        name: 'Remover a dependência de Marco Exemplo Concluído',
      }),
    )

    expect(await activeAlert(section(dialog))).toHaveTextContent(/Não conseguimos salvar/)
    expect(within(section(dialog)).getByText('Marco Exemplo Concluído')).toBeVisible()
  })
})
