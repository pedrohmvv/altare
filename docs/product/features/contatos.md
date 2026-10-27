# Features: Contatos & Fornecedores (`features/contatos.md`)

> **Status:** **Aprovado pelo usuário em 2026-10-27** (`D-034`). Cobre o **Bloco 3.1**: fichas de Fornecedor e de Pessoa, funil de status, histórico de interações, Próximo Passo Único, visitas agendadas, arquivos e links, aviso de duplicidade, lista com visões e a **busca global do app**.
>
> **Onde aparece na tela:** área **Contatos** (`experience.md` §3.1, item 6). A busca global fica no cabeçalho da casca de navegação, em todas as áreas.
>
> **Fontes:** `docs/product/scope.md` §4, `docs/design/experience.md` (§3.1 e §3.2, fluxo de captura do fornecedor), `docs/product/jobs.md`, `D-002`, `D-013`, `D-021`, `D-029`, `D-031`, `D-034`.
>
> **Convenções:** `F-CTT-xx` identifica a feature. "Autor" é o usuário da sessão. Qualquer um dos dois cria e edita. Estados e valores derivados nunca são digitados. Nada é pré-carregado: o Altare não sugere fornecedores. Dados de terceiros (telefone, e-mail, Instagram) ficam só no banco do casal e **não vão para logs**.

---

## Visão da Área

**Jobs atendidos:** manter uma base limpa de fornecedores e pessoas, saber em que pé está cada conversa, onde estão os PDFs enviados e qual é o próximo passo.

| Objeto | O que é | Tem funil? | Tem Próximo Passo? |
| :--- | :--- | :--- | :--- |
| **Fornecedor** | Empresa ou profissional que o casal cotou ou contratou (espaço, buffet, fotografia etc.) | Sim | Sim |
| **Pessoa** | Alguém que não vende nada ao casal: indicação, familiar, contato do local | Não | Não |
| **Interação** | Registro datado de uma conversa ou evento (só no Fornecedor) | — | — |
| **Visita** | Visita agendada a um fornecedor, com data e hora | — | — |

---

## F-CTT-01 — Ficha do Fornecedor e Captura Rápida

**Captura rápida (celular e desktop):** o formulário inicial pede só **Nome**, **Categoria** e, opcionalmente, telefone, Instagram e nota (campos recolhidos por padrão). Ao salvar, abre a ficha. Há também "Salvar e adicionar outro".

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto, obrigatório | Nome do fornecedor. Duplicidade só **avisa** (F-CTT-08) |
| **Categorias** | Uma ou mais categorias do catálogo (`F-PLN-02`), **obrigatória ao menos uma** | Mostra o estado da categoria no escopo. Vincular uma categoria `Fica de fora` é permitido e exibe o aviso "categoria fora do escopo" |
| **Quem atende** | Texto curto | Nome e função da pessoa de contato, como "Ana, comercial" (`D-034`: uma só pessoa, texto livre) |
| **Telefone / WhatsApp** | Telefone brasileiro | Normalizado para `wa.me/55…` como em `F-CNV-01`: botão "Abrir WhatsApp" quando válido. Telefone inválido mostra erro e não gera link |
| **E-mail** | E-mail | Validação de formato. Botão "Enviar e-mail" |
| **Instagram** | Texto | Aceita `@usuario` ou URL. Guarda o usuário e abre `instagram.com/usuario` |
| **Site** | URL | Se faltar `https://`, é acrescentado. Mostra o domínio |
| **Cidade ou região** | Texto curto | Livre |
| **Indicado por** | Texto curto | Livre. Ex.: "Pessoa Exemplo" |
| **Nota** | Texto | Livre |
| **Status** | Funil | F-CTT-03 |
| **Próximo Passo** | Ação, data-alvo e responsável | F-CTT-05 |

**Regras**
1. **Excluir** é lógico e recuperável. Um fornecedor com proposta, decisão ou contrato **não pode ser excluído** até a decisão ser reaberta, o contrato cancelado e as propostas excluídas (`F-PRP-01`, regra 5; `F-CTR-01`).
2. Telefone, e-mail e Instagram são opcionais. Sem eles a ficha continua válida.
3. Mudar a categoria **não** altera o orçamento nem o cronograma. Esses vínculos nascem das propostas e decisões (Bloco 3.2).
4. No cartão e na ficha, o **WhatsApp** é a ação de destaque no celular (alvo ≥ 44 px).

