# Módulo `guests`

> Regras gerais: leia `AGENTS.md` (raiz) e os docs abaixo. Este arquivo só traz o que é específico do módulo.

**Propósito:** é dono da lista nominal de convidados: núcleos familiares, pessoas, acompanhante (+1), status com histórico, contatos e endereço. Não é dono do orçamento (`budget`), do Dossiê (`dossier`) nem do Porte das Definições Base (`wedding`): esses módulos leem a contagem daqui, nunca a copiam.

## Superfície pública
- `application/public.py`: ainda não existe; nasce no PR 2 com `GetGuestHeadcount` (`D-073`).
- `domain/events.py`: nenhum evento (o *dispatcher* está adiado, `D-060`).

Nada além disso pode ser importado por outro módulo (`architecture.md` §4; contrato 5 de §9).

## Invariantes
- Há um casamento só (`D-002`). Nome do núcleo único entre os vivos, sem diferenciar caixa nem espaços (`name_key`).
- Núcleo nasce com a 1ª pessoa e nunca fica sem pessoas vivas; a escrita que muda a composição sobe `members_revision`, para duas saídas simultâneas se conflitarem (`D-072`).
- Acompanhante: mesmo núcleo do titular, no máximo um por titular, e não leva outro; só ele pode ficar sem nome (`F-CNV-02`).
- Status livre (qualquer um para qualquer outro); o motivo só existe com `Não irá`; cada mudança real grava uma linha de histórico com o perfil (`F-CNV-04`).
- A idade só vale para criança e nunca muda a faixa sozinha (`F-CNV-03`).
- **Dado pessoal de terceiros** (nome, telefone, e-mail, endereço, restrição alimentar, motivo): nunca em log, nunca em URL, só nas respostas autenticadas com `no-store` (`altare-seguranca-privacidade`).
- Autoria e perfil vêm da sessão; os dois perfis editam tudo; toda escrita envia a `version` que a tela viu.

## Dependências permitidas
- Não importa nenhum outro módulo.
- Camadas: domínio só usa a biblioteca padrão e o `shared_kernel` (`architecture.md` §2 e §9).

## Docs
- Features: `docs/product/features/convidados-enxoval-e-dia-d.md`, parte Convidados (`F-CNV-01` a `F-CNV-08`).
- Decisões: `D-030`, `D-071`, `D-072`.
- Persistência: migration `0007` (`guest_households`, `guests`, `guest_status_changes`).
- Arquitetura e domínio: `docs/engineering/architecture.md` §5 (derivar, não duplicar) e §10 (histórico); `docs/engineering/stack.md` §4.
- Web: `apps/web/src/features/guests/`.

## Em aberto
- Leitura pelo assistente (Nível 5): passa por caso de uso e **sem contatos por padrão**; nada daqui vai a LLM, WhatsApp ou hospedagem sem decisão registrada.
- Purga definitiva de convidados e retenção: adiadas (só viram obrigação se o Altare abrir a outros casais).

## Como testar
- `make test-api` e `make lint-api` na raiz.
- Domínio: pytest e Hypothesis. Aplicação: *fakes* das portas (`tests/modules/guests/conftest.py`).
- Contratos de import: `import-linter` no `make lint-api`.
