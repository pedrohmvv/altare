// Ordem e nomes das seções da vitrine. Cada `id` é o do título da seção, e um teste confere que o
// índice acompanha a página (identity-showcase.test.tsx).
const PARTS = [
  {
    name: 'Identidade',
    sections: [
      ['conf-cores', 'Cores'],
      ['conf-tipografia', 'Tipografia'],
      ['conf-arranjos', 'Arranjos da marca'],
      ['conf-arco', 'Arco'],
      ['conf-ramo', 'Ramo de oliveira'],
      ['conf-icones', 'Ícones com significado fixo'],
      ['conf-favicon', 'Favicon e ícone do app'],
      ['conf-dossie', 'Dossiê do Dia D'],
    ],
  },
  {
    name: 'Componentes',
    sections: [
      ['conf-botoes', 'Botões'],
      ['conf-campos', 'Campos'],
      ['conf-segmentado', 'Seletor segmentado'],
      ['conf-dinheiro', 'Dinheiro'],
      ['conf-selos', 'Selos e cartões'],
      ['conf-tabelas', 'Tabelas'],
      ['conf-vazios', 'Estados vazios'],
      ['conf-sobreposicoes', 'Diálogo, cartão, abas, dica e notificações'],
    ],
  },
] as const

/** Índice de links para as seções da vitrine, em duas partes (D-058). */
export function ShowcaseIndex() {
  return (
    <nav aria-label="Índice da vitrine" className="mt-8 grid gap-6 md:grid-cols-2">
      {PARTS.map((part) => (
        <div key={part.name} className="flex flex-col gap-2">
          <p className="text-eyebrow text-ink-muted">{part.name}</p>
          <ul className="flex flex-wrap gap-x-5 gap-y-1">
            {part.sections.map(([id, label]) => (
              <li key={id}>
                <a
                  href={`#${id}`}
                  className="text-ui-sm text-primary underline-offset-4 hover:text-primary-hover hover:underline"
                >
                  {label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  )
}
