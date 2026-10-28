import contextlib
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.wedding.domain.errors import InvalidReferenceUrl, InvalidScopeValue
from wedding.modules.wedding.domain.reference import (
    ReferenceKind,
    ScopeReference,
    parse_link,
)
from wedding.shared_kernel.errors import Forbidden
from wedding.shared_kernel.profile import ProfileKind

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
