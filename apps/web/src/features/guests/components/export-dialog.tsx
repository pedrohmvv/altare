import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { SegmentedControl } from '@/components/ui/segmented-control'
import { useToast } from '@/components/ui/toast'
import { ApiError } from '@/lib/api/errors'
import { type ExportFormat, useExportGuests } from '../api/use-export-guests'
import { copy } from '../copy'
import type { FormAlertState } from '../lib/server-errors'
import { FormAlert } from './form-alert'

const labels = copy.export

const FORMATS: ExportFormat[] = ['xlsx', 'csv']

function alertFor(error: unknown): FormAlertState {
  if (!(error instanceof ApiError)) return { kind: 'error', text: labels.errors.network }
  // Uma pessoa da tela já não existe na lista: o arquivo não diria o que a tela anunciou.
  if (error.code === 'not_found') return { kind: 'error', text: labels.errors.stale }
  return { kind: 'error', text: error.message }
}

/**
 * Baixa a lista que está na tela (F-CNV-08): o formato e as pessoas visíveis vão num POST, e o
 * arquivo volta pronto. O filtro e a busca são do navegador, por isso só os ids viajam.
 */
export function ExportDialog({ guestIds }: { guestIds: string[] }) {
  const [open, setOpen] = useState(false)
  const [format, setFormat] = useState<ExportFormat>('xlsx')
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const exporting = useExportGuests()
  const { toast } = useToast()

  const download = () => {
    setAlert(null)
    exporting.mutate(
      { format, guestIds },
      {
        onSuccess: () => {
          setOpen(false)
          toast({ title: labels.done.title, description: labels.done.description, tone: 'success' })
        },
        onError: (error) => setAlert(alertFor(error)),
      },
    )
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next)
        if (!next) setAlert(null)
      }}
    >
      <DialogTrigger asChild>
        <Button variant="secondary" disabled={guestIds.length === 0}>
          {labels.button}
        </Button>
      </DialogTrigger>
      <DialogContent title={labels.title} description={labels.description}>
        <div className="flex flex-col gap-2">
          <p data-testid="export-count" className="text-body font-medium text-ink">
            {labels.count(guestIds.length)}
          </p>
          <p className="text-body-sm text-ink-muted">{labels.countHint}</p>
        </div>
        <fieldset className="flex flex-col gap-2">
          <legend className="mb-2 text-body font-medium text-ink">{labels.formatLegend}</legend>
          <SegmentedControl
            aria-label={labels.formatLegend}
            value={format}
            onValueChange={(next) => setFormat(next as ExportFormat)}
            options={FORMATS.map((value) => ({ value, label: labels.formats[value] }))}
          />
          <p className="text-body-sm text-ink-muted">{labels.formatHint[format]}</p>
        </fieldset>
        <p className="text-body-sm text-ink">{labels.care}</p>
        <p role="status" className="text-body-sm text-ink-muted">
          {exporting.isPending ? labels.generating : ''}
        </p>
        <FormAlert alert={alert} />
        <DialogFooter>
          <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
            {labels.cancel}
          </Button>
          <Button type="button" loading={exporting.isPending} onClick={download}>
            {labels.download}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
