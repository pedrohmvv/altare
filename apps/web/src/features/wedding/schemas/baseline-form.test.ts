import { describe, expect, it } from 'vitest'
import type { Baseline } from '../api/baseline'
import { copy } from '../copy'
import { type FormValues, makeSchema, toFormValues, toUpdate } from './baseline-form'

const EMPTY_BASELINE: Baseline = {
  date: { status: 'Em definição', note: null, version: 1, value: { kind: 'nenhuma' } },
  city: { status: 'Em definição', note: null, version: 1, value: null },
  format: { status: 'Em definição', note: null, version: 1, value: null },
  size: { status: 'Em definição', note: null, version: 1, value: { minimum: null, maximum: null } },
  ceiling: { status: 'Em definição', note: null, version: 1, value: { cents: null } },
  ceremony: { status: 'Em definição', note: null, version: 1, value: { kinds: [], detail: null } },
}

const blank = (key: keyof Baseline = 'city') => toFormValues(key, EMPTY_BASELINE)

function errorsOf(key: keyof Baseline, values: FormValues) {
  const result = makeSchema(key).safeParse(values)
  if (result.success) return {}
  return Object.fromEntries(result.error.issues.map((issue) => [issue.path[0], issue.message]))
}

describe('formulário das definições', () => {
  it('um casamento novo abre com tudo vazio e em definição, sem dado inventado', () => {
    for (const key of ['date', 'city', 'format', 'size', 'ceiling', 'ceremony'] as const) {
      const values = blank(key)
      expect(values.status).toBe('Em definição')
      expect(values.note).toBe('')
      expect(errorsOf(key, values)).toEqual({})
    }
  })

  it.each([
    ['date', 'dateKind'],
    ['city', 'text'],
    ['format', 'text'],
    ['size', 'minimum'],
    ['ceiling', 'cents'],
    ['ceremony', 'kinds'],
  ] as const)('%s: marcar Definido sem valor é bloqueado, com mensagem acionável', (key, path) => {
    expect(errorsOf(key, { ...blank(key), status: 'Definido' })).toEqual({
      [path]: copy.errors.valueRequired,
    })
  })

  it('cidade: com valor pode ser Definida; só espaços não é valor', () => {
    expect(errorsOf('city', { ...blank(), status: 'Definido', text: 'Cidade Exemplo' })).toEqual({})
    expect(errorsOf('city', { ...blank(), status: 'Definido', text: '   ' })).toHaveProperty('text')
    expect(errorsOf('city', { ...blank(), text: 'x'.repeat(81) })).toEqual({
      text: copy.errors.textTooLong,
    })
  })

  it('nota passa de 500 caracteres: erro no campo da nota', () => {
    expect(errorsOf('city', { ...blank(), note: 'x'.repeat(501) })).toEqual({
      note: copy.errors.noteTooLong,
    })
  })

  describe('data', () => {
    const janela = (over: Partial<FormValues> = {}): FormValues => ({
      ...blank('date'),
      dateKind: 'janela',
      startMonth: '3',
      startYear: '2027',
      endMonth: '5',
      endYear: '2027',
      ...over,
    })

    it('janela completa vale, inclusive de um mês só', () => {
      expect(errorsOf('date', janela({ status: 'Definido' }))).toEqual({})
      expect(errorsOf('date', janela({ endMonth: '3' }))).toEqual({})
    })

    it('janela incompleta diz o que falta, mesmo em definição', () => {
      expect(errorsOf('date', janela({ startMonth: '', endYear: '' }))).toEqual({
        startMonth: copy.errors.month,
        endYear: copy.errors.year,
      })
    })

    it('ano fora de 2000 a 2100 ou com letras é recusado', () => {
      expect(errorsOf('date', janela({ startYear: '1999' }))).toHaveProperty('startYear')
      expect(errorsOf('date', janela({ endYear: '21x0' }))).toHaveProperty('endYear')
    })

    it('fim antes do início é recusado, atravessando o ano', () => {
      expect(errorsOf('date', janela({ endMonth: '2' }))).toEqual({
        endMonth: copy.errors.windowOrder,
      })
      expect(errorsOf('date', janela({ endYear: '2026', endMonth: '12' }))).toEqual({
        endMonth: copy.errors.windowOrder,
      })
      expect(
        errorsOf('date', janela({ startMonth: '11', endMonth: '2', endYear: '2028' })),
      ).toEqual({})
    })

    it('data exata exige a data', () => {
      const exata = { ...blank('date'), dateKind: 'exata' } as const
      expect(errorsOf('date', exata)).toEqual({ exact: copy.errors.exact })
      expect(errorsOf('date', { ...exata, exact: '2027-05-01', status: 'Definido' })).toEqual({})
    })

    it('rótulo da janela passa de 60 caracteres', () => {
      expect(errorsOf('date', janela({ dateLabel: 'x'.repeat(61) }))).toEqual({
        dateLabel: copy.errors.labelTooLong,
      })
    })
  })

  describe('porte', () => {
    const porte = (minimum: string, maximum: string) => ({ ...blank('size'), minimum, maximum })

    it('faixa válida, inclusive mínimo igual ao máximo', () => {
      expect(errorsOf('size', porte('80', '120'))).toEqual({})
      expect(errorsOf('size', porte('50', '50'))).toEqual({})
    })

    it('um lado só é recusado, e diz qual falta', () => {
      expect(errorsOf('size', porte('80', ''))).toEqual({ maximum: copy.errors.sizeBoth })
      expect(errorsOf('size', porte('', '80'))).toEqual({ minimum: copy.errors.sizeBoth })
    })

    it('faixa invertida, decimal, zero e passando do limite', () => {
      expect(errorsOf('size', porte('120', '80'))).toEqual({ minimum: copy.errors.sizeOrder })
      expect(errorsOf('size', porte('8,5', '80'))).toEqual({ minimum: copy.errors.sizeNumber })
      expect(errorsOf('size', porte('0', '80'))).toEqual({ minimum: copy.errors.sizeNumber })
      expect(errorsOf('size', porte('80', '10001'))).toEqual({ maximum: copy.errors.sizeLimit })
    })
  })

  it('teto: zero e acima do limite são recusados; vazio não é zero', () => {
    expect(errorsOf('ceiling', { ...blank('ceiling'), cents: 0 })).toEqual({
      cents: copy.errors.ceilingPositive,
    })
    expect(errorsOf('ceiling', { ...blank('ceiling'), cents: 10 ** 12 + 1 })).toEqual({
      cents: copy.errors.ceilingLimit,
    })
    expect(
      errorsOf('ceiling', { ...blank('ceiling'), cents: 2_800_000, status: 'Definido' }),
    ).toEqual({})
  })

  it('cerimônia: detalhe sem tipo é recusado', () => {
    expect(errorsOf('ceremony', { ...blank('ceremony'), detail: 'algo' })).toEqual({
      detail: copy.errors.ceremonyKindsForDetail,
    })
    expect(
      errorsOf('ceremony', { ...blank('ceremony'), kinds: ['Civil'], detail: 'algo' }),
    ).toEqual({})
  })
})

