"""
scripts/connectors/twitch.py

Conector Twitch IRC con autenticacion anonima (justinfan). Solo lectura
de chat publico de canales especificados. No requiere registro de bot ni
OAuth - usa el flujo Anonymous chat que Twitch expone via IRC.

Decisiones:
  - Implementacion directa con asyncio.open_connection (no usamos
    twitchio porque sus deps son pesadas y solo necesitamos READ).
  - Reconnect automatico con backoff exponencial.
  - Parser simple de IRC + tags (Twitch extiende IRC con metadatos:
    user-id, color, badges, emotes, etc).

Sprint 13 - Migracion del Studio Panel Node a Python como modulo de TarroBot.
"""

from __future__ import annotations

import asyncio
import random
import re
import time
from typing import Optional

from . import Connector, Message


# Servidor Twitch IRC con SSL
TWITCH_IRC_HOST = "irc.chat.twitch.tv"
TWITCH_IRC_PORT_SSL = 6697

# Capabilities que pedimos para tener tags + comandos extendidos
TWITCH_CAPS = "twitch.tv/tags twitch.tv/commands twitch.tv/membership"

# Backoff de reconexion (segundos)
RECONNECT_BACKOFF_INITIAL = 2.0
RECONNECT_BACKOFF_MAX = 60.0


