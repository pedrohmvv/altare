"""O anexo de um marco ou de uma avulsa (F-CRN-08): o endereço do link, o arquivo copiado, os textos
opcionais, o autor que remove e a remoção lógica."""

import contextlib
import re
import unicodedata
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.schedule.domain.attachments import (
    AttachedFile,
    Attachment,
    AttachmentKind,
    display_domain,
    parse_link,
)
from wedding.modules.schedule.domain.errors import (
    AttachmentFileNotAllowed,
    InvalidAttachmentUrl,
    InvalidScheduleValue,
)
from wedding.modules.schedule.domain.values import OwnerKind
from wedding.shared_kernel.errors import Forbidden
from wedding.shared_kernel.profile import ProfileKind

INVALID = InvalidAttachmentUrl
AGORA = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)


class TestParseLink:
    """O mesmo corpus do `wedding` (F-PLN-06): o `schedule` não importa outro módulo, e a cópia
    promove para o `shared_kernel` no terceiro uso (contatos)."""

    def test_mostra_o_dominio_sem_www_e_em_minusculas(self):  # F-CRN-08
        link = parse_link("  HTTPS://www.Exemplo.com.br/inspiracao/mesa?ref=1#topo ")
        assert link.url == "https://www.exemplo.com.br/inspiracao/mesa?ref=1#topo"
        assert link.domain == "exemplo.com.br"

    def test_http_tambem_vale(self):
        assert parse_link("http://exemplo.com").domain == "exemplo.com"

    @pytest.mark.parametrize(
        "url",
        [
            "",
            "   ",
            "exemplo.com",
            "//exemplo.com",
            "javascript:alert(1)",
            "JAVASCRIPT:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "ftp://exemplo.com/arquivo",
            "file:///etc/passwd",
            "http://",
            "https:///caminho",
            "https://localhost",
            "https://exem plo.com",
            "https://exemplo.com/a b",
            "https://usuario:senha@exemplo.com",
            "https://exemplo.com\n.evil.com",
            "https://" + "a" * 2000 + ".com",
        ],
    )
    def test_endereco_invalido_e_recusado_com_um_erro_proprio(self, url):
        with pytest.raises(InvalidAttachmentUrl):
            parse_link(url)

    @given(
        st.from_regex(r"[a-z0-9]{1,12}(\.[a-z0-9]{1,12}){1,3}", fullmatch=True),
        st.sampled_from(["http", "https", "HTTP", "Https"]),
        st.from_regex(r"(/[A-Za-z0-9_-]{0,10}){0,3}", fullmatch=True),
    )
    def test_todo_endereco_http_bem_formado_vale_e_o_dominio_e_o_do_host(self, host, scheme, path):
        link = parse_link(f"{scheme}://{host}{path}")
        assert link.url.startswith(scheme.lower() + "://")
        assert link.domain == host.removeprefix("www.")

    # Endereço que o navegador (WHATWG) lê diferente do que o domínio mostrado diz, ou com caractere
    # invisível, de controle ou de formato: o domínio visível é o indicador de confiança.
    @pytest.mark.parametrize(
        "url",
        [
            "https://banco-exemplo.com\\.gov.br/x",
            "https://exemplo.com\\@x.com",
            "https://exemplo.com/caminho\\segmento",
            "https://exemplo\u202e.com",
            "https://exemplo.com/\u202etxt.pdf",
            "https://exemplo\u200b.com",
            "https://exemplo.com/\u200bx",
            "https://exemplo\u200e.com",
            "https://exemplo.com/\x7f",
            "https://exemplo.com/\x00",
            "https://ex_emplo.com",
            "https://exemplo.com%2eevil.com",
            "https://exemplo!.com",
            "https://[::1]/x",
            "https://" + "ü" * 64 + ".com",
        ],
        ids=[
            "barra invertida no host",
            "barra invertida antes da arroba",
            "barra invertida no caminho",
            "bidi no host",
            "bidi no caminho",
            "largura zero no host",
            "largura zero no caminho",
            "marca esquerda-direita no host",
            "DEL",
            "NUL",
            "sublinhado no host",
            "host com porcento",
            "host com exclamacao",
            "IPv6",
            "IDN que nao codifica",
        ],
    )
    def test_endereco_enganoso_ou_com_caractere_invisivel_e_recusado(self, url):
        with pytest.raises(INVALID):
            parse_link(url)

    def test_idn_vira_punycode_no_endereco_guardado_e_no_dominio_exibido(self):
        link = parse_link(" https://WWW.München.de:8443/Bahn?q=ü#topo ")
        assert link.url == "https://www.xn--mnchen-3ya.de:8443/Bahn?q=ü#topo"
        assert link.domain == "xn--mnchen-3ya.de"

    def test_a_porta_e_o_resto_da_url_seguem_como_antes(self):
        link = parse_link("HTTP://Exemplo.com:8080/A/B?x=1")
        assert (link.url, link.domain) == ("http://exemplo.com:8080/A/B?x=1", "exemplo.com")

    @given(
        st.builds(
            lambda host, tail: f"https://{host}{tail}",
            st.text(
                alphabet=st.sampled_from(list("abz19.-_\\\u202e\u200b\u200e\x7fü@:% ")), max_size=14
            ),
            st.text(alphabet=st.sampled_from(list("/a1.\\\u202e\u200b\x7f\x01é? ")), max_size=10),
        )
        | st.text()
    )
    def test_nenhum_endereco_aceito_tem_barra_invertida_controle_ou_formato(self, texto):
        try:
            link = parse_link(texto)
        except INVALID:
            return
        assert "\\" not in link.url
        assert all(unicodedata.category(char) not in ("Cc", "Cf") for char in link.url)
        assert re.fullmatch(r"[a-z0-9.-]+", link.domain)
        assert "." in link.domain

    @given(st.text())
    def test_nunca_estoura_com_erro_que_nao_seja_o_do_dominio(self, texto):
        with contextlib.suppress(InvalidAttachmentUrl):
            parse_link(texto)


