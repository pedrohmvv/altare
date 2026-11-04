import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { GET_SCHEDULE, PUT_MILESTONE, PUT_STATE, renderSchedule } from '@/test/render-schedule'
import { ID, SCHEDULE, scheduleWith } from '@/test/schedule-fixtures'
import { activeAlert, memory, openMilestone } from '@/test/schedule-helpers'

const open = openMilestone

describe('detalhe do marco (F-CRN-09)', () => {
  it('mostra fase, estado, responsável, categoria, prazo, nota, o que ele pede e o que ele libera', async () => {
    const { user } = renderSchedule()
    const dialog = await open(user, 'Marco Exemplo Destravado')

    expect(within(dialog).getByText('Fase: Fase Exemplo Um')).toBeVisible()
    expect(within(dialog).getByText('Destravado')).toBeVisible()
    expect(within(dialog).getByRole('combobox', { name: 'Responsável' })).toHaveTextContent('Noiva')
    expect(within(dialog).getByLabelText('Prazo-alvo')).toHaveValue('2027-03-15')
    expect(within(dialog).getByLabelText('Nota')).toHaveValue('Nota de exemplo.')
    expect(within(dialog).getByRole('combobox', { name: 'Categoria' })).toHaveTextContent(
      'Espaço Exemplo',
    )
    const dependsOn = within(dialog).getByRole('list', { name: 'Depende de' })
    expect(within(dependsOn).getByText(/Marco Exemplo Concluído/)).toBeVisible()
    const unlocks = within(dialog).getByRole('list', { name: 'Libera' })
    expect(within(unlocks).getByText('Marco Exemplo Bloqueado')).toBeVisible()
  })

  it('sem categoria nem vínculos, diz isso em palavras', async () => {
    const { user } = renderSchedule()
    const dialog = await open(user, 'Marco Exemplo Opcional')

    expect(within(dialog).getByRole('combobox', { name: 'Categoria' })).toHaveTextContent(
      'Sem categoria',
    )
    expect(within(dialog).getByText('Não depende de nenhum marco.')).toBeVisible()
    expect(within(dialog).getByText('Não libera nenhum marco.')).toBeVisible()
  })

  it('o bloqueado repete o que falta, com os nomes', async () => {
    const { user } = renderSchedule()
    const dialog = await open(user, 'Marco Exemplo Bloqueado')

    expect(within(dialog).getByText('Bloqueado')).toBeVisible()
    expect(within(dialog).getByText('Aguardando: Marco Exemplo Destravado')).toBeVisible()
  })

  it('o aviso de predecessor não resolvido também aparece no painel', async () => {
    const { user } = renderSchedule()
    const dialog = await open(user, 'Marco Exemplo com Aviso')

    expect(
      within(dialog).getByText(
        'Concluído antes de: Marco Exemplo Bloqueado, Marco Exemplo da Categoria',
      ),
    ).toBeVisible()
  })
})

