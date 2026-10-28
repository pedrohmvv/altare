import { describe, expect, it } from 'vitest'
import { LOGIN_PATH, safeDestination } from './destination'

describe('safeDestination', () => {
  it.each([
    ['/', '/'],
    ['/orcamento', '/orcamento'],
    ['/orcamento?lente=minha', '/orcamento?lente=minha'],
    ['/contatos#novo', '/contatos#novo'],
  ])('aceita o caminho da própria aplicação: %s', (entrada, saida) => {
    expect(safeDestination(entrada)).toBe(saida)
  })

  it.each([
    ['//evil.example', 'URL sem protocolo'],
    ['https://evil.example/', 'URL absoluta'],
    ['http://localhost/orcamento', 'URL absoluta mesmo na mesma origem'],
    ['javascript:alert(1)', 'esquema perigoso'],
    ['/\\evil.example', 'barra invertida'],
    ['\\\\evil.example', 'barras invertidas'],
    ['/ok\nSet-Cookie: a=b', 'caractere de controle'],
    ['/ok\u0000', 'byte nulo'],
    ['orcamento', 'sem a barra inicial'],
    ['', 'vazio'],
    [`${LOGIN_PATH}`, 'a própria tela de login'],
    [`${LOGIN_PATH}?destino=/orcamento`, 'a tela de login com parâmetro'],
  ])('recusa %s (%s)', (entrada) => {
    expect(safeDestination(entrada)).toBeUndefined()
  })

  it.each([undefined, null, 42, {}, ['/ok']])('recusa o que não é texto (%j)', (entrada) => {
    expect(safeDestination(entrada)).toBeUndefined()
  })
})
