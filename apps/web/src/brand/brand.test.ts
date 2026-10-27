import { describe, expect, it } from 'vitest'
import { planBrandCopy } from '../../scripts/brand'

const FAVICON = [
  'altare-favicon.svg',
  'favicon.ico',
  'altare-favicon-16.png',
  'altare-favicon-32.png',
  'altare-favicon-48.png',
]
const APP_ICON = [
  'altare-app-icon.svg',
  'altare-app-icon-180.png',
  'altare-app-icon-192.png',
  'altare-app-icon-512.png',
]

const complete = [
  'fonte/altare-simbolo-oliva.svg',
  'fonte/altare-wordmark-marfim.svg',
  'fonte/ornamentos/arco-simples.svg',
  ...FAVICON.map((f) => `componentes/favicon/${f}`),
  ...APP_ICON.map((f) => `componentes/app-icon/${f}`),
]

const targets = (files: string[]) => planBrandCopy(files).map((c) => c.to)

describe('planBrandCopy', () => {
  it('copia os logos-mestre de fonte/ para logo/', () => {
    expect(planBrandCopy(complete)).toContainEqual({
      from: 'fonte/altare-simbolo-oliva.svg',
      to: 'logo/altare-simbolo-oliva.svg',
    })
  })

  it('copia os ornamentos para ornamentos/', () => {
    expect(planBrandCopy(complete)).toContainEqual({
      from: 'fonte/ornamentos/arco-simples.svg',
      to: 'ornamentos/arco-simples.svg',
    })
  })

  it('copia só o favicon SVG, o .ico e os PNG de 16, 32 e 48 px', () => {
    const favicon = targets(complete).filter((t) => t.startsWith('favicon/'))
    expect(favicon).toEqual(FAVICON.map((f) => `favicon/${f}`).sort())
  })

  it('copia o ícone do app em SVG e PNG de 180, 192 e 512 px', () => {
    const icon = targets(complete).filter((t) => t.startsWith('app-icon/'))
    expect(icon).toEqual(APP_ICON.map((f) => `app-icon/${f}`).sort())
  })

  it('ignora PNG de logo, o ícone de 1024 px, favicons grandes e o resto de componentes/', () => {
    const extras = [
      ...complete,
      'componentes/logo/altare-simbolo-oliva-256.png',
      'componentes/app-icon/altare-app-icon-1024.png',
      'componentes/favicon/altare-favicon-192.png',
      'componentes/favicon/altare-favicon-512.png',
      'componentes/paginas/capa.png',
      'tokens.json',
    ]
    expect(planBrandCopy(extras)).toEqual(planBrandCopy(complete))
  })

  it('devolve o plano ordenado pelo destino e igual em chamadas repetidas', () => {
    const plan = targets(complete)
    expect(plan).toEqual([...plan].sort())
    expect(planBrandCopy([...complete].reverse())).toEqual(planBrandCopy(complete))
  })

  it.each([
    ['componentes/favicon/favicon.ico'],
    ['componentes/favicon/altare-favicon.svg'],
    ['componentes/app-icon/altare-app-icon-512.png'],
  ])('falha em voz alta quando o pacote não tem %s', (missing) => {
    const without = complete.filter((f) => f !== missing)
    expect(() => planBrandCopy(without)).toThrow(missing)
  })
})
