import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { ApiError } from '@/lib/api/errors'
import { newTaskId, RESPONSIBLES, type Responsible, type Schedule } from '../api/schedule'
import { useCreateTask } from '../api/use-task-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import { type TaskFormValues, taskSchema, toTaskFields } from '../schemas/task-form'
import { FormAlert } from './form-alert'

const labels = copy.form
const text = copy.task.create

const ALERTS = {
  conflict: copy.task.form.conflict,
  network: text.network,
}

export interface NewTaskDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  /** Os ids de agora: o id da avulsa nova se acha pela diferença com o que a API devolve. */
  taskIds: readonly string[]
  /** O perfil da sessão, o responsável padrão (nunca `Ambos`); sem ele, a primeira escolha. */
  profile?: Responsible
  /** `taskId` é `null` se não houve exatamente um id novo: a tela não abre nada, só avisa. */
  onCreated: (created: { schedule: Schedule; taskId: string | null }) => void
  onCloseAutoFocus: (event: Event) => void
}

/**
 * "Nova avulsa" (F-CRN-06): título, responsável (o perfil de quem cria), prazo e nota, os dois
 * últimos opcionais. O responsável escolhido sempre vai no pedido.
 */
export function NewTaskDialog({
  open,
  onOpenChange,
  taskIds,
  profile,
  onCreated,
  onCloseAutoFocus,
}: NewTaskDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title={text.title}
        description={text.description}
        onCloseAutoFocus={onCloseAutoFocus}
      >
        <NewTaskForm
          taskIds={taskIds}
          profile={profile ?? RESPONSIBLES[0] ?? 'Noivo'}
          onCancel={() => onOpenChange(false)}
          onCreated={onCreated}
        />
      </DialogContent>
    </Dialog>
  )
}

function NewTaskForm({
  taskIds,
  profile,
  onCancel,
  onCreated,
}: {
  taskIds: readonly string[]
  profile: Responsible
  onCancel: () => void
  onCreated: NewTaskDialogProps['onCreated']
}) {
  const create = useCreateTask()
  const [alert, setAlert] = useState<AlertState | null>(null)
  const form = useForm<TaskFormValues>({
    resolver: zodResolver(taskSchema),
    mode: 'onTouched',
    defaultValues: { title: '', responsible: profile, target_date: '', note: '' },
  })
  const { control, register, handleSubmit, formState } = form
  const errors = formState.errors

  const submit = handleSubmit((values) => {
    setAlert(null)
    create.mutate(toTaskFields(values), {
      onSuccess: (schedule) => onCreated({ schedule, taskId: newTaskId(taskIds, schedule) }),
      onError: (error) => {
        if (error instanceof ApiError && error.code === 'task_title_required') {
          form.setError('title', { message: error.message }, { shouldFocus: true })
          return
        }
        setAlert(alertFromError(error, ALERTS))
      },
    })
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
      <Input
        type="date"
        label={copy.task.form.target}
        hint={labels.targetHint}
        error={errors.target_date?.message}
        {...register('target_date')}
      />
      <Textarea
        label={labels.note}
        hint={labels.noteHint}
        rows={3}
        error={errors.note?.message}
        {...register('note')}
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
