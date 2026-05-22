"""
scripts/social_manager.py

Orquestador de conectores sociales. Mantiene la lista de conectores
activos, recibe los mensajes que cada uno emite, los persiste en
SQLite via message_store, y los broadcastea por WebSocket a las
pantallas conectadas (panel control + dashboard live).

Sprint 13 - Migracion del Studio Panel Node a Python como modulo de TarroBot.
"""

from __future__ import annotations

import asyncio
from typing import Optional

from connectors import Connector, Message
import message_store


class SocialManager:
    """
    Singleton que vive en el server FastAPI principal (tarrobot-live.py).
    Cada conector le pasa mensajes via on_message; el manager los
    persiste y los emite por WS al frontend.

    Uso tipico desde tarrobot-live.py:
        manager.set_ws_broadcast(callback_async)
        await manager.register(TwitchConnector(channels=["retrotarros"]))
        await manager.register(DiscordConnector(token=..., guild_id=..., channel_ids=[...]))
    """

    def __init__(self):
        self._connectors: list[Connector] = []
        self._ws_broadcast = None  # async callable(message_dict) -> None
        self._current_session_id: Optional[str] = None
        # Sprint 16 B16.1: hook async para auto-respond
        # Tipicamente seteado por tarrobot-live.py al callable que dispara
        # /api/social/respond con el message_id.
        self._auto_respond_handler = None  # async callable(message_dict) -> None

    # ─── lifecycle ───

    async def register(self, connector: Connector) -> None:
        """Registra y arranca un conector."""
        connector._on_message = self._on_message
        self._connectors.append(connector)
        try:
            await connector.start()
        except Exception as e:
            print(f"[social_manager] fallo start de {connector.platform}: {e}")

    async def shutdown(self) -> None:
        """Detiene todos los conectores. Idempotente."""
        for c in self._connectors:
            try:
                await c.stop()
            except Exception as e:
                print(f"[social_manager] error stop {c.platform}: {e}")
        self._connectors.clear()

    # ─── broadcast WS ───

    def set_ws_broadcast(self, callback) -> None:
        """
        callback: async callable(message_dict) que el server FastAPI provee.
        Cada mensaje recibido se broadcastea a todos los clientes WS.
        """
        self._ws_broadcast = callback

    def set_auto_respond_handler(self, callback) -> None:
        """
        Sprint 16 B16.1: hook que se dispara cuando llega un mensaje y
        auto_respond.should_auto_respond() devuelve True.
        callback: async callable(message_dict) -> None
        """
        self._auto_respond_handler = callback

    # ─── pipeline de mensaje entrante ───

    async def _on_message(self, msg: Message) -> None:
        """
        Hook que cada conector llama cuando recibe un mensaje. Pipeline:
          1. Etiquetar con la sesion de stream activa (si hay)
          2. Persistir en SQLite
          3. Broadcast por WS a clientes
        """
        # Anclaje a sesion actual
        if not msg.stream_session_id:
            sess = message_store.current_session()
            if sess:
                msg.stream_session_id = sess["id"]

        # Persistir
        try:
            await asyncio.to_thread(message_store.save_message, msg)
        except Exception as e:
            print(f"[social_manager] error save_message: {e}")

        # Broadcast
        if self._ws_broadcast:
            try:
                await self._ws_broadcast({
                    "tipo": "social-message",
                    "message": msg.to_dict(),
                })
            except Exception as e:
                print(f"[social_manager] error ws_broadcast: {e}")

        # Sprint 16 B16.1: auto-respond hook
        if self._auto_respond_handler:
            try:
                await self._auto_respond_handler(msg.to_dict())
            except Exception as e:
                print(f"[social_manager] error auto_respond_handler: {e}")

    # ─── consulta ───

    def status(self) -> dict:
        sess = message_store.current_session()
        return {
            "connectors": [c.get_status() for c in self._connectors],
            "current_session": sess,
            "message_counts": message_store.message_count(
                sess["id"] if sess else None
            ),
        }

    def list_connectors(self) -> list[Connector]:
        return list(self._connectors)

    def find_connector(self, platform: str) -> Optional[Connector]:
        for c in self._connectors:
            if c.platform == platform:
                return c
        return None


# Singleton modulo
manager = SocialManager()


__all__ = ["SocialManager", "manager"]
