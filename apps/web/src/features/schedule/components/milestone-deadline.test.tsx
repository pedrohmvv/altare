import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse } from '@/test/fake-api'
import { GET_SCHEDULE, renderSchedule, stubWideScreen } from '@/test/render-schedule'
import { ID, milestone, SCHEDULE, scheduleComData, scheduleWith } from '@/test/schedule-fixtures'

const row = (name: string) =>
  screen.getByRole('button', { name }).closest('tr') as HTMLTableRowElement
const card = (name: string) => screen.getByRole('heading', { name }).closest('li') as HTMLElement

async function wideComData() {
  stubWideScreen()
  const view = renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
  await screen.findByRole('table')
  return view
}

describe('prazo e janela na tabela, no Modo Com Data (F-CRN-05)', () => {
  it('mostra o prazo efetivo, a contagem e a janela calculada com o rótulo de sugestão genérica', async () => {
    await wideComData()
    const linha = within(row('Marco Exemplo com Janela Sugerida'))

    expect(linha.getByText('12/08/2026')).toBeVisible()
    expect(linha.getByText('faltam 12 dias')).toBeVisible()
    expect(linha.getByText('Janela: 12/04/2026 a 12/08/2026')).toBeVisible()
    expect(linha.getByText('sugestão genérica')).toBeVisible()
  })

  it('a data exata do prazo vai no title da contagem, que continua sendo texto visível', async () => {
    await wideComData()
    const contagem = within(row('Marco Exemplo com Janela Sugerida')).getByText('faltam 12 dias')

    expect(contagem).toHaveAttribute('title', '12/08/2026')
  })

  it('o separador entre as etiquetas é só visual, escondido do leitor de tela', async () => {
    await wideComData()
    const linha = row('Marco Exemplo com Prazo Manual')

    const separadores = Array.from(linha.querySelectorAll('[aria-hidden="true"]')).filter(
      (item) => item.textContent === ' · ',
    )
    // Duas etiquetas (sugestão e prazo de vocês), cada uma depois do seu separador.
    expect(separadores).toHaveLength(2)
  })

  it('uma janela editada pelo casal deixa de ser sugestão genérica', async () => {
    await wideComData()
    const linha = within(row('Marco Exemplo com Janela Editada'))

    expect(linha.getByText('15/05/2027')).toBeVisible()
    expect(linha.getByText('falta 1 dia')).toBeVisible()
    expect(linha.getByText('Janela: 17/04/2027 a 15/05/2027')).toBeVisible()
    expect(linha.queryByText('sugestão genérica')).not.toBeInTheDocument()
  })

  it('com prazo manual, o efetivo é o manual e a linha da janela diz que o prazo foi de vocês', async () => {
    await wideComData()
    const linha = within(row('Marco Exemplo com Prazo Manual'))

    expect(linha.getByText('30/07/2026')).toBeVisible()
    expect(linha.queryByText('12/08/2026')).not.toBeInTheDocument()
    expect(linha.getByText('é hoje')).toBeVisible()
    expect(linha.getByText('Janela: 12/04/2026 a 12/08/2026')).toBeVisible()
    expect(linha.getByText('prazo definido por vocês')).toBeVisible()
  })

  it('o atrasado diz há quantos dias venceu e continua com o selo Atrasado', async () => {
    await wideComData()
    const linha = within(row('Marco Exemplo Atrasado com Janela'))

    expect(linha.getByText('venceu há 3 dias')).toBeVisible()
    expect(linha.getByText('Atrasado')).toBeVisible()
  })

  it('sem janela e sem prazo diz "Sem prazo", sem contagem nem linha de janela', async () => {
    await wideComData()
    const linha = within(row('Marco Exemplo sem Janela'))

    expect(linha.getByText('Sem prazo')).toBeVisible()
    expect(linha.queryByText(/Janela:/)).not.toBeInTheDocument()
    expect(linha.queryByText(/faltam|falta|venceu|é hoje/)).not.toBeInTheDocument()
  })

  it('o concluído mostra o prazo, mas não tem contagem (days_left nulo)', async () => {
    await wideComData()
    const linha = within(row('Marco Exemplo Concluído com Janela'))

    expect(linha.getByText('12/08/2026')).toBeVisible()
    expect(linha.queryByText(/faltam|falta|venceu|é hoje/)).not.toBeInTheDocument()
  })
})

describe('prazo e janela nos cartões do celular (F-CRN-05)', () => {
  it('usa a data da lista (12 ago 2026), a contagem, a janela e o rótulo', async () => {
    renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    await screen.findByRole('heading', { name: 'Marco Exemplo com Janela Sugerida' })
    const cartao = within(card('Marco Exemplo com Janela Sugerida'))

    expect(cartao.getByText('12 ago 2026')).toBeVisible()
    expect(cartao.getByText('faltam 12 dias')).toHaveAttribute('title', '12 ago 2026')
    expect(cartao.getByText('Janela: 12 abr 2026 a 12 ago 2026')).toBeVisible()
    expect(cartao.getByText('sugestão genérica')).toBeVisible()
  })

  it('o prazo vem rotulado para o leitor de tela e o sem prazo diz "Sem prazo"', async () => {
    renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, scheduleComData()) })
    await screen.findByRole('heading', { name: 'Marco Exemplo sem Janela' })

    expect(within(card('Marco Exemplo sem Janela')).getByText('Sem prazo')).toBeVisible()
    expect(
      within(card('Marco Exemplo com Janela Editada')).getByText('Prazo-alvo:', { exact: false }),
    ).toBeInTheDocument()
  })
})

describe('Modo Sem Data (F-CRN-05)', () => {
  const semData = () => {
    // A API não calcula janela sem data exata: os deslocamentos existem, as datas não.
    const base = scheduleWith(ID.destravado, {
      window: { start_before: 14, end_before: 10, unit: 'meses', is_suggestion: true },
      days_left: 12,
    })
    return base
  }

  it('nenhum marco mostra janela calculada, mas o prazo manual continua com a contagem', async () => {
    renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, semData()) })
    await screen.findByRole('heading', { name: 'Marco Exemplo Destravado' })
    const cartao = within(card('Marco Exemplo Destravado'))

    expect(screen.queryByText(/Janela:/)).not.toBeInTheDocument()
    expect(cartao.getByText('15 mar 2027')).toBeVisible()
    expect(cartao.getByText('faltam 12 dias')).toBeVisible()
  })

  it('o marco sem prazo manual e sem janela calculada diz "Sem prazo"', async () => {
    renderSchedule({
      [GET_SCHEDULE]: jsonResponse(200, {
        ...SCHEDULE,
        phases: [
          {
            ...SCHEDULE.phases[0],
            milestones: [milestone({ id: ID.novo, title: 'Marco Exemplo' })],
          },
        ],
      }),
    })
    await screen.findByRole('heading', { name: 'Marco Exemplo' })

    expect(within(card('Marco Exemplo')).getByText('Sem prazo')).toBeVisible()
  })
})
