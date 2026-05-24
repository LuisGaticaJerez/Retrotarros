"""
teaser_jobs.py - Sprint 17 - Retrotarros Studio Suite

Job manager async para TarroTeaser. Permite disparar generaciones de teaser
desde el panel del estudio (UI) o via endpoint REST, con feedback de progreso
en vivo por WebSocket.

Restriccion de concurrencia: solo 1 job corriendo a la vez (Whisper es CPU-heavy
y ffmpeg en paralelo se pelea por I/O y cores). Si llega un segundo job mientras
hay uno corriendo, queda en queue y se procesa cuando el primero termina.

Disenado para vivir dentro del proceso FastAPI de tarrobot-live.py. NO usa
Redis/Celery/etc — todo en memoria. Si el proceso muere, los jobs se pierden
(asumimos sesion del estudio, no produccion 24/7).
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections import deque
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional

# Tipos
BroadcastFn = Callable[[dict], Awaitable[None]]


@dataclass
class TeaserJob:
    """Representa un job de generacion de teaser en memoria."""

    id: str
    slug: str
    video_path: str
    status: str = "queued"  # queued / running / done / error / cancelled
    progress: int = 0  # 0..100
    step: int = 0  # 0..5 (0 = no empezo, 1..5 = paso actual)
    total_steps: int = 5
    current_msg: str = ""
    log_lines: deque = field(default_factory=lambda: deque(maxlen=200))
    output_path: Optional[str] = None
    size_mb: Optional[float] = None
    duration_s: Optional[float] = None
    clips: Optional[list] = None
    ep_type: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serializa para JSON (FastAPI lo necesita). deque -> list."""
        d = asdict(self)
        d["log_lines"] = list(self.log_lines)
        return d


