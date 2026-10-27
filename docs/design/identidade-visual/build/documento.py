"""Páginas do guia de identidade visual do Altare (HTML 1280 x 720 por página; vira PDF pelo Chrome)."""
import componentes as comp
from componentes import ICONES, get
from lib import C, D, VERSAO, VERSOES, contrast, dec, esc, fmt, font_face, grade, marca_centro, trunc1

PAGES = []      # {slug, sec, title, body, cls}
SECOES = []     # (número, nome, página inicial)


def fig(name, w=None, h=None, cls="fig", crop=None):
    """Insere um componente. `crop` (x, y, w, h) mostra só parte da tela, para as telas de exemplo lerem maiores."""
    c = get(name)
    vb = crop or (0, 0, c["w"], c["h"])
    style = (f"width:{w}px;" if w else "") + (f"height:{h}px;" if h else "")
    return (f'<svg class="{cls}" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}" style="{style}" role="img" '
            f'aria-label="{esc(c["desc"])}">{c["body"]}</svg>')


def svg_inline(w, h, body, style=""):
    return f'<svg viewBox="0 0 {w} {h}" style="{style}">{body}</svg>'


def page(slug, sec, title, body, cls=""):
    PAGES.append({"slug": slug, "sec": sec, "title": title, "body": body, "cls": cls})


def secao(num, nome):
    SECOES.append((num, nome, len(PAGES) + 1))
    return f"{num:02d} · {nome}"


def lista(itens, cls="list"):
    return f'<ul class="{cls}">' + "".join(f"<li>{i}</li>" for i in itens) + "</ul>"


def notas(itens):
    return '<ol class="notes">' + "".join(f"<li><b>{k}</b><span>{v}</span></li>" for k, v in itens) + "</ol>"


# ================================================================ páginas

def capa():
    body = f'''
<div class="cover-text">
  <p class="kick light">Guia da marca</p>
  <h1>Identidade <i>visual</i></h1>
  <p class="lead">O que o Altare é, como fala e como a marca, as cores, a tipografia e os ornamentos devem ser usados.</p>
  <p class="ver">{VERSAO} · aprovada</p>
</div>
<div class="cover-arch">{svg_inline(400, 563, comp.ornamento("arco-duplo", 0, 0, 400, 563, cor=C["primary-ink"], opacidade=0.35)
                                    + marca_centro("vertical", "marfim", 200, 300, 112), "width:400px;height:563px")}</div>'''
    page("capa", None, "Capa", body, "cover")


def sumario():
    page("sumario", None, "Sumário", "__SUMARIO__")


