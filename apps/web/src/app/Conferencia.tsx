import { BadgeCheck, CircleAlert, HeartHandshake, Plus, Save, Trash2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogTrigger,
} from '@/components/ui/dialog'
import { EmptyState } from '@/components/ui/empty-state'
import { Input } from '@/components/ui/input'
import { Money } from '@/components/ui/money'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { SegmentedControl } from '@/components/ui/segmented-control'
import { Select } from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/components/ui/toast'
import { Tooltip } from '@/components/ui/tooltip'

const VARIANTS = ['primary', 'secondary', 'ghost', 'soft-destructive', 'link'] as const
const SIZES = ['sm', 'md', 'lg'] as const
const ESPACOS = [
  { nome: 'Espaço Exemplo A', capa: 1_000_000, extras: 248_000 },
  { nome: 'Espaço Exemplo B', capa: 850_000, extras: 145_050 },
  { nome: 'Espaço Exemplo C', capa: 1_200_000, extras: 0 },
]
const CATEGORIAS = [
  { value: 'espaco', label: 'Espaço' },
  { value: 'buffet', label: 'Buffet' },
  { value: 'foto', label: 'Fotografia (indisponível)', disabled: true },
]

const LENTES = [
  { value: 'casal', label: 'Visão do Casal' },
  { value: 'minha', label: 'Minha visão' },
]
const ETAPAS = [
  { value: 'a', label: 'Em definição' },
  { value: 'b', label: 'Definido' },
  { value: 'c', label: 'Indisponível', disabled: true },
]

