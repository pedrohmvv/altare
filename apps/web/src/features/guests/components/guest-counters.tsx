import type { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import type { BandCounts, GuestList } from '../api/guests'
import { copy } from '../copy'
import { formatPeople } from '../lib/numbers'
import { GuestSettingsDialog } from './guest-settings-dialog'

const labels = copy.counters

function bands(counts: BandCounts): string {
  const parts = [
    counts.adults > 0 ? labels.adults(counts.adults) : null,
    counts.paying_children > 0 ? labels.paying(counts.paying_children) : null,
    counts.exempt_children > 0 ? labels.exempt(counts.exempt_children) : null,
  ].filter((part) => part !== null)
  return parts.length === 0 ? labels.nobody : parts.join(' · ')
}

function Stat({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <dt className="text-eyebrow text-ink-muted">{label}</dt>
      {children}
    </div>
  )
}

const value = 'text-num-xl text-ink'
const detail = 'text-body-sm text-ink-muted'

/**
 * Os contadores no topo (F-CNV-06): Total Nominal, Estimado Ponderado e Confirmados, todos
 * derivados e calculados pelo servidor. Sem os pesos, o ponderado diz "defina os pesos" em vez de
 * mostrar um número presumido.
 */
export function GuestCounters({ list }: { list: GuestList }) {
  const { headcount, settings } = list
  const adjust = <Button variant="secondary">{copy.settings.button}</Button>
  return (
    <section
      aria-label={labels.label}
      className="flex flex-col gap-4 rounded-card border border-border bg-surface p-5 max-md:p-4"
    >
      <dl className="grid gap-5 sm:grid-cols-3">
        <Stat label={labels.total}>
          <dd className={value}>{headcount.total_nominal.total}</dd>
          <dd className={detail}>{bands(headcount.total_nominal)}</dd>
        </Stat>
        <Stat label={labels.weighted}>
          {headcount.weighted_rounded_up === null ? (
            <>
              <dd className="text-name text-ink">{labels.setWeights}</dd>
              <dd className={detail}>{labels.setWeightsHint}</dd>
            </>
          ) : (
            <>
              <dd className={value}>{headcount.weighted_rounded_up}</dd>
              <dd className={detail}>
                {labels.weightedDetail(
                  formatPeople(headcount.weighted_adults_hundredths ?? 0),
                  formatPeople(headcount.weighted_paying_children_hundredths ?? 0),
                )}
              </dd>
            </>
          )}
        </Stat>
        <Stat label={labels.confirmed}>
          <dd className={value}>{headcount.confirmed.total}</dd>
          <dd className={detail}>{bands(headcount.confirmed)}</dd>
        </Stat>
      </dl>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-body-sm text-ink-muted">
          {labels.notAttendingLabel}: {headcount.not_attending.total}
        </p>
        <GuestSettingsDialog settings={settings} trigger={adjust} />
      </div>
    </section>
  )
}
