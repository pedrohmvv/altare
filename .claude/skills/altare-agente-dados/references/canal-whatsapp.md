# Canal WhatsApp do assistente (Bloco 5.3, `D-042`)

Leia ao implementar o canal. Tudo aqui é **proposta de implementação**, não decisão: o provedor e o custo seguem em aberto (`OQ-IA-001`, `docs/engineering/stack.md` §10). Os limites e nomes da API oficial do WhatsApp Business mudam; **confirme na documentação vigente da Meta antes de codar**.

## Papel do canal
Conversa entre **o casal e o Altare**. Nunca envia mensagem a fornecedor e nunca lê conversas privadas (`docs/product/vision.md` §5, `docs/product/scope.md` §4). O canal é um adaptador de entrada fino (`architecture.md` §7 item 7): recebe texto, chama o núcleo e devolve a resposta.

## Vínculo de identidade do número
- Cada número fica vinculado a **um** usuário (`Noivo` ou `Noiva`), criado por ação autenticada no app (por exemplo, gerar um código que a pessoa envia pelo WhatsApp), nunca por texto livre na conversa.
- Número desconhecido recebe uma resposta neutra e **nenhum dado**. Não confirme nem negue a existência de conta.
- O `Actor` é montado do número vinculado: `Actor(kind="agent", on_behalf_of=<perfil>)`. A mensagem não pode alterar o perfil.
- Desvincular e trocar de número são ações do app, com registro (`created_by` da sessão).

## Webhook de entrada
- **Verificação de origem:** valide a assinatura HMAC-SHA256 do corpo bruto contra o segredo do app (cabeçalho `X-Hub-Signature-256`) antes de processar. Sem assinatura válida, descarte com `401`.
- **Verificação do endpoint** (desafio `hub.challenge` na ativação) com token configurado por variável de ambiente, nunca no repositório.
- **Idempotência:** o provedor reentrega. Use o identificador da mensagem recebida como parte da chave de idempotência (`SKILL.md`, princípio 4).
- **Responda rápido** (confirmação ao provedor) e processe a mensagem fora do ciclo da requisição; a resposta ao usuário sai como mensagem nova. Não há fila externa na stack (`stack.md` §2); use execução em processo e trate perda em reinício como risco aceito até decidir o agendador (Bloco 5.2).
- O endpoint precisa de URL pública com HTTPS: **exige o app na nuvem** (`stack.md` §9), o que não vale para o uso local dos Níveis 0 e 1.

## Janela de atendimento e modelos
- Mensagens livres só podem ser enviadas dentro da janela de atendimento (em geral 24 horas após a última mensagem do usuário). Fora dela, só **modelos aprovados** pelo provedor.
- Como o assistente responde ao casal, a conversa começa por eles e a janela normalmente está aberta. Notificações proativas (Bloco 5.2, `D-013`) fora da janela exigem modelo aprovado e custo por conversa: tema do Bloco 5.2, não deste canal.

## Confirmação de `ChangeProposal`
- A prévia da proposta é enviada como texto curto: o que vai mudar, valores e quem é afetado, com o `detail` em pt-BR.
- Confirmação por **resposta explícita** ou **botão de resposta** (a API limita a poucos botões por mensagem; confirmar e rejeitar cabem). Resposta ambígua ("ok, talvez") **não** confirma.
- A confirmação chama `ApproveChangeProposal` com o `Actor` humano do número vinculado e `proposed_by = agent`. Proposta tem validade (`Expirada`, `architecture.md` §12); aprovar proposta expirada falha com erro compreensível.
- Mutação de alto impacto (excluir, mudar o cenário ativo, registrar decisão) pode exigir confirmar no app. Defina a lista no detalhamento do Nível 5 (`OQ-IA-001` item 2).

## Limites práticos
- Tamanho máximo de texto por mensagem e formatos de mídia: confira na documentação vigente; respostas longas viram resumo mais link para a tela do app.
- Áudio, imagem e PDF recebidos só entram no fluxo se o Bloco 5.1 (extrator) decidir tratá-los; até lá, responda que o canal aceita texto.
- Dados enviados ao provedor do WhatsApp e ao LLM são dados em terceiros: minimize o conteúdo (`altare-seguranca-privacidade`). Não registre texto de mensagens em logs.
- Limites de taxa de envio e custo por conversa: levantar antes de ligar o canal (`stack.md` §10).
