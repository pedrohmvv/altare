# Features: Planejamento & Caminhos (`features/planejamento-e-caminhos.md`)

> **Status:** **Aprovado pelo usuário em 2026-10-27** (`D-029`). Cobre o **Bloco 1.1** (Definições Base e Mapa de Escopo). Os **Caminhos Macro** (comparação de formatos) pertencem ao **Bloco 2.2** e serão detalhados quando o território de Possibilidades for tratado.
>
> **Implementação:** em 4 PRs (`D-066`). `F-PLN-01` está implementada (`D-067`), assim como `F-PLN-02` a `F-PLN-05` e `F-PLN-08` (`D-068`); `F-PLN-06` (referências) também (`D-069`), e os efeitos em cadeia de `F-PLN-07` só valem quando o orçamento e o cronograma existirem.
>
> **Fontes:** `docs/product/scope.md` §1, `docs/design/experience.md` (Fluxo 1, objetos 2 e 3), `docs/product/jobs.md` (J1), `D-026` (produto não confessional) e `D-029`.
>
> **Convenções:** `F-PLN-xx` identifica a feature. "Autor" é sempre o usuário da sessão (`stack.md` §6). Dinheiro em centavos. Nenhum campo vem preenchido com dado do casamento (`AGENTS.md` §2).

---

## Visão da Área

| Aba (experience.md §3.1) | Conteúdo | Bloco |
| :--- | :--- | :--- |
| **Definições Base & Caminhos Macro** | Painel de Definições Base (aqui) + comparação de caminhos macro (Bloco 2.2) | 1.1 + 2.2 |
| **Mapa de Escopo** | Categorias, status, prioridade individual, estimativa, nota e referências | 1.1 |

**Job atendido:** J1. *Definir os caminhos macro e o que o casamento terá ou ficará de fora.*

---

## F-PLN-01 — Painel de Definições Base

**O que é:** o quadro das variáveis estruturais do casamento. Cada uma começa `Em definição` e passa a `Definido` quando o casal decide.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Data ou época** | `nenhuma` · `janela` (mês/ano inicial e final, rótulo opcional) · `data exata` | Só a **data exata** muda o cronograma para o *Modo Com Data* (Bloco 1.3). Janela é informativa |
| **Cidade ou região** | Texto curto | Livre. Nenhuma sugestão pré-carregada |
| **Formato** | Texto curto | Livre. No Bloco 2.2 pode ser definido por uma decisão de Caminho Macro |
| **Porte** | Faixa de convidados (mínimo e máximo, inteiros) | Mostra ao lado, **derivada e nunca copiada**, a contagem da lista de convidados quando existir (Bloco 1.2) |
| **Teto macro** | Dinheiro em centavos | Referência global. Os tetos reais ficam nos cenários do Bloco 2.1 |
| **Tipo de cerimônia** (`D-026`) | Seleção múltipla: `Religiosa` · `Civil` · `Simbólica`, mais detalhe em texto livre | Dado do casal, nunca presumido. Termos de uma tradição só aparecem se o casal os escrever |

**Estados por campo:** `Em definição` → `Definido`, com **nota livre** ("por que estamos em dúvida").

**Regras**
1. `Definido` exige valor preenchido.
2. Alterar um campo `Definido` mostra o **impacto** (ex.: "a data recalcula janelas do cronograma") e pede confirmação.
3. Toda alteração fica no **histórico básico**, com autor e data (`architecture.md` §10).
4. Voltar de `Definido` para `Em definição` é permitido.
5. Qualquer dos dois pode editar. Não há aprovação conjunta (`D-029`).

**Critérios de aceite**
- Num casamento recém-criado, todos os campos aparecem vazios e `Em definição`.
- Marcar `Definido` sem valor é bloqueado, com mensagem acionável.
- Trocar uma data exata já `Definida` exige confirmação e registra autor e valor anterior.
- Teto macro aceita `R$ 28.000,00` e é gravado como `2800000`.
- Em celular de 320 px, o painel não tem rolagem horizontal.

---

## F-PLN-02 — Catálogo de Categorias do Escopo

**O que é:** a lista de frentes de um casamento. O Altare traz um **catálogo inicial** com nomes neutros (`D-026`), e o casal o adapta.

**Catálogo inicial (proposta):**

| Grupo | Categorias |
| :--- | :--- |
| Cerimônia | Cerimônia civil · Cerimônia religiosa ou simbólica |
| Espaço e alimentação | Espaço · Buffet · Bebidas e bar · Bolo e doces |
| Registro | Fotografia · Vídeo |
| Som e ambiente | Música (DJ, banda) · Decoração e flores · Iluminação e som |
| Estética | Trajes · Beleza (noivos) |
| Papelaria e lembranças | Convites e papelaria · Lembrancinhas |
| Condução | Cerimonial do dia |
| Pós-festa | Noite de núpcias · Lua de mel |

