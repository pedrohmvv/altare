# Experiência do Produto (`experience.md`)

> **Status:** Aprovado na **Fase 3 (Experiência)** em 2026-10-24 (incluindo decisões `D-012`, `D-013` e `D-014`).

Este documento traduz o conceito e o escopo aprovados na Fase 2 em:
1. **Jornada Ponta a Ponta do Casal**
2. **Objetos do Produto (Modelo de Domínio e Relações)**
3. **Arquitetura de Informação e Navegação (Desktop vs. Mobile)**
4. **Fluxos Principais Passo a Passo (Manual na v1 + Encaixes de IA na v1.1)**

---

## 1. Jornada Ponta a Ponta do Casal

A experiência do produto acompanha a evolução real do planejamento de um casamento sem assessoria de preparação. O sistema não joga todas as complexidades de uma vez: ele destaca o que importa em cada momento.

```
[Estágio 1: Marco Zero] ──► [Estágio 2: Caminhos & Orçamentos] ──► [Estágio 3: Cotações & Decisões] ──► [Estágio 4: Contratos, Lista & Enxoval] ──► [Estágio 5: Dossiê do Dia D]
  - Escopo (entra/fora)       - Possibilidades Macro                 - Contatos e Próximo Passo            - Parcelas e Fluxo de Caixa                  - Consolidação automática
  - Lista nominal inicial     - Simulador de Orçamentos              - Comparação e Custo Comparável       - Confirmação de Convidados                  - Entrega ao Cerimonialista
  - (v1.1: Entrevista IA)     - Destravamento do Cronograma          - Avaliação Noivo/Noiva + Decisão     - Controle e Exportação de Presentes         - (v1.1: Revisão Geral IA)
```

1. **Estágio 1 — Marco Zero (Alinhamento e Dimensionamento):**
   - O casal entra no sistema sem precisar ter data, cidade ou orçamento fechado.
   - Define o **Mapa de Escopo** (o que entra, o que talvez entre e o que fica de fora) e rascunha a **Lista Nominal Inicial de Convidados** por núcleos familiares para descobrir o tamanho real do casamento.
   - *(Na v1.1, o casal pode optar por iniciar esse estágio através da **Entrevista Guiada por IA**, que sugere o rascunho inicial com base no gosto e perfil dos dois).*
2. **Estágio 2 — Caminhos Macro e Simulação de Orçamentos em Paralelo:**
   - Antes de sair pedindo 30 orçamentos, o casal compara **Possibilidades Macro** (ex.: *Praia vs. Campo vs. Cidade*) conectadas ao **Simulador de Múltiplos Orçamentos em Paralelo**.
   - Ao escolherem o caminho macro e promoverem um cenário de orçamento como **Ativo**, as próximas fases do **Cronograma** são destravadas.
3. **Estágio 3 — Exploração, Cotação e Decisão por Categoria:**
   - Para cada categoria destravada (começando pelos contratos âncora, como Espaço e Buffet), o casal cadastra **Contatos/Fornecedores**, anota interações e controla o **Próximo Passo**.
   - As propostas recebidas viram **Possibilidades**, têm seus custos extras equalizados no **Normalizador de Custo Comparável**, recebem a avaliação individual do `Noivo` e da `Noiva` e são comparadas lado a lado no computador.
   - Ao baterem o martelo, registram a **Decisão** (com o motivo da escolha e do descarte das demais).
4. **Estágio 4 — Contratação, Gestão Financeira, Convidados e Enxoval:**
   - A possibilidade escolhida vira **Contrato Ativo**, alimentando a coluna `Contratado` do orçamento e gerando o **Cronograma de Pagamentos (Parcelas)**.
   - Em paralelo, o casal evolui o status da **Lista de Convidados** e organiza o **Enxoval / Lista de Presentes** (controlando o que precisa para a casa nova e exportando a seleção de presentes para site externo ou envio direto aos convidados).
5. **Estágio 5 — Reta Final e Hand-off para o(a) Cerimonialista do Dia:**
   - Tudo o que foi decidido e contratado ao longo dos meses já está consolidado automaticamente no **Dossiê do Dia D**, pronto para ser revisado com o(a) cerimonialista do dia.

