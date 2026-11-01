from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from wedding.modules.guests.domain.contact import (
    clean_email,
    clean_postal_code,
    normalize_phone,
)
from wedding.modules.guests.domain.errors import CompanionNeedsName, InvalidGuestValue
from wedding.modules.guests.domain.values import (
    MAX_DIETARY,
    MAX_NOTE,
    MAX_NUMBER,
    MAX_REASON,
    MAX_SHORT,
    MAX_STREET,
    AgeBand,
    GuestStatus,
    Probability,
    Side,
    clean_age,
    clean_guest_name,
    clean_household_name,
    clean_state,
    clean_text,
    name_key,
)
from wedding.shared_kernel.profile import ProfileKind


@dataclass
class Household:
    """Um núcleo familiar (F-CNV-01). `version` é mantido pelo mapeamento (bloqueio otimista);
    `members_revision` sobe quando a composição muda, para duas saídas simultâneas se conflitarem
    (um núcleo nunca fica sem pessoas)."""

    id: UUID
    name: str
    side: Side
    street: str | None = None
    number: str | None = None
    complement: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    note: str | None = None
    name_key: str = field(init=False, default="")
    members_revision: int = 0
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    version: int = 0

    def __post_init__(self) -> None:
        self._apply(
            self._cleaned(
                self.name,
                self.street,
                self.number,
                self.complement,
                self.district,
                self.city,
                self.state,
                self.postal_code,
                self.note,
            )
        )

    @staticmethod
    def _cleaned(
        name: str,
        street: str | None,
        number: str | None,
        complement: str | None,
        district: str | None,
        city: str | None,
        state: str | None,
        postal_code: str | None,
        note: str | None,
    ) -> tuple[str | None, ...]:
        return (
            clean_household_name(name),
            clean_text(street, MAX_STREET),
            clean_text(number, MAX_NUMBER),
            clean_text(complement, MAX_SHORT),
            clean_text(district, MAX_SHORT),
            clean_text(city, MAX_SHORT),
            clean_state(state),
            clean_postal_code(postal_code),
            clean_text(note, MAX_NOTE),
        )

    def _apply(self, values: tuple[str | None, ...]) -> None:
        (
            name,
            self.street,
            self.number,
            self.complement,
            self.district,
            self.city,
            self.state,
            self.postal_code,
            self.note,
        ) = values
        assert name is not None
        self.name, self.name_key = name, name_key(name)

    def update(
        self,
        *,
        name: str,
        side: Side,
        street: str | None = None,
        number: str | None = None,
        complement: str | None = None,
        district: str | None = None,
        city: str | None = None,
        state: str | None = None,
        postal_code: str | None = None,
        note: str | None = None,
    ) -> bool:
        cleaned = self._cleaned(
            name, street, number, complement, district, city, state, postal_code, note
        )
        current = (
            self.name,
            self.street,
            self.number,
            self.complement,
            self.district,
            self.city,
            self.state,
            self.postal_code,
            self.note,
        )
        if cleaned == current and side is self.side:
            return False
        self._apply(cleaned)
        self.side = side
        return True

    def touch_members(self) -> None:
        self.members_revision += 1

    def delete(self, now: datetime, by: UUID | None) -> None:
        self.deleted_at, self.deleted_by = now, by

    def restore(self) -> None:
        self.deleted_at, self.deleted_by = None, None


