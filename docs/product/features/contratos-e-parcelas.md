# Features: Contratos & Parcelas (`features/contratos-e-parcelas.md`)

> **Status:** **Aprovado pelo usuário em 2026-10-27** (`D-036`). Cobre o **Bloco 3.3**: contrato (por decisão ou direto), dados do Dia D, plano e parcelas de pagamento, Fluxo de Pagamentos, o **Realizado (Pago)** e o **Contratado** do Orçamento Ativo, e a exportação do fluxo.
>
> **Onde aparece na tela:** a lista de **Contratos** é uma segunda aba da área **Possibilidades & Decisões** (`experience.md` §3.1, item 4); o contrato também abre a partir da categoria decidida e da ficha do fornecedor. O **Fluxo de Pagamentos** é a **aba 3** de **Orçamento & Simulador** (`experience.md` §3.1, item 5).
>
> **Fontes:** `docs/product/scope.md` §3, `docs/design/experience.md` (objeto 8, Fluxo 4), `docs/engineering/architecture.md` §5 (derivar, não duplicar), `propostas-por-categoria.md` (`D-035`), `orcamento-e-simulador.md` (`D-032`), `contatos.md` (`D-034`), `D-030`, `D-036`.
>
> **Convenções:** `F-CTR-xx` identifica a feature. "Autor" é o usuário da sessão. Valores em centavos, aceitando `R$ 28.000,00` na edição. Cálculos só no backend. **Todo número do exemplo é fictício.** Estados e valores derivados nunca são digitados. O Altare não movimenta dinheiro: só registra o que o casal combinou e pagou.

---

## Visão da Área

**Jobs atendidos:** J9 (saber quanto já comprometemos, quanto pagamos e quanto falta desembolsar a cada mês) e a base do hand-off do Dia D.

| Objeto | O que é | Persistido? |
| :--- | :--- | :--- |
| **Contrato** | O compromisso fechado com um fornecedor, numa categoria | Sim (fato) |
| **Parcela** | Um pagamento previsto ou realizado de um contrato | Sim (fato) |
| **Contratado** (por categoria) | Soma dos valores dos contratos ativos da categoria | **Derivado** |
| **Realizado (Pago)** (por categoria) | Soma dos valores efetivamente pagos nas parcelas `Pago` | **Derivado** |
| **A pagar** (por categoria) | Contratado menos Realizado | **Derivado** |

---

## F-CTR-01 — Contrato

**Origem (dois caminhos)**

| Origem | Como nasce |
| :--- | :--- |
| **Por decisão** | Criado **automaticamente** ao registrar a decisão da categoria (`F-PRP-08`), com o estado `Aguardando assinatura`. Traz fornecedor, categoria e proposta de origem |
| **Direto** (`D-036`) | Criado pelo casal, sem proposta nem decisão, na aba **Contratos**. Serve para o que não passa por cotação (alianças, roupas, compras em loja) |

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Título** | Texto, obrigatório | Por decisão: "Fornecedor — Pacote", editável. Direto: livre. Ex.: "Contrato Exemplo — Espaço" |
| **Categoria** | Categoria do catálogo (`F-PLN-02`), obrigatória | Fixa quando por decisão. Direta: não pode estar `Fica de fora` |
| **Fornecedor** | Contato do tipo Fornecedor | **Obrigatório** por decisão. **Opcional** no direto |
| **Favorecido** | Texto curto | Só no direto **sem** fornecedor. Quem recebe o pagamento. Obrigatório nesse caso |
| **Proposta de origem** | Leitura | Só por decisão. Link para a proposta |
| **Valor fechado** | Dinheiro, centavos | Obrigatório para contar. Por decisão: **copiado uma vez** do Custo Total Real Comparável no momento da decisão, **editável**. Sem total comparável (falta base de convidados), nasce **vazio** e mostra "defina o valor" |
| **Estado** | `Aguardando assinatura` · `Assinado` · `Cancelado` | Padrão `Aguardando assinatura` |
| **Data da assinatura** | Data | Obrigatória ao marcar `Assinado`. Padrão hoje. Não pode ser futura |
| **Observações** | Texto | Livre |
| **Arquivos e links** | PDF e imagens | F-CTR-02 |
| **Dados do Dia D** | Responsável, itens contratados e combinados | F-CTR-03 |

