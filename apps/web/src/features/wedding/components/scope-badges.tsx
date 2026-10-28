import { CircleCheck, MessagesSquare } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import type { ScopeCategory, ScopeStatus } from '../api/scope'
import { copy } from '../copy'

/** `Entra` é acordo (sálvia com `circle-check`); `Em discussão`, `Talvez` e `Fica de fora` são neutros, sempre em texto. */
export function ScopeStatusBadge({ status }: { status: ScopeStatus }) {
  if (status === 'Entra (Essencial)') {
    return (
      <Badge variant="consensus" icon={<CircleCheck />}>
        {status}
      </Badge>
    )
  }
  return <Badge variant={status === 'Talvez (Se couber)' ? 'outline' : 'neutral'}>{status}</Badge>
}

/**
 * O alinhamento das duas prioridades, derivado pela API (F-PLN-04). Divergir é um convite a
 * conversar, em argila e com `messages-square`, nunca vermelho; falta avaliar diz quem falta.
 */
export function AlignmentBadge({ alignment }: { alignment: ScopeCategory['alignment'] }) {
  if (alignment.state === 'alinhados') {
    return (
      <Badge variant="consensus" icon={<CircleCheck />}>
        {copy.scope.alignment.aligned}
      </Badge>
    )
  }
  if (alignment.state === 'divergem') {
    return (
      <Badge variant="attention" icon={<MessagesSquare />}>
        {copy.scope.alignment.diverge}
      </Badge>
    )
  }
  const [only, other] = alignment.missing
  return (
    <Badge>
      {only && !other ? copy.scope.alignment.waitingFor(only) : copy.scope.alignment.both}
    </Badge>
  )
}
