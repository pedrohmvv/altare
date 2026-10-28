import { useQuery } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { EmptyState } from '@/components/ui/empty-state'
import { useMediaQuery } from '@/lib/use-media-query'
import { guestListQueryOptions } from '../api/guests'
import { copy } from '../copy'
import type { GuestsSearch } from '../search'
import { GuestCounters } from './guest-counters'
import { HouseholdCard } from './household-card'
import { HouseholdSheet } from './household-sheet'
import { HouseholdTable } from './household-table'
import { NewHouseholdDialog, NewHouseholdTrigger } from './new-household-dialog'

export interface GuestListProps {
  search: GuestsSearch
  onSearchChange: (patch: Partial<GuestsSearch>) => void
}

/** A lista de convidados por núcleo (F-CNV-07): tabela agrupada no computador, cartões no celular. */
export function GuestList({ search, onSearchChange }: GuestListProps) {
  const query = useQuery(guestListQueryOptions)
  const wide = useMediaQuery('(min-width: 768px)')
  // O último núcleo aberto continua montado durante a animação de saída do painel. Quem abriu o
  // painel recebe o foco de volta ao fechá-lo (o Radix só o faz com um gatilho).
  const opener = useRef<HTMLElement | null>(null)
  const [lastOpened, setLastOpened] = useState<string | undefined>(undefined)
  if (search.nucleo && search.nucleo !== lastOpened) setLastOpened(search.nucleo)

  if (query.isPending) {
    return (
      <Card aria-busy>
        <p className="text-body-sm text-ink-muted">{copy.list.loading}</p>
        <div aria-hidden className="mt-4 flex flex-col gap-3">
          <div className="h-3 w-2/3 rounded-pill bg-surface-sunken" />
          <div className="h-3 w-1/2 rounded-pill bg-surface-sunken" />
          <div className="h-16 rounded-card bg-surface-sunken" />
        </div>
      </Card>
    )
  }
  if (query.isError) {
    return (
      <Card>
        <p className="text-body font-medium text-ink">{copy.list.loadError.title}</p>
        <p className="text-body-sm text-ink-muted">{copy.list.loadError.description}</p>
        <Button variant="secondary" className="mt-3" onClick={() => void query.refetch()}>
          {copy.list.loadError.retry}
        </Button>
      </Card>
    )
  }

  const { households } = query.data
  if (households.length === 0) {
    return (
      <NewHouseholdDialog>
        <Card>
          <EmptyState
            title={copy.list.empty.title}
            description={copy.list.empty.description}
            action={<NewHouseholdTrigger />}
          />
        </Card>
      </NewHouseholdDialog>
    )
  }

  const open = (householdId: string, from: HTMLElement) => {
    opener.current = from
    onSearchChange({ nucleo: householdId })
  }
  const sheetHousehold = households.find(
    (household) => household.id === (search.nucleo ?? lastOpened),
  )

  return (
    <NewHouseholdDialog>
      <div className="flex flex-col gap-6">
        <h2 className="sr-only">{copy.list.title}</h2>
        <GuestCounters list={query.data} />
        <div className="flex flex-wrap gap-3">
          <NewHouseholdTrigger />
        </div>
        {sheetHousehold && (
          <HouseholdSheet
            household={sheetHousehold}
            others={households
              .filter((household) => household.id !== sheetHousehold.id)
              .map((household) => ({ id: household.id, name: household.name }))}
            open={Boolean(search.nucleo)}
            onOpenChange={(isOpen) => !isOpen && onSearchChange({ nucleo: undefined })}
            onCloseAutoFocus={(event) => {
              event.preventDefault()
              opener.current?.focus()
            }}
          />
        )}
        {wide ? (
          <HouseholdTable households={households} onOpen={open} />
        ) : (
          <ul className="flex flex-col gap-3">
            {households.map((household) => (
              <HouseholdCard key={household.id} household={household} onOpen={open} />
            ))}
          </ul>
        )}
      </div>
    </NewHouseholdDialog>
  )
}
