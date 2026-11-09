import type { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Chip } from '@/components/ui/chip'
import { Input } from '@/components/ui/input'
import { AGE_BANDS, GUEST_STATUSES, PROBABILITIES, SIDES } from '../api/guests'
import { copy } from '../copy'
import { filtersFromSearch, hasActiveFilters } from '../lib/guest-filters'
import type { Lens, SessionProfile } from '../lib/sides'
import {
  BAND_SLUGS,
  type GuestsSearch,
  PROBABILITY_SLUGS,
  SIDE_SLUGS,
  STATUS_SLUGS,
} from '../search'

const labels = copy.filters

function Group({ legend, children }: { legend: string; children: ReactNode }) {
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="text-eyebrow text-ink-muted">{legend}</legend>
      <div className="flex flex-wrap gap-2">{children}</div>
    </fieldset>
  )
}

export interface GuestToolbarProps {
  search: GuestsSearch
  onSearchChange: (patch: Partial<GuestsSearch>) => void
  /** O texto da busca mora no navegador, nunca na URL. */
  query: string
  onQueryChange: (query: string) => void
  lens: Lens
  profile: SessionProfile
  /** "N de M pessoas": só quando algo estreita a lista. */
  count: { shown: number; total: number } | null
  onClear: () => void
}

/** Busca, filtros e a lente da lista (F-CNV-07). Os filtros moram na URL; a busca, não. */
export function GuestToolbar({
  search,
  onSearchChange,
  query,
  onQueryChange,
  lens,
  profile,
  count,
  onClear,
}: GuestToolbarProps) {
  const toggle = <K extends keyof GuestsSearch>(key: K, value: GuestsSearch[K]) =>
    onSearchChange({ [key]: search[key] === value ? undefined : value } as Partial<GuestsSearch>)
  const narrowed = hasActiveFilters(filtersFromSearch(search)) || query.trim() !== ''

  return (
    <section aria-label={labels.label} className="flex flex-col gap-4">
      <Input
        label={labels.search}
        hint={labels.searchHint}
        type="search"
        autoComplete="off"
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
      />
      <div className="flex flex-col gap-4">
        <Group legend={labels.side}>
          {SIDES.map((side, index) => {
            const slug = SIDE_SLUGS[index]
            return (
              <Chip key={side} pressed={search.lado === slug} onClick={() => toggle('lado', slug)}>
                {copy.sides[side]}
              </Chip>
            )
          })}
          {lens === 'minha' && (
            <Chip pressed={search.outro === true} onClick={() => toggle('outro', true)}>
              {labels.other}
            </Chip>
          )}
        </Group>
        <Group legend={labels.band}>
          {AGE_BANDS.map((band, index) => {
            const slug = BAND_SLUGS[index]
            return (
              <Chip
                key={band}
                pressed={search.faixa === slug}
                onClick={() => toggle('faixa', slug)}
              >
                {copy.bands[band]}
              </Chip>
            )
          })}
        </Group>
        <Group legend={labels.probability}>
          {PROBABILITIES.map((probability, index) => {
            const slug = PROBABILITY_SLUGS[index]
            return (
              <Chip
                key={probability}
                pressed={search.probabilidade === slug}
                onClick={() => toggle('probabilidade', slug)}
              >
                {copy.probabilities[probability]}
              </Chip>
            )
          })}
        </Group>
        <Group legend={labels.status}>
          {GUEST_STATUSES.map((status, index) => {
            const slug = STATUS_SLUGS[index]
            return (
              <Chip
                key={status}
                pressed={search.status === slug}
                onClick={() => toggle('status', slug)}
              >
                {copy.statuses[status]}
              </Chip>
            )
          })}
        </Group>
        <div className="flex flex-wrap gap-2">
          <Chip pressed={search.semconvite === true} onClick={() => toggle('semconvite', true)}>
            {labels.noInvite}
          </Chip>
          <Chip pressed={search.restricao === true} onClick={() => toggle('restricao', true)}>
            {labels.dietary}
          </Chip>
        </div>
      </div>
      {lens === 'minha' && search.outro !== true && (
        <p className="text-body-sm text-ink-muted">{labels.lensNote(profile)}</p>
      )}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p role="status" className="text-body-sm text-ink-muted">
          {count ? labels.count(count.shown, count.total) : ''}
        </p>
        {narrowed && (
          <Button variant="ghost" size="sm" onClick={onClear}>
            {labels.clear}
          </Button>
        )}
      </div>
    </section>
  )
}
