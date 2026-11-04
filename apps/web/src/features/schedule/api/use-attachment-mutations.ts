import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import { type ChecklistOwner, SCHEDULE_WRITE_SCOPE, type Schedule, scheduleKeys } from './schedule'

/**
 * A escrita de um anexo devolve o cronograma inteiro, que vai ao cache (os anexos vêm dentro dele);
 * nada é otimista. Entra no escopo serial das escritas do cronograma, como o checklist.
 */
function useAttachmentWrite<Vars>(send: (vars: Vars) => Promise<Schedule>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: send,
    scope: SCHEDULE_WRITE_SCOPE,
    onSuccess: (schedule) => queryClient.setQueryData(scheduleKeys.all, schedule),
    onError: () => void queryClient.invalidateQueries({ queryKey: scheduleKeys.all }),
  })
}

export interface AttachmentTexts {
  title: string | null
  comment: string | null
}

export const useAddLinkAttachment = () =>
  useAttachmentWrite(async (v: AttachmentTexts & { owner: ChecklistOwner; url: string }) =>
    unwrap(
      await api.POST('/api/v1/schedule/{owner_kind}/{owner_id}/attachments/links', {
        params: { path: { owner_kind: v.owner.kind, owner_id: v.owner.id } },
        body: { url: v.url, title: v.title, comment: v.comment },
      }),
    ),
  )

/** O servidor guarda o nome e o tamanho do arquivo na hora de anexar; a tela só diz qual arquivo. */
const useLinkUploadedFile = () =>
  useAttachmentWrite(async (v: AttachmentTexts & { owner: ChecklistOwner; fileId: string }) =>
    unwrap(
      await api.POST('/api/v1/schedule/{owner_kind}/{owner_id}/attachments/files', {
        params: { path: { owner_kind: v.owner.kind, owner_id: v.owner.id } },
        body: { file_id: v.fileId, title: v.title, comment: v.comment },
      }),
    ),
  )

/**
 * Envia o arquivo (o módulo de arquivos confere o tipo pela assinatura real e o tamanho) e só então o
 * anexa ao dono. O envio fica **fora** do escopo serial: um arquivo de 20 MB travaria o checklist, e
 * só a escrita no cronograma precisa esperar a vez. Se a segunda etapa falhar, sobra um arquivo sem
 * anexo: inofensivo, e enviar de novo o reaproveita (o conteúdo é endereçado pelo hash).
 */
export function useAddFileAttachment() {
  const link = useLinkUploadedFile()
  return useMutation({
    mutationFn: async (v: AttachmentTexts & { owner: ChecklistOwner; file: File }) => {
      const uploaded = unwrap(
        await api.POST('/api/v1/files', {
          body: { file: '' },
          bodySerializer: () => {
            const form = new FormData()
            form.append('file', v.file)
            return form
          },
        }),
      )
      return link.mutateAsync({
        owner: v.owner,
        fileId: uploaded.id,
        title: v.title,
        comment: v.comment,
      })
    },
  })
}

/** Só o autor remove; o servidor diz 403 aos demais. Não se desfaz: o registro fica guardado. */
export const useRemoveAttachment = () =>
  useAttachmentWrite(async (v: { attachmentId: string }) =>
    unwrap(
      await api.DELETE('/api/v1/schedule/attachments/{attachment_id}', {
        params: { path: { attachment_id: v.attachmentId } },
      }),
    ),
  )
