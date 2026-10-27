from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.clock import SystemClock
from wedding.shared_kernel.ids import UuidGenerator, new_id
from wedding.shared_kernel.profile import ProfileKind


def test_perfis_usam_os_nomes_do_dominio():
    assert [p.value for p in ProfileKind] == ["Noivo", "Noiva", "Ambos"]
    assert ProfileKind("Noiva") is ProfileKind.NOIVA


@pytest.mark.parametrize("perfil", [ProfileKind.NOIVO, ProfileKind.NOIVA])
def test_ator_guarda_usuario_e_perfil_da_sessao(perfil):
    usuario = uuid4()
    ator = Actor(user_id=usuario, profile=perfil)
    assert (ator.user_id, ator.profile) == (usuario, perfil)


def test_ator_nao_pode_ser_o_perfil_ambos():
    with pytest.raises(ValueError, match="Ambos"):
        Actor(user_id=uuid4(), profile=ProfileKind.AMBOS)


def test_ator_e_imutavel():
    ator = Actor(user_id=uuid4(), profile=ProfileKind.NOIVO)
    with pytest.raises(AttributeError):
        ator.profile = ProfileKind.NOIVA  # type: ignore[misc]


def test_ids_sao_uuid_unicos_v7_ou_v4():
    ids = [new_id() for _ in range(1000)]
    assert all(isinstance(i, UUID) for i in ids)
    assert len(set(ids)) == 1000
    assert {i.version for i in ids} <= {4, 7}


def test_gerador_de_ids_usa_a_mesma_regra():
    assert UuidGenerator().new_id().version in {4, 7}
    assert UuidGenerator().new_id() != UuidGenerator().new_id()


def test_relogio_do_sistema_devolve_utc_com_fuso():
    agora = SystemClock().now()
    assert agora.tzinfo is UTC
    assert abs(datetime.now(UTC) - agora) < timedelta(seconds=5)
