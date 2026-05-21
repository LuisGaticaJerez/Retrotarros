"""
tarrobot-probar-voces.py
Genera un MP3 de muestra con CADA preset de voz definido en PRESETS_VOZ.
Despues los podes escuchar uno por uno para elegir tu favorito.

Uso:
    python scripts/tarrobot-probar-voces.py
    python scripts/tarrobot-probar-voces.py --frase "Hola, soy TarroBot..."
    python scripts/tarrobot-probar-voces.py --reproducir   (los abre con el player default uno por uno)

Output: studio/voces-muestra/<preset>.mp3
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tarrobot import PRESETS_VOZ, REPO

FRASE_DEFAULT = (
    "¡Hola, hola humanos! Soy TarroBot, mascota de Retrotarros. "
    "Te voy a contar un dato curioso. ¿Te acordás de Super Mario 64? "
    "Salió en 1996 y vendió más de 11 millones de copias."
)

OUT_DIR = REPO / "studio" / "voces-muestra"


async def generar_muestra(preset: str, voz: str, pitch: str, rate: str, frase: str) -> Path | None:
    try:
        import edge_tts
    except ImportError:
        print("ERROR: edge-tts no esta instalado", file=sys.stderr)
        return None

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{preset}.mp3"

    try:
        communicate = edge_tts.Communicate(frase, voice=voz, pitch=pitch, rate=rate)
        await communicate.save(str(out))
        return out
    except Exception as e:
        print(f"  [ERR] {preset}: {e}", file=sys.stderr)
        return None


async def main_async(args):
    frase = args.frase or FRASE_DEFAULT
    print(f"Generando muestras de los {len(PRESETS_VOZ)} presets de voz...")
    print(f"Frase: {frase[:80]}{'...' if len(frase) > 80 else ''}")
    print(f"Output: {OUT_DIR}")
    print()

    import time
    inicio = time.time()

    # Generar en paralelo (con limite)
    sem = asyncio.Semaphore(4)

    async def worker(nombre, voz, pitch, rate):
        async with sem:
            print(f"  [TTS] {nombre:18} {voz:30} pitch={pitch:6} rate={rate}")
            out = await generar_muestra(nombre, voz, pitch, rate, frase)
            return (nombre, out)

    tareas = [worker(n, v, p, r) for n, (v, p, r) in PRESETS_VOZ.items()]
    resultados = await asyncio.gather(*tareas)

    elapsed = time.time() - inicio
    ok = sum(1 for n, o in resultados if o)
    print()
    print(f"=== {ok}/{len(PRESETS_VOZ)} muestras generadas en {elapsed:.1f}s ===")
    print(f"Carpeta: {OUT_DIR}")
    print()
    print("Para escucharlas:")
    print(f"  start \"\" \"{OUT_DIR}\"")
    print("(O ir manualmente con el Explorador)")

    if args.reproducir:
        import subprocess
        print()
        print("Abriendo carpeta...")
        try:
            subprocess.Popen(["explorer", str(OUT_DIR)])
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="Genera muestras de todos los presets de voz")
    parser.add_argument("--frase", help="Frase a sintetizar (default: saludo + dato Mario 64)")
    parser.add_argument("--reproducir", action="store_true", help="Abre la carpeta con muestras al terminar")
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
