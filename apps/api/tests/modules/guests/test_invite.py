from datetime import date
from uuid import UUID

import pytest

from wedding.modules.guests.domain.entities import Household
from wedding.modules.guests.domain.errors import InvalidInvite
from wedding.modules.guests.domain.values import InviteChannel, Side

HOJE = date(2026, 10, 28)


def nucleo() -> Household:
    return Household(id=UUID(int=1), name="Família Exemplo", side=Side.COMUM)


def test_o_nucleo_nasce_sem_convite_enviado():  # F-CNV-05
    household = nucleo()

    assert (household.invite_sent_on, household.invite_channel) == (None, None)


def test_registrar_o_envio_guarda_a_data_e_o_canal_juntos():  # F-CNV-05
    household = nucleo()

    changed = household.record_invite(date(2026, 10, 20), InviteChannel.WHATSAPP, today=HOJE)

    assert changed is True
    assert (household.invite_sent_on, household.invite_channel) == (
        date(2026, 10, 20),
        InviteChannel.WHATSAPP,
    )


def test_o_envio_de_hoje_vale_e_o_futuro_e_recusado():
    household = nucleo()
    household.record_invite(HOJE, InviteChannel.PRINTED, today=HOJE)

    with pytest.raises(InvalidInvite):
        household.record_invite(date(2026, 10, 29), InviteChannel.PRINTED, today=HOJE)
    assert household.invite_sent_on == HOJE


def test_repetir_o_mesmo_envio_nao_e_mudanca():
    household = nucleo()
    household.record_invite(HOJE, InviteChannel.EMAIL, today=HOJE)

    assert household.record_invite(HOJE, InviteChannel.EMAIL, today=HOJE) is False


def test_editar_so_o_canal_ou_so_a_data_e_mudanca():
    household = nucleo()
    household.record_invite(HOJE, InviteChannel.EMAIL, today=HOJE)

    assert household.record_invite(HOJE, InviteChannel.OTHER, today=HOJE) is True
    assert household.record_invite(date(2026, 10, 1), InviteChannel.OTHER, today=HOJE) is True


def test_limpar_o_envio_volta_a_nao_enviado_e_limpar_de_novo_nao_muda():
    household = nucleo()
    household.record_invite(HOJE, InviteChannel.IN_PERSON, today=HOJE)

    assert household.clear_invite() is True
    assert (household.invite_sent_on, household.invite_channel) == (None, None)
    assert household.clear_invite() is False


def test_os_cinco_canais_da_spec():
    assert [c.value for c in InviteChannel] == [
        "WhatsApp",
        "E-mail",
        "Impresso",
        "Pessoalmente",
        "Outro",
    ]
