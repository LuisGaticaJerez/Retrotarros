"""Aplica la propuesta de hashtags y etiquetas a los videos del canal con la API de YouTube (OAuth de escritorio).

Seguro por defecto: sin --aplicar solo muestra el antes y el despues. Antes de escribir guarda un respaldo con la metadata real
(incluye las etiquetas verdaderas, que yt-dlp no entrega bien). Cambia SOLO la linea final de hashtags de la descripcion, las
etiquetas y, con --titulos, los hashtags escritos dentro del titulo. Lo demas del video queda igual.

Credencial: crea un cliente OAuth tipo "Aplicacion de escritorio" en Google Cloud (YouTube Data API v3 activada) y guarda el JSON como
.cache/youtube/client_secret.json. La primera vez abre el navegador para que tu inicies sesion y autorices; el permiso queda en
.cache/youtube/token.json (ambos fuera de git).

Uso:
  python scripts/youtube_aplicar.py --respaldo                    # solo baja y guarda la metadata real
  python scripts/youtube_aplicar.py [--solo id1,id2] [--titulos]  # prueba: muestra los cambios, no escribe
  python scripts/youtube_aplicar.py --aplicar [--solo ...]        # escribe (pide confirmar)
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / ".cache" / "youtube"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
HASHTAG = r"#[^\s#,]+"
RESTO_RE = re.compile(rf"{HASHTAG}|[,\s]")
BASURA = {"#fyp", "#fypシ", "#love", "#happy", "#inspiration", "#viral", "#instagood", "#follow", "#followme", "#youtube", "#beatifull",
          "#shortvideo", "#short", "#foryou", "#trending", "#collection"}


def servicio():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    token, secret = CACHE / "token.json", CACHE / "client_secret.json"
    creds = Credentials.from_authorized_user_file(str(token), SCOPES) if token.exists() else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not secret.exists():
                sys.exit(f"Falta {secret}. Mira las instrucciones al inicio de este archivo.")
            creds = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES).run_local_server(port=0)
        CACHE.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(token), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)   # el token da acceso al canal: solo el dueño lo lee
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        try:
            os.chmod(token, 0o600)
        except OSError:
            pass   # en Windows el permiso real lo da la carpeta del usuario; igual queda fuera de git (.cache/)
    return build("youtube", "v3", credentials=creds)


def leer_snippets(yt, ids: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet", id=",".join(ids[i:i + 50])).execute()
        for it in r.get("items", []):
            out[it["id"]] = it["snippet"]
    return out


CAMPOS_SNIPPET = ("title", "description", "categoryId", "tags", "defaultLanguage", "defaultAudioLanguage")


def cuerpo_snippet(video_id: str, sn: dict, **cambios) -> dict:
    """Cuerpo para videos().update(part="snippet"). Esa llamada REEMPLAZA el snippet completo: lo que no se reenvia se pierde
    (asi el idioma de audio quedo en en-US). Toda escritura de videos debe armar su cuerpo aqui: reenvia cada campo escribible
    tal como viene y aplica solo los cambios pedidos."""
    snippet = {k: sn[k] for k in CAMPOS_SNIPPET if sn.get(k)}
    snippet.update({k: v for k, v in cambios.items() if k in CAMPOS_SNIPPET})
    return {"id": video_id, "snippet": snippet}


def nueva_descripcion(desc: str, hashtags: list[str], limpiar_cuerpo: bool = False) -> str:
    """Quita la basura de otras redes, reemplaza el bloque final de hashtags y deja el resto del texto intacto."""
    if limpiar_cuerpo:   # quita CUALQUIER hashtag suelto dentro del texto (no solo la basura conocida) y restos como "゚viral"
        desc = re.sub(r"[ 	]*#(?!\d)\S*|゚\w*", "", desc)
    for b in BASURA:
        desc = re.sub(rf"(?i)(?<!\w){re.escape(b)}(?!\w)", "", desc)
    lineas = desc.rstrip().split("\n")
    while lineas and not RESTO_RE.sub("", lineas[-1]):   # linea vacia o hecha solo de hashtags y comas
        lineas.pop()
    cuerpo = "\n".join(l.rstrip() for l in lineas).rstrip()
    return (cuerpo + "\n\n" if cuerpo else "") + " ".join(hashtags)


def nuevo_titulo(titulo: str) -> str:
    return re.sub(r"\s*#(?!\d)\S+", "", titulo).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--propuesta", default=None)
    ap.add_argument("--solo", default="")
    ap.add_argument("--titulos", action="store_true", help="tambien quita los hashtags escritos dentro del titulo")
    ap.add_argument("--respaldo", action="store_true")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--limpiar-cuerpo", action="store_true", help="quita tambien los hashtags sueltos dentro del texto de la descripcion")
    ap.add_argument("--olvidar", action="store_true", help="borra el token guardado (termina la autorizacion en este PC) y sale")
    a = ap.parse_args()
    if a.olvidar:
        (CACHE / "token.json").unlink(missing_ok=True)
        print("Token borrado. Para revocar el permiso del todo: myaccount.google.com/permissions")
        return
    prop_path = Path(a.propuesta) if a.propuesta else sorted((REPO / "data" / "youtube").glob("propuesta-*.json"))[-1]
    props = {p["id"]: p for p in json.loads(prop_path.read_text(encoding="utf-8"))["videos"]}
    ids = [x for x in a.solo.split(",") if x] or list(props)
    yt = servicio()
    snips = leer_snippets(yt, ids)
    faltan = [i for i in ids if i not in snips]
    if faltan:
        print("AVISO: no son de este canal o no existen:", faltan)
    resp = REPO / "data" / "youtube" / f"respaldo-api-{time.strftime('%Y-%m-%d-%H%M%S')}.json"   # nunca pisa un respaldo anterior
    resp.write_text(json.dumps(snips, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Respaldo con la metadata real de {len(snips)} videos -> {resp}")
    if a.respaldo:
        return
    cambios = []
    for vid, sn in snips.items():
        p = props[vid]
        desc = nueva_descripcion(sn.get("description", ""), p["hashtags_nuevos"], a.limpiar_cuerpo)
        tags = p["etiquetas_nuevas"]
        titulo = nuevo_titulo(sn["title"]) if a.titulos else sn["title"]
        if desc == sn.get("description") and tags == sn.get("tags") and titulo == sn["title"]:
            continue
        cambios.append((vid, sn, titulo, desc, tags))
        print(f"\n== {vid} | {sn['title'][:60]}")
        if titulo != sn["title"]:
            print(f"   TITULO: {sn['title']!r} -> {titulo!r}")
        print(f"   HASHTAGS: {' '.join(re.findall(HASHTAG, sn.get('description', ''))[-8:])}  ->  {' '.join(p['hashtags_nuevos'])}")
        print(f"   ETIQUETAS ({len(sn.get('tags', []))} -> {len(tags)}): {', '.join(tags[:8])}...")
    print(f"\n{len(cambios)} videos cambiarian de {len(snips)}.")
    if not a.aplicar:
        print("Modo prueba: no se escribio nada. Usa --aplicar para escribir.")
        return
    if input(f"Escribir {len(cambios)} cambios en YouTube (cuesta {50 * len(cambios)} de 10000 unidades de cuota)? escribe SI: ").strip() != "SI":
        sys.exit("Cancelado.")
    ok = 0
    for vid, sn, titulo, desc, tags in cambios:
        try:
            yt.videos().update(part="snippet", body=cuerpo_snippet(vid, sn, title=titulo, description=desc, tags=tags)).execute()
            ok += 1
            print(f"OK {vid}")
        except Exception as e:  # noqa: BLE001
            print(f"ERROR {vid}: {e}")
            if "quota" in str(e).lower():
                break
        time.sleep(0.5)
    print(f"Listo: {ok} de {len(cambios)} aplicados.")


if __name__ == "__main__":
    main()
