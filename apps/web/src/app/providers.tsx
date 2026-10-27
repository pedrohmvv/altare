import type { ReactNode } from 'react'
import { ToastProvider } from '@/components/ui/toast'

/** Provedores globais do app (architecture.md §11). */
export function Providers({ children }: { children: ReactNode }) {
  return <ToastProvider>{children}</ToastProvider>
}
