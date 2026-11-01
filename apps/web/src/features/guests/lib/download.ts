/** O nome que a API deu ao arquivo (`Content-Disposition`), ou o de reserva se o header faltar. */
export function filenameFrom(response: Response, fallback: string): string {
  const header = response.headers.get('content-disposition') ?? ''
  const match = /filename="([^"\\/]+)"/.exec(header)
  return match?.[1] ?? fallback
}

/** Entrega o arquivo ao navegador e solta a URL de objeto logo depois do clique. */
export function saveFile(blob: Blob, filename: string) {
  const href = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = href
  link.download = filename
  link.hidden = true
  document.body.append(link)
  link.click()
  link.remove()
  // Revogar no mesmo instante cancelaria o download em alguns navegadores.
  setTimeout(() => URL.revokeObjectURL(href), 0)
}
