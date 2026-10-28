import { fileURLToPath } from 'node:url'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import { defineConfig } from 'vitest/config'
import { pwaOptions } from './scripts/pwa-manifest.ts'

// Onde a API escuta; o E2E sobe a dele numa porta própria.
const apiOrigin = process.env.API_ORIGIN ?? 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react(), tailwindcss(), VitePWA(pwaOptions)],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    proxy: { '/api': apiOrigin },
  },
  // O `vite preview` serve o build de produção, o único onde o service worker existe.
  preview: {
    proxy: { '/api': apiOrigin },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: false,
  },
})
