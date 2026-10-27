---
name: altare-analytics-metricas
description: >-
  Como medir o Altare sem rastreador de terceiros: North Star, funil, métricas derivadas do próprio
  banco. Use quando falarem de métricas, KPI, funil, retenção, tracking ou analytics, ou propuserem
  Google Analytics, Mixpanel, PostHog ou qualquer SDK de uso.
---

# Analytics e métricas

Com dois usuários, métrica não é pipeline: é uma pergunta que o casal quer responder, escrita como consulta sobre dados que já existem.

## Docs a consultar

- `docs/engineering/architecture.md` §5 (derivar, não duplicar), §6 (eventos de domínio), §10 (histórico básico e a auditoria completa que `D-022` rejeitou), §3 item 3 (consultas leem SQL direto e devolvem DTOs de leitura).
- `docs/product/features/centro-de-comando.md`: `F-CCD-03` (as 9 regras de "Atenção agora") e `F-CCD-06` (termômetro do orçamento).
- `docs/engineering/roadmap.md`: critério de conclusão de cada nível, que serve de funil.
- `docs/product/vision.md` §2 e §3, `docs/product/jobs.md`.
- `docs/product/decisions.md`: `D-002`, `D-013`, `D-022`, `D-038`.

## Princípios

1. **Nada de dado de uso sai do sistema.** Sem SDK de analytics, pixel, session replay ou envio a terceiros. Convidados são pessoas que não consentiram em ser medidas, e o ganho para duas pessoas é nulo. A política de dados é de `altare-seguranca-privacidade`.
2. **Métrica é consulta sobre fato persistido.** Mesma fonte da tela, sem tabela de métricas nem cópia de dados (`architecture.md` §5).
3. **Evento de domínio não é log de analytics.** Os eventos de `architecture.md` §6 são síncronos, em processo, sem persistência nem reprocessamento. Para série no tempo, use os carimbos das linhas: `created_at`, `updated_at`, `deleted_at`, a data da decisão e a "Data do pagamento" da parcela (`F-CTR-04`).
4. **Histórico que não existe é decisão de produto.** Se a métrica exige saber quando um status mudou e isso não está guardado, não crie rastreamento escondido: `D-022` rejeitou a trilha completa. Proponha ao usuário, com uma decisão `D-xxx` (via `altare-docs-vivas`).
5. **Poucas métricas, lidas pelos dois.** Uma consulta por pergunta, sob demanda. Só vira tela se o casal pedir.
6. **Medir o casamento, não as pessoas.** A autoria serve a rastreabilidade (`docs/product/personas.md` §2), não a ranquear quem fez mais.

## North Star (candidatas; a escolha final é do usuário)

| Candidata | Consulta | Vantagem | Limite |
| :--- | :--- | :--- | :--- |
| **A. Decisões registradas com motivo** | Contagem de decisões (macro e por categoria) por mês | Mede o valor central: não reabrir discussão (J8) | Cai a zero quando as decisões acabam |
| **B. Cobertura das categorias essenciais** | % das categorias com status `Entra` que têm decisão registrada ou contrato ativo | Mede progresso real do casamento e termina no Dossiê | Depende de o Mapa de Escopo estar preenchido |

Recomendação (não decisão): **B como North Star**, com **A como métrica de apoio**. B é limitada, converge ao Dossiê e não depende de frequência de uso.

## Funil do marco zero ao Dossiê

É um funil de **progresso do casamento**, não de conversão: ninguém "abandona", apenas ainda não chegou.

| Etapa | Bloco | Fato no banco |
| :--- | :--- | :--- |
| Definir | 1.1 | Definições Base em `Definido`; nenhuma categoria `Em discussão` |
| Dimensionar | 1.2 | Convidados cadastrados; Estimado Ponderado calculável |
| Ordenar | 1.3 | Marcos `Destravado` e `Concluído` |
| Escolher o caminho | 2.1 e 2.2 | Cenário `Oficial/Ativo` existente; decisão macro registrada |
| Cotar | 3.1 e 3.2 | Fornecedores com proposta; categorias com 2 ou mais propostas |
| Decidir | 3.2 | Decisão por categoria |
| Contratar e pagar | 3.3 | Contratos `Assinado`; parcelas `Pago` e `Pendente` |
| Entregar | 4.2 | Versão entregue do Dossiê (`F-DOS-07`) |

## Saúde

- **Reuse as 9 regras de "Atenção agora" (`F-CCD-03`)** como contagens: parcela atrasada, próximo passo atrasado, marco atrasado, avaliação faltando, `Conversar juntos` e as demais. Não crie uma segunda definição de "atrasado": uma só consulta serve à Home e à métrica.
- **Avaliação dupla completa:** % das possibilidades avaliadas pelos dois. Indica que o recurso central é usado.
- **Travamento:** dias entre o cadastro de uma proposta e a decisão da categoria (`created_at` contra a data da decisão).
- **Uso dos dois perfis:** registros criados e editados por semana por usuário (`created_by`, `updated_by`) e, se a tabela de sessões guardar histórico, logins por semana. Sirva-se disso para ver se **os dois** usam, nunca para compará-los.

## Anti-métricas (não medir, não otimizar)

- Tempo na tela, número de aberturas, sequências diárias, qualquer "engajamento". O produto é sereno, não viciante.
- Comparar Noivo contra Noiva.
- Qualquer métrica que exija mandar dado de convidado a terceiros.
- Conversão, aquisição e retenção em 30 dias: pertencem à hipótese de SaaS (`altare-gtm-pricing`, dormente).
- Notificação ativa para "puxar" o uso: `D-013` a deixou para v1.1+ e `D-038` manteve a Home sem alertas ativos.

## Como implementar

1. Formule a pergunta com o casal (`altare-produto`) antes de escrever qualquer consulta.
2. Escreva como consulta na camada `application/queries` do módulo dono do dado, devolvendo um DTO de leitura. Sem tabela nova para métricas.
3. Exponha sob demanda: relatório pontual ou, se o casal pedir, um cartão na Home. Nenhum comando de métricas existe hoje; qualquer um é proposta a confirmar.
4. Teste a consulta com dados fictícios rotulados (`altare-testes-qa`).
5. Se a métrica pedir uma coluna só para medir, pare e pergunte (`architecture.md` §10).

**Não construir:** data warehouse, ETL, fila de eventos, BI, teste A/B, coortes, significância estatística (n = 2).

## Bom / ruim

Ruim: adicionar um SDK de analytics "para entender como usamos". Envia dado de casal e de convidados a terceiros sem necessidade.

Bom: `SELECT` da cobertura de categorias `Entra` com contrato ativo, executado quando o casal pergunta "quanto falta?".

Ruim: gravar um evento `tela_aberta` em tabela própria. É vigilância sem pergunta.

Bom: reutilizar a consulta de parcelas atrasadas de `F-CCD-03` como indicador de saúde.

## Limites e vizinhas

- Decidir o que priorizar ou se o produto é bom: `altare-produto`. Esta skill mede, não decide.
- Política de dados pessoais, exportação e exclusão: `altare-seguranca-privacidade`.
- Custo, latência e qualidade do agente (`AgentRun`, evals): `altare-engenharia-de-ia`.
- Escrita da consulta em si (camadas, DTO de leitura): `altare-arquitetura`.
- Aquisição e conversão (hipótese SaaS): `altare-gtm-pricing`.

## Em aberto

- A **North Star** não foi escolhida. A decisão é do usuário e, quando tomada, vira `D-xxx`.
- Se a tabela de sessões (módulo `identity`) retém histórico, o que permite "logins por semana": a confirmar quando o módulo existir.
