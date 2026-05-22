"""
scripts/message_store.py

Persistencia local en SQLite de mensajes del chat multi-plataforma
(Twitch, Discord, YouTube, etc) y sesiones de stream. Reemplaza el
backend Supabase del Studio Panel original con almacenamiento 100% local
para mantener la filosofia TarroBot (todo corre en el PC del estudio).

Schema:
  - streams: una fila por cada sesion de stream/podcast.
  - messages: una fila por cada mensaje recibido. FK a streams si se
    capturo durante una sesion activa.

Sprint 13 - Migracion del Studio Panel Node a Python como modulo de TarroBot.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Optional

# Reusar la ubicacion canonica del repo (DATA_DIR = repo/data)
import sys
sys.path.insert(0, str(Path(__file__).parent))
import tarrobot as _t
DB_PATH = _t.REPO / "data" / "tarrobot-messages.db"


# ─────────────────────────────────────────────────────────────────────────
# Schema SQL
# ─────────────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS streams (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL,
    title TEXT,
    started_ts_ms INTEGER NOT NULL,
    ended_ts_ms INTEGER,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_streams_started ON streams(started_ts_ms DESC);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    channel TEXT NOT NULL,
    user_name TEXT NOT NULL,
    user_avatar TEXT,
    user_badge TEXT,
    text TEXT NOT NULL,
    timestamp_ms INTEGER NOT NULL,
    pinned INTEGER NOT NULL DEFAULT 0,
    replied INTEGER NOT NULL DEFAULT 0,
    slide_id TEXT,
    stream_session_id TEXT,
    meta TEXT,                -- JSON serializado
    FOREIGN KEY(stream_session_id) REFERENCES streams(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(stream_session_id, timestamp_ms);
CREATE INDEX IF NOT EXISTS idx_messages_platform ON messages(platform, timestamp_ms DESC);
CREATE INDEX IF NOT EXISTS idx_messages_pinned ON messages(pinned, timestamp_ms DESC);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp_ms DESC);
"""


# ─────────────────────────────────────────────────────────────────────────
# Conexion + setup
# ─────────────────────────────────────────────────────────────────────────

_conn: Optional[sqlite3.Connection] = None


def get_conn() -> sqlite3.Connection:
    """
    Devuelve la conexion SQLite singleton. Crea la DB si no existe y aplica
    el schema. Thread-safe con check_same_thread=False (FastAPI async).
    """
    global _conn
    if _conn is not None:
        return _conn
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    _conn = sqlite3.connect(
        str(DB_PATH),
        check_same_thread=False,
        isolation_level=None,  # autocommit
    )
    _conn.row_factory = sqlite3.Row
    _conn.execute("PRAGMA foreign_keys = ON;")
    _conn.execute("PRAGMA journal_mode = WAL;")  # mejor para concurrencia
    _conn.executescript(SCHEMA_SQL)
    return _conn


def close_conn() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


# ─────────────────────────────────────────────────────────────────────────
# CRUD mensajes
# ─────────────────────────────────────────────────────────────────────────

