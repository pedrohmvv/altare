import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Controller, type FieldPath, useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { ApiError } from '@/lib/api/errors'
import {
  type CategoryOption,
  findMilestone,
  RESPONSIBLES,
  type ScheduleMilestone,
  scheduleKeys,
} from '../api/schedule'
import { useUpdateMilestone } from '../api/use-milestone-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import {
  type MilestoneFormValues,
  milestoneSchema,
  NO_CATEGORY,
  toFormValues,
  toUpdateFields,
} from '../schemas/milestone-form'
import { FormAlert } from './form-alert'

const labels = copy.form

const FORM_ALERTS = {
  conflict: labels.errors.conflict,
  network: labels.errors.network,
}

/** O `code` estável do erro da API que pertence a um campo do formulário. */
const FIELD_BY_CODE: Record<string, FieldPath<MilestoneFormValues>> = {
  milestone_title_required: 'title',
  category_not_available: 'category_id',
}

/** O que o formulário precisa saber do cronograma para oferecer as escolhas. */
export interface MilestoneFormProps {
  milestone: ScheduleMilestone
  /** A fase em que o marco está agora. */
  phaseId: string
  phases: readonly { id: string; title: string }[]
  categoryOptions: readonly CategoryOption[]
}

/** Título, fase, categoria, responsável, prazo-alvo (só data, pode limpar) e nota (F-CRN-01, F-CRN-05). */
export function MilestoneForm({ milestone, phaseId, phases, categoryOptions }: MilestoneFormProps) {
  const queryClient = useQueryClient()
  const update = useUpdateMilestone()
  // O marco de quando o formulário abriu: um conflito nunca troca o que foi digitado, e a versão
  // enviada é a dele, a não ser que o resto do marco continue igual (só o estado mudou, por nós).
  const [opened, setOpened] = useState({ milestone, phaseId })
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const [saved, setSaved] = useState(false)
  const form = useForm<MilestoneFormValues>({
    resolver: zodResolver(milestoneSchema),
    mode: 'onTouched',
    defaultValues: toFormValues(opened.milestone, opened.phaseId),
  })
  const { control, register, handleSubmit, setValue, watch, formState } = form
  const errors = formState.errors

  const sameContent =
    opened.milestone.title === milestone.title &&
    opened.phaseId === phaseId &&
    opened.milestone.category?.id === milestone.category?.id &&
    opened.milestone.responsible === milestone.responsible &&
    opened.milestone.note === milestone.note &&
    opened.milestone.target_date === milestone.target_date
  const version = sameContent ? milestone.version : opened.milestone.version

  // A categoria ligada que já não é uma opção continua na lista: nunca a trocamos em silêncio.
  const linked = milestone.category
  const categories = [
    { value: NO_CATEGORY, label: labels.noCategory },
    ...categoryOptions.map((option) => ({ value: option.id, label: option.name })),
    ...(linked && !categoryOptions.some((option) => option.id === linked.id)
      ? [{ value: linked.id, label: linked.name ?? copy.sheet.links.unnamedCategory }]
      : []),
  ]

  const submit = handleSubmit((values) => {
    setAlert(null)
    setSaved(false)
    update.mutate(
      { milestoneId: milestone.id, ...toUpdateFields(values), version },
      {
        onSuccess: (schedule) => {
          const latest = findMilestone(schedule, milestone.id)
          if (!latest) return
          setOpened({ milestone: latest.milestone, phaseId: latest.phase.id })
          form.reset(toFormValues(latest.milestone, latest.phase.id))
          setSaved(true)
        },
        onError: (error) => {
          const field = error instanceof ApiError ? FIELD_BY_CODE[error.code] : undefined
          if (error instanceof ApiError && field) {
            form.setError(field, { message: error.message }, { shouldFocus: true })
            return
          }
          setAlert(alertFromError(error, FORM_ALERTS))
        },
      },
    )
  })

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    const latest = findMilestone(queryClient.getQueryData(scheduleKeys.all), milestone.id)
    setReloading(false)
    if (!latest) return
    setOpened({ milestone: latest.milestone, phaseId: latest.phase.id })
    form.reset(toFormValues(latest.milestone, latest.phase.id))
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
      <Input
        label={labels.titleLabel}
        required
        autoComplete="off"
        error={errors.title?.message}
        {...register('title')}
      />
      <Controller
        control={control}
        name="phase_id"
        render={({ field }) => (
          <Select
            label={labels.phase}
            options={phases.map((phase) => ({ value: phase.id, label: phase.title }))}
            value={field.value}
            onValueChange={(value) => {
              setSaved(false)
              field.onChange(value)
            }}
          />
        )}
      />
      <Controller
        control={control}
        name="category_id"
        render={({ field }) => (
          <Select
            label={labels.category}
            hint={labels.categoryHint}
            options={categories}
            ref={field.ref}
            value={field.value}
            error={errors.category_id?.message}
            onValueChange={(value) => {
              setSaved(false)
              field.onChange(value)
            }}
          />
        )}
      />
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
