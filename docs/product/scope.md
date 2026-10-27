# Escopo por Território (`scope.md`)

> **Status:** Aprovado na Fase 2 (Conceito) em 2026-10-24 (incluindo decisões `D-001` a `D-011`). **Em revisão por área** (`D-029`): o detalhamento por feature está em `docs/product/features/`, e ele prevalece sobre este documento onde houver diferença.

Este documento detalha cada território do produto em quatro dimensões: **o trabalho real do casal**, **o que entra na primeira versão (v1 — Agora)**, **o que entra depois (Backlog de Futuro: v1.1+)** e **o que fica explicitamente de fora**. Nenhuma funcionalidade mapeada para o futuro deve ser perdida.

---

## 1. Planejamento Inicial (Definição do Casamento)

- **Trabalho do casal:** Sair do marco zero definindo as diretrizes do casamento (época/ano-alvo, região/cidade-alvo, formato, porte estimado), comparar caminhos macro quando ainda há dúvida sobre o estilo/localidade e decidir, categoria por categoria, **o que o casamento terá** (essencial / desejável) e **o que ficará de fora** (descartado, com motivo registrado).
- **Entra na v1 (Agora):**
  - **Painel de Definições Base do Casamento:** variáveis estruturais que podem estar no estado *"Em definição"* (vinculadas às Possibilidades Macro) ou *"Definido"*: data/época, localidade, formato, teto de orçamento e faixa de convidados.
  - **Mapa de Escopo do Casamento:** lista de categorias/frentes possíveis de um casamento brasileiro (cerimônia civil, cerimônia religiosa/simbólica, espaço, gastronomia/buffet, bebidas/bar, foto, vídeo, música/DJ/banda, decoração/flores, iluminação/som, trajes, beleza/dia da noiva e noivo, papelaria/convites, lembrancinhas, doces/bolo, cerimonial do dia, noite de núpcias, lua de mel, etc.) onde o casal classifica cada item como:
    - `Entra (Essencial)` $\rightarrow$ ativa automaticamente a categoria no Orçamento e no Cronograma.
    - `Talvez (Se couber)` $\rightarrow$ entra como item opcional para simulação de impacto financeiro.
    - `Em discussão` $\rightarrow$ quando Noivo e Noiva ainda têm opiniões diferentes.
    - `Fica de fora` $\rightarrow$ fica arquivado com o motivo do descarte, sem poluir o planejamento ativo.
  - **Visão de Alinhamento do Casal:** cada perfil (`Noivo` e `Noiva`) pode marcar sua prioridade individual por categoria antes de baterem o martelo juntos.
  - **Revisado em `D-029`** (detalhamento em `docs/product/features/planejamento-e-caminhos.md`):
    - **Tipo de cerimônia** (religiosa, civil, simbólica ou mais de uma) como campo das Definições Base, nunca presumido (`D-026`).
    - **Estimativa inicial de valor** por categoria no Mapa de Escopo, lida depois pelo Orçamento (coluna *Estimado*).
    - **Nota livre** por categoria e por perfil.
    - **Referências por categoria** (links e imagens de inspiração), sem leitura automática de páginas.
    - Prioridade individual em três níveis (`Quero muito`, `Se couber`, `Dispenso`). Qualquer um dos dois pode mudar o status conjunto, com histórico de autoria.
- **Entra depois (v1.1+ — Futuro):**
  - **Entrevistas Guiadas por IA para Rascunho Inicial (`D-010`):** conversa estruturada conduzida por IA (individualmente com Noivo e Noiva ou em conjunto) sobre o perfil, gostos, referências, prioridades e limites do casal. Ao final, a IA gera uma **proposta completa de rascunho do casamento** (sugestão de formato/caminhos macro, classificação inicial de categorias que entram/ficam de fora e distribuição percentual sugerida do orçamento) para revisão e confirmação do casal.
- **Fica de fora:**
  - Testes/quizzes estáticos e genéricos de revista sem personalização.

---

## 2. Cronograma (Marcos, Prazos e Dependências até o Dia D)

