"""
resena_deck.py - Retrotarros Studio Suite
Genera el deck del formato RESENA: retrospectiva de UN solo juego ("¿envejecio
bien?"), <=10 min, talento alterna Luis/Koko 1 y 1 (nunca los dos juntos, nunca
cierra con bateria). Aprobado con Luis 2026-07-21 via brainstorming skill.

Estructura (8 slides fijas, sin excepciones; +1 opcional si el juego vino de
un pedido de la comunidad -- ver 00 PEDIDO):
  00 PEDIDO         - OPCIONAL, solo si data["pedido"] existe. Muestra la
                       captura de pantalla del comentario que pidio el juego
                       (leida en voz alta como cold-open) antes de revelar el
                       nombre en la Portada. Aprobado con Luis 2026-08-15.
  01 PORTADA        - SOLO "RESEÑA RETROTARRISTICA" + titulo del juego. NUNCA
                       el nombre del presentador (se identifica hablando).
  02 FICHA TECNICA  - box art + consola/anio/developer/genero + EN COLECCION.
                       Si no hay box art real (regla: nunca logo/artwork promo),
                       usa fallback con tarjeta de color (ver _ficha_cart).
  03 CONTEXTO       - que prometia el juego en su epoca.
  04 COMPARATIVA    - OBLIGATORIO en toda resena (regla Luis 2026-07-26). Dos
                       TarroVision lado a lado + VS al medio, para contexto
                       historico que se compara mejor viendolo lado a lado (ej.
                       arcade original vs puerto casero, original vs secuela,
                       version occidental vs japonesa). Titulo SIEMPRE
                       "COMPARATIVA", agnostico sin importar que se compare.
                       SIN dato/texto en el slide (ajuste Luis 2026-07-26): solo
                       las dos pantallas ocupando todo el alto, el contexto se
                       cuenta hablado mientras se muestra el gameplay. Las
                       namebox bajo cada pantalla quedan VACIAS a proposito: el
                       nombre se escribe encima en la edicion posterior, nunca
                       se hardcodea en el HTML/capture.
  05 TARROVISION 1  - jugabilidad hoy (gameplay placeholder + dato).
  06 TARROVISION 2  - graficos/sonido hoy (gameplay placeholder + dato).
  07 VEREDICTO      - etiqueta cualitativa grande + resumen.
  08 CIERRE         - suscribete + campana. NUNCA bateria.

Capa de notas (tecla N / boton / click derecho oculto) copiada 1:1 del patron
de los episodios SEGA (studio/master-system-top-mundial.html) - no reinventar.
Texto publico mas grande que el resto de los decks de episodio (feedback Luis:
"algunos nos ven desde la tv"), sin llegar a grotesco.
Navegacion: boton, flechas de teclado, Y click en el deck (mitad derecha
avanza, mitad izquierda retrocede; click dentro de .notas no cambia de slide).

Box art en studio/resenas/img/resenas/<key>.jpg (key = slug del titulo, o el
que se pase explicito en data['img_key']). Salida en studio/resenas/<slug>.html
(carpeta APARTE del resto de episodios, pedido explicito de Luis 2026-07-21).
Nota 2026-07-23: img/ vive DENTRO de resenas/ (Luis reorganizo
studio/img/resenas/ -> studio/resenas/img/resenas/), no al lado como los
demas episodios -- por eso el src del HTML es relativo directo, sin '../'.
"""
from __future__ import annotations
import os
import re
from pathlib import Path

from resena_lint import ESCALA_VEREDICTO, formatear, revisar

REPO = Path(__file__).resolve().parent.parent


def _slug(s: str) -> str:
    s = s.lower()
    for a, b in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", "ü": "u"}.items():
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _nueva(data: dict) -> bool:
    """La grafica nueva (portada con caja, chips, escala, viñetas...) solo se activa con
    data['grafica'] == 'nueva'. Sin la marca, o con 'clasica', el HTML sale como siempre."""
    return data.get("grafica") == "nueva"


def _notas(bloque: dict | None, previo: str = "") -> str:
    """<aside class="notas"> por slide. bloque = {'titulo':.., 'lineas':[...], 'cue': '...'}
    `previo` es HTML que va antes del titulo del bloque (ej. POR CONFIRMAR)."""
    if not bloque and not previo:
        return ""
    bloque = bloque or {}
    titulo = _esc(bloque.get("titulo", "NOTAS"))
    lineas = "".join(f'<div class="n-line">{_esc(t)}</div>' for t in bloque.get("lineas", []))
    cue = f'<div class="n-cue">{_esc(bloque["cue"])}</div>' if bloque.get("cue") else ""
    cuerpo = f"<h4>{titulo}</h4>{lineas}{cue}" if bloque else ""
    return f'<aside class="notas">{previo}{cuerpo}</aside>'


def _bloque_por_confirmar(data: dict) -> str:
    """Bloque destacado al inicio de las notas de la portada con lo que hay que
    verificar antes de grabar (data['por_confirmar'], lista de textos cortos)."""
    items = data.get("por_confirmar") or []
    if not items:
        return ""
    lineas = "".join(f'<div class="n-line">{_esc(t)}</div>' for t in items)
    return f'<div class="n-pc"><h4>POR CONFIRMAR ANTES DE GRABAR</h4>{lineas}</div>'


def _ficha_cart(data: dict) -> str:
    """Box art real si existe studio/resenas/img/resenas/<key>.jpg; si no, fallback con
    tarjeta de color (regla del canal: nunca logo/artwork promocional)."""
    key = data.get("img_key") or _slug(data["juego"])
    img_path = REPO / "studio" / "resenas" / "img" / "resenas" / f"{key}.jpg"
    if img_path.exists():
        # el HTML vive en studio/resenas/, la imagen en studio/resenas/img/resenas/
        # -> ruta relativa directa, img/ es hija de resenas/, no hermana.
        return f'<div class="ficha-cart"><img src="img/resenas/{key}.jpg" alt="" onerror="this.style.display=\'none\'"></div>'
    return (
        '<div class="ficha-cart"><div class="ficha-fallback">'
        f'<div class="ff-title">{_esc(data["juego"])}</div>'
        f'<div class="ff-sub">{_esc(data.get("consola", ""))}</div>'
        '</div></div>'
    )


