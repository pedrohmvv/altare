---
name: altare-ui-ux
description: >-
  UI/UX do Altare: fluxos do casal, heurísticas de usabilidade aplicadas ao produto, postura desktop (planejar junto) versus mobile (consultar e capturar), navegação das 7 áreas, onboarding do casamento novo, estados vazio, carregando, erro e desabilitado, confirmações destrutivas e a estrutura que cada mensagem deve ter. Use sempre que for desenhar ou revisar uma tela, fluxo, formulário, navegação, estado de interface ou o ícone flutuante do assistente, e ao detalhar uma feature nova, mesmo que o pedido seja só 'como essa tela deveria funcionar' ou 'o que mostrar quando não tem dado'. NÃO use para tokens, cor e primitivos (use altare-design), estrutura de código (use altare-frontend), checklist de acessibilidade (use altare-acessibilidade) nem para escrever as palavras (use altare-conteudo-copy: aqui só se define o que a mensagem precisa dizer).
---

# UI/UX do Altare

## Docs a consultar
- `docs/design/experience.md`: §1 jornada, §3 navegação e comportamento desktop e mobile, §4 fluxos 1 a 8.
- `docs/design/design-system.md`: §10 padrões (formulário, detalhe lateral, filtros, confirmação, feedback) e §10.1 navegação.
- `docs/design/identity.md` §9 (estados de interface) e `docs/design/visual-direction.md` §2 (densidade e tom das divergências).
- `docs/product/features/<area>.md` da tela (campos, regras e critérios de aceite); `centro-de-comando.md` F-CCD-03, F-CCD-08 e F-CCD-09.
- `docs/product/jobs.md` (o trabalho que a tela serve). Decisões: `D-003`, `D-012`, `D-021`, `D-038`, `D-042`.

## Princípios
1. **Toda tela define as duas posturas** (`D-003`). Desktop é planejar junto: comparação lado a lado, simulador, detalhe lateral. Mobile é consultar e capturar: próximo passo, custo comparável, abrir WhatsApp, anexar PDF, registrar nota. O que só cabe no desktop vai para "Mais" no celular sem perder a função.
2. **Navegação aprovada:** 7 áreas mais o **Assistente** como 8ª, separado ao fim (`D-050`); no mobile, barra inferior com 4 destinos mais "Mais", que também abre o Assistente, e o "+ Registrar Rápido" (`design-system.md` §10.1, `D-025`). O Registrar Rápido reaproveita os formulários da área e abre cada um em até 2 toques (`D-038`). Não invente uma 9ª área sem decisão registrada.
3. **Capturar em segundos, decidir com calma.** Registrar um contato ou anexar um PDF nunca exige preencher campo opcional; a decisão (comparar, registrar motivo) é que ganha espaço e tempo.
4. **Divergência é convite, não erro.** Quando as avaliações de `Noivo` e `Noiva` diferem, a interface sugere conversar; nunca acusa. Acordo e atenção usam `consensus-*` e `attention-*`, nunca vermelho (`altare-design`).
5. **O outro vê na hora, mas cada um edita só o seu.** Avaliações são visíveis de imediato e cada pessoa altera apenas a própria coluna (`D-021`). A lente (`Visão do Casal` / `Minha visão`) muda foco, não autoria.
6. **Detalhe sem sair da lista.** Informação extensa (PDF, histórico, avaliação) abre em painel lateral no desktop e em folha inferior no mobile. Filtros são *chips* com estado na URL.
7. **Custo Real Comparável em primeiro plano.** Onde há preço, o total comparável vem à frente do preço de capa, para a opção "barata" não enganar.
8. **Reconhecer, não lembrar.** Estado sempre em texto completo ("Aguardando avaliação da Noiva"), nunca só ícone ou cor. "Bloqueado" explica o que falta ("Aguardando: …").