**Regras**
1. **Valor fechado é fato, não derivado.** Depois de criado, **não acompanha** a proposta nem a base de convidados. Por decisão, a tela mostra "difere do comparável em R$ X" quando o valor editado for diferente do total da proposta (só informativo).
2. **Contratado conta desde a criação** (`D-036`): contratos `Aguardando assinatura` e `Assinado` somam. `Cancelado` não soma.
3. **Cancelar:**
   - **Por decisão:** cancelar o contrato é **reabrir a decisão da categoria** (`F-PRP-08`): uma única ação, explicada na confirmação.
   - **Direto:** cancela só o contrato.
   - Em ambos os casos, as parcelas `Pendente` ficam **canceladas** (guardadas, fora dos totais).
4. **Contrato com parcela `Pago` não pode ser cancelado nem excluído.** A tela orienta: desfazer o pagamento, ou ajustar o valor do contrato ao que foi efetivamente devido. Reembolsos e multas ficam fora da v1.
5. **Excluir** é lógico e recuperável. Só vale para contrato direto e sem parcelas `Pago`. Contrato por decisão se encerra reabrindo a decisão.
6. Mudar o valor fechado atualiza o Contratado na hora e o saldo "a programar" (F-CTR-04). A alteração fica no histórico básico, com autor e data. **Não há registro de aditivos** na v1 (`D-036`).
7. **Efeitos de um contrato direto com fornecedor:** o fornecedor passa a `Contratado` (derivado, `F-CTT-03`) e a categoria é acrescentada à ficha dele. O marco "Fechar …" da categoria é concluído, como na decisão (`F-CRN-03`, regra 6).
8. **Categoria com contrato ativo** não pode ir para `Fica de fora` nem `Em discussão` (`F-PLN-07`, regra 3).
9. Qualquer um dos dois cria e edita.

**Critérios de aceite**
- Registrar a decisão de uma categoria cria o contrato `Aguardando assinatura`, com o valor copiado da proposta (R$ 2.550,00 no exemplo de `F-PRP-03`), e o Contratado da categoria passa a R$ 2.550,00.
- Editar o valor para R$ 2.700,00 mostra "difere do comparável em R$ 150,00" e atualiza o Contratado.
- Uma decisão com total comparável sem valor cria o contrato vazio com "defina o valor", e o Contratado fica "—".
- Marcar `Assinado` sem data é bloqueado; com data futura, também.
- Criar um contrato direto sem título, sem categoria, ou sem fornecedor **e** sem favorecido é bloqueado.
- Cancelar um contrato por decisão reabre a decisão e devolve o Contratado a "—".
- Cancelar ou excluir um contrato com parcela `Pago` é recusado com orientação.
- Um contrato direto com fornecedor `Contratado` o marca assim na ficha e conclui o marco "Fechar …" da categoria.

---

## F-CTR-02 — Arquivos do Contrato

**Regras**
1. Os mesmos controles de `F-CTT-07`: **arquivo** (PDF ou imagem, via `FileStorage`, com validação de tipo real e tamanho) ou **link**.
2. Cada arquivo tem um **tipo**: `Contrato assinado` · `Minuta` · `Outro`. O Dossiê do Dia D (Bloco 4.2) usa o `Contrato assinado`.
3. Título e comentário opcionais. Autor como rótulo. Só o autor remove o seu, de forma lógica e recuperável.
4. Visualização do PDF dentro do app. No celular, o envio abre a câmera ou a galeria.
5. O contrato e seus arquivos entram na **busca global** (`F-CTT-10`): título, fornecedor ou favorecido, categoria e nome de arquivo.

**Critérios de aceite**
- Anexar um PDF do tipo `Contrato assinado` o mostra no contrato e permite abri-lo.
- Um arquivo com extensão trocada é recusado.

---

## F-CTR-03 — Dados do Dia D no Contrato

