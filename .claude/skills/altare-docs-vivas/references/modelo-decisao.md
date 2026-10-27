# Modelo de decisão (`docs/product/decisions.md`)

Formato extraído das entradas reais (`D-029`, `D-038`, `D-041`). Cada entrada é separada da anterior por uma linha `---`. Não renumere nem reescreva entradas antigas.

## Cabeçalho

```markdown
## D-0xx — Título curto no formato "Tema: o que foi decidido"
- **Data:** AAAA-MM-DD
- **Fase:** Fase em que o projeto está (ex.: Implementação — Nível 0; Pós-Congelamento (Detalhamento de Produto))
```

## Campos opcionais de origem (use um quando houver)

- `- **Pedido do usuário:**` citação ou paráfrase fiel do pedido (`D-029`, `D-039`).
- `- **Esclarecimento do usuário:**` quando corrige ou refina algo (`D-026`).

## Corpo

```markdown
- **Decisão:**
  1. Primeiro ponto, verificável e específico. Cite o doc afetado e outros `D-xxx` entre crases.
  2. Segundo ponto.
- **Ajustes em arquivos aprovados:** `arquivo.md` (o que mudou). Use quando a decisão altera um doc já aprovado.
- **Razão:** por que, em uma ou duas frases. O que doía antes.
- **O que ficou rejeitado:**
  - Alternativa considerada e o motivo da rejeição.
  - Outra alternativa, com o motivo.
```

## Fechamento (use o que se aplicar)

- `- **Resolve:** `OQ-XXX-nnn`` quando fecha uma pergunta de `open-questions.md` (`D-026`).
- `- **Inalterado:**` o que **não** mudou, para evitar leitura errada (`D-028`).
- `- **Premissas mantidas:**` (`D-026`).
- `- **Adiado, com gatilho para retomar:**` seguido de tabela `Item | Gatilho` (`D-028`).
- `- **Aprovado (AAAA-MM-DD):**` o que o usuário aprovou, com a data e, se útil, a palavra dele (`D-029`).
- `- **Escolhido pelo usuário:**` quando ele escolheu entre opções (`D-038`).
- `- **Pendente:**` o próximo passo e se tem urgência.
- `- **Em aberto (`OQ-XXX-nnn`, sem bloquear ...):**` quando abre uma pergunta nova (`D-042`).

## Regras de escrita

1. Uma decisão, um tema. Se há dois assuntos, são duas entradas.
2. Cada ponto da decisão precisa ser testável: alguém consegue dizer se foi cumprido.
3. A "Razão" explica o problema, não repete a decisão.
4. A seção "O que ficou rejeitado" nunca fica vazia: se nada foi rejeitado, provavelmente não havia decisão.
5. Revisão de decisão antiga: nova entrada que cita a antiga (`D-020` revisou `D-019`). Não edite a antiga.
6. Citações a docs usam caminho relativo a `docs/` entre crases e `§` para seção.
7. Datas absolutas. Sem "hoje", "ontem" ou "semana passada".
8. Aprovação só entra depois que o usuário aprovou. Antes disso, use `**Pendente:**`.