def _slide_pedido(num: int, data: dict) -> str:
    """Slide 00 opcional -- cold-open con la captura del comentario que pidio
    el juego, leida en voz alta antes de revelar el nombre en la Portada
    (regla Luis 2026-08-15: el reveal va al INICIO, no despues del veredicto,
    porque ahi ya se dijo/mostro el nombre todo el video y pierde el gancho)."""
    pedido = data["pedido"]
    key = pedido.get("img_key") or f'{data.get("img_key") or _slug(data["juego"])}-pedido'
    img_path = REPO / "studio" / "resenas" / "img" / "resenas" / f"{key}.png"
    img_html = (
        f'<img class="ped-shot" src="img/resenas/{key}.png" alt="" onerror="this.style.display=\'none\'">'
        if img_path.exists() else ""
    )
    cta = _esc(pedido.get("cta") or "Y eso hicimos.")
    return (
        f'<section class="slide active"><span class="slide-num">{num:02d}</span>'
        '<div class="pedido">'
        '<div class="ped-tag">NOS LO PIDIERON</div>'
        f'{img_html}'
        f'<div class="ped-cta">{cta}</div>'
        '</div>'
        f'{_notas(data.get("notas", {}).get("pedido"))}'
        '</section>'
    )


def _caja_key(data: dict) -> str | None:
    """Clave de la caja (studio/resenas/img/resenas/<key>.jpg) si el archivo existe."""
    key = data.get("img_key") or _slug(data["juego"])
    ruta = REPO / "studio" / "resenas" / "img" / "resenas" / f"{key}.jpg"
    return key if ruta.exists() else None


def _caja_ancha(key: str) -> bool:
    """True si la caja es cuadrada o apaisada (ancho/alto > 0.85): en la grafica nueva se
    acota por ancho para que no tape el texto. Si no se puede medir, se trata como alta."""
    try:
        from PIL import Image
        with Image.open(REPO / "studio" / "resenas" / "img" / "resenas" / f"{key}.jpg") as im:
            return im.width / im.height > 0.85
    except Exception:  # noqa: BLE001
        return False


def _slide_portada(num: int, data: dict, active: bool = True) -> str:
    cls = "slide active" if active else "slide"
    caja = _caja_key(data) if _nueva(data) else None
    if caja:
        estilo = ' style="width:30%;height:auto"' if _caja_ancha(caja) else ""
        return (
            f'<section class="{cls}" style="overflow:hidden"><span class="slide-num">{num:02d}</span>'
            f'<div class="portada-fondo" style="background-image:url(img/resenas/{caja}.jpg)"></div>'
            f'<img class="portada-caja"{estilo} src="img/resenas/{caja}.jpg" alt="">'
            '<div class="portada con-caja">'
            '<div class="ep-tag">RESEÑA RETROTARRISTICA</div>'
            f'<div class="ep-title">{_esc(data["juego"]).upper()}</div>'
            f'<div class="ep-sub">{_esc(data["gancho_sub"])}</div>'
            '</div>'
            f'{_notas(data.get("notas", {}).get("portada"), _bloque_por_confirmar(data))}'
            '</section>'
        )
    return (
        f'<section class="{cls}"><span class="slide-num">{num:02d}</span>'
        '<div class="portada">'
        '<div class="ep-tag">RESEÑA RETROTARRISTICA</div>'
        f'<div class="ep-title">{_esc(data["juego"]).upper()}</div>'
        f'<div class="ep-sub">{_esc(data["gancho_sub"])}</div>'
        '</div>'
        f'{_notas(data.get("notas", {}).get("portada"), _bloque_por_confirmar(data))}'
        '</section>'
    )


def _chips_plataformas(data: dict) -> str:
    """Chips de plataforma en orden de lanzamiento (grafica nueva). Sale de data['plataformas']
    ([nombre, año], ignora lo mal formado) y, si no hay ninguno valido, de consola separada por '·'."""
    pares: list[tuple[str, str]] = []
    plataformas = data.get("plataformas")
    if isinstance(plataformas, (list, tuple)):
        for p in plataformas:
            if isinstance(p, (list, tuple)) and p and isinstance(p[0], str) and p[0].strip():
                anio = str(p[1]).strip() if len(p) > 1 and p[1] else ""
                pares.append((p[0].strip(), anio))
    if not pares:
        pares = [(n.strip(), "") for n in str(data.get("consola") or "").split("·") if n.strip()]
    chips = []
    for i, (nombre, anio) in enumerate(pares):
        extra = f"<i>{_esc(anio)}</i>" if anio else ""
        clase = "chip first" if i == 0 else "chip"
        chips.append(f'<span class="{clase}"><b>{_esc(nombre.upper())}</b>{extra}</span>')
    if not chips:
        return ""
    return '<div class="chips">' + '<span class="arr">▸</span>'.join(chips) + "</div>"


def _slide_ficha(num: int, data: dict) -> str:
    # en_coleccion: True | False | "familia" (no esta, pero hay algo de la familia
    # del juego: se explica en la linea opcional familia_texto).
    if data.get("en_coleccion") is True:
        owned = '<div class="ficha-owned">EN LA COLECCION</div>'
    else:
        owned = '<div class="ficha-owned faltan">NO ESTA EN LA COLECCION</div>'
        if data.get("en_coleccion") == "familia" and data.get("familia_texto"):
            owned += f'<div class="ficha-familia">{_esc(data["familia_texto"])}</div>'
    consola = (_chips_plataformas(data) if _nueva(data) else "") or _esc(data["consola"])
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        '<div class="ficha-detail">'
        f'{_ficha_cart(data)}'
        '<div class="ficha-info">'
        f'<div class="ficha-title">{_esc(data["juego"]).upper()}</div>'
        '<div class="ficha-stats">'
        f'<div class="ficha-stat"><span class="lbl">CONSOLA</span><span class="val">{consola}</span></div>'
        f'<div class="ficha-stat"><span class="lbl">AÑO</span><span class="val">{_esc(data["anio"])}</span></div>'
        f'<div class="ficha-stat"><span class="lbl">DESARROLLADOR</span><span class="val">{_esc(data["developer"])}</span></div>'
        f'<div class="ficha-stat"><span class="lbl">GENERO</span><span class="val">{_esc(data["genero"])}</span></div>'
        '</div>'
        f'{owned}'
        '</div></div>'
        f'{_notas(data.get("notas", {}).get("ficha"))}'
        '</section>'
    )


