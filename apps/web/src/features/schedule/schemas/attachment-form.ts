import { z } from 'zod'
import { copy } from '../copy'

/** Os limites da API para o título e o comentário de um anexo. */
export const MAX_ATTACHMENT_TITLE = 120
export const MAX_ATTACHMENT_COMMENT = 500
export const MAX_URL = 2000

/** O que o `accept` do campo oferece, e o que o navegador confere no tipo declarado. */
export const ATTACHMENT_FILE_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp']

const text = copy.attachments
const optionalTexts = {
  title: z.string().trim().max(MAX_ATTACHMENT_TITLE, text.errors.tooLong(MAX_ATTACHMENT_TITLE)),
  comment: z
    .string()
    .trim()
    .max(MAX_ATTACHMENT_COMMENT, text.errors.tooLong(MAX_ATTACHMENT_COMMENT)),
}

/** O endereço de um link anexado: só http ou https; o servidor confere de novo. */
export const attachmentLinkSchema = z.object({
  url: z
    .string()
    .trim()
    .regex(/^https?:\/\/\S+$/i, text.link.invalid)
    .max(MAX_URL, text.link.invalid),
  ...optionalTexts,
})

/**
 * O arquivo escolhido: só o tipo declarado é conferido aqui (o servidor confere a assinatura real e o
 * tamanho, até 20 MB).
 */
export const attachmentFileSchema = z.object({
  file: z
    .custom<FileList>()
    .refine((files) => (files?.length ?? 0) > 0, text.file.required)
    .refine((files) => {
      const chosen = files?.[0]
      return !chosen || ATTACHMENT_FILE_TYPES.includes(chosen.type)
    }, text.file.invalidType),
  ...optionalTexts,
})

export type AttachmentLinkValues = z.infer<typeof attachmentLinkSchema>
export type AttachmentFileValues = z.infer<typeof attachmentFileSchema>
