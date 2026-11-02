import { useQueryClient } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter } from '@/components/ui/dialog'
import { type ManualState, type ScheduleMilestone, scheduleKeys } from '../api/schedule'
import { useChangeMilestoneState } from '../api/use-milestone-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import { FormAlert } from './form-alert'

const labels = copy.sheet.actions
type Confirmation = 'start' | 'done' | 'reopen'

const STATE_ALERTS = {
  conflict: copy.sheet.stateConflict,
  blocked: copy.sheet.stateBlocked,
  network: copy.sheet.stateNetwork,
}

/**
 * Marcar em andamento, concluir e reabrir (F-CRN-03). O estado e o bloqueio vêm da API; a tela só
 * pede a confirmação que a regra manda: ignorar o bloqueio, ou avisar o que reabrir devolve ao
 * bloqueio. Nada é otimista: o estado só muda quando o servidor responde.
 */
export function MilestoneStateActions({ milestone }: { milestone: ScheduleMilestone }) {
  const change = useChangeMilestoneState()
  const queryClient = useQueryClient()
  const [confirming, setConfirming] = useState<Confirmation | null>(null)
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const [done, setDone] = useState('')
  // O botão que tinha o foco some quando o estado muda: o foco vai ao título da seção, que fica.
  const title = useRef<HTMLHeadingElement>(null)
  // A confirmação não tem gatilho no Radix: guardamos o botão que a abriu para devolver o foco.
  const origin = useRef<HTMLElement | null>(null)
  const confirmed = useRef(false)
  const waiting = milestone.blocked_by.length > 0

  function send(
    state: ManualState | null,
    ignoreBlock: boolean,
    options: { fromDialog: boolean } = { fromDialog: false },
  ) {
    setAlert(null)
    setDone('')
    change.mutate(
      { milestoneId: milestone.id, state, ignoreBlock, version: milestone.version },
      {
        onSuccess: () => {
          if (options.fromDialog) confirmed.current = true
          else title.current?.focus()
          setConfirming(null)
          setDone(copy.sheet.done[state ?? 'reopened'])
        },
        onError: (error) => {
          setConfirming(null)
          setAlert(alertFromError(error, STATE_ALERTS))
        },
      },
    )
  }

  function ask(state: ManualState | null, from: HTMLElement) {
    origin.current = from
    confirmed.current = false
    if (state !== null && waiting) return setConfirming(state === 'Concluído' ? 'done' : 'start')
    if (state === null && milestone.state === 'Concluído' && milestone.unlocks.length > 0) {
      return setConfirming('reopen')
    }
    send(state, false)
  }

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    setReloading(false)
    setAlert(null)
  }

  // Sem `DialogTrigger` o Radix não devolve o foco, então a tela o leva: ao título da seção se a
  // ação foi confirmada (o botão de origem muda ou some); ao botão de origem se foi cancelada
  // (botão, Esc ou clique fora) ou deu erro, desde que ele ainda esteja na tela.
  function afterConfirmation(event: Event) {
    event.preventDefault()
    const from = origin.current
    const target = !confirmed.current && from?.isConnected ? from : title.current
    confirmed.current = false
    target?.focus()
  }

  const pending = (state: ManualState | null) =>
    change.isPending && change.variables?.state === state
  const state = milestone.state
  const canStart = state === 'Bloqueado' || state === 'Destravado'
  const canFinish = state !== 'Concluído'
  const canReopen = state === 'Em andamento' || state === 'Concluído'

  return (
    <section aria-label={copy.sheet.stateTitle} className="flex flex-col gap-3">
      <h3 ref={title} tabIndex={-1} className="text-body font-semibold text-ink">
        {copy.sheet.stateTitle}
      </h3>
      <div className="flex flex-wrap gap-3">
        {canStart && (
          <Button
            variant="secondary"
            onClick={(event) => ask('Em andamento', event.currentTarget)}
            loading={pending('Em andamento')}
            disabled={change.isPending}
          >
            {labels.start}
          </Button>
        )}
        {canFinish && (
          <Button
            onClick={(event) => ask('Concluído', event.currentTarget)}
            loading={pending('Concluído')}
            disabled={change.isPending}
          >
            {labels.done}
          </Button>
        )}
        {canReopen && (
          <Button
            variant="secondary"
            onClick={(event) => ask(null, event.currentTarget)}
            loading={pending(null)}
            disabled={change.isPending}
          >
            {labels.reopen}
          </Button>
        )}
      </div>
      <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
      <p role="status" className="text-body-sm text-consensus-ink">
        {done}
      </p>
      <Dialog open={confirming !== null} onOpenChange={(open) => !open && setConfirming(null)}>
        {confirming === 'reopen' ? (
          <ReopenConfirmation
            onCloseAutoFocus={afterConfirmation}
            milestone={milestone}
            loading={change.isPending}
            onCancel={() => setConfirming(null)}
            onConfirm={() => send(null, false, { fromDialog: true })}
          />
        ) : confirming ? (
          <IgnoreBlockConfirmation
            onCloseAutoFocus={afterConfirmation}
            milestone={milestone}
            kind={confirming}
            loading={change.isPending}
            onCancel={() => setConfirming(null)}
            onConfirm={() =>
              send(confirming === 'done' ? 'Concluído' : 'Em andamento', true, { fromDialog: true })
            }
          />
        ) : null}
      </Dialog>
    </section>
  )
}

