"""
capcut_ready.py - Sprint 18 - Retrotarros Studio Suite

Empaqueta TODO lo necesario para abrir un episodio en CapCut sin pelear
con carpetas dispersas: master OBS + teaser TarroTeaser + cartelas PNG +
descripcion YT + thumbnails sugeridos + README con orden de import.

NO genera el .draft de CapCut (eso es research pausado en
docs/capcut-automation-research.md). Solo organiza los assets para
que arrastres a CapCut en 30 segundos.

Output:
    <repo>/recordings/<slug>/capcut-ready/
        ├── README.txt
        ├── master.mp4               (link/copia del master OBS)
        ├── teaser.mp4               (si existe)
        ├── descripcion.txt          (titulos + descripcion + hashtags)
        ├── cartelas/
        │   ├── slide-01.png
        │   ├── slide-02.png
        │   └── ...
        └── thumbnails/
            ├── slide-01.png         (mismas que cartelas pero con thumbnail-* nombre)

Uso:
    from capcut_ready import empaquetar
    result = empaquetar("n64-top-precios")
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Optional


# ────────────────────────────────────────────────────────────────────
# Paths
# ────────────────────────────────────────────────────────────────────

def _resolve_repo() -> Path:
    env_repo = os.environ.get("RETROTARROS_REPO")
    if env_repo:
        p = Path(env_repo).resolve()
        if p.exists():
            return p
    return Path(__file__).resolve().parent.parent


import sys as _sys
_sys.path.insert(0, str(_resolve_repo() / "scripts"))
from _studio_layout import STUDIO, find_html


def capcut_ready_dir(slug: str) -> Path:
    return _resolve_repo() / "recordings" / slug / "capcut-ready"


# ────────────────────────────────────────────────────────────────────
# Resolucion de assets
# ────────────────────────────────────────────────────────────────────

def _find_master(slug: str) -> Optional[Path]:
    """Master de OBS auto-record (o cualquier mp4 en recordings/<slug>/)."""
    repo = _resolve_repo()
    rec_dir = repo / "recordings" / slug
    if not rec_dir.exists():
        return None
    # Buscar master-*.mp4 mas reciente, fallback a cualquier .mp4
    candidates = sorted(
        list(rec_dir.glob("master-*.mp4")) + list(rec_dir.glob("*.mp4")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _find_teaser(slug: str) -> Optional[Path]:
    """Teaser generado por TarroTeaser."""
    teaser_dir = STUDIO / "teasers" / slug
    if not teaser_dir.exists():
        return None
    candidates = sorted(
        teaser_dir.glob("*tarroteaser*.mp4"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    any_mp4 = sorted(teaser_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    return any_mp4[0] if any_mp4 else None


def _find_cartelas(slug: str) -> list[Path]:
    """Cartelas PNG del slide del estudio (capture-slides output)."""
    try:
        html_path = find_html(slug)
    except (FileNotFoundError, FileExistsError):
        return []
    cap_dir = html_path.parent / "captures" / slug
    if not cap_dir.exists():
        return []
    return sorted(cap_dir.glob("*.png"))


def _find_descripcion(slug: str) -> Optional[Path]:
    """Output de /api/episodio/exportar-descripcion."""
    repo = _resolve_repo()
    desc = repo / "studio" / "exports" / f"{slug}-publicacion.txt"
    return desc if desc.exists() else None


# ────────────────────────────────────────────────────────────────────
# Empaquetado
# ────────────────────────────────────────────────────────────────────

def empaquetar(slug: str, copy_videos: bool = False) -> dict:
    """Crea la carpeta capcut-ready/ para un slug.

    Args:
        slug: episodio (kebab-case)
        copy_videos: si True copia master.mp4 y teaser.mp4 (consume MB).
            Si False, no los copia (asume que CapCut puede importarlos via
            atajo en README). Default False para ser frugal con disco.
    """
    if not slug or not slug.replace("-", "").isalnum():
        return {"ok": False, "error": "slug invalido"}

    out_dir = capcut_ready_dir(slug)
    out_dir.mkdir(parents=True, exist_ok=True)

    inventory = {
        "slug": slug,
        "out_dir": str(out_dir),
        "files": [],
        "missing": [],
        "notes": [],
    }

    # 1) Master OBS
    master = _find_master(slug)
    if master:
        target = out_dir / "master.mp4"
        if copy_videos:
            shutil.copy2(master, target)
            inventory["files"].append({"role": "master", "path": str(target), "source": str(master), "copied": True})
        else:
            inventory["files"].append({"role": "master", "path": str(master), "copied": False})
            inventory["notes"].append(f"master apuntado en {master} (no copiado para ahorrar disco)")
    else:
        inventory["missing"].append("master.mp4 (no se encontro recordings/<slug>/master-*.mp4)")

    # 2) Teaser TarroTeaser
    teaser = _find_teaser(slug)
    if teaser:
        target = out_dir / "teaser.mp4"
        if copy_videos:
            shutil.copy2(teaser, target)
            inventory["files"].append({"role": "teaser", "path": str(target), "source": str(teaser), "copied": True})
        else:
            inventory["files"].append({"role": "teaser", "path": str(teaser), "copied": False})
            inventory["notes"].append(f"teaser apuntado en {teaser}")
    else:
        inventory["missing"].append("teaser.mp4 (genera con card TARROTEASER antes)")

    # 3) Cartelas (siempre se copian, son chicas)
    cartelas = _find_cartelas(slug)
    if cartelas:
        cart_dir = out_dir / "cartelas"
        cart_dir.mkdir(exist_ok=True)
        for c in cartelas:
            target = cart_dir / c.name
            try:
                shutil.copy2(c, target)
                inventory["files"].append({"role": "cartela", "path": str(target)})
            except Exception as e:
                inventory["notes"].append(f"no se pudo copiar {c.name}: {e}")
    else:
        inventory["missing"].append(f"cartelas/ (no hay PNGs en studio/captures/{slug}/)")

    # 4) Descripcion YT
    descripcion = _find_descripcion(slug)
    if descripcion:
        target = out_dir / "descripcion.txt"
        try:
            shutil.copy2(descripcion, target)
            inventory["files"].append({"role": "descripcion", "path": str(target)})
        except Exception as e:
            inventory["notes"].append(f"no se pudo copiar descripcion: {e}")
    else:
        inventory["missing"].append("descripcion.txt (genera con card EXPORTAR PUBLICACION antes)")

    # 5) README de orden de import
    readme_path = out_dir / "README.txt"
    readme = _build_readme(slug, inventory)
    readme_path.write_text(readme, encoding="utf-8")
    inventory["files"].append({"role": "readme", "path": str(readme_path)})

    return {
        "ok": True,
        "slug": slug,
        "out_dir": str(out_dir),
        "inventory": inventory,
    }


def _build_readme(slug: str, inv: dict) -> str:
    """Genera README.txt con instrucciones para CapCut."""
    files = inv.get("files", [])
    missing = inv.get("missing", [])

    master = next((f for f in files if f.get("role") == "master"), None)
    teaser = next((f for f in files if f.get("role") == "teaser"), None)
    cartelas = [f for f in files if f.get("role") == "cartela"]
    descripcion = next((f for f in files if f.get("role") == "descripcion"), None)

    lines = []
    lines.append("=" * 60)
    lines.append(f"CAPCUT READY · {slug}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Orden sugerido para armar el episodio final en CapCut:")
    lines.append("")
    lines.append("1. Abrir CapCut > New Project > 16:9 (1920x1080) 60 FPS")
    lines.append("")
    if master:
        copied = master.get("copied", True)
        path = master.get("path", "?")
        lines.append(f"2. Importar el MASTER del episodio:")
        lines.append(f"   {path}")
        if not copied:
            lines.append(f"   (esta apuntando al original, no se copio para ahorrar disco)")
        lines.append(f"   - Drag al timeline.")
        lines.append(f"   - Click derecho > Audio > 'Voice Enhancement' (limpia musica de fondo).")
        lines.append("")
    else:
        lines.append("2. (Falta master.mp4 - graba primero con OBS auto-record)")
        lines.append("")
    if cartelas:
        lines.append(f"3. Importar CARTELAS HTML del estudio ({len(cartelas)} PNGs en cartelas/):")
        lines.append("   - Drag las que quieras encima del video como overlay.")
        lines.append("   - Tip: las cartelas 'paneo' van bien entre bloques.")
        lines.append("")
    if teaser:
        path = teaser.get("path", "?")
        lines.append(f"4. (Opcional) Importar el TEASER pre-generado:")
        lines.append(f"   {path}")
        lines.append("   - Sirve como gancho del primer minuto o como cold open.")
        lines.append("")
    if descripcion:
        lines.append("5. Al exportar, abrir descripcion.txt y copiar:")
        lines.append("   - Uno de los 3 titulos sugeridos.")
        lines.append("   - La descripcion completa con timestamps.")
        lines.append("   - Los hashtags al final.")
        lines.append("")
    lines.append("=" * 60)
    lines.append("ASSETS EN ESTA CARPETA")
    lines.append("=" * 60)
    if files:
        for f in files:
            lines.append(f"  [{f.get('role', '?')}] {f.get('path', '')}")
    if missing:
        lines.append("")
        lines.append("FALTAN:")
        for m in missing:
            lines.append(f"  - {m}")
    lines.append("")
    lines.append("=" * 60)
    lines.append(f"Generado por TarroBot Studio · capcut_ready.empaquetar('{slug}')")
    return "\n".join(lines)