describe('editar responsável, prazo e nota (F-CRN-05)', () => {
  it('envia só o que o marco tem de editável, com a versão que a tela viu', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_MILESTONE(ID.destravado)]: mem.write(ID.destravado, () => ({
        responsible: 'Noivo',
        note: 'Outra nota.',
        target_date: '2027-04-01',
        version: 2,
      })),
    })
    const dialog = await open(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('combobox', { name: 'Responsável' }))
    await user.click(screen.getByRole('option', { name: 'Noivo' }))
    const prazo = within(dialog).getByLabelText('Prazo-alvo')
    await user.clear(prazo)
    await user.type(prazo, '2027-04-01')
    const nota = within(dialog).getByLabelText('Nota')
    await user.clear(nota)
    await user.type(nota, 'Outra nota.')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.callsTo(PUT_MILESTONE(ID.destravado))).toHaveLength(1))
    expect(api.callsTo(PUT_MILESTONE(ID.destravado))[0]?.body).toEqual({
      title: 'Marco Exemplo Destravado',
      phase_id: ID.faseUm,
      category_id: ID.espaco,
      responsible: 'Noivo',
      note: 'Outra nota.',
      target_date: '2027-04-01',
      version: 1,
    })
    expect(await within(dialog).findByText('Alterações salvas.')).toBeVisible()
    // O cronograma devolvido vai direto para o cache: nenhuma segunda leitura.
    expect(api.callsTo(GET_SCHEDULE)).toHaveLength(1)
  })

  it('o prazo pode ser tirado e a nota em branco vira nenhuma nota', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_MILESTONE(ID.destravado)]: mem.write(ID.destravado, () => ({
        note: null,
        target_date: null,
        version: 2,
      })),
    })
    const dialog = await open(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('button', { name: 'Tirar o prazo' }))
    await user.clear(within(dialog).getByLabelText('Nota'))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.callsTo(PUT_MILESTONE(ID.destravado))).toHaveLength(1))
    expect(api.callsTo(PUT_MILESTONE(ID.destravado))[0]?.body).toEqual({
      title: 'Marco Exemplo Destravado',
      phase_id: ID.faseUm,
      category_id: ID.espaco,
      responsible: 'Noiva',
      note: null,
      target_date: null,
      version: 1,
    })
  })

  it('uma nota longa demais é recusada ao lado do campo, sem chamar a API', async () => {
    const { api, user } = renderSchedule()
    const dialog = await open(user, 'Marco Exemplo Destravado')

    const nota = within(dialog).getByLabelText('Nota')
    await user.clear(nota)
    await user.click(nota)
    await user.paste('a'.repeat(501))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    expect(await within(dialog).findByText('Usem até 500 caracteres.')).toBeVisible()
    expect(nota).toHaveAttribute('aria-invalid', 'true')
    expect(api.callsTo(PUT_MILESTONE(ID.destravado))).toHaveLength(0)
  })

  it('um conflito de versão oferece a versão mais recente e nunca sobrescreve', async () => {
    let lidas = 0
    const newer = scheduleWith(ID.destravado, { note: 'Nota do outro.', version: 5 })
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: () => {
        lidas += 1
        return jsonResponse(200, lidas === 1 ? SCHEDULE : newer)
      },
      [PUT_MILESTONE(ID.destravado)]: problemResponse(409, 'version_conflict'),
    })
    const dialog = await open(user, 'Marco Exemplo Destravado')

    const nota = within(dialog).getByLabelText('Nota')
    await user.clear(nota)
    await user.type(nota, 'Minha nota.')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    const alerta = await activeAlert(dialog)
    expect(within(alerta).getByText(/alterado em outra tela/)).toBeVisible()
    await user.click(within(alerta).getByRole('button', { name: 'Ver a versão mais recente' }))

    await waitFor(() => expect(within(dialog).getByLabelText('Nota')).toHaveValue('Nota do outro.'))
    expect(api.callsTo(PUT_MILESTONE(ID.destravado))).toHaveLength(1)
    for (const region of within(dialog).getAllByRole('alert')) expect(region).toBeEmptyDOMElement()
  })

  it('uma falha de rede avisa e mantém o que foi digitado', async () => {
    const { user } = renderSchedule({
      [PUT_MILESTONE(ID.destravado)]: () => {
        throw new TypeError('Failed to fetch')
      },
    })
    const dialog = await open(user, 'Marco Exemplo Destravado')

    const nota = within(dialog).getByLabelText('Nota')
    await user.clear(nota)
    await user.type(nota, 'Ainda aqui.')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    expect(await within(dialog).findByText(/Não conseguimos salvar agora/)).toBeVisible()
    expect(nota).toHaveValue('Ainda aqui.')
  })

  it('um erro da API sem campo mostra a frase dela em português', async () => {
    const { user } = renderSchedule({
      [PUT_MILESTONE(ID.destravado)]: problemResponse(422, 'invalid_schedule_value', {
        detail: 'Esse valor não serve para o marco.',
      }),
    })
    const dialog = await open(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    expect(await within(dialog).findByText('Esse valor não serve para o marco.')).toBeVisible()
  })
})

