import { cva } from 'class-variance-authority'
import { CircleAlert, CircleCheck, Info, X } from 'lucide-react'
import { Toast as RadixToast } from 'radix-ui'
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from 'react'
import { Button } from './button'

export type ToastTone = 'success' | 'attention' | 'info'

export interface ToastOptions {
  title: string
  description?: string
  /** Cor, ícone e texto andam juntos (identity.md §7). O padrão é `info`. */
  tone?: ToastTone
  action?: {
    label: string
    /** Como fazer o mesmo em outro lugar da tela, já que a notificação some em 4 s. */
    altText: string
    onClick: () => void
  }
}

interface ToastContextValue {
  toast: (options: ToastOptions) => string
  dismiss: (id: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

const DURATION_MS = 4000
// Tempo para a animação de saída terminar antes de tirar a notificação da fila.
const CLEANUP_MS = 500

const ICONS = { success: CircleCheck, attention: CircleAlert, info: Info } as const

const toastVariants = cva(
  [
    'pointer-events-auto flex items-start gap-3 rounded-card border border-border p-4 shadow-nivel-1',
    'data-[state=closed]:animate-toast-out data-[state=open]:animate-toast-in',
    'data-[swipe=cancel]:translate-x-0 data-[swipe=cancel]:transition-transform',
    'data-[swipe=end]:translate-x-(--radix-toast-swipe-end-x) data-[swipe=move]:translate-x-(--radix-toast-swipe-move-x)',
  ],
  {
    variants: {
      tone: {
        success: 'bg-consensus-bg text-consensus-ink',
        attention: 'bg-attention-bg text-attention-ink',
        info: 'bg-surface text-ink',
      },
    },
  },
)

interface ToastItem extends ToastOptions {
  id: string
  open: boolean
}

/** Notificações de 4 s em região `aria-live="polite"`, com pausa ao passar o mouse ou focar. */
export function ToastProvider({ children }: { children?: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([])
  const counter = useRef(0)

  const remove = useCallback((id: string) => {
    setItems((current) => current.filter((item) => item.id !== id))
  }, [])

  const close = useCallback(
    (id: string) => {
      setItems((current) =>
        current.map((item) => (item.id === id ? { ...item, open: false } : item)),
      )
      setTimeout(() => remove(id), CLEANUP_MS)
    },
    [remove],
  )

  const toast = useCallback((options: ToastOptions) => {
    counter.current += 1
    const id = `toast-${counter.current}`
    setItems((current) => [...current, { ...options, id, open: true }])
    return id
  }, [])

  const value = useMemo(() => ({ toast, dismiss: close }), [toast, close])

  return (
    <ToastContext value={value}>
      <RadixToast.Provider
        duration={DURATION_MS}
        label="Notificações ({hotkey})"
        swipeDirection="right"
      >
        {children}
        {items.map((item) => {
          const tone = item.tone ?? 'info'
          const Icon = ICONS[tone]
          return (
            <RadixToast.Root
              key={item.id}
              type="background"
              open={item.open}
              onOpenChange={(open) => {
                if (!open) close(item.id)
              }}
              className={toastVariants({ tone })}
            >
              <Icon aria-hidden className="mt-0.5 size-5 shrink-0" />
              <div className="flex min-w-0 flex-1 flex-col gap-1">
                <RadixToast.Title className="text-body font-medium">{item.title}</RadixToast.Title>
                {item.description && (
                  <RadixToast.Description className="text-body-sm">
                    {item.description}
                  </RadixToast.Description>
                )}
                {item.action && (
                  <RadixToast.Action asChild altText={item.action.altText}>
                    <Button
                      variant="secondary"
                      size="sm"
                      className="mt-1 self-start"
                      onClick={item.action.onClick}
                    >
                      {item.action.label}
                    </Button>
                  </RadixToast.Action>
                )}
              </div>
              <RadixToast.Close asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Fechar notificação"
                  className="-m-2"
                >
                  <X aria-hidden />
                </Button>
              </RadixToast.Close>
            </RadixToast.Root>
          )
        })}
        <RadixToast.Viewport
          label="Notificações ({hotkey})"
          className="fixed inset-x-4 bottom-[calc(var(--shell-bottom-offset,0px)+1rem)] z-60 m-0 flex list-none flex-col gap-3 p-0 outline-none md:inset-x-auto md:top-4 md:right-4 md:bottom-auto md:w-96"
        />
      </RadixToast.Provider>
    </ToastContext>
  )
}

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast precisa ser usado dentro de um <ToastProvider>.')
  }
  return context
}
