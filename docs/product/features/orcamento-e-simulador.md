# Features: Orçamento & Simulador (`features/orcamento-e-simulador.md`)

> **Status:** **Aprovado pelo usuário em 2026-10-27** (`D-032`). Cobre o **Bloco 2.1** (Orçamento Vivo e Simulador). O **Fluxo de Pagamentos (parcelas)** é do **Bloco 3.3** e será detalhado depois.
>
> **Fontes:** `docs/product/scope.md` §3, `docs/design/experience.md` (Fluxo 2, objeto 3), `docs/product/jobs.md` (J3, J9), `features/planejamento-e-caminhos.md` (F-PLN-05, F-PLN-07), `features/convidados-enxoval-e-dia-d.md` (F-CNV-03, F-CNV-06), `D-009` e `D-032`.
>
> **Convenções:** `F-ORC-xx` identifica a feature. Dinheiro em **centavos inteiros**, nunca `float` (`stack.md` §4). **Todo cálculo vive só no backend** (`stack.md` §5.1); a tela exibe e pede recálculo. Nenhum valor é presumido: tetos, preços e percentuais **começam vazios**.

---

## Visão da Área

**Jobs atendidos:** J3 (teto, simulação em paralelo e estimativas) e J9 (acompanhar Teto vs. Estimado vs. Contratado vs. Realizado).

**Abas da área** (`experience.md` §3.1):

| Aba | Conteúdo | Bloco |
| :--- | :--- | :--- |
| **Orçamento Oficial Ativo** | Tabela viva do cenário ativo, com as 4 colunas | 2.1 (Contratado e Realizado chegam nos Blocos 3.2 e 3.3) |
| **Simulador** | Cenários em paralelo e comparativo lado a lado | 2.1 |
| **Fluxo de Pagamentos** | Parcelas e desembolso mensal | 3.3 |

**Modelo:** o **cenário** guarda as premissas e os ajustes que são dele. As **linhas de categoria** são **derivadas do Mapa de Escopo** (`architecture.md`, "derivar, não duplicar"): uma categoria que passa a `Entra` aparece em todos os cenários sem cópia.

---

## F-ORC-01 — Cenários: Criar, Clonar, Renomear, Excluir e Ativo

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto, obrigatório | Único por casamento, sem diferenciar maiúsculas. Ex.: "Cenário A" |
| **Nota** | Texto livre | — |
| **Ativo** | Sim/não | **No máximo um** cenário é o `Oficial / Ativo` |

**Regras**
1. **Criar:** um cenário novo nasce **vazio** (sem teto, base manual, sem reserva), com as linhas derivadas das categorias `Entra`; categorias `Talvez` nascem **fora**.
2. **Clonar:** copia premissas, ajustes das linhas e a nota. O clone se chama "{nome} (cópia)" e **nunca nasce ativo**.
3. **O primeiro cenário criado vira o ativo automaticamente.** Os seguintes nascem em simulação.
4. **Excluir** é lógico e recuperável. Não é possível excluir o **ativo** enquanto houver outros cenários (promova outro antes). Se for o único, a exclusão é permitida e deixa o casamento "sem orçamento oficial".
5. **Promover a ativo:** pede confirmação e mostra o impacto (as colunas Contratado e Realizado passam a ser exibidas no novo ativo, F-ORC-06). A troca é registrada no histórico com autor e data. Os demais cenários **não se perdem**.
6. Qualquer um dos dois edita. Edição simultânea usa **bloqueio otimista**: conflito mostra "isto mudou enquanto você editava" e oferece recarregar (`architecture.md` §8).

**Critérios de aceite**
- Criar o primeiro cenário o marca como ativo; criar o segundo, não.
- Clonar o "Cenário A" gera "Cenário A (cópia)" em simulação, com os mesmos valores.
- Excluir o ativo com outro cenário existente é recusado com "promova outro cenário antes".
- Promover "Cenário B" exige confirmação, desativa o A e registra a troca.
- Dois cenários com o mesmo nome são bloqueados.

---

## F-ORC-02 — Premissas do Cenário

