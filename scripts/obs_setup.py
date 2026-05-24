"""
obs_setup.py - Sprint 18 - Retrotarros Studio Suite

Auto-setup de OBS con el template "Retrotarros Standard": 9 escenas, sources
basicos, audio + browser source apuntando a la TarroVision live.

NO sobreescribe lo que ya exista (idempotente). Solo crea lo que falte.
Dry-run primero para que el operador apruebe antes de ejecutar.

Uso:
    from obs_setup import RETROTARROS_TEMPLATE, apply_template
    result = await apply_template(obs_client, dry_run=True)
    # ... usuario aprueba ...
    result = await apply_template(obs_client, dry_run=False)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Optional


# ────────────────────────────────────────────────────────────────────
# Template "Retrotarros Standard"
# ────────────────────────────────────────────────────────────────────
#
# 9 escenas: general, tarrobot, koko, luis, intro, outro, transition,
# closeup-cartucho, closeup-caja.
#
# Sources clave:
#   - 'tarrobot-live': Browser Source apuntando a http://localhost:8001/live
#     que se inserta en la escena tarrobot.
#   - 'lower-third': Text source para titulos dinamicos (Sprint 18 D).
#
# Audio: no creamos mic capture automatico (depende del hardware del operador).
# Solo dejamos los Inputs Mixer en la config global de OBS.

@dataclass
class TemplateScene:
    name: str
    description: str = ""


@dataclass
class TemplateInput:
    """Input (source) a crear si no existe."""
    input_name: str
    input_kind: str           # browser_source, text_ft2_source_v2, etc
    input_settings: dict = field(default_factory=dict)
    parent_scene: str | None = None  # si se debe insertar como source en una escena


# Template canonico Retrotarros Standard
RETROTARROS_TEMPLATE = {
    "version": "1.0",
    "scenes": [
        TemplateScene("intro",            "Cortina de entrada del episodio"),
        TemplateScene("cam-cenital",      "Plano cenital de la mesa (escena general)"),
        TemplateScene("cam-luis",         "Camara apuntando a Luis"),
        TemplateScene("cam-koko",         "Camara apuntando a Koko"),
        TemplateScene("tarrobot-full",    "TarroVision a pantalla completa (cuando TarroBot habla)"),
        TemplateScene("closeup-cartucho", "Close-up del cartucho sobre la mesa"),
        TemplateScene("closeup-caja",     "Close-up de la caja del juego"),
        TemplateScene("transition",       "Cortina entre bloques"),
        TemplateScene("outro",            "Despedida del episodio"),
    ],
    "inputs": [
        TemplateInput(
            input_name="tarrobot-live",
            input_kind="browser_source",
            input_settings={
                "url": "http://localhost:8001/live",
                "width": 1920,
                "height": 1080,
                "reroute_audio": False,
                "shutdown": False,
                "restart_when_active": False,
            },
            parent_scene="tarrobot-full",
        ),
        TemplateInput(
            input_name="lower-third",
            input_kind="text_ft2_source_v2",
            input_settings={
                "text": "",
                "font": {"face": "Orbitron", "size": 28, "style": "Bold", "flags": 0},
                "outline": True,
                "drop_shadow": True,
                "color1": 4294967295,  # 0xFFFFFFFF blanco
            },
            parent_scene="cam-cenital",
        ),
    ],
    "default_scene_after_setup": "cam-cenital",
}


# ────────────────────────────────────────────────────────────────────
# Diff: que falta crear
# ────────────────────────────────────────────────────────────────────

async def diff_template(client, template: dict | None = None) -> dict:
    """Compara el estado actual de OBS con el template. Devuelve plan.

    Plan = {
        scenes_to_create: [...],
        scenes_existing: [...],
        inputs_to_create: [...],
        inputs_existing: [...],
        notes: [...]
    }
    """
    tpl = template or RETROTARROS_TEMPLATE
    plan = {
        "scenes_to_create": [],
        "scenes_existing": [],
        "inputs_to_create": [],
        "inputs_existing": [],
        "notes": [],
    }

    # 1) Escenas
    try:
        sl = await client.get_scene_list()
        existing_scenes = {s.get("sceneName", "") for s in sl.get("scenes", [])}
    except Exception as e:
        plan["notes"].append(f"no se pudo listar escenas: {e}")
        return plan

    for sc in tpl["scenes"]:
        if sc.name in existing_scenes:
            plan["scenes_existing"].append({"name": sc.name})
        else:
            plan["scenes_to_create"].append(asdict(sc))

    # 2) Inputs
    try:
        il = await client._request("GetInputList")
        existing_inputs = {i.get("inputName", "") for i in il.get("inputs", [])}
    except Exception as e:
        plan["notes"].append(f"no se pudo listar inputs: {e}")
        existing_inputs = set()

    for inp in tpl["inputs"]:
        if inp.input_name in existing_inputs:
            plan["inputs_existing"].append({"name": inp.input_name, "kind": inp.input_kind})
        else:
            plan["inputs_to_create"].append({
                "name": inp.input_name,
                "kind": inp.input_kind,
                "parent_scene": inp.parent_scene,
            })

    return plan


# ────────────────────────────────────────────────────────────────────
# Apply: crear lo que falta
# ────────────────────────────────────────────────────────────────────

async def apply_template(
    client,
    template: dict | None = None,
    dry_run: bool = True,
) -> dict:
    """Crea las escenas/inputs faltantes.

    Si dry_run=True, solo devuelve el plan sin tocar nada.
    Si dry_run=False, crea y devuelve {created, skipped, errors}.

    Idempotente: jamas sobreescribe lo que ya existe.
    """
    tpl = template or RETROTARROS_TEMPLATE
    plan = await diff_template(client, tpl)

    if dry_run:
        return {
            "dry_run": True,
            "plan": plan,
            "would_create_scenes": len(plan["scenes_to_create"]),
            "would_create_inputs": len(plan["inputs_to_create"]),
        }

    created = {"scenes": [], "inputs": []}
    skipped = {"scenes": [s["name"] for s in plan["scenes_existing"]],
               "inputs": [i["name"] for i in plan["inputs_existing"]]}
    errors = []

    # 1) Crear escenas
    for sc in plan["scenes_to_create"]:
        try:
            await client._request("CreateScene", {"sceneName": sc["name"]})
            created["scenes"].append(sc["name"])
        except Exception as e:
            errors.append({"target": f"scene:{sc['name']}", "error": str(e)})

    # 2) Crear inputs (en su parent_scene si esta seteada, sino en la default actual)
    default_scene = tpl.get("default_scene_after_setup")
    # Buscar la version full de cada input desde el template (no del plan que es resumen)
    inputs_by_name = {i.input_name: i for i in tpl["inputs"]}

    for inp_entry in plan["inputs_to_create"]:
        inp = inputs_by_name.get(inp_entry["name"])
        if not inp:
            continue
        target_scene = inp.parent_scene or default_scene
        if not target_scene:
            errors.append({"target": f"input:{inp.input_name}", "error": "no hay parent_scene ni default"})
            continue
        try:
            await client._request("CreateInput", {
                "sceneName": target_scene,
                "inputName": inp.input_name,
                "inputKind": inp.input_kind,
                "inputSettings": inp.input_settings,
                "sceneItemEnabled": True,
            })
            created["inputs"].append({"name": inp.input_name, "scene": target_scene})
        except Exception as e:
            errors.append({"target": f"input:{inp.input_name}", "error": str(e)})

    return {
        "dry_run": False,
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "plan": plan,
    }
