# Features: Propostas por Categoria (`features/propostas-por-categoria.md`)

> **Status:** **Aprovado pelo usuário em 2026-10-27** (`D-035`). Cobre o **Bloco 3.2**: propostas de fornecedores por categoria, Normalizador de Custo Comparável, quadro lado a lado, avaliação dupla, decisão por categoria e o que ela provoca em Orçamento, Cronograma e Contatos.
>
> **Onde aparece na tela:** área **Possibilidades & Decisões** (`experience.md` §3.1). A comparação lado a lado e o visualizador de PDF seguem `experience.md` §3.2. As propostas também aparecem na aba "Propostas" da ficha do fornecedor (`F-CTT-01`).
>
> **Fontes:** `docs/product/scope.md` §5, `docs/design/experience.md`, `docs/product/features/possibilidades-e-decisoes.md` (modelo compartilhado, `D-033`), `contatos.md` (`D-034`), `orcamento-e-simulador.md` (`D-032`), `D-007`, `D-012`, `D-021`, `D-035`.
>
> **Convenções:** `F-PRP-xx` identifica a feature. "Autor" é o usuário da sessão. Valores em centavos. Cálculos só no backend. Todo número do exemplo é fictício. Estados e valores derivados nunca são digitados. Nenhuma proposta é sugerida ou pré-carregada.

---

## Visão da Área

**Jobs atendidos:** J7 (comparar propostas com custo real) e J8 (avaliar individualmente e registrar a decisão com motivo).

**Reaproveitado do Bloco 2.2 (`F-POS-03`, `F-POS-04`, `F-POS-05`):** avaliação dupla, selo de consenso e registro de decisão com motivos. Aqui a possibilidade é do tipo `Proposta`, ligada a **uma categoria** e a **um fornecedor**.

| Objeto | O que é |
| :--- | :--- |
| **Proposta** | Um pacote de um fornecedor para uma categoria. O mesmo fornecedor pode ter vários pacotes |
| **Custo Total Real Comparável** | **Derivado**: preço base mais custos extras necessários |
| **Decisão da categoria** | A escolha de **uma** proposta e o descarte das demais, com motivos |

---

## F-PRP-01 — Proposta

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Fornecedor** | Contato do tipo Fornecedor, obrigatório | Não pode estar `Descartado`: reative-o antes. Pessoas não têm proposta |
| **Categoria** | Categoria do catálogo (`F-PLN-02`), obrigatória | Se não for uma das categorias do fornecedor, é **acrescentada** à ficha dele, com aviso |
| **Nome do pacote** | Texto, obrigatório | Único por fornecedor e categoria. Ex.: "Pacote Exemplo Completo" |
| **Preço base** | Valor total **ou** preço por pessoa | F-PRP-02 |
| **Custos extras** | Lista | F-PRP-03 |
| **Itens inclusos** | Lista de textos | Adicionar, editar, remover e reordenar |
| **Itens não inclusos** | Lista de textos | Idem |
| **Condições de pagamento** | Texto livre | Ex.: "sinal de 30% e saldo em 6 parcelas". Não gera parcelas: elas nascem no contrato (Bloco 3.3) |
| **Observações** | Texto | Livre |
| **Arquivos e links** | PDF original, imagens e links | F-PRP-04 |
| **Estado** | `Em análise` · `Escolhida` · `Descartada` | Padrão `Em análise`. Muda pela decisão ou por descarte individual |

**Regras**
1. **Onde criar:** na ficha do fornecedor ("Nova proposta", com o fornecedor já definido) ou na categoria ("Nova proposta", escolhendo o fornecedor ou criando um fornecedor na hora, só com nome, porque a categoria já é conhecida).
2. **"Duplicar como novo pacote"** copia os campos e abre a edição, para registrar variações do mesmo fornecedor.
3. Qualquer um dos dois cria e edita. A autoria fica no histórico básico.
4. **Descarte individual:** uma proposta pode ser descartada antes da decisão, com **motivo obrigatório**. Reabrir a devolve a `Em análise`.
5. **Excluir** é lógico e recuperável. Uma proposta `Escolhida` só pode ser excluída depois de **reabrir a decisão** (F-PRP-08). Um fornecedor com proposta ou decisão não pode ser excluído antes disso (`F-CTT-01`).
6. **Categoria decidida não recebe propostas novas:** é preciso reabrir a decisão.
7. Cadastrar a **primeira proposta** de um fornecedor **sugere** mover o status do fornecedor para `Orçamento recebido`. O casal confirma (`F-CTT-03`).

