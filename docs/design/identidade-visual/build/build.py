# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools>=4.61", "uharfbuzz>=0.50", "brotli>=1.1", "pillow>=11", "pymupdf>=1.25"]
# ///
"""Gera tudo em ../ : componentes (SVG + PNG), marca em todas as cores e tamanhos, ornamentos, favicon e ícone de app,
o guia em HTML e PDF, as páginas em PNG e componentes/INDEX.md.

Uso (de dentro de build/):
    uv run build.py            # gera a partir dos mestres em ../fonte/
    uv run build.py --marca    # antes, regera os mestres a partir da Newsreader e de ../tokens.json
Precisa do Google Chrome instalado (render de SVG e impressão do PDF).
"""
import base64
import concurrent.futures as cf
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if "--marca" in sys.argv:
    import marca
    marca.gerar()

from PIL import Image

import componentes
import documento
from lib import COMP, FONTE, MED, ROOT, VERSOES, font_face

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
INDEX = []  # (caminho relativo a componentes/, descrição)
PECAS = [("wordmark", "Wordmark"), ("simbolo", "Símbolo"), ("vertical", "Lockup vertical"), ("assinatura", "Assinatura formal"),
         ("simbolo-pequeno", "Símbolo pequeno (≤ 24 px)")]


def svg_doc(w, h, body, font=True):
    style = f"<defs><style>{font_face(body)}</style></defs>" if font else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f"{style}{body}</svg>\n")


def render(svg_path, png_path, w, h, scale=1):
    """SVG -> PNG transparente, exatamente w x h (x scale) pixels, via Chrome."""
    with tempfile.TemporaryDirectory() as d:
        html = Path(d) / "x.html"
        html.write_text(f'<html><body style="margin:0;background:transparent">'
                        f'<img src="file://{Path(svg_path).resolve()}" style="width:{w}px;height:{h}px;display:block"></body></html>')
        shot = Path(d) / "x.png"
        ww, hh = max(int(round(w)), 500), max(int(round(h)), 500)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size={ww},{hh}",
                        f"--force-device-scale-factor={scale}", "--default-background-color=00000000",
                        f"--screenshot={shot}", f"file://{html}"], capture_output=True, timeout=180)
        im = Image.open(shot)
        im.crop((0, 0, int(round(w * scale)), int(round(h * scale)))).save(png_path)


def data_uri(png):
    return "data:image/png;base64," + base64.b64encode(Path(png).read_bytes()).decode()


def jobs_run(jobs):
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(lambda j: render(*j), jobs))


def rel(p):
    return str(Path(p).relative_to(COMP))