- **Trabalho do casal:** Sem assessoria de preparação, saber exatamente **o que precisa ser decidido agora**, **o que depende de outra decisão anterior** e **quem (Noivo, Noiva ou Ambos)** está responsável por cada tarefa ou marco.
- **Entra na v1 (Agora):**
  - **Marcos (Milestones) e Tarefas/Decisões em Fases Lógicas:**
    - *Fase 1: Marco Zero & Definições Base* (escopo, lista preliminar, simulação de orçamento e escolha de caminho macro).
    - *Fase 2: Contrato Âncora* (data e espaço/local).
    - *Fase 3: Fornecedores Essenciais* (gastronomia, foto/vídeo, cerimonialista do dia, música/celebrante).
    - *Fase 4: Identidade, Complementares e Convidados* (decoração, trajes, convites, enxoval/lista de presentes).
    - *Fase 5: Reta Final & Hand-off* (confirmação de presença, degustações finais, quitação de contratos e entrega do Dossiê do Dia D ao cerimonialista).
  - **Dependências explícitas (Bloqueios):** indicação clara de quais decisões travam outras (ex.: *"Fechar Decoração"* depende de *"Fechar Espaço"*), separando visualmente o que está **Destravado (Pronto para agir)** do que está **Bloqueado**.
  - **Modo Sem Data vs. Modo Com Data:** funciona por sequência lógica enquanto a data exata do casamento ainda está em aberto e recalcula janelas/prazos automaticamente assim que a data oficial é definida.
  - **Atribuição de Responsável:** `Noivo`, `Noiva` ou `Ambos`.
  - **Revisado em `D-031`** (detalhamento em `docs/product/features/cronograma.md`): **catálogo inicial de 29 marcos** editável, ligado ao Mapa de Escopo; edição total de marcos, fases e dependências; **janelas sugeridas** relativas à data (editáveis); **tarefas avulsas**, **checklist**, **anexos e links** e **calendário mensal**.
- **Entra depois (v1.1+ — Futuro):**
  - Sincronização com agendas externas (Google Calendar / Apple Calendar).
  - **Notificações personalizadas por IA (`D-008`):** avisos inteligentes adaptados ao momento do cronograma e às pendências individuais do Noivo e da Noiva.
- **Fica de fora:**
  - Gráfico de Gantt corporativo complexo em horas/minutos de projeto.

---

## 3. Orçamento (Teto, Simulador de Múltiplos Orçamentos, Estimado, Contratado e Realizado)

- **Trabalho do casal:** Simular cenários financeiros completos desde o marco zero e controlar se o casamento cabe no bolso tanto no valor global quanto no fluxo de caixa mensal (sinal, parcelas e saldo final).
- **Entra na v1 (Agora):**
  - **Simulador de Múltiplos Orçamentos Completos em Paralelo (`D-009`):**
    - Capacidade de criar, clonar e comparar **orçamentos inteiros em paralelo** (ex.: *"Cenário A: Praia (120 convidados)"* vs. *"Cenário B: Campo (160 convidados)"* vs. *"Cenário C: Cidade Enxuto"*).
    - Cada orçamento simulado tem seu próprio teto global, número estimado de convidados, categorias ativas/opcionais e valores planejados/estimados.
    - Comparativo lado a lado entre os orçamentos simulados (total planejado, total estimado, custo por convidado, diferença para o teto) e botão para **definir/promover um cenário como o Orçamento Oficial Ativo** (sem perder os cenários alternativos caso queiram consultar ou reativar).
  - **Quatro colunas vivas por categoria e no consolidado geral:**
    1. **Planejado (Teto da Categoria):** meta definida para a categoria.
    2. **Estimado:** projeção baseada nas possibilidades em análise (ou estimativa manual enquanto não há cotação).
    3. **Contratado:** valor real fechado (preço base + adicionais/taxas da possibilidade escolhida).
    4. **Realizado (Pago):** soma das parcelas já pagas vs. saldo pendente a pagar.
  - **Cronograma de Pagamentos (Parcelas / Fluxo de Desembolso):** registro de cada pagamento de contrato fechado (data de vencimento, valor, meio de pagamento como PIX/boleto/cartão, status `Pendente`/`Pago`, comprovante e quem pagou: `Noivo`, `Noiva` ou `Conta Conjunta`).
  - **Revisado em `D-036`** (detalhamento em `docs/product/features/contratos-e-parcelas.md`): contrato **por decisão ou direto**; Contratado conta desde a criação do contrato; parcelas com **valor pago editável**, vencimento "no dia do evento", **assistente de plano de pagamento**, Fluxo de Pagamentos com exportação em Excel/CSV e indicador **"A pagar"**.
  - **Cálculo variável por convidado:** categorias com custo *per capita* (ex.: buffet, bar, convites/lembrancinhas) calculam automaticamente com base na contagem da lista de convidados (ou da premissa do cenário simulado).
  - **Revisado em `D-032`** (detalhamento em `docs/product/features/orcamento-e-simulador.md`): **base de convidados escolhida por cenário** com arredondamento para cima; **fator da criança pagante** por linha; linhas **derivadas do Mapa de Escopo**; Contratado e Realizado como fatos do casamento, exibidos só no cenário ativo; **reserva para imprevistos**, **indicador de uso do teto** e **exportação em Excel/CSV**.
