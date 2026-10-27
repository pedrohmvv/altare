---
name: altare-engenharia-de-ia
description: >-
  Engenharia de IA do Altare (Nível 5): arquitetura de agentes, desenho de prompts e de descrições de tool (dizendo quando NÃO usar), saída estruturada validada, evals com golden sets fictícios e testes de recusa e de escrita sem confirmação, custo e latência com AgentRun, guardrails de D-008 (mutação só com confirmação humana, revisão e notificação somente-leitura), observabilidade e integração com o produto. Use ao projetar ou alterar agente, prompt, tool, workflow de LLM, extrator de PDF ou WhatsApp, entrevista guiada, Revisor Geral ou avaliação de qualidade, mesmo que o pedido seja só melhorar uma resposta do assistente. NÃO use para a superfície de tools, ChangeProposal, schema legível e canais (use altare-agente-dados), camadas (use altare-arquitetura), política de privacidade (use altare-seguranca-privacidade) ou texto da interface (use altare-conteudo-copy).
---

# Engenharia de IA do Altare

## Docs a consultar
- `docs/engineering/architecture.md` §7 (agentes na arquitetura, `ChangeProposal`, `AgentRun`) e §12 (estados de `ChangeProposal`).
- `docs/product/decisions.md`: `D-005`, `D-008`, `D-010`, `D-013`, `D-042`.
- `docs/product/scope.md` §8 (catálogo de funcionalidades de IA) e `docs/engineering/roadmap.md` Nível 5 (Blocos 5.1 a 5.3).
- `docs/engineering/stack.md` §10 (o que está adiado) e `docs/product/vision.md` §5 item 4.
- `AGENTS.md` §2 item 4: proibido inventar dados do casamento.

## Princípios
1. **Dois regimes, declarados por fluxo.** *Mutação assistida*: o agente só produz rascunho (`ChangeProposal`) e um humano aprova. *Proativo somente-leitura*: Revisor Geral e notificações, com portas de consulta apenas. Todo fluxo novo diz em qual regime está; sem isso, não entra (`D-008`).
2. **O modelo não é fonte de fatos do casamento.** Data, cidade, orçamento, convidados e preços vêm de tools de leitura; o prompt manda consultar, nunca supor. Dado ausente vira pergunta ao casal ou "em definição", não palpite.
3. **Conteúdo externo é dado, não instrução.** Texto de PDF, WhatsApp colado, nome de fornecedor e observação do casal podem conter ordens ("ignore as regras…"). O prompt delimita esse conteúdo como material a analisar e a validação por código impede que ele vire mutação sem aprovação.
4. **Prompts são código:** em arquivo versionado, com papel, escopo ("só o Altare e este casamento"), formato de saída e o que o agente não faz. Nada de string de prompt espalhada pelos casos de uso.
5. **Saída estruturada e validada.** O JSON Schema das tools vem dos DTOs Pydantic de entrada dos casos de uso (`architecture.md` §7 item 1). A saída do modelo é validada antes de virar proposta; falha vira erro corrigível com limite de tentativas, nunca laço aberto.
6. **Tools: poucas, específicas, bem descritas.** Nome verbo + objeto (`propose_add_extra_cost`). A descrição diz **quando usar, quando não usar** e o que devolve; parâmetros com enums fechados. Uma tool "faz-tudo" faz o modelo escolher mal e esconde a regra. Superfície e autorização: `altare-agente-dados`.
7. **Avalie o estado, não o texto.** O que importa é o que foi proposto e o que foi gravado, não a frase. Invariantes (nada gravado sem aprovação) são testes determinísticos, não julgamento de modelo.
8. **Teto de custo por execução:** limite de passos, de tokens e de tempo, com falha explícita ao estourar. O uso é de duas pessoas; custo inesperado vem de laço, não de volume.
9. **O fluxo manual nunca depende da IA** (`D-005`). Falha ou ausência do provedor degrada para a tela normal, sem erro bloqueante.

