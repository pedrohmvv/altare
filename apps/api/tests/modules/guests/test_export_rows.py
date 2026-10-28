import re
from datetime import date

import pytest
from hypothesis import given
from hypothesis import strategies as st
from tests.modules.guests.conftest import NOIVO

from wedding.modules.guests.application.commands.add_companion import AddCompanionCommand
from wedding.modules.guests.application.commands.add_guest import AddGuestCommand
from wedding.modules.guests.application.commands.change_guest_status import (
    ChangeGuestStatusCommand,
)
from wedding.modules.guests.application.commands.create_household import CreateHouseholdCommand
from wedding.modules.guests.application.commands.record_household_invite import (
    RecordHouseholdInviteCommand,
)
from wedding.modules.guests.application.export_rows import (
    HEADERS,
    build_export_rows,
    is_formula_like,
    neutralize_cell,
)
from wedding.modules.guests.application.fields import GuestFields, HouseholdFields
from wedding.modules.guests.domain.values import AgeBand, GuestStatus, InviteChannel, Side

PERIGOSOS = ["=SOMA(1;1)", "+5511999999999", "-1", "@cmd", "\t=1", "\r=1", " =1+1", "  @x", "\n=1"]
SEGUROS = ["Maria da Silva", "1+1", "x=y", "a-b", "email@exemplo.invalid", "", "'=1", "Ana (=)"]


class TestNeutralizarCelula:
    @pytest.mark.parametrize("texto", PERIGOSOS)
    def test_o_que_comeca_como_formula_ganha_um_apostrofo(self, texto):
        assert is_formula_like(texto)
        assert neutralize_cell(texto) == f"'{texto}"
        assert not is_formula_like(neutralize_cell(texto))

    @pytest.mark.parametrize("texto", SEGUROS)
    def test_o_resto_do_texto_nao_muda(self, texto):
        assert not is_formula_like(texto)
        assert neutralize_cell(texto) == texto

    @pytest.mark.parametrize("inicio", list("=+-@\t\r"))
    def test_cada_caractere_perigoso_da_lista_e_barrado_no_inicio(self, inicio):
        assert neutralize_cell(f"{inicio}qualquer coisa").startswith("'")

    @given(st.text())
    def test_nenhum_texto_sai_perigoso_e_so_ganha_o_apostrofo(self, texto):
        neutro = neutralize_cell(texto)

        assert not is_formula_like(neutro)
        assert neutro in (texto, f"'{texto}")
        if not is_formula_like(texto):
            assert neutro == texto

    @given(st.text())
    def test_neutralizar_duas_vezes_e_o_mesmo_que_uma(self, texto):
        assert neutralize_cell(neutralize_cell(texto)) == neutralize_cell(texto)


def lista_de_exemplo(world):
    uc = world.use_cases()
    uc.create_household.execute(
        CreateHouseholdCommand(
            HouseholdFields(
                name="Família Exemplo",
                side=Side.NOIVA,
                street="Rua Exemplo",
                number="100",
                complement="apto 2",
                district="Bairro Exemplo",
                city="Cidade Exemplo",
                state="SP",
                postal_code="00000-000",
            ),
            GuestFields(
                name="Convidado Exemplo A",
                phone="(11) 91234-5678",
                email="convidado@exemplo.invalid",
                dietary_restriction="Sem lactose",
                note="Mesa perto da porta",
            ),
        ),
        NOIVO,
    )
    lista = uc.get_guest_list.execute(NOIVO)
    familia = lista.households[0]
    uc.add_guest.execute(
        AddGuestCommand(
            familia.id,
            GuestFields(name="Criança Exemplo", band=AgeBand.PAYING_CHILD, age=9),
        ),
        NOIVO,
    )
    uc.add_companion.execute(AddCompanionCommand(familia.guests[0].id, None), NOIVO)
    lista = uc.get_guest_list.execute(NOIVO)
    crianca = next(g for g in lista.households[0].guests if g.name == "Criança Exemplo")
    uc.change_guest_status.execute(
        ChangeGuestStatusCommand(crianca.id, GuestStatus.DECLINED, "Viagem", crianca.version), NOIVO
    )
    uc.create_household.execute(
        CreateHouseholdCommand(
            HouseholdFields(name="Amigos Exemplo", side=Side.COMUM),
            GuestFields(name="Convidado Exemplo Z"),
        ),
        NOIVO,
    )
    lista = uc.get_guest_list.execute(NOIVO)
    familia = next(h for h in lista.households if h.name == "Família Exemplo")
    return uc.record_household_invite.execute(
        RecordHouseholdInviteCommand(
            familia.id, familia.version, date(2026, 10, 20), InviteChannel.WHATSAPP, False
        ),
        NOIVO,
    )


