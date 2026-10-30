"""
resena_kit.py - Retrotarros Studio Suite
Esqueleto del kit de publicacion YouTube de una reseña
(docs/descripciones/descripcion-<out_slug>.md).

El codigo solo arma lo mecanico (hashtags, tags, estructura, CTA, pie). Todo lo
que es voz humana (titulo con dato curioso, gancho, contexto, pregunta,
comentario fijado) queda como marcador [REDACTAR: ...] para escribirlo a mano:
nada de prosa automatica. Diseño: docs/superpowers/specs/2026-10-28-resena-kit-design.md

    python scripts/resena_kit.py .cache/gen_resena_<juego>.py
        crea el esqueleto (nunca pisa un kit existente: sale con codigo 2)
"""
from __future__ import annotations
import re
import sys
from datetime import date
from pathlib import Path

from resena_lint import capturar_driver

REPO = Path(__file__).resolve().parent.parent
CARPETA_KITS = REPO / "docs" / "descripciones"

CTA = "🔔 Suscríbete a RETROTARROS para más reseñas retro: nostalgia + juegos + música."
COLA_TAGS = [
    "retroreseñas", "reseña retro", "retrogaming", "juegos retro",
    "nostalgia gamer", "¿envejeció bien?", "retrotarros",
]
LISTA_RESENAS = "PLOBtQJdDMEDA"   # id de la lista Retroreseñas del canal (para el bloque "Sigue con")
MARCADOR_TAGS ="[REDACTAR: sumar tags propios del juego: personas, secuela, términos]"


def _camel(texto: str) -> str:
    texto = texto.replace("'", "").replace("’", "")
    palabras = re.findall(r"[0-9A-Za-zÀ-ÿ]+", texto)
    return "".join(p[0].upper() + p[1:] for p in palabras)


def hashtag_juego(data: dict) -> str:
    propio = (data.get("hashtag_juego") or "").strip().lstrip("#")
    if propio:
        return "#" + propio
    nombre = str(data.get("juego") or "").split(":")[0]
    camel = _camel(nombre)
    return "#" + camel if camel else ""


# Nombres de consola como los usa el canal en sus hashtags (prefijo en minusculas -> hashtag).
_ALIAS_CONSOLAS = (
    ("neo geo", "NeoGeo"), ("playstation 2", "PS2"), ("playstation 3", "PS3"),
    ("sega genesis", "MegaDrive"), ("sega mega drive", "MegaDrive"), ("mega drive", "MegaDrive"),
    ("super nintendo", "SNES"), ("nintendo entertainment system", "NES"), ("ms-dos", "PC"),
)


def _sin_parentesis(texto: str) -> str:
    return re.sub(r"\s*\([^)]*\)", "", texto).strip()


def _plataformas(consola: str) -> list[str]:
    """Plataformas de la ficha, separadas por · o /, sin parentesis. 'Arcade (Neo Geo MVS)'
    se queda con lo de adentro: 'Neo Geo MVS'."""
    salida: list[str] = []
    for p in re.split(r"[·/]", consola):
        m = re.match(r"\s*arcade\s*\((.+)\)\s*$", p, re.IGNORECASE)
        p = m.group(1).strip() if m else _sin_parentesis(p.strip())
        if p:
            salida.append(p)
    return salida


def _anio(data: dict) -> str:
    """Primer año de 4 digitos ('1987 (arcade) / 1988 (NES)' -> '1987')."""
    bruto = str(data.get("anio") or "").strip()
    m = re.search(r"\d{4}", bruto)
    return m.group(0) if m else bruto


def hashtag_consola(data: dict) -> str:
    plataformas = _plataformas(str(data.get("consola") or ""))
    if not plataformas:
        return ""
    primera = plataformas[0]
    for prefijo, hashtag in _ALIAS_CONSOLAS:
        if primera.lower().startswith(prefijo):
            return "#" + hashtag
    camel = _camel(primera)
    return "#" + camel if camel else ""


