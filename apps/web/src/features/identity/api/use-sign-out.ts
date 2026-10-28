import { useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { LOGIN_PATH } from '../destination'
import { useLogout } from './use-logout'

/**
 * Sair: encerra a sessão no servidor, vai para a entrada e só então esquece os dados em memória.
 * A ordem importa: limpar antes faria a tela que ainda está aberta consultar de novo, receber 401 e
 * guardar a própria tela como destino da próxima entrada.
 */
export function useSignOut() {
  const logout = useLogout()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  async function signOut() {
    try {
      await logout.mutateAsync()
    } catch {
      return // `logout.isError` conta o que aconteceu, e a tela continua onde está
    }
    await navigate({ to: LOGIN_PATH })
    queryClient.getQueryCache().clear()
  }

  return { signOut, isPending: logout.isPending, hasFailed: logout.isError }
}
