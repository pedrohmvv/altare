---
name: altare-backend-api
description: >-
  Convenções da API FastAPI do Altare: rotas /api/v1, problem+json, bloqueio otimista (version e 409),
  DTOs Pydantic, operationId, paginação, autoria vinda da sessão. Use ao criar ou alterar rota,
  router, schema, mapper, tratamento de erro ou contrato OpenAPI em apps/api.
---

# API do Altare (FastAPI)

## Docs a consultar
- `docs/engineering/architecture.md` §8 (convenções de API e de erros), §3 itens 3 e 5, §10 (`version`, exclusão lógica).
- `docs/engineering/stack.md` §3 (FastAPI, Pydantic v2, uploads), §6 (autoria e perfis).
- Specs de cada área em `docs/product/features/` para nomes de ação e regras que viram `422`.

## Princípios
1. **O router é um adaptador fino.** Valida a entrada, chama **um** caso de uso e traduz o resultado. Regra de negócio no router não é reaproveitável pelo agente do Nível 5 nem testável sem HTTP.
2. **Autoria vem da sessão, nunca do corpo.** Nenhum schema de entrada tem `created_by`, `author`, `profile` de quem age. O `Actor` é montado da sessão e passado ao caso de uso. Campo de autoria no corpo permite se passar pelo outro perfil.
3. **Ação de domínio é sub-recurso, não verbo solto.** `POST /possibilities/{id}/decide`, `POST /installments/{id}/pay`, `POST /budget-scenarios/{id}/activate`. CRUD continua REST. Isso mantém um caso de uso por rota e um `operationId` legível.
4. **`operationId` estável por rota** (ex.: `decide_possibility`). Ele vira o nome da função do cliente TypeScript; renomear quebra o frontend e o drift check acusa.
5. **Dinheiro em centavos inteiros, campos com sufixo `_cents`.** Datas `DATE` em ISO (`2026-10-26`), instantes ISO-8601 UTC, IDs UUID em string. Formatação `R$` é do frontend.
6. **Erro é contrato:** `application/problem+json` (RFC 9457) com `code` estável de máquina e `detail` em pt-BR acionável. Nunca vazar stack trace, SQL, caminho de arquivo ou nome de tabela.
7. **Concorrência otimista:** toda atualização envia `version`; divergência responde `409` com `code: "version_conflict"`. Sem `last write wins` silencioso entre dois logins no mesmo registro.
8. **Paginação `limit`/`offset`** (volume pequeno), sem cursor. Filtros e ordenação como query params tipados.
9. **O OpenAPI é o contrato único.** Schemas só refletem o que o frontend e o agente precisam; mudar schema é mudar contrato.

## Mapeamento de erros
| Origem | HTTP | `code` (exemplos fictícios de formato) |
| :--- | :--- | :--- |
| `NotFound` | 404 | `not_found` |
| `Forbidden` | 403 | `forbidden` |
| `DomainRuleViolated` | 422 | `category_out_of_scope`, `proposal_already_decided` |
| `Conflict` | 409 | `duplicate_contact` |
| `VersionConflict` | 409 | `version_conflict` |
| Validação Pydantic | 422 | `validation_error` com campo e mensagem por campo |
| Não autenticado | 401 | `unauthenticated` |

O erro de domínio carrega o `code`; o `detail` em pt-BR sai de um único lugar (mapa de mensagens), não de strings espalhadas. O agente (Nível 5) lê estes mesmos erros: `detail` precisa dizer o que corrigir (ver `altare-agente-dados`).

## Checklist
- [ ] Rota sob `/api/v1`, substantivo no plural, ação como sub-recurso com `POST`?
- [ ] `operationId` definido e único?
- [ ] Router chama exatamente um caso de uso; sem `Session`, SQL ou regra dentro dele?
- [ ] Schema de entrada sem campo de autoria e sem `float` de dinheiro?
- [ ] Atualização exige `version` e documenta o `409`?
- [ ] Todo erro de domínio mapeado para status e `code` estável, com `detail` em pt-BR?
- [ ] Erro `422` do Pydantic devolve o campo, para o formulário (React Hook Form) marcar o input?
- [ ] Upload: `POST /files` multipart; download `GET /files/{id}` autenticado com `Content-Disposition`; validação em `altare-seguranca-privacidade`?
- [ ] Mutador exige o header anti-CSRF e cookie de sessão?
- [ ] Teste de adaptador com `TestClient` e *snapshot* do OpenAPI atualizado?
- [ ] Rodou a geração de tipos e o frontend compila (`altare-monorepo`)?

## Bom / ruim
```python
# ruim: autoria no corpo, verbo solto, regra no router, erro cru
@router.post("/payInstallment")
def pay(body: PayBody):                    # body.paid_by_profile vem do cliente
    if body.amount > 0: ...
    raise HTTPException(400, str(exc))     # vaza detalhe interno

# bom
@router.post("/installments/{installment_id}/pay", operation_id="pay_installment")
def pay(installment_id: UUID, body: PayInstallmentIn,
        uc: PayInstallment = Depends(...), actor: Actor = Depends(current_actor)):
    return uc.execute(PayInstallmentCommand(installment_id, body.paid_cents, body.version), actor)
```
```json
{ "type": "about:blank", "title": "Conflito de versão", "status": 409,
  "code": "version_conflict",
  "detail": "Este registro foi alterado por outra pessoa. Recarregue e tente de novo." }
```

## Limites e vizinhas
- Camadas, `public.py`, quando criar porta: `altare-arquitetura`.
- Colunas `version`, `deleted_at` e índices por trás destas rotas: `altare-banco-de-dados`.
- Cookie, sessão, CSRF, rate limit e validação de upload: `altare-seguranca-privacidade`.
- Geração `openapi-typescript`, drift e CI: `altare-monorepo`. Consumo no frontend: `altare-frontend`.
- Tools de agente chamam os mesmos casos de uso, não as rotas: `altare-agente-dados`.
- Testes de rota e de OpenAPI: `altare-testes-qa`.
