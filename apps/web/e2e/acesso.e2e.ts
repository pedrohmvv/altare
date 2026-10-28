import { expect, test } from '@playwright/test'
import {
  AREAS,
  expectLoginPage,
  fillCredentials,
  goToArea,
  isMobile,
  PASSWORD,
  signIn,
  signOut,
  whoIs,
} from './support'

test.describe('entrada e sessão', () => {
  test('sem sessão, uma área leva à entrada e guarda o destino com a lente', async ({ page }) => {
    await page.goto('/orcamento?lente=minha')

    await expectLoginPage(page)
    await expect(page).toHaveTitle('Entrar · Altare')
    expect(new URL(page.url()).pathname).toBe('/entrar')
    expect(new URL(page.url()).searchParams.get('destino')).toBe('/orcamento?lente=minha')
  })

  test('um destino de outro site é ignorado', async ({ page }) => {
    await page.goto('/entrar?destino=https://evil.example/')

    await expectLoginPage(page)
    expect(new URL(page.url()).searchParams.has('destino')).toBe(false)
  })

  test('senha errada avisa com calma, guarda o usuário e devolve o foco à senha vazia', async ({
    page,
  }, testInfo) => {
    const quem = whoIs(testInfo)
    await page.goto('/entrar')
    await fillCredentials(page, quem.username, 'senha-errada-12345')

    await expect(page.getByRole('alert')).toContainText('Confira o usuário e a senha')
    await expect(page.getByLabel('Usuário')).toHaveValue(quem.username)
    await expect(page.getByLabel('Senha')).toHaveValue('')
    await expect(page.getByLabel('Senha')).toBeFocused()
    await expectLoginPage(page)
  })

  test('entrar leva ao destino com a lente, e a sessão sobrevive a recarregar', async ({
    page,
  }, testInfo) => {
    await page.goto('/orcamento?lente=minha')
    await expectLoginPage(page)
    await fillCredentials(page, whoIs(testInfo).username, PASSWORD)

    await expect(
      page.getByRole('heading', { level: 1, name: 'O orçamento de vocês' }),
    ).toBeVisible()
    expect(new URL(page.url()).pathname).toBe('/orcamento')
    expect(new URL(page.url()).searchParams.get('lente')).toBe('minha')

    await page.reload()
    await expect(
      page.getByRole('heading', { level: 1, name: 'O orçamento de vocês' }),
    ).toBeVisible()
  })

  test('quem já entrou e abre a entrada vai direto para a Visão Geral', async ({
    page,
  }, testInfo) => {
    await signIn(page, whoIs(testInfo))
    await page.goto('/entrar')

    await expect(page.getByRole('heading', { level: 1, name: 'O momento de vocês' })).toBeVisible()
    expect(new URL(page.url()).pathname).toBe('/')
  })

  test('sair encerra a sessão: voltar a uma área leva de novo à entrada', async ({
    page,
  }, testInfo) => {
    await signIn(page, whoIs(testInfo))

    await signOut(page, isMobile(testInfo))
    expect(new URL(page.url()).pathname).toBe('/entrar')

    await page.goto('/contatos')
    await expectLoginPage(page)
    expect(new URL(page.url()).searchParams.get('destino')).toBe('/contatos')
  })

  test('mostra o perfil de quem entrou, e não o usuário', async ({ page }, testInfo) => {
    await signIn(page, whoIs(testInfo))
    const perfil = whoIs(testInfo).profile

    if (isMobile(testInfo)) {
      await page
        .getByRole('navigation', { name: 'Navegação principal (celular)' })
        .getByRole('button', { name: 'Mais' })
        .click()
      await expect(page.getByRole('dialog', { name: 'Mais áreas' })).toContainText(perfil)
    } else {
      await expect(page.getByRole('complementary')).toContainText(perfil)
      await expect(page.getByRole('complementary')).toContainText('sessão individual')
    }
  })

  test('a casca existe só depois de entrar: a próxima área abre sem pedir a senha de novo', async ({
    page,
  }, testInfo) => {
    await signIn(page, whoIs(testInfo))
    const area = AREAS[5]
    await goToArea(page, area, isMobile(testInfo))
    expect(new URL(page.url()).pathname).toBe(area.path)
  })
})
