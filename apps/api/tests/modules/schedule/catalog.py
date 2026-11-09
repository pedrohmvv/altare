"""O catálogo inicial do cronograma (F-CRN-02), transcrito à mão de `cronograma.md`.

É a prova independente da migration `0010`, que traz a sua própria cópia, e o cenário dos testes do
módulo. Cada marco: (código, fase a partir de zero, título, categoria, depende de, janela: início
antes, fim antes, unidade). A categoria é o nome no catálogo do Mapa (0005), que no C11 é "Música
(DJ, banda)" e não "Música".
"""

import uuid

FASES = [
    "Marco Zero",
    "Contrato Âncora",
    "Fornecedores Essenciais",
    "Identidade, Complementares e Convidados",
    "Reta Final",
]
MARCOS = [
    ("C01", 0, "Classificar o Mapa de Escopo", None, (), None),
    ("C02", 0, "Montar a lista preliminar de convidados", None, (), None),
    ("C03", 0, "Definir o teto macro e simular orçamentos", None, ("C01", "C02"), None),
    ("C04", 0, "Escolher o caminho macro (formato e região)", None, ("C03",), None),
    ("C05", 1, "Definir a data (ou janela de datas)", None, ("C04",), None),
    ("C06", 1, "Fechar o Espaço", "Espaço", ("C05",), (14, 10, "meses")),
    ("C07", 2, "Fechar o Buffet", "Buffet", ("C06",), (12, 8, "meses")),
    ("C08", 2, "Fechar a Fotografia", "Fotografia", ("C06",), (12, 8, "meses")),
    ("C09", 2, "Fechar o Vídeo", "Vídeo", ("C06",), (12, 8, "meses")),
    ("C10", 2, "Fechar o Cerimonial do dia", "Cerimonial do dia", ("C06",), (10, 7, "meses")),
    ("C11", 2, "Fechar a Música", "Música (DJ, banda)", ("C06",), (10, 6, "meses")),
    ("C12", 2, "Organizar a cerimônia civil", "Cerimônia civil", ("C05",), (6, 3, "meses")),
    (
        "C13",
        2,
        "Organizar a cerimônia religiosa ou simbólica",
        "Cerimônia religiosa ou simbólica",
        ("C05",),
        (12, 6, "meses"),
    ),
    ("C14", 3, "Fechar Decoração e flores", "Decoração e flores", ("C06",), (9, 5, "meses")),
    ("C15", 3, "Fechar Iluminação e som", "Iluminação e som", ("C06",), (8, 5, "meses")),
    ("C16", 3, "Fechar Bebidas e bar", "Bebidas e bar", ("C07",), (8, 5, "meses")),
    ("C17", 3, "Fechar Bolo e doces", "Bolo e doces", ("C07",), (6, 3, "meses")),
    ("C18", 3, "Definir os trajes", "Trajes", ("C05",), (10, 5, "meses")),
    ("C19", 3, "Contratar a beleza", "Beleza (noivos)", ("C18",), (6, 3, "meses")),
    (
        "C20",
        3,
        "Convites e papelaria",
        "Convites e papelaria",
        ("C02", "C06"),
        (7, 4, "meses"),
    ),
    ("C21", 3, "Lembrancinhas", "Lembrancinhas", ("C06",), (5, 3, "meses")),
    ("C22", 3, "Montar o enxoval e a lista de presentes", None, ("C05",), (6, 3, "meses")),
    ("C23", 3, "Planejar a lua de mel", "Lua de mel", ("C05",), (8, 3, "meses")),
    ("C24", 3, "Reservar a noite de núpcias", "Noite de núpcias", ("C06",), (4, 2, "meses")),
    ("C25", 4, "Enviar os convites", None, ("C20",), (4, 2, "meses")),
    ("C26", 4, "Confirmar as presenças", None, ("C25",), (2, 1, "meses")),
    ("C27", 4, "Degustações e provas finais", None, ("C07", "C18"), (2, 1, "meses")),
    ("C28", 4, "Quitar os contratos", None, ("C26",), (4, 1, "semanas")),
    ("C29", 4, "Entregar o Dossiê ao cerimonialista", None, ("C10", "C26"), (4, 2, "semanas")),
]
SEED_NS = uuid.UUID("5c0e7a6e-2b0d-5f61-9a39-6c1d7e0f5a01")
SEED_NS = uuid.UUID("5c0e7a6e-2b0d-5f61-9a39-6c1d7e0f5a01")


def seed_id(chave: str) -> uuid.UUID:
    return uuid.uuid5(SEED_NS, chave)


def marco_id(codigo: str) -> uuid.UUID:
    return seed_id(f"marco:{codigo}")


def fase_id(numero: int) -> uuid.UUID:
    """A fase pelo número do catálogo, de 1 a 5."""
    return seed_id(f"fase:{numero}")


def categoria_id(nome: str) -> uuid.UUID:
    return seed_id(f"categoria:{nome}")
