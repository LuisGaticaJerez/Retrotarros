"""
resena_lint.py - Retrotarros Studio Suite
Revisa el DATA de una reseña contra las reglas escritas del formato antes de
generar el HTML. `generar_resena` lo llama siempre; tambien se puede correr
sobre un driver suelto:

    python scripts/resena_lint.py .cache/gen_resena_<juego>.py

revisar(data, out_slug) devuelve (errores, avisos). Los errores frenan la
generacion; los avisos solo se muestran. Diseño: docs/superpowers/specs/
2026-10-28-resena-lint-design.md
"""
from __future__ import annotations
import re

ESCALA_VEREDICTO = ("IMPRESCINDIBLE", "JUEGAZO", "MEMORABLE", "COLECCIONABLE")

CAMPOS_PANTALLA = (
    "juego", "gancho_sub", "consola", "developer", "genero",
    "contexto_texto", "jugabilidad_dato", "audiovisual_dato",
    "veredicto_resumen", "cierre_sub",
)

BLOQUES_NOTAS = (
    "portada", "ficha", "contexto", "comparativa",
    "jugabilidad", "audiovisual", "veredicto", "cierre",
)

_TILDES = re.compile("[áéíóúüÁÉÍÓÚÜ]")


def _bloque(data: dict, nombre: str) -> dict:
    notas = data.get("notas") or {}
    return notas.get(nombre) or {}


def _lineas(data: dict, nombre: str) -> list[str]:
    return [str(t) for t in (_bloque(data, nombre).get("lineas") or [])]


def revisar(data: dict, out_slug: str) -> tuple[list[str], list[str]]:
    errores: list[str] = []
    avisos: list[str] = []

    tag = str(data.get("veredicto_tag") or "").strip().upper()
    if tag not in ESCALA_VEREDICTO:
        errores.append(
            f"veredicto_tag '{data.get('veredicto_tag')}' fuera de la escala "
            f"({', '.join(ESCALA_VEREDICTO)})"
        )

    for campo in CAMPOS_PANTALLA:
        valor = data.get(campo)
        if valor and _TILDES.search(str(valor)):
            errores.append(f"tilde en texto de pantalla: {campo}")

    if not any("TRAMA RESUMIDA" in t for t in _lineas(data, "contexto")):
        errores.append("notas.contexto sin una linea con 'TRAMA RESUMIDA'")

    if not any("arcade" in t.lower() for t in _lineas(data, "ficha")):
        errores.append("notas.ficha no menciona 'arcade' (verificar version arcade previa)")

    es_pedido = bool(data.get("pedido"))
    if es_pedido and not out_slug.endswith("-pedido"):
        errores.append("reseña con 'pedido' pero el slug no termina en '-pedido'")
    if not es_pedido and out_slug.endswith("-pedido"):
        errores.append("el slug termina en '-pedido' pero el DATA no tiene 'pedido'")

    return errores, avisos


def formatear(errores: list[str], avisos: list[str]) -> str:
    partes = []
    if errores:
        partes.append("ERRORES (frenan la generacion):")
        partes += [f"  - {e}" for e in errores]
    if avisos:
        partes.append("AVISOS:")
        partes += [f"  - {a}" for a in avisos]
    return "\n".join(partes)
