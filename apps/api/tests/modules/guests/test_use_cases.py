from uuid import uuid4

import pytest
from tests.modules.guests.conftest import NOIVA, NOIVO

from wedding.modules.guests.application.commands.add_companion import AddCompanionCommand
from wedding.modules.guests.application.commands.add_guest import AddGuestCommand
from wedding.modules.guests.application.commands.change_guest_status import (
    ChangeGuestStatusCommand,
)
from wedding.modules.guests.application.commands.create_household import CreateHouseholdCommand
from wedding.modules.guests.application.commands.delete_guest import (
    CompanionChoice,
    DeleteGuestCommand,
)
from wedding.modules.guests.application.commands.delete_household import DeleteHouseholdCommand
from wedding.modules.guests.application.commands.move_guest import MoveGuestCommand
from wedding.modules.guests.application.commands.restore_guest import RestoreGuestCommand
from wedding.modules.guests.application.commands.restore_household import (
    RestoreHouseholdCommand,
)
from wedding.modules.guests.application.commands.update_guest import UpdateGuestCommand
from wedding.modules.guests.application.commands.update_household import (
    UpdateHouseholdCommand,
)
from wedding.modules.guests.application.dto import GuestDto, GuestListDto, HouseholdDto
from wedding.modules.guests.application.fields import GuestFields, HouseholdFields
from wedding.modules.guests.domain.errors import (
    CompanionAlreadyExists,
    CompanionCannotHaveCompanion,
    CompanionChoiceRequired,
    CompanionMovesWithHolder,
    CompanionNeedsName,
    DuplicateHouseholdName,
    GuestNameRequired,
    InvalidGuestValue,
    LastGuestInHousehold,
)
from wedding.modules.guests.domain.values import GuestStatus, Probability, Side
from wedding.shared_kernel.errors import NotFound, VersionConflict
from wedding.shared_kernel.profile import ProfileKind


def household_of(lista: GuestListDto, nome: str) -> HouseholdDto:
    return next(h for h in lista.households if h.name == nome)


def guest_of(lista: GuestListDto, nome: str) -> GuestDto:
    return next(g for h in lista.households for g in h.guests if g.name == nome)


def novo_nucleo(world, nome="Família Exemplo", primeira="Convidado Exemplo A", ator=NOIVO, **extra):
    lista = world.use_cases().create_household.execute(
        CreateHouseholdCommand(
            HouseholdFields(name=nome, side=Side.COMUM, **extra), GuestFields(name=primeira)
        ),
        ator,
    )
    return lista, household_of(lista, nome.strip())


def nova_pessoa(world, nucleo: HouseholdDto, nome: str, ator=NOIVO, **campos):
    lista = world.use_cases().add_guest.execute(
        AddGuestCommand(nucleo.id, GuestFields(name=nome, **campos)), ator
    )
    return lista, guest_of(lista, nome)


def mudar_status(world, pessoa: GuestDto, status, motivo=None, ator=NOIVO, versao=None):
    return world.use_cases().change_guest_status.execute(
        ChangeGuestStatusCommand(
            pessoa.id, status, motivo, pessoa.version if versao is None else versao
        ),
        ator,
    )