describe('toUpdate', () => {
  const versao = 7

  it('teto: R$ 28.000,00 vai como 2800000 centavos', () => {
    const update = toUpdate(
      'ceiling',
      { ...blank('ceiling'), cents: 2_800_000, status: 'Definido' },
      versao,
    )
    expect(update).toEqual({
      key: 'ceiling',
      body: { status: 'Definido', note: null, version: 7, value: { cents: 2_800_000 } },
    })
  })

  it('texto perde os espaços; em branco vira nulo; nota em branco vira nula', () => {
    expect(
      toUpdate('city', { ...blank(), text: '  Cidade Exemplo ', note: '  ' }, versao).body,
    ).toMatchObject({
      value: 'Cidade Exemplo',
      note: null,
    })
    expect(toUpdate('city', { ...blank(), text: '   ' }, versao).body).toMatchObject({
      value: null,
    })
  })

  it('data: sem data, janela e exata', () => {
    expect(toUpdate('date', blank('date'), versao).body).toMatchObject({
      value: { kind: 'nenhuma' },
    })
    expect(
      toUpdate(
        'date',
        {
          ...blank('date'),
          dateKind: 'janela',
          startMonth: '3',
          startYear: '2027',
          endMonth: '5',
          endYear: '2027',
          dateLabel: ' outono ',
        },
        versao,
      ).body,
    ).toMatchObject({
      value: {
        kind: 'janela',
        window_start: { year: 2027, month: 3 },
        window_end: { year: 2027, month: 5 },
        label: 'outono',
      },
    })
    expect(
      toUpdate('date', { ...blank('date'), dateKind: 'exata', exact: '2027-05-01' }, versao).body,
    ).toMatchObject({ value: { kind: 'exata', exact: '2027-05-01' } })
  })

  it('porte e cerimônia', () => {
    expect(
      toUpdate('size', { ...blank('size'), minimum: '80', maximum: '120' }, versao).body,
    ).toMatchObject({
      value: { minimum: 80, maximum: 120 },
    })
    expect(toUpdate('size', blank('size'), versao).body).toMatchObject({
      value: { minimum: null, maximum: null },
    })
    expect(
      toUpdate('ceremony', { ...blank('ceremony'), kinds: ['Civil'], detail: ' d ' }, versao).body,
    ).toMatchObject({ value: { kinds: ['Civil'], detail: 'd' } })
  })

  it('devolve o que a API mandou: abrir e salvar sem mexer não muda nada', () => {
    const baseline: Baseline = {
      ...EMPTY_BASELINE,
      date: {
        status: 'Definido',
        note: 'ok',
        version: 3,
        value: { kind: 'exata', exact: '2027-05-01' },
      },
      size: { status: 'Definido', note: null, version: 2, value: { minimum: 80, maximum: 120 } },
    }
    expect(toUpdate('date', toFormValues('date', baseline), 3).body).toMatchObject({
      status: 'Definido',
      note: 'ok',
      value: { kind: 'exata', exact: '2027-05-01' },
    })
    expect(toUpdate('size', toFormValues('size', baseline), 2).body).toMatchObject({
      value: { minimum: 80, maximum: 120 },
    })
  })
})