**Critérios de aceite**
- Criar uma proposta sem fornecedor, categoria ou nome do pacote é bloqueado com mensagem acionável.
- Dois pacotes com o mesmo nome no mesmo fornecedor e categoria são bloqueados.
- Escolher uma categoria que o fornecedor não tinha a acrescenta à ficha e avisa.
- Um fornecedor `Descartado` não aparece para novas propostas, e a tela explica como reativá-lo.
- Descartar uma proposta sem motivo é bloqueado.
- "Duplicar como novo pacote" abre a cópia sem gravá-la antes da confirmação.

---

## F-PRP-02 — Preço Base e Quantidade (`D-035`)

**Dois modos**, como no Simulador (`F-ORC-04`):

| Modo | Campo | Total do preço base |
| :--- | :--- | :--- |
| **Valor total** | Dinheiro em centavos | O próprio valor |
| **Por pessoa** | Preço por pessoa, em centavos | `preço × quantidade`, arredondado ao centavo |

**Quantidade (modo Por pessoa):** é a mesma de `F-ORC-03`, lida do **cenário ativo**, **sem cópia**: `quantidade = arredondar para cima(A + K × fator)`.
1. `A` e `K` vêm da **base de convidados do cenário ativo**. Com a base `Número manual`, a quantidade é o próprio número e o fator não se aplica.
2. **Fator da criança pagante:** a proposta pode ter o seu (campo opcional, percentual). Vazio, **lê o fator da linha da categoria no cenário ativo**. Vazio também lá, vale 100%.
3. O cabeçalho da proposta mostra a base em linguagem clara: "Quantidade: 5 pessoas (base do cenário ativo, arredondada para cima)".

**Quando a quantidade não existe**
- Sem cenário ativo: "defina o cenário ativo" nos totais por pessoa.
- Base `Estimado Ponderado` sem pesos, ou `Número manual` vazio: "defina a base de convidados" (`F-ORC-03`, regras 2 e 3).
- Nesses casos, o **total comparável é "—"** e a tela diz o motivo. **Nenhum número é presumido**. Propostas no modo Valor total não dependem da base.

**Critérios de aceite** *(valores fictícios; base do cenário ativo resulta em 5 pessoas)*
- Preço por pessoa de R$ 200,00 resulta em total de preço base de R$ 1.000,00.
- Mudar o cenário ativo para uma base de 6 pessoas atualiza o total sem recarregar.
- Sem cenário ativo, o total de uma proposta por pessoa mostra "—" e "defina o cenário ativo", enquanto uma proposta em valor total continua mostrando o seu.
- Um fator de 50% na proposta prevalece sobre o fator da linha; apagá-lo volta a ler o da linha.

---

## F-PRP-03 — Custos Extras e Custo Total Real Comparável (`D-007`, `D-035`)

**O que é:** o **Normalizador de Custo Comparável**. Soma o que o fornecedor não coloca no preço, para comparar propostas em pé de igualdade.

**Custo extra**

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Descrição** | Texto, obrigatório | Ex.: "Gerador", "ECAD", "Taxa de rolha", "Horas extras", "Deslocamento", "Mobiliário complementar" |
| **Cobrança** | `Fixo` · `Por pessoa` | Por pessoa usa a quantidade de F-PRP-02 |
| **Valor** | Dinheiro em centavos | Valor total (Fixo) ou por pessoa |
| **Necessidade** | `Necessário` · `Opcional` | Padrão `Necessário` |
| **Nota** | Texto curto, opcional | Ex.: "só se a festa passar das 23h" |

