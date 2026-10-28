---
name: altare-docs-vivas
description: >-
  Mantém a documentação viva do Altare: decisões D-xxx, features F-XXX-NN, open-questions, fase no
  AGENTS.md, CLAUDE.md de módulo. Use quando uma decisão for tomada ou revista, uma feature detalhada
  ou aprovada, um módulo criado, a fase avançar, ou ao ouvir 'registra', 'documenta', 'aprovado' ou
  'atualiza os docs'.
---

# Documentação viva

Os docs são a única memória entre sessões. Um doc atrasado é uma decisão perdida.

## Docs a consultar

- `AGENTS.md` §1 (fase e status), §2 regra 5 (manutenção), §3 (o que o agente decide e o que pergunta), §4 (mapa dos docs).
- `docs/product/decisions.md` (formato real, último `D-xxx`) e `docs/product/open-questions.md`.
- `docs/product/features/` (um arquivo por área, `D-029`).
- `docs/engineering/architecture.md` §4 (módulos) e §9 (contratos de import).
- `D-039` (skills de projeto e `CLAUDE.md` por módulo).

## Princípios

1. **Mesma resposta.** A decisão e os arquivos afetados mudam no mesmo turno (`AGENTS.md` §2 regra 5). Deixar "para depois" é como a fase atual fica mentindo.
2. **`decisions.md` é o registro de ADRs.** Não há pasta de ADRs (`D-039`). Entrada antiga não se reescreve: uma revisão é uma nova decisão que aponta para a anterior (`D-020` revisou `D-019`).
3. **Só o usuário aprova.** Marque `Aprovado` com data apenas depois de uma aprovação explícita. Um doc novo nasce como "Rascunho, aguardando aprovação" (`D-029`: a feature só é definitiva quando o usuário aprova).
4. **Doc estável não muda em silêncio.** Ao reescrever um, liste antes e depois: o que mudou e por quê (`AGENTS.md` §2 regra 5).
5. **Uma fonte por regra.** Regras operacionais vivem em `AGENTS.md`; o `CLAUDE.md` da raiz só aponta; skills e `CLAUDE.md` de módulo apontam para os docs sem copiá-los.
6. **Docs em português** (`AGENTS.md` §4). Datas absolutas (`2026-10-27`), nunca "hoje" ou "semana passada".

## Ao tomar uma decisão

1. **É minha ou do usuário?** Fronteiras de produto, novos módulos e mudança de fase são do usuário (`AGENTS.md` §3). Pergunte com proposta reversível.
2. **Número:** leia o último `## D-xxx` de `decisions.md` e some 1. Não reuse nem pule.
3. **Entrada:** use `references/modelo-decisao.md`. Separe por `---`.
4. **Arquivos afetados:** atualize cada um e cite o `D-xxx` onde a regra aparece (padrão `(`D-034`)`).
5. **`open-questions.md`:**
   - resolveu: mova para "Perguntas Resolvidas" como `~~**OQ-... — título**~~ $\rightarrow$ **Resolvida em `D-xxx`** (resumo)`;
   - abriu: entrada em "Perguntas Abertas" com *por que importa*, *o que falta decidir* e *o que bloqueia*;
   - atualize o "Status Global" e use o prefixo do tema (`OQ-PROD`, `OQ-ENG`, `OQ-DS`, `OQ-IA`).
6. **`AGENTS.md` §1:** atualize "Fase atual" e "Status de código/arquitetura"; ajuste "Como Retomar" se o próximo passo mudou. Doc novo entra em §4 (mapa).
7. **Conteúdo técnico** vem da skill da área, não daqui.
8. **Feche o turno** dizendo ao usuário o que mudou e em quais arquivos.

## Ao especificar uma feature

- Um arquivo por área em `docs/product/features/`, ID `F-<ÁREA>-NN`. Prefixos em uso: `PLN`, `CNV`, `CRN`, `ORC`, `POS`, `CTT`, `PRP`, `CTR`, `ENX`, `DOS`, `CCD`. Área nova: 3 letras, únicas (confira com `grep -rn "F-XXX-" docs`).
- Estrutura em `references/modelo-feature.md`.
- Escreva campos em tabela, regras numeradas, estados explícitos e **critérios de aceite verificáveis**: eles viram os testes (`altare-testes-qa`).
- Diga o que é **derivado** e não digitado (`docs/engineering/architecture.md` §5). Cadastro duplicado envelhece.
- Exemplos fictícios e rotulados ("Espaço Exemplo"); nenhum dado real ou inventado do casamento.
- Termine com "Fora desta área" e com os pontos a validar em uso, cada um reversível e com gatilho.
- Ao fechar: decisão de detalhamento (padrão `D-029` a `D-038`), marcar "Revisado em `D-xxx`" no bloco do `roadmap.md` e ajustar `scope.md` se o escopo mudou. O doc de feature **prevalece** sobre `scope.md` onde divergirem (`AGENTS.md` §4).

