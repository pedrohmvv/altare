import { claro, tipografia } from '../../../../docs/design/identidade-visual/tokens.json'

// Nomes completos das classes: o Tailwind só gera o que lê escrito no código.
const TEXT_CLASS: Record<string, string> = {
  display: 'text-display',
  title: 'text-title',
  heading: 'text-heading',
  name: 'text-name',
  'body-lg': 'text-body-lg',
  body: 'text-body',
  ui: 'text-ui',
  'body-sm': 'text-body-sm',
  'ui-sm': 'text-ui-sm',
  eyebrow: 'text-eyebrow',
  'ui-xs': 'text-ui-xs',
  'num-xl': 'text-num-xl',
  'num-lg': 'text-num-lg',
  num: 'text-num',
  'num-sm': 'text-num-sm',
}

/** Cores do tema claro e escala tipográfica, lidas do `tokens.json` (guia, págs. 20 e 26). */
export function TokensShowcase() {
  return (
    <div className="mt-12 flex flex-col gap-12">
      <section aria-labelledby="conf-cores" className="flex flex-col gap-4">
        <h2 id="conf-cores" className="text-heading">
          Cores
        </h2>
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {claro.map((color) => (
            <li key={color.token} className="flex gap-3">
              <span
                aria-hidden
                className="size-12 shrink-0 rounded-control border border-border"
                style={{ backgroundColor: `var(--${color.token})` }}
              />
              <div className="flex min-w-0 flex-col">
                <span className="text-ui font-semibold text-ink">{color.nome}</span>
                <span className="text-num-sm text-ink-muted">
                  {color.token} · {color.hex}
                </span>
                <span className="text-body-sm text-ink-muted">{color.funcao}</span>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="conf-tipografia" className="flex flex-col gap-4">
        <h2 id="conf-tipografia" className="text-heading">
          Tipografia
        </h2>
        <ul className="flex flex-col">
          {tipografia.escala.map((step) => (
            <li
              key={step.token}
              className="grid gap-1 border-b border-border py-3 last:border-b-0 md:grid-cols-[12rem_minmax(0,1fr)] md:items-baseline md:gap-6"
            >
              <div className="flex flex-col">
                <span className="text-num-sm font-medium text-ink">{step.token}</span>
                <span className="text-body-sm text-ink-muted">
                  {step.px}/{step.lh} · {step.peso} · {step.uso}
                </span>
              </div>
              <span className={`${TEXT_CLASS[step.token] ?? ''} text-ink`}>{step.amostra}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
