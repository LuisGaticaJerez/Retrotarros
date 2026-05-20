"""
tarrobot.py
Asistente de datos curiosos retro Retrotarros · TarroBot.

Uso:
    python scripts/tarrobot.py "Super Mario 64"           # busca en DB local
    python scripts/tarrobot.py "Super Mario 64" --slide   # + genera HTML
    python scripts/tarrobot.py "X" --generate             # genera con Claude API
    python scripts/tarrobot.py --add "tema" "texto" --state talking
    python scripts/tarrobot.py --list                      # lista todos los datos

Requisitos:
    pip install anthropic    (solo para --generate)

Para --generate, setear variable de entorno:
    PowerShell:  $env:ANTHROPIC_API_KEY = "sk-ant-..."
    cmd:         setx ANTHROPIC_API_KEY "sk-ant-..."   (persistente, reabrir terminal)
"""

import argparse
import json
import os
import random
import re
import sys
from pathlib import Path
from datetime import date

REPO = Path(__file__).parent.parent
DB_PATH = REPO / "data" / "tarrobot-database.json"
TEMPLATE = REPO / "studio" / "_template-tarrobot-slide.html"
OUT_DIR = REPO / "studio" / "tarrobot-out"

ESTADOS = [
    "idle", "talking", "excited", "sleep", "thinking", "winking",
    "confused", "glitched", "fact", "happy", "sad", "angry", "loading"
]

LABEL_POR_ESTADO = {
    "idle":     "DATO CURIOSO",
    "talking":  "DATO CURIOSO",
    "excited":  "DATO BOMBA · MIND BLOWN",
    "fact":     "FACT TIME · DATO ESTRELLA",
    "thinking": "PROCESANDO DATO...",
    "winking":  "ENTRE NOSOTROS...",
    "confused": "EN SERIO?",
    "happy":    "BUENA NOTICIA",
    "sad":      "QUE PENA",
    "angry":    "ESTO NO ME GUSTA",
    "loading":  "BUSCANDO INFO...",
    "glitched": "SEÑAL CORRUPTA",
    "sleep":    "DESCANSANDO",
}


# ─────────────────────────────────────────────────────────────────────────
# Util
# ─────────────────────────────────────────────────────────────────────────

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s.strip("-")


def cargar_db() -> dict:
    if not DB_PATH.exists():
        return {"version": 1, "actualizado": str(date.today()), "datos": []}
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def guardar_db(data: dict) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["actualizado"] = str(date.today())
    DB_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def buscar(tema: str, db: dict) -> list:
    """Substring match case-insensitive contra el campo 'tema'."""
    t = tema.lower()
    return [d for d in db["datos"] if t in d.get("tema", "").lower()]


def agregar_dato(
    tema: str,
    texto: str,
    estado: str,
    db: dict,
    consola: str = "",
    ano: int = 0,
    editor: str = "",
    fuente: str = "manual",
) -> dict:
    base_slug = slugify(tema)
    # Evitar colision de IDs
    existing_ids = {d["id"] for d in db["datos"]}
    n = 1
    new_id = f"{base_slug}-{n}"
    while new_id in existing_ids:
        n += 1
        new_id = f"{base_slug}-{n}"

    dato = {
        "id": new_id,
        "tema": tema,
        "texto": texto,
        "estado": estado,
        "consola": consola or "",
        "ano": ano or 0,
        "editor": editor or "",
        "creado": str(date.today()),
        "fuente": fuente,
    }
    db["datos"].append(dato)
    guardar_db(db)
    return dato


# ─────────────────────────────────────────────────────────────────────────
# LLM (Claude API)
# ─────────────────────────────────────────────────────────────────────────

def generar_con_llm(tema: str) -> dict | None:
    """
    Llama a Claude API para generar 3 propuestas de datos curiosos.
    Requiere variable de entorno ANTHROPIC_API_KEY.
    """
    try:
        import anthropic
    except ImportError:
        print("ERROR: libreria 'anthropic' no instalada.", file=sys.stderr)
        print("Instalala con: pip install anthropic", file=sys.stderr)
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: variable de entorno ANTHROPIC_API_KEY no definida.", file=sys.stderr)
        print("", file=sys.stderr)
        print("PowerShell (sesion actual):", file=sys.stderr)
        print('  $env:ANTHROPIC_API_KEY = "sk-ant-..."', file=sys.stderr)
        print("", file=sys.stderr)
        print("PowerShell (persistente):", file=sys.stderr)
        print('  [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY","sk-ant-...","User")', file=sys.stderr)
        print("  (despues reabrir la terminal)", file=sys.stderr)
        return None

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Eres TarroBot, mascota del canal de YouTube Retrotarros sobre videojuegos retro.
Genera 3 datos curiosos cortos sobre: "{tema}".

