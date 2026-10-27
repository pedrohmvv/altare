import { MessageSquareText } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { cn } from '@/lib/cn'
import { useHiddenOnScrollDown } from '@/lib/use-hidden-on-scroll-down'
import { copy } from '../copy'

/**
 * Ícone flutuante do Assistente (D-050, desenho em D-054 item 11): pílula secundária de 48 px, recolhida
 * por padrão, que só abre quando clicada. O painel é provisório; o chat é do Bloco 5.3 (D-042).
 * Quem monta decide onde ele some (a própria área Assistente) e reserva o espaço no fim do conteúdo.
 * Ao rolar para baixo ele se recolhe da vista para não cobrir o que se lê; continua na ordem de Tab
 * (e reaparece quando recebe foco), então o teclado e o leitor de tela nunca o perdem.
 */
export function AssistantLauncher() {
  const [open, setOpen] = useState(false)
  // Com o cartão aberto a pílula fica à vista: ele nasce ancorado nela.
  const hidden = useHiddenOnScrollDown() && !open

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="secondary"
          size="lg"
          data-hidden={hidden || undefined}
          className={cn(
            'fixed right-4 bottom-[calc(var(--shell-bottom-offset)+1rem)] z-30 rounded-pill shadow-nivel-1 md:right-8.5 md:bottom-6',
            'transition-[opacity,translate,background-color] duration-base ease-standard',
            'data-[hidden=true]:pointer-events-none data-[hidden=true]:translate-y-4 data-[hidden=true]:opacity-0',
            'data-[hidden=true]:focus-visible:pointer-events-auto data-[hidden=true]:focus-visible:translate-y-0 data-[hidden=true]:focus-visible:opacity-100',
          )}
        >
          <MessageSquareText aria-hidden />
          {copy.launcher.label}
        </Button>
      </PopoverTrigger>
      <PopoverContent
        title={copy.launcher.panel.title}
        description={copy.launcher.panel.description}
      />
    </Popover>
  )
}
