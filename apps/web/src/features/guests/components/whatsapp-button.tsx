import { MessageCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { copy } from '../copy'
import { isWhatsappUrl } from '../lib/names'

/**
 * "Abrir WhatsApp" em um toque (pág. 34 e 39 do guia): o link vem pronto da API e só existe para
 * celular válido. Sem ele, nada é mostrado. O nome acessível diz de quem é a conversa.
 */
export function WhatsAppButton({ url, name }: { url: string | null; name: string }) {
  if (!isWhatsappUrl(url)) return null
  return (
    <Button asChild variant="secondary" size="sm" className="relative z-10">
      <a href={url} target="_blank" rel="noopener noreferrer" aria-label={copy.whatsapp.for(name)}>
        <MessageCircle aria-hidden />
        {copy.whatsapp.label}
      </a>
    </Button>
  )
}