---

## 2. Objetos do Produto e Suas Relações (Modelo Conceitual)

Para que o produto nunca pareça uma colcha de retalhos, todos os módulos operam sobre **10 objetos centrais** conectados entre si:

| Objeto | O que representa | Como se conecta aos demais |
| :--- | :--- | :--- |
| **1. Perfil (`Noivo` / `Noiva` / `Ambos`)** | Identidade de quem está usando ou de quem é a responsabilidade/opinião. | Assina avaliações em `Possibilidades`, assume `Próximos Passos`, `Tarefas` e `Parcelas`, e recebe notificações personalizadas (v1.1). |
| **2. Categoria de Escopo** | Uma frente do casamento (ex.: *Espaço*, *Gastronomia*, *Fotografia*, *Cerimonial do Dia*). | Tem status de escopo (`Entra`, `Talvez`, `Em discussão`, `Fica de fora`). Se `Entra` ou `Talvez`, aparece nos `Cenários de Orçamento`, no `Cronograma` e agrupa `Possibilidades`. |
| **3. Cenário de Orçamento** | Um plano financeiro completo do casamento (um marcado como `Oficial/Ativo` e N cenários em `Simulação Paralela`). | Contém um teto global, uma premissa de convidados (ou vínculo com a `Lista de Convidados`) e linhas de orçamento por `Categoria de Escopo` (*Planejado*, *Estimado*, *Contratado*, *Realizado*). |
| **4. Marco / Tarefa de Cronograma** | Uma decisão ou entrega no tempo, pertencente a uma Fase do planejamento. | Pode ter **dependências** (outros Marcos/Categorias que precisam estar resolvidos antes), um status (`Bloqueado`, `Destravado`, `Em andamento`, `Concluído`), prazo-alvo e responsável (`Noivo`/`Noiva`/`Ambos`). |
| **5. Contato / Fornecedor** | Uma empresa ou pessoa relevante para o casamento. | Vincula-se a uma ou mais `Categorias`, guarda dados de contato (WhatsApp, Instagram), arquivos, `Histórico de Interações`, um único `Próximo Passo` ativo e pode gerar uma ou mais `Possibilidades`. |
| **6. Possibilidade (Macro ou Proposta)** | Uma alternativa em análise — seja um **Caminho Macro** (ex.: *Casar no Campo*) ou uma **Proposta de Fornecedor** (ex.: *Buffet X - Cardápio Ouro*). | Possui Preço Base + **Itens Inclusos** + **Custos Adicionais/Ocultos** = **Custo Total Comparável**, anexos (PDFs), e **Avaliação Individual Dupla (`Noivo` e `Noiva`)** composta por: Classificação rápida (`Favorito`, `Gostei`, `Com ressalvas`, `Descartaria`) + Nota de `1 a 5` + Comentário livre (`D-012`). |
| **7. Decisão Registrada** | O ato de escolher uma `Possibilidade` e descartar as concorrentes. | Guarda a data, o **Motivo da Escolha** e o **Motivo do Descarte** das outras opções. Quando é uma proposta de fornecedor, promove o item para `Contratado` no Orçamento e no `Dossiê do Dia D`. |
| **8. Contrato & Parcela** | O compromisso financeiro e operacional resultante de uma `Possibilidade` escolhida. | Vincula o PDF do contrato assinado, observações críticas para o Dia D e a lista de **Parcelas** (vencimento, valor, meio de pagamento, status `Pendente`/`Pago`, comprovante). |
| **9. Convidado & Núcleo Familiar** | Pessoa real na lista do casamento, agrupada por família/núcleo. | Define faixa (`Adulto`, `Criança pagante`, `Criança isenta`), probabilidade (`Certeza`, `Provável`, `Fase 2`) e status (`Rascunho`, `Convidado`, `Confirmado`, `Não irá`). Alimenta automaticamente as categorias *per capita* do `Orçamento`. |
| **10. Item de Enxoval / Presente** | Item para a casa nova ou cota de presente. | Possui cômodo/categoria, prioridade, valor estimado, link, destino (`Pedir na lista` vs. `Comprar nós mesmos`), status (`Precisamos`, `Na lista`, `Já ganhamos`, `Já compramos`) e quem presenteou. Exportável para site externo/convidados. |

