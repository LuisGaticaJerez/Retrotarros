"""
scripts/llm_resolver.py

Sprint 15 - Estrategia de minimizar gasto LLM.

Antes de llamar a Claude, los endpoints opinar/quiz/precio/exportar-descripcion
consultan dos capas de pre-generado:

  1. Pauta cargada con contenido enriquecido (Sprint 15 B15.1+B15.2):
     - opiniones_alternativas, comentarios_cortos, quiz_pregenerado por dato
     - catchphrases_episodio, intros_cold_open, outros_cliffhanger
     - publicacion completa (titulos, descripcion, hashtags, thumbnails, ig_post)

  2. Cache local con TTL 30 dias (Sprint 15 B15.5):
     - tarrobot-cache-llm.json en data/. Hasta 5 respuestas por key.
     - Si Luis pidio "opinar mario galaxy" 3 veces, se cachean las 3 y
       en futuras vuelve random alguna.

Si ambas capas fallan, se llama Claude y la respuesta se cachea.

Tambien expone telemetria (B15.6): cuenta llamadas por endpoint y estimacion
de gasto (haiku ~$0.001/call de promedio).
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path
from typing import Optional

# Path canonico del repo
sys.path.insert(0, str(Path(__file__).parent))
import tarrobot as _t

CACHE_PATH = _t.REPO / "data" / "tarrobot-cache-llm.json"
CACHE_TTL_DAYS = 30
CACHE_MAX_PER_KEY = 5

# Sprint 15 B15.6: telemetria
LLM_TELEMETRY = {
    "calls": {},                    # {endpoint: count}
    "calls_total": 0,
    "estimated_cost_usd": 0.0,      # acumulado
    "session_started_ts": time.time(),
}

# Costo estimado promedio por endpoint (USD, haiku-4-5).
# Estos son numeros aproximados basados en tamano tipico de prompt + respuesta.
LLM_COST_ESTIMATE = {
    "opinar": 0.0008,
    "cuentame": 0.001,
    "precio_opinion": 0.0008,
    "quiz": 0.0006,
    "social_respond": 0.0008,
    "social_chat_reply": 0.0008,
    "pauta_auto_tema": 0.05,        # mucho mas grande
    "pauta_auto_tema_enriquecido": 0.08,
    "sugerir_orden": 0.003,
    "exportar_descripcion": 0.005,
    "default": 0.001,
}


# ─────────────────────────────────────────────────────────────────────────
# Modo barato (B15.7)
# ─────────────────────────────────────────────────────────────────────────

_modo_barato: bool = False


def set_modo_barato(activo: bool) -> None:
    global _modo_barato
    _modo_barato = bool(activo)


def is_modo_barato() -> bool:
    return _modo_barato


# ─────────────────────────────────────────────────────────────────────────
# Cache JSON
# ─────────────────────────────────────────────────────────────────────────

_cache: Optional[dict] = None


def _load_cache() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    if CACHE_PATH.exists():
        try:
            _cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            _cache = {}
    else:
        _cache = {}
    return _cache


def _save_cache() -> None:
    if _cache is None:
        return
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        CACHE_PATH.write_text(
            json.dumps(_cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[llm_resolver] no se pudo guardar cache: {e}")


def _normalize_key(key: str) -> str:
    """Normaliza para que 'Mario Galaxy' y 'mario galaxy' usen el mismo cache."""
    return (key or "").strip().lower()


def cache_get(endpoint: str, key: str) -> Optional[dict]:
    """Devuelve una respuesta cacheada random, o None."""
    if not endpoint or not key:
        return None
    cache = _load_cache()
    k = _normalize_key(key)
    section = cache.get(endpoint, {})
    entry = section.get(k)
    if not entry:
        return None
    responses = entry.get("responses", [])
    if not responses:
        return None
    # Filtrar por TTL
    cutoff = time.time() - (CACHE_TTL_DAYS * 86400)
    valid = [r for r in responses if r.get("ts", 0) >= cutoff]
    if not valid:
        # Todo vencido: limpiar entrada
        del section[k]
        if not section:
            cache.pop(endpoint, None)
        _save_cache()
        return None
    chosen = random.choice(valid)
    # Marcar uso (LRU light)
    entry["last_used_ts"] = time.time()
    return chosen.get("payload")


def cache_save(endpoint: str, key: str, payload: dict) -> None:
    """Guarda una respuesta en cache. Mantiene max CACHE_MAX_PER_KEY por key."""
    if not endpoint or not key or not payload:
        return
    cache = _load_cache()
    k = _normalize_key(key)
    section = cache.setdefault(endpoint, {})
    entry = section.setdefault(k, {"responses": [], "last_used_ts": time.time()})
    entry["responses"].append({"payload": payload, "ts": time.time()})
    # Acotar
    if len(entry["responses"]) > CACHE_MAX_PER_KEY:
        entry["responses"] = entry["responses"][-CACHE_MAX_PER_KEY:]
    entry["last_used_ts"] = time.time()
    _save_cache()


def cache_stats() -> dict:
    cache = _load_cache()
    total_entries = 0
    total_responses = 0
    by_endpoint = {}
    for endpoint, section in cache.items():
        n_keys = len(section)
        n_responses = sum(len(e.get("responses", [])) for e in section.values())
        by_endpoint[endpoint] = {"keys": n_keys, "responses": n_responses}
        total_entries += n_keys
        total_responses += n_responses
    return {
        "total_keys": total_entries,
        "total_responses": total_responses,
        "by_endpoint": by_endpoint,
    }


# ─────────────────────────────────────────────────────────────────────────
# Resolver desde pauta enriquecida (B15.3)
# ─────────────────────────────────────────────────────────────────────────

def _buscar_dato_de_pauta(pauta: dict, tema: str) -> Optional[dict]:
    """Busca el dato cuyo 'tema' matchea el query (fuzzy lowercase)."""
    if not pauta or not tema:
        return None
    q = tema.lower().strip()
    datos = pauta.get("datos", [])
    # Match exacto primero
    for d in datos:
        if d.get("tema", "").lower() == q:
            return d
    # Match parcial
    for d in datos:
        t = d.get("tema", "").lower()
        if t and (q in t or t in q):
            return d
    return None


def resolver_opinion(pauta: Optional[dict], tema: str) -> Optional[dict]:
    """
    Busca opinion pre-generada en la pauta para el tema. Devuelve
    {texto, estado} o None si no hay match.
    """
    if not pauta:
        return None
    dato = _buscar_dato_de_pauta(pauta, tema)
    if not dato:
        return None
    opciones = dato.get("opiniones_alternativas") or []
    if not opciones:
        return None
    texto = random.choice(opciones)
    return {"texto": texto, "estado": dato.get("estado", "talking")}


def resolver_comentario_corto(pauta: Optional[dict], tema: str) -> Optional[str]:
    """Comentario corto contextual al dato. None si no hay match."""
    if not pauta:
        return None
    dato = _buscar_dato_de_pauta(pauta, tema)
    if not dato:
        return None
    opciones = dato.get("comentarios_cortos") or []
    if not opciones:
        return None
    return random.choice(opciones)


def resolver_quiz(pauta: Optional[dict], tema_hint: Optional[str] = None) -> Optional[dict]:
    """
    Pregunta de trivia pre-generada. Si tema_hint match a un dato, usa el
    quiz de ese dato. Sino, elige random de cualquier dato con quiz.
    Devuelve {pregunta, respuesta, pista, tema}.
    """
    if not pauta:
        return None
    datos = pauta.get("datos", [])
    if not datos:
        return None
    if tema_hint:
        dato = _buscar_dato_de_pauta(pauta, tema_hint)
        if dato:
            quizzes = dato.get("quiz_pregenerado") or []
            if quizzes:
                q = random.choice(quizzes)
                return {
                    "pregunta": q.get("pregunta", ""),
                    "respuesta_esperada": q.get("respuesta", ""),
                    "pista_opcional": q.get("pista", ""),
                    "tema": dato.get("tema", ""),
                }
    # Fallback: cualquier dato con quiz
    datos_con_quiz = [d for d in datos if d.get("quiz_pregenerado")]
    if not datos_con_quiz:
        return None
    dato = random.choice(datos_con_quiz)
    q = random.choice(dato["quiz_pregenerado"])
    return {
        "pregunta": q.get("pregunta", ""),
        "respuesta_esperada": q.get("respuesta", ""),
        "pista_opcional": q.get("pista", ""),
        "tema": dato.get("tema", ""),
    }


def resolver_publicacion(pauta: Optional[dict]) -> Optional[dict]:
    """Devuelve el dict de publicacion pre-generado, o None."""
    if not pauta:
        return None
    pub = pauta.get("publicacion")
    return pub if pub and isinstance(pub, dict) else None


def resolver_catchphrase_episodio(pauta: Optional[dict]) -> Optional[str]:
    """Catchphrase contextual al episodio (en vez de las genericas)."""
    if not pauta:
        return None
    opciones = pauta.get("catchphrases_episodio") or []
    if not opciones:
        return None
    return random.choice(opciones)


# ─────────────────────────────────────────────────────────────────────────
# Telemetria (B15.6)
# ─────────────────────────────────────────────────────────────────────────

def track_llm_call(endpoint: str, cost_override: Optional[float] = None) -> None:
    """Llamado por cada endpoint que realmente llamo Claude (no cache hit)."""
    LLM_TELEMETRY["calls"][endpoint] = LLM_TELEMETRY["calls"].get(endpoint, 0) + 1
    LLM_TELEMETRY["calls_total"] += 1
    cost = cost_override if cost_override is not None else LLM_COST_ESTIMATE.get(
        endpoint, LLM_COST_ESTIMATE["default"]
    )
    LLM_TELEMETRY["estimated_cost_usd"] += cost


def reset_telemetry() -> None:
    LLM_TELEMETRY["calls"].clear()
    LLM_TELEMETRY["calls_total"] = 0
    LLM_TELEMETRY["estimated_cost_usd"] = 0.0
    LLM_TELEMETRY["session_started_ts"] = time.time()


def telemetry_snapshot() -> dict:
    return {
        "calls_total": LLM_TELEMETRY["calls_total"],
        "calls_by_endpoint": dict(LLM_TELEMETRY["calls"]),
        "estimated_cost_usd": round(LLM_TELEMETRY["estimated_cost_usd"], 4),
        "session_minutes": int((time.time() - LLM_TELEMETRY["session_started_ts"]) / 60),
        "modo_barato": is_modo_barato(),
        "cache": cache_stats(),
    }


__all__ = [
    "set_modo_barato", "is_modo_barato",
    "cache_get", "cache_save", "cache_stats",
    "resolver_opinion", "resolver_comentario_corto", "resolver_quiz",
    "resolver_publicacion", "resolver_catchphrase_episodio",
    "track_llm_call", "reset_telemetry", "telemetry_snapshot",
]
