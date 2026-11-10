"""
mock_coleccion.py - maqueta de la grafica nueva de COLECCIONES (solo diseno, no es el generador).

Arma `mock-nes-nueva.html` con datos reales de la coleccion NES (los del driver `.cache/gen_nes_coleccion.py`)
y las cajas que ya existen en el repo (carpeta img/ de esta misma carpeta). Reusa el CSS/JS base de los
decks de coleccion ya publicados (recuperado del historial de git, commit 29e93c1^) y la TarroVision
nueva/ancha de scripts/tarrovision.py. Las cajas que faltan (DuckTales, Mega Man 5, etc.) salen con el
respaldo de color, como en los rankings.

Uso:  python mock_coleccion.py   (desde cualquier lado) -> escribe mock-nes-nueva.html aqui mismo.
Sin tildes en el HTML (regla de assets visuales del canal).
"""
from __future__ import annotations
import random
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[3]
sys.path.insert(0, str(REPO / "scripts"))
import tarrovision as TV   # noqa: E402

BASE_SHA = "29e93c1^"      # ultimo commit con studio/colecciones/n64-coleccion.html (la base clasica)
BASE_PATH = "studio/colecciones/n64-coleccion.html"

CAJAS = {  # clave -> archivo en img/
    "super-mario-bros-3": "super-mario-bros-3.jpg", "kirby-s-adventure": "kirby-s-adventure.jpg",
    "the-legend-of-zelda": "the-legend-of-zelda.jpg", "metroid": "metroid.jpg", "punch-out": "punch-out.jpg",
    "dragon-s-lair": "dragon-s-lair.jpg", "dr-mario": "dr-mario.jpg", "top-gun": "top-gun.jpg",
    "super-mario-bros-duck-hunt": "super-mario-bros-duck-hunt.jpg",
}
ACENTOS = ["mg", "cy", "ye"]
COLOR = {"mg": "#FF2E88", "cy": "#00E5FF", "ye": "#FFD23F"}

DATA = {
    "doc_title": "NES · Coleccion completa", "header_tag": "ESTUDIO · NES COLECCION · 34 JUEGOS · GEN 3",
    "portada": {"tag": "GENERACION 3 · 8 BITS · NINTENDO · 1983-1994", "title_vs": "COLECCION", "title_rest": "NES",
                "sub": "EL CATALOGO COMPLETO POR GENERO"},
    "categorias": [
        {"name": "PLATAFORMAS", "count": 7, "joyas": [("SUPER MARIO BROS. 3", 1990, "NINTENDO", "super-mario-bros-3"),
            ("KIRBY'S ADVENTURE", 1993, "NINTENDO", "kirby-s-adventure"), ("DUCKTALES", 1989, "CAPCOM", None)]},
        {"name": "ACCION", "count": 9, "joyas": [("THE LEGEND OF ZELDA", 1987, "NINTENDO", "the-legend-of-zelda"),
            ("METROID", 1987, "NINTENDO", "metroid"), ("MEGA MAN 5", 1992, "CAPCOM", None)]},
        {"name": "AVENTURA", "count": 5, "joyas": [("SUPER MARIO BROS. / DUCK HUNT", 1988, "NINTENDO", "super-mario-bros-duck-hunt"),
            ("8 EYES", 1990, "TAXAN", None), ("DRAGON'S LAIR", 1990, "CSG IMAGESOFT", "dragon-s-lair")]},
        {"name": "DEPORTES / LUCHA", "count": 3, "joyas": [("PUNCH-OUT!!", 1987, "NINTENDO", "punch-out"),
            ("R.C. PRO-AM", 1988, "RARE", None), ("WWF KING OF THE RING", 1993, "LJN", None)]},
        {"name": "PUZZLE", "count": 3, "joyas": [("DR. MARIO", 1990, "NINTENDO", "dr-mario"),
            ("YOSHI", 1992, "NINTENDO", None), ("WARIO'S WOODS", 1994, "NINTENDO", None)]},
        {"name": "ARCADE · SHOOTER · SIM", "count": 7, "joyas": [("TOP GUN", 1987, "KONAMI", "top-gun"),
            ("SILENT SERVICE", 1989, "KONAMI", None), ("CAPTAIN SKYHAWK", 1990, "RARE", None)]},
    ],
    "hardware": [
        {"name": "NES ACTION SET", "tag": "STANDARD · 1988", "color": "mg",
         "desc": "El pack gris clasico con la Zapper y el combo Super Mario Bros / Duck Hunt. Asi entro la NES a millones de casas."},
        {"name": "NES CLASSIC EDITION", "tag": "MINI · 2016", "color": "cy",
         "desc": "La reedicion mini de Nintendo con 30 juegos via HDMI. El homenaje moderno a la consola que empezo todo."},
        {"name": "LA ZAPPER", "tag": "LIGHT GUN", "color": "ye",
         "desc": "La pistola naranja de Duck Hunt y Barker Bill's. Apuntar a la tele de tubo era pura magia ochentera."},
    ],
    "balance": {"juegos": 34, "joyas": 18, "extra": [("CONSOLA", "NES", "la que empezo todo", "mg"), ("STUDIO REY", "CAPCOM", "rey 3rd-party del NES", "cy")]},
    "proximo": {"titulo": "NES TOP MUNDIAL", "consola": "NES", "tag": "RANKING"},
}


