import { Plus, Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

const VARIANTS = ['primary', 'secondary', 'ghost', 'soft-destructive', 'link'] as const
const SIZES = ['sm', 'md', 'lg'] as const

// Conferência visual dos primitivos (etapa (c)); a vitrine /design-system a substitui na etapa (e).
export function Conferencia() {
  return (
    <div className="mt-12 flex flex-col gap-12">
      <section aria-labelledby="conf-botoes" className="flex flex-col gap-4">
        <h2 id="conf-botoes" className="text-heading">
          Botões
        </h2>
        {SIZES.map((size) => (
          <div key={size} className="flex flex-wrap items-center gap-3">
            {VARIANTS.map((variant) => (
              <Button key={variant} variant={variant} size={size}>
                {variant}
              </Button>
            ))}
          </div>
        ))}
        <div className="flex flex-wrap items-center gap-3">
          <Button>
            <Plus aria-hidden /> Novo contato
          </Button>
          <Button loading>Salvando</Button>
          <Button disabled>Desabilitado</Button>
          <Button variant="secondary" size="icon" aria-label="Salvar">
            <Save aria-hidden />
          </Button>
        </div>
      </section>

      <section aria-labelledby="conf-campos" className="flex max-w-md flex-col gap-5">
        <h2 id="conf-campos" className="text-heading">
          Campos
        </h2>
        <Input
          label="Nome do espaço"
          placeholder="Espaço Exemplo A"
          hint="Como aparece nas listas"
        />
        <Input label="Preço base" prefix="R$" suffix="por pessoa" inputMode="numeric" required />
        <Input
          label="Capacidade"
          defaultValue="abc"
          error="Informe um número de convidados."
          required
        />
        <Input label="Campo desabilitado" disabled defaultValue="Espaço Exemplo B" />
        <Textarea label="Observações" hint="Só vocês dois veem isto" />
        <Textarea label="Observações com erro" error="Escreva ao menos uma frase." />
        <Select label="Categoria" placeholder="Escolha uma categoria">
          <option value="espaco">Espaço</option>
          <option value="buffet">Buffet</option>
        </Select>
        <Select label="Categoria com erro" error="Escolha uma categoria." placeholder="Escolha">
          <option value="espaco">Espaço</option>
        </Select>
        <div className="flex flex-col">
          <Checkbox label="Incluir bebidas" />
          <Checkbox label="Marcado" defaultChecked />
          <Checkbox label="Todos os convidados" checked="indeterminate" />
          <Checkbox label="Desabilitado" disabled />
        </div>
      </section>
    </div>
  )
}