> **O Dossiê do Dia D** não é um cadastro separado que dá trabalho dobrado: ele é uma **visão viva consolidada** gerada automaticamente a partir dos objetos `Categoria de Escopo` + `Contato/Fornecedor` + `Decisão/Contrato` + `Parcelas pendentes no dia` + `Resumo de Convidados`.

---

## 3. Arquitetura de Informação e Navegação

A navegação foi desenhada para refletir a forma como vocês pensam o casamento, com adaptação clara entre **Computador (planejamento conjunto profundo)** e **Celular (consulta e captura rápida)**.

### 3.1. Estrutura de Navegação Principal (7 Áreas + Seletor Rápido de Perfil)

> **Revisado em `D-020`/`D-021` (2026-10-26):** cada pessoa tem **login individual** (`Noivo` ou `Noiva`) e a autoria sempre vem da sessão. O seletor passou a ser uma **lente de visão**, não uma troca de identidade.

No topo/lateral, um **Seletor de Lente** permite alternar com 1 clique entre:
- `Visão do Casal (Juntos)` *(padrão no computador quando estão sentados lado a lado)*
- `Minha visão` *(destaca pendências, avaliações e alertas de quem está logado, `Noivo` ou `Noiva`)*

Avaliações individuais são visíveis ao outro imediatamente. Para avaliar como o outro no computador compartilhado, a pessoa troca de usuário (login rápido por senha).

As **7 áreas principais** da aplicação são:

1. **Visão Geral (Centro de Comando):**
   - Resumo do momento atual: definições base do casamento, decisões destravadas da vez, próximos passos com fornecedores vencendo na semana, termômetro do orçamento ativo (Planejado vs. Estimado vs. Contratado vs. Pago), contagem atual de convidados e próximas parcelas a vencer.
   - *(Na v1.1: exibe também o painel de insights/alertas do **Revisor Geral de IA**).*
2. **Planejamento & Caminhos (Marco Zero e Escopo):**
   - **Aba 1 — Definições Base & Caminhos Macro:** comparação lado a lado dos macro-cenários do casamento (ex.: Praia vs. Campo vs. Cidade) e status das definições fundamentais.
   - **Aba 2 — Mapa de Escopo do Casamento:** quadro completo do que `Entra`, `Talvez`, `Em discussão` e `Fica de fora`, mostrando onde Noivo e Noiva já concordam ou divergem.
3. **Cronograma & Dependências:**
   - Visão por **Fases Lógicas** mostrando o que está **Destravado agora** vs. **Bloqueado por outra decisão**, com filtro por responsável (`Noivo`, `Noiva`, `Ambos`).
4. **Possibilidades & Decisões (Por Categoria):**
   - Navegação por categoria ativa do casamento (Espaço, Buffet, Foto, etc.).
   - Dentro de cada categoria: quadro comparativo lado a lado das propostas, **Normalizador de Custo Comparável**, notas individuais do Noivo e da Noiva, PDFs anexados e registro da **Decisão Final**.
   - **Aba "Contratos" (`D-036`):** lista de todos os contratos (por decisão ou diretos), com progresso de pagamento e acesso às parcelas.
5. **Orçamento & Simulador:**
   - **Aba 1 — Orçamento Oficial Ativo:** tabela viva com as 4 colunas (*Planejado*, *Estimado*, *Contratado*, *Realizado/Pago*) por categoria.
   - **Aba 2 — Simulador de Orçamentos em Paralelo (`D-009`):** comparação lado a lado entre múltiplos cenários completos de orçamento, permitindo editar premissas (nº de convidados, teto, itens inclusos) e promover um cenário a oficial.
   - **Aba 3 — Fluxo de Pagamentos (Parcelas):** calendário/lista mensal de desembolsos (sinais, parcelas abertas e quitadas).
6. **Contatos & Fornecedores:**
   - Lista e quadro por status (`Para contatar` $\rightarrow$ `Contratado`), com foco imediato no **Próximo Passo**, link direto para abrir o WhatsApp, histórico de interações e todos os PDFs/arquivos daquele fornecedor.
