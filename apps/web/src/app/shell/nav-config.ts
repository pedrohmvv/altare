import {
  CalendarDays,
  Columns3,
  Compass,
  Contact,
  House,
  type LucideIcon,
  MessageSquareText,
  Users,
  Wallet,
} from 'lucide-react'

export type AreaPath =
  | '/'
  | '/planejamento'
  | '/cronograma'
  | '/possibilidades'
  | '/orcamento'
  | '/contatos'
  | '/convidados'
  | '/assistente'

export interface NavItem {
  to: AreaPath
  /** Nome da área na barra lateral e na folha "Mais". Igual ao título da página. */
  label: string
  /** Nome curto da barra inferior do celular, onde o rótulo precisa caber em ~70 px. */
  shortLabel: string
  icon: LucideIcon
  /** `bar` aparece na barra inferior; `more` fica na folha "Mais" (design-system.md §10.1). */
  placement: 'bar' | 'more'
  /** O Assistente fica separado das 7 áreas por uma hairline (D-050). */
  group: 'areas' | 'assistant'
}

/** Fonte única das 8 áreas: a ordem aqui é a ordem na barra lateral (design-system.md §10.1). */
export const NAV_ITEMS: readonly NavItem[] = [
  {
    to: '/',
    label: 'Visão Geral',
    shortLabel: 'Início',
    icon: House,
    placement: 'bar',
    group: 'areas',
  },
  {
    to: '/planejamento',
    label: 'Planejamento & Caminhos',
    shortLabel: 'Planejamento',
    icon: Compass,
    placement: 'more',
    group: 'areas',
  },
  {
    to: '/cronograma',
    label: 'Cronograma & Dependências',
    shortLabel: 'Cronograma',
    icon: CalendarDays,
    placement: 'more',
    group: 'areas',
  },
  {
    to: '/possibilidades',
    label: 'Possibilidades & Decisões',
    shortLabel: 'Opções',
    icon: Columns3,
    placement: 'bar',
    group: 'areas',
  },
  {
    to: '/orcamento',
    label: 'Orçamento & Simulador',
    shortLabel: 'Orçamento',
    icon: Wallet,
    placement: 'bar',
    group: 'areas',
  },
  {
    to: '/contatos',
    label: 'Contatos & Fornecedores',
    shortLabel: 'Contatos',
    icon: Contact,
    placement: 'bar',
    group: 'areas',
  },
  {
    to: '/convidados',
    label: 'Convidados, Enxoval & Dia D',
    shortLabel: 'Convidados',
    icon: Users,
    placement: 'more',
    group: 'areas',
  },
  {
    to: '/assistente',
    label: 'Assistente',
    shortLabel: 'Assistente',
    icon: MessageSquareText,
    placement: 'more',
    group: 'assistant',
  },
]