describe('estados manuais (F-CRN-03)', () => {
  it('marcar um Destravado em andamento envia sem ignorar bloqueio e mostra o novo estado', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_STATE(ID.destravado)]: mem.write(ID.destravado, () => ({
        state: 'Em andamento',
        version: 2,
      })),
    })
    const dialog = await open(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('button', { name: 'Marcar em andamento' }))

    await waitFor(() => expect(api.callsTo(PUT_STATE(ID.destravado))).toHaveLength(1))
    expect(api.callsTo(PUT_STATE(ID.destravado))[0]?.body).toEqual({
      state: 'Em andamento',
      ignore_block: false,
      version: 1,
    })
    expect(await within(dialog).findByText('Em andamento')).toBeVisible()
    expect(within(dialog).getByText('Marco marcado em andamento.')).toBeVisible()
    expect(api.callsTo(GET_SCHEDULE)).toHaveLength(1)
  })

  it('concluir um Destravado envia Concluído e passa a oferecer Reabrir', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_STATE(ID.opcional)]: mem.write(ID.opcional, () => ({ state: 'Concluído', version: 2 })),
    })
    const dialog = await open(user, 'Marco Exemplo Opcional')

    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

    await waitFor(() => expect(api.callsTo(PUT_STATE(ID.opcional))).toHaveLength(1))
    expect(api.callsTo(PUT_STATE(ID.opcional))[0]?.body).toMatchObject({
      state: 'Concluído',
      ignore_block: false,
    })
    expect(await within(dialog).findByRole('button', { name: 'Reabrir' })).toBeVisible()
    expect(within(dialog).queryByRole('button', { name: 'Concluir' })).not.toBeInTheDocument()
    // O botão que tinha o foco sumiu: o foco vai a um ponto estável, o título "Estado".
    await waitFor(() =>
      expect(within(dialog).getByRole('heading', { name: 'Estado' })).toHaveFocus(),
    )
  })

  it('cada estado oferece só as ações que fazem sentido', async () => {
    const { user } = renderSchedule()
    const andamento = await open(user, 'Marco Exemplo em Andamento')

    expect(within(andamento).getByRole('button', { name: 'Concluir' })).toBeVisible()
    expect(within(andamento).getByRole('button', { name: 'Reabrir' })).toBeVisible()
    expect(
      within(andamento).queryByRole('button', { name: 'Marcar em andamento' }),
    ).not.toBeInTheDocument()
  })

  describe('marco com algo aguardando: confirmação de ignorar o bloqueio', () => {
    it('pede confirmação listando o que falta e só então envia ignore_block', async () => {
      const mem = memory()
      const { api, user } = renderSchedule({
        [GET_SCHEDULE]: mem.get,
        [PUT_STATE(ID.bloqueado)]: mem.write(ID.bloqueado, () => ({
          state: 'Concluído',
          version: 2,
        })),
      })
      const dialog = await open(user, 'Marco Exemplo Bloqueado')

      await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

      const confirmacao = await screen.findByRole('dialog', { name: 'Ignorar o bloqueio?' })
      expect(within(confirmacao).getByText('Marco Exemplo Destravado')).toBeVisible()
      expect(api.callsTo(PUT_STATE(ID.bloqueado))).toHaveLength(0)

      await user.click(within(confirmacao).getByRole('button', { name: 'Concluir mesmo assim' }))

      await waitFor(() => expect(api.callsTo(PUT_STATE(ID.bloqueado))).toHaveLength(1))
      expect(api.callsTo(PUT_STATE(ID.bloqueado))[0]?.body).toEqual({
        state: 'Concluído',
        ignore_block: true,
        version: 1,
      })
      await waitFor(() =>
        expect(
          screen.queryByRole('dialog', { name: 'Ignorar o bloqueio?' }),
        ).not.toBeInTheDocument(),
      )
      await waitFor(() =>
        expect(within(dialog).getByRole('heading', { name: 'Estado' })).toHaveFocus(),
      )
    })

    it('a lista do que falta tem título no nível certo, abaixo do título do diálogo', async () => {
      const { user } = renderSchedule()
      const dialog = await open(user, 'Marco Exemplo Bloqueado')

      await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

      const confirmacao = await screen.findByRole('dialog', { name: 'Ignorar o bloqueio?' })
      expect(within(confirmacao).queryByRole('heading', { level: 4 })).not.toBeInTheDocument()
      expect(
        within(confirmacao).getByRole('heading', { level: 3, name: 'O que falta' }),
      ).toBeVisible()
    })

    it('cancelar não envia nada e devolve o foco ao botão que abriu a confirmação', async () => {
      const { api, user } = renderSchedule()
      const dialog = await open(user, 'Marco Exemplo Bloqueado')

      const origem = within(dialog).getByRole('button', { name: 'Marcar em andamento' })
      await user.click(origem)
      const confirmacao = await screen.findByRole('dialog', { name: 'Ignorar o bloqueio?' })
      await user.click(within(confirmacao).getByRole('button', { name: 'Cancelar' }))

      expect(api.callsTo(PUT_STATE(ID.bloqueado))).toHaveLength(0)
      expect(screen.queryByRole('dialog', { name: 'Ignorar o bloqueio?' })).not.toBeInTheDocument()
      await waitFor(() => expect(origem).toHaveFocus())
    })

    it('Esc também cancela e devolve o foco ao botão de origem', async () => {
      const { api, user } = renderSchedule()
      const dialog = await open(user, 'Marco Exemplo Bloqueado')

      const origem = within(dialog).getByRole('button', { name: 'Concluir' })
      await user.click(origem)
      await screen.findByRole('dialog', { name: 'Ignorar o bloqueio?' })
      await user.keyboard('{Escape}')

      await waitFor(() =>
        expect(
          screen.queryByRole('dialog', { name: 'Ignorar o bloqueio?' }),
        ).not.toBeInTheDocument(),
      )
      // O Esc fecha só a confirmação: o painel continua aberto.
      expect(screen.getByRole('dialog', { name: 'Marco Exemplo Bloqueado' })).toBeVisible()
      expect(api.callsTo(PUT_STATE(ID.bloqueado))).toHaveLength(0)
      await waitFor(() => expect(origem).toHaveFocus())
    })

    it('se a confirmação dá erro, o aviso aparece e o foco volta ao botão de origem', async () => {
      const { user } = renderSchedule({
        [PUT_STATE(ID.bloqueado)]: problemResponse(500, 'internal_error', {
          detail: 'Falha da API.',
        }),
      })
      const dialog = await open(user, 'Marco Exemplo Bloqueado')

      const origem = within(dialog).getByRole('button', { name: 'Concluir' })
      await user.click(origem)
      const confirmacao = await screen.findByRole('dialog', { name: 'Ignorar o bloqueio?' })
      await user.click(within(confirmacao).getByRole('button', { name: 'Concluir mesmo assim' }))

      expect(await within(dialog).findByText('Falha da API.')).toBeVisible()
      await waitFor(() => expect(origem).toHaveFocus())
    })

    it('a categoria por classificar aparece na lista do que falta, com a frase da API', async () => {
      const { user } = renderSchedule()
      const dialog = await open(user, 'Marco Exemplo da Categoria')

      await user.click(within(dialog).getByRole('button', { name: 'Marcar em andamento' }))

      const confirmacao = await screen.findByRole('dialog', { name: 'Ignorar o bloqueio?' })
      expect(
        within(confirmacao).getByText('Aguardando classificar a categoria no Mapa de Escopo'),
      ).toBeVisible()
      await user.click(
        within(confirmacao).getByRole('button', { name: 'Marcar em andamento mesmo assim' }),
      )
    })

    it('o Em andamento que ainda tem o que aguardar também pede confirmação para concluir', async () => {
      const { api, user } = renderSchedule()
      const dialog = await open(user, 'Marco Exemplo em Andamento')

      await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

      expect(await screen.findByRole('dialog', { name: 'Ignorar o bloqueio?' })).toBeVisible()
      expect(api.callsTo(PUT_STATE(ID.andamento))).toHaveLength(0)
    })

    it('se o servidor diz que passou a estar bloqueado, explica e não força', async () => {
      const { api, user } = renderSchedule({
        [PUT_STATE(ID.opcional)]: problemResponse(422, 'milestone_blocked', {
          detail: 'Detalhe da API.',
        }),
      })
      const dialog = await open(user, 'Marco Exemplo Opcional')

      await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))

      expect(await within(dialog).findByText(/passou a aguardar outra coisa/)).toBeVisible()
      expect(api.callsTo(PUT_STATE(ID.opcional))).toHaveLength(1)
      expect(api.callsTo(PUT_STATE(ID.opcional))[0]?.body).toMatchObject({ ignore_block: false })
    })
  })

  describe('reabrir', () => {
    it('um Concluído que libera outros avisa quais voltam a ficar bloqueados e só então reabre', async () => {
      const mem = memory()
      const { api, user } = renderSchedule({
        [GET_SCHEDULE]: mem.get,
        [PUT_STATE(ID.concluido)]: mem.write(ID.concluido, () => ({
          state: 'Destravado',
          version: 2,
        })),
      })
      const dialog = await open(user, 'Marco Exemplo Concluído')

      await user.click(within(dialog).getByRole('button', { name: 'Reabrir' }))

      const confirmacao = await screen.findByRole('dialog', { name: 'Reabrir este marco?' })
      expect(within(confirmacao).getByText('Marco Exemplo Destravado')).toBeVisible()
      expect(
        within(confirmacao).getByText(
          /Os que ainda não foram concluídos podem voltar a ficar bloqueados\./,
        ),
      ).toBeVisible()
      expect(within(confirmacao).getByRole('heading', { level: 3, name: 'Libera' })).toBeVisible()
      expect(api.callsTo(PUT_STATE(ID.concluido))).toHaveLength(0)

      await user.click(within(confirmacao).getByRole('button', { name: 'Reabrir marco' }))

      await waitFor(() => expect(api.callsTo(PUT_STATE(ID.concluido))).toHaveLength(1))
      expect(api.callsTo(PUT_STATE(ID.concluido))[0]?.body).toEqual({
        state: null,
        ignore_block: false,
        version: 1,
      })
    })

    it('um marco que não libera ninguém reabre direto, sem confirmação', async () => {
      const mem = memory()
      const { api, user } = renderSchedule({
        [GET_SCHEDULE]: mem.get,
        [PUT_STATE(ID.aviso)]: mem.write(ID.aviso, () => ({ state: 'Destravado', version: 2 })),
      })
      const dialog = await open(user, 'Marco Exemplo com Aviso')

      await user.click(within(dialog).getByRole('button', { name: 'Reabrir' }))

      await waitFor(() => expect(api.callsTo(PUT_STATE(ID.aviso))).toHaveLength(1))
      expect(screen.queryByRole('dialog', { name: 'Reabrir este marco?' })).not.toBeInTheDocument()
    })
  })

  it('um conflito de versão no estado avisa e oferece a versão mais recente', async () => {
    let lidas = 0
    const { user } = renderSchedule({
      [GET_SCHEDULE]: () => {
        lidas += 1
        return jsonResponse(
          200,
          lidas === 1 ? SCHEDULE : scheduleWith(ID.opcional, { state: 'Concluído', version: 4 }),
        )
      },
      [PUT_STATE(ID.opcional)]: problemResponse(409, 'version_conflict'),
    })
    const dialog = await open(user, 'Marco Exemplo Opcional')

    await user.click(within(dialog).getByRole('button', { name: 'Marcar em andamento' }))

    const alerta = await activeAlert(dialog)
    expect(within(alerta).getByText(/alterado em outra tela/)).toBeVisible()
    await user.click(within(alerta).getByRole('button', { name: 'Ver a versão mais recente' }))
    expect(await within(dialog).findByRole('button', { name: 'Reabrir' })).toBeVisible()
  })

  it('depois de mudar o estado, salvar a nota usa a versão nova, que é a nossa', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_STATE(ID.opcional)]: mem.write(ID.opcional, () => ({ state: 'Concluído', version: 2 })),
      [PUT_MILESTONE(ID.opcional)]: mem.write(ID.opcional, () => ({ version: 3 })),
    })
    const dialog = await open(user, 'Marco Exemplo Opcional')

    await user.click(within(dialog).getByRole('button', { name: 'Concluir' }))
    await within(dialog).findByRole('button', { name: 'Reabrir' })
    await user.type(within(dialog).getByLabelText('Nota'), 'Feito.')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.callsTo(PUT_MILESTONE(ID.opcional))).toHaveLength(1))
    expect(api.callsTo(PUT_MILESTONE(ID.opcional))[0]?.body).toMatchObject({
      note: 'Feito.',
      version: 2,
    })
  })
})
