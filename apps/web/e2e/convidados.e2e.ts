import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { expect, type Locator, type Page, type TestInfo, test } from '@playwright/test'
import credentials from './credentials.json' with { type: 'json' }
import { AREAS, goToArea, isMobile, signIn, whoIs } from './support'

// Os dois projetos dividem o banco temporário, e a lista de convidados é uma só: cada projeto
// cria os seus núcleos, com o seu sufixo, e confere os contadores só pela diferença que ele causa.
// O desktop roda primeiro, com a lista vazia, e por isso é o único a conferir o número absoluto.
const PLANEJAMENTO = AREAS[1]
const CONVIDADOS = AREAS[6]
const SEM_ROLAGEM = () => document.documentElement.scrollWidth <= window.innerWidth

type Lado = 'Noivo' | 'Noiva'

const DADOS = (mobile: boolean) => {
  const sufixo = mobile ? 'M' : 'D'
  const meu: Lado = mobile ? 'Noiva' : 'Noivo'
  const outro: Lado = mobile ? 'Noivo' : 'Noiva'
  const pessoa = (n: number) => `Convidado Exemplo ${sufixo}${n}`
  return {
    sufixo,
    meu,
    outro,
    // O núcleo do lado de quem está logado e o do outro lado.
    a: `Família Exemplo ${sufixo}`,
    b: `Grupo Exemplo ${sufixo}`,
    p1: pessoa(1),
    p2: pessoa(2),
    p3: pessoa(3),
    p4: pessoa(4),
    p5: pessoa(5),
    acompanhante: `Acompanhante Exemplo ${sufixo}`,
  }
}

const slug = (lado: Lado) => lado.toLowerCase()

async function abrirConvidados(page: Page, testInfo: TestInfo, caminho?: string) {
  await signIn(page, whoIs(testInfo))
  if (caminho) {
    await page.goto(caminho)
    await expect(
      page.getByRole('main').getByRole('heading', { level: 1, name: CONVIDADOS.title }),
    ).toBeVisible()
  } else {
    await goToArea(page, CONVIDADOS, isMobile(testInfo))
  }
}

const contadores = (page: Page) => page.getByRole('region', { name: 'Contadores da lista' })

/** O número grande de um contador, lido da lista de definições (o rótulo e o valor são irmãos). */
async function contador(page: Page, rotulo: string) {
  const termo = contadores(page).locator('dt', { hasText: rotulo })
  return Number(await termo.locator('xpath=following-sibling::dd[1]').textContent())
}

async function total(page: Page) {
  const vazio = page.getByText('Ainda sem convidados')
  // A lista carrega depois da tela: espera um dos dois estados antes de ler.
  await expect(vazio.or(contadores(page))).toBeVisible()
  if (await vazio.isVisible()) return 0
  return contador(page, 'Total nominal')
}

async function escolher(page: Page, dentro: Locator, rotulo: string, opcao: string) {
  await dentro.getByRole('combobox', { name: rotulo, exact: true }).click()
  await page.getByRole('option', { name: opcao, exact: true }).click()
}

type Pessoa = { nome: string; probabilidade?: string }

async function criarNucleo(page: Page, nome: string, lado: Lado, pessoas: Pessoa[]) {
  const [primeira, ...demais] = pessoas
  await page.getByRole('button', { name: 'Adicionar núcleo' }).first().click()
  const novo = page.getByRole('dialog', { name: 'Novo núcleo' })
  await novo.getByLabel('Nome do núcleo').fill(nome)
  await escolher(page, novo, 'Lado', lado)
  await novo.getByLabel('Nome', { exact: true }).fill(primeira.nome)
  if (primeira.probabilidade) await escolher(page, novo, 'Probabilidade', primeira.probabilidade)
  await novo.getByRole('button', { name: 'Criar núcleo' }).click()

  const sequencia = page.getByRole('dialog', { name: `Pessoas de ${nome}` })
  await expect(sequencia).toBeVisible()
  for (const pessoa of demais) {
    await sequencia.getByLabel('Nome', { exact: true }).fill(pessoa.nome)
    if (pessoa.probabilidade) {
      await escolher(page, sequencia, 'Probabilidade', pessoa.probabilidade)
    }
    await sequencia.getByRole('button', { name: 'Adicionar pessoa' }).click()
    await expect(sequencia.getByRole('status')).toHaveText(`${pessoa.nome} foi adicionada.`)
  }
  await sequencia.getByRole('button', { name: 'Concluir' }).click()
  await expect(sequencia).toBeHidden()
}