- **Entra depois (v1.1+ — Futuro):**
  - Alertas proativos e notificações personalizadas de vencimento de parcelas e desvios de orçamento.
  - Projeção de fluxo de caixa mensal comparada à capacidade de poupança mensal do casal.
- **Fica de fora:**
  - Movimentação financeira ou pagamento bancário dentro do aplicativo (Open Banking / checkout).

---

## 4. Contatos (Pessoas e Fornecedores com Histórico e Próximo Passo)

- **Trabalho do casal:** Manter uma base limpa de todos os fornecedores e pessoas envolvidas (espaços, buffets, fotógrafos, cerimonialista do dia, indicações), sabendo em que pé está cada conversa, onde estão os PDFs enviados e qual é o próximo passo.
- **Entra na v1 (Agora):**
  - **Ficha do Contato/Fornecedor:** nome, categoria(s), telefone/WhatsApp (com link direto `wa.me`), Instagram/site, e-mail, cidade/região e quem indicou.
  - **Status do Relacionamento:** `Para contatar` $\rightarrow$ `Aguardando orçamento` $\rightarrow$ `Orçamento recebido` $\rightarrow$ `Em negociação / Visita` $\rightarrow$ `Contratado` / `Descartado`.
  - **Histórico de Interações:** timeline datada do que foi conversado ou combinado, com autoria (`Noivo` ou `Noiva`).
  - **Próximo Passo Único:** campo de destaque na ficha e na listagem com `Ação necessária`, `Data-alvo` e `Responsável (Noivo/Noiva/Ambos)`.
  - **Arquivos e Links Vinculados:** PDFs de propostas, minutas de contrato, fotos de visita e links de portfólio.
- **Entra depois (v1.1+ — Futuro):**
  - Captura rápida via encaminhamento de mensagem/contato do WhatsApp ou atalho mobile.
- **Fica de fora:**
  - Integração direta com a API do WhatsApp para ler conversas privadas automaticamente em tempo real.
  - **Revisado em `D-034`** (detalhamento em `docs/product/features/contatos.md`): dois tipos (**Fornecedor** e **Pessoa**); funil de 6 estados confirmado, com transição livre e motivo de descarte opcional; **visitas agendadas com data e hora** no calendário; **aviso de duplicidade**; **busca global do app**.

---

## 5. Possibilidades (Cenários Macro + Propostas de Fornecedores)

