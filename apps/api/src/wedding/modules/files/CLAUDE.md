# Módulo `files`

> Regras gerais: leia `AGENTS.md` (raiz) e os docs abaixo. Este arquivo só traz o que é específico do módulo.

**Propósito:** é dono do arquivo enviado (`FileAsset`) e das regras de upload e download. Não é dono do vínculo do arquivo a contatos, propostas, contratos e parcelas (`ATTACHMENT`): ele nasce no bloco que anexa.

## Superfície pública
- `application/public.py`: `FileAssetDto`, o que outro módulo guarda para apontar para um arquivo. O `GetFileInfo` (dados sem o conteúdo) é ligado a quem precisa pelo `bootstrap`, que é o único que conhece os dois módulos; o `wedding` o usa para conferir que uma referência é imagem (`D-069`).
- `domain/events.py`: nenhum evento.

Nada além disso pode ser importado por outro módulo (`architecture.md` §4; contrato 5 de §9).

## Invariantes
- O tipo vem da **assinatura real** do arquivo (PDF, JPG, PNG ou WebP), nunca da extensão nem do tipo que o cliente informou.
- Nenhum arquivo passa de 20 MB, e nenhum é vazio.
- O nome que a pessoa deu ao arquivo só serve para exibir e sugerir no download: nunca vira caminho em disco. O disco guarda pelo SHA-256 do conteúdo.
- O mesmo conteúdo fica uma vez em disco, mas cada envio tem o seu registro, com o nome original e quem enviou.
- Só uma sessão autenticada envia ou lê (`D-063`).

## Dependências permitidas
- Não importa nenhum outro módulo.
- Camadas: domínio só usa a biblioteca padrão e o `shared_kernel` (`architecture.md` §2 e §9).
- O `LocalFileStorage` mora em `platform/storage`; este módulo só conhece a porta `FileStorage`.

## Docs
- Features: `F-PLN-06`, `F-CTT-07`, `F-CRN-08`, `F-PRP-04` e `F-CTR-02` (quem anexa); este módulo só guarda o arquivo.
- Decisões: `D-059`, `D-063`.
- Arquitetura e domínio: `docs/engineering/architecture.md` §12 (`ATTACHMENT`); `docs/engineering/stack.md` §3 (`FileStorage` e validação de upload).

## Como testar
- `make test-api` e `make lint-api` na raiz.
- Domínio: pytest puro e Hypothesis. Aplicação: fakes das portas. Infraestrutura: SQLite e disco temporários (`architecture.md` §9).
- Contratos de import: `import-linter` no `make lint-api`.
