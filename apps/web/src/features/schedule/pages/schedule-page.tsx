import { PageHeader } from '@/components/ui/page-header'
import { ScheduleList } from '../components/schedule-list'
import { copy } from '../copy'
import type { ScheduleSearch } from '../search'

export interface SchedulePageProps {
  /** O que a URL guarda: o marco aberto no painel lateral. */
  search: ScheduleSearch
  /** Pede uma mudança na URL; `undefined` num campo o tira. */
  onSearchChange: (patch: Partial<ScheduleSearch>) => void
}

/** A página não conhece o roteador: recebe a URL e devolve o que quer mudar, e assim se testa sem ele. */
export function SchedulePage({ search, onSearchChange }: SchedulePageProps) {
  return (
    <>
      <PageHeader eyebrow={copy.eyebrow} title={copy.title} description={copy.description} />
      <div className="mt-10">
        <ScheduleList search={search} onSearchChange={onSearchChange} />
      </div>
    </>
  )
}
