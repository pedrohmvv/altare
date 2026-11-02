/** O que a URL de `/cronograma` guarda: o marco aberto no painel lateral (design-system §10). */
export interface ScheduleSearch {
  /** O id do marco aberto no painel lateral. */
  marco?: string
}

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

/**
 * Valor desconhecido é descartado: um link velho ou editado à mão nunca quebra a página. Fica fora
 * da feature carregada sob demanda para o roteador poder importá-lo sem trazer a tela junto.
 */
export function validateScheduleSearch(search: Record<string, unknown>): ScheduleSearch {
  const result: ScheduleSearch = {}
  if (typeof search.marco === 'string' && UUID.test(search.marco)) result.marco = search.marco
  return result
}
