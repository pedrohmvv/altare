# Modelo de especificação de feature (`docs/product/features/<area>.md`)

Formato extraído de `contatos.md` e dos demais arquivos da pasta. Um arquivo por área (`D-029`); as features de uma área compartilham o prefixo `F-<ÁREA>-NN`.

## Índice

1. Cabeçalho
2. Visão da Área
3. Bloco de feature
4. Fora desta área
5. Pontos a validar em uso

## 1. Cabeçalho

```markdown
# Features: <Nome da Área> (`features/<arquivo>.md`)

> **Status:** **Rascunho, aguardando aprovação do usuário.** Cobre o **Bloco X.Y**: <resumo do conteúdo>.
> *(Depois da aprovação: "**Aprovado pelo usuário em AAAA-MM-DD** (`D-0xx`).")*
>
> **Onde aparece na tela:** área **<Nome>** (`docs/design/experience.md` §3.1, item N).
>
> **Fontes:** `docs/product/scope.md` §N, `docs/design/experience.md`, `docs/product/jobs.md` (Jx), `D-0xx`.
>
> **Convenções:** `F-XXX-nn` identifica a feature. "Autor" é o usuário da sessão. Estados e valores derivados nunca são digitados. Nada é pré-carregado nem presumido sobre o casamento (`AGENTS.md` §2).

---
```

## 2. Visão da Área

```markdown
## Visão da Área

**Jobs atendidos:** <frase com os jobs de `jobs.md`>.

| Objeto | O que é | Tem <propriedade chave>? |
| :--- | :--- | :--- |
| **<Objeto>** | <definição curta> | Sim / Não |

---
```

## 3. Bloco de feature (repita)

```markdown
## F-XXX-01 — <Nome da feature> (`D-0xx`, quando nasceu de uma decisão)

<Um parágrafo: o que é e para que serve. Quando útil, a captura rápida no celular e no desktop.>

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto, obrigatório | <regra de validação e o que acontece em caso de erro> |
| **<Campo derivado>** | Derivado | <de onde vem; nunca digitado> |

**Estados:** `Estado A` → `Estado B` · `Estado C`.   <!-- quando houver máquina de estados -->

**Regras**
1. Regra numerada, uma por linha, verificável.
2. Exclusão é lógica e recuperável; diga o que impede excluir.
3. Efeitos em outras áreas (e qual `F-XXX-nn` os trata).

**Critérios de aceite**
- Cenário concreto com dados fictícios rotulados ("Espaço Exemplo") e o resultado esperado.
- Caso de erro com mensagem acionável.
- Comportamento no celular quando for relevante.

---
```

## 4. Fora desta área

```markdown
## Fora desta área (v1)
- **<Ideia>:** v1.1+ (`scope.md` §N) ou "não entra" (`D-0xx`), com o motivo curto.
```

## 5. Pontos a validar em uso

Padronize o título como `Pontos a validar em uso`, para o `grep -n "^## Pontos"` achar (`altare-produto` usa essa seção como roteiro de validação).

```markdown
## Pontos a validar em uso
1. O que pode incomodar e como reverter, sem mudar a regra (ex.: trocar um rótulo).
2. ~~Ponto de bloco anterior~~: **resolvido em `D-0xx`**.
```

Dependências com blocos seguintes entram aqui também, marcadas com o bloco. Itens resolvidos ficam riscados e apontam para a decisão.

## Regras de escrita

1. Campos em tabela, regras numeradas e critérios de aceite verificáveis: viram testes (`altare-testes-qa`).
2. Diga o que é **derivado** (`docs/engineering/architecture.md` §5).
3. Exemplos fictícios e rotulados; nenhum dado real ou inventado do casamento.
4. Cada feature referencia o bloco do roadmap e os `D-xxx` que a originaram.
5. O doc **prevalece** sobre `scope.md` onde houver diferença; ajuste `scope.md` na mesma resposta.
6. Só vira "Aprovado" depois da aprovação explícita do usuário; registre `D-0xx` (ver `modelo-decisao.md`).
