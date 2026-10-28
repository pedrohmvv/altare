import type { VitePWAOptions } from 'vite-plugin-pwa'
import tokens from '../../../docs/design/identidade-visual/tokens.json' with { type: 'json' }

// Uma cor só, a do tokens.json: a barra do sistema e a tela de abertura do app instalado.
const THEME_COLOR = tokens.marca.app_icon.theme_color_claro

/** Os ícones de marca copiados do guia (`make brand`): um quadrado cheio, que o sistema arredonda, com o
 * versal a 40%, dentro da zona segura do ícone adaptável. */
const icon = (size: 192 | 512, purpose: 'any' | 'maskable') => ({
  src: `/brand/app-icon/altare-app-icon-${size}.png`,
  sizes: `${size}x${size}`,
  type: 'image/png',
  purpose,
})

export const manifest = {
  name: 'Altare',
  short_name: 'Altare',
  description: 'O planejamento do casamento de vocês, num lugar só.',
  lang: 'pt-BR',
  start_url: '/',
  scope: '/',
  display: 'standalone',
  theme_color: THEME_COLOR,
  background_color: THEME_COLOR,
  icons: [icon(192, 'any'), icon(512, 'any'), icon(192, 'maskable'), icon(512, 'maskable')],
} as const satisfies VitePWAOptions['manifest'] & object

export const pwaOptions = {
  // A versão nova espera em silêncio e entra na próxima abertura do app: nunca recarrega a tela
  // no meio de um formulário, e não exige nenhum aviso novo na interface (D-064).
  registerType: 'prompt',
  manifest,
  workbox: {
    // Instalável e com o app shell em cache; sem modo offline de escrita (stack.md §5).
    globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2,webmanifest}'],
    navigateFallback: '/index.html',
    // A API nunca recebe a casca no lugar da resposta, e nada dela é guardado em cache.
    navigateFallbackDenylist: [/^\/api\//],
    runtimeCaching: [],
    cleanupOutdatedCaches: true,
  },
} satisfies Partial<VitePWAOptions>
