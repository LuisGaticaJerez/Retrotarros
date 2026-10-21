"""Notas de critica de varios juegos desde Wikipedia, sin abrir el navegador.

Lee el cuadro de recepcion (Video game reviews) del wikitexto de cada articulo y muestra Metacritic (MC),
GameRankings (GR), Famitsu, IGN, GameSpot, EGM, Game Informer. Sirve para armar rankings de calidad
(Infravalorados) en minutos. Los numeros vienen de Wikipedia, que cita esas fuentes: confirmarlos antes de
decirlos en camara.

Uso:
  python scripts/wiki_reception.py "Vagrant Story" "Klonoa: Door to Phantomile" "Alundra"
  python scripts/wiki_reception.py --lista candidatos.txt        # un titulo de Wikipedia por linea

Notas:
- Usar el titulo exacto de Wikipedia (a veces lleva sufijo: "Wild Arms (video game)").
- Si un juego no tiene cuadro de recepcion se imprime vacio.
- Pausa de 1 s entre pedidos para no recibir 429.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "RetrotarrosBot/1.0 (luis.gatica.jerez@gmail.com)"}
CLAVES = ("MC", "GR", "Fam", "IGN", "GSpot", "EGM", "GI", "GRadar")


def wikitexto(titulo: str) -> str:
    url = ("https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&rvslots=main"
           "&redirects=1&format=json&titles=" + urllib.parse.quote(titulo))
    for intento in range(4):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
            pag = next(iter(d["query"]["pages"].values()))
            return pag["revisions"][0]["slots"]["main"]["*"]
        except Exception:
            time.sleep(3 * (intento + 1))
    return ""


def notas(texto: str) -> dict:
    m = re.search(r"\{\{Video game reviews([\s\S]*?)\n\}\}", texto)
    caja = m.group(1) if m else ""
    out = {}
    for linea in caja.split("\n"):
        k = re.match(r"\s*\|\s*(\w+)\s*=\s*(.*)", linea)
        if k and k.group(1) in CLAVES:
            valor = re.sub(r"<ref[\s\S]*?(</ref>|/>)|\{\{[^}]*\}\}|<[^>]+>", "", k.group(2)).strip()
            out[k.group(1)] = valor[:40]
    return out


def main(argv: list[str]) -> None:
    titulos = argv
    if argv[:1] == ["--lista"] and len(argv) > 1:
        titulos = [l.strip() for l in open(argv[1], encoding="utf-8") if l.strip()]
    for t in titulos:
        n = notas(wikitexto(t))
        print(f"{t} | " + ", ".join(f"{k}={v}" for k, v in n.items()))
        time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
