import { defineConfig, devices } from '@playwright/test'

const API_PORT = 8105
const WEB_PORT = 4175

// O E2E usa o Chrome instalado (`channel: 'chrome'`): nenhum navegador é baixado.
export default defineConfig({
  testDir: './e2e',
  testMatch: '**/*.e2e.ts',
  // Um por vez: os dois projetos dividem o mesmo banco temporário, cada um com o seu usuário.
  workers: 1,
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: `http://127.0.0.1:${WEB_PORT}`,
    channel: 'chrome',
    locale: 'pt-BR',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } },
    },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
  ],
  webServer: [
    {
      command: 'node e2e/start-api.mjs',
      url: `http://127.0.0.1:${API_PORT}/api/v1/health`,
      env: { E2E_API_PORT: String(API_PORT) },
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      // O build de produção: é o único onde o service worker existe.
      command: `pnpm build && pnpm exec vite preview --host 127.0.0.1 --port ${WEB_PORT} --strictPort`,
      url: `http://127.0.0.1:${WEB_PORT}`,
      env: { API_ORIGIN: `http://127.0.0.1:${API_PORT}` },
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
})
