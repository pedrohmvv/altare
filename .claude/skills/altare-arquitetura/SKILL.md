---
name: altare-arquitetura
description: >-
  Camadas do Altare (domínio, aplicação, adaptadores, infraestrutura), limites entre módulos via
  public.py, CQRS leve, eventos, quando criar porta ou abstração. Use ao criar ou mover módulo, caso
  de uso, entidade, porta ou evento, ao decidir onde um código mora ou ao ver import cruzando camadas.
  Módulo novo nasce com CLAUDE.md.
---

# Arquitetura do Altare

## Docs a consultar
- `docs/engineering/architecture.md` §2 (camadas), §3 (limites pragmáticos), §4 (pastas), §6 (eventos), §9 (contratos `import-linter`), §12 (mapa do domínio), §13 (o que entra em cada bloco).
- `docs/engineering/stack.md` §3 (backend) e §11 (Bloco 0.1).
- `docs/product/decisions.md`: `D-022`, `D-027` (arquitetura), `D-039` (skills e `CLAUDE.md` por módulo).

## Princípios
1. **Dependências apontam para dentro.** Domínio só importa a biblioteca padrão e o `shared_kernel`; aplicação não importa adaptadores, infraestrutura nem `platform`. Quem quebra isso falha o build do `import-linter`, e é mais barato obedecer que discutir.
2. **A arquitetura existe por causa do agente (Nível 5).** O agente é só mais um adaptador de entrada chamando os mesmos casos de uso, com um `Actor`. Se um código só funciona chamado pelo HTTP, ele está no lugar errado.
3. **Rigor proporcional.** Entidade rica só onde há regra: orçamento e simulador, contadores de convidados, custo comparável, decisão, grafo de cronograma, contrato e parcelas. Cadastro simples (convidado, item de enxoval, interação) usa dataclass magra, sem comportamento.
4. **Leitura separada de escrita.** Comando passa por entidade e repositório; consulta (Home, comparador, quadro de orçamento, Dossiê, listagens) lê SQL direto e devolve DTO de leitura. Carregar agregado para montar tela cria join artificial no domínio.
5. **Porta só onde há variação ou E/S externa:** persistência (repositórios e `UnitOfWork`), `FileStorage`, `Clock`, `IdGenerator`, `PasswordHasher` e, no Nível 5, `LLMClient` e `Notifier`. Biblioteca pura não ganha porta.
6. **Um caso de uso = uma transação** (um `UnitOfWork`). Injeção de dependência manual; `Depends` do FastAPI só no adaptador.
7. **Derivar, não duplicar** (`architecture.md` §5): só se persiste fato. `Contratado`, `Realizado`, `Destravado` e custo comparável são calculados na leitura. Se você sentir vontade de "sincronizar" duas colunas, a segunda não deveria existir.
8. **Eventos síncronos só para consistência que não dá para derivar** (ex.: `ProposalDecided` conclui o marco). Efeito colateral (notificação, auditoria) é handler pós-commit. Sem broker nem fila.
9. **Módulo novo nasce com `CLAUDE.md`** na própria pasta (`D-039`). Use o modelo de `altare-docs-vivas`; ele aponta para `AGENTS.md` e `docs/`, sem repetir regras gerais.
10. **Decisão arquitetural vira `D-xxx` em `docs/product/decisions.md`**, com motivo e alternativas rejeitadas. Não existe pasta de ADRs. Desvio da arquitetura aprovada sem decisão registrada é bug de processo (`architecture.md`, cabeçalho).

## Checklist
- [ ] O arquivo está na camada certa (`domain/`, `application/commands|queries`, `adapters/`, `infrastructure/`)?
- [ ] Outro módulo é acessado só por `application/public.py` ou `domain/events.py`?
- [ ] Há regra de negócio numérica fora do domínio (em SQL de consulta, router ou componente)? Mover para função pura reutilizada.
- [ ] A abstração nova tem **duas implementações reais hoje** ou fala com E/S externa? Senão, apague.
- [ ] O caso de uso abre exatamente um `UnitOfWork`?
- [ ] Algum valor persistido poderia ser derivado?
- [ ] Mutação que o agente poderá pedir está num caso de uso reutilizável (e não presa a um router)?
- [ ] Módulo novo: `CLAUDE.md` criado e `import-linter` com o módulo registrado?
- [ ] Mudou uma regra desta arquitetura? Registre `D-xxx` antes.

## Bom / ruim
```python
# ruim: porta para biblioteca pura e repositório para cadastro magro
class SlugifierPort(Protocol): ...
class GuestNoteRepository(Protocol): ...   # dataclass sem regra

# bom: função pura no domínio; cadastro simples sem camada de entidade rica
def per_capita_total(unit_cents: int, headcount: int) -> int: ...
```
```python
# ruim: módulo budget importando o interior de contracts
from wedding.modules.contracts.infrastructure.repositories import ContractRepository

# bom: pela superfície pública
from wedding.modules.contracts.application.public import ContractedTotals
```
```python
# ruim: regra no router (o agente não consegue reutilizar)
@router.post("/installments/{id}/pay")
def pay(id: UUID, db: Session = Depends(get_db)):
    inst = db.get(Installment, id); inst.status = "Pago"; db.commit()

# bom: o router só traduz HTTP para o caso de uso
def pay(id: UUID, uc: PayInstallment = Depends(...), actor: Actor = Depends(...)):
    return uc.execute(PayInstallmentCommand(installment_id=id), actor)
```

## Limites e vizinhas
- Esta skill decide **onde as coisas moram e quem pode importar quem**. Convenções de rota, erro e DTO HTTP: `altare-backend-api`. Tabelas, mapeamento e migrations: `altare-banco-de-dados`.
- Ferramentas de agente, `ChangeProposal` e canais: `altare-agente-dados` (superfície) e `altare-engenharia-de-ia` (comportamento). Aqui só vale "o agente é um adaptador de entrada".
- Formato do `D-xxx` e modelo do `CLAUDE.md` de módulo: `altare-docs-vivas`.
- Estilo de código dentro de cada arquivo: `altare-escrita-de-codigo`. Estrutura do frontend: `altare-frontend`. Estrutura de apps e CI: `altare-monorepo`.

## Em aberto
- Mapeamento imperativo do SQLAlchemy pode atritar com o Pyright; o plano B (`to_domain`/`to_row` só nos agregados ricos) está em `architecture.md` §3 item 2 e §14. Só acione com atrito comprovado.
- Biblioteca de orquestração de agentes: adiada para o Bloco 5.1 (`architecture.md` §7).