def sobre():
    s = secao(1, "Sobre o Altare")
    body = f'''
<div class="cols3">
  <div><h3>Propósito</h3><p class="big">Organizar a festa sem perder de vista <i>para quê</i> ela existe.</p>
    <p>O Altare é o planejador de casamento do casal: um caderno autoral com a precisão de uma boa ferramenta de decisão.</p>
    <p class="small">Uso pessoal e exclusivo do Noivo e da Noiva. Expansão para outros casais é hipótese futura, não premissa.</p></div>
  <div><h3>O que faz</h3>{lista([
      "Compara propostas pelo <b>custo total comparável</b>, com avaliação dos dois.",
      "Simula orçamentos completos em paralelo e promove um a oficial.",
      "Mostra o que está <b>destravado</b> e o que depende de outra decisão.",
      "Guarda contatos, PDFs e o próximo passo de cada fornecedor, com WhatsApp em 1 toque.",
      "Organiza convidados, enxoval e o <b>Dossiê do Dia&nbsp;D</b>."], "list tight")}</div>
  <div><h3>Para quem</h3><p>O casal, cada um com login próprio. A autoria vem sempre da sessão.</p>
    <div class="ex"><span class="tag">Visão do Casal</span><b>Juntos, no computador</b><span>Planejamento profundo, lado a lado.</span></div>
    <div class="ex"><span class="tag">Minha visão</span><b>Cada um, no celular</b><span>Pendências, avaliações e próximos passos de quem está logado.</span></div></div>
</div>'''
    page("sobre", s, "Um caderno de casamento com <i>o altar no centro</i>", body)

    wm = svg_inline(560, 160, marca_centro("wordmark", "oliva", 280, 80, 96), "width:480px")
    rows = [("Origem", "Latim e italiano <i>altare</i>, “altar”"), ("Pronúncia", "al-TÁ-re (em português, <i>al-TA-ri</i>)"),
            ("Grafia", "Altare, com inicial maiúscula. ALTARE só na assinatura formal. Nunca altare, AltarE ou com acento"),
            ("Gênero", "Masculino: “o Altare”, “no Altare”"), ("Escolha", "Do Noivo, autor do projeto (D-023)")]
    trs = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
    body = f'''
<div class="cols2 wide-left">
  <div><div class="name-stage">{wm}</div><table class="kv">{trs}</table></div>
  <div><h3>Por que este nome</h3>
    <p>O compromisso é o centro; a festa é o meio. O produto organiza a festa, e o nome lembra <b>para quê</b>: tudo se ordena ao altar.</p>
    <p>É latim sem ser “matrimonium”: nomeia o lugar, não a instituição. Sóbrio, belo e fácil de dizer.</p>
    <p class="small">Não confessional: o altar de “subir ao altar”, seja a cerimônia religiosa de qualquer tradição, civil ou simbólica. O tipo de cerimônia é escolha do casal.</p>
    <div class="box warn"><b>Risco assumido</b><p class="small">Existe a assessoria Altare Cerimonial (Juiz de Fora, MG) e os domínios .com, .app, .com.br, .co e .io já estão registrados. Para uso pessoal, aceito. Antes de qualquer uso público, reavaliar o nome e buscar no INPI.</p></div></div>
</div>'''
    page("nome", s, "Altare, <i>o nome</i>", body)

    regras = [("Números são sagrados", "Sempre mono tabular, alinhados e sem enfeite."),
              ("Nomes são protagonistas", "Espaços, fornecedores e cenários em serifa."),
              ("Cor significa algo", "Nenhuma cor decorativa. Terracota nunca é “só bonita”."),
              ("Sem ansiedade", "Divergência e atenção são convites ao diálogo, nunca erro vermelho."),
              ("Sacralidade discreta", "O sagrado aparece pela proporção, pelo silêncio e pela luz, nunca por símbolos.")]
    cards = "".join(f'<div class="rule-card"><span class="n">{i + 1}</span><h4>{k}</h4><p>{v}</p></div>' for i, (k, v) in enumerate(regras))
    eixos = [("Superfície", "Papel Areia, Marfim, hairlines Amêndoa", "Grade rígida, alinhamento tabular"),
             ("Tipografia", "Serifa editorial nos protagonistas", "Mono tabular em todo número"),
             ("Cor", "Oliva, sálvia e terracota naturais", "Semântica fixa: consenso × atenção"),
             ("Voz", "“Vocês”, acolhedora, solene sem peso", "Direta, acionável, sem enrolação")]
    trs = "".join(f"<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>" for a, b, c in eixos)
    body = f'''
<p class="lead-in">Um caderno autoral de casamento com a precisão de uma boa ferramenta de decisão, em tom de sacralidade discreta.</p>
<table class="axes"><thead><tr><th></th><th>Calor · caderno</th><th>Rigor · ferramenta</th></tr></thead><tbody>{trs}</tbody></table>
<h3 class="mt">Cinco regras de ouro</h3><div class="cols5">{cards}</div>'''
    page("principio", s, "O altar no centro. <i>A festa a serviço.</i>", body)


