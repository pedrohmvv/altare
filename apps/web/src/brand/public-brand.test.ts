/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { planBrandCopy } from '../../scripts/brand'
import { listFiles } from '../../scripts/files'

const source = join(import.meta.dirname, '../../../../docs/design/identidade-visual')
const target = join(import.meta.dirname, '../../public/brand')

const plan = planBrandCopy(listFiles(source))

describe('public/brand versionado', () => {
  it('tem exatamente os arquivos do plano, sem faltar nem sobrar (rode `make brand`)', () => {
    expect(listFiles(target)).toEqual(plan.map((c) => c.to))
  })

  it('tem o mesmo conteúdo do pacote de identidade (rode `make brand`)', () => {
    const different = plan.filter(
      ({ from, to }) => !readFileSync(join(source, from)).equals(readFileSync(join(target, to))),
    )
    expect(different).toEqual([])
  })
})