**Regras**
1. O casal pode **criar** categorias e grupos, **renomear** e **ocultar** (a categoria some das telas sem perder histórico). Categorias do catálogo não são apagadas, só ocultadas.
2. Exclusão lógica para as criadas pelo casal (`architecture.md` §10).
3. Nome único por casamento, sem diferenciar maiúsculas.
4. O catálogo é uma **semente**: depois de criado o casamento, é dado do casal e pode mudar sem afetar nenhum outro.

**Critérios de aceite**
- Ao iniciar, as categorias aparecem agrupadas e sem status (`Em discussão` por padrão).
- Criar duas categorias com o mesmo nome é bloqueado.
- Ocultar uma categoria com histórico a tira das listas e a deixa recuperável.

---

## F-PLN-03 — Status de Escopo e Motivo de Descarte

| Status | Significado | Efeito (F-PLN-07) |
| :--- | :--- | :--- |
| `Em discussão` *(padrão)* | Ainda sem decisão conjunta | Nenhum |
| `Entra (Essencial)` | Faz parte do casamento | Ativa orçamento e cronograma |
| `Talvez (Se couber)` | Opcional | Entra como item opcional na simulação |
| `Fica de fora` | Descartada | Arquiva a categoria |

**Regras**
1. **`Fica de fora` exige motivo** (texto). Sem motivo, não salva.
2. **Qualquer um dos dois** pode mudar o status, e a mudança é registrada com autor, data e status anterior (`D-029`).
3. Reabrir uma categoria `Fica de fora` é permitido. **Os motivos anteriores permanecem** no histórico da categoria.
4. Mudar para `Fica de fora` uma categoria com contrato ou possibilidades já registradas (blocos futuros) exige confirmação explicando o que acontece com elas.

**Critérios de aceite**
- Salvar `Fica de fora` sem motivo mostra erro e mantém o status anterior.
- O histórico da categoria lista, em ordem, quem mudou o quê e quando.
- Uma categoria reaberta mostra o motivo do descarte anterior.

---

## F-PLN-04 — Prioridade Individual e Alinhamento

**O que é:** antes de decidirem juntos, cada um marca o quanto quer aquela categoria.

**Escala (`D-029`):** `Quero muito` · `Se couber` · `Dispenso`.

**Alinhamento (derivado, nunca editado):**

| Situação | Condição |
| :--- | :--- |
| `Alinhados` | As duas prioridades são iguais |
| `Divergem` | As prioridades diferem |
| `Falta avaliar` | Falta a avaliação de um dos dois (mostra quem) |

**Regras**
1. Cada pessoa edita **só a sua** prioridade; a do outro é leitura, visível de imediato (`D-021`).
2. A prioridade **não muda o status conjunto**. Ela informa a conversa.
3. Rótulos por perfil (`Noivo`, `Noiva`), sem cor por perfil (`D-025`).
4. O texto de estado é sempre completo ("Aguardando avaliação da Noiva"), nunca só ícone.

**Critérios de aceite**
- Com a Noiva logada, ela não consegue alterar a prioridade do Noivo.
- Duas prioridades diferentes mostram `Divergem` com o ícone e o texto de atenção, sem usar vermelho.
- Uma categoria avaliada só por um dos dois mostra `Aguardando avaliação do outro perfil` com o nome.

---

## F-PLN-05 — Estimativa Inicial e Nota por Categoria (`D-029`)

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Estimativa inicial** | Dinheiro em centavos, opcional | É a expectativa de valor **antes de haver cotação**. Alimenta a coluna *Estimado* no Bloco 2.1 |
| **Nota** | Texto livre, por perfil | O que cada um espera daquela frente. Cada um edita só a sua; a do outro é leitura |

**Regras**
1. A estimativa é guardada **na categoria** e **lida** pelo orçamento no Bloco 2.1, sem cópia (`architecture.md`, "derivar, não duplicar"). O cenário pode sobrescrevê-la localmente, com "voltar ao valor da categoria" (`D-032`, `F-ORC-04`).
2. Categoria `Fica de fora` não conta no somatório.
3. O Mapa mostra o **total das estimativas** das categorias `Entra`, e a soma das `Talvez` à parte. Apenas informativo, sem comparar com o teto aqui (comparação com teto é do Bloco 2.1).

**Critérios de aceite**
- Estimativa vazia não conta como zero: aparece como "sem estimativa".
- O total das categorias `Entra` muda assim que uma estimativa é editada ou o status muda.
- A nota de um perfil não é editável pelo outro.

