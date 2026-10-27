"""Base do gerador da identidade visual do Altare: tokens, contraste WCAG, fontes embutidas, marca, texto e ícones em SVG.

Tudo parte de ../tokens.json (valores) e de ../fonte/ (desenho da marca). Nada aqui redesenha a marca.
"""
import base64
import io
import json
import math
import re
from functools import lru_cache
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

BUILD = Path(__file__).resolve().parent
ROOT = BUILD.parent
FONTE = ROOT / "fonte"
COMP = ROOT / "componentes"
ASSETS = BUILD / "assets"
TOKENS = json.loads((ROOT / "tokens.json").read_text())
MED = json.loads((BUILD / "medidas.json").read_text())
VERSAO = f"versão {TOKENS['versao']} · {TOKENS['data']}"

# ---------------------------------------------------------------- tokens

CLARO = TOKENS["claro"]
ESCURO = TOKENS["escuro"]
C = {t["token"]: t["hex"] for t in CLARO}
D = {t["token"]: t["hex"] for t in ESCURO}
A = TOKENS["apoio"]
C["primary-ink"] = A["primary-ink"]
C["branco"], C["preto"] = A["branco"], A["preto"]
VERSOES = TOKENS["marca"]["versoes"]
GEO = TOKENS["marca"]["geometria"]
MIN = TOKENS["marca"]["minimos"]
ICON = TOKENS["marca"]["app_icon"]
NOME = {t["hex"]: t["nome"] for t in CLARO}


def rgb(hx):
    return tuple(int(hx[i:i + 2], 16) for i in (1, 3, 5))


def cmyk(hx):
    """Conversão ingênua RGB→CMYK (sem perfil de cor). Só aproximação: confirmar em prova."""
    r, g, b = (v / 255 for v in rgb(hx))
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 100)
    return tuple(round(100 * (1 - v - k) / (1 - k)) for v in (r, g, b)) + (round(100 * k),)


def luminance(hx):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb(hx))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def grade(ratio):
    if ratio >= 7:
        return "AAA"
    if ratio >= 4.5:
        return "AA"
    if ratio >= 3:
        return "AA grande"
    return "falha"


def trunc1(ratio):
    """Trunca (não arredonda): 4,47 vira 4,4, para nunca exibir como aprovado um par que reprova."""
    return math.floor(ratio * 10) / 10


def fmt(ratio):
    return f"{trunc1(ratio):.1f}".replace(".", ",") + " : 1"


def dec(v, n=1):
    return f"{v:.{n}f}".replace(".", ",")


# ---------------------------------------------------------------- fontes (subconjunto woff2 embutido)

FAMILIAS = {
    "serif": '"Newsreader", Georgia, serif',
    "sans": '"Plus Jakarta Sans", system-ui, sans-serif',
    "mono": '"JetBrains Mono", ui-monospace, monospace',
}
_ARQ = [  # (arquivo, família CSS, faixa de peso, estilo, marcador de uso no SVG)
    ("Newsreader-VF.ttf", "Newsreader", "200 800", "normal", "Newsreader"),
    ("Newsreader-Italic-VF.ttf", "Newsreader", "200 800", "italic", 'font-style="italic"'),
    ("PlusJakartaSans-VF.ttf", "Plus Jakarta Sans", "200 800", "normal", "Plus Jakarta"),
    ("JetBrainsMono-VF.ttf", "JetBrains Mono", "100 800", "normal", "JetBrains"),
]
_UNI = (list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + [0x152, 0x153, 0x2013, 0x2014, 0x2018, 0x2019, 0x201A,
        0x201C, 0x201D, 0x201E, 0x2022, 0x2026, 0x2032, 0x2033, 0x2039, 0x203A, 0x2190, 0x2191, 0x2192, 0x2193, 0x2212,
        0x2248, 0x2260, 0x2264, 0x2265, 0x00D7, 0x2715, 0x2713, 0x2197, 0x2198])


@lru_cache(maxsize=None)
def _woff2_b64(arquivo):
    f = TTFont(ASSETS / "fontes" / arquivo)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=_UNI)
    sub.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def font_face(body=None):
    """@font-face das famílias usadas em `body` (todas, se body for None)."""
    css = ""
    for arquivo, fam, peso, estilo, marca in _ARQ:
        if body is not None and marca not in body:
            continue
        if body is not None and estilo == "italic" and "Newsreader" not in body:
            continue
        css += (f'@font-face{{font-family:"{fam}";src:url(data:font/woff2;base64,{_woff2_b64(arquivo)}) format("woff2");'
                f'font-weight:{peso};font-style:{estilo}}}')
    return css


