import { PageHeader } from '@/components/ui/page-header'
import { BaselinePanel } from '../components/baseline-panel'
import { copy } from '../copy'

export function WeddingPage() {
  return (
    <>
      <PageHeader eyebrow={copy.eyebrow} title={copy.title} description={copy.description} />
      <div className="mt-10">
        <BaselinePanel />
      </div>
    </>
  )
}
