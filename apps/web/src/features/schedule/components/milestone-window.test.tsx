import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import {
  GET_SCHEDULE,
  PUT_MILESTONE,
  PUT_STATE,
  PUT_WINDOW,
  renderSchedule,
} from '@/test/render-schedule'
import { ID, SCHEDULE, scheduleComData, scheduleWith } from '@/test/schedule-fixtures'
import { activeAlert, memory, openMilestone } from '@/test/schedule-helpers'

const SUGERIDA = 'Marco Exemplo com Janela Sugerida'
const SEM_JANELA = 'Marco Exemplo sem Janela'

/** O que a API devolveria depois de o casal editar a janela do marco "sugerido" para 12 a 8 meses. */
const EDITED = {
  window: { start_before: 12, end_before: 8, unit: 'meses', is_suggestion: false },
  window_start: '2026-06-12',
  window_end: '2026-10-12',
  effective_target: '2026-10-12',
  days_left: 61,
  version: 2,
} as const

const section = (dialog: HTMLElement) =>
  within(dialog).getByRole('region', { name: 'Janela' }) as HTMLElement

const start = (dialog: HTMLElement) => within(section(dialog)).getByLabelText('Início')
const end = (dialog: HTMLElement) => within(section(dialog)).getByLabelText('Fim')

async function fill(
  user: ReturnType<typeof renderSchedule>['user'],
  field: HTMLElement,
  value: string,
) {
  await user.clear(field)
  await user.type(field, value)
}

describe('a seção "Janela" do painel, no Modo Com Data (F-CRN-05)', () => {
  it('diz a janela em palavras, mostra as datas calculadas e que é sugestão genérica', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SUGERIDA)
    const janela = within(section(dialog))

    expect(janela.getByText('de 14 a 10 meses antes da data')).toBeVisible()
    expect(janela.getByText('Datas calculadas: 12/04/2026 a 12/08/2026')).toBeVisible()
    expect(janela.getByText('Sugestão genérica: ainda ninguém editou esta janela.')).toBeVisible()
  })

  it('a janela editada em semanas não é sugestão e o editor abre com os valores dela', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, 'Marco Exemplo com Janela Editada')
    const janela = within(section(dialog))

    expect(janela.getByText('de 8 a 4 semanas antes da data')).toBeVisible()
    expect(janela.queryByText(/Sugestão genérica/)).not.toBeInTheDocument()
    expect(start(dialog)).toHaveValue('8')
    expect(end(dialog)).toHaveValue('4')
    expect(janela.getByRole('combobox', { name: 'Unidade' })).toHaveTextContent('semanas')
  })

  it('o painel mostra o prazo em vigor e a contagem', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SUGERIDA)

    expect(within(dialog).getByText('12/08/2026')).toBeVisible()
    expect(within(dialog).getByText('faltam 12 dias')).toHaveAttribute('title', '12/08/2026')
  })

  it('"Salvar janela" fica desligado enquanto nada mudou, com o motivo em texto', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SUGERIDA)
    const salvar = within(section(dialog)).getByRole('button', { name: 'Salvar janela' })

    expect(salvar).toBeDisabled()
    expect(
      within(section(dialog)).getByText('Mudem o início, o fim ou a unidade para salvar.'),
    ).toBeVisible()

    await fill(user, start(dialog), '12')
    expect(salvar).toBeEnabled()

    await fill(user, start(dialog), '14')
    expect(salvar).toBeDisabled()
  })

  it('envia os deslocamentos e a versão do marco, e o sucesso aparece no painel, sem toast', async () => {
    const mem = memory(scheduleComData())
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_WINDOW(ID.janelaSugerida)]: mem.write(ID.janelaSugerida, () => EDITED),
    })
    const dialog = await openMilestone(user, SUGERIDA)

    await fill(user, start(dialog), '12')
    await fill(user, end(dialog), '8')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    await waitFor(() => expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))).toHaveLength(1))
    expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))[0]?.body).toEqual({
      start_before: 12,
      end_before: 8,
      unit: 'meses',
      version: 1,
    })
    const janela = within(section(dialog))
    expect(await janela.findByText('Janela salva.')).toBeVisible()
    expect(janela.getByText('de 12 a 8 meses antes da data')).toBeVisible()
    expect(janela.getByText('Datas calculadas: 12/06/2026 a 12/10/2026')).toBeVisible()
    // A janela do casal deixa de ser sugestão genérica, e o prazo em vigor acompanha o fim dela.
    expect(janela.queryByText(/Sugestão genérica/)).not.toBeInTheDocument()
    expect(within(dialog).getByText('12/10/2026')).toBeVisible()
    // O cronograma devolvido vai direto para o cache: nenhuma segunda leitura.
    expect(api.callsTo(GET_SCHEDULE)).toHaveLength(1)
    expect(screen.queryByRole('region', { name: /notificações/i })).not.toBeInTheDocument()
  })

  it('depois de salvar, o foco vai ao título da seção e o botão volta a ficar desligado', async () => {
    const mem = memory(scheduleComData())
    const { user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_WINDOW(ID.janelaSugerida)]: mem.write(ID.janelaSugerida, () => EDITED),
    })
    const dialog = await openMilestone(user, SUGERIDA)

    await fill(user, start(dialog), '12')
    await fill(user, end(dialog), '8')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    await within(section(dialog)).findByText('Janela salva.')
    expect(within(section(dialog)).getByRole('heading', { name: 'Janela' })).toHaveFocus()
    expect(within(section(dialog)).getByRole('button', { name: 'Salvar janela' })).toBeDisabled()
  })

  it('trocar a unidade para semanas vai no corpo', async () => {
    const mem = memory(scheduleComData())
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_WINDOW(ID.janelaSugerida)]: mem.write(ID.janelaSugerida, () => EDITED),
    })
    const dialog = await openMilestone(user, SUGERIDA)

    await user.click(within(section(dialog)).getByRole('combobox', { name: 'Unidade' }))
    await user.click(screen.getByRole('option', { name: 'semanas' }))
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    await waitFor(() => expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))).toHaveLength(1))
    expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))[0]?.body).toMatchObject({
      start_before: 14,
      end_before: 10,
      unit: 'semanas',
    })
  })
})

