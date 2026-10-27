# Personas e Papéis (`personas.md`)

> **Status:** Aprovado na Fase 2 (Conceito) em 2026-10-24.

---

## 1. O Casal (Usuários Primários)

O sistema possui **dois perfis individuais nomeados** (Noivo e Noiva) que compartilham o mesmo casamento. Toda criação, edição, nota de avaliação ou decisão preserva a autoria (`Noivo`, `Noiva` ou `Casal`).

### 1.1. O Noivo (Idealizador / Co-planejador)
- **Papel no planejamento:** Co-líder do planejamento do casamento do marco zero até o dia D. Idealizador da ferramenta por sentir na pele a necessidade de estruturar o processo sem assessoria de preparação.
- **Preocupações principais:**
  - Ter visão sistêmica: entender o que falta decidir, o que trava o quê e se a soma das decisões cabe no orçamento.
  - Comparar propostas com racionalidade (igualando bases de comparação quando um fornecedor inclui algo que outro cobra à parte).
  - Não deixar pontas soltas com fornecedores nem perder arquivos/condições negociadas.
- **Como interage com o perfil individual:** Cadastra opções, registra suas impressões/notas individuais sobre espaços e fornecedores, estrutura categorias e acompanha próximos passos.

### 1.2. A Noiva (Co-planejadora)
- **Papel no planejamento:** Co-líder em todas as definições, pesquisas, cotações e decisões do casamento.
- **Preocupações principais:**
  - Alinhar prioridades e expectativas do casamento junto com o noivo (o que é inegociável vs. o que é dispensável).
  - Capturar e avaliar referências, fornecedores e propostas sem que a organização vire um fardo burocrático.
  - Visualizar com clareza o impacto das escolhas no orçamento e no cronograma geral, tanto quando sentam juntos no computador quanto ao consultar algo rápido pelo celular.
- **Como interage com o perfil individual:** Cadastra opções e contatos, registra sua nota/avaliação e percepções próprias em cada possibilidade (permitindo ver onde o casal concorda de imediato e onde precisa conversar antes de bater o martelo).

---

## 2. Por Que Dois Perfis Separados Importam no Produto

Em vez de uma conta genérica onde "alguém editou", a distinção entre **Noivo**, **Noiva** e **Ambos (Casal)** habilita três comportamentos centrais:

1. **Avaliação independente antes do consenso:** Ao analisar opções (ex.: 4 espaços ou 3 fotógrafos), cada um pode registrar sua percepção/favorito individualmente, destacando visualmente onde há consenso imediato e onde há divergência para conversar no fim de semana.
2. **Responsabilidade clara nos próximos passos:** Cada pendência ou follow-up com fornecedor (ex.: *"Pedir minuta do contrato para o Buffet X"*) tem um responsável claro (`Noivo`, `Noiva` ou `Juntos`).
3. **Histórico rastreável:** Saber quem adicionou uma observação ou registrou um contato evita ruído de comunicação ("achei que você tinha falado com ele").

---

## 3. Papéis Secundários / Indiretos

### 3.1. Cerimonialista do Dia (Consumidor de Saída — Sem Login na v1)
- **Contexto:** Como o casal não terá assessoria durante a preparação, contratará um(a) profissional focado(a) na execução da reta final e do Dia D.
- **Relação com o produto:** Não precisa operar o sistema no dia a dia da preparação, mas é o **destinatário do Dossiê do Dia D** gerado pelo produto na reta final (contendo todos os fornecedores fechados, contratos, contatos de emergência, escopo contratado de cada item, pagamentos pendentes no dia e observações críticas).

### 3.2. Fornecedores e Contatos (Entidades Gerenciadas, Não Usuários)
- **Contexto:** Espaços, buffets, fotógrafos, músicos, celebrante, cartório, decoração, cerimonialista, etc.
- **Relação com o produto:** Não têm acesso ao sistema. São representados internamente como registros de **Contatos** ligados a **Possibilidades**, **Contratos/Orçamento** e **Histórico de Interações**.
