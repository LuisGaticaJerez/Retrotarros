"""
tarroshort_jobs.py - Sprint 19 - Retrotarros Studio Suite

Job manager async para TarroShort (MP4 vertical con TarroBot leyendo). Mismo
patron que teaser_jobs.py: 1 job a la vez (Playwright + ffmpeg son CPU/IO heavy),
feedback de progreso en vivo por WebSocket, todo en memoria.

Vive dentro del proceso FastAPI de tarrobot-live.py.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import Awaitable, Callable, Optional

BroadcastFn = Callable[[dict], Awaitable[None]]


@dataclass
class TarroShortJob:
    id: str
    slug: str                 # slug del short (o de la pauta si from_pauta)
    from_pauta: bool = False
    status: str = "queued"    # queued / running / done / error / cancelled
    progress: int = 0
    current_msg: str = ""
    log_lines: deque = field(default_factory=lambda: deque(maxlen=200))
    output_path: Optional[str] = None
    size_mb: Optional[float] = None
    html_path: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["log_lines"] = list(self.log_lines)
        return d


class TarroShortJobManager:
    def __init__(self, broadcast_fn: Optional[BroadcastFn] = None, max_jobs_history: int = 50):
        self._jobs: dict[str, TarroShortJob] = {}
        self._order: deque[str] = deque(maxlen=max_jobs_history)
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._broadcast = broadcast_fn
        self._worker_task: Optional[asyncio.Task] = None
        self._current_job_id: Optional[str] = None
        self._stopped = False

    def set_broadcast(self, broadcast_fn: BroadcastFn) -> None:
        self._broadcast = broadcast_fn

    async def start(self) -> None:
        if self._worker_task and not self._worker_task.done():
            return
        self._stopped = False
        self._worker_task = asyncio.create_task(self._worker_loop(), name="tarroshort-worker")

    async def stop(self) -> None:
        self._stopped = True
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

    async def submit(self, slug: str, from_pauta: bool = False, **params) -> str:
        job_id = uuid.uuid4().hex[:12]
        job = TarroShortJob(id=job_id, slug=slug, from_pauta=from_pauta, params=dict(params))
        self._jobs[job_id] = job
        self._order.append(job_id)
        await self._queue.put(job_id)
        await self._broadcast_event({
            "tipo": "tarroshort.queued",
            "job": job.to_dict(),
            "queue_size": self._queue.qsize(),
        })
        return job_id

    def get(self, job_id: str) -> Optional[TarroShortJob]:
        return self._jobs.get(job_id)

    def list_recent(self, limit: int = 20) -> list[dict]:
        jobs = [self._jobs[jid] for jid in self._order if jid in self._jobs]
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return [j.to_dict() for j in jobs[:limit]]

    def current_job_id(self) -> Optional[str]:
        return self._current_job_id

    async def _worker_loop(self) -> None:
        while not self._stopped:
            try:
                job_id = await self._queue.get()
            except asyncio.CancelledError:
                break
            job = self._jobs.get(job_id)
            if not job or job.status == "cancelled":
                continue
            self._current_job_id = job_id
            try:
                await self._run_job(job)
            except Exception as e:
                job.status = "error"
                job.error = f"{type(e).__name__}: {e}"
                job.finished_at = time.time()
                await self._broadcast_event({
                    "tipo": "tarroshort.error", "job_id": job_id, "error": job.error,
                })
            finally:
                self._current_job_id = None

    async def _run_job(self, job: TarroShortJob) -> None:
        job.status = "running"
        job.started_at = time.time()
        await self._broadcast_event({"tipo": "tarroshort.started", "job": job.to_dict()})

        loop = asyncio.get_running_loop()

        def progress_cb(msg) -> None:
            msg = str(msg)
            job.current_msg = msg
            job.log_lines.append(msg)
            # heuristica simple de progreso por palabras clave
            if "armando clip" in msg:
                job.progress = max(job.progress, 50)
            elif "voz" in msg:
                job.progress = max(job.progress, 30)
            elif "renderizando" in msg or "HTML armado" in msg:
                job.progress = max(job.progress, 15)
            elif "concatenando" in msg:
                job.progress = max(job.progress, 85)
            asyncio.run_coroutine_threadsafe(
                self._broadcast_event({
                    "tipo": "tarroshort.progress", "job_id": job.id,
                    "progress": job.progress, "msg": msg,
                }), loop,
            )

        # Import tarde (Playwright/ffmpeg/edge-tts solo si se usa el job)
        from tarroshort_render import generar_tarroshort, construir_desde_pauta

        params = dict(job.params)
        render_slug = job.slug

        def _work():
            nonlocal render_slug
            if job.from_pauta:
                html = construir_desde_pauta(job.slug, params.get("out_slug"), progress=progress_cb)
                render_slug = html.stem
                job.html_path = str(html)
            return generar_tarroshort(
                render_slug,
                voice=params.get("voice", "es-CL-CatalinaNeural"),
                pitch=params.get("pitch", "+12Hz"),
                rate=params.get("rate", "+0%"),
                out_path=params.get("out_path"),
                progress=progress_cb,
            )

        out = await asyncio.to_thread(_work)

        job.status = "done"
        job.progress = 100
        job.output_path = str(out)
        try:
            from pathlib import Path as _P
            job.size_mb = round(_P(out).stat().st_size / (1024 * 1024), 2)
        except Exception:
            job.size_mb = None
        job.finished_at = time.time()
        await self._broadcast_event({"tipo": "tarroshort.done", "job": job.to_dict()})

    async def _broadcast_event(self, payload: dict) -> None:
        if not self._broadcast:
            return
        try:
            await self._broadcast(payload)
        except Exception as e:
            print(f"[tarroshort_jobs] broadcast fallo: {e}")
