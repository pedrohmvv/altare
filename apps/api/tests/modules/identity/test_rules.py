from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.identity.domain.entities import UserSession
from wedding.modules.identity.domain.rules import (
    login_retry_after,
    session_expired,
    should_touch,
)

AGORA = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def _sessao(criada_ha: timedelta, vista_ha: timedelta) -> UserSession:
    return UserSession(
        id=uuid4(),
        user_id=uuid4(),
        token_hash="h" * 64,
        created_at=AGORA - criada_ha,
        last_seen_at=AGORA - vista_ha,
    )


def test_sessao_recem_criada_nao_esta_vencida():
    assert not session_expired(_sessao(timedelta(0), timedelta(0)), AGORA)


def test_sessao_sem_uso_por_menos_de_30_dias_segue_valida():
    assert not session_expired(_sessao(timedelta(days=40), timedelta(days=30, seconds=-1)), AGORA)


def test_sessao_sem_uso_por_30_dias_vence():
    assert session_expired(_sessao(timedelta(days=40), timedelta(days=30)), AGORA)


def test_sessao_com_uso_recente_vence_aos_90_dias_desde_a_criacao():
    assert session_expired(_sessao(timedelta(days=90), timedelta(minutes=1)), AGORA)


def test_sessao_com_uso_recente_segue_valida_antes_dos_90_dias():
    assert not session_expired(_sessao(timedelta(days=90, seconds=-1), timedelta(minutes=1)), AGORA)


@given(
    criada=st.integers(min_value=0, max_value=200),
    vista=st.integers(min_value=0, max_value=200),
    depois=st.integers(min_value=0, max_value=200),
)
def test_sessao_vencida_nunca_volta_a_valer_com_o_tempo(criada, vista, depois):
    sessao = _sessao(timedelta(days=max(criada, vista)), timedelta(days=vista))
    if session_expired(sessao, AGORA):
        assert session_expired(sessao, AGORA + timedelta(days=depois))


def test_renovar_o_uso_so_depois_de_uma_hora():
    assert not should_touch(_sessao(timedelta(days=2), timedelta(minutes=59, seconds=59)), AGORA)
    assert should_touch(_sessao(timedelta(days=2), timedelta(hours=1)), AGORA)


def _falhas(*minutos_atras: float) -> list[datetime]:
    return [AGORA - timedelta(minutes=m) for m in minutos_atras]


def test_menos_de_cinco_falhas_recentes_nao_bloqueiam():
    assert login_retry_after(_falhas(1, 2, 3, 4), AGORA) is None


def test_cinco_falhas_em_15_minutos_bloqueiam_ate_a_mais_antiga_sair_da_janela():
    # a mais antiga tem 10 min: faltam 5 min (300 s) para ela sair da janela
    assert login_retry_after(_falhas(10, 8, 6, 4, 2), AGORA) == 300


def test_o_tempo_de_espera_arredonda_para_cima():
    antiga = AGORA - timedelta(minutes=14, seconds=59, milliseconds=500)
    falhas = [antiga, *_falhas(5, 4, 3, 2)]
    assert login_retry_after(falhas, AGORA) == 1


def test_falha_com_exatamente_15_minutos_ja_saiu_da_janela():
    assert login_retry_after(_falhas(15, 4, 3, 2, 1), AGORA) is None


@pytest.mark.parametrize("quantidade", [0, 1, 2, 3, 4])
def test_poucas_falhas_nunca_bloqueiam_em_qualquer_ritmo(quantidade):
    assert login_retry_after(_falhas(*[0.5] * quantidade), AGORA) is None


@given(minutos=st.lists(st.floats(min_value=0, max_value=14.9), min_size=5, max_size=20))
def test_cinco_ou_mais_falhas_na_janela_sempre_bloqueiam_por_no_maximo_15_minutos(minutos):
    espera = login_retry_after(_falhas(*minutos), AGORA)
    assert espera is not None
    assert 0 < espera <= 15 * 60
