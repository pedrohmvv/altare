import csv
import io
import zipfile
from datetime import date, datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from openpyxl import load_workbook

from wedding.modules.guests.adapters.http.exporters import write_csv, write_xlsx
from wedding.modules.guests.application.export_rows import (
    HEADERS,
    ExportRow,
    is_formula_like,
)

PERIGOSOS = ["=SOMA(1;1)", "+5511999999999", "-1", "@cmd", "\t=1", "\r=1"]


def linha(**campos) -> ExportRow:
    base = {
        "Núcleo": "Família Exemplo",
        "Lado": "Comum",
        "Nome": "Convidado Exemplo A",
        "Faixa": "Adulto",
        "Idade": None,
        "Probabilidade": "Provável",
        "Status": "Rascunho",
        "Restrição alimentar": None,
        "Observação": None,
        "Telefone": None,
        "E-mail": None,
        "Endereço do núcleo": None,
        "Convite enviado (data)": None,
        "Canal": None,
        "Motivo (Não irá)": None,
    }
    base.update(campos)
    return ExportRow(tuple(base[h] for h in HEADERS))


EXEMPLO = [
    linha(
        Nome="Criança Exemplo",
        Faixa="Criança pagante",
        Idade=9,
        Status="Não irá",
        **{
            "Restrição alimentar": "Sem glúten",
            "Observação": "Sentar perto; de preferência\nlonge da caixa de som",
            "Telefone": "(11) 91234-5678",
            "E-mail": "convidado@exemplo.invalid",
            "Endereço do núcleo": "Rua Exemplo, 100, Cidade Exemplo/SP, CEP 00000-000",
            "Convite enviado (data)": date(2026, 10, 20),
            "Canal": "WhatsApp",
            "Motivo (Não irá)": 'Viagem; disse "talvez no ano que vem"',
        },
    ),
    linha(Nome="Convidado Exemplo B"),
]


def ler_csv(dados: bytes) -> list[list[str]]:
    texto = dados.decode("utf-8-sig")
    return list(csv.reader(io.StringIO(texto, newline=""), delimiter=";"))


class TestCsv:
    def test_comeca_com_o_bom_do_utf8_para_o_excel_em_portugues(self):  # F-CNV-08, regra 3
        dados = write_csv(EXEMPLO)

        assert dados.startswith(b"\xef\xbb\xbf")

    def test_separa_por_ponto_e_virgula_e_termina_as_linhas_com_crlf(self):
        dados = write_csv(EXEMPLO[1:])

        assert dados.decode("utf-8-sig").splitlines(keepends=True)[0].endswith("\r\n")
        assert dados.decode("utf-8-sig").splitlines()[0] == ";".join(HEADERS)

    def test_cada_campo_cai_na_sua_coluna_e_os_acentos_sobrevivem(self):
        tabela = ler_csv(write_csv(EXEMPLO))

        assert tabela[0] == list(HEADERS)
        crianca = dict(zip(HEADERS, tabela[1], strict=True))
        assert crianca["Nome"] == "Criança Exemplo"
        assert crianca["Faixa"] == "Criança pagante"
        assert crianca["Status"] == "Não irá"
        assert crianca["Idade"] == "9"
        assert crianca["Convite enviado (data)"] == "20/10/2026"
        assert crianca["Observação"] == "Sentar perto; de preferência\nlonge da caixa de som"
        assert crianca["Motivo (Não irá)"] == 'Viagem; disse "talvez no ano que vem"'
        vazia = dict(zip(HEADERS, tabela[2], strict=True))
        assert (vazia["Idade"], vazia["Telefone"], vazia["Convite enviado (data)"]) == ("", "", "")

    @pytest.mark.parametrize("texto", PERIGOSOS)
    def test_texto_que_parece_formula_sai_com_apostrofo(self, texto):
        tabela = ler_csv(write_csv([linha(Observação=texto, Nome=texto)]))

        celulas = dict(zip(HEADERS, tabela[1], strict=True))
        assert celulas["Observação"] == f"'{texto}"
        assert celulas["Nome"] == f"'{texto}"
        assert not any(is_formula_like(c) for c in tabela[1])

    @given(st.text(max_size=60))
    @settings(max_examples=150)
    def test_nenhuma_celula_do_csv_comeca_perigosa_e_o_texto_original_se_recupera(self, texto):
        tabela = ler_csv(write_csv([linha(Observação=texto)]))
        celula = tabela[1][HEADERS.index("Observação")]

        assert not is_formula_like(celula)
        assert celula in (texto, f"'{texto}")

    def test_sem_pessoas_so_o_cabecalho(self):
        assert ler_csv(write_csv([])) == [list(HEADERS)]