**Cálculo (derivado, nunca editado)**
- **Total do extra** = valor (Fixo) ou `valor × quantidade` (Por pessoa).
- **Custo Total Real Comparável** = total do preço base + soma dos totais dos extras `Necessário`.
- Os extras `Opcional` **não somam**. Aparecem à parte: "Com opcionais: R$ …".
- **Custo por convidado equivalente** (`D-035`) = Custo Total Real Comparável ÷ `arredondar para cima(A + K)` do cenário ativo (sem fator), como em `F-ORC-03`, regra 5. Permite comparar propostas em modos diferentes. Sem base: "—".
- Se algum componente depende da quantidade e ela não existe, o total é "—" (F-PRP-02).

**Regras**
1. Mudar a necessidade de um extra recalcula na hora.
2. Cada linha mostra seu total calculado.
3. Qualquer um adiciona, edita e remove extras, e a autoria fica no histórico básico.

**Critérios de aceite** *(quantidade fictícia de 5 pessoas)*
- Preço por pessoa de R$ 200,00 (R$ 1.000,00), extra Fixo necessário "Gerador" de R$ 1.500,00 e extra Por pessoa necessário "Taxa de rolha" de R$ 10,00 (R$ 50,00) resultam em **Custo Total Real Comparável de R$ 2.550,00**.
- Um extra opcional de R$ 800,00 não altera o R$ 2.550,00 e mostra "Com opcionais: R$ 3.350,00".
- Marcar o extra "Gerador" como `Opcional` leva o total a R$ 1.050,00.
- Com 5 pessoas, o custo por convidado equivalente de R$ 2.550,00 é R$ 510,00.
- Um extra sem descrição é bloqueado.

---

## F-PRP-04 — PDF Original, Arquivos e Links

**Regras**
1. Os mesmos controles de `F-CTT-07`: **arquivo** (PDF ou imagem, via `FileStorage`, com validação de tipo real e tamanho) ou **link** (domínio visível, sem leitura automática da página).
2. Título e comentário opcionais. Autor como rótulo. Qualquer um adiciona; **só o autor** remove o seu, de forma lógica e recuperável.
3. **Visualização do PDF** dentro do app: no desktop, em painel lateral ao lado do quadro comparativo; no celular, em 1 toque.
4. O sistema **não lê o conteúdo** do PDF. Os campos são digitados pelo casal (a extração por IA é v1.1+, `scope.md` §5).
5. No celular, o envio abre a câmera ou a galeria.

**Critérios de aceite**
- Anexar um PDF a uma proposta o mostra com nome e tamanho, e permite abri-lo no painel lateral.
- Um arquivo com extensão trocada é recusado.
- No celular, abrir o PDF leva 1 toque a partir do cartão da proposta.

---

## F-PRP-05 — Avaliação Dupla e Selo de Consenso

**Regras:** **as mesmas** de `F-POS-03` e `F-POS-04` (`D-012`, `D-021`, `D-033`): classificação obrigatória (`Favorito`, `Gostei`, `Com ressalvas`, `Descartaria`), nota de 1 a 5 opcional que **só informa**, comentário opcional, cada um edita só a sua, e a avaliação do outro aparece de imediato. O selo (`Aguardando avaliação`, `Ambos descartariam`, `Consenso Favorito`, `Conversar juntos`) é **derivado** com a mesma tabela.

**Particularidades**
1. A avaliação **continua editável** depois da decisão, com a alteração no histórico.
2. **Descartar uma proposta** não apaga as avaliações.
3. O Custo Total Real Comparável aparece junto da avaliação, mas **não entra no selo**.

**Critérios de aceite**
- Noivo `Favorito` e Noiva `Gostei` mostram `Consenso Favorito` numa proposta, com ícone e texto.
- Noivo `Favorito` e Noiva `Descartaria` mostram `Conversar juntos`, sem vermelho.
- A Noiva logada não altera a avaliação do Noivo.

---

## F-PRP-06 — Quadro Comparativo Lado a Lado

