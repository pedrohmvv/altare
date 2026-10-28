from datetime import UTC, datetime
from uuid import UUID

import pytest

from wedding.modules.guests.domain.entities import Guest, Household
from wedding.modules.guests.domain.errors import (
    CompanionNeedsName,
    GuestNameRequired,
    InvalidEmail,
    InvalidGuestValue,
    InvalidPhone,
)
from wedding.modules.guests.domain.values import (
    AgeBand,
    GuestStatus,
    Probability,
    Side,
    name_key,
)

AGORA = datetime(2026, 10, 28, 12, tzinfo=UTC)
ID = UUID(int=1)
OUTRO = UUID(int=2)


def nucleo(**campos) -> Household:
    return Household(id=ID, name="Família Exemplo", side=Side.COMUM, **campos)


def pessoa(**campos) -> Guest:
    base = {"id": ID, "household_id": OUTRO, "position": 0, "name": "Convidado Exemplo A"}
    return Guest(**(base | campos))


class TestHousehold:
    def test_nome_e_lado_obrigatorios_e_chave_derivada(self):
        household = nucleo()

        assert household.name_key == name_key("Família Exemplo")
        assert household.side is Side.COMUM

    def test_endereco_e_normalizado(self):
        household = nucleo(
            street=" Rua Exemplo ", state="sp", postal_code="00000-000", number="100", city=" "
        )

        assert household.street == "Rua Exemplo"
        assert household.state == "SP"
        assert household.postal_code == "00000000"
        assert household.city is None

    def test_cep_fora_do_formato_e_recusado(self):
        with pytest.raises(InvalidGuestValue):
            nucleo(postal_code="123")

    def test_atualizar_so_conta_mudanca_real(self):
        household = nucleo(note="Do lado da mãe")
        iguais = {"name": "  Família  Exemplo ", "side": Side.COMUM, "note": "Do lado da mãe"}

        assert household.update(**iguais) is False
        assert household.update(**(iguais | {"side": Side.NOIVA})) is True
        assert household.side is Side.NOIVA

    def test_renomear_recalcula_a_chave(self):
        household = nucleo()

        household.update(name="Outra Família Exemplo", side=Side.COMUM)

        assert household.name_key == name_key("Outra Família Exemplo")

    def test_mudar_a_composicao_sobe_a_revisao_dos_membros(self):
        household = nucleo()

        household.touch_members()

        assert household.members_revision == 1

    def test_excluir_e_restaurar(self):
        household = nucleo()

        household.delete(AGORA, OUTRO)
        assert (household.deleted_at, household.deleted_by) == (AGORA, OUTRO)

        household.restore()
        assert (household.deleted_at, household.deleted_by) == (None, None)


