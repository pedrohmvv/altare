import { cva, type VariantProps } from 'class-variance-authority'
import { LoaderCircle } from 'lucide-react'
import { Slot } from 'radix-ui'
import type { ComponentProps } from 'react'
import { cn } from '@/lib/cn'

const buttonVariants = cva(
  [
    'inline-flex items-center justify-center gap-2 rounded-control font-medium whitespace-nowrap',
    'text-body transition-colors duration-fast ease-standard',
    'pointer-coarse:min-h-11 pointer-coarse:min-w-11',
    'disabled:cursor-default disabled:opacity-40 [&_svg]:size-5 [&_svg]:shrink-0',
  ],
  {
    variants: {
      variant: {
        primary: 'bg-primary text-primary-ink hover:bg-primary-hover active:bg-primary-hover',
        secondary:
          'border border-border-strong bg-surface text-ink hover:bg-surface-muted active:bg-surface-sunken',
        ghost: 'text-ink hover:bg-surface-muted active:bg-surface-sunken',
        'soft-destructive':
          'bg-attention-bg text-attention-ink hover:brightness-95 active:brightness-90',
        link: 'text-primary underline underline-offset-4 hover:text-primary-hover',
      },
      size: {
        sm: 'h-8 px-3 text-body-sm',
        md: 'h-10 px-4 max-md:h-12',
        lg: 'h-12 px-5',
        icon: 'size-10 max-md:size-12',
      },
    },
    compoundVariants: [
      { variant: 'link', className: 'h-auto min-h-0 min-w-0 px-0 pointer-coarse:min-h-0' },
    ],
    defaultVariants: { variant: 'primary', size: 'md' },
  },
)

type CommonProps = Omit<ComponentProps<'button'>, 'size'> &
  Pick<VariantProps<typeof buttonVariants>, 'variant'> & {
    /** Mostra o indicador de carregamento e bloqueia o clique (ignorado com `asChild`). */
    loading?: boolean
    /** Aplica o estilo ao único filho (por exemplo, um link) em vez de renderizar um `<button>`. */
    asChild?: boolean
  }

type IconButtonProps = CommonProps & { size: 'icon'; 'aria-label': string }
type TextButtonProps = CommonProps & { size?: 'sm' | 'md' | 'lg' }

export type ButtonProps = IconButtonProps | TextButtonProps

export function Button({
  variant,
  size,
  loading = false,
  asChild = false,
  type = 'button',
  disabled,
  className,
  children,
  ...props
}: ButtonProps) {
  const classes = cn(buttonVariants({ variant, size }), className)

  if (asChild) {
    return (
      <Slot.Root className={classes} {...props}>
        {children}
      </Slot.Root>
    )
  }

  return (
    <button
      type={type}
      className={classes}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading && <LoaderCircle aria-hidden className="animate-spin" />}
      {children}
    </button>
  )
}