def tom():
    s = secao(2, "Personalidade e tom de voz")
    body = f'''
<div class="cols2">
  <div class="box yes"><h3>Somos</h3>{lista([
      "Um caderno do casal: calmo, organizado e direto.",
      "Solenes sem peso, calorosos sem diminutivo.",
      "Precisos com dinheiro, prazo e dependência.",
      "Discretos na fé: o essencial no centro, sem pregar."], "list tight")}</div>
  <div class="box no"><h3>Não somos</h3>{lista([
      "Revista de noiva: corações, laços, dourado e confete.",
      "Planilha fria ou sistema de gestão corporativo.",
      "Aplicativo ansioso: alertas vermelhos, contagem regressiva, urgência.",
      "Devocional ou “igrejinha”: versículos, cruz, pomba, vitral."], "list tight")}</div>
</div>
<h3 class="mt">Princípios de escrita</h3>
<div class="cols4">
  <div class="pr"><b>1 · Falar com “vocês”</b><p>Ou com o perfil ativo, em Minha visão. Nunca “o usuário”.</p></div>
  <div class="pr"><b>2 · Uma ação por frase</b><p>Verbo no início, prazo no fim: “Confirmar a visita até sexta”.</p></div>
  <div class="pr"><b>3 · Convite, não alarme</b><p>Divergência vira conversa; custo extra vira fato com número.</p></div>
  <div class="pr"><b>4 · Sem trocadilho nem emoji</b><p>Sem piadas de casamento, sem exclamações em série.</p></div>
</div>'''
    page("personalidade", s, "O que somos e o que <i>não somos</i>", body)

    rows = [("Bem-vindos ao Altare.", "Olá, casal 20! Bora casar?"),
            ("Próximo passo de vocês: confirmar a visita até sexta.", "ATENÇÃO! Tarefa atrasada!!!"),
            ("Vocês avaliaram de forma diferente. Vale conversar antes de decidir.", "Conflito detectado entre os usuários."),
            ("Esta proposta tem R$ 1.200,00 em custos extras.", "Cuidado: preço escondido!"),
            ("Nada por aqui ainda. Que tal começar pelo primeiro contato?", "Nenhum registro encontrado."),
            ("Decisão registrada.", "Uhuul! Vocês arrasaram, pombinhos!")]
    trs = "".join(f"<tr><td class='y'>{a}</td><td class='n'>{b}</td></tr>" for a, b in rows)
    body = f'''
<div class="cols2 wide-left">
  <div><table class="say"><thead><tr><th>Diga assim</th><th>Não assim</th></tr></thead><tbody>{trs}</tbody></table></div>
  <div><h3>Assinatura <span class="pill">opcional</span></h3>
    <div class="quote">“Primeiro o altar. <i>Depois, todo o resto.</i>”</div>
    <p class="small">Candidatas para login e documentos formais. Nenhuma é obrigatória: o Altare pode ficar sem assinatura.</p>
    <div class="use">1 · “Tudo em ordem, o essencial no centro.”</div>
    <div class="use">2 · “Primeiro o altar. Depois, todo o resto.”</div>
    <div class="use">3 · “A festa em ordem, para o que importa.”</div></div>
</div>'''
    page("tom-de-voz", s, "Diga assim, <i>não assim</i>", body)

    sim = ["Proporção calma e espaço generoso", "Serifa clássica e versal espaçada, em uso raro", "Hairlines e o motivo do arco",
           "Luz suave: areia, marfim, sálvia", "Silêncio: sem sons, sem animação festiva", "Latim somente no nome"]
    nao = ["Cruz, crucifixo, pomba, cálice, hóstia, vitral, auréola", "Alianças entrelaçadas, corações, laços, flores coloridas",
           "Dourado saturado, brilhos, confete", "Frases devocionais, versículos ou latim decorativo na interface",
           "Tom pietista ou de panfleto", "Ícones religiosos como decoração"]
    body = f'''
<p class="lead-in">Sacralidade e beleza como atmosfera, sem cara de “igrejinha” nem de devocional. O sagrado está no que o casal vive, não no que a tela enfeita.</p>
<div class="cols2">
  <div class="box yes"><h3>Como o sagrado aparece</h3>{lista(sim, "list tight")}</div>
  <div class="box no"><h3>Como o sagrado não aparece</h3>{lista(nao, "list tight")}</div>
</div>
<p class="small mt-s">O único ícone com coração (heart-handshake) fica restrito ao selo de consenso. Nenhum símbolo de uma tradição religiosa específica: a marca serve a qualquer cerimônia.</p>'''
    page("sacralidade", s, "Sacralidade <i>discreta</i>", body)


def marca_pgs():
    s = secao(3, "A marca")
    page("marca-conceito", s, "A letra sobre <i>a mesa</i>", f'<div class="figwrap">{fig("conceito", w=1152)}</div>')
    page("marca-anatomia", s, "<i>Anatomia</i> da marca", f'<div class="figwrap">{fig("anatomia", w=1152)}</div>')
    page("marca-grade", s, "Construção na <i>grade</i>", f'<div class="figwrap">{fig("grade", h=520)}</div>')
    page("marca-lockups", s, "Quatro arranjos, <i>nenhum lado a lado</i>", f'<div class="figwrap">{fig("lockups", w=1152)}</div>')
    page("versao-pequena", s, "Correção óptica: a <i>versão pequena</i>", f'<div class="figwrap">{fig("versao-pequena", w=1152)}</div>')


def versoes():
    s = secao(4, "Versões de cor")
    page("versoes-de-cor", s, "As seis <i>versões de cor</i>", f'<div class="figwrap">{fig("versoes-de-cor", h=520)}</div>')
    trs = ""
    for v in VERSOES:
        r = contrast(v["cor"], v["fundo"])
        thumb = svg_inline(120, 52, marca_centro("wordmark", v["sufixo"], 60, 26, 24), "width:120px;height:52px")
        trs += (f'<tr><td><span class="thumb" style="background:{v["fundo"]}">{thumb}</span></td><td><b>{esc(v["nome"])}</b><br>'
                f'<span class="file">altare-*-{v["sufixo"]}.svg</span></td><td>{v["fundo_nome"]}</td><td class="num">{fmt(r)}</td>'
                f'<td>{esc(v["regra"])}</td></tr>')
    body = (f'<table class="rules"><thead><tr><th></th><th>Versão</th><th>Fundo</th><th>Contraste</th><th>Quando usar</th></tr></thead>'
            f'<tbody>{trs}</tbody></table><p class="small">Contraste WCAG 2.2 entre a cor da marca e o fundo de uso. A WCAG não exige contraste para '
            f'logotipos; adotamos 4,5 : 1 como mínimo próprio. Terracota nunca entra na marca.</p>')
    page("versoes-regras", s, "Qual versão, <i>em qual fundo</i>", body)


def respiro():
    s = secao(5, "Respiro e tamanho mínimo")
    page("area-de-respiro", s, "Área de <i>respiro</i>", f'<div class="figwrap">{fig("area-de-respiro", w=1152)}</div>')
    page("tamanho-minimo", s, "Tamanho <i>mínimo</i>", f'<div class="figwrap">{fig("tamanho-minimo", w=1152)}</div>')


