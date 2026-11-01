import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.exc import IntegrityError

from wedding.platform.db.engine import create_db_engine

# Valor que faria as vezes de um dado pessoal de convidado (altare-seguranca-privacidade).
SENTINELA = "Convidado Exemplo Sentinela"


def test_erro_de_banco_nao_traz_os_parametros_da_consulta(tmp_path):
    meta = MetaData()
    pessoas = Table(
        "pessoas",
        meta,
        Column("id", Integer, primary_key=True),
        Column("nome", String, nullable=False, unique=True),
    )
    engine = create_db_engine(f"sqlite:///{tmp_path / 'teste.db'}")
    meta.create_all(engine)
    with engine.begin() as conexao:
        conexao.execute(pessoas.insert().values(nome=SENTINELA))

    with pytest.raises(IntegrityError) as erro, engine.begin() as conexao:
        conexao.execute(pessoas.insert().values(nome=SENTINELA))

    assert SENTINELA not in str(erro.value)
    assert SENTINELA not in repr(erro.value)
