---
name: altare-agente-dados
description: >-
  Ponte entre os dados do Altare e o assistente (Nível 5, D-042): tools = casos de uso, escrita só por
  ChangeProposal com confirmação (D-008), schema legível por agente, canais de chat e WhatsApp. Use ao
  criar tool ou canal do assistente, expor dado ao agente ou desenhar tabela ou view que o agente lê.
---

# Dados para o agente do Altare

## Docs a consultar
- `docs/product/decisions.md`: `D-042` (três canais, núcleo único), `D-008` (mutação só com confirmação), `D-005`, `D-027`.
- `docs/engineering/architecture.md` §7 (agente como adaptador de entrada, `ChangeProposal`, `AgentRun`), §3, §8 (erros).
- `docs/product/vision.md` §5 (não é mensageiro) e `docs/product/scope.md` §8 item 6.
- `docs/product/features/contatos.md` F-CTT-10 (busca global, base da busca aproximada). Pendências em `docs/product/open-questions.md` `OQ-IA-001`.
- Detalhes do WhatsApp: [references/canal-whatsapp.md](references/canal-whatsapp.md).

## Princípios
1. **Uma tool é um caso de uso.** Ela chama `application/commands|queries` e nada abaixo disso: nunca SQL, repositório ou rota HTTP. Assim regra, histórico e autorização são os mesmos de quem usa a tela. Tool que contorna o caso de uso cria um segundo caminho de escrita sem as regras.
2. **Mesma autorização da API.** O agente roda com `Actor(kind="agent", on_behalf_of=Noivo|Noiva)`, derivado da sessão (chat) ou do número vinculado (WhatsApp). Ele nunca vê mais que a pessoa vê, e a lente `Minha visão` é filtro de tela, não autorização.
3. **Leitura é livre; escrita é proposta.** Tools de leitura recebem **só portas de consulta**, sem `UnitOfWork`: gravar fica impossível por construção. Tools de escrita se chamam `propose_*` e chamam `ProposeChange(use_case, payload)`, que valida, calcula a prévia e persiste um `ChangeProposal`. **Não existe tool de aprovar.** Só a sessão humana executa `ApproveChangeProposal` (`D-008`).
4. **Idempotência por proposta.** Cada `ChangeProposal` tem uma chave de idempotência (conversa + mensagem + tool + hash do payload). Retry do modelo ou reentrega do webhook devolve a mesma proposta, não cria outra. Aprovar duas vezes devolve o resultado da primeira. Aprovar com `version` defasada falha com `version_conflict` e a proposta precisa ser refeita.
5. **Erro que o agente consegue corrigir.** A tool devolve o mesmo `problem+json` da API (`code` estável, `detail` em pt-BR) mais o necessário para a próxima tentativa: o campo inválido, os valores aceitos de um enum e, em ambiguidade, a lista de candidatos (ex.: três fornecedores com nome parecido). Mensagem genérica faz o agente inventar.
6. **Um canal é um adaptador fino.** Traduz mensagem para o núcleo e a resposta para o formato do canal; não tem regra de negócio nem prompt próprio. Trocar de canal não pode mudar o que é permitido.
7. **WhatsApp é canal entre o casal e o Altare, nunca com fornecedores** e não lê conversas privadas do casal (`vision.md` §5, `D-042`). Tool que envia mensagem a terceiro não existe.

## Schema legível por agente
O agente descobre o sistema pelos nomes e descrições. Projete para quem lê sem conhecer o código:
- **Nomes autoexplicativos**, no vocabulário do domínio (`base_price_cents`, `paid_cents`, `next_step_due_on`). Nada de `val1`, `flag`, `tipo2`.
- **Enums fechados** com os valores das specs (`Pendente`/`Pago`, `Em análise`/`Escolhida`/`Descartada`). Valor livre vira alucinação.
- **`comment` em tabela e coluna** quando o nome não esgotar o sentido, dizendo unidade e regra ("em centavos", "exclusão lógica: ignorar se preenchido").
- **Views de leitura** para o que o agente mais pergunta (parcelas a pagar, próximos passos, custo comparável por categoria), que escondem derivações e `deleted_at`. Elas reutilizam as consultas das telas (`architecture.md` §3 item 3), não reimplementam a regra.
- **Chave de busca por nome aproximado:** achar fornecedor, convidado ou categoria por nome parecido. A busca global (F-CTT-10) é por trecho, sem acento e **sem correção de digitação**; a tolerância a erro de digitação é adição do Nível 5. Ela deve rodar igual em SQLite e PostgreSQL (`OQ-IA-001`): prefira candidatos filtrados e comparados na aplicação, sem extensão de banco.
- Ambiguidade nunca é resolvida em silêncio: devolva candidatos e peça escolha.

## Checklist
- [ ] A tool chama um caso de uso existente (ou cria um, reutilizável pela API)?
- [ ] Leitura sem `UnitOfWork`; escrita só via `ProposeChange`? Nenhuma tool aprova.
- [ ] `Actor` com `on_behalf_of` vem de sessão ou número vinculado, nunca do texto da mensagem?
- [ ] Chave de idempotência definida; reentrega não duplica?
- [ ] Erro devolve `code`, `detail` em pt-BR, campo e valores aceitos?
- [ ] Descrição da tool diz quando usar **e quando não usar** (texto em `altare-engenharia-de-ia`)?
- [ ] Dado novo exposto tem nome claro, enum fechado e `comment`?
- [ ] Canal novo é só adaptador: sem regra de negócio, sem permissão própria?
- [ ] Nenhum dado pessoal desnecessário volta para o modelo (`altare-seguranca-privacidade`)?

## Bom / ruim
```python
# ruim: tool com SQL direto e escrita sem proposta
def tool_mark_paid(installment_id): db.execute("UPDATE installments SET status='Pago' ...")

# bom: leitura por consulta; escrita vira proposta com prévia
def tool_propose_pay_installment(ctx: AgentContext, installment_id: UUID, paid_cents: int):
    return ctx.propose_change("pay_installment",
        {"installment_id": installment_id, "paid_cents": paid_cents},
        idempotency_key=ctx.key("pay_installment", installment_id, paid_cents))
```
```json
{ "code": "ambiguous_vendor", "detail": "Encontrei 2 fornecedores parecidos com 'Buffet Ex'. Qual deles?",
  "candidates": [{"id": "…", "name": "Buffet Exemplo A"}, {"id": "…", "name": "Buffet Exemplo B"}] }
```

## Limites e vizinhas
- Como o agente raciocina, prompts, descrições de tool, evals, custo, latência e guardrails: `altare-engenharia-de-ia`.
- Colunas, migrations e views como SQL: `altare-banco-de-dados` (que aponta para esta skill em "o que muda por causa do agente").
- Onde o agente se encaixa nas camadas: `altare-arquitetura`. Erros e rotas: `altare-backend-api`.
- Autenticação, vínculo de número, dados enviados a terceiros: `altare-seguranca-privacidade`. Componente do chat flutuante: `altare-frontend`; texto das respostas: `altare-conteudo-copy`.

## Em aberto
- O módulo de chat é a 8ª área, "Assistente" (`D-050`). Detalhamento do Nível 5 e busca aproximada portátil: `OQ-IA-001`.
- Custo, conta do WhatsApp Business e hospedagem do webhook (exige app na nuvem): `OQ-IA-001`, `stack.md` §9 e §10.
- Provedor de LLM e orquestração: Bloco 5.1, ainda não decididos.