class TwitchConnector(Connector):
    """
    Conector de Twitch IRC. Configurable con una lista de canales a
    escuchar. No requiere credenciales (usa anonymous justinfan).

    Ejemplo:
        conn = TwitchConnector(channels=["retrotarros"])
        await manager.register(conn)
    """

    platform = "twitch"

    def __init__(self, channels: list[str], on_message=None):
        super().__init__(on_message=on_message)
        # Normalizar nombres de canales: sin # adelante, minusculas
        self.channels = [self._normalize_channel(c) for c in channels]
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._stop_event = asyncio.Event()
        self._backoff = RECONNECT_BACKOFF_INITIAL

    @staticmethod
    def _normalize_channel(ch: str) -> str:
        ch = ch.strip().lower()
        if ch.startswith("#"):
            ch = ch[1:]
        return ch

    # ─── lifecycle ───

    async def start(self) -> None:
        if self._task and not self._task.done():
            return  # ya esta corriendo
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_loop(), name=f"twitch-connector-{','.join(self.channels)}")

    async def stop(self) -> None:
        self._stop_event.set()
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
        self._set_connected(False)

    # ─── loop principal ───

    async def _run_loop(self) -> None:
        """Loop con reconexion automatica + backoff exponencial."""
        while not self._stop_event.is_set():
            try:
                await self._connect_and_listen()
                # Si salimos sin excepcion, fue desconexion normal
                self._set_connected(False, "desconexion normal")
            except asyncio.CancelledError:
                break
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
                print(f"[twitch] error en loop: {err}")
                self._set_connected(False, err)

            if self._stop_event.is_set():
                break

            # Backoff con jitter
            wait = self._backoff + random.uniform(0, 1.0)
            print(f"[twitch] reconectando en {wait:.1f}s...")
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=wait)
                break  # stop pedido
            except asyncio.TimeoutError:
                pass  # timeout = continuar reconectando
            self._backoff = min(self._backoff * 2, RECONNECT_BACKOFF_MAX)

    async def _connect_and_listen(self) -> None:
        """Una iteracion: conectar, autenticar, unirse a canales, leer mensajes."""
        # Anonymous user: nick `justinfan<random>` no requiere PASS
        anon_nick = f"justinfan{random.randint(10000, 99999)}"

        print(f"[twitch] conectando a {TWITCH_IRC_HOST}:{TWITCH_IRC_PORT_SSL} (anon {anon_nick})...")
        reader, writer = await asyncio.open_connection(
            TWITCH_IRC_HOST, TWITCH_IRC_PORT_SSL, ssl=True
        )
        self._reader = reader
        self._writer = writer

        # Pedir capabilities + identificar como anon
        await self._send(f"CAP REQ :{TWITCH_CAPS}")
        await self._send(f"NICK {anon_nick}")

        # Esperar a que el server confirme conexion (PING o 001 welcome)
        ready = False
        joined = False
        async for line in self._iter_lines(timeout=15.0):
            if line.startswith("PING"):
                await self._send(line.replace("PING", "PONG", 1))
            if " 001 " in line or " 376 " in line or "GLOBALUSERSTATE" in line:
                ready = True
                # Unirse a todos los canales
                for ch in self.channels:
                    await self._send(f"JOIN #{ch}")
                joined = True
                break
            if line.startswith("CAP * ACK"):
                # ack de capabilities recibido
                pass

        if not ready:
            raise RuntimeError("Twitch no respondio con welcome a tiempo")
        if not joined:
            raise RuntimeError("No se pudo unir a los canales")

        # Marcado como conectado
        self._set_connected(True)
        self._backoff = RECONNECT_BACKOFF_INITIAL  # reset backoff
        print(f"[twitch] conectado a #{', #'.join(self.channels)}")

        # Loop de mensajes
        async for line in self._iter_lines():
            await self._handle_line(line)

    async def _iter_lines(self, timeout: Optional[float] = None):
        """Generador de lineas del IRC. timeout None = sin timeout."""
        while True:
            try:
                if timeout:
                    raw = await asyncio.wait_for(
                        self._reader.readline(), timeout=timeout
                    )
                else:
                    raw = await self._reader.readline()
            except asyncio.TimeoutError:
                raise
            if not raw:
                # EOF - server cerro
                raise ConnectionError("Twitch IRC cerro la conexion")
            line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            if not line:
                continue
            yield line

    async def _send(self, line: str) -> None:
        if not self._writer:
            return
        self._writer.write((line + "\r\n").encode("utf-8"))
        await self._writer.drain()

    # ─── parser de mensajes IRC con tags Twitch ───

    async def _handle_line(self, line: str) -> None:
        """Parsea una linea IRC y emite Message si es PRIVMSG."""
        # PING keepalive
        if line.startswith("PING"):
            await self._send(line.replace("PING", "PONG", 1))
            return

        # Formato Twitch con tags:
        #   @tag1=value1;tag2=value2 :user!user@user.tmi.twitch.tv PRIVMSG #channel :mensaje
        tags = {}
        rest = line
        if line.startswith("@"):
            tag_part, rest = line[1:].split(" ", 1)
            for kv in tag_part.split(";"):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    tags[k] = v
                else:
                    tags[kv] = ""

        # Detectar PRIVMSG
        if " PRIVMSG " not in rest:
            return

        # Parse: :user!user@user.tmi.twitch.tv PRIVMSG #channel :mensaje
        m = re.match(
            r"^:([^!]+)![^ ]+ PRIVMSG #([^ ]+) :(.*)$",
            rest,
        )
        if not m:
            return
        user_login = m.group(1)
        channel = m.group(2)
        text = m.group(3)

        # display-name del tag (puede tener mayusculas, login no)
        display = tags.get("display-name") or user_login
        badges = tags.get("badges", "")
        primary_badge = self._primary_badge(badges)
        msg_id = tags.get("id") or f"twitch-{int(time.time()*1000)}-{random.randint(0,9999)}"

        msg = Message(
            id=msg_id,
            platform="twitch",
            channel=channel,
            user_name=display,
            text=text,
            timestamp_ms=Message.now_ms(),
            user_avatar=None,  # Twitch IRC no expone avatar
            user_badge=primary_badge,
            meta={
                "user_login": user_login,
                "user_id": tags.get("user-id"),
                "color": tags.get("color"),
                "badges": badges,
                "emotes": tags.get("emotes"),
                "is_subscriber": tags.get("subscriber") == "1",
                "is_moderator": tags.get("mod") == "1",
                "is_first_message": tags.get("first-msg") == "1",
            },
        )
        await self._emit(msg)

    @staticmethod
    def _primary_badge(badges_str: str) -> Optional[str]:
        """De 'broadcaster/1,subscriber/12,premium/1' extrae el badge mas relevante."""
        if not badges_str:
            return None
        priority = ["broadcaster", "moderator", "vip", "subscriber", "premium"]
        present = [b.split("/")[0] for b in badges_str.split(",")]
        for p in priority:
            if p in present:
                return p
        return present[0] if present else None


__all__ = ["TwitchConnector"]
