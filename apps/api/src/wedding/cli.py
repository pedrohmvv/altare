import json
from pathlib import Path
from typing import Annotated

import typer

from wedding.modules.identity.adapters.cli import build_cli as build_identity_cli
from wedding.platform.bootstrap.app import build_app
from wedding.platform.bootstrap.identity import IdentityContainer
from wedding.platform.config import Settings


def create_cli(settings: Settings | None = None) -> typer.Typer:
    cli = typer.Typer(no_args_is_help=True)

    @cli.callback()
    def _root() -> None:
        """Operações administrativas do Altare."""

    @cli.command("export-openapi")
    def export_openapi(
        output: Annotated[Path, typer.Option("--output", "-o", help="Arquivo de saída.")] = Path(
            "openapi.json"
        ),
    ) -> None:
        """Grava o contrato OpenAPI, de onde saem os tipos do frontend."""
        contract = build_app().openapi()
        output.write_text(
            json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    identity = IdentityContainer(settings or Settings())
    cli.add_typer(build_identity_cli(identity.use_cases))
    return cli


app = create_cli()
