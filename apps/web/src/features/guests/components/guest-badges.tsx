import { CircleCheck, CircleMinus } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import type { GuestStatus, Side } from '../api/guests'
import { copy } from '../copy'

/**
 * `Confirmado` é acordo (sálvia com `circle-check`). `Não irá` é um fato, não um erro: fica neutro,
 * com `circle-minus`. O status vai sempre em texto completo (identity.md §7).
 */
export function GuestStatusBadge({ status }: { status: GuestStatus }) {
  if (status === 'Confirmado') {
    return (
      <Badge variant="consensus" icon={<CircleCheck />}>
        {copy.statuses[status]}
      </Badge>
    )
  }
  if (status === 'Não irá') {
    return <Badge icon={<CircleMinus />}>{copy.statuses[status]}</Badge>
  }
  return (
    <Badge variant={status === 'Convidado' ? 'outline' : 'neutral'}>{copy.statuses[status]}</Badge>
  )
}

/** O lado se distingue por rótulo, sem cor por perfil (design-system.md §3.3). */
export function SideBadge({ side }: { side: Side }) {
  return <Badge variant="outline">{copy.sides[side]}</Badge>
}
