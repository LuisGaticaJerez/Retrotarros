"""
coleccion_grafica.py - Retrotarros Studio Suite
===============================================
Grafica nueva de los episodios de COLECCION. Se activa SOLO con data["grafica"] = "nueva"
en generar_deck() (scripts/coleccion_deck.py); sin la marca este modulo ni se importa y el
HTML sale identico, byte a byte, al de siempre.

La estructura del deck no cambia (portada, indice, por categoria paneo + triple de joyas,
hardware, balance, cierre); cambia como se ve: letra para TV, cajas reales de los juegos,
slides que llenan la pantalla y TarroVision (scripts/tarrovision.py) con el formato real
del gameplay. Reusa el CSS/JS base del generador clasico (studio/templates/_base-coleccion.html).

Campos del data, todos opcionales (sin ellos la slide sale igual, con respaldos):
  categorias[].joyas[].img   clave o ruta de la caja (si falta: img/<slug>/<slug-del-titulo>.jpg)
  categorias[].joyas[].nota  texto para la capa de notas (tecla N) del triple
  categorias[].notas         lista de lineas para la capa de notas del paneo
  hardware[].img             clave o ruta de la foto del equipo (si falta: img/<slug>/hw-<slug-del-nombre>.jpg)
  tarrovision                "nueva" (4:3, por defecto) o "ancha" (16:9) para el triple de joyas
  proximo                    {"titulo", "consola", "tag"}: tarjeta SIGUE CON del cierre

Las cajas se buscan relativas a la carpeta de salida (studio/colecciones/img/<slug>/).
Disenio: docs/superpowers/specs/2026-11-10-colecciones-grafica-design.md
Sin tildes en el HTML (regla de assets visuales del canal).
"""
from __future__ import annotations

import html
import random
import re
from pathlib import Path

import coleccion_deck as D
import tarrovision as TV

ACENTOS = ["mg", "cy", "ye"]
MIN_CAJAS_MOSAICO = 6     # con menos cajas el mosaico no se usa y portada/cierre salen sin fondo de cajas
CELDAS_MOSAICO = (6, 2)   # columnas x filas
ESCRIBIR_NOTAS_JS = (
    "<script>(function(){function t(){document.body.classList.toggle('read-mode');}"
    "document.addEventListener('keydown',function(e){if(e.key==='n'||e.key==='N'){t();}});"
    "if(location.search.indexOf('notas=1')>=0){t();}})();</script>\n"
)


def _esc(s) -> str:
    return html.escape(str(s), quote=False)


def _slug(s: str) -> str:
    s = s.lower()
    for a, b in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", "ü": "u"}.items():
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def _inyectar(texto: str, viejo: str, nuevo: str) -> str:
    """Reemplaza `viejo` por `nuevo` una sola vez; RuntimeError si `viejo` no esta."""
    if viejo not in texto:
        raise RuntimeError(f"coleccion_grafica: no encontre {viejo!r} en el HTML base")
    return texto.replace(viejo, nuevo, 1)


# --------------------------------------------------------------------------- imagenes

def _buscar_img(out_dir: Path, slug: str, valor: str | None, por_defecto: str) -> str | None:
    """Ruta relativa (a out_dir) de una imagen, o None si no existe.
    `valor` puede ser una ruta con extension (relativa a out_dir) o una clave; sin valor se usa `por_defecto`."""
    if valor and re.search(r"\.(jpe?g|png|webp)$", valor, re.I):
        return valor if (out_dir / valor).exists() else None
    clave = valor or por_defecto
    for ext in ("jpg", "png"):
        rel = f"img/{slug}/{clave}.{ext}"
        if (out_dir / rel).exists():
            return rel
    return None


AR_VERTICAL = 0.7   # proporcion (ancho / alto) que se asume sin imagen: caja vertical de cartucho


def _aspecto(ruta: Path) -> float:
    """Ancho / alto de un PNG o JPEG leyendo solo el encabezado; AR_VERTICAL si no se puede leer."""
    try:
        b = ruta.read_bytes()[:200000]
        if b[:8] == bytes([137, 80, 78, 71, 13, 10, 26, 10]):
            w, h = int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")
        elif b[:2] == bytes([255, 216]):
            i = 2
            while i < len(b) - 9:
                if b[i] != 255:
                    i += 1
                    continue
                marca = b[i + 1]
                if marca in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = int.from_bytes(b[i + 5:i + 7], "big"), int.from_bytes(b[i + 7:i + 9], "big")
                    break
                i += 2 + int.from_bytes(b[i + 2:i + 4], "big")
            else:
                return AR_VERTICAL
        else:
            return AR_VERTICAL
        return round(w / h, 3) if w and h else AR_VERTICAL
    except (OSError, ValueError):
        return AR_VERTICAL


