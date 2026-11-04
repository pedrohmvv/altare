import { CalendarClock } from 'lucide-react'
import type { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { copy } from '../copy'

/** O destino do link; a rota o troca por um `Link` do roteador, e a página o testa sem ele. */
export type PlanningLink = (label: string) => ReactNode

const plainLink: PlanningLink = (label) => <a href="/planejamento">{label}</a>

/**
 * O Modo Sem Data dito com calma (F-CRN-05): sem data exata não há janela calculada, e o caminho
 * para definir a data está ao lado. Vale também quando a data do casamento é só uma janela.
 */
export function NoDateBanner({ planningLink = plainLink }: { planningLink?: PlanningLink }) {
  return (
    <Card variant="muted" className="flex items-start gap-3">
      <CalendarClock aria-hidden className="mt-0.5 size-5 shrink-0 text-ink-muted" />
      <div className="flex flex-col items-start gap-1">
        <p className="text-body text-ink">{copy.banner.text}</p>
        <Button asChild variant="link" size="sm">
          {planningLink(copy.banner.link)}
        </Button>
      </div>
    </Card>
  )
}
