# Features: Convidados, Enxoval & Dia D (`features/convidados-enxoval-e-dia-d.md`)

> **Status:** **Parte Convidados aprovada pelo usuário em 2026-10-27** (`D-030`). **Parte Enxoval e Lista de Presentes (Bloco 4.1) aprovada pelo usuário em 2026-10-27** (`D-037`), no fim deste arquivo. **Parte Dossiê do Dia D (Bloco 4.2) aprovada pelo usuário em 2026-10-27** (`D-038`), também no fim deste arquivo.
>
> **Implementação (parte Convidados):** em 5 PRs (`D-071`). `F-CNV-01`, `02` e `04` estão implementadas (`D-072`): núcleo que nasce com a primeira pessoa, acompanhante a confirmar, status livre com motivo e histórico e o "Abrir WhatsApp"; `F-CNV-03` e `06` também (`D-073`): contadores derivados, pesos e limites de idade vazios até o casal definir, sugestão de faixa que nunca muda a pessoa e o contrato de contagem para o Orçamento; `F-CNV-05` e `07` também (`D-074`): convite por núcleo com a oferta de mover os rascunhos, busca (só no navegador), filtros na URL e a lente `Minha visão`; `F-CNV-08` também (`D-075`): exportação em Excel (padrão) ou CSV das pessoas que estão na tela, com fórmula neutralizada e o aviso de cuidado; o E2E e o fechamento seguem no PR 5.
>
> **Fontes:** `docs/product/scope.md` §6, `docs/design/experience.md` (Fluxo 5, objeto 9), `docs/product/jobs.md` (J2, J10), `D-029` e `D-030`.
>
> **Convenções:** `F-CNV-xx` identifica a feature. "Autor" é o usuário da sessão. Nenhum dado de convidado é pré-carregado. Dados de terceiros (telefone, e-mail, endereço) ficam só no banco do casal e **não vão para logs**.

---

## Visão da Subárea

**Jobs atendidos:** J2 (dimensionar a lista) e J10 (gerir a lista ao longo do planejamento).

**Quem usa e como:** no computador, para montar e conferir a lista juntos. No celular, para atualizar status e falar com a família em poucos toques.

**Modelo:** `Núcleo` (família ou grupo) → `Convidado` (pessoa). Os contadores são **derivados**, nunca digitados (`architecture.md`, "derivar, não duplicar").

---

## F-CNV-01 — Núcleos e Convidados

**Núcleo**

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto, obrigatório | Ex.: "Família Silva". Único por casamento, sem diferenciar maiúsculas |
| **Lado** | `Noivo` · `Noiva` · `Comum` | Obrigatório |
| **Endereço postal** | Logradouro, número, complemento, bairro, cidade, UF, CEP; todos opcionais | Para convite impresso. CEP validado só no formato (8 dígitos) |
| **Observação** | Texto livre | — |
| **Convite enviado** | Data e canal (F-CNV-05) | Opcional |

**Convidado**

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto | Obrigatório, exceto acompanhante a confirmar (F-CNV-02) |
| **Faixa** | `Adulto` · `Criança pagante` · `Criança isenta` | Padrão `Adulto` (F-CNV-03) |
| **Idade** | Inteiro, opcional | Só para crianças (F-CNV-03) |
| **Probabilidade** | `Certeza` · `Provável` · `Fase 2` | Padrão `Provável` |
| **Status** | `Rascunho` · `Convidado` · `Confirmado` · `Não irá` | Padrão `Rascunho` (F-CNV-04) |
| **Restrição alimentar** | Texto curto | Opcional. Alimenta o Dossiê (Bloco 4.2) |
| **Observação** | Texto livre | — |
| **Telefone / WhatsApp** | Telefone brasileiro | Normalizado para `wa.me/55…`; mostra o botão "Abrir WhatsApp" quando válido |
| **E-mail** | E-mail | Validado só no formato |

**Regras**
1. Um núcleo tem **um ou mais** convidados. Mover um convidado entre núcleos é permitido.
2. Excluir um núcleo com convidados pede confirmação e é **lógico** (recuperável, `architecture.md` §10).
3. **Cadastro rápido:** ao criar um núcleo, o formulário continua aberto para adicionar pessoas em sequência, sem voltar à lista.
4. O núcleo herda o lado nos novos convidados, que não têm lado próprio.
5. Qualquer um dos dois edita tudo. A autoria fica no histórico básico.

**Critérios de aceite**
- Criar o núcleo "Família Exemplo" com 4 pessoas leva um único fluxo contínuo.
- Dois núcleos com o mesmo nome são bloqueados com mensagem acionável.
- Telefone `(11) 91234-5678` gera `https://wa.me/5511912345678`. Telefone inválido mostra erro e não gera link.
- Excluir um núcleo o tira da lista e dos contadores, e ele pode ser restaurado.

---

## F-CNV-02 — Acompanhante (+1) a Confirmar

**O que é:** uma vaga de acompanhante cuja pessoa ainda não tem nome.

**Regras**
1. O acompanhante é um **convidado** ligado ao titular, com o nome opcional (`design`: aparece como "Acompanhante de {titular}").
2. Entra nos contadores como qualquer pessoa, com a faixa padrão `Adulto` e a probabilidade e o status próprios (padrão `Rascunho`).
3. Ao informar o nome, ele passa a ser um convidado comum, mantendo o vínculo ao titular como informação.
4. Excluir o titular pergunta o que fazer com o acompanhante (excluir junto ou manter).

**Critérios de aceite**
- Adicionar "+1" ao titular cria uma linha sem nome, contada em *Total Nominal*.
- Preencher o nome do acompanhante não altera os contadores.

---

## F-CNV-03 — Faixa e Idade da Criança

**O que é:** a faixa define se o convidado entra na base de custo por pessoa.

