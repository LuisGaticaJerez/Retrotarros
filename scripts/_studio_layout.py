"""
scripts/_studio_layout.py - Retrotarros Studio Suite
Mapeo compartido slug -> carpeta de categoria dentro de studio/, y helper para
encontrar un HTML por slug sin importar en que subcarpeta quedo despues de la
reorganizacion de 2026-07-21. Importado por los generadores de deck, el render
de TarroShorts, y capture-slides.py -- no se repite esta logica en cada script.
"""
from __future__ import annotations
import os
import re
from pathlib import Path


def _repo() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent.parent] + list(here.parents):
        if (p / "studio").is_dir() and (p / "scripts").is_dir():
            return p
    return here.parent.parent


def _studio_root() -> Path:
    env = os.environ.get("RETROTARROS_STUDIO_ROOT")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    return REPO / "studio"


REPO = _repo()
STUDIO = _studio_root()

# Orden importa: se evalua de arriba a abajo, la primera regla que matchea gana.
EPISODE_CATEGORY_RULES: list[tuple[str, str]] = [
    (r"^teaser-", "teasers"),
    (r"-top-mundial$", "rankings/top-mundial"),
    (r"-top-precios$", "rankings/top-precios"),
    (r"-retrotarros-vs-mundo$", "rankings/retrotarros-vs-mundo"),
    (r"-coleccion$", "colecciones"),
    (r"^saga-", "sagas"),
    (r"^retro-", "specials"),
    (r"^n64-(hardware-raro|joyas-ocultas|kirkhope-rare|nintendo-vs-playstation|no-latam)$", "curaduria-n64"),
    (r"-archivo-koko$", "colecciones/archivo-koko"),
]

SHORT_CATEGORY_RULES: list[tuple[str, str]] = [
    (r"^tarroshort-datos-", "datos"),
    (r"^tarroshort-(mas-caros-historia|mejor-consola-retro)$", "cross-console"),
    (r"^tarroshort-.*-top-mundial$", "rankings/top-mundial"),
    (r"^tarroshort-.*-top-precios$", "rankings/top-precios"),
    (r"^tarroshort-.*-coleccion$", "colecciones"),
    (r"^tarroshort-retro-", "specials"),
]


def episode_category(slug: str) -> str:
    """Devuelve la carpeta relativa a studio/ para un episodio largo (ej. 'rankings/top-precios').
    Lanza ValueError si el slug no matchea ninguna regla conocida -- mejor fallar
    ruidoso que adivinar mal y dejar un archivo perdido."""
    for pattern, folder in EPISODE_CATEGORY_RULES:
        if re.search(pattern, slug):
            return folder
    raise ValueError(f"episode_category: '{slug}' no matchea ninguna regla conocida")


def short_category(slug: str) -> str:
    """Igual que episode_category pero para tarroshort-*.html (studio/shorts-html/)."""
    for pattern, folder in SHORT_CATEGORY_RULES:
        if re.search(pattern, slug):
            return folder
    raise ValueError(f"short_category: '{slug}' no matchea ninguna regla conocida")


def find_html(slug: str) -> Path:
    """Busca <slug>.html en todo studio/ (recursivo). Slug pelado, sin ruta --
    asi los comandos CLI existentes (python scripts/tarroshort_render.py <slug>)
    siguen funcionando igual que antes de la reorganizacion."""
    matches = list(STUDIO.glob(f"**/{slug}.html"))
    if not matches:
        raise FileNotFoundError(f"No existe {slug}.html en ninguna subcarpeta de studio/")
    if len(matches) > 1:
        raise FileExistsError(f"'{slug}.html' matcheo mas de un archivo: {matches}")
    return matches[0]
