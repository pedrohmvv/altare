import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { ApiError } from '@/lib/api/errors'
import { findTask, RESPONSIBLES, type ScheduleTask, scheduleKeys } from '../api/schedule'
import { useUpdateTask } from '../api/use-task-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import {
  type TaskFormValues,
  taskSchema,
  toTaskFields,
  toTaskFormValues,
} from '../schemas/task-form'
import { FormAlert } from './form-alert'

const labels = copy.form
const text = copy.task.form

const ALERTS = {
  conflict: text.conflict,
  network: labels.errors.network,
}

/** Título, responsável, prazo (só data, pode tirar) e nota da avulsa (F-CRN-06). */
export function TaskForm({ task }: { task: ScheduleTask }) {
  const queryClient = useQueryClient()
  const update = useUpdateTask()
  // A avulsa de quando o formulário abriu: um conflito nunca troca o que foi digitado, e a versão
  // enviada é a dela, a não ser que o conteúdo continue o mesmo (só o estado mudou, por nós).
  const [opened, setOpened] = useState(task)
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const [saved, setSaved] = useState(false)
  const form = useForm<TaskFormValues>({
    resolver: zodResolver(taskSchema),
    mode: 'onTouched',
    defaultValues: toTaskFormValues(opened),
  })
  const { control, register, handleSubmit, setValue, setFocus, watch, formState } = form
  const errors = formState.errors

  const sameContent =
    opened.title === task.title &&
    opened.responsible === task.responsible &&
    opened.note === task.note &&
    opened.target_date === task.target_date
  const version = sameContent ? task.version : opened.version

  const submit = handleSubmit((values) => {
    setAlert(null)
    setSaved(false)
    update.mutate(
      { taskId: task.id, ...toTaskFields(values), version },
      {
        onSuccess: (schedule) => {
          const latest = findTask(schedule, task.id)
          if (!latest) return
          setOpened(latest)
          form.reset(toTaskFormValues(latest))
          setSaved(true)
        },
        onError: (error) => {
          if (error instanceof ApiError && error.code === 'task_title_required') {
            form.setError('title', { message: error.message }, { shouldFocus: true })
            return
          }
          setAlert(alertFromError(error, ALERTS))
        },
      },
    )
  })

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    const latest = findTask(queryClient.getQueryData(scheduleKeys.all), task.id)
    setReloading(false)
    if (!latest) return
    setOpened(latest)
    form.reset(toTaskFormValues(latest))
    setAlert(null)
  }

  return (
    <form
      onSubmit={submit}
      noValidate
      className="flex flex-col gap-4"
      onChange={() => setSaved(false)}
    >
      <h3 className="text-body font-semibold text-ink">{text.title}</h3>
      <Input
        label={labels.titleLabel}
        required
        autoComplete="off"
        error={errors.title?.message}
        {...register('title')}
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
          label={text.target}
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
              // O botão some ao limpar o campo: o foco vai para o campo.
              setFocus('target_date')
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
