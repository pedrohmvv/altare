import { Controller, type UseFormReturn } from 'react-hook-form'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { AGE_BANDS, PROBABILITIES } from '../api/guests'
import { copy } from '../copy'
import type { GuestFormValues } from '../schemas/guest-forms'

const labels = copy.forms.guest

export interface GuestFieldsProps {
  form: UseFormReturn<GuestFormValues>
  /** O acompanhante pode ficar sem nome até saberem quem é (F-CNV-02). */
  companion?: boolean
  /** O motivo só existe enquanto a pessoa está em `Não irá` (F-CNV-04). */
  showDeclineReason?: boolean
}

/** Os campos de uma pessoa (F-CNV-01): o nome, a faixa, a probabilidade, os contatos e as notas. */
export function GuestFields({
  form,
  companion = false,
  showDeclineReason = false,
}: GuestFieldsProps) {
  const { register, control, watch, formState } = form
  const errors = formState.errors
  const isChild = watch('band') !== 'Adulto'
  return (
    <div className="flex flex-col gap-4">
      <Input
        label={labels.name}
        hint={companion ? labels.companionNameHint : undefined}
        autoComplete="off"
        error={errors.name?.message}
        {...register('name')}
      />
      <div className="grid gap-4 sm:grid-cols-2">
        <Controller
          control={control}
          name="band"
          render={({ field }) => (
            <Select
              label={labels.band}
              options={AGE_BANDS.map((band) => ({ value: band, label: copy.bands[band] }))}
              value={field.value}
              onValueChange={field.onChange}
            />
          )}
        />
        <Controller
          control={control}
          name="probability"
          render={({ field }) => (
            <Select
              label={labels.probability}
              options={PROBABILITIES.map((probability) => ({
                value: probability,
                label: copy.probabilities[probability],
              }))}
              value={field.value}
              onValueChange={field.onChange}
            />
          )}
        />
      </div>
      {isChild && (
        <Input
          label={labels.age}
          hint={labels.ageHint}
          inputMode="numeric"
          autoComplete="off"
          error={errors.age?.message}
          {...register('age')}
        />
      )}
      <Input
        label={labels.phone}
        hint={labels.phoneHint}
        type="tel"
        autoComplete="off"
        error={errors.phone?.message}
        {...register('phone')}
      />
      <Input
        label={labels.email}
        type="email"
        autoComplete="off"
        error={errors.email?.message}
        {...register('email')}
      />
      <Input
        label={labels.dietary}
        autoComplete="off"
        error={errors.dietary_restriction?.message}
        {...register('dietary_restriction')}
      />
      {showDeclineReason && (
        <Input
          label={labels.declineReason}
          hint={labels.declineReasonHint}
          autoComplete="off"
          error={errors.decline_reason?.message}
          {...register('decline_reason')}
        />
      )}
      <Textarea label={labels.note} rows={3} error={errors.note?.message} {...register('note')} />
    </div>
  )
}