class TestGuest:
    def test_padroes_da_spec(self):  # F-CNV-01
        guest = pessoa()

        assert guest.band is AgeBand.ADULT
        assert guest.probability is Probability.PROBABLE
        assert guest.status is GuestStatus.DRAFT

    def test_nome_e_obrigatorio_fora_do_acompanhante(self):
        with pytest.raises(GuestNameRequired):
            pessoa(name=None)

    def test_acompanhante_pode_ficar_sem_nome(self):  # F-CNV-02
        guest = pessoa(name=None, companion_of_id=OUTRO)

        assert guest.is_companion
        assert guest.name is None

    def test_contatos_sao_validados_e_normalizados(self):
        guest = pessoa(phone="(11) 91234-5678", email=" convidado@exemplo.invalid ")

        assert guest.phone == "11912345678"
        assert guest.email == "convidado@exemplo.invalid"
        with pytest.raises(InvalidPhone):
            pessoa(phone="123")
        with pytest.raises(InvalidEmail):
            pessoa(email="convidado")

    def test_idade_so_para_crianca(self):
        assert pessoa(band=AgeBand.EXEMPT_CHILD, age=4).age == 4
        with pytest.raises(InvalidGuestValue):
            pessoa(age=4)

    def test_mudar_para_adulto_com_idade_e_recusado(self):
        guest = pessoa(band=AgeBand.PAYING_CHILD, age=9)

        with pytest.raises(InvalidGuestValue):
            guest.update(**_campos(guest, band=AgeBand.ADULT))

    def test_atualizar_so_conta_mudanca_real(self):
        guest = pessoa(dietary_restriction="Sem lactose")

        assert guest.update(**_campos(guest)) is False
        assert guest.update(**_campos(guest, probability=Probability.CERTAIN)) is True
        assert guest.probability is Probability.CERTAIN

    def test_informar_o_nome_do_acompanhante_mantem_o_vinculo(self):  # F-CNV-02, regra 3
        guest = pessoa(name=None, companion_of_id=OUTRO)

        assert guest.update(**_campos(guest, name="Acompanhante Exemplo")) is True
        assert guest.name == "Acompanhante Exemplo"
        assert guest.companion_of_id == OUTRO

    def test_motivo_so_existe_com_nao_ira(self):  # F-CNV-04, regra 2
        guest = pessoa()

        assert guest.change_status(GuestStatus.DECLINED, " Viagem ") is True
        assert (guest.status, guest.decline_reason) == (GuestStatus.DECLINED, "Viagem")

        assert guest.change_status(GuestStatus.CONFIRMED, None) is True
        assert (guest.status, guest.decline_reason) == (GuestStatus.CONFIRMED, None)

    def test_nao_ira_aceita_ficar_sem_motivo(self):
        guest = pessoa()

        guest.change_status(GuestStatus.DECLINED, None)

        assert guest.decline_reason is None

    def test_motivo_com_outro_status_e_recusado(self):
        guest = pessoa()

        with pytest.raises(InvalidGuestValue):
            guest.change_status(GuestStatus.CONFIRMED, "Viagem")

    def test_repetir_o_status_nao_e_mudanca(self):
        guest = pessoa(status=GuestStatus.CONFIRMED)

        assert guest.change_status(GuestStatus.CONFIRMED, None) is False

    def test_qualquer_status_vai_para_qualquer_outro(self):  # decisão 3 do usuário
        for origem in GuestStatus:
            for destino in GuestStatus:
                guest = pessoa(status=origem)
                assert guest.change_status(destino, None) is (origem is not destino)
                assert guest.status is destino

    def test_motivo_so_se_edita_enquanto_nao_ira(self):
        guest = pessoa(status=GuestStatus.DECLINED, decline_reason="Viagem")

        assert guest.update(**_campos(guest, decline_reason="Trabalho")) is True
        assert guest.decline_reason == "Trabalho"

        confirmado = pessoa(status=GuestStatus.CONFIRMED)
        with pytest.raises(InvalidGuestValue):
            confirmado.update(**_campos(confirmado, decline_reason="Viagem"))

    def test_mover_para_outro_nucleo(self):
        guest = pessoa()

        assert guest.move_to(OUTRO, 3) is False
        destino = UUID(int=9)
        assert guest.move_to(destino, 3) is True
        assert (guest.household_id, guest.position) == (destino, 3)

    def test_desvincular_acompanhante_exige_nome(self):  # F-CNV-02, regra 4 e decisão 11
        sem_nome = pessoa(name=None, companion_of_id=OUTRO)
        with pytest.raises(CompanionNeedsName):
            sem_nome.unlink_companion()

        com_nome = pessoa(name="Acompanhante Exemplo", companion_of_id=OUTRO)
        com_nome.unlink_companion()
        assert not com_nome.is_companion

    def test_excluir_e_restaurar(self):
        guest = pessoa()

        guest.delete(AGORA, OUTRO)
        assert guest.deleted_at == AGORA

        guest.restore()
        assert guest.deleted_at is None


def _campos(guest: Guest, **mudancas):
    atuais = {
        "name": guest.name,
        "band": guest.band,
        "age": guest.age,
        "probability": guest.probability,
        "dietary_restriction": guest.dietary_restriction,
        "note": guest.note,
        "phone": guest.phone,
        "email": guest.email,
        "decline_reason": guest.decline_reason,
    }
    return atuais | mudancas
