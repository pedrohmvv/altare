import { PageHeader } from '@/components/ui/page-header'
import { Conferencia } from './Conferencia'
import { TokensShowcase } from './tokens-showcase'

// Vitrine em construção (etapa (e)): tokens, tipografia e os primitivos com variantes e estados.
export function DesignSystemPage() {
  return (
    <>
      <PageHeader
        eyebrow="Exemplo · conferência"
        title="Design System"
        description="Espaço Exemplo A · texto de interface"
      />
      <TokensShowcase />
      <Conferencia />
    </>
  )
}