async function abrirNucleo(page: Page, nome: string) {
  await page.getByRole('button', { name: nome, exact: true }).click()
  const painel = page.getByRole('dialog', { name: nome, exact: true })
  await expect(painel).toBeVisible()
  return painel
}

async function fecharPainel(page: Page, painel: Locator) {
  // Um cartão de status que acabou de fechar ainda anima a saída e ainda recebe o Esc: espera só o
  // painel ficar aberto.
  await expect(page.getByRole('dialog')).toHaveCount(1)
  await page.keyboard.press('Escape')
  await expect(painel).toBeHidden()
}

const pessoaNoPainel = (painel: Locator, nome: string) =>
  painel.getByRole('listitem').filter({ hasText: nome }).first()

async function mudarStatus(page: Page, painel: Locator, nome: string, de: string, para: string) {
  await painel.getByRole('button', { name: `Mudar o status de ${nome}, hoje ${de}` }).click()
  const cartao = page.getByRole('dialog', { name: `Status de ${nome}` })
  await cartao.getByRole('button', { name: para, exact: true }).click()
  return cartao
}

test.describe('Convidados: a lista nominal (F-CNV-01 a F-CNV-08)', () => {
  // Cada teste continua o anterior: os núcleos nascem no primeiro e os demais os usam.
  test.describe.configure({ mode: 'serial' })

  test('monta a lista: o núcleo nasce com a primeira pessoa, as outras vêm em sequência e o nome repetido é recusado', async ({
    page,
  }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo)
    const antes = await total(page)

    await criarNucleo(page, d.a, d.meu, [
      { nome: d.p1, probabilidade: 'Certeza' },
      { nome: d.p2, probabilidade: 'Certeza' },
      { nome: d.p3 },
    ])
    await criarNucleo(page, d.b, d.outro, [{ nome: d.p4 }, { nome: d.p5, probabilidade: 'Fase 2' }])

    await expect(page.getByRole('button', { name: d.a, exact: true })).toBeVisible()
    await expect(page.getByRole('button', { name: d.b, exact: true })).toBeVisible()
    expect(await total(page)).toBe(antes + 5)

    // Maiúsculas e minúsculas não fazem outro núcleo.
    await page.getByRole('button', { name: 'Adicionar núcleo' }).first().click()
    const repetido = page.getByRole('dialog', { name: 'Novo núcleo' })
    await repetido.getByLabel('Nome do núcleo').fill(d.a.toUpperCase())
    await escolher(page, repetido, 'Lado', d.meu)
    await repetido.getByLabel('Nome', { exact: true }).fill('Convidado Exemplo Repetido')
    await repetido.getByRole('button', { name: 'Criar núcleo' }).click()
    await expect(repetido.getByText(/Já existe um núcleo com este nome/)).toBeVisible()
    await repetido.getByRole('button', { name: 'Cancelar' }).click()
    await expect(repetido).toBeHidden()
  })

  test('os contadores vêm do servidor: sem pesos o estimado pede os pesos, e 100/70/30 dá 3,7 e mostra 4', async ({
    page,
  }, testInfo) => {
    const mobile = isMobile(testInfo)
    await abrirConvidados(page, testInfo)
    if (!mobile) {
      await expect(contadores(page).getByText('Defina os pesos')).toBeVisible()
    }

    await contadores(page).getByRole('button', { name: 'Ajustar pesos e idades' }).click()
    const pesos = page.getByRole('dialog', { name: 'Pesos e idades das crianças' })
    await pesos.getByLabel('Certeza', { exact: true }).fill('100')
    await pesos.getByLabel('Provável', { exact: true }).fill('70')
    await pesos.getByLabel('Fase 2', { exact: true }).fill('30')
    await pesos.getByLabel('Criança isenta até').fill('5')
    await pesos.getByLabel('Criança pagante até').fill('12')
    await pesos.getByRole('button', { name: 'Salvar' }).click()
    await expect(pesos).toBeHidden()

    await expect(contadores(page).getByText('Defina os pesos')).toBeHidden()
    if (!mobile) {
      // 2 Certeza + 2 Provável + 1 Fase 2 = 2 + 1,4 + 0,3 = 3,7, mostrado para cima: 4 (F-CNV-06).
      expect(await contador(page, 'Estimado ponderado')).toBe(4)
      expect(await contador(page, 'Total nominal')).toBe(5)
      expect(await contador(page, 'Confirmados')).toBe(0)
    }
  })

  test('muda o status de qualquer um para qualquer outro, com motivo em Não irá, e guarda o histórico', async ({
    page,
  }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo)
    const confirmadosAntes = await contador(page, 'Confirmados')
    const naoIraoAntes = (await page.getByText(/^Não irão: \d+$/).textContent()) ?? ''

    const painel = await abrirNucleo(page, d.a)
    await mudarStatus(page, painel, d.p1, 'Rascunho', 'Confirmado')
    await expect(
      painel.getByRole('button', { name: `Mudar o status de ${d.p1}, hoje Confirmado` }),
    ).toBeVisible()

    const cartao = await mudarStatus(page, painel, d.p2, 'Rascunho', 'Não irá')
    await cartao.getByLabel('Motivo de não ir').fill('Viagem marcada')
    await cartao.getByRole('button', { name: 'Confirmar', exact: true }).click()
    await expect(
      painel.getByRole('button', { name: `Mudar o status de ${d.p2}, hoje Não irá` }),
    ).toBeVisible()
    await expect(pessoaNoPainel(painel, d.p2).getByText('Viagem marcada')).toBeVisible()

    await pessoaNoPainel(painel, d.p2).getByRole('button', { name: 'Ver histórico' }).click()
    const historico = pessoaNoPainel(painel, d.p2).getByRole('region', {
      name: 'Histórico de status',
    })
    await expect(historico.getByText('De Rascunho para Não irá')).toBeVisible()
    await expect(historico.getByText('Motivo: Viagem marcada')).toBeVisible()

    await fecharPainel(page, painel)
    expect(await contador(page, 'Confirmados')).toBe(confirmadosAntes + 1)
    await expect(page.getByText(/^Não irão: \d+$/)).not.toHaveText(naoIraoAntes)
  })

  test('o acompanhante nasce sem nome, entra na contagem e continua nela quando ganha nome', async ({
    page,
  }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo)
    const antes = await total(page)

    const painel = await abrirNucleo(page, d.a)
    await pessoaNoPainel(painel, d.p3)
      .getByRole('button', { name: 'Adicionar acompanhante' })
      .click()
    // Sem nome, a lista mostra "Acompanhante de {titular}".
    await expect(painel.getByText(`Acompanhante de ${d.p3}`).first()).toBeVisible()
    // O titular já tem o seu: o botão some.
    await expect(
      pessoaNoPainel(painel, d.p3).getByRole('button', { name: 'Adicionar acompanhante' }),
    ).toBeHidden()

    await painel.getByRole('button', { name: `Editar Acompanhante de ${d.p3}` }).click()
    const edicao = page.getByRole('dialog', { name: 'Editar pessoa' })
    await edicao.getByLabel('Nome', { exact: true }).fill(d.acompanhante)
    await edicao.getByRole('button', { name: 'Salvar pessoa' }).click()
    await expect(edicao).toBeHidden()
    await expect(pessoaNoPainel(painel, d.acompanhante)).toBeVisible()
    await expect(
      pessoaNoPainel(painel, d.acompanhante).getByText(`Acompanhante de ${d.p3}`),
    ).toBeVisible()

    await fecharPainel(page, painel)
    expect(await total(page)).toBe(antes + 1)
  })

  test('o celular vira WhatsApp, o fixo não, e a idade só sugere a faixa', async ({
    page,
  }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo)
    const painel = await abrirNucleo(page, d.a)

    await painel.getByRole('button', { name: `Editar ${d.p3}` }).click()
    const edicao = page.getByRole('dialog', { name: 'Editar pessoa' })
    await edicao.getByLabel('Telefone / WhatsApp').fill('(11) 91234-5678')
    await edicao.getByLabel('Observação').fill('=1+1')
    await escolher(page, edicao, 'Faixa', 'Criança pagante')
    await edicao.getByRole('textbox', { name: 'Idade' }).fill('4')
    await edicao.getByRole('button', { name: 'Salvar pessoa' }).click()
    await expect(edicao).toBeHidden()

    const link = painel.getByRole('link', { name: `Abrir WhatsApp de ${d.p3}` })
    await expect(link).toHaveAttribute('href', 'https://wa.me/5511912345678')

    // Com os limites de idade definidos, a idade sugere, mas a faixa só muda quando vocês aplicam.
    await expect(painel.getByText('Pela idade (4 anos): Criança isenta.')).toBeVisible()
    await expect(pessoaNoPainel(painel, d.p3).getByText(/Criança pagante · 4 anos/)).toBeVisible()
    await painel.getByRole('button', { name: `Aplicar a faixa Criança isenta a ${d.p3}` }).click()
    await expect(pessoaNoPainel(painel, d.p3).getByText(/Criança isenta · 4 anos/)).toBeVisible()

    await painel.getByRole('button', { name: `Editar ${d.p1}` }).click()
    const fixo = page.getByRole('dialog', { name: 'Editar pessoa' })
    await fixo.getByLabel('Telefone / WhatsApp').fill('(11) 3456-7890')
    await fixo.getByRole('button', { name: 'Salvar pessoa' }).click()
    await expect(fixo).toBeHidden()
    await expect(pessoaNoPainel(painel, d.p1).getByText('(11) 3456-7890')).toBeVisible()
    await expect(painel.getByRole('link', { name: `Abrir WhatsApp de ${d.p1}` })).toHaveCount(0)
  })

  test('registra o convite por núcleo e só move os rascunhos quando vocês aceitam', async ({
    page,
  }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo)

    // A.p3 está em Rascunho: a oferta aparece, e recusar mantém tudo como está.
    const painelA = await abrirNucleo(page, d.a)
    await expect(painelA.getByText('Convite ainda não enviado.')).toBeVisible()
    await painelA.getByRole('button', { name: 'Registrar convite' }).click()
    const convite = page.getByRole('dialog', { name: 'Convite do núcleo' })
    await convite.getByLabel('Data do envio').fill('2020-01-15')
    await escolher(page, convite, 'Canal', 'WhatsApp')
    await convite.getByRole('button', { name: 'Salvar envio' }).click()
    await expect(convite.getByText('Mover os rascunhos para Convidado?')).toBeVisible()
    await convite.getByRole('button', { name: 'Manter como estão' }).click()
    await expect(convite).toBeHidden()
    await expect(painelA.getByText(/Enviado em .* por WhatsApp\./)).toBeVisible()
    await expect(
      painelA.getByRole('button', { name: `Mudar o status de ${d.p3}, hoje Rascunho` }),
    ).toBeVisible()
    await fecharPainel(page, painelA)

    // O filtro "Convite não enviado" tira o núcleo que já foi convidado.
    await page.getByRole('button', { name: 'Convite não enviado', exact: true }).click()
    await expect(page).toHaveURL(/semconvite=true/)
    await expect(page.getByRole('button', { name: d.b, exact: true })).toBeVisible()
    await expect(page.getByRole('button', { name: d.a, exact: true })).toBeHidden()
    await page.getByRole('button', { name: 'Limpar filtros' }).click()
    await expect(page.getByRole('button', { name: d.a, exact: true })).toBeVisible()

    // No outro núcleo, aceitar a oferta passa os dois rascunhos a Convidado.
    const painelB = await abrirNucleo(page, d.b)
    await painelB.getByRole('button', { name: 'Registrar convite' }).click()
    const outro = page.getByRole('dialog', { name: 'Convite do núcleo' })
    await outro.getByLabel('Data do envio').fill('2020-01-16')
    await escolher(page, outro, 'Canal', 'Impresso')
    await outro.getByRole('button', { name: 'Salvar envio' }).click()
    await outro.getByRole('button', { name: 'Mover para Convidado' }).click()
    await expect(outro).toBeHidden()
    await expect(
      painelB.getByRole('button', { name: `Mudar o status de ${d.p4}, hoje Convidado` }),
    ).toBeVisible()
    await expect(
      painelB.getByRole('button', { name: `Mudar o status de ${d.p5}, hoje Convidado` }),
    ).toBeVisible()
  })

  test('os filtros moram na URL e o voltar os desfaz; a busca nunca vai para a URL', async ({
    page,
  }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo)
    const nucleo = (nome: string) => page.getByRole('button', { name: nome, exact: true })

    await page.getByRole('group', { name: 'Lado' }).getByRole('button', { name: d.meu }).click()
    await expect(page).toHaveURL(new RegExp(`lado=${slug(d.meu)}`))
    await expect(nucleo(d.a)).toBeVisible()
    await expect(nucleo(d.b)).toBeHidden()
    await page.goBack()
    await expect(page).not.toHaveURL(/lado=/)
    await expect(nucleo(d.b)).toBeVisible()

    await page.getByLabel('Buscar por nome').fill(d.p4)
    await expect(nucleo(d.b)).toBeVisible()
    await expect(nucleo(d.a)).toBeHidden()
    expect(page.url()).not.toContain('Exemplo')
    expect(page.url()).not.toContain(encodeURIComponent(d.p4))
    await page.getByRole('button', { name: 'Limpar filtros' }).click()
    await expect(nucleo(d.a)).toBeVisible()
  })

  test('Minha visão mostra o meu lado e o Comum, e o outro lado fica a um toque', async ({
    page,
  }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo, '/convidados?lente=minha')
    const nucleo = (nome: string) => page.getByRole('button', { name: nome, exact: true })

    await expect(
      page.getByText(
        `Minha visão: o lado ${d.meu === 'Noivo' ? 'do Noivo' : 'da Noiva'} e o Comum.`,
      ),
    ).toBeVisible()
    await expect(nucleo(d.a)).toBeVisible()
    await expect(nucleo(d.b)).toBeHidden()

    await page.getByRole('button', { name: 'Mostrar também o outro lado' }).click()
    await expect(nucleo(d.b)).toBeVisible()
  })

  test('o outro perfil altera o mesmo núcleo: o conflito oferece a versão mais recente e não sobrescreve', async ({
    page,
    browser,
  }, testInfo) => {
    test.skip(isMobile(testInfo), 'o conflito entre os dois perfis é provado uma vez, no desktop')
    const d = DADOS(false)
    const outroPerfil = credentials.noiva
    await abrirConvidados(page, testInfo)
    const painel = await abrirNucleo(page, d.a)
    await painel.getByRole('button', { name: 'Editar núcleo' }).click()
    const meu = page.getByRole('dialog', { name: 'Editar núcleo' })

    // Enquanto o diálogo está aberto com a versão antiga, a Noiva salva uma observação.
    const contexto = await browser.newContext({
      baseURL: testInfo.project.use.baseURL,
      locale: 'pt-BR',
      viewport: { width: 1440, height: 900 },
    })
    try {
      const dela = await contexto.newPage()
      await signIn(dela, outroPerfil)
      await goToArea(dela, CONVIDADOS, false)
      const painelDela = await abrirNucleo(dela, d.a)
      await painelDela.getByRole('button', { name: 'Editar núcleo' }).click()
      const edicaoDela = dela.getByRole('dialog', { name: 'Editar núcleo' })
      await edicaoDela.getByLabel('Observação').fill('Observação da Noiva')
      await edicaoDela.getByRole('button', { name: 'Salvar núcleo' }).click()
      await expect(edicaoDela).toBeHidden()
    } finally {
      await contexto.close()
    }

    await meu.getByLabel('Observação').fill('Observação do Noivo')
    await meu.getByRole('button', { name: 'Salvar núcleo' }).click()
    await expect(meu.getByRole('alert')).toContainText('Este registro foi alterado em outra tela')
    await meu.getByRole('button', { name: 'Ver a versão mais recente' }).click()
    await expect(meu.getByLabel('Observação')).toHaveValue('Observação da Noiva')
  })

  test('exclui o núcleo e o Desfazer o devolve com as pessoas', async ({ page }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo)
    const antes = await total(page)

    const painel = await abrirNucleo(page, d.b)
    await painel.getByRole('button', { name: 'Excluir núcleo' }).click()
    const confirmacao = page.getByRole('alertdialog', { name: `Excluir ${d.b}?` })
    await confirmacao.getByRole('button', { name: 'Excluir núcleo' }).click()
    await expect(page.getByRole('button', { name: d.b, exact: true })).toBeHidden()
    expect(await total(page)).toBe(antes - 2)

    await page.getByRole('button', { name: 'Desfazer' }).first().click()
    await expect(page.getByRole('button', { name: d.b, exact: true })).toBeVisible()
    expect(await total(page)).toBe(antes)
  })

  test('o Porte do Planejamento mostra a contagem da lista, sem copiá-la', async ({
    page,
  }, testInfo) => {
    await abrirConvidados(page, testInfo)
    const naLista = await total(page)

    await goToArea(page, PLANEJAMENTO, isMobile(testInfo))
    await expect(page.getByText(`Na lista agora: ${naLista} pessoas`)).toBeVisible()
  })

  test('exporta o que está na tela em CSV e em Excel, com a fórmula como texto', async ({
    page,
  }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo)
    await page.getByRole('group', { name: 'Lado' }).getByRole('button', { name: d.meu }).click()
    const contagem = await page.getByText(/^\d+ de \d+ pessoas$/).textContent()
    const naTela = Number(contagem?.split(' ')[0])

    await page.getByRole('button', { name: 'Exportar lista' }).click()
    const exportar = page.getByRole('dialog', { name: 'Exportar a lista' })
    await expect(exportar.getByText(`${naTela} pessoas na lista exportada.`)).toBeVisible()
    await expect(exportar.getByText(/Guardem com cuidado/)).toBeVisible()

    await exportar.getByRole('radio', { name: 'CSV' }).click()
    const [csv] = await Promise.all([
      page.waitForEvent('download'),
      exportar.getByRole('button', { name: 'Baixar arquivo' }).click(),
    ])
    expect(csv.suggestedFilename()).toMatch(/^lista-de-convidados-\d{4}-\d{2}-\d{2}\.csv$/)
    const texto = readFileSync(await csv.path(), 'utf-8')
    expect(texto.startsWith('﻿Núcleo;Lado;Nome;')).toBe(true)
    expect(texto).toContain(d.a)
    expect(texto).not.toContain(d.b)
    // Uma linha por pessoa mais o cabeçalho, e a observação "=1+1" sai como texto, com apóstrofo.
    expect(texto.split('\r\n').filter(Boolean)).toHaveLength(naTela + 1)
    expect(texto).toContain("'=1+1")
    await expect(exportar).toBeHidden()

    // O diálogo lembra o último formato; o Excel é escolhido de novo, às claras.
    await page.getByRole('button', { name: 'Exportar lista' }).click()
    const segundo = page.getByRole('dialog', { name: 'Exportar a lista' })
    await segundo.getByRole('radio', { name: 'Excel' }).click()
    const [xlsx] = await Promise.all([
      page.waitForEvent('download'),
      segundo.getByRole('button', { name: 'Baixar arquivo' }).click(),
    ])
    expect(xlsx.suggestedFilename()).toMatch(/^lista-de-convidados-\d{4}-\d{2}-\d{2}\.xlsx$/)
    const caminho = await xlsx.path()
    const lerParte = (parte: string) =>
      execFileSync('unzip', ['-p', caminho, parte], { encoding: 'utf-8' })
    // O texto "=1+1" ficou como texto na célula, e nenhuma célula da planilha é fórmula.
    const folha = lerParte('xl/worksheets/sheet1.xml')
    expect(folha).toContain('<t>=1+1</t>')
    expect(folha).not.toContain('<f>')
  })

  test('o painel abre pelo teclado, fecha com Esc e devolve o foco ao nome do núcleo', async ({
    page,
  }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo)
    const nome = page.getByRole('button', { name: d.a, exact: true })

    await nome.focus()
    await page.keyboard.press('Enter')
    const painel = page.getByRole('dialog', { name: d.a, exact: true })
    await expect(painel).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(painel).toBeHidden()
    await expect(nome).toBeFocused()
  })

  test('cabe em 320 px, sem rolagem horizontal, com o painel aberto', async ({
    page,
  }, testInfo) => {
    const d = DADOS(isMobile(testInfo))
    await abrirConvidados(page, testInfo)
    await page.setViewportSize({ width: 320, height: 700 })
    expect(await page.evaluate(SEM_ROLAGEM)).toBe(true)

    await abrirNucleo(page, d.a)
    expect(await page.evaluate(SEM_ROLAGEM)).toBe(true)
  })
})