| Premissa | Tipo | Regras |
| :--- | :--- | :--- |
| **Teto global** | Dinheiro em centavos, opcional | Vazio até o casal definir. Pode ser sugerido pelo teto macro de `F-PLN-01` (apenas como referência exibida; **não copiado**) |
| **Base de convidados** | Uma das quatro opções de F-ORC-03 | Padrão: `Estimado Ponderado` |
| **Número manual** | Inteiro | Só quando a base for `Número manual` |
| **Reserva para imprevistos** | Percentual com até 2 casas, opcional (`D-032`) | **Vazia** até o casal definir; mostrada **à parte** (F-ORC-05) |

**Critérios de aceite**
- Num cenário novo, teto, número manual e reserva aparecem vazios.
- Digitar `R$ 120.000,00` no teto grava `12000000`.
- O teto macro de `F-PLN-01`, quando definido, aparece como "referência: R$ …" sem preencher o teto do cenário.
- A reserva aceita `10` e `7,5`, e recusa valores negativos.

---

## F-ORC-03 — Base de Convidados e Arredondamento (`D-032`)

**O que é:** o número de pessoas que o cenário usa nos custos por pessoa. A leitura da lista é feita **pela interface pública do módulo de convidados**, sem cópia.

**Quatro bases** (cada cenário escolhe uma):

| Base | Adultos (A) | Crianças pagantes (K) |
| :--- | :--- | :--- |
| **Estimado Ponderado** (`F-CNV-06`) | Soma dos adultos pelo peso da probabilidade; `Confirmado` conta 100% | Idem, para crianças pagantes |
| **Total Nominal, sem isentos** | Todos os adultos, exceto `Não irá` | Todas as crianças pagantes, exceto `Não irá` |
| **Só Certeza e Confirmados** | Adultos com probabilidade `Certeza` **ou** status `Confirmado`, exceto `Não irá` | Idem, para crianças pagantes |
| **Número manual** | O número digitado | Não se aplica |

Em todas as bases da lista, **crianças isentas** e quem está `Não irá` ficam **fora da base de custo**.

**Quantidade de uma linha por pessoa (F-ORC-04):** `quantidade = arredondar para cima(A + K × fator)`, em que `fator` é o da linha (padrão 1, ou seja, 100%). Na base `Número manual`, a quantidade é o próprio número, e o fator não se aplica.

**Regras**
1. **Arredondamento sempre para cima** (`D-032`): a contagem fracionária nunca subestima o custo.
2. Se a base for `Estimado Ponderado` e os **pesos** ainda não existirem (`F-CNV-06`), as linhas por pessoa mostram "defina os pesos" e os totais indicam "estimado incompleto". **Nenhum número é presumido.**
3. Se a base for `Número manual` sem número, as linhas por pessoa mostram "defina o número".
4. O cabeçalho do cenário mostra a base em linguagem clara: "Base: 5 pessoas (Estimado Ponderado, arredondado para cima)".
5. **Custo por convidado** = Total Estimado ÷ `arredondar para cima(A + K)` (sem fator), em centavos arredondados ao mais próximo. Sem base ou sem pessoas: "—".

**Critérios de aceite** *(pesos 100/70/30)*
- Lista: 2 adultos `Certeza`, 2 adultos `Provável`, 1 adulto `Fase 2` e 1 criança pagante `Certeza`, nenhum confirmado. A = 2 + 1,4 + 0,3 = 3,7 e K = 1. Linha de buffet a R$ 200,00 por pessoa com fator 50%: 3,7 + 1 × 0,5 = 4,2, arredonda para 5, e o custo é R$ 1.000,00.
- Nessa mesma lista, a base do cenário exibe "5 pessoas" (3,7 + 1 = 4,7 arredonda para 5).
- Sem pesos definidos, a base `Estimado Ponderado` mostra "defina os pesos" nas linhas por pessoa.
- Uma criança isenta não altera nenhuma base.
- Marcar alguém `Confirmado` atualiza a base e os custos sem recarregar.

---

## F-ORC-04 — Linhas de Categoria

**Quais linhas existem:** uma por categoria do Mapa de Escopo, **derivada** do status (`F-PLN-07`):

| Status da categoria | Linha no cenário |
| :--- | :--- |
| `Entra (Essencial)` | **Incluída** sempre |
| `Talvez (Se couber)` | **Opcional**: o casal liga ou desliga **por cenário** (nasce desligada) |
| `Em discussão` | Aparece numa seção recolhida "Em discussão", **fora dos totais** |
| `Fica de fora` ou oculta | **Não aparece**. Os valores guardados voltam se a categoria for reaberta |

