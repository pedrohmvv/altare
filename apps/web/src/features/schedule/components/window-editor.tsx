import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useEffect, useId, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import {
  findMilestone,
  type MilestoneWindow,
  type ScheduleMilestone,
  scheduleKeys,
  type WindowUnit,
} from '../api/schedule'
import { useUpdateMilestoneWindow } from '../api/use-milestone-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import {
  toWindowBody,
  toWindowFormValues,
  type WindowFormValues,
  windowSchema,
} from '../schemas/window-form'
import { FormAlert } from './form-alert'

const labels = copy.window

const ALERTS = { conflict: labels.errors.conflict, network: labels.errors.network }

const UNITS: WindowUnit[] = ['meses', 'semanas']

const sameWindow = (a: MilestoneWindow | null, b: MilestoneWindow | null) =>
  a?.start_before === b?.start_before && a?.end_before === b?.end_before && a?.unit === b?.unit

export interface WindowEditorProps {
  milestone: ScheduleMilestone
  /** O foco entra no início ao abrir (o "Definir janela" abriu o editor vazio). */
  focusOnOpen?: boolean
  /** Só o editor de uma janela nova tem Cancelar: ele volta ao "Definir janela". */
  onCancel?: () => void
  /** Chamado depois de salvar: quem tem o título da seção leva o foco para lá. */
  onSaved: () => void
}

/**
 * O editor da janela (F-CRN-05, regra 5): início, fim e unidade, com a versão do marco. Como no
 * formulário do marco, a versão enviada é a de quando o editor abriu, a não ser que a janela
 * continue igual (só o resto do marco mudou): um conflito nunca vira sobrescrita silenciosa.
 */
export function WindowEditor({ milestone, focusOnOpen, onCancel, onSaved }: WindowEditorProps) {
  const queryClient = useQueryClient()
  const update = useUpdateMilestoneWindow()
  const [opened, setOpened] = useState({ window: milestone.window, version: milestone.version })
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const [saved, setSaved] = useState(false)
  const hintId = useId()
  const unitHintId = useId()
  const form = useForm<WindowFormValues>({
    resolver: zodResolver(windowSchema),
    mode: 'onTouched',
    defaultValues: toWindowFormValues(opened.window),
  })
  const { control, register, handleSubmit, watch, formState, setFocus } = form
  const errors = formState.errors
  const unit = watch('unit')
  const version = sameWindow(opened.window, milestone.window) ? milestone.version : opened.version

  useEffect(() => {
    if (focusOnOpen) setFocus('start_before')
  }, [focusOnOpen, setFocus])

  function adopt(latest: ScheduleMilestone) {
    setOpened({ window: latest.window, version: latest.version })
    form.reset(toWindowFormValues(latest.window))
  }

  const submit = handleSubmit((values) => {
    setAlert(null)
    setSaved(false)
    const body = toWindowBody(values)
    update.mutate(
      {
        milestoneId: milestone.id,
        startBefore: body.start_before,
        endBefore: body.end_before,
        unit: body.unit,
        version,
      },
      {
        onSuccess: (schedule) => {
          const latest = findMilestone(schedule, milestone.id)
          if (!latest) return
          adopt(latest.milestone)
          setSaved(true)
          onSaved()
        },
        onError: (error) => setAlert(alertFromError(error, ALERTS)),
      },
    )
  })

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    const latest = findMilestone(queryClient.getQueryData(scheduleKeys.all), milestone.id)
    setReloading(false)
    if (!latest) return
    adopt(latest.milestone)
    setAlert(null)
  }

  const unchanged = !formState.isDirty

  return (
    <form
      onSubmit={submit}
      noValidate
      className="flex flex-col gap-4"
      onChange={() => setSaved(false)}
    >
      <div className="grid grid-cols-2 gap-3">
        <Input
          label={labels.start}
          inputMode="numeric"
          autoComplete="off"
          aria-describedby={unitHintId}
          error={errors.start_before?.message}
          {...register('start_before')}
        />
        <Input
          label={labels.end}
          inputMode="numeric"
          autoComplete="off"
          aria-describedby={unitHintId}
          error={errors.end_before?.message}
          {...register('end_before')}
        />
      </div>
      <p id={unitHintId} className="-mt-1 text-body-sm text-ink-muted">
        {labels.hints[unit]}
      </p>
      <Controller
        control={control}
        name="unit"
        render={({ field }) => (
          <Select
            label={labels.unit}
            options={UNITS.map((value) => ({ value, label: labels.units[value] }))}
            value={field.value}
            onValueChange={(value) => {
              setSaved(false)
              field.onChange(value)
            }}
          />
        )}
      />
      <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
      <div className="flex flex-wrap items-center gap-3">
        <Button
          type="submit"
          loading={update.isPending}
          disabled={unchanged}
          aria-describedby={unchanged && !saved ? hintId : undefined}
        >
          {labels.save}
        </Button>
        {onCancel && (
          <Button type="button" variant="ghost" onClick={onCancel}>
            {labels.cancelDefine}
          </Button>
        )}
        <p role="status" className="text-body-sm text-consensus-ink">
          {saved ? labels.saved : ''}
        </p>
      </div>
      {unchanged && !saved && (
        <p id={hintId} className="-mt-2 text-body-sm text-ink-muted">
          {labels.noChange}
        </p>
      )}
    </form>
  )
}
