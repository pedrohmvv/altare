import { expect, test } from '@playwright/test'
import { AREAS, goToArea, isMobile, openMore, signIn, whoIs } from './support'

test.describe('navegação pelas 8 áreas e pela lente', () => {
  test('cada área abre o seu título, o título do documento e cabe na largura da tela', async ({
    page,
  }, testInfo) => {
    await signIn(page, whoIs(testInfo))
    const mobile = isMobile(testInfo)

    for (const area of AREAS) {
      await goToArea(page, area, mobile)
      expect(new URL(page.url()).pathname, area.label).toBe(area.path)
      await expect(page).toHaveTitle(`${area.label} · Altare`)
      const cabe = await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      )
      expect(cabe, `${area.label} cabe na largura`).toBe(true)
    }
  })

  test('o foco vai ao título da página nova, para o leitor de tela anunciar a troca', async ({
    page,
  }, testInfo) => {
    await signIn(page, whoIs(testInfo))
    const mobile = isMobile(testInfo)

    await goToArea(page, AREAS[4], mobile)
    await expect(page.getByRole('main').getByRole('heading', { level: 1 })).toBeFocused()
  })

  test('a lente "Minha visão" fica na URL e acompanha a navegação; voltar a "Visão do Casal" a tira', async ({
    page,
  }, testInfo) => {
    await signIn(page, whoIs(testInfo))
    const mobile = isMobile(testInfo)
    const lente = () => new URL(page.url()).searchParams.get('lente')
    expect(lente()).toBeNull()

    if (mobile) {
      const sheet = await openMore(page)
      await sheet.getByRole('radio', { name: 'Minha visão' }).click()
      await page.keyboard.press('Escape')
    } else {
      await page.getByRole('radio', { name: 'Minha visão' }).click()
    }
    await expect.poll(lente).toBe('minha')

    await goToArea(page, AREAS[5], mobile)
    expect(lente()).toBe('minha')

    if (mobile) {
      const sheet = await openMore(page)
      await sheet.getByRole('radio', { name: 'Visão do Casal' }).click()
      await page.keyboard.press('Escape')
    } else {
      await page.getByRole('radio', { name: 'Visão do Casal' }).click()
    }
    await expect.poll(lente).toBeNull()
  })

  test('um caminho desconhecido, já com sessão, abre a página não encontrada dentro da casca', async ({
    page,
  }, testInfo) => {
    await signIn(page, whoIs(testInfo))

    await page.goto('/nao-existe')
    await expect(page.getByRole('heading', { name: 'Não encontramos esta página' })).toBeVisible()
    await page.getByRole('main').getByRole('link', { name: 'Ir para a Visão Geral' }).click()
    await expect(page.getByRole('heading', { level: 1, name: 'O momento de vocês' })).toBeVisible()
  })
})