## Módulo novo nasce com `CLAUDE.md` (`D-039`)

- **Quando:** no mesmo commit em que a pasta `apps/api/src/wedding/modules/<módulo>/` é criada.
- **O quê:** `CLAUDE.md` curto na pasta do módulo, seguindo `references/modelo-claude-md-modulo.md` (até 40 linhas). Ele aponta para `AGENTS.md` e para os docs, e não repete regra geral.
- **O `identity` já existe** (`D-061`): o `CLAUDE.md` dele é o exemplo vivo. Não crie `CLAUDE.md` de módulo que ainda não existe.
- **Docs que cada um deve linkar:**

| Módulo | Docs de feature e referência |
| :--- | :--- |
| `identity` | Sem doc de feature. `docs/engineering/stack.md` §6, `D-020`, `D-021`, `architecture.md` §12 |
| `wedding` | `features/planejamento-e-caminhos.md` (`F-PLN`) |
| `guests` | `features/convidados-enxoval-e-dia-d.md`, parte Convidados (`F-CNV`) |
| `schedule` | `features/cronograma.md` (`F-CRN`) |
| `budget` | `features/orcamento-e-simulador.md` (`F-ORC`) |
| `possibilities` | `features/possibilidades-e-decisoes.md` (`F-POS`) e `features/propostas-por-categoria.md` (`F-PRP`) |
| `vendors` | `features/contatos.md` (`F-CTT`) |
| `contracts` | `features/contratos-e-parcelas.md` (`F-CTR`) |
| `trousseau` | `features/convidados-enxoval-e-dia-d.md`, parte Enxoval (`F-ENX`) |
| `dossier` | `features/convidados-enxoval-e-dia-d.md`, parte Dossiê (`F-DOS`) |
| `files` | Sem doc de feature. `stack.md` §3 (`FileStorage`), `architecture.md` §12 (`ATTACHMENT`), `F-CTT-07`, `F-CTR-02`, `F-PRP-04`, `F-CRN-08` |

O Centro de Comando (`features/centro-de-comando.md`, `F-CCD`) não tem módulo em `architecture.md` §4: ver "Em aberto".

## Checklist de fim de turno

- [ ] Toda decisão do turno está em `decisions.md`, com o próximo número.
- [ ] Os arquivos afetados citam o `D-xxx` e foram atualizados na mesma resposta.
- [ ] `open-questions.md` está limpo e acionável, com o "Status Global" correto.
- [ ] `AGENTS.md` §1 reflete a fase e o próximo passo; §4 lista docs novos.
- [ ] Nada estável foi reescrito sem dizer ao usuário o que mudou.
- [ ] Aprovações têm data e vieram do usuário.

## Bom / ruim

Ruim: corrigir uma regra antiga editando o texto da `D-034` em `decisions.md`. Apaga o histórico do porquê.

Bom: nova `D-0xx` com "Ajustes em arquivos aprovados" apontando para `D-034`, e o doc da área atualizado com a citação.

Ruim: "ficou combinado que vai assim" sem registro. Na próxima sessão ninguém sabe.

Bom: entrada com Decisão, Razão e O que ficou rejeitado, escrita no mesmo turno.

## Limites e vizinhas

- Conteúdo técnico da decisão: skill da área (`altare-arquitetura`, `altare-banco-de-dados`, `altare-backend-api`, `altare-engenharia-de-ia` e as demais).
- Se uma ideia merece entrar no escopo: `altare-produto`.
- Commit e PR das mudanças de docs: `altare-commit` e `altare-pull-request`.
- Redação do texto voltado ao casal: `altare-conteudo-copy`.

## Em aberto

- **Escopo do `CLAUDE.md` no web:** `D-039` fala em "cada módulo da arquitetura". Esta skill cria o arquivo só no módulo do backend e pede que ele cite a pasta `features/<módulo>` do web quando existir. Se o usuário quiser um arquivo também no web, é decisão nova.
- **Centro de Comando e exportação de dados** (`F-CCD`) são consultas sobre outras áreas (`architecture.md` §13, Nível 4) e não têm módulo próprio em §4. Decidir onde moram é pendência de arquitetura, para `altare-arquitetura`.