# ---------------------------------------------------------------- marca (mestres de ../fonte/)

H = MED["H"]


@lru_cache(maxsize=None)
def read_svg(rel):
    s = (FONTE / rel).read_text()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    inner = re.sub(r"<title[^>]*>.*?</title>", "", s)
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", inner.strip())
    return vb, inner


def place(rel, x, y, w=None, h=None, extra="", recolor=None):
    """<svg> aninhado com o viewBox do próprio arquivo: o desenho nunca é alterado, só posicionado e escalado."""
    vb, inner = read_svg(rel)
    if w is None:
        w = h * vb[2] / vb[3]
    if h is None:
        h = w * vb[3] / vb[2]
    if recolor:
        for a, b in recolor.items():
            inner = inner.replace(a, b)
    return (f'<svg x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}" overflow="visible" {extra}>{inner}</svg>')


def marca(peca, sfx, ox, oy, cap, extra="", recolor=None):
    """Posiciona uma peça pela origem do desenho (linha de base do A; no wordmark, início da linha de base).
    `cap` é a altura de versal desejada do A (no vertical, do A do símbolo), em px."""
    rel = f"altare-{peca}-{sfx}.svg"
    vb, _ = read_svg(rel)
    s = cap / H
    return place(rel, ox + vb[0] * s, oy + vb[1] * s, vb[2] * s, vb[3] * s, extra, recolor)


def caixa(peca, cap):
    """Caixa de tinta (x0, y0, x1, y1) da peça relativa à origem, na escala de `cap`."""
    vb, _ = read_svg(f"altare-{peca}-oliva.svg")
    s = cap / H
    return vb[0] * s, vb[1] * s, (vb[0] + vb[2]) * s, (vb[1] + vb[3]) * s


def marca_centro(peca, sfx, cx, cy, cap, **kw):
    """Centraliza a caixa de tinta da peça em (cx, cy)."""
    x0, y0, x1, y1 = caixa(peca, cap)
    return marca(peca, sfx, cx - (x0 + x1) / 2, cy - (y0 + y1) / 2, cap, **kw)


def ornamento(nome, x, y, w=None, h=None, cor=None, opacidade=None):
    rec = {}
    if cor:
        rec['stroke="#5C6158"'] = f'stroke="{cor}"'
    if opacidade is not None:
        rec['opacity="0.7"'] = f'opacity="{opacidade}"'
    return place(f"ornamentos/{nome}.svg", x, y, w, h, recolor=rec or None)


def cor_da_versao(sfx):
    return next(v for v in VERSOES if v["sufixo"] == sfx)


# ---------------------------------------------------------------- texto em SVG

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size=16, weight=400, fill=None, anchor="start", fam="sans", ls=0, extra=""):
    fill = fill or C["ink"]
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family=\'{FAMILIAS[fam]}\' font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}em" {extra}>{s}</text>')


def wrap(s, n):
    out, line = [], ""
    for w in s.split():
        if len(line) + len(w) + 1 > n and line:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    return out + ([line] if line else [])


def lines(x, y, s, n, size, lh, **kw):
    return "".join(t(x, y + i * lh, esc(l), size, **kw) for i, l in enumerate(wrap(s, n)))


def rect(x, y, w, h, fill, rx=0, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" {extra}/>'


def line(x1, y1, x2, y2, stroke, sw=1, extra=""):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


# ---------------------------------------------------------------- ícones Lucide (traço 1,5 px no tamanho de uso)

@lru_cache(maxsize=None)
def _icon_inner(nome):
    s = (ASSETS / "icones" / f"{nome}.svg").read_text()
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    return re.sub(r"^\s*<svg[^>]*>|</svg>\s*$", "", s.strip(), flags=re.S).strip()


def icon(nome, x, y, size=20, cor=None, sw=1.5):
    k = size / 24
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})" fill="none" stroke="{cor or C["ink"]}" '
            f'stroke-width="{sw / k:.3f}" stroke-linecap="round" stroke-linejoin="round">{_icon_inner(nome)}</g>')


def icones_disponiveis():
    return sorted(p.stem for p in (ASSETS / "icones").glob("*.svg"))
