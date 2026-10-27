---
name: altare-gtm-pricing
description: >-
  Skill DORMENTE: só vale depois que o usuário decidir explorar a hipótese de abrir o Altare a outros casais (D-002). Cobre posicionamento, segmentos, modelos e faixa de preço, aquisição e os pré-requisitos técnicos e jurídicos dessa abertura (multi-tenant, LGPD como obrigação, suporte, backup, custo por casal). Use quando o usuário falar em lançar, vender, cobrar, monetizar, SaaS, assinatura, plano, landing page, beta aberto, outros casais ou aquisição de clientes. Se a hipótese ainda não foi aberta pelo usuário, não proponha nada comercial: responda que está fora da premissa de uso pessoal e ofereça registrar a ideia como pergunta em aberto. NÃO use para decidir o que construir na v1 ou se o produto é bom (use `altare-produto`), para métricas de uso (use `altare-analytics-metricas`) nem para implementar autenticação, isolamento de dados ou LGPD (use `altare-seguranca-privacidade`).
---

# Go-to-market e pricing (dormente)

> **Aviso.** O Altare é de uso pessoal, exclusivo do casal. Qualquer expansão para outros casais é **hipótese futura, nunca premissa** (`D-002`, `docs/product/vision.md` §2, nota sobre expansão; `AGENTS.md` §2 regra 4). Enquanto o usuário não abrir essa hipótese de forma explícita, esta skill não produz plano comercial, preço nem mudança na v1.

## Quando ela está ativa

- **Ativa** somente se o usuário disser, nesta conversa ou numa decisão registrada, que quer explorar a abertura a outros casais.
- **Dormente** para perguntas soltas como "e se a gente vendesse isso?". Resposta padrão: "Isso está fora da premissa atual de uso pessoal (`D-002`). Posso registrar como pergunta em aberto em `docs/product/open-questions.md` e seguimos com a v1." Registrar via `altare-docs-vivas`, sem escrever plano.
- **Ao ativar,** abra uma decisão `D-xxx` de exploração dizendo o que a hipótese investiga e o que ela **não muda** na v1. O motivo: sem esse registro, a v1 passa a ser distorcida por uma hipótese que nunca foi aprovada.

## Docs a consultar

- `docs/product/vision.md` §2 (nota de expansão), §4 (diferenciação), §5 (não-objetivos), §6 (princípio de marca).
- `docs/product/personas.md` §3 (cerimonialista e fornecedores não são usuários na v1).
- `docs/product/decisions.md`: `D-001`, `D-002`, `D-023`, `D-025`, `D-026`, `D-028`.
- `docs/engineering/stack.md` §2 (sem multi-tenant), §6 (login de duas contas), §9 (candidatos de nuvem, não decididos), §12 (riscos).
- `docs/design/identity.md` §1.5 (assinatura verbal não adotada).

## Quando ativa

### Posicionamento

- Parta dos diferenciais de `vision.md` §4: o Altare une escopo, propostas, comparação, contrato, parcelas e arquivos por categoria, onde planilha, pasta e WhatsApp separam tudo. Esse é o argumento a testar, não um slogan pronto.
- **Não confessional (`D-026`):** nenhuma comunicação pressupõe tradição religiosa. O tipo de cerimônia é dado do casal.
- **Sem assinatura verbal:** `D-025` decidiu não adotar uma. Não crie slogan e o apresente como oficial.
- Não se posicione como portal ou marketplace: `vision.md` §5.2 e §4 (portais são o contraste).

### Segmentos

- **Natural:** casais no Brasil que conduzem a preparação por conta própria e contratam só cerimonialista para o dia (`vision.md` §2). *Depende de pesquisa:* tamanho do grupo e como se descrevem.
- **Fora do foco:** assessores e cerimonialistas como operadores do sistema (`D-001` rejeitou módulo multi-usuário para assessores) e fornecedores (o Altare não é marketplace).

### Preço

