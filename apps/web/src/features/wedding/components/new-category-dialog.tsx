import { CircleAlert } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { MoneyInput } from '@/components/ui/money-input'
import { Select } from '@/components/ui/select'
import { useCreateScopeCategory } from '../api/use-scope-mutations'
import { copy } from '../copy'
import { scopeErrorText } from '../lib/error-text'
import { type GroupOption, validName } from './category-details'

const labels = copy.scope.manage

export function NewCategoryDialog({
  groups,
  open,
  onOpenChange,
}: {
  groups: readonly GroupOption[]
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title={labels.newCategoryDialog.title}
        description={labels.newCategoryDialog.description}
      >
        <NewCategoryForm groups={groups} onDone={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  )
}

function NewCategoryForm({
  groups,
  onDone,
}: {
  groups: readonly GroupOption[]
  onDone: () => void
}) {
  const create = useCreateScopeCategory()
  const [name, setName] = useState('')
  const [groupId, setGroupId] = useState(groups[0]?.id ?? '')
  const [estimate, setEstimate] = useState<number | null>(null)
  const [nameError, setNameError] = useState(false)
  const [alert, setAlert] = useState<string | null>(null)

  function submit() {
    if (!validName(name)) {
      setNameError(true)
      return
    }
    setNameError(false)
    setAlert(null)
    create.mutate(
      { groupId, name: name.trim(), estimateCents: estimate },
      { onSuccess: onDone, onError: (error) => setAlert(scopeErrorText(error).text) },
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
          <p className="flex items-start gap-2 rounded-control bg-attention-bg px-3 py-2.5 text-body-sm text-attention-ink">
            <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
            {alert}
          </p>
        )}
      </div>
      <DialogFooter>
        <Button variant="ghost" onClick={onDone}>
          {labels.newCategoryDialog.cancel}
        </Button>
        <Button onClick={submit} loading={create.isPending}>
          {labels.newCategoryDialog.create}
        </Button>
      </DialogFooter>
    </div>
  )
}