- **Trabalho do casal:** Tanto no marco zero (comparando **caminhos macro**, como *Casar na praia vs. no campo vs. na cidade*) quanto em cada categoria do casamento (comparando **propostas de fornecedores**, como *Espaço A vs. Espaço B*), levantar as opções disponíveis, equalizar propostas que vêm em formatos diferentes, dar notas/opiniões individuais (Noivo vs. Noiva) e registrar a decisão final com o motivo.
- **Entra na v1 (Agora):**
  - **Dois níveis de Possibilidades (`D-007`):**
    1. **Possibilidades Macro (Cenários/Formatos do Casamento):** comparação de caminhos iniciais (formato, região/cidade, porte, vínculo direto com um cenário do Simulador de Orçamentos, prós/contras logísticos para convidados e avaliação de cada perfil) antes mesmo de ter fornecedores específicos.
    2. **Possibilidades por Categoria (Propostas de Fornecedores):** vinculadas a uma Categoria/Decisão e a um Contato/Fornecedor (permitindo mais de um pacote do mesmo fornecedor).
  - **Normalizador de Custo Comparável:** soma **Preço Base da Proposta** + **Custos Extras/Ocultos Necessários** (ex.: gerador, ECAD, taxa de rolha, horas extras, deslocamento, mobiliário complementar) = **Custo Total Real Comparável**.
  - **Visão de Comparação Lado a Lado:** tabela comparativa mostrando preço base, custos extras, custo total comparável, condições de pagamento (à vista vs. parcelado), itens inclusos, itens não inclusos e PDFs originais.
  - **Avaliação Dupla (`Noivo` & `Noiva`):** nota/favorito e comentário individual de cada perfil em cada possibilidade, evidenciando convergências e divergências.
  - **Revisado em `D-033`** (detalhamento em `docs/product/features/possibilidades-e-decisoes.md`): custo do Caminho Macro **derivado do cenário vinculado**; **selo de consenso** derivado (nota só informa); decisão macro com **efeitos sugeridos e confirmados** (Definições Base, orçamento e cronograma); decisão **reversível**; referências no caminho.
  - **Revisado em `D-035`** (detalhamento em `docs/product/features/propostas-por-categoria.md`): preço base **por pessoa ou total**; **Custo Total Real Comparável** derivado (extras `Necessário`/`Opcional`, fixos ou por pessoa); pagamento em texto livre; quadro de 2 a 5 propostas **sem destacar a melhor**; **uma decisão por categoria**; Contratado derivado; o Estimado **não** é alimentado por propostas (só faixa de referência).
  - **Registro de Decisão:** ao bater o martelo, uma possibilidade vira `Escolhida / Contratada` (atualizando as Definições Base ou o Orçamento + Dossiê do Dia D) e as demais viram `Descartadas`, com registro obrigatório do **Motivo da escolha / Motivo do descarte**.
- **Entra depois (v1.1+ — Futuro):**
  - Preenchimento assistido por IA da tabela comparativa a partir da leitura de múltiplos PDFs/textos (com revisão humana).
- **Fica de fora:**
  - Leilão reverso ou envio automático de mensagens para fornecedores.

---

## 6. Convidados e Enxoval / Lista de Presentes

- **Trabalho do casal:** Manter a lista nominal de convidados desde o início (pois ela define o porte do casamento e o custo de buffet/espaço) e organizar a lista de presentes com dupla função (`D-006`): controlar o enxoval/itens da casa nova e servir de rascunho pronto para exportar/cadastrar num site externo ou formatar para enviar diretamente aos convidados.
- **Entra na v1 (Agora):**
  - **Lista Nominal de Convidados:**
    - Cadastro agrupado por **Núcleo/Família** (ex.: *"Família Tio João"*), lado (`Noivo`, `Noiva`, `Comum`), faixa (`Adulto`, `Criança pagante`, `Criança isenta`), grau de prioridade/probabilidade (`Essencial / Certeza`, `Provável`, `Lista de espera / Fase 2`) e status do convite (`Rascunho`, `Convidado`, `Confirmado`, `Não irá`).
    - **Painel de Contagem Automática:** exibe *Total Nominal*, *Estimado Ponderado* e *Confirmados*, alimentando diretamente os cálculos por pessoa no Orçamento.
  - **Revisado em `D-030`** (detalhamento em `docs/product/features/convidados-enxoval-e-dia-d.md`): estimado ponderado por **pesos editáveis** (vazios até o casal definir); restrição alimentar, contatos, **acompanhante (+1)** e idade da criança por convidado; endereço postal por núcleo; **convite enviado por núcleo** (data e canal); motivo opcional em `Não irá`; **exportação em Excel, com CSV como opção**. Importação de planilha segue em v1.1+.
  - **Gestão de Enxoval & Lista de Presentes com Exportação (`D-006`):**
    - Cadastro de itens da casa nova e cotas: cômodo/categoria (Cozinha, Quarto, Sala, Eletros, Cotas Lua de Mel, etc.), nome do item, prioridade, valor estimado, link/loja de referência, destino (`Para pedir na lista de presentes` vs. `Comprar nós mesmos`) e status (`Precisamos`, `Na lista de presentes`, `Já ganhamos`, `Já compramos`), além de campo para anotar **quem presenteou**.
    - **Exportação e Formatação:** exportar a seleção de presentes em planilha/CSV (para importar/cadastrar rapidamente em site externo de presentes) ou gerar visão/texto formatado para enviar diretamente aos convidados.
