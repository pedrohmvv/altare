"""O grafo de dependências (F-CRN-03, regra 2): ciclo, caminho do ciclo e o que restaura."""

from itertools import pairwise, product
from uuid import UUID

from hypothesis import given
from hypothesis import strategies as st

from wedding.modules.schedule.domain.entities import Dependency
from wedding.modules.schedule.domain.graph import depends_path, find_cycle, split_restorable


def n(numero: int) -> UUID:
    return UUID(int=numero)


def dep(marco: int, depende_de: int) -> Dependency:
    return Dependency(n(marco), n(depende_de))


def test_sem_arestas_nao_ha_caminho_nem_ciclo():
    assert depends_path([], n(1), n(2)) is None
    assert find_cycle([], n(1), [n(2)]) is None


def test_caminho_direto_e_transitivo_segue_o_depende_de():
    arestas = [dep(1, 2), dep(2, 3)]
    assert depends_path(arestas, n(1), n(2)) == (n(1), n(2))
    assert depends_path(arestas, n(1), n(3)) == (n(1), n(2), n(3))
    assert depends_path(arestas, n(3), n(1)) is None


def test_ciclo_direto_a_depende_de_b_e_b_passa_a_depender_de_a():
    arestas = [dep(1, 2)]  # A depende de B
    assert find_cycle(arestas, n(2), [n(1)]) == (n(2), n(1), n(2))


def test_ciclo_transitivo_traz_o_caminho_inteiro_comecando_e_terminando_no_marco():
    # B depende de A, C depende de B; fazer A depender de C fecha A → C → B → A.
    arestas = [dep(2, 1), dep(3, 2)]
    assert find_cycle(arestas, n(1), [n(3)]) == (n(1), n(3), n(2), n(1))


def test_o_caminho_do_ciclo_e_o_mais_curto():
    arestas = [dep(2, 1), dep(3, 2), dep(4, 3), dep(4, 1)]
    assert find_cycle(arestas, n(1), [n(4)]) == (n(1), n(4), n(1))


def test_predecessor_sem_volta_nao_fecha_ciclo():
    arestas = [dep(2, 1), dep(3, 1)]
    assert find_cycle(arestas, n(3), [n(2)]) is None


def test_varios_predecessores_acusam_o_primeiro_que_fecha_ciclo():
    arestas = [dep(2, 1)]
    assert find_cycle(arestas, n(1), [n(3), n(2)]) == (n(1), n(2), n(1))


def test_dependencias_antigas_do_proprio_marco_nao_atrapalham():
    # A depende de B hoje; trocar para A depender de C não é ciclo.
    assert find_cycle([dep(1, 2)], n(1), [n(3)]) is None


def test_restaurar_traz_as_arestas_que_nao_fecham_ciclo():
    aceitas, fora = split_restorable([], [dep(1, 2), dep(3, 1)])
    assert aceitas == [dep(1, 2), dep(3, 1)]
    assert fora == []


def test_restaurar_deixa_de_fora_a_aresta_que_hoje_fecharia_ciclo():
    # Hoje B depende de C. Voltar A traria A→B e C→A: C→A→B→C fecha ciclo na segunda.
    atuais = [dep(2, 3)]
    aceitas, fora = split_restorable(atuais, [dep(1, 2), dep(3, 1)])
    assert aceitas == [dep(1, 2)]
    assert fora == [dep(3, 1)]


def test_as_arestas_aceitas_contam_para_as_seguintes():
    aceitas, fora = split_restorable([], [dep(1, 2), dep(2, 1)])
    assert aceitas == [dep(1, 2)]
    assert fora == [dep(2, 1)]


def _acliclico(arestas) -> bool:
    restantes = set(arestas)
    nos = {x for a in arestas for x in a}
    while nos:
        livres = {x for x in nos if not any(a.milestone_id == x for a in restantes)}
        if not livres:
            return False
        nos -= livres
        restantes = {a for a in restantes if a.depends_on_id in nos}
    return True


def _alcanca(arestas, origem, destino) -> bool:
    vistos, fila = set(), [origem]
    while fila:
        atual = fila.pop()
        if atual == destino:
            return True
        if atual in vistos:
            continue
        vistos.add(atual)
        fila.extend(a.depends_on_id for a in arestas if a.milestone_id == atual)
    return False


PARES = st.lists(st.tuples(st.integers(1, 6), st.integers(1, 6)), max_size=40)


@given(PARES)
def test_o_grafo_continua_aciclico_depois_de_qualquer_sequencia_de_arestas_aceitas(pares):
    arestas: list[Dependency] = []
    for marco, predecessor in pares:
        if marco == predecessor or dep(marco, predecessor) in arestas:
            continue
        ciclo = find_cycle(arestas, n(marco), [n(predecessor)])
        # Recusa se, e só se, o predecessor já depende do marco (direta ou transitivamente).
        assert (ciclo is not None) == _alcanca(arestas, n(predecessor), n(marco))
        if ciclo is None:
            arestas.append(dep(marco, predecessor))
        assert _acliclico(arestas)


@given(PARES)
def test_o_caminho_do_ciclo_e_feito_de_arestas_que_existem(pares):
    arestas: list[Dependency] = []
    for marco, predecessor in pares:
        if marco == predecessor:
            continue
        ciclo = find_cycle(arestas, n(marco), [n(predecessor)])
        if ciclo is None:
            arestas.append(dep(marco, predecessor))
            continue
        assert ciclo[0] == ciclo[-1] == n(marco)
        assert ciclo[1] == n(predecessor)
        # O primeiro passo é a aresta proposta; os demais já existem.
        assert all(Dependency(a, b) in arestas for a, b in pairwise(ciclo[1:]))


@given(PARES, PARES)
def test_restaurar_nunca_devolve_um_grafo_com_ciclo(atuais, volta):
    base: list[Dependency] = []
    for marco, predecessor in atuais:
        if marco != predecessor and find_cycle(base, n(marco), [n(predecessor)]) is None:
            base.append(dep(marco, predecessor))
    candidatas = [dep(a, b) for a, b in volta if a != b and dep(a, b) not in base]
    aceitas, fora = split_restorable(base, candidatas)
    assert set(aceitas) | set(fora) == set(candidatas)
    assert not set(aceitas) & set(fora)
    assert _acliclico([*base, *aceitas])


def test_produto_de_exemplo_para_o_helper_de_alcance():
    # Guarda os dois oráculos do teste acima contra um erro de transcrição.
    arestas = [dep(1, 2), dep(2, 3)]
    assert all(
        _alcanca(arestas, n(a), n(b)) == (a < b)
        for a, b in product(range(1, 4), repeat=2)
        if a != b
    )
    assert _acliclico(arestas)
    assert not _acliclico([dep(1, 2), dep(2, 1)])