def _slide_contexto(num: int, data: dict) -> str:
    caja = _caja_key(data) if _nueva(data) else None
    if caja:
        estilo_img = ' style="width:30vw;height:auto"' if _caja_ancha(caja) else ""
        return (
            f'<section class="slide"><span class="slide-num">{num:02d}</span>'
            '<div class="contexto con-imagen">'
            f'<img class="ctx-img"{estilo_img} src="img/resenas/{caja}.jpg" alt="">'
            '<div class="ctx-texto">'
            '<div class="ctx-tag">CONTEXTO DE EPOCA</div>'
            f'<div class="ctx-year">Llegamos a <b>{_esc(data["anio"])}</b></div>'
            f'<div class="ctx-body">{_esc(data["contexto_texto"])}</div>'
            '</div></div>'
            f'{_notas(data.get("notas", {}).get("contexto"))}'
            '</section>'
        )
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        '<div class="contexto">'
        '<div class="ctx-tag">CONTEXTO DE EPOCA</div>'
        f'<div class="ctx-year">Llegamos a <b>{_esc(data["anio"])}</b></div>'
        f'<div class="ctx-body">{_esc(data["contexto_texto"])}</div>'
        '</div>'
        f'{_notas(data.get("notas", {}).get("contexto"))}'
        '</section>'
    )


def _tv(ch: int) -> str:
    return (
        '<div class="tarrovision">'
        f'<div class="tv-controls-top"><span class="tv-led"></span><span class="tv-brand">TARROVISION</span><span class="tv-channel">CH {ch:02d}</span></div>'
        '<div class="tv-screen"><div class="tv-screen-inner"><div class="tv-noscreen">'
        '<div class="tv-noscreen-big">NO SIGNAL</div><div class="tv-noscreen-sub">Inserta gameplay aqui</div></div></div></div>'
        '<div class="tv-controls-bottom"><div class="tv-knob"></div><div class="tv-knob cy"></div><div class="tv-speaker"></div></div>'
        '</div>'
    )


def _vinetas(data: dict) -> str:
    """Tres viñetas numeradas (grafica nueva). Vacio si no hay exactamente 3 pares [titulo, texto]
    bien formados: en ese caso la slide conserva el bloque de texto."""
    v = data.get("jugabilidad_vinetas")
    if not isinstance(v, (list, tuple)) or len(v) != 3:
        return ""
    filas = []
    for i, e in enumerate(v, 1):
        if not (isinstance(e, (list, tuple)) and len(e) >= 2 and isinstance(e[0], str) and isinstance(e[1], str)):
            return ""
        filas.append(
            f'<div class="vineta"><div class="vn">{i:02d}</div><div class="vt">'
            f'<div class="vtit">{_esc(e[0].upper())}</div><div class="vtxt">{_esc(e[1])}</div></div></div>'
        )
    return '<div class="gp-vinetas">' + "".join(filas) + "</div>"


def _compositor(data: dict) -> str:
    """Etiqueta BANDA SONORA con el credito del compositor (grafica nueva)."""
    texto = data.get("audiovisual_compositor")
    if not isinstance(texto, str) or not texto.strip():
        return ""
    return (f'<div class="gp-compositor"><div class="gc-lbl">BANDA SONORA</div>'
            f'<div class="gc-txt">{_esc(texto)}</div></div>')


def _proxima(data: dict) -> str:
    """Tarjeta PROXIMA RESEÑA del cierre (grafica nueva). Opcional: se completa despues de grabar."""
    p = data.get("proxima")
    if not isinstance(p, dict) or not isinstance(p.get("juego"), str) or not p["juego"].strip():
        return ""
    meta = " · ".join(str(x).strip() for x in (p.get("consola"), p.get("anio")) if x and str(x).strip())
    key = p.get("img_key")
    hay_img = isinstance(key, str) and (REPO / "studio" / "resenas" / "img" / "resenas" / f"{key}.jpg").exists()
    img = f'<img class="cp-img" src="img/resenas/{key}.jpg" alt="">' if hay_img else ""
    return (
        '<div class="cierre-proxima">' + img + '<div class="cp-info">'
        '<div class="cp-lbl">PROXIMA RESEÑA</div>'
        f'<div class="cp-juego">{_esc(p["juego"])}</div>'
        f'<div class="cp-meta">{_esc(meta)}</div></div></div>'
    )


def _slide_tarrovision(num: int, titulo: str, ch: int, dato: str, notas_bloque, data: dict,
                       reemplazo: str = "", extra: str = "") -> str:
    """`reemplazo` sustituye el bloque EL DATO (viñetas); `extra` va debajo (compositor)."""
    dato_html = reemplazo or f'<div class="gp-dato"><span class="lbl">EL DATO</span>{_esc(dato)}</div>'
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        f'<div class="gp-head"><div class="gp-title">{_esc(titulo)}</div>'
        f'<div class="gp-meta">{_esc(data["consola"]).upper()} · {_esc(data["anio"])} · GAMEPLAY</div></div>'
        '<div class="gp-body">'
        f'<div class="gp-tv">{_tv(ch)}</div>'
        '<div class="gp-side">'
        f'{dato_html}{extra}'
        '</div></div>'
        f'{_notas(notas_bloque)}'
        '</section>'
    )