def incorretos():
    s = secao(6, "Usos incorretos")
    names = [c["name"] for c in comp.REG if c["folder"] == "usos-incorretos"]
    for i, chunk in enumerate((names[:6], names[6:])):
        cells = "".join(f"<div>{fig(n, w=340)}</div>" for n in chunk)
        page(f"usos-incorretos-{i + 1}", s, "O que <i>não fazer</i>" + (" (continuação)" if i else ""), f'<div class="grid3">{cells}</div>')


def _matriz(P, fgs, bgs):
    head = "<tr><th>texto ↓ / fundo →</th>" + "".join(f"<th>{n}</th>" for _, n in bgs) + "</tr>"
    rows = ""
    for f, fn in fgs:
        rows += f"<tr><th class='rh'>{fn}</th>"
        for b_, _ in bgs:
            if P[f] == P[b_]:
                rows += "<td class='same'>—</td>"
                continue
            r = contrast(P[f], P[b_])
            lab = P["ink"] if contrast(P["ink"], P[b_]) > 4.5 else P["canvas"]
            rows += (f"<td style='background:{P[b_]}'><b style='color:{P[f]}'>Aa</b>"
                     f"<span class='gr' style='color:{lab}'>{dec(trunc1(r))} · {grade(r)}</span></td>")
        rows += "</tr>"
    return f'<table class="cmat">{head}{rows}</table>'


FGS = [("ink", "ink"), ("ink-muted", "ink-muted"), ("ink-subtle", "ink-subtle"), ("primary", "primary"), ("accent", "accent"),
       ("accent-ink", "accent-ink"), ("consensus-ink", "consensus-ink"), ("attention-ink", "attention-ink"), ("primary-ink", "primary-ink")]
BGS = [("canvas", "canvas"), ("surface", "surface"), ("surface-muted", "s-muted"), ("surface-sunken", "s-sunken"),
       ("consensus-bg", "consensus"), ("attention-bg", "attention"), ("primary", "primary")]


def cores():
    s = secao(7, "Cores")
    page("paleta-clara", s, "Paleta do <i>tema claro</i>", f'<div class="figwrap">{fig("paleta-clara", w=1152)}</div>')
    page("paleta-escura", s, "Paleta do <i>tema escuro</i>, Noite Oliva", f'<div class="figwrap">{fig("paleta-escura", w=1152)}</div>')
    nota = ('<p class="small">Fórmula de luminância relativa da WCAG 2.2. AAA ≥ 7 : 1 · AA ≥ 4,5 : 1 (texto normal) · AA grande ≥ 3 : 1 '
            '(texto a partir de 24 px, ou 18,66 px em negrito, e componentes gráficos) · falha &lt; 3 : 1.</p>')
    page("contraste-claro", s, "Contraste WCAG · <i>claro</i>", _matriz(C, FGS, BGS) + nota)
    page("contraste-escuro", s, "Contraste WCAG · <i>escuro</i>", _matriz(D, FGS, BGS) + nota, "dark")

    pares = [("accent", "canvas", "Terracota sobre Papel Areia"), ("accent", "surface", "Terracota sobre Marfim"),
             ("accent-ink", "canvas", "Terracota Escura sobre Papel Areia"), ("ink-subtle", "surface", "Musgo Claro sobre Marfim"),
             ("ink-subtle", "surface-muted", "Musgo Claro sobre Champagne"), ("border", "surface", "Amêndoa sobre Marfim"),
             ("border-strong", "canvas", "Amêndoa Forte sobre Papel Areia")]
    li = ""
    for f, b_, nome in pares:
        r = contrast(C[f], C[b_])
        meta = 3 if f.startswith("border") else 4.5
        ok = r >= meta
        li += f"<li class='{'ok' if ok else 'ko'}'><b>{nome}</b>: {fmt(r)} · {'passa' if ok else 'não passa'} ({'controle' if meta == 3 else 'texto'} ≥ {dec(meta)})</li>"
    body = f'''
<div class="cols2">
  <div><h3>Proporção de uso · 60-30-10</h3>
    <div class="prop"><span style="flex:60;background:{C["canvas"]};color:{C["ink"]};border:1px solid {C["border"]}">Superfícies 60%</span>
      <span style="flex:30;background:{C["primary"]};color:{C["primary-ink"]}">Estrutura e texto 30%</span>
      <span style="flex:7;background:{C["consensus-bg"]};color:{C["consensus-ink"]}">7%</span>
      <span style="flex:3;background:{C["accent"]};color:#fff"></span></div>
    <p>Muito Papel Areia e Marfim, o oliva e o carvão como estrutura, e a semântica em pequenas doses. <b>Terracota ocupa no máximo 5% de qualquer tela</b>: se passar disso, a tela está gritando.</p>
    {lista(["Cor nunca é o único sinal: consenso, divergência e atenção sempre com ícone + texto.",
            "Texto terracota pequeno usa Terracota Escura (accent-ink).", "Amêndoa é só divisória; controles usam Amêndoa Forte.",
            "Musgo Claro (placeholder) só sobre Marfim."], "list tight small2")}</div>
  <div><h3>Pares que pedem cuidado · claro</h3><ul class="list tight small2 pairs">{li}</ul>
    <p class="small">Calculado automaticamente a partir de tokens.json. Se um par mudar de faixa, este guia muda junto.</p></div>
</div>'''
    page("proporcao-e-limites", s, "Proporção e <i>limites</i>", body)


