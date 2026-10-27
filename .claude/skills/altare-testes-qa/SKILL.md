---
name: altare-testes-qa
description: >-
  Estratégia de testes e qualidade automatizada do Altare, em Python e TypeScript. Cobre a pirâmide por camada, TDD (RED antes de GREEN), Hypothesis para invariantes numéricas, Vitest com Testing Library, Playwright desktop e mobile, SQLite temporário, o portão em PostgreSQL antes do primeiro deploy e a configuração e os gates de Ruff, Pyright, Biome, tsc, import-linter, dependency-cruiser e pre-commit. Use sempre que for implementar feature, regra de negócio, correção de bug ou refatoração (o teste vem primeiro), ao decidir que teste escrever, ao configurar linter, formatter, tipos ou quality gate, mesmo que o usuário só diga implemente isso. NÃO use para rodar ou manter o pipeline no CI (use altare-devops), para o checklist manual de acessibilidade (use altare-acessibilidade) nem para revisar um diff (use altare-code-review).
---

# Testes e qualidade

Dinheiro, parcelas e contagem de convidados são o que o casal confere à mão. Um erro de centavo ou de arredondamento destrói a confiança no produto inteiro, e não há equipe de QA: os testes são o QA. Por isso a regra de negócio é testada sem banco, sem rede e em milissegundos.

## Docs a consultar

- `docs/engineering/architecture.md` §9 (pirâmide por camada e contratos `import-linter`) e §3 (fakes das portas).
- `docs/engineering/stack.md` §4 (portabilidade, portão Postgres) e §7 (qualidade e automação).
- `docs/design/design-system.md` §12 (testes do front, teste do `tokens.css`) e `docs/product/decisions.md` D-028 (o que foi adiado).
- Critérios de aceite em `docs/product/features/*.md` e fluxos em `docs/design/experience.md` §4.

## Princípios

1. **TDD: RED antes de GREEN.** Escreva o teste, rode, veja falhar **pelo motivo certo** (a asserção, não um `ImportError`) e mostre a saída da falha. Só então escreva o mínimo para passar e refatore com o teste verde. Um teste que nunca falhou não prova nada. Não vale para config, arquivo gerado (`tokens.css`) nem experimento descartável.
2. **Teste na camada mais barata que prova a regra.** Domínio puro primeiro; só suba de camada quando o risco estiver na integração.
3. **Os critérios de aceite dos docs de feature viram casos de teste.** O teste cita o `F-XXX-NN` que verifica.
4. **Dados de teste são fictícios e rotulados** ("Espaço Exemplo"). Nunca dados reais do casamento (`AGENTS.md` §2).
5. **Um teste, um comportamento, nome em português que descreve o resultado** (`test_cenario_ativo_unico_ao_promover_outro`).
6. **Teste de componente por papel e comportamento** (`getByRole`, teclado), não por classe CSS nem por detalhe de implementação.

## Pirâmide por camada

| Camada | O que testar | Ferramenta |
| :--- | :--- | :--- |
| Domínio | Regras puras e **invariantes numéricas** (orçamento, contadores de convidados, parcelas, arredondamento de F-ORC-03) | pytest + Hypothesis |
| Aplicação | Casos de uso com **fakes das portas**, sem banco e sem rede; um caso de uso = uma transação | pytest |
| Infraestrutura | Repositórios, mapeamento e migrations Alembic (sobe, desce, sobe) em SQLite real e temporário | pytest |
| Adaptadores HTTP | `TestClient` com app composto; status e `code` de erro (`problem+json`); snapshot do OpenAPI | pytest, httpx |
| Frontend | Componentes, hooks de tela e utilitários; navegação da casca; validação Zod | Vitest + Testing Library |
| Ponta a ponta | Fluxos críticos de `experience.md` §4 em projeto *desktop* e *mobile*; entra **com o login** | Playwright |
| Portabilidade | A suíte de integração também contra **PostgreSQL** (contêiner efêmero) **antes do primeiro deploy** | Docker ou testcontainers |

