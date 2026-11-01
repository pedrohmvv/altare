from fastapi import Response


def private_no_store(response: Response) -> None:
    """Dependência de router: a resposta tem dado pessoal de terceiros e não pode ser guardada por
    cache nenhum (altare-seguranca-privacidade)."""
    response.headers["Cache-Control"] = "private, no-store"
