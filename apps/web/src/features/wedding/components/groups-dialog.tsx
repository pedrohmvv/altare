import { CircleAlert } from 'lucide-react'
import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import type { ScopeGroup } from '../api/scope'
import {
  useCreateScopeGroup,
  useDeleteScopeGroup,
  useRenameScopeGroup,
  useSetScopeGroupVisibility,
} from '../api/use-scope-mutations'
import { copy } from '../copy'
import { scopeErrorText } from '../lib/error-text'
import { validName } from './category-details'

const labels = copy.scope.manage

export function GroupsDialog({
  groups,
  open,
  onOpenChange,
}: {
  groups: readonly ScopeGroup[]
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const [alert, setAlert] = useState<string | null>(null)
  const onError = (error: unknown) => setAlert(scopeErrorText(error).text)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title={labels.groupsDialog.title}
        description={labels.groupsDialog.description}
      >
        <div role="alert">
          {alert && (
            <p className="flex items-start gap-2 rounded-control bg-attention-bg px-3 py-2.5 text-body-sm text-attention-ink">
              <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
              {alert}
            </p>
          )}
        </div>
        <ul className="flex flex-col">
          {groups.map((group) => (
            <GroupRow
              key={`${group.id}-${group.version}`}
              group={group}
              onError={onError}
              onOk={() => setAlert(null)}
            />
          ))}
        </ul>
        <NewGroupForm onError={onError} onOk={() => setAlert(null)} />
      </DialogContent>
    </Dialog>
  )
}

function GroupRow({
  group,
  onError,
  onOk,
}: {
  group: ScopeGroup
  onError: (error: unknown) => void
  onOk: () => void
}) {
  const rename = useRenameScopeGroup()
  const visibility = useSetScopeGroupVisibility()
  const remove = useDeleteScopeGroup()
  const [renaming, setRenaming] = useState(false)
  const [draft, setDraft] = useState(group.name)
  const [draftError, setDraftError] = useState(false)

  function saveName() {
    if (!validName(draft)) {
      setDraftError(true)
      return
    }
    setDraftError(false)
    rename.mutate(
      { groupId: group.id, name: draft.trim(), version: group.version },
      {
        onSuccess: () => {
          setRenaming(false)
          onOk()
        },
        onError,
      },
    )
  }

  return (
    <li className="flex flex-col gap-2 border-t border-border py-3 first:border-t-0">
      {renaming ? (
        <div className="flex flex-col gap-2">
          <Input
            label={labels.groupsDialog.newName(group.name)}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            error={draftError ? labels.nameInvalid : undefined}
            autoComplete="off"
          />
          <div className="flex gap-2">
            <Button size="sm" onClick={saveName} loading={rename.isPending}>
              {labels.groupsDialog.saveName}
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setRenaming(false)}>
              {labels.groupsDialog.cancel}
            </Button>
          </div>
        </div>
      ) : (
        <>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-body font-medium text-ink">{group.name}</span>
            {group.origin === 'catalogo' && <Badge>{labels.groupsDialog.fromCatalog}</Badge>}
            {group.hidden && <Badge variant="outline">{labels.groupsDialog.hidden}</Badge>}
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="secondary"
              onClick={() => {
                setDraft(group.name)
                setRenaming(true)
              }}
            >
              <span className="sr-only">{labels.groupsDialog.rename(group.name)}</span>
              <span aria-hidden>Renomear</span>
            </Button>
            <Button
              size="sm"
              variant="ghost"
              loading={visibility.isPending}
              onClick={() =>
                visibility.mutate(
                  { groupId: group.id, hidden: !group.hidden, version: group.version },
                  { onSuccess: onOk, onError },
                )
              }
            >
              <span className="sr-only">
                {group.hidden
                  ? labels.groupsDialog.show(group.name)
                  : labels.groupsDialog.hide(group.name)}
              </span>
              <span aria-hidden>{group.hidden ? 'Mostrar' : 'Ocultar'}</span>
            </Button>
            {group.can_delete && (
              <Button
                size="sm"
                variant="soft-destructive"
                loading={remove.isPending}
                onClick={() =>
                  remove.mutate(
                    { groupId: group.id, version: group.version },
                    { onSuccess: onOk, onError },
                  )
                }
              >
                <span className="sr-only">{labels.groupsDialog.delete(group.name)}</span>
                <span aria-hidden>Excluir</span>
              </Button>
            )}
          </div>
        </>
      )}
    </li>
  )
}

function NewGroupForm({ onError, onOk }: { onError: (error: unknown) => void; onOk: () => void }) {
  const create = useCreateScopeGroup()
  const [name, setName] = useState('')
  const [nameError, setNameError] = useState(false)

  function submit() {
    if (!validName(name)) {
      setNameError(true)
      return
    }
    setNameError(false)
    create.mutate(
      { name: name.trim() },
      {
        onSuccess: () => {
          setName('')
          onOk()
        },
        onError,
      },
    )
  }

  return (
    <div className="flex flex-col gap-3 border-t border-border pt-4">
      <Input
        label={labels.groupsDialog.newLabel}
        value={name}
        onChange={(event) => setName(event.target.value)}
        error={nameError ? labels.nameInvalid : undefined}
        autoComplete="off"
      />
      <div>
        <Button onClick={submit} loading={create.isPending}>
          {labels.groupsDialog.create}
        </Button>
      </div>
    </div>
  )
}
