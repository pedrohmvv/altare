import { z } from 'zod'
import type { components } from '@/lib/api/schema'
import type { Baseline, BaselineKey } from '../api/baseline'
import { copy } from '../copy'

type Schemas = components['schemas']

const STATUSES = ['Em definição', 'Definido'] as const
const DATE_KINDS = ['nenhuma', 'janela', 'exata'] as const
const CEREMONY_KINDS = ['Religiosa', 'Civil', 'Simbólica'] as const

const MIN_YEAR = 2000
const MAX_YEAR = 2100
const MAX_NOTE = 500
const MAX_TEXT = 80
const MAX_LABEL = 60
const MAX_DETAIL = 200
const MAX_GUESTS = 10_000
const MAX_CEILING_CENTS = 10 ** 12

/** Um formulário só para as seis definições: cada chave usa a sua parte e ignora as outras. */
const formShape = z.object({
  status: z.enum(STATUSES),
  note: z.string(),
  dateKind: z.enum(DATE_KINDS),
  startMonth: z.string(),
  startYear: z.string(),
  endMonth: z.string(),
  endYear: z.string(),
  dateLabel: z.string(),
  exact: z.string(),
  text: z.string(),
  minimum: z.string(),
  maximum: z.string(),
  cents: z.number().nullable(),
  kinds: z.array(z.enum(CEREMONY_KINDS)),
  detail: z.string(),
})

export type FormValues = z.infer<typeof formShape>

type Path = keyof FormValues
type Report = (path: Path, message: string) => void

const isYear = (text: string) => /^\d{4}$/.test(text) && +text >= MIN_YEAR && +text <= MAX_YEAR

function checkMonthYear(
  report: Report,
  month: string,
  year: string,
  paths: { month: Path; year: Path },
) {
  if (month === '') report(paths.month, copy.errors.month)
  if (!isYear(year.trim())) report(paths.year, copy.errors.year)
}

function checkDate(v: FormValues, report: Report) {
  if (v.dateKind === 'janela') {
    checkMonthYear(report, v.startMonth, v.startYear.trim(), {
      month: 'startMonth',
      year: 'startYear',
    })
    checkMonthYear(report, v.endMonth, v.endYear.trim(), { month: 'endMonth', year: 'endYear' })
    const complete =
      [v.startMonth, v.endMonth].every(Boolean) && [v.startYear, v.endYear].every(isYear)
    if (complete && +v.endYear * 12 + +v.endMonth < +v.startYear * 12 + +v.startMonth) {
      report('endMonth', copy.errors.windowOrder)
    }
    if (v.dateLabel.trim().length > MAX_LABEL) report('dateLabel', copy.errors.labelTooLong)
  }
  if (v.dateKind === 'exata' && !/^\d{4}-\d{2}-\d{2}$/.test(v.exact)) {
    report('exact', copy.errors.exact)
  }
}

function checkSize(v: FormValues, report: Report) {
  const minimum = v.minimum.trim()
  const maximum = v.maximum.trim()
  if (minimum === '' && maximum === '') return
  if (minimum === '' || maximum === '') {
    report(minimum === '' ? 'minimum' : 'maximum', copy.errors.sizeBoth)
    return
  }
  const isCount = (text: string) => /^\d+$/.test(text) && +text >= 1
  if (!isCount(minimum)) report('minimum', copy.errors.sizeNumber)
  if (!isCount(maximum)) report('maximum', copy.errors.sizeNumber)
  if (!(isCount(minimum) && isCount(maximum))) return
  if (+maximum > MAX_GUESTS) report('maximum', copy.errors.sizeLimit)
  else if (+minimum > +maximum) report('minimum', copy.errors.sizeOrder)
}

function checkCeiling(v: FormValues, report: Report) {
  if (v.cents === null) return
  if (v.cents <= 0) report('cents', copy.errors.ceilingPositive)
  else if (v.cents > MAX_CEILING_CENTS) report('cents', copy.errors.ceilingLimit)
}

function checkCeremony(v: FormValues, report: Report) {
  if (v.kinds.length === 0 && v.detail.trim() !== '') {
    report('detail', copy.errors.ceremonyKindsForDetail)
  }
  if (v.detail.trim().length > MAX_DETAIL) report('detail', copy.errors.detailTooLong)
}

/** Onde aparece o aviso de "falta o valor": o primeiro controle da definição. */
const VALUE_PATH: Record<BaselineKey, Path> = {
  date: 'dateKind',
  city: 'text',
  format: 'text',
  size: 'minimum',
  ceiling: 'cents',
  ceremony: 'kinds',
}

