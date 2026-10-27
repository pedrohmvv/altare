---
name: altare-produto
description: >-
  Critérios para decidir o que construir, adiar ou cortar no Altare: valor percebido, uso recorrente
  do casal, priorização na pirâmide de blocos. Use quando surgir ideia de feature, pedido de
  priorização, dúvida de escopo (v1, depois, fora), 'isso está bom?', ou antes de começar um bloco
  novo.
---

# Produto: o Altare é bom?

O Altare é um app pessoal de duas pessoas. "Bom" aqui quer dizer: o casal deixa a planilha, a pasta e o grupo de WhatsApp para decidir o casamento num só lugar, e continua voltando por vontade própria.

## Docs a consultar

- `docs/product/vision.md` §1 (problema), §3 (proposta de valor), §4 (diferenciação), §5 (não-objetivos).
- `docs/product/jobs.md` (J1 a J11, na ordem da jornada) e `docs/product/personas.md`.
- `docs/product/scope.md`: cada território tem "entra na v1", "depois" e "fica de fora"; §9 resume.
- `docs/engineering/roadmap.md`: a pirâmide e o critério de conclusão de cada nível (`D-018`).
- `docs/product/decisions.md`: `D-002` (uso pessoal), `D-005` (manual antes de IA), `D-008`, `D-026` (não confessional), `D-029` (como o escopo é revisado).
- `docs/product/features/*.md`: a seção final de cada área (ver "Validar com os dois").
- `AGENTS.md` §2 regra 4 e §3 (o que o agente decide e o que pergunta).

## Princípios

1. **Uso real vence escalabilidade (`D-002`).** Nenhuma decisão da v1 sacrifica a simplicidade do uso do casal por causa de uma hipótese de SaaS. Quem propõe o contrário carrega o ônus da prova.
2. **O teste de valor é a substituição.** Um nível só está pronto quando substitui o que prometeu substituir. Exemplo do roadmap: o Nível 3 só fecha quando vocês abandonam as planilhas de cotação e as pastas soltas de PDF.
3. **Fluxo manual completo antes de IA (`D-005`).** Se uma ideia só funciona com LLM, ela é do Nível 5, não da v1.
4. **Sucesso é decisão tomada, não tempo de tela.** O produto é calmo por identidade (`docs/design/identity.md` §1). Não otimize para engajamento.
5. **Nunca invente dados do casamento** (data, cidade, orçamento, convidados, estilo). São variáveis em aberto que o produto ajuda a definir (`AGENTS.md` §2).
6. **Fronteira é decisão do usuário.** O agente propõe, o usuário muda o que entra na v1 (`AGENTS.md` §3).

## Os quatro critérios

| Critério | Pergunta | Sinal bom | Sinal ruim |
| :--- | :--- | :--- | :--- |
| **Valor percebido** | Isso tira algo da planilha, da pasta ou do WhatsApp (`vision.md` §4)? | O casal para de abrir o arquivo antigo; uma decisão deixa de ser rediscutida (J8) | Precisam manter a planilha em paralelo "por garantia" |
| **Facilidade de aprender e usar** | Dá para fazer sem explicação na primeira sessão? | Capturar um fornecedor leva poucos toques (J6, `F-CTT-01`); o celular serve para consulta | Precisam de tutorial; o celular só "mostra" e o desktop faz tudo |
| **Uso recorrente** | Voltam sem obrigação? | Usam a Home e atualizam Próximos Passos na rotina de `vision.md` §2 | Só abrem quando um dos dois cobra |
| **Viabilidade comercial** | Seria vendável a outros casais? | **Só hipótese futura.** Não entra em nenhuma decisão da v1 | Usar como argumento para adicionar complexidade |

## Como priorizar

Ordem de desempate, do mais forte para o mais fraco:

1. **Dependência técnica:** a pirâmide manda. Um bloco só começa com o inferior utilizável (`roadmap.md`).
2. **Dependência de uso real:** o que o casal precisa no momento da jornada em que está (`jobs.md`, Momentos 1 a 5).
3. **Custo de não ter:** PDF perdido, decisão reaberta, parcela esquecida pesam mais que conforto.
4. **Esforço:** entre itens equivalentes, o menor primeiro.

Perguntas de corte para qualquer ideia nova:

