import { Tabs as RadixTabs } from 'radix-ui'
import type { ComponentProps } from 'react'
import { cn } from '@/lib/cn'

export const Tabs = RadixTabs.Root

/** Rola na horizontal no celular; o contêiner corta o anel de foco, por isso o anel das abas é interno. */
export function TabsList({ className, ...props }: ComponentProps<typeof RadixTabs.List>) {
  return (
    <RadixTabs.List
      className={cn('flex gap-1 overflow-x-auto border-b border-border', className)}
      {...props}
    />
  )
}

export function TabsTrigger({ className, ...props }: ComponentProps<typeof RadixTabs.Trigger>) {
  return (
    <RadixTabs.Trigger
      className={cn(
        '-mb-px inline-flex min-h-10 shrink-0 items-center border-b-2 border-transparent px-4',
        'text-body font-medium whitespace-nowrap text-ink-muted pointer-coarse:min-h-11',
        'transition-colors duration-fast ease-standard hover:text-ink',
        'data-[state=active]:border-primary data-[state=active]:text-ink',
        'focus-visible:shadow-[inset_0_0_0_2px_var(--focus-gap,var(--canvas)),inset_0_0_0_4px_var(--focus-ring)]',
        className,
      )}
      {...props}
    />
  )
}

export function TabsContent({ className, ...props }: ComponentProps<typeof RadixTabs.Content>) {
  return <RadixTabs.Content className={cn('mt-4', className)} {...props} />
}