def esc(s):
    return s.replace("&", "&amp;")


def caja_css(k):
    return f"url('img/{CAJAS[k]}')" if k in CAJAS else None


def celda_mosaico(k, acc):
    if k in CAJAS:
        return f'<i style="background-image:url(\'img/{CAJAS[k]}\')"></i>'
    return f'<i class="fb {acc}"></i>'


def mosaico(tenue=False, cols=6, filas=2):
    items = [(j[3], ACENTOS[i % 3]) for i, c in enumerate(DATA["categorias"]) for j in c["joyas"]]
    random.Random("nes-coleccion").shuffle(items)
    n = cols * filas
    celdas = "".join(celda_mosaico(k, a) for k, a in items[:n])
    return f'<div class="g-mos{" tenue" if tenue else ""}" style="--cols:{cols};--filas:{filas}">{celdas}</div>'


def caja(k, titulo, acc):
    if k in CAJAS:
        return f'<img class="g-caja" src="img/{CAJAS[k]}" alt="">'
    return f'<div class="g-caja fb {acc}"><span>{esc(titulo)}</span></div>'


def thumbs(c, acc):
    return "".join(
        (f'<img src="img/{CAJAS[j[3]]}" alt="">' if j[3] in CAJAS else f'<b class="fb {acc}"></b>') for j in c["joyas"])


def s_portada(n):
    p, cats = DATA["portada"], DATA["categorias"]
    return (f'<section class="slide active g-nueva"><span class="slide-num">{n:02d}</span>{mosaico()}'
            '<div class="g-portada"><div class="g-sello">COLECCION RETROTARROS</div>'
            f'<div class="g-ptag">{p["tag"]}</div>'
            f'<div class="g-ptitle"><span class="vs">{p["title_vs"]}</span> {p["title_rest"]}</div>'
            f'<div class="g-psub">{p["sub"]}</div>'
            '<div class="g-pills">'
            f'<div class="g-pill mg"><b>{DATA["balance"]["juegos"]}</b><span>JUEGOS</span></div>'
            f'<div class="g-pill cy"><b>{len(cats)}</b><span>CATEGORIAS</span></div>'
            f'<div class="g-pill ye"><b>{DATA["balance"]["joyas"]}</b><span>JOYAS</span></div>'
            '</div></div></section>')


def s_indice(n):
    cats = DATA["categorias"]
    cards = []
    for i, c in enumerate(cats, 1):
        acc = ACENTOS[(i - 1) % 3]
        cards.append(f'<div class="g-icard {acc}"><div class="g-inum">{i:02d}</div>'
                     f'<div class="g-itxt"><div class="g-iname">{c["name"]}</div><div class="g-icount"><b>{c["count"]}</b> TITULOS</div></div>'
                     f'<div class="g-ithumbs">{thumbs(c, acc)}</div></div>')
    return (f'<section class="slide g-nueva"><span class="slide-num">{n:02d}</span><div class="g-indice">'
            '<div class="g-ititle">SELECCIONA TU CATEGORIA</div>'
            f'<div class="g-igrid" style="--cols:3">{"".join(cards)}</div>'
            f'<div class="g-itotal">{DATA["balance"]["juegos"]} JUEGOS · PRESS START</div></div></section>')


