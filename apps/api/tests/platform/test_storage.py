import hashlib
import os
from threading import Thread

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from wedding.platform.storage.local import LocalFileStorage


def _chave(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


@pytest.fixture
def storage(tmp_path):
    return LocalFileStorage(tmp_path / "arquivos")


def _ler(storage, chave) -> bytes:
    return b"".join(storage.read(chave))


def test_guarda_e_devolve_o_conteudo(storage):
    conteudo = b"%PDF-1.7 conteudo de exemplo"
    storage.put(_chave(conteudo), conteudo)
    assert _ler(storage, _chave(conteudo)) == conteudo


def test_sabe_se_o_conteudo_existe(storage):
    conteudo = b"exemplo"
    assert storage.exists(_chave(conteudo)) is False
    storage.put(_chave(conteudo), conteudo)
    assert storage.exists(_chave(conteudo)) is True


def test_o_nome_em_disco_e_so_o_hash_em_duas_pastas(storage, tmp_path):
    conteudo = b"exemplo"
    chave = _chave(conteudo)
    storage.put(chave, conteudo)
    arquivos = [p for p in (tmp_path / "arquivos").rglob("*") if p.is_file()]
    assert [p.relative_to(tmp_path / "arquivos").as_posix() for p in arquivos] == [
        f"{chave[:2]}/{chave}"
    ]


def test_gravar_de_novo_o_mesmo_conteudo_nao_reescreve_o_arquivo(storage, tmp_path):
    conteudo = b"exemplo"
    chave = _chave(conteudo)
    storage.put(chave, conteudo)
    caminho = tmp_path / "arquivos" / chave[:2] / chave
    antes = caminho.stat().st_ino, caminho.stat().st_mtime_ns
    storage.put(chave, conteudo)
    assert (caminho.stat().st_ino, caminho.stat().st_mtime_ns) == antes


def test_nao_deixa_arquivo_temporario_depois_de_gravar(storage, tmp_path):
    conteudo = b"exemplo"
    storage.put(_chave(conteudo), conteudo)
    nomes = [p.name for p in (tmp_path / "arquivos").rglob("*") if p.is_file()]
    assert all(not nome.startswith(".") for nome in nomes)


def test_so_o_dono_do_computador_le_os_arquivos(storage, tmp_path):
    conteudo = b"exemplo"
    chave = _chave(conteudo)
    storage.put(chave, conteudo)
    caminho = tmp_path / "arquivos" / chave[:2] / chave
    assert caminho.stat().st_mode & 0o077 == 0


def test_falha_na_gravacao_nao_deixa_um_arquivo_pela_metade(storage, tmp_path, monkeypatch):
    def quebrar(*_args, **_kwargs):
        raise OSError("disco cheio")

    monkeypatch.setattr(os, "replace", quebrar)
    conteudo = b"exemplo"
    with pytest.raises(OSError, match="disco cheio"):
        storage.put(_chave(conteudo), conteudo)
    restos = [p for p in (tmp_path / "arquivos").rglob("*") if p.is_file()]
    assert restos == []
    assert storage.exists(_chave(conteudo)) is False


@pytest.mark.parametrize(
    "chave",
    ["", "abc", "../../etc/passwd", "a" * 63, "a" * 65, "A" * 64, "g" * 64, "a" * 62 + "/x"],
)
def test_recusa_qualquer_chave_que_nao_seja_um_sha256_em_minusculas(storage, chave):
    with pytest.raises(ValueError, match="SHA-256"):
        storage.put(chave, b"x")
    with pytest.raises(ValueError, match="SHA-256"):
        storage.exists(chave)
    with pytest.raises(ValueError, match="SHA-256"):
        list(storage.read(chave))


def test_ler_o_que_nao_existe_e_um_erro_claro(storage):
    with pytest.raises(FileNotFoundError):
        list(storage.read("a" * 64))


def test_le_em_pedacos_sem_carregar_tudo_de_uma_vez(storage):
    conteudo = os.urandom(200_000)
    storage.put(_chave(conteudo), conteudo)
    pedacos = list(storage.read(_chave(conteudo)))
    assert len(pedacos) > 1
    assert all(len(p) <= 64 * 1024 for p in pedacos)


def test_duas_gravacoes_simultaneas_do_mesmo_conteudo_dao_um_arquivo_so(storage):
    conteudo = os.urandom(50_000)
    chave = _chave(conteudo)
    threads = [Thread(target=storage.put, args=(chave, conteudo)) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert _ler(storage, chave) == conteudo


@settings(max_examples=40, deadline=None)
@given(conteudo=st.binary(min_size=0, max_size=5000))
def test_qualquer_conteudo_volta_igual_ao_que_foi_gravado(tmp_path_factory, conteudo):
    storage = LocalFileStorage(tmp_path_factory.mktemp("prop"))
    storage.put(_chave(conteudo), conteudo)
    assert _ler(storage, _chave(conteudo)) == conteudo
