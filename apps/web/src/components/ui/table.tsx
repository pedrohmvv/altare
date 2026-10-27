import { type ComponentProps, createContext, useContext } from 'react'
import { cn } from '@/lib/cn'

type Density = 'comfortable' | 'compact'

interface TableContextValue {
  density: Density
  stickyFirstColumn: boolean
}

// A densidade e a primeira coluna fixa chegam às células por contexto, não por variantes de grupo:
// as classes de texto do Altare definem família e peso, e uma variante as sobrescreveria.
const TableContext = createContext<TableContextValue>({
  density: 'comfortable',
  stickyFirstColumn: false,
})

export type TableProps = Omit<ComponentProps<'table'>, 'aria-label'> & {
  /** Nome da região rolável, anunciado pelo leitor de tela. */
  label: string
  density?: Density
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
    <TableContext value={{ density, stickyFirstColumn }}>
      <section
        aria-label={label}
        // biome-ignore lint/a11y/noNoninteractiveTabindex: região rolável precisa de foco para rolar por teclado (design-system.md §7)
        tabIndex={0}
        className={cn(
          'overflow-auto rounded-card border border-border bg-surface [--focus-gap:var(--surface)]',
          containerClassName,
        )}
      >
        <table className={cn('w-full border-collapse text-left', className)} {...props} />
      </section>
    </TableContext>
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

const padding = (density: Density) => (density === 'compact' ? 'px-4 py-1.5' : 'px-4 py-3')

/** Cabeçalho de coluna (`scope="col"`, fixo no topo) ou de linha (`scope="row"`). */
export function TableHead({
  scope = 'col',
  numeric = false,
  className,
  ...props
}: ComponentProps<'th'> & { numeric?: boolean }) {
  const { density, stickyFirstColumn } = useContext(TableContext)
  const isRow = scope === 'row'
  return (
    <th
      scope={scope}
      className={cn(
        padding(density),
        stickyFirstColumn && 'first:sticky first:left-0',
        isRow
          ? [
              'bg-surface font-medium text-ink',
              density === 'compact' ? 'text-body-sm' : 'text-body',
            ]
          : [
              'sticky top-0 z-10 bg-surface-muted text-eyebrow text-ink-muted normal-case tracking-normal',
              stickyFirstColumn && 'first:z-20',
            ],
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
  const { density, stickyFirstColumn } = useContext(TableContext)
  const compact = density === 'compact'
  return (
    <td
      className={cn(
        padding(density),
        stickyFirstColumn && 'first:sticky first:left-0 first:bg-surface',
        numeric
          ? ['text-right', compact ? 'text-num-sm' : 'text-num']
          : compact
            ? 'text-body-sm'
            : 'text-body',
        className,
      )}
      {...props}
    />
  )
}