export function hasValue(key: BaselineKey, v: FormValues): boolean {
  switch (key) {
    case 'date':
      return v.dateKind !== 'nenhuma'
    case 'city':
    case 'format':
      return v.text.trim() !== ''
    case 'size':
      return v.minimum.trim() !== '' || v.maximum.trim() !== ''
    case 'ceiling':
      return v.cents !== null
    case 'ceremony':
      return v.kinds.length > 0
  }
}

/** A mesma regra que a API aplica (F-PLN-01): serve para avisar cedo, o servidor decide. */
export function makeSchema(key: BaselineKey) {
  return formShape.superRefine((v, ctx) => {
    const report: Report = (path, message) =>
      ctx.addIssue({ code: 'custom', path: [path], message })
    if (v.note.trim().length > MAX_NOTE) report('note', copy.errors.noteTooLong)
    if ((key === 'city' || key === 'format') && v.text.trim().length > MAX_TEXT) {
      report('text', copy.errors.textTooLong)
    }
    if (key === 'date') checkDate(v, report)
    if (key === 'size') checkSize(v, report)
    if (key === 'ceiling') checkCeiling(v, report)
    if (key === 'ceremony') checkCeremony(v, report)
    if (v.status === 'Definido' && !hasValue(key, v))
      report(VALUE_PATH[key], copy.errors.valueRequired)
  })
}

const EMPTY: FormValues = {
  status: 'Em definição',
  note: '',
  dateKind: 'nenhuma',
  startMonth: '',
  startYear: '',
  endMonth: '',
  endYear: '',
  dateLabel: '',
  exact: '',
  text: '',
  minimum: '',
  maximum: '',
  cents: null,
  kinds: [],
  detail: '',
}

export function toFormValues(key: BaselineKey, baseline: Baseline): FormValues {
  const field = baseline[key]
  const base = { ...EMPTY, status: field.status, note: field.note ?? '' }
  switch (key) {
    case 'date': {
      const { kind, window_start, window_end, label, exact } = baseline.date.value
      return {
        ...base,
        dateKind: kind,
        startMonth: window_start ? String(window_start.month) : '',
        startYear: window_start ? String(window_start.year) : '',
        endMonth: window_end ? String(window_end.month) : '',
        endYear: window_end ? String(window_end.year) : '',
        dateLabel: label ?? '',
        exact: exact ?? '',
      }
    }
    case 'city':
    case 'format':
      return { ...base, text: baseline[key].value ?? '' }
    case 'size':
      return {
        ...base,
        minimum: baseline.size.value.minimum?.toString() ?? '',
        maximum: baseline.size.value.maximum?.toString() ?? '',
      }
    case 'ceiling':
      return { ...base, cents: baseline.ceiling.value.cents ?? null }
    case 'ceremony':
      return {
        ...base,
        kinds: baseline.ceremony.value.kinds ?? [],
        detail: baseline.ceremony.value.detail ?? '',
      }
  }
}

/** Um pedido de alteração, já com o corpo certo para cada rota. */
export type BaselineUpdate =
  | { key: 'date'; body: Schemas['DateFieldIn'] }
  | { key: 'city'; body: Schemas['TextFieldIn'] }
  | { key: 'format'; body: Schemas['TextFieldIn'] }
  | { key: 'size'; body: Schemas['SizeFieldIn'] }
  | { key: 'ceiling'; body: Schemas['CeilingFieldIn'] }
  | { key: 'ceremony'; body: Schemas['CeremonyFieldIn'] }

const optional = (text: string) => text.trim() || null

function dateValue(v: FormValues): Schemas['DateValueSchema'] {
  if (v.dateKind === 'exata') return { kind: 'exata', exact: v.exact }
  if (v.dateKind === 'janela') {
    return {
      kind: 'janela',
      window_start: { year: Number(v.startYear), month: Number(v.startMonth) },
      window_end: { year: Number(v.endYear), month: Number(v.endMonth) },
      label: optional(v.dateLabel),
    }
  }
  return { kind: 'nenhuma' }
}

/** Dos valores do formulário, já validados, para o corpo da rota da chave. */
export function toUpdate(key: BaselineKey, v: FormValues, version: number): BaselineUpdate {
  const common = { status: v.status, note: optional(v.note), version }
  switch (key) {
    case 'date':
      return { key, body: { ...common, value: dateValue(v) } }
    case 'city':
    case 'format':
      return { key, body: { ...common, value: optional(v.text) } }
    case 'size':
      return {
        key,
        body: {
          ...common,
          value: {
            minimum: v.minimum.trim() === '' ? null : Number(v.minimum),
            maximum: v.maximum.trim() === '' ? null : Number(v.maximum),
          },
        },
      }
    case 'ceiling':
      return { key, body: { ...common, value: { cents: v.cents } } }
    case 'ceremony':
      return { key, body: { ...common, value: { kinds: v.kinds, detail: optional(v.detail) } } }
  }
}
