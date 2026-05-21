"""
obs_controller.py
Cliente WebSocket para obs-websocket v5 (OBS 28+).

Implementa solo lo que TarroBot necesita:
  - Conectar/desconectar con handshake SHA256
  - Listar escenas y obtener escena actual
  - Cambiar escena
  - Mostrar/ocultar fuentes dentro de una escena (toggle)
  - Listener de eventos (no usado por ahora, solo no rompe la conexion)

Protocolo:
  https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md

Decisiones:
  - websockets puro (ya viene con uvicorn[standard]) en vez de obsws-python:
    una dep menos en el installer y control total del flujo.
  - Singleton _client: hay un solo OBS por instancia de TarroBot.
  - Tolerante: si OBS no esta corriendo, conectar lanza excepcion pero el
    server sigue funcionando normal (todo lo OBS queda como no-op).
"""

import asyncio
import base64
import hashlib
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import websockets
    from websockets.exceptions import ConnectionClosed
except ImportError:
    websockets = None
    ConnectionClosed = Exception


class OBSError(Exception):
    """Cualquier fallo conversacional con OBS."""
    pass


class OBSClient:
    """
    Cliente WebSocket obs-websocket v5.

    Uso:
        c = OBSClient("localhost", 4455, "mipass")
        await c.connect()
        escenas = await c.get_scene_list()
        await c.set_scene("cam-koko")
        await c.disconnect()
    """

    def __init__(self, host: str = "localhost", port: int = 4455, password: str = ""):
        self.host = host
        self.port = int(port)
        self.password = password or ""
        self.ws = None
        self.connected: bool = False
        self.rpc_version: int = 1
        self._req_counter: int = 0
        self._pending: Dict[str, asyncio.Future] = {}
        self._counter_lock = asyncio.Lock()
        self._listener_task: Optional[asyncio.Task] = None
        self._last_error: Optional[str] = None

    # ────────────────────── conexion ──────────────────────

    async def connect(self, timeout: float = 5.0) -> None:
        if websockets is None:
            raise OBSError("falta libreria 'websockets'. pip install websockets")
        url = f"ws://{self.host}:{self.port}"
        try:
            self.ws = await asyncio.wait_for(
                websockets.connect(url, subprotocols=["obswebsocket.json"]),
                timeout=timeout,
            )
        except (OSError, asyncio.TimeoutError) as e:
            raise OBSError(f"no se pudo conectar a OBS en {url}: {e}")

        # 1) Recibir Hello (op 0)
        try:
            hello_raw = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
        except asyncio.TimeoutError:
            await self._close_silent()
            raise OBSError("OBS no envio Hello (timeout)")
        hello = json.loads(hello_raw)
        if hello.get("op") != 0:
            await self._close_silent()
            raise OBSError(f"esperaba Hello (op 0), llego {hello}")
        d = hello.get("d", {})
        self.rpc_version = int(d.get("rpcVersion", 1))

        # 2) Construir Identify (op 1) con auth si OBS lo pide
        identify: Dict[str, Any] = {
            "op": 1,
            "d": {
                "rpcVersion": self.rpc_version,
                "eventSubscriptions": 0,  # no suscribirse a eventos por ahora
            },
        }
        auth_info = d.get("authentication")
        if auth_info:
            if not self.password:
                await self._close_silent()
                raise OBSError("OBS requiere password pero no se configuro ninguna")
            challenge = auth_info["challenge"]
            salt = auth_info["salt"]
            secret = base64.b64encode(
                hashlib.sha256((self.password + salt).encode("utf-8")).digest()
            ).decode("ascii")
            auth_resp = base64.b64encode(
                hashlib.sha256((secret + challenge).encode("utf-8")).digest()
            ).decode("ascii")
            identify["d"]["authentication"] = auth_resp

        await self.ws.send(json.dumps(identify))

        # 3) Recibir Identified (op 2)
        try:
            ident_raw = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
        except asyncio.TimeoutError:
            await self._close_silent()
            raise OBSError("OBS no envio Identified (password mala?)")
        ident = json.loads(ident_raw)
        if ident.get("op") != 2:
            await self._close_silent()
            raise OBSError(f"esperaba Identified (op 2), llego {ident}")

        self.connected = True
        self._listener_task = asyncio.create_task(self._listener_loop())

    async def _listener_loop(self) -> None:
        """Lee mensajes del WebSocket y resuelve futures de _pending."""
        try:
            async for raw in self.ws:
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                op = msg.get("op")
                if op == 7:  # RequestResponse
                    d = msg.get("d", {})
                    rid = d.get("requestId")
                    fut = self._pending.pop(rid, None)
                    if fut and not fut.done():
                        fut.set_result(d)
                elif op == 5:  # Event
                    # Por ahora ignoramos eventos. Si en el futuro queremos
                    # reaccionar a "scene changed" (por si Luis cambia escena
                    # manual en OBS), aca seria el hook.
                    pass
        except ConnectionClosed:
            pass
        except Exception as e:
            self._last_error = f"listener error: {e}"
        finally:
            self.connected = False

    async def _close_silent(self) -> None:
        try:
            if self.ws:
                await self.ws.close()
        except Exception:
            pass

    async def disconnect(self) -> None:
        self.connected = False
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
        await self._close_silent()
        # cancelar futures pendientes
        for fut in self._pending.values():
            if not fut.done():
                fut.set_exception(OBSError("desconectado"))
        self._pending.clear()

    # ────────────────────── requests ──────────────────────

    async def _request(self, request_type: str,
                       request_data: Optional[dict] = None,
                       timeout: float = 5.0) -> Dict[str, Any]:
        if not self.connected or self.ws is None:
            raise OBSError("OBS no conectado")
        async with self._counter_lock:
            self._req_counter += 1
            rid = f"tarrobot-req-{self._req_counter}"
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[rid] = fut
        await self.ws.send(json.dumps({
            "op": 6,
            "d": {
                "requestType": request_type,
                "requestId": rid,
                "requestData": request_data or {},
            }
        }))
        try:
            d = await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(rid, None)
            raise OBSError(f"timeout en request {request_type}")
        status = d.get("requestStatus", {})
        if not status.get("result", False):
            code = status.get("code", "?")
            comment = status.get("comment", "")
            raise OBSError(f"OBS rechazo {request_type}: [{code}] {comment}")
        return d.get("responseData", {}) or {}

    # ────────────────────── helpers de alto nivel ──────────────────────

    async def get_scene_list(self) -> Dict[str, Any]:
        """
        Devuelve dict con currentProgramSceneName + scenes[].
        scenes = [{sceneName, sceneIndex}, ...]
        """
        return await self._request("GetSceneList")

    async def get_current_scene(self) -> str:
        r = await self._request("GetCurrentProgramScene")
        return r.get("currentProgramSceneName") or r.get("sceneName") or ""

    async def set_scene(self, scene_name: str) -> None:
        await self._request("SetCurrentProgramScene", {"sceneName": scene_name})

    async def get_scene_items(self, scene_name: str) -> List[Dict[str, Any]]:
        r = await self._request("GetSceneItemList", {"sceneName": scene_name})
        return r.get("sceneItems", []) or []

    async def set_input_volume_db(self, input_name: str, db: float) -> None:
        """
        Sprint 12 C7: ajusta volumen de un Input en OBS (en decibeles).
        Rango razonable: -60 (casi mute) a 0 (full). Default musica: -20.
        """
        await self._request("SetInputVolume", {
            "inputName": input_name,
            "inputVolumeDb": float(db),
        })

    async def get_input_volume_db(self, input_name: str) -> float:
        r = await self._request("GetInputVolume", {"inputName": input_name})
        return float(r.get("inputVolumeDb", 0.0))

    async def set_input_mute(self, input_name: str, muted: bool) -> None:
        await self._request("SetInputMute", {
            "inputName": input_name,
            "inputMuted": bool(muted),
        })

    async def get_input_mute(self, input_name: str) -> bool:
        r = await self._request("GetInputMute", {"inputName": input_name})
        return bool(r.get("inputMuted", False))

    async def set_source_enabled(self, scene_name: str, source_name: str,
                                 enabled: bool) -> None:
        """
        Muestra (enabled=True) u oculta (enabled=False) una fuente dentro
        de una escena. Match case-insensitive del nombre.
        """
        items = await self.get_scene_items(scene_name)
        target = None
        sname_lower = source_name.lower()
        for it in items:
            if (it.get("sourceName") or "").lower() == sname_lower:
                target = it
                break
        if target is None:
            raise OBSError(
                f"fuente '{source_name}' no esta en la escena '{scene_name}'. "
                f"Disponibles: {[i.get('sourceName') for i in items]}"
            )
        sid = target.get("sceneItemId")
        await self._request("SetSceneItemEnabled", {
            "sceneName": scene_name,
            "sceneItemId": sid,
            "sceneItemEnabled": bool(enabled),
        })