def tipografia():
    s = secao(8, "Tipografia")
    page("familias", s, "Três famílias, <i>três papéis</i>", f'<div class="figwrap">{fig("familias", w=1152)}</div>')
    page("hierarquia", s, "A <i>escala</i> tipográfica", f'<div class="figwrap">{fig("hierarquia", h=530)}</div>')
    page("especime", s, "<i>Especímen</i>", f'<div class="figwrap">{fig("especime", h=530)}</div>')
    page("numeros", s, "Números <i>em pt-BR</i>", f'<div class="figwrap">{fig("numeros", w=1152)}</div>')
    body = f'''<div class="cols2">
  <div><h3>Texto corrido</h3>{lista([
      "Corpo de 16 px (mínimo 16 px em campos no mobile, evita o zoom do iOS), entrelinha 1,5.",
      "Linhas de até 68 caracteres. Alinhado à esquerda, nunca justificado.",
      "<b>Nunca serifa</b> em botões, rótulos de formulário e cabeçalhos de tabela.",
      "Versal só no eyebrow (12 px, +0,08 em) e na assinatura formal.",
      "Itálico da Newsreader só em tags editoriais e ênfases raras."], "list tight")}</div>
  <div><h3>Detalhes pt-BR e carregamento</h3>{lista([
      "Vírgula decimal; R$ + espaço não separável (U+00A0).",
      "Aspas curvas “ ”, reticências …, travessão — com espaços.",
      "Woff2 self-hosted (Fontsource), latin + latin-ext, font-display: swap.",
      "Preload de Newsreader 400 e Plus Jakarta Sans 400.",
      "Fallbacks Georgia / system-ui / ui-monospace com size-adjust."], "list tight")}</div>
</div>'''
    page("regras-de-texto", s, "Regras de <i>texto</i>", body)


def elementos():
    s = secao(9, "Elementos de apoio")
    page("arco", s, "O arco de <i>volta perfeita</i>", f'<div class="figwrap">{fig("arco", w=1152)}</div>')
    page("ramo", s, "O ramo de <i>oliveira</i>", f'<div class="figwrap">{fig("ramo", w=1152)}</div>')
    page("superficies", s, "Papel, cantos, linhas e <i>profundidade</i>", f'<div class="figwrap">{fig("superficies", h=530)}</div>')
    page("iconografia", s, "<i>Ícones</i> com significado fixo", f'<div class="figwrap">{fig("iconografia", w=1152)}</div>')
    page("interface", s, "A marca na <i>interface</i>", f'<div class="figwrap">{fig("interface", h=530)}</div>')
    page("estados-e-movimento", s, "Estados e <i>movimento</i>", f'<div class="figwrap">{fig("estados-e-movimento", w=1152)}</div>')


def aplicacoes():
    s = secao(10, "Aplicações")

    def side(slug, title, name, itens, h=520, crop=None):
        page(slug, s, title, f'<div class="app-side"><div class="figwrap">{fig(name, h=h, crop=crop)}</div>{notas(itens)}</div>')

    page("favicon-e-app", s, "Favicon e <i>ícone do app</i>", f'<div class="figwrap">{fig("favicon-e-icone-de-app", w=1100)}</div>')
    side("login", "Tela de <i>login</i>", "tela-de-login", [
        ("Lockup vertical", "O arranjo de entrada: login, splash e capa do Dossiê."),
        ("Arco duplo e ramo", "Musgo a 70%, nunca atrás do formulário."),
        ("Cartão Marfim", "Campos com Amêndoa Forte e foco em anel duplo."),
        ("Saudação", "“Bem-vindos ao Altare.” Sem cadastro público.")], h=500)
    side("visao-geral", "Visão Geral no <i>desktop</i>", "visao-geral", [
        ("Wordmark na barra lateral", "Símbolo só no mobile."),
        ("Lente", "Visão do Casal ou Minha visão, no topo."),
        ("Em definição", "Data, cidade, convidados e estilo nunca são inventados."),
        ("Cartões planos", "Hairline, raio 10, nome em serifa.")], h=500)
    page("mobile", s, "No <i>celular</i>", f'<div class="figwrap">{fig("mobile", h=530)}</div>')
    side("comparador", "Comparar <i>propostas</i>", "comparador", [
        ("Custo comparável", "O número que decide, em mono 24 px."),
        ("Custos extras", "Terracota com ícone e sinal +."),
        ("Avaliação dupla", "Noivo e Noiva lado a lado, visíveis aos dois."),
        ("Situação", "Consenso em Sálvia, conversa em Argila.")], h=500)
    side("tema-escuro", "Tema escuro <i>Noite Oliva</i>", "tema-escuro", [
        ("Sálvia Clara", "A marca vira Sálvia sobre Noite."),
        ("Sem textura", "O papel some no escuro."),
        ("Sem sombra", "Profundidade por degraus de surface."),
        ("Mesma semântica", "Consenso e atenção mantêm significado.")], h=500)
    side("dossie", "Dossiê do Dia D · <i>impressão</i>", "dossie-do-dia-d", [
        ("Papel branco, sem fundo", "Economia de tinta e leitura em preto e branco."),
        ("Assinatura formal + arcada", "ALTARE em versal, hairline e o título do documento."),
        ("Serifa nos títulos, mono nos dados", "Horários, telefones e valores tabulares."),
        ("Bordas Amêndoa Forte", "#8F846F garante leitura em fotocópia."),
        ("Uma seção por página", "Quebra de página por fornecedor."),
        ("Campos vazios explícitos", "[a definir] até o casal preencher. Nada é inventado.")], h=510, crop=(110, 0, 726, 1000))


