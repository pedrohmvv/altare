import { deflateSync } from 'node:zlib'
import { expect, type Page, test } from '@playwright/test'
import credentials from './credentials.json' with { type: 'json' }
import { AREAS, goToArea, isMobile, signIn, whoIs } from './support'

// Os dois projetos dividem o banco temporário: cada um usa os seus campos e as suas frentes.
const PLANEJAMENTO = AREAS[1]
const SEM_ROLAGEM = () => document.documentElement.scrollWidth <= window.innerWidth

type Dados = {
  campo: string
  frente: string
  avaliada: string
  referencias: string
  sufixo: string
}
const DADOS = (mobile: boolean): Dados =>
  mobile
    ? { campo: 'Formato', frente: 'Vídeo', avaliada: 'Espaço', referencias: 'Trajes', sufixo: 'm' }
    : {
        campo: 'Cidade ou região',
        frente: 'Fotografia',
        avaliada: 'Buffet',
        referencias: 'Beleza (noivos)',
        sufixo: 'd',
      }

async function abrirPlanejamento(page: Page, testInfo: Parameters<typeof whoIs>[0]) {
  await signIn(page, whoIs(testInfo))
  await goToArea(page, PLANEJAMENTO, isMobile(testInfo))
}

async function abrirMapa(page: Page, testInfo: Parameters<typeof whoIs>[0]) {
  await abrirPlanejamento(page, testInfo)
  await page.getByRole('tab', { name: 'Mapa de Escopo' }).click()
  await expect(
    page.getByRole('heading', { level: 3, name: 'Cerimônia', exact: true }),
  ).toBeVisible()
}

// Pelo DOM e não pelo papel: com o painel aberto a página fica `aria-hidden` (modal).
const classificadas = async (page: Page) =>
  Number(await page.locator('[role="progressbar"]').getAttribute('aria-valuenow'))

const painel = (page: Page, nome: string) => page.getByRole('dialog', { name: nome, exact: true })
const abrirFrente = async (page: Page, nome: string) => {
  await page.getByRole('button', { name: nome, exact: true }).click()
  await expect(painel(page, nome)).toBeVisible()
}

test.describe('Planejamento: Definições Base (F-PLN-01)', () => {
  test('define, confirma a mudança de algo já definido e deixa o histórico', async ({
    page,
  }, testInfo) => {
    const { campo, sufixo } = DADOS(isMobile(testInfo))
    await abrirPlanejamento(page, testInfo)
    const linha = (texto: string) =>
      page.getByRole('button', { name: new RegExp(`^${campo}`) }).filter({ hasText: texto })

    await page.getByRole('button', { name: new RegExp(`^${campo}`) }).click()
    await page.getByRole('textbox', { name: campo, exact: true }).fill(`Valor E2E ${sufixo}`)
    await page.getByRole('radio', { name: 'Definido', exact: true }).click()
    await page.getByRole('button', { name: 'Salvar definição' }).click()
    await expect(linha(`Valor E2E ${sufixo}`)).toBeVisible()
    await expect(linha('Definido')).toBeVisible()

    // Mudar algo já definido mostra o antes e o depois e só envia ao confirmar.
    await page.getByRole('button', { name: new RegExp(`^${campo}`) }).click()
    await page.getByRole('textbox', { name: campo, exact: true }).fill(`Valor E2E ${sufixo} novo`)
    await page.getByRole('button', { name: 'Salvar definição' }).click()
    const dialogo = page.getByRole('dialog')
    await expect(dialogo.getByText('Mudar algo que vocês já definiram?')).toBeVisible()
    await expect(dialogo.getByText(`Valor E2E ${sufixo}`, { exact: true })).toBeVisible()
    await dialogo.getByRole('button', { name: 'Voltar' }).click()
    await expect(page.getByRole('textbox', { name: campo, exact: true })).toHaveValue(
      `Valor E2E ${sufixo} novo`,
    )
    await page.getByRole('button', { name: 'Salvar definição' }).click()
    await page.getByRole('button', { name: 'Confirmar mudança' }).click()
    await expect(linha(`Valor E2E ${sufixo} novo`)).toBeVisible()

    await page.getByRole('button', { name: 'Ver histórico' }).click()
    const historico = page.getByRole('dialog', { name: 'Histórico das definições' })
    await expect(historico.getByRole('listitem').filter({ hasText: campo }).first()).toBeVisible()
    await expect(historico.getByText(`Valor E2E ${sufixo} novo`).first()).toBeVisible()
  })

  test('o teto aceita R$ 28.000,00 e mostra R$ 28.000', async ({ page }, testInfo) => {
    test.skip(isMobile(testInfo), 'o teto é definido uma vez, no projeto desktop')
    await abrirPlanejamento(page, testInfo)
    await page.getByRole('button', { name: /^Teto macro/ }).click()
    await page.getByRole('textbox', { name: 'Teto macro', exact: true }).fill('28.000,00')
    await page.getByRole('radio', { name: 'Definido', exact: true }).click()
    await page.getByRole('button', { name: 'Salvar definição' }).click()
    await expect(page.getByRole('button', { name: /^Teto macro/ })).toContainText(/R\$\s28\.000/)
  })

  test('marcar Definido sem valor é bloqueado, com mensagem', async ({ page }, testInfo) => {
    await abrirPlanejamento(page, testInfo)
    await page.getByRole('button', { name: /^Tipo de cerimônia/ }).click()
    await page.getByRole('radio', { name: 'Definido', exact: true }).click()
    await page.getByRole('button', { name: 'Salvar definição' }).click()
    await expect(page.getByText(/Preencham o valor antes de marcar como Definido/)).toBeVisible()
  })

  test('cabe em 320 px, sem rolagem horizontal', async ({ page }, testInfo) => {
    await abrirPlanejamento(page, testInfo)
    await page.setViewportSize({ width: 320, height: 700 })
    expect(await page.evaluate(SEM_ROLAGEM)).toBe(true)
  })
})