- **Entra depois (v1.1+ — Futuro):**
  - **Revisado em `D-037`** (detalhamento na parte Enxoval de `docs/product/features/convidados-enxoval-e-dia-d.md`): itens **por unidade e cotas em dinheiro**, com **quantidade e recebimentos** (status e totais derivados), enxoval **separado do Orçamento**, exportação em Excel/CSV e **lista formatada em texto** para os convidados.
  - Organização de mesas/grupos de assento para a recepção.
  - Importação em lote de listas antigas e apoio de IA para redigir mensagens personalizadas de agradecimento para quem deu presente.
- **Fica de fora:**
  - Site público dos noivos, página web de RSVP aberta na internet e checkout financeiro próprio para convidados.

---

## 7. Dossiê de Hand-off para o(a) Cerimonialista do Dia

- **Trabalho do casal:** Como não há assessoria durante o planejamento, entregar ao(à) cerimonialista do dia uma visão consolidada, sem precisar montar um documento do zero na véspera do casamento.
- **Entra na v1 (Agora):**
  - **Visão e Exportação "Dossiê do Dia D":** consolida automaticamente todos os fornecedores com status `Contratado`, contatos dos responsáveis no dia, resumo do escopo contratado, links para os contratos/PDFs, saldos a pagar no dia do evento, resumo quantitativo de convidados (adultos, crianças, restrições) e observações operacionais críticas registradas durante o planejamento.
- **Revisado em `D-038`** (detalhamento na parte Dossiê de `docs/product/features/convidados-enxoval-e-dia-d.md`): **Local do evento** e **horários-chave** (lista curta), **checklist de itens físicos**, **versões entregues** com "o que mudou", impressão pelo navegador e valor dos contratos desligado por padrão.
- **Entra depois (v1.1+ — Futuro):**
  - Roteiro minuto a minuto do Dia D (timeline de montagem, cerimônia e festa) e acesso de leitura/colaboração pontual para o(a) cerimonialista do dia.
- **Fica de fora:**
  - Plataforma multi-casamentos para agências de assessoria.

---

## 8. Apoio de IA (Arquitetura Pós-Fluxo Manual — v1.1+)

- **Governança de IA (`D-005` + `D-008`):** A v1 nasce **100% funcional no fluxo manual**. Quando a camada de IA entrar na v1.1, ela operará sob duas regras claras:
  1. **Nenhuma alteração de dados sem confirmação (Mutação Assistida):** Qualquer criação ou edição em escopo, orçamento, possibilidades, contratos ou contatos gerada por IA é apresentada primeiro como um **rascunho/diff revisável** que só é salvo após confirmação explícita do usuário.
  2. **Autonomia para Revisão Geral e Notificações (Somente-Leitura / Proativa):** A IA pode rodar proativamente (ou sob demanda) para **revisar o planejamento inteiro sem alterar dados** e **enviar notificações personalizadas** para o Noivo e para a Noiva.

### Catálogo Completo de Funcionalidades de IA (Mapeadas para v1.1+):
1. **Entrevista Guiada por IA para Rascunho Inicial do Casamento (`D-010`) *[Mutação com confirmação]*:**
   - Entrevista o casal sobre gostos, perfil, prioridades, sonhos e restrições, propondo ao final o rascunho de Escopo do Casamento, Cenários Macro e distribuição inicial do Orçamento para aprovação.
2. **Extrator de Proposta de PDF / Texto de WhatsApp *[Mutação com confirmação]*:**
   - Lê PDFs de orçamento ou mensagens longas coladas do WhatsApp e preenche um rascunho estruturado de `Possibilidade` (preço à vista/parcelado, itens inclusos, taxas extras/ocultas detectadas, validade).
