from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from wedding.modules.guests.application.dto import GuestListDto

HEADERS = (
    "Núcleo",
    "Lado",
    "Nome",
    "Faixa",
    "Idade",
    "Probabilidade",
    "Status",
    "Restrição alimentar",
    "Observação",
    "Telefone",
    "E-mail",
    "Endereço do núcleo",
    "Convite enviado (data)",
    "Canal",
    "Motivo (Não irá)",
)

Cell = str | int | date | None


@dataclass(frozen=True)
class ExportRow:
    """Uma pessoa por linha, nas colunas fixas da F-CNV-08. Os textos saem crus, como estão na
    lista; quem escreve o arquivo os protege contra fórmula (`neutralize_cell`)."""

    cells: tuple[Cell, ...]


def is_formula_like(text: str) -> bool:
    """O Excel e o LibreOffice tratam como fórmula o que começa com `=`, `+`, `-` ou `@`, e a
    tabulação e o retorno de carro no começo escondem esses caracteres (OWASP, "CSV injection").
    Vale também depois de espaços iniciais, por segurança."""
    return text[:1] in ("\t", "\r") or text.lstrip()[:1] in ("=", "+", "-", "@")


def neutralize_cell(text: str) -> str:
    """Para o CSV, onde não há tipo de célula: um apóstrofo na frente tira o texto do caminho da
    fórmula e, se o programa o mostrar, é só um apóstrofo; o resto do texto fica intacto."""
    return f"'{text}" if is_formula_like(text) else text


def _address(household) -> str:  # type: ignore[no-untyped-def]
    place = "/".join(part for part in (household.city, household.state) if part)
    parts = (
        ", ".join(part for part in (household.street, household.number) if part),
        household.complement,
        household.district,
        place,
        f"CEP {household.postal_code}" if household.postal_code else None,
    )
    return ", ".join(part for part in parts if part)


def build_export_rows(
    listing: GuestListDto, guest_ids: Sequence[UUID] | None = None
) -> list[ExportRow]:
    """As linhas da exportação, na ordem da lista (núcleo por nome, pessoa por cadastro). O endereço
    e o convite do núcleo se repetem em cada linha dele (F-CNV-08, regra 1). `guest_ids` leva só o
    que está na tela (regra 2); ausente, leva todas. Nada de id, versão, auditoria nem histórico."""
    wanted = None if guest_ids is None else set(guest_ids)
    rows: list[ExportRow] = []
    for household in listing.households:
        address = _address(household)
        for guest in household.guests:
            if wanted is not None and guest.id not in wanted:
                continue
            name = guest.name or (
                f"Acompanhante de {guest.holder_name}" if guest.holder_name else "Acompanhante"
            )
            rows.append(
                ExportRow(
                    (
                        household.name,
                        household.side.value,
                        name,
                        guest.band.value,
                        guest.age,
                        guest.probability.value,
                        guest.status.value,
                        guest.dietary_restriction,
                        guest.note,
                        guest.phone,
                        guest.email,
                        address or None,
                        household.invite_sent_on,
                        household.invite_channel.value if household.invite_channel else None,
                        guest.decline_reason,
                    )
                )
            )
    return rows