**Regras**
1. A **idade** é opcional e só vale para `Criança pagante` e `Criança isenta`.
2. O casal pode definir **limites de idade** nas configurações da lista: "isenta até N anos" e "pagante até M anos". **Começam vazios**, porque a regra de cobrança depende de cada fornecedor e o Altare não presume nenhuma.
3. Com os limites definidos e a idade informada, o sistema **sugere** a faixa ("pela idade: pagante") com um toque para aplicar. **Nunca altera a faixa sozinho.**
4. Alterar os limites **não muda** convidados já classificados.

**Critérios de aceite**
- Sem limites definidos, nenhuma sugestão aparece.
- Com "isenta até 5" e uma criança de 4 anos, aparece a sugestão `Criança isenta`; recusar mantém a faixa atual.
- Mudar o limite de 5 para 6 não altera nenhuma faixa já salva.

---

## F-CNV-04 — Probabilidade, Status do Convite e Motivo

**Status por pessoa**

| Status | Significado |
| :--- | :--- |
| `Rascunho` *(padrão)* | Na lista, sem convite |
| `Convidado` | Convite enviado, sem resposta |
| `Confirmado` | Presença confirmada |
| `Não irá` | Declinou |

**Regras**
1. O status é **por pessoa**, e o núcleo mostra o resumo ("3 de 4 confirmados").
2. `Não irá` aceita **motivo ou anotação opcional** (`D-030`). Não é obrigatório.
3. `Não irá` sai de *Total Nominal*, de *Estimado Ponderado* e de *Confirmados*, mas continua listado, com a contagem à parte.
4. Qualquer mudança de status é registrada com autor e data no histórico básico.
5. Mudar a **probabilidade** de quem já está `Confirmado` é permitido e não altera o status.

**Critérios de aceite**
- Marcar `Não irá` com motivo salva o motivo; sem motivo salva normalmente.
- Uma pessoa `Não irá` não conta nos três contadores e aparece em "Não irão: N".
- O resumo do núcleo muda ao alterar o status de qualquer membro, sem recarregar.

---

## F-CNV-05 — Convite Enviado por Núcleo (`D-030`)

| Campo | Tipo |
| :--- | :--- |
| **Data de envio** | Data |
| **Canal** | `WhatsApp` · `E-mail` · `Impresso` · `Pessoalmente` · `Outro` |

**Regras**
1. É **por núcleo**: enviar o convite a uma família é um ato único.
2. Ao registrar o envio, o sistema **oferece** mover os membros em `Rascunho` para `Convidado` (uma confirmação, nunca automático).
3. Editar ou limpar o envio **não reverte** os status das pessoas.
4. A lista mostra núcleos **sem convite enviado** como filtro.

**Critérios de aceite**
- Registrar o envio para "Família Exemplo" oferece mover 4 pessoas de `Rascunho` para `Convidado`; recusar mantém os status.
- O filtro "Convite não enviado" lista só os núcleos sem data.

---

## F-CNV-06 — Contadores e Pesos

**Contadores (derivados, sempre visíveis no topo)**

| Contador | Regra |
| :--- | :--- |
| **Total Nominal** | Todas as pessoas cadastradas, exceto `Não irá`. Inclui crianças isentas (é a contagem de cabeças) |
| **Confirmados** | Pessoas com status `Confirmado` |
| **Estimado Ponderado** | Base de custo por pessoa (abaixo) |
| **Não irão** | Pessoas com status `Não irá` (informativo) |

Cada contador mostra o **detalhamento por faixa** (adultos, crianças pagantes, crianças isentas), usado também pelo Dossiê.

**Estimado Ponderado**
1. **Exclui crianças isentas** (não entram na base de custo por pessoa) e quem está `Não irá`.
2. Quem está `Confirmado` conta **100%**, qualquer que seja a probabilidade.
3. Os demais contam pelo **peso da probabilidade**: `Certeza`, `Provável` e `Fase 2`, três percentuais editáveis pelo casal.
4. Os pesos **começam vazios**. Enquanto vazios, o contador mostra "defina os pesos" e o Orçamento (Bloco 2.1) não recebe valor, em vez de usar um número presumido.
5. O valor é exibido arredondado ao inteiro. No orçamento, a contagem fracionária é **arredondada para cima** nos custos por pessoa (`D-032`, `F-ORC-03`).
6. O cálculo vive **só no backend** (`stack.md` §5.1).

**Critérios de aceite**
- Com pesos 100/70/30, 2 `Certeza` + 2 `Provável` + 1 `Fase 2` (todos adultos, nenhum confirmado) dão 2 + 1,4 + 0,3 = 3,7, exibido como 4.
- Uma criança isenta aumenta o *Total Nominal* e não altera o *Estimado Ponderado*.
- Sem pesos definidos, aparece "defina os pesos" no lugar do número.
- Marcar alguém `Confirmado` faz a pessoa contar 100% imediatamente.

---

## F-CNV-07 — Visões, Busca e Filtros

| Recurso | Comportamento |
| :--- | :--- |
| **Agrupamento** | Por núcleo (padrão), com resumo por núcleo |
| **Busca** | Por nome do convidado ou do núcleo, sem diferenciar maiúsculas nem acentos |
| **Filtros** | Lado, faixa, probabilidade, status, convite não enviado, com restrição alimentar. Estado na **URL** (`design-system.md` §10) |
| **Lente `Casal`** | Mostra todos |
| **Lente `Minha visão`** | Mostra por padrão **o meu lado mais `Comum`** (o outro lado fica um toque atrás) |
| **Desktop** | Tabela agrupada com painel lateral do núcleo |
| **Mobile** | Cartões por núcleo; status em um toque; botão "Abrir WhatsApp" por pessoa |

**Critérios de aceite**
- Buscar "silva" encontra "Família Silva" e "Maria da Silva".
- Aplicar filtros altera a URL, e o botão voltar do navegador os desfaz.
- Com o Noivo logado em `Minha visão`, aparecem núcleos do lado `Noivo` e `Comum`.
- Em 320 px, nenhuma linha exige rolagem horizontal.

---

## F-CNV-08 — Exportação da Lista (`D-030`)

