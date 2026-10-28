import { type QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LucideProvider } from 'lucide-react'
import type { ReactNode } from 'react'
import { ToastProvider } from '@/components/ui/toast'

/** Provedores globais do app (architecture.md §11). */
export function Providers({
  children,
  queryClient,
}: {
  children: ReactNode
  queryClient: QueryClient
}) {
  return (
    <QueryClientProvider client={queryClient}>
      {/* Traço de 1,5 px que não escala com o tamanho do ícone (identity.md §7, guia pág. 33). */}
      <LucideProvider strokeWidth={1.5} nonScalingStroke>
        <ToastProvider>{children}</ToastProvider>
      </LucideProvider>
    </QueryClientProvider>
  )
}
