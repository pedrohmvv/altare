import {
  BadgeCheck,
  CircleAlert,
  CircleArrowRight,
  CircleCheck,
  FileText,
  Handshake,
  HeartHandshake,
  Lock,
  LockOpen,
  type LucideIcon,
  MessageCircle,
  MessagesSquare,
  Paperclip,
} from 'lucide-react'
import type { ReactNode } from 'react'
import { Card } from '@/components/ui/card'
import { claro, forma, marca } from '../../../../docs/design/identidade-visual/tokens.json'

const token = (name: string) => {
  const found = claro.find((color) => color.token === name)
  if (!found) throw new Error(`Token ausente no tokens.json: ${name}`)
  return found
}
const musgo = token('ink-muted')
const amendoaForte = token('border-strong')
const percent = (ratio: number) => `${Math.round(ratio * 100)}%`

const SECTION = 'flex flex-col gap-5'
const H2 = 'text-heading'
const SOURCE = 'text-body-sm text-ink-muted'

function SectionHead({ id, title, source }: { id: string; title: string; source: string }) {
  return (
    <div className="flex flex-col gap-1">
      <h2 id={id} className={H2}>
        {title}
      </h2>
      <p className={SOURCE}>{source}</p>
    </div>
  )
}

/** Cartão de catálogo: o ativo, o nome, para que serve e o arquivo (guia, págs. 12, 30 e 31). */
function Specimen({
  name,
  use,
  file,
  stage,
  children,
}: {
  name: string
  use: string
  file: string
  stage: string
  children: ReactNode
}) {
  return (
    <li className="flex flex-col gap-2">
      <Card className={`flex items-center justify-center overflow-hidden ${stage}`}>
        {children}
      </Card>
      <h3 className="mt-1 text-ui font-semibold text-ink">{name}</h3>
      <p className={SOURCE}>{use}</p>
      <p className="text-num-sm text-ink-muted">{file}</p>
    </li>
  )
}

function Specs({ rows }: { rows: readonly (readonly [string, string])[] }) {
  return (
    <dl className="grid grid-cols-[6rem_minmax(0,1fr)] gap-x-6 gap-y-2 border-t border-border pt-4 md:grid-cols-[6rem_minmax(0,1fr)_6rem_minmax(0,1fr)]">
      {rows.map(([label, value]) => (
        <div key={label} className="contents">
          <dt className="text-body-sm text-ink-muted">{label}</dt>
          <dd className="text-body-sm text-ink">{value}</dd>
        </div>
      ))}
    </dl>
  )
}

const ARRANJOS = [
  {
    name: 'Wordmark',
    use: 'Cabeçalho do app no desktop, e-mail, exportações.',
    file: 'altare-wordmark-<cor>.svg',
    src: '/brand/logo/altare-wordmark-oliva.svg',
    alt: 'Wordmark Altare em oliva',
    size: 'w-3/5',
  },
  {
    name: 'Símbolo',
    use: 'Cabeçalho mobile, favicon, ícone do app, avatar.',
    file: 'altare-simbolo-<cor>.svg',
    src: '/brand/logo/altare-simbolo-oliva.svg',
    alt: 'Símbolo Altare em oliva',
    size: 'w-1/2',
  },
  {
    name: 'Vertical',
    use: 'Tela de login, splash do PWA, capa do Dossiê.',
    file: 'altare-vertical-<cor>.svg',
    src: '/brand/logo/altare-vertical-oliva.svg',
    alt: 'Lockup vertical Altare em oliva',
    size: 'w-1/2',
  },
  {
    name: 'Assinatura formal',
    use: 'Dossiê do Dia D, impressão, rodapés formais.',
    file: 'altare-assinatura-<cor>.svg',
    src: '/brand/logo/altare-assinatura-carvao.svg',
    alt: 'Assinatura formal ALTARE em carvão',
    size: 'w-3/5',
  },
] as const

const ARCOS = [
  {
    name: 'Arco simples',
    use: 'Moldura de ilustrações e estados vazios.',
    file: 'fonte/ornamentos/arco-simples.svg',
    src: '/brand/ornamentos/arco-simples.svg',
    size: 'h-44',
  },
  {
    name: 'Arco duplo',
    use: 'Tela de login, splash e capa do Dossiê.',
    file: 'fonte/ornamentos/arco-duplo.svg',
    src: '/brand/ornamentos/arco-duplo.svg',
    size: 'h-44',
  },
  {
    name: 'Arcada',
    use: 'Faixa de cabeçalho em documentos impressos.',
    file: 'fonte/ornamentos/arcada.svg',
    src: '/brand/ornamentos/arcada.svg',
    size: 'w-4/5',
  },
] as const

