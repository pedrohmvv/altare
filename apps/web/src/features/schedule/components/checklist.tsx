import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useEffect, useId, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { ApiError } from '@/lib/api/errors'
import {
  type ChecklistItem,
  type ChecklistOwner,
  type ChecklistProgress,
  scheduleKeys,
} from '../api/schedule'
import {
  useAddChecklistItem,
  useRemoveChecklistItem,
  useReorderChecklist,
  useUpdateChecklistItem,
} from '../api/use-checklist-mutations'
import { copy } from '../copy'
import { type AlertState, checklistAlertFromError } from '../lib/errors'
import { type ChecklistTextValues, checklistTextSchema } from '../schemas/checklist-form'
import { FormAlert } from './form-alert'

const text = copy.checklist

type Direction = 'up' | 'down'

export interface ChecklistProps {
  /** De quem é o checklist: o marco ou a avulsa. */
  owner: ChecklistOwner
  items: readonly ChecklistItem[]
  progress: ChecklistProgress
}

/**
 * O checklist de subtarefas (F-CRN-07), o mesmo no marco e na avulsa: marcar, editar o texto,
 * reordenar (Subir e Descer, sem arrastar), remover e adicionar. Nada é otimista; as escritas usam
 * um escopo serial, uma depois da outra. Marcar não muda o estado do dono, e remover não se desfaz.
 */