def s_paneo(n, i):
    c = DATA["categorias"][i - 1]
    acc = ACENTOS[(i - 1) % 3]
    return (f'<section class="slide g-nueva"><span class="slide-num">{n:02d}</span>'
            f'<div class="g-paneo {acc}"><div class="g-pcard">'
            f'<div class="g-pnum">CAT {i:02d}/{len(DATA["categorias"]):02d}</div><div class="g-pname">{c["name"]}</div>'
            f'<div class="g-pbig">{c["count"]}</div><div class="g-pbigl">TITULOS EN LA COLECCION</div>'
            f'<div class="g-ptease"><span>SIGUEN 3 JOYAS</span><div class="g-pthumbs">{thumbs(c, acc)}</div></div></div>'
            f'<div class="gp-tv tvw">{TV.tv(i, "ancha")}</div></div></section>')


def s_triple(n, i):
    c = DATA["categorias"][i - 1]
    acc = ACENTOS[(i - 1) % 3]
    celdas = []
    for k, (t, ano, ed, key) in enumerate(c["joyas"], 1):
        bg = f' style="--bg:{caja_css(key)}"' if key in CAJAS else ""
        celdas.append(f'<div class="g-cell{" nobg" if key not in CAJAS else ""}"{bg}>'
                      f'<div class="g-celltv">{TV.tv(k, "nueva")}</div>'
                      f'<div class="g-cellinfo">{caja(key, t, acc)}<div class="g-celltxt">'
                      f'<div class="g-celltag">EN LA COLECCION</div><div class="g-celltitle">{esc(t)}</div>'
                      f'<div class="g-chips"><span class="y">{ano}</span><span>{ed}</span></div></div></div></div>')
    return (f'<section class="slide g-nueva"><span class="slide-num">{n:02d}</span><div class="g-triple {acc}">'
            f'<div class="g-thead"><span>{c["name"]}</span> · 3 JOYAS DESTACADAS</div>'
            f'<div class="g-tgrid">{"".join(celdas)}</div></div></section>')


def s_hardware(n):
    cards = []
    for h in DATA["hardware"]:
        cards.append(f'<div class="g-hcard {h["color"]}"><div class="g-hfoto"><span>FOTO DEL EQUIPO</span></div>'
                     f'<div class="g-hname">{h["name"]}</div><div class="g-chips"><span class="y">{h["tag"]}</span></div>'
                     f'<p>{esc(h["desc"])}</p></div>')
    return (f'<section class="slide g-nueva"><span class="slide-num">{n:02d}</span><div class="g-hard">'
            '<div class="g-htitle">HARDWARE</div><div class="g-hsub">EL FIERRO NES DEL ESTUDIO</div>'
            f'<div class="g-hgrid">{"".join(cards)}</div></div></section>')


def s_balance(n):
    b, cats = DATA["balance"], DATA["categorias"]
    mx = max(c["count"] for c in cats)
    barras = "".join(
        f'<div class="g-brow {ACENTOS[i % 3]}"><span class="g-bl">{c["name"]}</span>'
        f'<span class="g-bt"><i style="width:{c["count"] / mx * 100:.0f}%"></i></span><b>{c["count"]}</b></div>'
        for i, c in enumerate(cats))
    extra = "".join(f'<div class="g-xcard {col}"><h3>{l}</h3><b>{v}</b><p>{s}</p></div>' for l, v, s, col in b["extra"])
    return (f'<section class="slide g-nueva"><span class="slide-num">{n:02d}</span><div class="g-bal">'
            '<div class="g-btitle">BALANCE FINAL</div><div class="g-bsub">LA COLECCION EN NUMEROS</div>'
            '<div class="g-bgrid"><div class="g-bstats">'
            f'<div class="g-stat mg"><h3>JUEGOS</h3><b>{b["juegos"]}</b><p>cartuchos en la coleccion</p></div>'
            f'<div class="g-stat cy"><h3>CATEGORIAS</h3><b>{len(cats)}</b><p>generos cubiertos</p></div>'
            f'<div class="g-stat ye"><h3>JOYAS</h3><b>{b["joyas"]}</b><p>destacadas en gameplay</p></div></div>'
            f'<div class="g-bchart"><div class="g-bct">JUEGOS POR CATEGORIA</div>{barras}<div class="g-bx">{extra}</div></div>'
            '</div></div></section>')


