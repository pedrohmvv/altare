from typing import NamedTuple


class Message(NamedTuple):
    title: str
    detail: str


# Único lugar com os textos dos erros (altare-backend-api); código novo ganha a sua linha aqui.
MESSAGES: dict[str, Message] = {
    "not_found": Message(
        "Não encontrado",
        "Não encontramos este registro. Ele pode ter sido removido.",
    ),
    "forbidden": Message(
        "Acesso negado",
        "Esta ação não está disponível para o seu perfil.",
    ),
    "unauthenticated": Message(
        "Sessão necessária",
        "Entre com o seu usuário para continuar.",
    ),
    "version_conflict": Message(
        "Conflito de versão",
        "Este registro foi alterado por outra pessoa. Recarregue e tente de novo.",
    ),
    "validation_error": Message(
        "Dados inválidos",
        "Alguns campos precisam de ajuste. Confira as mensagens de cada campo.",
    ),
    "method_not_allowed": Message(
        "Método não permitido",
        "Esta rota não aceita este tipo de requisição.",
    ),
    "internal_error": Message(
        "Erro interno",
        "Algo deu errado do nosso lado. Tente de novo em instantes.",
    ),
}

_GENERIC = Message(
    "Não foi possível concluir",
    "Não foi possível concluir esta ação. Tente de novo em instantes.",
)


def message_for(code: str) -> Message:
    return MESSAGES.get(code, _GENERIC)