def _cajas(data: dict, out_dir: Path, slug: str) -> None:
    """Completa joya["_caja"] (ruta relativa o None) y joya["_ar"] (proporcion) en una copia del data que recibe el generador."""
    for c in data["categorias"]:
        for j in c["joyas"]:
            j["_caja"] = _buscar_img(out_dir, slug, j.get("img"), _slug(j["title"]))
            j["_ar"] = _aspecto(out_dir / j["_caja"]) if j["_caja"] else AR_VERTICAL
    for h in data.get("hardware") or []:
        h["_foto"] = _buscar_img(out_dir, slug, h.get("img"), "hw-" + _slug(h["name"]))


def _todas_las_cajas(data: dict) -> list[str]:
    return [j["_caja"] for c in data["categorias"] for j in c["joyas"] if j.get("_caja")]


# --------------------------------------------------------------------------- piezas

def _mosaico(data: dict, slug: str, tenue: bool = False) -> str:
    cajas = _todas_las_cajas(data)
    if len(cajas) < MIN_CAJAS_MOSAICO:
        return ""
    cols, filas = CELDAS_MOSAICO
    items = sorted(set(cajas))
    random.Random(slug).shuffle(items)
    celdas = "".join(
        f'<i style="background-image:url(\'{items[k % len(items)]}\')"></i>' for k in range(cols * filas))
    return f'<div class="g-mosw"><div class="g-mos{" tenue" if tenue else ""}" style="--cols:{cols};--filas:{filas}">{celdas}</div></div>'


def _miniaturas(clase: str, c: dict, acc: str, alto_max: int, ancho: int, hueco: int) -> str:
    """Tira de las cajas de una categoria. Cada caja conserva su proporcion; el alto comun se achica
    para que la tira entre en `ancho` px (las cajas apaisadas de N64 o SNES son mucho mas anchas que las verticales)."""
    joyas = c["joyas"]
    suma = sum(j.get("_ar", AR_VERTICAL) for j in joyas) or 1
    alto = min(alto_max, (ancho - hueco * (len(joyas) - 1)) / suma)
    piezas = "".join(
        (f'<img src="{j["_caja"]}" alt="">' if j.get("_caja") else f'<b class="fb {acc}"></b>') for j in joyas)
    return f'<div class="{clase}" style="--th:{alto:.0f}px">{piezas}</div>'


def _caja(j: dict, acc: str) -> str:
    if j.get("_caja"):
        return f'<img class="g-caja" style="--ar:{j.get("_ar", AR_VERTICAL)}" src="{j["_caja"]}" alt="">'
    return f'<div class="g-caja fb {acc}"><span>{_esc(j["title"])}</span></div>'


def _chips(j: dict) -> str:
    partes = []
    if j.get("ano"):
        partes.append(f'<span class="y">{_esc(j["ano"])}</span>')
    if j.get("editor"):
        partes.append(f'<span>{_esc(j["editor"])}</span>')
    return f'<div class="g-chips">{"".join(partes)}</div>' if partes else ""


def _notas(titulo: str, lineas: list[str]) -> str:
    lineas = [l for l in lineas if l]
    if not lineas:
        return ""
    items = "".join(f"<li>{_esc(l)}</li>" for l in lineas)
    return f'<aside class="notas"><div class="notas-t">{_esc(titulo)}</div><ul>{items}</ul></aside>'


def _totales(data: dict) -> tuple[int, int, int]:
    """Juegos, categorias y joyas, calculados desde las categorias (no tipeados a mano)."""
    cats = data["categorias"]
    return sum(c["count"] for c in cats), len(cats), sum(len(c["joyas"]) for c in cats)


# --------------------------------------------------------------------------- slides

def _s_portada(n: int, data: dict, slug: str) -> str:
    p = data["portada"]
    juegos, ncat, njoyas = _totales(data)
    return (
        f'  <section class="slide active g-nueva">\n    <span class="slide-num">{n:02d}</span>\n{_mosaico(data, slug)}\n'
        '    <div class="g-portada"><div class="g-sello">COLECCION RETROTARROS</div>\n'
        f'      <div class="g-ptag">{p["tag"]}</div>\n'
        f'      <div class="g-ptitle"><span class="vs">{p["title_vs"]}</span> {p["title_rest"]}</div>\n'
        f'      <div class="g-psub">{p["sub"]}</div>\n'
        '      <div class="g-pills">'
        f'<div class="g-pill mg"><b>{juegos}</b><span>JUEGOS</span></div>'
        f'<div class="g-pill cy"><b>{ncat}</b><span>CATEGORIAS</span></div>'
        f'<div class="g-pill ye"><b>{njoyas}</b><span>JOYAS</span></div>'
        '</div></div>\n  </section>'
    )


def _columnas_indice(n: int) -> int:
    if n <= 2:
        return max(n, 1)
    if n == 4:
        return 2
    return 4 if n >= 10 else 3


