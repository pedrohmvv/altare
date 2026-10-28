from argon2 import PasswordHasher as Argon2

from wedding.modules.identity.infrastructure.argon2_hasher import Argon2PasswordHasher

SENHA = "senha-exemplo-12345"


def test_hash_nao_e_a_senha_e_muda_a_cada_chamada():
    hasher = Argon2PasswordHasher()
    primeiro, segundo = hasher.hash(SENHA), hasher.hash(SENHA)
    assert SENHA not in primeiro
    assert primeiro != segundo
    assert primeiro.startswith("$argon2id$")


def test_verifica_a_senha_certa_e_recusa_a_errada():
    hasher = Argon2PasswordHasher()
    registrado = hasher.hash(SENHA)
    assert hasher.verify(registrado, SENHA) is True
    assert hasher.verify(registrado, "outra-senha-exemplo") is False


def test_hash_corrompido_e_recusado_sem_erro():
    assert Argon2PasswordHasher().verify("isto-nao-e-um-hash", SENHA) is False


def test_hash_com_parametros_mais_fracos_precisa_ser_regravado():
    fraco = Argon2(time_cost=1, memory_cost=8, parallelism=1).hash(SENHA)
    hasher = Argon2PasswordHasher()
    assert hasher.needs_rehash(fraco) is True
    assert hasher.needs_rehash(hasher.hash(SENHA)) is False


def test_usuario_inexistente_gasta_uma_verificacao_e_nao_levanta_erro():
    assert Argon2PasswordHasher().verify_unknown_user(SENHA) is None
