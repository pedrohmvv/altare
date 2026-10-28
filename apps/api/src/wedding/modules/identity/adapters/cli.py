from collections.abc import Iterator
from contextlib import contextmanager
from enum import StrEnum
from typing import Annotated

import typer
from sqlalchemy.exc import OperationalError

from wedding.modules.identity.application.commands.create_user import CreateUserCommand
from wedding.modules.identity.application.commands.set_password import SetPasswordCommand
from wedding.modules.identity.application.use_cases import IdentityProvider
from wedding.platform.http.messages import message_for
from wedding.shared_kernel.errors import DomainError
from wedding.shared_kernel.profile import ProfileKind


class LoginProfile(StrEnum):
    """Só os perfis que têm login: `Ambos` não existe aqui."""

    NOIVO = "Noivo"
    NOIVA = "Noiva"


@contextmanager
def _exit_with_message_on_error() -> Iterator[None]:
    try:
        yield
    except DomainError as error:
        typer.echo(f"Erro: {message_for(error.code).detail}", err=True)
        raise typer.Exit(1) from error
    except OperationalError as error:
        if "no such table" not in str(error.orig):
            raise
        typer.echo(
            "Erro: o banco ainda não foi migrado. Rode `make migrate` e tente de novo.", err=True
        )
        raise typer.Exit(1) from error


def build_cli(provide: IdentityProvider) -> typer.Typer:
    """Os comandos de usuário. Não há cadastro público: é por aqui que os dois logins nascem."""
    cli = typer.Typer()

    @cli.command("create-user")
    def create_user(
        profile: Annotated[LoginProfile, typer.Option("--profile", help="Noivo ou Noiva.")],
        username: Annotated[str, typer.Option("--username", help="Usuário de login.")],
    ) -> None:
        """Cria um dos dois logins do casal. A senha é pedida sem aparecer na tela."""
        password = typer.prompt("Senha", hide_input=True, confirmation_prompt=True)
        with _exit_with_message_on_error():
            user = provide().create_user.execute(
                CreateUserCommand(username, ProfileKind(profile.value), password)
            )
        typer.echo(f"Usuário {user.username} criado com o perfil {user.profile.value}.")

    @cli.command("set-password")
    def set_password(
        username: Annotated[str, typer.Option("--username", help="Usuário de login.")],
    ) -> None:
        """Troca a senha e encerra as sessões abertas do usuário."""
        password = typer.prompt("Nova senha", hide_input=True, confirmation_prompt=True)
        with _exit_with_message_on_error():
            provide().set_password.execute(SetPasswordCommand(username, password))
        typer.echo(f"Senha de {username} trocada. As sessões abertas foram encerradas.")

    return cli
