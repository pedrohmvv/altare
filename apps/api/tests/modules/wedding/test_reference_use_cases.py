from uuid import UUID, uuid4

import pytest
from tests.modules.wedding.conftest import NOIVA, NOIVO

from wedding.modules.wedding.application.commands.add_image_reference import (
    AddImageReferenceCommand,
)
from wedding.modules.wedding.application.commands.add_link_reference import AddLinkReferenceCommand
from wedding.modules.wedding.application.commands.remove_reference import RemoveReferenceCommand
from wedding.modules.wedding.application.scope_dto import ReferenceDto
from wedding.modules.wedding.domain.errors import (
    InvalidReferenceUrl,
    InvalidScopeValue,
    ReferenceFileNotImage,
)
from wedding.modules.wedding.domain.reference import ReferenceKind
from wedding.shared_kernel.errors import Forbidden, NotFound
from wedding.shared_kernel.profile import ProfileKind

IMAGEM = UUID(int=7001)
PDF = UUID(int=7002)


@pytest.fixture
def categoria(world) -> UUID:
    _, category_id = world.seed_catalog()
    world.files[IMAGEM] = True
    world.files[PDF] = False
    return category_id


def adicionar_link(world, categoria, url="https://exemplo.com/mesa", ator=NOIVO, **extra):
    return world.reference_use_cases().add_link_reference.execute(
        AddLinkReferenceCommand(categoria, url, extra.get("title"), extra.get("comment")), ator
    )


def lista(world, categoria, ator=NOIVO) -> list[ReferenceDto]:
    return world.reference_use_cases().list_references.execute(categoria, ator)


def test_link_adicionado_aparece_com_dominio_autor_e_titulo(world, categoria):  # F-PLN-06
    refs = adicionar_link(world, categoria, "HTTPS://www.Exemplo.com/mesa", title=" Mesa ")
    (ref,) = refs
    assert (ref.kind, ref.url, ref.domain, ref.title) == (
        ReferenceKind.LINK,
        "https://www.exemplo.com/mesa",
        "exemplo.com",
        "Mesa",
    )
    assert (ref.profile, ref.file_id, ref.can_remove) == (ProfileKind.NOIVO, None, True)


def test_endereco_invalido_e_recusado_e_nada_e_guardado(world, categoria):
    with pytest.raises(InvalidReferenceUrl):
        adicionar_link(world, categoria, "javascript:alert(1)")
    assert lista(world, categoria) == []


def test_comentario_longo_e_recusado(world, categoria):
    with pytest.raises(InvalidScopeValue):
        adicionar_link(world, categoria, comment="x" * 501)


def test_imagem_de_arquivo_enviado_vale_e_pdf_e_arquivo_inexistente_nao(world, categoria):
    uc = world.reference_use_cases()
    refs = uc.add_image_reference.execute(
        AddImageReferenceCommand(categoria, IMAGEM, "Salão", None), NOIVA
    )
    assert (refs[0].kind, refs[0].file_id, refs[0].url, refs[0].profile) == (
        ReferenceKind.IMAGE,
        IMAGEM,
        None,
        ProfileKind.NOIVA,
    )
    with pytest.raises(ReferenceFileNotImage):
        uc.add_image_reference.execute(AddImageReferenceCommand(categoria, PDF, None, None), NOIVA)
    with pytest.raises(NotFound):
        uc.add_image_reference.execute(
            AddImageReferenceCommand(categoria, uuid4(), None, None), NOIVA
        )
    assert len(lista(world, categoria)) == 1


def test_categoria_inexistente_ou_excluida_nao_aceita_referencia(world, categoria):
    with pytest.raises(NotFound):
        adicionar_link(world, uuid4())
    world.scope_store.categories[categoria].deleted_at = world.clock.now()
    with pytest.raises(NotFound):
        adicionar_link(world, categoria)


def test_sem_limite_de_referencias_e_a_mais_nova_vem_primeiro(world, categoria, clock):
    for numero in range(30):
        clock.advance(minutes=1)
        adicionar_link(world, categoria, f"https://exemplo.com/{numero}")
    refs = lista(world, categoria)
    assert len(refs) == 30
    assert refs[0].url == "https://exemplo.com/29"
    assert refs[-1].url == "https://exemplo.com/0"


def test_so_o_autor_pode_remover_e_o_outro_so_ve(world, categoria):  # F-PLN-06, regra 2
    (ref,) = adicionar_link(world, categoria, ator=NOIVO)
    (visto,) = lista(world, categoria, ator=NOIVA)
    assert visto.can_remove is False
    with pytest.raises(Forbidden):
        world.reference_use_cases().remove_reference.execute(
            RemoveReferenceCommand(categoria, ref.id), NOIVA
        )
    assert len(lista(world, categoria)) == 1


def test_o_autor_remove_a_sua_e_ela_sai_da_lista_mas_fica_guardada(world, categoria):
    (ref,) = adicionar_link(world, categoria, ator=NOIVO)
    restantes = world.reference_use_cases().remove_reference.execute(
        RemoveReferenceCommand(categoria, ref.id), NOIVO
    )
    assert restantes == []
    guardada = world.reference_store[ref.id]
    assert guardada.deleted_at is not None
    assert guardada.deleted_by == NOIVO.user_id


def test_remover_referencia_inexistente_ou_de_outra_categoria_e_nao_encontrado(world, categoria):
    (ref,) = adicionar_link(world, categoria)
    uc = world.reference_use_cases()
    with pytest.raises(NotFound):
        uc.remove_reference.execute(RemoveReferenceCommand(categoria, uuid4()), NOIVO)
    with pytest.raises(NotFound):
        uc.remove_reference.execute(RemoveReferenceCommand(uuid4(), ref.id), NOIVO)
    uc.remove_reference.execute(RemoveReferenceCommand(categoria, ref.id), NOIVO)
    with pytest.raises(NotFound):
        uc.remove_reference.execute(RemoveReferenceCommand(categoria, ref.id), NOIVO)


def test_listar_categoria_inexistente_e_nao_encontrado(world):
    with pytest.raises(NotFound):
        world.reference_use_cases().list_references.execute(uuid4(), NOIVO)