**O que é:** o que o(a) cerimonialista precisa saber do fornecedor. O Dossiê do Dia D (Bloco 4.2) **apenas lê** estes campos: não há cadastro duplicado.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Responsável no dia — nome** | Texto curto | Quem estará no evento. Pode ser diferente de "Quem atende" |
| **Responsável no dia — WhatsApp** | Telefone brasileiro | Normalizado para `wa.me/55…` (`F-CTT-01`) |
| **Responsável no dia — função** | Texto curto, opcional | Ex.: "coordenação de equipe" |
| **Itens contratados** | Lista de textos | Por decisão: **copiada uma vez** dos itens inclusos da proposta e das descrições dos extras `Necessário`, com o prefixo "Extra:" nestes. Editável |
| **Combinados operacionais críticos** | Lista de textos | Livre. Ex.: "Horário limite de som: 02h00", "inclui 10 refeições de staff" |

**Regras**
1. Na criação por decisão, o responsável no dia é **sugerido** com o "Quem atende" e o WhatsApp do fornecedor, e o casal confirma ou edita. É uma cópia única.
2. Adicionar, editar, remover e reordenar itens e combinados.
3. **Pendências do Dossiê (derivadas):** o contrato mostra "Faltam dados para o Dossiê: …" quando faltar o responsável no dia (nome ou WhatsApp), os itens contratados, ou o PDF `Contrato assinado` num contrato `Assinado`. É só informação: **não bloqueia nada**.

**Critérios de aceite**
- Um contrato por decisão traz os itens inclusos da proposta e os extras necessários com "Extra:".
- Editar os itens do contrato **não** altera a proposta.
- Um contrato `Assinado` sem PDF `Contrato assinado` mostra a pendência.
- Um WhatsApp inválido mostra erro e não gera link.

---

## F-CTR-04 — Parcelas

**O que é:** cada pagamento previsto do contrato.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Descrição** | Texto, obrigatório | Ex.: "Sinal", "Parcela 2 de 6", "Quitação" |
| **Vencimento** | **Data** · **No dia do evento** | "No dia do evento" usa a data do casamento (`F-PLN-01`) quando `Definida`; senão mostra "no dia do evento (data a definir)" |
| **Valor previsto** | Dinheiro, centavos, obrigatório | Maior que zero |
| **Meio de pagamento** | `PIX` · `Boleto` · `Cartão` · `Transferência` · `Dinheiro` · `Outro` | Opcional |
| **Responsável** | `Noivo` · `Noiva` · `Ambos` | Quem cuida do pagamento. Padrão `Ambos` |
| **Status** | `Pendente` · `Pago` | Padrão `Pendente` |
| **Nota** | Texto curto, opcional | — |

**Ao marcar `Pago` (`D-036`)**

| Campo | Regras |
| :--- | :--- |
| **Data do pagamento** | Obrigatória. Padrão hoje. Não pode ser futura |
| **Valor pago** | Obrigatório. Padrão: o valor previsto. **Pode ser diferente** (juros, desconto, multa). A diferença é mostrada ("pago R$ 20,00 a mais") |
| **Pago por** | `Noivo` · `Noiva` · `Conta Conjunta`. Obrigatório |
| **Comprovante** | Arquivo (PDF ou imagem) ou link, opcional. Mesmos controles de `F-CTT-07` |

**Derivados**
- **`Atrasada`:** `Pendente` com vencimento anterior a hoje. Mostra ícone e texto, nunca só cor. "No dia do evento" só atrasa depois de passada a data do casamento `Definida`.
- **Dias para vencer:** "vence em 3 dias" em linguagem direta, com a data no `title`.

**Regras**
1. **Desfazer pagamento** devolve a `Pendente`, pede confirmação e registra no histórico com autor e data. Os dados do pagamento anterior ficam no histórico.
2. **Parcela `Pago` não é excluída**: desfaz-se o pagamento antes. Parcela `Pendente` pode ser excluída.
3. Parcelas só existem em contratos `Aguardando assinatura` ou `Assinado`. As de um contrato `Cancelado` ficam guardadas e fora dos totais.
4. **Saldo do contrato (derivado):** "Programado R$ X de R$ Y" com X a soma dos valores previstos de todas as parcelas do contrato. Se X < Y: "faltam R$ Z a programar". Se X > Y: "R$ Z acima do valor do contrato", em argila (`attention`) com ícone e texto. É **só aviso**, não bloqueia.
5. No celular, marcar `Pago` leva poucos toques: o formulário abre com data de hoje e valor previsto, e o casal só escolhe quem pagou.
6. Qualquer um dos dois cria, edita e marca como paga. A autoria fica no histórico básico.