describe('validar a janela antes de enviar (F-CRN-05)', () => {
  it('o início menor que o fim é recusado ao lado do campo, sem chamar a API', async () => {
    const { api, user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SUGERIDA)

    await fill(user, start(dialog), '3')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    expect(
      await within(section(dialog)).findByText(
        'O início precisa ser maior ou igual ao fim (a janela começa antes de terminar).',
      ),
    ).toBeVisible()
    expect(start(dialog)).toHaveAttribute('aria-invalid', 'true')
    expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))).toHaveLength(0)
  })

  it('decimal e acima do teto são recusados, e o foco vai ao primeiro campo inválido', async () => {
    const { api, user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SUGERIDA)

    await fill(user, start(dialog), '121')
    await fill(user, end(dialog), '1,5')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    expect(await within(section(dialog)).findByText('Usem no máximo 120 meses.')).toBeVisible()
    expect(
      within(section(dialog)).getByText('Informem um número inteiro de 0 a 120.'),
    ).toBeVisible()
    await waitFor(() => expect(start(dialog)).toHaveFocus())
    expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))).toHaveLength(0)
  })

  it('o 422 do servidor (invalid_window) vai para a região de erro, e o formulário continua', async () => {
    const { user } = renderSchedule({
      [GET_SCHEDULE]: jsonResponse(200, scheduleComData()),
      [PUT_WINDOW(ID.janelaSugerida)]: problemResponse(422, 'invalid_window', {
        detail: 'A janela não cabe antes da data do casamento.',
      }),
    })
    const dialog = await openMilestone(user, SUGERIDA)

    await fill(user, start(dialog), '12')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    const alerta = await activeAlert(section(dialog))
    expect(within(alerta).getByText('A janela não cabe antes da data do casamento.')).toBeVisible()
    expect(start(dialog)).toHaveValue('12')
  })

  it('uma falha de rede avisa e mantém o que foi digitado', async () => {
    const { user } = renderSchedule({
      [GET_SCHEDULE]: jsonResponse(200, scheduleComData()),
      [PUT_WINDOW(ID.janelaSugerida)]: () => {
        throw new TypeError('Failed to fetch')
      },
    })
    const dialog = await openMilestone(user, SUGERIDA)

    await fill(user, start(dialog), '12')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    expect(
      await within(section(dialog)).findByText(/Não conseguimos salvar a janela agora/),
    ).toBeVisible()
    expect(start(dialog)).toHaveValue('12')
  })
})

