import { Link } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/ui/empty-state'
import { PageHeader } from '@/components/ui/page-header'

export function NotFoundPage() {
  return (
    <>
      <PageHeader
        eyebrow="Página não encontrada"
        title="Não encontramos esta página"
        description="O endereço pode ter mudado ou ter um erro de digitação."
        actions={
          <Button asChild>
            <Link to="/">Ir para a Visão Geral</Link>
          </Button>
        }
      />
      <EmptyState
        className="mt-10"
        illustration="ramo-grande"
        title="Nada por aqui"
        description="Escolham uma área no menu para continuar."
      />
    </>
  )
}
