import json

from typer.testing import CliRunner

from wedding.cli import app
from wedding.platform.bootstrap.app import build_app

runner = CliRunner()


def test_export_openapi_grava_o_contrato_em_json(tmp_path):
    destino = tmp_path / "openapi.json"
    resultado = runner.invoke(app, ["export-openapi", "--output", str(destino)])
    assert resultado.exit_code == 0, resultado.output
    assert json.loads(destino.read_text(encoding="utf-8")) == build_app().openapi()


def test_export_openapi_termina_com_quebra_de_linha(tmp_path):
    destino = tmp_path / "openapi.json"
    runner.invoke(app, ["export-openapi", "--output", str(destino)])
    assert destino.read_text(encoding="utf-8").endswith("}\n")