**Critérios de aceite**
- Marcar uma parcela `Pago` sem informar quem pagou é bloqueado.
- Marcar `Pago` com data de amanhã é bloqueado.
- Uma parcela de R$ 1.000,00 paga com R$ 1.020,00 mostra "pago R$ 20,00 a mais", e o Realizado soma R$ 1.020,00.
- Uma parcela `Pendente` com vencimento de ontem mostra `Atrasada` com ícone e texto.
- "No dia do evento" sem data do casamento `Definida` mostra "data a definir" e nunca fica `Atrasada`.
- Desfazer um pagamento devolve a `Pendente` e reduz o Realizado.
- Excluir uma parcela `Pago` é recusado.
- Contrato de R$ 10.000,00 com parcelas somando R$ 9.000,00 mostra "faltam R$ 1.000,00 a programar", sem bloquear.

---

## F-CTR-05 — Assistente de Plano de Pagamento (`D-036`)

**O que é:** gera as parcelas de um contrato a partir de uma combinação comum (sinal, parcelas iguais e quitação). O casal pode, depois, **ajustar cada parcela à mão**.

| Entrada | Tipo | Regras |
| :--- | :--- | :--- |
| **Sinal** | Percentual **ou** valor, opcional | Com data de vencimento |
| **Parcelas iguais** | Quantidade, inteiro ≥ 0 | Mensais |
| **Primeiro vencimento** | Data | Obrigatório se houver parcelas iguais. As demais seguem mês a mês, respeitando o fim do mês (31 → 30 ou 28/29) |
| **Quitação** | Percentual **ou** valor, opcional | Vencimento: "X dias antes do evento" (exige data do casamento `Definida`), "No dia do evento" ou uma data |
| **Meio de pagamento e responsável** | Como em `F-CTR-04` | Valem para todas as geradas |

**Regras**
1. **Pré-visualização** antes de gerar, com a lista de parcelas, datas, valores e o resumo "Programado R$ X de R$ Y".
2. **Parcelas iguais** = (valor do contrato − sinal − quitação) ÷ quantidade, **arredondado para baixo ao centavo**; a **diferença em centavos vai para a última parcela**, de modo que a soma **sempre bate** com o valor do contrato.
3. Sinal mais quitação **não podem ultrapassar** o valor do contrato. Valor do contrato vazio bloqueia o assistente com "defina o valor".
4. Descrições automáticas: "Sinal", "Parcela N de M" e "Quitação".
5. **Gerar de novo** substitui só as parcelas `Pendente`, com confirmação. As `Pago` **nunca** são tocadas, e o valor já pago é descontado do restante a distribuir.
6. Sem o assistente, o casal lança parcela por parcela. O assistente não é obrigatório.

**Critérios de aceite** *(contrato fictício de R$ 10.000,00)*
- Sinal de 30% (R$ 3.000,00), quitação de 20% (R$ 2.000,00) e 6 parcelas iguais geram 8 parcelas: o sinal, 5 de R$ 833,33, uma última de R$ 833,35 e a quitação, somando R$ 10.000,00.
- Sinal de 60% com quitação de 50% é bloqueado, com a orientação de que passam do valor do contrato.
- Primeiro vencimento em 31/01 gera a segunda parcela em 28/02 (ou 29/02 em ano bissexto).
- "Quitação 15 dias antes do evento" sem data do casamento `Definida` é bloqueada, com a opção de escolher uma data.
- Gerar de novo com 2 parcelas `Pago` mantém as duas e redistribui só o saldo restante entre as pendentes.

---

## F-CTR-06 — Fluxo de Pagamentos (aba 3 de Orçamento & Simulador)

**O que é:** a visão mensal dos desembolsos de **todos os contratos**: o que já saiu, o que vence e o que está atrasado.