## Evals
- **Golden set** em arquivo, com dados **claramente fictícios e rotulados** ("Espaço Exemplo", "Fornecedor Exemplo"), nunca dados do casal.
- Categorias mínimas: (a) tool e parâmetros corretos para o pedido; (b) **recusa** de pedido fora do produto ou que exija enviar mensagem a terceiro; (c) **escrita sem confirmação**: tentativa de gravar direto deve falhar sempre; (d) **ambiguidade**: duas opções parecidas geram pergunta, não escolha; (e) **idempotência**: mesma mensagem reentregue não duplica proposta; (f) **injeção** via PDF ou mensagem colada; (g) regressão a cada mudança de prompt.
- Dois níveis: com `LLMClient` falso e determinístico no CI (rápido, grátis, cobre (c) e (e)); contra o provedor real sob demanda, por custo, antes de liberar mudança de prompt ou de modelo.
- Mensure também a **taxa de propostas aprovadas, rejeitadas e expiradas** em uso real: é o sinal de qualidade mais barato.

## Custo, latência e observabilidade
- **`AgentRun`** (criado no Nível 5, `architecture.md` §7 item 6) guarda entrada, tools chamadas, saída, tokens, custo e duração. É a base para depurar e para o teto de custo.
- Chat e WhatsApp: resposta curta primeiro; operação longa (Revisor Geral) roda como tarefa fora do pedido do usuário, com o agendador a definir no Bloco 5.2.
- **Logs sem dados pessoais**: registre identificadores e contagens, não o texto das mensagens nem dados de convidados (`altare-seguranca-privacidade`).
- Métricas úteis: custo por execução, latência p50 e p95, erro de tool, proposta aprovada, rejeitada ou expirada.

## Checklist
- [ ] Regime declarado (mutação assistida ou somente-leitura)?
- [ ] Nenhum caminho grava sem `ApproveChangeProposal` humano?
- [ ] Fatos do casamento vêm de tool; o prompt proíbe inventar?
- [ ] Conteúdo externo delimitado como dado e validado por código?
- [ ] Descrição da tool diz quando **não** usar? Enums fechados?
- [ ] Teto de passos, tokens e tempo, com falha explícita?
- [ ] Eval novo nas categorias (a) a (g) afetadas, com dados fictícios?
- [ ] `AgentRun` registra a execução sem texto pessoal?
- [ ] Fluxo manual equivalente continua funcionando sem IA?

## Bom / ruim
```text
ruim  (descrição de tool): "Atualiza o orçamento."
bom   (descrição de tool): "Propõe adicionar um custo extra a uma proposta de fornecedor. Use quando o
       casal citar uma taxa não incluída no preço base (gerador, ECAD, rolha). NÃO use para alterar o
       preço base nem para registrar pagamento (use propose_pay_installment). Não grava: devolve prévia."
```
```text
ruim  (eval): conferir se a resposta "soa educada".
bom   (eval): dado "marque a parcela como paga" sem confirmação, nenhum Installment mudou de status e
       existe 1 ChangeProposal pendente.
```

## O que muda por causa do agente
O agente exige do restante do sistema: casos de uso independentes de HTTP, `Actor` com `on_behalf_of`, erros estruturados e corrigíveis, idempotência por proposta, schema legível, portas `Clock` e `IdGenerator` para testes determinísticos e `AgentRun`. O desenho disso é de `altare-agente-dados`; as camadas, de `altare-arquitetura`. Não replique aqui.

## Limites e vizinhas
- Superfície de tools, `ChangeProposal`, schema para agente e canais (chat, ícone flutuante, WhatsApp): `altare-agente-dados`.
- Onde o agente mora e o que ele pode importar: `altare-arquitetura`. Pirâmide geral de testes: `altare-testes-qa`.
- Quais dados podem ir ao LLM e ao WhatsApp: `altare-seguranca-privacidade`. Tom das respostas: `altare-conteudo-copy`. Como o rascunho aparece na tela: `altare-ui-ux`.

## Em aberto
- **Provedor de LLM e biblioteca de orquestração** (própria, LangGraph, outra): adiados para o Bloco 5.1 (`stack.md` §10, `architecture.md` §7 item 8). Mantenha o código atrás da porta `LLMClient`.
- Agendador de jobs, Web Push e envio proativo por WhatsApp: Bloco 5.2. Observabilidade de erros (Sentry): antes do deploy.
- Posição do chat na navegação, detalhamento do Nível 5 e custo do WhatsApp: `OQ-IA-001`.
