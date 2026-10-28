import { useQuery } from '@tanstack/react-query'
import { ChevronUp, CircleAlert, CircleUser } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { cn } from '@/lib/cn'
import { meQueryOptions } from '../api/me'
import { useSignOut } from '../api/use-sign-out'
import { copy } from '../copy'

export interface SessionBlockProps {
  /**
   * `sidebar`: o pé da barra lateral larga, como na pág. 38 do guia; `rail`: só um ícone, no trilho
   * do tablet; `sheet`: dentro da folha "Mais" do celular, já sem o cartão ancorado.
   */
  variant: 'sidebar' | 'rail' | 'sheet'
}

/** Quem está na sessão e como sair. O guia desenha só o texto; o botão e o cartão são do D-061. */
export function SessionBlock({ variant }: SessionBlockProps) {
  const { data: user } = useQuery(meQueryOptions)
  const { signOut, isPending, hasFailed } = useSignOut()
  if (!user) return null

  const failure = (
    // A região existe sempre: um aviso que nasce já pronto não é anunciado.
    <div role="alert">
      {hasFailed && (
        <p className="flex items-start gap-1.5 text-body-sm text-attention-ink">
          <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
          {copy.session.signOutFailed}
        </p>
      )}
    </div>
  )
  const signOutButton = (
    <Button variant="secondary" loading={isPending} onClick={signOut} className="w-full">
      {copy.session.signOut}
    </Button>
  )

  if (variant === 'sheet') {
    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-3">
          <div className="flex flex-col">
            <p className="text-body-sm font-semibold text-ink">{user.profile}</p>
            <p className="text-ui-xs text-ink-muted">{copy.session.individualSession}</p>
          </div>
          <Button variant="secondary" loading={isPending} onClick={signOut}>
            {copy.session.signOut}
          </Button>
        </div>
        {failure}
      </div>
    )
  }

  const isRail = variant === 'rail'
  return (
    <Popover>
      <PopoverTrigger asChild>
        {isRail ? (
          <Button
            variant="ghost"
            size="icon"
            aria-label={`${user.profile}, ${copy.session.individualSession}`}
            className="mx-auto"
          >
            <CircleUser aria-hidden />
          </Button>
        ) : (
          <button
            type="button"
            className={cn(
              'flex w-full items-center justify-between gap-2 rounded-control px-3.5 py-2 text-left',
              'transition-colors duration-fast ease-standard hover:bg-surface-muted pointer-coarse:min-h-11',
            )}
          >
            <span className="flex flex-col">
              <span className="text-body-sm font-semibold text-ink">{user.profile}</span>
              <span className="text-ui-xs text-ink-muted">{copy.session.individualSession}</span>
            </span>
            <ChevronUp aria-hidden className="size-4 shrink-0 text-ink-subtle" />
          </button>
        )}
      </PopoverTrigger>
      <PopoverContent
        title={user.profile}
        description={copy.session.individualSession}
        side={isRail ? 'right' : 'top'}
        align={isRail ? 'end' : 'start'}
      >
        {signOutButton}
        {failure}
      </PopoverContent>
    </Popover>
  )
}
