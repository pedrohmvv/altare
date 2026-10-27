"""Gera os SVGs-mestre da marca em ../fonte/ a partir dos contornos reais da Newsreader e da geometria de tokens.json.

Os mestres são a única origem do desenho da marca: componentes e documento só posicionam e recolorem.
Depois de aprovados, os mestres podem ser refinados à mão; a partir daí, não rode mais `build.py --marca`.
"""
import io
import json
import math
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

BUILD = Path(__file__).resolve().parent
ROOT = BUILD.parent
FONTE = ROOT / "fonte"
TOKENS = json.loads((ROOT / "tokens.json").read_text())
G = TOKENS["marca"]["geometria"]
VERSOES = TOKENS["marca"]["versoes"]
NEWSREADER = BUILD / "assets" / "fontes" / "Newsreader-VF.ttf"

H = 200.0                                   # altura de versal do A nos mestres, em unidades do viewBox
M = H / G["altura_de_versal_modulos"]       # módulo


def num(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Fonte:
    """Instância estática (wght, opsz) da Newsreader, com shaping HarfBuzz (kerning) e contornos em SVG."""

    def __init__(self, path, wght, opsz):
        inst = instancer.instantiateVariableFont(TTFont(path), {"wght": wght, "opsz": opsz})
        buf = io.BytesIO()
        inst.save(buf)
        data = buf.getvalue()
        self.tt = TTFont(io.BytesIO(data))
        self.upm = self.tt["head"].unitsPerEm
        self.cap = self.tt["OS/2"].sCapHeight
        self.xh = self.tt["OS/2"].sxHeight
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.hb = hb.Font(hb.Face(data))

    def shape(self, text, tracking=0.0):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": False})
        out, x = [], 0.0
        n = len(buf.glyph_infos)
        for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
            out.append((self.order[info.codepoint], x + pos.x_offset, pos.y_offset))
            x += pos.x_advance + (tracking * self.upm if i < n - 1 else 0)
        return out

    def outline(self, text, cap_px, tracking=0.0, dx=0.0, dy=0.0):
        """Contorno com linha de base em y=dy (y para baixo) e versal = cap_px. Retorna (d, caixa de tinta)."""
        s = cap_px / self.cap
        parts, xs, ys = [], [], []
        for name, gx, gy in self.shape(text, tracking):
            pen = SVGPathPen(self.gs, ntos=num)
            self.gs[name].draw(TransformPen(pen, (s, 0, 0, -s, dx + gx * s, dy - gy * s)))
            parts.append(pen.getCommands())
            bp = BoundsPen(self.gs)
            self.gs[name].draw(bp)
            if bp.bounds:
                x0, y0, x1, y1 = bp.bounds
                xs += [dx + (gx + x0) * s, dx + (gx + x1) * s]
                ys += [dy - (gy + y1) * s, dy - (gy + y0) * s]
        return " ".join(parts), (min(xs), min(ys), max(xs), max(ys))


def rect_d(x, y, w, h):
    return f"M{num(x)} {num(y)}H{num(x + w)}V{num(y + h)}H{num(x)}Z"


def simbolo_d(f, cap, cx=0.0, base=0.0, pequeno=False):
    """A sobre a mensa: o A centrado em cx com linha de base em `base`; a mensa abaixo, na folga definida."""
    m = cap / G["altura_de_versal_modulos"]
    folga = G["pequeno_folga_modulos" if pequeno else "folga_modulos"] * m
    esp = G["pequeno_espessura_mensa_modulos" if pequeno else "espessura_mensa_modulos"] * m
    larg = G["largura_mensa_modulos"] * m
    _, (ax0, _, ax1, _) = f.outline("A", cap)
    d_a, box = f.outline("A", cap, dx=cx - (ax0 + ax1) / 2, dy=base)
    d = d_a + " " + rect_d(cx - larg / 2, base + folga, larg, esp)
    return d, (min(box[0], cx - larg / 2), box[1], max(box[2], cx + larg / 2), base + folga + esp)


def svg(box, paths, title="Altare"):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(x0)} {num(y0)} {num(w)} {num(h)}" '
            f'width="{num(w)}" height="{num(h)}" role="img" aria-labelledby="t"><title id="t">{title}</title>{paths}</svg>\n')


# ---------------------------------------------------------------- ornamentos

ORN = "#5C6158"


