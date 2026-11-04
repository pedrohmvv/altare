import { zodResolver } from '@hookform/resolvers/zod'
import { FileText, ImageIcon, Paperclip } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogFooter,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { formatBytes } from '@/lib/bytes'
import { formatInstant } from '@/lib/date'
import type { Attachment, ChecklistOwner } from '../api/schedule'
import {
  useAddFileAttachment,
  useAddLinkAttachment,
  useRemoveAttachment,
} from '../api/use-attachment-mutations'
import { copy } from '../copy'
import { type AlertState, attachmentAlertFromError, attachmentFieldOf } from '../lib/errors'
import {
  ATTACHMENT_FILE_TYPES,
  type AttachmentFileValues,
  type AttachmentLinkValues,
  attachmentFileSchema,
  attachmentLinkSchema,
} from '../schemas/attachment-form'
import { FormAlert } from './form-alert'

const text = copy.attachments

type FormKind = 'file' | 'link'
type FocusTarget = 'heading' | FormKind

const isHttp = (url: string) => /^https?:\/\/\S+$/i.test(url)
const filePath = (fileId: string) => `/api/v1/files/${fileId}`
const orNull = (value: string) => value.trim() || null

/** O nome que a pessoa reconhece: o título, ou o nome do arquivo, ou o domínio do link. */
function labelOf(item: Attachment): string {
  return item.title ?? item.file?.name ?? item.domain ?? item.url ?? text.title
}

export interface AttachmentsProps {
  /** De quem são os anexos: o marco ou a avulsa. */
  owner: ChecklistOwner
  items: readonly Attachment[]
}

/**
 * Os anexos do marco ou da avulsa (F-CRN-08): arquivos (PDF ou imagem) e links, com quem anexou e
 * quando. Sem miniatura nem visualizador: o arquivo e o link abrem em outra aba. Remover tira da
 * lista e deixa o registro guardado; não há Desfazer. O foco vai ao título depois de uma ação, porque
 * o botão que a pessoa usou some ou muda.
 */
export function Attachments({ owner, items }: AttachmentsProps) {
  const titleId = useId()
  const heading = useRef<HTMLHeadingElement>(null)
  const buttons = useRef<Record<FormKind, HTMLButtonElement | null>>({ file: null, link: null })
  const remove = useRemoveAttachment()
  const [adding, setAdding] = useState<FormKind | null>(null)
  const [returnFocus, setReturnFocus] = useState<FocusTarget | null>(null)
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [done, setDone] = useState('')
  const [sending, setSending] = useState(false)
  const [target, setTarget] = useState<Attachment | null>(null)
  const [confirming, setConfirming] = useState(false)
  const [removeAlert, setRemoveAlert] = useState<AlertState | null>(null)
  // Sem gatilho dentro do diálogo, o foco volta ao botão que o abriu, ou ao título se ele sumiu.
  const origin = useRef<HTMLElement | null>(null)
  const removed = useRef(false)

  // O formulário e os botões se alternam: o foco só vai depois que o novo estado está na tela.
  useEffect(() => {
    if (adding !== null || returnFocus === null) return
    const element = returnFocus === 'heading' ? heading.current : buttons.current[returnFocus]
    element?.focus()
    setReturnFocus(null)
  }, [adding, returnFocus])

  function start() {
    setAlert(null)
    setDone('')
  }

  function open(kind: FormKind) {
    start()
    setAdding(kind)
  }

  function finishAdding() {
    setSending(false)
    setDone(text.added)
    setReturnFocus('heading')
    setAdding(null)
  }

  function cancelAdding() {
    setSending(false)
    setAlert(null)
    setReturnFocus(adding)
    setAdding(null)
  }

  function askToRemove(item: Attachment, button: HTMLElement) {
    start()
    origin.current = button
    removed.current = false
    setRemoveAlert(null)
    setTarget(item)
    setConfirming(true)
  }

  function confirmRemoval() {
    if (!target) return
    setRemoveAlert(null)
    remove.mutate(
      { attachmentId: target.id },
      {
        onSuccess: () => {
          removed.current = true
          setDone(text.removed)
          setConfirming(false)
        },
        onError: (error) =>
          setRemoveAlert(attachmentAlertFromError(error, text.errors.removeNetwork)),
      },
    )
  }

  const formProps = {
    owner,
    onPending: setSending,
    onStart: start,
    onAdded: finishAdding,
    onCancel: cancelAdding,
    onFailed: (error: unknown) => setAlert(attachmentAlertFromError(error)),
  }

  return (
    <section aria-labelledby={titleId} className="flex flex-col gap-3">
      <h3 ref={heading} tabIndex={-1} id={titleId} className="text-body font-semibold text-ink">
        {text.title}
      </h3>
      {items.length === 0 ? (
        <p className="text-body-sm text-ink-muted">{text.empty}</p>
      ) : (
        <ul aria-labelledby={titleId} className="flex flex-col gap-2">
          {items.map((item) => (
            <AttachmentRow key={item.id} item={item} onRemove={askToRemove} />
          ))}
        </ul>
      )}
      {adding === null && (
        <div className="flex flex-wrap gap-2">
          <Button
            ref={(element) => {
              buttons.current.file = element
            }}
            variant="secondary"
            size="sm"
            onClick={() => open('file')}
          >
            {text.addFile}
          </Button>
          <Button
            ref={(element) => {
              buttons.current.link = element
            }}
            variant="secondary"
            size="sm"
            onClick={() => open('link')}
          >
            {text.addLink}
          </Button>
        </div>
      )}
      {adding === 'file' && <FileForm {...formProps} />}
      {adding === 'link' && <LinkForm {...formProps} />}
      <FormAlert alert={alert} />
      <p role="status" className="text-body-sm text-consensus-ink">
        {sending ? text.sending : done}
      </p>
      <AlertDialog
        open={confirming}
        onOpenChange={(next) => {
          setConfirming(next)
          if (!next) setRemoveAlert(null)
        }}
      >
        {target && (
          <AlertDialogContent
            title={text.removeDialog.title(labelOf(target))}
            description={text.removeDialog.description}
            pending={remove.isPending}
            onCloseAutoFocus={(event) => {
              event.preventDefault()
              const button = origin.current
              const next = !removed.current && button?.isConnected ? button : heading.current
              next?.focus()
            }}
          >
            <FormAlert alert={removeAlert} />
            <AlertDialogFooter>
              <AlertDialogCancel asChild>
                <Button variant="ghost" disabled={remove.isPending}>
                  {text.removeDialog.cancel}
                </Button>
              </AlertDialogCancel>
              <Button
                variant="soft-destructive"
                onClick={confirmRemoval}
                loading={remove.isPending}
              >
                {text.removeDialog.confirm}
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        )}
      </AlertDialog>
    </section>
  )
}