- Serve a qual job (J1 a J11)? Sem job, é desejo, não necessidade.
- Cabe num território de `scope.md`? Está em `docs/product/features/`? Se não, pare e pergunte.
- Dá para **derivar** em vez de cadastrar (`docs/engineering/architecture.md` §5)? Cadastro duplicado envelhece.
- Reaproveita um formulário ou componente que já existe?

## Dizer não (e quando perguntar)

- **Fora por definição:** site público e RSVP, marketplace de fornecedores, mensageiro automático, IA que altera dado sem confirmação, planta baixa ou mapa 3D (`vision.md` §5), e todos os blocos "Fica de fora" de `scope.md`.
- **Como recusar:** cite a fronteira, mostre o que já existe para o caso, e ofereça registrar a ideia em `scope.md` como v1.1+ ou em `docs/product/open-questions.md`. Não implemente "só um pouquinho".
- **Pedidos que parecem pequenos e atravessam a fronteira:** "mandar a mensagem ao fornecedor pelo app" contraria `vision.md` §5.3. O WhatsApp de `D-042` é só entre o casal e o Altare.
- **Mudar fronteira, módulo ou o que entra na v1:** pergunte, com uma proposta explícita e reversível, no formato de lote curto (`AGENTS.md` §2 regra 3).

## Validar com os dois (não com o mercado)

Os docs de feature terminam com uma seção de pontos a validar, cada um reversível e com gatilho. O título varia: `Pontos a validar em uso`, `Pontos a validar no bloco` ou `Pontos de atenção`. Procure com `grep -n "^## Pontos" docs/product/features/*.md` e use esses pontos como roteiro. Não os copie para outro lugar.

Sessão curta (20 a 30 minutos, os dois juntos):

1. Escolha de 1 a 3 pontos do doc da área que acabou de ser construída.
2. Peça uma tarefa real, sem explicar: "registrem o fornecedor que acabaram de cotar". Observe onde hesitam. Não conduza.
3. Pergunte o que fariam hoje sem o Altare. Se a resposta ainda é planilha ou WhatsApp, o valor não foi percebido.
4. Anote: o que fizeram, onde travaram, o que mudariam, e se a mudança é reversível.
5. Destino do aprendizado:
   - ajuste reversível (rótulo, limite, padrão): edite o doc da área e diga o que mudou;
   - mudança de regra ou de escopo: nova decisão `D-xxx`, via `altare-docs-vivas`;
   - dúvida sem resposta: `docs/product/open-questions.md`.

## Checklist antes de construir

- [ ] Qual job (J1 a J11) e qual bloco do roadmap?
- [ ] Está em `scope.md` como v1 e detalhado em `docs/product/features/`? Se não, perguntar antes.
- [ ] O fluxo funciona sem IA?
- [ ] O que concreto ele substitui?
- [ ] Algum dado do casamento foi inventado nos exemplos ou nos valores padrão?
- [ ] Reaproveita o que existe ou deriva em vez de cadastrar?
- [ ] O critério de aceite é verificável (vira teste em `altare-testes-qa`)?

## Bom / ruim

Ruim: "Vamos adicionar login social e convite para outros casais para ganhar usuários." Viola `D-002` e adianta uma hipótese que ninguém pediu.

Bom: "Decisão da categoria Espaço Exemplo com motivo do descarte das outras: evita reabrir a discussão meses depois (J8)." Liga a feature a um job real.

Ruim: tratar "retenção em 30 dias" como meta. Com dois usuários, o número não diz nada.

Bom: "Os dois atualizaram seus Próximos Passos esta semana e a lista de Atenção agora diminuiu." É o hábito que o produto quer provocar.

## Limites e vizinhas

- Medir se funcionou (North Star, funil, saúde): `altare-analytics-metricas`.
- Preço, posicionamento e aquisição (hipótese SaaS, dormente): `altare-gtm-pricing`.
- Desenhar o fluxo, o onboarding e os estados de tela: `altare-ui-ux`.
- Escrever o texto que o casal lê: `altare-conteudo-copy`.
- Registrar decisão, spec de feature ou pergunta em aberto: `altare-docs-vivas`.

Esta skill decide **se vale** e **em que ordem**. Ela não desenha, não mede e não registra.
