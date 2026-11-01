import { z } from 'zod'
import {
  AGE_BANDS,
  type AgeBand,
  type Guest,
  type Household,
  PROBABILITIES,
  SIDES,
} from '../api/guests'
import { copy } from '../copy'

const errors = copy.forms.errors

const MAX_NAME = 80
const text = (max: number) => z.string().trim().max(max, errors.tooLong(max))
const oneOf = <T extends string>(values: readonly T[], message: string) =>
  z.string().refine((value) => values.includes(value as T), message)

/** O formulário do núcleo (F-CNV-01): nome e lado obrigatórios, o resto do endereço é opcional. */
export const householdSchema = z.object({
  name: z.string().trim().min(1, errors.householdName).max(MAX_NAME, errors.tooLong(MAX_NAME)),
  side: oneOf(SIDES, errors.side),
  street: text(120),
  number: text(20),
  complement: text(60),
  district: text(60),
  city: text(60),
  state: z
    .string()
    .trim()
    .regex(/^([A-Za-z]{2})?$/, errors.state),
  postal_code: z
    .string()
    .trim()
    .regex(/^(\d{5}-?\d{3})?$/, errors.postalCode),
  note: text(500),
})

export type HouseholdFormValues = z.infer<typeof householdSchema>

/** O formulário da pessoa (F-CNV-01). O telefone e o e-mail são conferidos pela API, que é quem sabe. */
export function makeGuestSchema(options: { nameRequired: boolean }) {
  return z
    .object({
      name: text(MAX_NAME),
      band: oneOf(AGE_BANDS, errors.age),
      age: z.string().trim(),
      probability: oneOf(PROBABILITIES, errors.age),
      dietary_restriction: text(120),
      note: text(500),
      phone: text(30),
      email: text(254),
      decline_reason: text(300),
    })
    .superRefine((values, context) => {
      if (options.nameRequired && values.name === '') {
        context.addIssue({ code: 'custom', path: ['name'], message: errors.guestName })
      }
      if (values.band !== 'Adulto' && values.age !== '') {
        const age = Number(values.age)
        if (!/^\d{1,2}$/.test(values.age) || age > 17) {
          context.addIssue({ code: 'custom', path: ['age'], message: errors.age })
        }
      }
    })
}

export type GuestFormValues = z.infer<ReturnType<typeof makeGuestSchema>>

export const EMPTY_HOUSEHOLD: HouseholdFormValues = {
  name: '',
  side: '',
  street: '',
  number: '',
  complement: '',
  district: '',
  city: '',
  state: '',
  postal_code: '',
  note: '',
}

export const EMPTY_GUEST: GuestFormValues = {
  name: '',
  band: 'Adulto',
  age: '',
  probability: 'Provável',
  dietary_restriction: '',
  note: '',
  phone: '',
  email: '',
  decline_reason: '',
}

const orEmpty = (value: string | null) => value ?? ''
const orNull = (value: string) => (value.trim() === '' ? null : value.trim())

export function toHouseholdFormValues(household: Household): HouseholdFormValues {
  return {
    name: household.name,
    side: household.side,
    street: orEmpty(household.street),
    number: orEmpty(household.number),
    complement: orEmpty(household.complement),
    district: orEmpty(household.district),
    city: orEmpty(household.city),
    state: orEmpty(household.state),
    postal_code: orEmpty(household.postal_code),
    note: orEmpty(household.note),
  }
}

export function toGuestFormValues(guest: Guest): GuestFormValues {
  return {
    name: orEmpty(guest.name),
    band: guest.band,
    age: guest.age === null ? '' : String(guest.age),
    probability: guest.probability,
    dietary_restriction: orEmpty(guest.dietary_restriction),
    note: orEmpty(guest.note),
    phone: orEmpty(guest.phone),
    email: orEmpty(guest.email),
    decline_reason: orEmpty(guest.decline_reason),
  }
}

/** O corpo da API: vazio vira `null`, e a idade só segue para criança. */
export function toHouseholdBody(values: HouseholdFormValues) {
  return {
    name: values.name.trim(),
    side: SIDES.find((side) => side === values.side) ?? 'Comum',
    street: orNull(values.street),
    number: orNull(values.number),
    complement: orNull(values.complement),
    district: orNull(values.district),
    city: orNull(values.city),
    state: orNull(values.state),
    postal_code: orNull(values.postal_code),
    note: orNull(values.note),
  }
}

export function toGuestBody(values: GuestFormValues) {
  const band: AgeBand = AGE_BANDS.find((candidate) => candidate === values.band) ?? 'Adulto'
  return {
    name: orNull(values.name),
    band,
    age: band === 'Adulto' || values.age === '' ? null : Number(values.age),
    probability: PROBABILITIES.find((candidate) => candidate === values.probability) ?? 'Provável',
    dietary_restriction: orNull(values.dietary_restriction),
    note: orNull(values.note),
    phone: orNull(values.phone),
    email: orNull(values.email),
  }
}

/** O motivo de não ir é do formulário, não do corpo comum: só vale com o status `Não irá`. */
export const toDeclineReason = (values: GuestFormValues) => orNull(values.decline_reason)
