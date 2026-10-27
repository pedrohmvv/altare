import { Tooltip as RadixTooltip } from 'radix-ui'
import type { ReactNode } from 'react'

export interface TooltipProps {
  /** Texto de apoio. Nunca a única fonte de uma informação crítica (design-system.md §8). */
  content: ReactNode
  /** O gatilho: um único elemento focável, que já precisa ter nome acessível. */
  children: ReactNode
  /** Atraso antes de aparecer, em ms. */
  delayDuration?: number
  side?: 'top' | 'right' | 'bottom' | 'left'
}

export function Tooltip({ content, children, delayDuration = 300, side = 'top' }: TooltipProps) {
  return (
    <RadixTooltip.Provider delayDuration={delayDuration}>
      <RadixTooltip.Root>
        <RadixTooltip.Trigger asChild>{children}</RadixTooltip.Trigger>
        <RadixTooltip.Portal>
          <RadixTooltip.Content
            side={side}
            sideOffset={6}
            className="z-50 max-w-xs rounded-control bg-ink px-2 py-1 text-body-sm text-canvas shadow-nivel-1 data-[state=closed]:animate-overlay-out data-[state=delayed-open]:animate-overlay-in data-[state=instant-open]:animate-overlay-in"
          >
            {content}
          </RadixTooltip.Content>
        </RadixTooltip.Portal>
      </RadixTooltip.Root>
    </RadixTooltip.Provider>
  )
}
