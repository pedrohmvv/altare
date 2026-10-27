import {
  Calendar,
  Gift,
  House,
  LayoutDashboard,
  type LucideIcon,
  Map as MapIcon,
  MessageSquareText,
  Scale,
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
  /** Ícone da barra lateral e da folha "Mais" (guia de identidade, Visão Geral no desktop). */
  icon: LucideIcon
  /** Só para os destinos da barra inferior do celular (`design-system.md` §10.1). */
  bar?: {
    /** Rótulo curto do guia, que cabe em ~70 px por destino. */
    label: string
    /** Nome lido pelo leitor de tela quando o rótulo é abreviado (contém o rótulo visível). */
    name?: string
    icon: LucideIcon
  }
  /** O Assistente fica separado das 7 áreas por uma hairline (D-050). */
  group: 'areas' | 'assistant'
}

/** Fonte única das 8 áreas: a ordem aqui é a ordem na barra lateral (design-system.md §10.1). */
export const NAV_ITEMS: readonly NavItem[] = [
  {
    to: '/',
    label: 'Visão Geral',
    icon: LayoutDashboard,
    bar: { label: 'Início', icon: House },
    group: 'areas',
  },
  { to: '/planejamento', label: 'Planejamento & Caminhos', icon: MapIcon, group: 'areas' },
  { to: '/cronograma', label: 'Cronograma & Dependências', icon: Calendar, group: 'areas' },
  {
    to: '/possibilidades',
    label: 'Possibilidades & Decisões',
    icon: Scale,
    bar: { label: 'Possib.', name: 'Possibilidades', icon: Scale },
    group: 'areas',
  },
  {
    to: '/orcamento',
    label: 'Orçamento & Simulador',
    icon: Wallet,
    bar: { label: 'Orçam.', name: 'Orçamento', icon: Wallet },
    group: 'areas',
  },
  {
    to: '/contatos',
    label: 'Contatos & Fornecedores',
    icon: Users,
    bar: { label: 'Contatos', icon: Users },
    group: 'areas',
  },
  { to: '/convidados', label: 'Convidados, Enxoval & Dia D', icon: Gift, group: 'areas' },
  { to: '/assistente', label: 'Assistente', icon: MessageSquareText, group: 'assistant' },
]