**O que é:** baixar a lista para usar fora do Altare (por exemplo, enviar a uma gráfica ou conferir em planilha).

**Formatos:** **Excel (`.xlsx`) como padrão** e **CSV como opção**.

**Colunas (fixas):** Núcleo · Lado · Nome · Faixa · Idade · Probabilidade · Status · Restrição alimentar · Observação · Telefone · E-mail · Endereço do núcleo · Convite enviado (data) · Canal · Motivo (`Não irá`).

**Regras**
1. Uma linha por pessoa. O endereço e o convite do núcleo se repetem em cada linha dele.
2. Respeita os **filtros** ativos: exporta o que está na tela, com um aviso do tamanho ("142 pessoas").
3. **CSV** em UTF-8 com BOM e separador `;`, para abrir corretamente no Excel em português. **Excel** com cabeçalho fixo e larguras adequadas.
4. O download é gerado no backend e protegido por sessão.

**Critérios de aceite**
- O `.xlsx` abre no Excel sem aviso de arquivo corrompido, com acentos corretos.
- O CSV abre no Excel pt-BR com cada campo em sua coluna e sem caracteres quebrados.
- Exportar com o filtro "Lado Noiva" traz só essas pessoas, e o aviso mostra a contagem correta.

---

## Fora desta subárea (v1)
- **Importar lista de planilha:** fica para depois (já era v1.1+ em `scope.md` §6).
- **Mapa de mesas:** v1.1+.
- **Site público de RSVP e confirmação pelo convidado:** fora do produto.
- **Envio automático de convites:** fora do produto.
- **Enxoval e Lista de Presentes (Bloco 4.1):** detalhado na parte **Enxoval** deste arquivo (`D-037`). **Dossiê (Bloco 4.2):** detalhado na parte **Dossiê** deste arquivo (`D-038`).

## Pontos a validar nos blocos seguintes
1. ~~Arredondamento do custo por pessoa~~: **resolvido em `D-032`** (para cima).
2. Limites de idade de criança por fornecedor (podem diferir entre buffet e espaço): o fator da criança pagante por linha (`F-ORC-04`) cobre o valor cobrado; a idade de corte por fornecedor segue como ponto a validar em uso real.

---

# Parte Enxoval e Lista de Presentes (Bloco 4.1, `D-037`)

> **Status desta parte:** **Aprovada pelo usuário em 2026-10-27** (`D-037`).
>
> **Onde aparece na tela:** subárea **Enxoval & Lista de Presentes** da área **Convidados, Enxoval & Dia D** (`experience.md` §3.1, item 7).
>
> **Fontes:** `docs/product/scope.md` §6, `docs/design/experience.md` (Fluxo 6, objeto 10), `docs/product/jobs.md` (J10), `D-004`, `D-006`, `D-030`, `D-037`.
>
> **Convenções:** `F-ENX-xx` identifica a feature. Valores em centavos, aceitando `R$ 1.200,00` na edição. Todo número do exemplo é **fictício**. Qualquer um dos dois cria e edita, e a autoria fica no histórico básico. **A lista de presentes é interna** (`D-004`): sem site público, sem vitrine e sem checkout. Dados de convidados citados aqui vêm da lista pela interface pública do módulo de convidados, sem cópia (só o nome fica guardado, F-ENX-03).

## Visão da Parte

**Papel duplo (`D-006`):**
1. **Controle da casa nova:** o que o casal precisa, o que já ganhou e o que já comprou.
2. **Rascunho exportável:** a base para cadastrar a lista num site externo ou enviar a convidados.

| Objeto | O que é | Persistido? |
| :--- | :--- | :--- |
| **Grupo** | Cômodo ou categoria (Cozinha, Quarto…) | Sim |
| **Item** | Algo por unidade, com quantidade desejada | Sim |
| **Cota** | Um valor-alvo em dinheiro, com contribuições (ex.: lua de mel) | Sim |
| **Recebimento** | Um presente ou uma compra, registrados em um item | Sim (fato) |
| **Contribuição** | Um valor dado a uma cota | Sim (fato) |
| **Status**, quantidades atendidas e totais | O estado do item e quanto falta | **Derivados** |

---

## F-ENX-01 — Grupos (Cômodos e Categorias)

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto, obrigatório | Único, sem diferenciar maiúsculas |
| **Ordem** | Posição | Reordenável |
| **Arquivado** | Sim/não | Grupo arquivado some das telas ativas, com seus itens, e pode ser restaurado |

**Regras**
1. O sistema **sugere uma lista inicial editável**, como em `F-PLN-02`: Cozinha, Quarto, Sala, Banheiro, Área de serviço, Eletros e eletrônicos e Lua de mel. O casal renomeia, acrescenta, reordena e arquiva. Nenhuma é obrigatória.
2. Grupo com itens não pode ser **excluído**: só arquivado.
3. Qualquer um cria e edita.

**Critérios de aceite**
- Um casamento novo mostra as sugestões iniciais, todas editáveis.
- Dois grupos com o mesmo nome são bloqueados.
- Arquivar um grupo com itens os tira das telas ativas, e restaurar traz tudo de volta.

---

## F-ENX-02 — Item e Cota

**Item (por unidade)**

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto, obrigatório | Ex.: "Jogo de pratos" |
| **Grupo** | Um grupo, obrigatório | — |
| **Prioridade** | `Essencial` · `Desejável` · `Se sobrar` | Padrão `Desejável` |
| **Quantidade desejada** | Inteiro ≥ 1 | Padrão 1 |
| **Valor unitário estimado** | Dinheiro, opcional | Vazio é "sem valor", nunca zero |
| **Link** | URL, opcional | Mostra o domínio. **Sem leitura automática da página** (sem *scraping*) |
| **Loja** | Texto curto, opcional | — |
| **Imagem** | Arquivo, opcional | JPG, PNG ou WebP via `FileStorage`, com validação de tipo real e tamanho. No celular, abre a câmera ou a galeria. Aparece como miniatura |
| **Nota** | Texto, opcional | — |
| **Destino** | `Pedir na lista de presentes` · `Comprar nós mesmos` | Padrão `Pedir na lista de presentes` |
| **Na lista** | Sim/não | Só com destino `Pedir`. Indica que o item já foi cadastrado no site externo ou enviado aos convidados. Padrão não |

