/// <reference types="node" />
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderRoute } from '@/test/render-route'
import { claro, tipografia } from '../../../../docs/design/identidade-visual/tokens.json'

const uiDir = join(import.meta.dirname, '../components/ui')
// `field` é o mecanismo interno de rótulo e erro (D-046), não um primitivo da vitrine.
const INTERNAL = new Set(['field'])
const primitives = readdirSync(uiDir)
  .filter((file) => file.endsWith('.tsx') && !file.endsWith('.test.tsx'))
  .map((file) => file.replace('.tsx', ''))
  .filter((name) => !INTERNAL.has(name))

const vitrineSource = ['design-system-page.tsx', 'primitives-showcase.tsx', 'tokens-showcase.tsx']
  .map((file) => readFileSync(join(import.meta.dirname, file), 'utf-8'))
  .join('\n')

// design-system.md §12 e D-028: a vitrine mostra todos os primitivos, tokens e tipografia.
describe('vitrine /design-system', () => {
  it.each(primitives)('mostra o primitivo %s', (name) => {
    expect(vitrineSource).toContain(`@/components/ui/${name}'`)
  })

  it('se apresenta como a vitrine, diz que os exemplos são fictícios e não guarda o rótulo provisório', async () => {
    await renderRoute('/design-system')

    expect(await screen.findByRole('heading', { level: 1, name: 'Design System' })).toBeVisible()
    expect(screen.getByText('Vitrine · dados de exemplo')).toBeVisible()
    expect(screen.getByText(/exemplos são fictícios/i)).toBeVisible()
    expect(screen.queryByText(/conferência/i)).not.toBeInTheDocument()
  })

  it('lista cada cor do tema claro com a sua função (guia, pág. 20)', async () => {
    await renderRoute('/design-system')
    const colors = await screen.findByRole('region', { name: 'Cores' })
    for (const color of claro) {
      expect(within(colors).getByText(color.nome)).toBeInTheDocument()
      expect(within(colors).getByText(color.funcao)).toBeInTheDocument()
    }
  })

  it('mostra cada tamanho da escala tipográfica com a sua amostra (guia, pág. 26)', async () => {
    await renderRoute('/design-system')
    const scale = await screen.findByRole('region', { name: 'Tipografia' })
    for (const step of tipografia.escala) {
      expect(within(scale).getByText(step.token)).toBeInTheDocument()
      // O nome da classe de texto tem de existir no código para o Tailwind gerá-la (nome dinâmico não é lido).
      expect(within(scale).getByText(step.amostra)).toHaveClass(`text-${step.token}`)
    }
  })

  it('mostra o seletor segmentado com uma opção desabilitada', async () => {
    await renderRoute('/design-system')
    const groups = await screen.findAllByRole('radiogroup', { name: /exemplo/i })
    expect(groups.length).toBeGreaterThan(0)
    expect(screen.getByRole('radio', { name: 'Indisponível' })).toBeDisabled()
  })
})
