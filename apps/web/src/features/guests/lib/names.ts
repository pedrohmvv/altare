import type { Guest } from '../api/guests'
import { copy } from '../copy'

/** O nome que a lista mostra: o do convidado ou, no +1 ainda sem nome, "Acompanhante de {titular}". */
export function displayName(guest: Pick<Guest, 'name' | 'holder_name'>): string {
  if (guest.name) return guest.name
  return guest.holder_name ? copy.companion.of(guest.holder_name) : copy.companion.unnamed
}

/** Só um link do WhatsApp vindo da API vira `<a>`, mesmo que o banco um dia traga outra coisa. */
export function isWhatsappUrl(url: string | null): url is string {
  return url !== null && /^https:\/\/wa\.me\/55\d{10,11}$/.test(url)
}
