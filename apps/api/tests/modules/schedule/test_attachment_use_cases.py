"""Os anexos (F-CRN-08) de marcos e de avulsas como casos de uso: link, arquivo (com a cópia de
nome, tipo e tamanho), remover só o autor, o dono excluído e a leitura. O anexo nunca toca o dono:
o estado e a `version` dele ficam como estavam."""

from uuid import UUID

import pytest
from tests.modules.schedule.catalog import marco_id
from tests.modules.schedule.conftest import NOIVA, NOIVO

from wedding.modules.schedule.application.commands.add_file_attachment import (
    AddFileAttachmentCommand,
)
from wedding.modules.schedule.application.commands.add_link_attachment import (
    AddLinkAttachmentCommand,
)
from wedding.modules.schedule.application.commands.create_task import CreateTaskCommand
from wedding.modules.schedule.application.commands.delete_milestone import DeleteMilestoneCommand
from wedding.modules.schedule.application.commands.delete_task import DeleteTaskCommand
from wedding.modules.schedule.application.commands.remove_attachment import (
    RemoveAttachmentCommand,
)
from wedding.modules.schedule.application.commands.restore_milestone import (
    RestoreMilestoneCommand,
)
from wedding.modules.schedule.application.commands.restore_task import RestoreTaskCommand
from wedding.modules.schedule.application.dto import AttachmentDto, ScheduleDto
from wedding.modules.schedule.domain.attachments import AttachmentKind
from wedding.modules.schedule.domain.errors import (
    AttachmentFileNotAllowed,
    InvalidAttachmentUrl,
    InvalidScheduleValue,
)
from wedding.modules.schedule.domain.values import OwnerKind
from wedding.shared_kernel.errors import Forbidden, NotFound
from wedding.shared_kernel.profile import ProfileKind

MARCO = "C06"


def ler(world, ator=NOIVO) -> ScheduleDto:
    return world.use_cases().read_schedule.execute(ator)


def marco(world, codigo=MARCO, ator=NOIVO):
    return next(
        m for f in ler(world, ator).phases for m in f.milestones if m.id == marco_id(codigo)
    )


def nova_avulsa(world) -> UUID:
    return (
        world.use_cases()
        .create_task.execute(CreateTaskCommand("Avulsa Exemplo", None, None, None), NOIVO)
        .tasks[0]
        .id
    )


def avulsa(world, tarefa: UUID, ator=NOIVO):
    return next(t for t in ler(world, ator).tasks if t.id == tarefa)


def anexar_link(world, tipo=OwnerKind.MILESTONE, dono=None, ator=NOIVO, **campos):
    comando = {
        "url": "https://exemplo.com/mesa",
        "title": None,
        "comment": None,
        **campos,
    }
    dono = dono or marco_id(MARCO)
    return world.use_cases().add_link_attachment.execute(
        AddLinkAttachmentCommand(tipo, dono, **comando), ator
    )


def anexar_arquivo(world, arquivo, tipo=OwnerKind.MILESTONE, dono=None, ator=NOIVO, **campos):
    comando = {"title": None, "comment": None, **campos}
    dono = dono or marco_id(MARCO)
    return world.use_cases().add_file_attachment.execute(
        AddFileAttachmentCommand(tipo, dono, arquivo.file_id, **comando), ator
    )


def remover(world, anexo: AttachmentDto, ator=NOIVO):
    return world.use_cases().remove_attachment.execute(RemoveAttachmentCommand(anexo.id), ator)