**Cota (valor em dinheiro)**

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto, obrigatório | Ex.: "Cota de passeio" |
| **Grupo** | Um grupo, obrigatório | — |
| **Prioridade** | Como no item | — |
| **Valor-alvo** | Dinheiro, obrigatório | Maior que zero |
| **Link, nota e imagem** | Como no item | — |
| **Destino** | Sempre `Pedir na lista de presentes` | Não editável |
| **Na lista** | Sim/não | Como no item |

**Regras**
1. Item e Cota convivem na mesma lista, no mesmo grupo, com o tipo visível.
2. **Excluir** é lógico e recuperável. O item leva junto seus recebimentos (ou a cota, suas contribuições), e a restauração os traz de volta.
3. Alterar a quantidade desejada para **menos** do que já foi atendido é permitido: o excedente aparece como "N a mais".
4. Qualquer um cria e edita.

**Critérios de aceite**
- Criar um item sem nome ou sem grupo é bloqueado com mensagem acionável.
- Um valor unitário vazio mostra "sem valor", e o total do item não conta zero.
- Colar uma URL inválida mostra erro acionável.
- Um arquivo de imagem com extensão trocada é recusado.
- Uma cota sem valor-alvo é bloqueada.
- A cota não oferece a escolha de destino.
- No celular, adicionar uma foto da galeria leva poucos toques.

---

## F-ENX-03 — Recebimentos: Presentes e Compras (`D-037`)

**O que é:** o registro de cada vez que o casal ganha ou compra algo. É daqui que vêm as quantidades atendidas e o status.

**Recebimento de item**

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Origem** | `Presente` · `Compra nossa` | Obrigatória |
| **Quantidade** | Inteiro ≥ 1 | Obrigatória |
| **Data** | Data | Padrão hoje. Não pode ser futura |
| **Valor total do registro** | Dinheiro, opcional | Presente: o valor aproximado. Compra: o que foi pago |
| **Quem presenteou** | Convidado ou núcleo da lista **ou** texto livre | Só com origem `Presente`. Opcional |
| **Nota** | Texto curto, opcional | — |

**Contribuição de cota**

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Valor** | Dinheiro, obrigatório | Maior que zero |
| **Data** | Data | Padrão hoje. Não pode ser futura |
| **Quem deu** | Convidado ou núcleo da lista **ou** texto livre | Opcional |
| **Nota** | Texto curto, opcional | — |

**Regras**
1. **Ações rápidas** no item, para poucos toques no celular: "Registrar presente" e "Registrar compra" abrem o formulário com data de hoje e a **quantidade que falta** já preenchida.
2. **Quem presenteou:** ao escolher alguém da lista de convidados, o Altare **guarda o nome** (como estava na hora) e o vínculo. Se o convidado for excluído depois, o nome continua no registro, sem o vínculo. O Altare **não altera** nada na lista de convidados.
3. Registros podem ser **editados e removidos** por qualquer um, de forma lógica e recuperável, e a alteração fica no histórico básico.
4. Origem `Compra nossa` é permitida mesmo num item com destino `Pedir`, e `Presente` num item com destino `Comprar nós mesmos` (um convidado pode dar o que o casal pretendia comprar).
5. Registrar a **quantidade além do desejado** é permitido e mostra "N a mais".
6. **Sem vínculo com o Orçamento** (F-ENX-04, regra 5).

**Critérios de aceite**
- Registrar um presente de 4 unidades num item de 12 mostra "4 de 12" e o status `Em andamento`.
- "Registrar compra" abre com a quantidade restante já preenchida.
- Escolher um convidado em "Quem presenteou" guarda o nome, e excluir o convidado depois não apaga o nome do registro.
- Uma data de amanhã é bloqueada.
- Remover um recebimento reduz a quantidade atendida e atualiza o status.
- Uma contribuição de R$ 300,00 numa cota de R$ 1.000,00 mostra "R$ 300,00 de R$ 1.000,00 (30%)".

---

## F-ENX-04 — Status Derivado e Totais (`D-037`)

**Status do item (derivado, nunca editado):**

| Condição | Status |
| :--- | :--- |
| Nada atendido e **não** está na lista | `Precisamos` |
| Nada atendido, destino `Pedir` e **na lista** | `Na lista de presentes` |
| Atendido, mas **menos** que o desejado | `Em andamento` (ex.: "4 de 12") |
| Atendido por completo, **todos** os recebimentos são `Presente` | `Já ganhamos` |
| Atendido por completo, **todos** são `Compra nossa` | `Já compramos` |
| Atendido por completo, com **os dois** tipos | `Completo` (mostra "ganhos X, comprados Y") |

**Status da cota (derivado):** sem contribuições, `Precisamos` ou `Na lista de presentes`, como acima. Com contribuições abaixo do alvo, `Em andamento` ("R$ 300,00 de R$ 1.000,00"). No alvo ou acima, `Já ganhamos`.

**Totais da subárea (derivados, no cabeçalho)**

| Total | Cálculo |
| :--- | :--- |
| **Estimado da lista** | Σ (quantidade desejada × valor unitário) dos itens + Σ valor-alvo das cotas. Itens sem valor ficam fora e aparecem como "N itens sem valor" |
| **Ganho (em valor)** | Σ do valor registrado nos recebimentos `Presente` + Σ das contribuições. Registros sem valor ficam fora do total e são sinalizados |
| **Gasto do casal** | Σ do valor registrado nas `Compra nossa`. Registros sem valor ficam fora e são sinalizados |
| **Falta conseguir** | Σ (quantidade que falta × valor unitário) dos itens + Σ do que falta nas cotas. Itens sem valor ficam fora |
| **Progresso** | "N de M itens completos", contando itens e cotas |

