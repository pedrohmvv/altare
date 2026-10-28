import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { Guest, Household } from '../api/guests'
import { copy } from '../copy'
import { displayName } from '../lib/names'
import { summaryText } from '../lib/summary'
import { GuestStatusBadge, SideBadge } from './guest-badges'
import { WhatsAppButton } from './whatsapp-button'

const columns = copy.list.columns

/**
 * No computador, a tabela agrupada por núcleo (F-CNV-07): cada núcleo é um grupo de linhas com o
 * nome, o lado e o resumo no cabeçalho do grupo, e o painel lateral abre pelo nome.
 */
export function HouseholdTable({
  households,
  onOpen,
}: {
  households: readonly Household[]
  onOpen: (householdId: string, opener: HTMLElement) => void
}) {
  return (
    <Table label={copy.list.tableLabel} density="compact">
      <TableCaption srOnly>{copy.list.tableCaption}</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>{columns.name}</TableHead>
          <TableHead>{columns.band}</TableHead>
          <TableHead>{columns.probability}</TableHead>
          <TableHead>{columns.status}</TableHead>
          <TableHead>{columns.contact}</TableHead>
        </TableRow>
      </TableHeader>
      {households.map((household) => (
        <TableBody key={household.id}>
          <tr className="border-b border-border bg-surface-muted">
            <th scope="rowgroup" colSpan={5} className="px-4 py-2 text-left font-normal">
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={(event) => onOpen(household.id, event.currentTarget)}
                  className="rounded-control text-left text-name text-ink hover:underline"
                >
                  {household.name}
                </button>
                <SideBadge side={household.side} />
                <span className="text-body-sm text-ink-muted">
                  {summaryText(household.summary)}
                </span>
              </div>
            </th>
          </tr>
          {household.guests.map((guest) => (
            <GuestRow key={guest.id} guest={guest} />
          ))}
        </TableBody>
      ))}
    </Table>
  )
}

function GuestRow({ guest }: { guest: Guest }) {
  const name = displayName(guest)
  return (
    <TableRow>
      <TableCell>
        {name}
        {guest.name && guest.holder_name && (
          <span className="block text-ui-xs text-ink-muted">
            {copy.companion.of(guest.holder_name)}
          </span>
        )}
      </TableCell>
      <TableCell>
        {copy.bands[guest.band]}
        {guest.age !== null && (
          <span className="block text-ui-xs text-ink-muted">{copy.sheet.age(guest.age)}</span>
        )}
      </TableCell>
      <TableCell>{copy.probabilities[guest.probability]}</TableCell>
      <TableCell>
        <GuestStatusBadge status={guest.status} />
      </TableCell>
      <TableCell>
        <WhatsAppButton url={guest.whatsapp_url} name={name} />
      </TableCell>
    </TableRow>
  )
}