# ────────────────────── singleton + alias loader ──────────────────────

_client: Optional[OBSClient] = None
_alias_path: Optional[Path] = None
_alias_cache: Optional[Dict[str, Any]] = None


def cargar_alias(path: Path) -> Dict[str, Any]:
    """
    Carga el JSON de alias. Estructura esperada:
      {
        "escenas": { "camara koko": "cam-koko", "general": "cam-cenital" },
        "fuentes": { "logo": ["cam-cenital", "logo-overlay"] },
        "close_ups": { "cartucho": "cam-closeup-cartucho" },
        "default_scene": "cam-cenital",
        "tarrobot_scene": "tarrobot-full"
      }

    Si no existe el archivo, devuelve estructura vacia (no rompe).
    """
    global _alias_path, _alias_cache
    _alias_path = path
    if path.exists():
        try:
            _alias_cache = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[obs] error parseando {path}: {e}")
            _alias_cache = {}
    else:
        _alias_cache = {}
    # defaults
    _alias_cache.setdefault("escenas", {})
    _alias_cache.setdefault("fuentes", {})
    _alias_cache.setdefault("close_ups", {})
    _alias_cache.setdefault("default_scene", None)
    _alias_cache.setdefault("tarrobot_scene", None)
    return _alias_cache


def get_alias() -> Dict[str, Any]:
    return _alias_cache or {
        "escenas": {}, "fuentes": {}, "close_ups": {},
        "default_scene": None, "tarrobot_scene": None,
    }