**Regras**
1. Quantidades e status são **calculados no backend**, derivados na leitura (`architecture.md` §3).
2. "—" nunca é lido como zero. Totais incompletos dizem o motivo ("2 itens sem valor").
3. Cor nunca é o único sinal de status: ícone e texto sempre (`design-system.md` §3.3).
4. Excedentes ("a mais") **não** reduzem o "falta conseguir" abaixo de zero.
5. **Sem vínculo com o Orçamento do casamento** (`D-037`): o enxoval é a casa nova, separada das categorias do casamento. Os totais da subárea **não alimentam** o Orçamento nem os cenários. O que o casal paga a um fornecedor do casamento sem passar por proposta continua no **Contrato direto** (`F-CTR-01`).

**Critérios de aceite** *(valores fictícios)*
- Um item de 12 unidades a R$ 50,00 com 4 presentes registradas mostra `Em andamento`, "4 de 12" e "falta conseguir R$ 400,00".
- Com os 12 recebidos, todos como presente, o status é `Já ganhamos`. Com 8 de presente e 4 de compra, `Completo` com "ganhos 8, comprados 4".
- Um item sem valor unitário não entra no estimado nem no "falta", e o cabeçalho indica "1 item sem valor".
- Uma cota de R$ 1.000,00 com R$ 1.200,00 recebidos mostra `Já ganhamos` e "R$ 200,00 a mais", e o "falta conseguir" é R$ 0,00.
- Marcar um item `Pedir` como "Na lista" o leva de `Precisamos` a `Na lista de presentes`.
- Nenhum valor desta subárea aparece no Orçamento Ativo.

---

## F-ENX-05 — Exportação para Site Externo (`D-006`, `D-030`, `D-037`)

**O que é:** baixar os itens para cadastrar rapidamente em uma plataforma externa de presentes.

**Formatos:** **Excel (`.xlsx`) como padrão** e **CSV como opção**, como em `F-CNV-08`.

**Colunas (fixas):** Grupo · Tipo (`Item` ou `Cota`) · Nome · Quantidade desejada · Quantidade que falta · Valor unitário ou valor-alvo · Valor que falta (cotas) · Link · Loja · Nota.

**Regras**
1. Exporta o que está **na tela**, respeitando os filtros, com aviso do tamanho ("23 itens"). A visão **"Para a lista"** (destino `Pedir`, ainda não completos) é um atalho pronto de filtro.
2. **Não inclui** dados de convidados, "quem presenteou" nem recebimentos.
3. Valores em número, com formato monetário no Excel e **vírgula decimal** no CSV. **CSV** em UTF-8 com BOM e separador `;`. Valor vazio fica em branco, nunca zero.
4. **Depois de baixar**, o Altare **oferece** (desmarcado por padrão) marcar como "Na lista" os itens exportados com destino `Pedir` que ainda não estavam, mostrando a lista do que mudaria. O casal confirma ou ignora.
5. O download é gerado no backend e protegido por sessão.

**Critérios de aceite**
- O `.xlsx` abre no Excel sem aviso de arquivo corrompido, com acentos corretos.
- O CSV abre no Excel pt-BR com cada campo em sua coluna e sem caracteres quebrados.
- Exportar a visão "Para a lista" traz só itens `Pedir` ainda não completos, e o aviso mostra a contagem.
- A oferta de marcar "Na lista" vem desmarcada e lista os itens afetados.
- O arquivo não contém nenhum nome de convidado.

---

## F-ENX-06 — Lista Formatada para os Convidados (`D-006`, `D-037`)

**O que é:** um texto limpo, pronto para **copiar e colar** (por exemplo, no WhatsApp) e enviar diretamente aos convidados.

| Elemento | Comportamento |
| :--- | :--- |
| **Conteúdo** | Itens e cotas com destino `Pedir na lista de presentes` e ainda **não completos**, agrupados por **grupo**, na ordem dos grupos, depois por prioridade (`Essencial` primeiro) e por nome |
| **Mensagem inicial** | Campo de texto **opcional**, vazio por padrão: o Altare não escreve a mensagem do casal |
| **Opções** | **Mostrar valores** (padrão: desligado) e **Mostrar links** (padrão: ligado). Para itens com mais de uma unidade, mostra "faltam N" |
| **Pré-visualização** | Em tela, somente leitura. Para mudar o conteúdo, o casal edita o item |
| **Saída** | **Copiar** para a área de transferência e **baixar como arquivo de texto** (`.txt`, UTF-8) |
| **Formato** | Texto simples. Grupos em destaque no estilo do WhatsApp (`*Grupo*`) e itens em lista com marcadores |

**Regras**
1. **Nunca inclui** "quem presenteou", recebimentos, notas internas, prioridade em texto nem o valor estimado quando "Mostrar valores" estiver desligado.
2. Cotas aparecem como "Cota: Nome" e, com valores ligados, "faltam R$ X".
3. A lista é uma **visão sobre os mesmos dados**, sem cópia armazenada. Gerar de novo reflete o estado atual.
4. Itens `Completo`, `Já ganhamos` e `Já compramos` **não** entram.
5. **PDF e impressão** ficam fora desta área (`D-037`): `design-system.md` §13 adia a impressão até o Dossiê (Bloco 4.2).

**Critérios de aceite**
- Com valores desligados, o texto não contém nenhum "R$".
- Um item `Comprar nós mesmos` não aparece na lista.
- Um item de 12 unidades com 4 atendidas mostra "faltam 8".
- Copiar coloca o texto na área de transferência, e baixar gera um `.txt` com acentos corretos.
- O texto não contém nenhum nome de convidado.

---

## F-ENX-07 — Visões, Filtros e Busca

