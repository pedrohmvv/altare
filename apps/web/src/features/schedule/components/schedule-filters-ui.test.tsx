import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse } from '@/test/fake-api'
import { GET_SCHEDULE, renderSchedule, stubWideScreen } from '@/test/render-schedule'
import { FID, scheduleForFilters } from '@/test/schedule-fixtures'
import type { ScheduleSearch } from '../search'

// F-CRN-09: filtros, lentes e contadores; D-080 (a lente filtra no navegador), D-074 (chips e URL).
const NOIVO_M = 'Marco Exemplo do Noivo'
const NOIVA_M = 'Marco Exemplo da Noiva'
const AMBOS_M = 'Marco Exemplo de Ambos Atrasado'
const NOIVO_T = 'Avulsa Exemplo do Noivo'
const NOIVA_T = 'Avulsa Exemplo da Noiva Atrasada'

function setup(
  search: ScheduleSearch = {},
  session: { profile?: 'Noivo' | 'Noiva'; lens?: 'casal' | 'minha' } = {},
) {
  const view = renderSchedule(
    { [GET_SCHEDULE]: jsonResponse(200, scheduleForFilters()) },
    search,
    session,
  )
  return view
}

const toolbar = async () =>
  within(await screen.findByRole('region', { name: 'Filtros do cronograma' }))
const card = (name: string) => screen.queryByRole('button', { name })