class TestLinhas:
    def test_as_colunas_sao_as_da_spec_na_ordem(self):  # F-CNV-08
        assert HEADERS == (
            "Núcleo",
            "Lado",
            "Nome",
            "Faixa",
            "Idade",
            "Probabilidade",
            "Status",
            "Restrição alimentar",
            "Observação",
            "Telefone",
            "E-mail",
            "Endereço do núcleo",
            "Convite enviado (data)",
            "Canal",
            "Motivo (Não irá)",
        )

    def test_uma_linha_por_pessoa_com_o_endereco_e_o_convite_do_nucleo_repetidos(self, world):
        linhas = build_export_rows(lista_de_exemplo(world))

        da_familia = [r for r in linhas if r.cells[0] == "Família Exemplo"]
        assert len(linhas) == 4
        assert len(da_familia) == 3
        enderecos = {r.cells[11] for r in da_familia}
        assert enderecos == {
            "Rua Exemplo, 100, apto 2, Bairro Exemplo, Cidade Exemplo/SP, CEP 00000-000"
        }
        assert {(r.cells[12], r.cells[13]) for r in da_familia} == {
            (date(2026, 10, 20), "WhatsApp")
        }

    def test_o_conteudo_de_cada_coluna(self, world):
        linhas = build_export_rows(lista_de_exemplo(world))

        titular = next(r for r in linhas if r.cells[2] == "Convidado Exemplo A")
        assert titular.cells == (
            "Família Exemplo",
            "Noiva",
            "Convidado Exemplo A",
            "Adulto",
            None,
            "Provável",
            "Rascunho",
            "Sem lactose",
            "Mesa perto da porta",
            "(11) 91234-5678",
            "convidado@exemplo.invalid",
            "Rua Exemplo, 100, apto 2, Bairro Exemplo, Cidade Exemplo/SP, CEP 00000-000",
            date(2026, 10, 20),
            "WhatsApp",
            None,
        )
        crianca = next(r for r in linhas if r.cells[2] == "Criança Exemplo")
        assert (crianca.cells[3], crianca.cells[4], crianca.cells[6], crianca.cells[14]) == (
            "Criança pagante",
            9,
            "Não irá",
            "Viagem",
        )

    def test_o_acompanhante_sem_nome_sai_como_acompanhante_de_quem(self, world):  # F-CNV-02
        linhas = build_export_rows(lista_de_exemplo(world))

        assert "Acompanhante de Convidado Exemplo A" in {r.cells[2] for r in linhas}

    def test_o_nucleo_sem_endereco_nem_envio_sai_com_celulas_vazias(self, world):
        linhas = build_export_rows(lista_de_exemplo(world))

        amigos = next(r for r in linhas if r.cells[0] == "Amigos Exemplo")
        assert (amigos.cells[11], amigos.cells[12], amigos.cells[13]) == (None, None, None)

    def test_so_leva_as_pessoas_pedidas_e_mantem_a_ordem_da_lista(self, world):  # F-CNV-08, regra 2
        lista = lista_de_exemplo(world)
        noiva = next(h for h in lista.households if h.side is Side.NOIVA)
        pedidas = [g.id for g in noiva.guests]

        linhas = build_export_rows(lista, list(reversed(pedidas)))

        assert [r.cells[2] for r in linhas] == [
            "Convidado Exemplo A",
            "Acompanhante de Convidado Exemplo A",
            "Criança Exemplo",
        ]

    def test_sem_ids_leva_todas_e_com_lista_vazia_nao_leva_nenhuma(self, world):
        lista = lista_de_exemplo(world)

        assert len(build_export_rows(lista, None)) == 4
        assert build_export_rows(lista, []) == []

    def test_nenhuma_celula_traz_id_versao_nem_dado_de_auditoria(self, world):
        linhas = build_export_rows(lista_de_exemplo(world))

        uuid = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
        for linha in linhas:
            assert len(linha.cells) == len(HEADERS)
            assert not any(isinstance(c, str) and uuid.search(c) for c in linha.cells)
