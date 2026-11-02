import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { RESPONSIBLES, type Schedule, type ScheduleMilestone, scheduleKeys } from '../api/schedule'
import { useUpdateMilestone } from '../api/use-milestone-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import {
  type MilestoneFormValues,
  milestoneSchema,
  toFormValues,
  toUpdateFields,
} from '../schemas/milestone-form'
import { FormAlert } from './form-alert'

const labels = copy.form

const FORM_ALERTS = {
  conflict: labels.errors.conflict,
  blocked: labels.errors.network,
  network: labels.errors.network,
}

const findMilestone = (schedule: Schedule | undefined, id: string) =>
  schedule?.phases.flatMap((phase) => phase.milestones).find((item) => item.id === id)

/** O responsável, o prazo-alvo (só data, pode limpar) e a nota do marco (F-CRN-05). */
export function MilestoneForm({ milestone }: { milestone: ScheduleMilestone }) {
  const queryClient = useQueryClient()
  const update = useUpdateMilestone()
  // O marco de quando o formulário abriu: um conflito nunca troca o que foi digitado, e a versão
  // enviada é a dele, a não ser que o resto do marco continue igual (só o estado mudou, por nós).
  const [opened, setOpened] = useState(milestone)
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const [saved, setSaved] = useState(false)
  const form = useForm<MilestoneFormValues>({
    resolver: zodResolver(milestoneSchema),
    mode: 'onTouched',
    defaultValues: toFormValues(opened),
  })
  const { control, register, handleSubmit, setValue, watch, formState } = form
  const errors = formState.errors

  const sameContent =
    opened.responsible === milestone.responsible &&
    opened.note === milestone.note &&
    opened.target_date === milestone.target_date
  const version = sameContent ? milestone.version : opened.version

  const submit = handleSubmit((values) => {
    setAlert(null)
    setSaved(false)
    update.mutate(
      { milestoneId: milestone.id, ...toUpdateFields(values), version },
      {
        onSuccess: (schedule) => {
          const latest = findMilestone(schedule, milestone.id)
          if (!latest) return
          setOpened(latest)
          form.reset(toFormValues(latest))
          setSaved(true)
        },
        onError: (error) => setAlert(alertFromError(error, FORM_ALERTS)),
      },
    )
  })

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    const latest = findMilestone(queryClient.getQueryData<Schedule>(scheduleKeys.all), milestone.id)
    setReloading(false)
    if (!latest) return
    setOpened(latest)
    form.reset(toFormValues(latest))
    setAlert(null)
  }

  return (
    <form
      onSubmit={submit}
      noValidate
      className="flex flex-col gap-4"
      onChange={() => setSaved(false)}
    >
      <h3 className="text-body font-semibold text-ink">{labels.title}</h3>
      <Controller
        control={control}
        name="responsible"
        render={({ field }) => (
          <Select
            label={labels.responsible}
            options={RESPONSIBLES.map((value) => ({ value, label: copy.responsibles[value] }))}
            value={field.value}
            onValueChange={(value) => {
              setSaved(false)
              field.onChange(value)
            }}
          />
        )}
      />
      <div className="flex flex-col gap-2">
        <Input
          type="date"
          label={labels.target}
          hint={labels.targetHint}
          error={errors.target_date?.message}
          {...register('target_date')}
        />
        {watch('target_date') !== '' && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="self-start"
            onClick={() => {
              setSaved(false)
              setValue('target_date', '', { shouldDirty: true, shouldValidate: true })
            }}
          >
            {labels.clearTarget}
          </Button>
        )}
      </div>
      <Textarea
        label={labels.note}
        hint={labels.noteHint}
        rows={3}
        error={errors.note?.message}
        {...register('note')}
      />
      <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
      <div className="flex flex-wrap items-center gap-3">
        <Button type="submit" loading={update.isPending}>
          {labels.save}
        </Button>
        <p role="status" className="text-body-sm text-consensus-ink">
          {saved ? labels.saved : ''}
        </p>
      </div>
    </form>
  )
}
