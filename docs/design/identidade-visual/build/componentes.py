"""Componentes da identidade visual do Altare. Cada componente é um SVG único, usado no documento e exportado
como imagem separada em ../componentes/<pasta>/.

Regras: a marca entra sempre por marca()/place() a partir de ../fonte/, sem mexer no desenho.
Os únicos desenhos alterados de propósito são os exemplos de USO INCORRETO.
Telas de exemplo nunca trazem dados do casamento: data, cidade, convidados, orçamento e estilo ficam "Em definição".
"""
import re

import marca as gerador
from lib import (C, D, ESCURO, CLARO, GEO, H, ICON, MED, MIN, VERSOES, caixa, cmyk, contrast, dec, esc, fmt, icon, line,
                 lines, marca, marca_centro, ornamento, read_svg, rect, rgb, t)

REG = []


def add(folder, name, desc, w, h, body):
    REG.append({"folder": folder, "name": name, "desc": desc, "w": w, "h": h, "body": body})
    return REG[-1]


def get(name):
    return next(c for c in REG if c["name"] == name)


def bg(w, h, fill):
    return rect(0, 0, w, h, fill)


def card(x, y, w, h, fill=None, stroke=None, rx=10, extra=""):
    return rect(x, y, w, h, fill or C["surface"], rx, f'stroke="{stroke or C["border"]}" {extra}')


def eyebrow(x, y, s, fill=None, anchor="start", size=12):
    return t(x, y, esc(s.upper()), size, 600, fill or C["ink-muted"], anchor, ls=0.08)


def tw(s, size, k=0.56):
    """Largura aproximada de texto em Plus Jakarta Sans."""
    return len(s) * size * k


def chip(x, y, s, bg_, fg, ic=None, h=26, size=13, rx=None, weight=600):
    pad = 10
    iw = (size + 5) if ic else 0
    w = tw(s, size) + 2 * pad + iw
    out = rect(x, y, w, h, bg_, h / 2 if rx is None else rx)
    if ic:
        out += icon(ic, x + pad, y + (h - size - 1) / 2, size + 1, fg)
    out += t(x + pad + iw, y + h / 2 + size * 0.36, esc(s), size, weight, fg)
    return out, w


def button(x, y, s, kind="primary", P=None, w=None, h=40, size=15, ic=None):
    P = P or C
    styles = {
        "primary": (P["primary"], None, P.get("primary-ink", C["primary-ink"])),
        "secondary": (P["surface"], P["border-strong"], P["ink"]),
        "ghost": ("none", None, P["ink-muted"]),
        "destrutivo": (P["attention-bg"], None, P["attention-ink"]),
    }
    fill, stroke, fg = styles[kind]
    iw = size + 8 if ic else 0
    w = w or tw(s, size, 0.58) + 36 + iw
    out = rect(x, y, w, h, fill, 6, f'stroke="{stroke}"' if stroke else "")
    tx = x + w / 2 + iw / 2
    if ic:
        out += icon(ic, tx - tw(s, size, 0.58) / 2 - iw, y + (h - size - 2) / 2, size + 2, fg)
    out += t(tx, y + h / 2 + size * 0.36, esc(s), size, 600, fg, "middle")
    return out, w