Requisitos OBLIGATORIOS:
- Español chileno neutro con tuteo (NO voseo argentino: nada de "tenes", "queres", "decime", "vos").
- SIN tildes (a/e/i/o/u sin acento).
- Maximo 3 oraciones por dato, alrededor de 220 caracteres.
- Verificable y especifico: fechas, numeros, nombres reales.
- Tono curioso y entusiasta tipo "te voy a contar algo que no sabias".
- Cada dato distinto del otro (no parafrasear el mismo hecho).

Devuelve SOLO un JSON valido con esta estructura exacta, SIN texto extra ni codigo markdown:

{{
  "consola": "...",
  "ano": 0,
  "editor": "...",
  "datos": [
    {{"texto": "...", "estado_recomendado": "talking"}},
    {{"texto": "...", "estado_recomendado": "excited"}},
    {{"texto": "...", "estado_recomendado": "fact"}}
  ]
}}

Estados validos para "estado_recomendado": talking, excited, fact, winking, confused, happy, sad, angry, thinking.
"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        print(f"ERROR: llamada a Claude API fallo: {e}", file=sys.stderr)
        return None

    raw = response.content[0].text.strip()
    # Limpiar codeblocks si los devolvio
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: el LLM devolvio JSON invalido: {e}", file=sys.stderr)
        print(raw, file=sys.stderr)
        return None

    return result


# ─────────────────────────────────────────────────────────────────────────
# Slide HTML
# ─────────────────────────────────────────────────────────────────────────

def resaltar_quotes(texto: str) -> str:
    """
    Resalta automaticamente algunas palabras clave envolviendolas en <span class='quote'>.
    Heuristica: cantidades en USD, anios, "primer/primera", numeros grandes.
    """
    # USD X.XXX  o  USD XX
    texto = re.sub(r"(USD\s+[\d\.\,]+\+?)", r'<span class="quote">\1</span>', texto)
    # "primer/primera/unico/unica"
    texto = re.sub(r"\b(primer[oa]?|unic[oa])\b", r'<span class="quote">\1</span>', texto, flags=re.IGNORECASE)
    return texto


def generar_slide(dato: dict) -> Path | None:
    if not TEMPLATE.exists():
        print(f"ERROR: no existe el template {TEMPLATE}", file=sys.stderr)
        return None

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    template = TEMPLATE.read_text(encoding="utf-8")

    channel = random.randint(1, 99)
    label = LABEL_POR_ESTADO.get(dato["estado"], "DATO CURIOSO")
    meta_partes = [
        dato.get("consola", ""),
        str(dato.get("ano", "")) if dato.get("ano") else "",
        dato.get("editor", ""),
    ]
    meta = " · ".join(s for s in meta_partes if s and s != "0")

    texto_html = resaltar_quotes(dato["texto"])

    html = (
        template
        .replace("{{ESTADO}}", dato["estado"])
        .replace("{{TEMA}}", dato["tema"])
        .replace("{{TEXTO_HTML}}", texto_html)
        .replace("{{LABEL}}", label)
        .replace("{{META}}", meta or "RETROTARROS · TARROBOT")
        .replace("{{CHANNEL}}", f"CH {channel:02d}")
    )

    out_path = OUT_DIR / f"{dato['id']}.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


# ─────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────

def cmd_list(db: dict) -> int:
    if not db["datos"]:
        print("(base vacia)")
        return 0
    print(f"=== TarroBot DB · {len(db['datos'])} datos ===")
    print()
    for d in db["datos"]:
        meta = " · ".join(s for s in [d.get("consola", ""), str(d.get("ano", "") or "")] if s and s != "0")
        meta_str = f" [{meta}]" if meta else ""
        print(f"  · [{d['estado']:8}] {d['tema']:35}{meta_str}")
        print(f"             {d['texto'][:90]}{'...' if len(d['texto']) > 90 else ''}")
    return 0


