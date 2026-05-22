"""
scripts/auto_respond.py

Sprint 16 B16.1 - Auto-respond toggle.

Cuando esta activo, TarroBot responde automaticamente a mensajes del chat
que matchen los filtros configurados (mention_only, cooldown por user,
cooldown global, plataformas habilitadas).

El hook se enchufa en social_manager._on_message, despues del persist+broadcast.
Si should_auto_respond(msg) devuelve True, dispara la respuesta via callable
inyectado (tipicamente el endpoint /api/social/respond).
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Callable, Awaitable

# Path canonico
import sys
sys.path.insert(0, str(Path(__file__).parent))
import tarrobot as _t

STATE_PATH = _t.REPO / "data" / "tarrobot-auto-respond.json"


@dataclass
class AutoRespondConfig:
    """Configuracion del modo auto-respond. Persistida en JSON."""
    activo: bool = False
    mention_only: bool = True   # solo si el mensaje menciona a TarroBot
    cooldown_user_s: int = 60    # max 1 respuesta cada N seg al MISMO user
    cooldown_global_s: int = 15  # max 1 respuesta cada N seg en TOTAL
    skip_if_speaking: bool = True  # no auto-responder si TarroBot ya habla
    # Plataformas habilitadas. Vacio = todas.
    platforms: list[str] = field(default_factory=list)


_config: AutoRespondConfig = AutoRespondConfig()
# Runtime state (no persiste)
_last_response_per_user: dict[str, float] = {}
_last_global_response_ts: float = 0.0
_auto_responses_count: int = 0  # contador sesion actual


# ─────────────────────────────────────────────────────────────────────────
# Persistencia
# ─────────────────────────────────────────────────────────────────────────

def load_config() -> AutoRespondConfig:
    """Carga config del JSON si existe. Inicializa con defaults si no."""
    global _config
    if STATE_PATH.exists():
        try:
            data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            _config = AutoRespondConfig(**data)
        except Exception as e:
            print(f"[auto_respond] error cargando config: {e}, usando defaults")
            _config = AutoRespondConfig()
    return _config


def save_config() -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        STATE_PATH.write_text(
            json.dumps(asdict(_config), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[auto_respond] error guardando config: {e}")


def get_config() -> dict:
    return asdict(_config)


def update_config(**kwargs) -> AutoRespondConfig:
    """Actualiza config con kwargs, persiste y devuelve la nueva."""
    global _config
    for k, v in kwargs.items():
        if hasattr(_config, k) and v is not None:
            setattr(_config, k, v)
    save_config()
    return _config


def reset_counters() -> None:
    global _auto_responses_count, _last_global_response_ts, _last_response_per_user
    _auto_responses_count = 0
    _last_global_response_ts = 0.0
    _last_response_per_user.clear()


def status() -> dict:
    """Estado completo: config + counters."""
    return {
        "config": get_config(),
        "auto_responses_count": _auto_responses_count,
        "last_global_response_ts": _last_global_response_ts,
        "tracked_users": len(_last_response_per_user),
    }


# ─────────────────────────────────────────────────────────────────────────
# Decision: should_auto_respond?
# ─────────────────────────────────────────────────────────────────────────

# Variantes de "tarrobot" que Whisper/usuarios suelen escribir
_TARROBOT_PATTERNS = re.compile(
    r"\b(@?tarrobot|@?tarro[\s\-_]?bot|@?taro[\s\-_]?bot|@?retrotarros)\b",
    re.IGNORECASE,
)


def _mentions_tarrobot(text: str) -> bool:
    if not text:
        return False
    return bool(_TARROBOT_PATTERNS.search(text))


def should_auto_respond(msg: dict, is_speaking: bool = False) -> tuple[bool, str]:
    """
    Decide si TarroBot deberia auto-responder a este mensaje.
    Devuelve (True/False, motivo). Motivo es string para debug/logs.
    """
    if not _config.activo:
        return False, "auto-respond OFF"

    if _config.skip_if_speaking and is_speaking:
        return False, "TarroBot esta hablando"

    # Filtro de plataformas
    if _config.platforms:
        platform = msg.get("platform", "")
        if platform not in _config.platforms:
            return False, f"plataforma '{platform}' no habilitada"

    # Mention only
    if _config.mention_only:
        text = msg.get("text", "")
        if not _mentions_tarrobot(text):
            return False, "no menciona a TarroBot"

    # Cooldown global
    now = time.time()
    if (now - _last_global_response_ts) < _config.cooldown_global_s:
        wait = _config.cooldown_global_s - (now - _last_global_response_ts)
        return False, f"cooldown global ({wait:.1f}s restantes)"

    # Cooldown por user (clave: platform:user_id o platform:user_name si no hay id)
    meta = msg.get("meta") or {}
    user_id = meta.get("user_id") or msg.get("user_name", "")
    user_key = f"{msg.get('platform', 'x')}:{user_id}"
    last = _last_response_per_user.get(user_key, 0.0)
    if (now - last) < _config.cooldown_user_s:
        wait = _config.cooldown_user_s - (now - last)
        return False, f"cooldown user ({wait:.1f}s restantes)"

    return True, "OK"


def mark_responded(msg: dict) -> None:
    """Llamar despues de auto-responder para actualizar cooldowns."""
    global _last_global_response_ts, _auto_responses_count
    now = time.time()
    _last_global_response_ts = now
    meta = msg.get("meta") or {}
    user_id = meta.get("user_id") or msg.get("user_name", "")
    user_key = f"{msg.get('platform', 'x')}:{user_id}"
    _last_response_per_user[user_key] = now
    _auto_responses_count += 1


# Init: cargar config al importar el modulo
load_config()


__all__ = [
    "AutoRespondConfig", "load_config", "save_config", "get_config",
    "update_config", "reset_counters", "status",
    "should_auto_respond", "mark_responded",
]