class TestNucleos:
    def test_cria_o_nucleo_ja_com_a_primeira_pessoa(self, world):  # F-CNV-01, decisão 1
        lista, nucleo = novo_nucleo(world)

        assert [g.name for g in nucleo.guests] == ["Convidado Exemplo A"]
        assert (nucleo.version, nucleo.guests[0].version) == (1, 1)
        assert nucleo.guests[0].status is GuestStatus.DRAFT
        assert len(lista.households) == 1

    def test_o_cadastro_rapido_acrescenta_pessoas_em_sequencia(self, world):  # F-CNV-01
        _, nucleo = novo_nucleo(world)
        for nome in ("Convidado Exemplo B", "Convidado Exemplo C", "Convidado Exemplo D"):
            lista, _ = nova_pessoa(world, nucleo, nome)

        assert len(household_of(lista, "Família Exemplo").guests) == 4

    def test_nome_repetido_sem_diferenciar_caixa_e_recusado(self, world):  # F-CNV-01
        novo_nucleo(world, "Família Exemplo")

        with pytest.raises(DuplicateHouseholdName):
            novo_nucleo(world, "  FAMÍLIA   exemplo ")

    def test_nao_cria_o_nucleo_se_a_primeira_pessoa_e_invalida(self, world):
        with pytest.raises(GuestNameRequired):
            world.use_cases().create_household.execute(
                CreateHouseholdCommand(
                    HouseholdFields(name="Família Exemplo", side=Side.COMUM), GuestFields(name=None)
                ),
                NOIVO,
            )

        assert world.use_cases().get_guest_list.execute(NOIVO).households == ()

    def test_edita_o_nucleo_e_recusa_versao_velha(self, world):
        _, nucleo = novo_nucleo(world)

        lista = world.use_cases().update_household.execute(
            UpdateHouseholdCommand(
                nucleo.id,
                nucleo.version,
                HouseholdFields(
                    name="Família Exemplo",
                    side=Side.NOIVA,
                    street="Rua Exemplo",
                    number="100",
                    postal_code="00000-000",
                ),
            ),
            NOIVA,
        )

        editado = household_of(lista, "Família Exemplo")
        assert (editado.side, editado.street, editado.postal_code) == (
            Side.NOIVA,
            "Rua Exemplo",
            "00000-000",
        )
        assert editado.version == nucleo.version + 1
        with pytest.raises(VersionConflict):
            world.use_cases().update_household.execute(
                UpdateHouseholdCommand(
                    nucleo.id,
                    nucleo.version,
                    HouseholdFields(name="Outro Exemplo", side=Side.COMUM),
                ),
                NOIVO,
            )

    def test_renomear_para_o_proprio_nome_nao_conflita_mas_para_o_de_outro_sim(self, world):
        _, a = novo_nucleo(world, "Família Exemplo A")
        _, b = novo_nucleo(world, "Família Exemplo B")

        world.use_cases().update_household.execute(
            UpdateHouseholdCommand(
                a.id, a.version, HouseholdFields(name="FAMÍLIA EXEMPLO A", side=Side.COMUM)
            ),
            NOIVO,
        )
        with pytest.raises(DuplicateHouseholdName):
            world.use_cases().update_household.execute(
                UpdateHouseholdCommand(
                    b.id, b.version, HouseholdFields(name="família exemplo a", side=Side.COMUM)
                ),
                NOIVO,
            )

    def test_excluir_o_nucleo_o_tira_da_lista_e_restaurar_o_devolve(self, world):  # F-CNV-01
        _, nucleo = novo_nucleo(world)

        lista = world.use_cases().delete_household.execute(
            DeleteHouseholdCommand(nucleo.id, nucleo.version), NOIVO
        )
        assert lista.households == ()

        lista = world.use_cases().restore_household.execute(
            RestoreHouseholdCommand(nucleo.id), NOIVO
        )
        assert len(household_of(lista, "Família Exemplo").guests) == 1

    def test_restaurar_com_o_nome_ocupado_e_recusado(self, world):
        _, antigo = novo_nucleo(world, "Família Exemplo")
        world.use_cases().delete_household.execute(
            DeleteHouseholdCommand(antigo.id, antigo.version), NOIVO
        )
        novo_nucleo(world, "Família Exemplo")

        with pytest.raises(DuplicateHouseholdName):
            world.use_cases().restore_household.execute(RestoreHouseholdCommand(antigo.id), NOIVO)

    def test_restaurar_o_que_nao_esta_excluido_e_nao_encontrado(self, world):
        _, nucleo = novo_nucleo(world)

        with pytest.raises(NotFound):
            world.use_cases().restore_household.execute(RestoreHouseholdCommand(nucleo.id), NOIVO)

    def test_ordena_os_nucleos_por_nome(self, world):
        novo_nucleo(world, "Família Exemplo B")
        lista, _ = novo_nucleo(world, "Família Exemplo A")

        assert [h.name for h in lista.households] == ["Família Exemplo A", "Família Exemplo B"]

    def test_acrescentar_pessoa_a_nucleo_inexistente_ou_excluido_e_nao_encontrado(self, world):
        with pytest.raises(NotFound):
            world.use_cases().add_guest.execute(
                AddGuestCommand(uuid4(), GuestFields(name="Convidado Exemplo A")), NOIVO
            )


