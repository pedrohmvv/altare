import { useQuery, useQueryClient } from '@tanstack/react-query'
import { CircleAlert, MessagesSquare } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Money } from '@/components/ui/money'
import { Select } from '@/components/ui/select'
import { Sheet, SheetContent } from '@/components/ui/sheet'
import { Textarea } from '@/components/ui/textarea'
import { ApiError } from '@/lib/api/errors'
import { formatInstant } from '@/lib/date'
import {
  type Priority,
  SCOPE_STATUSES,
  type ScopeCategory,
  type ScopeStatus,
  scopeHistoryQueryOptions,
  scopeKeys,
} from '../api/scope'
import { useChangeScopeStatus, useSetMyEvaluation } from '../api/use-scope-mutations'
import { copy } from '../copy'
import { myEvaluation, otherEvaluation, type SessionProfile } from '../lib/scope-filters'
import { CategoryDetails, type GroupOption } from './category-details'
import { Chip } from './chip'
import { ReferencesSection } from './references-section'
import { AlignmentBadge, ScopeStatusBadge } from './scope-badges'

const PRIORITIES: readonly Priority[] = ['Quero muito', 'Se couber', 'Dispenso']

export interface CategorySheetProps {
  category: ScopeCategory
  groupName: string
  /** Os grupos para onde a frente pode ir. */
  groups: readonly GroupOption[]
  profile: SessionProfile
  open: boolean
  onOpenChange: (open: boolean) => void
}

/**
 * O detalhe da frente sem sair da lista (design-system.md §10, item 2). Duas ações são imediatas
 * (mudar o status e as prioridades têm o seu botão) e cada uma usa a `version` que a tela mostra;
 * o texto digitado de uma avaliação guarda a versão de quando abriu, para um conflito nunca virar
 * sobrescrita silenciosa.
 */
export function CategorySheet({
  category,
  groupName,
  groups,
  profile,
  open,
  onOpenChange,
}: CategorySheetProps) {
  const [editingDetails, setEditingDetails] = useState(false)
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent title={category.name} description={copy.scope.sheet.group(groupName)}>
        <Summary category={category} />
        <StatusSection category={category} locked={editingDetails} />
        <EvaluationSection category={category} profile={profile} />
        <ReferencesSection categoryId={category.id} />
        <CategoryDetails
          category={category}
          groups={groups}
          editing={editingDetails}
          onEditingChange={setEditingDetails}
        />
        <History categoryId={category.id} />
      </SheetContent>
    </Sheet>
  )
}

function Summary({ category }: { category: ScopeCategory }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <ScopeStatusBadge status={category.status} />
        <AlignmentBadge alignment={category.alignment} />
      </div>
      <p className="text-body-sm text-ink-muted">
        {category.estimate_cents === null ? (
          copy.scope.card.noEstimate
        ) : (
          <Money cents={category.estimate_cents} className="text-num text-ink" />
        )}
      </p>
    </div>
  )
}

