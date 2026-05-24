"""
obs_recorder.py - Sprint 18 - Retrotarros Studio Suite

Auto-recording sincronizado con la sesion de TarroBot. Cuando se carga una
pauta, opcionalmente arranca OBS en grabacion contra un path canonico:
    <repo>/recordings/<slug>/master-YYYYMMDD-HHMMSS.mp4

Al terminar, el path queda guardado para que TarroTeaser lo recoja automatico.

Estado persistente en memoria:
    auto_record_on_session = bool (toggle del operador)
    last_recording = {slug, path, started_at, stopped_at}

API publica:
    set_auto_record(on: bool)
    is_auto_record() -> bool
    last_recording_path(slug: str) -> str | None
    start_recording(client, slug: str) -> dict
    stop_recording(client) -> dict
    status(client) -> dict
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Optional


# ────────────────────────────────────────────────────────────────────
# Resolucion de paths (consistente con tarroteaser)
# ────────────────────────────────────────────────────────────────────

def _resolve_repo() -> Path:
    """Resuelve REPO root (env RETROTARROS_REPO o parent del script)."""
    env_repo = os.environ.get("RETROTARROS_REPO")
    if env_repo:
        p = Path(env_repo).resolve()
        if p.exists():
            return p
    return Path(__file__).resolve().parent.parent


def recording_dir_for(slug: str) -> Path:
    """Directorio destino para el master de un slug.

    Default: <repo>/recordings/<slug>/
    Override: env RETROTARROS_RECORDINGS_DIR (suma el slug al final).
    """
    env_out = os.environ.get("RETROTARROS_RECORDINGS_DIR")
    if env_out:
        return Path(env_out).resolve() / slug
    return _resolve_repo() / "recordings" / slug


# ────────────────────────────────────────────────────────────────────
# Estado in-memory
# ────────────────────────────────────────────────────────────────────

_state = {
    "auto_record": False,
    "last": None,  # {slug, dir, started_at, stopped_at, output_path}
}


def set_auto_record(on: bool) -> None:
    _state["auto_record"] = bool(on)


def is_auto_record() -> bool:
    return bool(_state["auto_record"])


def last_recording() -> Optional[dict]:
    return _state["last"]


def last_recording_path(slug: str) -> Optional[str]:
    """Devuelve el path del ultimo master para un slug, si existe en disco.

    Busca archivos master-*.mp4 en recording_dir_for(slug) y devuelve el mas
    reciente. None si no hay nada.
    """
    rec_dir = recording_dir_for(slug)
    if not rec_dir.exists():
        return None
    candidates = sorted(
        rec_dir.glob("master-*.mp4"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        # fallback: cualquier mp4 reciente en la carpeta
        any_mp4 = sorted(rec_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if any_mp4:
            return str(any_mp4[0])
        return None
    return str(candidates[0])


# ────────────────────────────────────────────────────────────────────
# Operaciones OBS
# ────────────────────────────────────────────────────────────────────

async def start_recording(client, slug: str) -> dict:
    """Configura el directorio de grabacion y arranca OBS Record.

    Args:
        client: OBSClient conectado
        slug: kebab-case del episodio

    Returns:
        {ok: bool, started: bool, dir: str, error?: str}
    """
    if client is None or not getattr(client, "connected", False):
        return {"ok": False, "error": "OBS desconectado"}

    rec_dir = recording_dir_for(slug)
    try:
        rec_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return {"ok": False, "error": f"no se pudo crear dir: {e}"}

    # 1) Estado actual (no arrancar si ya esta grabando)
    try:
        rs = await client._request("GetRecordStatus")
        if rs.get("outputActive"):
            return {
                "ok": False,
                "error": "OBS ya esta grabando. Para primero la grabacion actual.",
                "dir": str(rec_dir),
            }
    except Exception as e:
        return {"ok": False, "error": f"GetRecordStatus fallo: {e}"}

    # 2) Setear directorio de grabacion
    try:
        await client._request("SetRecordDirectory", {"recordDirectory": str(rec_dir)})
    except Exception as e:
        return {"ok": False, "error": f"SetRecordDirectory fallo: {e}", "dir": str(rec_dir)}

    # 3) Arrancar grabacion
    try:
        await client._request("StartRecord")
    except Exception as e:
        return {"ok": False, "error": f"StartRecord fallo: {e}", "dir": str(rec_dir)}

    _state["last"] = {
        "slug": slug,
        "dir": str(rec_dir),
        "started_at": time.time(),
        "stopped_at": None,
        "output_path": None,
    }
    return {"ok": True, "started": True, "dir": str(rec_dir), "slug": slug}


async def stop_recording(client) -> dict:
    """Para la grabacion actual. Captura el path del archivo generado.

    Returns:
        {ok: bool, stopped: bool, output_path?: str, error?: str}
    """
    if client is None or not getattr(client, "connected", False):
        return {"ok": False, "error": "OBS desconectado"}

    try:
        rs = await client._request("GetRecordStatus")
        if not rs.get("outputActive"):
            return {"ok": False, "error": "OBS no esta grabando"}
    except Exception as e:
        return {"ok": False, "error": f"GetRecordStatus fallo: {e}"}

    try:
        r = await client._request("StopRecord")
        output_path = r.get("outputPath", "")
    except Exception as e:
        return {"ok": False, "error": f"StopRecord fallo: {e}"}

    if _state["last"]:
        _state["last"]["stopped_at"] = time.time()
        _state["last"]["output_path"] = output_path

    return {"ok": True, "stopped": True, "output_path": output_path}


async def status(client) -> dict:
    """Estado actual de la grabacion."""
    out = {
        "auto_record": is_auto_record(),
        "last": _state["last"],
        "obs_recording": False,
        "obs_record_dir": None,
        "timecode": None,
    }
    if client is None or not getattr(client, "connected", False):
        return out
    try:
        rs = await client._request("GetRecordStatus")
        out["obs_recording"] = bool(rs.get("outputActive"))
        out["timecode"] = rs.get("outputTimecode", "")
    except Exception:
        pass
    try:
        rd = await client._request("GetRecordDirectory")
        out["obs_record_dir"] = rd.get("recordDirectory", "")
    except Exception:
        pass
    return out