def cmd_add(args, db: dict) -> int:
    tema, texto = args.add
    if args.state not in ESTADOS:
        print(f"ERROR: estado invalido. Validos: {', '.join(ESTADOS)}", file=sys.stderr)
        return 1
    dato = agregar_dato(
        tema, texto, args.state, db,
        consola=args.consola or "",
        ano=args.ano or 0,
        editor=args.editor or "",
        fuente="manual",
    )
    print(f"[OK] dato agregado: {dato['id']}")
    print(f"     tema: {dato['tema']}")
    print(f"     estado: {dato['estado']}")
    print(f"     texto: {dato['texto']}")
    if args.slide:
        out = generar_slide(dato)
        if out:
            print(f"[OK] slide HTML: {out}")
    return 0


def cmd_buscar(args, db: dict) -> int:
    matches = buscar(args.tema, db)

    if matches:
        print(f"\n=== {len(matches)} dato(s) sobre '{args.tema}' ===\n")
        for i, d in enumerate(matches, 1):
            print(f"[{i}] {d['tema']} · {d['estado']}")
            print(f"    {d['texto']}")
            meta = " · ".join(s for s in [d.get("consola", ""), str(d.get("ano", "") or ""), d.get("editor", "")] if s and s != "0")
            if meta:
                print(f"    {meta}")
            print()

        if args.slide:
            out = generar_slide(matches[0])
            if out:
                print(f"[OK] slide generado: {out}")
        return 0

    # Sin matches
    print(f"(no hay datos sobre '{args.tema}' en la base local)")

    if not args.generate:
        print("Tip: usa --generate para que Claude proponga 3 opciones.")
        return 0

    # --generate
    print("\n[Claude API] Generando 3 propuestas con Haiku...")
    result = generar_con_llm(args.tema)
    if result is None:
        return 1

    datos_llm = result.get("datos", [])
    if not datos_llm:
        print("ERROR: el LLM no devolvio datos.", file=sys.stderr)
        return 1

    print(f"\n=== Propuestas para '{args.tema}' ===\n")
    for i, d in enumerate(datos_llm, 1):
        estado_rec = d.get("estado_recomendado", "talking")
        print(f"[{i}] ({estado_rec})")
        print(f"    {d['texto']}\n")

    # Aprobar interactivo
    try:
        respuesta = input("Cual aprobas? (1/2/3, 'no' para descartar todas): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelado.")
        return 0

    if respuesta not in ("1", "2", "3"):
        print("Descartado. No se guardo nada.")
        return 0

    idx = int(respuesta) - 1
    elegida = datos_llm[idx]
    estado = elegida.get("estado_recomendado", "talking")
    if estado not in ESTADOS:
        estado = "talking"

    dato = agregar_dato(
        args.tema,
        elegida["texto"],
        estado,
        db,
        consola=result.get("consola", ""),
        ano=int(result.get("ano", 0) or 0),
        editor=result.get("editor", ""),
        fuente="LLM",
    )
    print(f"\n[OK] aprobado y guardado: {dato['id']}")
    if args.slide:
        out = generar_slide(dato)
        if out:
            print(f"[OK] slide: {out}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="TarroBot - asistente de datos curiosos retro Retrotarros",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("tema", nargs="?", help="Tema/juego/consola a buscar")
    parser.add_argument("--list", action="store_true", help="Lista todos los datos en la base")
    parser.add_argument("--generate", action="store_true", help="Si no hay match local, llama Claude API para generar 3 propuestas")
    parser.add_argument("--add", nargs=2, metavar=("TEMA", "TEXTO"), help="Agrega un dato manualmente")
    parser.add_argument("--state", default="talking", help=f"Estado de TarroBot (default: talking). Validos: {', '.join(ESTADOS)}")
    parser.add_argument("--consola", help="Consola del dato (NES, SNES, N64, etc.)")
    parser.add_argument("--ano", type=int, help="Anio del dato")
    parser.add_argument("--editor", help="Editor/estudio")
    parser.add_argument("--slide", action="store_true", help="Genera HTML slide standalone listo para CapCut/DaVinci")
    args = parser.parse_args()

    db = cargar_db()

    if args.list:
        return cmd_list(db)

    if args.add:
        return cmd_add(args, db)

    if not args.tema:
        parser.print_help()
        return 0

    return cmd_buscar(args, db)


if __name__ == "__main__":
    sys.exit(main() or 0)
