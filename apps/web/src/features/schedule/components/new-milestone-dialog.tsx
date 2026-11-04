import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { Controller, type FieldPath, useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { ApiError } from '@/lib/api/errors'
import { RESPONSIBLES, type Schedule } from '../api/schedule'
import { type Created, useCreateMilestone } from '../api/use-milestone-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import {
  type NewMilestoneFormValues,
  NO_CATEGORY,
  newMilestoneSchema,
} from '../schemas/milestone-form'
import { FormAlert } from './form-alert'

const labels = copy.form
const text = copy.newMilestone

const FIELD_BY_CODE: Record<string, FieldPath<NewMilestoneFormValues>> = {
  milestone_title_required: 'title',
  category_not_available: 'category_id',
}

const ALERTS = {
  conflict: text.conflict,
  network: text.network,
}

export interface NewMilestoneDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  schedule: Schedule
  /** A fase de onde o pedido partiu; sem ela, a primeira. */
  phaseId?: string
  onCreated: (created: Created) => void
  onCloseAutoFocus: (event: Event) => void
}

/**
 * "Novo marco" (F-CRN-01): título, fase (a de onde partiu, senão a primeira), responsável (Ambos) e
 * categoria opcional. O marco nasce no fim da fase; as dependências se ligam depois, no painel dele.
 */
export function NewMilestoneDialog({
  open,
  onOpenChange,
  schedule,
  phaseId,
  onCreated,
  onCloseAutoFocus,
}: NewMilestoneDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title={text.title}
        description={text.description}
        onCloseAutoFocus={onCloseAutoFocus}
      >
        <NewMilestoneForm
          schedule={schedule}
          phaseId={phaseId}
          onCancel={() => onOpenChange(false)}
          onCreated={onCreated}
        />
      </DialogContent>
    </Dialog>
  )
}

function NewMilestoneForm({
  schedule,
  phaseId,
  onCancel,
  onCreated,
}: {
  schedule: Schedule
  phaseId?: string
  onCancel: () => void
  onCreated: (created: Created) => void
}) {
  const create = useCreateMilestone()
  const [alert, setAlert] = useState<AlertState | null>(null)
  const form = useForm<NewMilestoneFormValues>({
    resolver: zodResolver(newMilestoneSchema),
    mode: 'onTouched',
    defaultValues: {
      title: '',
      phase_id: phaseId ?? schedule.phases[0]?.id ?? '',
      responsible: 'Ambos',
      category_id: NO_CATEGORY,
    },
  })
  const { control, register, handleSubmit, formState } = form
  const errors = formState.errors

  const submit = handleSubmit((values) => {
    setAlert(null)
    create.mutate(
      {
        title: values.title.trim(),
        phaseId: values.phase_id,
        responsible: values.responsible,
        categoryId: values.category_id === NO_CATEGORY ? null : values.category_id,
      },
      {
        onSuccess: onCreated,
        onError: (error) => {
          const field = error instanceof ApiError ? FIELD_BY_CODE[error.code] : undefined
          if (error instanceof ApiError && field) {
            form.setError(field, { message: error.message }, { shouldFocus: true })
            return
          }
          setAlert(alertFromError(error, ALERTS))
        },
      },
    )
  })

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-4">
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
            options={schedule.phases.map((phase) => ({ value: phase.id, label: phase.title }))}
            value={field.value}
            onValueChange={field.onChange}
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
            onValueChange={field.onChange}
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
            options={[
              { value: NO_CATEGORY, label: labels.noCategory },
              ...schedule.category_options.map((option) => ({
                value: option.id,
                label: option.name,
              })),
            ]}
            ref={field.ref}
            value={field.value}
            error={errors.category_id?.message}
            onValueChange={field.onChange}
          />
        )}
      />
      <FormAlert alert={alert} />
      <DialogFooter>
        <Button type="button" variant="ghost" onClick={onCancel}>
          {text.cancel}
        </Button>
        <Button type="submit" loading={create.isPending}>
          {text.submit}
        </Button>
      </DialogFooter>
    </form>
  )
}