def _slide_tarrovision_dual(num: int, ch_a: int, ch_b: int, notas_bloque, data: dict) -> str:
    """Slide de comparativa (2 TarroVision lado a lado + VS al medio), para
    contexto historico (ej. arcade vs puerto casero, original vs secuela).
    Titulo SIEMPRE "COMPARATIVA" -- agnostico, sin importar que se compare
    (regla Luis 2026-07-26). SIN dato/texto abajo -- el slide es solo las dos
    pantallas + VS, todo el contexto se dice hablado mientras se ve el gameplay
    (regla Luis 2026-07-26, ajuste post-captura: "es mejor ocuparlo en mostrar
    gameplay"). Las namebox quedan VACIAS a proposito -- el nombre se escribe
    encima en la edicion posterior, no se hardcodea."""
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        '<div class="gp-head"><div class="gp-title">COMPARATIVA</div>'
        f'<div class="gp-meta">{_esc(data["consola"]).upper()} · {_esc(data["anio"])}</div></div>'
        '<div class="dual-grid">'
        f'<div class="dual-cell">{_tv(ch_a)}<div class="tv-namebox"></div></div>'
        '<div class="dual-vs">VS</div>'
        f'<div class="dual-cell">{_tv(ch_b)}<div class="tv-namebox"></div></div>'
        '</div>'
        f'{_notas(notas_bloque)}'
        '</section>'
    )


def _escala_veredicto(data: dict) -> str:
    """Las cuatro categorias del canal, con la del veredicto encendida (gráfica nueva)."""
    tag = str(data.get("veredicto_tag") or "").strip().upper()
    pastillas = "".join(
        f'<div class="ver-pill{" on" if t == tag else ""}">{t}</div>' for t in ESCALA_VEREDICTO
    )
    return f'<div class="ver-escala">{pastillas}</div>'


def _slide_veredicto(num: int, data: dict) -> str:
    escala = _escala_veredicto(data) if _nueva(data) else ""
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        '<div class="veredicto">'
        '<div class="ver-pre">VEREDICTO RETROTARROS</div>'
        f'<div class="ver-tag">{_esc(data["veredicto_tag"]).upper()}</div>'
        f'{escala}'
        f'<div class="ver-resumen">{_esc(data["veredicto_resumen"])}</div>'
        '</div>'
        f'{_notas(data.get("notas", {}).get("veredicto"))}'
        '</section>'
    )


def _slide_cierre(num: int, data: dict) -> str:
    sub = data.get("cierre_sub") or ('Activa la campana para no perderte la proxima reseña. '
                                      '¿Que juego quieres que revisemos? Comenta abajo.')
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        '<div class="divider">'
        '<div class="pre mg">RETROTARROS</div>'
        '<div class="title mg">SUSCRIBETE</div>'
        f'<div class="sub">{_esc(sub)}</div>'
        f'{_proxima(data) if _nueva(data) else ""}'
        '</div>'
        f'{_notas(data.get("notas", {}).get("cierre"))}'
        '</section>'
    )


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
:root{--mg:#FF2E88;--cy:#00E5FF;--ye:#FFD23F;--dk:#06030f;--bo:#F5F0E8;--card-bg:rgba(12,6,32,.92)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:var(--dk);font-family:'Share Tech Mono',monospace;color:var(--bo)}
body{background-image:radial-gradient(ellipse 100% 50% at 50% -5%,rgba(255,46,136,.12) 0,transparent 65%),repeating-linear-gradient(0deg,transparent 0 39px,rgba(255,255,255,.014) 39px 40px),repeating-linear-gradient(90deg,transparent 0 39px,rgba(255,255,255,.014) 39px 40px)}
header{position:fixed;top:0;left:0;right:0;height:56px;z-index:200;background:rgba(6,3,15,.97);border-bottom:2px solid var(--mg);display:flex;align-items:center;justify-content:space-between;padding:0 28px}
.hdr-logo{font-family:'Orbitron';font-weight:900;font-size:23px;color:var(--mg);text-shadow:0 0 14px rgba(255,46,136,.6);letter-spacing:3px}
.hdr-tag{font-family:'Share Tech Mono';font-size:14px;color:var(--ye);letter-spacing:3px}
.hdr-rec{display:flex;align-items:center;gap:8px;font-family:'Press Start 2P';font-size:9px;color:var(--mg)}
.dot{width:10px;height:10px;background:var(--mg);border-radius:50%;animation:blink 1.2s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.15}}
.deck{position:fixed;top:56px;left:0;right:0;bottom:64px;overflow:hidden;cursor:pointer}
.slide{position:absolute;inset:0;padding:24px 40px;opacity:0;pointer-events:none;transition:opacity .22s;display:flex;flex-direction:column}
.slide.active{opacity:1;pointer-events:auto}
.slide-num{position:absolute;top:14px;right:22px;font-family:'Press Start 2P';font-size:10px;color:rgba(255,255,255,.22);letter-spacing:2px}

