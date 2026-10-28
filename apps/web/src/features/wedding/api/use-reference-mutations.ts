import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import { scopeKeys } from './scope'

/** A resposta de toda escrita é a lista atualizada da frente: vai direto para o cache. */
function useReferenceWrite<Vars>(
  categoryId: string,
  send: (vars: Vars) => Promise<Awaited<ReturnType<typeof listAfter>>>,
) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: send,
    onSuccess: (list) => queryClient.setQueryData(scopeKeys.references(categoryId), list),
  })
}

// Só para dar o tipo da lista devolvida pela API.
async function listAfter(categoryId: string) {
  return unwrap(
    await api.GET('/api/v1/wedding/scope/categories/{category_id}/references', {
      params: { path: { category_id: categoryId } },
    }),
  )
}

interface Texts {
  title: string | null
  comment: string | null
}

export function useAddLinkReference(categoryId: string) {
  return useReferenceWrite(categoryId, async (v: Texts & { url: string }) =>
    unwrap(
      await api.POST('/api/v1/wedding/scope/categories/{category_id}/references/links', {
        params: { path: { category_id: categoryId } },
        body: { url: v.url, title: v.title, comment: v.comment },
      }),
    ),
  )
}

/**
 * Envia o arquivo (o módulo de arquivos confere o tipo pela assinatura real) e só então o guarda como
 * referência. Se a segunda etapa falhar, sobra um arquivo sem referência: inofensivo, e o envio de
 * novo o reaproveita (o conteúdo é endereçado pelo hash).
 */
export function useAddImageReference(categoryId: string) {
  return useReferenceWrite(categoryId, async (v: Texts & { file: File }) => {
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
    return unwrap(
      await api.POST('/api/v1/wedding/scope/categories/{category_id}/references/images', {
        params: { path: { category_id: categoryId } },
        body: { file_id: uploaded.id, title: v.title, comment: v.comment },
      }),
    )
  })
}

export function useRemoveReference(categoryId: string) {
  return useReferenceWrite(categoryId, async (v: { referenceId: string }) =>
    unwrap(
      await api.DELETE('/api/v1/wedding/scope/categories/{category_id}/references/{reference_id}', {
        params: { path: { category_id: categoryId, reference_id: v.referenceId } },
      }),
    ),
  )
}
