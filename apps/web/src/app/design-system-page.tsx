import { PageHeader } from '@/components/ui/page-header'
import { IdentityShowcase } from './identity-showcase'
import { PrimitivesShowcase } from './primitives-showcase'
import { ShowcaseIndex } from './showcase-index'
import { TokensShowcase } from './tokens-showcase'

/**
 * Vitrine do design system, só em desenvolvimento (D-053, D-057): em duas partes, a identidade
 * (cores, tipografia e o catálogo do guia, D-058) e os componentes, com um índice no topo.
 */
export function DesignSystemPage() {
  return (
    <>
      <PageHeader
        eyebrow="Vitrine · dados de exemplo"
        title="Design System"
        description="Cores, tipografia e os componentes do Altare, com variantes e estados. Os exemplos são fictícios."
      />
      <ShowcaseIndex />
      <TokensShowcase />
      <IdentityShowcase />
      <PrimitivesShowcase />
    </>
  )
}