| Elemento | Conteúdo |
| :--- | :--- |
| **Quantidade** | De **2 a 5** propostas `Em análise` da **mesma categoria** |
| **Linhas, nesta ordem** | Fornecedor e pacote · Preço base (com o modo) · Extras necessários · **Custo Total Real Comparável** · Custo por convidado equivalente · Situação frente ao teto (F-PRP-07) · Com opcionais · Condições de pagamento · Itens inclusos · Itens não inclusos · PDF · Avaliação do Noivo · Avaliação da Noiva · Selo de consenso |
| **Destaque** | Nenhum. **O Altare não elege a "melhor" proposta**: o custo e o selo informam, e quem decide é o casal |
| **Ordenação** | Controle com "por custo total", "por selo" e "por nome". Padrão: por custo total, com as propostas sem total ao final |
| **Desktop** | Tabela com primeira coluna fixa e colunas ≥ 280 px por proposta, e **painel lateral de PDF** |
| **Mobile** | **Cartões empilhados com abas deslizantes**, focados no Custo Total, no resumo do que inclui, no PDF em 1 toque e no atalho para avaliar |
| **Estado** | A seleção fica na **URL** (compartilhável) |

**Regras**
1. Valores monetários à direita, em fonte mono tabular (`design-system.md` §4). O "—" nunca é lido como zero.
2. Uma proposta sem total mostra o motivo (F-PRP-02) na própria coluna.
3. Selecionar propostas de categorias diferentes é recusado.

**Critérios de aceite**
- Com duas propostas de R$ 2.550,00 e R$ 3.100,00, a coluna de custo total mostra os dois valores sem destacar nenhum como melhor.
- Selecionar uma sexta proposta é recusado com "compare até 5 propostas".
- Selecionar propostas de duas categorias é recusado com mensagem acionável.
- Recarregar a página com a seleção na URL restaura o quadro.
- Em 320 px, os cartões não exigem rolagem horizontal.

---

## F-PRP-07 — Orçamento: Faixa de Referência e Situação Frente ao Teto (`D-035`)

**Faixa de referência no Orçamento Ativo**
1. Na linha da categoria, no **cenário ativo** (aba Orçamento Ativo e detalhe da linha), aparece: "Propostas em análise: R$ X a R$ Y (N propostas)", com o **menor e o maior** Custo Total Real Comparável das propostas `Em análise` que têm total.
2. É **só referência**: **não altera o Estimado** (`D-035`). O Estimado continua sendo do casal, por cenário.
3. Propostas sem total não entram na faixa, e a linha diz "M sem total".
4. A faixa **não aparece nos cenários em simulação**: a base de convidados da proposta é a do cenário ativo.
5. Com uma proposta `Escolhida`, a linha mostra o **Contratado** (F-PRP-08) no lugar da faixa.

**Situação frente ao teto, por proposta**
1. Compara o Custo Total Real Comparável com o **Planejado** da categoria no cenário ativo, com a regra visual de `F-ORC-07`: dentro do teto (sálvia, ícone `circle-check`, "R$ X abaixo do teto") ou acima (argila, ícone `circle-alert`, "acima do teto em R$ X"). Cor nunca é o único sinal.
2. Sem Planejado: "sem teto na categoria". Sem cenário ativo: "sem cenário ativo". Sem total: "—".

**Critérios de aceite** *(valores fictícios)*
- Duas propostas em análise, de R$ 2.550,00 e R$ 3.100,00, mostram na linha "R$ 2.550,00 a R$ 3.100,00 (2 propostas)" e o Estimado fica inalterado.
- Uma proposta de R$ 3.100,00 numa categoria com Planejado de R$ 3.000,00 mostra "acima do teto em R$ 100,00", com ícone e texto.
- Uma categoria sem Planejado mostra "sem teto na categoria".
- A faixa não aparece num cenário em simulação.

---

## F-PRP-08 — Decisão por Categoria (`D-007`, `D-035`)

**O que é:** bater o martelo em **uma** proposta da categoria e descartar as demais, com os motivos. Reaproveita o fluxo de `F-POS-05`.

