import { expect, test } from '@playwright/test'
import { expectLoginPage } from './support'

test.describe('app instalável (PWA)', () => {
  test('o manifesto é servido, descreve o app e os ícones existem', async ({ page, request }) => {
    await page.goto('/entrar')
    const href = await page.locator('link[rel=manifest]').getAttribute('href')
    expect(href).toBe('/manifest.webmanifest')

    const manifest = await (await request.get('/manifest.webmanifest')).json()
    expect(manifest).toMatchObject({
      name: 'Altare',
      short_name: 'Altare',
      display: 'standalone',
      start_url: '/',
      scope: '/',
      lang: 'pt-BR',
      theme_color: '#F9F5EC',
    })
    for (const icon of manifest.icons) {
      const resposta = await request.get(icon.src)
      expect(resposta.status(), icon.src).toBe(200)
      expect(resposta.headers()['content-type']).toContain('image/png')
    }
  })

  test('o service worker é registrado, ativa e passa a controlar a página', async ({ page }) => {
    await page.goto('/entrar')
    await page.evaluate(async () => {
      await navigator.serviceWorker.ready
    })
    await page.reload()
    await expectLoginPage(page)
    expect(await page.evaluate(() => navigator.serviceWorker.controller !== null)).toBe(true)
  })

  test('a casca abre sem rede, e a API nunca é servida do cache', async ({ page, context }) => {
    await page.goto('/entrar')
    await page.evaluate(async () => {
      await navigator.serviceWorker.ready
    })
    await page.reload()
    await expectLoginPage(page)

    await context.setOffline(true)
    await page.reload()
    await expectLoginPage(page)
    // Um endereço de área, sem rede, também abre a casca (e a guarda leva à entrada).
    await page.goto('/orcamento')
    await expectLoginPage(page)
    // Sem rede, a API simplesmente não responde: nada dela foi guardado.
    await expect(
      page.evaluate(() => fetch('/api/v1/health').then((r) => r.status)),
    ).rejects.toThrow()
    await context.setOffline(false)
  })

  test('navegar até um endereço da API devolve a API, e não a casca do app', async ({ page }) => {
    await page.goto('/entrar')
    await page.evaluate(async () => {
      await navigator.serviceWorker.ready
    })
    await page.reload()

    const resposta = await page.goto('/api/v1/health')
    expect(resposta?.headers()['content-type']).toContain('application/json')
    await expect(page.locator('body')).toContainText('"status":"ok"')
  })
})