**Critérios de aceite**
- Criar um fornecedor só com nome e categoria funciona e deixa o status em `Para contatar`.
- Criar sem nome ou sem categoria é bloqueado com mensagem acionável.
- Telefone `(11) 91234-5678` gera `https://wa.me/5511912345678`. Telefone inválido mostra erro.
- `@exemplo.studio` abre `https://instagram.com/exemplo.studio`.
- Vincular uma categoria `Fica de fora` mostra o aviso, sem impedir.
- No celular, criar um fornecedor leva poucos toques e a ficha abre ao salvar.

---

## F-CTT-02 — Ficha da Pessoa

**O que é:** o lugar para quem aparece nas conversas sem ser fornecedor: quem indicou, um familiar que ajuda, o contato do local.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Nome** | Texto, obrigatório | Duplicidade só avisa (F-CTT-08) |
| **Relação** | Texto curto | Livre. Ex.: "Indicação", "Familiar" |
| **Telefone / WhatsApp** | Telefone brasileiro | Mesma regra de `F-CTT-01` |
| **E-mail** | E-mail | Mesma regra |
| **Instagram** | Texto | Mesma regra |
| **Cidade ou região** | Texto curto | Livre |
| **Nota** | Texto | Livre |

**Regras**
1. A Pessoa **não** tem funil, Próximo Passo, interações nem visitas.
2. Pode receber **arquivos e links** (F-CTT-07).
3. Exclusão lógica e recuperável.
4. Pessoa e Fornecedor aparecem na mesma lista, separados pelo filtro **Tipo**.

**Critérios de aceite**
- Uma Pessoa não mostra status nem Próximo Passo.
- Criar sem nome é bloqueado.

---

## F-CTT-03 — Funil de Status do Fornecedor (`D-034`)

**Estados:** `Para contatar` → `Aguardando orçamento` → `Orçamento recebido` → `Em negociação / Visita` → `Contratado` · `Descartado`.

**Regras**
1. Um fornecedor novo começa em `Para contatar`.
2. O casal pode mover para **qualquer** estado, em qualquer ordem. Não há bloqueio de sequência: a conversa real vai e volta.
3. Mudar de status é uma ação explícita (menu ou seletor, sem exigir arrastar). Cada mudança gera uma entrada automática na linha do tempo, marcada como "do sistema", com o estado anterior, o novo, o autor e a data.
4. **`Descartado`:** o **motivo é opcional** (campo de texto na hora de descartar). O fornecedor sai das visões padrão, mas aparece com o filtro de status. Ao descartar, o **Próximo Passo é removido** e registrado na linha do tempo. **Reativar** volta ao estado escolhido pelo casal.
5. **`Contratado`:** até o Bloco 3.2 é um estado **manual**. A partir do Bloco 3.2 passa a ser **derivado** da decisão por categoria e deixa de ser editável à mão (`D-035`). Um fornecedor é `Contratado` se **qualquer** proposta dele foi escolhida **ou** se tem um **contrato direto** ativo (`F-CTR-01`). A ficha mostra em **quais categorias** ele está contratado. Na entrega do bloco, os marcados à mão voltam a `Em negociação / Visita`, com entrada na linha do tempo (`F-PRP-08`). Reabrir a decisão devolve o fornecedor ao status que tinha antes dela.
6. **Sugestões, não automação:** ao agendar a primeira visita, a tela **sugere** mover para `Em negociação / Visita`, e o casal confirma. Cadastrar a primeira proposta de um fornecedor **sugere** `Orçamento recebido` (`F-PRP-01`, regra 7).

**Critérios de aceite**
- Mover de `Para contatar` direto para `Em negociação / Visita` é permitido.
- Cada mudança de status aparece na linha do tempo com autor e data.
- Descartar sem motivo funciona. Descartar com Próximo Passo pendente o remove e registra isso na linha do tempo.
- Reativar um descartado o devolve à lista padrão.

---