def save_message(msg: "Message") -> None:  # noqa: F821
    """Persiste un Message. Idempotente por id."""
    conn = get_conn()
    conn.execute(
        """
        INSERT OR REPLACE INTO messages
        (id, platform, channel, user_name, user_avatar, user_badge, text,
         timestamp_ms, pinned, replied, slide_id, stream_session_id, meta)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            msg.id, msg.platform, msg.channel, msg.user_name,
            msg.user_avatar, msg.user_badge, msg.text, msg.timestamp_ms,
            1 if msg.pinned else 0, 1 if msg.replied else 0,
            msg.slide_id, msg.stream_session_id,
            json.dumps(msg.meta, ensure_ascii=False) if msg.meta else None,
        ),
    )


def get_recent(limit: int = 100, platform: Optional[str] = None,
               session_id: Optional[str] = None) -> list[dict]:
    """Devuelve los mensajes mas recientes. Opcionalmente filtrado."""
    conn = get_conn()
    sql = "SELECT * FROM messages"
    params: list = []
    where = []
    if platform:
        where.append("platform = ?")
        params.append(platform)
    if session_id:
        where.append("stream_session_id = ?")
        params.append(session_id)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY timestamp_ms DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_pinned(session_id: Optional[str] = None) -> list[dict]:
    """Devuelve mensajes pinned, opcionalmente filtrados por sesion."""
    conn = get_conn()
    if session_id:
        rows = conn.execute(
            "SELECT * FROM messages WHERE pinned=1 AND stream_session_id=? "
            "ORDER BY timestamp_ms ASC",
            (session_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM messages WHERE pinned=1 ORDER BY timestamp_ms DESC LIMIT 100"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def set_pinned(message_id: str, pinned: bool) -> bool:
    """Marca/desmarca un mensaje como pinned. Devuelve True si se actualizo."""
    conn = get_conn()
    cur = conn.execute(
        "UPDATE messages SET pinned=? WHERE id=?",
        (1 if pinned else 0, message_id),
    )
    return cur.rowcount > 0


def set_replied(message_id: str, replied: bool) -> bool:
    conn = get_conn()
    cur = conn.execute(
        "UPDATE messages SET replied=? WHERE id=?",
        (1 if replied else 0, message_id),
    )
    return cur.rowcount > 0


def message_count(session_id: Optional[str] = None) -> dict:
    """Conteo de mensajes por plataforma."""
    conn = get_conn()
    sql = "SELECT platform, COUNT(*) as c FROM messages"
    params: list = []
    if session_id:
        sql += " WHERE stream_session_id=?"
        params.append(session_id)
    sql += " GROUP BY platform"
    rows = conn.execute(sql, params).fetchall()
    return {r["platform"]: r["c"] for r in rows}


# ─────────────────────────────────────────────────────────────────────────
# CRUD sesiones de stream
# ─────────────────────────────────────────────────────────────────────────

def start_stream_session(slug: str, title: Optional[str] = None) -> dict:
    """
    Inicia una nueva sesion de stream. Si hay una abierta (sin ended_ts_ms)
    la cierra primero. Devuelve la sesion nueva como dict.
    """
    conn = get_conn()
    now_ms = int(time.time() * 1000)
    # Cerrar sesion abierta si existe
    conn.execute(
        "UPDATE streams SET ended_ts_ms=? WHERE ended_ts_ms IS NULL",
        (now_ms,),
    )
    session_id = uuid.uuid4().hex
    conn.execute(
        "INSERT INTO streams (id, slug, title, started_ts_ms) VALUES (?, ?, ?, ?)",
        (session_id, slug, title, now_ms),
    )
    return {
        "id": session_id, "slug": slug, "title": title,
        "started_ts_ms": now_ms, "ended_ts_ms": None,
    }


def end_stream_session(session_id: str, notes: Optional[str] = None) -> bool:
    conn = get_conn()
    now_ms = int(time.time() * 1000)
    cur = conn.execute(
        "UPDATE streams SET ended_ts_ms=?, notes=? WHERE id=? AND ended_ts_ms IS NULL",
        (now_ms, notes, session_id),
    )
    return cur.rowcount > 0


def current_session() -> Optional[dict]:
    """Devuelve la sesion activa (sin ended_ts_ms), o None."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM streams WHERE ended_ts_ms IS NULL "
        "ORDER BY started_ts_ms DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None


def recent_sessions(limit: int = 10) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM streams ORDER BY started_ts_ms DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────────────────
# Internals
# ─────────────────────────────────────────────────────────────────────────

def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    # bool helpers
    d["pinned"] = bool(d.get("pinned"))
    d["replied"] = bool(d.get("replied"))
    # parsear meta JSON
    meta_raw = d.pop("meta", None)
    if meta_raw:
        try:
            d["meta"] = json.loads(meta_raw)
        except Exception:
            d["meta"] = {}
    else:
        d["meta"] = {}
    return d


__all__ = [
    "DB_PATH", "get_conn", "close_conn",
    "save_message", "get_recent", "get_pinned",
    "set_pinned", "set_replied", "message_count",
    "start_stream_session", "end_stream_session",
    "current_session", "recent_sessions",
]