**Campos de cada linha (guardados no cenário)**

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Tipo de custo** | `Fixo` · `Por pessoa` | Padrão `Fixo` |
| **Planejado** | Dinheiro em centavos, opcional | O teto da **categoria** neste cenário (valor total) |
| **Estimado** | Ver abaixo | — |
| **Fator da criança pagante** | Percentual, opcional | Só em `Por pessoa`. **Vazio conta como 100%** |
| **Incluir** | Sim/não | Só para categorias `Talvez` |

**Estimado**
- **`Fixo`:** o valor total estimado. Por padrão **lê a estimativa inicial da categoria** (`F-PLN-05`), sem copiar. O cenário pode **sobrescrever** o valor e há "voltar ao valor da categoria". Quem não sobrescreve acompanha mudanças futuras da categoria.
- **`Por pessoa`:** o **preço por pessoa** (centavos). O Estimado da linha = `preço × quantidade` (F-ORC-03), arredondado ao centavo. A estimativa da categoria aparece só como **referência** ("estimativa da categoria: R$ …"), sem preencher o preço, porque ela é um valor total.
- **Vazio** não é zero: aparece como "sem estimativa" e é sinalizado nos totais (F-ORC-05).
- **Propostas (Bloco 3.2, `D-035`):** **não alimentam o Estimado.** No cenário **ativo**, a linha mostra só uma **faixa de referência** (menor a maior Custo Total Real Comparável das propostas em análise), conforme `F-PRP-07`. Com uma proposta escolhida, a linha mostra o Contratado.

**Regras**
1. **Contratado** e **Realizado** não são campos da linha: são **derivados** e só aparecem no cenário **ativo** (F-ORC-06).
2. Mudar o tipo de custo mantém os demais campos, e o valor da outra modalidade fica guardado.
3. Valores são guardados em centavos; a edição aceita `R$ 28.000,00`.

**Critérios de aceite**
- Uma categoria nova que passa a `Entra` aparece, vazia, em todos os cenários.
- Uma categoria `Talvez` nasce desligada num cenário novo; ligá-la a inclui nos totais só daquele cenário.
- No cenário A, a estimativa da categoria é R$ 10.000,00 e não foi sobrescrita; mudá-la para R$ 12.000,00 atualiza o Estimado do cenário A. No cenário B, onde foi sobrescrita para R$ 9.000,00, nada muda.
- Uma linha `Por pessoa` com a estimativa da categoria definida mostra a referência e não preenche o preço por pessoa.
- Marcar uma categoria como `Fica de fora` a tira do cenário; reabri-la restaura os valores guardados.

---

## F-ORC-05 — Totais, Folga e Avisos

**Totais do cenário (sempre derivados)**

| Total | Cálculo |
| :--- | :--- |
| **Total Planejado** | Soma do Planejado das linhas incluídas |
| **Total Estimado** | Soma do Estimado das linhas incluídas |
| **Reserva** (`D-032`) | `Total Estimado × percentual`, arredondado ao centavo mais próximo. Zero se o percentual estiver vazio |
| **Total com reserva** | `Total Estimado + Reserva` |
| **Folga ou estouro** | `Teto global − Total com reserva`. Positivo = folga (`consensus`); negativo = estouro (`attention`) |
| **Custo por convidado** | F-ORC-03 |

**Avisos (texto + ícone, nunca só cor, nunca vermelho)**
- "**N linhas sem estimativa**": as linhas vazias não entram na soma e são contadas aqui.
- "**Estimado incompleto**": falta a base de convidados (pesos ou número manual).
- "**Os tetos das categorias somam R$ X, acima do teto global**": quando o Total Planejado ultrapassa o teto.
- "**Defina o teto global**": sem teto não há folga.

**Critérios de aceite**
- Espaço (Fixo) R$ 10.000,00 e Buffet (Por pessoa) com Estimado R$ 1.000,00 somam Total Estimado R$ 11.000,00. Com reserva de 10%, a Reserva é R$ 1.100,00 e o Total com reserva é R$ 12.100,00. Com teto de R$ 12.000,00, aparece "estouro de R$ 100,00" com ícone e texto de atenção.
- Duas linhas sem estimativa mostram "2 linhas sem estimativa" e a soma não conta zero como valor.
- Sem teto, aparece "Defina o teto global" no lugar da folga.
- Sem reserva definida, o Total com reserva é igual ao Total Estimado e a linha da reserva mostra "—".

