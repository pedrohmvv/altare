import { Card } from '@/components/ui/card'
import { EmptyState } from '@/components/ui/empty-state'
import { PageHeader } from '@/components/ui/page-header'
import { copy } from '../copy'

export function WeddingPage() {
  return (
    <>
      <PageHeader eyebrow={copy.eyebrow} title={copy.title} description={copy.description} />
      <Card className="mt-10">
        <EmptyState title={copy.empty.title} description={copy.empty.description} />
      </Card>
    </>
  )
}
