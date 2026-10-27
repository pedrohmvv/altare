export interface BrandCopy {
  from: string
  to: string
}

// Só o que o app usa de componentes/ (identity.md §2.6): o resto é guia, PNG de documento e loja de apps.
const FAVICON_FILES = [
  'altare-favicon.svg',
  'favicon.ico',
  'altare-favicon-16.png',
  'altare-favicon-32.png',
  'altare-favicon-48.png',
]
const APP_ICON_FILES = [
  'altare-app-icon.svg',
  'altare-app-icon-180.png',
  'altare-app-icon-192.png',
  'altare-app-icon-512.png',
]

/** Decide o que sai do pacote de identidade (caminhos relativos a ele) para public/brand. */
export function planBrandCopy(sourceFiles: string[]): BrandCopy[] {
  const available = new Set(sourceFiles)

  const required = (dir: string, files: string[], target: string): BrandCopy[] =>
    files.map((name) => {
      const from = `${dir}/${name}`
      if (!available.has(from)) {
        throw new Error(`Ativo de marca ausente no pacote de identidade: ${from}`)
      }
      return { from, to: `${target}/${name}` }
    })

  const logos = sourceFiles
    .filter((f) => /^fonte\/altare-[^/]+\.svg$/.test(f))
    .map((from) => ({ from, to: `logo/${from.slice('fonte/'.length)}` }))
  const ornaments = sourceFiles
    .filter((f) => /^fonte\/ornamentos\/[^/]+\.svg$/.test(f))
    .map((from) => ({ from, to: `ornamentos/${from.slice('fonte/ornamentos/'.length)}` }))

  return [
    ...logos,
    ...ornaments,
    ...required('componentes/favicon', FAVICON_FILES, 'favicon'),
    ...required('componentes/app-icon', APP_ICON_FILES, 'app-icon'),
  ].sort((a, b) => a.to.localeCompare(b.to))
}
