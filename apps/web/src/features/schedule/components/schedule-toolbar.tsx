import type { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Chip } from '@/components/ui/chip'
import { copy } from '../copy'
import {
  filtersFromSearch,
  hasActiveFilters,
  type Lens,
  lensApplies,
  type SessionProfile,
} from '../lib/schedule-filters'
import { RESPONSIBLE_SLUGS, type ScheduleSearch, STATE_SLUGS } from '../search'

const labels = copy.filters

/** Os estados, na ordem de `STATE_SLUGS`: os quatro do marco e o `A fazer` da avulsa; o texto é de `copy`. */
const STATE_LABELS = [
  copy.states.Bloqueado,
  copy.states.Destravado,
  copy.task.states['A fazer'],
  copy.states['Em andamento'],
  copy.states.Concluído,
] as const
const RESPONSIBLES = [
  copy.responsibles.Noivo,
  copy.responsibles.Noiva,
  copy.responsibles.Ambos,
] as const

function Group({ legend, children }: { legend: string; children: ReactNode }) {
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="text-eyebrow text-ink-muted">{legend}</legend>
      <div className="flex flex-wrap gap-2">{children}</div>
    </fieldset>
  )
}

export interface ScheduleToolbarProps {
  search: ScheduleSearch
  /** Cada filtro empurra uma entrada de histórico: o Voltar do navegador desfaz um por vez. */
  onSearchChange: (patch: Partial<ScheduleSearch>) => void
  lens: Lens
  profile?: SessionProfile
  /** "N de M itens": só quando algo estreita a lista. */
  count: { shown: number; total: number } | null
}

/**
 * Os filtros do cronograma e a nota da lente (F-CRN-09). Moram na URL; não há busca por texto. O
 * "Limpar filtros" limpa só os filtros: a lente e o painel aberto ficam.
 */
export function ScheduleToolbar({
  search,
  onSearchChange,
  lens,
  profile,
  count,
}: ScheduleToolbarProps) {
  const filters = filtersFromSearch(search)
  const toggle = <K extends keyof ScheduleSearch>(key: K, value: ScheduleSearch[K]) =>
    onSearchChange({ [key]: search[key] === value ? undefined : value } as Partial<ScheduleSearch>)
  const context = { filters, lens, profile }

  return (
    <section aria-label={labels.label} className="flex flex-col gap-4">
      <div className="flex flex-col gap-4">
        <Group legend={labels.responsible}>
          {RESPONSIBLES.map((label, index) => {
            const slug = RESPONSIBLE_SLUGS[index]
            return (
              <Chip
                key={label}
                pressed={search.responsavel === slug}
                onClick={() => toggle('responsavel', slug)}
              >
                {label}
              </Chip>
            )
          })}
        </Group>
        <Group legend={labels.state}>
          {STATE_LABELS.map((state, index) => {
            const slug = STATE_SLUGS[index]
            return (
              <Chip
                key={state}
                pressed={search.estado === slug}
                onClick={() => toggle('estado', slug)}
              >
                {state}
              </Chip>
            )
          })}
        </Group>
        <div className="flex flex-wrap gap-2">
          <Chip pressed={search.atrasados === true} onClick={() => toggle('atrasados', true)}>
            {labels.overdue}
          </Chip>
          <Chip pressed={search.avulsas === true} onClick={() => toggle('avulsas', true)}>
            {labels.tasksOnly}
          </Chip>
        </div>
      </div>
      {lens === 'minha' && profile && (
        <p className="text-body-sm text-ink-muted">
          {lensApplies(context) ? labels.lensNote[profile] : labels.lensOverridden}
        </p>
      )}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p role="status" className="text-body-sm text-ink-muted">
          {count ? labels.count(count.shown, count.total) : ''}
        </p>
        {hasActiveFilters(filters) && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() =>
              onSearchChange({
                responsavel: undefined,
                estado: undefined,
                atrasados: undefined,
                avulsas: undefined,
              })
            }
          >
            {labels.clear}
          </Button>
        )}
      </div>
    </section>
  )
}
