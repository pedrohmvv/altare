import { Check } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import type { DefinitionStatus } from '../api/baseline'
import { copy } from '../copy'

/** `Em definição` é o selo neutro do guia (pág. 38); `Definido` é acordo, em sálvia, com ícone e texto. */
export function DefinitionBadge({ status }: { status: DefinitionStatus }) {
  if (status === 'Definido') {
    return (
      <Badge variant="consensus" icon={<Check />}>
        {copy.status.Definido}
      </Badge>
    )
  }
  return <Badge>{copy.status['Em definição']}</Badge>
}