def leader(x0, y0, x1, y1, cor=None):
    cor = cor or C["ink-muted"]
    return (f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" stroke="{cor}" stroke-width="1.2" fill="none"/>'
            f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="4.5" fill="{cor}"/>')


def label(x, y, title, sub, anchor="start"):
    return t(x, y, esc(title), 19, 700, C["ink"], anchor) + t(x, y + 24, esc(sub), 16, 400, C["ink-muted"], anchor)


def hdim(x0, x1, y, lab, cor=None, above=True):
    cor = cor or C["ink-muted"]
    ty = y - 10 if above else y + 22
    return (f'<path d="M{x0:.1f} {y - 6:.1f} V{y + 6:.1f} M{x0:.1f} {y:.1f} H{x1:.1f} M{x1:.1f} {y - 6:.1f} V{y + 6:.1f}" '
            f'stroke="{cor}" stroke-width="1.2" fill="none"/>' + t((x0 + x1) / 2, ty, lab, 16, 700, C["ink"], "middle", "mono"))


def vdim(x, y0, y1, lab, cor=None, left=True):
    cor = cor or C["ink-muted"]
    tx = x - 12 if left else x + 12
    return (f'<path d="M{x - 6:.1f} {y0:.1f} H{x + 6:.1f} M{x:.1f} {y0:.1f} V{y1:.1f} M{x - 6:.1f} {y1:.1f} H{x + 6:.1f}" '
            f'stroke="{cor}" stroke-width="1.2" fill="none"/>'
            + t(tx, (y0 + y1) / 2 + 6, lab, 16, 700, C["ink"], "end" if left else "start", "mono"))


def textura(uid, x, y, w, h, opacidade=0.035, rx=0):
    return (f'<filter id="{uid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" '
            f'numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="matrix" values="0 0 0 0 0.14  0 0 0 0 0.16  0 0 0 0 0.13  0 0 0 1.4 -0.2"/></filter>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" filter="url(#{uid})" opacity="{opacidade}"/>')


# desenho do símbolo separado em A e mensa (para os diagramas de construção)
_SVB, _SINNER = read_svg("altare-simbolo-oliva.svg")
_SD = re.search(r'd="([^"]+)"', _SINNER).group(1)
A_D, MENSA_D = _SD[:_SD.rfind("M")], _SD[_SD.rfind("M"):]
SIM_BOX = MED["simbolo_box"]
SIM_INK_H = SIM_BOX[3] - SIM_BOX[1]
SIMP_INK_H = MED["simbolo_pequeno_box"][3] - MED["simbolo_pequeno_box"][1]
WORD_BOX = MED["wordmark_box"]
WORD_W = WORD_BOX[2] - WORD_BOX[0]
FORMAL_W = MED["assinatura_box"][2] - MED["assinatura_box"][0]
VERT_H = MED["vertical_box"][3] - MED["vertical_box"][1]


def nested(cx, base, cap, body):
    """Desenho em unidades do símbolo (origem na linha de base do A), posicionado por origem e versal."""
    s = cap / H
    x0, y0, w, h = _SVB
    return (f'<svg x="{cx + x0 * s:.2f}" y="{base + y0 * s:.2f}" width="{w * s:.2f}" height="{h * s:.2f}" '
            f'viewBox="{x0} {y0} {w} {h}" overflow="visible">{body}</svg>')


def cap_por_altura(h_px, pequeno=False):
    return h_px * H / (SIMP_INK_H if pequeno else SIM_INK_H)


# ================================================================ construção

def build_conceito():
    W, Hh = 1400, 640
    b = bg(W, Hh, C["canvas"])
    b += t(120, 70, "O símbolo não desenha um altar: é a letra A assentada sobre uma mesa. Lê-se como inicial e como altar.",
           20, 400, C["ink-muted"])
    stages = [
        (f'<path d="{A_D}" fill="{C["primary"]}"/>', "a letra", "O A da Newsreader: a inicial do nome, clássica e serena."),
        (f'<path d="{MENSA_D}" fill="{C["primary"]}"/><path d="{A_D}" fill="none" stroke="{C["border"]}" stroke-width="1.5" '
         f'stroke-dasharray="5 5" vector-effect="non-scaling-stroke"/>', "a mesa", "A mensa, a mesa do altar, reduzida a uma lâmina horizontal."),
        (f'<path d="{_SD}" fill="{C["primary"]}"/>', "a letra sobre a mesa",
         "A letra repousa sobre a mesa, com uma folga pequena. O altar no centro, sem símbolo religioso."),
    ]
    for i, (body, tag, cap) in enumerate(stages):
        x = 120 + i * 400
        b += card(x, 110, 300, 300)
        b += nested(x + 150, 330, 170, body)
        b += t(x, 450, f"{i + 1} · {tag}", 15, 600, C["primary"], ls=0.06)
        b += lines(x, 482, cap, 34, 18, 27, fill=C["ink"])
        if i < 2:
            b += t(x + 350, 270, "→", 40, 300, C["ink-subtle"], "middle")
    return add("construcao", "conceito", "Conceito do símbolo: a letra, a mesa, a letra sobre a mesa.", W, Hh, b)


def build_anatomia():
    W, Hh = 1400, 640
    b = bg(W, Hh, C["canvas"])
    b += eyebrow(110, 120, "Símbolo") + eyebrow(740, 120, "Wordmark")
    b += line(690, 100, 690, 590, C["border"])
    cx, base, cap = 300, 470, 260
    s = cap / H
    b += line(cx, 150, cx, 545, C["border-strong"], 1.2, 'stroke-dasharray="5 5"')
    b += t(cx, 575, "eixo comum", 15, 500, C["ink-muted"], "middle")
    b += marca("simbolo", "oliva", cx, base, cap)
    gap0, gap1 = base, base + GEO["folga_modulos"] * 10 * s
    sl1 = gap1 + GEO["espessura_mensa_modulos"] * 10 * s
    half = GEO["largura_mensa_modulos"] * 10 * s / 2
    b += label(500, 250, "A da Newsreader", "peso 500, eixo óptico 72") + leader(495, 244, 380, 320)
    b += label(500, 410, "Folga", "2 módulos: a letra paira") + leader(495, 404, cx + half - 8, (gap0 + gap1) / 2)
    b += label(500, 505, "Mensa", "27 × 1 módulos, cantos retos") + leader(495, 499, cx + half - 2, (gap1 + sl1) / 2)

    wx, wb, wc = 740, 300, 100
    sw = wc / H
    xh = MED["wordmark_xh"] * sw
    for yy, lab in ((wb - wc, "versal"), (wb - xh, "altura-x"), (wb, "linha de base")):
        b += line(wx - 10, yy, wx + WORD_W * sw + 16, yy, C["border-strong"], 1.2, 'stroke-dasharray="5 4"')
        b += t(wx + WORD_W * sw + 26, yy + 5, lab, 14, 600, C["ink-muted"])
    b += marca("wordmark", "oliva", wx, wb, wc)
    b += lines(wx, 350, "Newsreader 500, eixo óptico 72. Caixa de frase, kerning da própria fonte, sem espaçamento extra entre letras.",
               56, 16, 24, fill=C["ink-muted"])
    b += eyebrow(740, 445, "Assinatura formal")
    b += marca("assinatura", "carvao", wx, 505, 30)
    b += lines(wx, 545, "Versal com +0,26 em. Só em documentos impressos, no Dossiê e em rodapés formais.", 56, 16, 24,
               fill=C["ink-muted"])
    return add("construcao", "anatomia", "Anatomia: o A, a folga, a mensa e o eixo comum; wordmark e assinatura formal.", W, Hh, b)


def build_grade():
    W, Hh = 1400, 700
    b = bg(W, Hh, C["canvas"])
    b += t(110, 62, "Módulo (m) = 1/20 da altura de versal do A. Mensa: 27 × 1 m, a 2 m da linha de base.", 21, 700, C["ink"])
    b += t(110, 92, "O ápice do A passa da versal em 1,6 m (overshoot óptico da fonte). Medidas lidas de build/medidas.json.",
           16, 400, C["ink-muted"])
    mpx = 17
    cx, base = 520, 160 + 22 * mpx
    cap = 20 * mpx
    for i in range(-14, 15):
        xx = cx + i * mpx
        b += line(xx, base - 22 * mpx, xx, base + 3 * mpx, C["border"], 0.8)
    for j in range(-22, 4):
        yy = base + j * mpx
        b += line(cx - 14 * mpx, yy, cx + 14 * mpx, yy, C["border"], 0.8)
    b += nested(cx, base, cap, f'<path d="{_SD}" fill="{C["primary"]}" opacity="0.14"/>'
                               f'<path d="{_SD}" fill="none" stroke="{C["primary"]}" stroke-width="1.6" vector-effect="non-scaling-stroke"/>')
    b += line(cx - 14 * mpx, base - cap, cx + 14 * mpx, base - cap, C["border-strong"], 1.2, 'stroke-dasharray="5 4"')
    b += line(cx - 14 * mpx, base, cx + 14 * mpx, base, C["border-strong"], 1.2, 'stroke-dasharray="5 4"')
    aw = MED["A_largura_modulos"] * mpx
    b += hdim(cx - aw / 2, cx + aw / 2, base - 22 * mpx - 18, dec(MED["A_largura_modulos"]))
    b += hdim(cx - 13.5 * mpx, cx + 13.5 * mpx, base + 3 * mpx + 22, "27", above=False)
    b += vdim(cx - 14 * mpx - 24, base - cap, base, "20")
    ov = MED["A_overshoot_modulos"] * mpx
    b += vdim(cx - 14 * mpx - 24, base - cap - ov, base - cap, dec(MED["A_overshoot_modulos"]))
    b += vdim(cx + 14 * mpx + 24, base, base + 2 * mpx, "2", left=False)
    b += vdim(cx + 14 * mpx + 64, base + 2 * mpx, base + 3 * mpx, "1", left=False)
    rows = [("H · versal do A", "20 m"), ("Largura do A", f"{dec(MED['A_largura_modulos'])} m"),
            ("Mensa", "27 × 1 m (1,16 × o A)"), ("Folga A → mensa", "2 m"),
            ("Overshoot do ápice", f"{dec(MED['A_overshoot_modulos'])} m"), ("Versão pequena (≤ 24 px)", "mensa 2 m · folga 2 m"),
            ("Vertical", "versal do símbolo = 2,6 × wordmark"), ("Vertical · espaço", "1 versal do wordmark")]
    y = 180
    for k, v in rows:
        b += t(900, y, k, 16, 500, C["ink-muted"]) + t(1300, y, esc(v), 16, 500, C["ink"], "end", "mono")
        b += line(900, y + 14, 1300, y + 14, C["border"])
        y += 48
    return add("construcao", "grade", "Símbolo na grade modular: versal, largura do A, mensa, folga e overshoot.", W, Hh, b)


def build_lockups():
    W, Hh = 1400, 640
    b = bg(W, Hh, C["canvas"])
    items = [
        ("Wordmark", "Cabeçalho do app no desktop, e-mail, exportações.", "altare-wordmark-<cor>.svg",
         lambda cx, cy: marca_centro("wordmark", "oliva", cx, cy, 46)),
        ("Símbolo", "Cabeçalho mobile, favicon, ícone do app, avatar.", "altare-simbolo-<cor>.svg",
         lambda cx, cy: marca_centro("simbolo", "oliva", cx, cy, 110)),
        ("Vertical", "Tela de login, splash do PWA, capa do Dossiê.", "altare-vertical-<cor>.svg",
         lambda cx, cy: marca_centro("vertical", "oliva", cx, cy, 92)),
        ("Assinatura formal", "Dossiê do Dia D, impressão, rodapés formais.", "altare-assinatura-<cor>.svg",
         lambda cx, cy: marca_centro("assinatura", "carvao", cx, cy - 26, 22)
         + line(cx - 92, cy + 6, cx + 92, cy + 6, C["border-strong"]) + eyebrow(cx, cy + 34, "Dossiê do Dia D", anchor="middle")),
    ]
    for i, (nome, uso, arq, draw) in enumerate(items):
        x = 40 + i * 335
        b += card(x, 40, 315, 400)
        b += draw(x + 157.5, 240)
        b += t(x, 485, nome, 20, 700, C["ink"])
        b += lines(x, 513, uso, 36, 16, 23, fill=C["ink-muted"])
        b += t(x, 570, esc(arq), 13, 400, C["ink-subtle"], fam="mono")
    b += t(40, 620, "Não existe lockup horizontal (símbolo ao lado do wordmark): A + Altare repetiria a mesma letra.", 16, 600, C["ink"])
    return add("construcao", "lockups", "Os quatro arranjos da marca: wordmark, símbolo, vertical e assinatura formal.", W, Hh, b)


def build_versao_pequena(r):
    W, Hh = 1400, 600
    b = bg(W, Hh, C["canvas"])
    b += t(80, 60, "Com menos de 24 px de altura, a mensa de 1 módulo fica com menos de 1 px e some.", 20, 700, C["ink"])
    b += t(80, 90, "A versão pequena engrossa a mensa para 2 módulos. O A não muda.", 17, 400, C["ink-muted"])
    for row, (nome, peca, sub, raster) in enumerate((
            ("Padrão", "simbolo", "mensa 1 m · a partir de 24 px", r["s16"]),
            ("Pequena", "simbolo-pequeno", "mensa 2 m · de 16 a 23 px", r["s16p"]))):
        y = 150 + row * 210
        b += card(60, y, 1280, 180)
        b += t(90, y + 60, nome, 22, 700, C["ink"]) + t(90, y + 88, sub, 15, 400, C["ink-muted"])
        b += t(90, y + 140, esc(f"altare-{peca}-<cor>.svg"), 13, 400, C["ink-subtle"], fam="mono")
        x = 400
        for hpx in (16, 20, 24, 32, 48):
            cap = cap_por_altura(hpx, peca != "simbolo")
            b += marca_centro(peca, "oliva", x, y + 90, cap)
            b += t(x, y + 150, f"{hpx} px", 13, 500, C["ink-muted"], "middle", "mono")
            x += 90 if hpx < 32 else 110
        b += rect(1010, y + 18, 300, 144, C["surface-muted"], 8)
        b += (f'<image href="{raster}" x="1150" y="{y + 26}" width="144" height="128" '
              f'preserveAspectRatio="xMidYMid meet" style="image-rendering:pixelated"/>')
        b += t(1030, y + 82, "16 px", 15, 700, C["ink"]) + t(1030, y + 104, "ampliado 8×", 13, 500, C["ink-muted"])
    return add("construcao", "versao-pequena", "Correção óptica: símbolo padrão e versão pequena, com o 16 px ampliado.", W, Hh, b)


def build_area_de_respiro():
    W, Hh = 1400, 640
    b = bg(W, Hh, C["canvas"])

    def zona(peca, cx, cy, cap, nome):
        x0, y0, x1, y1 = caixa(peca, cap)
        ox, oy = cx - (x0 + x1) / 2, cy - (y0 + y1) / 2
        X0, Y0, X1, Y1 = ox + x0, oy + y0, ox + x1, oy + y1
        x = GEO["respiro_em_H"] * cap
        out = rect(X0 - x, Y0 - x, X1 - X0 + 2 * x, Y1 - Y0 + 2 * x, C["consensus-bg"], 0,
                   f'stroke="{C["primary"]}" stroke-width="1.2" stroke-dasharray="6 5" opacity="0.9"')
        out += rect(X0, Y0, X1 - X0, Y1 - Y0, C["canvas"], 0, f'stroke="{C["border-strong"]}" stroke-width="0.8"')
        out += marca(peca, "oliva", ox, oy, cap)
        for (qx, qy) in ((X0 - x, (Y0 + Y1) / 2 - x / 2), (X1, (Y0 + Y1) / 2 - x / 2), ((X0 + X1) / 2 - x / 2, Y0 - x),
                         ((X0 + X1) / 2 - x / 2, Y1)):
            out += rect(qx, qy, x, x, C["primary"], 0, 'opacity="0.18"')
            out += t(qx + x / 2, qy + x / 2 + 6, "x", 17, 700, C["primary"], "middle", "serif", extra='font-style="italic"')
        out += t(cx, Y1 + x + 46, nome, 17, 700, C["ink"], "middle")
        return out

    b += zona("wordmark", 400, 280, 96, "Wordmark")
    b += zona("simbolo", 1040, 280, 140, "Símbolo")
    b += t(700, 560, "x = metade da altura de versal do A (0,5 H), em todos os lados.", 19, 700, C["ink"], "middle")
    b += t(700, 590, "Nada entra nessa área: texto, borda, foto, ornamento ou outra marca.", 16, 400, C["ink-muted"], "middle")
    return add("construcao", "area-de-respiro", "Área de respiro: x = 0,5 × a altura de versal do A, no wordmark e no símbolo.", W, Hh, b)


def build_tamanho_minimo(r):
    W, Hh = 1400, 620
    b = bg(W, Hh, C["canvas"])
    itens = [
        ("Wordmark", f"{MIN['wordmark_px']} px · {MIN['wordmark_mm']} mm de largura",
         lambda cx, cy: marca_centro("wordmark", "oliva", cx, cy, MIN["wordmark_px"] * H / WORD_W)),
        ("Símbolo", f"{MIN['simbolo_px']} px · {MIN['simbolo_mm']} mm de altura",
         lambda cx, cy: marca_centro("simbolo", "oliva", cx, cy, cap_por_altura(MIN["simbolo_px"]))),
        ("Símbolo pequeno", f"{MIN['simbolo_pequeno_px']} px de altura (favicon)",
         lambda cx, cy: marca_centro("simbolo-pequeno", "oliva", cx, cy, cap_por_altura(MIN["simbolo_pequeno_px"], True))),
        ("Vertical", f"{MIN['vertical_px']} px · {MIN['vertical_mm']} mm de altura",
         lambda cx, cy: marca_centro("vertical", "oliva", cx, cy, MIN["vertical_px"] * H / VERT_H)),
        ("Assinatura formal", f"{MIN['assinatura_px']} px · {MIN['assinatura_mm']} mm de largura",
         lambda cx, cy: marca_centro("assinatura", "carvao", cx, cy, MIN["assinatura_px"] * H / FORMAL_W)),
    ]
    for i, (nome, sub, draw) in enumerate(itens):
        x = 60 + i * 258
        b += card(x, 60, 240, 240)
        b += draw(x + 120, 180)
        b += t(x, 335, nome, 18, 700, C["ink"]) + t(x, 360, esc(sub), 14, 500, C["ink-muted"], fam="mono")
    b += t(60, 430, "Tamanho real na tela, com densidade 1×. Abaixo do mínimo, a mensa e as serifas deixam de ler.", 17, 400, C["ink-muted"])
    b += rect(60, 460, 1280, 130, C["surface-muted"], 10)
    for i, (k, lab) in enumerate((("s16p", "Símbolo pequeno · 16 px"), ("f16", "Favicon · 16 px"), ("f32", "Favicon · 32 px"))):
        x = 90 + i * 420
        b += (f'<image href="{r[k]}" x="{x}" y="476" width="98" height="98" preserveAspectRatio="xMidYMid meet" '
              f'style="image-rendering:pixelated"/>')
        b += t(x + 116, 520, lab, 16, 700, C["ink"]) + t(x + 116, 545, "ampliado, pixel a pixel", 14, 400, C["ink-muted"])
    return add("construcao", "tamanho-minimo", "Tamanhos mínimos de cada arranjo e a validação em pixel do favicon.", W, Hh, b)


# ================================================================ versões de cor

def build_versoes_de_cor():
    W, Hh = 1400, 640
    b = bg(W, Hh, C["canvas"])
    for i, v in enumerate(VERSOES):
        col, row = i % 3, i // 3
        x, y = 40 + col * 448, 30 + row * 300
        stroke = f'stroke="{C["border"]}"' if v["fundo"] in (C["canvas"], C["branco"]) else ""
        b += rect(x, y, 424, 270, v["fundo"], 10, stroke)
        b += marca_centro("wordmark", v["sufixo"], x + 212, y + 112, 52)
        r = contrast(v["cor"], v["fundo"])
        sub = v["cor"] if v["sufixo"] not in ("salvia",) else D["ink-muted"]
        b += t(x + 24, y + 222, esc(v["nome"]), 17, 700, v["cor"])
        b += t(x + 24, y + 246, f'{v["cor"]} sobre {v["fundo"]} · {fmt(r)}', 13, 400, sub, fam="mono", extra='opacity="0.85"')
        b += marca_centro("simbolo", v["sufixo"], x + 384, y + 228, 26)
    return add("logo", "versoes-de-cor", "As seis versões de cor, cada uma sobre o fundo de uso, com o contraste calculado.", W, Hh, b)


# ================================================================ usos incorretos

def build_incorretos():
    f = gerador.Fonte(gerador.NEWSREADER, 500, 72)
    items = []

    def stage(uid, body, fundo=None):
        return (card(0, 0, 400, 300) + rect(14, 14, 372, 190, fundo or C["canvas"], 8) + body)

    cx, cy = 200, 109
    wm = lambda **kw: marca_centro("wordmark", "oliva", cx, cy, 40, **kw)
    items.append(("distorcer", "Não distorça", "Nunca estique, achate ou mude a proporção. Redimensione sempre pelos cantos.",
                  f'<g transform="translate({cx} {cy}) scale(1.5 0.7) translate({-cx} {-cy})">{wm()}</g>'))
    items.append(("girar", "Não gire", "A marca fica sempre na horizontal. A mensa é um plano: inclinada, deixa de ser mesa.",
                  f'<g transform="rotate(-14 {cx} {cy})">{wm()}</g>'))
    items.append(("terracota", "Não use terracota nem cores fora", "Terracota é do custo real e da atenção, nunca da marca. Só as seis versões aprovadas.",
                  wm(recolor={C["primary"]: C["accent"]})))
    efeito = (f'<defs><linearGradient id="g-ef" x1="0" x2="1"><stop offset="0" stop-color="#7a8f4a"/><stop offset="1" stop-color="#c9a545"/>'
              f'</linearGradient><filter id="f-ef"><feDropShadow dx="3" dy="5" stdDeviation="3" flood-opacity=".35"/></filter></defs>'
              f'<g filter="url(#f-ef)">{wm(recolor={C["primary"]: "url(#g-ef)"})}</g>')
    items.append(("efeitos", "Não aplique efeitos", "Sem degradê, dourado, sombra, brilho, contorno ou relevo. A marca é sempre chapada.", efeito))
    rr = contrast(C["primary"], "#2F3E31")
    items.append(("fundo-sem-contraste", "Não use fundo sem contraste",
                  f"Oliva sobre Oliva Noturno dá {fmt(rr)}. Use as combinações aprovadas de marca e fundo.",
                  rect(14, 14, 372, 190, "#2F3E31", 8) + wm()))
    lado = (marca_centro("simbolo", "oliva", 105, cy, 60) + marca_centro("wordmark", "oliva", 250, cy, 38))
    items.append(("lado-a-lado", "Não monte símbolo ao lado do nome", "Não existe lockup horizontal: A + Altare repete a letra. Use o vertical.", lado))
    d_caps, box = f.outline("ALTARE", 40)
    caps = (f'<path d="{d_caps}" fill="{C["primary"]}" transform="translate({cx - (box[0] + box[2]) / 2:.1f} '
            f'{cy - (box[1] + box[3]) / 2:.1f})"/>')
    items.append(("maiusculas", "Não escreva o wordmark em versal", "Versal só na assinatura formal, com +0,26 em. O wordmark é sempre Altare.", caps))
    mensa_errada = nested(cx, 140, 92, f'<path d="{A_D}" fill="{C["primary"]}"/><rect x="-150" y="0" width="300" height="34" rx="17" '
                                       f'fill="{C["primary"]}"/>')
    items.append(("mensa", "Não altere a mensa", "Não engrosse, arredonde, encoste ou estique a mensa. Ela é fina, reta e solta.", mensa_errada))
    items.append(("outra-fonte", "Não troque a fonte", "O nome só existe nos contornos da Newsreader 500. Nunca digite o logo em outra fonte.",
                  t(cx, cy + 22, "Altare", 62, 700, C["primary"], "middle", "sans")))
    cruz = (marca_centro("simbolo", "oliva", cx, cy + 12, 74)
            + f'<path d="M{cx} {cy - 86} V{cy - 50} M{cx - 12} {cy - 74} H{cx + 12}" stroke="{C["primary"]}" stroke-width="5" stroke-linecap="square"/>')
    items.append(("simbolo-religioso", "Não some símbolos religiosos",
                  "Nada de cruz, pomba, alianças ou corações junto da marca. O sagrado aparece pela proporção.", cruz))
    for i, (slug, title, desc, body) in enumerate(items, 1):
        b = stage(slug, body if slug != "fundo-sem-contraste" else body)
        b += f'<circle cx="32" cy="238" r="11" fill="{C["ink"]}"/>' + t(32, 243, "×", 16, 700, C["surface"], "middle")
        b += t(52, 244, esc(f"{i:02d} · {title}"), 16, 700, C["ink"])
        b += lines(22, 272, desc, 52, 13.5, 19, fill=C["ink-muted"])
        add("usos-incorretos", f"{i:02d}-{slug}", f"Uso incorreto: {title.lower()}.", 400, 300, b)


# ================================================================ cores

def _swatch(P, tok, x, y, w=335, h=112, dark=False):
    hx = tok["hex"]
    r_, g_, b_ = rgb(hx)
    ink, mut = (D["ink"], D["ink-muted"]) if dark else (C["ink"], C["ink-muted"])
    edge = D["border"] if dark else C["border"]
    out = rect(x, y, w, h, P["surface"], 10, f'stroke="{edge}"')
    out += rect(x + 10, y + 10, 92, h - 20, hx, 6, f'stroke="{edge}"')
    out += t(x + 116, y + 30, esc(tok["nome"]), 16, 700, ink)
    out += t(x + 116, y + 50, f'{hx} · --{tok["token"]}', 12.5, 500, P["primary"] if not dark else D["primary"], fam="mono")
    cy = cmyk(hx)
    out += t(x + 116, y + 67, f"RGB {r_} {g_} {b_} · CMYK {cy[0]} {cy[1]} {cy[2]} {cy[3]}", 10.5, 400, mut, fam="mono")
    out += lines(x + 116, y + 86, tok["funcao"], 36, 12, 16, fill=ink)
    return out


def build_paletas():
    for nome, P, lista, dark in (("paleta-clara", C, CLARO, False), ("paleta-escura", D, ESCURO, True)):
        W, Hh = 1400, 640
        b = bg(W, Hh, P["canvas"])
        for i, tok in enumerate(lista):
            col, row = i % 4, i // 4
            b += _swatch(P, tok, 20 + col * 345, 10 + row * 125, dark=dark)
        desc = "Paleta do tema claro: 17 tokens com hex, RGB, CMYK aproximado e função." if not dark else \
            "Paleta do tema escuro Noite Oliva: 18 tokens com hex, RGB, CMYK aproximado e função."
        add("cores", nome, desc, W, Hh, b)
    for tok in CLARO:
        b = bg(480, 200, C["canvas"]) + _swatch(C, tok, 10, 10, 460, 180)
        add("cores", f"cor-{tok['token']}", f"Swatch {tok['nome']} ({tok['hex']}) com RGB, CMYK aproximado e função.", 480, 200, b)


# ================================================================ tipografia

ESCALA = __import__("lib").TOKENS["tipografia"]["escala"]


def build_familias():
    W, Hh = 1400, 640
    b = bg(W, Hh, C["canvas"])
    fams = [
        ("serif", "Newsreader", "Serifa editorial", "Títulos, nomes de espaços, fornecedores e cenários, marca e Dossiê.",
         "400 · 500 · 600 · itálico 400", "Production Type · OFL", "Espaço Exemplo A"),
        ("sans", "Plus Jakarta Sans", "Interface", "Navegação, controles, rótulos, descrições, comentários e linha do tempo.",
         "400 · 500 · 600 · 700", "Tokotype · OFL", "Próximo passo de vocês"),
        ("mono", "JetBrains Mono", "Números", "Todo número que o casal compara: valores, notas, contagens, parcelas, datas em tabelas.",
         "400 · 500 · tabular", "JetBrains · OFL", "R$ 8.950,00"),
    ]
    for i, (fam, nome, papel, uso, pesos, lic, amostra) in enumerate(fams):
        x = 40 + i * 448
        b += card(x, 30, 424, 580)
        b += t(x + 28, 220, "Aa", 150, 500 if fam != "sans" else 600, C["primary"], fam=fam)
        b += eyebrow(x + 28, 270, papel)
        b += t(x + 28, 304, nome, 26, 600 if fam == "sans" else 500, C["ink"], fam=fam)
        b += lines(x + 28, 342, uso, 44, 15, 22, fill=C["ink-muted"])
        b += line(x + 28, 420, x + 396, 420, C["border"])
        b += t(x + 28, 450, "Pesos", 13, 600, C["ink-muted"]) + t(x + 396, 450, esc(pesos), 13, 500, C["ink"], "end", "mono")
        b += t(x + 28, 478, "Licença", 13, 600, C["ink-muted"]) + t(x + 396, 478, esc(lic), 13, 500, C["ink"], "end", "mono")
        b += line(x + 28, 500, x + 396, 500, C["border"])
        b += t(x + 28, 560, esc(amostra), 30 if fam != "mono" else 28, 500, C["ink"], fam=fam)
    return add("tipografia", "familias", "As três famílias: Newsreader (serifa), Plus Jakarta Sans (interface) e JetBrains Mono (números).", W, Hh, b)


def build_hierarquia():
    W, Hh = 1400, 720
    b = bg(W, Hh, C["canvas"])
    y = 20
    for e in ESCALA:
        rh = max(e["lh"] + 12, 48)
        b += line(40, y + rh, 1360, y + rh, C["border"])
        b += t(40, y + rh / 2 + 2, e["token"], 15, 600, C["ink"], fam="mono")
        b += t(40, y + rh / 2 + 20, esc(e["uso"]), 12, 400, C["ink-muted"])
        spec = f'{e["px"]}/{e["lh"]} · {e["peso"]} · mobile {e["mobile"]}'
        b += t(360, y + rh / 2 + 5, spec, 13, 400, C["ink-muted"], fam="mono")
        fam = e["familia"]
        ls = 0.08 if e["token"] == "eyebrow" else 0
        fill = C["ink"] if fam != "mono" else C["ink"]
        b += t(640, y + rh / 2 + e["px"] * 0.34, esc(e["amostra"]), e["px"], e["peso"], fill, fam=fam, ls=ls)
        y += rh
    return add("tipografia", "hierarquia", "Escala tipográfica: token, uso, tamanho/entrelinha, peso, mobile e amostra em tamanho real.", W, y + 20, b)


def build_especime():
    W, Hh = 1400, 700
    b = bg(W, Hh, C["canvas"])
    blocos = [
        ("serif", "Newsreader", ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz", "ÁÂÃÀÉÊÍÓÔÕÚÇ áâãàéêíóôõúç"], 30, 500),
        ("sans", "Plus Jakarta Sans", ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz", "ÁÂÃÀÉÊÍÓÔÕÚÇ áâãàéêíóôõúç ! ? “ ” … —"], 24, 400),
        ("mono", "JetBrains Mono", ["0123456789", "R$ 12.480,00 · 4,8 / 5 · 12,5% · 3 de 5", "+ − × ÷ = ( ) / : · 01/02 · 14h30"], 24, 400),
    ]
    y = 30
    for fam, nome, linhas, size, peso in blocos:
        b += eyebrow(40, y + 16, nome)
        yy = y + 54
        for l in linhas:
            b += t(40, yy, esc(l), size, peso, C["ink"], fam=fam)
            yy += size * 1.45
        y = yy + 6
        b += line(40, y - 14, 1360, y - 14, C["border"])
    b += t(40, y + 22, "Itálico editorial", 13, 600, C["ink-muted"])
    b += t(220, y + 24, "Tag editorial: a escolha mais serena das três.", 24, 400, C["ink"], fam="serif", extra='font-style="italic"')
    pesos = "".join(t(40 + i * 330, y + 76, f"{w} · Próximo passo", 20, w, C["ink"]) for i, w in enumerate((400, 500, 600, 700)))
    b += pesos
    return add("tipografia", "especime", "Especímen das três famílias: alfabetos, acentos, números, sinais, itálico e pesos.", W, y + 100, b)


def build_numeros():
    W, Hh = 1400, 640
    b = bg(W, Hh, C["canvas"])
    b += eyebrow(40, 40, "Formatos pt-BR")
    ex = [("Moeda", "R$ 12.480,00", "R$ + espaço não separável, milhar com ponto"), ("Nota", "4,8 / 5", "vírgula decimal, barra com espaços"),
          ("Porcentagem", "12,5%", "sem espaço antes do %"), ("Contagem", "3 de 5", "por extenso o “de”"),
          ("Data em tabela", "12/03", "dia/mês; ano só quando muda"), ("Parcela", "3/10", "número da parcela / total"),
          ("Diferença", "+ R$ 1.200,00", "sinal explícito em custo extra")]
    y = 80
    for k, v, nota in ex:
        b += t(40, y, k, 15, 600, C["ink-muted"]) + t(330, y, esc(v), 18, 500, C["ink"], "end", "mono")
        b += t(360, y, esc(nota), 14, 400, C["ink-muted"])
        b += line(40, y + 14, 660, y + 14, C["border"])
        y += 46
    b += eyebrow(740, 40, "Linha de orçamento · valores ilustrativos")
    b += card(740, 60, 620, 210)
    cols = ["Planejado", "Estimado", "Contratado", "Realizado"]
    right = [1010, 1120, 1230, 1340]
    for xr, c_ in zip(right, cols):
        b += t(xr, 96, c_, 12, 600, C["ink-muted"], "end")
    b += line(760, 110, 1340, 110, C["border"])
    rows = [("Espaço", ["15.000,00", "16.200,00", "16.200,00", "4.860,00"], False),
            ("Gastronomia", ["22.000,00", "24.650,00", "—", "—"], True)]
    yy = 146
    for nome, vals, alerta in rows:
        b += t(760, yy, nome, 19, 500, C["ink"], fam="serif")
        for i, (xr, v) in enumerate(zip(right, vals)):
            cor = C["accent-ink"] if alerta and i == 1 else C["ink"]
            b += t(xr, yy, v, 14, 400, cor, "end", "mono")
            if alerta and i == 1:
                b += icon("circle-alert", xr - 104, yy - 13, 15, C["accent"])
        b += line(760, yy + 22, 1340, yy + 22, C["border"])
        yy += 56
    b += t(760, 252, "Estimado acima do planejado: Terracota Escura + ícone de atenção, nunca só a cor.", 13, 400, C["ink-muted"])
    b += eyebrow(740, 320, "StatBlock")
    for i, (lab, val, sub) in enumerate((("Custo comparável", "R$ 8.950,00", "3 propostas"), ("Convidados", "Em definição", "lista em construção"))):
        x = 740 + i * 316
        b += rect(x, 340, 300, 120, C["surface-muted"], 10)
        b += t(x + 20, 372, lab, 12, 600, C["ink-muted"])
        mono = val[0].isdigit() or val.startswith("R$")
        b += t(x + 20, 412, esc(val), 24 if mono else 20, 500, C["ink"] if mono else C["ink-muted"], fam="mono" if mono else "sans")
        b += t(x + 20, 440, sub, 13, 400, C["ink-muted"])
    b += lines(740, 500, "Números sempre à direita nas colunas, em JetBrains Mono tabular. Rótulos em Plus Jakarta Sans. Valores do casamento "
                         "que ainda não existem aparecem como “Em definição”, nunca como zero.", 76, 15, 22, fill=C["ink"])
    return add("tipografia", "numeros", "Números em pt-BR: formatos, linha de orçamento com colunas tabulares e StatBlock.", W, Hh, b)


# ================================================================ elementos de apoio

def build_arco():
    W, Hh = 1400, 640
    b = bg(W, Hh, C["canvas"])
    vs = [("arco-simples", "Arco simples", "Moldura de ilustrações e estados vazios.", 110, 155),
          ("arco-duplo", "Arco duplo", "Tela de login, splash e capa do Dossiê.", 110, 155),
          ("arcada", "Arcada", "Faixa de cabeçalho em documentos impressos.", 300, 53)]
    for i, (nome, titulo, uso, w, h) in enumerate(vs):
        x = 40 + i * 448
        b += card(x, 30, 424, 330)
        b += ornamento(nome, x + 212 - w / 2, 195 - h / 2, w, h, cor=C["ink-muted"], opacidade=1)
        b += t(x, 400, titulo, 19, 700, C["ink"]) + lines(x, 426, uso, 44, 15, 22, fill=C["ink-muted"])
        b += t(x, 474, f"fonte/ornamentos/{nome}.svg", 12.5, 400, C["ink-subtle"], fam="mono")
    b += line(40, 510, 1360, 510, C["border"])
    specs = [("Proporção", "1 : 1,4 (meia-circunferência sobre retângulo)"), ("Traço", "1,25 px, sem preenchimento"),
             ("Cor", "Musgo #5C6158 a 70%; no escuro, Líquen"), ("Leitura", "arquitetura, não religião: ecoa a nave e o altar")]
    for i, (k, v) in enumerate(specs):
        x = 40 + (i % 2) * 660
        y = 548 + (i // 2) * 36
        b += t(x, y, k, 14, 600, C["ink-muted"]) + t(x + 120, y, esc(v), 15, 500, C["ink"])
    return add("elementos", "arco", "Arco de volta perfeita: simples, duplo e arcada, com proporção, traço e cor.", W, Hh, b)


def build_ramo():
    W, Hh = 1400, 640
    b = bg(W, Hh, C["canvas"])
    vs = [("ramo-grande", "Ramo grande", "Tela de login e 404. Único com nervuras e azeitonas.", 300, 112),
          ("ramo-pequeno", "Ramo pequeno", "Estados vazios e confirmações discretas.", 200, 80),
          ("ramo-faixa", "Faixa de ramos", "Cabeçalho do Dossiê e divisórias raras.", 320, 56)]
    for i, (nome, titulo, uso, w, h) in enumerate(vs):
        x = 40 + i * 448
        b += card(x, 30, 424, 330)
        b += ornamento(nome, x + 212 - w / 2, 195 - h / 2, w, h, cor=C["ink-muted"], opacidade=1)
        b += t(x, 400, titulo, 19, 700, C["ink"]) + lines(x, 426, uso, 44, 15, 22, fill=C["ink-muted"])
        b += t(x, 474, f"fonte/ornamentos/{nome}.svg", 12.5, 400, C["ink-subtle"], fam="mono")
    b += line(40, 510, 1360, 510, C["border"])
    specs = [("Desenho", "haste em curva, folhas alternadas que diminuem"), ("Traço", "1,25 px, sem preenchimento"),
             ("Cor", "Musgo #5C6158 a 70%; nunca verde vivo"), ("Limite", "um ornamento por tela, nunca atrás da marca")]
    for i, (k, v) in enumerate(specs):
        x = 40 + (i % 2) * 660
        y = 548 + (i // 2) * 36
        b += t(x, y, k, 14, 600, C["ink-muted"]) + t(x + 120, y, esc(v), 15, 500, C["ink"])
    return add("elementos", "ramo", "Ramo de oliveira em traço único: grande, pequeno e faixa.", W, Hh, b)


def build_superficies():
    W, Hh = 1400, 660
    b = bg(W, Hh, C["canvas"])
    b += eyebrow(40, 40, "Textura de papel")
    b += rect(40, 60, 300, 180, C["canvas"], 10, f'stroke="{C["border"]}"')
    b += textura("tx-a", 40, 60, 300, 180, 0.035, 10)
    b += rect(360, 60, 300, 180, C["canvas"], 10, f'stroke="{C["border"]}"')
    b += textura("tx-b", 360, 60, 300, 180, 0.35, 10)
    b += t(40, 266, "3,5% · como aparece", 14, 500, C["ink-muted"]) + t(360, 266, "10× mais forte · para enxergar", 14, 500, C["ink-muted"])
    b += lines(40, 296, "Ruído em feTurbulence só no canvas claro. Desligado no escuro, na impressão e com prefers-reduced-transparency.",
               80, 14, 20, fill=C["ink-muted"])
    b += eyebrow(740, 40, "Cantos")
    for i, (nome, r) in enumerate((("control · 6", 6), ("thumb · 8", 8), ("card · 10", 10), ("pill", 26))):
        x = 740 + i * 155
        b += rect(x, 60, 135, 92 if r != 26 else 52, C["surface"], r, f'stroke="{C["border-strong"]}"')
        b += t(x, 180, nome, 14, 500, C["ink-muted"], fam="mono")
    b += eyebrow(740, 230, "Linhas")
    b += line(740, 260, 1360, 260, C["border"]) + t(740, 284, "hairline · Amêndoa · divisórias (1,4 : 1, decorativa)", 14, 400, C["ink-muted"])
    b += rect(740, 300, 300, 40, C["surface"], 6, f'stroke="{C["border-strong"]}"') + t(756, 326, "Campo", 15, 400, C["ink-subtle"])
    b += t(1060, 326, "Amêndoa Forte · controles (3,4 : 1)", 14, 400, C["ink-muted"])
    b += eyebrow(40, 390, "Profundidade")
    b += ('<defs><filter id="sh1" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="4" stdDeviation="8" '
          'flood-color="#232A22" flood-opacity=".08"/></filter><filter id="sh2" x="-20%" y="-20%" width="140%" height="170%">'
          '<feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#232A22" flood-opacity=".12"/></filter></defs>')
    niveis = [("Nível 0 · plano + hairline", "cartões, tabelas", ""), ("Nível 1 · popover, menu", "0 4 16 · 8%", 'filter="url(#sh1)"'),
              ("Nível 2 · diálogo, gaveta", "0 12 32 · 12%", 'filter="url(#sh2)"')]
    for i, (nome, sub, fx) in enumerate(niveis):
        x = 40 + i * 330
        b += rect(x, 420, 300, 150, C["surface"], 10, f'stroke="{C["border"]}" {fx}')
        b += t(x + 20, 460, nome, 15, 700, C["ink"]) + t(x + 20, 484, sub, 13, 400, C["ink-muted"], fam="mono")
    b += rect(1030, 420, 330, 150, D["canvas"], 10)
    b += rect(1050, 440, 290, 110, D["surface-muted"], 10)
    b += t(1070, 480, "Escuro · sem sombra", 15, 700, D["ink"]) + t(1070, 504, "profundidade por degraus de surface", 13, 400, D["ink-muted"])
    return add("elementos", "superficies", "Textura de papel, cantos, linhas e os três níveis de profundidade (e o escuro sem sombra).", W, Hh, b)


ICONES = [("heart-handshake", "Consenso favorito", "primary"), ("messages-square", "Conversar juntos", "attention-ink"),
          ("circle-alert", "Atenção · custo extra", "accent"), ("lock-open", "Destravado", "consensus-ink"),
          ("lock", "Bloqueado", "ink-muted"), ("circle-check", "Pago · concluído", "consensus-ink"),
          ("circle-arrow-right", "Próximo passo", "primary"), ("message-circle", "Abrir WhatsApp", "primary"),
          ("paperclip", "Anexo", "ink"), ("file-text", "PDF", "ink"), ("badge-check", "Orçamento oficial", "primary"),
          ("handshake", "Alternativa sem coração", "ink-muted")]


def build_iconografia():
    W, Hh = 1400, 640
    b = bg(W, Hh, C["canvas"])
    for i, (ic, nome, cor) in enumerate(ICONES):
        col, row = i % 6, i // 6
        x, y = 40 + col * 223, 30 + row * 200
        b += card(x, y, 207, 180)
        b += icon(ic, x + 24, y + 26, 40, C[cor])
        b += t(x + 24, y + 112, esc(nome), 15, 700, C["ink"])
        b += t(x + 24, y + 138, ic, 13, 400, C["ink-muted"], fam="mono")
    b += eyebrow(40, 470, "Tamanhos · traço 1,5 px em qualquer tamanho")
    for i, s in enumerate((16, 20, 24)):
        x = 40 + i * 120
        b += icon("circle-arrow-right", x, 500, s, C["ink"])
        b += t(x, 560, f"{s} px", 13, 500, C["ink-muted"], fam="mono")
    b += lines(460, 500, "Lucide, cantos arredondados, herdando currentColor. 20 px é o padrão; 16 em tabelas densas; 24 na navegação. "
                         "Ícone sempre acompanhado de texto: cor e ícone nunca são o único sinal.", 92, 15, 22, fill=C["ink"])
    return add("elementos", "iconografia", "Mapa semântico de ícones Lucide, tamanhos e regra de ícone + texto.", W, Hh, b)


def build_interface():
    W, Hh = 1400, 720
    b = bg(W, Hh, C["canvas"])
    b += eyebrow(40, 40, "Botões · altura 40 · raio 6")
    x = 40
    for s, k, ic in (("Registrar decisão", "primary", None), ("Comparar", "secondary", None), ("Cancelar", "ghost", None),
                     ("Arquivar proposta", "destrutivo", None), ("Abrir WhatsApp", "primary", "message-circle")):
        o, w = button(x, 60, s, k, ic=ic)
        b += o
        x += w + 20
    b += eyebrow(40, 150, "Campos · borda Amêndoa Forte · foco em anel duplo")
    b += t(40, 182, "Valor da proposta", 14, 600, C["ink"])
    b += rect(40, 192, 320, 44, C["surface"], 6, f'stroke="{C["border-strong"]}"') + t(56, 220, "R$ 0,00", 16, 400, C["ink-subtle"], fam="mono")
    b += t(400, 182, "Nome do fornecedor", 14, 600, C["ink"])
    b += rect(396, 188, 328, 52, "none", 9, f'stroke="{C["focus-ring"] if "focus-ring" in C else C["primary"]}" stroke-width="2"')
    b += rect(400, 192, 320, 44, C["surface"], 6, f'stroke="{C["border-strong"]}"') + t(416, 220, "Espaço Exemplo A", 16, 400, C["ink"])
    b += t(760, 220, "Em foco: anel de 2 px no primário, afastado 2 px do campo.", 14, 400, C["ink-muted"])

    b += eyebrow(40, 300, "Perfis e lente")
    x = 40
    for s in ("Noivo", "Noiva", "Ambos"):
        o, w = chip(x, 316, s, C["surface-muted"], C["ink"], h=28, size=13)
        b += o
        x += w + 10
    b += rect(320, 314, 300, 34, C["surface-sunken"], 8)
    b += rect(323, 317, 150, 28, C["surface"], 6, f'stroke="{C["border"]}"')
    b += t(398, 336, "Visão do Casal", 13, 600, C["ink"], "middle") + t(546, 336, "Minha visão", 13, 500, C["ink-muted"], "middle")

    b += eyebrow(40, 400, "Selos de consenso, divergência e custo real")
    x = 40
    for s, bg_, fg, ic in (("Favorito dos dois", C["consensus-bg"], C["consensus-ink"], "heart-handshake"),
                           ("Conversar juntos", C["attention-bg"], C["attention-ink"], "messages-square"),
                           ("+ R$ 1.200,00 em custos extras", C["attention-bg"], C["accent-ink"], "circle-alert"),
                           ("Destravado", C["consensus-bg"], C["consensus-ink"], "lock-open"),
                           ("Bloqueado por: Espaço", C["surface-sunken"], C["ink-muted"], "lock")):
        o, w = chip(x, 416, s, bg_, fg, ic, h=30, size=13)
        b += o
        x += w + 12

    b += eyebrow(40, 500, "Avaliação dupla")
    b += card(40, 516, 420, 150)
    for i, (p, nota, cls, chip_bg, chip_fg) in enumerate((("Noivo", "4 / 5", "Gostei", C["surface-muted"], C["ink"]),
                                                          ("Noiva", "5 / 5", "Favorito", C["consensus-bg"], C["consensus-ink"]))):
        y = 556 + i * 60
        b += t(64, y, p, 15, 600, C["ink"]) + t(170, y, nota, 18, 500, C["ink"], fam="mono")
        o, _ = chip(250, y - 19, cls, chip_bg, chip_fg, h=26, size=12.5)
        b += o
        if i == 0:
            b += line(64, y + 22, 436, y + 22, C["border"])
    b += eyebrow(500, 500, "Valor comparável")
    b += card(500, 516, 380, 150)
    b += t(524, 552, "Custo total comparável", 13, 600, C["ink-muted"])
    b += t(524, 592, "R$ 8.950,00", 26, 500, C["ink"], fam="mono")
    b += t(524, 626, "base R$ 7.750,00", 13, 400, C["ink-muted"], fam="mono")
    b += t(700, 626, "+ R$ 1.200,00 extras", 13, 500, C["accent-ink"], fam="mono")
    b += eyebrow(920, 500, "Decisão registrada")
    b += card(920, 516, 440, 150, C["consensus-bg"], C["consensus-bg"])
    b += f'<circle cx="970" cy="568" r="24" fill="{C["consensus-ink"]}"/>' + icon("check", 958, 556, 24, C["consensus-bg"], 2)
    b += t(1010, 562, "Decisão registrada", 20, 500, C["consensus-ink"], fam="serif")
    b += t(1010, 588, "Escolhido por vocês dois · motivo salvo", 13, 500, C["consensus-ink"])
    b += t(944, 640, "Único momento de deleite: o selo se assenta em 400 ms.", 13, 400, C["consensus-ink"])
    return add("elementos", "interface", "A marca na interface: botões, campos, perfis, lente, selos, avaliação dupla, valor e decisão.", W, Hh, b)


def build_estados():
    W, Hh = 1400, 600
    b = bg(W, Hh, C["canvas"])
    b += card(40, 30, 420, 300)
    b += ornamento("ramo-pequeno", 170, 64, 160, 64, cor=C["ink-muted"])
    b += t(250, 176, "Nada por aqui ainda.", 20, 500, C["ink"], "middle", "serif")
    b += lines(84, 206, "Que tal adicionar o primeiro contato desta categoria?", 44, 15, 22, fill=C["ink-muted"])
    o, w = button(250 - 95, 258, "Adicionar contato", "primary", w=190)
    b += o
    b += eyebrow(40, 360, "Vazio") + t(40, 384, "ornamento + frase acolhedora + 1 ação", 14, 400, C["ink-muted"])
    b += card(500, 30, 420, 300)
    for i, (w_, h_) in enumerate(((240, 18), (360, 12), (320, 12), (200, 12))):
        b += rect(530, 70 + i * 34 + (0 if i == 0 else 10), w_, h_, C["surface-sunken"], 6)
    b += rect(530, 240, 360, 60, C["surface-muted"], 8)
    b += eyebrow(500, 360, "Carregando") + t(500, 384, "skeleton em Champagne; sem spinner de tela cheia", 14, 400, C["ink-muted"])
    b += card(960, 30, 400, 135)
    b += rect(980, 52, 360, 52, C["consensus-bg"], 8) + icon("circle-check", 994, 66, 22, C["consensus-ink"])
    b += t(1026, 84, "Proposta salva.", 15, 600, C["consensus-ink"])
    b += t(980, 136, "toast de 4 s, Sálvia + ícone + texto", 13, 400, C["ink-muted"])
    b += card(960, 185, 400, 145)
    b += rect(980, 205, 360, 80, C["attention-bg"], 8) + icon("messages-square", 994, 221, 22, C["attention-ink"])
    b += lines(1026, 238, "Vocês avaliaram esta opção de forma diferente. Vale conversar antes de decidir.", 40, 14, 20, fill=C["attention-ink"])
    b += t(980, 310, "atenção em Argila, nunca vermelho", 13, 400, C["ink-muted"])
    b += eyebrow(960, 360, "Sucesso e atenção")
    b += line(40, 420, 1360, 420, C["border"])
    mov = [("motion-fast", "150 ms", "hover, foco, troca de aba"), ("motion-base", "220 ms", "gavetas, diálogos, popovers"),
           ("motion-delight", "400 ms", "só no selo de decisão registrada"), ("reduced-motion", "≤ 1 ms", "tudo vira fade instantâneo")]
    for i, (k, v, uso) in enumerate(mov):
        x = 40 + i * 335
        b += t(x, 460, k, 14, 600, C["ink"], fam="mono") + t(x, 492, v, 22, 500, C["primary"], fam="mono")
        b += t(x, 520, uso, 14, 400, C["ink-muted"])
    b += t(40, 570, "Sem bounce, parallax, confete, som ou animação em loop. Movimento só explica mudança de estado.", 15, 500, C["ink"])
    return add("elementos", "estados-e-movimento", "Estados (vazio, carregando, sucesso, atenção) e tokens de movimento.", W, Hh, b)


# ================================================================ aplicações

def favicon_body(s=64):
    r = s * ICON["raio_favicon"]
    cap = s * ICON["versal_favicon"]
    return rect(0, 0, s, s, C["primary"], round(r, 2)) + marca_centro("simbolo-pequeno", "marfim", s / 2, s / 2, cap)


def app_icon_body(s=1024):
    return rect(0, 0, s, s, C["primary"]) + marca_centro("simbolo", "marfim", s / 2, s / 2 + s * 0.01, s * ICON["versal_app"])


def _favicon(x, y, s):
    return f'<svg x="{x}" y="{y}" width="{s}" height="{s}" viewBox="0 0 64 64">{favicon_body()}</svg>'


def _app(x, y, s, rx_ratio=0.225):
    return (f'<svg x="{x}" y="{y}" width="{s}" height="{s}" viewBox="0 0 1024 1024"><clipPath id="ai{int(x)}{int(y)}">'
            f'<rect width="1024" height="1024" rx="{1024 * rx_ratio:.0f}"/></clipPath><g clip-path="url(#ai{int(x)}{int(y)})">'
            f'{app_icon_body()}</g></svg>')


def build_favicon_app():
    W, Hh = 1400, 700
    b = bg(W, Hh, C["canvas"])
    for i, (P, nome) in enumerate(((C, "Aba clara"), (D, "Aba escura"))):
        y = 40 + i * 150
        bar = "#E8E2D4" if P is C else "#0E120E"
        b += rect(40, y, 760, 110, bar, 12)
        b += rect(56, y + 36, 300, 74, P["surface"] if P is C else D["surface"], 10)
        b += _favicon(76, y + 60, 24)
        b += t(112, y + 78, "Altare · Visão geral", 15, 500, P["ink"])
        b += t(330, y + 78, "×", 16, 400, P["ink-muted"], "middle")
        b += rect(372, y + 52, 160, 40, "none", 10) + t(380, y + 78, "Nova aba", 15, 400, P["ink-muted"])
        b += t(40, y + 134, nome, 13, 600, C["ink-muted"])
    b += eyebrow(40, 380, "Favicon · quadrado oliva com raio de 22%")
    x = 40
    for s in (16, 32, 48, 64, 96):
        b += _favicon(x, 440 - s / 2 + 40, s)
        b += t(x + s / 2, 540, f"{s}", 13, 500, C["ink-muted"], "middle", "mono")
        x += s + 40
    b += lines(40, 590, "O favicon usa sempre o símbolo pequeno (mensa de 2 módulos), com versal de 43% do lado. Arquivos: favicon.svg, favicon.ico (16, 32, 48).",
               90, 14, 20, fill=C["ink-muted"])
    b += rect(880, 30, 460, 640, "#2E382D", 40)
    b += rect(896, 46, 428, 608, "#C9D3C1", 28)
    for i in range(12):
        col, row = i % 4, i // 4
        x, y = 924 + col * 100, 90 + row * 120
        if i == 5:
            b += _app(x, y, 72)
            b += t(x + 36, y + 94, "Altare", 13, 600, "#232A22", "middle")
        else:
            b += rect(x, y, 72, 72, "#E9EEE3" if i % 3 else "#DDE4D6", 16, 'opacity="0.85"')
    b += rect(1010, 600, 200, 6, "#232A22", 3, 'opacity=".35"')
    b += t(1110, 484, "Ícone do app: quadrado cheio; o sistema arredonda.", 14, 600, "#232A22", "middle")
    b += t(1110, 506, "Versal = 40% do lado, dentro da zona segura.", 13, 400, "#3A4439", "middle")
    return add("aplicacoes", "favicon-e-icone-de-app", "Favicon em aba clara e escura, tamanhos do favicon e ícone do app na tela inicial.", W, Hh, b)


def build_login():
    W, Hh = 1400, 860
    b = bg(W, Hh, C["canvas"]) + textura("tx-login", 0, 0, W, Hh, 0.035)
    b += ornamento("arco-duplo", 210, 150, 400, 563, cor=C["ink-muted"])
    b += marca_centro("vertical", "oliva", 410, 450, 118)
    b += ornamento("ramo-pequeno", 330, 640, 160, 64, cor=C["ink-muted"])
    b += card(800, 200, 440, 460, C["surface"], C["border"])
    b += t(840, 270, "Bem-vindos ao Altare.", 32, 500, C["ink"], fam="serif")
    b += t(840, 304, "Entre com o seu usuário.", 16, 400, C["ink-muted"])
    for i, (lab, ph) in enumerate((("Usuário", "noivo ou noiva"), ("Senha", "••••••••••"))):
        y = 350 + i * 92
        b += t(840, y, lab, 14, 600, C["ink"])
        b += rect(840, y + 10, 360, 46, C["surface"], 6, f'stroke="{C["border-strong"]}"')
        b += t(856, y + 40, ph, 16, 400, C["ink-subtle"])
    o, _ = button(840, 552, "Entrar", "primary", w=360, h=48, size=16)
    b += o
    b += t(1020, 630, "Acesso exclusivo do casal.", 13, 400, C["ink-muted"], "middle")
    b += t(700, 820, "Canvas Papel Areia com textura · arco duplo e ramo em Musgo a 70% · lockup vertical oliva · cartão Marfim",
           13, 400, C["ink-muted"], "middle")
    return add("aplicacoes", "tela-de-login", "Tela de login: textura, arco duplo, lockup vertical, ramo e formulário em cartão Marfim.", W, Hh, b)


AREAS = [("layout-dashboard", "Visão Geral"), ("map", "Planejamento & Caminhos"), ("calendar", "Cronograma & Dependências"),
         ("scale", "Possibilidades & Decisões"), ("wallet", "Orçamento & Simulador"), ("users", "Contatos & Fornecedores"),
         ("gift", "Convidados, Enxoval & Dia D")]


def _visao_geral(P, sfx, dark):
    W, Hh = 1400, 900
    b = bg(W, Hh, P["canvas"])
    if not dark:
        b += textura("tx-vg", 0, 0, W, Hh, 0.035)
    b += rect(0, 0, 256, Hh, P["surface"]) + line(256, 0, 256, Hh, P["border"])
    b += marca("wordmark", sfx, 28, 62, 26)
    for i, (ic, nome) in enumerate(AREAS):
        y = 104 + i * 46
        ativo = i == 0
        if ativo:
            b += rect(16, y - 4, 224, 40, P["surface-muted"], 6)
        cor = P["primary"] if ativo else P["ink-muted"]
        b += icon(ic, 30, y + 6, 20, cor)
        b += t(60, y + 21, esc(nome), 12, 600 if ativo else 500, P["ink"] if ativo else P["ink-muted"])
    b += line(16, 444, 240, 444, P["border"])
    b += t(30, 476, "Noivo", 14, 600, P["ink"]) + t(30, 496, "sessão individual", 12, 400, P["ink-muted"])

    b += line(256, 72, W, 72, P["border"])
    b += t(290, 44, "Visão geral", 15, 600, P["ink"])
    b += rect(1050, 20, 300, 34, P["surface-sunken"], 8)
    b += rect(1053, 23, 150, 28, P["surface"], 6, f'stroke="{P["border"]}"')
    b += t(1128, 42, "Visão do Casal", 13, 600, P["ink"], "middle") + t(1276, 42, "Minha visão", 13, 500, P["ink-muted"], "middle")
    o, _ = chip(890, 24, "conteúdo ilustrativo", P["surface-sunken"], P["ink-muted"], h=26, size=12, weight=500)
    b += o

    b += eyebrow(290, 120, "Visão geral", P["ink-muted"])
    b += t(290, 162, "O momento de vocês", 38, 500, P["ink"], fam="serif")
    b += t(290, 194, "O que já está definido, o que destravou e o que vem a seguir.", 16, 400, P["ink-muted"])
    b += line(290, 222, 1366, 222, P["border"])

    def cartao(x, y, w, h, titulo, ic=None, icor=None):
        o = card(x, y, w, h, P["surface"], P["border"])
        if ic:
            o += icon(ic, x + 20, y + 20, 20, icor or P["ink-muted"])
        o += t(x + (50 if ic else 20), y + 36, titulo, 20, 500, P["ink"], fam="serif")
        return o

    b += cartao(290, 246, 520, 250, "Definições base")
    for i, k in enumerate(("Data do casamento", "Cidade", "Convidados", "Estilo")):
        y = 300 + i * 46
        b += t(310, y + 18, k, 15, 500, P["ink"])
        o, _ = chip(650, y, "Em definição", P["surface-sunken"], P["ink-muted"], h=26, size=12.5, weight=500)
        b += o
        if i < 3:
            b += line(310, y + 34, 790, y + 34, P["border"])
    b += cartao(830, 246, 536, 250, "Destravado agora", "lock-open", P["consensus-ink"])
    for i, (tarefa, quem) in enumerate((("Visitar os espaços pré-selecionados", "Ambos"), ("Pedir propostas de gastronomia", "Noiva"),
                                        ("Definir o teto do primeiro cenário", "Noivo"))):
        y = 300 + i * 62
        b += t(850, y + 18, tarefa, 15, 500, P["ink"])
        b += t(850, y + 40, "Destravado por: escopo definido", 12.5, 400, P["ink-muted"])
        o, _ = chip(1260, y + 4, quem, P["surface-muted"], P["ink"], h=26, size=12.5)
        b += o
    b += cartao(290, 516, 520, 360, "Próximos passos", "circle-arrow-right", P["primary"])
    for i, (passo, quem, quando, forn) in enumerate((("Confirmar a visita", "Noivo", "sex.", "Espaço Exemplo A"),
                                                     ("Enviar dúvidas sobre o cardápio", "Noiva", "seg.", "Buffet Exemplo B"),
                                                     ("Pedir a proposta em PDF", "Ambos", "qua.", "Foto Exemplo C"))):
        y = 572 + i * 96
        b += t(310, y + 20, forn, 18, 500, P["ink"], fam="serif")
        b += t(310, y + 44, passo, 15, 400, P["ink-muted"])
        o, _ = chip(310, y + 56, quem, P["surface-muted"], P["ink"], h=24, size=12)
        b += o
        b += t(790, y + 20, quando, 14, 500, P["ink-muted"], "end", "mono")
        b += icon("message-circle", 762, y + 44, 20, P["primary"])
        if i < 2:
            b += line(310, y + 88, 790, y + 88, P["border"])
    b += cartao(830, 516, 536, 180, "Orçamento oficial", "badge-check", P["primary"])
    b += t(850, 600, "Nenhum cenário oficial ainda.", 16, 500, P["ink"])
    b += t(850, 624, "Crie um cenário e promova-o a oficial quando quiserem.", 14, 400, P["ink-muted"])
    o, _ = button(850, 640, "Criar primeiro cenário", "secondary", P=P, h=38, size=14)
    b += o
    b += cartao(830, 716, 536, 160, "Comparativos em aberto", "scale", P["ink-muted"])
    for i, (cat, info, txt, bg_, fg, ic) in enumerate((("Espaço", "3 propostas", "Conversar juntos", P["attention-bg"], P["attention-ink"], "messages-square"),
                                                       ("Fotografia", "2 propostas", "Favorito dos dois", P["consensus-bg"], P["consensus-ink"], "heart-handshake"))):
        y = 770 + i * 50
        b += t(850, y + 18, cat, 17, 500, P["ink"], fam="serif") + t(980, y + 18, info, 14, 400, P["ink-muted"], fam="mono")
        o, _ = chip(1150, y, txt, bg_, fg, ic, h=28, size=12.5)
        b += o
    return W, Hh, b


def build_visao_geral():
    W, Hh, b = _visao_geral(C, "oliva", False)
    add("aplicacoes", "visao-geral", "Visão Geral no desktop: barra lateral, lente, definições em aberto, destravados e próximos passos.", W, Hh, b)
    W, Hh, b = _visao_geral(D, "salvia", True)
    add("aplicacoes", "tema-escuro", "A mesma Visão Geral no tema escuro Noite Oliva: sem textura e sem sombra.", W, Hh, b)


def _phone(x, y, inner, P=C):
    w, h = 360, 760
    return (rect(x, y, w, h, "#232A22", 48) + f'<svg x="{x + 12}" y="{y + 12}" width="{w - 24}" height="{h - 24}" viewBox="0 0 336 736">'
            f'<clipPath id="ph{x}"><rect width="336" height="736" rx="38"/></clipPath><g clip-path="url(#ph{x})">{inner}</g></svg>')


def build_mobile():
    W, Hh = 1400, 860
    b = bg(W, Hh, C["canvas"])
    P = C
    s = rect(0, 0, 336, 736, P["canvas"])
    s += t(28, 34, "9:41", 13, 600, P["ink"], fam="mono")
    s += marca("simbolo", "oliva", 38, 82, 22) + t(64, 84, "Visão geral", 16, 600, P["ink"])
    s += icon("search", 290, 66, 20, P["ink-muted"])
    s += line(0, 106, 336, 106, P["border"])
    s += eyebrow(20, 136, "Meus próximos passos")
    for i, (forn, passo, quando) in enumerate((("Espaço Exemplo A", "Confirmar a visita", "sex."), ("Foto Exemplo C", "Pedir a proposta em PDF", "qua."))):
        y = 152 + i * 156
        s += card(16, y, 304, 140, P["surface"], P["border"])
        s += t(32, y + 32, forn, 18, 500, P["ink"], fam="serif") + t(304, y + 32, quando, 13, 500, P["ink-muted"], "end", "mono")
        s += t(32, y + 56, passo, 14, 400, P["ink-muted"])
        o, _ = button(32, y + 78, "Abrir WhatsApp", "secondary", w=272, h=44, size=14, ic="message-circle")
        s += o
    s += eyebrow(20, 490, "Próximos pagamentos")
    s += card(16, 506, 304, 86, P["surface"], P["border"])
    s += t(32, 540, "Nenhuma parcela cadastrada.", 14, 500, P["ink"]) + t(32, 562, "Aparecem aqui ao registrar um contrato.", 12.5, 400, P["ink-muted"])
    s += rect(176, 600, 144, 48, P["primary"], 24) + icon("plus", 192, 614, 20, C["primary-ink"]) + t(218, 630, "Registrar", 14, 600, C["primary-ink"])
    s += rect(0, 664, 336, 72, P["surface"]) + line(0, 664, 336, 664, P["border"])
    for i, (ic, nome) in enumerate((("house", "Início"), ("scale", "Possib."), ("wallet", "Orçam."), ("users", "Contatos"), ("ellipsis", "Mais"))):
        x = 34 + i * 67
        cor = P["primary"] if i == 0 else P["ink-muted"]
        s += icon(ic, x - 11, 678, 22, cor) + t(x, 716, nome, 11, 600 if i == 0 else 500, cor, "middle")
    b += _phone(260, 50, s)

    s = rect(0, 0, 336, 736, P["canvas"])
    s += t(28, 34, "9:41", 13, 600, P["ink"], fam="mono")
    s += icon("chevron-left", 20, 66, 20, P["ink-muted"]) + t(48, 82, "Contatos", 14, 500, P["ink-muted"])
    s += line(0, 106, 336, 106, P["border"])
    s += eyebrow(20, 136, "Gastronomia")
    s += t(20, 172, "Buffet Exemplo B", 26, 500, P["ink"], fam="serif")
    o, _ = chip(20, 186, "Proposta recebida", P["surface-sunken"], P["ink-muted"], h=26, size=12, weight=500)
    s += o
    s += card(16, 228, 304, 132, P["surface"], P["border"])
    s += icon("circle-arrow-right", 32, 246, 20, P["primary"]) + t(60, 262, "Próximo passo", 13, 600, P["ink-muted"])
    s += t(32, 292, "Enviar dúvidas sobre o cardápio", 15, 600, P["ink"]) + t(32, 314, "Noiva · até seg.", 13, 400, P["ink-muted"])
    o, _ = button(32, 324, "Abrir WhatsApp", "primary", w=272, h=28, size=13, ic="message-circle")
    s += o
    s += eyebrow(20, 394, "Arquivos")
    s += card(16, 408, 304, 56, P["surface"], P["border"]) + icon("file-text", 32, 426, 20, P["ink"])
    s += t(62, 441, "Proposta-cardapio.pdf", 14, 500, P["ink"]) + icon("paperclip", 286, 426, 18, P["ink-muted"])
    s += eyebrow(20, 498, "Avaliações")
    s += card(16, 512, 304, 120, P["surface"], P["border"])
    for i, (p, nota, cls, cb, cf) in enumerate((("Noivo", "3 / 5", "Com ressalvas", P["attention-bg"], P["attention-ink"]),
                                                ("Noiva", "5 / 5", "Favorito", P["consensus-bg"], P["consensus-ink"]))):
        y = 548 + i * 52
        s += t(32, y, p, 14, 600, P["ink"]) + t(100, y, nota, 15, 500, P["ink"], fam="mono")
        o, _ = chip(170, y - 18, cls, cb, cf, h=24, size=12)
        s += o
    s += rect(16, 650, 304, 62, P["attention-bg"], 10) + icon("messages-square", 30, 668, 20, P["attention-ink"])
    s += lines(60, 676, "Vocês avaliaram de forma diferente. Vale conversar.", 34, 12.5, 17, fill=P["attention-ink"])
    b += _phone(780, 50, s)
    b += t(700, 840, "Mobile: barra inferior com 4 destinos + Mais, botão flutuante Registrar, WhatsApp em 1 toque · conteúdo ilustrativo",
           13, 400, C["ink-muted"], "middle")
    return add("aplicacoes", "mobile", "Mobile: próximos passos com WhatsApp, botão Registrar e detalhe de fornecedor com avaliação dupla.", W, Hh, b)


def build_comparador():
    W, Hh = 1400, 860
    P = C
    b = bg(W, Hh, P["canvas"]) + textura("tx-cmp", 0, 0, W, Hh, 0.035)
    b += eyebrow(40, 50, "Possibilidades · Espaço")
    b += t(40, 94, "Comparar propostas", 38, 500, P["ink"], fam="serif")
    b += t(40, 126, "Custo total comparável = preço base + itens que faltam + custos ocultos.", 16, 400, P["ink-muted"])
    o, _ = chip(1180, 30, "valores ilustrativos", P["surface-sunken"], P["ink-muted"], h=26, size=12, weight=500)
    b += o
    b += line(40, 152, 1360, 152, P["border"])
    cols = [("Espaço Exemplo A", "7.750,00", [("Mobiliário extra", "1.200,00")], "8.950,00",
             ("4 / 5", "Gostei", P["surface-muted"], P["ink"]), ("5 / 5", "Favorito", P["consensus-bg"], P["consensus-ink"]),
             ("Conversar juntos", P["attention-bg"], P["attention-ink"], "messages-square")),
            ("Espaço Exemplo B", "9.400,00", [], "9.400,00",
             ("5 / 5", "Favorito", P["consensus-bg"], P["consensus-ink"]), ("5 / 5", "Favorito", P["consensus-bg"], P["consensus-ink"]),
             ("Favorito dos dois", P["consensus-bg"], P["consensus-ink"], "heart-handshake")),
            ("Espaço Exemplo C", "6.900,00", [("Taxa de limpeza", "650,00"), ("Gerador", "1.100,00")], "8.650,00",
             ("2 / 5", "Com ressalvas", P["attention-bg"], P["attention-ink"]), ("3 / 5", "Gostei", P["surface-muted"], P["ink"]),
             ("Pouco interesse", P["surface-sunken"], P["ink-muted"], "lock"))]
    rows_y = {"base": 260, "extras": 310, "total": 420, "noivo": 500, "noiva": 556, "sit": 624, "pdf": 690}
    labels = [("base", "Preço base"), ("extras", "Custos adicionais"), ("total", "Custo comparável"), ("noivo", "Noivo"),
              ("noiva", "Noiva"), ("sit", "Situação"), ("pdf", "Anexos")]
    for k, lab in labels:
        b += t(40, rows_y[k], lab, 14, 600, P["ink-muted"])
    for i, (nome, base, extras, total, rn, rv, sit, ) in enumerate(cols):
        x = 260 + i * 370
        b += card(x, 172, 350, 650, P["surface"], P["border"])
        b += t(x + 24, 214, nome, 22, 500, P["ink"], fam="serif")
        b += line(x + 24, 232, x + 326, 232, P["border"])
        b += t(x + 326, rows_y["base"], f"R$ {base}", 16, 400, P["ink"], "end", "mono")
        if extras:
            for j, (en, ev) in enumerate(extras):
                y = rows_y["extras"] + j * 30
                b += icon("circle-alert", x + 24, y - 15, 18, P["accent"]) + t(x + 50, y, en, 14, 500, P["ink"])
                b += t(x + 326, y, f"+ R$ {ev}", 15, 500, P["accent-ink"], "end", "mono")
        else:
            b += t(x + 24, rows_y["extras"], "Nenhum: tudo incluso", 14, 500, P["consensus-ink"])
        b += rect(x + 12, rows_y["total"] - 40, 326, 60, P["surface-muted"], 8)
        b += t(x + 326, rows_y["total"], f"R$ {total}", 24, 500, P["ink"], "end", "mono")
        for k, (nota, cls, cb, cf) in (("noivo", rn), ("noiva", rv)):
            b += t(x + 24, rows_y[k], nota, 17, 500, P["ink"], fam="mono")
            o, _ = chip(x + 110, rows_y[k] - 19, cls, cb, cf, h=26, size=12.5)
            b += o
        st, sb, sf, si = sit
        o, _ = chip(x + 24, rows_y["sit"] - 20, st, sb, sf, si, h=30, size=13)
        b += o
        b += icon("file-text", x + 24, rows_y["pdf"] - 16, 20, P["ink"]) + t(x + 52, rows_y["pdf"], "proposta.pdf", 14, 500, P["ink"])
        o, _ = button(x + 24, 744, "Registrar decisão" if i == 1 else "Comparar detalhes", "primary" if i == 1 else "secondary", w=302, h=44)
        b += o
    return add("aplicacoes", "comparador", "Comparador de propostas: custo comparável, custos extras em terracota, avaliação dupla e situação.", W, Hh, b)


def build_dossie():
    W, Hh = 1400, 1000
    b = bg(W, Hh, C["surface-sunken"])
    s = 1.12
    pw, ph = 595 * s, 842 * s
    X, Y = 140, (Hh - ph) / 2
    b += rect(X, Y, pw, ph, "#FFFFFF", 2, 'stroke="#D9D2C2"')
    ink, borda = "#232A22", "#8F846F"
    cx = X + pw / 2
    b += marca_centro("assinatura", "carvao", cx, Y + 70, 16)
    b += line(cx - 120, Y + 96, cx + 120, Y + 96, borda)
    b += eyebrow(cx, Y + 122, "Dossiê do Dia D", ink, "middle")
    b += ornamento("arcada", cx - 120, Y + 140, 240, 42, cor="#5C6158")
    y = Y + 230
    b += t(X + 56, y, "Visão geral do dia", 22, 500, ink, fam="serif")
    b += line(X + 56, y + 14, X + pw - 56, y + 14, borda)
    for i, k in enumerate(("Data", "Cerimônia", "Recepção", "Cerimonial do dia", "Contato de emergência")):
        yy = y + 48 + i * 34
        b += t(X + 56, yy, k, 13, 600, "#5C6158") + t(X + 240, yy, "[a definir]", 13, 400, ink, fam="mono")
        b += line(X + 56, yy + 12, X + pw - 56, yy + 12, "#DFD5C3")
    y += 260
    b += t(X + 56, y, "Fornecedores contratados", 22, 500, ink, fam="serif")
    b += line(X + 56, y + 14, X + pw - 56, y + 14, borda)
    hx = [X + 56, X + 236, X + 386, X + 476]
    for hxi, h_ in zip(hx, ("Fornecedor", "Contato", "Chegada", "Observações críticas")):
        b += t(hxi, y + 44, h_.upper(), 10.5, 700, "#5C6158", ls=0.08)
    for i in range(4):
        yy = y + 78 + i * 40
        b += t(hx[0], yy, "[fornecedor contratado]", 13, 500, ink, fam="serif")
        b += t(hx[1], yy, "[telefone]", 12, 400, ink, fam="mono") + t(hx[2], yy, "[hh:mm]", 12, 400, ink, fam="mono")
        b += t(hx[3], yy, "[a definir]", 12, 400, ink)
        b += line(X + 56, yy + 14, X + pw - 56, yy + 14, "#DFD5C3")
    b += line(X + 56, Y + ph - 60, X + pw - 56, Y + ph - 60, "#DFD5C3")
    b += t(X + 56, Y + ph - 36, "Gerado pelo Altare em [data de geração]", 11, 400, "#5C6158")
    b += t(X + pw - 56, Y + ph - 36, "1 / N", 11, 400, "#5C6158", "end", "mono")
    notas = [("Papel branco, sem fundo", "Economia de tinta e leitura em preto e branco."),
             ("Assinatura formal + arcada", "ALTARE em versal, hairline e o título do documento."),
             ("Serifa nos títulos, mono nos dados", "Horários, telefones e valores sempre tabulares."),
             ("Bordas Amêndoa Forte", "#8F846F garante leitura em fotocópia."),
             ("Uma seção por página", "Quebra de página por fornecedor no documento final."),
             ("Campos vazios explícitos", "[a definir] até o casal preencher. Nada é inventado.")]
    for i, (k, v) in enumerate(notas):
        y = 180 + i * 120
        b += f'<circle cx="{X + pw + 70}" cy="{y - 6}" r="13" fill="{C["primary"]}"/>' + t(X + pw + 70, y - 1, str(i + 1), 13, 700, C["primary-ink"], "middle", "mono")
        b += t(X + pw + 96, y, k, 18, 700, C["ink"]) + lines(X + pw + 96, y + 26, v, 44, 15, 22, fill=C["ink-muted"])
    return add("aplicacoes", "dossie-do-dia-d", "Dossiê do Dia D em A4: assinatura formal, arcada, seções com campos a definir e notas de impressão.", W, Hh, b)


# ================================================================ registro

def build_all(rasters):
    REG.clear()
    build_conceito()
    build_anatomia()
    build_grade()
    build_lockups()
    build_versao_pequena(rasters)
    build_area_de_respiro()
    build_tamanho_minimo(rasters)
    build_versoes_de_cor()
    build_incorretos()
    build_paletas()
    build_familias()
    build_hierarquia()
    build_especime()
    build_numeros()
    build_arco()
    build_ramo()
    build_superficies()
    build_iconografia()
    build_interface()
    build_estados()
    build_favicon_app()
    build_login()
    build_visao_geral()
    build_mobile()
    build_comparador()
    build_dossie()
    return REG