describe('conflito de versão na janela (F-CRN-05, D-082)', () => {
  it('avisa, não sobrescreve e oferece a versão mais recente', async () => {
    let lidas = 0
    const newer = scheduleWith(
      ID.janelaSugerida,
      {
        window: { start_before: 9, end_before: 6, unit: 'meses', is_suggestion: false },
        window_start: '2026-09-12',
        window_end: '2026-12-12',
        version: 5,
      },
      scheduleComData(),
    )
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: () => {
        lidas += 1
        return jsonResponse(200, lidas === 1 ? scheduleComData() : newer)
      },
      [PUT_WINDOW(ID.janelaSugerida)]: problemResponse(409, 'version_conflict'),
    })
    const dialog = await openMilestone(user, SUGERIDA)

    await fill(user, start(dialog), '12')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    const alerta = await activeAlert(section(dialog))
    expect(within(alerta).getByText(/alterado em outra tela/)).toBeVisible()
    await user.click(within(alerta).getByRole('button', { name: 'Ver a versão mais recente' }))

    await waitFor(() => expect(start(dialog)).toHaveValue('9'))
    expect(end(dialog)).toHaveValue('6')
    expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))).toHaveLength(1)
    for (const region of within(section(dialog)).getAllByRole('alert')) {
      expect(region).toBeEmptyDOMElement()
    }
  })
})

describe('a versão do marco entre o formulário e o editor de janela (D-082)', () => {
  it('salvar a janela sobe a versão, e o formulário (conteúdo intacto) envia a nova', async () => {
    const mem = memory(scheduleComData())
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_WINDOW(ID.janelaSugerida)]: mem.write(ID.janelaSugerida, () => EDITED),
      [PUT_MILESTONE(ID.janelaSugerida)]: mem.write(ID.janelaSugerida, () => ({ version: 3 })),
    })
    const dialog = await openMilestone(user, SUGERIDA)

    await fill(user, start(dialog), '12')
    await fill(user, end(dialog), '8')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))
    await within(section(dialog)).findByText('Janela salva.')
    await user.type(within(dialog).getByLabelText('Nota'), 'Uma nota.')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.callsTo(PUT_MILESTONE(ID.janelaSugerida))).toHaveLength(1))
    expect(api.callsTo(PUT_MILESTONE(ID.janelaSugerida))[0]?.body).toMatchObject({ version: 2 })
  })

  it('salvar o formulário sobe a versão, e o editor (janela intacta) envia a nova', async () => {
    const mem = memory(scheduleComData())
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_MILESTONE(ID.janelaSugerida)]: mem.write(ID.janelaSugerida, () => ({
        note: 'Uma nota.',
        version: 2,
      })),
      [PUT_WINDOW(ID.janelaSugerida)]: mem.write(ID.janelaSugerida, () => ({
        ...EDITED,
        version: 3,
      })),
    })
    const dialog = await openMilestone(user, SUGERIDA)

    await fill(user, start(dialog), '12')
    await user.type(within(dialog).getByLabelText('Nota'), 'Uma nota.')
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))
    await within(dialog).findByText('Alterações salvas.')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    await waitFor(() => expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))).toHaveLength(1))
    expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))[0]?.body).toMatchObject({
      start_before: 12,
      version: 2,
    })
  })

  it('o estado do marco sobe a versão e o editor continua com o rascunho e a versão viva', async () => {
    const mem = memory(scheduleComData())
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_STATE(ID.janelaSugerida)]: mem.write(ID.janelaSugerida, () => ({
        state: 'Em andamento',
        version: 2,
      })),
      [PUT_WINDOW(ID.janelaSugerida)]: mem.write(ID.janelaSugerida, () => ({
        ...EDITED,
        version: 3,
      })),
    })
    const dialog = await openMilestone(user, SUGERIDA)

    await fill(user, start(dialog), '12')
    await user.click(within(dialog).getByRole('button', { name: 'Marcar em andamento' }))
    await within(dialog).findByText('Marco marcado em andamento.')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    await waitFor(() => expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))).toHaveLength(1))
    expect(api.callsTo(PUT_WINDOW(ID.janelaSugerida))[0]?.body).toMatchObject({ version: 2 })
  })
})

