# Módulo `schedule`

> Regras gerais: leia `AGENTS.md` (raiz) e os docs abaixo. Este arquivo só traz o que é específico do módulo.

**Propósito:** é dono do cronograma do casamento: fases, marcos (criar, renomear, mover de fase, excluir e restaurar), dependências entre marcos, o estado que o casal marca (`Em andamento`, `Concluído`), responsável, categoria ligada, prazo-alvo manual, janelas (início, fim e unidade, em deslocamentos antes da data do casamento), nota e o histórico de estado, e calcula as datas, o prazo efetivo e a contagem regressiva na leitura. Não é dono do Mapa de Escopo nem da data do casamento (`wedding`), da lista de convidados (`guests`) nem de anexos (`files`): lê o que precisa por portas, nunca copia.

## Superfície pública
- `application/public.py`: ainda não existe; nasce quando outro módulo precisar ler o cronograma (o Centro de Comando, Bloco 4.2).
- `domain/events.py`: nenhum evento (o *dispatcher* está adiado, `D-060`).

Nada além disso pode ser importado por outro módulo (`architecture.md` §4; contrato 5 de §9).

## Invariantes
- Só se grava **fato**: o estado manual (`Em andamento`, `Concluído` ou nenhum), responsável, prazo-alvo, nota. `Bloqueado`, `Destravado`, `Atrasado`, `Opcional`, `Arquivado`, "libera", avisos e progresso por fase são **derivados na leitura** (`domain/derivation.py`, `architecture.md` §5) e nunca vão ao banco. Reabrir é apagar a marca.
- "A depende de B" está resolvida quando B está `Concluído`, arquivado (categoria `Fica de fora`) ou opcional (`Talvez`); não é transitiva. Categoria `Em discussão` bloqueia o marco com o motivo "Aguardando classificar a categoria no Mapa de Escopo". Categoria oculta, de grupo oculto ou excluída conta como `Fica de fora` (`F-CRN-04`).
- O estado manual vence o derivado e nunca muda sozinho: `Concluído` não é desfeito por uma dependência reaberta; o marco ganha o aviso `depends_on_unresolved` (todo `Concluído` com predecessor não resolvido, reaberto ou nunca concluído). "Libera" não lista os arquivados.
- Marcar `Em andamento` ou `Concluído` num marco com algo aguardando (calculado sem a marca manual atual, então vale também saindo de `Concluído`) exige `ignore_block` (a confirmação é da tela); sem ele, `422 milestone_blocked`. O histórico (`milestone_changes`) guarda o estado antes e depois, o perfil e se o bloqueio foi ignorado; só mudança real vira linha.
- "Hoje" é o dia em Brasília, pelo `Clock` injetado.
- **O prazo manual (`target_date`) é o único prazo gravado; o resto se deriva** (`domain/derivation.py`, `domain/windows.py`). No Modo Com Data (data do casamento `Definida` e exata, lida pela porta `WeddingDateReader` a cada leitura), cada marco com janela ganha `window_start` e `window_end` (data menos o deslocamento; meses respeitam o fim do mês, semanas são 7 dias) e o prazo efetivo (`effective_target`) é o manual ou, sem ele, o fim da janela. No Modo Sem Data nada é calculado e o efetivo é só o manual. `days_left` (negativo é passado, 0 é hoje) e `Atrasado` olham o efetivo e valem só para marco não concluído e não arquivado. A função de cálculo é total: uma data que estoura o calendário (a data exata do casamento não tem o ano validado no `wedding`) não calcula janela, não derruba a leitura.
- **Janela:** `window_start_before >= window_end_before >= 0`, no máximo 120 meses ou 520 semanas, em três camadas (domínio, `CHECK` do banco da `0010` e teste); `0` e `0` é o dia do casamento. `window_edited` (`0012`) é o único registro de que o casal editou: sem ele, a janela é a "sugestão genérica" da semente (`is_suggestion`). `PUT .../window` substitui os três valores, exige a `version` do marco, vale em qualquer modo, em marco arquivado e em marco sem janela, e nunca mexe no prazo manual; a primeira edição conta mesmo com os mesmos deslocamentos e repetir uma janela já editada não grava. Não há remover janela nem "voltar à genérica" ainda.
- **A prévia de mudar a data** (`GET /schedule/date-preview`, só leitura) deriva o cronograma duas vezes, com a data de hoje e com a hipotética (ano de 2000 a 2100; sem `exact` é o cenário Sem Data), e compara. `changes` traz só marcos ativos, não concluídos, com janela e sem prazo manual cujas datas mudam; `manual_kept` conta os com prazo manual (o prazo deles não muda, a janela calculada acompanha a data) e `newly_overdue` os que passam a Atrasado. Concluídos e arquivados ficam fora de todas as contagens.
- A ligação com o Mapa é pelo **id** da categoria (catálogo do `wedding`, ids `uuid5` fixos), nunca pelo nome; a chave estrangeira física para `scope_categories` segue o precedente de `scope_references.file_id` (FK entre módulos no banco, mas o código só cruza por `public.py`).
- **O grafo de dependências é sempre acíclico** (`domain/graph.py`, função pura; `F-CRN-03`, regra 2): trocar os predecessores de um marco (`PUT .../dependencies`, que substitui o conjunto) recusa a auto-dependência (`self_dependency`) e o ciclo (`dependency_cycle`, com o caminho `C → A → B → C` em `data.path` e no texto). Repetir o conjunto atual não grava nada; a revisão das dependências (`dependencies_revision`) sobe a `version` do marco, como o `members_revision` do `guests`.
- **Excluir marco é lógico e leva junto, com o mesmo carimbo (`deleted_at`), os vínculos em que ele aparece, nos dois sentidos.** Restaurar traz de volta o marco, no fim da fase em que estava, e só os vínculos com aquele carimbo cuja outra ponta está viva e que hoje não fecham ciclo; o que ficou de fora vem em `left_out` (id, título e sentido). Um vínculo tirado à mão tem o carimbo do instante em que saiu e nunca volta por engano. O histórico de estado permanece.
- **Fases: criar, renomear e reordenar; não há excluir fase** (`D-080`). Reordenar exige exatamente as fases vivas (`invalid_phase_order`) e sobe a `version` só de quem mudou de posição.
- Marco novo nasce no fim da fase, sem estado marcado nem prazo; mudar de fase leva o marco para o fim da nova, sem tocar nas dependências. Título obrigatório (1 a 120 caracteres; fase, 1 a 60), em três camadas: domínio, `CHECK` do banco (`0011`) e teste.
- A categoria que o casal liga vem do Mapa pela porta `CategoryReader` (id; não oculta); `category_options` no agregado lista as visíveis na ordem do Mapa, mais as ocultas que algum marco já tem ligadas. Manter a categoria já ligada, mesmo oculta, não é uma nova ligação.
- Toda escrita envia a `version` do marco (ou da fase) que a tela viu, **exceto reordenar fases**: a lista é uma permutação exata das fases vivas, o último a gravar vence sem incoerência e uma fase criada no meio dá `invalid_phase_order` (sem 409 no contrato). Excluir e restaurar um marco sobem a `version` dos dependentes cujo conjunto de predecessores muda. Divergir dá `409 version_conflict`; autoria e perfil vêm da sessão.
- Nada do casamento é preenchido por padrão (`AGENTS.md` §2): responsável `Ambos` e nenhum prazo na semente; as janelas sugeridas são genéricas.

