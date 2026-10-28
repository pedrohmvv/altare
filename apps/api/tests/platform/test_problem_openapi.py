from wedding.platform.http.app import create_app
from wedding.platform.http.problem import problem_responses


def _esquema():
    app = create_app()

    @app.post(
        "/api/v1/_teste/erros", operation_id="testar_erros", responses=problem_responses(401, 422)
    )
    def testar(corpo: dict[str, str]) -> None:
        return None

    return app.openapi()


def test_erros_declarados_usam_o_media_type_problem_json():
    respostas = _esquema()["paths"]["/api/v1/_teste/erros"]["post"]["responses"]
    for status in ("401", "422"):
        assert list(respostas[status]["content"]) == ["application/problem+json"]
        referencia = respostas[status]["content"]["application/problem+json"]["schema"]["$ref"]
        assert referencia == "#/components/schemas/ProblemDetails"


def test_declarar_o_422_dispensa_o_erro_de_validacao_padrao_do_fastapi():
    esquema = _esquema()
    assert "HTTPValidationError" not in esquema["components"]["schemas"]


def test_o_schema_do_problem_details_tem_os_campos_do_contrato():
    problema = _esquema()["components"]["schemas"]["ProblemDetails"]
    assert {"title", "status", "code", "detail"} <= set(problema["required"])
    assert "errors" in problema["properties"]


def test_a_resposta_de_sucesso_continua_em_json():
    respostas = _esquema()["paths"]["/api/v1/health"]["get"]["responses"]
    assert list(respostas["200"]["content"]) == ["application/json"]
