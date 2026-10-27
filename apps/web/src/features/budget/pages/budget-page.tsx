import { EmptyState } from '@/components/ui/empty-state'
import { PageHeader } from '@/components/ui/page-header'
import { copy } from '../copy'

export function BudgetPage() {
  return (
    <>
      <PageHeader eyebrow={copy.eyebrow} title={copy.title} description={copy.description} />
      <EmptyState className="mt-10" title={copy.empty.title} description={copy.empty.description} />
    </>
  )
}
