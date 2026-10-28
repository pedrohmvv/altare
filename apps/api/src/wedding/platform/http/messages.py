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
    "csrf_missing": Message(
        "Pedido recusado",
        "Não foi possível confirmar este pedido. Recarregue a página e tente de novo.",
    ),
    "invalid_credentials": Message(
        "Usuário ou senha inválidos",
        "Confira o usuário e a senha e tente de novo.",
    ),
    "too_many_attempts": Message(
        "Muitas tentativas",
        "Houve muitas tentativas de entrada. Aguarde alguns minutos e tente de novo.",
    ),
    "invalid_username": Message(
        "Usuário inválido",
        "Use de 3 a 32 caracteres: letras minúsculas, números, ponto, hífen ou sublinhado.",
    ),
    "weak_password": Message(
        "Senha fraca",
        "Use uma senha com 12 a 128 caracteres.",
    ),
    "duplicate_username": Message(
        "Usuário já existe",
        "Já existe um usuário com este nome. Escolha outro.",
    ),
    "profile_taken": Message(
        "Perfil já em uso",
        "Já existe um usuário para este perfil.",
    ),
    "invalid_profile": Message(
        "Perfil inválido",
        "Escolha Noivo ou Noiva.",
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