class TestPessoas:
    def test_pessoa_nasce_com_os_padroes_da_spec(self, world):
        _, nucleo = novo_nucleo(world)
        _, pessoa = nova_pessoa(world, nucleo, "Convidado Exemplo B")

        assert (pessoa.status, pessoa.probability) == (GuestStatus.DRAFT, Probability.PROBABLE)
        assert pessoa.band.value == "Adulto"

    def test_edita_a_pessoa_e_o_telefone_vira_link(self, world):  # F-CNV-01
        _, nucleo = novo_nucleo(world)
        pessoa = nucleo.guests[0]

        lista = world.use_cases().update_guest.execute(
            UpdateGuestCommand(
                pessoa.id,
                pessoa.version,
                GuestFields(
                    name="Convidado Exemplo A",
                    probability=Probability.CERTAIN,
                    phone="(11) 91234-5678",
                    email="convidado@exemplo.invalid",
                    dietary_restriction="Sem lactose",
                ),
                None,
            ),
            NOIVA,
        )

        editada = guest_of(lista, "Convidado Exemplo A")
        assert editada.phone == "(11) 91234-5678"
        assert editada.whatsapp_url == "https://wa.me/5511912345678"
        assert (editada.probability, editada.dietary_restriction) == (
            Probability.CERTAIN,
            "Sem lactose",
        )
        assert editada.version == pessoa.version + 1

    def test_edicao_com_versao_velha_e_recusada(self, world):
        _, nucleo = novo_nucleo(world)
        pessoa = nucleo.guests[0]

        with pytest.raises(VersionConflict):
            world.use_cases().update_guest.execute(
                UpdateGuestCommand(
                    pessoa.id, pessoa.version + 1, GuestFields(name="Convidado Exemplo A"), None
                ),
                NOIVO,
            )

    def test_pessoa_inexistente_e_nao_encontrada(self, world):
        with pytest.raises(NotFound):
            world.use_cases().change_guest_status.execute(
                ChangeGuestStatusCommand(uuid4(), GuestStatus.CONFIRMED, None, 1), NOIVO
            )