describe('a barra de filtros (F-CRN-09)', () => {
  it('tem os grupos Responsável e Estado em fieldset com legenda, e os dois chips de atalho', async () => {
    setup()
    const bar = await toolbar()
    expect(bar.getByRole('group', { name: 'Responsável' })).toBeVisible()
    expect(bar.getByRole('group', { name: 'Estado' })).toBeVisible()
    for (const name of [
      'Noivo',
      'Noiva',
      'Ambos',
      'Bloqueado',
      'Destravado',
      'A fazer',
      'Em andamento',
      'Concluído',
      'Só atrasados',
      'Só avulsas',
    ]) {
      expect(bar.getByRole('button', { name })).toHaveAttribute('aria-pressed', 'false')
    }
    expect(bar.queryByRole('searchbox')).toBeNull()
    expect(bar.queryByRole('button', { name: 'Limpar filtros' })).toBeNull()
  })

  it('o responsável filtra marcos e avulsas, diz "N de M itens" e tocar de novo tira o filtro', async () => {
    const { user, probe } = setup()
    const bar = await toolbar()
    await user.click(bar.getByRole('button', { name: 'Noivo' }))

    expect(probe.current).toEqual({ responsavel: 'noivo' })
    expect(bar.getByRole('button', { name: 'Noivo' })).toHaveAttribute('aria-pressed', 'true')
    expect(bar.getByRole('status')).toHaveTextContent('2 de 8 itens')
    expect(card(NOIVO_M)).toBeVisible()
    expect(card(NOIVO_T)).toBeVisible()
    expect(card(NOIVA_M)).toBeNull()
    expect(card(NOIVA_T)).toBeNull()

    await user.click(bar.getByRole('button', { name: 'Noivo' }))
    expect(probe.current).toEqual({})
    expect(bar.getByRole('status')).toBeEmptyDOMElement()
    expect(card(NOIVA_M)).toBeVisible()
  })

  it('"Só atrasados" inclui marcos e avulsas atrasados', async () => {
    const { user } = setup()
    const bar = await toolbar()
    await user.click(bar.getByRole('button', { name: 'Só atrasados' }))
    expect(bar.getByRole('status')).toHaveTextContent('2 de 8 itens')
    expect(card(AMBOS_M)).toBeVisible()
    expect(card(NOIVA_T)).toBeVisible()
    expect(card(NOIVO_M)).toBeNull()
  })

  it('"Só avulsas" esconde todas as fases', async () => {
    const { user } = setup()
    const bar = await toolbar()
    await user.click(bar.getByRole('button', { name: 'Só avulsas' }))
    expect(bar.getByRole('status')).toHaveTextContent('4 de 8 itens')
    expect(screen.queryByRole('region', { name: 'Fase Exemplo Um' })).toBeNull()
    expect(screen.queryByRole('region', { name: 'Fase Exemplo Dois' })).toBeNull()
    expect(screen.getByRole('region', { name: 'Avulsas' })).toBeVisible()
  })

  it('o estado "A fazer" mostra só avulsas e "Bloqueado" só marcos', async () => {
    const { user } = setup()
    const bar = await toolbar()
    await user.click(bar.getByRole('button', { name: 'A fazer' }))
    expect(bar.getByRole('status')).toHaveTextContent('2 de 8 itens')
    expect(card(NOIVO_T)).toBeVisible()
    expect(card(NOIVO_M)).toBeNull()

    // Cada grupo tem uma escolha só: o Bloqueado troca o A fazer.
    await user.click(bar.getByRole('button', { name: 'Bloqueado' }))
    expect(bar.getByRole('button', { name: 'A fazer' })).toHaveAttribute('aria-pressed', 'false')
    expect(bar.getByRole('status')).toHaveTextContent('1 de 8 itens')
    expect(card(NOIVA_M)).toBeVisible()
  })

  it('o progresso de cada fase e os bloqueios continuam os de todos os itens', async () => {
    const { user } = setup()
    const bar = await toolbar()
    await user.click(bar.getByRole('button', { name: 'Noiva' }))

    const phaseOne = screen.getByRole('region', { name: 'Fase Exemplo Um' })
    expect(within(phaseOne).getByText('0 de 3 concluídos')).toBeVisible()
    expect(within(phaseOne).queryByText(NOIVO_M)).toBeNull()
    // O Noivo some da lista, e o que ele bloqueia continua dito pelo servidor.
    expect(within(phaseOne).getByText(`Aguardando: ${NOIVO_M}`)).toBeVisible()
    const phaseTwo = screen.getByRole('region', { name: 'Fase Exemplo Dois' })
    expect(within(phaseTwo).getByText('1 de 1 concluído')).toBeVisible()
  })

  it('a fase sem item visível some, e a que fica mantém o número do cronograma inteiro', async () => {
    stubWideScreen()
    setup({ responsavel: 'noiva', estado: 'concluido' })
    const table = await screen.findByRole('table')
    // Só o marco Concluído da Noiva casa: a Fase 2 fica, a Fase 1 e o grupo Avulsas somem.
    const headers = within(table).getAllByRole('rowheader')
    expect(headers).toHaveLength(1)
    expect(headers[0]).toHaveTextContent('Fase 2')
    expect(headers[0]).toHaveTextContent('Fase Exemplo Dois')
    expect(headers[0]).toHaveTextContent('1 de 1 concluído')
  })

  it('a seção Avulsas respeita o filtro e some se nenhuma avulsa casa', async () => {
    setup({ estado: 'bloqueado' })
    await toolbar()
    expect(screen.queryByRole('region', { name: 'Avulsas' })).toBeNull()
    expect(card(NOIVA_M)).toBeVisible()
  })

  it('sem resultado, diz com calma e oferece limpar os filtros', async () => {
    const { user, probe } = setup({ responsavel: 'noivo', estado: 'concluido' })
    expect(await screen.findByText('Nenhum item com esses filtros.')).toBeVisible()
    const clear = screen.getAllByRole('button', { name: 'Limpar filtros' })
    expect(clear.length).toBeGreaterThan(0)
    await user.click(clear.at(-1) as HTMLElement)
    expect(probe.current).toEqual({})
    expect(await screen.findByRole('region', { name: 'Fase Exemplo Um' })).toBeVisible()
  })

  it('"Limpar filtros" limpa só os filtros e mantém o painel aberto', async () => {
    const { probe } = setup({ avulsa: FID.tNoivo, estado: 'a-fazer', atrasados: true })
    await screen.findByRole('dialog', { name: NOIVO_T })
    // O painel é modal e esconde a página; o clique vai direto ao botão.
    fireEvent.click(screen.getByRole('button', { name: 'Limpar filtros', hidden: true }))
    expect(probe.current).toEqual({ avulsa: FID.tNoivo })
    expect(screen.getByRole('dialog', { name: NOIVO_T })).toBeVisible()
  })

  it('o painel abre pela URL mesmo com o item escondido pelo filtro', async () => {
    setup({ marco: FID.mNoivo, responsavel: 'noiva' })
    expect(await screen.findByRole('dialog', { name: NOIVO_M })).toBeVisible()
    expect(card(NOIVO_M)).toBeNull()
  })
})