PENDENCIAS = [
    "Identidade aprovada pelo usuário em 27/10/2026 (D-025), sem assinatura verbal e com heart-handshake só no selo de consenso.",
    "Mostrar o guia à Noiva.",
    "Refinar à mão o kerning do wordmark e o hinting do favicon a 16 px.",
    "Testar a impressão real do Dossiê em preto e branco.",
    "Antes de qualquer uso público: reavaliar o nome e buscar no INPI.",
]


def arquivos():
    s = secao(11, "Arquivos e pendências")
    body = f'''<div class="cols2">
  <div><h3>Arquivos entregues</h3><ul class="list tight files">
    <li><code>tokens.json</code> fonte única de cores, geometria, mínimos e escala tipográfica.</li>
    <li><code>fonte/</code> os 30 SVGs-mestre (5 peças × 6 cores) e os 6 ornamentos.</li>
    <li><code>componentes/logo/</code> mestres em SVG e PNG (256, 1024, 2048 px).</li>
    <li><code>componentes/favicon/</code> e <code>app-icon/</code> PNG de 16 a 1024 px, SVG e favicon.ico.</li>
    <li><code>componentes/</code> cores, tipografia, construção, usos incorretos, elementos, aplicações.</li>
    <li><code>componentes/paginas/</code> cada página deste guia em PNG; <code>INDEX.md</code> lista tudo.</li>
    <li><code>build/</code> scripts: <code>uv run build.py</code> (e <code>--marca</code> para regerar os mestres).</li></ul>
    <h3 class="mt">Onde mora cada regra</h3><p class="small">Regras escritas: <code>docs/design/identity.md</code>. Implementação: <code>docs/design/design-system.md</code>. Valores: <code>tokens.json</code>. Decisões: <code>docs/product/decisions.md</code>.</p></div>
  <div><h3>Status e próximos cuidados</h3><ul class="list tight small2">{"".join(f"<li>{p}</li>" for p in PENDENCIAS)}</ul></div>
</div>'''
    page("arquivos-e-pendencias", s, "Arquivos e <i>pendências</i>", body)


# ================================================================ montagem

