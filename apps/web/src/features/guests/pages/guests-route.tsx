import { useQuery } from '@tanstack/react-query'
import { useNavigate, useSearch } from '@tanstack/react-router'
import { meQueryOptions } from '@/features/identity'
import { type GuestsSearch, validateGuestsSearch } from '../search'
import { GuestsPage } from './guests-page'

/**
 * Liga a página à URL: lê os parâmetros (já validados) e muda só o que a página pediu, mantendo o
 * resto, inclusive a lente. A guarda de sessão já garantiu o usuário antes da tela abrir.
 */
export function GuestsRoute() {
  const search = validateGuestsSearch(useSearch({ strict: false }) as Record<string, unknown>)
  const lens = useSearch({
    strict: false,
    select: (all) => (all.lente === 'minha' ? 'minha' : 'casal'),
  })
  const navigate = useNavigate()
  const me = useQuery(meQueryOptions)
  if (!me.data) return null

  const onSearchChange = (patch: Partial<GuestsSearch>) => {
    void navigate({
      to: '.',
      search: ((previous: Record<string, unknown>) => ({ ...previous, ...patch })) as never,
    })
  }

  return (
    <GuestsPage
      search={search}
      onSearchChange={onSearchChange}
      profile={me.data.profile as 'Noivo' | 'Noiva'}
      lens={lens}
    />
  )
}
