---
name: altare-frontend
description: >-
  Convenções do frontend do Altare (apps/web: React 19, TypeScript, Vite, TanStack Router/Query/Table, React Hook Form + Zod, Tailwind v4): estrutura de pastas e limites (routes, features, components/ui, components/domain), onde mora cada tipo de estado, formulários com erro 422, atualização otimista, dinheiro em centavos, performance e testes com Vitest. Use sempre que for criar ou alterar tela, rota, componente, hook, formulário ou chamada de API no apps/web, mesmo que o pedido seja só 'adiciona uma tela de X' ou 'conecta isso na API'. Inclui o padrão do widget de chat flutuante (Bloco 5.3). NÃO use para aparência, tokens e primitivos (use altare-design), fluxos e heurísticas (use altare-ui-ux), checklist de acessibilidade (use altare-acessibilidade), textos (use altare-conteudo-copy) ou rotas e contratos do backend (use altare-backend-api).
---

# Frontend do Altare

## Docs a consultar
- `docs/engineering/architecture.md` §11 (estrutura e regras do frontend) e §9 (`dependency-cruiser`).
- `docs/engineering/stack.md` §5 (escolhas), §5.1 (onde mora cada cálculo), §6 (sessão e lente), §7 (testes).
- `docs/design/design-system.md` §9 (props dos componentes de domínio), §10 (padrões de interface), §12.
- O doc da área em `docs/product/features/` para a tela em construção: os critérios de aceite viram testes.
- `AGENTS.md` §1: no Nível 0 só existe o `apps/web`; API, login e PWA vêm depois (`D-028`).

## Princípios
1. **Rotas finas.** Arquivo em `routes/` só monta a página de `features/<modulo>/pages`. Assim a tela se testa sem o router.
2. **Feature se importa só pelo `index.ts`.** `components/ui` não importa de `features` nem de `lib/api`, para a vitrine `/design-system` funcionar sem backend. O `dependency-cruiser` cobra isso: corrija o import, não a regra.
3. **`components/domain` nasce no bloco que usa** (`D-028`), com as props puras de `design-system.md` §9. Enquanto só uma feature usa o componente, ele fica em `features/<m>/components`; sobe para `domain` quando a segunda precisar.
4. **Cada estado no seu lugar:**

   | Tipo | Onde | Por quê |
   | :--- | :--- | :--- |
   | Dados do servidor | TanStack Query, com *key factories* em `features/<m>/api` | Cache e invalidação após mutação |
   | Filtro, aba, seleção navegável, lente | URL (*search params* tipados) | Compartilhável e o voltar do navegador funciona |
   | Rascunho de campo, painel aberto | `useState` | É local |
   | Qualquer outra coisa | Não crie *store* global | Zustand só com necessidade comprovada |

5. **Regra numérica nunca mora no frontend.** Orçamento, estimado ponderado, custo comparável, destravado e bloqueado vêm da API (`stack.md` §5.1). No simulador, edite premissas com *debounce* e chame o endpoint de simulação. Um "totalzinho local" cria uma segunda verdade que diverge da primeira.
6. **Dinheiro é inteiro em centavos** (`*_cents`) na API e no estado. Formate só na borda, com `Money` (`Intl.NumberFormat('pt-BR')`). Nunca `parseFloat` nem `number` com decimais para valor.
7. **Autoria vem da sessão.** Não envie `created_by`, `author` nem perfil no corpo da requisição. A lente (`Visão do Casal` / `Minha visão`) muda foco e destaque, nunca a autoria.
8. **Tipos vêm do OpenAPI gerado** (`make api-types`). Não escreva tipo de resposta à mão; o *drift* derruba a CI (`altare-monorepo`).
9. **Erros pelo `code`, não pela mensagem.** A API devolve `problem+json` com `code` estável e `detail` em pt-BR. Use o `code` para decidir o comportamento e o `detail` para exibir.

   | Resposta | Comportamento |
   | :--- | :--- |
   | `422` | Mapear para os campos (`setError` do React Hook Form) |
   | `409` `version_conflict` | Avisar que o registro mudou e oferecer recarregar; nunca sobrescrever |
   | `401` | Ir ao login preservando o destino |
   | Rede | Erro inline com ação de tentar de novo; o formulário não perde o que foi digitado |

