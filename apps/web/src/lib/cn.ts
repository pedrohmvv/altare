import { type ClassValue, clsx } from 'clsx'
import { extendTailwindMerge } from 'tailwind-merge'
import { claro, forma, tipografia } from '../../../../docs/design/identidade-visual/tokens.json'

// Os nomes vêm do tokens.json, a mesma fonte do tokens.css, para o merge
// conhecer os utilitários do Altare sem uma segunda lista escrita à mão.
const colors = [...claro.map((c) => c.token), 'primary-ink', 'focus-ring', 'scrim']

const twMerge = extendTailwindMerge({
  extend: {
    theme: {
      color: colors,
      radius: Object.keys(forma.raios),
      shadow: Object.keys(forma.sombras),
    },
    classGroups: {
      'font-size': [{ text: tipografia.escala.map((t) => t.token) }],
    },
  },
})

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}
