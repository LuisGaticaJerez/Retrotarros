"""
tarrovision.py - Retrotarros Studio Suite
=========================================
TarroVision nueva y TarroVision ancha (la pantalla vacia donde se monta el gameplay).
Se activa SOLO con data["tarrovision"] en el driver de cada generador; sin la marca (o con
"clasica") el HTML sale identico, byte a byte, al de siempre: asi no se tocan los episodios
ya grabados o publicados.

Valores de data["tarrovision"]:
  "clasica"  (por defecto) la TV de siempre.
  "nueva"    mismo tamano que la clasica, con el visual nuevo (borde de neon, pantalla con
             marcas de encuadre, barras de color en el NO SIGNAL).
  "ancha"    visual nuevo con la pantalla en 16:9 exacto (la clasica mide ~1.5:1 y recorta o
             deja bandas al gameplay 16:9), mas grande en el slide de gameplay y en la comparativa.

Generadores que la usan: resena_deck.py y saga_deck.py (slides de gameplay y COMPARATIVA).
Los demas (top_deck, special_deck, retronota_deck, coleccion_deck) siguen con la clasica.

Sin tildes en el HTML (regla de assets visuales del canal).
"""
from __future__ import annotations

VARIANTES = ("clasica", "nueva", "ancha")

# Medidas del marco (px) que deben coincidir con el CSS: borde 2 + relleno 16/14 del cuerpo y
# relleno 10 del bisel. Con ellas la pantalla ancha mide exactamente 16:9 y el TV entra en el alto.
CH_X = 2 * (2 + 16) + 2 * 10                       # 56: ancho que el marco suma a la pantalla
CH_Y = 2 * (2 + 14) + 26 + 24 + 2 * 8 + 2 * 10     # 118: alto que el marco suma (barras, huecos, bisel)
ALTO_MAX_GAMEPLAY = 780                            # el mismo tope de alto de la TV clasica en el slide de gameplay


def variante(data: dict) -> str:
    """Lee data["tarrovision"]; ValueError si el valor no es uno de VARIANTES."""
    v = data.get("tarrovision", "clasica")
    if v not in VARIANTES:
        raise ValueError(f'tarrovision debe ser uno de {VARIANTES}, no {v!r}')
    return v


def activa(v: str) -> bool:
    """True si hay que usar el visual nuevo (nueva o ancha)."""
    return v in ("nueva", "ancha")


def tv(ch: int, v: str) -> str:
    """HTML de la TarroVision nueva (v = "nueva" o "ancha"). Mantiene las clases de la clasica
    (tarrovision, tv-controls-top, tv-screen-inner, tv-noscreen...) y agrega tvn / ancha."""
    if not activa(v):
        raise ValueError(f'tv() solo genera "nueva" o "ancha", no {v!r}')
    pista = "Inserta gameplay aqui &middot; 16:9" if v == "ancha" else "Inserta gameplay aqui"
    clases = "tarrovision tvn ancha" if v == "ancha" else "tarrovision tvn"
    return (
        f'<div class="{clases}">'
        f'<div class="tv-controls-top"><span class="tv-led"></span><span class="tv-brand">TARROVISION</span><span class="tv-channel">CH {ch:02d}</span></div>'
        '<div class="tv-screen"><div class="tv-screen-inner"><div class="tv-noscreen">'
        '<div class="tv-bars"></div>'
        '<div class="tv-noscreen-big">NO SIGNAL</div>'
        f'<div class="tv-noscreen-sub">{pista}</div></div>'
        '<i class="tv-c tl"></i><i class="tv-c tr"></i><i class="tv-c bl"></i><i class="tv-c br"></i>'
        '</div></div>'
        '<div class="tv-controls-bottom"><div class="tv-knob"></div><div class="tv-knob cy"></div>'
        '<div class="tv-speaker"></div><div class="tv-power"></div></div>'
        '</div>'
    )


def clase_contenedor(v: str) -> str:
    """Clase extra del contenedor (gp-tv o dual-cell): `tvw` solo con la TV ancha."""
    return " tvw" if v == "ancha" else ""


