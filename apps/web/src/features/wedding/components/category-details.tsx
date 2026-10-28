import { useQueryClient } from '@tanstack/react-query'
import { CircleAlert } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { MoneyInput } from '@/components/ui/money-input'
import { Select } from '@/components/ui/select'
import { type ScopeCategory, scopeKeys } from '../api/scope'
import {
  useDeleteScopeCategory,
  useSetScopeCategoryVisibility,
  useUpdateScopeCategory,
} from '../api/use-scope-mutations'
import { copy } from '../copy'
import { scopeErrorText } from '../lib/error-text'

const labels = copy.scope.manage

export function validName(name: string): boolean {
  const trimmed = name.trim()
  return trimmed.length > 0 && trimmed.length <= 60
}

export interface GroupOption {
  id: string
  name: string
}

interface CategoryDetailsProps {
  category: ScopeCategory
  groups: readonly GroupOption[]
  editing: boolean
  onEditingChange: (editing: boolean) => void
}

/**
 * Nome, grupo, estimativa, ocultar e excluir. Uma seção em edição por vez: enquanto os detalhes
 * estão abertos o resto do painel não muda a versão por baixo deles. A versão usada é a de quando
 * a edição abriu, então um conflito nunca vira sobrescrita.
 */
export function CategoryDetails({
  category,
  groups,
  editing,
  onEditingChange,
}: CategoryDetailsProps) {
  const visibility = useSetScopeCategoryVisibility()
  const [alert, setAlert] = useState<string | null>(null)

  return (
    <section aria-label={labels.details.title} className="flex flex-col gap-3">
      <h3 className="text-body font-semibold text-ink">{labels.details.title}</h3>
      {editing ? (
        <DetailsForm category={category} groups={groups} onDone={() => onEditingChange(false)} />
      ) : (
        <div className="flex flex-wrap gap-3">
          <Button variant="secondary" onClick={() => onEditingChange(true)}>
            {labels.details.edit}
          </Button>
          <Button
            variant="ghost"
            loading={visibility.isPending}
            onClick={() => {
              setAlert(null)
              visibility.mutate(
                { categoryId: category.id, hidden: !category.hidden, version: category.version },
                { onError: (error) => setAlert(scopeErrorText(error).text) },
              )
            }}
          >
            {category.hidden ? labels.details.show : labels.details.hide}
          </Button>
          {category.can_delete && <DeleteCategory category={category} />}
        </div>
      )}
      {!editing && category.hidden && (
        <p className="text-body-sm text-ink-muted">{labels.details.hiddenNote}</p>
      )}
      {!editing && !category.can_delete && (
        <p className="text-body-sm text-ink-muted">{labels.details.catalogNote}</p>
      )}
      <div role="alert">
        {alert && (
          <p className="flex items-start gap-2 rounded-control bg-attention-bg px-3 py-2.5 text-body-sm text-attention-ink">
            <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
            {alert}
          </p>
        )}
      </div>
    </section>
  )
}

function DetailsForm({
  category,
  groups,
  onDone,
}: {
  category: ScopeCategory
  groups: readonly GroupOption[]
  onDone: () => void
}) {
  const queryClient = useQueryClient()
  const update = useUpdateScopeCategory()
  const [baseVersion] = useState(category.version)
  const [name, setName] = useState(category.name)
  const [groupId, setGroupId] = useState(category.group_id)
  const [estimate, setEstimate] = useState<number | null>(category.estimate_cents)
  const [nameError, setNameError] = useState(false)
  const [alert, setAlert] = useState<{ conflict: boolean; text: string } | null>(null)

  function submit() {
    if (!validName(name)) {
      setNameError(true)
      return
    }
    setNameError(false)
    setAlert(null)
    update.mutate(
      {
        categoryId: category.id,
        name: name.trim(),
        groupId,
        estimateCents: estimate,
        version: baseVersion,
      },
      { onSuccess: onDone, onError: (error) => setAlert(scopeErrorText(error)) },
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <Input
        label={labels.details.name}
        value={name}
        onChange={(event) => setName(event.target.value)}
        error={nameError ? labels.nameInvalid : undefined}
        autoComplete="off"
      />
      <Select
        label={labels.details.group}
        options={groups.map((group) => ({ value: group.id, label: group.name }))}
        value={groupId}
        onValueChange={setGroupId}
      />
      <MoneyInput
        label={labels.details.estimate}
        hint={labels.details.estimateHint}
        value={estimate}
        onValueChange={setEstimate}
      />
      <div role="alert">
        {alert && (
          <div className="flex flex-col items-start gap-3 rounded-control bg-attention-bg px-3 py-2.5 text-body-sm text-attention-ink">
            <p className="flex items-start gap-2">
              <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
              {alert.text}
            </p>
            {alert.conflict && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  void queryClient.refetchQueries({ queryKey: scopeKeys.map }).then(onDone)
                }}
              >
                {labels.reload}
              </Button>
            )}
          </div>
        )}
      </div>
      <div className="flex flex-wrap gap-3">
        <Button onClick={submit} loading={update.isPending}>
          {labels.details.save}
        </Button>
        <Button variant="ghost" onClick={onDone}>
          {labels.details.cancel}
        </Button>
      </div>
    </div>
  )
}

function DeleteCategory({ category }: { category: ScopeCategory }) {
  const remove = useDeleteScopeCategory()
  const [open, setOpen] = useState(false)
  const [alert, setAlert] = useState<string | null>(null)
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="soft-destructive">{labels.details.delete}</Button>
      </DialogTrigger>
      <DialogContent title={labels.deleteDialog.title} description={labels.deleteDialog.body}>
        {alert && (
          <p role="alert" className="text-body-sm text-attention-ink">
            {alert}
          </p>
        )}
        <DialogFooter>
          <Button variant="ghost" onClick={() => setOpen(false)}>
            {labels.deleteDialog.cancel}
          </Button>
          <Button
            variant="soft-destructive"
            loading={remove.isPending}
            onClick={() =>
              remove.mutate(
                { categoryId: category.id, version: category.version },
                {
                  onSuccess: () => setOpen(false),
                  onError: (error) => setAlert(scopeErrorText(error).text),
                },
              )
            }
          >
            {labels.deleteDialog.confirm}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