| Recurso | Comportamento |
| :--- | :--- |
| **Lista por grupo** | Agrupada por grupo, na ordem dos grupos, com o total de cada grupo (estimado e "falta") |
| **Cada linha** | Miniatura, nome e tipo, prioridade, "N de M" ou "R$ X de R$ Y", status, destino, "Na lista" e valor estimado |
| **Filtros** | Grupo, status, destino, prioridade, tipo (`Item` ou `Cota`), "sem valor" e texto livre. Na **URL** (`D-021`) |
| **Atalho "Para a lista"** | Destino `Pedir`, ainda não completos (base da exportação, F-ENX-05) |
| **Lente** | **Não se aplica**: a lista é do casal e não tem responsável |
| **Desktop** | Tabela com painel lateral de detalhe e histórico dos recebimentos |
| **Mobile** | Cartões; detalhe em folha inferior; ações "Registrar presente" e "Registrar compra" em 1 toque |

**Regras**
1. Os itens e cotas são encontrados pela **busca global** (`F-CTT-10`): nome, grupo e loja.
2. Estado vazio: "Nenhum item ainda", com as ações "Novo item" e "Nova cota".
3. Tudo funciona em 320 px sem rolagem horizontal.

**Critérios de aceite**
- Filtrar por destino `Comprar nós mesmos` mostra só esses itens, e o botão voltar do navegador desfaz o filtro.
- O total de um grupo soma só os itens com valor e indica quantos ficaram de fora.
- Buscar por parte do nome de uma loja leva ao item.
- Em 320 px, nenhum cartão exige rolagem horizontal.

---

## Fora desta parte (v1)
- **Site público dos noivos, vitrine e checkout para convidados:** fora do produto (`D-004`).
- **Mensagens de agradecimento por IA:** v1.1+ (`scope.md` §6).
- **Marcar "agradecimento enviado" por presente e a visão "quem deu o quê":** não entram (`D-037`).
- **Importar lista de planilha ou de sites externos:** v1.1+.
- **Leitura automática de preço e foto a partir do link:** fora da v1 (sem *scraping*).
- **Pagamento ou controle do gasto no Orçamento do casamento:** não entra (`D-037`).
- **Lista formatada em PDF ou página imprimível:** não entra (`D-037`).
- **Responsável por item e lente por perfil:** não solicitados.

## Pontos a validar em uso
1. O status `Completo` para itens atendidos por presente e compra: se o rótulo incomodar, trocar (reversível, sem mudar a regra).
2. Se o casal passar a querer **controlar o gasto da casa nova** junto ao orçamento do casamento, revisitar o vínculo com o Orçamento, hoje separado.
3. Padrão de "Mostrar valores" desligado na lista formatada: ajustar se for o contrário do hábito do casal.
4. Se faltar um jeito de **agradecer** quem presenteou, retomar o "agradecimento enviado".

---

# Parte Dossiê do Dia D (Bloco 4.2, `D-038`)

> **Status desta parte:** **Aprovada pelo usuário em 2026-10-27** (`D-038`).
>
> **Onde aparece na tela:** subárea **Dossiê do Dia D** da área **Convidados, Enxoval & Dia D** (`experience.md` §3.1, item 7). A Visão Geral e o "Registrar Rápido" estão em `features/centro-de-comando.md`.
>
> **Fontes:** `docs/product/scope.md` §7, `docs/design/experience.md` (Fluxo 7, objeto 8), `docs/product/jobs.md` (J11), `D-001`, `D-028`, `D-036`, `D-038`.
>
> **Convenções:** `F-DOS-xx` identifica a feature. O Dossiê é uma **visão viva consolidada**, e não um cadastro paralelo: tudo o que já existe nas outras áreas é **lido, nunca digitado de novo**. Só são dados novos o **Local do evento**, os **horários-chave**, o **checklist de itens físicos** e as **versões entregues**. Todo número do exemplo é **fictício**. Qualquer um dos dois edita, e a autoria fica no histórico básico.

## Visão da Parte

**Jobs atendidos:** J11 (entregar ao(à) cerimonialista do dia um documento completo, sem montá-lo do zero na véspera), objetivo central de `D-001`.

| Seção | Origem | Dado novo? |
| :--- | :--- | :--- |
| Quadro do evento | Definições Base, Espaço contratado e convidados | **Local** e **horários-chave** |
| Fornecedores contratados | Contratos (`F-CTR-01`, `F-CTR-03`) | Não |
| Pagamentos | Parcelas (`F-CTR-04`) | Não |
| Convidados | Lista de convidados (`F-CNV-06`) | Não |
| Itens físicos | Checklist do casal | **Sim** |
| Versões entregues | Cópia datada do Dossiê | **Sim** |

---

## F-DOS-01 — Estrutura, Visualização Limpa e Pendências

**Regras**
1. As seções aparecem nesta ordem: **Quadro do evento**, **Fornecedores contratados**, **Pagamentos**, **Convidados**, **Itens físicos**.
2. **Visualização limpa:** um modo de leitura sem menus, botões de edição nem avisos, pensado para apresentar na reunião e imprimir. O modo de edição leva às áreas de origem.
3. **Pendências do Dossiê** (só em tela, **não saem na impressão**): uma lista no topo do que ainda falta, derivada:
   - data do casamento ainda não `Definida`;
   - Local do evento vazio;
   - contrato sem responsável no dia (nome ou WhatsApp), sem itens contratados, ou `Assinado` sem PDF assinado;
   - contrato `Aguardando assinatura`;
   - categorias `Entra (Essencial)` **sem contrato** ("Fotografia ainda não tem contrato");
   - item físico `A providenciar`.
4. As pendências **não bloqueiam** nada: o Dossiê pode ser aberto, impresso e entregue incompleto.
5. O Dossiê **só lê** as outras áreas: corrigir um dado leva à tela de origem.

**Critérios de aceite**
- Um casamento sem contratos mostra o Dossiê com as seções vazias e as pendências, sem erro.
- A visualização limpa não mostra botões de edição nem a lista de pendências.
- Corrigir o responsável no dia no contrato atualiza o Dossiê sem recarregar.

---

## F-DOS-02 — Quadro do Evento