class TestXlsx:
    def abrir(self, dados: bytes):
        # Sem data_only: uma fórmula apareceria com o tipo 'f'.
        return load_workbook(io.BytesIO(dados))

    def planilha(self, dados: bytes):
        ativa = self.abrir(dados).active
        assert ativa is not None
        return ativa

    def test_e_um_arquivo_xlsx_valido_que_abre_sem_aviso(self):  # F-CNV-08
        dados = write_xlsx(EXEMPLO)

        assert zipfile.is_zipfile(io.BytesIO(dados))
        assert self.abrir(dados).sheetnames == ["Convidados"]

    def test_cabecalho_em_negrito_fixo_com_filtro_e_larguras(self):  # F-CNV-08, regra 3
        planilha = self.planilha(write_xlsx(EXEMPLO))

        assert [c.value for c in planilha[1]] == list(HEADERS)
        assert all(c.font.bold for c in planilha[1])
        assert planilha.freeze_panes == "A2"
        assert planilha.auto_filter.ref == f"A1:O{len(EXEMPLO) + 1}"
        assert planilha.column_dimensions["L"].width > planilha.column_dimensions["B"].width

    def test_acentos_numeros_e_datas_de_verdade(self):
        planilha = self.planilha(write_xlsx(EXEMPLO))
        celulas = dict(zip(HEADERS, planilha[2], strict=True))

        assert celulas["Nome"].value == "Criança Exemplo"
        assert celulas["Status"].value == "Não irá"
        assert celulas["Idade"].value == 9
        assert isinstance(celulas["Idade"].value, int)
        convite = celulas["Convite enviado (data)"].value
        assert isinstance(convite, datetime)
        assert convite.date() == date(2026, 10, 20)
        assert celulas["Convite enviado (data)"].number_format == "DD/MM/YYYY"
        assert celulas["Observação"].value == "Sentar perto; de preferência\nlonge da caixa de som"

    @pytest.mark.parametrize("texto", PERIGOSOS)
    def test_texto_que_parece_formula_fica_texto_e_nunca_e_calculado(self, texto):
        planilha = self.planilha(write_xlsx([linha(Observação=texto, Nome=texto)]))

        for celula in planilha[2]:
            assert celula.data_type != "f"
        # O XML normaliza o retorno de carro em quebra de linha; o que importa é seguir sendo texto.
        guardado = planilha.cell(row=2, column=HEADERS.index("Observação") + 1).value
        assert guardado == texto.replace("\r", "\n")
        assert planilha.cell(row=2, column=HEADERS.index("Nome") + 1).data_type == "s"

    @given(st.text(max_size=80))
    @settings(max_examples=150, deadline=None)
    def test_qualquer_texto_vira_celula_de_texto_sem_derrubar_o_arquivo(self, texto):
        planilha = self.planilha(write_xlsx([linha(Observação=texto, Nome="Convidado Exemplo A")]))

        for celula in planilha[2]:
            assert celula.data_type != "f"

    def test_caractere_ilegal_no_xml_e_removido_em_vez_de_derrubar_a_exportacao(self):
        planilha = self.planilha(write_xlsx([linha(Observação="antes\x00\x1fdepois")]))

        assert planilha.cell(row=2, column=HEADERS.index("Observação") + 1).value == "antesdepois"

    def test_sem_pessoas_so_o_cabecalho(self):
        planilha = self.planilha(write_xlsx([]))

        assert planilha.max_row == 1
        assert planilha.auto_filter.ref == "A1:O2"
