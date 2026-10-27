# Features: Possibilidades & Decisões (`features/possibilidades-e-decisoes.md`)

> **Status:** **Aprovado pelo usuário em 2026-10-27** (`D-033`). Esta versão cobre o **Nível 1 de Possibilidades: Caminhos Macro (Bloco 2.2)**, com a **avaliação dupla** e o **registro de decisão** definidos de forma genérica. As **propostas de fornecedores por categoria (Bloco 3.2)** reaproveitam esse modelo e serão detalhadas depois.
>
> **Onde aparece na tela:** os Caminhos Macro ficam na aba **"Definições Base & Caminhos Macro"** da área **Planejamento & Caminhos** (`experience.md` §3.1). A área **Possibilidades & Decisões** (por categoria) recebe as propostas no Bloco 3.2.
>
> **Fontes:** `docs/product/scope.md` §5, `docs/design/experience.md` (Fluxo 1, objetos 6 e 7), `docs/product/jobs.md` (J1, J8), `D-007`, `D-012`, `D-021`, `D-033`.
>
> **Convenções:** `F-POS-xx` identifica a feature. "Autor" é o usuário da sessão. Nenhum caminho é pré-carregado: o Altare não sugere formatos nem regiões.

---

## Visão da Área

**Jobs atendidos:** J1 (comparar caminhos macro) e J8 (avaliar individualmente e registrar a decisão com motivo).

**Modelo compartilhado (Blocos 2.2 e 3.2):**

| Objeto | O que é | Usado em |
| :--- | :--- | :--- |
| **Possibilidade** | Uma alternativa em análise. Tipo `Macro` agora; `Proposta` no Bloco 3.2 | 2.2 e 3.2 |
| **Avaliação** | A opinião de **um** perfil sobre **uma** possibilidade | 2.2 e 3.2 |
| **Selo de consenso** | Indicador **derivado** do alinhamento das duas avaliações | 2.2 e 3.2 |
| **Decisão registrada** | A escolha de uma possibilidade e o descarte das demais, com motivos | 2.2 e 3.2 |

---

## F-POS-01 — Caminho Macro

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto, obrigatório | Único por casamento, sem diferenciar maiúsculas. Ex.: "Caminho Exemplo A" |
| **Descrição** | Texto curto | — |
| **Formato** | Texto curto | Livre. Nenhuma sugestão pré-carregada |
| **Cidade ou região** | Texto curto | Livre |
| **Porte** | Faixa de convidados (mínimo e máximo, inteiros) | Opcional |
| **Prós** | Lista de itens de texto | Adicionar, editar, remover e reordenar |
| **Contras** | Lista de itens de texto | Idem |
| **Logística para convidados** | Texto livre | Deslocamento, hospedagem etc., como o casal quiser descrever (`D-033`: sem campos estruturados) |
| **Referências** | Links e imagens | Como em `F-PLN-06` (F-POS-07) |
| **Cenário de orçamento vinculado** | Um cenário do Simulador, opcional | Ver F-POS-02 |
| **Estado** | `Em análise` · `Escolhida` · `Descartada` | Padrão `Em análise`. No máximo **um** caminho `Escolhida` |

**Regras**
1. Qualquer um dos dois cria e edita. A autoria fica no histórico básico.
2. **Excluir** é lógico e recuperável. Um caminho `Escolhida` só pode ser excluído depois de **reabrir a decisão** (F-POS-05).
3. Para comparar, são necessários **ao menos dois** caminhos `Em análise`.

**Critérios de aceite**
- Um casamento recém-criado não tem nenhum caminho e mostra um estado vazio com a ação "Criar o primeiro caminho".
- Criar um caminho sem nome é bloqueado.
- Dois caminhos com o mesmo nome são bloqueados com mensagem acionável.
- Excluir um caminho `Escolhida` é recusado com "reabra a decisão antes".

---

## F-POS-02 — Custo Exibido, Derivado do Cenário Vinculado

**Regras**
1. Cada caminho pode ser vinculado a **no máximo um** cenário do Simulador, e cada cenário a no máximo um caminho (`D-033`).
2. O custo **não é digitado**: é **lido do cenário** (`architecture.md`, "derivar, não duplicar"). Mostra **Total com reserva**, **custo por convidado**, **folga ou estouro** e a base de convidados (`F-ORC-05`).
3. Os avisos do cenário aparecem junto: "N linhas sem estimativa", "estimado incompleto", "defina o teto global".
4. **Sem cenário vinculado:** o painel mostra "Sem cenário vinculado" e as ações **"Vincular a um cenário"** ou **"Criar cenário para este caminho"**. Criar gera um cenário vazio com o nome do caminho e o vincula. Se for o primeiro cenário do casamento, ele **vira o ativo** (`F-ORC-01`, regra 3).
5. Excluir o cenário vinculado desfaz o vínculo e avisa.

