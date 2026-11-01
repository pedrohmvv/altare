import { PageHeader } from '@/components/ui/page-header'
import { GuestList } from '../components/guest-list'
import { copy } from '../copy'
import type { Lens, SessionProfile } from '../lib/sides'
import type { GuestsSearch } from '../search'

export interface GuestsPageProps {
  /** O que a URL guarda: o núcleo aberto no painel. */
  search: GuestsSearch
  /** Pede uma mudança na URL; `undefined` num campo o tira. */
  onSearchChange: (patch: Partial<GuestsSearch>) => void
  /** Quem está na sessão. */
  profile: SessionProfile
  /** A lente de visão: ausente é `casal`. */
  lens?: Lens
}

/** A página não conhece o roteador: recebe a URL e devolve o que quer mudar, e assim se testa sem ele. */
export function GuestsPage({ search, onSearchChange, profile, lens }: GuestsPageProps) {
  return (
    <>
      <PageHeader eyebrow={copy.eyebrow} title={copy.title} description={copy.description} />
      <div className="mt-10">
        <GuestList search={search} onSearchChange={onSearchChange} profile={profile} lens={lens} />
      </div>
    </>
  )
}