describe('a lente Minha visão (D-080, resposta 1)', () => {
  it('como Noiva, mostra os dela e os de Ambos e não os do Noivo, com a nota em texto', async () => {
    setup({}, { profile: 'Noiva', lens: 'minha' })
    const bar = await toolbar()
    expect(card(NOIVA_M)).toBeVisible()
    expect(card(AMBOS_M)).toBeVisible()
    expect(card(NOIVO_M)).toBeNull()
    expect(card(NOIVO_T)).toBeNull()
    expect(bar.getByRole('status')).toHaveTextContent('6 de 8 itens')
    expect(bar.getByText('Minha visão: itens da Noiva e de Ambos.')).toBeVisible()
  })

  it('como Noivo, a mesma regra, do lado dele', async () => {
    setup({}, { profile: 'Noivo', lens: 'minha' })
    const bar = await toolbar()
    expect(card(NOIVO_M)).toBeVisible()
    expect(card(NOIVA_M)).toBeNull()
    expect(bar.getByText('Minha visão: itens do Noivo e de Ambos.')).toBeVisible()
  })

  it('a lente Casal mostra tudo e não tem nota', async () => {
    setup({}, { profile: 'Noiva', lens: 'casal' })
    const bar = await toolbar()
    expect(card(NOIVO_M)).toBeVisible()
    expect(card(NOIVA_M)).toBeVisible()
    expect(bar.queryByText(/^Minha visão:/)).toBeNull()
    expect(bar.getByRole('status')).toBeEmptyDOMElement()
  })

  it('o filtro explícito de responsável vence a lente, e a tela diz isso', async () => {
    setup({ responsavel: 'noivo' }, { profile: 'Noiva', lens: 'minha' })
    const bar = await toolbar()
    expect(card(NOIVO_M)).toBeVisible()
    expect(card(NOIVA_M)).toBeNull()
    expect(bar.getByText('Filtro de responsável ativo: a lente não se aplica.')).toBeVisible()
    expect(bar.queryByText(/^Minha visão:/)).toBeNull()
  })

  it('"Limpar filtros" mantém a lente', async () => {
    const { user } = setup({ estado: 'destravado' }, { profile: 'Noiva', lens: 'minha' })
    const bar = await toolbar()
    await user.click(bar.getByRole('button', { name: 'Limpar filtros' }))
    expect(bar.getByText('Minha visão: itens da Noiva e de Ambos.')).toBeVisible()
    expect(card(NOIVO_M)).toBeNull()
  })

  it('sem perfil, a lente não filtra', async () => {
    setup({}, { lens: 'minha' })
    const bar = await toolbar()
    expect(card(NOIVO_M)).toBeVisible()
    expect(card(NOIVA_M)).toBeVisible()
    expect(bar.queryByText(/^Minha visão:/)).toBeNull()
  })
})

describe('o estado vazio só pela lente (F-CRN-09)', () => {
  /** Só a Noiva tem itens: o Noivo, na Minha visão, não vê nada. */
  function onlyNoiva() {
    const full = scheduleForFilters()
    const [, second] = full.phases
    if (!second) throw new Error('A fixture de filtros tem duas fases')
    return {
      ...full,
      phases: [
        { ...second, milestones: second.milestones.filter((m) => m.responsible === 'Noiva') },
      ],
      tasks: full.tasks.filter((t) => t.responsible === 'Noiva'),
    }
  }

  it('diz o que a lente mostra, com o artigo do perfil, e oferece a Visão do Casal', async () => {
    renderSchedule(
      { [GET_SCHEDULE]: jsonResponse(200, onlyNoiva()) },
      {},
      { profile: 'Noivo', lens: 'minha' },
    )
    // Sem filtro ativo, o título não fala de filtros.
    expect(await screen.findByText('Nada na Minha visão.')).toBeVisible()
    expect(screen.queryByText('Nenhum item com esses filtros.')).toBeNull()
    expect(
      screen.getByText('Na Minha visão aparecem só os itens do Noivo e os de Ambos.'),
    ).toBeVisible()
    expect(screen.getByRole('button', { name: 'Ver a Visão do Casal' })).toBeVisible()
    // Sem filtro explícito, não há o que limpar.
    expect(screen.queryByRole('button', { name: 'Limpar filtros' })).toBeNull()
  })

  it('"Ver a Visão do Casal" tira a lente, mostra os itens e leva o foco ao título da página', async () => {
    const { user } = renderSchedule(
      { [GET_SCHEDULE]: jsonResponse(200, onlyNoiva()) },
      {},
      { profile: 'Noivo', lens: 'minha' },
    )
    await user.click(await screen.findByRole('button', { name: 'Ver a Visão do Casal' }))

    expect(
      await screen.findByRole('button', { name: 'Marco Exemplo da Noiva Concluído' }),
    ).toBeVisible()
    expect(screen.queryByText('Nada na Minha visão.')).toBeNull()
    await waitFor(() => expect(screen.getByRole('heading', { level: 1 })).toHaveFocus())
  })

  it('a nota do Noiva usa o artigo certo', async () => {
    renderSchedule(
      { [GET_SCHEDULE]: jsonResponse(200, onlyNoiva()) },
      {},
      { profile: 'Noiva', lens: 'minha' },
    )
    expect(await screen.findByText('Minha visão: itens da Noiva e de Ambos.')).toBeVisible()
  })
})