describe('o prazo no painel e as dicas ligadas aos campos (F-CRN-05)', () => {
  it('o prazo em vigor sai em mono, como na tabela e no cartão (data como dado)', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SUGERIDA)

    expect(within(dialog).getByText('12/08/2026')).toHaveClass('text-num')
  })

  it('com prazo manual e janela, o painel diz ao lado do prazo que ele é de vocês', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, 'Marco Exemplo com Prazo Manual')

    expect(within(dialog).getByText('30/07/2026')).toBeVisible()
    expect(within(dialog).getByText('prazo definido por vocês')).toBeVisible()
  })

  it('sem prazo manual, ou sem janela, a etiqueta não aparece', async () => {
    const comPrazoSemJanela = scheduleWith(
      ID.semJanela,
      { target_date: '2026-09-01', effective_target: '2026-09-01', days_left: 30 },
      scheduleComData(),
    )
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, comPrazoSemJanela) })
    const sugerida = await openMilestone(user, SUGERIDA)
    expect(within(sugerida).queryByText('prazo definido por vocês')).not.toBeInTheDocument()
    await user.keyboard('{Escape}')

    const semJanela = await openMilestone(user, SEM_JANELA)
    expect(within(semJanela).queryByText('prazo definido por vocês')).not.toBeInTheDocument()
  })

  it('Início e Fim dizem a unidade ao leitor de tela, e a dica acompanha a unidade', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SUGERIDA)

    expect(start(dialog)).toHaveAccessibleDescription('Quantos meses antes da data do casamento.')
    expect(end(dialog)).toHaveAccessibleDescription('Quantos meses antes da data do casamento.')

    await user.click(within(section(dialog)).getByRole('combobox', { name: 'Unidade' }))
    await user.click(screen.getByRole('option', { name: 'semanas' }))
    expect(start(dialog)).toHaveAccessibleDescription('Quantas semanas antes da data do casamento.')
  })

  it('o editor vazio de "Definir janela" também tem a dica nos dois campos', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SEM_JANELA)

    await user.click(within(section(dialog)).getByRole('button', { name: 'Definir janela' }))

    expect(start(dialog)).toHaveAccessibleDescription('Quantos meses antes da data do casamento.')
    expect(end(dialog)).toHaveAccessibleDescription('Quantos meses antes da data do casamento.')

    await user.click(within(section(dialog)).getByRole('combobox', { name: 'Unidade' }))
    await user.click(screen.getByRole('option', { name: 'semanas' }))

    // Os campos vazios já foram tocados e levam também o erro; a dica vem por último.
    expect(start(dialog)).toHaveAccessibleDescription(
      /Quantas semanas antes da data do casamento\.$/,
    )
    expect(end(dialog)).toHaveAccessibleDescription(/Quantas semanas antes da data do casamento\.$/)
  })
})