3. **Equalizador de Comparação e Detector de Assimetrias *[Mutação com confirmação]*:**
   - Analisa todas as propostas de uma mesma categoria e destaca o que uma inclui e a outra cobra por fora (ex.: gerador, limpeza, rolha, horas extras), sugerindo ajustes no **Normalizador de Custo Comparável**.
4. **Revisor Geral do Planejamento (Auditoria Contínua Sem Alteração) (`D-008`) *[Somente-leitura / Proativa]*:**
   - Analisa o casamento de ponta a ponta em busca de inconsistências, riscos ou pontas soltas (ex.: *"O espaço escolhido comporta até 150 pessoas, mas a lista nominal atual soma 172 convidados (148 prováveis)"*; *"Vocês fecharam fotografia e vídeo, mas não há previsão de alimentação de staff no orçamento do buffet"*; *"As parcelas de novembro somam mais que a média mensal planejada"*).
5. **Notificações e Resumos Personalizados (`D-008` + `D-013`) *[Somente-leitura / Proativa]*:**
   - Envia resumos semanais ou alertas personalizados para o perfil do **Noivo** e da **Noiva** — via **Painel In-App, Notificações Push (celular/web) e WhatsApp** — com base nas responsabilidades de cada um, próximos passos vencendo com fornecedores, divergências de avaliação que precisam de conversa no fim de semana, parcelas próximas do vencimento e marcos recém-destravados no cronograma.

---

## 9. Resumo Consolidado: v1 (Agora) vs. Futuro (v1.1+)

| Território | Entra na v1 (Agora — Fluxo Manual Completo) | Fica Registrado para o Futuro (v1.1+) |
| :--- | :--- | :--- |
| **1. Planejamento Inicial** | Painel de Definições Base + Mapa de Escopo (Entra, Talvez, Em discussão, Fica de fora) com visão de alinhamento Noivo/Noiva. | **Entrevista guiada por IA (`D-010`)** para gerar rascunho inicial do casamento com base no perfil e gosto do casal. |
| **2. Cronograma** | Marcos e tarefas em 5 fases lógicas, dependências explícitas (destravado vs. bloqueado), modo sem/com data e responsável (`Noivo`/`Noiva`/`Ambos`). | Sincronização com Google/Apple Calendar + **notificações personalizadas por IA (`D-008`)**. |
| **3. Orçamento** | **Simulador de múltiplos orçamentos completos em paralelo (`D-009`)**, 4 colunas vivas (Planejado, Estimado, Contratado, Realizado), cronograma de parcelas e cálculo variável por convidado. | Projeção de poupança mensal vs. desembolso + alertas inteligentes de vencimento e desvio de orçamento. |
| **4. Contatos** | Ficha completa, funil de status, timeline de interações com autoria, arquivos/PDFs e **Próximo Passo Único**. | Captura rápida via encaminhamento do WhatsApp / atalho mobile. |
| **5. Possibilidades** | **Dois níveis (`D-007`)**: Cenários Macro + Propostas de Fornecedores; Normalizador de Custo Comparável; Comparação Lado a Lado; Avaliação Dupla Noivo/Noiva; Registro de Decisão com motivo. | **Extrator de PDF/WhatsApp por IA** + **Equalizador de assimetrias por IA** (sempre com confirmação). |
| **6. Convidados & Presentes** | Lista nominal por núcleo/família integrada ao orçamento + **Enxoval/Lista de Presentes de papel duplo (`D-006`)** (controle da casa nova + exportação/formatação para site externo ou convidados). | Mapa de mesas da recepção + importação em lote + rascunho de mensagens de agradecimento por IA. |
| **7. Hand-off Dia D** | **Dossiê do Dia D** consolidando contratos fechados, contatos do dia, itens contratados, saldos a pagar no dia e resumo de convidados. | Roteiro minuto a minuto do Dia D + acesso colaborativo pontual para o(a) cerimonialista. |
| **8. Camada de IA** | Arquitetura de dados preparada para receber a IA sem retrabalho. | **Revisor Geral do Planejamento (sem alteração de dados) (`D-008`)**, Notificações Personalizadas, Entrevista Inicial, Extração de Propostas e Equalização. |
