"""Propuesta de hashtags y etiquetas para todos los videos del inventario (no toca YouTube: solo escribe archivos para revisar).

Regla (Luis 2026-10-14, medida contra las paginas de hashtag de YouTube): 4 a 5 hashtags por video, un mix de
serie/tema + consola o juego + uno amplio (#Retrogaming) + marca (#Retrotarros). Nada de #Gaming (185 M de videos), #gamer
ni basura de otras redes (#fyp, #love, #happy, #inspiration...). Etiquetas sin '#', 15 a 20 keywords, bajo 500 caracteres.
Uso: python scripts/youtube_propuesta.py [data/youtube/inventario-AAAA-MM-DD.json]
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# (regex sobre el titulo, hashtag, etiquetas de la consola). El orden importa: lo mas especifico primero.
CONSOLAS = [
    (r"ps ?vita", "PSVita", ["ps vita", "playstation vita", "vita"]),
    (r"game ?boy", "GameBoy", ["game boy", "gameboy", "nintendo game boy"]),
    (r"game ?cube", "GameCube", ["gamecube", "nintendo gamecube"]),
    (r"master system", "MasterSystem", ["master system", "sega master system"]),
    (r"mega drive|genesis", "MegaDrive", ["mega drive", "sega mega drive", "sega genesis"]),
    (r"atari", "Atari2600", ["atari 2600", "atari"]),
    (r"n64|nintendo 64", "Nintendo64", ["nintendo 64", "n64"]),
    (r"super nintendo|snes", "SNES", ["snes", "super nintendo", "super nintendo juegos"]),
    (r"\bnes\b", "NES", ["nes", "nintendo nes", "nintendo entertainment system"]),
    (r"neo ?geo", "NeoGeo", ["neo geo", "snk"]),
    (r"playstation|ps1", "PlayStation", ["playstation", "ps1"]),
]

# Reseñas y shorts cuyo titulo no trae la consola o el juego: (hashtag del juego, hashtag de consola, nombre para etiquetas, consola para etiquetas)
MANUAL = {
    "l7dqPkwIgR0": ("KingOfFighters", "NeoGeo", "king of fighters 94", "neo geo"),
    "cTTrSz_NeVw": ("Battletoads", "NES", "battletoads", "nes"),
    "nfWhA1bcO3Y": ("SuperMarioWorld", "SNES", "super mario world yoshi's island", "snes"),
    "RkRTO4KBRBg": ("ZombiesAteMyNeighbors", "SNES", "zombies ate my neighbors", "snes"),
    "jI2DI6ow8mU": ("SuperMetroid", "SNES", "super metroid", "snes"),
    "Caipcc89-s0": ("MegaMan2", "NES", "mega man 2", "nes"),
    "vcxs-epemtg": ("DonkeyKongCountry", "SNES", "donkey kong country", "snes"),
    "7uPuw2yUJg0": ("Kirby", "NES", "kirby's adventure", "nes"),
    "93dORrQx41M": ("KillerInstinct", "Arcade", "killer instinct", "arcade"),
    "IM8_4uyqXfc": ("Pitfall", "SNES", "pitfall the mayan adventure", "snes"),
    "tTkYY0ufMVs": ("MortalKombat", "Arcade", "mortal kombat", "arcade"),
    "fAuqU-YuOAE": ("SuperMarioBros3", "NES", "super mario bros 3", "nes"),
    "uHm77p3QdlQ": ("LegendOfZelda", "NES", "the legend of zelda", "nes"),
    "kXYLtNJhGsQ": ("GoldenAxe", "MegaDrive", "golden axe", "mega drive"),
    "OxgvNe4iYM0": ("MetalGearSolid", "PlayStation", "metal gear solid", "playstation"),
    "BwORaLTNdv8": ("ChronoTrigger", "SNES", "chrono trigger", "snes"),
    "FV5PEI6LaHs": ("StreetFighterII", "SNES", "street fighter 2", "snes"),
    "hoUQHUQjTqE": ("Doom", "SNES", "doom", "snes"),
    "ValpUS4I0iI": ("SamuraiShodown", "NeoGeo", "samurai shodown", "neo geo"),
    "P9Fr4TbBL_k": ("WormsArmageddon", None, "worms armageddon", "pc"),
    "M1LaFij21Nw": ("MetalWarriors", "SNES", "metal warriors", "snes"),
    "_XCCPtZAgzo": ("CadillacsAndDinosaurs", "Arcade", "cadillacs and dinosaurs", "arcade"),
    "pHtdPA_CEIU": ("JewelMaster", "MegaDrive", "jewel master", "mega drive"),
    "geqtJjvYw7I": ("TopGear", "SNES", "top gear", "snes"),
    "Ub33C3AjKKU": ("Pokemon", "GameBoy", "pokemon rojo azul", "game boy"),
    "UfFzmQnb-J4": ("SuperSmashBrosMelee", "GameCube", "super smash bros melee", "gamecube"),
}
# Videos que Luis ya habia curado a mano: se respeta su eleccion (WorstGames) dentro de la regla de 4 a 5.
HASHTAGS_A_MANO = {"SXdGEd-uKdg": ["WorstGames", "Nintendo64", "Top10", "Retrogaming", "Retrotarros"]}
TAGS_ARCADE = ["arcade", "maquinitas", "juegos de arcade"]
TEMAS_SHORT = [(r"zelda", "Zelda"), (r"mario", "SuperMario"), (r"sonic", "Sonic"), (r"tetris", "Tetris"), (r"mortal kombat", "MortalKombat"),
               (r"sega", "Sega"), (r"padre", "DiaDelPadre"), (r"videojuegos", "Videojuegos")]
TITULO_HASHTAG_RE = re.compile(r"\s*#(?!\d)\S+")   # "#fypシ゚viral" entero; no toca "#1"

BASE_TAGS = ["retrotarros", "retrogaming", "juegos retro", "videojuegos retro", "nostalgia gamer", "videojuegos"]


def consola(titulo: str):
    t = titulo.lower()
    for rx, tag, tags in CONSOLAS:
        if re.search(rx, t):
            return tag, tags
    return None, []


def tipo(v: dict) -> str:
    t = v["titulo"].lower()
    if v["pestana"] == "shorts":
        return "short"
    if "abriendo el tarro" in t:
        return "abriendo"
    if "especial" in t or "special" in t:
        return "special"
    if "peores" in t:
        return "peores"
    if re.search(r"precio|mas caros|más caros|valen|cuanto valen|cuánto valen", t):
        return "precios"
    if "retrorese" in t.replace("ñ", "n") or "envejec" in t or v["id"] in MANUAL:
        return "resena"
    if re.search(r"top 10|top mundial|mejores|mejor juego|ranking", t):
        return "mundial"
    if "colecci" in t:
        return "coleccion"
    if "saga" in t:
        return "saga"
    return "otro"


def dedup(xs):
    seen, out = set(), []
    for x in xs:
        if x.lower() not in seen:
            seen.add(x.lower())
            out.append(x)
    return out


def proponer(v: dict) -> dict:
    t, k = tipo(v), v["id"]
    ctag, ctags = consola(v["titulo"])
    juego_tag = juego_nombre = None
    if k in MANUAL:
        juego_tag, ctag_m, juego_nombre, cnom = MANUAL[k]
        ctag = ctag or ctag_m
        if not ctags:
            ctags = TAGS_ARCADE if ctag_m == "Arcade" else [cnom]
    if k == "P9Fr4TbBL_k":   # el original es de PC (1999): no se etiqueta con una consola
        ctag = None
    h: list[str] = []
    tags: list[str] = []
    if t == "resena":
        h = ["RetroReseñas", juego_tag, ctag, "Retrogaming", "Retrotarros"]
        tags = ["retroreseñas", "reseña retro", "¿envejeció bien?", juego_nombre, f"{juego_nombre} reseña", f"{juego_nombre} retro",
                f"{juego_nombre} {ctags[0] if ctags else ''}".strip()] + ctags
    elif t == "mundial":
        h = ["Top10", ctag, "Retrogaming", "Videojuegos", "Retrotarros"]
        tags = ["top 10", "mejores juegos", "ranking de videojuegos", f"mejores juegos de {ctags[0] if ctags else 'la consola'}", "top mundial", "segun la critica"] + ctags
    elif t == "precios":
        h = ["Coleccionismo", ctag, "Retrogaming", "Top10", "Retrotarros"]
        tags = ["juegos mas caros", "cuanto valen los juegos retro", "precio de juegos retro", "pricecharting", "coleccionismo retro",
                "top precios", f"juegos mas caros de {ctags[0] if ctags else 'la consola'}"] + ctags
    elif t == "peores":
        h = ["Top10", ctag, "Retrogaming", "Videojuegos", "Retrotarros"]
        tags = ["peores juegos", "top 10 peores juegos", "los peores juegos", "juegos malos", "peores juegos de la historia",
                f"peores juegos de {ctags[0] if ctags else 'la consola'}"] + ctags
    elif t == "coleccion":
        h = ["Coleccionismo", ctag, "Retrogaming", "Videojuegos", "Retrotarros"]
        tags = ["coleccion de videojuegos", "coleccion retro", "coleccionismo retro", "coleccionista de videojuegos", "tour de coleccion",
                f"coleccion de {ctags[0] if ctags else 'consolas'}"] + ctags
    elif t == "saga":
        h = [v["titulo"].split()[-1] if False else "Zelda", "Nintendo", "Retrogaming", "Videojuegos", "Retrotarros"]
        tags = ["saga zelda", "historia de zelda", "todos los zelda", "zelda en orden", "legend of zelda", "nintendo"]
    elif t == "abriendo":
        h = ["AbriendoElTarro", "Coleccionismo", "Coleccionistas", "Retrogaming", "Retrotarros"]
        tags = ["abriendo el tarro", "entrevista coleccionista", "coleccionista", "coleccionismo", "coleccion de chile", "coleccionistas chilenos",
                "entrevista"]
    elif t == "special":
        h = ["DiaDelPadre" if "papás" in v["titulo"] or "padre" in v["titulo"].lower() else "Chile", "Retrogaming", "Videojuegos", "Retrotarros", "Nostalgia"]
        tags = ["especial retro", "videojuegos retro", "juegos retro por tema"] + (["dia del padre", "padres gamers"] if h[0] == "DiaDelPadre" else ["glorias navales", "mes del mar", "chile"])
    elif t == "short":
        tl = v["titulo"].lower()
        tema = next((tg for rx, tg in TEMAS_SHORT if re.search(rx, tl)), None)
        h = ["Shorts", tema or ctag, "Retrogaming", ctag if tema else None, "Retrotarros", "TarroBot"]
        tags = ["tarrobot", "retro", "datos curiosos", "videojuegos curiosidades"] + ctags + ([tema.lower()] if tema else [])
    else:
        h = ["Retrogaming", "Videojuegos", "Retrotarros"]
    if k in HASHTAGS_A_MANO:
        h = HASHTAGS_A_MANO[k]
    h = dedup([x for x in h if x])
    tags = dedup([x for x in tags + BASE_TAGS if x])
    corte, total = [], 0
    for x in tags:                      # respeta el tope de 500 caracteres de YouTube (con coma incluida)
        if total + len(x) + 1 > 480:
            break
        corte.append(x)
        total += len(x) + 1
    nuevo = TITULO_HASHTAG_RE.sub("", v["titulo"]).strip()
    return {"id": k, "tipo": t, "titulo": v["titulo"], "titulo_nuevo": nuevo if nuevo != v["titulo"] and nuevo else None, "hashtags_actuales": v["hashtags_descripcion"], "hashtags_nuevos": ["#" + x for x in h],
            "etiquetas_actuales": v["etiquetas"], "etiquetas_nuevas": corte, "revisar": t == "otro" or (t == "resena" and not juego_tag)}


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted((REPO / "data" / "youtube").glob("inventario-*.json"))[-1]
    inv = json.loads(src.read_text(encoding="utf-8"))
    props = [proponer(v) for v in inv["videos"]]
    hoy = date.today().isoformat()
    jp = REPO / "data" / "youtube" / f"propuesta-{hoy}.json"
    jp.write_text(json.dumps({"fecha": hoy, "origen": src.name, "videos": props}, ensure_ascii=False, indent=2), encoding="utf-8")
    lineas = [f"# Propuesta de hashtags y etiquetas ({hoy})", "", f"Origen: `{src.name}`. Solo lectura: nada se aplica hasta que se revise.", "",
              "| Tipo | Video | Hashtags actuales | Hashtags nuevos |", "|---|---|---|---|"]
    for p in props:
        lineas.append(f"| {p['tipo']}{' (revisar)' if p['revisar'] else ''} | {p['titulo'][:55].replace('|', '/')} | {' '.join(p['hashtags_actuales'][:8])} | {' '.join(p['hashtags_nuevos'])} |")
    # el informe legible va a docs/canal/rendimiento/ (ver CLAUDE.md); el JSON queda en data/youtube/
    informe = REPO / "docs" / "canal" / "rendimiento" / f"hashtags-propuesta-{hoy}.md"
    informe.parent.mkdir(parents=True, exist_ok=True)
    informe.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    por_tipo: dict[str, int] = {}
    for p in props:
        por_tipo[p["tipo"]] = por_tipo.get(p["tipo"], 0) + 1
    print("OK", jp, por_tipo, "| a revisar:", [p["id"] for p in props if p["revisar"]])


if __name__ == "__main__":
    main()
