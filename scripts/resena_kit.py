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
MARCADOR_TAGS = "[REDACTAR: sumar tags propios del juego: personas, secuela, términos]"


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


def hashtag_consola(data: dict) -> str:
    primera = re.split(r"[·/]", str(data.get("consola") or ""))[0]
    camel = _camel(primera)
    return "#" + camel if camel else ""


def hashtags(data: dict) -> str:
    partes = ["#RetroReseñas", hashtag_juego(data), hashtag_consola(data),
              "#Retrogaming", "#Retrotarros"]
    return " ".join(p for p in partes if p)


def _sin_parentesis(texto: str) -> str:
    return re.sub(r"\s*\([^)]*\)", "", texto).strip()


def tags(data: dict) -> str:
    juego = str(data.get("juego") or "").strip().lower()
    anio = str(data.get("anio") or "").strip()
    candidatos: list[str] = []
    if juego:
        candidatos += [juego, f"{juego} reseña"]
        if anio:
            candidatos.append(f"{juego} {anio}")
    candidatos.append(_sin_parentesis(str(data.get("developer") or "")).lower())
    candidatos += [p.strip().lower() for p in str(data.get("consola") or "").split("·")]
    candidatos.append(_sin_parentesis(str(data.get("genero") or "")).lower())
    candidatos += COLA_TAGS
    vistos: list[str] = []
    for t in candidatos:
        if t and t not in vistos:
            vistos.append(t)
    return ", ".join(vistos) + ", " + MARCADOR_TAGS


def esqueleto(data: dict, out_slug: str, hoy: str) -> str:
    juego = str(data.get("juego") or "")
    anio = str(data.get("anio") or "")
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


def main(argv: list[str]) -> int:
    if len(argv) == 1 and not argv[0].startswith("--"):
        return crear(argv[0])
    print("uso: python scripts/resena_kit.py .cache/gen_resena_<juego>.py")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
