import hashlib
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import insert, inspect, select, update
from sqlalchemy.exc import IntegrityError

from wedding.modules.files.application.commands.upload_file import UploadFile, UploadFileCommand
from wedding.modules.files.application.queries.get_file import GetFile
from wedding.modules.files.domain.entities import FileAsset
from wedding.modules.files.domain.value_objects import FileKind
from wedding.modules.files.infrastructure.mapping import start_mappers
from wedding.modules.files.infrastructure.tables import file_assets
from wedding.modules.files.infrastructure.uow import SqlFilesUnitOfWork
from wedding.platform.bootstrap.tables import load_tables
from wedding.platform.db.engine import create_db_engine, create_session_factory
from wedding.platform.db.metadata import metadata
from wedding.platform.storage.local import LocalFileStorage
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.ids import UuidGenerator
from wedding.shared_kernel.profile import ProfileKind

AGORA = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
ATOR = Actor(user_id=uuid4(), profile=ProfileKind.NOIVO)
PDF = b"%PDF-1.7\n%conteudo de exemplo"


@pytest.fixture
def banco(tmp_path, clock):
    load_tables()
    start_mappers()
    engine = create_db_engine(f"sqlite:///{tmp_path / 'arquivos.db'}")
    metadata.create_all(engine)
    factory = create_session_factory(engine)
    yield SimpleNamespace(
        engine=engine,
        clock=clock,
        storage=LocalFileStorage(tmp_path / "arquivos"),
        uow=lambda ator=ATOR: SqlFilesUnitOfWork(factory, clock, ator),
        raiz=tmp_path / "arquivos",
    )
    engine.dispose()


def _arquivo(nome="proposta.pdf", sha="a" * 64) -> FileAsset:
    return FileAsset(id=uuid4(), original_name=nome, kind=FileKind.PDF, size_bytes=10, sha256=sha)


def _gravar(banco, arquivo: FileAsset, ator=ATOR) -> None:
    with banco.uow(ator) as uow:
        uow.session.add(arquivo)
        uow.commit()


def test_arquivo_gravado_volta_pelo_id_com_o_tipo_como_enum(banco):
    arquivo = _arquivo()
    _gravar(banco, arquivo)
    with banco.uow() as uow:
        lido = uow.files.get(arquivo.id)
        assert lido is not None
        assert (lido.original_name, lido.kind, lido.size_bytes, lido.sha256) == (
            "proposta.pdf",
            FileKind.PDF,
            10,
            "a" * 64,
        )
        assert uow.files.get(uuid4()) is None


def test_o_registro_leva_o_historico_com_o_autor_da_sessao(banco):
    _gravar(banco, _arquivo())
    with banco.engine.connect() as conn:
        linha = conn.execute(select(file_assets)).one()
    assert (linha.created_at, linha.created_by, linha.version) == (AGORA, ATOR.user_id, 1)
    assert linha.content_type == "application/pdf"


def test_o_mesmo_conteudo_pode_ter_varios_registros(banco):
    _gravar(banco, _arquivo("proposta.pdf", sha="b" * 64))
    _gravar(banco, _arquivo("proposta-final.pdf", sha="b" * 64))
    with banco.engine.connect() as conn:
        assert len(conn.execute(select(file_assets)).all()) == 2


def test_arquivo_excluido_some_da_consulta(banco):
    arquivo = _arquivo()
    _gravar(banco, arquivo)
    with banco.engine.begin() as conn:
        conn.execute(update(file_assets).values(deleted_at=AGORA, deleted_by=ATOR.user_id))
    with banco.uow() as uow:
        assert uow.files.get(arquivo.id) is None


@pytest.mark.parametrize(
    "valores",
    [{"content_type": "text/html"}, {"size_bytes": 0}, {"size_bytes": -5}],
)
def test_o_banco_barra_tipo_desconhecido_e_tamanho_que_nao_e_positivo(banco, valores):
    base = {
        "id": uuid4(),
        "created_at": AGORA,
        "updated_at": AGORA,
        "version": 1,
        "original_name": "x.pdf",
        "content_type": "application/pdf",
        "size_bytes": 10,
        "sha256": "a" * 64,
    }
    with pytest.raises(IntegrityError), banco.engine.begin() as conn:
        conn.execute(insert(file_assets).values({**base, **valores}))


def test_ha_um_indice_no_hash_mas_ele_nao_e_unico(banco):
    indices = {i["name"]: i for i in inspect(banco.engine).get_indexes("file_assets")}
    assert indices["ix_file_assets_sha256"]["unique"] == 0


def test_fluxo_completo_envia_para_o_disco_e_le_de_volta(banco):
    ids = UuidGenerator()
    enviado = UploadFile(banco.uow, banco.storage, ids).execute(
        UploadFileCommand("Proposta Exemplo.pdf", PDF), ATOR
    )
    lido = GetFile(banco.uow, banco.storage).execute(enviado.id, ATOR)
    assert b"".join(lido.chunks) == PDF
    assert lido.file.name == "Proposta Exemplo.pdf"
    sha = hashlib.sha256(PDF).hexdigest()
    arquivos = [p for p in banco.raiz.rglob("*") if p.is_file()]
    assert [p.name for p in arquivos] == [sha]


def test_enviar_o_mesmo_arquivo_duas_vezes_guarda_um_so_conteudo(banco):
    ids = UuidGenerator()
    upload = UploadFile(banco.uow, banco.storage, ids)
    upload.execute(UploadFileCommand("a.pdf", PDF), ATOR)
    upload.execute(UploadFileCommand("b.pdf", PDF), ATOR)
    assert len([p for p in banco.raiz.rglob("*") if p.is_file()]) == 1
    with banco.engine.connect() as conn:
        assert len(conn.execute(select(file_assets)).all()) == 2