const RAMOS = [
  {
    name: 'Ramo grande',
    use: 'Tela de login e 404. Único com nervuras e azeitonas.',
    file: 'fonte/ornamentos/ramo-grande.svg',
    src: '/brand/ornamentos/ramo-grande.svg',
    size: 'w-3/4',
  },
  {
    name: 'Ramo pequeno',
    use: 'Estados vazios e confirmações discretas.',
    file: 'fonte/ornamentos/ramo-pequeno.svg',
    src: '/brand/ornamentos/ramo-pequeno.svg',
    size: 'w-1/2',
  },
  {
    name: 'Faixa de ramos',
    use: 'Cabeçalho do Dossiê e divisórias raras.',
    file: 'fonte/ornamentos/ramo-faixa.svg',
    src: '/brand/ornamentos/ramo-faixa.svg',
    size: 'w-5/6',
  },
] as const

// Mapa semântico fixo de identity.md §7 (guia, pág. 33). Nomes completos das classes: o Tailwind só gera o que lê.
const ICONES: readonly { name: string; lucide: string; Icon: LucideIcon; tone: string }[] = [
  {
    name: 'Consenso favorito',
    lucide: 'heart-handshake',
    Icon: HeartHandshake,
    tone: 'text-primary',
  },
  {
    name: 'Conversar juntos',
    lucide: 'messages-square',
    Icon: MessagesSquare,
    tone: 'text-attention-ink',
  },
  {
    name: 'Atenção · custo extra',
    lucide: 'circle-alert',
    Icon: CircleAlert,
    tone: 'text-accent',
  },
  { name: 'Destravado', lucide: 'lock-open', Icon: LockOpen, tone: 'text-consensus-ink' },
  { name: 'Bloqueado', lucide: 'lock', Icon: Lock, tone: 'text-ink-muted' },
  {
    name: 'Pago · concluído',
    lucide: 'circle-check',
    Icon: CircleCheck,
    tone: 'text-consensus-ink',
  },
  {
    name: 'Próximo passo',
    lucide: 'circle-arrow-right',
    Icon: CircleArrowRight,
    tone: 'text-primary',
  },
  { name: 'Abrir WhatsApp', lucide: 'message-circle', Icon: MessageCircle, tone: 'text-primary' },
  { name: 'Anexo', lucide: 'paperclip', Icon: Paperclip, tone: 'text-ink' },
  { name: 'PDF', lucide: 'file-text', Icon: FileText, tone: 'text-ink' },
  { name: 'Orçamento oficial', lucide: 'badge-check', Icon: BadgeCheck, tone: 'text-primary' },
  {
    name: 'Alternativa sem coração',
    lucide: 'handshake',
    Icon: Handshake,
    tone: 'text-ink-muted',
  },
]

const FAVICON_SIZES = [16, 32, 48, 64, 96] as const

const REGRAS_DOSSIE = [
  ['Papel branco, sem fundo', 'Economia de tinta e leitura em preto e branco.'],
  ['Assinatura formal + arcada', 'ALTARE em versal, hairline e o título do documento.'],
  ['Serifa nos títulos, mono nos dados', 'Horários, telefones e valores sempre tabulares.'],
  [`Bordas ${amendoaForte.nome}`, `${amendoaForte.hex} garante leitura em fotocópia.`],
  ['Uma seção por página', 'Quebra de página por fornecedor no documento final.'],
  ['Campos vazios explícitos', '[a definir] até o casal preencher. Nada é inventado.'],
] as const

/**
 * Catálogo da identidade (D-058): arranjos da marca, arco, ramo, ícones, favicon e ícone do app, e as
 * peças do Dossiê. É o guia de identidade (págs. 12, 30, 31, 33, 36 e 42) em formato de catálogo, com
 * os ativos copiados em `public/brand` e os valores do `tokens.json`.
 */