@dataclass
class Guest:
    """Uma pessoa da lista (F-CNV-01). Não tem lado próprio: herda o do núcleo. Sem nome só o
    acompanhante a confirmar (F-CNV-02); a idade só vale para criança e nunca muda a faixa."""

    id: UUID
    household_id: UUID
    position: int
    name: str | None
    band: AgeBand = AgeBand.ADULT
    age: int | None = None
    probability: Probability = Probability.PROBABLE
    status: GuestStatus = GuestStatus.DRAFT
    decline_reason: str | None = None
    dietary_restriction: str | None = None
    note: str | None = None
    phone: str | None = None
    email: str | None = None
    companion_of_id: UUID | None = None
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    version: int = 0

    def __post_init__(self) -> None:
        self._apply(
            *self._cleaned(
                self.name,
                self.band,
                self.age,
                self.dietary_restriction,
                self.note,
                self.phone,
                self.email,
                self.decline_reason,
                self.status,
            )
        )

    @property
    def is_companion(self) -> bool:
        return self.companion_of_id is not None

    def _cleaned(
        self,
        name: str | None,
        band: AgeBand,
        age: int | None,
        dietary_restriction: str | None,
        note: str | None,
        phone: str | None,
        email: str | None,
        decline_reason: str | None,
        status: GuestStatus,
    ) -> tuple[str | None, int | None, str | None, str | None, str | None, str | None, str | None]:
        reason = clean_text(decline_reason, MAX_REASON)
        if reason is not None and status is not GuestStatus.DECLINED:
            raise InvalidGuestValue()
        return (
            clean_guest_name(name, required=not self.is_companion),
            clean_age(age, band),
            clean_text(dietary_restriction, MAX_DIETARY),
            clean_text(note, MAX_NOTE),
            normalize_phone(phone),
            clean_email(email),
            reason,
        )

    def _apply(
        self,
        name: str | None,
        age: int | None,
        dietary_restriction: str | None,
        note: str | None,
        phone: str | None,
        email: str | None,
        decline_reason: str | None,
    ) -> None:
        self.name, self.age, self.dietary_restriction, self.note = (
            name,
            age,
            dietary_restriction,
            note,
        )
        self.phone, self.email, self.decline_reason = phone, email, decline_reason

    def update(
        self,
        *,
        name: str | None,
        band: AgeBand,
        age: int | None,
        probability: Probability,
        dietary_restriction: str | None,
        note: str | None,
        phone: str | None,
        email: str | None,
        decline_reason: str | None,
    ) -> bool:
        cleaned = self._cleaned(
            name, band, age, dietary_restriction, note, phone, email, decline_reason, self.status
        )
        current = (
            self.name,
            self.age,
            self.dietary_restriction,
            self.note,
            self.phone,
            self.email,
            self.decline_reason,
        )
        if cleaned == current and band is self.band and probability is self.probability:
            return False
        self._apply(*cleaned)
        self.band, self.probability = band, probability
        return True

    def change_status(self, to: GuestStatus, reason: str | None) -> bool:
        """Qualquer status vai para qualquer outro; o motivo só existe com `Não irá` e some ao
        sair dele (F-CNV-04). Repetir o status não é mudança."""
        cleaned = clean_text(reason, MAX_REASON)
        if cleaned is not None and to is not GuestStatus.DECLINED:
            raise InvalidGuestValue()
        if to is self.status:
            return False
        self.status = to
        self.decline_reason = cleaned
        return True

    def move_to(self, household_id: UUID, position: int) -> bool:
        if household_id == self.household_id:
            return False
        self.household_id, self.position = household_id, position
        return True

    def unlink_companion(self) -> None:
        """ "Manter" o acompanhante ao excluir o titular (F-CNV-02, regra 4): vira convidado comum,
        o que exige nome."""
        if self.name is None:
            raise CompanionNeedsName()
        self.companion_of_id = None

    def delete(self, now: datetime, by: UUID | None) -> None:
        self.deleted_at, self.deleted_by = now, by

    def restore(self) -> None:
        self.deleted_at, self.deleted_by = None, None


@dataclass
class GuestStatusChange:
    """Uma mudança de status (F-CNV-04, regra 4): só se acrescenta; o instante vem do histórico
    básico e o perfil fica na linha."""

    id: UUID
    guest_id: UUID
    from_status: GuestStatus
    to_status: GuestStatus
    reason: str | None
    profile: ProfileKind
