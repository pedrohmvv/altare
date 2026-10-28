import { zodResolver } from '@hookform/resolvers/zod'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { CircleAlert } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter } from '@/components/ui/dialog'
import { ApiError } from '@/lib/api/errors'
import { type Baseline, type BaselineKey, baselineQueryOptions } from '../api/baseline'
import { useUpdateBaselineField } from '../api/use-update-baseline-field'
import { copy } from '../copy'
import { describeValue } from '../lib/describe-value'
import { type FormValues, makeSchema, toFormValues, toUpdate } from '../schemas/baseline-form'
import { StatusFields, ValueFields } from './baseline-value-fields'

export interface BaselineFieldDialogProps {
  fieldKey: BaselineKey
  open: boolean
  onOpenChange: (open: boolean) => void
  /** O quadro como está agora no cache; o formulário abre com o que havia na hora de abrir. */
  baseline: Baseline
  /** Sem `DialogTrigger` o Radix não sabe para onde devolver o foco ao fechar; quem abre diz. */
  onCloseAutoFocus?: (event: Event) => void
}

export function BaselineFieldDialog({
  fieldKey,
  open,
  onOpenChange,
  baseline,
  onCloseAutoFocus,
}: BaselineFieldDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title={copy.fields[fieldKey].label}
        description={copy.fields[fieldKey].hint}
        onCloseAutoFocus={onCloseAutoFocus}
      >
        <FieldEditor fieldKey={fieldKey} latest={baseline} onDone={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  )
}

type Alert = { kind: 'conflict' | 'error'; text: string }

function FieldEditor({
  fieldKey,
  latest,
  onDone,
}: {
  fieldKey: BaselineKey
  latest: Baseline
  onDone: () => void
}) {
  // A versão que a pessoa viu ao abrir é a que vai no pedido: se alguém mudou no meio, a API recusa
  // (409) em vez de deixar um sobrescrever o outro.
  const [opened, setOpened] = useState(latest)
  const [alert, setAlert] = useState<Alert | null>(null)
  const [pending, setPending] = useState<FormValues | null>(null)
  const update = useUpdateBaselineField()
  const queryClient = useQueryClient()
  const { isFetching } = useQuery({ ...baselineQueryOptions, enabled: false })
  const schema = useMemo(() => makeSchema(fieldKey), [fieldKey])
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    mode: 'onTouched',
    defaultValues: toFormValues(fieldKey, opened),
  })

  const version = opened[fieldKey].version

  function save(values: FormValues) {
    setAlert(null)
    update.mutate(toUpdate(fieldKey, values, version), {
      onSuccess: onDone,
      onError: (error) => {
        setPending(null)
        if (error instanceof ApiError && error.code === 'version_conflict') {
          void queryClient.invalidateQueries({ queryKey: baselineQueryOptions.queryKey })
          setAlert({ kind: 'conflict', text: copy.errors.conflict })
          return
        }
        setAlert({
          kind: 'error',
          text: error instanceof ApiError ? error.message : copy.errors.network,
        })
      },
    })
  }

  const onValid = form.handleSubmit((values) => {
    // Mudar o valor de algo já definido pede confirmação, com o antes e o depois (F-PLN-01, regra 2).
    const before = describeValue(fieldKey, opened[fieldKey].value)
    const after = describeValue(fieldKey, toUpdate(fieldKey, values, version).body.value)
    if (opened[fieldKey].status === 'Definido' && before !== after) setPending(values)
    else save(values)
  })

  function reloadLatest() {
    setOpened(latest)
    form.reset(toFormValues(fieldKey, latest))
    setAlert(null)
  }

  if (pending) {
    return (
      <Confirmation
        fieldKey={fieldKey}
        before={describeValue(fieldKey, opened[fieldKey].value)}
        after={describeValue(fieldKey, toUpdate(fieldKey, pending, version).body.value)}
        saving={update.isPending}
        onBack={() => setPending(null)}
        onConfirm={() => save(pending)}
      />
    )
  }

  return (
    <form onSubmit={onValid} noValidate className="flex flex-col gap-6">
      <ValueFields fieldKey={fieldKey} form={form} />
      <StatusFields form={form} />

      {/* A região existe vazia desde o início: um aviso que nasce já pronto não é anunciado. */}
      <div role="alert">
        {alert && (
          <div className="flex flex-col items-start gap-3 rounded-control bg-attention-bg px-3 py-2.5 text-body-sm text-attention-ink">
            <p className="flex items-start gap-2">
              <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
              {alert.text}
            </p>
            {alert.kind === 'conflict' && (
              <Button
                type="button"
                variant="secondary"
                size="sm"
                disabled={isFetching}
                onClick={reloadLatest}
              >
                {copy.errors.conflictReload}
              </Button>
            )}
          </div>
        )}
      </div>

      <DialogFooter>
        <Button type="button" variant="ghost" onClick={onDone}>
          {copy.form.cancel}
        </Button>
        <Button type="submit" loading={update.isPending}>
          {copy.form.save}
        </Button>
      </DialogFooter>
    </form>
  )
}

function Confirmation({
  fieldKey,
  before,
  after,
  saving,
  onBack,
  onConfirm,
}: {
  fieldKey: BaselineKey
  before: string | null
  after: string | null
  saving: boolean
  onBack: () => void
  onConfirm: () => void
}) {
  const impact = fieldKey === 'date' ? copy.confirm.impact.date : null
  return (
    <div className="flex flex-col gap-5">
      <h3 className="text-heading text-ink">{copy.confirm.title}</h3>
      <dl className="flex flex-col gap-3">
        <div>
          <dt className="text-eyebrow text-ink-muted">{copy.confirm.before}</dt>
          <dd className="text-body text-ink">{before ?? copy.history.noValue}</dd>
        </div>
        <div>
          <dt className="text-eyebrow text-ink-muted">{copy.confirm.after}</dt>
          <dd className="text-body text-ink">{after ?? copy.history.noValue}</dd>
        </div>
      </dl>
      <div className="flex flex-col gap-1 text-body-sm text-ink-muted">
        {impact && <p>{impact}</p>}
        <p>{copy.confirm.history}</p>
      </div>
      <DialogFooter>
        <Button type="button" variant="ghost" onClick={onBack}>
          {copy.confirm.back}
        </Button>
        <Button type="button" loading={saving} onClick={onConfirm}>
          {copy.confirm.confirm}
        </Button>
      </DialogFooter>
    </div>
  )
}
