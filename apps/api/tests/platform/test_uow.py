from uuid import uuid4

import pytest
from sqlalchemy import func, select

from wedding.platform.db.uow import SqlAlchemyUnitOfWork
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.profile import ProfileKind


def _total(banco) -> int:
    with banco.engine.connect() as conn:
        return conn.execute(select(func.count()).select_from(banco.tabela)).scalar_one()


def test_commit_persiste_a_linha(banco, clock):
    uow = SqlAlchemyUnitOfWork(banco.factory, clock)
    with uow:
        uow.session.add(banco.Coisa(id=uuid4(), nome="Exemplo"))
        uow.commit()
    assert _total(banco) == 1


def test_sair_sem_commit_descarta_o_que_foi_escrito(banco, clock):
    uow = SqlAlchemyUnitOfWork(banco.factory, clock)
    with uow:
        uow.session.add(banco.Coisa(id=uuid4(), nome="Exemplo"))
        uow.session.flush()
    assert _total(banco) == 0


def _gravar_e_falhar(banco, uow) -> None:
    with uow:
        uow.session.add(banco.Coisa(id=uuid4(), nome="Exemplo"))
        uow.session.flush()
        raise RuntimeError("falhou")


def test_excecao_dentro_do_bloco_desfaz_a_transacao(banco, clock):
    with pytest.raises(RuntimeError, match="falhou"):
        _gravar_e_falhar(banco, SqlAlchemyUnitOfWork(banco.factory, clock))
    assert _total(banco) == 0


def test_rollback_explicito_desfaz_o_que_foi_escrito(banco, clock):
    uow = SqlAlchemyUnitOfWork(banco.factory, clock)
    with uow:
        uow.session.add(banco.Coisa(id=uuid4(), nome="Exemplo"))
        uow.session.flush()
        uow.rollback()
        uow.commit()
    assert _total(banco) == 0


def test_cada_bloco_abre_uma_sessao_nova(banco, clock):
    uow = SqlAlchemyUnitOfWork(banco.factory, clock)
    with uow:
        primeira = uow.session
    with uow:
        assert uow.session is not primeira


def test_usar_a_sessao_fora_do_bloco_e_um_erro(banco, clock):
    uow = SqlAlchemyUnitOfWork(banco.factory, clock)
    with pytest.raises(RuntimeError, match="fora de um bloco"):
        _ = uow.session


def test_duas_transacoes_na_mesma_linha_dao_conflito_de_versao(banco, clock):
    ident = uuid4()
    with SqlAlchemyUnitOfWork(banco.factory, clock) as criar:
        criar.session.add(banco.Coisa(id=ident, nome="Original"))
        criar.commit()

    primeira = SqlAlchemyUnitOfWork(banco.factory, clock)
    segunda = SqlAlchemyUnitOfWork(banco.factory, clock)
    with primeira, segunda:
        primeira.session.get_one(banco.Coisa, ident).nome = "Da primeira"
        segunda.session.get_one(banco.Coisa, ident).nome = "Da segunda"
        primeira.commit()
        with pytest.raises(VersionConflict) as erro:
            segunda.commit()
    assert erro.value.code == "version_conflict"
    with banco.engine.connect() as conn:
        assert conn.execute(select(banco.tabela.c.nome)).scalar_one() == "Da primeira"


def test_o_ator_pode_ser_definido_depois_de_abrir(banco, clock):
    ator = Actor(user_id=uuid4(), profile=ProfileKind.NOIVA)
    uow = SqlAlchemyUnitOfWork(banco.factory, clock)
    with uow:
        uow.act_as(ator)
        uow.session.add(banco.Coisa(id=uuid4(), nome="Exemplo"))
        uow.commit()
    with banco.engine.connect() as conn:
        assert conn.execute(select(banco.tabela.c.created_by)).scalar_one() == ator.user_id
