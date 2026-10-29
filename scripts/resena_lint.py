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
from pathlib import Path

ESCALA_VEREDICTO = ("IMPRESCINDIBLE", "JUEGAZO", "MEMORABLE", "COLECCIONABLE")

CAMPOS_PANTALLA = (
    "juego", "gancho_sub", "consola", "developer", "genero",
    "contexto_texto", "jugabilidad_dato", "audiovisual_dato",
    "veredicto_resumen", "cierre_sub", "familia_texto",
)

GRAFICAS = ("nueva", "clasica")

BLOQUES_NOTAS = (
    "portada", "ficha", "contexto", "comparativa",
    "jugabilidad", "audiovisual", "veredicto", "cierre",
)

PALABRAS_CRITICA = (
    "malo", "mala", "peor", "aburrido", "aburrida", "feo", "fea",
    "no compite", "fracaso", "lento", "lenta", "mediocre",
)

# Carpeta de box arts de reseñas (los tests la reemplazan por una temporal).
RUTA_CAJAS = Path(__file__).resolve().parent.parent / "studio" / "resenas" / "img" / "resenas"

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

    for campo, texto in _textos_nuevos(data):
        if _TILDES.search(texto):
            errores.append(f"tilde en texto de pantalla: {campo}")

    grafica = data.get("grafica")
    if grafica is not None and grafica not in GRAFICAS:
        errores.append(f"grafica '{grafica}' fuera de {GRAFICAS}")

    vinetas = data.get("jugabilidad_vinetas")
    if vinetas is not None:
        n = len(vinetas) if isinstance(vinetas, (list, tuple)) else -1
        if n != 3:
            errores.append(f"jugabilidad_vinetas debe tener 3 elementos (tiene {n})")
        elif not all(isinstance(v, (list, tuple)) and len(v) >= 2
                     and all(isinstance(t, str) and t.strip() for t in v[:2]) for v in vinetas):
            errores.append("jugabilidad_vinetas: cada elemento debe ser [titulo, texto] con dos textos no vacios")

    # la marca puede ir en el titulo del bloque o en una de sus lineas
    trama = [str(_bloque(data, "contexto").get("titulo") or "")] + _lineas(data, "contexto")
    if not any("trama resumida" in t.lower() for t in trama):
        errores.append("notas.contexto sin una linea con 'TRAMA RESUMIDA'")

    if not any("arcade" in t.lower() for t in _lineas(data, "ficha")):
        errores.append("notas.ficha no menciona 'arcade' (verificar version arcade previa)")

    es_pedido = bool(data.get("pedido"))
    if es_pedido and not out_slug.endswith("-pedido"):
        errores.append("reseña con 'pedido' pero el slug no termina en '-pedido'")
    if not es_pedido and out_slug.endswith("-pedido"):
        errores.append("el slug termina en '-pedido' pero el DATA no tiene 'pedido'")

    avisos += _avisos(data)
    return errores, avisos


def _sin_tildes(s: str) -> str:
    for a, b in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u"}.items():
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def _texto_bloque(bloque: dict) -> str:
    partes = [str(bloque.get("titulo") or ""), str(bloque.get("cue") or "")]
    partes += [str(t) for t in (bloque.get("lineas") or [])]
    return " ".join(partes)


def _textos_nuevos(data: dict) -> list[tuple[str, str]]:
    """Pares (campo, texto) de los textos de pantalla de la grafica nueva. Ignora
    sin fallar todo lo que no tenga la forma esperada."""
    pares: list[tuple[str, str]] = []
    vinetas = data.get("jugabilidad_vinetas")
    if isinstance(vinetas, (list, tuple)):
        for i, v in enumerate(vinetas):
            if isinstance(v, (list, tuple)):
                pares += [(f"jugabilidad_vinetas[{i}]", t) for t in v[:2] if isinstance(t, str)]
    compositor = data.get("audiovisual_compositor")
    if isinstance(compositor, str):
        pares.append(("audiovisual_compositor", compositor))
    proxima = data.get("proxima")
    if isinstance(proxima, dict):
        pares += [(f"proxima.{k}", proxima[k]) for k in ("juego", "consola") if isinstance(proxima.get(k), str)]
    plataformas = data.get("plataformas")
    if isinstance(plataformas, (list, tuple)):
        pares += [("plataformas", p[0]) for p in plataformas
                  if isinstance(p, (list, tuple)) and p and isinstance(p[0], str)]
    return pares