| Campo | Origem | Regras |
| :--- | :--- | :--- |
| **Data** | `F-PLN-01` | Exata `Definida`: data completa. Senão, o nível conhecido (mês e ano, ou época) com "data a definir" |
| **Cidade** e **tipo de cerimônia** | `F-PLN-01` | Só os que estiverem `Definidos` |
| **Espaço** | Contrato da categoria Espaço | Fornecedor e responsável no dia. Sem contrato: "Espaço ainda não contratado" |
| **Local do evento** | **Dado novo** | Texto livre, opcional: endereço, ponto de referência, estacionamento, como o casal quiser descrever |
| **Horários-chave** | **Dado novo** | Lista curta (**até 12 entradas**): **horário** (`HH:MM`) e **descrição**. Ex.: "16:00 — Cerimônia". Ordenada por horário |
| **Convidados** | `F-CNV-06` | Confirmados por faixa e quantos seguem sem resposta (F-DOS-05) |

**Regras**
1. **Horários-chave não são o roteiro minuto a minuto** (v1.1+, `scope.md` §7): não têm duração, responsável nem sequência de montagem.
2. Editar o Local ou os horários é feito no próprio Dossiê, no modo de edição.
3. Horário e descrição são obrigatórios em cada entrada. Dois horários iguais são permitidos.
4. O Dossiê **não presume** nenhum horário: a lista começa vazia.

**Critérios de aceite**
- Com data exata `Definida`, o quadro mostra a data completa. Sem ela, mostra "data a definir" com o nível conhecido.
- Adicionar "16:00 — Cerimônia" e "14:00 — Chegada da equipe" mostra os dois em ordem de horário.
- Uma décima terceira entrada é recusada com a orientação de que o roteiro minuto a minuto é futuro.
- Sem Espaço contratado, o quadro diz "Espaço ainda não contratado".

---

## F-DOS-03 — Fornecedores Contratados

**O que é:** uma ficha por **contrato** `Aguardando assinatura` ou `Assinado` (nunca `Cancelado`), incluindo contratos diretos (`F-CTR-01`).

| Campo da ficha | Origem |
| :--- | :--- |
| **Categoria** e **fornecedor** (ou favorecido) | Contrato |
| **Responsável no dia** | Nome, função e WhatsApp (`F-CTR-03`) |
| **Itens contratados** | Lista do contrato |
| **Combinados operacionais críticos** | Lista do contrato |
| **PDF do contrato** | Arquivo do tipo `Contrato assinado` (`F-CTR-02`) |
| **Estado** | `Aguardando assinatura` com ícone e texto, quando for o caso |
| **Valor fechado** | Só quando a opção "Mostrar valor dos contratos" estiver ligada |

**Regras**
1. Ordem: a das categorias no Mapa de Escopo, depois o título do contrato.
2. **"Mostrar valor dos contratos"** vem **desligada** por padrão: quem assume a operação do evento não precisa do valor total. Os **saldos a pagar** (F-DOS-04) aparecem sempre.
3. Na tela, o WhatsApp é um link `wa.me`. Na **impressão**, é o número por extenso, porque o link se perde no papel.
4. Contrato sem PDF assinado mostra "sem PDF assinado". Na impressão, o PDF aparece como "Contrato assinado: arquivo no Altare".
5. Contrato sem responsável no dia mostra "responsável no dia a definir".

**Critérios de aceite**
- Um contrato `Cancelado` não aparece.
- Um contrato `Aguardando assinatura` aparece com a sinalização em ícone e texto.
- Com a opção de valores desligada, nenhum valor fechado aparece nas fichas.
- O WhatsApp `(11) 91234-5678` é link na tela e aparece como número na impressão.

---

## F-DOS-04 — Pagamentos

**Duas partes:**

| Parte | Conteúdo |
| :--- | :--- |
| **A pagar no dia do evento** | Parcelas `Pendente` com vencimento **"No dia do evento"** ou na data do casamento: fornecedor, descrição, valor previsto, meio, responsável e o **total** |
| **Demais pendentes até o evento** | **Resumo por fornecedor**: quantas parcelas pendentes e a soma, com `Atrasada` sinalizada. Sem listar cada parcela |

**Regras**
1. Parcelas `Pago` não aparecem.
2. Os **valores sempre aparecem** nesta seção: é o que o(a) cerimonialista precisa saber sobre o que será pago no dia.
3. Sem a data do casamento `Definida`, "No dia do evento" aparece como "no dia do evento (data a definir)".
4. A seção é uma **visão sobre as parcelas**, sem cópia (`F-CTR-04`).

**Critérios de aceite** *(valores fictícios)*
- Uma parcela "Quitação" de R$ 2.000,00 com vencimento "No dia do evento" aparece em "A pagar no dia do evento", e o total soma R$ 2.000,00.
- Duas parcelas pendentes de R$ 833,33 de outro fornecedor aparecem no resumo como "2 parcelas, R$ 1.666,66".
- Uma parcela já `Pago` não aparece.

---

## F-DOS-05 — Convidados

**Conteúdo**
- **Confirmados** por faixa: adultos, crianças pagantes e crianças isentas (`F-CNV-06`).
- **Sem resposta**: convidados `Convidado` que ainda não confirmaram. `Não irá` aparece só como contagem.
- **Restrições alimentares:** lista de nome e restrição dos convidados com restrição registrada e que **não** estão `Não irá`, com o status de cada um.

**Regras**
1. As contagens usam as mesmas regras de `F-CNV-06`. Não há cálculo novo.
2. A opção **"Incluir restrições alimentares"** vem ligada. Desligada, a lista some do Dossiê e da impressão.
3. **Dados de terceiros:** o Dossiê contém nomes de convidados. A tela e a impressão **não** mostram telefone, e-mail nem endereço dos convidados.

**Critérios de aceite**
- Os números do Dossiê batem com os contadores da lista de convidados no mesmo instante.
- Um convidado `Não irá` com restrição **não** aparece na lista de restrições.
- Nenhum telefone ou e-mail de convidado aparece.

