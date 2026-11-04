import { Chip } from '@/components/ui/chip'
import { Money } from '@/components/ui/money'
import { Progress } from '@/components/ui/progress'
import { SegmentedControl } from '@/components/ui/segmented-control'
import type { ScopeMap } from '../api/scope'
import { SCOPE_STATUSES } from '../api/scope'
import { copy } from '../copy'
import { SLUG_BY_STATUS } from '../lib/scope-filters'
import type { PlanningSearch } from '../search'

interface ScopeToolbarProps {
  map: ScopeMap
  search: PlanningSearch
  onSearchChange: (patch: Partial<PlanningSearch>) => void
}

/** Progresso e totais vêm prontos da API (regra numérica só no backend); aqui só se exibem. */
export function ScopeToolbar({ map, search, onSearchChange }: ScopeToolbarProps) {
  const { progress, totals } = map
  return (
    <div className="flex flex-col gap-5">
      <Progress
        value={progress.classified}
        max={progress.total}
        label={copy.scope.progress(progress.classified, progress.total)}
        className="max-w-md"
      />

      <fieldset className="grid max-w-md gap-3 rounded-card bg-surface-muted p-4 sm:grid-cols-2">
        <legend className="sr-only">{copy.scope.totals.label}</legend>
        {(
          [
            ['essential', totals.essential_cents, totals.essential_without_estimate],
            ['maybe', totals.maybe_cents, totals.maybe_without_estimate],
          ] as const
        ).map(([key, cents, missing]) => (
          <div key={key} className="flex flex-col gap-0.5">
            <span className="text-ui-xs text-ink-muted">{copy.scope.totals[key]}</span>
            <Money cents={cents} className="text-num text-ink" />
            {missing > 0 && (
              <span className="text-ui-xs text-ink-muted">
                {copy.scope.totals.withoutEstimate(missing)}
              </span>
            )}
          </div>
        ))}
        <p className="text-ui-xs text-ink-muted sm:col-span-2">{copy.scope.totals.note}</p>
      </fieldset>

      <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
        <SegmentedControl
          aria-label={copy.scope.view.label}
          options={[
            { value: 'grupo', label: copy.scope.view.group },
            { value: 'status', label: copy.scope.view.status },
          ]}
          value={search.vista ?? 'grupo'}
          onValueChange={(value) =>
            onSearchChange({ vista: value === 'status' ? 'status' : undefined })
          }
        />
      </div>

      <fieldset className="flex flex-wrap gap-2">
        <legend className="sr-only">{copy.scope.filters.label}</legend>
        {SCOPE_STATUSES.map((status) => {
          const slug = SLUG_BY_STATUS[status]
          return (
            <Chip
              key={slug}
              pressed={search.status === slug}
              onClick={() => onSearchChange({ status: search.status === slug ? undefined : slug })}
            >
              {status}
            </Chip>
          )
        })}
        <Chip
          pressed={search.alinhamento === 'divergem'}
          onClick={() =>
            onSearchChange({
              alinhamento: search.alinhamento === 'divergem' ? undefined : 'divergem',
            })
          }
        >
          {copy.scope.filters.diverge}
        </Chip>
        <Chip
          pressed={search.alinhamento === 'falta'}
          onClick={() =>
            onSearchChange({ alinhamento: search.alinhamento === 'falta' ? undefined : 'falta' })
          }
        >
          {copy.scope.filters.missing}
        </Chip>
        <Chip
          pressed={Boolean(search.pendente)}
          onClick={() => onSearchChange({ pendente: search.pendente ? undefined : true })}
        >
          {copy.scope.filters.pending}
        </Chip>
        <Chip
          pressed={Boolean(search.ocultas)}
          onClick={() => onSearchChange({ ocultas: search.ocultas ? undefined : true })}
        >
          {copy.scope.filters.hidden}
        </Chip>
      </fieldset>
    </div>
  )
}
