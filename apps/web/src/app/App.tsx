import { Conferencia } from './Conferencia'

// Conferência visual provisória (etapas (a) a (c)); a vitrine /design-system substitui isto na etapa (e).
export function App() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <p className="text-eyebrow text-ink-muted">Exemplo · tokens</p>
      <img src="/brand/logo/altare-simbolo-oliva.svg" alt="" className="mb-4 h-12" />
      <h1 className="text-display">Altare</h1>
      <p className="text-body-lg text-ink-muted">Espaço Exemplo A · texto de interface</p>
      <p className="text-num-lg text-accent-ink">R$ 12.480,00</p>
      <Conferencia />
    </main>
  )
}
