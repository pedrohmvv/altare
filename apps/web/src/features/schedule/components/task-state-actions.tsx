import { useQueryClient } from '@tanstack/react-query'
import { useEffect, useId, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { findTask, type ScheduleTask, scheduleKeys, type TaskState } from '../api/schedule'
import { useChangeTaskState } from '../api/use-task-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import { isOpenItemsError, openItemsCount } from '../lib/open-items'
import { FormAlert } from './form-alert'
import { OpenItemsConfirmation } from './open-items-confirmation'

const labels = copy.task.actions

const STATE_ALERTS = {
  conflict: copy.task.stateConflict,
  network: copy.task.stateNetwork,
}

/**
 * Marcar em andamento, concluir e reabrir a avulsa (F-CRN-06): todo estado vale a qualquer momento e reabrir
 * volta a `A fazer`, sem confirmação. A única confirmação é concluir com itens do checklist em
 * aberto (F-CRN-07). Nada é otimista: o estado só muda quando o servidor responde.
 */
export function TaskStateActions({ task }: { task: ScheduleTask }) {
  const change = useChangeTaskState()
  const queryClient = useQueryClient()
  const [confirming, setConfirming] = useState(false)
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const [done, setDone] = useState('')
  // O botão que tinha o foco some quando o estado muda: o foco vai ao título da seção, que fica.
  const title = useRef<HTMLHeadingElement>(null)
  // A confirmação não tem gatilho no Radix: guardamos o botão que a abriu para devolver o foco.
  const origin = useRef<HTMLElement | null>(null)
  const confirmed = useRef(false)
  const openItems = openItemsCount(task.checklist_progress)
  const titleId = useId()
  // Se uma releitura em segundo plano zera os itens em aberto com a confirmação aberta, ela já não
  // tem o que dizer: fecha e leva o foco ao título, que fica.
  const previousOpen = useRef(openItems)
  useEffect(() => {
    if (confirming && previousOpen.current > 0 && openItems === 0) {
      // O Radix devolve o foco ao fechar: `confirmed` o manda ao título, e não ao botão de origem.
      confirmed.current = true
      setConfirming(false)
      title.current?.focus()
    }
    previousOpen.current = openItems
  }, [confirming, openItems])

  function send(state: TaskState, options: { fromDialog: boolean; ignoreOpenItems?: boolean }) {
    setAlert(null)
    setDone('')
    change.mutate(
      {
        taskId: task.id,
        state,
        ignoreOpenItems: options.ignoreOpenItems ?? false,
        version: task.version,
      },
      {
        onSuccess: () => {
          if (options.fromDialog) confirmed.current = true
          else title.current?.focus()
          setConfirming(false)
          setDone(copy.task.done[state === 'A fazer' ? 'reopened' : state])
        },
        onError: (error) => {
          setConfirming(false)
          if (isOpenItemsError(error)) return void askAgainAfterReading()
          setAlert(alertFromError(error, STATE_ALERTS))
        },
      },
    )
  }

  // O servidor viu itens em aberto que a tela não via: lê de novo e confirma com a contagem nova.
  async function askAgainAfterReading() {
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    const latest = findTask(queryClient.getQueryData(scheduleKeys.all), task.id)
    if (latest && openItemsCount(latest.checklist_progress) > 0) {
      confirmed.current = false
      return setConfirming(true)
    }
    setAlert({ kind: 'error', text: copy.confirm.openItems.stale })
  }

  function ask(state: TaskState, from: HTMLElement) {
    origin.current = from
    confirmed.current = false
    if (state === 'Concluída' && openItems > 0) return setConfirming(true)
    send(state, { fromDialog: false })
  }

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    setReloading(false)
    setAlert(null)
  }

  // Sem `DialogTrigger` o Radix não devolve o foco: ao título da seção se concluiu (o botão some),
  // e ao botão de origem se cancelou, desde que ele ainda esteja na tela.
  function afterConfirmation(event: Event) {
    event.preventDefault()
    const from = origin.current
    const target = !confirmed.current && from?.isConnected ? from : title.current
    confirmed.current = false
    target?.focus()
  }

  const pending = (state: TaskState) => change.isPending && change.variables?.state === state
  const state = task.state

  return (
    <section aria-labelledby={titleId} className="flex flex-col gap-3">
      <h3 ref={title} tabIndex={-1} id={titleId} className="text-body font-semibold text-ink">
        {copy.sheet.stateTitle}
      </h3>
      <div className="flex flex-wrap gap-3">
        {state === 'A fazer' && (
          <Button
            variant="secondary"
            onClick={(event) => ask('Em andamento', event.currentTarget)}
            loading={pending('Em andamento')}
            disabled={change.isPending}
          >
            {labels.start}
          </Button>
        )}
        {state !== 'Concluída' && (
          <Button
            onClick={(event) => ask('Concluída', event.currentTarget)}
            loading={pending('Concluída')}
            disabled={change.isPending}
          >
            {labels.done}
          </Button>
        )}
        {state !== 'A fazer' && (
          <Button
            variant="secondary"
            onClick={(event) => ask('A fazer', event.currentTarget)}
            loading={pending('A fazer')}
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
      <Dialog open={confirming} onOpenChange={(open) => !open && setConfirming(false)}>
        {openItems > 0 && (
          <OpenItemsConfirmation
            onCloseAutoFocus={afterConfirmation}
            openItems={openItems}
            loading={change.isPending}
            onCancel={() => setConfirming(false)}
            onConfirm={() => send('Concluída', { fromDialog: true, ignoreOpenItems: true })}
          />
        )}
      </Dialog>
    </section>
  )
}
