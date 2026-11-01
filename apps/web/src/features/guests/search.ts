/** O que a URL de `/convidados` guarda (design-system.md §10): o núcleo aberto no painel lateral. */
export interface GuestsSearch {
  /** O id do núcleo cujo painel está aberto. */
  nucleo?: string
}

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

/**
 * Valida o que veio da URL: valor desconhecido é descartado, nunca vira erro. Fica fora da feature
 * carregada sob demanda para o roteador poder importá-lo sem trazer a tela junto. A busca por nome
 * não entra na URL: ela guardaria dado de convidado no histórico e no log de quem serve a página.
 */
export function validateGuestsSearch(search: Record<string, unknown>): GuestsSearch {
  const nucleo =
    typeof search.nucleo === 'string' && UUID.test(search.nucleo) ? search.nucleo : undefined
  return nucleo ? { nucleo } : {}
}