## Estados de interface
| Estado | O que a tela faz | Armadilha |
| :--- | :--- | :--- |
| Vazio | Arco ou ramo em linha, uma frase que diz o que é e por que importa, **uma** ação | Tela em branco ou "nenhum registro" sem saída |
| Carregando | *Skeleton* do formato final | *Spinner* de tela cheia |
| Erro | Mensagem acionável com ação de tentar de novo; o formulário **não perde** o que foi digitado | Jargão técnico, `stack trace`, "Erro 500" |
| Sucesso | *Toast* de 4 s, com "Desfazer" quando seguro | Diálogo de "salvo com sucesso" |
| Desabilitado | Acompanha a dica do motivo | Botão cinza sem explicação |

- **Validar ao sair do campo e ao enviar**; erro junto do campo, em argila, com ícone e texto acionável. Obrigatoriedade escrita ("obrigatório"), sem asterisco.
- **Confirmação destrutiva só quando a ação não for desfazível.** O diálogo explica a consequência e que o registro **fica recuperável** (exclusão lógica, `D-022`). Ação segura usa *toast* com "Desfazer", sem diálogo.

## Estrutura de uma mensagem (as palavras são de `altare-conteudo-copy`)
Toda mensagem de erro, aviso ou estado vazio responde, nesta ordem e só no que couber:
1. **O que houve** (fato, sem culpa); 2. **por que importa** (efeito para o casal, se não for óbvio); 3. **o que fazer** (a ação, que também é um botão).

## Onboarding: o "casamento novo" (`F-CCD-09`)
- Não há tutorial nem *tour*. Sem dado nenhum, a Visão Geral mostra **um primeiro passo** ("Comece pelas Definições Base") e cartões vazios que dizem o que falta e onde registrar.
- **Nunca preencha com dado inventado** (`AGENTS.md` §2): sem data, convidados ou orçamento, o cartão fica vazio com orientação. O Cronograma funciona em *Modo Sem Data*.
- O produto aprende o casal conforme ele preenche; não há configuração prévia.

## Ícone flutuante do assistente (`D-042`, `D-050`): padrão de interação
- Fica no canto inferior direito das demais áreas, **recolhido por padrão**, e expande para um chat que já conhece a tela atual. **Nunca abre sozinho** e nunca cobre a tabela comparativa nem o conteúdo principal.
- Resposta é de leitura livre. Qualquer mudança aparece como **prévia com Confirmar e Rejeitar** explícitos (`D-008`); o assistente não "faz e avisa depois".
- **A casca já existe (`D-050`):** o ícone, oculto na própria área Assistente, e a área **Assistente** na navegação. O painel de chat de verdade é do Bloco 5.3; até lá o ícone abre um painel provisório que diz, com calma, que o assistente ainda não está disponível.

## Checklist (tela ou fluxo novo)
- [ ] Li o doc da área e o fluxo em `experience.md` §4; o job da tela está claro.
- [ ] Desktop e mobile descritos; o que vai para "Mais" no celular está dito.
- [ ] Estados vazio, carregando, erro e desabilitado desenhados.
- [ ] Destrutivo: tem confirmação com consequência, ou "Desfazer" se for seguro.
- [ ] Nenhuma ação depende de IA (`D-005`): o fluxo manual está completo sozinho.
- [ ] Nenhum dado do casamento inventado nos exemplos.
- [ ] Mensagens seguem a estrutura acima e os textos foram entregues a `altare-conteudo-copy`.
- [ ] Verificação de `altare-acessibilidade` prevista (teclado, foco, 320 px).

## Limites e vizinhas
- Cor, fonte, ícone e ornamento: `altare-design`. Estrutura de componentes, estado e rotas: `altare-frontend`.
- As palavras, o tom e os formatos: `altare-conteudo-copy`. Foco, teclado, contraste e leitor de tela: `altare-acessibilidade`.
- Se a tela vale a pena e em que ordem construir: `altare-produto`. Registrar decisão de fluxo: `altare-docs-vivas`.

## Em aberto
- Detalhamento do Nível 5, busca aproximada e WhatsApp: `OQ-IA-001`, itens 2 a 4.
- O "+ Registrar Rápido" no mobile também é um botão flutuante (`design-system.md` §9, `QuickAddFab`) e disputa o canto inferior direito com o ícone do assistente, que já existe (`D-050`). A convivência dos dois se decide no Bloco 3.1 (`OQ-IA-001`, item 5).
