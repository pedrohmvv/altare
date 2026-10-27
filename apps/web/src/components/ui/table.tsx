import type { ComponentProps } from 'react'
import { cn } from '@/lib/cn'

// A densidade e a primeira coluna fixa chegam às células pelos atributos de dados da <table>.
const CELL_SPACING =
  'px-4 py-3 group-data-[density=compact]/table:py-1.5 group-data-[density=compact]/table:text-body-sm'
const STICKY_FIRST =
  'group-data-[sticky-first]/table:first:sticky group-data-[sticky-first]/table:first:left-0'

export type TableProps = Omit<ComponentProps<'table'>, 'aria-label'> & {
  /** Nome da região rolável, anunciado pelo leitor de tela. */
  label: string
  density?: 'comfortable' | 'compact'
  /** Mantém a primeira coluna visível ao rolar na horizontal. */
  stickyFirstColumn?: boolean
  /** Classes do contêiner de rolagem; use `max-h-*` para o cabeçalho fixo valer na vertical. */
  containerClassName?: string
}

/** Rola dentro do próprio contêiner, que é focável por teclado (design-system.md §7, item 7). */
export function Table({
  label,
  density = 'comfortable',
  stickyFirstColumn = false,
  containerClassName,
  className,
  ...props
}: TableProps) {
  return (
    <section
      aria-label={label}
      // biome-ignore lint/a11y/noNoninteractiveTabindex: região rolável precisa de foco para rolar por teclado (design-system.md §7)
      tabIndex={0}
      className={cn(
        'overflow-auto rounded-card border border-border bg-surface [--focus-gap:var(--surface)]',
        containerClassName,
      )}
    >
      <table
        data-density={density}
        data-sticky-first={stickyFirstColumn || undefined}
        className={cn('group/table w-full border-collapse text-left text-body', className)}
        {...props}
      />
    </section>
  )
}

export function TableCaption({
  srOnly = false,
  className,
  ...props
}: ComponentProps<'caption'> & { srOnly?: boolean }) {
  return (
    <caption
      className={cn(
        srOnly ? 'sr-only' : 'px-4 py-3 text-left text-body-sm text-ink-muted',
        className,
      )}
      {...props}
    />
  )
}

export function TableHeader({ className, ...props }: ComponentProps<'thead'>) {
  return <thead className={cn(className)} {...props} />
}

export function TableBody({ className, ...props }: ComponentProps<'tbody'>) {
  return <tbody className={cn(className)} {...props} />
}

export function TableRow({ className, ...props }: ComponentProps<'tr'>) {
  return <tr className={cn('border-b border-border last:border-b-0', className)} {...props} />
}

/** Cabeçalho de coluna (`scope="col"`, fixo no topo) ou de linha (`scope="row"`). */
export function TableHead({
  scope = 'col',
  numeric = false,
  className,
  ...props
}: ComponentProps<'th'> & { numeric?: boolean }) {
  const isRow = scope === 'row'
  return (
    <th
      scope={scope}
      className={cn(
        CELL_SPACING,
        STICKY_FIRST,
        isRow
          ? 'bg-surface font-medium text-ink'
          : 'sticky top-0 z-10 bg-surface-muted text-eyebrow text-ink-muted normal-case tracking-normal group-data-[sticky-first]/table:first:z-20',
        numeric ? 'text-right' : 'text-left',
        className,
      )}
      {...props}
    />
  )
}

export function TableCell({
  numeric = false,
  className,
  ...props
}: ComponentProps<'td'> & { numeric?: boolean }) {
  return (
    <td
      className={cn(
        CELL_SPACING,
        STICKY_FIRST,
        'group-data-[sticky-first]/table:first:bg-surface',
        numeric && 'text-right font-mono tabular-nums',
        className,
      )}
      {...props}
    />
  )
}
