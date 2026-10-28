import { useQuery } from '@tanstack/react-query'
import { CircleAlert } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { formatInstant } from '@/lib/date'
import { type ScopeReference, scopeReferencesQueryOptions } from '../api/scope'
import {
  useAddImageReference,
  useAddLinkReference,
  useRemoveReference,
} from '../api/use-reference-mutations'
import { copy } from '../copy'
import { scopeErrorText } from '../lib/error-text'

const labels = copy.scope.sheet.references
const IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const isHttp = (url: string) => /^https?:\/\/\S+$/i.test(url)
const filePath = (fileId: string) => `/api/v1/files/${fileId}`

/**
 * As inspirações da frente (F-PLN-06): links e imagens num só lugar. O endereço só vira link
 * clicável se for http ou https, e nada é lido da página.
 */
export function ReferencesSection({ categoryId }: { categoryId: string }) {
  const query = useQuery(scopeReferencesQueryOptions(categoryId))
  const [adding, setAdding] = useState<'link' | 'image' | null>(null)

  return (
    <section aria-label={labels.title} className="flex flex-col gap-3">
      <h3 className="text-body font-semibold text-ink">{labels.title}</h3>
      {query.isPending && <p className="text-body-sm text-ink-muted">{labels.loading}</p>}
      {query.isError && <p className="text-body-sm text-ink-muted">{labels.loadError}</p>}
      {query.data?.length === 0 && <p className="text-body-sm text-ink-muted">{labels.empty}</p>}
      {query.data && query.data.length > 0 && (
        <ul className="flex flex-col">
          {query.data.map((reference) => (
            <ReferenceItem key={reference.id} categoryId={categoryId} reference={reference} />
          ))}
        </ul>
      )}
      {adding === 'link' && <LinkForm categoryId={categoryId} onDone={() => setAdding(null)} />}
      {adding === 'image' && <ImageForm categoryId={categoryId} onDone={() => setAdding(null)} />}
      {adding === null && (
        <div className="flex flex-wrap gap-3">
          <Button variant="secondary" onClick={() => setAdding('link')}>
            {labels.addLink}
          </Button>
          <Button variant="secondary" onClick={() => setAdding('image')}>
            {labels.addImage}
          </Button>
        </div>
      )}
    </section>
  )
}

function ReferenceItem({
  categoryId,
  reference,
}: {
  categoryId: string
  reference: ScopeReference
}) {
  const label = reference.title ?? reference.domain ?? labels.image.label
  return (
    <li className="flex gap-3 border-t border-border py-3 first:border-t-0">
      {reference.kind === 'imagem' && reference.file_id ? (
        <a
          href={filePath(reference.file_id)}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0"
        >
          <img
            src={filePath(reference.file_id)}
            alt={reference.title ?? labels.image.alt}
            loading="lazy"
            className="size-20 rounded-control border border-border object-cover"
          />
        </a>
      ) : null}
      <div className="flex min-w-0 flex-1 flex-col gap-0.5">
        {reference.kind === 'link' && reference.url && isHttp(reference.url) ? (
          <a
            href={reference.url}
            target="_blank"
            rel="noopener noreferrer"
            className="truncate text-body font-medium text-primary underline-offset-4 hover:underline"
          >
            {reference.title ?? reference.domain ?? reference.url}
          </a>
        ) : reference.kind === 'link' ? (
          <p className="truncate text-body font-medium text-ink">
            {reference.title ?? labels.image.label}
          </p>
        ) : (
          reference.title && (
            <p className="truncate text-body font-medium text-ink">{reference.title}</p>
          )
        )}
        {reference.kind === 'link' && reference.title && reference.domain && (
          <p className="text-ui-sm text-ink-muted">{reference.domain}</p>
        )}
        {reference.comment && <p className="text-body-sm text-ink-muted">{reference.comment}</p>}
        <p className="text-ui-xs text-ink-muted">
          {reference.by} · {formatInstant(reference.at)}
        </p>
      </div>
      {reference.can_remove && (
        <RemoveReference categoryId={categoryId} reference={reference} label={label} />
      )}
    </li>
  )
}

