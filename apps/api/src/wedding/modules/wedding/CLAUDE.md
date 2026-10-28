# Módulo `wedding`

> Regras gerais: leia `AGENTS.md` (raiz) e os docs abaixo. Este arquivo só traz o que é específico do módulo.

**Propósito:** é dono das Definições Base do casamento e, a partir do Bloco 1.1 (PRs seguintes), do Mapa de Escopo (categorias, status, prioridades, estimativas e referências). Não é dono da lista de convidados (`guests`), do orçamento (`budget`) nem do cronograma (`schedule`): esses módulos leem daqui, nunca copiam.

## Superfície pública
- `application/public.py`: ainda não existe; nasce quando outro módulo precisar ler uma definição.
- `domain/events.py`: nenhum evento (o *dispatcher* está adiado, `D-060`).

Nada além disso pode ser importado por outro módulo (`architecture.md` §4; contrato 5 de §9).

## Invariantes
- Há um casamento só (`D-002`): as seis variáveis (data, cidade, formato, porte, teto, cerimônia) são linhas criadas pela migration `0004`, nunca por um caso de uso. Faltar linha é banco mal migrado.
- `Definido` exige valor (`F-PLN-01`); o domínio barra e o `CHECK` do banco repete.
- Toda escrita envia a `version` que a tela viu; divergir dá `409` (`version_conflict`). É o primeiro módulo a comparar a versão do cliente, não só a do banco.
- Só mudança real vira linha de histórico, com o estado antes e depois e o **perfil** de quem mudou (guardado no registro, sem ler `identity`).
- Autoria e perfil vêm da sessão; nenhum corpo de entrada os carrega.
- Valor monetário em centavos (`ceiling`); nada do casamento é preenchido por padrão (`AGENTS.md` §2).

## Dependências permitidas
- Não importa nenhum outro módulo.
- Camadas: domínio só usa a biblioteca padrão e o `shared_kernel` (`architecture.md` §2 e §9).

## Docs
- Features: `docs/product/features/planejamento-e-caminhos.md` (`F-PLN-01` a `F-PLN-08`).
- Decisões: `D-029`, `D-066`, `D-067`.
- Arquitetura e domínio: `docs/engineering/architecture.md` §4, §5 (derivar, não duplicar) e §10 (histórico); `docs/engineering/stack.md` §4.
- Web: `apps/web/src/features/wedding/`.

## Como testar
- `make test-api` e `make lint-api` na raiz.
- Domínio: pytest e Hypothesis. Aplicação: *fakes* das portas (`tests/modules/wedding/conftest.py`). Infraestrutura e HTTP: SQLite migrado de verdade, para a semente existir.
- Contratos de import: `import-linter` no `make lint-api`.