| Recurso | Comportamento |
| :--- | :--- |
| **Lista por mês** (padrão) | Atrasadas no topo, depois um grupo por mês, e por fim "No dia do evento" e "Sem data definida". Cada grupo mostra total previsto, pago e pendente |
| **Calendário** | Grade mensal com as parcelas no **dia do vencimento**, como em `F-CRN-10`. No celular, grade compacta com a lista do dia logo abaixo |
| **Resumo** | Total contratado, total pago, **a pagar** e total atrasado, de todos os contratos ativos |
| **Cada item** | Descrição, contrato e fornecedor, categoria, valor previsto, vencimento, meio, responsável e status (`Pendente`, `Pago`, `Atrasada`) |
| **Filtros** | Status, categoria, contrato ou fornecedor, responsável, meio de pagamento e período. Na **URL** (`D-021`) |
| **Lente** | `Minha visão` filtra pelo **responsável** da parcela (o perfil da sessão e `Ambos`); `Casal` mostra todas |
| **Ação** | Marcar `Pago` direto do item, sem abrir o contrato |
| **Desktop** | Tabela agrupada por mês, valores à direita em mono tabular (`design-system.md` §4) |
| **Mobile** | Cartões por mês, com o botão "Marcar como paga" |

**Regras**
1. É uma **visão** sobre as parcelas, sem cópia. Contratos `Cancelado` não entram.
2. Os totais de um mês somam o previsto das `Pendente` e o **valor pago** das `Pago`.
3. Cor nunca é o único sinal.
4. **A projeção contra poupança e os alertas de vencimento** ficam em v1.1+ (`scope.md` §3, `D-013`).
5. Sem contratos: "Nenhum contrato ainda", com a ação "Ver contratos".

**Critérios de aceite**
- Uma parcela de R$ 833,33 vencendo em 10/03/2027 aparece no grupo de março de 2027 e no dia 10 do calendário.
- A parcela atrasada aparece no topo, com ícone e texto.
- Com a `Noiva` logada e a lente `Minha visão`, só aparecem parcelas da `Noiva` e de `Ambos`.
- Marcar uma parcela como paga no Fluxo atualiza o resumo e o Realizado do Orçamento sem recarregar.
- Aplicar um filtro altera a URL, e o botão voltar do navegador o desfaz.
- Em 320 px, nenhum cartão exige rolagem horizontal.

---

## F-CTR-07 — Efeito no Orçamento Ativo (`D-036`)

**Colunas (cenário ativo, `F-ORC-06`)**

| Coluna | Origem agora |
| :--- | :--- |
| **Contratado** | **Soma** dos valores fechados dos contratos **não cancelados** da categoria (`Aguardando assinatura` e `Assinado`). Contrato sem valor não conta, e a categoria mostra "—" se **nenhum** contrato tiver valor. Substitui o Contratado derivado da proposta de `F-PRP-08` |
| **Realizado (Pago)** | **Soma** dos **valores efetivamente pagos** das parcelas `Pago` dos contratos da categoria. Sem nenhuma parcela paga: "—" |
| **A pagar** (indicador, não coluna) | `Contratado − Realizado`. Se o pago passar do contratado, mostra "pago R$ X a mais" em argila, com ícone e texto |
| **Saldo da categoria** | **Não muda**: `Planejado − (Contratado, se houver; senão Estimado)`. O que já foi pago não altera quanto cabe no teto |

**Regras**
1. Contratado e Realizado continuam sendo **fatos do casamento** e só aparecem no cenário **ativo** (`D-032`).
2. Uma categoria `Talvez` com a linha **desligada** no cenário ativo **mostra e soma** seu Contratado e Realizado: são fatos, independentes da simulação.
3. O consolidado soma o Contratado e o Realizado de todas as categorias; "—" nunca conta como zero.
4. A barra de uso do teto (`F-ORC-07`) segue com o melhor valor conhecido (Contratado, se houver; senão Estimado).
5. O consolidado mostra "A pagar total" ao lado dos totais.

**Critérios de aceite**
- Dois contratos na mesma categoria, de R$ 3.000,00 e R$ 1.200,00, mostram Contratado de R$ 4.200,00.
- Pagar R$ 1.000,00 de um contrato de R$ 3.000,00 mostra Realizado de R$ 1.000,00 e "a pagar R$ 2.000,00".
- Um contrato `Cancelado` não soma.
- Uma categoria sem contratos mostra "—" em Contratado e Realizado, e o consolidado não os conta como zero.
- Um pagamento de R$ 1.020,00 numa parcela de R$ 1.000,00 soma R$ 1.020,00 no Realizado.

---

## F-CTR-08 — Lista de Contratos, Visões e Filtros

**Aba "Contratos" da área Possibilidades & Decisões**

