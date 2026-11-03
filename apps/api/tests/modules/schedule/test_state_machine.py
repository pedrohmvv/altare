"""O cronograma sob qualquer sequência de operações (`F-CRN-03` e `F-CRN-04`).

O Hypothesis sorteia classificar as categorias no Mapa de Escopo, marcar, reabrir, editar o prazo e
passar os dias, sobre o catálogo inicial inteiro (29 marcos e as suas 31 dependências), e confere
depois de cada passo as invariantes da derivação: o concluído não muda sozinho, arquivado e opcional
nunca bloqueiam, bloqueado sempre diz o que aguarda e a leitura é determinística.
"""

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
from tests.conftest import FixedClock
from tests.modules.schedule.catalog import MARCOS, categoria_id, marco_id
from tests.modules.schedule.conftest import NOIVA, NOIVO, World

from wedding.modules.schedule.application.commands.change_milestone_state import (
    ChangeMilestoneStateCommand,
)
from wedding.modules.schedule.application.commands.update_milestone import UpdateMilestoneCommand
from wedding.modules.schedule.application.dto import MilestoneDto, ScheduleDto
from wedding.modules.schedule.domain.errors import MilestoneBlocked
from wedding.modules.schedule.domain.values import (
    BlockerKind,
    ManualState,
    MilestoneState,
    Standing,
)
from wedding.shared_kernel.profile import ProfileKind

CODIGOS = [m[0] for m in MARCOS]
CATEGORIAS = sorted({m[3] for m in MARCOS if m[3]})
ATORES = st.sampled_from([NOIVO, NOIVA])
CODIGO = st.sampled_from(CODIGOS)
ESTADOS = st.sampled_from([ManualState.IN_PROGRESS, ManualState.DONE, None])
STANDINGS = st.sampled_from(list(Standing))


class ScheduleMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.clock = FixedClock(datetime(2026, 10, 28, 12, 0, tzinfo=UTC))
        self.world = World(self.clock)
        self.uc = self.world.use_cases()
        # O que o casal marcou, o único que a máquina deixa mudar o estado manual.
        self.manual: dict[UUID, ManualState | None] = {marco_id(c): None for c in CODIGOS}
        self.history_count = 0

    def _marcos(self) -> dict[UUID, MilestoneDto]:
        return _por_id(self.uc.read_schedule.execute(NOIVO))

    @rule(nome=st.sampled_from(CATEGORIAS), standing=STANDINGS)
    def classify(self, nome, standing):
        self.world.classify(nome, standing)

    @rule(nome=st.sampled_from(CATEGORIAS))
    def delete_category_from_the_map(self, nome):
        self.world.categories.pop(categoria_id(nome), None)

    @rule(codigo=CODIGO, estado=ESTADOS, ignorar=st.booleans(), ator=ATORES)
    def mark(self, codigo, estado, ignorar, ator):
        alvo = self._marcos()[marco_id(codigo)]
        esperava_bloqueio = estado is not None and estado is not self.manual[alvo.id]
        esperava_bloqueio = esperava_bloqueio and self._aguarda_algo(alvo)
        comando = ChangeMilestoneStateCommand(alvo.id, estado, ignorar, alvo.version)
        try:
            self.uc.change_milestone_state.execute(comando, ator)
        except MilestoneBlocked:
            # Só recusa se havia o que aguardar e a confirmação não veio.
            assert esperava_bloqueio
            assert not ignorar
            return
        assert not (esperava_bloqueio and not ignorar)
        if estado is not self.manual[alvo.id]:
            self.history_count += 1
        self.manual[alvo.id] = estado

    def _aguarda_algo(self, alvo: MilestoneDto) -> bool:
        """Independe da marca manual: o concluído não mostra bloqueios, mas avisa os
        predecessores não resolvidos, e a categoria em discussão continua valendo."""
        if alvo.state is not MilestoneState.DONE:
            return bool(alvo.blocked_by)
        info = self.world.categories.get(alvo.category.id) if alvo.category else None
        em_discussao = info is not None and info.standing is Standing.IN_DISCUSSION
        return bool(alvo.warnings) or em_discussao

    @rule(codigo=CODIGO, dias=st.integers(min_value=-5, max_value=5) | st.none())
    def set_deadline(self, codigo, dias):
        alvo = self._marcos()[marco_id(codigo)]
        prazo = None if dias is None else self.clock.now().date() + timedelta(days=dias)
        self.uc.update_milestone.execute(
            UpdateMilestoneCommand(alvo.id, ProfileKind.AMBOS, alvo.note, prazo, alvo.version),
            NOIVA,
        )

    @rule(dias=st.integers(min_value=1, max_value=3))
    def pass_days(self, dias):
        self.clock.advance(days=dias)

    @invariant()
    def tudo_o_que_se_deriva_confere(self):
        """Lê uma vez e confere todas as invariantes sobre a mesma leitura."""
        cronograma = self.uc.read_schedule.execute(NOIVO)
        self.a_leitura_e_deterministica_e_nao_mexe_em_nada(cronograma)
        self.so_o_casal_muda_o_estado_manual(cronograma)
        self.bloqueado_sempre_lista_ao_menos_um_motivo_e_destravado_nenhum(cronograma)
        self.arquivado_e_opcional_nunca_bloqueiam(cronograma)
        self.bloqueio_e_aviso_batem_com_o_estado_das_dependencias(cronograma)
        self.a_categoria_em_discussao_bloqueia_so_o_que_nao_esta_concluido(cronograma)
        self.atrasado_so_com_prazo_vencido_e_nao_concluido_nem_arquivado(cronograma)
        self.o_progresso_da_fase_confere_com_a_recontagem(cronograma)
        self.so_a_mudanca_real_vai_para_o_historico()

    def a_leitura_e_deterministica_e_nao_mexe_em_nada(self, cronograma: ScheduleDto) -> None:
        assert self.uc.read_schedule.execute(NOIVA) == cronograma

    def so_o_casal_muda_o_estado_manual(self, cronograma: ScheduleDto) -> None:
        """Concluído e Em andamento não mudam sozinhos: nenhuma classificação, prazo, data ou
        reabertura de outro marco os desfaz."""
        marcos = _por_id(cronograma)
        for marco in marcos.values():
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
        marcos = _por_id(cronograma)
        for marco in marcos.values():
            if marco.state is MilestoneState.BLOCKED:
                assert marco.blocked_by
            if marco.state is MilestoneState.UNLOCKED:
                assert not marco.blocked_by
            if marco.state is MilestoneState.DONE:
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
            assert not any(marcos[liberado].archived for liberado in (u.id for u in marco.unlocks))

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
        marcos = _por_id(cronograma)
        for marco in marcos.values():
            if marco.category is None:
                continue
            info = self.world.categories.get(marco.category.id)
            standing = info.standing if info else Standing.OUT
            tem_motivo_de_categoria = any(
                b.kind is BlockerKind.CATEGORY_UNCLASSIFIED for b in marco.blocked_by
            )
            em_discussao = standing is Standing.IN_DISCUSSION
            assert tem_motivo_de_categoria == (
                em_discussao and marco.state is not MilestoneState.DONE
            )
            assert marco.archived == (standing is Standing.OUT)
            assert marco.optional == (standing is Standing.MAYBE)

    def atrasado_so_com_prazo_vencido_e_nao_concluido_nem_arquivado(
        self, cronograma: ScheduleDto
    ) -> None:
        marcos = _por_id(cronograma)
        for marco in marcos.values():
            if marco.overdue:
                assert marco.target_date is not None
                assert marco.target_date < _hoje_em_brasilia(self.clock)
                assert marco.state is not MilestoneState.DONE
                assert not marco.archived
            elif marco.target_date is not None and marco.target_date < _hoje_em_brasilia(
                self.clock
            ):
                assert marco.state is MilestoneState.DONE or marco.archived

    def o_progresso_da_fase_confere_com_a_recontagem(self, cronograma: ScheduleDto) -> None:
        for fase in cronograma.phases:
            ativos = [m for m in fase.milestones if not m.archived]
            assert fase.progress.total == len(ativos)
            assert fase.progress.done == sum(m.state is MilestoneState.DONE for m in ativos)

    def so_a_mudanca_real_vai_para_o_historico(self):
        assert len(self.world.store.changes) == self.history_count
        for mudanca in self.world.store.changes:
            assert mudanca.state_before is not mudanca.state_after
            assert mudanca.profile is not ProfileKind.AMBOS
            assert not mudanca.ignored_block or mudanca.state_after is not None


def _por_id(cronograma: ScheduleDto) -> dict[UUID, MilestoneDto]:
    return {m.id: m for f in cronograma.phases for m in f.milestones}


def _hoje_em_brasilia(clock: FixedClock) -> date:
    return (clock.now() - timedelta(hours=3)).date()


ScheduleMachine.TestCase.settings = settings(max_examples=60, stateful_step_count=30, deadline=None)
TestScheduleMachine = ScheduleMachine.TestCase
