---
name: altare-seguranca-privacidade
description: >-
  Segurança e privacidade do Altare: LGPD, dados de convidados, login próprio (argon2, sessão server-
  side, cookie, CSRF, rate limit), validação de upload, segredos, logs sem dado pessoal, dado enviado
  a terceiros. Use ao mexer em login, sessão, permissões, upload, exportação, logs, segredos ou ao
  enviar dado do casal para fora.
---

# Segurança e privacidade do Altare

## Docs a consultar
- `docs/engineering/stack.md` §3 (autenticação própria, arquivos, validação de upload), §6 (perfis e sessão), §12 (risco de auth própria).
- `docs/engineering/architecture.md` §8 (cookie, CSRF, erros sem vazamento), §10 (exclusão lógica).
- `docs/product/decisions.md`: `D-002` (uso pessoal), `D-008`, `D-020`, `D-021`, `D-038` (exportação e minimização no Dossiê).
- `docs/product/features/centro-de-comando.md` F-CCD-10 (exportar todos os dados) e `docs/product/features/convidados-enxoval-e-dia-d.md` F-DOS-05 (convidados no Dossiê).

## LGPD: o que vale hoje
O Altare é de uso pessoal do casal (`D-002`). A Lei 13.709/2018, art. 4º, I, exclui o tratamento feito por pessoa natural para fins exclusivamente particulares e não econômicos; em princípio, **hoje ela não se aplica**. Isto **não é parecer jurídico**. Tratamos a LGPD como **boa prática agora** (é barato desde o início e caro de retrofitar) e como **obrigação** se o produto abrir para outros casais ou ganhar fim econômico (hipótese futura, `altare-gtm-pricing`). Nesse caso, reabra esta skill e registre `D-xxx`: base legal, encarregado, retenção e direitos do titular.

## Princípios
1. **Minimização.** Só colete o que a spec pede. O Dossiê do Dia D mostra contagens e restrições alimentares (nome e restrição), **sem telefone, e-mail ou endereço de convidado** (`D-038`). Dado de terceiro (convidado, fornecedor) é o mais sensível do produto: o casal é o controlador, o convidado é o titular.
2. **Autenticação própria e mínima.** Dois usuários criados por CLI, **sem cadastro público**. Senha com `argon2-cffi`; sessão **server-side** em tabela; cookie `HttpOnly`, `SameSite=Lax` e `Secure` em produção; **sem JWT em localStorage**. Rate limit simples no login.
3. **CSRF por header customizado** em todo método mutador, além do `SameSite`. Rota mutadora sem o header é rejeitada.
4. **Autoria vem da sessão**, nunca do corpo (`altare-backend-api`). É controle de acesso e trilha: sem isso um perfil age como o outro.
5. **Erros não vazam.** `problem+json` sem stack trace, SQL, caminho ou existência de conta ("usuário ou senha inválidos", sempre igual).
6. **Upload é entrada hostil.** Valide tipo MIME **e assinatura real** (PDF e imagem), tamanho máximo e hash SHA-256 (dedupe). Guarde fora da pasta pública com nome por hash e sirva por endpoint **autenticado**. Nunca use o nome enviado como caminho.
7. **Segredos só em ambiente** (`SECRET_KEY`, `DATABASE_URL`, credenciais de storage, LLM e WhatsApp). Nunca no repositório, em exemplo ou em log. `.env` no `.gitignore`; só `.env.example` sem valores reais.
8. **Logs sem dados pessoais.** Registre ids, códigos e contagens, não nome, telefone, e-mail, endereço, texto de mensagem nem conteúdo de PDF. A busca global já exige isso (F-CTT-10).
9. **Dado em terceiros é decisão consciente.** Enviar a LLM, ao WhatsApp, à hospedagem e ao storage S3 é compartilhar. Mande o mínimo, nunca dados de convidados sem necessidade, e registre o fornecedor em `## Em aberto` até decidir.
10. **Direito de levar e de apagar.** Exportação completa já está prevista (`.zip` com `dados.json`, `arquivos/` e `LEIA-ME.txt`, **sem senhas nem sessões**, `D-038`). Exclusão lógica serve ao uso diário; apagar de fato exige purga (implementação em `altare-banco-de-dados`).

## Checklist
- [ ] Campo novo com dado pessoal de terceiro é realmente necessário? Onde aparece (Dossiê, exportação, logs, LLM)?
- [ ] Rota nova exige sessão e, se mutadora, o header anti-CSRF?
- [ ] Nenhuma mensagem de erro revela se um usuário, e-mail ou registro existe?
- [ ] Upload: MIME + assinatura + tamanho + hash, armazenado fora do público, servido autenticado?
- [ ] Segredo novo lido de variável de ambiente e documentado em `.env.example` sem valor?
- [ ] Log novo sem dado pessoal?
- [ ] Dado vai para LLM, WhatsApp ou outro terceiro? Está minimizado e listado?
- [ ] Exportação nova omite senha, hash e sessão?
- [ ] Mudou algo que a LGPD exigiria se o produto abrir para outros casais? Anote em `## Em aberto`.

## Bom / ruim
```python
# ruim: confia no nome do arquivo e revela se o usuário existe
path = UPLOAD_DIR / file.filename
if not user: raise HTTPException(404, "Usuário não encontrado")

# bom: hash como nome, tipo validado pela assinatura, resposta uniforme
if not is_pdf_or_image(content_bytes): raise DomainRuleViolated("invalid_file_type")
stored = storage.put(content_bytes, name=sha256(content_bytes).hexdigest())
raise InvalidCredentials()   # sempre a mesma mensagem, exista ou não a conta
```
```text
ruim: log.info("mensagem de %s: %s", telefone, texto)
bom : log.info("whatsapp.recebido", extra={"user_id": uid, "message_id": mid, "chars": len(texto)})
```

## Limites e vizinhas
- Esta skill define **a política** (o que proteger, minimizar, exportar). A **implementação** em colunas, exclusão lógica e comando de purga é de `altare-banco-de-dados`.
- Formato de rotas, `problem+json` e `403`/`401`: `altare-backend-api`. Cookie e sessão na camada de plataforma: `altare-arquitetura`.
- Segredos e variáveis no pipeline e no deploy: `altare-devops`. Testes de segurança: `altare-testes-qa`. Itens de revisão: `altare-code-review`.
- Dados que o assistente envia ao modelo e ao WhatsApp, e o vínculo do número: `altare-agente-dados` e `altare-engenharia-de-ia`.
- Métricas de uso: o que pode ser medido sem expor dados de casal e de convidados (nada sai do banco para rastreadores de terceiros) é de `altare-analytics-metricas`; a regra de minimização continua desta skill.

## Em aberto
- **Backup automático e implantação** são requisito de hospedagem ainda não decidido (`D-038`, `stack.md` §9): sem backup, o risco de perda de dados do casal fica registrado.
- Provedor de nuvem, Postgres gerenciado e storage S3-compatível (candidatos em `stack.md` §9) definem onde os dados ficam e o contrato com o operador.
- Provedor de LLM e conta do WhatsApp Business: quais dados saem e sob que termos (Bloco 5.1 e `OQ-IA-001`).
- Passkeys/WebAuthn: evolução do login após o deploy (`stack.md` §10).
- Purga definitiva de registros e política de retenção: indefinidas; só viram obrigação se o produto abrir para outros casais.