7. **Convidados, Enxoval & Dia D:**
   - **Subárea Convidados:** lista nominal agrupada por núcleo familiar e indicadores de contagem (*Total*, *Ponderado*, *Confirmados*).
   - **Subárea Enxoval & Lista de Presentes:** controle dos itens da casa nova + módulo de exportação/formatação para site externo ou envio aos convidados.
   - **Subárea Dossiê do Dia D:** documento vivo estruturado para o(a) cerimonialista do dia, com modo de visualização limpa / exportação (PDF/impressão).

### 3.2. Comportamento Desktop vs. Mobile (`D-003`)

| Contexto | Foco no Computador (Tela Grande — Planejar Juntos) | Foco no Celular (Tela Vertical — Consulta e Ação Rápida) |
| :--- | :--- | :--- |
| **Entrada / Home** | Dashboard amplo com visão combinada de orçamento, dependências destravadas e comparativos em aberto. | Cartões diretos: *"Meus próximos passos"*, *"Próximos pagamentos"*, *"Busca rápida de fornecedor/PDF"* e botão flutuante **"+ Registrar Rápido"**. |
| **Comparação de Possibilidades** | **Tabela Lado a Lado multi-colunas** (3 a 5 propostas abertas simultaneamente com preço base, ajustes de custo comparável, notas do Noivo e da Noiva e visualizador lateral de PDF). | **Cartões empilhados / Abas deslizantes** focados no Custo Total Comparável, resumo do que inclui, PDF em 1 toque e botão rápido para deixar a nota/comentário individual. |
| **Simulador de Orçamentos** | Edição e comparação multi-cenários lado a lado (*Cenário A vs. Cenário B vs. Cenário C*). | Leitura rápida do resumo de cada cenário e consulta de quanto resta de saldo por categoria. |
| **Contatos / Fornecedores** | Tabela/Kanban completo com filtros e painel lateral de detalhes. | Lista enxuta com botão de 1 toque para abrir conversa no WhatsApp, ler último combinado, subir um PDF recém-recebido e atualizar o *Próximo Passo*. |

---

## 4. Fluxos Principais Passo a Passo

### Fluxo 1 — Largada no Marco Zero (Definir Escopo e Caminhos Macro)
1. **Abertura:** O casal acessa **Planejamento & Caminhos**. As variáveis base (*Data/Época*, *Cidade/Região*, *Formato*, *Porte*, *Teto*) começam como `Em definição`.
2. **Mapa de Escopo:** O casal percorre a lista de categorias sugeridas para um casamento no Brasil.
   - O Noivo e a Noiva marcam cada categoria como `Entra (Essencial)`, `Talvez (Se couber)` ou `Fica de fora` (anotando o motivo quando descartam algo, ex.: *"Sem assessoria completa de preparação — faremos pelo nosso sistema e contrataremos apenas cerimonialista do dia"*).
3. **Comparação de Caminhos Macro (`D-007`):** Se estão em dúvida entre formatos (ex.: *Campo no interior* vs. *Restaurante na capital*), criam 2 ou 3 **Possibilidades Macro**, anotam prós, contras, logística para convidados, dão suas avaliações individuais e vinculam cada uma a um cenário no **Simulador de Orçamentos**.
4. **Encaixe futuro da IA (v1.1 — `D-010`):** Um botão *"Iniciar com Entrevista Guiada por IA"* permite que o casal responda perguntas sobre gostos, referências e prioridades; ao final, a IA exibe uma prévia preenchida do Mapa de Escopo e dos Caminhos Macro para o casal revisar, ajustar e confirmar.

---

### Fluxo 2 — Simular Múltiplos Orçamentos Completos em Paralelo (`D-009`)
1. **Criação de Cenários:** Na área **Orçamento & Simulador**, o casal cria o `Cenário 1` (ou clona um cenário existente para criar o `Cenário 2` e o `Cenário 3`).
2. **Ajuste de Premissas por Cenário:** Em cada cenário, definem:
   - Teto global desejado.
   - Número de convidados considerado no cálculo (ex.: usar os *120 convidados essenciais* da lista nominal no Cenário A vs. os *170 totais* no Cenário B).
   - Quais categorias `Talvez` entram ou saem naquele cenário e qual o teto planejado de cada categoria.
