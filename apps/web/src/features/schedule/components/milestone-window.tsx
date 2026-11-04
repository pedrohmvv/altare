import { useEffect, useId, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { formatTableDay } from '@/lib/date'
import type { ScheduleMilestone } from '../api/schedule'
import { copy } from '../copy'
import { WindowEditor } from './window-editor'

const labels = copy.window

/**
 * A janela do marco no painel (F-CRN-05): em palavras ("de 14 a 10 meses antes da data"), com as
 * datas que a API calculou e o editor, só no Modo Com Data. Sem data exata a janela não tem datas,
 * e a seção diz quando elas aparecem. O marco sem janela oferece "Definir janela".
 */
export function MilestoneWindow({
  milestone,
  hasExactDate,
}: {
  milestone: ScheduleMilestone
  hasExactDate: boolean
}) {
  const titleId = useId()
  // Depois de salvar, o botão que tinha o foco se desliga: o foco vai ao título, que fica.
  const heading = useRef<HTMLHeadingElement>(null)
  const defineButton = useRef<HTMLButtonElement>(null)
  const [defining, setDefining] = useState(false)
  const [cancelled, setCancelled] = useState(false)
  const { window } = milestone

  // Cancelar tira o editor; só então o "Definir janela" existe de novo para receber o foco.
  useEffect(() => {
    if (cancelled && !defining) {
      defineButton.current?.focus()
      setCancelled(false)
    }
  }, [cancelled, defining])

  const range = window ? labels.range(window.start_before, window.end_before, window.unit) : null

  return (
    <section aria-labelledby={titleId} className="flex flex-col gap-3">
      <h3 ref={heading} tabIndex={-1} id={titleId} className="text-body font-semibold text-ink">
        {labels.title}
      </h3>
      {!hasExactDate ? (
        <p className="text-body-sm text-ink-muted">
          {range ? labels.noDateWithRange(range) : labels.noDateNoWindow}
        </p>
      ) : (
        <>
          {range ? (
            <div className="flex flex-col gap-0.5">
              <p className="text-body text-ink">{range}</p>
              {milestone.window_start && milestone.window_end && (
                <p className="text-body-sm text-ink-muted">
                  {labels.calculated(
                    formatTableDay(milestone.window_start),
                    formatTableDay(milestone.window_end),
                  )}
                </p>
              )}
              {window?.is_suggestion && (
                <p className="text-body-sm text-ink-muted">{labels.suggestion}</p>
              )}
            </div>
          ) : (
            !defining && <p className="text-body-sm text-ink-muted">{labels.noWindow}</p>
          )}
          {window || defining ? (
            <WindowEditor
              milestone={milestone}
              focusOnOpen={defining}
              onCancel={
                window
                  ? undefined
                  : () => {
                      setDefining(false)
                      setCancelled(true)
                    }
              }
              onSaved={() => heading.current?.focus()}
            />
          ) : (
            <Button
              ref={defineButton}
              variant="secondary"
              className="self-start"
              onClick={() => setDefining(true)}
            >
              {labels.define}
            </Button>
          )}
        </>
      )}
    </section>
  )
}