class TestAnexarLink:
    def test_o_link_aparece_no_marco_com_dominio_e_autor_da_sessao(self, world):  # F-CRN-08
        depois = anexar_link(
            world, url=" HTTPS://www.Exemplo.com/mesa ", title=" Mesa ", comment=" gostamos "
        )
        (anexo,) = next(
            m for f in depois.phases for m in f.milestones if m.id == marco_id(MARCO)
        ).attachments
        assert (anexo.kind, anexo.url, anexo.domain) == (
            AttachmentKind.LINK,
            "https://www.exemplo.com/mesa",
            "exemplo.com",
        )
        assert (anexo.title, anexo.comment, anexo.file) == ("Mesa", "gostamos", None)
        assert anexo.profile is ProfileKind.NOIVO
        assert anexo.added_at == world.clock.now()

    def test_o_link_vai_para_a_avulsa_e_nao_para_o_marco(self, world):
        tarefa = nova_avulsa(world)
        anexar_link(world, OwnerKind.TASK, tarefa)
        assert len(avulsa(world, tarefa).attachments) == 1
        assert all(not m.attachments for f in ler(world).phases for m in f.milestones)

    def test_o_autor_e_o_perfil_de_quem_chama(self, world):
        anexar_link(world, ator=NOIVA)
        assert marco(world).attachments[0].profile is ProfileKind.NOIVA

    @pytest.mark.parametrize(
        "url", ["javascript:alert(1)", "data:text/html,x", "ftp://exemplo.com/a", "https://x", ""]
    )
    def test_endereco_invalido_e_recusado_e_nada_e_gravado(self, world, url):
        with pytest.raises(InvalidAttachmentUrl):
            anexar_link(world, url=url)
        assert marco(world).attachments == ()

    def test_titulo_ou_comentario_longos_sao_recusados(self, world):
        with pytest.raises(InvalidScheduleValue):
            anexar_link(world, title="x" * 121)
        with pytest.raises(InvalidScheduleValue):
            anexar_link(world, comment="x" * 501)
        assert marco(world).attachments == ()

    def test_dono_inexistente_ou_com_o_tipo_trocado_da_404(self, world):
        with pytest.raises(NotFound):
            anexar_link(world, dono=UUID(int=2**100))
        with pytest.raises(NotFound):
            anexar_link(world, OwnerKind.TASK, marco_id(MARCO))

    def test_dono_excluido_da_404(self, world):
        uc = world.use_cases()
        uc.delete_milestone.execute(
            DeleteMilestoneCommand(marco_id(MARCO), marco(world).version), NOIVO
        )
        with pytest.raises(NotFound):
            anexar_link(world)

    def test_nao_ha_limite_de_anexos_por_item(self, world):  # decisão do usuário
        for numero in range(60):
            anexar_link(world, url=f"https://exemplo.com/{numero}")
        assert len(marco(world).attachments) == 60

    def test_anexar_nao_muda_o_estado_nem_a_version_do_dono(self, world):
        antes = marco(world)
        anexar_link(world)
        depois = marco(world)
        assert (depois.state, depois.version) == (antes.state, antes.version)
        assert len(depois.attachments) == 1

    def test_os_anexos_saem_na_ordem_em_que_foram_anexados(self, world):
        for numero in range(3):
            world.clock.advance(seconds=1)
            anexar_link(world, url=f"https://exemplo.com/{numero}")
        assert [a.url for a in marco(world).attachments] == [
            f"https://exemplo.com/{numero}" for numero in range(3)
        ]


class TestAnexarArquivo:
    def test_copia_nome_tipo_e_tamanho_do_arquivo_enviado(self, world):  # F-CRN-08 (cópia, D-085)
        arquivo = world.files.add("planta-exemplo.pdf", "application/pdf", 4096)
        anexar_arquivo(world, arquivo, title="Planta")
        (anexo,) = marco(world).attachments
        assert anexo.kind is AttachmentKind.FILE
        assert (anexo.url, anexo.domain) == (None, None)
        assert anexo.file is not None
        assert (anexo.file.id, anexo.file.name) == (arquivo.file_id, "planta-exemplo.pdf")
        assert (anexo.file.content_type, anexo.file.size_bytes) == ("application/pdf", 4096)
        assert anexo.title == "Planta"
        assert anexo.profile is ProfileKind.NOIVO

    def test_a_leitura_nao_consulta_o_files_so_o_ato_de_anexar_consulta(self, world):
        arquivo = world.files.add()
        anexar_arquivo(world, arquivo)
        consultas = world.files.calls
        ler(world)
        ler(world, NOIVA)
        assert world.files.calls == consultas == 1

    def test_o_anexo_guarda_a_copia_mesmo_se_o_files_mudar_depois(self, world):
        arquivo = world.files.add("original-exemplo.pdf")
        anexar_arquivo(world, arquivo)
        world.files.found[arquivo.file_id] = world.files.found[arquivo.file_id].__class__(
            arquivo.file_id, "outro.pdf", "application/pdf", 1
        )
        assert marco(world).attachments[0].file.name == "original-exemplo.pdf"  # type: ignore[union-attr]

    def test_vai_para_a_avulsa(self, world):
        tarefa = nova_avulsa(world)
        anexar_arquivo(
            world, world.files.add("foto-exemplo.png", "image/png", 10), OwnerKind.TASK, tarefa
        )
        (anexo,) = avulsa(world, tarefa).attachments
        assert anexo.file is not None
        assert anexo.file.content_type == "image/png"

    def test_arquivo_inexistente_da_404(self, world):
        fantasma = world.files.add()
        del world.files.found[fantasma.file_id]
        with pytest.raises(NotFound):
            anexar_arquivo(world, fantasma)
        assert marco(world).attachments == ()

    @pytest.mark.parametrize(
        "tipo", ["text/html", "application/zip", "application/octet-stream", "image/svg+xml"]
    )
    def test_arquivo_que_nao_e_pdf_nem_imagem_e_recusado(self, world, tipo):
        with pytest.raises(AttachmentFileNotAllowed):
            anexar_arquivo(world, world.files.add("x.bin", tipo))
        assert marco(world).attachments == ()

    def test_dono_excluido_da_404_mesmo_com_arquivo_valido(self, world):
        tarefa = nova_avulsa(world)
        world.use_cases().delete_task.execute(
            DeleteTaskCommand(tarefa, avulsa(world, tarefa).version), NOIVO
        )
        with pytest.raises(NotFound):
            anexar_arquivo(world, world.files.add(), OwnerKind.TASK, tarefa)

    def test_o_mesmo_arquivo_pode_ser_anexado_duas_vezes(self, world):
        arquivo = world.files.add()
        anexar_arquivo(world, arquivo)
        anexar_arquivo(world, arquivo)
        assert len(marco(world).attachments) == 2


