"""Integridade da lista de convidados sob qualquer sequência de operações.

O Hypothesis sorteia criar núcleo, acrescentar pessoa e acompanhante, editar, mudar status, mover,
excluir e restaurar, com nomes escolhidos de um conjunto pequeno para provocar colisões, e confere
depois de cada passo as invariantes que o domínio e o banco prometem (plano do PR 1, D-072).
"""

import contextlib
import math
from datetime import UTC, date, datetime
from fractions import Fraction

from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
from tests.conftest import FixedClock
from tests.modules.guests.conftest import NOIVA, NOIVO, World

from wedding.modules.guests.application.commands.add_companion import AddCompanionCommand
from wedding.modules.guests.application.commands.add_guest import AddGuestCommand
from wedding.modules.guests.application.commands.change_guest_status import (
    ChangeGuestStatusCommand,
)
from wedding.modules.guests.application.commands.clear_household_invite import (
    ClearHouseholdInviteCommand,
)
from wedding.modules.guests.application.commands.create_household import CreateHouseholdCommand
from wedding.modules.guests.application.commands.delete_guest import (
    CompanionChoice,
    DeleteGuestCommand,
)
from wedding.modules.guests.application.commands.delete_household import DeleteHouseholdCommand
from wedding.modules.guests.application.commands.move_guest import MoveGuestCommand
from wedding.modules.guests.application.commands.record_household_invite import (
    RecordHouseholdInviteCommand,
)
from wedding.modules.guests.application.commands.restore_guest import RestoreGuestCommand
from wedding.modules.guests.application.commands.restore_household import RestoreHouseholdCommand
from wedding.modules.guests.application.commands.update_guest import UpdateGuestCommand
from wedding.modules.guests.application.commands.update_guest_settings import (
    UpdateGuestSettingsCommand,
    WeightsCommand,
)
from wedding.modules.guests.application.fields import GuestFields, HouseholdFields
from wedding.modules.guests.domain.errors import (
    CompanionAlreadyExists,
    CompanionCannotHaveCompanion,
    CompanionChoiceRequired,
    CompanionMovesWithHolder,
    CompanionNeedsName,
    DuplicateHouseholdName,
    InvalidAgeLimits,
    LastGuestInHousehold,
)
from wedding.modules.guests.domain.values import (
    AgeBand,
    GuestStatus,
    InviteChannel,
    Probability,
    Side,
    name_key,
)
from wedding.shared_kernel.errors import NotFound, VersionConflict

HOUSEHOLD_NAMES = st.sampled_from(
    [
        "Família Exemplo",
        "FAMÍLIA EXEMPLO",
        " família  exemplo ",
        "Outra Família",
        "Terceira Família",
    ]
)
GUEST_NAMES = st.sampled_from(["Convidado Exemplo A", "Convidado Exemplo B", "Convidado Exemplo C"])
ACTORS = st.sampled_from([NOIVO, NOIVA])
PICK = st.integers(min_value=0, max_value=50)
EXPECTED = (
    CompanionAlreadyExists,
    CompanionCannotHaveCompanion,
    CompanionChoiceRequired,
    CompanionMovesWithHolder,
    CompanionNeedsName,
    DuplicateHouseholdName,
    LastGuestInHousehold,
    NotFound,
)


class GuestsMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.clock = FixedClock(datetime(2026, 10, 28, 12, 0, tzinfo=UTC))
        self.world = World(self.clock)
        self.uc = self.world.use_cases()
        self.deleted_guests: list = []
        self.deleted_households: list = []

    def _households(self):
        return self.uc.get_guest_list.execute(NOIVO).households

    def _guests(self):
        return [g for h in self._households() for g in h.guests]

    @rule(name=HOUSEHOLD_NAMES, side=st.sampled_from(list(Side)), actor=ACTORS)
    def create_household(self, name, side, actor):
        with contextlib.suppress(DuplicateHouseholdName):
            self.uc.create_household.execute(
                CreateHouseholdCommand(
                    HouseholdFields(name=name, side=side), GuestFields(name="Convidado Exemplo A")
                ),
                actor,
            )

    @rule(pick=PICK, name=GUEST_NAMES, actor=ACTORS)
    def add_guest(self, pick, name, actor):
        households = self._households()
        if households:
            household = households[pick % len(households)]
            self.uc.add_guest.execute(AddGuestCommand(household.id, GuestFields(name=name)), actor)

    @rule(pick=PICK, actor=ACTORS)
    def add_companion(self, pick, actor):
        guests = self._guests()
        if guests:
            with contextlib.suppress(CompanionAlreadyExists, CompanionCannotHaveCompanion):
                self.uc.add_companion.execute(
                    AddCompanionCommand(guests[pick % len(guests)].id, None), actor
                )

    @rule(
        pick=PICK,
        band=st.sampled_from(list(AgeBand)),
        age=st.one_of(st.none(), st.integers(0, 17)),
        probability=st.sampled_from(list(Probability)),
        name=st.one_of(st.none(), GUEST_NAMES),
        actor=ACTORS,
    )
    def edit_guest(self, pick, band, age, probability, name, actor):
        guests = self._guests()
        if guests:
            guest = guests[pick % len(guests)]
            keep_name = (
                name if guest.companion_of_id is not None else (name or "Convidado Exemplo A")
            )
            self.uc.update_guest.execute(
                UpdateGuestCommand(
                    guest.id,
                    guest.version,
                    GuestFields(
                        name=keep_name,
                        band=band,
                        age=None if band is AgeBand.ADULT else age,
                        probability=probability,
                    ),
                    guest.decline_reason,
                ),
                actor,
            )

    @rule(
        pick=PICK,
        status=st.sampled_from(list(GuestStatus)),
        reason=st.one_of(st.none(), st.just("Motivo Exemplo")),
        actor=ACTORS,
    )
    def change_status(self, pick, status, reason, actor):
        guests = self._guests()
        if guests:
            guest = guests[pick % len(guests)]
            self.clock.advance(minutes=1)
            self.uc.change_guest_status.execute(
                ChangeGuestStatusCommand(
                    guest.id,
                    status,
                    reason if status is GuestStatus.DECLINED else None,
                    guest.version,
                ),
                actor,
            )

    @rule(pick=PICK, destination=PICK, actor=ACTORS)
    def move_guest(self, pick, destination, actor):
        guests, households = self._guests(), self._households()
        if guests:
            guest = guests[pick % len(guests)]
            with contextlib.suppress(*EXPECTED):
                self.uc.move_guest.execute(
                    MoveGuestCommand(
                        guest.id, households[destination % len(households)].id, guest.version
                    ),
                    actor,
                )

    @rule(
        pick=PICK,
        choice=st.sampled_from([None, CompanionChoice.DELETE, CompanionChoice.KEEP]),
        actor=ACTORS,
    )
    def delete_guest(self, pick, choice, actor):
        guests = self._guests()
        if guests:
            guest = guests[pick % len(guests)]
            self.clock.advance(minutes=1)
            with contextlib.suppress(*EXPECTED):
                self.uc.delete_guest.execute(
                    DeleteGuestCommand(guest.id, guest.version, choice), actor
                )
                self.deleted_guests.append(guest.id)

    @rule(pick=PICK, actor=ACTORS)
    def delete_only_a_companion(self, pick, actor):
        companions = [g for g in self._guests() if g.companion_of_id is not None]
        if companions:
            companion = companions[pick % len(companions)]
            self.clock.advance(minutes=1)
            with contextlib.suppress(*EXPECTED):
                self.uc.delete_guest.execute(
                    DeleteGuestCommand(companion.id, companion.version, None), actor
                )
                self.deleted_guests.append(companion.id)

    @rule(actor=ACTORS)
    def restore_the_latest_deleted_guest(self, actor):
        if self.deleted_guests:
            with contextlib.suppress(*EXPECTED):
                self.uc.restore_guest.execute(RestoreGuestCommand(self.deleted_guests[-1]), actor)

    @rule(pick=PICK, actor=ACTORS)
    def restore_guest(self, pick, actor):
        if self.deleted_guests:
            with contextlib.suppress(*EXPECTED):
                self.uc.restore_guest.execute(
                    RestoreGuestCommand(self.deleted_guests[pick % len(self.deleted_guests)]), actor
                )

    @rule(pick=PICK, actor=ACTORS)
    def delete_household(self, pick, actor):
        households = self._households()
        if households:
            household = households[pick % len(households)]
            self.clock.advance(minutes=1)
            self.uc.delete_household.execute(
                DeleteHouseholdCommand(household.id, household.version), actor
            )
            self.deleted_households.append(household.id)

    @rule(pick=PICK, actor=ACTORS)
    def restore_household(self, pick, actor):
        if self.deleted_households:
            with contextlib.suppress(*EXPECTED):
                self.uc.restore_household.execute(
                    RestoreHouseholdCommand(
                        self.deleted_households[pick % len(self.deleted_households)]
                    ),
                    actor,
                )

    @rule(
        weights=st.one_of(
            st.none(),
            st.builds(
                WeightsCommand, st.integers(0, 100), st.integers(0, 100), st.integers(0, 100)
            ),
        ),
        exempt=st.one_of(st.none(), st.integers(0, 17)),
        paying=st.one_of(st.none(), st.integers(0, 17)),
        actor=ACTORS,
    )
    def update_settings(self, weights, exempt, paying, actor):
        people_before = {g.id: (g.band, g.age, g.version) for g in self._guests()}
        version = self.uc.get_guest_list.execute(NOIVO).settings.version
        with contextlib.suppress(InvalidAgeLimits):
            self.uc.update_guest_settings.execute(
                UpdateGuestSettingsCommand(version, weights, exempt, paying), actor
            )
        # F-CNV-03, regra 4: mudar pesos ou limites nunca toca em nenhuma pessoa.
        assert people_before == {g.id: (g.band, g.age, g.version) for g in self._guests()}

    @rule(
        pick=PICK,
        day=st.integers(1, 27),
        channel=st.sampled_from(list(InviteChannel)),
        move_drafts=st.booleans(),
        actor=ACTORS,
    )
    def record_invite(self, pick, day, channel, move_drafts, actor):
        households = self._households()
        if households:
            household = households[pick % len(households)]
            statuses_before = {g.id: g.status for g in household.guests}
            self.clock.advance(minutes=1)
            self.uc.record_household_invite.execute(
                RecordHouseholdInviteCommand(
                    household.id, household.version, date(2026, 10, day), channel, move_drafts
                ),
                actor,
            )
            after = {g.id: g.status for g in self._guests() if g.id in statuses_before}
            for guest_id, before in statuses_before.items():
                # F-CNV-05: só Rascunho muda, e só com a oferta aceita; o resto nunca é tocado.
                if move_drafts and before is GuestStatus.DRAFT:
                    assert after[guest_id] is GuestStatus.INVITED
                else:
                    assert after[guest_id] is before

    @rule(pick=PICK, actor=ACTORS)
    def clear_invite(self, pick, actor):
        households = self._households()
        if households:
            household = households[pick % len(households)]
            statuses_before = {g.id: g.status for g in household.guests}
            self.uc.clear_household_invite.execute(
                ClearHouseholdInviteCommand(household.id, household.version), actor
            )
            assert statuses_before == {
                g.id: g.status for g in self._guests() if g.id in statuses_before
            }

    @rule(pick=PICK)
    def stale_version_is_always_refused(self, pick):
        guests = self._guests()
        if guests:
            guest = guests[pick % len(guests)]
            try:
                self.uc.change_guest_status.execute(
                    ChangeGuestStatusCommand(
                        guest.id, GuestStatus.CONFIRMED, None, guest.version + 1
                    ),
                    NOIVO,
                )
                raise AssertionError("uma versão errada foi aceita")
            except VersionConflict:
                pass

    # --- invariantes

    def _live_households(self):
        return [h for h in self.world.store.households.values() if h.deleted_at is None]

    def _live_guests(self):
        live = {h.id for h in self._live_households()}
        return [
            g
            for g in self.world.store.guests.values()
            if g.deleted_at is None and g.household_id in live
        ]

    @invariant()
    def household_names_are_unique_among_the_living(self):
        keys = [h.name_key for h in self._live_households()]
        assert len(keys) == len(set(keys))
        assert all(h.name_key == name_key(h.name) for h in self._live_households())

    @invariant()
    def every_live_household_has_at_least_one_live_guest(self):
        for household in self._live_households():
            members = [g for g in self._live_guests() if g.household_id == household.id]
            assert members, "núcleo vivo ficou sem pessoas"

    @invariant()
    def companions_follow_the_rules(self):
        by_id = self.world.store.guests
        holders: dict = {}
        for guest in self._live_guests():
            if guest.companion_of_id is None:
                assert guest.name, "só o acompanhante fica sem nome"
                continue
            holder = by_id[guest.companion_of_id]
            assert holder.deleted_at is None
            assert holder.companion_of_id is None
            assert holder.household_id == guest.household_id
            assert guest.companion_of_id not in holders, "dois acompanhantes no titular"
            holders[guest.companion_of_id] = guest.id

    @invariant()
    def reason_and_age_only_where_they_belong(self):
        for guest in self.world.store.guests.values():
            if guest.decline_reason is not None:
                assert guest.status is GuestStatus.DECLINED
            if guest.age is not None:
                assert guest.band is not AgeBand.ADULT

    @invariant()
    def status_history_is_a_continuous_chain_ending_in_the_current_status(self):
        for guest in self.world.store.guests.values():
            chain = [c for c in self.world.changes if c.guest_id == guest.id]
            expected = GuestStatus.DRAFT
            for change in chain:
                assert change.from_status is expected
                assert change.from_status is not change.to_status
                expected = change.to_status
            assert guest.status is expected

    @invariant()
    def summaries_match_a_direct_recount(self):
        for household in self._households():
            summary = household.summary
            assert summary.total == len(household.guests)
            for status, counted in (
                (GuestStatus.CONFIRMED, summary.confirmed),
                (GuestStatus.INVITED, summary.invited),
                (GuestStatus.DRAFT, summary.draft),
                (GuestStatus.DECLINED, summary.declined),
            ):
                assert counted == sum(g.status is status for g in household.guests)

    @invariant()
    def headcount_matches_a_direct_recount_with_exact_fractions(self):
        listing = self.uc.get_guest_list.execute(NOIVO)
        live = self._live_guests()
        attending = [g for g in live if g.status is not GuestStatus.DECLINED]
        headcount = listing.headcount
        assert headcount.total_nominal.total == len(attending)
        assert headcount.confirmed.total == sum(
            g.status is GuestStatus.CONFIRMED for g in attending
        )
        assert headcount.not_attending.total == len(live) - len(attending)
        weights = listing.settings.weights
        if weights is None:
            assert headcount.weighted_rounded_up is None
        else:
            exact = sum(
                (
                    Fraction(
                        100 if g.status is GuestStatus.CONFIRMED else weights.of(g.probability), 100
                    )
                    for g in attending
                    if g.band is not AgeBand.EXEMPT_CHILD
                ),
                Fraction(0),
            )
            parts = (
                headcount.weighted_adults_hundredths,
                headcount.weighted_paying_children_hundredths,
            )
            assert Fraction(sum(p or 0 for p in parts), 100) == exact
            assert headcount.weighted_rounded_up == math.ceil(exact)
        # O contrato que o orçamento lê é a mesma conta da lista.
        assert self.uc.get_guest_headcount.execute(NOIVO) == headcount

    @invariant()
    def the_invite_is_a_date_and_a_channel_together_and_never_in_the_future(self):
        for household in self._live_households():
            assert (household.invite_sent_on is None) == (household.invite_channel is None)
            if household.invite_sent_on is not None:
                assert household.invite_sent_on <= date(2026, 10, 27)


GuestsMachine.TestCase.settings = settings(max_examples=60, stateful_step_count=30, deadline=None)
TestGuestsMachine = GuestsMachine.TestCase