Hypothesis serve onde há **propriedade**, não exemplo: soma das parcelas fecha o total, per capita arredondado nunca perde nem inventa centavo, contador ponderado nunca fica negativo. Exemplo isolado cobre o caso, a propriedade cobre a classe.

## Gates de qualidade

| Gate | Ferramenta | Escopo | Bloqueia o merge? |
| :--- | :--- | :--- | :--- |
| Lint e formato Python | **Ruff** (`check` e `format --check`) | só `apps/api` | Sim |
| Tipos Python | **Pyright**, modo `standard` (endurecer gradualmente) | `apps/api` | Sim |
| Contratos de camada | **import-linter** (`architecture.md` §9) | `apps/api` | Sim |
| Testes Python | pytest | `apps/api` | Sim |
| Lint e formato web | **Biome** (inclui regras de acessibilidade); Ruff não se aplica | `apps/web` | Sim |
| Tipos web | `tsc` (`strict`) | `apps/web` | Sim |
| Limites entre `features` | **dependency-cruiser** | `apps/web` | Sim |
| Testes web | Vitest, inclusive o que falha se `tokens.css` estiver defasado | `apps/web` | Sim |
| Build do web e drift do OpenAPI | `make api-types` sem diff | monorepo | Sim |
| E2E | Playwright desktop e mobile | após o login | Sim, quando existir |
| Suíte em PostgreSQL | pytest contra Postgres | `apps/api` | Bloqueia o **deploy** |
| Acessibilidade | verificação manual (`altare-acessibilidade`) | PR que toca UI | Sim, via checklist do PR |

Adiados por `D-028`, com gatilho: `axe` automatizado, *snapshots* visuais e script contra `hex` em componente. Não os reintroduza sem o gatilho.

`pre-commit` roda localmente os verificadores rápidos para o erro aparecer antes do commit. O que roda só no CI fica fora do hook para não travar o commit atômico.

## Bom / ruim

```python
# ruim: o teste passa por sorte e nunca falhou
def test_total():
    assert total_cents(1000, [200]) > 0

# bom: nomeia a regra, cita a feature, assevera o valor exato
def test_custo_comparavel_soma_extras_ao_preco_base():  # F-PRP-03
    assert comparable_total_cents(1_000_00, [200_00, 50_00]) == 1_250_00
```

```python
# bom: propriedade, não exemplo
@given(st.lists(st.integers(min_value=1, max_value=10**7), min_size=1))
def test_parcelas_somam_o_total(parts):
    assert sum(split_installments(sum(parts), len(parts))) == sum(parts)
```

## Checklist

- [ ] Escrevi o teste primeiro e vi ele falhar pela asserção?
- [ ] Está na camada mais barata que prova a regra?
- [ ] Há caso de borda (zero, um, arredondamento, exclusão lógica)?
- [ ] O critério de aceite do doc de feature está coberto e citado?
- [ ] Os gates da tabela passam localmente?
- [ ] Dados de teste fictícios e rotulados?

## Limites e vizinhas

- **Definir** gates e estratégia é aqui; **executar** o pipeline, ambientes e deploy é `altare-devops`.
- Acessibilidade manual: `altare-acessibilidade`. Escrita do código sob teste: `altare-escrita-de-codigo`.
- Camadas e fakes de portas (o desenho): `altare-arquitetura`. Revisão do diff: `altare-code-review`.
- Evals de agente de IA têm método próprio: `altare-engenharia-de-ia`.

## Em aberto

- **Hooks do `pre-commit`:** `stack.md` §7 lista Ruff, Pyright e Biome; `architecture.md` §2 e §14 acrescentam `import-linter` e `dependency-cruiser`. Decidido na `D-043`: o `pre-commit` e o `dependency-cruiser` ficam adiados (o primeiro, até o `apps/api`; o segundo, até a primeira `feature`). Ao criá-los, fechar a lista de hooks e registrar.