## F-CTT-04 — Histórico de Interações

**O que é:** a linha do tempo do que foi conversado ou combinado com **um fornecedor**.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Tipo** | `WhatsApp` · `Ligação` · `Visita` · `E-mail` · `Reunião` · `Outro` | Obrigatório. Padrão `WhatsApp` |
| **Data** | Data | Padrão hoje. **Não pode ser futura**: o futuro é Próximo Passo ou Visita |
| **Texto** | Texto, obrigatório | O que foi dito ou combinado |
| **Autor** | Perfil da sessão | Mostrado como rótulo `Noivo` ou `Noiva` |

**Regras**
1. Ordem da mais recente para a mais antiga. Entradas do sistema (mudança de status, visita realizada, Próximo Passo concluído ou removido) aparecem na mesma linha do tempo, com um rótulo "Sistema".
2. Qualquer um adiciona. **Só o autor** edita ou remove as suas, de forma lógica e recuperável. Entradas do sistema não são editáveis.
3. No celular, o formulário de nova interação abre pronto, com tipo `WhatsApp` e data de hoje.

**Critérios de aceite**
- Registrar uma interação com data de amanhã é bloqueado, com a orientação "use Próximo Passo ou Visita".
- Uma interação do Noivo não pode ser editada pela Noiva.
- A mudança de status aparece na linha do tempo como entrada do sistema.

---

## F-CTT-05 — Próximo Passo Único

**O que é:** a **única** ação pendente de cada fornecedor, em destaque na ficha e na lista.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Ação** | Texto, obrigatório quando existir | Ex.: "Pedir o orçamento do pacote maior" |
| **Data-alvo** | Data, opcional | Sem horário |
| **Responsável** | `Noivo` · `Noiva` · `Ambos` | Padrão: o perfil da sessão |

**Regras**
1. Cada fornecedor tem **no máximo um** Próximo Passo ativo. Fornecedor sem Próximo Passo mostra a ação "Definir próximo passo".
2. **Concluir** abre um passo curto: "O que aconteceu?" (texto e tipo, ambos opcionais, tipo padrão `Outro`). Isso cria uma interação com a ação concluída e, em seguida, pergunta o **próximo passo** ou permite escolher **"Sem próximo passo"**.
3. **`Atrasado`** é derivado: data-alvo anterior a hoje. Mostra ícone e texto, nunca só cor.
4. Qualquer um edita ou remove, e a mudança entra no histórico básico.
5. Fornecedores `Descartado` não têm Próximo Passo (F-CTT-03). Em `Contratado` o Próximo Passo continua permitido.
6. Os Próximos Passos de contatos alimentarão a visão "meus próximos passos" do Centro de Comando (Bloco 4.2), filtrada pela lente.

**Critérios de aceite**
- Salvar uma ação em branco é bloqueado. Definir um segundo Próximo Passo **substitui** o atual (com confirmação), nunca coexiste.
- Concluir um passo cria uma interação e abre a definição do próximo.
- Um passo com data-alvo de ontem mostra "Atrasado" com ícone e texto.
- Com a `Noiva` logada e a lente `Minha visão`, a lista mostra só os fornecedores cujo Próximo Passo é da `Noiva` ou de `Ambos`.

---

## F-CTT-06 — Visitas Agendadas (`D-034`)

**O que é:** visita marcada a um fornecedor (espaço, ateliê, degustação), com **data e hora**. Uma visita não é uma tarefa.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Data** | Data, obrigatória | — |
| **Hora** | Hora, obrigatória | Hora local, sem fuso por visita |
| **Local** | Texto curto, opcional | Endereço ou ponto de encontro, como o casal quiser escrever |
| **Participantes** | `Noivo` · `Noiva` · `Ambos` | Padrão `Ambos` |
| **Nota** | Texto, opcional | Ex.: o que perguntar ou levar |
| **Estado** | `Agendada` · `Realizada` · `Cancelada` | Padrão `Agendada` |

