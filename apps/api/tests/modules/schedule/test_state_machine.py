"""O cronograma sob qualquer sequência de operações (F-CRN-01, F-CRN-03, F-CRN-04 e F-CRN-05).

O Hypothesis sorteia classificar e ocultar categorias no Mapa de Escopo, marcar e reabrir, criar,
mover, excluir e restaurar marcos, trocar as dependências (com e sem ciclo), criar, renomear e
reordenar fases e passar os dias, sobre o catálogo inicial inteiro (29 marcos e as suas 31
dependências), definir a data do casamento (qualquer uma, com e sem `Definida`), editar a janela de
um marco (dentro e fora dos limites), pedir a prévia de mudar a data, criar, mudar de estado (com e
sem a permissão dos itens em aberto), excluir e restaurar avulsas, e adicionar, marcar, editar,
remover e reordenar (boa e ruim) itens do checklist de marcos e de avulsas, e confere depois de cada
passo as invariantes: a avulsa nunca aparece em "libera", bloqueios, dependências nem avisos de
marco algum, o item nunca muda o estado nem a `version` do dono, "feito" fica entre 0 e o total, as
posições ficam densas depois de reordenar, `checklist_open_items` só vem com item em aberto, o
prazo da avulsa segue a regra e a lista de avulsas segue a ordem da chave, o anexo (link ou arquivo)
de marco e de avulsa some com o dono excluído e volta com ele sem se apagar, anexar e remover nunca
mudam a `version` nem o estado do dono, só o autor remove (o outro perfil recebe `Forbidden` e nada
muda), o dono excluído barra anexar e remover, e o resto: o prazo
efetivo é o manual ou o fim da janela calculada, o concluído e o
arquivado não têm contagem nem atraso, só a janela nunca editada é "sugestão", o grafo é sempre
acíclico, marco excluído não aparece em lugar nenhum, o concluído não muda sozinho, arquivado e
opcional nunca bloqueiam, bloqueado sempre diz o que aguarda, restaurar logo depois de excluir
devolve as mesmas dependências e a leitura é determinística.
"""

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from functools import wraps
from itertools import pairwise
from uuid import UUID

import pytest
from hypothesis import assume, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule
from tests.conftest import FixedClock
from tests.modules.schedule.catalog import MARCOS, categoria_id, marco_id
from tests.modules.schedule.conftest import NOIVA, NOIVO, World