function RemoveReference({
  categoryId,
  reference,
  label,
}: {
  categoryId: string
  reference: ScopeReference
  label: string
}) {
  const remove = useRemoveReference(categoryId)
  const [open, setOpen] = useState(false)
  const [alert, setAlert] = useState<string | null>(null)
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" aria-label={labels.remove(label)}>
          Remover
        </Button>
      </DialogTrigger>
      <DialogContent title={labels.removeDialog.title} description={labels.removeDialog.body}>
        <div role="alert">
          {alert && <p className="text-body-sm text-attention-ink">{alert}</p>}
        </div>
        <DialogFooter>
          <Button variant="ghost" onClick={() => setOpen(false)}>
            {labels.removeDialog.cancel}
          </Button>
          <Button
            variant="soft-destructive"
            loading={remove.isPending}
            onClick={() =>
              remove.mutate(
                { referenceId: reference.id },
                {
                  onSuccess: () => setOpen(false),
                  onError: (error) => setAlert(scopeErrorText(error).text),
                },
              )
            }
          >
            {labels.removeDialog.confirm}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function FormAlert({ text }: { text: string | null }) {
  return (
    <div role="alert">
      {text && (
        <p className="flex items-start gap-2 rounded-control bg-attention-bg px-3 py-2.5 text-body-sm text-attention-ink">
          <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
          {text}
        </p>
      )}
    </div>
  )
}

const orNull = (text: string) => text.trim() || null

function LinkForm({ categoryId, onDone }: { categoryId: string; onDone: () => void }) {
  const add = useAddLinkReference(categoryId)
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const [comment, setComment] = useState('')
  const [urlError, setUrlError] = useState(false)
  const [alert, setAlert] = useState<string | null>(null)

  function submit() {
    if (!isHttp(url.trim())) {
      setUrlError(true)
      return
    }
    setUrlError(false)
    setAlert(null)
    add.mutate(
      { url: url.trim(), title: orNull(title), comment: orNull(comment) },
      { onSuccess: onDone, onError: (error) => setAlert(scopeErrorText(error).text) },
    )
  }

  return (
    <div className="flex flex-col gap-3">
      <Input
        label={labels.link.url}
        inputMode="url"
        autoComplete="off"
        autoCapitalize="none"
        spellCheck={false}
        value={url}
        onChange={(event) => setUrl(event.target.value)}
        error={urlError ? labels.link.invalid : undefined}
      />
      <Input
        label={labels.titleLabel}
        hint={labels.optional}
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <Input
        label={labels.commentLabel}
        hint={labels.optional}
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />
      <FormAlert text={alert} />
      <div className="flex flex-wrap gap-3">
        <Button onClick={submit} loading={add.isPending}>
          {labels.link.save}
        </Button>
        <Button variant="ghost" onClick={onDone}>
          {labels.cancel}
        </Button>
      </div>
    </div>
  )
}

function ImageForm({ categoryId, onDone }: { categoryId: string; onDone: () => void }) {
  const add = useAddImageReference(categoryId)
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [comment, setComment] = useState('')
  const [fileError, setFileError] = useState(false)
  const [alert, setAlert] = useState<string | null>(null)

  function submit() {
    if (!file || !IMAGE_TYPES.includes(file.type)) {
      setFileError(true)
      return
    }
    setFileError(false)
    setAlert(null)
    add.mutate(
      { file, title: orNull(title), comment: orNull(comment) },
      { onSuccess: onDone, onError: (error) => setAlert(scopeErrorText(error).text) },
    )
  }

  return (
    <div className="flex flex-col gap-3">
      <Input
        label={labels.image.file}
        hint={labels.image.hint}
        type="file"
        accept={IMAGE_TYPES.join(',')}
        onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        error={fileError ? labels.image.invalid : undefined}
      />
      <Input
        label={labels.titleLabel}
        hint={labels.optional}
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <Input
        label={labels.commentLabel}
        hint={labels.optional}
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />
      <FormAlert text={alert} />
      <div className="flex flex-wrap gap-3">
        <Button onClick={submit} loading={add.isPending}>
          {labels.image.save}
        </Button>
        <Button variant="ghost" onClick={onDone}>
          {labels.cancel}
        </Button>
      </div>
    </div>
  )
}
