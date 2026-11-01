import { Controller, type UseFormReturn } from 'react-hook-form'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { SIDES } from '../api/guests'
import { copy } from '../copy'
import type { HouseholdFormValues } from '../schemas/guest-forms'

const labels = copy.forms.household

/** Os campos do núcleo (F-CNV-01): nome e lado obrigatórios, o endereço é para o convite impresso. */
export function HouseholdFields({ form }: { form: UseFormReturn<HouseholdFormValues> }) {
  const { register, control, formState } = form
  const errors = formState.errors
  return (
    <div className="flex flex-col gap-4">
      <Input
        label={labels.name}
        hint={labels.nameHint}
        autoComplete="off"
        error={errors.name?.message}
        {...register('name')}
      />
      <Controller
        control={control}
        name="side"
        render={({ field }) => (
          <Select
            label={labels.side}
            placeholder={labels.sidePlaceholder}
            options={SIDES.map((side) => ({ value: side, label: copy.sides[side] }))}
            value={field.value}
            onValueChange={field.onChange}
            error={errors.side?.message}
          />
        )}
      />
      <fieldset className="flex flex-col gap-4">
        <legend className="text-body font-medium text-ink">{labels.address}</legend>
        <p className="-mt-2 text-body-sm text-ink-muted">{labels.addressHint}</p>
        <div className="grid gap-4 sm:grid-cols-[1fr_8rem]">
          <Input
            label={labels.street}
            autoComplete="off"
            error={errors.street?.message}
            {...register('street')}
          />
          <Input
            label={labels.number}
            autoComplete="off"
            error={errors.number?.message}
            {...register('number')}
          />
        </div>
        <Input
          label={labels.complement}
          autoComplete="off"
          error={errors.complement?.message}
          {...register('complement')}
        />
        <Input
          label={labels.district}
          autoComplete="off"
          error={errors.district?.message}
          {...register('district')}
        />
        <div className="grid gap-4 sm:grid-cols-[1fr_6rem_9rem]">
          <Input
            label={labels.city}
            autoComplete="off"
            error={errors.city?.message}
            {...register('city')}
          />
          <Input
            label={labels.state}
            autoComplete="off"
            maxLength={2}
            error={errors.state?.message}
            {...register('state')}
          />
          <Input
            label={labels.postalCode}
            autoComplete="off"
            inputMode="numeric"
            error={errors.postal_code?.message}
            {...register('postal_code')}
          />
        </div>
      </fieldset>
      <Textarea label={labels.note} rows={3} error={errors.note?.message} {...register('note')} />
    </div>
  )
}
