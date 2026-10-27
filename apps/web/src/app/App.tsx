import { PageHeader } from '@/components/ui/page-header'
import { ToastProvider } from '@/components/ui/toast'
import { Conferencia } from './Conferencia'

// Conferência visual provisória (etapas (a) a (c)); a vitrine /design-system substitui isto na etapa (e).
export function App() {
  return (
    <ToastProvider>
      <main className="mx-auto max-w-4xl px-4 py-10">
        <img src="/brand/logo/altare-simbolo-oliva.svg" alt="" className="mb-4 h-12" />
        <PageHeader
          eyebrow="Exemplo · conferência"
          title="Altare"
          description="Espaço Exemplo A · texto de interface"
        />
        <Conferencia />
      </main>
    </ToastProvider>
  )
}