test.describe('Planejamento: Mapa de Escopo (F-PLN-02 a F-PLN-05 e F-PLN-08)', () => {
  test('traz o catálogo: 8 grupos, 18 frentes e nada decidido por vocês', async ({
    page,
  }, testInfo) => {
    await abrirMapa(page, testInfo)
    await expect(page.getByRole('heading', { level: 3 })).toHaveCount(8)
    await expect(page.getByRole('progressbar')).toHaveAttribute('aria-valuemax', /^(18|19|2\d)$/)
  })

  test('classifica com motivo, reabre e vê o motivo anterior; o progresso acompanha', async ({
    page,
  }, testInfo) => {
    const { frente } = DADOS(isMobile(testInfo))
    await abrirMapa(page, testInfo)
    const antes = await classificadas(page)

    await abrirFrente(page, frente)
    const dialogo = painel(page, frente)
    await dialogo.getByRole('combobox', { name: 'Status' }).click()
    await page.getByRole('option', { name: 'Fica de fora' }).click()
    await dialogo.getByRole('button', { name: 'Confirmar: fica de fora' }).click()
    await expect(dialogo.getByText('Escrevam por que esta frente fica de fora.')).toBeVisible()
    await dialogo.getByRole('textbox', { name: /Por que fica de fora/ }).fill('fora do teto')
    await dialogo.getByRole('button', { name: 'Confirmar: fica de fora' }).click()
    await expect(
      dialogo.getByRole('region', { name: 'Status' }).getByText('Motivo: fora do teto'),
    ).toBeVisible()
    await expect.poll(() => classificadas(page)).toBe(antes + 1)

    await dialogo.getByRole('combobox', { name: 'Status' }).click()
    await page.getByRole('option', { name: 'Em discussão' }).click()
    await expect(dialogo.getByText('Motivo do descarte anterior: fora do teto')).toBeVisible()
    await expect.poll(() => classificadas(page)).toBe(antes)
    await expect(
      dialogo.getByRole('listitem').filter({ hasText: 'Fica de fora → Em discussão' }),
    ).toBeVisible()
  })

  test('o filtro mora na URL e o botão voltar o desfaz', async ({ page }, testInfo) => {
    await abrirMapa(page, testInfo)
    const chip = page.getByRole('button', { name: 'Fica de fora', exact: true })
    await chip.click()
    await expect(page).toHaveURL(/status=fora/)
    await expect(chip).toHaveAttribute('aria-pressed', 'true')
    await page.goBack()
    await expect(page).not.toHaveURL(/status=fora/)
    await expect(chip).toHaveAttribute('aria-pressed', 'false')
  })

  test('cada perfil avalia só a sua; o outro vê a divergência', async ({
    page,
    browser,
  }, testInfo) => {
    const mobile = isMobile(testInfo)
    const { avaliada } = DADOS(mobile)
    await abrirMapa(page, testInfo)
    await abrirFrente(page, avaliada)
    const meu = painel(page, avaliada)
    await meu.getByRole('button', { name: 'Quero muito' }).click()
    await meu.getByRole('textbox', { name: 'Minha nota' }).fill('adoramos')
    await meu.getByRole('button', { name: 'Salvar minha avaliação' }).click()
    await expect(meu.getByText('Avaliação salva.')).toBeVisible()

    const outroUsuario = mobile ? credentials.noivo : credentials.noiva
    const contexto = await browser.newContext({
      baseURL: testInfo.project.use.baseURL,
      locale: 'pt-BR',
      viewport: { width: 1440, height: 900 },
    })
    const outra = await contexto.newPage()
    await signIn(outra, outroUsuario)
    await goToArea(outra, PLANEJAMENTO, false)
    await outra.getByRole('tab', { name: 'Mapa de Escopo' }).click()
    await abrirFrente(outra, avaliada)
    const dela = painel(outra, avaliada)
    const doOutro = dela.getByRole('region', {
      name: new RegExp(`Avaliação d[oa] ${mobile ? 'Noiva' : 'Noivo'}`),
    })
    await expect(doOutro.getByText('Quero muito')).toBeVisible()
    await expect(doOutro.getByRole('textbox')).toHaveCount(0)
    await dela.getByRole('button', { name: 'Dispenso' }).click()
    await dela.getByRole('button', { name: 'Salvar minha avaliação' }).click()
    await expect(dela.getByText('Avaliação salva.')).toBeVisible()
    await expect(
      dela.getByText(
        'Vocês avaliaram esta frente de forma diferente. Vale conversar antes de decidir.',
      ),
    ).toBeVisible()

    // O primeiro vê a divergência na próxima leitura.
    await page.reload()
    // A categoria aberta mora na URL, então o painel volta aberto: fecha-se antes de seguir.
    await expect(painel(page, avaliada)).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(painel(page, avaliada)).toHaveCount(0)
    const cartao = page
      .getByRole('heading', { name: avaliada, exact: true })
      .locator('xpath=ancestor::li[1]')
    await expect(cartao.getByText('Divergem')).toBeVisible()
    await contexto.close()
  })

  test('nome repetido é recusado; criar, ocultar e excluir mexem no progresso', async ({
    page,
  }, testInfo) => {
    const { sufixo } = DADOS(isMobile(testInfo))
    const nome = `Frente E2E ${sufixo}`
    await abrirMapa(page, testInfo)
    // Com o painel aberto o resto da página fica `aria-hidden` (modal): a barra é lida pelo DOM.
    const total = async () =>
      Number(await page.locator('[role="progressbar"]').getAttribute('aria-valuemax'))
    const inicial = await total()

    await page.getByRole('button', { name: 'Nova categoria' }).click()
    const novo = page.getByRole('dialog', { name: 'Nova categoria' })
    await novo.getByRole('textbox', { name: 'Nome' }).fill('  fotografia ')
    await novo.getByRole('button', { name: 'Criar categoria' }).click()
    await expect(novo.getByText(/Já existe uma frente ou um grupo com este nome/)).toBeVisible()

    await novo.getByRole('textbox', { name: 'Nome' }).fill(nome)
    await novo.getByRole('textbox', { name: 'Estimativa inicial' }).fill('1.500,00')
    await novo.getByRole('button', { name: 'Criar categoria' }).click()
    await expect(page.getByRole('button', { name: nome, exact: true })).toBeVisible()
    await expect.poll(total).toBe(inicial + 1)

    await abrirFrente(page, nome)
    const dialogo = painel(page, nome)
    await dialogo.getByRole('button', { name: 'Ocultar da tela' }).click()
    await expect(dialogo.getByRole('button', { name: 'Mostrar na tela' })).toBeVisible()
    await expect.poll(total).toBe(inicial)

    await dialogo.getByRole('button', { name: 'Excluir categoria' }).click()
    await page
      .getByRole('dialog', { name: 'Excluir esta categoria?' })
      .getByRole('button', { name: 'Sim, excluir' })
      .click()
    await expect(page.getByRole('button', { name: nome, exact: true })).toHaveCount(0)
  })

  test('referências: guarda um link e uma imagem de verdade, e remove a própria', async ({
    page,
  }, testInfo) => {
    const { referencias } = DADOS(isMobile(testInfo))
    await abrirMapa(page, testInfo)
    await abrirFrente(page, referencias)
    const refs = painel(page, referencias).getByRole('region', { name: 'Referências' })

    await refs.getByRole('button', { name: 'Adicionar link' }).click()
    await refs.getByRole('textbox', { name: 'Endereço do link' }).fill('exemplo.com/mesa')
    await refs.getByRole('button', { name: 'Guardar link' }).click()
    await expect(
      refs.getByText('Cole um endereço completo, começando com http:// ou https://.'),
    ).toBeVisible()
    await refs
      .getByRole('textbox', { name: 'Endereço do link' })
      .fill('https://www.Exemplo.com/mesa')
    await refs.getByRole('textbox', { name: 'Título' }).fill('Mesa de madeira')
    await refs.getByRole('button', { name: 'Guardar link' }).click()
    const link = refs.getByRole('link', { name: /Mesa de madeira/ })
    await expect(link).toHaveAttribute('href', 'https://www.exemplo.com/mesa')
    await expect(link).toHaveAttribute('target', '_blank')
    await expect(refs.getByText('exemplo.com', { exact: true })).toBeVisible()

    await refs.getByRole('button', { name: 'Adicionar imagem' }).click()
    await refs.getByLabel('Imagem').setInputFiles({
      name: 'nao-e-imagem.png',
      mimeType: 'image/png',
      buffer: Buffer.from('isto não é uma imagem'),
    })
    await refs.getByRole('button', { name: 'Guardar imagem' }).click()
    await expect(refs.getByText(/Envie um PDF ou uma imagem JPG, PNG ou WebP/)).toBeVisible()

    await refs
      .getByLabel('Imagem')
      .setInputFiles({ name: 'salao.png', mimeType: 'image/png', buffer: PNG })
    await refs.getByRole('textbox', { name: 'Título' }).fill('Salão')
    await refs.getByRole('button', { name: 'Guardar imagem' }).click()
    const miniatura = refs.getByRole('img', { name: 'Salão' })
    await expect(miniatura).toBeVisible()
    await expect
      .poll(() => miniatura.evaluate((img: HTMLImageElement) => img.naturalWidth))
      .toBeGreaterThan(0)

    await refs.getByRole('button', { name: 'Remover Salão' }).click()
    await page
      .getByRole('dialog', { name: 'Remover esta referência?' })
      .getByRole('button', { name: 'Sim, remover' })
      .click()
    await expect(refs.getByRole('img', { name: 'Salão' })).toHaveCount(0)
  })

  test('pelo teclado: Enter abre a frente, Esc fecha e o foco volta ao cartão', async ({
    page,
  }, testInfo) => {
    const { frente } = DADOS(isMobile(testInfo))
    await abrirMapa(page, testInfo)
    const botao = page.getByRole('button', { name: frente, exact: true })
    await botao.focus()
    await page.keyboard.press('Enter')
    await expect(painel(page, frente)).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(painel(page, frente)).toHaveCount(0)
    await expect(botao).toBeFocused()
  })

  test('a lente Minha visão destaca, em texto, o que falta a minha avaliação', async ({
    page,
  }, testInfo) => {
    await abrirPlanejamento(page, testInfo)
    await page.goto('/planejamento?aba=escopo&lente=minha')
    await expect(page.getByText('Falta a sua avaliação').first()).toBeVisible()
  })

  test('na tela larga o status vira quadro de quatro colunas; no celular, lista', async ({
    page,
  }, testInfo) => {
    await abrirMapa(page, testInfo)
    await page.getByRole('radio', { name: 'Por status' }).click()
    const quadro = page.getByRole('region', { name: 'Quadro por status' })
    if (isMobile(testInfo)) {
      await expect(quadro).toHaveCount(0)
      await expect(page.getByRole('heading', { level: 3, name: 'Entra (Essencial)' })).toBeVisible()
    } else {
      await expect(quadro.getByRole('heading', { level: 3 })).toHaveCount(4)
    }
  })

  test('cabe em 320 px, com o painel aberto', async ({ page }, testInfo) => {
    const { frente } = DADOS(isMobile(testInfo))
    await abrirMapa(page, testInfo)
    await page.setViewportSize({ width: 320, height: 700 })
    expect(await page.evaluate(SEM_ROLAGEM)).toBe(true)
    await abrirFrente(page, frente)
    expect(await page.evaluate(SEM_ROLAGEM)).toBe(true)
  })
})