interface ConfirmationProps {
  milestone: ScheduleMilestone
  onCloseAutoFocus: (event: Event) => void
  loading: boolean
  onCancel: () => void
  onConfirm: () => void
}

function IgnoreBlockConfirmation({
  milestone,
  kind,
  loading,
  onCancel,
  onConfirm,
  onCloseAutoFocus,
}: ConfirmationProps & { kind: 'start' | 'done' }) {
  const text = copy.confirm.ignoreBlock
  return (
    <DialogContent
      title={text.title}
      description={text.description}
      onCloseAutoFocus={onCloseAutoFocus}
    >
      <div className="flex flex-col gap-1">
        <h3 className="text-body-sm font-semibold text-ink">{text.waitingLabel}</h3>
        <ul className="flex flex-col gap-1">
          {milestone.blocked_by.map((blocker) => (
            <li
              key={`${blocker.kind}-${blocker.milestone_id}-${blocker.label}`}
              className="text-body text-ink"
            >
              {blocker.label}
            </li>
          ))}
        </ul>
      </div>
      <DialogFooter>
        <Button variant="ghost" onClick={onCancel}>
          {copy.confirm.cancel}
        </Button>
        <Button onClick={onConfirm} loading={loading}>
          {kind === 'done' ? text.done : text.start}
        </Button>
      </DialogFooter>
    </DialogContent>
  )
}

function ReopenConfirmation({
  milestone,
  loading,
  onCancel,
  onConfirm,
  onCloseAutoFocus,
}: ConfirmationProps) {
  const text = copy.confirm.reopen
  return (
    <DialogContent
      title={text.title}
      description={text.description}
      onCloseAutoFocus={onCloseAutoFocus}
    >
      <div className="flex flex-col gap-1">
        <h3 className="text-body-sm font-semibold text-ink">{text.unlocksLabel}</h3>
        <ul className="flex flex-col gap-1">
          {milestone.unlocks.map((unlocked) => (
            <li key={unlocked.id} className="text-body text-ink">
              {unlocked.title}
            </li>
          ))}
        </ul>
      </div>
      <DialogFooter>
        <Button variant="ghost" onClick={onCancel}>
          {copy.confirm.cancel}
        </Button>
        <Button onClick={onConfirm} loading={loading}>
          {text.confirm}
        </Button>
      </DialogFooter>
    </DialogContent>
  )
}