## Dependências permitidas
- Não importa nenhum outro módulo: o Mapa de Escopo entra pela porta `CategoryReader` e a data do casamento pela `WeddingDateReader`, que o `bootstrap` liga ao `application/public.py` do `wedding`.
- Camadas: domínio só usa a biblioteca padrão e o `shared_kernel` (`architecture.md` §2 e §9).

## Docs
- Features: `docs/product/features/cronograma.md` (`F-CRN-01` a `F-CRN-10`; este módulo cobre `F-CRN-01` a `F-CRN-05`).
- Decisões: `D-031`, `D-026`, `D-067`, `D-072`, `D-080` (plano do bloco), `D-081` e `D-082` (este módulo).
- Arquitetura e domínio: `docs/engineering/architecture.md` §4, §5 (derivar, não duplicar) e §10 (histórico); `docs/engineering/stack.md` §4.
- Web: `apps/web/src/features/schedule/` (nasce com o front do bloco).

## Em aberto
- O histórico de estado é gravado, mas ainda não há rota para lê-lo.
- Prazo das tarefas avulsas, calendário e remover a janela ou voltar à genérica não existem ainda (PRs seguintes do bloco).

## Como testar
- `make test-api` e `make lint-api` na raiz.
- Domínio: pytest e Hypothesis (`test_windows.py`, `test_derivation.py`, `test_graph.py` e a máquina de estados, que sorteia criar, mover, excluir, restaurar, trocar dependências com e sem ciclo, definir a data do casamento, editar janelas e pedir a prévia). Aplicação: *fakes* das portas (`tests/modules/schedule/conftest.py`, com o catálogo inicial inteiro em memória). HTTP e migração: SQLite migrado de verdade, para a semente existir.
- Contratos de import: `import-linter` no `make lint-api`.
