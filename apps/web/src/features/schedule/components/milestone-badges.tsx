import { CircleAlert, CircleCheck, CircleDot, Lock, LockOpen } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import type { MilestoneState } from '../api/schedule'
import { copy } from '../copy'

/**
 * O estado do marco, sempre em texto e com o ícone do mapa semântico (identity.md §7): `Destravado`
 * é acordo (sálvia, `lock-open`), `Bloqueado` é neutro (`lock`) e `Concluído` leva `circle-check`.
 */
export function StateBadge({ state }: { state: MilestoneState }) {
  const label = copy.states[state]
  if (state === 'Destravado') {
    return (
      <Badge variant="consensus" icon={<LockOpen />}>
        {label}
      </Badge>
    )
  }
  if (state === 'Concluído') {
    return (
      <Badge variant="consensus" icon={<CircleCheck />}>
        {label}
      </Badge>
    )
  }
  if (state === 'Em andamento') {
    return (
      <Badge variant="outline" icon={<CircleDot />}>
        {label}
      </Badge>
    )
  }
  return (
    <Badge variant="neutral" icon={<Lock />}>
      {label}
    </Badge>
  )
}

/** O atraso é um fato dito com calma: argila, `circle-alert` e a palavra (nunca vermelho). */
export function OverdueBadge() {
  return (
    <Badge variant="attention" icon={<CircleAlert />}>
      {copy.overdue}
    </Badge>
  )
}

export function OptionalBadge() {
  return <Badge variant="outline">{copy.optional}</Badge>
}