def _link(**over):
    base = {
        "id": uuid4(),
        "owner_kind": OwnerKind.MILESTONE,
        "owner_id": uuid4(),
        "profile": ProfileKind.NOIVA,
        "url": "https://exemplo.com/mesa",
        "title": "  Mesa  ",
        "comment": " gostamos ",
    }
    return Attachment.new_link(**{**base, **over})


def _arquivo(**over) -> AttachedFile:
    base = {
        "file_id": uuid4(),
        "name": "contrato-exemplo.pdf",
        "content_type": "application/pdf",
        "size_bytes": 2048,
    }
    return AttachedFile(**{**base, **over})


def _anexo_de_arquivo(**over):
    base = {
        "id": uuid4(),
        "owner_kind": OwnerKind.TASK,
        "owner_id": uuid4(),
        "profile": ProfileKind.NOIVO,
        "file": _arquivo(),
        "title": None,
        "comment": None,
    }
    return Attachment.new_file(**{**base, **over})


class TestAttachment:
    def test_link_guarda_url_dominio_titulo_e_comentario_limpos(self):  # F-CRN-08
        anexo = _link()
        assert (anexo.kind, anexo.url, anexo.file_id, anexo.file) == (
            AttachmentKind.LINK,
            "https://exemplo.com/mesa",
            None,
            None,
        )
        assert (anexo.domain, anexo.title, anexo.comment) == ("exemplo.com", "Mesa", "gostamos")

    def test_o_link_e_guardado_normalizado_como_nas_referencias(self):
        assert _link(url=" HTTPS://Exemplo.com/A ").url == "https://exemplo.com/A"

    def test_o_link_invalido_nao_vira_anexo(self):
        with pytest.raises(InvalidAttachmentUrl):
            _link(url="javascript:alert(1)")

    def test_titulo_e_comentario_sao_opcionais(self):
        anexo = _link(title="   ", comment=None)
        assert (anexo.title, anexo.comment) == (None, None)

    def test_titulo_ou_comentario_longos_sao_recusados_e_nao_cortados(self):
        with pytest.raises(InvalidScheduleValue):
            _link(title="x" * 121)
        with pytest.raises(InvalidScheduleValue):
            _link(comment="x" * 501)
        assert _link(title="x" * 120, comment="y" * 500).title == "x" * 120

    def test_arquivo_copia_nome_tipo_e_tamanho_e_nao_tem_url(self):  # F-CRN-08 (copia de D-085)
        arquivo = _arquivo(name="foto-exemplo.png", content_type="image/png", size_bytes=99)
        anexo = _anexo_de_arquivo(file=arquivo, title=" Foto ")
        assert (anexo.kind, anexo.url, anexo.domain) == (AttachmentKind.FILE, None, None)
        assert anexo.file == arquivo
        assert anexo.file_id == arquivo.file_id
        assert (anexo.file_name, anexo.content_type, anexo.size_bytes) == (
            "foto-exemplo.png",
            "image/png",
            99,
        )
        assert anexo.title == "Foto"

    @pytest.mark.parametrize("tipo", ["application/pdf", "image/jpeg", "image/png", "image/webp"])
    def test_pdf_e_imagem_valem(self, tipo):
        assert _anexo_de_arquivo(file=_arquivo(content_type=tipo)).content_type == tipo

    @pytest.mark.parametrize(
        "tipo",
        [
            "text/html",
            "application/zip",
            "application/octet-stream",
            "",
            "imagem/png",
            "pdf",
            "image/svg+xml",
            "image/gif",
            "image/heic",
            "image/",
            "IMAGE/PNG",
        ],
    )
    def test_arquivo_que_nao_e_pdf_nem_imagem_e_recusado(self, tipo):
        with pytest.raises(AttachmentFileNotAllowed):
            _anexo_de_arquivo(file=_arquivo(content_type=tipo))

    def test_o_dono_e_o_marco_ou_a_avulsa_e_o_tipo_acompanha(self):
        marco, avulsa = uuid4(), uuid4()
        assert (
            _link(owner_kind=OwnerKind.MILESTONE, owner_id=marco).owner_kind is OwnerKind.MILESTONE
        )
        anexo = _link(owner_kind=OwnerKind.TASK, owner_id=avulsa)
        assert (anexo.owner_kind, anexo.owner_id) == (OwnerKind.TASK, avulsa)

    @pytest.mark.parametrize(
        ("url", "esperado"),
        [
            ("https://exemplo.com/mesa", "exemplo.com"),
            ("https://www.München.de/x", "xn--mnchen-3ya.de"),
            ("https://banco-exemplo.com\\.gov.br/x", "banco-exemplo.com"),
            ("https://exemplo\u202e.com/x", "exemplo.com"),
            ("https://WWW.ex_emplo.com/", "ex_emplo.com"),
            ("ftp://exemplo.com/arquivo", "exemplo.com"),
            ("https://localhost/x", "localhost"),
            ("http://[::1", None),
            ("isto nao e um endereco", None),
            ("", None),
        ],
    )
    def test_o_dominio_exibido_nunca_levanta_nem_com_linha_antiga_que_o_parse_atual_recusa(
        self, url, esperado
    ):
        """A leitura do cronograma inteiro não pode cair por um anexo gravado antes de uma regra
        mais apertada: mostra o que der (o host cru, sem controle nem a parte depois de `\\`)."""
        antigo = Attachment(
            uuid4(), OwnerKind.MILESTONE, uuid4(), AttachmentKind.LINK, ProfileKind.NOIVA, url=url
        )
        assert antigo.domain == esperado

    @given(st.text())
    def test_display_domain_e_total(self, texto):
        assert display_domain(texto) is None or isinstance(display_domain(texto), str)

    def test_o_perfil_ambos_nao_e_de_quem_anexa(self):
        with pytest.raises(ValueError, match="perfil de login"):
            _link(profile=ProfileKind.AMBOS)

    def test_so_o_autor_remove_o_seu_e_a_remocao_e_logica(self):  # F-CRN-08, regra 3
        anexo = _link()
        with pytest.raises(Forbidden):
            anexo.remove(ProfileKind.NOIVO, uuid4(), AGORA)
        assert anexo.deleted_at is None
        quem = uuid4()
        anexo.remove(ProfileKind.NOIVA, quem, AGORA)
        assert (anexo.deleted_at, anexo.deleted_by) == (AGORA, quem)