// Variantes e estados dos primitivos. Hover, ativo e foco são estados vivos: passe o mouse, clique e use Tab.
export function Conferencia() {
  const { toast } = useToast()

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
          <Button variant="secondary" size="icon" aria-label="Salvar">
            <Save aria-hidden />
          </Button>
        </div>
        <p className="text-body-sm text-ink-muted">Carregando</p>
        <div className="flex flex-wrap items-center gap-3">
          {VARIANTS.map((variant) => (
            <Button key={variant} variant={variant} loading>
              {variant}
            </Button>
          ))}
        </div>
        <p className="text-body-sm text-ink-muted">Desabilitado</p>
        <div className="flex flex-wrap items-center gap-3">
          {VARIANTS.map((variant) => (
            <Button key={variant} variant={variant} disabled>
              {variant}
            </Button>
          ))}
          <Button variant="secondary" size="icon" aria-label="Salvar (desabilitado)" disabled>
            <Save aria-hidden />
          </Button>
        </div>
        <p className="text-body-sm text-ink-muted">
          Hover, ativo e foco: passem o mouse, cliquem e usem Tab.
        </p>
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
        <Textarea label="Observações desabilitadas" disabled defaultValue="Somente leitura" />
        <Select label="Categoria" placeholder="Escolha uma categoria" options={CATEGORIAS} />
        <Select
          label="Categoria com erro"
          error="Escolha uma categoria."
          placeholder="Escolha"
          options={CATEGORIAS}
        />
        <Select
          label="Categoria obrigatória"
          required
          placeholder="Escolha uma categoria"
          options={CATEGORIAS}
        />
        <Select
          label="Categoria desabilitada"
          disabled
          defaultValue="espaco"
          options={CATEGORIAS}
        />
        <div className="flex flex-col">
          <Checkbox label="Incluir bebidas" />
          <Checkbox label="Marcado" defaultChecked />
          <Checkbox label="Todos os convidados" checked="indeterminate" />
          <Checkbox label="Desabilitado" disabled />
          <Checkbox label="Desabilitado e marcado" disabled defaultChecked />
        </div>
      </section>

      <section aria-labelledby="conf-segmentado" className="flex flex-col gap-4">
        <h2 id="conf-segmentado" className="text-heading">
          Seletor segmentado
        </h2>
        <div className="flex flex-wrap items-center gap-6">
          <SegmentedControl aria-label="Lente de exemplo" options={LENTES} defaultValue="casal" />
          <SegmentedControl
            aria-label="Etapa de exemplo, com opção desabilitada"
            options={ETAPAS}
            defaultValue="a"
          />
        </div>
      </section>

      <section aria-labelledby="conf-dinheiro" className="flex flex-col gap-4">
        <h2 id="conf-dinheiro" className="text-heading">
          Dinheiro
        </h2>
        <ul className="flex flex-col gap-1 text-body">
          <li>
            Resumo (auto): <Money cents={2_800_000} />
          </li>
          <li>
            Com centavos (auto): <Money cents={123_456} />
          </li>
          <li>
            Parcela (always): <Money cents={2_800_000} precision="always" />
          </li>
          <li>
            Custo extra (comparable): <Money cents={248_000} signed tone="comparable" />
          </li>
          <li>
            Dentro do teto: <Money cents={-310_000} signed tone="positive" />
          </li>
          <li>
            Acima do teto: <Money cents={145_050} signed precision="always" tone="attention" />
          </li>
          <li>
            Apoio: <Money cents={9_950_00} tone="muted" />
          </li>
        </ul>
      </section>

      <section aria-labelledby="conf-selos" className="flex flex-col gap-4">
        <h2 id="conf-selos" className="text-heading">
          Selos e cartões
        </h2>
        <div className="flex flex-wrap items-center gap-3">
          <Badge>Neutro</Badge>
          <Badge variant="primary">Primário</Badge>
          <Badge variant="outline">Contorno</Badge>
          <Badge variant="consensus" icon={<HeartHandshake />}>
            Consenso favorito
          </Badge>
          <Badge variant="attention" icon={<CircleAlert />}>
            1 extra pendente
          </Badge>
          <Badge variant="consensus" icon={<BadgeCheck />}>
            Oficial
          </Badge>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <h3 className="text-name">Espaço Exemplo A</h3>
            <p className="text-body-sm text-ink-muted">Cartão padrão, plano e sem sombra</p>
          </Card>
          <Card variant="interactive" asChild>
            <a href="#conf-selos">
              <h3 className="text-name">Espaço Exemplo B</h3>
              <p className="text-body-sm text-ink-muted">Interativo: passe o mouse ou use Tab</p>
            </a>
          </Card>
          <Card variant="muted">
            <h3 className="text-name">Espaço Exemplo C</h3>
            <p className="text-body-sm text-ink-muted">Cartão suave, para blocos de apoio</p>
          </Card>
        </div>
      </section>

      <section aria-labelledby="conf-tabelas" className="flex flex-col gap-6">
        <h2 id="conf-tabelas" className="text-heading">
          Tabelas
        </h2>
        {(['comfortable', 'compact'] as const).map((density) => (
          <Table
            key={density}
            label={`Comparativo de espaços, densidade ${density}`}
            density={density}
            stickyFirstColumn
            className="min-w-[36rem]"
          >
            <TableCaption>Comparativo de espaços (exemplo), densidade {density}</TableCaption>
            <TableHeader>
              <TableRow>
                <TableHead>Espaço</TableHead>
                <TableHead numeric>Preço de capa</TableHead>
                <TableHead numeric>Extras</TableHead>
                <TableHead numeric>Custo real comparável</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {ESPACOS.map((espaco) => (
                <TableRow key={espaco.nome}>
                  <TableHead scope="row">{espaco.nome}</TableHead>
                  <TableCell numeric>
                    <Money cents={espaco.capa} precision="always" />
                  </TableCell>
                  <TableCell numeric>
                    <Money
                      cents={espaco.extras}
                      precision="always"
                      signed
                      tone={espaco.extras > 0 ? 'comparable' : 'default'}
                    />
                  </TableCell>
                  <TableCell numeric>
                    <Money cents={espaco.capa + espaco.extras} precision="always" />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ))}
      </section>

      <section aria-labelledby="conf-vazios" className="grid gap-4 md:grid-cols-2">
        <h2 id="conf-vazios" className="text-heading md:col-span-2">
          Estados vazios
        </h2>
        <Card>
          <EmptyState
            headingLevel={3}
            title="Ainda sem fornecedores nesta categoria"
            description="Que tal adicionar o primeiro contato?"
            action={<Button>Adicionar contato</Button>}
          />
        </Card>
        <Card>
          <EmptyState
            headingLevel={3}
            illustration="arco"
            title="Nada por aqui ainda"
            description="Quando houver possibilidades, elas aparecem aqui."
          />
        </Card>
        <Card className="md:col-span-2">
          <EmptyState
            headingLevel={3}
            illustration="ramo-grande"
            title="Não encontramos esta página"
            description="O ramo grande é o da página não encontrada."
          />
        </Card>
      </section>

      <section aria-labelledby="conf-sobreposicoes" className="flex flex-col gap-6">
        <h2 id="conf-sobreposicoes" className="text-heading">
          Diálogo, cartão, abas, dica e notificações
        </h2>

        <div className="flex flex-wrap items-center gap-3">
          <Dialog>
            <DialogTrigger asChild>
              <Button>Registrar decisão</Button>
            </DialogTrigger>
            <DialogContent
              title="Registrar decisão"
              description="Confirmem o Espaço Exemplo A como a escolha do casal."
            >
              <Input
                label="Observação"
                hint="Opcional"
                placeholder="Por que escolhemos este espaço"
              />
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="secondary">Cancelar</Button>
                </DialogClose>
                <DialogClose asChild>
                  <Button
                    onClick={() =>
                      toast({
                        title: 'Decisão registrada',
                        description: 'Espaço Exemplo A.',
                        tone: 'success',
                      })
                    }
                  >
                    Confirmar
                  </Button>
                </DialogClose>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="secondary">Ver nota do espaço</Button>
            </PopoverTrigger>
            <PopoverContent
              title="Nota do Espaço Exemplo A"
              description="Cartão ancorado no gatilho, sem escurecer a página. Esc, Fechar ou um clique fora o fecham."
            />
          </Popover>
          <Tooltip content="Mover para a lixeira">
            <Button variant="secondary" size="icon" aria-label="Excluir fornecedor">
              <Trash2 aria-hidden />
            </Button>
          </Tooltip>
        </div>

        <Tabs defaultValue="ativo">
          <TabsList aria-label="Orçamento (exemplo)">
            <TabsTrigger value="ativo">Orçamento ativo</TabsTrigger>
            <TabsTrigger value="simulador">Simulador</TabsTrigger>
            <TabsTrigger value="pagamentos">Pagamentos</TabsTrigger>
            <TabsTrigger value="historico">Histórico de decisões</TabsTrigger>
            <TabsTrigger value="anexos">Anexos</TabsTrigger>
            <TabsTrigger value="arquivadas" disabled>
              Arquivadas
            </TabsTrigger>
          </TabsList>
          <TabsContent value="ativo">
            Total estimado: <Money cents={12_480_000} precision="always" />
          </TabsContent>
          <TabsContent value="simulador">Painel do simulador (exemplo)</TabsContent>
          <TabsContent value="pagamentos">Painel de pagamentos (exemplo)</TabsContent>
          <TabsContent value="historico">Painel do histórico (exemplo)</TabsContent>
          <TabsContent value="anexos">Painel de anexos (exemplo)</TabsContent>
        </Tabs>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            variant="secondary"
            onClick={() =>
              toast({ title: 'Salvo', description: 'Espaço Exemplo A.', tone: 'success' })
            }
          >
            Notificar sucesso
          </Button>
          <Button
            variant="secondary"
            onClick={() =>
              toast({
                title: 'Falta um extra',
                description: 'Informem o valor do transporte.',
                tone: 'attention',
              })
            }
          >
            Notificar atenção
          </Button>
          <Button
            variant="secondary"
            onClick={() => toast({ title: 'Lista atualizada', tone: 'info' })}
          >
            Notificar informação
          </Button>
          <Button
            variant="secondary"
            onClick={() =>
              toast({
                title: 'Contato arquivado',
                tone: 'info',
                action: {
                  label: 'Desfazer',
                  altText: 'Desfazer pelo histórico do contato',
                  onClick: () => toast({ title: 'Contato restaurado', tone: 'success' }),
                },
              })
            }
          >
            Notificar com Desfazer
          </Button>
        </div>
      </section>
    </div>
  )
}