class TestAcompanhante:
    def test_o_mais_um_nasce_sem_nome_no_nucleo_do_titular(self, world):  # F-CNV-02
        _, nucleo = novo_nucleo(world)
        titular = nucleo.guests[0]

        lista = world.use_cases().add_companion.execute(
            AddCompanionCommand(titular.id, None), NOIVO
        )

        acompanhante = household_of(lista, "Família Exemplo").guests[1]
        assert acompanhante.name is None
        assert (acompanhante.companion_of_id, acompanhante.holder_name) == (
            titular.id,
            "Convidado Exemplo A",
        )
        assert acompanhante.status is GuestStatus.DRAFT
        assert acompanhante.household_id == nucleo.id

    def test_so_um_acompanhante_por_titular(self, world):
        _, nucleo = novo_nucleo(world)
        titular = nucleo.guests[0]
        world.use_cases().add_companion.execute(AddCompanionCommand(titular.id, None), NOIVO)

        with pytest.raises(CompanionAlreadyExists):
            world.use_cases().add_companion.execute(AddCompanionCommand(titular.id, None), NOIVO)

    def test_acompanhante_nao_leva_acompanhante(self, world):
        _, nucleo = novo_nucleo(world)
        lista = world.use_cases().add_companion.execute(
            AddCompanionCommand(nucleo.guests[0].id, None), NOIVO
        )
        acompanhante = household_of(lista, "Família Exemplo").guests[1]

        with pytest.raises(CompanionCannotHaveCompanion):
            world.use_cases().add_companion.execute(
                AddCompanionCommand(acompanhante.id, None), NOIVO
            )

    def test_informar_o_nome_mantem_o_vinculo(self, world):  # F-CNV-02, regra 3
        _, nucleo = novo_nucleo(world)
        lista = world.use_cases().add_companion.execute(
            AddCompanionCommand(nucleo.guests[0].id, None), NOIVO
        )
        acompanhante = household_of(lista, "Família Exemplo").guests[1]

        lista = world.use_cases().update_guest.execute(
            UpdateGuestCommand(
                acompanhante.id,
                acompanhante.version,
                GuestFields(name="Acompanhante Exemplo"),
                None,
            ),
            NOIVO,
        )

        nomeado = guest_of(lista, "Acompanhante Exemplo")
        assert nomeado.companion_of_id == nucleo.guests[0].id

    def test_o_acompanhante_aparece_logo_depois_do_titular(self, world):
        _, nucleo = novo_nucleo(world)
        titular = nucleo.guests[0]
        nova_pessoa(world, nucleo, "Convidado Exemplo B")
        lista = world.use_cases().add_companion.execute(
            AddCompanionCommand(titular.id, None), NOIVO
        )

        nomes = [g.name for g in household_of(lista, "Família Exemplo").guests]

        assert nomes == ["Convidado Exemplo A", None, "Convidado Exemplo B"]


class TestStatus:
    def test_muda_o_status_e_grava_o_historico_com_o_perfil(self, world):  # F-CNV-04
        _, nucleo = novo_nucleo(world)
        pessoa = nucleo.guests[0]

        lista = mudar_status(world, pessoa, GuestStatus.INVITED, ator=NOIVA)

        assert guest_of(lista, "Convidado Exemplo A").status is GuestStatus.INVITED
        historico = world.use_cases().list_guest_status_history.execute(pessoa.id, NOIVO)
        assert [(h.from_status, h.to_status, h.profile) for h in historico] == [
            (GuestStatus.DRAFT, GuestStatus.INVITED, ProfileKind.NOIVA)
        ]

    def test_nao_ira_guarda_o_motivo_e_sem_motivo_tambem_salva(self, world):  # F-CNV-04
        _, nucleo = novo_nucleo(world, primeira="Convidado Exemplo A")
        _, segunda = nova_pessoa(world, nucleo, "Convidado Exemplo B")

        lista = mudar_status(world, nucleo.guests[0], GuestStatus.DECLINED, "Viagem")
        assert guest_of(lista, "Convidado Exemplo A").decline_reason == "Viagem"

        lista = mudar_status(world, segunda, GuestStatus.DECLINED)
        assert guest_of(lista, "Convidado Exemplo B").decline_reason is None

    def test_sair_de_nao_ira_apaga_o_motivo_e_o_historico_guarda(self, world):
        _, nucleo = novo_nucleo(world)
        lista = mudar_status(world, nucleo.guests[0], GuestStatus.DECLINED, "Viagem")
        declinou = guest_of(lista, "Convidado Exemplo A")

        lista = mudar_status(world, declinou, GuestStatus.CONFIRMED)

        assert guest_of(lista, "Convidado Exemplo A").decline_reason is None
        historico = world.use_cases().list_guest_status_history.execute(declinou.id, NOIVO)
        assert [(h.to_status, h.reason) for h in historico] == [
            (GuestStatus.CONFIRMED, None),
            (GuestStatus.DECLINED, "Viagem"),
        ]

    def test_motivo_com_outro_status_e_recusado(self, world):
        _, nucleo = novo_nucleo(world)

        with pytest.raises(InvalidGuestValue):
            mudar_status(world, nucleo.guests[0], GuestStatus.CONFIRMED, "Viagem")

    def test_repetir_o_status_nao_grava_historico_nem_sobe_a_versao(self, world):
        _, nucleo = novo_nucleo(world)
        pessoa = nucleo.guests[0]

        lista = mudar_status(world, pessoa, GuestStatus.DRAFT)

        assert guest_of(lista, "Convidado Exemplo A").version == pessoa.version
        assert world.use_cases().list_guest_status_history.execute(pessoa.id, NOIVO) == []

    def test_versao_velha_e_recusada_e_nao_grava_nada(self, world):
        _, nucleo = novo_nucleo(world)
        pessoa = nucleo.guests[0]

        with pytest.raises(VersionConflict):
            mudar_status(world, pessoa, GuestStatus.CONFIRMED, versao=pessoa.version + 1)

        assert world.use_cases().list_guest_status_history.execute(pessoa.id, NOIVO) == []

    def test_o_resumo_do_nucleo_acompanha_os_status(self, world):  # F-CNV-04, regra 1
        _, nucleo = novo_nucleo(world)
        _, b = nova_pessoa(world, nucleo, "Convidado Exemplo B")
        mudar_status(world, nucleo.guests[0], GuestStatus.CONFIRMED)

        lista = mudar_status(world, b, GuestStatus.CONFIRMED)

        resumo = household_of(lista, "Família Exemplo").summary
        assert (resumo.total, resumo.confirmed) == (2, 2)