def hashtags(data: dict) -> str:
    partes = ["#RetroReseñas", hashtag_juego(data), hashtag_consola(data),
              "#Retrogaming", "#Retrotarros"]
    return " ".join(p for p in partes if p)


def tags(data: dict) -> str:
    juego = str(data.get("juego") or "").strip().lower()
    anio = _anio(data)
    candidatos: list[str] = []
    if juego:
        candidatos += [juego, f"{juego} reseña"]
        if anio:
            candidatos.append(f"{juego} {anio}")
    for dev in re.split(r"[·/]", _sin_parentesis(str(data.get("developer") or ""))):
        candidatos.append(dev.replace(",", "").strip().lower())
    candidatos += [p.lower() for p in _plataformas(str(data.get("consola") or ""))]
    candidatos += [g.strip().lower() for g in
                   re.split(r"[/·]", _sin_parentesis(str(data.get("genero") or "")))]
    candidatos += COLA_TAGS
    vistos: list[str] = []
    for t in candidatos:
        if t and t not in vistos:
            vistos.append(t)
    return ", ".join(vistos) + ", " + MARCADOR_TAGS


def esqueleto(data: dict, out_slug: str, hoy: str) -> str:
    juego = str(data.get("juego") or "")
    anio = _anio(data)
    consola = str(data.get("consola") or "")
    agradecer = "\n[REDACTAR: agradecer a quien lo pidió]" if data.get("pedido") else ""
    return (
        f"# Descripción YouTube — Reseña: {juego} ({consola})\n\n"
        "Doc para copiar/pegar al subir la reseña. Español chileno neutro, con tildes.\n\n"
        "---\n\n"
        "## Títulos sugeridos (elegir uno)\n\n"
        "1. **[REDACTAR: título con dato curioso]** — gancho de dato curioso. (Recomendado)\n"
        f"2. **{juego} ({anio}): [REDACTAR: ¿sigue siendo ...?]** — gancho retrospectivo.\n\n"
        "---\n\n"
        "## Descripción (copiar/pegar)\n\n"
        "```\n"
        f"Volvemos a {anio} para revisar {juego}, [REDACTAR: qué es en una frase] 🎮\n\n"
        f"[REDACTAR: historia, cómo se juega hoy y comparativa]{agradecer}\n\n"
        "[REDACTAR: pregunta a la comunidad] Cuéntanos en los comentarios 👇\n\n"
        f"{CTA}\n\n"
        "Sigue con: [REDACTAR: video sugerido al publicar]\n"
        f"Todas las reseñas: https://www.youtube.com/playlist?list={LISTA_RESENAS}\n\n"
        "[REDACTAR: confirmar con tildes el nombre del juego, el año y los hashtags (#Juego #Consola)]\n"
        f"{hashtags(data)}\n"
        "```\n\n"
        "---\n\n"
        "## Tags YouTube (keywords)\n\n"
        "```\n"
        f"{tags(data)}\n"
        "```\n\n"
        "---\n\n"
        "## Comentario fijado (copiar/pegar)\n\n"
        "```\n"
        "Dato random: [REDACTAR: dato curioso]. [REDACTAR: pregunta a la comunidad]\n"
        "```\n\n"
        "---\n\n"
        f"**Slug:** `{out_slug}`\n"
        "**Formato:** Reseña (horizontal, hasta 10 min)\n"
        f"**Última actualización:** {hoy}\n"
    )


def crear(ruta_driver: str, carpeta: Path | None = None, hoy: str | None = None) -> int:
    """Escribe un kit por cada reseña que el driver genera. 0 si creo todos; 2 si
    alguno ya existia (no se toca) o el driver no genero ninguna reseña."""
    carpeta = carpeta or CARPETA_KITS
    hoy = hoy or date.today().isoformat()
    capturado = capturar_driver(ruta_driver)
    if not capturado:
        print("el driver no llamo a generar_resena")
        return 2
    carpeta.mkdir(parents=True, exist_ok=True)
    codigo = 0
    for data, out_slug in capturado:
        destino = carpeta / f"descripcion-{out_slug}.md"
        if destino.exists():
            print(f"ya existe, no se toca: {destino}")
            codigo = 2
            continue
        destino.write_text(esqueleto(data, out_slug, hoy), encoding="utf-8")
        print(f"creado: {destino}")
    return codigo