def css():
    v = ";".join(f"--{k}:{h}" for k, h in C.items())
    dv = ";".join(f"--{k}:{h}" for k, h in D.items())
    return """
__FONT__
:root{__VARS__}
.dark{__DVARS__}
*{box-sizing:border-box;margin:0;padding:0}
html{background:#D9D2C2}body{font-family:"Plus Jakarta Sans",system-ui,sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased}
.page{width:1280px;height:720px;margin:24px auto;background:var(--canvas);position:relative;overflow:hidden;padding:56px 64px 0;box-shadow:0 6px 24px rgba(35,42,34,.16)}
.rule{position:absolute;left:64px;right:64px;top:32px;height:1px;background:var(--border)}
.mark{position:absolute;right:64px;top:14px;width:26px;height:24px;background:var(--canvas);padding-left:8px}
.kick{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted)}
h2{font-family:Newsreader,Georgia,serif;font-size:40px;font-weight:500;letter-spacing:-.01em;color:var(--ink);margin:6px 0 22px;line-height:1.1}
h2 i,h1 i,.big i,.quote i{font-style:italic;font-weight:400;color:var(--primary)}
h3{font-size:17px;font-weight:700;margin-bottom:10px}h4{font-family:Newsreader,Georgia,serif;font-size:19px;font-weight:500;margin:8px 0 4px}
p{font-size:15.5px;line-height:1.5;margin-bottom:10px}.small{font-size:13.5px;color:var(--ink-muted);line-height:1.45}
.big{font-family:Newsreader,Georgia,serif;font-size:26px;line-height:1.25;font-weight:500;color:var(--ink)}
.lead-in{font-family:Newsreader,Georgia,serif;font-size:21px;line-height:1.35;color:var(--ink-muted);max-width:980px;margin-bottom:18px}
footer{position:absolute;left:64px;right:64px;bottom:20px;display:flex;justify-content:space-between;font-size:11.5px;color:var(--ink-muted)}
footer .pg{font-family:"JetBrains Mono",monospace}
.cols2{display:grid;grid-template-columns:1fr 1fr;gap:40px}.cols2.wide-left{grid-template-columns:1.3fr 1fr}.cols3{display:grid;grid-template-columns:repeat(3,1fr);gap:36px}
.cols4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.cols5{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}.mt{margin-top:24px}.mt-s{margin-top:12px}
.list{list-style:none;display:grid;gap:9px}.list li{font-size:15.5px;line-height:1.45;padding-left:20px;position:relative}
.list li:before{content:"";position:absolute;left:3px;top:.6em;width:6px;height:6px;border-radius:3px;background:var(--primary)}
.list.tight{gap:7px}.list.tight li{font-size:15px}.small2 li{font-size:14px !important}
.pairs li.ko:before{background:var(--accent)}.pairs li.ok:before{background:var(--consensus-ink)}
.ex{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin-top:10px;display:grid;gap:3px;font-size:14px}
.ex span{color:var(--ink-muted)}.ex b{font-family:Newsreader,Georgia,serif;font-size:18px;font-weight:500}
.tag,.pill{justify-self:start;background:var(--surface-sunken);color:var(--ink) !important;font-weight:600;font-size:11.5px;padding:2px 10px;border-radius:99px;letter-spacing:.02em}
.pill{font-size:11px;vertical-align:middle;margin-left:6px}
.box{border-radius:10px;padding:20px 22px}.box.yes{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--primary)}
.box.no{background:var(--surface-muted);border-left:3px solid var(--ink-muted)}.box.no li:before{background:var(--ink-muted)}
.box.warn{background:var(--attention-bg);margin-top:14px;padding:14px 16px}.box.warn b{color:var(--attention-ink)}.box.warn p{color:var(--attention-ink);margin:4px 0 0}
.pr{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px}.pr b{color:var(--primary);font-size:14.5px}.pr p{font-size:14px;margin:6px 0 0}
.rule-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;border-top:3px solid var(--primary)}
.rule-card .n{font-family:"JetBrains Mono",monospace;font-size:13px;color:var(--ink-muted)}.rule-card p{font-size:13.5px;color:var(--ink-muted);margin:0;line-height:1.4}
table.axes{width:100%;border-collapse:collapse}.axes th,.axes td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--border);font-size:15px}
.axes thead th{font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);border-bottom:1px solid var(--border-strong)}
.axes tbody th{font-weight:700;width:180px}
table.kv{width:100%;border-collapse:collapse;margin-top:10px}.kv th{width:120px;text-align:left;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-muted);padding:9px 0;border-bottom:1px solid var(--border);vertical-align:top}
.kv td{font-size:15px;padding:8px 0;border-bottom:1px solid var(--border);line-height:1.4}
.name-stage{background:var(--surface);border:1px solid var(--border);border-radius:10px;height:180px;display:grid;place-items:center}
table.say{width:100%;border-collapse:collapse}.say th{text-align:left;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);padding:0 10px 8px;border-bottom:1px solid var(--border-strong)}
.say td{font-size:14.5px;padding:10px 10px;border-bottom:1px solid var(--border);vertical-align:top;line-height:1.4}.say td.n{color:var(--ink-muted);text-decoration:line-through;text-decoration-color:var(--border-strong)}
.quote{font-family:Newsreader,Georgia,serif;font-size:26px;color:var(--ink);line-height:1.3;margin-bottom:10px}
.use{font-size:14.5px;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:9px 12px;margin-top:8px;line-height:1.4}
.figwrap{display:grid;place-items:center}.fig{display:block;max-width:100%}
.app-side{display:grid;grid-template-columns:1fr 250px;gap:28px;align-items:center}
ol.notes{list-style:none;counter-reset:n;display:grid;gap:16px}.notes li{counter-increment:n;display:grid;gap:3px;padding-left:34px;position:relative}
.notes li:before{content:counter(n);position:absolute;left:0;top:0;width:22px;height:22px;border-radius:11px;background:var(--primary);color:var(--primary-ink);font:600 12px/22px "JetBrains Mono",monospace;text-align:center}
.notes b{font-size:15px}.notes span{font-size:13.5px;color:var(--ink-muted);line-height:1.4}
table.rules{width:100%;border-collapse:collapse}.rules th{text-align:left;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-muted);padding:0 8px 6px;border-bottom:1px solid var(--border-strong)}
.rules td{font-size:13.5px;padding:6px 8px;border-bottom:1px solid var(--border);vertical-align:middle;line-height:1.35}.rules td.num{font-family:"JetBrains Mono",monospace;font-weight:500;white-space:nowrap}
.thumb{display:inline-grid;place-items:center;width:128px;height:54px;border-radius:8px;border:1px solid var(--border)}.file{font-size:11.5px;color:var(--ink-muted);font-family:"JetBrains Mono",monospace}
.grid3{display:grid;grid-template-columns:repeat(3,340px);gap:12px 24px;justify-content:center}
table.cmat{border-collapse:separate;border-spacing:5px;margin:-8px -5px 4px}.cmat th{font-size:11.5px;font-weight:600;color:var(--ink-muted);text-align:center;padding:2px 4px;font-family:"JetBrains Mono",monospace}
.cmat th.rh{text-align:left;color:var(--ink);font-size:12px;padding-right:8px}.cmat td{width:136px;height:43px;text-align:center;border-radius:8px;border:1px solid var(--border)}
.cmat td b{display:block;font-weight:700;font-size:17px;line-height:1.05}.cmat td .gr{font-size:10.5px;font-weight:600;font-family:"JetBrains Mono",monospace}
.cmat td.same{background:transparent;border:1px dashed var(--border);color:var(--ink-muted)}
.prop{display:flex;height:56px;border-radius:10px;overflow:hidden;margin-bottom:14px}.prop span{display:grid;place-items:center;font-size:12.5px;font-weight:600;text-align:center;padding:0 6px}
code{font-family:"JetBrains Mono",monospace;font-size:.84em;background:var(--surface-muted);padding:1px 5px;border-radius:5px}
.files li{font-size:14px !important}
.toc{display:grid;grid-template-columns:1fr 1fr;gap:4px 60px;margin-top:6px}.toc div{display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding:10px 0;font-size:17px}
.toc b{font-family:"JetBrains Mono",monospace;font-weight:500;color:var(--ink-muted);margin-right:14px;font-size:14px}.toc span.p{font-family:"JetBrains Mono",monospace;color:var(--ink-muted)}
.toc .nm{font-family:Newsreader,Georgia,serif;font-size:20px}
/* tema escuro (página de contraste escuro) */
.page.dark{background:var(--canvas);color:var(--ink)}.page.dark h2,.page.dark .cmat th.rh{color:var(--ink)}
/* capa */
.cover{background:var(--primary);color:var(--primary-ink);padding:0}.cover .rule{background:var(--primary-ink);opacity:.25}
.cover-text{position:absolute;left:96px;top:170px;width:600px}.kick.light{color:#C9DBC3}
.cover h1{font-family:Newsreader,Georgia,serif;font-size:80px;font-weight:500;letter-spacing:-.015em;margin:14px 0 18px;line-height:1}
.cover h1 i{color:#C9DBC3}.cover .lead{font-size:19px;max-width:520px;color:#E4ECE4;line-height:1.5}.cover .ver{font-size:13px;color:#B7CDB0;margin-top:22px;font-family:"JetBrains Mono",monospace}
.cover-arch{position:absolute;right:120px;top:80px;width:400px;height:563px}
@media print{@page{size:1280px 720px;margin:0}html{background:none}.page{margin:0;box-shadow:none;break-after:page}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
""".replace("__VARS__", v).replace("__DVARS__", dv)