**Critérios de aceite**
- Um caminho vinculado ao "Cenário A" mostra o Total com reserva e o custo por convidado do A, e muda quando o A muda, sem digitação.
- Vincular um cenário que já pertence a outro caminho é recusado com o nome do outro caminho.
- "Criar cenário para este caminho" cria e vincula; se não havia nenhum cenário, o criado vira ativo e a tela avisa.
- Sem vínculo, não aparece nenhum valor monetário no lugar do custo.

---

## F-POS-03 — Avaliação Dupla (`D-012`, `D-021`)

**O que é:** cada pessoa registra o que acha de uma possibilidade, na sua própria sessão.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Classificação** | `Favorito` · `Gostei` · `Com ressalvas` · `Descartaria` | **Obrigatória** para a avaliação contar. Botões de seleção única |
| **Nota** | Inteiro de 1 a 5 | **Opcional**. Botões numéricos em mono, não estrelas (`D-025`) |
| **Comentário** | Texto livre | Opcional |

**Regras**
1. Cada pessoa edita **só a sua** avaliação; a do outro é leitura e **aparece de imediato** (`D-021`).
2. Para avaliar como o outro no computador compartilhado, troca-se de usuário (login rápido).
3. A avaliação **continua editável** depois da decisão; a alteração fica no histórico com autor e data.
4. Rótulos por perfil (`Noivo`, `Noiva`), **sem cor por perfil** (`D-025`). O estado é sempre textual ("Aguardando avaliação da Noiva").
5. A nota **informa** e **não entra** no selo de consenso (`D-033`). Quando as duas notas existem, mostra-se ao lado, em mono ("5 e 2").

**Critérios de aceite**
- Com a Noiva logada, ela não consegue alterar a avaliação do Noivo.
- Salvar sem classificação mostra erro e não registra avaliação.
- Salvar com classificação e sem nota nem comentário é aceito.
- A avaliação do Noivo aparece para a Noiva logo após ser salva, sem recarregar.

---

## F-POS-04 — Selo de Consenso e Comparação

**Selo de consenso (derivado, nunca editado)** (`D-012`, `design-system.md` §9):

| Situação (classificações) | Selo | Tom |
| :--- | :--- | :--- |
| Falta a avaliação de um dos dois | `Aguardando avaliação` + quem falta | Neutro |
| **Ambos** `Descartaria` | `Ambos descartariam` | Neutro |
| **Ambos** `Favorito` ou `Gostei` | `Consenso Favorito` | `consensus` (sálvia), ícone `heart-handshake` |
| Qualquer outra combinação | `Conversar juntos` | `attention` (argila), ícone `messages-square` |

Regras de leitura: a ordem de avaliação das regras é a da tabela, de cima para baixo. O selo se chama `Consenso Favorito` mesmo quando as duas avaliações são `Gostei` (`D-033`). `Com ressalvas` de qualquer um dos dois leva a `Conversar juntos`, a menos que ambos sejam `Descartaria`.

**Comparação lado a lado**

| Elemento | Conteúdo |
| :--- | :--- |
| **Quantidade** | De 2 a 5 caminhos `Em análise` |
| **Linhas** | Formato · Cidade ou região · Porte · Prós · Contras · Logística · **Custo** (F-POS-02) · Avaliação do Noivo · Avaliação da Noiva · Selo de consenso |
| **Destaque** | Selo "Menor total com reserva" entre os caminhos com cenário vinculado **e totais completos** (`F-ORC-08`) |
| **Desktop** | Tabela com primeira coluna fixa e colunas ≥ 280 px por caminho |
| **Mobile** | **Cartões empilhados** com abas deslizantes |
| **Estado** | A seleção fica na **URL** (compartilhável) |

**Critérios de aceite**
- Noivo `Favorito` e Noiva `Gostei` mostram `Consenso Favorito` com ícone e texto.
- Noivo `Favorito` e Noiva `Descartaria` mostram `Conversar juntos` com ícone e texto, sem usar vermelho.
- Os dois `Descartaria` mostram `Ambos descartariam`.
- Os dois `Com ressalvas` mostram `Conversar juntos`.
- Só o Noivo avaliou: mostra `Aguardando avaliação da Noiva`.
- Notas 5 e 2 não alteram o selo, e aparecem como "5 e 2".
- Selecionar um sexto caminho é recusado com "compare até 5 caminhos".

---

## F-POS-05 — Registro de Decisão Macro

**O que é:** bater o martelo: escolher um caminho e descartar os demais, com os motivos.

**Fluxo**
1. O casal clica em **"Registrar decisão"** e escolhe o caminho vencedor entre os `Em análise`.
2. Escreve o **motivo da escolha** (**obrigatório**).
3. Para **cada** caminho descartado, escreve o **motivo do descarte** (**obrigatório**). Há "usar o mesmo texto nos demais" como atalho.
4. Se faltar a avaliação de um dos dois, a tela **avisa** ("Falta a avaliação da Noiva") e permite seguir com confirmação.
5. A tela mostra o que será **sugerido** (abaixo) e pede confirmação.

