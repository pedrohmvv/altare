from datetime import UTC, datetime, timedelta
from threading import Thread

from wedding.modules.identity.infrastructure.login_attempts import InMemoryLoginAttempts

AGORA = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
SEMPRE = datetime(2000, 1, 1, tzinfo=UTC)


def test_devolve_so_as_falhas_a_partir_do_instante_pedido():
    tentativas = InMemoryLoginAttempts()
    tentativas.add_failure("a|ip", AGORA - timedelta(minutes=10))
    tentativas.add_failure("a|ip", AGORA)
    assert tentativas.failures("a|ip", AGORA - timedelta(minutes=5)) == [AGORA]


def test_chaves_diferentes_nao_se_misturam():
    tentativas = InMemoryLoginAttempts()
    tentativas.add_failure("a|ip", AGORA)
    assert tentativas.failures("b|ip", SEMPRE) == []


def test_limpar_zera_a_contagem_da_chave():
    tentativas = InMemoryLoginAttempts()
    tentativas.add_failure("a|ip", AGORA)
    tentativas.clear("a|ip")
    tentativas.clear("chave-que-nao-existe")
    assert tentativas.failures("a|ip", SEMPRE) == []


def test_falhas_vencidas_de_outras_chaves_sao_varridas_para_a_memoria_nao_crescer():
    tentativas = InMemoryLoginAttempts()
    tentativas.add_failure("antigo|ip", AGORA)
    tentativas.add_failure("novo|ip", AGORA + timedelta(minutes=20))
    assert tentativas.failures("antigo|ip", SEMPRE) == []
    assert tentativas.failures("novo|ip", SEMPRE) == [AGORA + timedelta(minutes=20)]


def test_aguenta_falhas_de_varias_threads_ao_mesmo_tempo():
    tentativas = InMemoryLoginAttempts()

    def errar() -> None:
        for _ in range(200):
            tentativas.add_failure("a|ip", AGORA)

    threads = [Thread(target=errar) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(tentativas.failures("a|ip", SEMPRE)) == 1600