def s_cierre(n):
    p = DATA["proximo"]
    return (f'<section class="slide g-nueva"><span class="slide-num">{n:02d}</span>{mosaico(True)}'
            '<div class="g-cierre"><div class="g-cpre">PROXIMO CAPITULO</div><div class="g-ctitle">SIGUE LA SAGA</div>'
            '<div class="g-csig"><div class="g-cthumb">'
            f'<span>{p["tag"]}</span><b>{p["consola"]}</b></div><div class="g-ctxt"><div class="g-csl">SIGUE CON</div>'
            f'<div class="g-cname">{p["titulo"]}</div></div></div>'
            '<div class="g-cta"><span class="mg">CUENTANOS TU FAVORITA</span><span class="cy">PIDE OTRA CONSOLA</span>'
            '<span class="ye">SUSCRIBETE</span></div></div></section>')


CSS = """
/* ===== GRAFICA NUEVA DE COLECCIONES (maqueta) ===== */
.g-nueva .g-mos{position:absolute;inset:-24px;display:grid;grid-template-columns:repeat(var(--cols),1fr);grid-template-rows:repeat(var(--filas),1fr);filter:blur(9px) brightness(.38) saturate(1.25);z-index:0}
.g-mos.tenue{filter:blur(12px) brightness(.26) saturate(1.2)}
.g-mos i{display:block;background-size:cover;background-position:center top}
.fb.mg{background:linear-gradient(135deg,#7a0f46,#FF2E88)}.fb.cy{background:linear-gradient(135deg,#065a68,#00a8c0)}.fb.ye{background:linear-gradient(135deg,#7a5c00,#d9a800)}
.g-portada,.g-cierre,.g-indice,.g-paneo,.g-triple,.g-hard,.g-bal{position:relative;z-index:2;height:100%}
/* portada */
.g-portada{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:18px;text-shadow:0 0 30px #000,0 0 10px #000}
.g-sello{font:400 22px 'Press Start 2P';color:var(--ye);letter-spacing:6px;padding:12px 24px;border:2px solid var(--ye);background:rgba(6,3,15,.6)}
.g-ptag{font:400 26px 'Press Start 2P';color:var(--cy);letter-spacing:6px}
.g-ptitle{font:900 170px 'Orbitron';color:#fff;line-height:1;letter-spacing:2px}.g-ptitle .vs{color:var(--mg);text-shadow:0 0 34px rgba(255,46,136,.7)}
.g-psub{font:400 38px 'Share Tech Mono';color:var(--ye);letter-spacing:6px}
.g-pills{display:flex;gap:28px;margin-top:14px}
.g-pill{display:flex;flex-direction:column;align-items:center;padding:16px 44px;background:rgba(6,3,15,.78);border:2px solid;border-radius:6px;min-width:260px}
.g-pill b{font:900 76px 'Orbitron';line-height:1}.g-pill span{font:400 20px 'Press Start 2P';letter-spacing:3px;margin-top:10px;color:#fff}
.g-pill.mg{border-color:var(--mg)}.g-pill.mg b{color:var(--mg)}.g-pill.cy{border-color:var(--cy)}.g-pill.cy b{color:var(--cy)}.g-pill.ye{border-color:var(--ye)}.g-pill.ye b{color:var(--ye)}
/* indice */
.g-indice{display:flex;flex-direction:column;align-items:center;gap:22px;padding-top:8px}
.g-ititle{font:400 34px 'Press Start 2P';color:var(--mg);letter-spacing:8px;text-shadow:0 0 16px rgba(255,46,136,.5)}
.g-igrid{display:grid;grid-template-columns:repeat(var(--cols),1fr);gap:22px;width:100%;max-width:1780px;flex:1;align-content:stretch}
.g-icard{display:grid;grid-template-columns:auto 1fr;grid-template-rows:1fr auto;gap:6px 22px;padding:22px 26px;background:rgba(12,6,32,.82);border-left:6px solid var(--acc);border-radius:6px;align-items:center}
.g-icard.mg{--acc:var(--mg)}.g-icard.cy{--acc:var(--cy)}.g-icard.ye{--acc:var(--ye)}
.g-inum{font:900 64px 'Orbitron';color:var(--acc);grid-row:1}
.g-itxt{grid-row:1}.g-iname{font:900 38px 'Orbitron';color:#fff;line-height:1.1;letter-spacing:2px}
.g-icount{font:400 26px 'Share Tech Mono';color:rgba(255,255,255,.75);margin-top:8px}.g-icount b{font:900 56px 'Orbitron';color:var(--acc);margin-right:10px;vertical-align:middle}
.g-ithumbs{grid-column:1/3;display:flex;gap:12px;height:150px}.g-ithumbs img,.g-ithumbs b{height:100%;width:auto;aspect-ratio:.7;object-fit:cover;border-radius:3px;box-shadow:0 4px 14px rgba(0,0,0,.6)}
.g-itotal{font:400 28px 'Press Start 2P';color:var(--cy);letter-spacing:6px}
/* paneo */
.g-paneo{display:grid;grid-template-columns:600px 1fr;gap:34px;align-items:stretch}
.g-paneo.mg{--acc:var(--mg)}.g-paneo.cy{--acc:var(--cy)}.g-paneo.ye{--acc:var(--ye)}
.g-pcard{display:flex;flex-direction:column;justify-content:center;gap:12px;padding:30px;background:linear-gradient(180deg,rgba(12,6,32,.9),rgba(45,27,105,.6));border-left:8px solid var(--acc);border-radius:8px}
.g-pnum{font:400 24px 'Press Start 2P';color:var(--ye);letter-spacing:4px}
.g-pname{font:900 50px 'Orbitron';color:#fff;line-height:1.08;letter-spacing:3px;text-shadow:0 0 18px rgba(255,46,136,.4)}
.g-pbig{font:900 170px 'Orbitron';color:var(--acc);line-height:.95;margin-top:10px;text-shadow:0 0 26px currentColor}
.g-pbigl{font:400 24px 'Press Start 2P';color:#fff;letter-spacing:3px;line-height:1.5}
.g-ptease{margin-top:14px;padding-top:16px;border-top:1px solid rgba(255,255,255,.2)}.g-ptease>span{font:400 20px 'Press Start 2P';color:var(--cy);letter-spacing:3px}
.g-pthumbs{display:flex;gap:14px;margin-top:14px;height:150px}.g-pthumbs img,.g-pthumbs b{height:100%;aspect-ratio:.7;object-fit:cover;border-radius:3px;box-shadow:0 4px 14px rgba(0,0,0,.6)}
.g-paneo .gp-tv{display:flex;align-items:center;justify-content:center;min-width:0}
.g-paneo .gp-tv.tvw{container-type:size;width:100%}
/* triple */
.g-triple{display:flex;flex-direction:column;gap:14px;max-width:1830px;margin:0 auto}
.g-triple.mg{--acc:var(--mg)}.g-triple.cy{--acc:var(--cy)}.g-triple.ye{--acc:var(--ye)}
.g-thead{align-self:center;font:400 26px 'Press Start 2P';letter-spacing:5px;color:#fff;padding:10px 22px;border:2px solid var(--acc);background:rgba(6,3,15,.7)}.g-thead span{color:var(--acc)}
.g-tgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;flex:1;min-height:0}
.g-cell{position:relative;display:flex;flex-direction:column;gap:14px;padding:18px;border-radius:10px;overflow:hidden;background:rgba(12,6,32,.9);isolation:isolate}
.g-cell::before{content:"";position:absolute;inset:-30px;background:var(--bg) center/cover;filter:blur(22px) brightness(.32) saturate(1.3);z-index:-1}
.g-cell.nobg::before{background:linear-gradient(135deg,#2D1B69,#4a2a99)}
.g-celltv{display:flex;justify-content:center}.g-celltv .tarrovision.tvn{width:100%;height:auto;aspect-ratio:auto;max-width:none}
.g-cellinfo{display:flex;gap:20px;align-items:center;min-height:0;flex:1}
.g-caja{height:100%;max-height:250px;aspect-ratio:.7;object-fit:cover;border-radius:4px;box-shadow:0 8px 24px rgba(0,0,0,.7),0 0 0 2px rgba(255,255,255,.12);transform:rotate(-3deg);flex:none}
.g-caja.fb{display:flex;align-items:center;justify-content:center;padding:10px;text-align:center}.g-caja.fb span{font:900 20px 'Orbitron';color:#fff;line-height:1.2}
.g-celltxt{display:flex;flex-direction:column;gap:12px;min-width:0}
.g-celltag{align-self:flex-start;font:400 16px 'Press Start 2P';color:#04121a;background:var(--cy);padding:7px 12px;letter-spacing:2px}
.g-celltitle{font:900 36px 'Orbitron';color:#fff;line-height:1.1}
.g-chips{display:flex;gap:10px;flex-wrap:wrap}.g-chips span{font:400 24px 'Share Tech Mono';color:var(--cy);border:2px solid rgba(0,229,255,.5);background:rgba(0,229,255,.08);padding:4px 14px;border-radius:20px}.g-chips span.y{color:var(--ye);border-color:rgba(255,210,63,.6);background:rgba(255,210,63,.1)}
/* hardware */
.g-hard{display:flex;flex-direction:column;align-items:center;gap:10px}
.g-htitle{font:900 90px 'Orbitron';color:#fff;line-height:1}.g-hsub{font:400 30px 'Share Tech Mono';color:var(--mg);letter-spacing:6px;margin-bottom:12px}
.g-hgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;width:100%;max-width:1780px;flex:1;min-height:0}
.g-hcard{display:flex;flex-direction:column;gap:14px;padding:22px 24px;background:var(--card-bg);border-top:6px solid var(--acc);border-radius:6px}
.g-hcard.mg{--acc:var(--mg)}.g-hcard.cy{--acc:var(--cy)}.g-hcard.ye{--acc:var(--ye)}
.g-hfoto{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;border-radius:6px;background:repeating-linear-gradient(45deg,rgba(255,255,255,.04) 0 14px,transparent 14px 28px),linear-gradient(135deg,#1a1230,#2D1B69);border:2px dashed rgba(255,255,255,.25)}
.g-hfoto span{font:400 22px 'Press Start 2P';color:rgba(255,255,255,.4);letter-spacing:4px}
.g-hname{font:900 38px 'Orbitron';color:#fff;line-height:1.1}.g-hcard p{font:400 26px 'Share Tech Mono';color:rgba(255,255,255,.82);line-height:1.4}
/* balance */
.g-bal{display:flex;flex-direction:column;align-items:center;gap:6px}
.g-btitle{font:900 90px 'Orbitron';color:#fff;line-height:1}.g-bsub{font:400 30px 'Share Tech Mono';color:var(--mg);letter-spacing:6px;margin-bottom:16px}
.g-bgrid{display:grid;grid-template-columns:520px 1fr;gap:34px;width:100%;max-width:1780px;flex:1;min-height:0}
.g-bstats{display:flex;flex-direction:column;gap:18px}
.g-stat{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;background:var(--card-bg);border-top:5px solid var(--c);border-radius:6px}
.g-stat.mg,.g-xcard.mg{--c:var(--mg)}.g-stat.cy,.g-xcard.cy{--c:var(--cy)}.g-stat.ye,.g-xcard.ye{--c:var(--ye)}
.g-stat h3,.g-xcard h3{font:400 20px 'Press Start 2P';color:var(--ye);letter-spacing:4px}.g-stat b{font:900 120px 'Orbitron';color:var(--c);line-height:1;text-shadow:0 0 22px currentColor}.g-stat p,.g-xcard p{font:400 24px 'Share Tech Mono';color:rgba(255,255,255,.78)}
.g-bchart{display:flex;flex-direction:column;gap:14px;padding:26px 32px;background:var(--card-bg);border-radius:6px}
.g-bct{font:400 22px 'Press Start 2P';color:var(--cy);letter-spacing:4px;margin-bottom:6px}
.g-brow{display:grid;grid-template-columns:400px 1fr 70px;gap:20px;align-items:center}
.g-brow.mg{--c:var(--mg)}.g-brow.cy{--c:var(--cy)}.g-brow.ye{--c:var(--ye)}
.g-bl{font:900 24px 'Orbitron';color:#fff;letter-spacing:1px}.g-bt{height:34px;background:rgba(255,255,255,.07);border-radius:4px;overflow:hidden}.g-bt i{display:block;height:100%;background:var(--c);box-shadow:0 0 14px var(--c)}.g-brow b{font:900 36px 'Orbitron';color:var(--c);text-align:right}
.g-bx{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:auto}
.g-xcard{display:flex;flex-direction:column;align-items:center;padding:14px;border-top:4px solid var(--c);background:rgba(255,255,255,.04)}.g-xcard b{font:900 64px 'Orbitron';color:var(--c);line-height:1.1}
/* cierre */
.g-cierre{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;text-align:center}
.g-cpre{font:400 26px 'Press Start 2P';color:var(--cy);letter-spacing:8px}
.g-ctitle{font:900 120px 'Orbitron';color:var(--cy);text-shadow:0 0 30px rgba(0,229,255,.6);line-height:1}
.g-csig{display:flex;align-items:center;gap:30px;padding:22px 34px;background:rgba(6,3,15,.8);border:2px solid var(--mg);border-radius:10px;box-shadow:0 0 30px rgba(255,46,136,.35)}
.g-cthumb{width:320px;aspect-ratio:16/9;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(135deg,#2D1B69,#FF2E88);border-radius:6px}.g-cthumb span{font:400 16px 'Press Start 2P';color:var(--ye);letter-spacing:3px}.g-cthumb b{font:900 64px 'Orbitron';color:#fff}
.g-ctxt{text-align:left}.g-csl{font:400 20px 'Press Start 2P';color:var(--mg);letter-spacing:4px}.g-cname{font:900 52px 'Orbitron';color:#fff;margin-top:10px;line-height:1.1}
.g-cta{display:flex;gap:26px;font:400 24px 'Press Start 2P';letter-spacing:3px}.g-cta span{padding:14px 22px;border:2px solid;background:rgba(6,3,15,.7)}
.g-cta .mg{color:var(--mg);border-color:var(--mg)}.g-cta .cy{color:var(--cy);border-color:var(--cy)}.g-cta .ye{color:var(--ye);border-color:var(--ye)}
"""