class TestRemover:
    def test_o_autor_remove_e_o_anexo_sai_da_lista(self, world):  # F-CRN-08, regra 3
        anexar_link(world)
        anexo = marco(world).attachments[0]
        depois = remover(world, anexo)
        assert (
            next(
                m for f in depois.phases for m in f.milestones if m.id == marco_id(MARCO)
            ).attachments
            == ()
        )

    def test_a_remocao_e_logica_a_linha_fica_guardada_com_quem_e_quando(self, world):
        anexar_link(world)
        anexo = marco(world).attachments[0]
        world.clock.advance(minutes=5)
        remover(world, anexo)
        guardado = world.store.attachments[anexo.id]
        assert guardado.deleted_at == world.clock.now()
        assert guardado.deleted_by == NOIVO.user_id

    def test_o_outro_perfil_recebe_403_e_nada_muda(self, world):
        anexar_link(world, ator=NOIVA)
        anexo = marco(world).attachments[0]
        with pytest.raises(Forbidden):
            remover(world, anexo, NOIVO)
        assert len(marco(world).attachments) == 1

    def test_anexo_inexistente_ou_ja_removido_da_404(self, world):
        anexar_link(world)
        anexo = marco(world).attachments[0]
        remover(world, anexo)
        with pytest.raises(NotFound):
            remover(world, anexo)
        with pytest.raises(NotFound):
            world.use_cases().remove_attachment.execute(
                RemoveAttachmentCommand(UUID(int=2**100)), NOIVO
            )

    def test_com_o_dono_excluido_o_anexo_nao_e_alcancavel_da_404(self, world):
        anexar_link(world)
        anexo = marco(world).attachments[0]
        world.use_cases().delete_milestone.execute(
            DeleteMilestoneCommand(marco_id(MARCO), marco(world).version), NOIVO
        )
        with pytest.raises(NotFound):
            remover(world, anexo)

    def test_remover_nao_muda_a_version_do_dono(self, world):
        anexar_link(world)
        anexo = marco(world).attachments[0]
        antes = marco(world)
        remover(world, anexo)
        assert marco(world).version == antes.version

    def test_remover_um_nao_mexe_nos_outros(self, world):
        for numero in range(3):
            world.clock.advance(seconds=1)
            anexar_link(world, url=f"https://exemplo.com/{numero}")
        meio = marco(world).attachments[1]
        remover(world, meio)
        assert [a.url for a in marco(world).attachments] == [
            "https://exemplo.com/0",
            "https://exemplo.com/2",
        ]


class TestLeitura:
    def test_can_remove_e_derivado_do_perfil_de_quem_le(self, world):  # F-CRN-08, regra 3
        anexar_link(world, ator=NOIVA)
        assert marco(world, ator=NOIVA).attachments[0].can_remove is True
        assert marco(world, ator=NOIVO).attachments[0].can_remove is False

    def test_o_marco_sem_anexos_vem_com_lista_vazia(self, world):
        assert all(m.attachments == () for f in ler(world).phases for m in f.milestones)
        assert all(t.attachments == () for t in ler(world).tasks)

    def test_excluir_o_marco_esconde_os_anexos_e_restaurar_os_traz_de_volta(self, world):
        uc = world.use_cases()
        arquivo = world.files.add()
        anexar_arquivo(world, arquivo)
        anexar_link(world)
        antes = marco(world).attachments
        assert len(antes) == 2
        uc.delete_milestone.execute(
            DeleteMilestoneCommand(marco_id(MARCO), marco(world).version), NOIVO
        )
        assert all(m.id != marco_id(MARCO) for f in ler(world).phases for m in f.milestones)
        assert len(world.store.attachments) == 2  # nada é apagado
        assert all(a.deleted_at is None for a in world.store.attachments.values())
        uc.restore_milestone.execute(RestoreMilestoneCommand(marco_id(MARCO)), NOIVO)
        assert marco(world).attachments == antes

    def test_excluir_a_avulsa_esconde_os_anexos_e_restaurar_os_traz_de_volta(self, world):
        uc = world.use_cases()
        tarefa = nova_avulsa(world)
        anexar_link(world, OwnerKind.TASK, tarefa)
        antes = avulsa(world, tarefa).attachments
        assert len(antes) == 1
        uc.delete_task.execute(DeleteTaskCommand(tarefa, avulsa(world, tarefa).version), NOIVO)
        assert ler(world).tasks == ()
        uc.restore_task.execute(RestoreTaskCommand(tarefa), NOIVO)
        assert avulsa(world, tarefa).attachments == antes

    def test_o_anexo_de_um_dono_nao_aparece_no_outro(self, world):
        anexar_link(world, dono=marco_id("C01"))
        assert marco(world, "C01").attachments != ()
        assert marco(world, "C02").attachments == ()