function iconOf(item: Attachment) {
  if (item.kind === 'link') return Paperclip
  return item.file?.content_type === 'application/pdf' ? FileText : ImageIcon
}

function hrefOf(item: Attachment): string | null {
  if (item.kind === 'file') return item.file ? filePath(item.file.id) : null
  // O endereço vem do banco: só http e https viram link; qualquer outro esquema é texto.
  return item.url && isHttp(item.url) ? item.url : null
}

function AttachmentRow({
  item,
  onRemove,
}: {
  item: Attachment
  onRemove: (item: Attachment, button: HTMLElement) => void
}) {
  const label = labelOf(item)
  const Icon = iconOf(item)
  const href = hrefOf(item)

  return (
    <li className="flex items-start gap-3 rounded-card border border-border bg-surface p-3">
      <Icon aria-hidden className="mt-0.5 size-5 shrink-0 text-ink" />
      <div className="flex min-w-0 flex-1 flex-col gap-0.5">
        {href ? (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-body font-medium break-words text-primary underline-offset-4 hover:underline pointer-coarse:flex pointer-coarse:min-h-11 pointer-coarse:items-center"
          >
            {label}
            <span className="sr-only"> {text.opensInNewTab}</span>
          </a>
        ) : (
          <p className="text-body font-medium break-words text-ink">{label}</p>
        )}
        {item.kind === 'file' && item.file && (
          <p className="text-ui-sm text-ink-muted">
            {item.title && <>{item.file.name} · </>}
            <span className="text-num-sm">{formatBytes(item.file.size_bytes)}</span>
          </p>
        )}
        {item.kind === 'link' && item.title && item.domain && (
          <p className="text-ui-sm text-ink-muted">{item.domain}</p>
        )}
        {item.comment && <p className="text-body-sm text-ink-muted">{item.comment}</p>}
        <p className="text-ui-xs text-ink-muted">
          {item.by} · {formatInstant(item.at)}
        </p>
      </div>
      {item.can_remove && (
        <Button
          variant="ghost"
          size="sm"
          aria-label={text.removeFor(label)}
          onClick={(event) => onRemove(item, event.currentTarget)}
        >
          {text.remove}
        </Button>
      )}
    </li>
  )
}