_VOSEO = re.compile(r"\b(tenés|querés|sabés|decime|elegís|defendés|vos)\b", re.IGNORECASE)


def _secciones(texto: str) -> dict[str, str]:
    """Cuerpo de cada seccion '## ...' del kit, indexado por el titulo."""
    partes = re.split(r"\n## ", texto)
    return {p.split("\n", 1)[0].strip(): p.split("\n", 1)[1] if "\n" in p else "" for p in partes[1:]}


def _bloque_codigo(cuerpo: str | None) -> str | None:
    m = re.search(r"```\n(.*?)```", cuerpo or "", re.DOTALL)
    return m.group(1) if m else None


def _seccion(secciones: dict[str, str], prefijo: str) -> str | None:
    for titulo, cuerpo in secciones.items():
        if titulo.startswith(prefijo):
            return cuerpo
    return None


def revisar_kit(texto: str) -> list[str]:
    """Errores de un kit terminado. Lista vacia = listo para pegar en YouTube."""
    texto = texto.replace("\r\n", "\n")
    errores: list[str] = []
    pendientes = texto.count("[REDACTAR")
    if pendientes:
        errores.append(f"quedan {pendientes} marcadores [REDACTAR sin redactar")
    secciones = _secciones(texto)

    desc = _bloque_codigo(_seccion(secciones, "Descripción"))
    if desc is None:
        errores.append("falta el bloque de la descripción")
    else:
        if "Suscríbete a RETROTARROS" not in desc:
            errores.append("falta el CTA de suscripción en la descripción")
        lineas = [l for l in desc.splitlines() if l.startswith("#")]
        marcas = lineas[-1].split() if lineas else []
        if not 4 <= len(marcas) <= 5:
            errores.append(f"hashtags: hay {len(marcas)} (deben ser 4 o 5)")
        if marcas and marcas[0] != "#RetroReseñas":
            errores.append("el primer hashtag debe ser #RetroReseñas")
        if marcas and marcas[-1] != "#Retrotarros":
            errores.append("el último hashtag debe ser #Retrotarros")

    tags_txt = _bloque_codigo(_seccion(secciones, "Tags YouTube"))
    if tags_txt is None:
        errores.append("falta la sección de tags")
    else:
        if len(tags_txt.strip()) > 500:
            errores.append(f"el bloque de tags mide {len(tags_txt.strip())} caracteres (máximo 500)")
        n = len([t for t in tags_txt.split(",") if t.strip()])
        if not 15 <= n <= 25:
            errores.append(f"tags: hay {n} (deben ser entre 15 y 25)")

    comentario = _bloque_codigo(_seccion(secciones, "Comentario fijado"))
    if not comentario or not comentario.strip():
        errores.append("falta el comentario fijado")

    for m in sorted({m.group(0).lower() for m in _VOSEO.finditer(texto)}):
        errores.append(f"voseo rioplatense: '{m}'")
    return errores


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "--revisar":
        ruta = Path(argv[1])
        if not ruta.exists():
            print(f"no existe: {ruta}")
            return 2
        errores = revisar_kit(ruta.read_text(encoding="utf-8"))
        for e in errores:
            print(f"  - {e}")
        print(f"{ruta.name}: {len(errores)} errores")
        return 1 if errores else 0
    if len(argv) == 1 and not argv[0].startswith("--"):
        return crear(argv[0])
    print("uso: python scripts/resena_kit.py .cache/gen_resena_<juego>.py")
    print("     python scripts/resena_kit.py --revisar docs/descripciones/descripcion-<slug>.md")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
