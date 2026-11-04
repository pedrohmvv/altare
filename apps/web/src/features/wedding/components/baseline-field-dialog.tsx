import { zodResolver } from '@hookform/resolvers/zod'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { CircleAlert } from 'lucide-react'
import { type ReactNode, useEffect, useMemo, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter } from '@/components/ui/dialog'
import { ApiError } from '@/lib/api/errors'
import { type Baseline, type BaselineKey, baselineQueryOptions } from '../api/baseline'
import { useDateImpact } from '../api/use-date-impact'
import { useUpdateBaselineField } from '../api/use-update-baseline-field'
import { copy } from '../copy'
import { describeValue } from '../lib/describe-value'
import { type FormValues, makeSchema, toFormValues, toUpdate } from '../schemas/baseline-form'
import { StatusFields, ValueFields } from './baseline-value-fields'
import { DateImpact } from './date-impact'

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
  // A prévia só faz sentido na confirmação da data, com a data que o formulário tem agora (o estado
  // depois da mudança): só uma data exata `Definida` dá Modo Com Data; qualquer outra é Sem Data.
  const impact = useDateImpact(
    pending?.dateKind === 'exata' && pending.status === 'Definido' ? pending.exact : undefined,
    fieldKey === 'date' && pending !== null,
  )
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
        before={describeValue(fieldKey, opened[fieldKey].value)}
        after={describeValue(fieldKey, toUpdate(fieldKey, pending, version).body.value)}
        impact={
          fieldKey === 'date' ? <DateImpact data={impact.data} failed={impact.isError} /> : null
        }
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
  before,
  after,
  impact,
  saving,
  onBack,
  onConfirm,
}: {
  before: string | null
  after: string | null
  /** O que a mudança faz em outra área; só a data tem. */
  impact: ReactNode
  saving: boolean
  onBack: () => void
  onConfirm: () => void
}) {
  // O formulário sai e a confirmação entra: o foco vai ao título dela, que o leitor de tela lê.
  const heading = useRef<HTMLHeadingElement>(null)
  useEffect(() => heading.current?.focus(), [])
  return (
    <div className="flex flex-col gap-5">
      <h3 ref={heading} tabIndex={-1} className="text-heading text-ink">
        {copy.confirm.title}
      </h3>
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
        {impact}
        <p>{copy.confirm.history}</p>
      </div>
      {/* No celular a confirmação rola: o rodapé fica à vista, para o confirmar nunca ficar abaixo da dobra. */}
      <DialogFooter className="max-md:sticky max-md:-bottom-5 max-md:-mb-5 max-md:border-t max-md:border-border max-md:bg-surface max-md:pt-3 max-md:pb-5">
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
