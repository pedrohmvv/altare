import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { GET_SCHEDULE, PUT_MILESTONE, renderSchedule } from '@/test/render-schedule'
import { ID, SCHEDULE, scheduleWith, scheduleWithMoved } from '@/test/schedule-fixtures'
import { memory, openMilestone } from '@/test/schedule-helpers'

const PUT = PUT_MILESTONE(ID.destravado)

describe('editar o marco inteiro: título, fase e categoria (F-CRN-01)', () => {
  it('o formulário mostra o título, a fase e a categoria de agora', async () => {
    const { user } = renderSchedule()
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    expect(within(dialog).getByLabelText('Título (obrigatório)')).toHaveValue(
      'Marco Exemplo Destravado',
    )
    expect(within(dialog).getByRole('combobox', { name: 'Fase' })).toHaveTextContent(
      'Fase Exemplo Um',
    )
    expect(within(dialog).getByRole('combobox', { name: 'Categoria' })).toHaveTextContent(
      'Espaço Exemplo',
    )
    expect(
      within(dialog).getByText(/decide se o marco fica Bloqueado, Opcional ou arquivado/),
    ).toBeVisible()
  })

  it('editar só a nota envia o marco inteiro, porque o PUT substitui tudo', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT]: mem.write(ID.destravado, () => ({ note: 'Só a nota.', version: 2 })),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    const nota = within(dialog).getByLabelText('Nota')
    await user.clear(nota)
    await user.type(nota, 'Só a nota.')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.callsTo(PUT)).toHaveLength(1))
    expect(api.callsTo(PUT)[0]?.body).toEqual({
      title: 'Marco Exemplo Destravado',
      phase_id: ID.faseUm,
      category_id: ID.espaco,
      responsible: 'Noiva',
      note: 'Só a nota.',
      target_date: '2027-03-15',
      version: 1,
    })
  })

  it('renomear envia o título novo e o painel passa a ter o nome novo', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT]: mem.write(ID.destravado, () => ({ title: 'Nome Novo Exemplo', version: 2 })),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    const titulo = within(dialog).getByLabelText('Título (obrigatório)')
    await user.clear(titulo)
    await user.type(titulo, '  Nome Novo Exemplo  ')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.callsTo(PUT)).toHaveLength(1))
    expect(api.callsTo(PUT)[0]?.body).toMatchObject({ title: 'Nome Novo Exemplo' })
    expect(await screen.findByRole('dialog', { name: 'Nome Novo Exemplo' })).toBeVisible()
  })

  it('mover de fase envia o phase_id novo e o painel mostra a fase nova', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT]: mem.set(scheduleWithMoved(ID.destravado, ID.faseDois, { version: 2 })),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('combobox', { name: 'Fase' }))
    await user.click(screen.getByRole('option', { name: 'Fase Exemplo Dois' }))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.callsTo(PUT)).toHaveLength(1))
    expect(api.callsTo(PUT)[0]?.body).toMatchObject({ phase_id: ID.faseDois, version: 1 })
    expect(await within(dialog).findByText('Fase: Fase Exemplo Dois')).toBeVisible()
    expect(within(dialog).getByRole('combobox', { name: 'Fase' })).toHaveTextContent(
      'Fase Exemplo Dois',
    )
  })

  it('trocar a categoria envia o id novo e "Sem categoria" envia nulo', async () => {
    const mem = memory()
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT]: mem.write(ID.destravado, () => ({ version: 2 })),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('combobox', { name: 'Categoria' }))
    await user.click(screen.getByRole('option', { name: 'Buffet Exemplo' }))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))
    await waitFor(() => expect(api.callsTo(PUT)).toHaveLength(1))
    expect(api.callsTo(PUT)[0]?.body).toMatchObject({ category_id: ID.buffet })

    await user.click(within(dialog).getByRole('combobox', { name: 'Categoria' }))
    await user.click(screen.getByRole('option', { name: 'Sem categoria' }))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))
    await waitFor(() => expect(api.callsTo(PUT)).toHaveLength(2))
    expect(api.callsTo(PUT)[1]?.body).toMatchObject({ category_id: null, version: 2 })
  })

  it('uma categoria ligada que saiu das opções continua escolhida, sem ser trocada em silêncio', async () => {
    const mem = memory({
      ...SCHEDULE,
      category_options: SCHEDULE.category_options.filter((option) => option.id !== ID.espaco),
    })
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT]: mem.write(ID.destravado, () => ({ version: 2 })),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    expect(within(dialog).getByRole('combobox', { name: 'Categoria' })).toHaveTextContent(
      'Espaço Exemplo',
    )
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))
    await waitFor(() => expect(api.callsTo(PUT)).toHaveLength(1))
    expect(api.callsTo(PUT)[0]?.body).toMatchObject({ category_id: ID.espaco })
  })

  it('sem título o formulário bloqueia ao lado do campo, sem chamar a API', async () => {
    const { api, user } = renderSchedule()
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.clear(within(dialog).getByLabelText('Título (obrigatório)'))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    expect(await within(dialog).findByText('Informem o título do marco.')).toBeVisible()
    expect(within(dialog).getByLabelText('Título (obrigatório)')).toHaveAttribute(
      'aria-invalid',
      'true',
    )
    expect(api.callsTo(PUT)).toHaveLength(0)
  })

  it('um título longo demais é recusado no campo', async () => {
    const { api, user } = renderSchedule()
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    const titulo = within(dialog).getByLabelText('Título (obrigatório)')
    await user.clear(titulo)
    await user.click(titulo)
    await user.paste('a'.repeat(121))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    expect(await within(dialog).findByText('Usem até 120 caracteres.')).toBeVisible()
    expect(api.callsTo(PUT)).toHaveLength(0)
  })

  it('o 422 de título em branco do servidor aparece no campo Título', async () => {
    const { user } = renderSchedule({
      [PUT]: problemResponse(422, 'milestone_title_required', {
        detail: 'Dê um título ao marco.',
      }),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    expect(await within(dialog).findByText('Dê um título ao marco.')).toBeVisible()
    expect(within(dialog).getByLabelText('Título (obrigatório)')).toHaveAttribute(
      'aria-invalid',
      'true',
    )
  })

  it('o 422 de categoria indisponível aparece no campo Categoria', async () => {
    const { user } = renderSchedule({
      [PUT]: problemResponse(422, 'category_not_available', {
        detail: 'Esta categoria não está disponível no Mapa de Escopo.',
      }),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    expect(
      await within(dialog).findByText('Esta categoria não está disponível no Mapa de Escopo.'),
    ).toBeVisible()
    expect(within(dialog).getByRole('combobox', { name: 'Categoria' })).toHaveAttribute(
      'aria-invalid',
      'true',
    )
    await waitFor(() =>
      expect(within(dialog).getByRole('combobox', { name: 'Categoria' })).toHaveFocus(),
    )
  })

  it('o título é obrigatório por escrito e marcado para o leitor de tela', async () => {
    const { user } = renderSchedule()
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    const titulo = within(dialog).getByLabelText('Título (obrigatório)')
    expect(titulo).toHaveAttribute('aria-required', 'true')
  })

  it('um conflito de versão com título editado mantém o rascunho e oferece a versão mais recente', async () => {
    let lidas = 0
    const newer = scheduleWith(ID.destravado, { title: 'Título do outro', version: 5 })
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: () => {
        lidas += 1
        return jsonResponse(200, lidas === 1 ? SCHEDULE : newer)
      },
      [PUT]: problemResponse(409, 'version_conflict'),
    })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    const titulo = within(dialog).getByLabelText('Título (obrigatório)')
    await user.clear(titulo)
    await user.type(titulo, 'Meu título')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await user.click(
      await within(dialog).findByRole('button', { name: 'Ver a versão mais recente' }),
    )

    await waitFor(() =>
      expect(screen.getByRole('dialog', { name: 'Título do outro' })).toBeVisible(),
    )
    expect(
      within(screen.getByRole('dialog', { name: 'Título do outro' })).getByLabelText(
        'Título (obrigatório)',
      ),
    ).toHaveValue('Título do outro')
    expect(api.callsTo(PUT)).toHaveLength(1)
  })
})
