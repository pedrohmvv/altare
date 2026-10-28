/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { checkDesignRules, type Sources } from '../scripts/design-rules'
import { listFiles } from '../scripts/files'

const rules = (sources: Sources) => checkDesignRules(sources).map((v) => v.rule)
const file = (code: string): Sources => ({ 'src/components/ui/exemplo.tsx': code })

// design-system.md §12 e D-055: valor de marca só entra por token. Componente usa classe de token
// (`bg-surface`, `text-ink`, `text-ui`); `#RRGGBB` e valor solto de cor ou de fonte ficam de fora.
describe('regras de design em src (D-055)', () => {
  it('barra cor em hex', () => {
    expect(rules(file(`<div className="x" style={{ color: '#F9F5EC' }} />`))).toContain('sem-hex')
    expect(rules(file(`const c = "#fff"`))).toContain('sem-hex')
    expect(rules(file(`const c = "#3A4B3C80"`))).toContain('sem-hex')
  })

  it('não confunde âncora e identificador com hex', () => {
    expect(rules(file(`<a href="#conteudo">Ir</a>`))).toEqual([])
    expect(rules(file(`<h2 id="conf-botoes">Botões</h2>`))).toEqual([])
    expect(rules(file(`<a href="#conf-selos" />`))).toEqual([])
  })

  it('barra função de cor literal', () => {
    expect(rules(file(`const s = 'rgb(35 42 34 / .45)'`))).toContain('sem-cor-funcional')
    expect(rules(file(`const s = "hsl(120 20% 20%)"`))).toContain('sem-cor-funcional')
    expect(rules(file(`const s = "oklch(0.5 0.1 120)"`))).toContain('sem-cor-funcional')
  })

  it.each([
    'bg-[#3A4B3C]',
    'text-[15px]',
    'text-[#232A22]',
    'font-[600]',
    'font-[Georgia]',
    'border-[#8F846F]',
    'leading-[1.2]',
    'tracking-[0.1em]',
    'shadow-[0_4px_16px_rgb(0,0,0,.1)]',
    'md:text-[15px]',
    'hover:bg-[#fff]',
  ])('barra a classe arbitrária %s', (cls) => {
    expect(rules(file(`<div className="flex ${cls}" />`))).toContain('classe-arbitraria-sem-token')
  })

  it.each([
    'bg-surface',
    'text-ui',
    'text-ui-sm',
    'font-semibold',
    'border-border-strong',
    'min-w-[36rem]',
    'max-w-[75rem]',
    'md:grid-cols-[4.5rem_minmax(0,1fr)]',
    'pb-[calc(var(--shell-bottom-offset)+2rem)]',
    'max-h-[85dvh]',
    'data-[state=active]:font-semibold',
    'group-data-[status=active]:text-primary',
    'has-[input:focus-visible]:shadow-[0_0_0_2px_var(--focus-gap,var(--canvas)),0_0_0_4px_var(--focus-ring)]',
    'text-[length:var(--tamanho)]',
  ])('deixa passar %s', (cls) => {
    expect(rules(file(`<div className="flex ${cls}" />`))).toEqual([])
  })

  it('barra valor solto de cor ou de fonte no style, mas aceita var(--token)', () => {
    expect(rules(file(`<i style={{ backgroundColor: 'tomato' }} />`))).toContain(
      'style-com-valor-solto',
    )
    expect(rules(file(`<i style={{ fontSize: '15px' }} />`))).toContain('style-com-valor-solto')
    expect(rules(file(`<i style={{ fontFamily: 'Georgia' }} />`))).toContain(
      'style-com-valor-solto',
    )
    expect(rules(file('<i style={{ backgroundColor: `var(--surface)` }} />'))).toEqual([])
    expect(rules(file(`<i style={{ color: 'var(--ink)' }} />`))).toEqual([])
  })

  it('aponta o arquivo e o trecho encontrado', () => {
    expect(checkDesignRules({ 'src/app/a.tsx': `const c = "#F9F5EC"` })).toEqual([
      { rule: 'sem-hex', file: 'src/app/a.tsx', found: '#F9F5EC' },
    ])
  })

  it('o código de src usa só tokens', () => {
    const srcDir = join(import.meta.dirname)
    const sources: Sources = {}
    for (const entry of listFiles(srcDir)) {
      // Os tipos do OpenAPI são saída de máquina (make api-types), não código escrito à mão.
      const generated = /\.d\.ts$/.test(entry)
      if (
        !/\.tsx?$/.test(entry) ||
        /\.test\.tsx?$/.test(entry) ||
        generated ||
        entry.startsWith('test/')
      )
        continue
      sources[`src/${entry}`] = readFileSync(join(srcDir, entry), 'utf-8')
    }

    expect(Object.keys(sources).length).toBeGreaterThan(50)
    expect(checkDesignRules(sources)).toEqual([])
  })
})
