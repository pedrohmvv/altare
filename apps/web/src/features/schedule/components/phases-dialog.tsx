import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { ApiError } from '@/lib/api/errors'
import { type SchedulePhase, scheduleKeys } from '../api/schedule'
import { useCreatePhase, useRenamePhase, useReorderPhases } from '../api/use-milestone-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import { type PhaseTitleValues, phaseTitleSchema } from '../schemas/milestone-form'
import { FormAlert } from './form-alert'

const text = copy.phases

const ALERTS = {
  conflict: text.errors.conflict,
  network: text.errors.network,
}

type Direction = 'up' | 'down'

export interface PhasesDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  phases: readonly SchedulePhase[]
  onCloseAutoFocus: (event: Event) => void
}

/**
 * As fases do cronograma (F-CRN-01): renomear, subir e descer (sem arrastar) e criar uma nova no
 * fim. Não há excluir fase. Reordenar envia a lista completa de ids; nada é otimista.
 */
export function PhasesDialog({ open, onOpenChange, phases, onCloseAutoFocus }: PhasesDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title={text.title}
        description={text.description}
        onCloseAutoFocus={onCloseAutoFocus}
      >
        <PhasesEditor phases={phases} />
      </DialogContent>
    </Dialog>
  )
}

function PhasesEditor({ phases }: { phases: readonly SchedulePhase[] }) {
  const queryClient = useQueryClient()
  const reorder = useReorderPhases()
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [done, setDone] = useState('')
  const [reloading, setReloading] = useState(false)
  // Depois de recarregar, os campos voltam a mostrar os nomes de agora.
  const [reloadKey, setReloadKey] = useState(0)
  const buttons = useRef(new Map<string, HTMLButtonElement>())
  const [followFocus, setFollowFocus] = useState<{
    id: string
    direction: Direction
    /** A ordem que a tela espera ver: o cache pode chegar à tela depois da resposta. */
    order: string
  } | null>(null)

  // O foco acompanha a fase movida: o botão que ela tinha, ou o outro se este já não pode agir.
  useEffect(() => {
    if (!followFocus || reorder.isPending) return
    if (phases.map((phase) => phase.id).join() !== followFocus.order) return
    const same = buttons.current.get(`${followFocus.id}:${followFocus.direction}`)
    const other = buttons.current.get(
      `${followFocus.id}:${followFocus.direction === 'up' ? 'down' : 'up'}`,
    )
    ;(same && !same.disabled ? same : other)?.focus()
    setFollowFocus(null)
  }, [followFocus, reorder.isPending, phases])

  function move(index: number, direction: Direction) {
    const ids = phases.map((phase) => phase.id)
    const target = direction === 'up' ? index - 1 : index + 1
    const [moved] = ids.splice(index, 1)
    if (moved === undefined) return
    ids.splice(target, 0, moved)
    setAlert(null)
    setDone('')
    reorder.mutate(
      { ids },
      {
        onSuccess: () => {
          setDone(text.moved)
          setFollowFocus({ id: moved, direction, order: ids.join() })
        },
        onError: (error) => setAlert(alertFromError(error, ALERTS)),
      },
    )
  }

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    setReloading(false)
    setAlert(null)
    setReloadKey((key) => key + 1)
  }

  return (
    <div className="flex flex-col gap-5">
      <section aria-labelledby="phases-list-title" className="flex flex-col gap-3">
        <h3 id="phases-list-title" className="text-body font-semibold text-ink">
          {text.listTitle}
        </h3>
        <ul className="flex flex-col gap-4">
          {phases.map((phase, index) => (
            <PhaseRow
              key={`${phase.id}-${reloadKey}`}
              phase={phase}
              number={index + 1}
              canMoveUp={index > 0}
              canMoveDown={index < phases.length - 1}
              busy={reorder.isPending}
              onMove={(direction) => move(index, direction)}
              register={(direction, element) => {
                const key = `${phase.id}:${direction}`
                if (element) buttons.current.set(key, element)
                else buttons.current.delete(key)
              }}
              onSaved={() => {
                setAlert(null)
                setDone(text.renamed)
              }}
              onFailed={(error) => setAlert(alertFromError(error, ALERTS))}
              onStart={() => {
                setAlert(null)
                setDone('')
              }}
            />
          ))}
        </ul>
      </section>
      <NewPhase
        onCreated={() => {
          setAlert(null)
          setDone(text.createdPhase)
        }}
        onFailed={(error) => setAlert(alertFromError(error, ALERTS))}
        onStart={() => {
          setAlert(null)
          setDone('')
        }}
      />
      <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
      <p role="status" className="text-body-sm text-consensus-ink">
        {done}
      </p>
    </div>
  )
}