describe('marco sem janela (F-CRN-05)', () => {
  it('diz que não tem janela e oferece "Definir janela"', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SEM_JANELA)

    expect(within(section(dialog)).getByText('Este marco ainda não tem janela.')).toBeVisible()
    expect(within(section(dialog)).queryByLabelText('Início')).not.toBeInTheDocument()
    expect(within(section(dialog)).getByRole('button', { name: 'Definir janela' })).toBeVisible()
  })

  it('"Definir janela" abre o editor vazio com o foco no início, e Cancelar devolve o foco', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SEM_JANELA)

    await user.click(within(section(dialog)).getByRole('button', { name: 'Definir janela' }))

    expect(start(dialog)).toHaveValue('')
    expect(end(dialog)).toHaveValue('')
    expect(within(section(dialog)).getByRole('combobox', { name: 'Unidade' })).toHaveTextContent(
      'meses',
    )
    await waitFor(() => expect(start(dialog)).toHaveFocus())

    await user.click(within(section(dialog)).getByRole('button', { name: 'Cancelar' }))
    expect(within(section(dialog)).queryByLabelText('Início')).not.toBeInTheDocument()
    expect(within(section(dialog)).getByRole('button', { name: 'Definir janela' })).toHaveFocus()
  })

  it('cria a janela do marco, que deixa de estar sem janela e nunca é sugestão', async () => {
    const mem = memory(scheduleComData())
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_WINDOW(ID.semJanela)]: mem.write(ID.semJanela, () => ({
        window: { start_before: 6, end_before: 3, unit: 'meses', is_suggestion: false },
        window_start: '2026-12-12',
        window_end: '2027-03-12',
        effective_target: '2027-03-12',
        days_left: 130,
        version: 2,
      })),
    })
    const dialog = await openMilestone(user, SEM_JANELA)

    await user.click(within(section(dialog)).getByRole('button', { name: 'Definir janela' }))
    await user.type(start(dialog), '6')
    await user.type(end(dialog), '3')
    await user.click(within(section(dialog)).getByRole('button', { name: 'Salvar janela' }))

    await waitFor(() => expect(api.callsTo(PUT_WINDOW(ID.semJanela))).toHaveLength(1))
    expect(api.callsTo(PUT_WINDOW(ID.semJanela))[0]?.body).toEqual({
      start_before: 6,
      end_before: 3,
      unit: 'meses',
      version: 1,
    })
    const janela = within(section(dialog))
    expect(await janela.findByText('de 6 a 3 meses antes da data')).toBeVisible()
    expect(janela.getByText('Janela salva.')).toBeVisible()
    expect(janela.queryByText(/Sugestão genérica/)).not.toBeInTheDocument()
    expect(janela.queryByRole('button', { name: 'Definir janela' })).not.toBeInTheDocument()
  })
})

describe('a seção "Janela" no Modo Sem Data (F-CRN-05)', () => {
  const withOffsets = () =>
    scheduleWith(ID.destravado, {
      window: { start_before: 14, end_before: 10, unit: 'meses', is_suggestion: true },
    })

  it('diz que a janela aparece com a data exata e não oferece editor', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, withOffsets()) })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')
    const janela = within(section(dialog))

    expect(
      janela.getByText(
        'Janela de 14 a 10 meses antes da data. As datas aparecem quando vocês definirem a data exata do casamento.',
      ),
    ).toBeVisible()
    expect(janela.queryByLabelText('Início')).not.toBeInTheDocument()
    expect(janela.queryByRole('button', { name: /janela/i })).not.toBeInTheDocument()
  })

  it('sem janela, diz com calma que dá para criar uma depois da data exata', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, SCHEDULE) })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    expect(
      within(section(dialog)).getByText(
        'Este marco ainda não tem janela. Com a data exata definida, vocês podem criar uma.',
      ),
    ).toBeVisible()
    expect(
      within(section(dialog)).queryByRole('button', { name: 'Definir janela' }),
    ).not.toBeInTheDocument()
  })
})

