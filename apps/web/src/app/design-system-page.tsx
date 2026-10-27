import { PageHeader } from '@/components/ui/page-header'
import { Conferencia } from './Conferencia'

// Conferência visual provisória (etapas (a) a (d)); a vitrine /design-system definitiva vem na etapa (e).
export function DesignSystemPage() {
  return (
    <>
      <PageHeader
        eyebrow="Exemplo · conferência"
        title="Design System"
        description="Espaço Exemplo A · texto de interface"
      />
      <Conferencia />
    </>
  )
}
