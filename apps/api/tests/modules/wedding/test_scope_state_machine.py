"""Integridade do Mapa de Escopo sob qualquer sequência de operações.

O Hypothesis sorteia criar, renomear, mover, ocultar, excluir, mudar status e avaliar, com nomes
escolhidos de um conjunto pequeno para provocar colisões, e confere depois de cada passo as
invariantes que o banco e o domínio prometem (plano do PR 2, D-068).
"""

import contextlib
from datetime import UTC, datetime

from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
from tests.conftest import FixedClock
from tests.modules.wedding.conftest import NOIVA, NOIVO, World

from wedding.modules.wedding.application.commands.change_scope_status import (
    ChangeScopeStatusCommand,
)
from wedding.modules.wedding.application.commands.create_scope_category import (
    CreateScopeCategoryCommand,
)
from wedding.modules.wedding.application.commands.create_scope_group import CreateScopeGroupCommand
from wedding.modules.wedding.application.commands.delete_scope_category import (
    DeleteScopeCategoryCommand,
)
from wedding.modules.wedding.application.commands.delete_scope_group import DeleteScopeGroupCommand
from wedding.modules.wedding.application.commands.set_my_evaluation import SetMyEvaluationCommand
from wedding.modules.wedding.application.commands.set_scope_category_visibility import (
    SetScopeCategoryVisibilityCommand,
)
from wedding.modules.wedding.application.commands.set_scope_group_visibility import (
    SetScopeGroupVisibilityCommand,
)
from wedding.modules.wedding.application.commands.update_scope_category import (
    UpdateScopeCategoryCommand,
)
from wedding.modules.wedding.domain.errors import (
    CatalogItemNotDeletable,
    DiscardReasonRequired,
    DuplicateScopeName,
    GroupNotEmpty,
)
from wedding.modules.wedding.domain.scope_values import Origin, Priority, ScopeStatus
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.profile import ProfileKind

NAMES = st.sampled_from(["Foto", "FOTO", " foto ", "Vídeo", "Bolo", "bolo  doce", "Flores"])
ACTORS = st.sampled_from([NOIVO, NOIVA])
PICK = st.integers(min_value=0, max_value=50)


class ScopeMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.clock = FixedClock(datetime(2026, 10, 28, 12, 0, tzinfo=UTC))
        self.world = World(self.clock)
        self.world.seed_catalog()
        self.uc = self.world.scope_use_cases()

    def _groups(self):
        return self.uc.get_scope_map.execute(NOIVO).groups

    def _categories(self):
        return [c for g in self._groups() for c in g.categories]

    @rule(name=NAMES, actor=ACTORS)
    def create_group(self, name, actor):
        with contextlib.suppress(DuplicateScopeName):
            self.uc.create_scope_group.execute(CreateScopeGroupCommand(name), actor)

    @rule(pick=PICK, name=NAMES, estimate=st.one_of(st.none(), st.integers(1, 10**6)), actor=ACTORS)
    def create_category(self, pick, name, estimate, actor):
        groups = self._groups()
        group = groups[pick % len(groups)]
        with contextlib.suppress(DuplicateScopeName):
            self.uc.create_scope_category.execute(
                CreateScopeCategoryCommand(group.id, name, estimate), actor
            )

    @rule(
        pick=PICK, group_pick=PICK, name=NAMES, estimate=st.one_of(st.none(), st.integers(1, 10**6))
    )
    def update_category(self, pick, group_pick, name, estimate):
        categories, groups = self._categories(), self._groups()
        if not categories:
            return
        category = categories[pick % len(categories)]
        target = groups[group_pick % len(groups)]
        with contextlib.suppress(DuplicateScopeName):
            self.uc.update_scope_category.execute(
                UpdateScopeCategoryCommand(
                    category.id, name, target.id, estimate, category.version
                ),
                NOIVO,
            )

    @rule(pick=PICK, hidden=st.booleans())
    def hide_category(self, pick, hidden):
        categories = self._categories()
        if categories:
            category = categories[pick % len(categories)]
            self.uc.set_scope_category_visibility.execute(
                SetScopeCategoryVisibilityCommand(category.id, hidden, category.version), NOIVA
            )

    @rule(pick=PICK, hidden=st.booleans())
    def hide_group(self, pick, hidden):
        groups = self._groups()
        group = groups[pick % len(groups)]
        self.uc.set_scope_group_visibility.execute(
            SetScopeGroupVisibilityCommand(group.id, hidden, group.version), NOIVA
        )

    @rule(pick=PICK)
    def delete_category(self, pick):
        categories = self._categories()
        if categories:
            category = categories[pick % len(categories)]
            try:
                self.uc.delete_scope_category.execute(
                    DeleteScopeCategoryCommand(category.id, category.version), NOIVO
                )
            except CatalogItemNotDeletable:
                assert category.origin is Origin.CATALOG

    @rule(pick=PICK)
    def delete_group(self, pick):
        groups = self._groups()
        group = groups[pick % len(groups)]
        with contextlib.suppress(CatalogItemNotDeletable, GroupNotEmpty):
            self.uc.delete_scope_group.execute(
                DeleteScopeGroupCommand(group.id, group.version), NOIVO
            )

    @rule(
        pick=PICK,
        status=st.sampled_from(list(ScopeStatus)),
        reason=st.sampled_from([None, " ", "motivo"]),
        actor=ACTORS,
    )
    def change_status(self, pick, status, reason, actor):
        categories = self._categories()
        if categories:
            category = categories[pick % len(categories)]
            self.clock.advance(minutes=1)
            try:
                self.uc.change_scope_status.execute(
                    ChangeScopeStatusCommand(category.id, status, reason, category.version), actor
                )
            except DiscardReasonRequired:
                assert status is ScopeStatus.OUT

    @rule(pick=PICK, priority=st.one_of(st.none(), st.sampled_from(list(Priority))), actor=ACTORS)
    def evaluate(self, pick, priority, actor):
        categories = self._categories()
        if categories:
            category = categories[pick % len(categories)]
            mine = category.noivo if actor.profile is ProfileKind.NOIVO else category.noiva
            self.uc.set_my_evaluation.execute(
                SetMyEvaluationCommand(category.id, priority, None, mine.version), actor
            )

    @rule(pick=PICK)
    def stale_version_is_always_refused(self, pick):
        categories = self._categories()
        if categories:
            category = categories[pick % len(categories)]
            try:
                self.uc.change_scope_status.execute(
                    ChangeScopeStatusCommand(
                        category.id, ScopeStatus.ESSENTIAL, None, category.version + 1
                    ),
                    NOIVO,
                )
                raise AssertionError("uma versão errada foi aceita")
            except VersionConflict:
                pass

    # --- invariantes

    @invariant()
    def names_are_unique_among_the_living(self):
        store = self.world.scope_store
        categories = [c.name_key for c in store.categories.values() if c.deleted_at is None]
        groups = [g.name_key for g in store.groups.values() if g.deleted_at is None]
        assert len(categories) == len(set(categories))
        assert len(groups) == len(set(groups))

    @invariant()
    def every_live_category_has_exactly_the_pair_of_evaluations(self):
        store = self.world.scope_store
        for category in store.categories.values():
            profiles = {p for (cid, p) in store.evaluations if cid == category.id}
            assert profiles == {ProfileKind.NOIVO, ProfileKind.NOIVA}

    @invariant()
    def no_live_category_without_a_live_group_and_catalog_never_deleted(self):
        store = self.world.scope_store
        for category in store.categories.values():
            if category.deleted_at is None:
                assert store.groups[category.group_id].deleted_at is None
            if category.origin is Origin.CATALOG:
                assert category.deleted_at is None
        for group in store.groups.values():
            if group.origin is Origin.CATALOG:
                assert group.deleted_at is None

    @invariant()
    def status_history_is_a_continuous_chain_ending_in_the_current_status(self):
        for category in self.world.scope_store.categories.values():
            chain = [c for c in self.world.status_changes if c.category_id == category.id]
            expected = ScopeStatus.IN_DISCUSSION
            for change in chain:
                assert change.from_status is expected
                assert change.from_status is not change.to_status
                if change.to_status is ScopeStatus.OUT:
                    assert change.reason
                expected = change.to_status
            assert category.status is expected

    @invariant()
    def progress_and_totals_match_a_direct_recount(self):
        mapa = self.uc.get_scope_map.execute(NOIVO)
        visible = [c for g in mapa.groups for c in g.categories if c.visible]
        assert mapa.progress.total == len(visible)
        assert mapa.progress.classified == sum(
            c.status is not ScopeStatus.IN_DISCUSSION for c in visible
        )
        essential = [c for c in visible if c.status is ScopeStatus.ESSENTIAL]
        assert mapa.totals.essential_cents == sum(c.estimate_cents or 0 for c in essential)
        assert mapa.totals.essential_without_estimate == sum(
            c.estimate_cents is None for c in essential
        )


ScopeMachine.TestCase.settings = settings(max_examples=60, stateful_step_count=30, deadline=None)
TestScopeMachine = ScopeMachine.TestCase