**Fluxo**
1. Na categoria, o casal clica em **"Registrar decisão"** e escolhe a **proposta vencedora** entre as `Em análise`. **Basta uma proposta** para decidir (contratar sem comparar).
2. Escreve o **motivo da escolha** (**obrigatório**).
3. Para **cada proposta descartada pela decisão**, escreve o **motivo do descarte** (**obrigatório**), com o atalho "usar o mesmo texto nos demais". As já descartadas individualmente mantêm seu motivo.
4. A tela **avisa**, e o casal confirma para seguir, quando houver: avaliação faltando de um dos dois, proposta vencedora **acima do teto** da categoria, ou total **sem valor** (por falta de base de convidados), caso em que o Contratado ficará "—".
5. A tela mostra os efeitos (abaixo) e pede confirmação.

**Efeitos**

| Efeito | Comportamento |
| :--- | :--- |
| **Contrato e Contratado** | A decisão **cria o contrato** `Aguardando assinatura` (`F-CTR-01`), com o valor **copiado uma vez** do Custo Total Real Comparável (editável). O **Contratado** da categoria passa a ser a soma dos contratos (`F-CTR-07`), só no cenário ativo (`F-ORC-06`) |
| **Cronograma** | O marco **"Fechar …"** da categoria é concluído **automaticamente** (`F-CRN-03`, regra 6), destravando o que depende dele. Categorias sem marco "Fechar" não têm este efeito |
| **Fornecedor** | O fornecedor da proposta escolhida passa a `Contratado` (derivado, `F-CTT-03`). Cada mudança entra na linha do tempo dele |
| **Fornecedores das descartadas** | **Oferece**, **desmarcado por padrão**, marcar como `Descartado` os fornecedores que ficaram **sem nenhuma outra proposta ativa**, com a nota "descartado na decisão de [categoria]" |
| **Estimado** | **Nenhum.** O Estimado não é alterado (F-PRP-07) |

**Registro:** data, autor, proposta escolhida, motivo da escolha e motivos de cada descarte. A escolhida vai a `Escolhida`, e as demais a `Descartada`.

**Reabrir a decisão**
1. Qualquer um pode **reabrir**: as propostas descartadas **pela decisão** voltam a `Em análise` (as descartadas individualmente continuam `Descartada`), **os motivos ficam no histórico** e o marco "Fechar …" é reaberto.
2. O **contrato** da decisão é **cancelado** (`F-CTR-01`, regra 3) e o **Contratado** da categoria volta a "—". **Reabrir é recusado enquanto houver parcela `Pago`** no contrato; desfaça os pagamentos antes.
3. O fornecedor volta ao **status que tinha antes da decisão**, guardado no registro, com entrada na linha do tempo. Fornecedores marcados `Descartado` pela oferta **não** são reativados sozinhos.
4. Uma nova decisão gera um **novo registro**, sem apagar os anteriores.

**Regras de coerência com o escopo**
1. Uma categoria com proposta `Escolhida` **não pode** ir para `Fica de fora` nem `Em discussão` no Mapa de Escopo. É preciso reabrir a decisão (`F-PLN-07`, regra 3).
2. Só existe **uma** decisão ativa por categoria. Para escolher mais de um fornecedor numa mesma área, o casal usa categorias separadas no Mapa de Escopo (`D-035`).

**Transição na entrega do bloco**
- Até o Bloco 3.2, `Contratado` era um status manual do fornecedor (`F-CTT-03`). Na entrega do bloco, ele passa a ser derivado, e **os fornecedores marcados à mão como `Contratado` voltam a `Em negociação / Visita`**, com entrada na linha do tempo explicando o motivo.

**Critérios de aceite**
- Registrar sem motivo da escolha, ou com um descarte sem motivo, é bloqueado com mensagem acionável.
- Decidir uma categoria com uma única proposta funciona e não pede motivos de descarte.
- A decisão conclui o marco "Fechar o Espaço", destrava os marcos que dependem dele e mostra o Contratado na linha da categoria no Orçamento Ativo.
- Escolher uma proposta de R$ 3.100,00 com Planejado de R$ 3.000,00 mostra o aviso "acima do teto em R$ 100,00" e só segue com confirmação.
- O fornecedor da escolhida passa a `Contratado`, e a mudança aparece na linha do tempo dele.
- A oferta de descartar fornecedores vem desmarcada.
- Reabrir a decisão reabre o marco, zera o Contratado ("—"), devolve o fornecedor ao status anterior e preserva os motivos no histórico.
- Mover uma categoria com decisão para `Fica de fora` é recusado com "reabra a decisão antes".
- Adicionar uma proposta a uma categoria decidida é recusado com "reabra a decisão antes".