def css(v: str) -> str:
    """CSS del visual nuevo; vacio con la clasica. Va al final del bloque de estilo del generador
    (despues del CSS clasico: gana por especificidad y por orden)."""
    if not activa(v):
        return ""
    base = (
        # carcasa: borde de neon magenta a cyan, brillo suave y bisel mas delgado
        ".tarrovision.tvn{border:2px solid transparent;border-radius:16px;padding:14px 16px;gap:8px;"
        "background:linear-gradient(180deg,#1d1d25,#0a0a10) padding-box,linear-gradient(135deg,var(--mg),var(--cy)) border-box;"
        "box-shadow:0 0 28px rgba(255,46,136,.22),0 0 44px rgba(0,229,255,.16),0 22px 60px rgba(0,0,0,.7),"
        "inset 0 1px 0 rgba(255,255,255,.08)}\n"
        ".tvn .tv-controls-top{height:26px}\n"
        ".tvn .tv-brand{font-size:13px;text-shadow:0 0 10px rgba(255,210,63,.45)}\n"
        ".tvn .tv-channel{font-size:13px;padding:2px 10px}\n"
        ".tvn .tv-screen{padding:10px;border-radius:10px;background:#14141a;"
        "box-shadow:inset 0 0 0 2px #2c2c36,inset 0 0 14px rgba(0,0,0,.7)}\n"
        ".tvn .tv-screen-inner{border-radius:6px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.06),inset 0 0 50px rgba(0,0,0,.9)}\n"
        # reflejo diagonal del vidrio
        ".tvn .tv-screen-inner::after{content:\"\";position:absolute;inset:0;pointer-events:none;z-index:3;"
        "background:linear-gradient(115deg,rgba(255,255,255,.045) 0,rgba(255,255,255,.045) 12%,transparent 12.2%)}\n"
        # pantalla sin senal: barras de color abajo y marcas de encuadre en las cuatro esquinas
        ".tvn .tv-bars{position:absolute;left:0;right:0;bottom:0;height:9%;opacity:.5;"
        "background:linear-gradient(90deg,#c8c8c8 0 14.28%,#c8c800 0 28.57%,#00c8c8 0 42.85%,#00c800 0 57.14%,"
        "#c800c8 0 71.43%,#c80000 0 85.71%,#0000c8 0 100%)}\n"
        ".tvn .tv-noscreen-big{font-size:24px}\n"
        ".tvn .tv-noscreen-sub{font-size:15px;letter-spacing:1px}\n"
        ".tvn .tv-c{position:absolute;width:26px;height:26px;border:0 solid var(--cy);opacity:.75;z-index:4}\n"
        ".tvn .tv-c.tl{top:14px;left:14px;border-top-width:3px;border-left-width:3px}\n"
        ".tvn .tv-c.tr{top:14px;right:14px;border-top-width:3px;border-right-width:3px}\n"
        ".tvn .tv-c.bl{bottom:14px;left:14px;border-bottom-width:3px;border-left-width:3px}\n"
        ".tvn .tv-c.br{bottom:14px;right:14px;border-bottom-width:3px;border-right-width:3px}\n"
        # controles de abajo: mas delgados, con boton de encendido
        ".tvn .tv-controls-bottom{height:24px;grid-template-columns:auto auto 1fr auto;padding:0 6px;gap:12px}\n"
        ".tvn .tv-knob{width:22px;height:22px}\n"
        ".tvn .tv-knob::after{top:4px;height:7px}\n"
        ".tvn .tv-speaker{height:16px}\n"
        ".tvn .tv-power{width:14px;height:14px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#8cffb0,#19b45a 60%,#07391c);"
        "box-shadow:0 0 8px rgba(25,180,90,.7)}\n"
    )
    if v != "ancha":
        return base
    ancha = (
        # pantalla 16:9 exacta; el TV se ajusta al ancho o al alto disponible
        ".tarrovision.tvn.ancha{grid-template-rows:auto auto auto}\n"
        ".tarrovision.tvn.ancha .tv-screen-inner{height:auto;aspect-ratio:16/9}\n"
        # slide de gameplay: contenedor con unidades de contenedor, la pantalla crece hasta llenar el alto
        f".gp-tv.tvw{{container-type:size;width:100%}}\n"
        f".gp-tv .tarrovision.tvn.ancha{{height:auto;aspect-ratio:auto;max-width:none;"
        f"width:calc(min(100cqw - {CH_X}px,(min(100cqh,{ALTO_MAX_GAMEPLAY}px) - {CH_Y}px)*16/9) + {CH_X}px)}}\n"
        # comparativa: dos TV que se reparten todo el ancho; el VS pasa a ser una insignia sobre la union
        ".dual-grid.tvw{position:relative;gap:14px;padding:0 4px 20px}\n"
        ".dual-grid.tvw .dual-cell{flex:1 1 0;max-width:none}\n"
        ".dual-cell.tvw .tarrovision.tvn.ancha{height:auto;aspect-ratio:auto;width:100%;max-width:none}\n"
        ".dual-grid.tvw .dual-vs{position:absolute;left:50%;top:calc(50% - 38px);transform:translate(-50%,-50%);z-index:5;"
        "width:96px;height:96px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:42px;"
        "background:var(--dk);border:3px solid var(--ye);box-shadow:0 0 26px rgba(255,210,63,.55)}\n"
    )
    return base + ancha