def vb_size(path):
    import re
    s = Path(path).read_text()
    v = [float(x) for x in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    return v[2], v[3]


def main():
    if COMP.exists():
        shutil.rmtree(COMP)          # pasta gerada: só conteúdo deste script
    COMP.mkdir(parents=True)
    tmp = Path(tempfile.mkdtemp())

    # 1. rasters pequenos para as páginas de correção óptica e tamanho mínimo
    pre = {}
    for key, rel_svg, hpx in (("s16", "altare-simbolo-oliva.svg", 16), ("s16p", "altare-simbolo-pequeno-oliva.svg", 16)):
        w, h = vb_size(FONTE / rel_svg)
        pre[key] = (FONTE / rel_svg, w * hpx / h, hpx)
    (tmp / "fav.svg").write_text(svg_doc(64, 64, componentes.favicon_body(), font=False))
    pre["f16"] = (tmp / "fav.svg", 16, 16)
    pre["f32"] = (tmp / "fav.svg", 32, 32)
    jobs_run([(src, tmp / f"{k}.png", round(w, 2), h) for k, (src, w, h) in pre.items()])
    rasters = {k: data_uri(tmp / f"{k}.png") for k in pre}

    # 2. componentes
    reg = componentes.build_all(rasters)
    jobs = []
    for c in reg:
        folder = COMP / c["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        sp, pp = folder / f'{c["name"]}.svg', folder / f'{c["name"]}.png'
        sp.write_text(svg_doc(c["w"], c["h"], c["body"]))
        jobs.append((sp, pp, c["w"], c["h"], 2))
        INDEX.append((rel(sp), c["desc"] + " (vetorial)"))
        INDEX.append((rel(pp), c["desc"] + " (PNG 2x)"))

    # 3. marca: cópia exata dos mestres + PNG transparente
    logo = COMP / "logo"
    logo.mkdir(exist_ok=True)
    for v in VERSOES:
        for peca, label in PECAS:
            src = FONTE / f"altare-{peca}-{v['sufixo']}.svg"
            dst = logo / src.name
            shutil.copy(src, dst)
            INDEX.append((rel(dst), f"{label} {v['nome'].lower()}, cópia exata de fonte/{src.name} (vetorial; fundo de uso: {v['fundo_nome']})."))
            vw, vh = vb_size(src)
            larguras = (32, 64) if peca == "simbolo-pequeno" else (256, 1024, 2048)
            for w in larguras:
                png = logo / f"{src.stem}-{w}.png"
                jobs.append((dst, png, w, round(w * vh / vw, 2), 1))
                INDEX.append((rel(png), f"{label} {v['nome'].lower()}, PNG transparente com {w} px de largura."))
    orn = COMP / "ornamentos"
    orn.mkdir(exist_ok=True)
    for src in sorted((FONTE / "ornamentos").glob("*.svg")):
        dst = orn / src.name
        shutil.copy(src, dst)
        INDEX.append((rel(dst), f"Ornamento {src.stem.replace('-', ' ')}, cópia exata de fonte/ornamentos/{src.name} (vetorial)."))
        vw, vh = vb_size(src)
        png = orn / f"{src.stem}-1024.png"
        jobs.append((dst, png, 1024, round(1024 * vh / vw, 2), 1))
        INDEX.append((rel(png), f"Ornamento {src.stem.replace('-', ' ')}, PNG transparente com 1024 px de largura."))

    # 4. favicon e ícone de app
    for folder, body, base, sizes, desc in (
            ("favicon", componentes.favicon_body(), 64, (16, 32, 48, 192, 512),
             "Favicon: símbolo pequeno Marfim no quadrado Oliva com raio de 22%"),
            ("app-icon", componentes.app_icon_body(), 1024, (180, 192, 512, 1024),
             "Ícone de app: símbolo Marfim em quadrado Oliva cheio (o sistema arredonda; serve como maskable)")):
        d = COMP / folder
        d.mkdir(exist_ok=True)
        sp = d / f"altare-{folder}.svg"
        sp.write_text(svg_doc(base, base, body, font=False))
        INDEX.append((rel(sp), desc + " (vetorial)."))
        for size in sizes:
            png = d / f"altare-{folder}-{size}.png"
            jobs.append((sp, png, size, size, 1))
            INDEX.append((rel(png), f"{desc}, {size} × {size} px."))
    jobs_run(jobs)
    ico = COMP / "favicon" / "favicon.ico"
    Image.open(COMP / "favicon" / "altare-favicon-48.png").save(ico, sizes=[(16, 16), (32, 32), (48, 48)])
    INDEX.append((rel(ico), "favicon.ico com 16, 32 e 48 px."))

    # 5. documento HTML + PDF + páginas
    html, pages = documento.build_html()
    out_html = ROOT / "altare-identidade-visual.html"
    out_html.write_text(html)
    out_pdf = ROOT / "altare-identidade-visual.pdf"
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={out_pdf}",
                    f"file://{out_html}"], capture_output=True, timeout=600)
    import pymupdf as fitz
    pg = COMP / "paginas"
    pg.mkdir(exist_ok=True)
    doc = fitz.open(out_pdf)
    assert len(doc) == len(pages), (len(doc), len(pages))
    for (i, slug), p in zip(pages, doc):
        png = pg / f"pagina-{i:02d}-{slug}.png"
        p.get_pixmap(matrix=fitz.Matrix(2560 / p.rect.width, 2560 / p.rect.width)).save(png)
        INDEX.append((rel(png), f"Página {i:02d} do guia ({slug.replace('-', ' ')}), 2560 × 1440 px."))

    # 6. INDEX.md
    groups = {}
    for path, desc in INDEX:
        groups.setdefault(path.split("/")[0], []).append((path, desc))
    order = ["logo", "ornamentos", "favicon", "app-icon", "construcao", "cores", "tipografia", "usos-incorretos", "elementos",
             "aplicacoes", "paginas"]
    md = ["# Altare · componentes da identidade visual", "",
          "Gerado por `../build/build.py`. A marca vem só de `../fonte/` (5 peças × 6 cores + 6 ornamentos), e os valores de",
          "`../tokens.json`. PNGs de componentes em 2x; marca em PNG transparente. Os SVGs de componentes trazem as fontes",
          "(Newsreader, Plus Jakarta Sans, JetBrains Mono, todas OFL) embutidas em subconjunto. Não edite esta pasta à mão.", ""]
    for g in order:
        md += [f"## {g}/", ""] + [f"- `{p}`: {d}" for p, d in sorted(groups.get(g, []))] + [""]
    (COMP / "INDEX.md").write_text("\n".join(md))
    shutil.rmtree(tmp)
    print(f"{len(reg)} componentes · {len(INDEX)} arquivos no índice · {len(pages)} páginas · {out_pdf}")


if __name__ == "__main__":
    main()