class TeaserJobManager:
    """Mantiene el estado de todos los jobs y procesa de a uno.

    Uso:
        manager = TeaserJobManager(broadcast_fn=ws.broadcast_live)
        await manager.start()  # arranca el worker
        job_id = await manager.submit(video_path, slug, **params)
        job = manager.get(job_id)
        await manager.stop()
    """

    def __init__(self, broadcast_fn: Optional[BroadcastFn] = None,
                 max_jobs_history: int = 50):
        self._jobs: dict[str, TeaserJob] = {}
        self._order: deque[str] = deque(maxlen=max_jobs_history)
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._broadcast = broadcast_fn
        self._worker_task: Optional[asyncio.Task] = None
        self._current_job_id: Optional[str] = None
        self._stopped = False

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def set_broadcast(self, broadcast_fn: BroadcastFn) -> None:
        """Permite re-setear el broadcaster post-init (orden de wiring)."""
        self._broadcast = broadcast_fn

    async def start(self) -> None:
        """Arranca el worker que procesa la queue. Llamar en lifespan startup."""
        if self._worker_task and not self._worker_task.done():
            return
        self._stopped = False
        self._worker_task = asyncio.create_task(self._worker_loop(), name="teaser-worker")

    async def stop(self) -> None:
        """Detiene el worker (graceful). Llamar en lifespan shutdown."""
        self._stopped = True
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

    async def submit(self, video_path: str, slug: str, **params) -> str:
        """Encola un nuevo job. Devuelve el job_id."""
        job_id = uuid.uuid4().hex[:12]
        job = TeaserJob(
            id=job_id,
            slug=slug,
            video_path=video_path,
            params=dict(params),
        )
        self._jobs[job_id] = job
        self._order.append(job_id)
        await self._queue.put(job_id)
        await self._broadcast_event({
            "tipo": "teaser.queued",
            "job": job.to_dict(),
            "queue_size": self._queue.qsize(),
        })
        return job_id

    def get(self, job_id: str) -> Optional[TeaserJob]:
        return self._jobs.get(job_id)

    def list_recent(self, limit: int = 20) -> list[dict]:
        """Devuelve los ultimos N jobs ordenados por created_at desc."""
        jobs = [self._jobs[jid] for jid in self._order if jid in self._jobs]
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return [j.to_dict() for j in jobs[:limit]]

    def current_job_id(self) -> Optional[str]:
        return self._current_job_id

    async def cancel(self, job_id: str) -> bool:
        """Marca un job como cancelado.

        Nota: si esta corriendo, la cancelacion no detiene Whisper/ffmpeg
        (corren en thread separado). Solo previene que job posteriores se
        ejecuten si el actual termina. Para v1 es suficiente.
        """
        job = self._jobs.get(job_id)
        if not job:
            return False
        if job.status in ("done", "error", "cancelled"):
            return False
        if job.status == "queued":
            job.status = "cancelled"
            job.finished_at = time.time()
            await self._broadcast_event({
                "tipo": "teaser.cancelled",
                "job_id": job_id,
            })
            return True
        # Running: marcamos cancel-requested pero igual termina (limit v1)
        job.error = "cancelacion solicitada (el job actual termina su corrida)"
        return True

    # ------------------------------------------------------------------
    # Worker interno
    # ------------------------------------------------------------------

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
                    "tipo": "teaser.error",
                    "job_id": job_id,
                    "error": job.error,
                })
            finally:
                self._current_job_id = None

    async def _run_job(self, job: TeaserJob) -> None:
        job.status = "running"
        job.started_at = time.time()
        await self._broadcast_event({
            "tipo": "teaser.started",
            "job": job.to_dict(),
        })

        # Capturamos el loop para que el callback (que vive en thread worker)
        # pueda agendar coroutines de broadcast de manera thread-safe.
        loop = asyncio.get_running_loop()

        def progress_cb(step: int, total: int, msg: str, **extra) -> None:
            """Callback que invoca tarroteaser desde el thread worker."""
            job.step = step
            job.total_steps = total
            job.current_msg = msg
            job.progress = int((step / max(1, total)) * 100)
            line = f"[{step}/{total}] {msg}"
            job.log_lines.append(line)
            # agendar broadcast en el event loop (este callback corre en thread)
            asyncio.run_coroutine_threadsafe(
                self._broadcast_event({
                    "tipo": "teaser.progress",
                    "job_id": job.id,
                    "step": step,
                    "total": total,
                    "progress": job.progress,
                    "msg": msg,
                }),
                loop,
            )

        # Importar tarroteaser tarde para que el modulo se cargue sin requerir
        # whisper/ffmpeg al boot del server (los pide solo si se usa el job).
        from tarroteaser import generar_teaser

        params = dict(job.params)
        # Correr en thread (Whisper + ffmpeg son sync y bloquean)
        result = await asyncio.to_thread(
            generar_teaser,
            video_path=job.video_path,
            slug=job.slug,
            ep_type=params.get("ep_type"),
            num_highlights=int(params.get("num_highlights", 3)),
            clip_duration=float(params.get("clip_duration", 3.0)),
            max_clip_duration=float(params.get("max_clip_duration", 6.0)),
            model=params.get("model", "small"),
            out_dir=params.get("out_dir"),
            progress_callback=progress_cb,
        )

        job.status = "done"
        job.progress = 100
        job.step = job.total_steps
        job.output_path = result.get("output_path")
        job.size_mb = result.get("size_mb")
        job.duration_s = result.get("duration_s")
        job.clips = result.get("clips")
        job.ep_type = result.get("ep_type")
        job.finished_at = time.time()

        await self._broadcast_event({
            "tipo": "teaser.done",
            "job": job.to_dict(),
        })

    async def _broadcast_event(self, payload: dict) -> None:
        """Wrap del broadcast con guardia: si no esta seteado, log y sigue."""
        if not self._broadcast:
            return
        try:
            await self._broadcast(payload)
        except Exception as e:
            print(f"[teaser_jobs] broadcast fallo: {e}")
