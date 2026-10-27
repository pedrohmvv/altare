---
name: altare-conteudo-copy
description: >-
  Tom de voz e textos em pt-BR do Altare: voz calma, direta e que fala com vocês, vocabulário do casamento brasileiro, nomes fixos dos conceitos do produto, formatos de valores, datas e notas, rótulos de botão com verbo, mensagens de erro e de estado vazio, texto neutro quanto à religião e onde guardar as strings. Use sempre que for escrever ou revisar qualquer texto que o casal lê: rótulo, botão, mensagem, estado vazio, toast, e-mail, lista exportada, nome de seção ou resposta do assistente, mesmo que o pedido seja só 'coloca um texto aí' ou 'qual nome damos pra isso'. NÃO use para decidir onde a mensagem aparece e o que ela precisa dizer (use altare-ui-ux), para cor, fonte e ícone (use altare-design) nem para o prompt do assistente (use altare-engenharia-de-ia).
---

# Conteúdo e copy do Altare

## Docs a consultar
- `docs/design/visual-direction.md` §5 (tom de voz e exemplos) e `docs/design/identity.md` §1.3 e §1.4 (sacralidade discreta, voz e microcopy).
- `docs/design/design-system.md` §9 (nomes dos componentes de domínio, como "Consenso Favorito") e §11 (formatos).
- `docs/design/identity.md` §4 (detalhes pt-BR: `R$` com espaço não separável, aspas curvas, reticências).
- `docs/product/features/<area>.md`: cada área já nomeia seus estados, rótulos e mensagens. Decisões: `D-015`, `D-023`, `D-025`, `D-026`.

## Princípios
1. **Voz:** parceiro calmo, organizado e direto. Fala com **"vocês"** ou com o perfil ativo (`Noivo`, `Noiva`). Solene sem peso, caloroso sem diminutivo. A calma é o que sustenta o princípio da marca, "o altar no centro, a festa a serviço".
2. **O que nunca aparece:** emoji, exclamação (use só se for saudação rara), trocadilho com casamento, diminutivo, tom pietista ou de panfleto, versículo, latim (existe só no nome) e jargão técnico em erro.
3. **Não confessional** (`D-026`). O tipo de cerimônia é dado do casal: escreva "local da cerimônia", "cerimônia civil", "cerimônia religiosa ou simbólica". Termos de uma tradição (paróquia, celebrante, rito) só aparecem se o próprio casal os cadastrou.
4. **Sem assinatura verbal.** `D-025` decidiu não adotar slogan na interface; não crie um.
5. **Divergência e atraso são fatos ditos com calma.** "Vocês avaliaram esta opção de forma diferente. Vale conversar antes de decidir." e "Parcela do Espaço Exemplo venceu há 3 dias", nunca "ATENÇÃO" nem culpa.
6. **Um nome por conceito, o dos docs.** Use sempre: Próximo Passo, Custo Real Comparável, Orçamento Oficial Ativo, Registrar decisão, Conversar juntos, Consenso Favorito, Destravado e Bloqueado, Em definição e Definido, Dossiê do Dia D. Sinônimo novo vira dois conceitos na cabeça do casal.
7. **Botão é verbo mais objeto:** "Registrar decisão", "Adicionar custo extra", "Promover a orçamento oficial", "Exportar lista de presentes". Nunca "OK", "Enviar" ou "Clique aqui". Botão destrutivo diz o que apaga ("Excluir fornecedor").
8. **Estado em texto completo** ("Aguardando avaliação da Noiva"), nunca só ícone ou cor.
9. **Vocabulário do Brasil:** cerimonialista do dia, buffet, espaço, cartório, sinal, parcelas, PIX, boleto, assessoria. Prefira o termo em português a anglicismo ("prazo", não "deadline"). `PIX` e `WhatsApp` ficam como são.
10. **Frase curta, uma ideia, no máximo 68 caracteres por linha de leitura corrida.** No celular, ainda menos.
11. **Exemplos e dados de teste são fictícios e rotulados** ("Espaço Exemplo", "Fornecedor Exemplo"). Texto de exemplo nunca afirma data, cidade, valor ou número de convidados do casamento (`AGENTS.md` §2).

## Formatos
| Item | Formato | Observação |
| :--- | :--- | :--- |
| Valor em resumo | `R$ 28.000` | Sem centavos quando inteiro |
| Valor em parcela e pagamento | `R$ 28.000,00` | Sempre com centavos |
| `R$` e número | Espaço não separável (U+00A0) | Evita quebra de linha entre os dois |
| Acréscimo ou diferença | `+ R$ 4.800` | Com sinal |
| Nota | `4,8 / 5` | Vírgula decimal |
| Data em lista | `26 out 2026` | |
| Data em tabela | `26/10/2026` | |
| Prazo relativo | "em 3 dias" | A data exata vai no `title` ou *tooltip* |
| Pontuação | Aspas curvas “ ” e reticências `…` | |

## Antes e depois
| Ruim | Bom |
| :--- | :--- |
| Oops! Algo deu errado [emoji] | Não conseguimos salvar agora. O que vocês digitaram continua aqui. Tentar de novo. |
| Erro 409 | Este registro foi alterado em outra tela. Recarreguem para ver a versão mais recente. |
| ATENÇÃO!!! Parcela vencida! | Parcela do Espaço Exemplo venceu há 3 dias (R$ 4.500,00). |
| Nenhum registro encontrado. | Ainda sem fornecedores nesta categoria. Que tal adicionar o primeiro contato? |
| Enviar | Registrar decisão |
| Reserve a igreja do seu sonho | Reserve o local da cerimônia |
| R$28000 ou 28.000 reais | R$ 28.000 |
| Vocês discordaram, resolvam isso | Vocês avaliaram esta opção de forma diferente. Vale conversar antes de decidir. |

## Onde guardar o texto
- Idioma único, pt-BR, **sem biblioteca de i18n**. Textos ficam em constantes por feature (por exemplo, um módulo `copy` dentro de `features/<m>`), nunca espalhados em JSX. Assim o tom se revisa em um só lugar.
- Mensagem de erro da API vem em `detail` (pt-BR) e segue esta skill; ver `altare-backend-api`.
- Exportações (CSV e lista formatada para convidados) levam texto limpo, sem ornamento nem emoji, com `R$` e vírgula decimal.

## Checklist
- [ ] Fala com "vocês" ou com o perfil, sem emoji, trocadilho nem exclamação.
- [ ] Usa o nome fixo do conceito, sem sinônimo novo.
- [ ] Botão tem verbo e objeto; destrutivo diz o que apaga.
- [ ] Valores, datas e notas no formato da tabela acima.
- [ ] Nenhum termo de tradição que o casal não tenha cadastrado.
- [ ] Texto de exemplo é fictício e rotulado.
- [ ] A string está numa constante da feature, não no JSX.

## Limites e vizinhas
- Onde a mensagem aparece e o que ela precisa dizer (estrutura em três partes): `altare-ui-ux`. Aqui se escolhem as palavras.
- Cor, fonte e ícone do estado: `altare-design`. Clareza para leitor de tela: `altare-acessibilidade`.
- O tom das respostas do assistente segue esta skill; as instruções do prompt ficam em `altare-engenharia-de-ia`.
- Decisão de nome novo de conceito: `altare-docs-vivas`.

## Em aberto
- Formato de resposta do assistente no WhatsApp (formatação, tamanho): depende da API escolhida e do `OQ-IA-001`.
