import { readFileSync, writeFileSync } from 'node:fs'
import { buildTokensCss, type Tokens } from './tokens'

const source = new URL('../../../docs/design/identidade-visual/tokens.json', import.meta.url)
const target = new URL('../src/styles/tokens.css', import.meta.url)

const tokens = JSON.parse(readFileSync(source, 'utf-8')) as Tokens
writeFileSync(target, buildTokensCss(tokens))