describe('"Voltar à sugestão" ao lado do prazo-alvo (F-CRN-05, regra 2)', () => {
  const MANUAL = 'Marco Exemplo com Prazo Manual'

  it('com prazo manual, janela e data exata, limpa o campo e mostra a sugestão', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, MANUAL)
    const prazo = within(dialog).getByLabelText('Prazo-alvo')
    expect(prazo).toHaveValue('2026-07-30')

    await user.click(within(dialog).getByRole('button', { name: 'Voltar à sugestão' }))

    expect(prazo).toHaveValue('')
    expect(within(dialog).getByText('Sugestão: 12/08/2026')).toBeVisible()
    expect(within(dialog).queryByRole('button', { name: 'Voltar à sugestão' })).toBeNull()
    expect(prazo).toHaveFocus()
  })

  it('salvar depois grava o prazo manual como nulo, com a versão do marco', async () => {
    const mem = memory(scheduleComData())
    const { api, user } = renderSchedule({
      [GET_SCHEDULE]: mem.get,
      [PUT_MILESTONE(ID.prazoManual)]: mem.write(ID.prazoManual, () => ({
        target_date: null,
        effective_target: '2026-08-12',
        days_left: 12,
        version: 2,
      })),
    })
    const dialog = await openMilestone(user, MANUAL)

    await user.click(within(dialog).getByRole('button', { name: 'Voltar à sugestão' }))
    await user.click(within(dialog).getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.callsTo(PUT_MILESTONE(ID.prazoManual))).toHaveLength(1))
    expect(api.callsTo(PUT_MILESTONE(ID.prazoManual))[0]?.body).toMatchObject({
      target_date: null,
      version: 1,
    })
    expect(await within(dialog).findByText('12/08/2026')).toBeVisible()
  })

  it('o campo tem a sugestão como descrição e a dica de que em branco vale a sugestão', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SUGERIDA)

    expect(within(dialog).getByLabelText('Prazo-alvo')).toHaveAccessibleDescription(
      'Em branco, vale a sugestão. Sugestão: 12/08/2026',
    )
  })

  it('com prazo manual, a dica é a de sempre e a sugestão ainda não é descrição', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, MANUAL)

    expect(within(dialog).getByLabelText('Prazo-alvo')).toHaveAccessibleDescription(
      'Só a data. Podem deixar em branco.',
    )
  })

  it('"Tirar o prazo", sem sugestão, também leva o foco ao campo', async () => {
    const comPrazo = scheduleWith(
      ID.semJanela,
      { target_date: '2026-09-01', effective_target: '2026-09-01', days_left: 30 },
      scheduleComData(),
    )
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, comPrazo) })
    const dialog = await openMilestone(user, SEM_JANELA)

    await user.click(within(dialog).getByRole('button', { name: 'Tirar o prazo' }))

    expect(within(dialog).getByLabelText('Prazo-alvo')).toHaveFocus()
  })

  it('sem prazo manual, não há o botão, mas a sugestão aparece perto do campo', async () => {
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    const dialog = await openMilestone(user, SUGERIDA)

    expect(within(dialog).getByLabelText('Prazo-alvo')).toHaveValue('')
    expect(within(dialog).getByText('Sugestão: 12/08/2026')).toBeVisible()
    expect(within(dialog).queryByRole('button', { name: 'Voltar à sugestão' })).toBeNull()
  })

  it('sem janela, o prazo manual só pode ser tirado, não há sugestão', async () => {
    const comPrazo = scheduleWith(
      ID.semJanela,
      { target_date: '2026-09-01', effective_target: '2026-09-01', days_left: 30 },
      scheduleComData(),
    )
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, comPrazo) })
    const dialog = await openMilestone(user, SEM_JANELA)

    expect(within(dialog).queryByRole('button', { name: 'Voltar à sugestão' })).toBeNull()
    expect(within(dialog).getByRole('button', { name: 'Tirar o prazo' })).toBeVisible()
    expect(within(dialog).queryByText(/^Sugestão:/)).not.toBeInTheDocument()
  })

  it('no Modo Sem Data, o prazo manual só pode ser tirado, mesmo com os deslocamentos da janela', async () => {
    const semData = scheduleWith(ID.destravado, {
      window: { start_before: 14, end_before: 10, unit: 'meses', is_suggestion: true },
    })
    const { user } = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, semData) })
    const dialog = await openMilestone(user, 'Marco Exemplo Destravado')

    expect(within(dialog).queryByRole('button', { name: 'Voltar à sugestão' })).toBeNull()
    expect(within(dialog).getByRole('button', { name: 'Tirar o prazo' })).toBeVisible()
    expect(within(dialog).queryByText(/^Sugestão:/)).not.toBeInTheDocument()
  })
})