3. **Comparação Lado a Lado:** O sistema mostra os cenários lado a lado com o **Total Planejado**, **Total Estimado**, **Custo por Convidado** e **Folga/Estouro em relação ao Teto**.
4. **Definição do Orçamento Ativo:** O casal marca um dos cenários como `Orçamento Oficial Ativo` (podendo manter os demais salvos para consulta ou troca futura).

---

### Fluxo 3 — Da Cotação no WhatsApp até a Decisão Comparada (Coração do Produto)
1. **Captura do Fornecedor e Próximo Passo:** O casal encontra um fornecedor (ex.: *Espaço Serra Verde*), cadastra em **Contatos**, clica para chamar no WhatsApp e define o Próximo Passo: *"Cobrar PDF de orçamento até sexta — Responsável: Noivo"*.
2. **Cadastro da Possibilidade (Proposta):** Quando o PDF chega:
   - **Na v1 (Manual):** O usuário anexa o PDF, informa o Preço Base (ex.: R$ 25.000), condições de pagamento e lista o que está incluso.
   - *(Na v1.1 — Com IA: o usuário sobe o PDF ou cola a mensagem do WhatsApp; a IA extrai o rascunho completo e destaca taxas ocultas para o usuário revisar e clicar em **"Confirmar e Salvar"**).*
3. **Normalização de Custo Comparável:** Na proposta do *Espaço Serra Verde*, o casal adiciona no **Normalizador de Custo** os itens que o espaço exige contratar por fora (ex.: `+ R$ 4.500 Gerador obrigatório`, `+ R$ 3.000 Mobiliário básico`). O sistema calcula e destaca: **Preço de Capa: R$ 25.000 $\rightarrow$ Custo Real Comparável: R$ 32.500**.
4. **Avaliação Individual (`Noivo` e `Noiva` — `D-012`):** Cada um entra com seu perfil e registra:
   - **Classificação rápida:** `Favorito`, `Gostei`, `Com ressalvas` ou `Descartaria`;
   - **Nota de 1 a 5**;
   - **Comentário individual** com suas percepções.
   O sistema calcula o indicador de alinhamento do casal (ex.: *Consenso Favorito*, *Divergência para conversar*, *Ambos descartariam*).
5. **Comparação e Decisão Registrada:** Sentados juntos no computador, abrem a **Visão Lado a Lado** da categoria *Espaço*, comparam o Custo Real Comparável, o impacto no Orçamento Ativo e as notas dos dois.
6. **Bater o Martelo:** Clicam em **"Registrar Decisão"**, escolhem a opção vencedora e escrevem o **Motivo da Escolha** e o **Motivo do Descarte** das concorrentes.
7. **Efeito em Cadeia Automático:**
   - A categoria *Espaço* no Orçamento atualiza a coluna `Contratado`.
   - O marco *"Fechar Espaço"* no Cronograma é concluído, **destravando automaticamente** os marcos dependentes (ex.: *Decoração*, *Iluminação*).
   - O fornecedor vai automaticamente para o **Dossiê do Dia D**.

---

### Fluxo 4 — Gestão de Contrato e Fluxo de Pagamentos (Parcelas)
1. Ao marcar uma possibilidade como `Contratada`, o sistema abre o registro do **Contrato**: anexo do PDF assinado, dados do responsável para o Dia D e combinados críticos (ex.: *"Horário limite de som: 02h00; inclui 10 refeições de staff"*).
2. O casal lança o plano de pagamento acordado (ex.: *Sinal de 30% no PIX + 6 parcelas no boleto + 20% 15 dias antes do evento*).
3. À medida que pagam cada parcela, marcam como `Pago` (anexando o comprovante se quiserem), e a coluna `Realizado (Pago)` do orçamento avança automaticamente.

---

