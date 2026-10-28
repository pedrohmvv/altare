import { Badge } from '@/components/ui/badge'
import { Money } from '@/components/ui/money'
import type { ScopeCategory } from '../api/scope'
import { copy } from '../copy'
import { AlignmentBadge, ScopeStatusBadge } from './scope-badges'

/** Uma frente na lista: nome em serifa (nome de espaço, fornecedor ou frente, `identity.md` §4), status e alinhamento em texto. */
export function ScopeCategoryCard({ category }: { category: ScopeCategory }) {
  return (
    <li className="flex flex-col gap-2 rounded-card border border-border bg-surface p-4">
      <div className="flex items-start justify-between gap-3">
        <h4 className="text-name text-ink">{category.name}</h4>
        <ScopeStatusBadge status={category.status} />
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <AlignmentBadge alignment={category.alignment} />
        {category.hidden && <Badge variant="outline">{copy.scope.card.hidden}</Badge>}
      </div>
      <p className="text-body-sm text-ink-muted">
        {category.estimate_cents === null ? (
          copy.scope.card.noEstimate
        ) : (
          <Money cents={category.estimate_cents} className="text-num-sm text-ink" />
        )}
      </p>
      {category.status === 'Fica de fora' && category.discard_reason && (
        <p className="text-body-sm text-ink-muted">
          {copy.scope.card.discardReason}: {category.discard_reason}
        </p>
      )}
    </li>
  )
}