// Um PNG válido de 40 x 30 px, de cor sólida, montado na hora (nada é lido do disco).
const PNG = (() => {
  const crc = (data: Buffer) => {
    let c = ~0
    for (const byte of data) {
      c ^= byte
      for (let k = 0; k < 8; k++) c = c & 1 ? (c >>> 1) ^ 0xedb88320 : c >>> 1
    }
    return ~c >>> 0
  }
  const chunk = (type: string, data: Buffer) => {
    const body = Buffer.concat([Buffer.from(type), data])
    const size = Buffer.alloc(4)
    size.writeUInt32BE(data.length)
    const sum = Buffer.alloc(4)
    sum.writeUInt32BE(crc(body))
    return Buffer.concat([size, body, sum])
  }
  const [w, h] = [40, 30]
  const header = Buffer.alloc(13)
  header.writeUInt32BE(w, 0)
  header.writeUInt32BE(h, 4)
  header.set([8, 2, 0, 0, 0], 8)
  const row = Buffer.concat([Buffer.from([0]), Buffer.alloc(w * 3, 180)])
  const pixels = deflateSync(Buffer.concat(Array.from({ length: h }, () => row)))
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', header),
    chunk('IDAT', pixels),
    chunk('IEND', Buffer.alloc(0)),
  ])
})()
