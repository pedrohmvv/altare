/// <reference types="node" />
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderRoute } from '@/test/render-route'

const publicDir = join(import.meta.dirname, '../../public')

const region = (name: string) => screen.findByRole('region', { name })
const open = async () => {
  await renderRoute('/design-system')
  await screen.findByRole('heading', { level: 1, name: 'Design System' })
}

// Catálogo da identidade (D-058): as páginas 12, 30, 31, 33, 36 e 42 do guia, em formato de catálogo.
describe('catálogo de identidade na vitrine', () => {
  it('Arranjos da marca mostra os quatro arranjos, com o arquivo de cada um, e avisa que não há lockup horizontal (guia, pág. 12)', async () => {
    await open()
    const section = await region('Arranjos da marca')

    const arranjos = [
      ['Wordmark', 'altare-wordmark-<cor>.svg'],
      ['Símbolo', 'altare-simbolo-<cor>.svg'],
      ['Vertical', 'altare-vertical-<cor>.svg'],
      ['Assinatura formal', 'altare-assinatura-<cor>.svg'],
    ] as const
    for (const [name, file] of arranjos) {
      expect(within(section).getByRole('heading', { level: 3, name })).toBeVisible()
      expect(within(section).getByText(file)).toBeVisible()
    }
    expect(within(section).getAllByRole('img')).toHaveLength(4)
    expect(within(section).getByText(/Não existe lockup horizontal/)).toBeVisible()
  })

  it('Arco mostra os três arcos com as regras de proporção, traço e cor lidas do tokens.json (guia, pág. 30)', async () => {
    await open()
    const section = await region('Arco')

    for (const name of ['Arco simples', 'Arco duplo', 'Arcada']) {
      expect(within(section).getByRole('heading', { level: 3, name })).toBeVisible()
    }
    expect(within(section).getAllByRole('img')).toHaveLength(3)
    expect(within(section).getByText(/1 : 1,4/)).toBeVisible()
    expect(within(section).getByText(/1,25 px, sem preenchimento/)).toBeVisible()
    expect(within(section).getByText(/Musgo #5C6158 a 70%/)).toBeVisible()
    expect(within(section).getByText(/arquitetura, não religião/)).toBeVisible()
  })

  it('Ramo de oliveira mostra os três ramos com as regras de desenho, cor e limite (guia, pág. 31)', async () => {
    await open()
    const section = await region('Ramo de oliveira')

    for (const name of ['Ramo grande', 'Ramo pequeno', 'Faixa de ramos']) {
      expect(within(section).getByRole('heading', { level: 3, name })).toBeVisible()
    }
    expect(within(section).getAllByRole('img')).toHaveLength(3)
    expect(within(section).getByText(/haste em curva, folhas alternadas/)).toBeVisible()
    expect(within(section).getByText(/nunca verde vivo/)).toBeVisible()
    expect(within(section).getByText(/um ornamento por tela, nunca atrás da marca/)).toBeVisible()
  })

  it('Ícones com significado fixo mostra os 12 ícones com nome e nome no Lucide, e os tamanhos 16, 20 e 24 (guia, pág. 33)', async () => {
    await open()
    const section = await region('Ícones com significado fixo')

    const icons = [
      ['Consenso favorito', 'heart-handshake'],
      ['Conversar juntos', 'messages-square'],
      ['Atenção · custo extra', 'circle-alert'],
      ['Destravado', 'lock-open'],
      ['Bloqueado', 'lock'],
      ['Pago · concluído', 'circle-check'],
      ['Próximo passo', 'circle-arrow-right'],
      ['Abrir WhatsApp', 'message-circle'],
      ['Anexo', 'paperclip'],
      ['PDF', 'file-text'],
      ['Orçamento oficial', 'badge-check'],
      ['Alternativa sem coração', 'handshake'],
    ] as const
    for (const [name, lucide] of icons) {
      expect(within(section).getByText(name)).toBeVisible()
      expect(within(section).getByText(lucide)).toBeVisible()
    }
    for (const size of ['16 px', '20 px', '24 px']) {
      expect(within(section).getByText(size)).toBeVisible()
    }
    expect(within(section).getByText(/cor e ícone nunca são o único sinal/)).toBeVisible()
  })

  it('Favicon e ícone do app mostra o favicon nos cinco tamanhos, os arquivos e o ícone do app, com os percentuais do tokens.json (guia, pág. 36)', async () => {
    await open()
    const section = await region('Favicon e ícone do app')

    for (const size of ['16', '32', '48', '64', '96']) {
      expect(within(section).getByText(size)).toBeVisible()
    }
    expect(within(section).getByText(/versal de 43% do lado/)).toBeVisible()
    expect(within(section).getByText(/raio de 22%/i)).toBeVisible()
    expect(within(section).getByText(/versal = 40% do lado/i)).toBeVisible()
    expect(within(section).getByText(/quadrado cheio; o sistema arredonda/i)).toBeVisible()
    expect(within(section).getByText(/altare-app-icon\.svg/)).toBeVisible()
  })

  it('Dossiê do Dia D mostra as peças reais e as seis regras de impressão, sem montar o documento (guia, pág. 42)', async () => {
    await open()
    const section = await region('Dossiê do Dia D')

    const rules = within(section).getAllByRole('listitem')
    expect(rules).toHaveLength(6)
    expect(within(section).getByText('Papel branco, sem fundo')).toBeVisible()
    expect(within(section).getByText('Campos vazios explícitos')).toBeVisible()
    // As peças são as da marca; o documento em si é do Bloco 4.2 (D-028).
    expect(within(section).getAllByRole('img').length).toBeGreaterThanOrEqual(2)
    expect(within(section).getByText(/nasce no Bloco 4\.2/)).toBeVisible()
    expect(within(section).queryByText('[a definir]')).not.toBeInTheDocument()
  })

  it('todo ativo de marca mostrado existe em public/brand', async () => {
    await open()
    const main = screen.getByRole('main')

    const sources = [...main.querySelectorAll('img')]
      .map((img) => img.getAttribute('src') ?? '')
      .filter((src) => src.startsWith('/brand/'))
    expect(sources.length).toBeGreaterThanOrEqual(20)
    for (const src of sources) {
      expect(existsSync(join(publicDir, src)), src).toBe(true)
    }
  })

  it('toda imagem do catálogo tem texto alternativo', async () => {
    await open()
    for (const img of screen.getByRole('main').querySelectorAll('img')) {
      expect(img.getAttribute('alt'), img.getAttribute('src') ?? '').not.toBeNull()
    }
  })
})

describe('índice da vitrine', () => {
  it('lista toda seção da página, na ordem, e cada link leva ao título da seção', async () => {
    await open()
    const nav = screen.getByRole('navigation', { name: 'Índice da vitrine' })
    const links = within(nav).getAllByRole('link')
    const sections = [...screen.getByRole('main').querySelectorAll('section[aria-labelledby]')]

    expect(links).toHaveLength(sections.length)
    links.forEach((link, i) => {
      const target = document.getElementById((link.getAttribute('href') ?? '').slice(1))
      expect(target, link.textContent ?? '').not.toBeNull()
      expect(target?.textContent).toBe(link.textContent)
      expect(sections[i]?.getAttribute('aria-labelledby')).toBe(target?.id)
    })
  })

  it('separa as duas partes, Identidade e Componentes', async () => {
    await open()
    const nav = screen.getByRole('navigation', { name: 'Índice da vitrine' })

    expect(within(nav).getByText('Identidade')).toBeVisible()
    expect(within(nav).getByText('Componentes')).toBeVisible()
    expect(within(nav).getByRole('link', { name: 'Cores' })).toBeVisible()
    expect(within(nav).getByRole('link', { name: 'Botões' })).toBeVisible()
  })
})