| Recurso | Comportamento |
| :--- | :--- |
| **Conteúdo** | Todos os contratos, por decisão ou diretos. Por padrão, esconde os `Cancelado` |
| **Cada item** | Título, fornecedor ou favorecido, categoria, valor fechado, estado, **progresso de pagamento** ("pago R$ X de R$ Y"), próxima parcela a vencer e as pendências do Dossiê |
| **Filtros** | Estado, categoria, origem (decisão ou direto), fornecedor, "com parcela atrasada" e "com pendências do Dossiê". Na **URL** |
| **Ação** | "Novo contrato direto" (F-CTR-01) |
| **Selo derivado `Quitado`** | Quando não há parcela `Pendente` e o total pago alcança o valor fechado |
| **Desktop** | Tabela com painel lateral de detalhe |
| **Mobile** | Cartões |

**Regras**
1. A **ficha do fornecedor** ganha a aba "Contratos" (os dele) e mostra o resumo "pago R$ X de R$ Y".
2. A **categoria decidida** mostra um atalho "Ver contrato".
3. Estado vazio: "Nenhum contrato ainda", com a ação "Novo contrato direto".

**Critérios de aceite**
- Um contrato com todas as parcelas pagas mostra `Quitado`.
- O filtro "com parcela atrasada" lista só os contratos que têm uma.
- Cancelados só aparecem com o filtro de estado.
- Em 320 px, nenhum cartão exige rolagem horizontal.

---

## F-CTR-09 — Exportação do Fluxo de Pagamentos (`D-036`)

**Formatos:** **Excel (`.xlsx`) como padrão** e **CSV como opção**, como em `F-CNV-08`.

**Colunas (fixas):** Contrato · Fornecedor ou favorecido · Categoria · Descrição da parcela · Vencimento · Valor previsto · Meio de pagamento · Responsável · Status · Data do pagamento · Valor pago · Pago por.

**Regras**
1. Uma linha por parcela. Respeita os **filtros** ativos: exporta o que está na tela, com aviso do tamanho ("23 parcelas").
2. Valores em número, com formato monetário no Excel e **vírgula decimal** no CSV. **CSV** em UTF-8 com BOM e separador `;`. **Excel** com cabeçalho fixo e larguras adequadas.
3. O download é gerado no backend e protegido por sessão.

**Critérios de aceite**
- O `.xlsx` abre no Excel sem aviso de arquivo corrompido e com acentos corretos.
- O CSV abre no Excel pt-BR com cada campo em sua coluna.
- Exportar com o filtro "Atrasadas" traz só essas parcelas, e o aviso mostra a contagem.

---

## Fora desta área (v1)
- **Movimentação financeira e Open Banking** dentro do app: fora do produto (`scope.md` §3).
- **Projeção de poupança versus desembolso e alertas de vencimento ou desvio:** v1.1+.
- **Notificações de vencimento** (in-app, push, WhatsApp): v1.1+ (`D-013`).
- **Registro de aditivos de valor** e **política de cancelamento ou reajuste** como campos: não entram (`D-036`).
- **Reembolsos, multas e rescisão com devolução de valores:** fora da v1. O casal ajusta o valor do contrato ao que foi devido.
- **Conciliação bancária e leitura de comprovantes por IA:** fora da v1.
- **Assinatura eletrônica dentro do app:** fora do produto.

## Pontos de atenção para as próximas áreas e para o uso
1. **Bloco 4.2:** o Dossiê lê o contrato (responsável no dia, itens, combinados e PDF `Contrato assinado`) e os saldos a pagar "No dia do evento". O Centro de Comando consome parcelas a vencer e atrasadas.
2. **Validar em uso:** contratos por pessoa de buffet costumam ter **garantia mínima** e ajuste final conforme os confirmados. Hoje o valor fechado é um número fixo, editável. Se o ajuste for frequente, criar um campo de "quantidade contratada".
3. **Validar em uso:** mostrar Contratado e Realizado de uma categoria `Talvez` desligada somando no consolidado (regra 2 de `F-CTR-07`).
4. ~~**Bloco 4.1:** itens do enxoval pagos fora de contrato.~~ Resolvido em `D-037`: o enxoval é **separado do Orçamento** e tem registro próprio de compras. O **Contrato direto** fica para compras do casamento.