def build_html():
    PAGES.clear()
    SECOES.clear()
    capa()
    sumario()
    sobre()
    tom()
    marca_pgs()
    versoes()
    respiro()
    incorretos()
    cores()
    tipografia()
    elementos()
    aplicacoes()
    arquivos()
    toc = "".join(f'<div><span><b>{n:02d}</b><span class="nm">{esc(nome)}</span></span><span class="p">{p:02d}</span></div>'
                  for n, nome, p in SECOES)
    total = len(PAGES)
    mark = svg_inline(30, 28, marca_centro("simbolo", "oliva", 15, 14, 20), "width:26px;height:24px")
    mark_d = svg_inline(30, 28, marca_centro("simbolo", "salvia", 15, 14, 20), "width:26px;height:24px")
    out = []
    for i, p in enumerate(PAGES, 1):
        body = p["body"].replace("__SUMARIO__", f'<div class="toc">{toc}</div>')
        if p["cls"] == "cover":
            head, foot = '<div class="rule"></div>', ""
        else:
            title = p["title"] if p["slug"] != "sumario" else "<i>Sumário</i>"
            head = (f'<div class="rule"></div><div class="mark">{mark_d if p["cls"] == "dark" else mark}</div>'
                    f'<div class="kick">{p["sec"] or "Altare"}</div><h2>{title}</h2>')
            foot = f'<footer><span>Altare · identidade visual · {VERSAO}</span><span class="pg">{i:02d} / {total:02d}</span></footer>'
        out.append(f'<section class="page {p["cls"]}" id="p{i:02d}">{head}{body}{foot}</section>')
    html = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Altare · identidade visual</title><style>{css().replace("__FONT__", font_face())}</style></head><body>{"".join(out)}</body></html>')
    return html, [(i, p["slug"]) for i, p in enumerate(PAGES, 1)]
