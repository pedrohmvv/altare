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
    "unsupported_file_type": Message(
        "Tipo de arquivo não aceito",
        "Envie um PDF ou uma imagem JPG, PNG ou WebP.",
    ),
    "file_too_large": Message(
        "Arquivo grande demais",
        "O arquivo passa de 20 MB. Envie uma versão menor.",
    ),
    "empty_file": Message(
        "Arquivo vazio",
        "O arquivo está vazio. Escolha outro e tente de novo.",
    ),
    "baseline_value_required": Message(
        "Falta o valor",
        "Preencha o valor antes de marcar como Definido, ou deixe o campo Em definição.",
    ),
    "invalid_baseline_value": Message(
        "Valor não aceito",
        "Confira o valor deste campo: o formato ou o limite informado não é aceito.",
    ),
    "invalid_scope_value": Message(
        "Valor não aceito",
        (
            "Confira o texto ou o valor: o nome vai até 60 caracteres, "
            "e a estimativa precisa ser maior que zero."
        ),
    ),
    "discard_reason_required": Message(
        "Falta o motivo",
        "Escreva por que esta frente fica de fora antes de salvar.",
    ),
    "catalog_item_not_deletable": Message(
        "Não dá para excluir",
        "Itens que já vieram com o Altare não são excluídos. Oculte para tirar das telas.",
    ),
    "group_not_empty": Message(
        "O grupo ainda tem categorias",
        "Mova ou exclua as categorias do grupo antes de excluí-lo.",
    ),
    "duplicate_scope_name": Message(
        "Nome já usado",
        "Já existe uma frente ou um grupo com este nome. Escolha outro.",
    ),
    "invalid_reference_url": Message(
        "Endereço não aceito",
        "Cole um endereço completo, começando com http:// ou https://.",
    ),
    "reference_file_not_image": Message(
        "Só imagens",
        ("Referências aceitam imagens JPG, PNG ou WebP. Um PDF não entra como referência."),
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