Não há número neste repositório e nenhum deve ser inventado. Modelos de referência e o que cada um assume:

| Modelo | Racional | Risco |
| :--- | :--- | :--- |
| Pagamento único por casamento | O casamento é um evento finito; o uso dura da largada ao Dia D | O custo de nuvem, armazenamento e IA continua depois da cobrança |
| Assinatura mensal | Acompanha custo contínuo | O casal para de usar ao casar; cobrar por algo de prazo conhecido irrita |
| Passe por temporada (prazo fixo até o Dia D mais um período de exportação) | Casa com a finitude e com a pirâmide | Exige regra de renovação e de fim de acesso |
| Base grátis (v1 manual) e camada de IA paga | A v1 já é completa sem IA (`D-005`); a IA tem custo variável | Define cedo demais o que é "básico" |

**Depende de pesquisa:** disposição a pagar e custo real por casal. Os custos conhecidos vêm de nuvem e Postgres gerenciado e armazenamento S3-compatível (`stack.md` §9, candidatos não decididos), do provedor de LLM (Bloco 5.1, em aberto) e do WhatsApp (`OQ-IA-001`).

### Aquisição

Canais candidatos, sem ordem, a validar com dados:

- **Indicação entre casais** que já usaram. *Depende de haver casais que usaram.*
- **Conteúdo** sobre planejar sem assessoria, onde está o público do segmento.
- **Cerimonialistas do dia:** recebem o Dossiê (`personas.md` §3.1), então são ponto natural de apresentação. Hipótese, sem login deles na v1.
- **Portais de casamento** são a alternativa que o Altare critica (`vision.md` §4): avalie o custo e a coerência antes de anunciar neles.
- **Momento:** o ganho maior está no marco zero (`jobs.md`, Momento 1). A aquisição precisa chegar cedo na jornada do casal.

### Pré-requisitos que a abertura dispara

| Área | O que muda | Skill dona |
| :--- | :--- | :--- |
| Multi-tenant | Hoje é um casamento e duas contas, sem cadastro público (`stack.md` §2 e §6). Passa a exigir isolamento por casal, cadastro, recuperação de acesso e convite do parceiro | `altare-arquitetura`, `altare-banco-de-dados` |
| LGPD | A exceção de uso particular e não econômico deixa de valer: base legal, direitos dos titulares, convidados como terceiros, política de privacidade | `altare-seguranca-privacidade` |
| Autenticação | O login próprio de duas contas precisa ser reavaliado (recuperação, passkeys) | `altare-seguranca-privacidade` |
| Backup | Backup automático já é requisito de implantação pendente (`D-038` item 4); com clientes vira obrigação | `altare-devops` |
| Acessibilidade | O gatilho do `axe` automatizado em `D-028` inclui "o produto se abrir a outros casais" | `altare-acessibilidade`, `altare-testes-qa` |
| Custo por casal | Nuvem, armazenamento, LLM e WhatsApp passam a escalar com os clientes | `altare-devops` |
| Suporte, termos de uso, cobrança e notas fiscais | Fora do repositório: exigem orientação jurídica e contábil profissional | usuário |

## Regras ao usar esta skill

- Nenhuma decisão comercial sacrifica a simplicidade da v1 (`vision.md` §2).
- Marque o que **depende de pesquisa de mercado** e peça a pesquisa; não preencha com número ou benchmark de memória.
- Toda conclusão que mudar escopo, arquitetura ou prazo vira `D-xxx` (`altare-docs-vivas`) e passa pela confirmação do usuário (`AGENTS.md` §3).

## Limites e vizinhas

- O que construir na v1 e se o produto é bom: `altare-produto`.
- Medir o uso (inclusive conversão, se a hipótese for ativada): `altare-analytics-metricas`.
- Implementar isolamento, autenticação e LGPD: `altare-seguranca-privacidade`.
- Custos de infraestrutura e deploy: `altare-devops`.
- Texto público e tom de voz: `altare-conteudo-copy`.