interface PhaseRowProps {
  phase: SchedulePhase
  number: number
  canMoveUp: boolean
  canMoveDown: boolean
  busy: boolean
  onMove: (direction: Direction) => void
  register: (direction: Direction, element: HTMLButtonElement | null) => void
  onStart: () => void
  onSaved: () => void
  onFailed: (error: unknown) => void
}

function PhaseRow({
  phase,
  number,
  canMoveUp,
  canMoveDown,
  busy,
  onMove,
  register,
  onStart,
  onSaved,
  onFailed,
}: PhaseRowProps) {
  const rename = useRenamePhase()
  // A fase de quando a linha abriu: um conflito nunca troca o que foi digitado. A versão enviada é
  // a dela, a não ser que o nome continue o mesmo (outra ação, como reordenar, pode tê-la subido).
  const [opened, setOpened] = useState(phase)
  const form = useForm<PhaseTitleValues>({
    resolver: zodResolver(phaseTitleSchema),
    mode: 'onTouched',
    defaultValues: { title: phase.title },
  })
  const version = opened.title === phase.title ? phase.version : opened.version

  const submit = form.handleSubmit(({ title }) => {
    onStart()
    rename.mutate(
      { phaseId: phase.id, title, version },
      {
        onSuccess: (schedule) => {
          const latest = schedule.phases.find((item) => item.id === phase.id)
          if (latest) {
            setOpened(latest)
            form.reset({ title: latest.title })
          }
          onSaved()
        },
        onError: (error) => {
          if (error instanceof ApiError && error.code === 'phase_title_required') {
            form.setError('title', { message: error.message }, { shouldFocus: true })
            return
          }
          onFailed(error)
        },
      },
    )
  })

  return (
    <li className="flex flex-col gap-2 md:flex-row md:items-end">
      <form
        onSubmit={submit}
        noValidate
        className="flex flex-col gap-2 md:flex-1 md:flex-row md:items-end"
      >
        <Input
          label={copy.phase.label(number)}
          required
          className="md:flex-1"
          autoComplete="off"
          error={form.formState.errors.title?.message}
          {...form.register('title')}
        />
        <Button
          type="submit"
          variant="secondary"
          size="sm"
          className="self-start md:shrink-0 md:self-auto"
          aria-label={text.saveFor(phase.title)}
          loading={rename.isPending}
        >
          {text.save}
        </Button>
      </form>
      <div className="flex gap-2 md:shrink-0">
        <Button
          ref={(element) => register('up', element)}
          variant="ghost"
          size="sm"
          aria-label={text.upFor(phase.title)}
          disabled={!canMoveUp || busy}
          onClick={() => onMove('up')}
        >
          {text.up}
        </Button>
        <Button
          ref={(element) => register('down', element)}
          variant="ghost"
          size="sm"
          aria-label={text.downFor(phase.title)}
          disabled={!canMoveDown || busy}
          onClick={() => onMove('down')}
        >
          {text.down}
        </Button>
      </div>
    </li>
  )
}

function NewPhase({
  onStart,
  onCreated,
  onFailed,
}: {
  onStart: () => void
  onCreated: () => void
  onFailed: (error: unknown) => void
}) {
  const create = useCreatePhase()
  const form = useForm<PhaseTitleValues>({
    resolver: zodResolver(phaseTitleSchema),
    mode: 'onTouched',
    defaultValues: { title: '' },
  })

  const submit = form.handleSubmit(({ title }) => {
    onStart()
    create.mutate(
      { title },
      {
        onSuccess: () => {
          form.reset({ title: '' })
          onCreated()
        },
        onError: (error) => {
          if (error instanceof ApiError && error.code === 'phase_title_required') {
            form.setError('title', { message: error.message }, { shouldFocus: true })
            return
          }
          onFailed(error)
        },
      },
    )
  })

  return (
    <section aria-labelledby="phases-new-title" className="flex flex-col gap-3">
      <h3 id="phases-new-title" className="text-body font-semibold text-ink">
        {text.newTitle}
      </h3>
      <form onSubmit={submit} noValidate className="flex flex-col gap-2">
        <Input
          label={text.newLabel}
          required
          autoComplete="off"
          error={form.formState.errors.title?.message}
          {...form.register('title')}
        />
        <Button
          type="submit"
          variant="secondary"
          size="sm"
          className="self-start"
          loading={create.isPending}
        >
          {text.add}
        </Button>
      </form>
    </section>
  )
}