---

## F-PLN-06 — Referências por Categoria (`D-029`)

**O que é:** o lugar para guardar inspirações que hoje ficam espalhadas no Pinterest, no Instagram e no WhatsApp.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Tipo** | `Link` · `Imagem` | — |
| **Link** | URL | Mostra o domínio. **Sem leitura automática do conteúdo da página** (sem *scraping*) |
| **Imagem** | Arquivo (JPG, PNG, WebP) | Usa o `FileStorage` (`stack.md` §3): validação de tipo real e tamanho |
| **Título** | Texto curto, opcional | — |
| **Comentário** | Texto, opcional | — |
| **Autor** | Perfil da sessão | Mostrado como rótulo |

**Regras**
1. Uma categoria pode ter várias referências, sem limite fixo na v1.
2. Qualquer um adiciona. Só o **autor** remove a sua; remoção lógica e recuperável.
3. Imagens aparecem como miniaturas; no celular, o envio abre a câmera ou a galeria.

**Critérios de aceite**
- Colar uma URL inválida mostra erro acionável.
- Enviar um arquivo que não é imagem real (extensão trocada) é recusado.
- No celular, adicionar uma foto da galeria leva poucos toques e o resultado aparece na categoria.

---

## F-PLN-07 — Efeitos em Cadeia do Escopo

| Ao mudar para | Orçamento (Bloco 2.1) | Cronograma (Bloco 1.3) |
| :--- | :--- | :--- |
| `Entra` | Cria a linha da categoria nos cenários | Ativa os marcos da categoria |
| `Talvez` | Linha opcional, ligada/desligada por cenário | Marcos opcionais, não bloqueantes |
| `Fica de fora` | Linha arquivada | Marcos arquivados |
| `Em discussão` | Nenhum | Marcos da categoria ficam `Bloqueado`, com o motivo "Aguardando classificar a categoria" (refinado em `D-031`) |

**Regras**
1. Os efeitos são **derivados na leitura** (`architecture.md` §3), não copiados. Enquanto os Blocos 1.3 e 2.1 não existem, esta feature só **registra** o status; os efeitos passam a valer quando cada bloco chega.
2. Arquivar nunca apaga: voltar a `Entra` restaura a linha e os marcos com o histórico.
3. **Categoria com decisão registrada** (proposta `Escolhida`, Bloco 3.2) ou **contrato ativo** (Bloco 3.3) **não pode** ir para `Fica de fora` nem `Em discussão`. A tela pede para reabrir a decisão antes (`D-035`).

**Critérios de aceite** *(verificáveis quando os blocos de destino existirem)*
- Mudar para `Entra` faz a categoria aparecer no orçamento ativo e nos marcos sem digitação.
- Mudar para `Fica de fora` a tira das telas ativas, e a reabertura traz tudo de volta.

---

## F-PLN-08 — Visões, Filtros e Progresso do Mapa

| Recurso | Comportamento |
| :--- | :--- |
| **Agrupamento** | Por grupo (padrão) ou por status |
| **Filtros** | Status, alinhamento (`Divergem`, `Falta avaliar`) e "só o que falta eu avaliar". Estado na **URL** (`design-system.md` §10) |
| **Progresso** | "N de M categorias classificadas" (M exclui ocultas; "classificada" = status diferente de `Em discussão`) |
| **Lente `Minha visão`** | Destaca categorias em que falta a **minha** prioridade |
| **Lente `Casal`** | Destaca categorias que divergem |
| **Desktop** | Quadro com colunas de status e painel lateral da categoria |
| **Mobile** | Lista agrupada em cartões; detalhe em folha inferior |

**Critérios de aceite**
- Aplicar um filtro altera a URL, e o botão voltar do navegador desfaz o filtro.
- O progresso muda ao classificar uma categoria, sem recarregar.
- Em 320 px, nenhum cartão exige rolagem horizontal.

---

## Fora desta área e deste bloco
- **Caminhos Macro** e sua avaliação dupla: Bloco 2.2, especificados em `features/possibilidades-e-decisoes.md` (`D-033`) e exibidos na aba "Definições Base & Caminhos Macro" desta área.
- **Entrevista Guiada por IA** (`D-010`): v1.1+.
- **Roteiro fixo de uma tradição religiosa:** fora do produto na v1 (`D-026`).
- **Quizzes genéricos:** fora do produto.

## Pontos a validar no bloco
1. ~~Como a estimativa inicial é sobrescrita por cenário (F-PLN-05)~~: **resolvido em `D-032`** (sobrescrita por linha de cenário).
2. Se o catálogo inicial (F-PLN-02) está completo para vocês: revisar em uso real, sem custo, pois é editável.