**Regras**
1. Um fornecedor pode ter **várias** visitas.
2. **Calendário do Cronograma (`F-CRN-10`):** as visitas `Agendadas` aparecem no **dia** da visita, com a hora e o nome do fornecedor, como itens somente leitura. Clicar abre a ficha do fornecedor. É uma **visão** sobre os mesmos dados, sem cópia.
3. Marcar `Realizada` cria automaticamente uma interação do tipo `Visita`, na data da visita, com a nota da visita como texto (ou "Visita realizada"), editável pelo autor.
4. Marcar `Cancelada` gera uma entrada do sistema na linha do tempo. A visita deixa de aparecer no calendário.
5. Uma visita `Agendada` cuja data já passou mostra o selo derivado **"Passou"** e a pergunta "Foi realizada ou cancelada?". Visita não gera `Atrasado`.
6. Agendar a primeira visita **sugere** mover o status (F-CTT-03).
7. A hora existe só na visita. **Marcos e tarefas continuam sem horário** (`D-031`).

**Critérios de aceite**
- Uma visita em 15/03/2027 às 14:00 aparece no dia 15/03/2027 do calendário, com "14:00".
- Marcar uma visita como `Realizada` cria a interação `Visita` na linha do tempo.
- Uma visita cancelada some do calendário.
- Uma visita `Agendada` no passado mostra "Passou".

---

## F-CTT-07 — Arquivos e Links

**O que é:** PDFs de propostas, minutas de contrato, fotos de visita e links de portfólio.

**Regras**
1. Vale para **Fornecedor** e **Pessoa**, com os mesmos controles de `F-PLN-06` e `F-CRN-08`: **arquivo** (PDF ou imagem, via `FileStorage`, com validação de tipo real e tamanho) ou **link** (domínio visível, sem leitura automática da página).
2. Título e comentário opcionais. Autor mostrado como rótulo.
3. Qualquer um adiciona. **Só o autor** remove o seu, de forma lógica e recuperável.
4. Visualização do PDF dentro do app. No celular, o envio abre a câmera ou a galeria.
5. Os arquivos aparecem na ficha e são encontrados pela busca global (F-CTT-10), pelo **nome do arquivo ou título**, não pelo conteúdo.
6. As propostas do Bloco 3.2 reaproveitam este mesmo mecanismo de anexo (`F-PRP-04`), e as propostas e seus arquivos também entram na busca global.

**Critérios de aceite**
- Anexar um PDF a um fornecedor o mostra na ficha com nome e tamanho, e permite abri-lo.
- Um arquivo com extensão trocada (não é PDF real) é recusado.
- URL inválida mostra erro acionável.

---

## F-CTT-08 — Aviso de Duplicidade (`D-034`)

**Regras**
1. Ao salvar um Fornecedor ou Pessoa, o Altare compara **telefone** (normalizado, só dígitos), **e-mail** (sem diferenciar maiúsculas) e **Instagram** (usuário normalizado) com os demais contatos **ativos**, de qualquer tipo.
2. Havendo coincidência, mostra um **aviso**, com o nome do contato existente e um link para ele. O casal pode **"Salvar mesmo assim"** ou **abrir o existente**. O aviso **não bloqueia**.
3. Campos vazios não são comparados. Contatos excluídos não entram.
4. A comparação por nome não faz parte da v1.
5. Ao editar, o contato não é comparado consigo mesmo.

**Critérios de aceite**
- Salvar um telefone `(11) 91234-5678` quando outro contato tem `11912345678` mostra o aviso.
- "Salvar mesmo assim" conclui o salvamento.
- Dois contatos sem telefone não geram aviso.

---

## F-CTT-09 — Lista, Visões e Filtros

| Recurso | Comportamento |
| :--- | :--- |
| **Lista** | Desktop em tabela e celular em cartões. Colunas e cartão: nome, categorias, status, Próximo Passo (ação e data-alvo, com `Atrasado` quando for o caso), próxima visita e botão WhatsApp |
| **Por status** | Agrupa por estado do funil. Desktop em colunas; celular em seções recolhíveis (sem rolagem horizontal em 320 px). Mudar o status é por menu, não por arrastar |
| **Filtros** | Tipo (Fornecedor ou Pessoa), categoria, status, responsável do Próximo Passo, "Próximo Passo atrasado", "Com visita agendada" e texto livre |
| **Lente** | `Minha visão` filtra pelo responsável do Próximo Passo (o perfil da sessão e `Ambos`); `Casal` mostra todos |
| **Ordenação padrão** | Próximo Passo atrasado primeiro, depois por data-alvo mais próxima, depois sem Próximo Passo, e por nome |
| **Padrão** | Esconde `Descartado`. O filtro de status o mostra |
| **Por categoria** | A visão da categoria (`F-PLN-08`) mostra a contagem de fornecedores por status e leva à lista já filtrada |

