"""
obs_healthcheck.py - Sprint 18 - Retrotarros Studio Suite

Diagnostico de la configuracion de OBS para grabar episodios Retrotarros.
Corre una serie de checks via obs-websocket v5 y devuelve estado +
instrucciones de fix para cada uno.

Disenado para que el operador del estudio abra el panel y vea de un
vistazo si OBS esta listo o que falta. Sin tocar nada en OBS.

Uso desde tarrobot-live.py:
    from obs_healthcheck import run_healthcheck
    result = await run_healthcheck(obs_client, alias_path)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Optional


# ────────────────────────────────────────────────────────────────────
# Modelo
# ────────────────────────────────────────────────────────────────────

# Status posibles para un check:
#   ok    = todo bien, nada que hacer
#   warn  = funciona pero deberia revisarse (no bloquea grabacion)
#   error = bloquea uso, requiere intervencion del operador
#   skip  = no se pudo correr (precondicion fallo, ej OBS desconectado)
STATUS_OK = "ok"
STATUS_WARN = "warn"
STATUS_ERROR = "error"
STATUS_SKIP = "skip"


@dataclass
class Check:
    """Resultado de un check individual."""
    id: str                  # slug del check (ej "canvas_resolution")
    label: str               # titulo legible (ej "Resolucion del canvas")
    status: str              # ok | warn | error | skip
    msg: str                 # mensaje corto del estado
    fix: Optional[str] = None  # instruccion legible si status != ok
    detail: Optional[dict] = None  # datos crudos opcionales (para debug)


@dataclass
class HealthcheckResult:
    """Resultado agregado del healthcheck."""
    ok: bool                 # True si NO hay ningun check error
    checks: list[Check]
    summary: dict            # {ok: N, warn: N, error: N, skip: N}

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "checks": [asdict(c) for c in self.checks],
            "summary": self.summary,
        }


# ────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────

def _check_pass(id: str, label: str, msg: str, detail: dict | None = None) -> Check:
    return Check(id=id, label=label, status=STATUS_OK, msg=msg, detail=detail)


def _check_warn(id: str, label: str, msg: str, fix: str, detail: dict | None = None) -> Check:
    return Check(id=id, label=label, status=STATUS_WARN, msg=msg, fix=fix, detail=detail)


def _check_err(id: str, label: str, msg: str, fix: str, detail: dict | None = None) -> Check:
    return Check(id=id, label=label, status=STATUS_ERROR, msg=msg, fix=fix, detail=detail)


def _check_skip(id: str, label: str, msg: str) -> Check:
    return Check(id=id, label=label, status=STATUS_SKIP, msg=msg)


# ────────────────────────────────────────────────────────────────────
# Checks individuales
# ────────────────────────────────────────────────────────────────────

async def _check_obs_version(client) -> Check:
    """Check OBS y obs-websocket version."""
    try:
        v = await client._request("GetVersion")
        obs_ver = v.get("obsVersion", "?")
        ws_ver = v.get("obsWebSocketVersion", "?")
        platform = v.get("platform", "?")
        # obs-websocket v5+ requerido
        try:
            major = int(ws_ver.split(".")[0])
        except (ValueError, IndexError):
            major = 0
        if major < 5:
            return _check_warn(
                "obs_version",
                "Version de OBS + obs-websocket",
                f"OBS {obs_ver} · ws {ws_ver}",
                "Actualiza obs-websocket plugin a v5+. Settings > Tools > obs-websocket Settings",
                {"obs": obs_ver, "websocket": ws_ver, "platform": platform},
            )
        return _check_pass(
            "obs_version",
            "Version de OBS + obs-websocket",
            f"OBS {obs_ver} · ws {ws_ver} ({platform})",
            {"obs": obs_ver, "websocket": ws_ver, "platform": platform},
        )
    except Exception as e:
        return _check_err(
            "obs_version", "Version de OBS + obs-websocket",
            f"no se pudo consultar: {e}",
            "Verifica que el plugin obs-websocket este instalado y habilitado",
        )


async def _check_canvas(client) -> tuple[Check, Check]:
    """Check resolucion + FPS del canvas."""
    try:
        v = await client._request("GetVideoSettings")
        base_w = int(v.get("baseWidth", 0))
        base_h = int(v.get("baseHeight", 0))
        fps_num = int(v.get("fpsNumerator", 30))
        fps_den = int(v.get("fpsDenominator", 1)) or 1
        fps = fps_num / fps_den

        if base_w == 1920 and base_h == 1080:
            res_check = _check_pass(
                "canvas_resolution",
                "Resolucion del canvas",
                f"{base_w}x{base_h} (1080p OK)",
                {"width": base_w, "height": base_h},
            )
        else:
            res_check = _check_warn(
                "canvas_resolution",
                "Resolucion del canvas",
                f"{base_w}x{base_h} (esperado 1920x1080)",
                "Settings > Video > Base (Canvas) Resolution = 1920x1080",
                {"width": base_w, "height": base_h},
            )

        if 59 <= fps <= 61:
            fps_check = _check_pass(
                "canvas_fps",
                "FPS del canvas",
                f"{fps:.1f} FPS",
                {"fps": fps},
            )
        elif 29 <= fps <= 31:
            fps_check = _check_warn(
                "canvas_fps",
                "FPS del canvas",
                f"{fps:.1f} FPS (recomendado 60 para mejor calidad de paneos)",
                "Settings > Video > Common FPS Values = 60",
                {"fps": fps},
            )
        else:
            fps_check = _check_warn(
                "canvas_fps",
                "FPS del canvas",
                f"{fps:.1f} FPS (inusual)",
                "Settings > Video > Common FPS Values = 60",
                {"fps": fps},
            )

        return res_check, fps_check
    except Exception as e:
        err = _check_err(
            "canvas_resolution", "Resolucion del canvas",
            f"no se pudo consultar: {e}",
            "Revisar permisos del plugin obs-websocket",
        )
        return err, _check_skip("canvas_fps", "FPS del canvas", "depende de canvas_resolution")


async def _check_scenes(client, alias: dict) -> list[Check]:
    """Para cada escena en obs-aliases.json, verifica que exista en OBS."""
    checks = []
    try:
        sl = await client.get_scene_list()
        existing = {s.get("sceneName", "") for s in sl.get("scenes", [])}
    except Exception as e:
        return [_check_err(
            "scenes_list", "Listado de escenas OBS",
            f"no se pudo consultar: {e}",
            "Reconecta a OBS desde el panel",
        )]

    # 1) default_scene
    default_scene = alias.get("default_scene")
    if default_scene:
        if default_scene in existing:
            checks.append(_check_pass(
                "scene_default", "Escena default",
                f"'{default_scene}' OK"))
        else:
            checks.append(_check_err(
                "scene_default", "Escena default",
                f"'{default_scene}' no existe en OBS",
                f"Crea una escena llamada '{default_scene}' o cambia default_scene en obs-aliases.json",
            ))

    # 2) tarrobot_scene
    tar_scene = alias.get("tarrobot_scene")
    if tar_scene:
        if tar_scene in existing:
            checks.append(_check_pass(
                "scene_tarrobot", "Escena de TarroBot (auto-cambio al hablar)",
                f"'{tar_scene}' OK"))
        else:
            checks.append(_check_err(
                "scene_tarrobot", "Escena de TarroBot (auto-cambio al hablar)",
                f"'{tar_scene}' no existe en OBS",
                f"Crea una escena llamada '{tar_scene}' que muestre la TarroVision a pantalla completa",
            ))

    # 3) Escenas mapeadas en aliases.escenas
    escenas_dict = alias.get("escenas", {}) or {}
    target_scenes = set(escenas_dict.values())  # nombres reales OBS
    missing = sorted(s for s in target_scenes if s not in existing)
    if not missing:
        checks.append(_check_pass(
            "scenes_aliases", "Escenas mapeadas en obs-aliases.json",
            f"{len(target_scenes)} escenas mapeadas, todas existen",
            {"existing_count": len(existing), "mapped": len(target_scenes)},
        ))
    else:
        checks.append(_check_err(
            "scenes_aliases", "Escenas mapeadas en obs-aliases.json",
            f"{len(missing)} escenas faltan en OBS: {', '.join(missing)}",
            "Crea esas escenas en OBS con nombre EXACTO, o quita los mapeos no usados en obs-aliases.json",
            {"missing": missing, "existing": sorted(existing)},
        ))

    # 4) Close-ups
    close_ups = alias.get("close_ups", {}) or {}
    cu_targets = set(close_ups.values())
    cu_missing = sorted(s for s in cu_targets if s not in existing)
    if not cu_targets:
        pass  # sin close-ups configurados es OK
    elif not cu_missing:
        checks.append(_check_pass(
            "scenes_closeups", "Escenas de close-up",
            f"{len(cu_targets)} close-ups OK",
        ))
    else:
        checks.append(_check_warn(
            "scenes_closeups", "Escenas de close-up",
            f"{len(cu_missing)} close-ups faltan: {', '.join(cu_missing)}",
            "Crea las escenas faltantes o quita los close-ups no usados en obs-aliases.json",
            {"missing": cu_missing},
        ))

    return checks


async def _check_audio_inputs(client, alias: dict) -> list[Check]:
    """Chequea inputs de audio criticos: musica-fondo y al menos 1 mic."""
    checks = []
    try:
        il = await client._request("GetInputList")
        inputs = il.get("inputs", []) or []
    except Exception as e:
        return [_check_err(
            "inputs_list", "Listado de inputs OBS",
            f"no se pudo consultar: {e}",
            "Reconecta a OBS",
        )]

    input_names = {(i.get("inputName") or "") for i in inputs}
    input_kinds = {
        (i.get("inputName") or ""): (i.get("inputKind") or "")
        for i in inputs
    }

    # 1) Musica de fondo
    musica = alias.get("musica_fondo", {}) or {}
    musica_input = musica.get("input_name")
    if musica_input:
        if musica_input in input_names:
            checks.append(_check_pass(
                "input_musica", "Input de musica de fondo",
                f"'{musica_input}' OK ({input_kinds.get(musica_input, '?')})",
            ))
        else:
            checks.append(_check_warn(
                "input_musica", "Input de musica de fondo",
                f"'{musica_input}' no existe (no podras usar la card MUSICA)",
                f"Agrega un input de audio (Media Source o WASAPI) llamado '{musica_input}' en alguna escena",
            ))

    # 2) Al menos un mic
    mic_kinds = {"wasapi_input_capture", "coreaudio_input_capture", "pulse_input_capture", "audio_input_capture"}
    mics = [n for n, k in input_kinds.items() if k in mic_kinds]
    if mics:
        checks.append(_check_pass(
            "input_mic", "Microfono detectado",
            f"{len(mics)} mic(s): {', '.join(mics[:3])}",
            {"mics": mics},
        ))
    else:
        checks.append(_check_err(
            "input_mic", "Microfono detectado",
            "no se detecto ningun input de audio tipo microfono",
            "Settings > Audio > Mic/Auxiliary, o agrega un Audio Input Capture en alguna escena",
        ))

    return checks


async def _check_recording(client) -> Check:
    """Verifica el directorio de grabacion."""
    try:
        r = await client._request("GetRecordDirectory")
        rec_dir = r.get("recordDirectory", "")
        if not rec_dir:
            return _check_warn(
                "recording_dir", "Directorio de grabacion",
                "no configurado",
                "Settings > Output > Recording > Recording Path",
            )
        # Verificar que existe y se puede escribir
        p = Path(rec_dir)
        if not p.exists():
            return _check_warn(
                "recording_dir", "Directorio de grabacion",
                f"'{rec_dir}' no existe en disco",
                "Crea la carpeta o cambia el path en Settings > Output > Recording",
                {"path": rec_dir},
            )
        return _check_pass(
            "recording_dir", "Directorio de grabacion",
            f"'{rec_dir}' OK",
            {"path": rec_dir},
        )
    except Exception as e:
        return _check_warn(
            "recording_dir", "Directorio de grabacion",
            f"no se pudo consultar: {e}",
            "Plugin obs-websocket viejo? Update a v5+",
        )


async def _check_browser_sources(client, alias: dict) -> Check:
    """Detecta si hay browser source apuntando al tarrobot-live.html (capa virtual)."""
    try:
        il = await client._request("GetInputList", {"inputKind": "browser_source"})
        browser_inputs = il.get("inputs", []) or []
    except Exception:
        return _check_skip(
            "browser_sources", "Browser Sources (TarroBot live)",
            "no se pudo listar browser sources",
        )

    if not browser_inputs:
        return _check_warn(
            "browser_sources", "Browser Sources (TarroBot live)",
            "no se detecto ningun Browser Source en OBS",
            "Agrega un Browser Source apuntando a http://localhost:8001/live para ver la TarroVision en escena",
        )

    # Buscar uno que apunte a tarrobot live o slide HTML del estudio
    tarrobot_found = False
    urls = []
    for inp in browser_inputs:
        try:
            s = await client._request("GetInputSettings", {"inputName": inp["inputName"]})
            settings = s.get("inputSettings", {}) or {}
            url = settings.get("url", "") or settings.get("local_file", "") or ""
            urls.append(url[:80])
            url_low = url.lower()
            if "tarrobot" in url_low or "localhost:8001" in url_low or "127.0.0.1:8001" in url_low:
                tarrobot_found = True
        except Exception:
            continue

    if tarrobot_found:
        return _check_pass(
            "browser_sources", "Browser Sources (TarroBot live)",
            f"{len(browser_inputs)} browser source(s), TarroBot detectado",
            {"urls": urls},
        )
    return _check_warn(
        "browser_sources", "Browser Sources (TarroBot live)",
        f"{len(browser_inputs)} browser source(s) pero ninguno apunta a TarroBot",
        "Agrega un Browser Source con URL http://localhost:8001/live (la TarroVision)",
        {"urls": urls},
    )


# ────────────────────────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────────────────────────

async def run_healthcheck(client, alias: dict) -> HealthcheckResult:
    """Corre todos los checks. Si client es None o no esta conectado,
    devuelve un solo check con status=error y resto skipped."""
    checks: list[Check] = []

    if client is None or not getattr(client, "connected", False):
        checks.append(_check_err(
            "obs_connected", "Conexion a OBS",
            "OBS no conectado (panel desconectado o OBS cerrado)",
            "Abre OBS, asegurate que obs-websocket este habilitado, y aprieta CONECTAR en la card de OBS",
        ))
        # Mark resto como skip
        for cid, clabel in [
            ("obs_version", "Version de OBS + obs-websocket"),
            ("canvas_resolution", "Resolucion del canvas"),
            ("canvas_fps", "FPS del canvas"),
            ("scenes_aliases", "Escenas mapeadas en obs-aliases.json"),
            ("input_mic", "Microfono detectado"),
            ("recording_dir", "Directorio de grabacion"),
            ("browser_sources", "Browser Sources (TarroBot live)"),
        ]:
            checks.append(_check_skip(cid, clabel, "OBS desconectado"))
    else:
        # Conectado: correr todos los checks
        checks.append(_check_pass("obs_connected", "Conexion a OBS", "WS conectado"))
        checks.append(await _check_obs_version(client))
        res_check, fps_check = await _check_canvas(client)
        checks.append(res_check)
        checks.append(fps_check)
        checks.extend(await _check_scenes(client, alias))
        checks.extend(await _check_audio_inputs(client, alias))
        checks.append(await _check_recording(client))
        checks.append(await _check_browser_sources(client, alias))

    summary = {
        "ok": sum(1 for c in checks if c.status == STATUS_OK),
        "warn": sum(1 for c in checks if c.status == STATUS_WARN),
        "error": sum(1 for c in checks if c.status == STATUS_ERROR),
        "skip": sum(1 for c in checks if c.status == STATUS_SKIP),
    }
    overall_ok = summary["error"] == 0
    return HealthcheckResult(ok=overall_ok, checks=checks, summary=summary)
