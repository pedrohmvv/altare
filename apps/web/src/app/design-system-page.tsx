import { PageHeader } from '@/components/ui/page-header'
import { PrimitivesShowcase } from './primitives-showcase'
import { TokensShowcase } from './tokens-showcase'

/** Vitrine do design system, só em desenvolvimento (D-053, D-057): tokens, tipografia e os primitivos. */
export function DesignSystemPage() {
  return (
    <>
      <PageHeader
        eyebrow="Vitrine · dados de exemplo"
        title="Design System"
        description="Cores, tipografia e os componentes do Altare, com variantes e estados. Os exemplos são fictícios."
      />
      <TokensShowcase />
      <PrimitivesShowcase />
    </>
  )
}
