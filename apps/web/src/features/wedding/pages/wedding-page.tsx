import { PageHeader } from '@/components/ui/page-header'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BaselinePanel } from '../components/baseline-panel'
import { ScopeMap } from '../components/scope-map'
import { copy } from '../copy'
import type { Lens, SessionProfile } from '../lib/scope-filters'
import type { PlanningSearch } from '../search'

export interface WeddingPageProps {
  /** O que a URL guarda: aba, vista, filtros e a categoria aberta. */
  search: PlanningSearch
  /** Pede uma mudança na URL; `undefined` num campo o tira. */
  onSearchChange: (patch: Partial<PlanningSearch>) => void
  /** Quem está na sessão. */
  profile: SessionProfile
  /** A lente de visão: ausente é `casal`. */
  lens?: Lens
}

/** A página não conhece o roteador: recebe a URL e devolve o que quer mudar, e assim se testa sem ele. */
export function WeddingPage({ search, onSearchChange, profile, lens }: WeddingPageProps) {
  return (
    <>
      <PageHeader eyebrow={copy.eyebrow} title={copy.title} description={copy.description} />
      <Tabs
        className="mt-10"
        value={search.aba ?? 'definicoes'}
        onValueChange={(value) =>
          onSearchChange({ aba: value === 'escopo' ? 'escopo' : undefined, categoria: undefined })
        }
      >
        <TabsList aria-label={copy.tabs.label}>
          <TabsTrigger value="definicoes">{copy.tabs.baseline}</TabsTrigger>
          <TabsTrigger value="escopo">{copy.tabs.scope}</TabsTrigger>
        </TabsList>
        <TabsContent value="definicoes" className="mt-6">
          <BaselinePanel />
        </TabsContent>
        <TabsContent value="escopo" className="mt-6">
          <ScopeMap search={search} onSearchChange={onSearchChange} profile={profile} lens={lens} />
        </TabsContent>
      </Tabs>
    </>
  )
}
