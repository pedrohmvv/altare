import { useNavigate, useSearch } from '@tanstack/react-router'
import { SegmentedControl } from '@/components/ui/segmented-control'
import type { RootSearch } from '@/routes/router'

const OPTIONS = [
  { value: 'casal', label: 'Visão do Casal' },
  { value: 'minha', label: 'Minha visão' },
]

/** A lente muda foco e destaque, nunca a autoria (stack.md §6). Fica na URL: `?lente=minha`. */
export function LensSwitcher() {
  const lente = useSearch({ strict: false, select: (search) => search.lente })
  const navigate = useNavigate()

  return (
    <SegmentedControl
      aria-label="Lente de visão"
      options={OPTIONS}
      value={lente ?? 'casal'}
      onValueChange={(value) =>
        navigate({
          to: '.',
          search: (previous: RootSearch): RootSearch => ({
            ...previous,
            lente: value === 'minha' ? 'minha' : undefined,
          }),
        })
      }
    />
  )
}
