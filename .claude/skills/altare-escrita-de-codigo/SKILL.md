---
name: altare-escrita-de-codigo
description: >-
  Como escrever código limpo e sem cara de IA no Altare (Python em apps/api, TypeScript em apps/web):
  nomes, funções pequenas, erros de domínio, dinheiro em centavos, onde o arquivo mora. Use ao
  escrever, editar ou refatorar qualquer código de produção ou de teste do repositório.
---

# Escrita de código

Código que o casal e o próprio autor vão ler daqui a seis meses, sozinhos, sem assessoria. O critério é simples: quem abre o arquivo entende o que ele faz e por que existe, sem comentário e sem caçar três arquivos.

## Docs a consultar

- `docs/engineering/architecture.md` §3 (limites pragmáticos), §4 (onde cada arquivo mora, backend), §8 (erros e mapeamento HTTP), §11 (frontend).
- `docs/engineering/stack.md` §4 (dinheiro, datas, enums, IDs) e §5.1 (onde mora cada cálculo).
- `docs/design/design-system.md` §11 (textos em constantes por feature, formatos).
- `AGENTS.md` §2, regra 4 (nunca inventar dados do casamento).

## Princípios

1. **Um arquivo, uma responsabilidade nomeada.** Em `application/commands/` há um arquivo por caso de uso de escrita (`activate_budget_scenario.py`), e em `queries/` um por consulta. Arquivo com nome `utils`, `helpers`, `common` ou `misc` é sinal de que faltou decidir onde o código mora.
2. **Função pequena faz uma coisa e tem nome de verbo.** Se o nome precisa de "e" ou "and", são duas funções. Se precisa de comentário para explicar um bloco, extraia o bloco e dê a ele o nome que o comentário teria.
3. **Nomes seguem o vocabulário dos docs.** Identificadores em inglês, como nos docs (`ScopeCategory`, `BudgetScenario`, `decide`, `activate`); texto exibido ao casal em pt-BR, centralizado em constantes por feature. Misturar os dois idiomas num identificador (`calcularTotal_cents`) dificulta buscar no código o que os docs descrevem.
4. **Erro de domínio tem tipo próprio.** Regra violada vira `DomainRuleViolated` (ou `NotFound`, `Forbidden`, `Conflict`), que o adaptador converte para HTTP (`architecture.md` §8). Capturar `Exception` para devolver `None` esconde a falha de quem precisa corrigir.
5. **Valide na borda, confie no miolo.** Pydantic valida a entrada HTTP e o domínio protege as próprias invariantes. Checar o mesmo `None` em cada camada duplica a regra e a deixa divergir.
6. **Dinheiro é inteiro em centavos**, com sufixo `_cents`, do banco à borda. `float` em valor monetário gera diferença de centavo que o casal vai ver na tela de parcelas.
7. **Regra numérica só no backend** (`stack.md` §5.1). O frontend exibe o que a API devolve; reimplementar soma ou arredondamento no React cria duas verdades.
8. **Duplicação se resolve na terceira ocorrência, no lugar certo.** Duas cópias ainda pedem mais contexto; três pedem uma função no módulo dono da regra. Uma abstração criada para um único uso é especulação.

## Sinais de código de IA (evite)

| Sinal | Por que é ruim | Correção |
| :--- | :--- | :--- |
| Comentário que repete o código (`# soma os valores`) | Envelhece e vira mentira | Apague; melhore o nome. Comente só o porquê não óbvio (uma regra de negócio, um limite de biblioteca) |
| Abstração para um caso só (`BaseRepository`, `StrategyFactory`) | Indireção sem variação (`architecture.md` §3, item 4) | Função ou classe direta; porta só onde há variação ou E/S externa |
| `try/except Exception` com `log` e retorno silencioso | Engole o erro e esconde bug | Deixe o erro de domínio subir ao adaptador; capture só o que sabe tratar |
| Validação repetida em toda camada | Regra duplicada | Valide na borda (Pydantic) e no domínio |
| Arquivo solto fora de `modules/<m>/<camada>/` ou de `features/<m>/` | Quebra o `import-linter` e o gate de limites do frontend | Mova para a camada certa |
| Nome genérico (`data`, `result`, `manager`, `handle`) | Não diz o que contém | `installments_due`, `ScenarioCostSummary` |
| Parâmetro ou flag que ninguém usa | Superfície inventada | Remova; reintroduza quando houver o segundo uso |
| Texto de interface espalhado no JSX | Tom e vocabulário divergem | Constante por feature (`design-system.md` §11) |
| Dado fictício que parece real do casamento | Viola `AGENTS.md` §2 | Rotule: "Espaço Exemplo", "Fornecedor Exemplo" |

## Bom / ruim

```python
# ruim: float, exceção genérica, retorno silencioso
def total(price, extras):
    try:
        return round(price * 1.1 + sum(extras), 2)
    except Exception:
        return None

# bom: centavos inteiros e erro de domínio tipado
def comparable_total_cents(base_price_cents: int, extras_cents: list[int]) -> int:
    return base_price_cents + sum(extras_cents)
```

```python
# bom: o domínio protege a regra, o adaptador traduz para 422
def activate(self, scenario: BudgetScenario) -> None:
    if scenario.is_deleted:
        raise DomainRuleViolated("Cenário excluído não pode ser ativado.")
```

```tsx
// ruim: o frontend refaz a regra numérica
const total = items.reduce((sum, i) => sum + i.base_price_cents * guests, 0);

// bom: a tela exibe scenario.total_cents, já calculado no backend,
// e só o formata com o primitivo Money (components/ui)
```

## Checklist antes de entregar

- [ ] Cada arquivo novo está na pasta que `architecture.md` §4 ou §11 prevê?
- [ ] Nenhuma função faz mais de uma coisa nem exige comentário para ser entendida?
- [ ] Nenhum `except` amplo, nenhuma validação repetida, nenhum parâmetro sem uso?
- [ ] Dinheiro em centavos e sem regra numérica duplicada no frontend?
- [ ] Texto de interface em constante por feature, em pt-BR e sem emoji?
- [ ] Dados de exemplo rotulados como fictícios?
- [ ] O teste que prova o comportamento existe (veja `altare-testes-qa`)?

## Limites e vizinhas

- **Escrever** código é aqui; **revisar** um diff é `altare-code-review`.
- Camadas, `public.py`, portas e eventos: `altare-arquitetura`.
- Rotas, DTOs HTTP e `problem+json`: `altare-backend-api`.
- Tabelas e migrations: `altare-banco-de-dados`.
- Estrutura de componentes React e estado: `altare-frontend`.
- Tokens, cores e texto do produto: `altare-design` e `altare-conteudo-copy`.