def arco_d(x, y, w, h):
    r = w / 2
    return f"M{num(x)} {num(y + h)}V{num(y + r)}A{num(r)} {num(r)} 0 0 1 {num(x + w)} {num(y + r)}V{num(y + h)}"


def ornamento_svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num(w)} {num(h)}" width="{num(w)}" height="{num(h)}" '
            f'role="img" aria-labelledby="t"><title id="t">{title}</title>'
            f'<g fill="none" stroke="{ORN}" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" '
            f'vector-effect="non-scaling-stroke" opacity="0.7">{body}</g></svg>\n')


def _bez(p, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    u = 1 - t
    x = u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3
    y = u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3
    dx = 3 * u * u * (x1 - x0) + 6 * u * t * (x2 - x1) + 3 * t * t * (x3 - x2)
    dy = 3 * u * u * (y1 - y0) + 6 * u * t * (y2 - y1) + 3 * t * t * (y3 - y2)
    return x, y, math.atan2(dy, dx)


def _folha(x, y, ang, comp, larg, nervura):
    tx, ty = x + comp * math.cos(ang), y + comp * math.sin(ang)
    mx, my = (x + tx) / 2, (y + ty) / 2
    nx, ny = -math.sin(ang) * larg, math.cos(ang) * larg
    d = (f'<path d="M{num(x)} {num(y)}Q{num(mx + nx)} {num(my + ny)} {num(tx)} {num(ty)}'
         f'Q{num(mx - nx)} {num(my - ny)} {num(x)} {num(y)}Z"/>')
    if nervura:
        ex, ey = x + 0.72 * comp * math.cos(ang), y + 0.72 * comp * math.sin(ang)
        d += f'<path d="M{num(x)} {num(y)}L{num(ex)} {num(ey)}"/>'
    return d


def ramo(p, n_folhas, comp0, nervura=True, azeitonas=(), espelho=False):
    """Ramo de oliveira em traço único: haste em Bézier, folhas alternadas que diminuem até a ponta."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    body = (f'<path d="M{num(x0)} {num(y0)}C{num(x1)} {num(y1)} {num(x2)} {num(y2)} {num(x3)} {num(y3)}"/>')
    for i in range(n_folhas):
        t = 0.10 + 0.82 * i / max(n_folhas - 1, 1)
        x, y, a = _bez(p, t)
        lado = 1 if i % 2 == 0 else -1
        if espelho:
            lado = -lado
        comp = comp0 * (1 - 0.38 * t)
        body += _folha(x, y, a + lado * math.radians(38), comp, comp * 0.24, nervura)
    x, y, a = _bez(p, 1.0)
    body += _folha(x, y, a, comp0 * 0.55, comp0 * 0.55 * 0.24, nervura)
    for t, lado in azeitonas:
        x, y, a = _bez(p, t)
        px, py = x + 10 * math.cos(a + lado * math.radians(80)), y + 10 * math.sin(a + lado * math.radians(80))
        cx, cy = px + 7 * math.cos(a + lado * math.radians(80)), py + 7 * math.sin(a + lado * math.radians(80))
        body += f'<path d="M{num(x)} {num(y)}L{num(px)} {num(py)}"/>'
        body += (f'<ellipse cx="{num(cx)}" cy="{num(cy)}" rx="5.2" ry="7.2" '
                 f'transform="rotate({num(math.degrees(a + lado * math.radians(80)) - 90)} {num(cx)} {num(cy)})"/>')
    return body


def ornamentos():
    out = {}
    out["arco-simples"] = ornamento_svg(142, 200, f'<path d="{arco_d(1, 1, 140, 198)}"/>', "Arco de volta perfeita")
    out["arco-duplo"] = ornamento_svg(142, 200, f'<path d="{arco_d(1, 1, 140, 198)}"/><path d="{arco_d(11, 11, 120, 188)}"/>',
                                      "Arco de volta perfeita, linha dupla")
    arcada = "".join(f'<path d="{arco_d(1 + i * 48, 1, 40, 56)}"/>' for i in range(7)) + '<path d="M1 57H329"/>'
    out["arcada"] = ornamento_svg(330, 58, arcada, "Arcada: faixa de arcos para cabeçalhos impressos")
    out["ramo-grande"] = ornamento_svg(320, 120, ramo(((8, 100), (90, 70), (200, 20), (312, 26)), 11, 46,
                                                     azeitonas=((0.42, 1), (0.66, -1))), "Ramo de oliveira")
    out["ramo-pequeno"] = ornamento_svg(160, 64, ramo(((6, 54), (50, 40), (100, 14), (154, 14)), 6, 30, nervura=False),
                                        "Ramo de oliveira, pequeno")
    esq = ramo(((150, 30), (110, 22), (60, 16), (6, 26)), 7, 30, nervura=False)
    dir_ = ramo(((170, 30), (210, 22), (260, 16), (314, 26)), 7, 30, nervura=False, espelho=True)
    out["ramo-faixa"] = ornamento_svg(320, 56, esq + dir_ + '<circle cx="160" cy="30" r="2.2"/>', "Faixa de ramos de oliveira")
    return out


# ---------------------------------------------------------------- mestres

def gerar():
    FONTE.mkdir(parents=True, exist_ok=True)
    for old in FONTE.glob("*.svg"):
        old.unlink()
    f = Fonte(NEWSREADER, 500, 72)
    k = H / f.cap

    sym_d, sym_box = simbolo_d(f, H)
    sym_p_d, sym_p_box = simbolo_d(f, H, pequeno=True)
    word_d, word_box = f.outline("Altare", H)
    formal_d, formal_box = f.outline("ALTARE", H, tracking=G["formal_tracking_em"])

    hw = H / G["vertical_razao_versal_simbolo_wordmark"]   # versal do wordmark no vertical
    v_sym_d, v_sym_box = simbolo_d(f, H, cx=0, base=0)
    w_tmp, w_tmp_box = f.outline("Altare", hw)
    top_cap_w = v_sym_box[3] + G["vertical_espaco_em_versais_do_wordmark"] * hw
    base_w = top_cap_w + hw
    w_dx = -(w_tmp_box[0] + w_tmp_box[2]) / 2
    v_word_d, v_word_box = f.outline("Altare", hw, dx=w_dx, dy=base_w)
    v_box = (min(v_sym_box[0], v_word_box[0]), v_sym_box[1], max(v_sym_box[2], v_word_box[2]), v_word_box[3])

    pecas = {
        "simbolo": (sym_box, sym_d, "Altare"),
        "simbolo-pequeno": (sym_p_box, sym_p_d, "Altare"),
        "wordmark": (word_box, word_d, "Altare"),
        "vertical": (v_box, v_sym_d + " " + v_word_d, "Altare"),
        "assinatura": (formal_box, formal_d, "ALTARE"),
    }
    for v in VERSOES:
        for nome, (box, d, title) in pecas.items():
            (FONTE / f"altare-{nome}-{v['sufixo']}.svg").write_text(svg(box, f'<path fill="{v["cor"]}" d="{d}"/>', title))

    orn = FONTE / "ornamentos"
    orn.mkdir(exist_ok=True)
    for old in orn.glob("*.svg"):
        old.unlink()
    for nome, s in ornamentos().items():
        (orn / f"{nome}.svg").write_text(s)

    _, (ax0, ay0, ax1, _) = f.outline("A", H)
    medidas = {
        "H": H, "modulo": M,
        "fonte": {"familia": "Newsreader", "wght": 500, "opsz": 72, "upm": f.upm, "cap": f.cap, "xh": f.xh},
        "A_largura": round(ax1 - ax0, 2), "A_largura_modulos": round((ax1 - ax0) / M, 2),
        "A_topo": round(ay0, 2), "A_overshoot_modulos": round((-ay0 - H) / M, 2),
        "simbolo_box": [round(v, 2) for v in sym_box],
        "simbolo_pequeno_box": [round(v, 2) for v in sym_p_box],
        "wordmark_box": [round(v, 2) for v in word_box],
        "wordmark_xh": round(f.xh * k, 2),
        "assinatura_box": [round(v, 2) for v in formal_box],
        "vertical_box": [round(v, 2) for v in v_box],
        "vertical_wordmark_versal": round(hw, 2),
        "vertical_wordmark_linha_de_base": round(base_w, 2),
        "vertical_simbolo_base_mensa": round(v_sym_box[3], 2),
    }
    (BUILD / "medidas.json").write_text(json.dumps(medidas, indent=1, ensure_ascii=False) + "\n")
    return medidas


if __name__ == "__main__":
    print(json.dumps(gerar(), indent=1, ensure_ascii=False))
