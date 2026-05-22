"""
scripts/connectors/discord_conn.py

Conector Discord usando discord.py. Bot reader que se conecta al servidor
de Discord especificado y escucha mensajes en los canales configurados.

Setup previo (ver docs/discord-bot-setup.md):
  - App Discord creada con Privileged Gateway Intents activados
    (Presence + Server Members + Message Content)
  - Bot invitado al servidor con permisos lector/reactor
  - Variables de entorno en el .env:
      DISCORD_BOT_TOKEN=<token>
      DISCORD_GUILD_ID=<guild id>
      DISCORD_CHANNEL_IDS=id1,id2,id3  (comma-separated)

Sprint 13 - Migracion del Studio Panel Node a Python como modulo de TarroBot.
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Optional

from . import Connector, Message

try:
    import discord
    _DISCORD_AVAILABLE = True
except ImportError:
    discord = None
    _DISCORD_AVAILABLE = False


class DiscordConnector(Connector):
    """
    Conector Discord. Bot reader.

    Ejemplo:
        conn = DiscordConnector(
            token=os.environ['DISCORD_BOT_TOKEN'],
            guild_id=int(os.environ['DISCORD_GUILD_ID']),
            channel_ids=[int(x) for x in os.environ['DISCORD_CHANNEL_IDS'].split(',')],
        )
        await manager.register(conn)
    """

    platform = "discord"

    def __init__(self, token: str, guild_id: int,
                 channel_ids: Optional[list[int]] = None, on_message=None):
        super().__init__(on_message=on_message)
        if not _DISCORD_AVAILABLE:
            raise ImportError(
                "Falta 'discord.py'. Instalalo con: pip install discord.py"
            )
        self.token = token
        self.guild_id = int(guild_id)
        # None o lista vacia = escuchar TODOS los canales del guild
        self.channel_ids = set(int(c) for c in (channel_ids or []))
        self._client: Optional[discord.Client] = None

    # ─── lifecycle ───

    async def start(self) -> None:
        if self._task and not self._task.done():
            return

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        self._client = discord.Client(intents=intents)

        # Hooks - ver setup_hooks abajo
        self._setup_hooks(self._client)

        # Correr en background task
        self._task = asyncio.create_task(
            self._run_client(),
            name="discord-connector",
        )

    async def stop(self) -> None:
        if self._client:
            try:
                await self._client.close()
            except Exception:
                pass
            self._client = None
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
        self._set_connected(False)

    # ─── client ───

    async def _run_client(self) -> None:
        """Loop principal del cliente discord.py."""
        try:
            await self._client.start(self.token, reconnect=True)
        except discord.LoginFailure as e:
            self._set_connected(False, f"login failure: {e}")
            print(f"[discord] LoginFailure (token invalido?): {e}")
        except Exception as e:
            self._set_connected(False, f"{type(e).__name__}: {e}")
            print(f"[discord] error: {e}")

    def _setup_hooks(self, client) -> None:
        """Registra event handlers via decorators sobre el client."""

        @client.event
        async def on_ready():
            self._set_connected(True)
            user = client.user
            guild = client.get_guild(self.guild_id)
            guild_name = guild.name if guild else "?"
            channels_str = (
                ", ".join(f"#{c.name}" for c in guild.text_channels
                          if not self.channel_ids or c.id in self.channel_ids)
                if guild else "?"
            )
            print(f"[discord] Bot conectado como {user} (id={user.id})")
            print(f"[discord] Watching guild '{guild_name}' (ID: {self.guild_id})")
            print(f"[discord] Listening to: {channels_str}")

        @client.event
        async def on_disconnect():
            self._set_connected(False, "disconnected")
            print("[discord] disconnected")

        @client.event
        async def on_resumed():
            self._set_connected(True)
            print("[discord] session resumed")

        @client.event
        async def on_message(msg):
            # Ignorar mensajes de bots (incluido el propio bot)
            if msg.author.bot:
                return
            # Filtrar por guild (no escuchar DMs ni otros servers)
            if msg.guild is None or msg.guild.id != self.guild_id:
                return
            # Filtrar por canales especificos si hay lista
            if self.channel_ids and msg.channel.id not in self.channel_ids:
                return

            normalized = self._to_message(msg)
            await self._emit(normalized)

    async def send_to_channel(self, channel_id: int, text: str) -> None:
        """
        Sprint 14: TarroBot escribe en un canal Discord (write-back).
        Lanza ValueError si el canal no se encuentra o si el bot no tiene
        permisos para escribir.
        """
        if not self._client or not self.is_connected():
            raise RuntimeError("Discord no esta conectado")
        channel = self._client.get_channel(int(channel_id))
        if channel is None:
            # Intentar fetch (puede ser canal de un guild que no esta cacheado)
            try:
                channel = await self._client.fetch_channel(int(channel_id))
            except Exception as e:
                raise ValueError(f"canal {channel_id} no encontrado: {e}")
        # Trimear a 2000 chars (limite Discord)
        if len(text) > 2000:
            text = text[:1997] + "..."
        try:
            await channel.send(text)
        except Exception as e:
            raise RuntimeError(f"fallo send a canal {channel_id}: {e}")

    def _to_message(self, msg) -> Message:
        """Convierte un discord.Message a nuestro Message normalizado."""
        author = msg.author
        avatar_url = None
        try:
            avatar_url = str(author.display_avatar.url) if author.display_avatar else None
        except Exception:
            pass

        # Badge: si es owner del guild o admin, lo etiquetamos
        badge = None
        try:
            if author.id == msg.guild.owner_id:
                badge = "owner"
            elif any(r.permissions.administrator for r in author.roles if hasattr(r, "permissions")):
                badge = "admin"
        except Exception:
            pass

        return Message(
            id=f"discord-{msg.id}",
            platform="discord",
            channel=msg.channel.name,
            user_name=author.display_name or author.name,
            text=msg.content,
            timestamp_ms=int(msg.created_at.timestamp() * 1000),
            user_avatar=avatar_url,
            user_badge=badge,
            meta={
                "user_id": str(author.id),
                "user_login": author.name,
                "channel_id": str(msg.channel.id),
                "guild_id": str(msg.guild.id) if msg.guild else None,
                "has_attachments": len(msg.attachments) > 0,
                "is_pinned_in_discord": msg.pinned,
                "mentions": [str(u.id) for u in msg.mentions],
            },
        )


# ─────────────────────────────────────────────────────────────────────────
# Factory desde env vars
# ─────────────────────────────────────────────────────────────────────────

def from_env() -> Optional[DiscordConnector]:
    """
    Construye un DiscordConnector leyendo de variables de entorno:
      DISCORD_BOT_TOKEN
      DISCORD_GUILD_ID
      DISCORD_CHANNEL_IDS (comma-separated, opcional)

    Devuelve None si falta el token o no esta discord.py instalado.
    Asi tarrobot-live.py puede llamar from_env() sin abortar si Luis no
    configuro Discord.
    """
    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        return None
    if not _DISCORD_AVAILABLE:
        print("[discord] discord.py no instalada, saltando conector Discord")
        return None
    guild_id_raw = os.environ.get("DISCORD_GUILD_ID", "").strip()
    if not guild_id_raw:
        print("[discord] falta DISCORD_GUILD_ID, saltando")
        return None
    try:
        guild_id = int(guild_id_raw)
    except ValueError:
        print(f"[discord] DISCORD_GUILD_ID no es numero: '{guild_id_raw}'")
        return None
    channel_ids_raw = os.environ.get("DISCORD_CHANNEL_IDS", "").strip()
    channel_ids = []
    if channel_ids_raw:
        for x in channel_ids_raw.split(","):
            x = x.strip()
            if x:
                try:
                    channel_ids.append(int(x))
                except ValueError:
                    print(f"[discord] channel id invalido: '{x}'")
    return DiscordConnector(token=token, guild_id=guild_id, channel_ids=channel_ids)


__all__ = ["DiscordConnector", "from_env"]