def _avisos(data: dict) -> list[str]:
    avisos: list[str] = []

    palabras = len(str(data.get("contexto_texto") or "").split())
    if palabras > 75:
        avisos.append(f"contexto_texto tiene {palabras} palabras (meta: 50 a 70)")

    for nombre in BLOQUES_NOTAS:
        bloque = _bloque(data, nombre)
        if not bloque:
            avisos.append(f"falta el bloque de notas '{nombre}'")
        elif _TILDES.search(_texto_bloque(bloque)):
            avisos.append(f"tilde en notas.{nombre}")

    textos = [(c, str(data.get(c) or "")) for c in CAMPOS_PANTALLA] + _textos_nuevos(data)
    for campo, bruto in textos:
        texto = _sin_tildes(bruto).lower()
        for palabra in PALABRAS_CRITICA:
            if re.search(rf"\b{re.escape(palabra)}\b", texto):
                avisos.append(f"posible critica dura en pantalla: '{palabra}' en {campo}")

    grafica = data.get("grafica")
    if grafica is None:
        avisos.append('sin la marca grafica: sale con la grafica clasica; las reseñas nuevas deben llevar grafica="nueva"')
    elif grafica == "nueva":
        if not data.get("jugabilidad_vinetas"):
            avisos.append("grafica nueva sin jugabilidad_vinetas (la slide usa el bloque de texto de hoy)")
        if "·" in str(data.get("consola") or "") and not data.get("plataformas"):
            avisos.append("grafica nueva con varias plataformas y falta el campo plataformas (chips sin año)")

    lineas_ficha = " ".join(_lineas(data, "ficha")).lower()
    if "·" in str(data.get("consola") or "") and "primer" not in lineas_ficha:
        avisos.append("varias plataformas y notas.ficha sin linea que diga cual salio primero ('primera'/'primero')")

    n_jug = len(_lineas(data, "jugabilidad"))
    if _bloque(data, "jugabilidad") and n_jug < 3:
        avisos.append(f"notas.jugabilidad tiene {n_jug} lineas (minimo 3 con mecanicas reales)")

    todo_notas = " ".join(_texto_bloque(_bloque(data, n)) for n in BLOQUES_NOTAS).lower()
    if "por confirmar" in todo_notas and not data.get("por_confirmar"):
        avisos.append("las notas dicen 'por confirmar' pero el campo por_confirmar esta vacio")

    avisos += _aviso_caja(data)
    return avisos


def _aviso_caja(data: dict) -> list[str]:
    try:
        from PIL import Image
    except ImportError:
        return []
    clave = data.get("img_key") or _slug(str(data.get("juego") or ""))
    ruta = RUTA_CAJAS / f"{clave}.jpg"
    if not ruta.exists():
        return []
    try:
        with Image.open(ruta) as im:
            ancho = im.width
    except OSError:
        return []
    if ancho < 400:
        return [f"caja de {ancho} px de ancho (menos de 400 px): conviene bajar una mejor"]
    return []


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _sin_tildes(s.lower()).replace("ñ", "n")).strip("-")


def formatear(errores: list[str], avisos: list[str]) -> str:
    partes = []
    if errores:
        partes.append("ERRORES (frenan la generacion):")
        partes += [f"  - {e}" for e in errores]
    if avisos:
        partes.append("AVISOS:")
        partes += [f"  - {a}" for a in avisos]
    return "\n".join(partes)


def capturar_driver(ruta: str) -> list[tuple[dict, str]]:
    """Ejecuta un driver de reseña con generar_resena reemplazada por una funcion
    que solo anota (data, out_slug): no se genera ningun archivo. Devuelve las
    llamadas capturadas (lista vacia si el driver no llamo a generar_resena)."""
    import runpy
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import resena_deck
    capturado: list[tuple[dict, str]] = []

    def _captura(data, out_slug, lint=True):
        capturado.append((data, out_slug))
        return Path(out_slug)

    original = resena_deck.generar_resena
    resena_deck.generar_resena = _captura
    try:
        runpy.run_path(ruta, run_name="__lint__")
    finally:
        resena_deck.generar_resena = original
    return capturado


def main(argv: list[str]) -> int:
    """CLI: revisa el DATA de un driver sin generar nada.
    Devuelve 0 sin errores, 1 con errores, 2 por uso incorrecto o driver que
    no llamo a generar_resena."""
    if len(argv) != 1:
        print("uso: python scripts/resena_lint.py .cache/gen_resena_<juego>.py")
        return 2
    capturado = capturar_driver(argv[0])
    if not capturado:
        print("el driver no llamo a generar_resena")
        return 2
    codigo = 0
    for data, out_slug in capturado:
        errores, avisos = revisar(data, out_slug)
        print(f"{out_slug}: {len(errores)} errores, {len(avisos)} avisos")
        resultado = formatear(errores, avisos)
        if resultado:
            print(resultado)
        if errores:
            codigo = 1
    return codigo


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
