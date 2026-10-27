---
name: altare-banco-de-dados
description: >-
  Persistência do Altare: SQLAlchemy 2, migrations Alembic, índices, constraints, dinheiro em
  centavos, UUID, histórico (version, deleted_at), portabilidade SQLite para PostgreSQL. Use ao criar
  ou alterar tabela, coluna, índice, migration, repositório ou consulta SQL, mesmo que seja só um
  campo novo.
---

# Banco de dados do Altare

## Docs a consultar
- `docs/engineering/stack.md` §4 (convenções e portabilidade SQLite para PostgreSQL, as 9 regras) e §3 (SQLAlchemy síncrono, Alembic).
- `docs/engineering/architecture.md` §5 (derivar, não duplicar), §10 (mixin de histórico e exclusão lógica), §12 (mapa do domínio e máquinas de estado), §3 itens 2 e 3.
- Spec de cada área em `docs/product/features/` para campos, estados e regras antes de modelar. As entidades entram **junto do bloco que as usa** (`stack.md` §11 item 3).

## Princípios
1. **Persista fato, derive o resto.** `Estimado`, `Contratado`, `Realizado`, contadores de convidados, `Destravado` e custo comparável são calculados na leitura. Coluna "espelho" cria dois lugares para errar e exige sincronizar; só `Planejado (Teto)` é decisão persistida.
2. **Dinheiro é inteiro em centavos** (`BIGINT`), coluna com sufixo `_cents`. Nunca `float` nem `Numeric` com arredondamento implícito. Cálculo per capita usa o arredondamento definido na spec e testado.
3. **Enum é `VARCHAR` + `CHECK`** (`native_enum=False`). Enum nativo do Postgres não existe no SQLite e trava a migração futura.
4. **Tempo:** instantes em UTC via `TypeDecorator` que preserva fuso (o SQLite descarta); vencimentos e prazos em `DATE`; exibição em `America/Sao_Paulo` só na borda.
5. **IDs UUID** (v7 quando disponível, senão v4): não expõem contagem sequencial e não colidem ao migrar.
6. **SQLite configurado na conexão:** `PRAGMA foreign_keys=ON`, `journal_mode=WAL`, `busy_timeout`. Sem `foreign_keys=ON` as FKs são decoração.
7. **Sem SQL específico de SQLite.** JSON pelo tipo `JSON` do SQLAlchemy, sem consulta profunda dentro do JSON. Isso é o que torna a troca para Postgres mecânica.
8. **Todo registro herda o mixin** (`architecture.md` §10): `id`, `created_at/updated_at`, `created_by/updated_by` (da sessão; o aprovador humano quando a proposta veio de agente), `deleted_at/deleted_by`, `version`. Repositório filtra `deleted_at IS NULL` por padrão; restaurar é caso de uso explícito.
9. **Unicidade com exclusão lógica = índice único parcial** (`WHERE deleted_at IS NULL`). Exemplo: exatamente um `BudgetScenario` ativo por casamento, garantido por índice, não só por código.
10. **Convenção de nomes de constraints no `MetaData`**, obrigatória para o Alembic em batch mode gerar `ALTER` reproduzível.
11. **Modelagem incremental:** não crie tabela de entidade que nenhum bloco usa ainda.

## Migrations (Alembic)
- `render_as_batch=True` para SQLite. Uma migration por intenção, nome em inglês descritivo.
- Teste de integração: **subir, descer, subir**. Migration sem `downgrade` verificado não entra.
- Migration de dados separada da de schema. Nunca editar migration já aplicada em ambiente com dados reais; crie outra.
- Antes do primeiro deploy: suíte inteira também em PostgreSQL (container efêmero) e script único SQLite para Postgres validado por contagem de linhas e somatório financeiro por tabela (`stack.md` §4 itens 8 e 9).

## Checklist
- [ ] A coluna é fato ou deveria ser derivada? Há spec dizendo qual?
- [ ] Dinheiro em `_cents BIGINT`; datas em `DATE`; instantes em UTC; id UUID?
- [ ] Enum com `CHECK`, valores iguais aos do domínio e da spec (`Pendente`/`Pago`, `Rascunho`/`Convidado`...)?
- [ ] Mixin aplicado e unicidade escrita como índice parcial com `deleted_at IS NULL`?
- [ ] FKs e índices nas colunas usadas em filtro das listagens e do Dossiê? (volume é pequeno: índice por uso real, não por hábito)
- [ ] Constraint com nome pela convenção do `MetaData`?
- [ ] Migration com `downgrade` e teste sobe/desce/sobe?
- [ ] Nenhuma função ou sintaxe só do SQLite (`json_extract`, `INSERT OR REPLACE`, `rowid`)?
- [ ] Consulta de leitura devolve DTO e não carrega agregado (`architecture.md` §3 item 3)?
- [ ] Tabela e colunas têm `comment` quando o nome não bastar (ver agente, abaixo)?

## Bom / ruim
```python
# ruim: float, enum nativo, duas fontes do mesmo total, unicidade sem parcial
base_price = mapped_column(Float)
status = mapped_column(Enum(InstallmentStatus))        # enum nativo
contracted_total_cents = mapped_column(BigInteger)     # espelho da soma dos contratos
UniqueConstraint("wedding_id", "name")                 # bloqueia recriar após excluir

# bom
base_price_cents = mapped_column(BigInteger, nullable=False)
status = mapped_column(Enum(InstallmentStatus, native_enum=False, create_constraint=True))
Index("uq_scenario_name_live", "wedding_id", "name", unique=True,
      sqlite_where=text("deleted_at IS NULL"), postgresql_where=text("deleted_at IS NULL"))
```

## O que muda por causa do agente
O assistente do Nível 5 (`D-042`) lê o schema por *views* e por busca, e escreve só por casos de uso. Para o banco isso significa nomes autoexplicativos, enums fechados, `comment` em tabelas e colunas e *views* de leitura. O desenho completo (chaves de busca, busca aproximada) está em `altare-agente-dados`; não replique aqui. Regra prática de hoje: nomeie pensando em quem lê sem conhecer o código.

## Limites e vizinhas
- Quais dados são pessoais, por quanto tempo guardar, o que exportar e excluir: `altare-seguranca-privacidade`. Aqui entra só a **implementação** (colunas, exclusão lógica, comando de purga).
- Onde o repositório e a `UnitOfWork` moram: `altare-arquitetura`. Contrato HTTP e `version` na rota: `altare-backend-api`.
- Testes de repositório, migração e Postgres: `altare-testes-qa`. Pipeline e deploy: `altare-devops`.
- Schema legível por agente: `altare-agente-dados`.

## Em aberto
- Purga definitiva de **registros** (hard delete) não está especificada; os docs só preveem purga administrativa de **arquivos** excluídos (`architecture.md` §10). Defina junto com `altare-seguranca-privacidade` se o produto abrir para outros casais.
- Provedor de PostgreSQL gerenciado e de storage: candidatos em `stack.md` §9, ainda não decididos (`altare-devops`).
- Busca aproximada portátil entre SQLite e Postgres: `OQ-IA-001`.
