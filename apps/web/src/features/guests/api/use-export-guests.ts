import { useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import { filenameFrom, saveFile } from '../lib/download'

export type ExportFormat = 'xlsx' | 'csv'

/**
 * Pede o arquivo por POST: o corpo leva só o formato e os ids das pessoas que estão na tela, então
 * nada que o casal digitou na busca vai para a URL. O arquivo é gerado pelo servidor e entregue
 * ao navegador aqui mesmo; nada dele fica guardado.
 */
export const useExportGuests = () =>
  useMutation({
    mutationFn: async (vars: { format: ExportFormat; guestIds: string[] }) => {
      const result = await api.POST('/api/v1/guests/exports', {
        body: { format: vars.format, guest_ids: vars.guestIds },
        parseAs: 'blob',
      })
      const blob = unwrap(result)
      saveFile(blob, filenameFrom(result.response, `lista-de-convidados.${vars.format}`))
    },
  })
