import json
from pathlib import Path
from typing import Annotated

import typer

from wedding.platform.bootstrap.app import build_app

app = typer.Typer(no_args_is_help=True)


@app.callback()
def _root() -> None:
    """Operações administrativas do Altare."""


@app.command("export-openapi")
def export_openapi(
    output: Annotated[Path, typer.Option("--output", "-o", help="Arquivo de saída.")] = Path(
        "openapi.json"
    ),
) -> None:
    """Grava o contrato OpenAPI, de onde saem os tipos do frontend."""
    contract = build_app().openapi()
    output.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