### Fluxo 5 — Lista Nominal de Convidados Conectada ao Orçamento
1. O casal cadastra os convidados agrupados por **Núcleo Familiar** (ex.: *Família Silva — 4 pessoas: 2 adultos, 1 criança pagante, 1 criança isenta*), indicando lado (`Noivo`, `Noiva`, `Comum`) e prioridade (`Certeza/Essencial`, `Provável`, `Fase 2`).
2. O topo da tela mostra três números em tempo real:
   - **Total Lista Completa** (todos os cadastrados).
   - **Contagem Base para Orçamento** (ex.: *Certeza + Prováveis*, descontando crianças isentas).
   - **Confirmados (RSVP interno)**.
3. Qualquer alteração nessa contagem reflete imediatamente nas categorias do Orçamento e nas Propostas configuradas com cálculo *por convidado* (ex.: Buffet, Bebidas).

---

### Fluxo 6 — Enxoval da Casa Nova e Exportação da Lista de Presentes (`D-006`)
1. Na área **Enxoval & Lista de Presentes**, o casal cadastra tudo o que deseja para a casa nova (por cômodo/categoria) ou cotas (ex.: passeios de lua de mel), definindo prioridade, valor estimado e link de referência.
2. Para cada item, definem se o destino é `Pedir na lista de presentes` ou `Comprar nós mesmos`.
3. Quando chega a hora de disponibilizar a lista para os convidados:
   - Clicam em **"Exportar para Site Externo (CSV/Planilha)"** para subir rapidamente em qualquer plataforma externa de casamento; ou
   - Clicam em **"Gerar Lista Formatada para Convidados"** para copiar/baixar uma versão limpa e organizada para enviar diretamente.
4. Conforme ganham ou compram os itens, atualizam o status para `Já ganhamos` (anotando quem deu o presente) ou `Já compramos`.

---

### Fluxo 7 — Passagem de Bastão: Dossiê do Dia D para o(a) Cerimonialista
1. Semanas antes do casamento, o casal abre a área **Dossiê do Dia D**.
2. Sem precisar digitar tudo de novo, o dossiê já exibe de forma limpa e estruturada:
   - Quadro resumo do evento (data, horários, local, contagem final de convidados adultos/crianças).
   - Ficha de cada fornecedor contratado (empresa, nome do responsável no dia, WhatsApp direto, itens exatos contratados, observações operacionais e link para o contrato em PDF).
   - Quadro de **Pagamentos Pendentes para a Semana / Dia do Evento** (quem ainda precisa receber saldo final e quanto).
   - Checklist de itens físicos que o casal levará para o local (ex.: alianças, bebidas compradas à parte, itens de papelaria/lembrancinhas).
3. O casal pode usar essa tela diretamente na reunião com o(a) cerimonialista do dia e exportar em PDF/documento organizado.

---

### Fluxo 8 — Revisão Geral e Notificações Personalizadas por IA (v1.1 — `D-008`)
1. **Revisão Geral (Sem Alteração de Dados):** Em segundo plano (ou ao clicar em *"Revisar Nosso Planejamento com IA"*), a IA analisa todos os objetos do casamento e gera um relatório de diagnóstico sem tocar em nenhum registro:
   - **Coerência de Capacidade:** compara a contagem da lista de convidados com a capacidade máxima das possibilidades de espaço/buffet.
   - **Cobertura de Escopo e Contratos:** avisa se alguma categoria marcada como `Entra (Essencial)` está sem teto de orçamento, sem cotações próximas do prazo ou se contratos fechados têm lacunas operacionais para o Dia D.
   - **Saúde Financeira:** aponta categorias onde a melhor possibilidade em análise supera o teto planejado e mostra onde há folga em outras categorias para compensar.
2. **Notificações Personalizadas (`D-008` + `D-013`):** O `Noivo` e a `Noiva` recebem avisos direcionados ao seu perfil através de **três canais (Painel In-App, Notificações Push no celular/navegador e WhatsApp)** — por exemplo: *"Você tem 2 follow-ups com espaços vencendo hoje"*, *"Sua noiva já avaliou as 3 opções de Fotografia — falta a sua nota para vocês compararem juntos no fim de semana"* ou *"Parcela do Espaço vence em 3 dias"*.
