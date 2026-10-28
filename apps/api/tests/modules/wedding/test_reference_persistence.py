from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import insert, select, text
from sqlalchemy.exc import IntegrityError

from wedding.modules.wedding.application.commands.add_image_reference import (
    AddImageReference,
    AddImageReferenceCommand,
)
from wedding.modules.wedding.application.commands.add_link_reference import (
    AddLinkReference,
    AddLinkReferenceCommand,
)
from wedding.modules.wedding.application.commands.remove_reference import (
    RemoveReference,
    RemoveReferenceCommand,
)
from wedding.modules.wedding.application.ports import StoredFile
from wedding.modules.wedding.application.queries.get_scope_map import GetScopeMap
from wedding.modules.wedding.application.queries.list_references import ListReferences
from wedding.modules.wedding.infrastructure.mapping import start_mappers
from wedding.modules.wedding.infrastructure.reference_tables import scope_references
from wedding.modules.wedding.infrastructure.uow import SqlWeddingUnitOfWork
from wedding.platform.bootstrap.tables import load_tables
from wedding.platform.db.engine import create_db_engine, create_session_factory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import Forbidden
from wedding.shared_kernel.ids import UuidGenerator
from wedding.shared_kernel.profile import ProfileKind

API_DIR = Path(__file__).parents[3]
NOIVO = Actor(user_id=uuid4(), profile=ProfileKind.NOIVO)
NOIVA = Actor(user_id=uuid4(), profile=ProfileKind.NOIVA)
AGORA = datetime(2026, 10, 28, tzinfo=UTC)


class _Catalogo:
    def __init__(self) -> None:
        self.imagens: set[UUID] = set()

    def find(self, file_id: UUID, actor: Actor) -> StoredFile | None:
        return StoredFile(file_id, True) if file_id in self.imagens else None


@pytest.fixture
def banco(tmp_path, clock):
    load_tables()
    start_mappers()
    url = f"sqlite:///{tmp_path / 'ref.db'}"
    config = Config(str(API_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    engine = create_db_engine(url)
    factory = create_session_factory(engine)

    def uow(ator: Actor = NOIVO) -> SqlWeddingUnitOfWork:
        return SqlWeddingUnitOfWork(factory, clock, ator)

    ids, catalogo = UuidGenerator(), _Catalogo()
    with engine.connect() as conn:
        categoria = conn.execute(text("SELECT id FROM scope_categories LIMIT 1")).scalar_one()
    yield SimpleNamespace(
        engine=engine,
        clock=clock,
        uow=uow,
        categoria=UUID(str(categoria)),
        catalogo=catalogo,
        listar=ListReferences(uow, clock),
        link=AddLinkReference(uow, ids, clock),
        imagem=AddImageReference(uow, ids, clock, catalogo),
        remover=RemoveReference(uow, clock),
        mapa=GetScopeMap(uow),
    )
    engine.dispose()


def _arquivo(engine) -> UUID:
    """Um registro de `file_assets`, como o módulo de arquivos o deixa depois de um envio."""
    arquivo = uuid4()
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO file_assets (id, created_at, updated_at, version, original_name, "
                "content_type, size_bytes, sha256) VALUES (:id, '2026-10-28', '2026-10-28', 1, "
                "'foto.png', 'image/png', 10, :sha)"
            ),
            {"id": arquivo.hex, "sha": "a" * 64},
        )
    return arquivo


def test_link_e_imagem_voltam_pela_lista_do_mais_novo_ao_mais_antigo(banco, clock):
    imagem = _arquivo(banco.engine)
    banco.catalogo.imagens.add(imagem)
    banco.link.execute(
        AddLinkReferenceCommand(banco.categoria, "https://exemplo.com/a", None, None), NOIVO
    )
    clock.advance(minutes=5)
    banco.imagem.execute(
        AddImageReferenceCommand(banco.categoria, imagem, "Salão", "luz boa"), NOIVA
    )

    imagem_ref, link_ref = banco.listar.execute(banco.categoria, NOIVO)
    assert (imagem_ref.file_id, imagem_ref.title, imagem_ref.comment) == (
        imagem,
        "Salão",
        "luz boa",
    )
    assert (imagem_ref.profile, imagem_ref.can_remove) == (ProfileKind.NOIVA, False)
    assert (link_ref.url, link_ref.domain, link_ref.can_remove) == (
        "https://exemplo.com/a",
        "exemplo.com",
        True,
    )
    assert imagem_ref.added_at > link_ref.added_at


def test_remocao_e_logica_e_so_do_autor(banco):
    (ref,) = banco.link.execute(
        AddLinkReferenceCommand(banco.categoria, "https://exemplo.com", None, None), NOIVO
    )
    with pytest.raises(Forbidden):
        banco.remover.execute(RemoveReferenceCommand(banco.categoria, ref.id), NOIVA)
    assert len(banco.listar.execute(banco.categoria, NOIVO)) == 1

    banco.remover.execute(RemoveReferenceCommand(banco.categoria, ref.id), NOIVO)
    assert banco.listar.execute(banco.categoria, NOIVO) == []
    with banco.engine.connect() as conn:
        linha = conn.execute(
            select(scope_references.c.deleted_at, scope_references.c.deleted_by)
        ).one()
    assert linha.deleted_at is not None
    assert linha.deleted_by == NOIVO.user_id


def test_a_lista_so_traz_as_da_categoria(banco):
    with banco.engine.connect() as conn:
        outra = UUID(
            str(conn.execute(text("SELECT id FROM scope_categories LIMIT 1 OFFSET 1")).scalar_one())
        )
    banco.link.execute(
        AddLinkReferenceCommand(outra, "https://exemplo.com/outra", None, None), NOIVO
    )
    assert banco.listar.execute(banco.categoria, NOIVO) == []
    assert len(banco.listar.execute(outra, NOIVO)) == 1


def _inserir(conn, **valores):
    base = {
        "id": uuid4(),
        "created_at": AGORA,
        "updated_at": AGORA,
        "version": 1,
        "kind": "link",
        "profile": "Noivo",
        "url": "https://exemplo.com",
    }
    return conn.execute(insert(scope_references).values({**base, **valores}))


class TestRestricoesDoBanco:
    def test_linha_valida_entra(self, banco):
        with banco.engine.begin() as conn:
            _inserir(conn, category_id=banco.categoria)

    @pytest.mark.parametrize(
        "valores",
        [
            {"url": None},
            {"kind": "imagem", "url": None},
            {"kind": "imagem"},
            {"kind": "outro"},
            {"profile": "Ambos"},
        ],
    )
    def test_forma_invalida_e_barrada(self, banco, valores):
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            _inserir(conn, category_id=banco.categoria, **valores)

    def test_link_com_arquivo_junto_e_barrado(self, banco):
        arquivo = _arquivo(banco.engine)
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            _inserir(conn, category_id=banco.categoria, file_id=arquivo)

    def test_arquivo_inexistente_e_categoria_inexistente_sao_barrados_pela_chave_estrangeira(
        self, banco
    ):
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            _inserir(conn, category_id=banco.categoria, kind="imagem", url=None, file_id=uuid4())
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            _inserir(conn, category_id=uuid4())

    def test_nao_se_apaga_um_arquivo_que_e_referencia(self, banco):
        arquivo = _arquivo(banco.engine)
        with banco.engine.begin() as conn:
            _inserir(conn, category_id=banco.categoria, kind="imagem", url=None, file_id=arquivo)
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            conn.execute(text("DELETE FROM file_assets"))
