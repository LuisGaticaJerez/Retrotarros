"""
scripts/connectors/__init__.py

Interface comun para todos los conectores de plataformas sociales que el
TarroBot Studio Panel agrega. Cada plataforma (Twitch, Discord, YouTube,
SSN bridge) implementa la clase abstracta Connector y emite Messages
normalizados via la cola asincrona del SocialManager.

Sprint 13 - Migracion del Studio Panel Node a Python como modulo de TarroBot.
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable, Awaitable


# ─────────────────────────────────────────────────────────────────────────
# Mensaje normalizado
# ─────────────────────────────────────────────────────────────────────────

@dataclass
class Message:
    """
    Mensaje normalizado que cualquier conector emite. Se persiste en SQLite
    y se broadcastea por WebSocket al dashboard.

    El schema es deliberadamente plano para simplificar el storage y la UI.
    Campos extra especificos de plataforma van en `meta` (dict serializable).
    """
    id: str                              # identificador unico (uuid o id de plataforma)
    platform: str                        # 'twitch' | 'discord' | 'youtube' | 'ssn-instagram' | ...
    channel: str                         # nombre del canal/chat de origen
    user_name: str                       # display name del autor
    text: str                            # contenido del mensaje
    timestamp_ms: int                    # timestamp unix en ms (cliente: receive)
    user_avatar: Optional[str] = None    # URL del avatar si la plataforma lo expone
    user_badge: Optional[str] = None     # ej: mod, sub, vip, owner
    pinned: bool = False                 # marcado por el operador via panel
    replied: bool = False                # ya fue respondido on-air
    slide_id: Optional[str] = None       # slug del slide HTML activo cuando llego
    stream_session_id: Optional[str] = None  # sesion de stream actual
    meta: dict = field(default_factory=dict)  # campos extra por plataforma

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def now_ms() -> int:
        return int(time.time() * 1000)


# ─────────────────────────────────────────────────────────────────────────
# Conector base (abstracto)
# ─────────────────────────────────────────────────────────────────────────

class Connector(ABC):
    """
    Clase base de todos los conectores. Cada implementacion concreta debe:
      - Implementar start(), stop(), is_connected(), get_status()
      - Llamar self._emit(message) cuando recibe un mensaje nuevo.

    El SocialManager registra los conectores activos y maneja la cola.
    """

    platform: str = "unknown"

    def __init__(self, on_message: Optional[Callable[[Message], Awaitable[None]]] = None):
        """
        on_message: callable async que el SocialManager pasa al construir el
        conector. Se llama una vez por cada mensaje recibido.
        """
        self._on_message = on_message
        self._connected: bool = False
        self._last_error: Optional[str] = None
        self._connect_ts: Optional[float] = None
        self._messages_received: int = 0
        self._task: Optional[asyncio.Task] = None

    @abstractmethod
    async def start(self) -> None:
        """Inicia la conexion. Debe ser idempotente."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Cierra la conexion. Debe ser idempotente."""
        ...

    def is_connected(self) -> bool:
        return self._connected

    def get_status(self) -> dict:
        return {
            "platform": self.platform,
            "connected": self._connected,
            "last_error": self._last_error,
            "connected_since_ts": self._connect_ts,
            "messages_received": self._messages_received,
        }

    async def _emit(self, message: Message) -> None:
        """Helper interno: el conector lo llama cuando recibe un mensaje."""
        self._messages_received += 1
        if self._on_message:
            try:
                await self._on_message(message)
            except Exception as e:
                print(f"[{self.platform}] error en on_message handler: {e}")

    def _set_connected(self, connected: bool, error: Optional[str] = None) -> None:
        self._connected = connected
        self._last_error = error
        if connected and self._connect_ts is None:
            self._connect_ts = time.time()
        elif not connected:
            self._connect_ts = None


__all__ = ["Message", "Connector"]
