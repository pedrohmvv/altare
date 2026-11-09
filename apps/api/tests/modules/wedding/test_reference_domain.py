import contextlib
import re
import unicodedata
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.wedding.domain.errors import InvalidReferenceUrl, InvalidScopeValue
from wedding.modules.wedding.domain.reference import (
    ReferenceKind,
    ScopeReference,
    display_domain,
    parse_link,
)
from wedding.shared_kernel.errors import Forbidden
from wedding.shared_kernel.profile import ProfileKind

INVALID = InvalidReferenceUrl
AGORA = datetime(2026, 10, 28, 12, 0, tzinfo=UTC)


class TestParseLink:
    def test_mostra_o_dominio_sem_www_e_em_minusculas(self):  # F-PLN-06
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
        with pytest.raises(InvalidReferenceUrl):
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
        with contextlib.suppress(InvalidReferenceUrl):
            parse_link(texto)


class TestScopeReference:
    def _link(self, **over):
        base = {
            "id": uuid4(),
            "category_id": uuid4(),
            "profile": ProfileKind.NOIVA,
            "url": "https://exemplo.com/mesa",
            "title": "  Mesa  ",
            "comment": " gostamos ",
        }
        return ScopeReference.new_link(**{**base, **over})

    def test_link_guarda_url_dominio_titulo_e_comentario_limpos(self):
        ref = self._link()
        assert (ref.kind, ref.url, ref.file_id) == (
            ReferenceKind.LINK,
            "https://exemplo.com/mesa",
            None,
        )
        assert (ref.domain, ref.title, ref.comment) == ("exemplo.com", "Mesa", "gostamos")

    def test_titulo_e_comentario_sao_opcionais(self):
        ref = self._link(title="   ", comment=None)
        assert (ref.title, ref.comment) == (None, None)

    def test_titulo_longo_ou_comentario_longo_e_recusado(self):
        with pytest.raises(InvalidScopeValue):
            self._link(title="x" * 121)
        with pytest.raises(InvalidScopeValue):
            self._link(comment="x" * 501)

    def test_imagem_guarda_o_arquivo_e_nao_tem_url(self):
        arquivo = uuid4()
        ref = ScopeReference.new_image(
            id=uuid4(),
            category_id=uuid4(),
            profile=ProfileKind.NOIVO,
            file_id=arquivo,
            title=None,
            comment=None,
        )
        assert (ref.kind, ref.file_id, ref.url, ref.domain) == (
            ReferenceKind.IMAGE,
            arquivo,
            None,
            None,
        )

    def test_so_o_autor_remove_a_sua_e_a_remocao_e_logica(self):  # F-PLN-06, regra 2
        ref = self._link()
        outro = uuid4()
        with pytest.raises(Forbidden):
            ref.remove(ProfileKind.NOIVO, outro, AGORA)
        assert ref.deleted_at is None
        autor = uuid4()
        ref.remove(ProfileKind.NOIVA, autor, AGORA)
        assert (ref.deleted_at, ref.deleted_by) == (AGORA, autor)


class TestDominioTotal:
    """O domínio exibido nunca levanta: uma referência gravada antes de uma regra mais apertada de
    `parse_link` não pode derrubar a listagem das referências."""

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
        ],
    )
    def test_referencia_antiga_que_o_parse_atual_recusa_mostra_o_host_cru_sem_estourar(
        self, url, esperado
    ):
        antiga = ScopeReference(
            id=uuid4(),
            category_id=uuid4(),
            kind=ReferenceKind.LINK,
            profile=ProfileKind.NOIVA,
            url=url,
        )
        assert antiga.domain == esperado

    @given(st.text())
    def test_display_domain_e_total_e_nunca_mostra_barra_invertida_nem_controle(self, texto):
        dominio = display_domain(texto)
        assert dominio is None or isinstance(dominio, str)
        assert all(
            char != "\\" and unicodedata.category(char) not in ("Cc", "Cf")
            for char in (dominio or "")
        )
