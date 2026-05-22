"""
scripts/connectors/youtube.py

Conector YouTube Live Chat usando Data API v3 con API key (read-only).
NO requiere OAuth porque solo lee el chat publico de un stream activo.

Flujo:
  1. Resolver liveChatId desde YOUTUBE_VIDEO_ID via /videos?part=liveStreamingDetails
  2. Loop polling /liveChat/messages respetando pollingIntervalMillis (5-30s)
  3. Por cada mensaje nuevo: emit Message via _emit (parent class)

Setup previo:
  - Crear API key en https://console.cloud.google.com (proyecto + YouTube Data API v3 habilitada)
  - Variables de entorno:
      YOUTUBE_API_KEY=AIza...
      YOUTUBE_VIDEO_ID=<id del stream activo>  (puede cambiarse por endpoint cuando arranca live)

Decisiones:
  - urllib.request en lugar de google-api-python-client (cero deps extra,
    el endpoint es simple). asyncio.to_thread para no bloquear.
  - El liveChatId se resuelve al start() y se cachea.
  - Si el stream termina, la API devuelve "live chat ended" y el conector
    se marca como desconectado (no reintenta).
  - El video_id se puede cambiar via set_video_id() sin recrear el conector.

Sprint 13 - Migracion del Studio Panel Node a Python como modulo de TarroBot.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import urllib.parse
import urllib.request
from typing import Optional

from . import Connector, Message


YT_API_BASE = "https://www.googleapis.com/youtube/v3"
DEFAULT_POLL_MS = 5000     # default si la API no nos dice
MIN_POLL_MS = 2000         # nunca pollear mas seguido que esto
MAX_POLL_MS = 30000        # cap superior


class YouTubeConnector(Connector):
    """
    Conector YouTube Live Chat.

    Ejemplo:
        conn = YouTubeConnector(api_key=..., video_id=...)
        await manager.register(conn)
    """

    platform = "youtube"

    def __init__(self, api_key: str, video_id: Optional[str] = None, on_message=None):
        super().__init__(on_message=on_message)
        self.api_key = api_key
        self.video_id = video_id
        self.live_chat_id: Optional[str] = None
        self._next_page_token: Optional[str] = None
        self._poll_interval_ms = DEFAULT_POLL_MS
        self._stop_event = asyncio.Event()
        # set de message ids vistos para evitar duplicar (la API a veces
        # repite mensajes en bordes de paginas)
        self._seen_ids: set[str] = set()

    # ─── lifecycle ───

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        if not self.video_id:
            self._set_connected(False, "falta YOUTUBE_VIDEO_ID")
            print("[youtube] no hay video_id configurado, no arranco")
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_loop(), name="youtube-connector")

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
        self._set_connected(False)

    def set_video_id(self, video_id: str) -> None:
        """Cambia el video objetivo. Requiere stop + start para tomar efecto."""
        self.video_id = video_id
        self.live_chat_id = None
        self._next_page_token = None
        self._seen_ids.clear()

    # ─── loop principal ───

    async def _run_loop(self) -> None:
        """Loop: resolver liveChatId, despues polling de mensajes."""
        try:
            await self._resolve_live_chat_id()
        except Exception as e:
            err = f"resolve_live_chat_id fallo: {e}"
            print(f"[youtube] {err}")
            self._set_connected(False, err)
            return

        if not self.live_chat_id:
            self._set_connected(False, "video sin live chat activo")
            print(f"[youtube] video {self.video_id} no tiene live chat activo")
            return

        self._set_connected(True)
        print(f"[youtube] conectado · video={self.video_id} · liveChatId={self.live_chat_id[:20]}...")

        while not self._stop_event.is_set():
            try:
                ended = await self._poll_once()
                if ended:
                    print("[youtube] live chat terminado por YouTube")
                    self._set_connected(False, "live ended")
                    break
            except Exception as e:
                err = f"poll error: {e}"
                print(f"[youtube] {err}")
                self._set_connected(False, err)
                # Backoff antes de reintentar
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=10.0)
                    break
                except asyncio.TimeoutError:
                    pass
                self._set_connected(True)
                continue

            # Esperar el intervalo que la API pide (clamped)
            interval_sec = max(MIN_POLL_MS, min(self._poll_interval_ms, MAX_POLL_MS)) / 1000.0
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=interval_sec)
                break  # stop pedido
            except asyncio.TimeoutError:
                pass  # timeout = seguir polling

    # ─── HTTP helpers ───

    async def _http_get_json(self, url: str) -> dict:
        """GET con json response. Usa to_thread para no bloquear."""
        def _do():
            req = urllib.request.Request(url, headers={"User-Agent": "TarroBot/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                return json.loads(resp.read().decode("utf-8"))
        return await asyncio.to_thread(_do)

    async def _resolve_live_chat_id(self) -> None:
        """Llama videos.list para sacar liveStreamingDetails.activeLiveChatId."""
        params = {
            "part": "liveStreamingDetails",
            "id": self.video_id,
            "key": self.api_key,
        }
        url = f"{YT_API_BASE}/videos?{urllib.parse.urlencode(params)}"
        data = await self._http_get_json(url)
        items = data.get("items", [])
        if not items:
            raise RuntimeError(f"video {self.video_id} no encontrado")
        lsd = items[0].get("liveStreamingDetails", {})
        self.live_chat_id = lsd.get("activeLiveChatId")
        # si no esta activo, dejamos live_chat_id en None (loop sale)

    async def _poll_once(self) -> bool:
        """Trae la siguiente pagina. Retorna True si el chat termino."""
        params = {
            "liveChatId": self.live_chat_id,
            "part": "snippet,authorDetails",
            "key": self.api_key,
        }
        if self._next_page_token:
            params["pageToken"] = self._next_page_token
        url = f"{YT_API_BASE}/liveChat/messages?{urllib.parse.urlencode(params)}"

        try:
            data = await self._http_get_json(url)
        except urllib.error.HTTPError as e:
            # 403 = quota exceeded o key invalida
            # 404 = chat ended
            if e.code == 404:
                return True  # live ended
            raise

        # Actualizar pagina + intervalo
        self._next_page_token = data.get("nextPageToken")
        if "pollingIntervalMillis" in data:
            try:
                self._poll_interval_ms = int(data["pollingIntervalMillis"])
            except (TypeError, ValueError):
                pass

        # Procesar items
        for item in data.get("items", []):
            await self._handle_yt_message(item)

        # Si la API devuelve isLiveEnded explicito
        offline = data.get("offlineAt")
        if offline:
            return True
        return False

    async def _handle_yt_message(self, item: dict) -> None:
        """Convierte un item de live chat API a Message normalizado."""
        msg_id = item.get("id")
        if not msg_id or msg_id in self._seen_ids:
            return
        self._seen_ids.add(msg_id)
        # mantener el set acotado
        if len(self._seen_ids) > 1000:
            # mantener solo los ultimos 500
            self._seen_ids = set(list(self._seen_ids)[-500:])

        snippet = item.get("snippet", {}) or {}
        author = item.get("authorDetails", {}) or {}

        # YouTube no expone text para todos los tipos (super chat, gift, etc).
        # Para mensajes de texto normal: textMessageDetails.messageText.
        text = (
            snippet.get("textMessageDetails", {}).get("messageText")
            or snippet.get("displayMessage")
            or ""
        )
        if not text:
            # Skip mensajes sin texto (eventos como sub, ban, etc)
            return

        # Badge prioritizado
        badge = None
        if author.get("isChatOwner"):
            badge = "broadcaster"
        elif author.get("isChatModerator"):
            badge = "moderator"
        elif author.get("isChatSponsor"):
            badge = "sponsor"  # YouTube member

        # Timestamp
        publish_iso = snippet.get("publishedAt", "")
        try:
            from datetime import datetime
            ts = int(datetime.fromisoformat(publish_iso.replace("Z", "+00:00")).timestamp() * 1000)
        except Exception:
            ts = Message.now_ms()

        msg = Message(
            id=f"youtube-{msg_id}",
            platform="youtube",
            channel=self.video_id or "?",
            user_name=author.get("displayName") or "?",
            text=text,
            timestamp_ms=ts,
            user_avatar=author.get("profileImageUrl"),
            user_badge=badge,
            meta={
                "channel_id": author.get("channelId"),
                "channel_url": author.get("channelUrl"),
                "is_verified": author.get("isVerified", False),
                "is_chat_owner": author.get("isChatOwner", False),
                "is_chat_moderator": author.get("isChatModerator", False),
                "is_chat_sponsor": author.get("isChatSponsor", False),
                "yt_message_type": snippet.get("type"),
            },
        )
        await self._emit(msg)


# ─────────────────────────────────────────────────────────────────────────
# Factory desde env vars
# ─────────────────────────────────────────────────────────────────────────

def from_env() -> Optional[YouTubeConnector]:
    """
    Construye YouTubeConnector leyendo YOUTUBE_API_KEY + YOUTUBE_VIDEO_ID.
    Devuelve None si falta la api key (no se puede arrancar sin ella).
    Si falta video_id, devuelve un conector que start() va a fallar limpio.
    """
    api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        return None
    video_id = os.environ.get("YOUTUBE_VIDEO_ID", "").strip() or None
    return YouTubeConnector(api_key=api_key, video_id=video_id)


__all__ = ["YouTubeConnector", "from_env"]
