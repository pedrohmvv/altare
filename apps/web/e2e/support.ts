import { expect, type Page, type TestInfo } from '@playwright/test'
import credentials from './credentials.json' with { type: 'json' }

export const PASSWORD = credentials.password

/** Cada projeto entra com um usuário só seu, para o limite de tentativas de um não pesar no outro. */
export function whoIs(testInfo: TestInfo) {
  return testInfo.project.name === 'mobile' ? credentials.noiva : credentials.noivo
}

export const isMobile = (testInfo: TestInfo) => testInfo.project.name === 'mobile'

export const AREAS = [
  { path: '/', label: 'Visão Geral', title: 'O momento de vocês', bar: 'Início' },
  { path: '/planejamento', label: 'Planejamento & Caminhos', title: 'O rumo de vocês' },
  { path: '/cronograma', label: 'Cronograma & Dependências', title: 'O que pode andar agora' },
  {
    path: '/possibilidades',
    label: 'Possibilidades & Decisões',
    title: 'Comparar propostas',
    bar: 'Possibilidades',
  },
  {
    path: '/orcamento',
    label: 'Orçamento & Simulador',
    title: 'O orçamento de vocês',
    bar: 'Orçamento',
  },
  {
    path: '/contatos',
    label: 'Contatos & Fornecedores',
    title: 'Quem vocês estão consultando',
    bar: 'Contatos',
  },
  { path: '/convidados', label: 'Convidados, Enxoval & Dia D', title: 'Quem estará com vocês' },
  { path: '/assistente', label: 'Assistente', title: 'Conversem com o assistente' },
] as const

export type Area = (typeof AREAS)[number]

export async function fillCredentials(page: Page, username: string, password: string) {
  await page.getByLabel('Usuário').fill(username)
  await page.getByLabel('Senha').fill(password)
  await page.getByRole('button', { name: 'Entrar' }).click()
}

export async function expectLoginPage(page: Page) {
  await expect(page.getByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })).toBeVisible()
}

/** Entra pela tela de entrada e espera a casca abrir. */
export async function signIn(page: Page, who: { username: string }, from = '/') {
  await page.goto(from)
  await expectLoginPage(page)
  await fillCredentials(page, who.username, PASSWORD)
  // A própria tela de entrada tem `main` e `h1`: a espera é ela sair, e não um título aparecer.
  await expect(page.getByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })).toBeHidden()
  await expect(page.getByRole('navigation', { name: /Navegação principal/ })).toBeVisible()
}

const mobileBar = (page: Page) =>
  page.getByRole('navigation', { name: 'Navegação principal (celular)' })
const sidebar = (page: Page) => page.getByRole('navigation', { name: 'Navegação principal' })

export async function openMore(page: Page) {
  await mobileBar(page).getByRole('button', { name: 'Mais' }).click()
  const sheet = page.getByRole('dialog', { name: 'Mais áreas' })
  await expect(sheet).toBeVisible()
  return sheet
}

/** Vai a uma área como o casal vai: pela barra lateral no desktop; pela barra inferior ou pela folha "Mais" no celular. */
export async function goToArea(page: Page, area: Area, mobile: boolean) {
  if (!mobile) {
    await sidebar(page).getByRole('link', { name: area.label }).click()
  } else if ('bar' in area) {
    await mobileBar(page).getByRole('link', { name: area.bar }).click()
  } else {
    const sheet = await openMore(page)
    await sheet.getByRole('link', { name: area.label }).click()
  }
  await expect(
    page.getByRole('main').getByRole('heading', { level: 1, name: area.title }),
  ).toBeVisible()
}

export async function signOut(page: Page, mobile: boolean) {
  if (mobile) {
    const sheet = await openMore(page)
    await sheet.getByRole('button', { name: 'Sair' }).click()
  } else {
    await page
      .getByRole('complementary')
      .getByRole('button', { name: /sessão individual/ })
      .click()
    await page.getByRole('dialog').getByRole('button', { name: 'Sair' }).click()
  }
  await expectLoginPage(page)
}
