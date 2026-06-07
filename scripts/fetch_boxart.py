"""
fetch_boxart.py - Retrotarros Studio Suite
Descarga box art (cara frontal) desde gamesdatabase.org para un set de juegos.

Estrategia robusta: por cada juego, abre su pagina /game/nintendo-nes/<slug>,
extrae el nombre EXACTO del archivo Box (de la miniatura Box/Thumb/Thumb_<file>),
y descarga la version grande /Media/SYSTEM/Nintendo_NES/Box/Big/<file>.

Guarda en studio/img/<out_dir>/<key>.jpg  (key = slug del titulo, asi los shorts
y decks lo toman automatico).

Uso (como modulo):
  from fetch_boxart import descargar
  descargar(system, out_dir, [(key, [slug1, slug2, ...]), ...])
"""
from __future__ import annotations
import re, sys, time, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://www.gamesdatabase.org"


def _get(url: str, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def _slugs(title: str):
    """Genera candidatos de slug estilo gamesdatabase.org."""
    t = title.lower()
    base = (t.replace("&", "and").replace("'", "-").replace(".", "-")
            .replace(":", "-").replace("/", "-").replace("!", "-"))
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    cands = [base, base + "-", re.sub(r"-+", "-", base)]
    # sin guiones repetidos + variante sin trailing
    out = []
    for c in cands:
        c = re.sub(r"-+", "-", c)
        for v in (c, c.rstrip("-"), c + "-"):
            if v and v not in out:
                out.append(v)
    return out


def descargar(system_path: str, out_dir: str, juegos: list, progress=print) -> dict:
    """juegos: lista de (key, title, [slugs_extra opcionales])."""
    dst = REPO / "studio" / "img" / out_dir
    dst.mkdir(parents=True, exist_ok=True)
    res = {"ok": [], "fail": []}
    for entry in juegos:
        key, title = entry[0], entry[1]
        extra = entry[2] if len(entry) > 2 else []
        slugs = extra + _slugs(title)
        found = None
        for slug in slugs:
            page_url = f"{BASE}/game/{system_path}/{slug}"
            try:
                html = _get(page_url)
            except Exception:
                continue
            m = re.search(r'/Media/SYSTEM/([^/]+)/Box/Thumb/Thumb_([^"\']+\.(?:jpg|jpeg|png))', html, re.I)
            if m:
                sysfolder, fname = m.group(1), m.group(2)
                found = f"{BASE}/Media/SYSTEM/{sysfolder}/Box/Big/{fname}"
                break
        if not found:
            res["fail"].append((key, title))
            progress(f"  [FAIL] {title} (no encontre box)")
            continue
        try:
            img = _get(found.replace(" ", "%20"), binary=True)
            if len(img) < 2000 or img[:3] == b"\xef\xbb\xbf" or b"<html" in img[:200].lower():
                raise ValueError("no es imagen valida")
            (dst / f"{key}.jpg").write_bytes(img)
            res["ok"].append((key, title))
            progress(f"  [OK]   {title} -> {key}.jpg ({len(img)//1024}kb)")
        except Exception as e:
            res["fail"].append((key, title))
            progress(f"  [FAIL] {title}: {e}")
        time.sleep(0.4)
    return res


if __name__ == "__main__":
    print("Modulo. Importar descargar() desde un driver en .cache/.")
