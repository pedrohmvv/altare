import { Link, useNavigate, useSearch } from '@tanstack/react-router'
import { type ScheduleSearch, validateScheduleSearch } from '../search'
import { SchedulePage } from './schedule-page'

/**
 * Liga a página à URL: lê os parâmetros (já validados) e muda só o que a página pediu, mantendo o
 * resto, inclusive a lente.
 */
export function ScheduleRoute() {
  const search = validateScheduleSearch(useSearch({ strict: false }) as Record<string, unknown>)
  const navigate = useNavigate()

  const onSearchChange = (patch: Partial<ScheduleSearch>) => {
    void navigate({
      to: '.',
      search: ((previous: Record<string, unknown>) => ({ ...previous, ...patch })) as never,
    })
  }

  // O link às Definições Base passa pelo roteador e leva só a lente, como os links da casca.
  const planningLink = (label: string) => (
    <Link
      to="/planejamento"
      search={((previous: { lente?: 'minha' }) => ({ lente: previous.lente })) as never}
    >
      {label}
    </Link>
  )

  return (
    <SchedulePage search={search} onSearchChange={onSearchChange} planningLink={planningLink} />
  )
}