def main():
    base = subprocess.run(["git", "show", f"{BASE_SHA}:{BASE_PATH}"], cwd=REPO, capture_output=True, check=True).stdout.decode("utf-8")
    head = base[: base.index("<body>") + len("<body>")]
    foot = base[base.index('<nav class="footer">'):]
    head = head.replace("</style>", CSS + TV.css("nueva") + TV.css("ancha") + "\n</style>", 1)
    head = head.replace("RETROTARROS · N64 · Coleccion completa", "RETROTARROS · MAQUETA grafica nueva colecciones")
    cats = DATA["categorias"]
    slides, n = [], 1
    slides.append(s_portada(n)); n += 1
    slides.append(s_indice(n)); n += 1
    slides.append(s_paneo(n, 1)); n += 1
    slides.append(s_triple(n, 1)); n += 1
    slides.append(s_paneo(n, 2)); n += 1
    slides.append(s_triple(n, 2)); n += 1
    slides.append(s_hardware(n)); n += 1
    slides.append(s_balance(n)); n += 1
    slides.append(s_cierre(n)); n += 1
    hdr = ('\n\n<header><div class="hdr-logo">RETROTARROS</div><div class="hdr-tag">' + DATA["header_tag"] +
           '</div><div class="hdr-rec"><div class="dot"></div>EN VIVO</div></header>\n\n<div class="deck" id="deck">\n\n' +
           "\n\n".join(slides) + "\n\n</div>\n\n")
    out = AQUI / "mock-nes-nueva.html"
    out.write_text(head + hdr + foot, encoding="utf-8")
    print("OK ->", out, "slides:", len(slides))


if __name__ == "__main__":
    main()