---

## F-ORC-06 — Orçamento Oficial Ativo (tabela das 4 colunas)

**O que é:** a tabela viva do cenário **ativo**, com **Planejado · Estimado · Contratado · Realizado** por categoria e no consolidado.

| Coluna | Origem |
| :--- | :--- |
| **Planejado** | Linha do cenário (F-ORC-04) |
| **Estimado** | Linha do cenário (F-ORC-04) |
| **Contratado** | **Derivado** da soma dos contratos não cancelados da categoria (Bloco 3.3, `D-036`, `F-CTR-07`). Sem contrato com valor, "—" |
| **Realizado (Pago)** | **Derivado** da soma dos valores efetivamente pagos das parcelas `Pago` (Bloco 3.3, `D-036`). Sem pagamentos, "—". O indicador **"A pagar"** (Contratado − Realizado) acompanha a linha |
| **Saldo da categoria** | `Planejado − (Contratado, se houver; senão Estimado)`. Positivo = `consensus`; negativo = `attention`. Sem Planejado: "—" |

**Regras**
1. **Contratado e Realizado são fatos do casamento**, e não pertencem a um cenário. Por isso só aparecem no ativo; os cenários em simulação têm só Planejado e Estimado (`D-032`).
2. Editar Planejado e Estimado nesta tabela edita o **cenário ativo**, os mesmos dados do Simulador.
3. A linha de consolidado soma cada coluna; "—" não conta como zero.
4. **Desktop:** tabela com colunas numéricas à direita em fonte mono tabular (`design-system.md` §4). **Mobile:** cartões por categoria com Estimado, Contratado, Realizado e o **saldo** em destaque.
5. Sem cenário ativo, a aba mostra um estado vazio com a ação "Criar o primeiro cenário".

**Critérios de aceite**
- Com o cenário A ativo, a aba mostra suas linhas; promover o B troca as linhas exibidas sem recarregar a página.
- Contratado e Realizado mostram "—" enquanto os Blocos 3.2 e 3.3 não existirem, e a soma deles não conta zero.
- Planejado R$ 10.000,00 e Estimado R$ 9.000,00 mostram saldo de R$ 1.000,00 em `consensus`, com ícone e texto.
- Em 320 px, nenhuma linha exige rolagem horizontal.

---

## F-ORC-07 — Indicador de Uso do Teto por Categoria (`D-032`)

**O que é:** uma barra horizontal por linha que mostra quanto do **Planejado** da categoria já está comprometido.

| Elemento | Regra |
| :--- | :--- |
| **Valor da barra** | O **melhor valor conhecido**: Contratado, se houver; senão Estimado |
| **Preenchimento** | `valor ÷ Planejado`, limitado a 100% visualmente |
| **Dentro do teto** | Sálvia (`consensus`), com ícone `circle-check` |
| **Acima do teto** | Argila (`attention`), com ícone `circle-alert` e texto "acima do teto em R$ X" |
| **Texto** | Sempre completo: "R$ 9.000,00 de R$ 10.000,00 (90%)" |
| **Sem Planejado** | Sem barra; mostra "sem teto na categoria" |

**Regras**
1. A cor nunca é o único sinal (`design-system.md` §3.3 e §7).
2. Aparece no Orçamento Ativo e no detalhe do cenário; no comparativo mostra só o texto.

**Critérios de aceite**
- Estimado R$ 11.000,00 com Planejado R$ 10.000,00 mostra a barra cheia em argila, ícone de atenção e "acima do teto em R$ 1.000,00".
- Estimado R$ 9.000,00 com Planejado R$ 10.000,00 mostra 90% em sálvia com texto completo.
- Sem Planejado, não há barra e aparece "sem teto na categoria".

---

## F-ORC-08 — Comparativo Lado a Lado

**O que é:** a comparação de **2 a 4 cenários** escolhidos pelo casal.

