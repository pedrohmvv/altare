from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import insert, select, text
from sqlalchemy.exc import IntegrityError

from wedding.modules.guests.application.commands.add_companion import (
    AddCompanion,
    AddCompanionCommand,
)
from wedding.modules.guests.application.commands.add_guest import AddGuest, AddGuestCommand
from wedding.modules.guests.application.commands.change_guest_status import (
    ChangeGuestStatus,
    ChangeGuestStatusCommand,
)
from wedding.modules.guests.application.commands.create_household import (
    CreateHousehold,
    CreateHouseholdCommand,
)
from wedding.modules.guests.application.commands.delete_guest import (
    CompanionChoice,
    DeleteGuest,
    DeleteGuestCommand,
)
from wedding.modules.guests.application.commands.delete_household import (
    DeleteHousehold,
    DeleteHouseholdCommand,
)
from wedding.modules.guests.application.commands.move_guest import MoveGuest, MoveGuestCommand
from wedding.modules.guests.application.commands.restore_guest import (
    RestoreGuest,
    RestoreGuestCommand,
)
from wedding.modules.guests.application.commands.restore_household import (
    RestoreHousehold,
    RestoreHouseholdCommand,
)
from wedding.modules.guests.application.commands.update_guest import (
    UpdateGuest,
    UpdateGuestCommand,
)
from wedding.modules.guests.application.fields import GuestFields, HouseholdFields
from wedding.modules.guests.application.queries.get_guest_list import GetGuestList
from wedding.modules.guests.application.queries.list_guest_status_history import (
    ListGuestStatusHistory,
)
from wedding.modules.guests.domain.age import AgeLimits
from wedding.modules.guests.domain.entities import Guest, Household
from wedding.modules.guests.domain.errors import (
    CompanionAlreadyExists,
    DuplicateHouseholdName,
    LastGuestInHousehold,
)
from wedding.modules.guests.domain.headcount import Weights
from wedding.modules.guests.domain.values import AgeBand, GuestStatus, Probability, Side
from wedding.modules.guests.infrastructure.mapping import start_mappers
from wedding.modules.guests.infrastructure.tables import guest_households, guests
from wedding.modules.guests.infrastructure.uow import SqlGuestsUnitOfWork
from wedding.platform.bootstrap.tables import load_tables
from wedding.platform.db.engine import create_db_engine, create_session_factory
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import VersionConflict
from wedding.shared_kernel.ids import UuidGenerator
from wedding.shared_kernel.profile import ProfileKind

API_DIR = Path(__file__).parents[3]
NOIVO = Actor(user_id=uuid4(), profile=ProfileKind.NOIVO)
NOIVA = Actor(user_id=uuid4(), profile=ProfileKind.NOIVA)
SENTINELA = "Convidado Exemplo Sentinela"
AGORA = datetime(2026, 10, 28, tzinfo=UTC)


