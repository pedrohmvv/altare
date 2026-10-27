import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from wedding.cli import create_cli
from wedding.modules.identity.adapters.cli import build_cli
from wedding.platform.bootstrap.app import build_app
from wedding.platform.config import Settings
from wedding.shared_kernel.profile import ProfileKind

runner = CliRunner()
SENHA = "senha-exemplo-12345"
CSRF = {"X-Altare-CSRF": "1"}
ENTRADA = f"{SENHA}\n{SENHA}\n"


def _cli(world):
    return build_cli(world.use_cases)


def _criar(world, *argumentos, entrada=ENTRADA):
    return runner.invoke(_cli(world), ["create-user", *argumentos], input=entrada)


def test_cria_o_usuario_pedindo_a_senha_escondida_e_confirmada(world):
    resultado = _criar(world, "--profile", "Noivo", "--username", "Exemplo.Noivo")
    assert resultado.exit_code == 0, resultado.output
    (usuario,) = world.store.users.values()
    assert (usuario.username, usuario.profile) == ("exemplo.noivo", ProfileKind.NOIVO)
    assert usuario.password_hash == world.hasher.hash(SENHA)
    assert "exemplo.noivo" in resultado.output
    assert SENHA not in resultado.output


def test_a_senha_nao_e_uma_opcao_da_linha_de_comando(world):
    resultado = _criar(world, "--profile", "Noivo", "--username", "x.yz", "--password", SENHA)
    assert resultado.exit_code == 2
    assert world.store.users == {}


def test_o_perfil_ambos_nao_existe_na_cli(world):
    resultado = _criar(world, "--profile", "Ambos", "--username", "exemplo.noivo")
    assert resultado.exit_code == 2
    assert world.store.users == {}


@pytest.mark.parametrize(
    ("entrada", "usuario", "mensagem"),
    [
        ("curta\ncurta\n", "exemplo.noivo", "Use uma senha com 12 a 128 caracteres."),
        (ENTRADA, "com espaço", "Use de 3 a 32 caracteres"),
    ],
)
def test_dado_invalido_sai_com_a_mensagem_em_portugues_e_codigo_1(
    world, entrada, usuario, mensagem
):
    resultado = _criar(world, "--profile", "Noivo", "--username", usuario, entrada=entrada)
    assert resultado.exit_code == 1
    assert mensagem in resultado.output
    assert world.store.users == {}


def test_usuario_repetido_e_perfil_repetido_sao_recusados(world):
    world.add_user("exemplo.noivo", ProfileKind.NOIVO)
    repetido = _criar(world, "--profile", "Noiva", "--username", "exemplo.noivo")
    perfil = _criar(world, "--profile", "Noivo", "--username", "outro.usuario")
    assert repetido.exit_code == perfil.exit_code == 1
    assert "Já existe um usuário com este nome" in repetido.output
    assert "Já existe um usuário para este perfil" in perfil.output


def test_trocar_a_senha_derruba_as_sessoes_do_usuario(world):
    usuario = world.add_user()
    world.add_session(usuario, token="aberta")
    nova = "outra-senha-exemplo-98765"
    resultado = runner.invoke(
        _cli(world), ["set-password", "--username", "exemplo.noivo"], input=f"{nova}\n{nova}\n"
    )
    assert resultado.exit_code == 0, resultado.output
    assert world.store.users[usuario.id].password_hash == world.hasher.hash(nova)
    assert world.store.sessions == {}


def test_trocar_a_senha_de_quem_nao_existe_e_um_erro(world):
    resultado = runner.invoke(_cli(world), ["set-password", "--username", "ninguem"], input=ENTRADA)
    assert resultado.exit_code == 1
    assert "Não encontramos" in resultado.output


def test_banco_sem_migracao_diz_o_que_fazer(tmp_path):
    cli = create_cli(Settings(database_url=f"sqlite:///{tmp_path / 'vazio.db'}"))
    resultado = runner.invoke(
        cli, ["create-user", "--profile", "Noivo", "--username", "exemplo.noivo"], input=ENTRADA
    )
    assert resultado.exit_code == 1
    assert "make migrate" in resultado.output


def test_a_cli_completa_cria_os_dois_usuarios_num_banco_migrado(api):
    cli = create_cli(api.settings)
    for perfil, usuario in (("Noivo", "exemplo.noivo"), ("Noiva", "exemplo.noiva")):
        resultado = runner.invoke(
            cli, ["create-user", "--profile", perfil, "--username", usuario], input=ENTRADA
        )
        assert resultado.exit_code == 0, resultado.output
    # a CLI grava com o Argon2 de verdade, então a API que confere a senha também o usa
    app = build_app(api.settings, clock=api.world.clock)
    cliente = TestClient(app, base_url="https://testserver", headers=CSRF)
    entrou = cliente.post(
        "/api/v1/auth/login", json={"username": "exemplo.noiva", "password": SENHA}
    )
    assert entrou.status_code == 200
    assert entrou.json()["profile"] == "Noiva"