def _s_indice(n: int, data: dict) -> str:
    cats = data["categorias"]
    cols = _columnas_indice(len(cats))
    filas = -(-len(cats) // cols)
    ancho_tarjeta = int((1780 - 22 * (cols - 1)) / cols) - 60   # ancho util de la tira de cajas (tarjeta menos relleno y borde)
    tarjetas = []
    for i, c in enumerate(cats, 1):
        acc = ACENTOS[(i - 1) % 3]
        tarjetas.append(
            f'<div class="g-icard {acc}"><div class="g-inum">{i:02d}</div>'
            f'<div class="g-itxt"><div class="g-iname">{c["name"]}</div>'
            f'<div class="g-icount"><b>{c["count"]}</b> TITULOS</div></div>'
            f'{_miniaturas("g-ithumbs", c, acc, 84 if filas >= 3 else 150, ancho_tarjeta, 12)}</div>')
    juegos = _totales(data)[0]
    return (
        f'  <section class="slide g-nueva">\n    <span class="slide-num">{n:02d}</span>\n'
        '    <div class="g-indice"><div class="g-ititle">SELECCIONA TU CATEGORIA</div>\n'
        f'      <div class="g-igrid{" r3" if filas >= 3 else ""}" style="--cols:{cols}">{"".join(tarjetas)}</div>\n'
        f'      <div class="g-itotal">{juegos} JUEGOS · PRESS START</div></div>\n  </section>'
    )


def _clase_nombre(nombre: str) -> str:
    return "n1" if len(nombre) <= 12 else ("n2" if len(nombre) <= 18 else "n3")


def _s_paneo(n: int, ci: int, total: int, c: dict) -> str:
    acc = ACENTOS[(ci - 1) % 3]
    lineas = list(c.get("notas") or [])
    if c.get("juegos"):
        lineas.append(f"CATALOGO DE LA CATEGORIA ({len(c['juegos'])}):")
        lineas.extend(c["juegos"])
    notas = _notas(f"PANEO · {c['name']}", lineas)
    return (
        f'  <section class="slide g-nueva">\n    <span class="slide-num">{n:02d}</span>\n'
        f'    <div class="g-paneo {acc}"><div class="g-pcard">'
        f'<div class="g-pnum">CAT {ci:02d}/{total:02d}</div><div class="g-pname {_clase_nombre(c["name"])}">{c["name"]}</div>'
        f'<div class="g-pbig">{c["count"]}</div><div class="g-pbigl">TITULOS EN LA COLECCION</div>'
        f'<div class="g-ptease"><span>SIGUEN {len(c["joyas"])} JOYAS</span>{_miniaturas("g-pthumbs", c, acc, 150, 530, 14)}</div></div>'
        f'<div class="gp-tv tvw">{TV.tv(ci, "ancha")}</div></div>\n{notas}\n  </section>'
    )


def _variante_triple(data: dict) -> str:
    v = data.get("tarrovision", "nueva")
    if v == "clasica":
        v = "nueva"
    TV.variante({"tarrovision": v})   # ValueError si no es nueva ni ancha
    return v


def _s_triple(n: int, ci: int, c: dict, variante: str) -> str:
    acc = ACENTOS[(ci - 1) % 3]
    celdas = []
    for k, j in enumerate(c["joyas"], 1):
        bg = f' style="--bg:url(\'{j["_caja"]}\')"' if j.get("_caja") else ""
        celdas.append(
            f'<div class="g-cell{"" if j.get("_caja") else " nobg"}"{bg}>'
            f'<div class="g-celltv">{TV.tv(k, variante)}</div>'
            f'<div class="g-cellinfo"><div class="g-celltag">EN LA COLECCION</div>{_caja(j, acc)}<div class="g-celltxt">'
            f'<div class="g-celltitle{" l" if max(len(w) for w in j["title"].split()) >= 10 else ""}">{_esc(j["title"])}</div>'
            f'{_chips(j)}</div></div></div>')
    notas = _notas(f"JOYAS · {c['name']}", [f"{j['title']}: {j['nota']}" for j in c["joyas"] if j.get("nota")])
    return (
        f'  <section class="slide g-nueva">\n    <span class="slide-num">{n:02d}</span>\n'
        f'    <div class="g-triple {acc}"><div class="g-thead"><span>{c["name"]}</span> · {len(c["joyas"])} JOYAS DESTACADAS</div>'
        f'<div class="g-tgrid" style="--n:{len(c["joyas"])}">{"".join(celdas)}</div></div>\n{notas}\n  </section>'
    )


def _columnas_hardware(n: int) -> int:
    return {1: 1, 2: 2, 3: 3, 4: 2}.get(n, 3)


def _s_hardware(n: int, data: dict) -> str:
    hw = data["hardware"]
    tarjetas = []
    for h in hw:
        foto = (f'<div class="g-hfoto"><img src="{h["_foto"]}" alt=""></div>' if h.get("_foto")
                else '<div class="g-hfoto sin"><span>FOTO DEL EQUIPO</span></div>')
        tarjetas.append(
            f'<div class="g-hcard {h["color"]}">{foto}<div class="g-hname">{_esc(h["name"])}</div>'
            f'<div class="g-chips"><span class="y">{_esc(h["tag"])}</span></div><p>{_esc(h["desc"])}</p></div>')
    return (
        f'  <section class="slide g-nueva">\n    <span class="slide-num">{n:02d}</span>\n'
        f'    <div class="g-hard"><div class="g-htitle">{data["hardware_titulo"]}</div><div class="g-hsub">{data["hardware_sub"]}</div>\n'
        f'      <div class="g-hgrid" style="--cols:{_columnas_hardware(len(hw))}">{"".join(tarjetas)}</div></div>\n  </section>'
    )


def _s_balance(n: int, data: dict) -> str:
    b, cats = data["balance"], data["categorias"]
    juegos, ncat, njoyas = _totales(data)
    subs = [c.get("sub") for c in b.get("row1", [])] + [None, None, None]
    sub_juegos = subs[0] or "juegos en la coleccion"
    sub_cat = subs[1] or "generos cubiertos"
    sub_joyas = subs[2] or "destacadas en gameplay"
    mx = max(c["count"] for c in cats)
    barras = "".join(
        f'<div class="g-brow {ACENTOS[i % 3]}"><span class="g-bl">{c["name"]}</span>'
        f'<span class="g-bt"><i style="width:{c["count"] / mx * 100:.0f}%"></i></span><b>{c["count"]}</b></div>'
        for i, c in enumerate(cats))
    extra = b.get("row2") or []
    extras = ""
    if extra:
        tarj = "".join(
            f'<div class="g-xcard {e["color"]}"><h3>{e["label"]}</h3><b>{e["big"]}</b><p>{e["sub"]}</p></div>' for e in extra)
        extras = f'<div class="g-bx" style="--cols:{min(len(extra), 3)}">{tarj}</div>'
    return (
        f'  <section class="slide g-nueva">\n    <span class="slide-num">{n:02d}</span>\n'
        '    <div class="g-bal"><div class="g-btitle">BALANCE FINAL</div><div class="g-bsub">LA COLECCION EN NUMEROS</div>\n'
        '      <div class="g-bgrid"><div class="g-bstats">'
        f'<div class="g-stat mg"><h3>JUEGOS</h3><b>{juegos}</b><p>{sub_juegos}</p></div>'
        f'<div class="g-stat cy"><h3>CATEGORIAS</h3><b>{ncat}</b><p>{sub_cat}</p></div>'
        f'<div class="g-stat ye"><h3>JOYAS</h3><b>{njoyas}</b><p>{sub_joyas}</p></div></div>'
        f'<div class="g-bchart"><div class="g-bct">JUEGOS POR CATEGORIA</div>{barras}{extras}</div></div></div>\n  </section>'
    )


def _s_cierre(n: int, data: dict, slug: str) -> str:
    c, p = data["cierre"], data.get("proximo")
    if p:
        bloque = (
            '<div class="g-csig"><div class="g-cthumb">'
            f'<span>{_esc(p.get("tag", ""))}</span><b>{_esc(p.get("consola", ""))}</b></div>'
            f'<div class="g-ctxt"><div class="g-csl">SIGUE CON</div><div class="g-cname">{_esc(p["titulo"])}</div></div></div>')
    else:
        bloque = f'<div class="g-csub">{c["sub"]}</div>' if c.get("sub") else ""
    return (
        f'  <section class="slide g-nueva">\n    <span class="slide-num">{n:02d}</span>\n{_mosaico(data, slug, tenue=True)}\n'
        f'    <div class="g-cierre"><div class="g-cpre">{c["pre"]}</div><div class="g-ctitle">{c["title"]}</div>{bloque}'
        '<div class="g-cta"><span class="mg">COMENTA TU FAVORITA</span><span class="cy">PIDE OTRA CONSOLA</span>'
        '<span class="ye">SUSCRIBETE</span></div></div>\n  </section>'
    )


# --------------------------------------------------------------------------- CSS

def css_nueva() -> str:
    """CSS de la grafica nueva; se agrega al final del bloque de estilo del deck."""
    return (
        ".g-mosw{position:absolute;inset:0;overflow:hidden;z-index:0}\n"
        ".g-nueva .g-mos{position:absolute;inset:-24px;display:grid;grid-template-columns:repeat(var(--cols),1fr);"
        "grid-template-rows:repeat(var(--filas),1fr);filter:blur(9px) brightness(.38) saturate(1.25);z-index:0}\n"
        ".g-mos.tenue{filter:blur(12px) brightness(.26) saturate(1.2)}\n"
        ".g-mos i{display:block;background-size:cover;background-position:center top}\n"
        ".fb.mg{background:linear-gradient(135deg,#7a0f46,#FF2E88)}.fb.cy{background:linear-gradient(135deg,#065a68,#00a8c0)}"
        ".fb.ye{background:linear-gradient(135deg,#7a5c00,#d9a800)}\n"
        ".g-portada,.g-cierre,.g-indice,.g-paneo,.g-triple,.g-hard,.g-bal{position:relative;z-index:2;height:100%}\n"
        # portada
        ".g-portada{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:18px;"
        "text-shadow:0 0 30px #000,0 0 10px #000}\n"
        ".g-sello{font:400 22px 'Press Start 2P';color:var(--ye);letter-spacing:6px;padding:12px 24px;border:2px solid var(--ye);"
        "background:rgba(6,3,15,.6)}\n"
        ".g-ptag{font:400 26px 'Press Start 2P';color:var(--cy);letter-spacing:6px}\n"
        ".g-ptitle{font:900 170px 'Orbitron';color:#fff;line-height:1;letter-spacing:2px}"
        ".g-ptitle .vs{color:var(--mg);text-shadow:0 0 34px rgba(255,46,136,.7)}\n"
        ".g-psub{font:400 38px 'Share Tech Mono';color:var(--ye);letter-spacing:6px}\n"
        ".g-pills{display:flex;gap:28px;margin-top:14px}\n"
        ".g-pill{display:flex;flex-direction:column;align-items:center;padding:16px 44px;background:rgba(6,3,15,.78);"
        "border:2px solid;border-radius:6px;min-width:260px}\n"
        ".g-pill b{font:900 76px 'Orbitron';line-height:1}.g-pill span{font:400 20px 'Press Start 2P';letter-spacing:3px;"
        "margin-top:10px;color:#fff}\n"
        ".g-pill.mg{border-color:var(--mg)}.g-pill.mg b{color:var(--mg)}.g-pill.cy{border-color:var(--cy)}.g-pill.cy b{color:var(--cy)}"
        ".g-pill.ye{border-color:var(--ye)}.g-pill.ye b{color:var(--ye)}\n"
        # indice
        ".g-indice{display:flex;flex-direction:column;align-items:center;gap:22px;padding-top:8px}\n"
        ".g-ititle{font:400 34px 'Press Start 2P';color:var(--mg);letter-spacing:8px;text-shadow:0 0 16px rgba(255,46,136,.5)}\n"
        ".g-igrid{display:grid;grid-template-columns:repeat(var(--cols),1fr);gap:22px;width:100%;max-width:1780px;flex:1;min-height:0;"
        "align-content:stretch}\n"
        ".g-icard{display:grid;grid-template-columns:auto 1fr;grid-template-rows:1fr auto;gap:6px 22px;padding:22px 26px;"
        "background:rgba(12,6,32,.82);border-left:6px solid var(--acc);border-radius:6px;align-items:center;min-height:0;overflow:hidden}\n"
        ".g-icard.mg{--acc:var(--mg)}.g-icard.cy{--acc:var(--cy)}.g-icard.ye{--acc:var(--ye)}\n"
        ".g-inum{font:900 64px 'Orbitron';color:var(--acc);grid-row:1}\n"
        ".g-itxt{grid-row:1;min-width:0}.g-iname{font:900 38px 'Orbitron';color:#fff;line-height:1.1;letter-spacing:2px}\n"
        ".g-icount{font:400 26px 'Share Tech Mono';color:rgba(255,255,255,.75);margin-top:8px}"
        ".g-icount b{font:900 56px 'Orbitron';color:var(--acc);margin-right:10px;vertical-align:middle}\n"
        ".g-ithumbs{grid-column:1/3;display:flex;gap:12px;height:var(--th,150px)}"
        ".g-ithumbs img,.g-ithumbs b{height:100%;width:auto;border-radius:3px;box-shadow:0 4px 14px rgba(0,0,0,.6)}"
        ".g-ithumbs b{aspect-ratio:.7}\n"
        # indice compacto (3 filas o mas): mismo apilado, todo mas bajo
        ".g-igrid.r3 .g-icard{padding:12px 22px;gap:4px 18px}\n"
        ".g-igrid.r3 .g-ithumbs{gap:10px}\n"
        ".g-igrid.r3 .g-inum{font-size:50px}.g-igrid.r3 .g-iname{font-size:30px}"
        ".g-igrid.r3 .g-icount{font-size:24px;margin-top:2px}.g-igrid.r3 .g-icount b{font-size:40px}\n"
        ".g-itotal{font:400 28px 'Press Start 2P';color:var(--cy);letter-spacing:6px}\n"
        # paneo
        ".g-paneo{display:grid;grid-template-columns:600px 1fr;gap:34px;align-items:stretch}\n"
        ".g-paneo.mg{--acc:var(--mg)}.g-paneo.cy{--acc:var(--cy)}.g-paneo.ye{--acc:var(--ye)}\n"
        ".g-pcard{display:flex;flex-direction:column;justify-content:center;gap:12px;padding:30px;"
        "background:linear-gradient(180deg,rgba(12,6,32,.9),rgba(45,27,105,.6));border-left:8px solid var(--acc);border-radius:8px;min-width:0}\n"
        ".g-pnum{font:400 24px 'Press Start 2P';color:var(--ye);letter-spacing:4px}\n"
        ".g-pname{font:900 50px 'Orbitron';color:#fff;line-height:1.08;letter-spacing:3px;text-shadow:0 0 18px rgba(255,46,136,.4);"
        "overflow-wrap:anywhere}.g-pname.n2{font-size:42px}.g-pname.n3{font-size:36px;letter-spacing:2px}\n"
        ".g-pbig{font:900 170px 'Orbitron';color:var(--acc);line-height:.95;margin-top:10px;text-shadow:0 0 26px currentColor}\n"
        ".g-pbigl{font:400 24px 'Press Start 2P';color:#fff;letter-spacing:3px;line-height:1.5}\n"
        ".g-ptease{margin-top:14px;padding-top:16px;border-top:1px solid rgba(255,255,255,.2)}"
        ".g-ptease>span{font:400 20px 'Press Start 2P';color:var(--cy);letter-spacing:3px}\n"
        ".g-pthumbs{display:flex;gap:14px;margin-top:14px;height:var(--th,150px)}"
        ".g-pthumbs img,.g-pthumbs b{height:100%;width:auto;border-radius:3px;box-shadow:0 4px 14px rgba(0,0,0,.6)}"
        ".g-pthumbs b{aspect-ratio:.7}\n"
        ".g-paneo .gp-tv{display:flex;align-items:center;justify-content:center;min-width:0}\n"
        ".g-paneo .gp-tv.tvw{container-type:size;width:100%}\n"
        # triple
        ".g-triple{display:flex;flex-direction:column;gap:14px;max-width:1830px;margin:0 auto}\n"
        ".g-triple.mg{--acc:var(--mg)}.g-triple.cy{--acc:var(--cy)}.g-triple.ye{--acc:var(--ye)}\n"
        ".g-thead{align-self:center;font:400 26px 'Press Start 2P';letter-spacing:5px;color:#fff;padding:10px 22px;"
        "border:2px solid var(--acc);background:rgba(6,3,15,.7)}.g-thead span{color:var(--acc)}\n"
        ".g-tgrid{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:24px;flex:1;min-height:0}\n"
        ".g-cell{position:relative;display:flex;flex-direction:column;gap:14px;padding:18px;border-radius:10px;overflow:hidden;"
        "background:rgba(12,6,32,.9);isolation:isolate;min-width:0}\n"
        ".g-cell::before{content:\"\";position:absolute;inset:-30px;background:var(--bg) center/cover;"
        "filter:blur(22px) brightness(.32) saturate(1.3);z-index:-1}\n"
        ".g-cell.nobg::before{background:linear-gradient(135deg,#2D1B69,#4a2a99)}\n"
        ".g-celltv{display:flex;justify-content:center}"
        ".g-celltv .tarrovision.tvn{width:100%;height:auto;aspect-ratio:auto;max-width:none}\n"
        ".g-cellinfo{display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto 1fr;gap:12px 20px;align-items:center;min-height:0;flex:1}\n"
        # la caja conserva su proporcion (--ar = ancho / alto): vertical hasta 215 px de alto, apaisada hasta 235 px de ancho
        ".g-caja{height:min(215px,calc(235px / var(--ar,.7)));width:auto;border-radius:4px;"
        "box-shadow:0 8px 24px rgba(0,0,0,.7),0 0 0 2px rgba(255,255,255,.12);transform:rotate(-3deg);flex:none}\n"
        ".g-caja.fb{height:215px;aspect-ratio:.7;display:flex;align-items:center;justify-content:center;padding:10px;text-align:center}"
        ".g-caja.fb span{font:900 20px 'Orbitron';color:#fff;line-height:1.2}\n"
        ".g-celltxt{display:flex;flex-direction:column;gap:12px;min-width:0}\n"
        ".g-celltag{grid-column:1/3;justify-self:start;font:400 20px 'Press Start 2P';color:#04121a;background:var(--cy);padding:7px 12px;letter-spacing:2px}\n"
        ".g-celltitle.l{font-size:28px}\n"
        ".g-celltitle{font:900 36px 'Orbitron';color:#fff;line-height:1.1;overflow-wrap:break-word}\n"
        ".g-chips{display:flex;gap:10px;flex-wrap:wrap}"
        ".g-chips span{font:400 24px 'Share Tech Mono';color:var(--cy);border:2px solid rgba(0,229,255,.5);"
        "background:rgba(0,229,255,.08);padding:4px 14px;border-radius:20px}"
        ".g-chips span.y{color:var(--ye);border-color:rgba(255,210,63,.6);background:rgba(255,210,63,.1)}\n"
        # hardware
        ".g-hard{display:flex;flex-direction:column;align-items:center;gap:10px}\n"
        ".g-htitle{font:900 90px 'Orbitron';color:#fff;line-height:1}"
        ".g-hsub{font:400 30px 'Share Tech Mono';color:var(--mg);letter-spacing:6px;margin-bottom:12px}\n"
        ".g-hgrid{display:grid;grid-template-columns:repeat(var(--cols),1fr);gap:26px;width:100%;max-width:1780px;flex:1;min-height:0}\n"
        ".g-hcard{display:flex;flex-direction:column;gap:12px;padding:20px 24px;background:var(--card-bg);"
        "border-top:6px solid var(--acc);border-radius:6px;min-height:0;overflow:hidden}\n"
        ".g-hcard.mg{--acc:var(--mg)}.g-hcard.cy{--acc:var(--cy)}.g-hcard.ye{--acc:var(--ye)}\n"
        ".g-hfoto{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;border-radius:6px;overflow:hidden;"
        "background:linear-gradient(135deg,#1a1230,#2D1B69)}\n"
        ".g-hfoto img{width:100%;height:100%;object-fit:contain}\n"
        ".g-hfoto.sin{background:repeating-linear-gradient(45deg,rgba(255,255,255,.04) 0 14px,transparent 14px 28px),"
        "linear-gradient(135deg,#1a1230,#2D1B69);border:2px dashed rgba(255,255,255,.25)}\n"
        ".g-hfoto span{font:400 22px 'Press Start 2P';color:rgba(255,255,255,.4);letter-spacing:4px}\n"
        ".g-hname{font:900 34px 'Orbitron';color:#fff;line-height:1.1}"
        ".g-hcard p{font:400 24px 'Share Tech Mono';color:rgba(255,255,255,.82);line-height:1.35}\n"
        # balance
        ".g-bal{display:flex;flex-direction:column;align-items:center;gap:6px}\n"
        ".g-btitle{font:900 90px 'Orbitron';color:#fff;line-height:1}"
        ".g-bsub{font:400 30px 'Share Tech Mono';color:var(--mg);letter-spacing:6px;margin-bottom:16px}\n"
        ".g-bgrid{display:grid;grid-template-columns:520px 1fr;gap:34px;width:100%;max-width:1780px;flex:1;min-height:0}\n"
        ".g-bstats{display:flex;flex-direction:column;gap:18px}\n"
        ".g-stat{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;background:var(--card-bg);"
        "border-top:5px solid var(--c);border-radius:6px}\n"
        ".g-stat.mg,.g-xcard.mg{--c:var(--mg)}.g-stat.cy,.g-xcard.cy{--c:var(--cy)}.g-stat.ye,.g-xcard.ye{--c:var(--ye)}\n"
        ".g-stat h3,.g-xcard h3{font:400 20px 'Press Start 2P';color:var(--ye);letter-spacing:4px}"
        ".g-stat b{font:900 120px 'Orbitron';color:var(--c);line-height:1;text-shadow:0 0 22px currentColor}"
        ".g-stat p,.g-xcard p{font:400 24px 'Share Tech Mono';color:rgba(255,255,255,.78)}\n"
        ".g-bchart{display:flex;flex-direction:column;gap:12px;padding:24px 32px;background:var(--card-bg);border-radius:6px;min-height:0}\n"
        ".g-bct{font:400 22px 'Press Start 2P';color:var(--cy);letter-spacing:4px;margin-bottom:4px}\n"
        ".g-brow{display:grid;grid-template-columns:470px 1fr 70px;gap:20px;align-items:center}\n"
        ".g-brow.mg{--c:var(--mg)}.g-brow.cy{--c:var(--cy)}.g-brow.ye{--c:var(--ye)}\n"
        ".g-bl{font:900 22px 'Orbitron';color:#fff;letter-spacing:1px;white-space:nowrap}"
        ".g-bt{height:30px;background:rgba(255,255,255,.07);border-radius:4px;overflow:hidden}"
        ".g-bt i{display:block;height:100%;background:var(--c);box-shadow:0 0 14px var(--c)}"
        ".g-brow b{font:900 34px 'Orbitron';color:var(--c);text-align:right}\n"
        ".g-bx{display:grid;grid-template-columns:repeat(var(--cols),1fr);gap:18px;margin-top:auto}\n"
        ".g-xcard{display:flex;flex-direction:column;align-items:center;padding:12px;border-top:4px solid var(--c);"
        "background:rgba(255,255,255,.04)}.g-xcard b{font:900 60px 'Orbitron';color:var(--c);line-height:1.1}\n"
        # cierre
        ".g-cierre{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;text-align:center}\n"
        ".g-cpre{font:400 26px 'Press Start 2P';color:var(--cy);letter-spacing:8px}\n"
        ".g-ctitle{font:900 120px 'Orbitron';color:var(--cy);text-shadow:0 0 30px rgba(0,229,255,.6);line-height:1}\n"
        ".g-csub{font:400 30px 'Share Tech Mono';color:rgba(255,255,255,.85);max-width:1200px;line-height:1.5;"
        "text-shadow:0 0 16px #000}\n"
        ".g-csig{display:flex;align-items:center;gap:30px;padding:22px 34px;background:rgba(6,3,15,.8);border:2px solid var(--mg);"
        "border-radius:10px;box-shadow:0 0 30px rgba(255,46,136,.35)}\n"
        ".g-cthumb{width:320px;aspect-ratio:16/9;display:flex;flex-direction:column;align-items:center;justify-content:center;"
        "background:linear-gradient(135deg,#2D1B69,#FF2E88);border-radius:6px}"
        ".g-cthumb span{font:400 20px 'Press Start 2P';color:var(--ye);letter-spacing:3px}"
        ".g-cthumb b{font:900 64px 'Orbitron';color:#fff}\n"
        ".g-ctxt{text-align:left}.g-csl{font:400 20px 'Press Start 2P';color:var(--mg);letter-spacing:4px}"
        ".g-cname{font:900 52px 'Orbitron';color:#fff;margin-top:10px;line-height:1.1}\n"
        ".g-cta{display:flex;gap:26px;font:400 24px 'Press Start 2P';letter-spacing:3px}"
        ".g-cta span{padding:14px 22px;border:2px solid;background:rgba(6,3,15,.7)}\n"
        ".g-cta .mg{color:var(--mg);border-color:var(--mg)}.g-cta .cy{color:var(--cy);border-color:var(--cy)}"
        ".g-cta .ye{color:var(--ye);border-color:var(--ye)}\n"
        # capa de notas (tecla N): nunca sale en las capturas, que fuerzan read-mode apagado
        ".g-nueva .notas{display:none}\n"
        "body.read-mode .slide.active .notas{display:block;position:absolute;top:0;right:0;bottom:0;width:600px;z-index:30;"
        "background:rgba(6,3,15,.97);border-left:3px solid var(--mg);padding:26px 30px;overflow-y:auto}\n"
        ".notas-t{font:400 20px 'Press Start 2P';color:var(--mg);letter-spacing:3px;margin-bottom:18px;line-height:1.5}\n"
        ".notas ul{list-style:none}.notas li{font:400 24px 'Share Tech Mono';color:var(--bo);line-height:1.4;padding:6px 0;"
        "border-bottom:1px solid rgba(255,255,255,.1)}\n"
        "body.read-mode::after{content:\"MODO LECTURA\";position:fixed;top:62px;right:20px;z-index:300;font:400 16px 'Press Start 2P';"
        "color:#000;background:var(--ye);padding:6px 10px}\n"
    )


# --------------------------------------------------------------------------- generador

def generar(data: dict, out_slug: str, out_dir: Path | None = None, lista: bool = True) -> Path:
    """Deck de coleccion con la grafica nueva. Llamado desde coleccion_deck.generar_deck."""
    import copy
    data = copy.deepcopy(data)            # _cajas() anota rutas en el data: no tocar el del driver
    out_dir = Path(out_dir) if out_dir else D.REPO / "studio" / "colecciones"
    out_dir.mkdir(parents=True, exist_ok=True)
    _cajas(data, out_dir, out_slug)
    variante = _variante_triple(data)

    base = D.BASE.read_text(encoding="utf-8")
    head = base[: base.index("<body>") + len("<body>")]
    foot = base[base.index('<nav class="footer">'):]
    head = _inyectar(head, "</style>", css_nueva() + TV.css("nueva") + TV.css("ancha") + "</style>")
    foot = _inyectar(foot, "</body>", ESCRIBIR_NOTAS_JS + "</body>")
    head = re.sub(r"<title>.*?</title>", f'<title>RETROTARROS · {data["doc_title"]}</title>', head, flags=re.DOTALL)

    cats = data["categorias"]
    slides, n = [], 1
    slides.append(_s_portada(n, data, out_slug)); n += 1
    slides.append(_s_indice(n, data)); n += 1
    for ci, c in enumerate(cats, 1):
        slides.append(_s_paneo(n, ci, len(cats), c)); n += 1
        slides.append(_s_triple(n, ci, c, variante)); n += 1
    if data.get("hardware"):
        slides.append(_s_hardware(n, data)); n += 1
    slides.append(_s_balance(n, data)); n += 1
    slides.append(_s_cierre(n, data, out_slug)); n += 1

    hdr = (
        '\n\n<header>\n'
        '  <div class="hdr-logo">RETROTARROS</div>\n'
        f'  <div class="hdr-tag">{data["header_tag"]}</div>\n'
        '  <div class="hdr-rec"><div class="dot"></div>EN VIVO</div>\n'
        '</header>\n\n'
        '<div class="deck" id="deck">\n\n' + "\n\n".join(slides) + '\n\n</div>\n\n'
    )
    out = out_dir / f"{out_slug}.html"
    out.write_text(head + hdr + foot, encoding="utf-8")
    if lista:
        print("LISTA ->", D._escribir_lista_md(data, out_slug))
    return out