class TestMover:
    def test_move_a_pessoa_para_o_fim_do_outro_nucleo(self, world):
        _, origem = novo_nucleo(world, "Família Exemplo A")
        _, pessoa = nova_pessoa(world, origem, "Convidado Exemplo B")
        _, destino = novo_nucleo(world, "Família Exemplo B", primeira="Convidado Exemplo C")

        lista = world.use_cases().move_guest.execute(
            MoveGuestCommand(pessoa.id, destino.id, pessoa.version), NOIVO
        )

        assert [g.name for g in household_of(lista, "Família Exemplo B").guests] == [
            "Convidado Exemplo C",
            "Convidado Exemplo B",
        ]
        assert [g.name for g in household_of(lista, "Família Exemplo A").guests] == [
            "Convidado Exemplo A"
        ]

    def test_o_acompanhante_vai_junto_com_o_titular(self, world):  # decisão 4 do usuário
        _, origem = novo_nucleo(world, "Família Exemplo A")
        titular = origem.guests[0]
        nova_pessoa(world, origem, "Convidado Exemplo B")
        world.use_cases().add_companion.execute(AddCompanionCommand(titular.id, None), NOIVO)
        _, destino = novo_nucleo(world, "Família Exemplo B", primeira="Convidado Exemplo C")

        lista = world.use_cases().move_guest.execute(
            MoveGuestCommand(titular.id, destino.id, titular.version), NOIVO
        )

        nomes = [g.name for g in household_of(lista, "Família Exemplo B").guests]
        assert nomes == ["Convidado Exemplo C", "Convidado Exemplo A", None]

    def test_acompanhante_nao_muda_de_nucleo_sozinho(self, world):
        _, origem = novo_nucleo(world, "Família Exemplo A")
        lista = world.use_cases().add_companion.execute(
            AddCompanionCommand(origem.guests[0].id, None), NOIVO
        )
        acompanhante = household_of(lista, "Família Exemplo A").guests[1]
        _, destino = novo_nucleo(world, "Família Exemplo B")

        with pytest.raises(CompanionMovesWithHolder):
            world.use_cases().move_guest.execute(
                MoveGuestCommand(acompanhante.id, destino.id, acompanhante.version), NOIVO
            )

    def test_mover_a_ultima_pessoa_do_nucleo_e_recusado(self, world):  # decisão 6 do plano
        _, origem = novo_nucleo(world, "Família Exemplo A")
        _, destino = novo_nucleo(world, "Família Exemplo B")

        with pytest.raises(LastGuestInHousehold):
            world.use_cases().move_guest.execute(
                MoveGuestCommand(origem.guests[0].id, destino.id, origem.guests[0].version), NOIVO
            )

    def test_mover_titular_com_acompanhante_que_esvazia_o_nucleo_e_recusado(self, world):
        _, origem = novo_nucleo(world, "Família Exemplo A")
        world.use_cases().add_companion.execute(
            AddCompanionCommand(origem.guests[0].id, None), NOIVO
        )
        _, destino = novo_nucleo(world, "Família Exemplo B")

        with pytest.raises(LastGuestInHousehold):
            world.use_cases().move_guest.execute(
                MoveGuestCommand(origem.guests[0].id, destino.id, origem.guests[0].version), NOIVO
            )

    def test_destino_inexistente_e_nao_encontrado(self, world):
        _, origem = novo_nucleo(world)
        _, pessoa = nova_pessoa(world, origem, "Convidado Exemplo B")

        with pytest.raises(NotFound):
            world.use_cases().move_guest.execute(
                MoveGuestCommand(pessoa.id, uuid4(), pessoa.version), NOIVO
            )

    def test_sair_do_nucleo_sobe_a_versao_dele(self, world):  # invariante 2 sob concorrência
        _, origem = novo_nucleo(world, "Família Exemplo A")
        _, pessoa = nova_pessoa(world, origem, "Convidado Exemplo B")
        _, destino = novo_nucleo(world, "Família Exemplo B")

        lista = world.use_cases().move_guest.execute(
            MoveGuestCommand(pessoa.id, destino.id, pessoa.version), NOIVO
        )

        assert household_of(lista, "Família Exemplo A").version > origem.version