def guardar_alias(data: Dict[str, Any]) -> None:
    global _alias_cache
    _alias_cache = data
    if _alias_path:
        _alias_path.parent.mkdir(parents=True, exist_ok=True)
        _alias_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def resolver_escena(nombre_o_alias: str) -> Optional[str]:
    """
    Busca un alias por voz y devuelve el nombre REAL de la escena en OBS.
    Si el alias no esta mapeado, devuelve el nombre tal cual (asumiendo
    que el usuario uso el nombre real). Match case-insensitive.
    """
    if not nombre_o_alias:
        return None
    a = get_alias()
    key = nombre_o_alias.lower().strip()
    # match exacto
    if key in a["escenas"]:
        return a["escenas"][key]
    # match parcial: si el alias contiene la query (ej "koko" → "camara koko")
    for alias_key, real in a["escenas"].items():
        if key in alias_key.lower() or alias_key.lower() in key:
            return real
    return nombre_o_alias  # fallback: usar tal cual


def resolver_close_up(tema: str) -> Optional[str]:
    """Busca escena de close-up por palabra clave."""
    if not tema:
        return None
    a = get_alias().get("close_ups", {})
    key = tema.lower().strip()
    if key in a:
        return a[key]
    for alias_key, real in a.items():
        if alias_key.lower() in key or key in alias_key.lower():
            return real
    return None


# ────────────────────── singleton lifecycle ──────────────────────

async def conectar(host: str, port: int, password: str) -> OBSClient:
    """Cierra cualquier conexion previa y abre una nueva."""
    global _client
    if _client and _client.connected:
        try:
            await _client.disconnect()
        except Exception:
            pass
    _client = OBSClient(host, port, password)
    await _client.connect()
    return _client


async def desconectar() -> None:
    global _client
    if _client:
        try:
            await _client.disconnect()
        except Exception:
            pass
    _client = None


def cliente() -> Optional[OBSClient]:
    return _client


def is_connected() -> bool:
    return _client is not None and _client.connected


async def status() -> Dict[str, Any]:
    """Estado consultable desde el panel."""
    if not is_connected():
        return {"connected": False, "host": None, "port": None,
                "current_scene": None, "scenes": []}
    try:
        info = await _client.get_scene_list()
        return {
            "connected": True,
            "host": _client.host,
            "port": _client.port,
            "current_scene": info.get("currentProgramSceneName"),
            "scenes": [s.get("sceneName") for s in info.get("scenes", [])],
        }
    except Exception as e:
        return {"connected": False, "error": str(e),
                "host": _client.host, "port": _client.port,
                "current_scene": None, "scenes": []}
