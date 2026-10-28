export const LOGIN_PATH = '/entrar'

// Base fictícia: só serve para o parser de URL decidir se o caminho sai da própria aplicação.
const ORIGIN = 'http://altare.invalid'

function hasForbiddenCharacter(text: string): boolean {
  return [...text].some((char) => {
    const code = char.charCodeAt(0)
    return char === '\\' || code < 0x20 || code === 0x7f
  })
}

/**
 * Para onde voltar depois de entrar. Só vale um caminho da própria aplicação: qualquer outra coisa
 * seria um redirecionamento aberto, que levaria o casal a outro site com a sessão recém-criada.
 */
export function safeDestination(raw: unknown): string | undefined {
  if (typeof raw !== 'string' || !raw.startsWith('/') || raw.startsWith('//')) return undefined
  if (hasForbiddenCharacter(raw)) return undefined
  const url = new URL(raw, ORIGIN)
  if (url.origin !== ORIGIN) return undefined
  if (url.pathname === LOGIN_PATH || url.pathname.startsWith(`${LOGIN_PATH}/`)) return undefined
  return raw
}