export function IdentityShowcase() {
  return (
    <div className="mt-12 flex flex-col gap-12">
      <section aria-labelledby="conf-arranjos" className={SECTION}>
        <SectionHead
          id="conf-arranjos"
          title="Arranjos da marca"
          source="Guia, pág. 12 · quatro arranjos, nenhum lado a lado"
        />
        <ul className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {ARRANJOS.map((arranjo) => (
            <Specimen key={arranjo.name} {...arranjo} stage="h-64">
              {arranjo.name === 'Assinatura formal' ? (
                // Na pág. 12 a assinatura vem com a hairline e o título do documento abaixo.
                <div className="flex w-full flex-col items-center gap-3">
                  <img src={arranjo.src} alt={arranjo.alt} className={arranjo.size} />
                  <hr className="w-3/4 border-border-strong" />
                  <p className="text-eyebrow text-ink-muted">Dossiê do Dia D</p>
                </div>
              ) : (
                <img src={arranjo.src} alt={arranjo.alt} className={arranjo.size} />
              )}
            </Specimen>
          ))}
        </ul>
        <p className="text-ui font-semibold text-ink">
          Não existe lockup horizontal (símbolo ao lado do wordmark): A + Altare repetiria a mesma
          letra.
        </p>
      </section>

      <section aria-labelledby="conf-arco" className={SECTION}>
        <SectionHead
          id="conf-arco"
          title="Arco"
          source="Guia, pág. 30 · o arco de volta perfeita"
        />
        <ul className="grid gap-5 md:grid-cols-3">
          {ARCOS.map((arco) => (
            <Specimen key={arco.name} {...arco} stage="h-56">
              <img src={arco.src} alt={arco.name} className={arco.size} />
            </Specimen>
          ))}
        </ul>
        <Specs
          rows={[
            ['Proporção', '1 : 1,4 (meia-circunferência sobre retângulo)'],
            [
              'Traço',
              `${forma.ornamento_traco_px.toString().replace('.', ',')} px, sem preenchimento`,
            ],
            [
              'Cor',
              `${musgo.nome} ${musgo.hex} a ${percent(forma.ornamento_opacidade)}; no escuro, Líquen`,
            ],
            ['Leitura', 'arquitetura, não religião: ecoa a nave e o altar'],
          ]}
        />
      </section>

      <section aria-labelledby="conf-ramo" className={SECTION}>
        <SectionHead
          id="conf-ramo"
          title="Ramo de oliveira"
          source="Guia, pág. 31 · o ramo de oliveira"
        />
        <ul className="grid gap-5 md:grid-cols-3">
          {RAMOS.map((ramo) => (
            <Specimen key={ramo.name} {...ramo} stage="h-56">
              <img src={ramo.src} alt={ramo.name} className={ramo.size} />
            </Specimen>
          ))}
        </ul>
        <Specs
          rows={[
            ['Desenho', 'haste em curva, folhas alternadas que diminuem'],
            [
              'Traço',
              `${forma.ornamento_traco_px.toString().replace('.', ',')} px, sem preenchimento`,
            ],
            [
              'Cor',
              `${musgo.nome} ${musgo.hex} a ${percent(forma.ornamento_opacidade)}; nunca verde vivo`,
            ],
            ['Limite', 'um ornamento por tela, nunca atrás da marca'],
          ]}
        />
      </section>

      <section aria-labelledby="conf-icones" className={SECTION}>
        <SectionHead
          id="conf-icones"
          title="Ícones com significado fixo"
          source="Guia, pág. 33 · identity.md §7 · Lucide"
        />
        <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {ICONES.map(({ name, lucide, Icon, tone }) => (
            <li key={lucide}>
              <Card className="flex h-full flex-col gap-3">
                <Icon aria-hidden className={`size-10 ${tone}`} />
                <span className="mt-2 text-ui font-semibold text-ink">{name}</span>
                <span className="text-num-sm text-ink-muted">{lucide}</span>
              </Card>
            </li>
          ))}
        </ul>
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:gap-12">
          <div className="flex flex-col gap-2">
            <p className="text-eyebrow text-ink-muted">
              Tamanhos · traço 1,5 px em qualquer tamanho
            </p>
            <div className="flex items-end gap-8">
              {[
                ['16 px', 'size-4'],
                ['20 px', 'size-5'],
                ['24 px', 'size-6'],
              ].map(([label, size]) => (
                <div key={label} className="flex flex-col items-start gap-2">
                  <CircleArrowRight aria-hidden className={`${size} text-ink`} />
                  <span className="text-num-sm text-ink-muted">{label}</span>
                </div>
              ))}
            </div>
          </div>
          <p className="max-w-prose text-body text-ink">
            Lucide, cantos arredondados, herdando currentColor. 20 px é o padrão; 16 em tabelas
            densas; 24 na navegação. Ícone sempre acompanhado de texto: cor e ícone nunca são o
            único sinal.
          </p>
        </div>
      </section>

      <section aria-labelledby="conf-favicon" className={SECTION}>
        <SectionHead
          id="conf-favicon"
          title="Favicon e ícone do app"
          source="Guia, pág. 36 · favicon e ícone do app"
        />
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="flex flex-col gap-5">
            <div className="flex flex-col gap-2">
              <div className="rounded-card bg-surface-sunken p-3">
                <div className="flex items-center gap-3 rounded-control bg-surface px-4 py-3 md:max-w-xs">
                  <img
                    src="/brand/favicon/altare-favicon.svg"
                    alt="Favicon na aba"
                    width={24}
                    height={24}
                  />
                  <span className="min-w-0 flex-1 truncate text-ui-sm text-ink">
                    Altare · Visão geral
                  </span>
                  <span aria-hidden className="text-ink-muted">
                    ×
                  </span>
                </div>
              </div>
              <p className="text-ui-sm font-semibold text-ink-muted">Aba clara</p>
              <p className={SOURCE}>A aba escura chega com o tema escuro (D-028).</p>
            </div>
            <div className="flex flex-col gap-3">
              <p className="text-eyebrow text-ink-muted">
                Favicon · quadrado oliva com raio de {percent(marca.app_icon.raio_favicon)}
              </p>
              <ul className="flex flex-wrap items-end gap-8">
                {FAVICON_SIZES.map((size) => (
                  <li key={size} className="flex flex-col items-center gap-2">
                    <img
                      src="/brand/favicon/altare-favicon.svg"
                      alt={`Favicon de ${size} px`}
                      width={size}
                      height={size}
                    />
                    <span className="text-num-sm text-ink-muted">{size}</span>
                  </li>
                ))}
              </ul>
              <p className="text-body-sm text-ink-muted">
                O favicon usa sempre o símbolo pequeno (mensa de 2 módulos), com versal de{' '}
                {percent(marca.app_icon.versal_favicon)} do lado. Arquivos: favicon.svg, favicon.ico
                (16, 32, 48).
              </p>
            </div>
          </div>
          <div className="flex flex-col gap-3">
            <Card variant="muted" className="flex flex-wrap items-end gap-8">
              <figure className="flex flex-col items-center gap-2">
                <img
                  src="/brand/app-icon/altare-app-icon.svg"
                  alt="Ícone do app, como entregue"
                  width={96}
                  height={96}
                />
                <figcaption className="text-num-sm text-ink-muted">como entregue</figcaption>
              </figure>
              <figure className="flex flex-col items-center gap-2">
                <img
                  src="/brand/app-icon/altare-app-icon.svg"
                  alt="Ícone do app, como o sistema exibe"
                  width={96}
                  height={96}
                  className="overflow-hidden"
                  style={{ borderRadius: percent(marca.app_icon.raio_favicon) }}
                />
                <figcaption className="text-num-sm text-ink-muted">como o sistema exibe</figcaption>
              </figure>
            </Card>
            <p className="text-ui font-semibold text-ink">
              Ícone do app: quadrado cheio; o sistema arredonda.
            </p>
            <p className="text-body-sm text-ink-muted">
              Versal = {percent(marca.app_icon.versal_app)} do lado, dentro da zona segura.
            </p>
            <p className="text-body-sm text-ink-muted">
              Arquivos: altare-app-icon.svg e PNG de 180, 192 e 512 px.
            </p>
          </div>
        </div>
      </section>

      <section aria-labelledby="conf-dossie" className={SECTION}>
        <SectionHead
          id="conf-dossie"
          title="Dossiê do Dia D"
          source="Guia, pág. 42 · Dossiê do Dia D · impressão"
        />
        <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
          <Card className="flex flex-col items-center gap-3 self-start py-10">
            <img
              src="/brand/logo/altare-assinatura-carvao.svg"
              alt="Assinatura formal ALTARE"
              className="w-48"
            />
            <hr className="w-60 max-w-full border-border-strong" />
            <p className="text-eyebrow text-ink">Dossiê do Dia D</p>
            <img src="/brand/ornamentos/arcada.svg" alt="Arcada" className="mt-2 w-60 max-w-full" />
          </Card>
          <ol className="flex flex-col gap-5">
            {REGRAS_DOSSIE.map(([title, text], i) => (
              <li key={title} className="flex gap-4">
                <span
                  aria-hidden
                  className="flex size-7 shrink-0 items-center justify-center rounded-pill bg-primary text-num-sm text-primary-ink"
                >
                  {i + 1}
                </span>
                <div className="flex flex-col">
                  <span className="text-ui font-semibold text-ink">{title}</span>
                  <span className="text-body-sm text-ink-muted">{text}</span>
                </div>
              </li>
            ))}
          </ol>
        </div>
        <p className={SOURCE}>
          Aqui estão só as peças e as regras: o documento do Dossiê nasce no Bloco 4.2 (F-DOS).
        </p>
      </section>
    </div>
  )
}