class TestExcluirPessoa:
    def test_exclui_a_pessoa_e_a_restauracao_a_devolve(self, world):
        _, nucleo = novo_nucleo(world)
        _, pessoa = nova_pessoa(world, nucleo, "Convidado Exemplo B")

        lista = world.use_cases().delete_guest.execute(
            DeleteGuestCommand(pessoa.id, pessoa.version, None), NOIVO
        )
        assert [g.name for g in household_of(lista, "Família Exemplo").guests] == [
            "Convidado Exemplo A"
        ]

        lista = world.use_cases().restore_guest.execute(RestoreGuestCommand(pessoa.id), NOIVO)
        assert len(household_of(lista, "Família Exemplo").guests) == 2

    def test_excluir_a_ultima_pessoa_e_recusado(self, world):  # decisão 1 do usuário
        _, nucleo = novo_nucleo(world)
        pessoa = nucleo.guests[0]

        with pytest.raises(LastGuestInHousehold):
            world.use_cases().delete_guest.execute(
                DeleteGuestCommand(pessoa.id, pessoa.version, None), NOIVO
            )

    def test_titular_com_acompanhante_exige_escolher_o_que_fazer(self, world):  # F-CNV-02, regra 4
        _, nucleo = novo_nucleo(world)
        nova_pessoa(world, nucleo, "Convidado Exemplo B")
        titular = nucleo.guests[0]
        world.use_cases().add_companion.execute(AddCompanionCommand(titular.id, None), NOIVO)

        with pytest.raises(CompanionChoiceRequired):
            world.use_cases().delete_guest.execute(
                DeleteGuestCommand(titular.id, titular.version, None), NOIVO
            )

    def test_excluir_junto_leva_o_acompanhante_e_restaurar_traz_os_dois(self, world):
        _, nucleo = novo_nucleo(world)
        nova_pessoa(world, nucleo, "Convidado Exemplo B")
        titular = nucleo.guests[0]
        world.use_cases().add_companion.execute(AddCompanionCommand(titular.id, None), NOIVO)

        lista = world.use_cases().delete_guest.execute(
            DeleteGuestCommand(titular.id, titular.version, CompanionChoice.DELETE), NOIVO
        )
        assert [g.name for g in household_of(lista, "Família Exemplo").guests] == [
            "Convidado Exemplo B"
        ]

        lista = world.use_cases().restore_guest.execute(RestoreGuestCommand(titular.id), NOIVO)
        assert len(household_of(lista, "Família Exemplo").guests) == 3

    def test_manter_o_acompanhante_nomeado_o_desvincula(self, world):
        _, nucleo = novo_nucleo(world)
        titular = nucleo.guests[0]
        lista = world.use_cases().add_companion.execute(
            AddCompanionCommand(titular.id, None), NOIVO
        )
        acompanhante = household_of(lista, "Família Exemplo").guests[1]
        lista = world.use_cases().update_guest.execute(
            UpdateGuestCommand(
                acompanhante.id,
                acompanhante.version,
                GuestFields(name="Acompanhante Exemplo"),
                None,
            ),
            NOIVO,
        )

        lista = world.use_cases().delete_guest.execute(
            DeleteGuestCommand(titular.id, titular.version, CompanionChoice.KEEP), NOIVO
        )

        restante = guest_of(lista, "Acompanhante Exemplo")
        assert (restante.companion_of_id, restante.holder_name) == (None, None)

    def test_manter_o_acompanhante_sem_nome_e_recusado(self, world):  # decisão 11 do plano
        _, nucleo = novo_nucleo(world)
        nova_pessoa(world, nucleo, "Convidado Exemplo B")
        titular = nucleo.guests[0]
        world.use_cases().add_companion.execute(AddCompanionCommand(titular.id, None), NOIVO)

        with pytest.raises(CompanionNeedsName):
            world.use_cases().delete_guest.execute(
                DeleteGuestCommand(titular.id, titular.version, CompanionChoice.KEEP), NOIVO
            )

    def test_excluir_so_o_acompanhante(self, world):
        _, nucleo = novo_nucleo(world)
        lista = world.use_cases().add_companion.execute(
            AddCompanionCommand(nucleo.guests[0].id, None), NOIVO
        )
        acompanhante = household_of(lista, "Família Exemplo").guests[1]

        lista = world.use_cases().delete_guest.execute(
            DeleteGuestCommand(acompanhante.id, acompanhante.version, None), NOIVO
        )

        assert len(household_of(lista, "Família Exemplo").guests) == 1

    def test_restaurar_acompanhante_com_titular_excluido_e_nao_encontrado(self, world):
        _, nucleo = novo_nucleo(world)
        nova_pessoa(world, nucleo, "Convidado Exemplo B")
        titular = nucleo.guests[0]
        lista = world.use_cases().add_companion.execute(
            AddCompanionCommand(titular.id, None), NOIVO
        )
        acompanhante = household_of(lista, "Família Exemplo").guests[1]
        world.use_cases().delete_guest.execute(
            DeleteGuestCommand(acompanhante.id, acompanhante.version, None), NOIVO
        )
        titular = guest_of(world.use_cases().get_guest_list.execute(NOIVO), "Convidado Exemplo A")
        world.use_cases().delete_guest.execute(
            DeleteGuestCommand(titular.id, titular.version, None), NOIVO
        )

        with pytest.raises(NotFound):
            world.use_cases().restore_guest.execute(RestoreGuestCommand(acompanhante.id), NOIVO)

    def test_versao_velha_na_exclusao_e_recusada(self, world):
        _, nucleo = novo_nucleo(world)
        _, pessoa = nova_pessoa(world, nucleo, "Convidado Exemplo B")

        with pytest.raises(VersionConflict):
            world.use_cases().delete_guest.execute(
                DeleteGuestCommand(pessoa.id, pessoa.version + 1, None), NOIVO
            )


def test_a_autoria_vem_da_sessao(world):
    novo_nucleo(world, ator=NOIVA)

    assert [a.profile for a in world.actors] == [ProfileKind.NOIVA]