10. **Otimismo só em ação de baixo risco** (marcar tarefa, mudar status). O resto invalida a query. Valor financeiro nunca é otimista.
11. **Performance proporcional a 2 usuários.** Sem virtualização nem `memo` preventivo antes de medir. O que vale: *debounce* no simulador, tabela comparativa (TanStack Table) com rolagem contida no próprio contêiner, rotas carregadas sob demanda (*code splitting* por rota) para o PWA abrir rápido no celular e fontes autohospedadas.
12. **PDF começa nativo** (`<object>` ou nova aba). `react-pdf` só quando o painel lateral pedir (`stack.md` §5).

## Checklist (tela ou componente novo)
- [ ] Li o doc de feature e os critérios de aceite viraram testes.
- [ ] Imports respeitam a regra de camadas (`dependency-cruiser` verde).
- [ ] Nenhum cálculo de negócio no cliente; nenhum `float` em valor.
- [ ] Formulário: React Hook Form + Zod para UX, erro `422` mapeado para o campo, botão com `loading`.
- [ ] Desktop e mobile definidos (`altare-ui-ux`); estados vazio, carregando e erro existem.
- [ ] Textos em constantes da feature (`altare-conteudo-copy`).
- [ ] `lint` (Biome), `typecheck` (`tsc`) e `test` (Vitest) verdes.
- [ ] Verificação manual de acessibilidade feita (`altare-acessibilidade`).

## Bom / ruim
```tsx
// ruim: regra de negócio no cliente, float, import interno de outra feature
import { useBudget } from '@/features/budget/api/queries'
const total = items.reduce((s, i) => s + i.price * guests, 0)
<span>R$ {total.toFixed(2)}</span>

// bom: a API calcula, a borda formata, a feature expõe só o index
import { useBudgetSimulation } from '@/features/budget'
const { data } = useBudgetSimulation(scenarioId, premises) // premises com debounce
<Money cents={data.total_cents} precision="always" />
```

## Widget de chat flutuante (`D-042`, Bloco 5.3)
- Componente da casca do app, **só UI**: mensagens, campo de texto e a prévia de uma `ChangeProposal` com Confirmar e Rejeitar explícitos. Sem regra de negócio; consome a API do assistente pelo cliente OpenAPI gerado.
- O contexto da tela (rota e id do registro aberto) segue como parâmetro. O widget não lê dados de outras features.
- **O ícone flutuante e o painel provisório nascem na etapa (d) do Bloco 0.2** (`D-050`), sem regra de negócio: só o botão, o texto de que o assistente ainda não está disponível e o fechamento. **O chat de verdade (mensagens, campo de texto, prévia de `ChangeProposal`) não nasce antes do Bloco 5.3.**
- Padrão de interação em `altare-ui-ux`; foco e `aria-live` em `altare-acessibilidade`.

## Limites e vizinhas
- Aparência, tokens e primitivos: `altare-design`. Fluxo, estados e heurísticas: `altare-ui-ux`. Palavras: `altare-conteudo-copy`. Checklist de a11y: `altare-acessibilidade`.
- Rotas, DTOs e erros do lado do servidor: `altare-backend-api`. Geração de tipos e *drift*: `altare-monorepo`.
- Estratégia de testes e gates: `altare-testes-qa`. Estilo de código geral: `altare-escrita-de-codigo`.

## Em aberto
- Convivência do ícone do assistente com o "+ Registrar Rápido" no canto inferior direito: `OQ-IA-001`, item 5 (Bloco 3.1).