export function Checklist({ owner, items, progress }: ChecklistProps) {
  const titleId = useId()
  const queryClient = useQueryClient()
  // O botão que tinha o foco some ao remover: o foco vai ao título da seção, que fica.
  const heading = useRef<HTMLHeadingElement>(null)
  const reorder = useReorderChecklist()
  const add = useAddChecklistItem()
  const remove = useRemoveChecklistItem()
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [done, setDone] = useState('')
  const [reloading, setReloading] = useState(false)
  // Depois de recarregar, as linhas voltam a mostrar os textos de agora.
  const [reloadKey, setReloadKey] = useState(0)
  const buttons = useRef(new Map<string, HTMLButtonElement>())
  const [followFocus, setFollowFocus] = useState<{
    id: string
    direction: Direction
    /** A ordem que a tela espera ver: o cache pode chegar à tela depois da resposta. */
    order: string
  } | null>(null)

  // O foco acompanha o item movido: o botão que ele tinha, ou o outro se este já não pode agir.
  useEffect(() => {
    if (!followFocus || reorder.isPending) return
    if (items.map((item) => item.id).join() !== followFocus.order) return
    const same = buttons.current.get(`${followFocus.id}:${followFocus.direction}`)
    const other = buttons.current.get(
      `${followFocus.id}:${followFocus.direction === 'up' ? 'down' : 'up'}`,
    )
    ;(same && !same.disabled ? same : other)?.focus()
    setFollowFocus(null)
  }, [followFocus, reorder.isPending, items])

  function start() {
    setAlert(null)
    setDone('')
  }

  function move(index: number, direction: Direction) {
    const ids = items.map((item) => item.id)
    const [moved] = ids.splice(index, 1)
    if (moved === undefined) return
    ids.splice(direction === 'up' ? index - 1 : index + 1, 0, moved)
    start()
    reorder.mutate(
      { owner, ids },
      {
        onSuccess: () => {
          setDone(text.moved)
          setFollowFocus({ id: moved, direction, order: ids.join() })
        },
        onError: (error) => setAlert(checklistAlertFromError(error)),
      },
    )
  }

  function removeItem(item: ChecklistItem) {
    start()
    remove.mutate(
      { itemId: item.id, version: item.version },
      {
        onSuccess: () => {
          heading.current?.focus()
          setDone(text.removed)
        },
        onError: (error) => setAlert(checklistAlertFromError(error)),
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
    <section aria-labelledby={titleId} className="flex flex-col gap-3">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3">
        <h3 ref={heading} tabIndex={-1} id={titleId} className="text-body font-semibold text-ink">
          {text.title}
        </h3>
        {progress.total > 0 && (
          <span className="text-num-sm text-ink-muted">
            {text.progress(progress.done, progress.total)}
          </span>
        )}
      </div>
      {items.length === 0 ? (
        <p className="text-body-sm text-ink-muted">{text.empty}</p>
      ) : (
        <ul aria-labelledby={titleId} className="flex flex-col gap-3">
          {items.map((item, index) => (
            <ChecklistRow
              key={`${item.id}-${reloadKey}`}
              item={item}
              canMoveUp={index > 0}
              canMoveDown={index < items.length - 1}
              // Reordenar com uma adição ou remoção pendente enviaria uma lista que já não é a do
              // servidor (ordem inválida): a reordenação espera qualquer escrita de lista.
              busy={reorder.isPending || add.isPending || remove.isPending}
              removing={remove.isPending && remove.variables?.itemId === item.id}
              onMove={(direction) => move(index, direction)}
              onRemove={() => removeItem(item)}
              register={(direction, element) => {
                const key = `${item.id}:${direction}`
                if (element) buttons.current.set(key, element)
                else buttons.current.delete(key)
              }}
              onStart={start}
              onSaved={(message) => setDone(message)}
              onFailed={(error) => setAlert(checklistAlertFromError(error))}
            />
          ))}
        </ul>
      )}
      <NewItem
        owner={owner}
        add={add}
        onStart={start}
        onAdded={() => setDone(text.added)}
        onFailed={(error) => setAlert(checklistAlertFromError(error))}
      />
      <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
      <p role="status" className="text-body-sm text-consensus-ink">
        {done}
      </p>
    </section>
  )
}

interface RowProps {
  item: ChecklistItem
  canMoveUp: boolean
  canMoveDown: boolean
  busy: boolean
  /** O item está sendo removido: marcar agora entraria na fila depois da remoção. */
  removing: boolean
  onMove: (direction: Direction) => void
  onRemove: () => void
  register: (direction: Direction, element: HTMLButtonElement | null) => void
  onStart: () => void
  onSaved: (message: string) => void
  onFailed: (error: unknown) => void
}

function ChecklistRow({
  item,
  canMoveUp,
  canMoveDown,
  busy,
  removing,
  onMove,
  onRemove,
  register,
  onStart,
  onSaved,
  onFailed,
}: RowProps) {
  const update = useUpdateChecklistItem()
  const checkboxId = useId()
  const edit = useRef<HTMLButtonElement>(null)
  const [editing, setEditing] = useState(false)
  // O item de quando a edição abriu: um conflito nunca troca o que foi digitado. A versão enviada é
  // a dele, a não ser que o texto continue o mesmo (marcar também sobe a versão do item).
  const [opened, setOpened] = useState(item)
  const form = useForm<ChecklistTextValues>({
    resolver: zodResolver(checklistTextSchema),
    mode: 'onTouched',
    defaultValues: { text: item.text },
  })
  const version = opened.text === item.text ? item.version : opened.version

  function openEditor() {
    setOpened(item)
    form.reset({ text: item.text })
    setEditing(true)
  }

  function closeEditor() {
    setEditing(false)
    // O campo some: o foco volta ao botão que o abriu.
    setTimeout(() => edit.current?.focus(), 0)
  }

  function toggle(done: boolean) {
    // A caixa fica desabilitada enquanto espera e perderia o foco: ela o recebe de volta depois.
    const hadFocus = document.activeElement?.id === checkboxId
    onStart()
    update.mutate(
      { itemId: item.id, text: item.text, done, version: item.version },
      {
        onSuccess: () => {
          if (hadFocus) setTimeout(() => document.getElementById(checkboxId)?.focus(), 0)
        },
        onError: onFailed,
      },
    )
  }

  const submit = form.handleSubmit(({ text: next }) => {
    onStart()
    update.mutate(
      { itemId: item.id, text: next, done: item.done, version },
      {
        onSuccess: () => {
          onSaved(text.saved)
          closeEditor()
        },
        onError: (error) => {
          if (error instanceof ApiError && error.code === 'checklist_text_required') {
            form.setError('text', { message: error.message }, { shouldFocus: true })
            return
          }
          onFailed(error)
        },
      },
    )
  })

  if (editing) {
    return (
      <li className="flex flex-col gap-2">
        <form onSubmit={submit} noValidate className="flex flex-col gap-2">
          <Input
            label={text.textLabel}
            autoComplete="off"
            autoFocus
            error={form.formState.errors.text?.message}
            {...form.register('text')}
          />
          <div className="flex flex-wrap gap-2">
            <Button
              type="submit"
              variant="secondary"
              size="sm"
              aria-label={text.saveFor(opened.text)}
              loading={update.isPending}
            >
              {text.save}
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              aria-label={text.cancelFor(opened.text)}
              onClick={closeEditor}
            >
              {text.cancel}
            </Button>
          </div>
        </form>
      </li>
    )
  }

  // Enquanto a escrita do item espera, Remover mandaria a versão de antes dela e daria 409 provocado
  // pela própria tela: tudo da linha fica parado até a resposta.
  const pending = update.isPending
  const locked = busy || pending
  return (
    <li className="flex flex-col gap-2">
      <Checkbox
        id={checkboxId}
        label={item.text}
        checked={item.done}
        disabled={pending || removing}
        onCheckedChange={(checked) => toggle(checked === true)}
      />
      <div className="flex flex-wrap gap-2">
        <Button
          ref={edit}
          variant="ghost"
          size="sm"
          aria-label={text.editFor(item.text)}
          disabled={locked}
          onClick={openEditor}
        >
          {text.edit}
        </Button>
        <Button
          ref={(element) => register('up', element)}
          variant="ghost"
          size="sm"
          aria-label={text.upFor(item.text)}
          disabled={!canMoveUp || locked}
          onClick={() => onMove('up')}
        >
          {text.up}
        </Button>
        <Button
          ref={(element) => register('down', element)}
          variant="ghost"
          size="sm"
          aria-label={text.downFor(item.text)}
          disabled={!canMoveDown || locked}
          onClick={() => onMove('down')}
        >
          {text.down}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          aria-label={text.removeFor(item.text)}
          disabled={locked}
          onClick={onRemove}
        >
          {text.remove}
        </Button>
      </div>
    </li>
  )
}

function NewItem({
  owner,
  add,
  onStart,
  onAdded,
  onFailed,
}: {
  owner: ChecklistOwner
  add: ReturnType<typeof useAddChecklistItem>
  onStart: () => void
  onAdded: () => void
  onFailed: (error: unknown) => void
}) {
  const form = useForm<ChecklistTextValues>({
    resolver: zodResolver(checklistTextSchema),
    // Só ao adicionar: o campo vazio é o estado normal de quem já terminou a lista.
    mode: 'onSubmit',
    defaultValues: { text: '' },
  })

  const submit = form.handleSubmit(({ text: next }) => {
    onStart()
    add.mutate(
      { owner, text: next },
      {
        onSuccess: () => {
          form.reset({ text: '' })
          onAdded()
          // O botão de enviar estava ocupado e perdeu o foco: ele volta ao campo, pronto para o próximo.
          setTimeout(() => form.setFocus('text'), 0)
        },
        onError: (error) => {
          if (error instanceof ApiError && error.code === 'checklist_text_required') {
            form.setError('text', { message: error.message }, { shouldFocus: true })
            return
          }
          onFailed(error)
        },
      },
    )
  })

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-2">
      <Input
        label={text.newLabel}
        autoComplete="off"
        error={form.formState.errors.text?.message}
        {...form.register('text')}
      />
      <Button
        type="submit"
        variant="secondary"
        size="sm"
        className="self-start"
        loading={add.isPending}
      >
        {text.add}
      </Button>
    </form>
  )
}