**Regras**
1. Filtros e visão ficam na **URL** (`D-021`).
2. Estado vazio: "Nenhum contato ainda" com a ação "Novo contato".
3. Tudo funciona em 320 px sem rolagem horizontal.

**Critérios de aceite**
- Um fornecedor com Próximo Passo atrasado aparece no topo da lista padrão.
- O filtro de categoria mostra só os fornecedores vinculados a ela.
- `Descartado` só aparece com o filtro de status.
- Recarregar a página mantém filtros e visão.

---

## F-CTT-10 — Busca Global do App (`D-034`)

**O que é:** um campo de busca no cabeçalho, em todas as áreas, para chegar a qualquer coisa pelo nome.

**Regras**
1. **O que é encontrado hoje:** contatos (nome, "quem atende", categoria, telefone, e-mail, Instagram, cidade e "indicado por"), nomes de arquivos e títulos de anexos, categorias do escopo, núcleos e convidados, marcos e tarefas avulsas, caminhos macro e cenários de orçamento.
2. **Cresce com o produto:** propostas, contratos e parcelas, itens do enxoval entram quando suas áreas forem construídas. Cada área registra o que é pesquisável.
3. Busca por **trecho**, sem diferenciar acento nem maiúsculas. Mínimo de 2 caracteres. **Sem busca no conteúdo dos PDFs** e sem correção de digitação na v1.
4. Resultados **agrupados por tipo**, com os mais relevantes de cada grupo e a opção "ver todos" levando à área já filtrada. Clicar abre o item.
5. **Itens excluídos** não aparecem. Itens `Descartado` e `Fica de fora` aparecem com o estado rotulado.
6. Atalho de teclado no desktop (`/` ou `Cmd/Ctrl+K`). No celular, um ícone no cabeçalho. Totalmente acessível por teclado.
7. A busca **ignora a lente**: procura no casamento todo.
8. Executada no backend. Nenhum dado de contato vai para logs.

**Critérios de aceite**
- Buscar "ana" encontra um contato com "Ana, comercial" em "quem atende".
- Buscar sem acento ("acai") encontra "Açaí".
- Um contato excluído não aparece.
- Buscar o nome de um arquivo leva à ficha do contato que o contém.
- Um termo com 1 caractere não dispara a busca.

---

## Fora desta área (v1)
- **Captura rápida por encaminhamento do WhatsApp ou atalho de celular:** v1.1+ (`scope.md` §4).
- **Integração com a API do WhatsApp** para ler conversas: fora do produto.
- **Várias pessoas de contato por fornecedor**, cada uma com telefone e função: não entra (`D-034`); "Quem atende" é um texto livre.
- **Indicador de contato parado há N dias:** não entra (`D-034`). O Próximo Passo e o filtro de atrasados cobrem o caso.
- **Detecção de duplicidade por nome:** não entra.
- **Notificações e lembretes** (in-app, push, WhatsApp): v1.1+ (`D-013`).
- **Sincronização de visitas com Google/Apple Calendar:** v1.1+.
- **Busca no conteúdo de PDFs:** não entra na v1.
- **Arrastar cartões entre colunas:** não entra na v1.

## Pontos de atenção para as próximas áreas
1. ~~**Bloco 3.2:** `Contratado` derivado, várias categorias, recusa de exclusão e a sugestão `Orçamento recebido`.~~ Resolvido em `D-035` (`propostas-por-categoria.md`). A ficha ganha a aba **Propostas** e os chips de categorias contratadas.
2. **Bloco 3.3:** o contato responsável para o Dia D vem do contrato, não da ficha do fornecedor.
3. **Bloco 4.2:** "meus próximos passos" no Centro de Comando consome os Próximos Passos (F-CTT-05).