**Efeitos sugeridos (cada um com confirmação, `D-033`)**

| Efeito | Comportamento |
| :--- | :--- |
| **Definições Base** | Sugere preencher **Formato**, **Cidade ou região** e **Porte** com os valores do caminho, mostrando "atual → novo" por campo. Vêm marcados só os campos ainda `Em definição`. Campos já `Definido` vêm desmarcados e com aviso de impacto (`F-PLN-01`, regra 2). Ao aplicar, o campo passa a `Definido`. Campos vazios no caminho não são sugeridos |
| **Orçamento** | Se houver cenário vinculado que **não** seja o ativo, oferece **promovê-lo a Orçamento Oficial Ativo** (desmarcado por padrão; pede a confirmação de `F-ORC-01`) |
| **Cronograma** | O marco **"Escolher o caminho macro"** (C04) é concluído **automaticamente** (`F-CRN-03`, regra 6), destravando o que depende dele |

**Registro:** data, autor, caminho escolhido, motivos da escolha e de cada descarte. O vencedor vai a `Escolhida`, e os demais a `Descartada`.

**Reabrir a decisão**
1. Qualquer um pode **reabrir**: todos voltam a `Em análise`, **os motivos anteriores ficam no histórico** e o marco C04 é reaberto (`F-CRN-03`, regra 5).
2. Os valores já aplicados às Definições Base e ao orçamento **não são revertidos automaticamente**; a tela avisa e lista o que foi aplicado, para o casal ajustar.
3. Uma nova decisão gera um **novo registro**, sem apagar os anteriores.

**Critérios de aceite**
- Registrar sem motivo da escolha, ou com um descarte sem motivo, é bloqueado com mensagem acionável.
- Escolher o "Caminho Exemplo A" com Formato e Região `Em definição` sugere os dois campos já marcados; com a Região `Definido`, a Região vem desmarcada e com aviso.
- Aplicar a sugestão marca Formato e Região como `Definido` e registra o autor.
- A decisão conclui o marco C04 e destrava C05.
- Reabrir a decisão volta todos a `Em análise`, reabre C04 e preserva os motivos no histórico.
- Com a avaliação da Noiva faltando, a tela avisa e só segue com confirmação.

---

## F-POS-06 — Visões, Filtros e Lente

| Recurso | Comportamento |
| :--- | :--- |
| **Lista de caminhos** | Cartões com nome, formato, região, custo derivado, estado e selo de consenso |
| **Filtros** | Estado, selo de consenso e "só o que falta eu avaliar". Estado na **URL** |
| **Lente `Casal`** | Destaca caminhos em `Conversar juntos` |
| **Lente `Minha visão`** | Destaca caminhos em que falta **a minha** avaliação |
| **Desktop** | Lista com painel lateral de detalhe (prós, contras, avaliações, referências) |
| **Mobile** | Cartões; detalhe em folha inferior; avaliar em poucos toques |

**Critérios de aceite**
- Com o Noivo em `Minha visão`, caminhos que ele ainda não avaliou aparecem destacados.
- Aplicar um filtro altera a URL, e o botão voltar do navegador o desfaz.
- Em 320 px, nenhum cartão exige rolagem horizontal.

---

## F-POS-07 — Referências do Caminho

**Regras:** as mesmas de `F-PLN-06` (`D-029`): **link** (domínio visível, sem leitura automática da página) ou **imagem** (JPG, PNG, WebP via `FileStorage`, com validação de tipo real e tamanho); título e comentário opcionais; autor mostrado como rótulo; só o autor remove o seu, de forma lógica.

**Critérios de aceite**
- Colar uma URL inválida mostra erro acionável.
- Um arquivo que não é imagem real é recusado.
- No celular, adicionar uma foto da galeria leva poucos toques.

---

## O que o Bloco 3.2 acrescenta depois (não entra agora)
- Tipo de possibilidade `Proposta`, ligada a uma categoria e a um contato.
- Preço base, itens incluídos e **custos extras** (Normalizador de Custo Comparável), PDFs e condições de pagamento.
- Decisão **por categoria**, com efeito em Contratado e no marco "Fechar …".

## Fora desta área neste bloco
- **Campos próprios de logística, época e anexos** em cada caminho: não solicitados (logística é texto livre).
- **Entrevista Guiada por IA** que gera caminhos (`D-010`): v1.1+.
- **Votação cega** (ver a avaliação do outro só depois de avaliar): rejeitada, as avaliações são visíveis de imediato (`D-021`).

## Pontos a validar em uso
1. O selo `Consenso Favorito` com duas avaliações `Gostei`: se o nome incomodar, trocar o rótulo (reversível, sem mudar a regra).
2. A regra `Com ressalvas` leva a `Conversar juntos`: reavaliar se aparecer em excesso.
3. No Bloco 3.2, definir a decisão por categoria e o efeito em Contratado.
