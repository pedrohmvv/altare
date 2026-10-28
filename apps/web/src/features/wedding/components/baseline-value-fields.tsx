import { Controller, type UseFormReturn } from 'react-hook-form'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { MoneyInput } from '@/components/ui/money-input'
import { SegmentedControl } from '@/components/ui/segmented-control'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { MONTHS } from '@/lib/date'
import type { BaselineKey } from '../api/baseline'
import { copy } from '../copy'
import type { FormValues } from '../schemas/baseline-form'

const CEREMONY_KINDS = ['Religiosa', 'Civil', 'Simbólica'] as const

const DATE_KINDS = [
  { value: 'nenhuma', label: copy.form.date.none },
  { value: 'janela', label: copy.form.date.window },
  { value: 'exata', label: copy.form.date.exact },
]

const STATUSES = [
  { value: 'Em definição', label: copy.status['Em definição'] },
  { value: 'Definido', label: copy.status.Definido },
]

interface FieldsProps {
  form: UseFormReturn<FormValues>
}

function DateFields({ form }: FieldsProps) {
  const { control, register, watch } = form
  const { errors } = form.formState
  const kind = watch('dateKind')
  const month = (name: 'startMonth' | 'endMonth', label: string) => (
    <Controller
      control={control}
      name={name}
      render={({ field }) => (
        <Select
          label={label}
          placeholder="Escolham"
          options={MONTHS}
          value={field.value}
          onValueChange={field.onChange}
          error={errors[name]?.message}
        />
      )}
    />
  )
  const year = (name: 'startYear' | 'endYear', label: string) => (
    <Input
      label={label}
      inputMode="numeric"
      maxLength={4}
      autoComplete="off"
      error={errors[name]?.message}
      {...register(name)}
    />
  )

  return (
    <div className="flex flex-col gap-5">
      <Controller
        control={control}
        name="dateKind"
        render={({ field }) => (
          <SegmentedControl
            aria-label={copy.form.date.kind}
            options={DATE_KINDS}
            value={field.value}
            onValueChange={field.onChange}
          />
        )}
      />
      {errors.dateKind?.message && (
        <p className="text-body-sm text-attention-ink">{errors.dateKind.message}</p>
      )}
      {kind === 'janela' && (
        <>
          <div className="grid grid-cols-2 gap-3">
            {month('startMonth', copy.form.date.startMonth)}
            {year('startYear', copy.form.date.startYear)}
          </div>
          <div className="grid grid-cols-2 gap-3">
            {month('endMonth', copy.form.date.endMonth)}
            {year('endYear', copy.form.date.endYear)}
          </div>
          <Input
            label={copy.form.date.label}
            hint={copy.form.date.labelHint}
            error={errors.dateLabel?.message}
            {...register('dateLabel')}
          />
        </>
      )}
      {kind === 'exata' && (
        <Input
          type="date"
          label={copy.form.date.exactDay}
          error={errors.exact?.message}
          {...register('exact')}
        />
      )}
    </div>
  )
}

function SizeFields({ form }: FieldsProps) {
  const { errors } = form.formState
  return (
    <div className="grid grid-cols-2 gap-3">
      <Input
        label={copy.form.size.minimum}
        inputMode="numeric"
        autoComplete="off"
        error={errors.minimum?.message}
        {...form.register('minimum')}
      />
      <Input
        label={copy.form.size.maximum}
        inputMode="numeric"
        autoComplete="off"
        error={errors.maximum?.message}
        {...form.register('maximum')}
      />
    </div>
  )
}

function CeremonyFields({ form }: FieldsProps) {
  const { errors } = form.formState
  return (
    <div className="flex flex-col gap-5">
      <Controller
        control={form.control}
        name="kinds"
        render={({ field }) => (
          <fieldset className="flex flex-col">
            <legend className="mb-1.5 text-body-sm font-semibold text-ink">
              {copy.form.ceremony.kinds}
            </legend>
            {CEREMONY_KINDS.map((kind) => (
              <Checkbox
                key={kind}
                label={kind}
                checked={field.value.includes(kind)}
                onCheckedChange={(checked) =>
                  field.onChange(
                    checked === true
                      ? [...field.value, kind]
                      : field.value.filter((item) => item !== kind),
                  )
                }
              />
            ))}
            {errors.kinds?.message && (
              <p className="mt-1.5 text-body-sm text-attention-ink">{errors.kinds.message}</p>
            )}
          </fieldset>
        )}
      />
      <Input
        label={copy.form.ceremony.detail}
        hint={copy.form.ceremony.detailHint}
        error={errors.detail?.message}
        {...form.register('detail')}
      />
    </div>
  )
}

/** A parte do formulário que muda de uma definição para outra. */
export function ValueFields({ fieldKey, form }: FieldsProps & { fieldKey: BaselineKey }) {
  const { errors } = form.formState
  switch (fieldKey) {
    case 'date':
      return <DateFields form={form} />
    case 'city':
    case 'format':
      return (
        <Input
          label={copy.fields[fieldKey].label}
          error={errors.text?.message}
          autoComplete="off"
          {...form.register('text')}
        />
      )
    case 'size':
      return <SizeFields form={form} />
    case 'ceiling':
      return (
        <Controller
          control={form.control}
          name="cents"
          render={({ field }) => (
            <MoneyInput
              label={copy.fields.ceiling.label}
              value={field.value}
              onValueChange={field.onChange}
              onBlur={field.onBlur}
              ref={field.ref}
              error={errors.cents?.message}
            />
          )}
        />
      )
    case 'ceremony':
      return <CeremonyFields form={form} />
  }
}

/** A situação e a nota valem para qualquer definição. */
export function StatusFields({ form }: FieldsProps) {
  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col gap-1.5">
        <span className="text-body-sm font-semibold text-ink">{copy.form.status}</span>
        <Controller
          control={form.control}
          name="status"
          render={({ field }) => (
            <SegmentedControl
              aria-label={copy.form.status}
              options={STATUSES}
              value={field.value}
              onValueChange={field.onChange}
            />
          )}
        />
      </div>
      <Textarea
        label={copy.form.note}
        hint={copy.form.noteHint}
        rows={3}
        error={form.formState.errors.note?.message}
        {...form.register('note')}
      />
    </div>
  )
}
