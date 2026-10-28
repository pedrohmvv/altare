import { useQuery } from '@tanstack/react-query'
import { useNavigate, useSearch } from '@tanstack/react-router'
import { meQueryOptions } from '@/features/identity'
import { type PlanningSearch, validatePlanningSearch } from '../search'
import { WeddingPage } from './wedding-page'

/**
 * Liga a página à URL: lê os parâmetros (já validados) e muda só o que a página pediu, mantendo o
 * resto, inclusive a lente. A guarda de sessão já garantiu o usuário antes da tela abrir.
 */
export function WeddingRoute() {
  const search = validatePlanningSearch(useSearch({ strict: false }) as Record<string, unknown>)
  const navigate = useNavigate()
  const me = useQuery(meQueryOptions)
  if (!me.data) return null

  const onSearchChange = (patch: Partial<PlanningSearch>) => {
    void navigate({
      to: '.',
      search: ((previous: Record<string, unknown>) => ({ ...previous, ...patch })) as never,
    })
  }

  return (
    <WeddingPage
      search={search}
      onSearchChange={onSearchChange}
      profile={me.data.profile as 'Noivo' | 'Noiva'}
    />
  )
}