| Elemento | Conteúdo |
| :--- | :--- |
| **Cabeçalho de cada cenário** | Nome, selo "Oficial / Ativo" quando for o caso, teto, base de convidados e reserva |
| **Totais** | Total Planejado, Total Estimado, Reserva, Total com reserva, **custo por convidado**, **folga ou estouro** |
| **Linhas por categoria** | Estimado e Planejado de cada cenário, alinhados por categoria; categoria ausente no cenário aparece como "—" |
| **Destaque** | Selo "Menor total com reserva" no cenário de menor valor entre os comparáveis (apenas entre cenários com totais completos) |

**Regras**
1. O comparativo é **leitura**. Para editar, há o botão "Editar cenário", que leva ao detalhe.
2. Um cenário com "estimado incompleto" não recebe o selo de menor valor e mostra o aviso.
3. **Desktop:** tabela com primeira coluna fixa (categorias) e colunas ≥ 280 px por cenário (`design-system.md` §9). **Mobile:** **cartões empilhados** por cenário, com abas deslizantes.
4. O estado da seleção fica na **URL** (compartilhável).

**Critérios de aceite**
- Selecionar A, B e C mostra três colunas com os totais e o custo por convidado de cada um.
- Um cenário sem a categoria Vídeo mostra "—" na linha de Vídeo.
- Se o B está com "estimado incompleto", o selo de menor valor considera só A e C.
- Selecionar um quinto cenário é recusado com "compare até 4 cenários".
- O botão voltar do navegador desfaz a seleção.

---

## F-ORC-09 — Exportação do Orçamento (`D-032`)

**Formatos:** **Excel (`.xlsx`) como padrão** e **CSV como opção** (mesmo padrão de `F-CNV-08`, `D-030`).

**Exporta:** o **cenário aberto** ou o **comparativo** atual.

| Exportação | Excel | CSV |
| :--- | :--- | :--- |
| **Cenário** | Aba "Resumo" (nome, teto, base, reserva, totais, folga) e aba "Linhas" (categoria, grupo, tipo, planejado, preço por pessoa, quantidade, fator, estimado e, no ativo, contratado, realizado e saldo) | Só a tabela "Linhas", com a linha final "Total" |
| **Comparativo** | Aba "Comparativo": categorias nas linhas e, por cenário, Planejado e Estimado, com totais | A mesma tabela plana |

**Regras**
1. No Excel, valores em **número com formato de moeda** (e não texto), cabeçalho fixo e larguras ajustadas. No CSV: UTF-8 com BOM, separador `;`, decimal com vírgula e **sem** separador de milhar.
2. "Sem estimativa" é exportado como **célula vazia**, nunca como zero.
3. O arquivo é gerado no backend e protegido por sessão.

**Critérios de aceite**
- O `.xlsx` abre sem aviso de corrupção, com acentos corretos, e os valores somam em fórmulas do Excel (são números).
- O CSV abre no Excel pt-BR com cada campo na sua coluna.
- Uma linha sem estimativa aparece com a célula vazia no `.xlsx` e no CSV.

---

## Fora desta área neste bloco
- **Fluxo de Pagamentos e parcelas:** Bloco 3.3.
- **Contratado e Realizado reais:** Bloco 3.3 (`contratos-e-parcelas.md`). Aqui só a estrutura e o "—".
- **Alimentar o Estimado a partir de propostas:** não entra (`D-035`). O Bloco 3.2 só exibe uma faixa de referência (`F-PRP-07`).
- **Projeção de fluxo de caixa vs. poupança e alertas de desvio:** v1.1+ (`scope.md` §3).
- **Movimentação financeira dentro do app:** fora do produto.
- **Nota por linha de categoria:** não solicitada.

## Pontos a validar nos blocos seguintes
1. ~~**Bloco 3.2:** como as propostas alimentam o Estimado.~~ Resolvido em `D-035`: não alimentam; o Estimado fica intacto e a decisão só gera o Contratado derivado.
2. ~~**Bloco 3.3:** saldo considerar o que já foi pago.~~ Resolvido em `D-036`: o saldo **não muda**; o pago aparece em "A pagar". Contratado e Realizado de uma categoria `Talvez` com a linha desligada **aparecem e somam** (são fatos).
3. **Uso real:** se a regra de isentos sempre fora da base de custo serve a todos os fornecedores (alguns cobram a partir de uma idade diferente). Se não servir, o fator por linha pode passar a existir também para isentos.
