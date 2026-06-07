"""
fetch_boxart_wiki.py - Retrotarros Studio Suite
Descarga box art (portada) LIMPIA desde Wikipedia (sin marca de agua, NTSC).

Usa la API: generator=search para resolver el articulo del juego + pageimages
(piprop=original) para traer la imagen principal del articulo, que en articulos
de videojuegos ES la caratula de la caja.

Guarda en studio/img/<out_dir>/<key>.jpg

Uso (modulo):
  from fetch_boxart_wiki import descargar
  descargar(out_dir, [(key, "search query"), ...])
"""
from __future__ import annotations
import json, sys, time, urllib.request, urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UA = "RetrotarrosBot/1.0 (canal retrogaming; contacto luis.gatica.jerez@gmail.com)"
API = "https://en.wikipedia.org/w/api.php"


def _get(url: str, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def _resolve_title(query: str):
    """Resuelve el titulo exacto del articulo via search API."""
    q = urllib.parse.urlencode({
        "action": "query", "format": "json",
        "list": "search", "srsearch": query, "srlimit": "1",
    })
    data = json.loads(_get(f"{API}?{q}"))
    hits = data.get("query", {}).get("search", [])
    return hits[0]["title"] if hits else None


def _summary_image(title: str):
    """REST summary -> originalimage.source (la caratula del infobox)."""
    t = urllib.parse.quote(title.replace(" ", "_"), safe="_()")
    data = json.loads(_get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{t}"))
    return data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")


def _img_url(query: str):
    # 1) intento directo (query como titulo)
    for title in (query, _resolve_title(query)):
        if not title:
            continue
        try:
            url = _summary_image(title)
        except Exception:
            url = None
        if url and url.rsplit(".", 1)[-1].lower() != "svg":
            return url, title
    return None, None


def descargar(out_dir: str, juegos: list, progress=print) -> dict:
    """juegos: lista de (key, query). query = nombre del juego + 'video game'."""
    dst = REPO / "studio" / "img" / out_dir
    dst.mkdir(parents=True, exist_ok=True)
    res = {"ok": [], "fail": []}
    for key, query in juegos:
        try:
            url, title = _img_url(query)
            if not url:
                res["fail"].append((key, query)); progress(f"  [FAIL] {query} (sin imagen)"); continue
            # evitar SVG/logo; preferir jpg/png raster
            ext = url.rsplit(".", 1)[-1].lower()
            if ext == "svg":
                res["fail"].append((key, query)); progress(f"  [FAIL] {query} (es SVG/logo)"); continue
            img = _get(url, binary=True)
            if len(img) < 2000:
                raise ValueError("imagen muy chica")
            (dst / f"{key}.jpg").write_bytes(img)
            res["ok"].append((key, title)); progress(f"  [OK]   {query} <- {title} ({len(img)//1024}kb)")
        except Exception as e:
            res["fail"].append((key, query)); progress(f"  [FAIL] {query}: {e}")
        time.sleep(0.3)
    return res


if __name__ == "__main__":
    print("Modulo. Importar descargar() desde un driver en .cache/.")
