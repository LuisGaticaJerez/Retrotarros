"""Pruebas de la escritura segura de videos (scripts/youtube_aplicar.py).

videos().update reemplaza el snippet completo: lo que no se reenvia se pierde (asi quedo el idioma de audio en en-US).
Sin pytest: se corre con `python scripts/test_youtube_aplicar.py`.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import youtube_aplicar as A  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
COMPLETO = {"title": "T", "description": "D", "categoryId": "20", "tags": ["x"], "defaultLanguage": "es",
            "defaultAudioLanguage": "es-419", "channelId": "no se escribe", "publishedAt": "no se escribe"}


def test_cuerpo_snippet_conserva_todos_los_campos_escribibles():
    cuerpo = A.cuerpo_snippet("a", COMPLETO)
    assert cuerpo == {"id": "a", "snippet": {"title": "T", "description": "D", "categoryId": "20", "tags": ["x"],
                                            "defaultLanguage": "es", "defaultAudioLanguage": "es-419"}}


def test_cuerpo_snippet_aplica_solo_los_cambios_pedidos():
    cuerpo = A.cuerpo_snippet("a", COMPLETO, description="nueva", tags=["y"])
    s = cuerpo["snippet"]
    assert s["description"] == "nueva" and s["tags"] == ["y"]
    assert s["title"] == "T" and s["defaultAudioLanguage"] == "es-419" and s["defaultLanguage"] == "es"


def test_cuerpo_snippet_omite_lo_que_el_video_no_tiene():
    assert A.cuerpo_snippet("a", {"title": "T", "categoryId": "20"}) == {"id": "a", "snippet": {"title": "T", "categoryId": "20"}}


def test_ningun_script_arma_el_cuerpo_de_update_a_mano():
    """Todo videos().update(...) debe recibir el cuerpo de cuerpo_snippet; un body armado a mano pierde campos."""
    for ruta in sorted(SCRIPTS.glob("*.py")):
        if ruta.name.startswith("test_"):
            continue
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if ".update(part=" in linea and "videos()" in linea and ".execute()" in linea:   # la llamada real, no un docstring
                assert re.search(r"body=cuerpo_\w+\(|body=A\.cuerpo_snippet\(|body=cuerpo_snippet\(", linea), f"{ruta.name}: {linea.strip()}"


def main() -> int:
    pruebas = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    fallas = 0
    for nombre, fn in pruebas:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            fallas += 1
            print(f"FALLA {nombre}: {type(exc).__name__}: {exc}")
    if fallas:
        print(f"{fallas} de {len(pruebas)} pruebas fallaron")
        return 1
    print(f"OK {len(pruebas)} pruebas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