interface FormProps {
  owner: ChecklistOwner
  /** A escrita está no ar: a região de status anuncia o envio. */
  onPending: (pending: boolean) => void
  onStart: () => void
  onAdded: () => void
  onCancel: () => void
  onFailed: (error: unknown) => void
}

/** O erro da API num campo: a frase dela (`detail`), em português. */
const messageOf = (error: unknown) => (error instanceof Error ? error.message : '')

function LinkForm({ owner, onPending, onStart, onAdded, onCancel, onFailed }: FormProps) {
  const add = useAddLinkAttachment()
  const form = useForm<AttachmentLinkValues>({
    resolver: zodResolver(attachmentLinkSchema),
    mode: 'onTouched',
    defaultValues: { url: '', title: '', comment: '' },
  })
  const { errors } = form.formState

  useEffect(() => onPending(add.isPending), [add.isPending, onPending])

  const submit = form.handleSubmit(({ url, title, comment }) => {
    onStart()
    add.mutate(
      { owner, url, title: orNull(title), comment: orNull(comment) },
      {
        onSuccess: onAdded,
        onError: (error) => {
          if (attachmentFieldOf(error) === 'url') {
            form.setError('url', { message: messageOf(error) }, { shouldFocus: true })
            return
          }
          onFailed(error)
        },
      },
    )
  })

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-3">
      <Input
        label={text.link.label}
        hint={text.link.hint}
        inputMode="url"
        autoComplete="off"
        autoCapitalize="none"
        spellCheck={false}
        autoFocus
        error={errors.url?.message}
        {...form.register('url')}
      />
      <Input
        label={text.titleLabel}
        hint={text.optional}
        autoComplete="off"
        error={errors.title?.message}
        {...form.register('title')}
      />
      <Input
        label={text.commentLabel}
        hint={text.optional}
        autoComplete="off"
        error={errors.comment?.message}
        {...form.register('comment')}
      />
      <div className="flex flex-wrap gap-2">
        <Button type="submit" loading={add.isPending}>
          {text.link.submit}
        </Button>
        <Button
          type="button"
          variant="ghost"
          disabled={add.isPending}
          // Com `onTouched`, sair do campo vazio mostra o erro; ele empurraria o botão entre apertar e
          // soltar e o clique se perderia. Apertar o Cancelar não tira o foco do campo.
          onMouseDown={(event) => event.preventDefault()}
          onClick={onCancel}
        >
          {text.cancel}
        </Button>
      </div>
    </form>
  )
}

function FileForm({ owner, onPending, onStart, onAdded, onCancel, onFailed }: FormProps) {
  const add = useAddFileAttachment()
  const form = useForm<AttachmentFileValues>({
    resolver: zodResolver(attachmentFileSchema),
    mode: 'onTouched',
    defaultValues: { title: '', comment: '' },
  })
  const { errors } = form.formState

  useEffect(() => onPending(add.isPending), [add.isPending, onPending])

  const submit = form.handleSubmit(({ file, title, comment }) => {
    const chosen = file[0]
    if (!chosen) return
    onStart()
    add.mutate(
      { owner, file: chosen, title: orNull(title), comment: orNull(comment) },
      {
        onSuccess: onAdded,
        onError: (error) => {
          if (attachmentFieldOf(error) === 'file') {
            form.setError('file', { message: messageOf(error) }, { shouldFocus: true })
            return
          }
          onFailed(error)
        },
      },
    )
  })

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-3">
      {/* Sem `capture`: no celular o sistema oferece câmera, galeria ou arquivos. */}
      <Input
        label={text.file.label}
        hint={text.file.hint}
        type="file"
        accept={ATTACHMENT_FILE_TYPES.join(',')}
        autoFocus
        error={errors.file?.message}
        {...form.register('file')}
      />
      <Input
        label={text.titleLabel}
        hint={text.optional}
        autoComplete="off"
        error={errors.title?.message}
        {...form.register('title')}
      />
      <Input
        label={text.commentLabel}
        hint={text.optional}
        autoComplete="off"
        error={errors.comment?.message}
        {...form.register('comment')}
      />
      <div className="flex flex-wrap gap-2">
        <Button type="submit" loading={add.isPending}>
          {text.file.submit}
        </Button>
        <Button
          type="button"
          variant="ghost"
          disabled={add.isPending}
          // Com `onTouched`, sair do campo vazio mostra o erro; ele empurraria o botão entre apertar e
          // soltar e o clique se perderia. Apertar o Cancelar não tira o foco do campo.
          onMouseDown={(event) => event.preventDefault()}
          onClick={onCancel}
        >
          {text.cancel}
        </Button>
      </div>
    </form>
  )
}