@pytest.fixture
def banco(tmp_path, clock):
    """O banco como a migration o deixa (vazio de convidados): é o que o app encontra."""
    load_tables()
    start_mappers()
    url = f"sqlite:///{tmp_path / 'convidados.db'}"
    config = Config(str(API_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    engine = create_db_engine(url)
    factory = create_session_factory(engine)

    def uow(ator: Actor = NOIVO) -> SqlGuestsUnitOfWork:
        return SqlGuestsUnitOfWork(factory, clock, ator)

    ids = UuidGenerator()
    yield SimpleNamespace(
        engine=engine,
        clock=clock,
        uow=uow,
        lista=GetGuestList(uow),
        criar=CreateHousehold(uow, ids),
        acrescentar=AddGuest(uow, ids),
        acompanhante=AddCompanion(uow, ids),
        atualizar=UpdateGuest(uow),
        status=ChangeGuestStatus(uow, ids),
        mover=MoveGuest(uow),
        excluir=DeleteGuest(uow, clock),
        restaurar=RestoreGuest(uow),
        excluir_nucleo=DeleteHousehold(uow, clock),
        restaurar_nucleo=RestoreHousehold(uow),
        historico=ListGuestStatusHistory(uow),
    )
    engine.dispose()


def _novo_nucleo(banco, nome="Família Exemplo", primeira="Convidado Exemplo A", **extra):
    lista = banco.criar.execute(
        CreateHouseholdCommand(
            HouseholdFields(name=nome, side=Side.COMUM, **extra), GuestFields(name=primeira)
        ),
        NOIVO,
    )
    return next(h for h in lista.households if h.name == nome)


class TestLeituraEEscrita:
    def test_a_lista_nasce_vazia(self, banco):  # AGENTS.md §2: nada é semeado
        assert banco.lista.execute(NOIVO).households == ()

    def test_grava_e_le_o_nucleo_com_as_pessoas_e_o_telefone_normalizado(self, banco):
        nucleo = _novo_nucleo(
            banco, street="Rua Exemplo", number="100", state="sp", postal_code="00000-000"
        )
        lista = banco.acrescentar.execute(
            AddGuestCommand(
                nucleo.id,
                GuestFields(
                    name="Convidado Exemplo B",
                    band=AgeBand.PAYING_CHILD,
                    age=9,
                    probability=Probability.CERTAIN,
                    phone="(11) 91234-5678",
                    email="convidado@exemplo.invalid",
                    dietary_restriction="Sem lactose",
                ),
            ),
            NOIVA,
        )

        lido = lista.households[0]
        assert (lido.street, lido.state, lido.postal_code) == ("Rua Exemplo", "SP", "00000-000")
        segunda = lido.guests[1]
        assert (segunda.band, segunda.age, segunda.probability) == (
            AgeBand.PAYING_CHILD,
            9,
            Probability.CERTAIN,
        )
        assert segunda.phone == "(11) 91234-5678"
        assert segunda.whatsapp_url == "https://wa.me/5511912345678"
        assert (lido.version, segunda.version) == (1, 1)
        with banco.engine.connect() as conn:
            guardado = conn.execute(select(guests.c.phone, guests.c.created_by)).all()
        assert ("11912345678", NOIVA.user_id) in [tuple(r) for r in guardado]

    def test_acompanhante_nasce_sem_nome_e_segue_o_titular(self, banco):
        nucleo = _novo_nucleo(banco)
        lista = banco.acompanhante.execute(AddCompanionCommand(nucleo.guests[0].id, None), NOIVO)

        acompanhante = lista.households[0].guests[1]
        assert acompanhante.name is None
        assert acompanhante.holder_name == "Convidado Exemplo A"

    def test_mudar_o_status_grava_o_historico_com_o_perfil(self, banco):
        pessoa = _novo_nucleo(banco).guests[0]

        banco.status.execute(
            ChangeGuestStatusCommand(pessoa.id, GuestStatus.DECLINED, "Viagem", pessoa.version),
            NOIVA,
        )

        historico = banco.historico.execute(pessoa.id, NOIVO)
        assert [(h.from_status, h.to_status, h.reason, h.profile) for h in historico] == [
            (GuestStatus.DRAFT, GuestStatus.DECLINED, "Viagem", ProfileKind.NOIVA)
        ]
        assert historico[0].changed_at == banco.clock.now()

    def test_excluir_e_restaurar_o_nucleo_pelo_banco(self, banco):
        nucleo = _novo_nucleo(banco)

        assert (
            banco.excluir_nucleo.execute(
                DeleteHouseholdCommand(nucleo.id, nucleo.version), NOIVO
            ).households
            == ()
        )
        lista = banco.restaurar_nucleo.execute(RestoreHouseholdCommand(nucleo.id), NOIVO)

        assert [h.name for h in lista.households] == ["Família Exemplo"]
        assert len(lista.households[0].guests) == 1

    def test_mover_leva_o_acompanhante_e_restaurar_excluido_junto_traz_os_dois(self, banco):
        origem = _novo_nucleo(banco, "Família Exemplo A")
        destino = _novo_nucleo(banco, "Família Exemplo B", primeira="Convidado Exemplo C")
        banco.acrescentar.execute(
            AddGuestCommand(origem.id, GuestFields(name="Convidado Exemplo B")), NOIVO
        )
        titular = origem.guests[0]
        banco.acompanhante.execute(AddCompanionCommand(titular.id, None), NOIVO)
        titular = banco.lista.execute(NOIVO).households[0].guests[0]

        lista = banco.mover.execute(
            MoveGuestCommand(titular.id, destino.id, titular.version), NOIVO
        )

        nomes = {h.name: [g.name for g in h.guests] for h in lista.households}
        assert nomes["Família Exemplo B"] == ["Convidado Exemplo C", "Convidado Exemplo A", None]
        titular = next(
            g for h in lista.households for g in h.guests if g.name == "Convidado Exemplo A"
        )
        banco.excluir.execute(
            DeleteGuestCommand(titular.id, titular.version, CompanionChoice.DELETE), NOIVO
        )
        lista = banco.restaurar.execute(RestoreGuestCommand(titular.id), NOIVO)
        assert {h.name: len(h.guests) for h in lista.households}["Família Exemplo B"] == 3

    def test_a_posicao_de_uma_pessoa_excluida_nao_e_reaproveitada(self, banco):
        nucleo = _novo_nucleo(banco)
        banco.acrescentar.execute(
            AddGuestCommand(nucleo.id, GuestFields(name="Convidado Exemplo B")), NOIVO
        )
        segunda = banco.lista.execute(NOIVO).households[0].guests[1]
        banco.excluir.execute(DeleteGuestCommand(segunda.id, segunda.version, None), NOIVO)
        banco.acrescentar.execute(
            AddGuestCommand(nucleo.id, GuestFields(name="Convidado Exemplo C")), NOIVO
        )

        lista = banco.restaurar.execute(RestoreGuestCommand(segunda.id), NOIVO)

        assert [g.name for g in lista.households[0].guests] == [
            "Convidado Exemplo A",
            "Convidado Exemplo B",
            "Convidado Exemplo C",
        ]

    def test_edicao_com_versao_velha_e_recusada(self, banco):
        pessoa = _novo_nucleo(banco).guests[0]
        banco.atualizar.execute(
            UpdateGuestCommand(
                pessoa.id,
                pessoa.version,
                GuestFields(name="Convidado Exemplo A", probability=Probability.PHASE_2),
                None,
            ),
            NOIVO,
        )

        with pytest.raises(VersionConflict):
            banco.atualizar.execute(
                UpdateGuestCommand(
                    pessoa.id, pessoa.version, GuestFields(name="Convidado Exemplo A"), None
                ),
                NOIVA,
            )


class TestConcorrencia:
    """Duas pessoas agindo ao mesmo tempo: o banco decide quem chega primeiro."""

    def test_o_mesmo_nome_de_nucleo_criado_ao_mesmo_tempo_da_nome_ja_usado(self, banco):
        with banco.uow() as a, banco.uow(NOIVA) as b:
            a.guests.add_household(Household(id=uuid4(), name=SENTINELA, side=Side.COMUM))
            b.guests.add_household(
                Household(id=uuid4(), name=f" {SENTINELA.upper()} ", side=Side.COMUM)
            )
            a.commit()
            with pytest.raises(DuplicateHouseholdName) as erro:
                b.commit()
        assert SENTINELA not in str(erro.value)

    def test_dois_acompanhantes_para_o_mesmo_titular_ao_mesmo_tempo_dao_erro_de_dominio(
        self, banco
    ):
        titular = _novo_nucleo(banco).guests[0]

        def acompanhante() -> Guest:
            return Guest(
                id=uuid4(),
                household_id=banco_household,
                position=1,
                name=None,
                companion_of_id=titular.id,
            )

        banco_household = titular.household_id
        with banco.uow() as a, banco.uow(NOIVA) as b:
            a.guests.add_guest(acompanhante())
            b.guests.add_guest(acompanhante())
            a.commit()
            with pytest.raises(CompanionAlreadyExists):
                b.commit()

    def test_duas_saidas_simultaneas_do_mesmo_nucleo_se_conflitam(self, banco):
        nucleo = _novo_nucleo(banco)
        banco.acrescentar.execute(
            AddGuestCommand(nucleo.id, GuestFields(name="Convidado Exemplo B")), NOIVO
        )
        primeira, segunda = banco.lista.execute(NOIVO).households[0].guests

        def sair(uow, guest_id):
            guest = uow.guests.get_guest(guest_id)
            household = uow.guests.get_household(nucleo.id)
            guest.delete(banco.clock.now(), None)
            household.touch_members()

        with banco.uow() as a, banco.uow(NOIVA) as b:
            sair(a, primeira.id)
            sair(b, segunda.id)
            a.commit()
            with pytest.raises(VersionConflict):
                b.commit()
        # O núcleo não ficou vazio: a segunda saída não foi gravada.
        assert len(banco.lista.execute(NOIVO).households[0].guests) == 1

    def test_o_caso_de_uso_recusa_a_saida_da_ultima_pessoa(self, banco):
        pessoa = _novo_nucleo(banco).guests[0]

        with pytest.raises(LastGuestInHousehold):
            banco.excluir.execute(DeleteGuestCommand(pessoa.id, pessoa.version, None), NOIVO)


class TestRegrasDoBanco:
    """O banco repete o que cabe em CHECK, índice e chave estrangeira (invariantes 1 a 7)."""

    def _household(self, conn, **valores):
        base = {
            "id": uuid4(),
            "created_at": AGORA,
            "updated_at": AGORA,
            "version": 1,
            "name": "Família Exemplo",
            "name_key": "família exemplo",
            "side": "Comum",
            "members_revision": 0,
        }
        household = {**base, **valores}
        conn.execute(insert(guest_households).values(household))
        return household["id"]

    def _guest(self, conn, household_id, **valores):
        base = {
            "id": uuid4(),
            "created_at": AGORA,
            "updated_at": AGORA,
            "version": 1,
            "household_id": household_id,
            "position": 0,
            "name": "Convidado Exemplo A",
            "band": "Adulto",
            "probability": "Provável",
            "status": "Rascunho",
        }
        guest = {**base, **valores}
        conn.execute(insert(guests).values(guest))
        return guest["id"]

    def test_nome_vivo_repetido_e_barrado_mas_o_de_excluido_pode_voltar(self, banco):
        with banco.engine.begin() as conn:
            self._household(conn)
            with pytest.raises(IntegrityError), conn.begin_nested():
                self._household(conn)
            conn.execute(text("UPDATE guest_households SET deleted_at = '2026-10-28 00:00:00'"))
            self._household(conn)

    def test_o_erro_do_banco_nao_traz_o_dado_pessoal(self, banco):
        with banco.engine.begin() as conn:
            self._household(conn, name=SENTINELA, name_key=SENTINELA.casefold())
            with pytest.raises(IntegrityError) as erro, conn.begin_nested():
                self._household(conn, name=SENTINELA, name_key=SENTINELA.casefold())
        assert SENTINELA not in str(erro.value)

    @pytest.mark.parametrize(
        "valores",
        [
            {"side": "Outro"},
            {"state": "S"},
            {"postal_code": "123"},
            {"members_revision": -1},
        ],
    )
    def test_nucleo_com_valor_fora_das_regras_e_barrado(self, banco, valores):
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            self._household(conn, **valores)

    @pytest.mark.parametrize(
        "valores",
        [
            {"band": "Outra"},
            {"probability": "Talvez"},
            {"status": "Pendente"},
            {"position": -1},
            {"name": None},  # sem nome só o acompanhante
            {"age": 7},  # adulto com idade
            {"band": "Criança isenta", "age": 18},
            {"band": "Criança isenta", "age": -1},
            {"decline_reason": "Viagem"},  # motivo sem Não irá
            {"status": "Convidado", "decline_reason": "Viagem"},
            {"phone": "123456789"},
        ],
    )
    def test_pessoa_com_valor_fora_das_regras_e_barrada(self, banco, valores):
        with banco.engine.begin() as conn:
            household = self._household(conn)
            with pytest.raises(IntegrityError):
                self._guest(conn, household, **valores)

    def test_pessoa_valida_no_limite_passa(self, banco):
        with banco.engine.begin() as conn:
            household = self._household(conn)
            self._guest(
                conn, household, band="Criança paganta".replace("paganta", "pagante"), age=17
            )
            self._guest(
                conn, household, status="Não irá", decline_reason="Viagem", phone="11912345678"
            )

    def test_so_um_acompanhante_vivo_por_titular_mas_o_excluido_libera_a_vaga(self, banco):
        with banco.engine.begin() as conn:
            household = self._household(conn)
            titular = self._guest(conn, household)
            primeiro = self._guest(conn, household, name=None, companion_of_id=titular)
            with pytest.raises(IntegrityError), conn.begin_nested():
                self._guest(conn, household, name=None, companion_of_id=titular)
            conn.execute(
                text("UPDATE guests SET deleted_at = '2026-10-28 00:00:00' WHERE id = :id"),
                {"id": primeiro.hex},
            )
            self._guest(conn, household, name=None, companion_of_id=titular)

    def test_acompanhante_nao_e_titular_de_si_mesmo(self, banco):
        with banco.engine.begin() as conn:
            household = self._household(conn)
            mesma = uuid4()
            with pytest.raises(IntegrityError):
                self._guest(conn, household, id=mesma, name=None, companion_of_id=mesma)

    def test_pessoa_de_nucleo_inexistente_e_barrada_pela_chave_estrangeira(self, banco):
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            self._guest(conn, uuid4())

    def test_nao_se_apaga_um_nucleo_que_ainda_tem_pessoas(self, banco):
        with banco.engine.begin() as conn:
            household = self._household(conn)
            self._guest(conn, household)
            with pytest.raises(IntegrityError):
                conn.execute(text("DELETE FROM guest_households"))

    def test_historico_com_o_mesmo_status_ou_motivo_fora_de_lugar_e_barrado(self, banco):
        with banco.engine.begin() as conn:
            household = self._household(conn)
            pessoa = self._guest(conn, household)
            for de, para, motivo in (
                ("Rascunho", "Rascunho", None),
                ("Rascunho", "Convidado", "Viagem"),
            ):
                with pytest.raises(IntegrityError), conn.begin_nested():
                    conn.execute(
                        text(
                            "INSERT INTO guest_status_changes (id, created_at, updated_at, "
                            "version, guest_id, from_status, to_status, reason, profile) "
                            "VALUES (:id, '2026-10-28', '2026-10-28', 1, :g, :de, :para, "
                            ":motivo, 'Noivo')"
                        ),
                        {
                            "id": uuid4().hex,
                            "g": pessoa.hex,
                            "de": de,
                            "para": para,
                            "motivo": motivo,
                        },
                    )


class TestConfiguracoes:
    """Pesos e limites de idade: uma linha vazia, semeada pela migration (F-CNV-03 e F-CNV-06)."""

    def test_a_semente_vem_vazia_e_na_versao_1(self, banco):
        with banco.uow() as uow:
            settings = uow.guests.get_settings()

            assert settings.weights is None
            assert settings.age_limits == AgeLimits(None, None)
            assert settings.version == 1

    def test_grava_os_pesos_e_os_limites_e_sobe_a_versao(self, banco):
        with banco.uow(NOIVA) as uow:
            uow.guests.get_settings().update(Weights(100, 70, 30), AgeLimits(5, 12))
            uow.commit()

        with banco.uow() as uow:
            settings = uow.guests.get_settings()
            assert settings.weights == Weights(100, 70, 30)
            assert settings.age_limits == AgeLimits(5, 12)
            assert settings.version == 2

    def test_duas_edicoes_simultaneas_das_configuracoes_se_conflitam(self, banco):
        with banco.uow() as a, banco.uow(NOIVA) as b:
            a.guests.get_settings().update(Weights(100, 70, 30), AgeLimits())
            b.guests.get_settings().update(Weights(90, 60, 20), AgeLimits())
            a.commit()
            with pytest.raises(VersionConflict):
                b.commit()

    @pytest.mark.parametrize(
        "valores",
        [
            {"weight_certain_pct": 100},  # só um dos três pesos
            {"weight_certain_pct": 100, "weight_probable_pct": 70},
            {"weight_certain_pct": 101, "weight_probable_pct": 70, "weight_phase_2_pct": 30},
            {"weight_certain_pct": -1, "weight_probable_pct": 70, "weight_phase_2_pct": 30},
            {"exempt_until_age": 18},
            {"paying_until_age": -1},
            {"exempt_until_age": 8, "paying_until_age": 5},
        ],
    )
    def test_configuracao_fora_das_regras_e_barrada_pelo_banco(self, banco, valores):
        sets = ", ".join(f"{coluna} = {valor}" for coluna, valor in valores.items())
        with banco.engine.begin() as conn, pytest.raises(IntegrityError):
            conn.execute(text(f"UPDATE guest_settings SET {sets}"))

    def test_os_tres_pesos_e_os_limites_coerentes_passam(self, banco):
        with banco.engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE guest_settings SET weight_certain_pct = 0, weight_probable_pct = 100, "
                    "weight_phase_2_pct = 50, exempt_until_age = 5, paying_until_age = 5"
                )
            )
