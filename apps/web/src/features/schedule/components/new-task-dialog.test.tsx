import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { GET_SCHEDULE, POST_TASK, renderSchedule } from '@/test/render-schedule'
import { ID, scheduleWithTasks, task } from '@/test/schedule-fixtures'
import { memory } from '@/test/schedule-helpers'

// F-CRN-06: "Nova avulsa" (responsável padrão = perfil da sessão; foco; id achado por diferença).
const NEW = task({ id: ID.avulsaNova, title: 'Avulsa Exemplo Nova', responsible: 'Noiva' })

function setup(
  profile: 'Noivo' | 'Noiva' = 'Noiva',
  post: (store: ReturnType<typeof memory>) => object = (store) => ({
    [POST_TASK]: store.addTask(NEW),
  }),
) {
  const store = memory(scheduleWithTasks([]))
  const view = renderSchedule(
    { [GET_SCHEDULE]: store.get, ...post(store) } as never,
    {},
    { profile },
  )
  return { store, ...view }
}

/** O botão do cabeçalho: o primeiro; o do estado vazio da seção vem depois. */
async function headerButton() {
  const [button] = await screen.findAllByRole('button', { name: 'Nova avulsa' })
  return button as HTMLElement
}

async function openDialog(user: ReturnType<typeof renderSchedule>['user']) {
  await user.click(await headerButton())
  return screen.findByRole('dialog', { name: 'Nova avulsa' })
}

describe('Nova avulsa (F-CRN-06)', () => {
  it('abre pelo botão do cabeçalho, com o perfil da sessão como responsável', async () => {
    const { user } = setup('Noiva')
    const dialog = await openDialog(user)
    expect(within(dialog).getByRole('combobox', { name: 'Responsável' })).toHaveTextContent('Noiva')
    expect(within(dialog).getByLabelText('Prazo')).toHaveValue('')
    expect(within(dialog).getByLabelText('Nota')).toHaveValue('')
  })

  it('o perfil Noivo vira o padrão do Noivo, nunca Ambos', async () => {
    const { user, api } = setup('Noivo')
    const dialog = await openDialog(user)
    expect(within(dialog).getByRole('combobox', { name: 'Responsável' })).toHaveTextContent('Noivo')
    await user.type(within(dialog).getByLabelText('Título (obrigatório)'), 'Avulsa Exemplo Nova')
    await user.click(within(dialog).getByRole('button', { name: 'Criar avulsa' }))
    await waitFor(() => expect(api.callsTo(POST_TASK)).toHaveLength(1))
    expect(api.callsTo(POST_TASK)[0]?.body).toMatchObject({ responsible: 'Noivo' })
  })

  it('título vazio é bloqueado, com o aviso junto do campo', async () => {
    const { user, api } = setup()
    const dialog = await openDialog(user)
    await user.click(within(dialog).getByRole('button', { name: 'Criar avulsa' }))
    expect(await within(dialog).findByText('Informem o título da avulsa.')).toBeVisible()
    expect(api.callsTo(POST_TASK)).toHaveLength(0)
  })

  it('envia sempre o responsável escolhido, o prazo e a nota, e abre o painel da avulsa criada', async () => {
    const { user, api, probe } = setup('Noiva')
    const dialog = await openDialog(user)
    await user.type(within(dialog).getByLabelText('Título (obrigatório)'), '  Avulsa Exemplo Nova ')
    await user.click(within(dialog).getByRole('combobox', { name: 'Responsável' }))
    await user.click(screen.getByRole('option', { name: 'Ambos' }))
    await user.type(within(dialog).getByLabelText('Prazo'), '2027-05-01')
    await user.type(within(dialog).getByLabelText('Nota'), 'Nota de exemplo.')
    await user.click(within(dialog).getByRole('button', { name: 'Criar avulsa' }))

    const panel = await screen.findByRole('dialog', { name: 'Avulsa Exemplo Nova' })
    expect(api.callsTo(POST_TASK)[0]?.body).toEqual({
      title: 'Avulsa Exemplo Nova',
      responsible: 'Ambos',
      note: 'Nota de exemplo.',
      target_date: '2027-05-01',
    })
    expect(probe.current).toEqual({ avulsa: ID.avulsaNova })
    await waitFor(() => expect(panel.contains(document.activeElement)).toBe(true))
  })

  it('sem exatamente um id novo, não abre painel e só anuncia que a avulsa foi criada', async () => {
    const { user } = setup('Noiva', (store) => ({
      [POST_TASK]: () => {
        store.state.schedule = scheduleWithTasks([
          NEW,
          task({ id: ID.avulsaDois, title: 'Avulsa Exemplo de Outra Tela' }),
        ])
        return jsonResponse(201, store.state.schedule)
      },
    }))
    const dialog = await openDialog(user)
    await user.type(within(dialog).getByLabelText('Título (obrigatório)'), 'Avulsa Exemplo Nova')
    await user.click(within(dialog).getByRole('button', { name: 'Criar avulsa' }))

    const notice = await screen.findByText('Avulsa criada.')
    // Um aviso visível (o toast), e não só uma região para o leitor de tela.
    expect(notice.closest('.sr-only')).toBeNull()
    expect(notice).toBeVisible()
    expect(screen.queryByRole('dialog')).toBeNull()
  })

  it('cancelar e Esc devolvem o foco ao botão de origem', async () => {
    const { user } = setup()
    const origin = await headerButton()
    await user.click(origin)
    await user.click(
      within(await screen.findByRole('dialog', { name: 'Nova avulsa' })).getByRole('button', {
        name: 'Cancelar',
      }),
    )
    await waitFor(() => expect(origin).toHaveFocus())

    await user.click(origin)
    await screen.findByRole('dialog', { name: 'Nova avulsa' })
    await user.keyboard('{Escape}')
    await waitFor(() => expect(origin).toHaveFocus())
  })

  it('um 422 de título vazio vira o aviso do campo', async () => {
    const { user } = setup('Noiva', () => ({
      [POST_TASK]: problemResponse(422, 'task_title_required', { detail: 'Informem o título.' }),
    }))
    const dialog = await openDialog(user)
    await user.type(within(dialog).getByLabelText('Título (obrigatório)'), 'x')
    await user.click(within(dialog).getByRole('button', { name: 'Criar avulsa' }))
    expect(await within(dialog).findByText('Informem o título.')).toBeVisible()
  })

  it('no estado vazio da seção, o botão "Nova avulsa" abre o mesmo diálogo e devolve o foco a ele', async () => {
    const { user } = setup()
    const section = await screen.findByRole('region', { name: 'Avulsas' })
    const origin = within(section).getByRole('button', { name: 'Nova avulsa' })
    await user.click(origin)
    const dialog = await screen.findByRole('dialog', { name: 'Nova avulsa' })
    await user.click(within(dialog).getByRole('button', { name: 'Cancelar' }))
    await waitFor(() => expect(origin).toHaveFocus())
  })
})