---

## F-DOS-06 — Itens Físicos que o Casal Leva (`D-038`)

**O que é:** o checklist do que o casal levará ao local (alianças, bebidas compradas à parte, papelaria, lembrancinhas). Está no Fluxo 7 da experiência e entra agora no escopo.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto, obrigatório | — |
| **Quantidade** | Inteiro ≥ 1, opcional | — |
| **Responsável** | `Noivo` · `Noiva` · `Ambos` | Padrão `Ambos` |
| **Estado** | `A providenciar` · `Pronto` | Padrão `A providenciar` |
| **Nota** | Texto curto, opcional | — |

**Regras**
1. A lista **começa vazia**: o Altare não sugere itens.
2. Reordenável. Qualquer um adiciona, edita e remove. Excluir é lógico e recuperável.
3. Mostra "N de M prontos". O estado tem ícone e texto, e na impressão usa uma caixa de seleção (☐ ou ☑).
4. Itens `A providenciar` entram nas **pendências** do Dossiê (F-DOS-01).
5. A lente **não** filtra o Dossiê. O responsável aparece como rótulo.

**Critérios de aceite**
- Criar um item sem nome é bloqueado com mensagem acionável.
- Marcar um item como `Pronto` atualiza o "N de M prontos" e a impressão mostra ☑.
- Um casamento novo mostra a lista vazia, sem itens sugeridos.

---

## F-DOS-07 — Versões Entregues (`D-038`)

**O que é:** guardar uma **cópia datada** do Dossiê no momento em que ele é entregue, e saber depois **o que mudou** desde então.

**Registrar versão entregue**

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Data e hora** | Automática | — |
| **Autor** | Perfil da sessão | — |
| **Nota** | Texto curto, opcional | Ex.: "entregue na reunião" |
| **Conteúdo** | Cópia **congelada** de todas as seções e das opções ligadas no momento | Imutável |

**Regras**
1. **Imutável:** uma versão não é editada nem excluída. É o registro histórico do que foi entregue.
2. As versões ficam numa lista, da mais recente para a mais antiga. Abrir uma mostra o Dossiê **como estava**, em modo somente leitura, com a mesma impressão.
3. **"O que mudou desde a última entrega"**, na tela do Dossiê: uma lista em linguagem direta, por seção, com o **antes → depois** nos campos simples e **adicionado** ou **removido** nas listas. Exemplos: "Fotografia: responsável no dia mudou de Ana para Beto", "Buffet: novo item contratado", "Confirmados: de 98 para 104", "Itens físicos: 1 item a mais".
4. Sem versão registrada, a seção diz "Nenhuma versão entregue ainda".
5. Arquivos referenciados (PDF do contrato) **não são copiados**: se forem removidos depois, a versão antiga mostra "arquivo removido".
6. A exportação dos dados do casal (`F-CCD-10`) inclui as versões entregues.

**Critérios de aceite**
- Registrar uma versão guarda o Dossiê como estava, e mudar o Local depois **não** altera a versão guardada.
- Depois de mudar o responsável no dia de um contrato, "o que mudou" mostra o antes e o depois.
- Uma versão não oferece editar nem excluir.
- Abrir uma versão antiga mostra os valores da época.

---

## F-DOS-08 — Impressão e PDF (`D-038`)

**O que é:** a saída do Dossiê para a reunião, **pelo navegador** ("Imprimir ou salvar em PDF"), com estilos próprios de impressão. **Não há PDF gerado no servidor** (sem dependência nova).

**Regras**
1. **A4 em retrato**, com margens confortáveis, texto escuro sobre fundo branco e **tokens de papel** (`design-system.md` §13, gatilho do Bloco 4.2).
2. **Cabeçalho** com o nome "Dossiê do Dia D", o nome do casamento, a data do casamento (ou "data a definir") e a data de geração. **Rodapé** com a numeração de páginas.
3. **Sem controles de interface:** menus, botões, a lista de pendências e a navegação não saem.
4. **Cada ficha de fornecedor não se parte** entre páginas, e cada seção começa em página nova quando houver espaço.
5. Links viram **texto legível** (o WhatsApp, por extenso) e a cor **nunca é o único sinal**: estados têm ícone ou texto.
6. As opções (**Mostrar valor dos contratos**, **Incluir restrições alimentares**) valem para a impressão.
7. A impressão usa as **fontes e a paleta da marca** adaptadas ao papel (`identity.md`).

**Critérios de aceite**
- A prévia de impressão mostra o cabeçalho, o rodapé e nenhum botão.
- Nenhuma ficha de fornecedor é cortada entre duas páginas.
- Com o valor dos contratos desligado, a impressão não traz valores fechados.
- Salvar em PDF mantém acentos e a fonte da marca.

---

## Fora desta parte (v1)
- **Roteiro minuto a minuto do Dia D** e **acesso de leitura ao sistema pelo(a) cerimonialista:** v1.1+ (`scope.md` §7).
- **PDF gerado no servidor** com layout garantido: não entra (`D-038`). A impressão é pelo navegador.
- **Observações gerais livres no topo do Dossiê:** não entram (`D-038`). Os combinados críticos de cada fornecedor cobrem o caso.
- **Envio do Dossiê por e-mail ou WhatsApp:** fora da v1. O casal imprime ou salva em PDF e envia por fora.
- **Plataforma multi-casamentos para assessorias:** fora do produto.
- **Assinatura ou confirmação de recebimento pelo(a) cerimonialista:** fora do produto.

## Pontos a validar em uso
1. O limite de **12 horários-chave**: se o casal precisar de mais, o caminho natural é o roteiro minuto a minuto (v1.1+), não ampliar a lista.
2. O layout de impressão em A4: validar em uma impressão real e em PDF antes de entregar a um(a) cerimonialista.
3. Se o(a) cerimonialista pedir o **valor total dos contratos**, ligar a opção; a decisão fica com o casal.
4. A comparação "o que mudou" em campos de texto longos: se ficar verbosa, resumir.