---

## F-PRP-09 — Visões, Filtros e Lente

**Lista de categorias (entrada da área)**

| Recurso | Comportamento |
| :--- | :--- |
| **Conteúdo** | Categorias `Entra` e `Talvez`, mais as `Em discussão` ou `Fica de fora` que já tenham propostas, com o estado do Escopo rotulado |
| **Por categoria** | Estado derivado: `Sem proposta` · `Em análise (N)` · `Decidida`, o Contratado quando houver e quantas avaliações faltam |
| **Entrar na categoria** | Mostra as propostas em cartões, o quadro comparativo, "Registrar decisão" e o histórico de decisões |

**Dentro da categoria**

| Recurso | Comportamento |
| :--- | :--- |
| **Filtros** | Estado, fornecedor, selo de consenso e "só o que falta eu avaliar". Estado na **URL** |
| **Lente `Casal`** | Destaca propostas em `Conversar juntos` |
| **Lente `Minha visão`** | Destaca propostas em que falta **a minha** avaliação |
| **Mobile** | Cartões; detalhe em folha inferior; avaliar em poucos toques |

**Regras**
1. As propostas de um fornecedor também aparecem na aba "Propostas" da ficha dele, com categoria, custo total, estado e selo.
2. Propostas são encontradas pela **busca global** (`F-CTT-10`): nome do pacote, fornecedor, categoria e nome de arquivo.
3. Estado vazio da categoria: "Nenhuma proposta ainda", com a ação "Nova proposta".

**Critérios de aceite**
- Uma categoria `Entra` sem propostas aparece como `Sem proposta`.
- Com o Noivo em `Minha visão`, as propostas que ele ainda não avaliou aparecem destacadas.
- Aplicar um filtro altera a URL, e o botão voltar do navegador o desfaz.
- Buscar o nome de um pacote na busca global leva à proposta.
- Em 320 px, nenhum cartão exige rolagem horizontal.

---

## Fora desta área (v1)
- **Extração de dados de PDF ou WhatsApp por IA** e **equalizador de assimetrias por IA:** v1.1+ (`scope.md` §5).
- **Leilão reverso e envio automático de mensagens a fornecedores:** fora do produto.
- **Mais de uma proposta vencedora por categoria:** não entra (`D-035`). Categorias separadas resolvem.
- **Validade da proposta e selo "Vencida":** não entra (`D-035`).
- **Histórico de revisões de preço da proposta:** não entra (`D-035`). A alteração de qualquer campo fica no histórico básico, mas sem versões navegáveis.
- **Alimentar o Estimado a partir de propostas:** não entra. Só há a faixa de referência (F-PRP-07).
- **Parcelas e meios de pagamento:** Bloco 3.3. A condição de pagamento da proposta é texto livre.
- **Contrato, parcelas e Contratado:** Bloco 3.3 (`contratos-e-parcelas.md`, `D-036`).

## Pontos de atenção para as próximas áreas
1. ~~**Bloco 3.3:** criação do contrato e divergência com o custo comparável.~~ Resolvido em `D-036`: o contrato é criado **automaticamente** com a decisão, com o valor copiado e editável, e a divergência aparece como "difere do comparável em R$ X".
2. ~~**Bloco 3.3:** saldo da categoria considerar o que foi pago.~~ Resolvido em `D-036`: o saldo **não muda**; o pago aparece no indicador "A pagar".
3. **Bloco 4.2:** o Centro de Comando consome "propostas em `Conversar juntos`" e "avaliações pendentes de cada perfil".
4. **Validar em uso:** a base de convidados do cenário ativo como única referência de quantidade; se cenários de simulação precisarem comparar propostas com a base deles, revisitar.