/* PORTADA (sin nombre de presentador: se identifica hablando, no en pantalla) */
.portada{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.portada .ep-tag{font-family:'Press Start 2P';font-size:15px;color:var(--cy);letter-spacing:5px;margin-bottom:24px}
.portada .ep-title{font-family:'Orbitron';font-weight:900;font-size:90px;line-height:1;color:#fff;margin-bottom:20px}
.portada .ep-sub{font-family:'Share Tech Mono';font-size:25px;color:var(--ye);letter-spacing:2px;max-width:1100px}

/* PEDIDO (00, opcional -- captura del comentario que pidio el juego) */
.pedido{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:28px}
.pedido .ped-tag{font-family:'Press Start 2P';font-size:15px;color:var(--cy);letter-spacing:5px}
.pedido .ped-shot{width:1500px;max-width:92vw;height:auto;max-height:700px;border-radius:14px;border:2px solid rgba(255,255,255,.25);box-shadow:0 22px 60px rgba(0,0,0,.7)}
.pedido .ped-cta{font-family:'Orbitron';font-weight:900;font-size:38px;color:var(--ye)}

/* FICHA TECNICA -- columna de la caja con ancho dinamico (minmax) para que
   quepan bien tanto cajas verticales (3:4, la mayoria NTSC) como horizontales
   (algunas ediciones/plataformas) sin comprimirse (regla Luis 2026-07-29) */
.ficha-detail{flex:1;display:grid;grid-template-columns:minmax(320px,440px) 1fr;gap:40px;align-items:center;padding:0 30px;min-height:0}
.ficha-cart{display:flex;align-items:center;justify-content:center;height:100%;max-height:440px}
.ficha-cart img{max-height:440px;max-width:100%;width:auto;height:auto;object-fit:contain;border:3px solid rgba(255,255,255,.85);border-radius:8px;box-shadow:0 18px 50px rgba(0,0,0,.7)}
.ficha-fallback{width:100%;max-width:340px;aspect-ratio:3/4;background:linear-gradient(160deg,var(--mg),#7a0044);border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px;box-shadow:0 18px 50px rgba(0,0,0,.7);border:3px solid rgba(255,255,255,.3)}
.ficha-fallback .ff-title{font-family:'Orbitron';font-weight:900;font-size:30px;color:#fff;line-height:1.15;margin-bottom:14px}
.ficha-fallback .ff-sub{font-family:'Press Start 2P';font-size:12px;color:rgba(255,255,255,.85);letter-spacing:2px}
.ficha-info{display:flex;flex-direction:column;gap:18px}
.ficha-title{font-family:'Orbitron';font-weight:900;font-size:57px;color:#fff;line-height:1.05}
.ficha-stats{display:grid;grid-template-columns:1fr 1fr;gap:14px 24px;background:rgba(255,255,255,.04);border-left:4px solid var(--cy);padding:20px 24px}
.ficha-stat .lbl{display:block;font-family:'Press Start 2P';font-size:10px;color:var(--cy);letter-spacing:2px;margin-bottom:7px}
.ficha-stat .val{font-family:'Share Tech Mono';font-size:25px;color:#fff}
.ficha-owned{align-self:flex-start;font-family:'Orbitron';font-weight:900;font-size:32px;color:var(--dk);background:var(--ye);padding:9px 24px;border-radius:5px;letter-spacing:1px;box-shadow:0 0 22px rgba(255,210,63,.6)}
.ficha-owned.faltan{color:var(--bo);background:transparent;border:2px solid rgba(255,255,255,.3);box-shadow:none;font-size:25px}

/* CONTEXTO DE EPOCA */
.contexto{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;gap:28px;padding:0 60px}
.contexto .ctx-tag{font-family:'Press Start 2P';font-size:15px;color:var(--mg);letter-spacing:5px}
.contexto .ctx-year{font-family:'Orbitron';font-weight:900;font-size:67px;color:#fff}
.contexto .ctx-year b{color:var(--ye)}
.contexto .ctx-body{font-family:'Share Tech Mono';font-size:30px;line-height:1.6;color:rgba(255,255,255,.92);max-width:1300px;background:rgba(255,255,255,.04);border-left:4px solid var(--mg);padding:26px 34px;text-align:left}

/* TARROVISION */
.gp-head{text-align:center;flex:none;padding-top:6px;margin-bottom:8px}
.gp-title{font-family:'Orbitron';font-weight:900;font-size:46px;color:#fff;line-height:1}
.gp-meta{font-family:'Share Tech Mono';font-size:17px;color:var(--ye);letter-spacing:3px;margin-top:4px}
.gp-body{flex:1;display:grid;grid-template-columns:1fr 480px;gap:40px;align-items:center;min-height:0;padding:0 16px 8px}
.gp-tv{height:100%;display:flex;align-items:center;justify-content:center;min-height:0}
.gp-tv .tarrovision{height:min(100%,780px);aspect-ratio:4/3;max-width:100%}
.gp-side{display:flex;flex-direction:column;gap:18px}
.gp-dato{background:rgba(255,255,255,.04);border-left:4px solid var(--cy);padding:20px 24px;font-family:'Share Tech Mono';font-size:28px;line-height:1.5;color:rgba(255,255,255,.92)}
.gp-dato .lbl{display:block;font-family:'Press Start 2P';font-size:14px;color:var(--cy);letter-spacing:2px;margin-bottom:12px}
.tarrovision{position:relative;background:linear-gradient(180deg,#1a1a1f,#0d0d12);border-radius:22px;padding:20px 24px;box-shadow:0 0 0 2px rgba(255,255,255,.04),0 22px 60px rgba(0,0,0,.7),inset 0 1px 0 rgba(255,255,255,.08),inset 0 -2px 0 rgba(0,0,0,.4);display:grid;grid-template-rows:auto 1fr auto;gap:12px}

/* TARROVISION VS (comparativa dual, regla Luis 2026-07-26 -- SIN dato, solo
   las dos pantallas + VS, todo el alto disponible) */
.dual-grid{flex:1;display:flex;justify-content:center;align-items:center;gap:28px;min-height:0;padding:0 20px 20px}
.dual-cell{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;min-height:0;height:100%;flex:0 1 900px;max-width:900px;min-width:0}
.dual-cell .tarrovision{height:min(100%,675px);aspect-ratio:4/3;max-width:100%}
.dual-vs{font-family:'Orbitron';font-weight:900;font-size:56px;color:var(--ye);text-shadow:0 0 18px rgba(255,210,63,.55);flex:0 0 auto}
/* namebox VACIA a proposito: solo el marco, el nombre se escribe encima en la edicion */
.tv-namebox{display:inline-flex;align-items:center;justify-content:center;padding:8px 24px;border:1px solid var(--ye);background:rgba(255,210,63,.04);position:relative;border-radius:2px;max-width:90%;min-width:220px;min-height:46px}
.tv-namebox::before,.tv-namebox::after{content:"";position:absolute;width:7px;height:7px;background:var(--dk);border:1px solid var(--ye)}
.tv-namebox::before{top:-4px;left:-4px}
.tv-namebox::after{bottom:-4px;right:-4px}
.tv-controls-top{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:0 6px}
.tv-led{width:10px;height:10px;border-radius:50%;background:radial-gradient(circle at 30% 30%,#ff8fb8,var(--mg) 60%,#7a0030);box-shadow:0 0 10px rgba(255,46,136,.8)}
.tv-brand{flex:1;text-align:center;font-family:'Press Start 2P';font-size:14px;color:var(--ye);letter-spacing:4px}
.tv-channel{font-family:'Share Tech Mono';font-size:14px;color:var(--cy);padding:4px 10px;border:1px solid rgba(0,229,255,.4);background:rgba(0,229,255,.06)}
.tv-screen{position:relative;background:#2a2a2f;border-radius:14px;padding:16px;box-shadow:inset 0 0 0 2px #3a3a3f,inset 0 0 14px rgba(0,0,0,.6);min-height:0}
.tv-screen-inner{position:relative;width:100%;height:100%;background:#000;border-radius:18px/8px;overflow:hidden;box-shadow:inset 0 0 0 1px rgba(255,255,255,.05),inset 0 0 40px rgba(0,0,0,.95)}
.tv-screen-inner::before{content:"";position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(0,0,0,0) 0 2px,rgba(0,0,0,.18) 2px 3px);z-index:3;mix-blend-mode:multiply}
.tv-noscreen{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(circle at 50% 50%,rgba(45,27,105,.6),#000 80%);color:rgba(255,255,255,.35);text-align:center;padding:30px;z-index:2}
.tv-noscreen-big{font-family:'Press Start 2P';font-size:21px;color:var(--mg);letter-spacing:4px;margin-bottom:12px;text-shadow:0 0 12px rgba(255,46,136,.5)}
.tv-noscreen-sub{font-family:'Share Tech Mono';font-size:14px;color:rgba(0,229,255,.55)}
.tv-controls-bottom{display:grid;grid-template-columns:auto auto 1fr;align-items:center;gap:14px;padding:4px 6px 0}
.tv-knob{width:32px;height:32px;border-radius:50%;background:radial-gradient(circle at 30% 30%,#5a5a60,#2a2a30 60%,#0a0a0e);box-shadow:inset 0 1px 0 rgba(255,255,255,.15),inset 0 -2px 0 rgba(0,0,0,.4),0 2px 4px rgba(0,0,0,.6);position:relative}
.tv-knob::after{content:"";position:absolute;top:6px;left:50%;width:2px;height:10px;background:var(--ye);transform:translateX(-50%) rotate(45deg)}
.tv-knob.cy::after{background:var(--cy);transform:translateX(-50%) rotate(-30deg)}
.tv-speaker{height:26px;background:repeating-linear-gradient(90deg,#0a0a0e 0 3px,#1a1a1f 3px 6px);border-radius:4px}

/* VEREDICTO */
.veredicto{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:30px}
.veredicto .ver-pre{font-family:'Press Start 2P';font-size:15px;color:var(--cy);letter-spacing:5px}
.veredicto .ver-tag{font-family:'Orbitron';font-weight:900;font-size:76px;color:var(--dk);background:var(--ye);padding:22px 52px;border-radius:8px;letter-spacing:2px;box-shadow:0 0 40px rgba(255,210,63,.6)}
.veredicto .ver-resumen{font-family:'Share Tech Mono';font-size:28px;line-height:1.6;color:rgba(255,255,255,.92);max-width:1100px}

/* DIVIDER (cierre) */
.divider{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.divider .pre{font-family:'Press Start 2P';font-size:14px;letter-spacing:6px;margin-bottom:22px}
.divider .pre.cy{color:var(--cy)}.divider .pre.mg{color:var(--mg)}
.divider .title{font-family:'Orbitron';font-weight:900;font-size:76px;line-height:1;color:#fff;margin-bottom:20px}
.divider .title.cy{color:var(--cy);text-shadow:0 0 22px rgba(0,229,255,.5)}.divider .title.mg{color:var(--mg);text-shadow:0 0 22px rgba(255,46,136,.55)}
.divider .sub{font-family:'Share Tech Mono';font-size:25px;color:rgba(255,255,255,.75);letter-spacing:2px;max-width:900px;line-height:1.6}

/* CAPA DE NOTAS (teleprompter · tecla N) - copiado 1:1 del patron SEGA */
.notas{position:absolute;top:0;right:0;width:460px;height:100%;z-index:150;display:none;flex-direction:column;gap:10px;padding:26px 22px 30px;overflow-y:auto;background:linear-gradient(90deg,rgba(6,3,15,.55) 0%,rgba(6,3,15,.96) 26%);border-left:2px solid var(--ye);backdrop-filter:blur(2px)}
body.read-mode .slide.active .notas{display:flex}
.notas h4{font-family:'Press Start 2P';font-size:10px;color:var(--ye);letter-spacing:2px;margin-top:4px}
.notas h4:first-child{margin-top:0}
.notas .n-line{font-family:'Share Tech Mono';font-size:16.7px;line-height:1.5;color:rgba(255,255,255,.92);border-left:3px solid var(--cy);padding:3px 0 3px 11px}
.notas .n-cue{border-left-color:var(--mg);color:var(--ye)}
.notas .n-cue b{color:#fff}
.read-indicator{position:fixed;top:64px;right:16px;z-index:300;font-family:'Press Start 2P';font-size:9px;color:#000;background:var(--ye);padding:6px 10px;border-radius:3px;display:none;box-shadow:0 0 14px rgba(255,210,63,.5)}
body.read-mode .read-indicator{display:block}
.notas-hotzone{position:fixed;bottom:0;right:0;width:230px;height:150px;z-index:299}
.notas-toggle{position:fixed;bottom:74px;right:16px;z-index:300;font-family:'Press Start 2P';font-size:10px;letter-spacing:1px;color:var(--ye);background:rgba(6,3,15,.92);border:2px solid var(--ye);padding:10px 14px;border-radius:4px;cursor:pointer;box-shadow:0 0 14px rgba(255,210,63,.3);transition:opacity .2s,background .15s,color .15s;opacity:0}
.notas-hotzone:hover ~ .notas-toggle,.notas-toggle:hover{opacity:1}
.notas-toggle:hover{background:var(--ye);color:#000}
body.read-mode .notas-toggle{opacity:1;background:var(--ye);color:#000;box-shadow:0 0 18px rgba(255,210,63,.6)}

nav.footer{position:fixed;bottom:0;left:0;right:0;height:64px;background:rgba(6,3,15,.97);border-top:2px solid var(--cy);display:flex;align-items:center;justify-content:space-between;padding:0 28px;z-index:200}
.nav-btn{background:transparent;border:2px solid var(--cy);color:var(--cy);font-family:'Press Start 2P';font-size:10px;padding:10px 18px;letter-spacing:2px;cursor:pointer;border-radius:2px}
.nav-btn:disabled{opacity:.25}
.nav-center{display:flex;flex-direction:column;align-items:center;gap:6px;flex:1;margin:0 24px}
.nav-counter{font-family:'Press Start 2P';font-size:12px;color:var(--mg);letter-spacing:3px}
.nav-progress{width:100%;max-width:480px;height:4px;background:rgba(255,255,255,.08);border-radius:2px;overflow:hidden}
.nav-progress .bar{height:100%;background:linear-gradient(90deg,var(--mg),var(--cy));width:0;transition:width .25s}
.nav-hint{font-family:'Share Tech Mono';font-size:13px;color:rgba(255,255,255,.4);letter-spacing:2px}
"""

# CSS de los campos opcionales: solo se agrega al HTML cuando el DATA los usa,
# asi una reseña que no los usa sale byte a byte igual que antes.
CSS_POR_CONFIRMAR = """
.notas .n-pc{border:2px solid var(--ye);background:rgba(255,210,63,.1);border-radius:4px;padding:10px 12px;display:flex;flex-direction:column;gap:8px}
.notas .n-pc .n-line{border-left-color:var(--ye)}
"""
CSS_FAMILIA = """
.ficha-familia{align-self:flex-start;font-family:'Share Tech Mono';font-size:21px;color:var(--cy);letter-spacing:1px;margin-top:-4px}
"""

# CSS de la grafica nueva (data["grafica"] == "nueva"): solo se agrega en ese caso.
CSS_NUEVA = """
.portada-fondo{position:absolute;inset:-40px;background-size:cover;background-position:center;filter:blur(18px) brightness(.38) saturate(1.2);z-index:0}
.portada-caja{position:absolute;right:120px;top:50%;transform:translateY(-50%) rotate(3deg);height:70%;border-radius:6px;box-shadow:0 0 60px rgba(255,46,136,.55),0 18px 50px rgba(0,0,0,.8);z-index:1}
.portada.con-caja{position:relative;z-index:2;align-items:flex-start;text-align:left;padding-left:90px;max-width:58%}
.ver-escala{display:flex;gap:14px;margin-top:6px}
.ver-pill{font-family:'Orbitron';font-weight:700;font-size:20px;letter-spacing:1px;padding:10px 20px;border-radius:6px;border:2px solid rgba(255,255,255,.25);color:rgba(255,255,255,.4)}
.ver-pill.on{border-color:var(--ye);color:var(--ye);box-shadow:0 0 20px rgba(255,210,63,.5)}
.chips{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.chip{display:inline-flex;flex-direction:column;align-items:center;padding:6px 14px;border:2px solid rgba(0,229,255,.55);border-radius:6px;color:var(--cy);font-family:'Orbitron';font-size:20px;line-height:1.1}
.chip b{font-weight:700}
.chip i{font-style:normal;font-family:'Share Tech Mono';font-size:14px;color:rgba(255,255,255,.65)}
.chip.first{background:var(--ye);color:var(--dk);border-color:var(--ye);box-shadow:0 0 18px rgba(255,210,63,.55)}
.chip.first i{color:var(--dk)}
.chips .arr{color:var(--mg);font-size:20px}
.contexto.con-imagen{flex-direction:row;gap:80px;padding:0 90px;align-items:center;justify-content:center}
.ctx-img{width:auto;height:62vh;flex:none;border-radius:6px;box-shadow:0 0 40px rgba(0,229,255,.4);border:2px solid rgba(255,255,255,.25)}
.ctx-texto{flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:26px;align-items:flex-start;text-align:left;max-width:1000px}
.vineta{display:flex;gap:22px;align-items:center;margin-bottom:26px}
.vn{font-family:'Press Start 2P';font-size:20px;color:var(--dk);background:var(--ye);padding:16px 14px;border-radius:6px;min-width:72px;text-align:center}
.vtit{font-family:'Orbitron';font-weight:900;font-size:26px;color:#fff;letter-spacing:1px}
.vtxt{font-family:'Share Tech Mono';font-size:21px;color:rgba(255,255,255,.78);margin-top:4px}
.gp-compositor{margin-top:26px;border:2px solid var(--cy);border-radius:8px;padding:16px 22px;display:flex;flex-direction:column;gap:6px}
.gc-lbl{font-family:'Press Start 2P';font-size:12px;letter-spacing:3px;color:var(--cy)}
.gc-txt{font-family:'Orbitron';font-weight:700;font-size:28px;color:#fff}
.cierre-proxima{margin-top:38px;display:flex;align-items:center;gap:30px;border:2px solid var(--mg);border-radius:10px;padding:18px 34px;background:rgba(255,46,136,.08);text-align:left}
.cp-img{height:170px;border-radius:5px;box-shadow:0 0 24px rgba(255,46,136,.5)}
.cp-lbl{font-family:'Press Start 2P';font-size:14px;letter-spacing:4px;color:var(--ye)}
.cp-juego{font-family:'Orbitron';font-weight:900;font-size:50px;color:#fff;margin-top:10px;text-transform:uppercase}
.cp-meta{font-family:'Share Tech Mono';font-size:22px;color:rgba(255,255,255,.75);margin-top:8px}
"""

SCRIPT = """
const slides=document.querySelectorAll('.slide');const prevBtn=document.getElementById('prevBtn');
const nextBtn=document.getElementById('nextBtn');const counter=document.getElementById('counter');const bar=document.getElementById('bar');
let current=0;const total=slides.length;function pad(n){return String(n).padStart(2,'0')}
function go(i){if(i<0||i>=total)return;slides[current].classList.remove('active');current=i;slides[current].classList.add('active');
prevBtn.disabled=current===0;nextBtn.disabled=current===total-1;counter.textContent=pad(current+1)+' / '+pad(total);bar.style.width=((current+1)/total*100)+'%'}
prevBtn.addEventListener('click',()=>go(current-1));nextBtn.addEventListener('click',()=>go(current+1));
// Click en el deck: mitad derecha avanza, mitad izquierda retrocede (util grabando:
// no hay que apuntar al boton chico). No cambia de slide si el click fue dentro
// del panel de notas (para poder hacer scroll/leer sin querer cambiar de slide).
document.getElementById('deck').addEventListener('click',(e)=>{
  if(e.target.closest('.notas'))return;
  if(e.clientX<window.innerWidth/2)go(current-1);else go(current+1);
});
document.addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key===' '){e.preventDefault();go(current+1)}
  if(e.key==='ArrowLeft'){e.preventDefault();go(current-1)}
  if(e.key==='Home'){go(0)}
  if(e.key==='End'){go(total-1)}
  if(e.key==='n'||e.key==='N'){toggleRead()}
});
function toggleRead(){document.body.classList.toggle('read-mode')}
document.getElementById('notasToggle').addEventListener('click',toggleRead);
go(0);
"""


def generar_resena(data: dict, out_slug: str, lint: bool = True) -> Path:
    """Genera studio/resenas/<out_slug>.html. Corre scripts/resena_lint.py antes de
    escribir: los errores lanzan ValueError (no se escribe nada), los avisos se
    imprimen. `lint=False` o la variable de entorno RESENA_LINT=off lo saltan
    (solo para excepciones historicas)."""
    if lint and os.environ.get("RESENA_LINT", "").lower() != "off":
        errores, avisos = revisar(data, out_slug)
        if errores or avisos:
            print(formatear(errores, avisos))
        if errores:
            raise ValueError(formatear(errores, avisos))
    slides = []
    num = 1
    if data.get("pedido"):
        slides.append(_slide_pedido(num, data))
        num += 1
        slides.append(_slide_portada(num, data, active=False))
    else:
        slides.append(_slide_portada(num, data))
    num += 1
    slides.append(_slide_ficha(num, data))
    num += 1
    slides.append(_slide_contexto(num, data))
    num += 1
    ch = 1
    # Slide COMPARATIVA: obligatorio en toda resena (regla Luis 2026-07-26).
    # El titulo es SIEMPRE "COMPARATIVA", agnostico sin importar que se compare
    # (arcade vs puerto, original vs secuela, etc). SIN dato/texto en el slide --
    # solo las dos TarroVision + VS, el contexto se dice hablado (ajuste
    # Luis 2026-07-26: "es mejor ocuparlo en mostrar gameplay").
    slides.append(_slide_tarrovision_dual(
        num, ch, ch + 1,
        data.get("notas", {}).get("comparativa"), data,
    ))
    num += 1
    ch += 2
    slides.append(_slide_tarrovision(
        num, "JUGABILIDAD HOY", ch, data["jugabilidad_dato"], data.get("notas", {}).get("jugabilidad"), data,
        reemplazo=_vinetas(data) if _nueva(data) else ""))
    num += 1
    ch += 1
    slides.append(_slide_tarrovision(
        num, "GRAFICOS Y SONIDO HOY", ch, data["audiovisual_dato"], data.get("notas", {}).get("audiovisual"), data,
        extra=_compositor(data) if _nueva(data) else ""))
    num += 1
    slides.append(_slide_veredicto(num, data))
    num += 1
    slides.append(_slide_cierre(num, data))
    css = CSS
    if _nueva(data):
        css += CSS_NUEVA
    if data.get("por_confirmar"):
        css += CSS_POR_CONFIRMAR
    if data.get("en_coleccion") == "familia" and data.get("familia_texto"):
        css += CSS_FAMILIA
    html = (
        '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<title>RETROTARROS · RESEÑA · {_esc(data["juego"]).upper()}</title><style>{css}</style></head><body>'
        '<div class="read-indicator no-capture">● MODO LECTURA (N)</div>'
        '<div class="notas-hotzone no-capture"></div>'
        '<button class="notas-toggle no-capture" id="notasToggle">📖 NOTAS (N)</button>'
        '<header><div class="hdr-logo">RETROTARROS</div>'
        f'<div class="hdr-tag">RESEÑA · {_esc(data["juego"]).upper()}</div>'
        '<div class="hdr-rec"><div class="dot"></div>EN VIVO</div></header>'
        '<div class="deck" id="deck">\n' + "\n".join(slides) + '\n</div>'
        '<nav class="footer"><button class="nav-btn" id="prevBtn">◀ ANTERIOR</button>'
        '<div class="nav-center"><div class="nav-counter" id="counter">01 / 07</div>'
        '<div class="nav-progress"><div class="bar" id="bar"></div></div></div>'
        '<div class="nav-hint">← → NAVEGAR</div>'
        '<button class="nav-btn" id="nextBtn">SIGUIENTE ▶</button></nav>'
        f'<script>{SCRIPT}</script></body></html>'
    )
    out_dir = REPO / "studio" / "resenas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{out_slug}.html"
    out.write_text(html, encoding="utf-8")
    if data.get("por_confirmar"):
        print("POR CONFIRMAR ANTES DE GRABAR:")
        for t in data["por_confirmar"]:
            print(f"  - {t}")
    return out