from wedding.modules.schedule.application.commands.add_checklist_item import (
    AddChecklistItemCommand,
)
from wedding.modules.schedule.application.commands.add_file_attachment import (
    AddFileAttachmentCommand,
)
from wedding.modules.schedule.application.commands.add_link_attachment import (
    AddLinkAttachmentCommand,
)
from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneStateCommand,
)
from wedding.modules.schedule.application.commands.change_task_state import ChangeTaskStateCommand
from wedding.modules.schedule.application.commands.create_milestone import CreateMilestoneCommand
from wedding.modules.schedule.application.commands.create_phase import CreatePhaseCommand
from wedding.modules.schedule.application.commands.create_task import CreateTaskCommand
from wedding.modules.schedule.application.commands.delete_milestone import DeleteMilestoneCommand
from wedding.modules.schedule.application.commands.delete_task import DeleteTaskCommand
from wedding.modules.schedule.application.commands.remove_attachment import (
    RemoveAttachmentCommand,
)
from wedding.modules.schedule.application.commands.remove_checklist_item import (
    RemoveChecklistItemCommand,
)
from wedding.modules.schedule.application.commands.rename_phase import RenamePhaseCommand
from wedding.modules.schedule.application.commands.reorder_checklist import (
    ReorderChecklistCommand,
)
from wedding.modules.schedule.application.commands.reorder_phases import ReorderPhasesCommand
from wedding.modules.schedule.application.commands.restore_milestone import (
    RestoreMilestoneCommand,
)
from wedding.modules.schedule.application.commands.restore_task import RestoreTaskCommand
from wedding.modules.schedule.application.commands.set_milestone_dependencies import (
    SetMilestoneDependenciesCommand,
)
from wedding.modules.schedule.application.commands.update_checklist_item import (
    UpdateChecklistItemCommand,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestoneCommand
from wedding.modules.schedule.application.commands.update_milestone_window import (
    UpdateMilestoneWindowCommand,
)
from wedding.modules.schedule.application.commands.update_task import UpdateTaskCommand
from wedding.modules.schedule.application.dto import (
    AttachmentDto,
    ChecklistItemDto,
    MilestoneDto,
    ScheduleDto,
    TaskDto,
)
from wedding.modules.schedule.application.queries.preview_date_change import (
    PreviewDateChangeCommand,
)
from wedding.modules.schedule.domain.errors import (
    ChecklistOpenItems,
    DependencyCycle,
    InvalidChecklistOrder,
    InvalidMilestoneWindow,
    MilestoneBlocked,
    SelfDependency,
)
from wedding.modules.schedule.domain.values import (
    MAX_CHECKLIST_ITEMS,
    BlockerKind,
    ManualState,
    MilestoneState,
    OwnerKind,
    Standing,
    TaskState,
)
from wedding.modules.schedule.domain.windows import WindowUnit, window_dates
from wedding.shared_kernel.errors import Forbidden, NotFound
from wedding.shared_kernel.profile import ProfileKind

CATEGORIAS = sorted({m[3] for m in MARCOS if m[3]})
ATORES = st.sampled_from([NOIVO, NOIVA])
ESTADOS = st.sampled_from([ManualState.IN_PROGRESS, ManualState.DONE, None])
ESTADOS_DA_AVULSA = st.sampled_from(list(TaskState))
RESPONSAVEIS = st.sampled_from([None, ProfileKind.AMBOS, ProfileKind.NOIVO, ProfileKind.NOIVA])
STANDINGS = st.sampled_from(list(Standing))
ESCOLHA = st.integers(min_value=0, max_value=1000)
ESCOLHAS = st.lists(ESCOLHA, max_size=4)
# A data do casamento não tem o ano validado no `wedding`: o cronograma aguenta qualquer uma.
DATAS_DO_CASAMENTO = st.dates(min_value=date(1, 1, 1), max_value=date(9999, 12, 31))
DATAS_DA_PREVIA = st.dates(min_value=date(2000, 1, 1), max_value=date(2100, 12, 31))


def _alcanca(depende_de: dict[UUID, set[UUID]], origem: UUID, destino: UUID) -> bool:
    """Oráculo independente do grafo: `origem` depende de `destino`, direta ou transitivamente?"""
    vistos, pilha = set(), [origem]
    while pilha:
        atual = pilha.pop()
        if atual == destino:
            return True
        if atual not in vistos:
            vistos.add(atual)
            pilha.extend(depende_de.get(atual, ()))
    return False


def _aciclico(depende_de: dict[UUID, set[UUID]]) -> bool:
    restantes = {m: set(d) for m, d in depende_de.items()}
    while restantes:
        livres = [m for m, d in restantes.items() if not d & restantes.keys()]
        if not livres:
            return False
        for marco in livres:
            del restantes[marco]
    return True


class _SemAlvo(Exception):
    """O sorteio não achou o que a regra precisa (nenhuma avulsa, nenhum item): o passo não faz
    nada. Sem isto, `assume` descartaria a sequência inteira e o Hypothesis recusaria o teste."""


def _se_houver_alvo(regra):
    @wraps(regra)
    def embrulhada(self, *args, **kwargs):
        try:
            return regra(self, *args, **kwargs)
        except _SemAlvo:
            return None

    return embrulhada


class ScheduleMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.clock = FixedClock(datetime(2026, 10, 28, 12, 0, tzinfo=UTC))
        self.world = World(self.clock)
        self.uc = self.world.use_cases()
        # O que o casal marcou, o único que a máquina deixa mudar o estado manual.
        self.manual: dict[UUID, ManualState | None] = {marco_id(m[0]): None for m in MARCOS}
        self.deleted: set[UUID] = set()
        # Os marcos cuja janela o casal editou à mão: só os outros têm a "sugestão genérica".
        self.window_edited: set[UUID] = set()
        self.history_count = 0
        self.created = 0
        # As avulsas: o estado que o casal marcou e as excluídas.
        self.task_state: dict[UUID, TaskState] = {}
        self.deleted_tasks: set[UUID] = set()
        self.tasks_created = 0
        # O checklist de cada dono (marco ou avulsa) como o casal o deixou: os itens vivos na
        # ordem e o texto e o "feito" de cada um. Excluir o dono não mexe aqui: restaurar o traz.
        self.item_order: dict[UUID, list[UUID]] = {}
        self.item_fields: dict[UUID, tuple[str, bool]] = {}
        self.items_added = 0
        # Os anexos de cada dono (marco ou avulsa) como o casal os deixou, na ordem em que foram
        # anexados, e o autor de cada um. Excluir o dono não mexe aqui: restaurar o traz de volta.
        self.attachment_order: dict[UUID, list[UUID]] = {}
        self.attachment_author: dict[UUID, ProfileKind] = {}
        self.attachments_added = 0

    @initialize()
    def start_with_a_task_and_some_checklists(self) -> None:
        """O ponto de partida já tem uma avulsa com dois itens e itens em três marcos (um livre e
        dois bloqueados), para uma sequência curta chegar a concluir, reordenar e remover itens."""
        self._tick()
        self.tasks_created += 1
        titulo = f"Avulsa Gerada {self.tasks_created}"
        depois = self.uc.create_task.execute(CreateTaskCommand(titulo, None, None, None), NOIVA)
        tarefa = depois.tasks[0]
        self.task_state[tarefa.id] = TaskState.TODO
        donos = [
            (OwnerKind.TASK, tarefa.id),
            (OwnerKind.TASK, tarefa.id),
            *[(OwnerKind.MILESTONE, marco_id(codigo)) for codigo in ("C01", "C03", "C06")],
        ]
        for tipo, dono in donos:
            self._tick()
            self.items_added += 1
            texto = f"Item Gerado {self.items_added}"
            resposta = self.uc.add_checklist_item.execute(
                AddChecklistItemCommand(tipo, dono, texto), NOIVO
            )
            novo = _itens_do_dono(resposta, dono)[-1]
            self.item_order.setdefault(dono, []).append(novo.id)
            self.item_fields[novo.id] = (texto, False)

    # --- ajudas ---------------------------------------------------------------------------

    def _tick(self) -> None:
        """Cada passo acontece em um instante próprio: o carimbo da exclusão não se repete."""
        self.clock.advance(seconds=1)

    def _cronograma(self) -> ScheduleDto:
        return self.uc.read_schedule.execute(NOIVO)

    def _marcos(self) -> dict[UUID, MilestoneDto]:
        return _por_id(self._cronograma())

    def _vivo(self, escolha: int) -> MilestoneDto:
        vivos = sorted(self._marcos().values(), key=lambda m: m.id)
        assume(vivos)  # excluir tudo é permitido; sem marcos vivos o passo não tem o que sortear
        return vivos[escolha % len(vivos)]

    def _fase(self, escolha: int) -> UUID:
        fases = self._cronograma().phases
        return fases[escolha % len(fases)].id

    def _fase_de(self, marco: MilestoneDto) -> UUID:
        return next(
            f.id for f in self._cronograma().phases if marco.id in {m.id for m in f.milestones}
        )

    def _opcoes(self) -> list[UUID]:
        return [o.id for o in self._cronograma().category_options if self._visivel(o.id)]

    def _visivel(self, categoria: UUID) -> bool:
        info = self.world.categories.get(categoria)
        return info is not None and info.visible

    def _grafo(self) -> dict[UUID, set[UUID]]:
        return {m.id: {d.id for d in m.depends_on} for m in self._marcos().values()}

    # --- regras do Mapa e do relógio --------------------------------------------------------

    @rule(nome=st.sampled_from(CATEGORIAS), standing=STANDINGS, visivel=st.booleans())
    def classify(self, nome, standing, visivel):
        self._tick()
        self.world.classify(nome, standing, visivel)

    @rule(nome=st.sampled_from(CATEGORIAS))
    def delete_category_from_the_map(self, nome):
        self._tick()
        self.world.categories.pop(categoria_id(nome), None)

    @rule(dias=st.integers(min_value=1, max_value=3))
    def pass_days(self, dias):
        self.clock.advance(days=dias)

    @rule(horas=st.integers(min_value=1, max_value=23))
    def pass_hours(self, horas):
        """Atravessa a meia-noite de Brasília e a de UTC em instantes diferentes: o "hoje" é o dia
        de Brasília, nunca o de UTC."""
        self.clock.advance(hours=horas)

    @rule(exata=DATAS_DO_CASAMENTO | st.none(), definida=st.booleans())
    def set_wedding_date(self, exata, definida):
        """Modo Com Data (exata e `Definida`) ou Sem Data (sem data, ou ainda em definição)."""
        self._tick()
        self.world.set_wedding_date(exata, defined=definida)

    # --- estado, prazo e edição -------------------------------------------------------------

    @rule(
        escolha=ESCOLHA,
        inicio=st.integers(min_value=-2, max_value=130),
        fim=st.integers(min_value=-2, max_value=130),
        unidade=st.sampled_from(list(WindowUnit)),
        ator=ATORES,
    )
    def edit_window(self, escolha, inicio, fim, unidade, ator):
        """Em qualquer modo, em qualquer marco (arquivado ou sem janela): a janela vale se está nos
        limites; fora deles recusa sem gravar. Nunca toca o prazo manual."""
        self._tick()
        alvo = self._vivo(escolha)
        teto = 120 if unidade is WindowUnit.MONTHS else 520
        valida = 0 <= fim <= inicio <= teto
        comando = UpdateMilestoneWindowCommand(alvo.id, inicio, fim, unidade, alvo.version)
        try:
            depois = self.uc.update_milestone_window.execute(comando, ator)
        except InvalidMilestoneWindow:
            assert not valida
            assert _por_id(self._cronograma())[alvo.id] == alvo
            return
        assert valida
        self.window_edited.add(alvo.id)
        editado = _por_id(depois)[alvo.id]
        assert editado.window is not None
        assert (editado.window.start_before, editado.window.end_before, editado.window.unit) == (
            inicio,
            fim,
            unidade,
        )
        assert editado.window.is_suggestion is False
        assert editado.target_date == alvo.target_date

    @rule(exata=DATAS_DA_PREVIA | st.none())
    def preview_date_change(self, exata):
        """A prévia só lê: nada do cronograma nem da data muda, e só lista o que é elegível."""
        antes = (self._cronograma(), self.world.wedding_date, len(self.world.store.changes))
        previa = self.uc.preview_date_change.execute(PreviewDateChangeCommand(exata), NOIVO)
        assert (self._cronograma(), self.world.wedding_date, len(self.world.store.changes)) == antes
        marcos = _por_id(antes[0])
        for mudanca in previa.changes:
            marco = marcos[mudanca.id]
            assert marco.window is not None
            assert marco.target_date is None
            assert not marco.archived
            assert marco.state is not MilestoneState.DONE
            assert mudanca.window_before != mudanca.window_after
        assert previa.manual_kept == sum(
            m.window is not None
            and m.target_date is not None
            and not m.archived
            and m.state is not MilestoneState.DONE
            for m in marcos.values()
        )
        # A mesma data da atual não muda nada.
        if exata == self.world.wedding_date.exact and self.world.wedding_date.defined:
            assert previa.changes == ()

    @rule(
        escolha=ESCOLHA,
        estado=ESTADOS,
        ignorar=st.booleans(),
        ignorar_itens=st.booleans(),
        com_itens=st.booleans(),
        ator=ATORES,
    )
    def mark(self, escolha, estado, ignorar, ignorar_itens, com_itens, ator):
        self._tick()
        alvo = self._marco_para_marcar(escolha, com_itens)
        muda = estado is not self.manual[alvo.id]
        esperava_bloqueio = estado is not None and muda and self._aguarda_algo(alvo)
        esperava_itens = estado is ManualState.DONE and muda and self._tem_item_aberto(alvo.id)
        comando = ChangeMilestoneStateCommand(
            alvo.id, estado, ignorar, alvo.version, ignore_open_items=ignorar_itens
        )
        antes = self._cronograma()
        try:
            self.uc.change_milestone_state.execute(comando, ator)
        except MilestoneBlocked:
            # O bloqueio vem antes dos itens: só recusa se havia o que aguardar e sem confirmação.
            assert esperava_bloqueio
            assert not ignorar
            assert self._cronograma() == antes
            return
        except ChecklistOpenItems:
            # Só com item vivo em aberto, ao concluir, sem a permissão e depois do bloqueio.
            assert esperava_itens
            assert not ignorar_itens
            assert not (esperava_bloqueio and not ignorar)
            assert self._cronograma() == antes
            return
        assert not (esperava_bloqueio and not ignorar)
        assert not (esperava_itens and not ignorar_itens)
        if muda:
            self.history_count += 1
        self.manual[alvo.id] = estado
        if estado is ManualState.DONE:
            # Concluir não altera os itens.
            assert _por_id(self._cronograma())[alvo.id].checklist == alvo.checklist

    def _marco_para_marcar(self, escolha: int, com_itens: bool) -> MilestoneDto:
        marcos = self._marcos()
        if com_itens:
            com = sorted((m for m in marcos.values() if m.checklist), key=lambda m: m.id)
            if com:
                return com[escolha % len(com)]
        return self._vivo(escolha)

    def _tem_item_aberto(self, dono: UUID) -> bool:
        return any(not self.item_fields[i][1] for i in self.item_order.get(dono, []))

    def _aguarda_algo(self, alvo: MilestoneDto) -> bool:
        """Independe da marca manual: o concluído não mostra bloqueios, mas avisa os
        predecessores não resolvidos, e a categoria em discussão continua valendo."""
        if alvo.state is not MilestoneState.DONE:
            return bool(alvo.blocked_by)
        info = self.world.categories.get(alvo.category.id) if alvo.category else None
        em_discussao = info is not None and info.standing is Standing.IN_DISCUSSION
        return bool(alvo.warnings) or em_discussao

    @rule(escolha=ESCOLHA, dias=st.integers(min_value=-5, max_value=5) | st.none())
    def set_deadline(self, escolha, dias):
        self._tick()
        alvo = self._vivo(escolha)
        prazo = None if dias is None else self.clock.now().date() + timedelta(days=dias)
        self._atualizar(alvo, target_date=prazo)

    def _atualizar(self, alvo: MilestoneDto, **campos):
        padrao = {
            "title": alvo.title,
            "phase_id": self._fase_de(alvo),
            "responsible": ProfileKind.AMBOS,
            "category_id": alvo.category.id if alvo.category else None,
            "note": alvo.note,
            "target_date": alvo.target_date,
            "version": alvo.version,
        }
        comando = UpdateMilestoneCommand(milestone_id=alvo.id, **{**padrao, **campos})
        return self.uc.update_milestone.execute(comando, NOIVA)

    @rule(escolha=ESCOLHA, fase=ESCOLHA)
    def move_milestone(self, escolha, fase):
        self._tick()
        alvo = self._vivo(escolha)
        origem = self._fase_de(alvo)
        destino = self._fase(fase)
        antes = self._cronograma()
        depois = self._atualizar(alvo, phase_id=destino)
        assert [d.id for d in _por_id(depois)[alvo.id].depends_on] == [
            d.id for d in alvo.depends_on
        ]
        if destino != origem:
            nova = next(f for f in depois.phases if f.id == destino)
            assert nova.milestones[-1].id == alvo.id
        outros = {m.id: m.position for f in antes.phases for m in f.milestones if m.id != alvo.id}
        assert outros == {
            m.id: m.position for f in depois.phases for m in f.milestones if m.id != alvo.id
        }

    @rule(escolha=ESCOLHA, categoria=ESCOLHA)
    def link_category(self, escolha, categoria):
        self._tick()
        alvo = self._vivo(escolha)
        opcoes = [None, *self._opcoes()]
        self._atualizar(alvo, category_id=opcoes[categoria % len(opcoes)])

    # --- criar, excluir e restaurar ---------------------------------------------------------

    @rule(fase=ESCOLHA, predecessores=ESCOLHAS, categoria=ESCOLHA)
    def create_milestone(self, fase, predecessores, categoria):
        self._tick()
        self.created += 1
        vivos = sorted(self._marcos())
        escolhidos = tuple(vivos[p % len(vivos)] for p in predecessores) if vivos else ()
        opcoes = [None, *self._opcoes()]
        alvo_fase = self._fase(fase)
        criado = self.uc.create_milestone.execute(
            CreateMilestoneCommand(
                title=f"Marco Gerado {self.created}",
                phase_id=alvo_fase,
                responsible=ProfileKind.AMBOS,
                category_id=opcoes[categoria % len(opcoes)],
                depends_on=escolhidos,
            ),
            NOIVO,
        )
        depois = criado.schedule
        novo = _por_id(depois)[criado.milestone_id]
        assert novo.title == f"Marco Gerado {self.created}"
        self.manual[novo.id] = None
        fase_nova = next(f for f in depois.phases if f.id == alvo_fase)
        assert fase_nova.milestones[-1].id == novo.id
        assert {d.id for d in novo.depends_on} == set(escolhidos)

    @rule(escolha=ESCOLHA, ator=ATORES)
    def delete_milestone(self, escolha, ator):
        self._tick()
        alvo = self._vivo(escolha)
        self.uc.delete_milestone.execute(DeleteMilestoneCommand(alvo.id, alvo.version), ator)
        self.deleted.add(alvo.id)

    @rule(escolha=ESCOLHA)
    def restore_milestone(self, escolha):
        self._tick()
        if not self.deleted:
            return
        alvo = sorted(self.deleted)[escolha % len(self.deleted)]
        resposta = self.uc.restore_milestone.execute(RestoreMilestoneCommand(alvo), NOIVA)
        self.deleted.discard(alvo)
        marcos = _por_id(resposta.schedule)
        assert alvo in marcos
        # O que ficou de fora não está entre as dependências que voltaram.
        for fora in resposta.left_out:
            assert fora.title
            # (Se a outra ponta está excluída, ela nem aparece na leitura.)
            assert fora.milestone_id not in marcos or not _liga(marcos, alvo, fora.milestone_id)
        fase = next(f for f in resposta.schedule.phases if alvo in {m.id for m in f.milestones})
        assert fase.milestones[-1].id == alvo

    @rule(escolha=ESCOLHA, ator=ATORES)
    def delete_and_restore_right_away(self, escolha, ator):
        """Restaurar logo depois de excluir devolve o mesmo conjunto de dependências."""
        self._tick()
        alvo = self._vivo(escolha)
        antes = self._cronograma()
        marcos_antes = _por_id(antes)
        depende = {d.id for d in alvo.depends_on}
        libera = {u.id for u in alvo.unlocks}
        dependentes = {m.id: {d.id for d in m.depends_on} for m in marcos_antes.values()}
        versoes = {
            m.id: m.version
            for m in marcos_antes.values()
            if alvo.id in {d.id for d in m.depends_on}
        }
        apos_excluir = self.uc.delete_milestone.execute(
            DeleteMilestoneCommand(alvo.id, alvo.version), ator
        )
        # Os dependentes perderam um predecessor: a version deles sobe (conflito de edição).
        assert {m: _por_id(apos_excluir)[m].version for m in versoes} == {
            m: v + 1 for m, v in versoes.items()
        }
        self._tick()
        resposta = self.uc.restore_milestone.execute(RestoreMilestoneCommand(alvo.id), ator)
        assert resposta.left_out == ()
        assert {m: _por_id(resposta.schedule)[m].version for m in versoes} == {
            m: v + 2 for m, v in versoes.items()
        }
        marcos = _por_id(resposta.schedule)
        assert {d.id for d in marcos[alvo.id].depends_on} == depende
        # "Libera" omite arquivados: o conjunto completo vem do `depende_de` dos outros marcos.
        assert {m for m, deps in _grafo_de(marcos).items() if alvo.id in deps} == {
            m for m, deps in dependentes.items() if alvo.id in deps
        }
        assert {u.id for u in marcos[alvo.id].unlocks} == {
            m for m in libera if not marcos[m].archived
        }

    @rule(escolha=ESCOLHA)
    def delete_rewire_and_restore(self, escolha):
        """Excluir um marco que tem predecessor e dependente, ligar o predecessor ao dependente e
        restaurar: a volta fecharia um ciclo, então a dependência fica de fora e o grafo segue
        acíclico."""
        self._tick()
        marcos = self._marcos()
        candidatos = sorted(
            m.id
            for m in marcos.values()
            if m.depends_on and any(m.id in {d.id for d in o.depends_on} for o in marcos.values())
        )
        if not candidatos:
            return
        alvo = marcos[candidatos[escolha % len(candidatos)]]
        predecessor = alvo.depends_on[0].id
        dependente = next(
            o
            for o in sorted(marcos.values(), key=lambda m: m.id)
            if alvo.id in {d.id for d in o.depends_on}
        )
        self.uc.delete_milestone.execute(DeleteMilestoneCommand(alvo.id, alvo.version), NOIVO)
        self._tick()
        antes = _por_id(self._cronograma())
        atual = antes[predecessor]
        novos = (*(d.id for d in atual.depends_on), dependente.id)
        try:
            self.uc.set_milestone_dependencies.execute(
                SetMilestoneDependenciesCommand(predecessor, novos, atual.version), NOIVO
            )
        except DependencyCycle:
            ligou = False
        else:
            ligou = True
        self._tick()
        resposta = self.uc.restore_milestone.execute(RestoreMilestoneCommand(alvo.id), NOIVO)
        if ligou:
            assert resposta.left_out
        assert _aciclico(_grafo_de(_por_id(resposta.schedule)))

    @rule(escolha=ESCOLHA, predecessores=ESCOLHAS)
    def set_dependencies(self, escolha, predecessores):
        self._tick()
        alvo = self._vivo(escolha)
        vivos = sorted(self._marcos())
        escolhidos = tuple(vivos[p % len(vivos)] for p in predecessores)
        grafo = self._grafo()
        antes = self._cronograma()
        comando = SetMilestoneDependenciesCommand(alvo.id, escolhidos, alvo.version)
        try:
            depois = self.uc.set_milestone_dependencies.execute(comando, NOIVO)
        except SelfDependency:
            assert alvo.id in escolhidos
        except DependencyCycle as erro:
            assert alvo.id not in escolhidos
            assert any(_alcanca(grafo, p, alvo.id) for p in escolhidos)
            caminho = [p["id"] for p in erro.data["path"]]
            assert caminho[0] == caminho[-1] == alvo.id
            assert all(b in grafo[a] for a, b in pairwise(caminho[1:]))
            assert self._cronograma() == antes
        else:
            assert alvo.id not in escolhidos
            assert not any(_alcanca(grafo, p, alvo.id) for p in escolhidos)
            assert {d.id for d in _por_id(depois)[alvo.id].depends_on} == set(escolhidos)

    # --- avulsas ----------------------------------------------------------------------------

    def _tarefas(self) -> dict[UUID, TaskDto]:
        return {t.id: t for t in self._cronograma().tasks}

    def _tarefa_viva(self, escolha: int) -> TaskDto:
        vivas = sorted(self._tarefas().values(), key=lambda t: t.id)
        if not vivas:
            raise _SemAlvo
        return vivas[escolha % len(vivas)]

    @rule(
        responsavel=RESPONSAVEIS,
        dias=st.integers(min_value=-5, max_value=5) | st.none(),
        ator=ATORES,
    )
    def create_task(self, responsavel, dias, ator):
        """O responsável padrão é o perfil da sessão, nunca `Ambos`; o explícito vale."""
        self._tick()
        self.tasks_created += 1
        titulo = f"Avulsa Gerada {self.tasks_created}"
        prazo = None if dias is None else self.clock.now().date() + timedelta(days=dias)
        antes = set(self._tarefas())
        depois = self.uc.create_task.execute(
            CreateTaskCommand(titulo, responsavel, None, prazo), ator
        )
        (nova,) = [t for t in depois.tasks if t.id not in antes]
        assert nova.title == titulo
        assert nova.responsible is (responsavel or ator.profile)
        assert nova.state is TaskState.TODO
        assert nova.version == 1
        assert nova.checklist == ()
        self.task_state[nova.id] = TaskState.TODO

    @rule(
        escolha=ESCOLHA,
        estado=ESTADOS_DA_AVULSA,
        ignorar=st.booleans(),
        com_itens=st.booleans(),
        ator=ATORES,
    )
    @_se_houver_alvo
    def change_task_state(self, escolha, estado, ignorar, com_itens, ator):
        self._tick()
        alvo = self._tarefa_viva(escolha)
        if com_itens:
            com = sorted((t for t in self._tarefas().values() if t.checklist), key=lambda t: t.id)
            alvo = com[escolha % len(com)] if com else alvo
        esperava_itens = (
            estado is TaskState.DONE
            and estado is not self.task_state[alvo.id]
            and self._tem_item_aberto(alvo.id)
        )
        antes = self._cronograma()
        comando = ChangeTaskStateCommand(alvo.id, estado, ignorar, alvo.version)
        try:
            self.uc.change_task_state.execute(comando, ator)
        except ChecklistOpenItems:
            assert esperava_itens
            assert not ignorar
            assert self._cronograma() == antes
            return
        assert not (esperava_itens and not ignorar)
        self.task_state[alvo.id] = estado
        depois = self._tarefas()[alvo.id]
        assert depois.state is estado
        assert depois.checklist == alvo.checklist  # concluir não altera os itens

    @rule(escolha=ESCOLHA, dias=st.integers(min_value=-5, max_value=5) | st.none(), ator=ATORES)
    @_se_houver_alvo
    def edit_task(self, escolha, dias, ator):
        self._tick()
        alvo = self._tarefa_viva(escolha)
        prazo = None if dias is None else self.clock.now().date() + timedelta(days=dias)
        comando = UpdateTaskCommand(
            alvo.id, alvo.title, alvo.responsible, alvo.note, prazo, alvo.version
        )
        depois = _tarefas_por_id(self.uc.update_task.execute(comando, ator))[alvo.id]
        assert depois.target_date == prazo
        assert depois.version == alvo.version + (prazo != alvo.target_date)
        assert depois.state is alvo.state

    @rule(escolha=ESCOLHA, ator=ATORES)
    @_se_houver_alvo
    def delete_task(self, escolha, ator):
        self._tick()
        alvo = self._tarefa_viva(escolha)
        self.uc.delete_task.execute(DeleteTaskCommand(alvo.id, alvo.version), ator)
        self.deleted_tasks.add(alvo.id)

    @rule(escolha=ESCOLHA, ator=ATORES)
    @_se_houver_alvo
    def restore_task(self, escolha, ator):
        self._tick()
        if not self.deleted_tasks:
            raise _SemAlvo
        alvo = sorted(self.deleted_tasks)[escolha % len(self.deleted_tasks)]
        resposta = self.uc.restore_task.execute(RestoreTaskCommand(alvo), ator)
        self.deleted_tasks.discard(alvo)
        volta = _tarefas_por_id(resposta)[alvo]
        assert volta.state is self.task_state[alvo]  # o estado marcado e os itens voltam como eram
        assert [i.id for i in volta.checklist] == self.item_order.get(alvo, [])

    # --- checklist --------------------------------------------------------------------------

    def _donos(self, avulsa: bool) -> dict[UUID, MilestoneDto | TaskDto]:
        if avulsa:
            return dict(self._tarefas())
        return dict(self._marcos())

    def _dono(
        self, avulsa: bool, escolha: int, *, minimo_de_itens: int = 0
    ) -> tuple[OwnerKind, MilestoneDto | TaskDto]:
        """Sorteia o dono; com `minimo_de_itens`, prefere os que já têm tantos itens (com 29 marcos
        os itens se espalham demais para uma sequência curta chegar a reordenar ou concluir)."""
        donos = sorted(self._donos(avulsa).values(), key=lambda d: d.id)
        if not donos:
            raise _SemAlvo
        preferidos = [d for d in donos if len(d.checklist) >= minimo_de_itens]
        donos = preferidos or donos
        tipo = OwnerKind.TASK if avulsa else OwnerKind.MILESTONE
        return tipo, donos[escolha % len(donos)]

    def _item_vivo(
        self, avulsa: bool, escolha: int
    ) -> tuple[MilestoneDto | TaskDto, ChecklistItemDto]:
        com_itens = sorted(
            (d for d in self._donos(avulsa).values() if d.checklist), key=lambda d: d.id
        )
        if not com_itens:
            raise _SemAlvo
        dono = com_itens[escolha % len(com_itens)]
        return dono, dono.checklist[(escolha // 7) % len(dono.checklist)]

    def _dono_por_id(self, dono: UUID) -> MilestoneDto | TaskDto:
        return self._marcos().get(dono) or self._tarefas()[dono]

    def _nao_tocou_no_dono(self, antes: MilestoneDto | TaskDto) -> None:
        depois = self._dono_por_id(antes.id)
        assert (depois.state, depois.version) == (antes.state, antes.version)

    @rule(avulsa=st.booleans(), escolha=ESCOLHA, reusar=st.booleans(), ator=ATORES)
    @_se_houver_alvo
    def add_item(self, avulsa, escolha, reusar, ator):
        self._tick()
        tipo, dono = self._dono(avulsa, escolha, minimo_de_itens=1 if reusar else 0)
        self.items_added += 1
        texto = f"Item Gerado {self.items_added}"
        depois = self.uc.add_checklist_item.execute(
            AddChecklistItemCommand(tipo, dono.id, texto), ator
        )
        itens = _itens_do_dono(depois, dono.id)
        novo = itens[-1]
        assert novo.text == texto
        assert novo.done is False
        assert novo.version == 1
        assert novo.position == max((i.position for i in dono.checklist), default=-1) + 1
        assert [i.id for i in itens[:-1]] == [i.id for i in dono.checklist]
        self._nao_tocou_no_dono(dono)
        self.item_order.setdefault(dono.id, []).append(novo.id)
        self.item_fields[novo.id] = (texto, False)

    @rule(avulsa=st.booleans(), escolha=ESCOLHA, feito=st.booleans(), ator=ATORES)
    @_se_houver_alvo
    def mark_item(self, avulsa, escolha, feito, ator):
        self._tick()
        dono, item = self._item_vivo(avulsa, escolha)
        comando = UpdateChecklistItemCommand(item.id, item.text, feito, item.version)
        depois = self.uc.update_checklist_item.execute(comando, ator)
        novo = next(i for i in _itens_do_dono(depois, dono.id) if i.id == item.id)
        assert novo.done is feito
        assert novo.version == item.version + (feito != item.done)
        self._nao_tocou_no_dono(dono)
        self.item_fields[item.id] = (item.text, feito)

    @rule(avulsa=st.booleans(), escolha=ESCOLHA, numero=st.integers(1, 9), ator=ATORES)
    @_se_houver_alvo
    def edit_item_text(self, avulsa, escolha, numero, ator):
        self._tick()
        dono, item = self._item_vivo(avulsa, escolha)
        texto = f"Texto Editado {numero}"
        comando = UpdateChecklistItemCommand(item.id, texto, item.done, item.version)
        depois = self.uc.update_checklist_item.execute(comando, ator)
        novo = next(i for i in _itens_do_dono(depois, dono.id) if i.id == item.id)
        assert (novo.text, novo.done) == (texto, item.done)
        assert novo.version == item.version + (texto != item.text)
        self._nao_tocou_no_dono(dono)
        self.item_fields[item.id] = (texto, item.done)

    @rule(avulsa=st.booleans(), escolha=ESCOLHA, ator=ATORES)
    @_se_houver_alvo
    def remove_item(self, avulsa, escolha, ator):
        self._tick()
        dono, item = self._item_vivo(avulsa, escolha)
        depois = self.uc.remove_checklist_item.execute(
            RemoveChecklistItemCommand(item.id, item.version), ator
        )
        restantes = [i.id for i in _itens_do_dono(depois, dono.id)]
        assert restantes == [i.id for i in dono.checklist if i.id != item.id]
        self._nao_tocou_no_dono(dono)
        self.item_order[dono.id].remove(item.id)
        del self.item_fields[item.id]

    @rule(escolha=ESCOLHA, avulsa=st.booleans(), operacao=st.integers(0, 3))
    @_se_houver_alvo
    def touch_the_checklist_of_a_deleted_owner(self, escolha, avulsa, operacao):
        """Com o dono excluído os itens somem da leitura e nenhuma operação os alcança (404), nem
        adicionar, reordenar, editar ou remover; nada é gravado."""
        self._tick()
        excluidos = sorted(self.deleted_tasks if avulsa else self.deleted)
        itens = [(d, i) for d in excluidos for i in self.item_order.get(d, [])]
        if not excluidos:
            raise _SemAlvo
        dono = excluidos[escolha % len(excluidos)]
        tipo = OwnerKind.TASK if avulsa else OwnerKind.MILESTONE
        antes = self._cronograma()
        item = itens[escolha % len(itens)][1] if itens else UUID(int=2**100)
        tentativas = [
            lambda: self.uc.add_checklist_item.execute(
                AddChecklistItemCommand(tipo, dono, "Novo"), NOIVO
            ),
            lambda: self.uc.reorder_checklist.execute(
                ReorderChecklistCommand(tipo, dono, tuple(self.item_order.get(dono, []))), NOIVO
            ),
            lambda: self.uc.update_checklist_item.execute(
                UpdateChecklistItemCommand(item, "Texto", True, 1), NOIVO
            ),
            lambda: self.uc.remove_checklist_item.execute(
                RemoveChecklistItemCommand(item, 1), NOIVO
            ),
        ]
        with pytest.raises(NotFound):
            tentativas[operacao]()
        assert self._cronograma() == antes

    # --- anexos -----------------------------------------------------------------------------

    @rule(avulsa=st.booleans(), escolha=ESCOLHA, arquivo=st.booleans(), ator=ATORES)
    @_se_houver_alvo
    def add_attachment(self, avulsa, escolha, arquivo, ator):
        """Link ou arquivo, sem limite por item: vai para o fim da lista do dono com a autoria da
        sessão, e o dono (estado e `version`) fica como estava."""
        self._tick()
        tipo, dono = self._dono(avulsa, escolha)
        self.attachments_added += 1
        numero = self.attachments_added
        if arquivo:
            enviado = self.world.files.add(f"arquivo-{numero}.pdf", "application/pdf", numero)
            comando_arquivo = AddFileAttachmentCommand(tipo, dono.id, enviado.file_id, None, None)
            depois = self.uc.add_file_attachment.execute(comando_arquivo, ator)
        else:
            url = f"https://exemplo.com/{numero}"
            depois = self.uc.add_link_attachment.execute(
                AddLinkAttachmentCommand(tipo, dono.id, url, None, None), ator
            )
        anexos = _anexos_do_dono(depois, dono.id)
        novo = anexos[-1]
        assert [a.id for a in anexos[:-1]] == [a.id for a in dono.attachments]
        assert novo.profile is ator.profile
        assert (novo.file is not None) is arquivo
        self._nao_tocou_no_dono(dono)
        self.attachment_order.setdefault(dono.id, []).append(novo.id)
        self.attachment_author[novo.id] = ator.profile

    @rule(avulsa=st.booleans(), escolha=ESCOLHA, ator=ATORES)
    @_se_houver_alvo
    def remove_attachment(self, avulsa, escolha, ator):
        """Só o autor remove; o outro perfil recebe `Forbidden` e nada muda. Remover tira só aquele
        anexo da lista e não toca o dono."""
        self._tick()
        com_anexos = sorted((d for d in self._donos(avulsa).values() if d.attachments), key=_id)
        if not com_anexos:
            raise _SemAlvo
        dono = com_anexos[escolha % len(com_anexos)]
        anexo = dono.attachments[(escolha // 7) % len(dono.attachments)]
        comando = RemoveAttachmentCommand(anexo.id)
        if self.attachment_author[anexo.id] is not ator.profile:
            antes = self._cronograma()
            with pytest.raises(Forbidden):
                self.uc.remove_attachment.execute(comando, ator)
            assert self._cronograma() == antes
            return
        depois = self.uc.remove_attachment.execute(comando, ator)
        restantes = [a.id for a in _anexos_do_dono(depois, dono.id)]
        assert restantes == [a.id for a in dono.attachments if a.id != anexo.id]
        self._nao_tocou_no_dono(dono)
        self.attachment_order[dono.id].remove(anexo.id)
        del self.attachment_author[anexo.id]

    @rule(escolha=ESCOLHA, avulsa=st.booleans(), operacao=st.integers(0, 2))
    @_se_houver_alvo
    def touch_the_attachments_of_a_deleted_owner(self, escolha, avulsa, operacao):
        """Com o dono excluído os anexos somem da leitura e nem anexar nem remover os alcança
        (404); nada é gravado e nenhuma linha de anexo é apagada."""
        self._tick()
        excluidos = sorted(self.deleted_tasks if avulsa else self.deleted)
        if not excluidos:
            raise _SemAlvo
        dono = excluidos[escolha % len(excluidos)]
        tipo = OwnerKind.TASK if avulsa else OwnerKind.MILESTONE
        guardados = self.attachment_order.get(dono, [])
        anexo = guardados[escolha % len(guardados)] if guardados else UUID(int=2**100)
        enviado = self.world.files.add("novo.pdf", "application/pdf", 1)
        tentativas = [
            lambda: self.uc.add_link_attachment.execute(
                AddLinkAttachmentCommand(tipo, dono, "https://exemplo.com/x", None, None), NOIVO
            ),
            lambda: self.uc.add_file_attachment.execute(
                AddFileAttachmentCommand(tipo, dono, enviado.file_id, None, None), NOIVO
            ),
            lambda: self.uc.remove_attachment.execute(RemoveAttachmentCommand(anexo), NOIVO),
        ]
        antes = self._cronograma()
        linhas_antes = len(self.world.store.attachments)
        with pytest.raises(NotFound):
            tentativas[operacao]()
        assert self._cronograma() == antes
        assert len(self.world.store.attachments) == linhas_antes

    @rule(avulsa=st.booleans(), escolha=ESCOLHA, ordem=st.randoms(use_true_random=False))
    @_se_houver_alvo
    def reorder_items(self, avulsa, escolha, ordem):
        """Uma permutação exata dos vivos: as posições ficam 0..n-1 e só muda a version de quem
        saiu do lugar."""
        self._tick()
        tipo, dono = self._dono(avulsa, escolha, minimo_de_itens=2)
        ids = [i.id for i in dono.checklist]
        ordem.shuffle(ids)
        depois = self.uc.reorder_checklist.execute(
            ReorderChecklistCommand(tipo, dono.id, tuple(ids)), NOIVO
        )
        itens = _itens_do_dono(depois, dono.id)
        assert [i.id for i in itens] == ids
        assert [i.position for i in itens] == list(range(len(ids)))
        antes = {i.id: i for i in dono.checklist}
        for item in itens:
            mudou = antes[item.id].position != item.position
            assert item.version == antes[item.id].version + mudou
        self._nao_tocou_no_dono(dono)
        if dono.id in self.item_order:
            self.item_order[dono.id] = ids

    @rule(avulsa=st.booleans(), escolha=ESCOLHA, defeito=st.integers(0, 3))
    @_se_houver_alvo
    def reorder_items_badly(self, avulsa, escolha, defeito):
        """Lista que não é a permutação exata dos vivos é 422 e não muda nada."""
        self._tick()
        tipo, dono = self._dono(avulsa, escolha, minimo_de_itens=1)
        ids = [i.id for i in dono.checklist]
        intruso = UUID(int=2**100 + defeito)
        ruins = [
            [*ids, intruso],  # sobra um que não existe
            [*ids, *ids[:1]] if ids else [intruso],  # repete (ou, sem itens, o intruso)
            ids[:-1] if ids else [intruso],  # falta um (ou, sem itens, o intruso)
            [*ids[:-1], intruso] if ids else [intruso, intruso],  # troca um por outro
        ]
        antes = self._cronograma()
        with pytest.raises(InvalidChecklistOrder):
            self.uc.reorder_checklist.execute(
                ReorderChecklistCommand(tipo, dono.id, tuple(ruins[defeito])), NOIVO
            )
        assert self._cronograma() == antes

    # --- fases ------------------------------------------------------------------------------

    @rule(numero=st.integers(1, 50))
    def create_phase(self, numero):
        self._tick()
        antes = len(self._cronograma().phases)
        depois = self.uc.create_phase.execute(CreatePhaseCommand(f"Fase Gerada {numero}"), NOIVO)
        assert len(depois.phases) == antes + 1
        assert depois.phases[-1].milestones == ()

    @rule(escolha=ESCOLHA, numero=st.integers(1, 50))
    def rename_phase(self, escolha, numero):
        self._tick()
        fases = self._cronograma().phases
        alvo = fases[escolha % len(fases)]
        depois = self.uc.rename_phase.execute(
            RenamePhaseCommand(alvo.id, f"Fase Renomeada {numero}", alvo.version), NOIVA
        )
        nova = next(f for f in depois.phases if f.id == alvo.id)
        assert [m.id for m in nova.milestones] == [m.id for m in alvo.milestones]

    @rule(ordem=st.randoms(use_true_random=False))
    def reorder_phases(self, ordem):
        self._tick()
        fases = list(self._cronograma().phases)
        ordem.shuffle(fases)
        depois = self.uc.reorder_phases.execute(
            ReorderPhasesCommand(tuple(f.id for f in fases)), NOIVO
        )
        assert [f.id for f in depois.phases] == [f.id for f in fases]

    # --- invariantes ------------------------------------------------------------------------

    @invariant()
    def tudo_o_que_se_deriva_confere(self):
        """Lê uma vez e confere todas as invariantes sobre a mesma leitura."""
        cronograma = self._cronograma()
        self.a_leitura_e_deterministica_e_nao_mexe_em_nada(cronograma)
        self.o_grafo_e_sempre_aciclico(cronograma)
        self.marco_excluido_nao_aparece_em_lugar_nenhum(cronograma)
        self.as_fases_estao_em_ordem_e_cada_marco_esta_em_uma_so(cronograma)
        self.depende_de_e_libera_se_correspondem(cronograma)
        self.so_o_casal_muda_o_estado_manual(cronograma)
        self.bloqueado_sempre_lista_ao_menos_um_motivo_e_destravado_nenhum(cronograma)
        self.arquivado_e_opcional_nunca_bloqueiam(cronograma)
        self.bloqueio_e_aviso_batem_com_o_estado_das_dependencias(cronograma)
        self.a_categoria_em_discussao_bloqueia_so_o_que_nao_esta_concluido(cronograma)
        self.atrasado_so_com_prazo_efetivo_vencido_e_nao_concluido_nem_arquivado(cronograma)
        self.o_prazo_efetivo_e_o_manual_ou_o_fim_da_janela_calculada(cronograma)
        self.a_contagem_regressiva_so_existe_para_o_marco_ativo_com_prazo(cronograma)
        self.so_a_janela_nao_editada_e_sugestao(cronograma)
        self.o_progresso_da_fase_confere_com_a_recontagem(cronograma)
        self.so_a_mudanca_real_vai_para_o_historico()
        self.a_avulsa_nunca_aparece_nos_marcos(cronograma)
        self.as_avulsas_vivas_sao_as_que_o_casal_deixou_e_na_ordem_da_chave(cronograma)
        self.o_prazo_da_avulsa_segue_a_regra_do_marco(cronograma)
        self.o_checklist_e_o_que_o_casal_deixou_inclusive_depois_de_restaurar(cronograma)
        self.o_progresso_do_checklist_confere_com_a_recontagem(cronograma)
        self.as_posicoes_do_checklist_sao_unicas_e_a_ordem_e_a_da_posicao(cronograma)
        self.os_anexos_somem_e_voltam_com_o_dono_e_nunca_sao_apagados(cronograma)

    def a_leitura_e_deterministica_e_nao_mexe_em_nada(self, cronograma: ScheduleDto) -> None:
        assert self.uc.read_schedule.execute(NOIVO) == cronograma
        # Só o `can_remove` muda com quem lê: o resto da leitura é o mesmo para os dois perfis.
        assert _sem_can_remove(self.uc.read_schedule.execute(NOIVA)) == _sem_can_remove(cronograma)

    def o_grafo_e_sempre_aciclico(self, cronograma: ScheduleDto) -> None:
        assert _aciclico(_grafo_de(_por_id(cronograma)))

    def marco_excluido_nao_aparece_em_lugar_nenhum(self, cronograma: ScheduleDto) -> None:
        marcos = _por_id(cronograma)
        assert not self.deleted & marcos.keys()
        for marco in marcos.values():
            referidos = {d.id for d in marco.depends_on} | {u.id for u in marco.unlocks}
            referidos |= {w.milestone_id for w in marco.warnings}
            referidos |= {b.milestone_id for b in marco.blocked_by if b.milestone_id}
            assert not self.deleted & referidos

    def as_fases_estao_em_ordem_e_cada_marco_esta_em_uma_so(self, cronograma: ScheduleDto) -> None:
        assert [f.position for f in cronograma.phases] == list(range(len(cronograma.phases)))
        vistos: list[UUID] = []
        for fase in cronograma.phases:
            assert len({m.position for m in fase.milestones}) == len(fase.milestones)
            assert [m.position for m in fase.milestones] == sorted(
                m.position for m in fase.milestones
            )
            vistos.extend(m.id for m in fase.milestones)
        assert len(vistos) == len(set(vistos))

    def depende_de_e_libera_se_correspondem(self, cronograma: ScheduleDto) -> None:
        marcos = _por_id(cronograma)
        for marco in marcos.values():
            for dep in marco.depends_on:
                dono = marcos[dep.id]
                # "Libera" omite os arquivados, que saíram das listas ativas.
                assert (marco.id in {u.id for u in dono.unlocks}) == (not marco.archived)
            for lib in marco.unlocks:
                assert marco.id in {d.id for d in marcos[lib.id].depends_on}
                assert not marcos[lib.id].archived

    def so_o_casal_muda_o_estado_manual(self, cronograma: ScheduleDto) -> None:
        """Concluído e Em andamento não mudam sozinhos: nenhuma classificação, prazo, data,
        exclusão ou reabertura de outro marco os desfaz."""
        for marco in _por_id(cronograma).values():
            manual = self.manual[marco.id]
            if manual is ManualState.DONE:
                assert marco.state is MilestoneState.DONE
            elif manual is ManualState.IN_PROGRESS:
                assert marco.state is MilestoneState.IN_PROGRESS
            else:
                assert marco.state in (MilestoneState.BLOCKED, MilestoneState.UNLOCKED)

    def bloqueado_sempre_lista_ao_menos_um_motivo_e_destravado_nenhum(
        self, cronograma: ScheduleDto
    ) -> None:
        for marco in _por_id(cronograma).values():
            if marco.state is MilestoneState.BLOCKED:
                assert marco.blocked_by
            if marco.state in (MilestoneState.UNLOCKED, MilestoneState.DONE):
                assert not marco.blocked_by
            assert all(motivo.label for motivo in marco.blocked_by)

    def arquivado_e_opcional_nunca_bloqueiam(self, cronograma: ScheduleDto) -> None:
        marcos = _por_id(cronograma)
        for marco in marcos.values():
            for motivo in marco.blocked_by:
                if motivo.kind is BlockerKind.MILESTONE:
                    assert motivo.milestone_id is not None
                    faltando = marcos[motivo.milestone_id]
                    assert not faltando.archived
                    assert not faltando.optional
                    assert faltando.state is not MilestoneState.DONE
                else:
                    assert motivo.milestone_id is None

    def bloqueio_e_aviso_batem_com_o_estado_das_dependencias(self, cronograma: ScheduleDto) -> None:
        marcos = _por_id(cronograma)
        for marco in marcos.values():
            pendentes = [d.id for d in marco.depends_on if not d.resolved]
            for dep in marco.depends_on:
                outro = marcos[dep.id]
                assert dep.resolved == (
                    outro.state is MilestoneState.DONE or outro.archived or outro.optional
                )
            if marco.state is MilestoneState.DONE:
                assert [w.milestone_id for w in marco.warnings] == pendentes
            else:
                assert marco.warnings == ()
                assert [
                    b.milestone_id for b in marco.blocked_by if b.kind is BlockerKind.MILESTONE
                ] == pendentes

    def a_categoria_em_discussao_bloqueia_so_o_que_nao_esta_concluido(
        self, cronograma: ScheduleDto
    ) -> None:
        for marco in _por_id(cronograma).values():
            if marco.category is None:
                continue
            info = self.world.categories.get(marco.category.id)
            standing = Standing.OUT if info is None or not info.visible else info.standing
            tem_motivo_de_categoria = any(
                b.kind is BlockerKind.CATEGORY_UNCLASSIFIED for b in marco.blocked_by
            )
            em_discussao = standing is Standing.IN_DISCUSSION
            assert tem_motivo_de_categoria == (
                em_discussao and marco.state is not MilestoneState.DONE
            )
            assert marco.archived == (standing is Standing.OUT)
            assert marco.optional == (standing is Standing.MAYBE)

    def atrasado_so_com_prazo_efetivo_vencido_e_nao_concluido_nem_arquivado(
        self, cronograma: ScheduleDto
    ) -> None:
        hoje = (self.clock.now() - timedelta(hours=3)).date()
        for marco in _por_id(cronograma).values():
            vencido = marco.effective_target is not None and marco.effective_target < hoje
            ativo = marco.state is not MilestoneState.DONE and not marco.archived
            assert marco.overdue == (vencido and ativo)

    def o_prazo_efetivo_e_o_manual_ou_o_fim_da_janela_calculada(
        self, cronograma: ScheduleDto
    ) -> None:
        com_data = self.world.wedding_date.is_exact_and_defined
        assert cronograma.has_exact_date == com_data
        for marco in _por_id(cronograma).values():
            calculada = None
            if com_data and marco.window is not None:
                calculada = window_dates(
                    self.world.wedding_date.exact,  # type: ignore[arg-type]
                    marco.window.start_before,
                    marco.window.end_before,
                    marco.window.unit,
                )
            assert (marco.window_start, marco.window_end) == (calculada or (None, None))
            if calculada:
                assert marco.window_start <= marco.window_end  # type: ignore[operator]
            fim = calculada[1] if calculada else None
            assert marco.effective_target == (marco.target_date or fim)

    def a_contagem_regressiva_so_existe_para_o_marco_ativo_com_prazo(
        self, cronograma: ScheduleDto
    ) -> None:
        hoje = (self.clock.now() - timedelta(hours=3)).date()
        for marco in _por_id(cronograma).values():
            if (
                marco.state is MilestoneState.DONE
                or marco.archived
                or marco.effective_target is None
            ):
                assert marco.days_left is None
            else:
                assert marco.days_left == (marco.effective_target - hoje).days

    def so_a_janela_nao_editada_e_sugestao(self, cronograma: ScheduleDto) -> None:
        for marco in _por_id(cronograma).values():
            if marco.window is None:
                assert marco.id not in self.window_edited
            else:
                assert marco.window.is_suggestion == (marco.id not in self.window_edited)

    def o_progresso_da_fase_confere_com_a_recontagem(self, cronograma: ScheduleDto) -> None:
        for fase in cronograma.phases:
            ativos = [m for m in fase.milestones if not m.archived]
            assert fase.progress.total == len(ativos)
            assert fase.progress.done == sum(m.state is MilestoneState.DONE for m in ativos)

    def so_a_mudanca_real_vai_para_o_historico(self) -> None:
        assert len(self.world.store.changes) == self.history_count
        for mudanca in self.world.store.changes:
            assert mudanca.state_before is not mudanca.state_after
            assert mudanca.profile is not ProfileKind.AMBOS
            assert not mudanca.ignored_block or mudanca.state_after is not None

    def a_avulsa_nunca_aparece_nos_marcos(self, cronograma: ScheduleDto) -> None:
        """Avulsa não passa pela derivação: nenhum marco a lista em "libera", "depende de",
        bloqueios ou avisos (F-CRN-06, regra 1 e critério de aceite)."""
        todas = set(self.task_state)
        for marco in _por_id(cronograma).values():
            referidos = {d.id for d in marco.depends_on} | {u.id for u in marco.unlocks}
            referidos |= {w.milestone_id for w in marco.warnings}
            referidos |= {b.milestone_id for b in marco.blocked_by if b.milestone_id}
            assert not todas & referidos
        assert not todas & _por_id(cronograma).keys()

    def as_avulsas_vivas_sao_as_que_o_casal_deixou_e_na_ordem_da_chave(
        self, cronograma: ScheduleDto
    ) -> None:
        vivas = {t.id: t for t in cronograma.tasks}
        assert vivas.keys() == self.task_state.keys() - self.deleted_tasks
        for tarefa in vivas.values():
            assert tarefa.state is self.task_state[tarefa.id]
            assert tarefa.responsible is not None
        chave = [
            (
                t.state is TaskState.DONE,
                t.target_date is None,
                t.target_date or date.min,
                t.title,
                t.id,
            )
            for t in cronograma.tasks
        ]
        assert chave == sorted(chave)

    def o_prazo_da_avulsa_segue_a_regra_do_marco(self, cronograma: ScheduleDto) -> None:
        hoje = (self.clock.now() - timedelta(hours=3)).date()
        for tarefa in cronograma.tasks:
            concluida = tarefa.state is TaskState.DONE
            conta = tarefa.target_date is not None and not concluida
            vencida = tarefa.target_date is not None and tarefa.target_date < hoje
            assert tarefa.overdue == (vencida and not concluida)
            if conta:
                assert tarefa.days_left == (tarefa.target_date - hoje).days  # type: ignore[operator]
            else:
                assert tarefa.days_left is None

    def o_checklist_e_o_que_o_casal_deixou_inclusive_depois_de_restaurar(
        self, cronograma: ScheduleDto
    ) -> None:
        """Excluir o dono esconde os itens sem apagar e restaurar os traz de volta: o dono vivo
        sempre mostra exatamente os itens que o casal deixou, na ordem, com texto e "feito"."""
        donos = [*_por_id(cronograma).values(), *cronograma.tasks]
        for dono in donos:
            assert [i.id for i in dono.checklist] == self.item_order.get(dono.id, [])
            for item in dono.checklist:
                assert (item.text, item.done) == self.item_fields[item.id]
        vivos = [i.id for dono in donos for i in dono.checklist]
        assert len(vivos) == len(set(vivos))

    def o_progresso_do_checklist_confere_com_a_recontagem(self, cronograma: ScheduleDto) -> None:
        for dono in [*_por_id(cronograma).values(), *cronograma.tasks]:
            progresso = dono.checklist_progress
            assert progresso.total == len(dono.checklist) <= MAX_CHECKLIST_ITEMS
            assert progresso.done == sum(i.done for i in dono.checklist)
            assert 0 <= progresso.done <= progresso.total

    def as_posicoes_do_checklist_sao_unicas_e_a_ordem_e_a_da_posicao(
        self, cronograma: ScheduleDto
    ) -> None:
        for dono in [*_por_id(cronograma).values(), *cronograma.tasks]:
            posicoes = [i.position for i in dono.checklist]
            assert posicoes == sorted(set(posicoes))
            assert all(p >= 0 for p in posicoes)

    def os_anexos_somem_e_voltam_com_o_dono_e_nunca_sao_apagados(
        self, cronograma: ScheduleDto
    ) -> None:
        """O dono vivo mostra exatamente os anexos que o casal deixou, na ordem, com a autoria da
        sessão e o `can_remove` do perfil de quem lê; o anexo de dono excluído está fora da leitura
        mas a linha segue guardada, viva, esperando a restauração."""
        donos = [*_por_id(cronograma).values(), *cronograma.tasks]
        for dono in donos:
            assert [a.id for a in dono.attachments] == self.attachment_order.get(dono.id, [])
            for anexo in dono.attachments:
                assert anexo.profile is self.attachment_author[anexo.id]
                assert anexo.can_remove is (anexo.profile is NOIVO.profile)  # a leitura é do Noivo
                assert (anexo.url is None) is (anexo.file is not None)
        visiveis = [a.id for dono in donos for a in dono.attachments]
        assert len(visiveis) == len(set(visiveis))
        for dono in {*self.deleted, *self.deleted_tasks}:
            for anexo in self.attachment_order.get(dono, []):
                assert self.world.store.attachments[anexo].deleted_at is None
                assert anexo not in visiveis


def _id(item: MilestoneDto | TaskDto) -> UUID:
    return item.id


def _sem_can_remove(cronograma: ScheduleDto) -> ScheduleDto:
    def neutro(anexos: tuple[AttachmentDto, ...]) -> tuple[AttachmentDto, ...]:
        return tuple(replace(a, can_remove=False) for a in anexos)

    return replace(
        cronograma,
        phases=tuple(
            replace(
                fase,
                milestones=tuple(
                    replace(m, attachments=neutro(m.attachments)) for m in fase.milestones
                ),
            )
            for fase in cronograma.phases
        ),
        tasks=tuple(replace(t, attachments=neutro(t.attachments)) for t in cronograma.tasks),
    )


def _anexos_do_dono(cronograma: ScheduleDto, dono: UUID) -> tuple[AttachmentDto, ...]:
    donos = {**_por_id(cronograma), **_tarefas_por_id(cronograma)}
    return donos[dono].attachments


def _tarefas_por_id(cronograma: ScheduleDto) -> dict[UUID, TaskDto]:
    return {t.id: t for t in cronograma.tasks}


def _itens_do_dono(cronograma: ScheduleDto, dono: UUID) -> tuple[ChecklistItemDto, ...]:
    donos = {**_por_id(cronograma), **_tarefas_por_id(cronograma)}
    return donos[dono].checklist


def _por_id(cronograma: ScheduleDto) -> dict[UUID, MilestoneDto]:
    return {m.id: m for f in cronograma.phases for m in f.milestones}


def _grafo_de(marcos: dict[UUID, MilestoneDto]) -> dict[UUID, set[UUID]]:
    return {m.id: {d.id for d in m.depends_on} for m in marcos.values()}


def _liga(marcos: dict[UUID, MilestoneDto], a: UUID, b: UUID) -> bool:
    """Há dependência direta entre os dois, em qualquer sentido."""
    return b in {d.id for d in marcos[a].depends_on} or a in {d.id for d in marcos[b].depends_on}


ScheduleMachine.TestCase.settings = settings(max_examples=50, stateful_step_count=30, deadline=None)
TestScheduleMachine = ScheduleMachine.TestCase