function StatusSection({ category, locked }: { category: ScopeCategory; locked: boolean }) {
  const change = useChangeScopeStatus()
  const [askingReason, setAskingReason] = useState(false)
  const [reason, setReason] = useState('')
  const [reasonError, setReasonError] = useState(false)
  const [alert, setAlert] = useState<string | null>(null)

  function send(status: ScopeStatus, why: string | null) {
    setAlert(null)
    change.mutate(
      { categoryId: category.id, status, reason: why, version: category.version },
      {
        onSuccess: () => {
          setAskingReason(false)
          setReason('')
        },
        onError: (error) =>
          setAlert(
            error instanceof ApiError && error.code === 'version_conflict'
              ? copy.scope.sheet.status.conflict
              : error instanceof ApiError
                ? error.message
                : copy.scope.sheet.status.network,
          ),
      },
    )
  }

  function choose(status: string) {
    const next = SCOPE_STATUSES.find((candidate) => candidate === status)
    if (!next || next === category.status) return
    if (next === 'Fica de fora') {
      setAskingReason(true)
      return
    }
    setAskingReason(false)
    send(next, null)
  }

  function confirmOut() {
    if (reason.trim() === '') {
      setReasonError(true)
      return
    }
    setReasonError(false)
    send('Fica de fora', reason.trim())
  }

  const labels = copy.scope.sheet.status
  return (
    <section aria-label={labels.label} className="flex flex-col gap-3">
      <Select
        label={labels.label}
        options={SCOPE_STATUSES.map((status) => ({ value: status, label: status }))}
        value={category.status}
        onValueChange={choose}
        disabled={change.isPending || locked}
      />
      {category.discard_reason && (
        <p className="text-body-sm text-ink-muted">
          {category.status === 'Fica de fora'
            ? labels.reason(category.discard_reason)
            : labels.previousReason(category.discard_reason)}
        </p>
      )}
      {askingReason && (
        <div className="flex flex-col gap-3">
          <Textarea
            label={labels.reasonLabel}
            hint={labels.reasonHint}
            rows={3}
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            error={reasonError ? labels.reasonRequired : undefined}
          />
          <div className="flex flex-wrap gap-3">
            <Button onClick={confirmOut} loading={change.isPending}>
              {labels.confirmOut}
            </Button>
            <Button variant="ghost" onClick={() => setAskingReason(false)}>
              {labels.cancel}
            </Button>
          </div>
        </div>
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

function EvaluationSection({
  category,
  profile,
}: {
  category: ScopeCategory
  profile: SessionProfile
}) {
  const [reload, setReload] = useState(0)
  const other: SessionProfile = profile === 'Noivo' ? 'Noiva' : 'Noivo'
  const theirs = otherEvaluation(category, profile)
  const titleId = `evaluation-other-${category.id}`

  return (
    <>
      {category.alignment.state === 'divergem' && (
        <p className="flex items-start gap-2 rounded-control bg-attention-bg px-3 py-2.5 text-body-sm text-attention-ink">
          <MessagesSquare aria-hidden className="mt-0.5 size-4 shrink-0" />
          {copy.scope.sheet.divergence}
        </p>
      )}
      <EvaluationForm
        key={reload}
        category={category}
        profile={profile}
        onReload={() => setReload((n) => n + 1)}
      />
      <section aria-labelledby={titleId} className="flex flex-col gap-1">
        <h3 id={titleId} className="text-body font-semibold text-ink">
          {copy.scope.sheet.evaluation.otherTitle(other)}
        </h3>
        <p className="text-body text-ink">
          {theirs.priority ?? copy.scope.sheet.evaluation.notYet}
        </p>
        {theirs.note && <p className="text-body-sm text-ink-muted">{theirs.note}</p>}
      </section>
    </>
  )
}

function EvaluationForm({
  category,
  profile,
  onReload,
}: {
  category: ScopeCategory
  profile: SessionProfile
  onReload: () => void
}) {
  const mine = myEvaluation(category, profile)
  const labels = copy.scope.sheet.evaluation
  const queryClient = useQueryClient()
  const save = useSetMyEvaluation()
  // Os valores e a versão de quando o formulário abriu: um conflito não troca o que foi digitado.
  const [priority, setPriority] = useState<Priority | null>(mine.priority)
  const [note, setNote] = useState(mine.note ?? '')
  const [baseVersion, setBaseVersion] = useState(mine.version)
  const [alert, setAlert] = useState<{ conflict: boolean; text: string } | null>(null)
  const [saved, setSaved] = useState(false)

  function submit() {
    setAlert(null)
    setSaved(false)
    save.mutate(
      { categoryId: category.id, priority, note: note.trim() || null, version: baseVersion },
      {
        onSuccess: (map) => {
          const updated = map.groups.flatMap((g) => g.categories).find((c) => c.id === category.id)
          if (updated) setBaseVersion(myEvaluation(updated, profile).version)
          setSaved(true)
        },
        onError: (error) =>
          setAlert(
            error instanceof ApiError && error.code === 'version_conflict'
              ? { conflict: true, text: labels.conflict }
              : {
                  conflict: false,
                  text: error instanceof ApiError ? error.message : labels.network,
                },
          ),
      },
    )
  }

  return (
    <section aria-label={labels.title} className="flex flex-col gap-4">
      <h3 className="text-body font-semibold text-ink">{labels.title}</h3>
      <fieldset className="flex flex-col gap-2">
        <legend className="mb-1 text-body-sm font-semibold text-ink">{labels.priority}</legend>
        <div className="flex flex-wrap gap-2">
          {PRIORITIES.map((option) => (
            <Chip
              key={option}
              pressed={priority === option}
              onClick={() => setPriority(priority === option ? null : option)}
            >
              {option}
            </Chip>
          ))}
        </div>
      </fieldset>
      <Textarea
        label={labels.noteLabel}
        hint={labels.noteHint}
        rows={3}
        value={note}
        onChange={(event) => setNote(event.target.value)}
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
                  void queryClient.refetchQueries({ queryKey: scopeKeys.map }).then(onReload)
                }}
              >
                {labels.reload}
              </Button>
            )}
          </div>
        )}
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <Button onClick={submit} loading={save.isPending}>
          {labels.save}
        </Button>
        <p role="status" className="text-body-sm text-consensus-ink">
          {saved ? labels.saved : ''}
        </p>
      </div>
    </section>
  )
}

function History({ categoryId }: { categoryId: string }) {
  const history = useQuery(scopeHistoryQueryOptions(categoryId))
  const labels = copy.scope.sheet.history
  return (
    <section aria-label={labels.title} className="flex flex-col gap-2">
      <h3 className="text-body font-semibold text-ink">{labels.title}</h3>
      {history.isError && <p className="text-body-sm text-ink-muted">{labels.loadError}</p>}
      {history.data?.length === 0 && <p className="text-body-sm text-ink-muted">{labels.empty}</p>}
      {history.data && history.data.length > 0 && (
        <ul className="flex flex-col">
          {history.data.map((change) => (
            <li key={change.id} className="border-t border-border py-2 first:border-t-0">
              <p className="text-ui-sm text-ink-muted">
                {change.by} · {formatInstant(change.at)}
              </p>
              <p className="text-body-sm text-ink">
                {labels.change(change.from_status, change.to_status)}
              </p>
              {change.reason && (
                <p className="text-body-sm text-ink-muted">
                  {copy.scope.sheet.status.reason(change.reason)}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
