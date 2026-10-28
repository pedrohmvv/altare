from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select

from wedding.platform.db.uow import SqlAlchemyUnitOfWork
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.profile import ProfileKind


def _linha(banco):
    with banco.engine.connect() as conn:
        return conn.execute(select(banco.tabela)).one()


def _criar(banco, clock, ator=None):
    ident = uuid4()
    with SqlAlchemyUnitOfWork(banco.factory, clock, ator) as uow:
        uow.session.add(banco.Coisa(id=ident, nome="Exemplo"))
        uow.commit()
    return ident


def test_criacao_carimba_instantes_em_utc_e_versao_inicial(banco, clock):
    _criar(banco, clock)
    linha = _linha(banco)
    agora = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
    assert (linha.created_at, linha.updated_at) == (agora, agora)
    assert linha.created_at.tzinfo is UTC
    assert linha.version == 1


def test_criacao_registra_o_ator_da_sessao(banco, clock):
    ator = Actor(user_id=uuid4(), profile=ProfileKind.NOIVO)
    _criar(banco, clock, ator)
    linha = _linha(banco)
    assert (linha.created_by, linha.updated_by) == (ator.user_id, ator.user_id)


def test_sem_ator_a_autoria_fica_nula(banco, clock):
    _criar(banco, clock)
    linha = _linha(banco)
    assert (linha.created_by, linha.updated_by) == (None, None)


def test_exclusao_logica_comeca_vazia(banco, clock):
    _criar(banco, clock)
    linha = _linha(banco)
    assert (linha.deleted_at, linha.deleted_by) == (None, None)


def test_alteracao_atualiza_instante_autor_e_versao_sem_mexer_na_criacao(banco, clock):
    criador = Actor(user_id=uuid4(), profile=ProfileKind.NOIVO)
    editor = Actor(user_id=uuid4(), profile=ProfileKind.NOIVA)
    ident = _criar(banco, clock, criador)
    clock.advance(hours=2)
    with SqlAlchemyUnitOfWork(banco.factory, clock, editor) as uow:
        uow.session.get_one(banco.Coisa, ident).nome = "Alterado"
        uow.commit()
    linha = _linha(banco)
    assert linha.created_at == datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
    assert linha.updated_at == datetime(2026, 10, 27, 14, 0, tzinfo=UTC)
    assert (linha.created_by, linha.updated_by) == (criador.user_id, editor.user_id)
    assert linha.version == 2


def test_gravar_o_mesmo_valor_nao_conta_como_alteracao(banco, clock):
    ident = _criar(banco, clock)
    clock.advance(hours=2)
    with SqlAlchemyUnitOfWork(banco.factory, clock) as uow:
        coisa = uow.session.get_one(banco.Coisa, ident)
        coisa.nome = coisa.nome
        uow.commit()
    linha = _linha(banco)
    assert linha.updated_at == datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
    assert linha.version == 1
