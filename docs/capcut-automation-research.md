# Research · automatización de CapCut

> **Estado:** PAUSADO 2026-05-18. El research mostró que el ROI no justifica el esfuerzo para la cadencia actual (~1 teaser/semana). Workflow manual con tarroteaser + CapCut manual sigue siendo lo recomendado.
>
> Este doc preserva los findings por si en el futuro queremos retomar (3+ teasers/semana o producto SaaS).

## Lo que se buscaba

Generar archivos de proyecto CapCut (`.draft`) programáticamente desde `tarroteaser.py` con:
- MP4 del teaser ya cargado en timeline
- Voice Enhancement aplicado automático (quita música del master)
- Lower-thirds con título del episodio
- Intro/outro pre-cargados
- Música de fondo según paleta

Resultado: vos abrís CapCut → ves el proyecto listo → solo pulís lo que quieras.

## Findings técnicos (verificados 2026-05-18)

### Estructura de proyectos CapCut Global Windows

**Ubicación:** `C:\Users\Balbr\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\<projectId>\`

**Archivos clave por proyecto:**
| Archivo | Tamaño | Rol |
|---|---|---|
| `draft_content.json` | 12 KB - 612 KB | **Timeline + materials + tracks** (lo crítico) |
| `draft_content.json.bak` | igual | Backup automático |
| `draft_meta_info.json` | 27 KB | Metadata (nombre, fechas, cover) |
| `draft_agency_config.json` | 5.7 KB | Config de cuenta CapCut |
| `crypto_key_store.dat` | 421 B - 7 KB | **Clave de encriptación** (ver abajo) |
| `attachment_editing.json` | 2.5 KB | Estado de edición UI |
| `Resources/`, `Timelines/`, `adjust_mask/` | varía | Recursos auxiliares |
| `.locked` (a veces) | 0 B | Marker - significado incierto |

### ⚠️ Encriptación parcial

**Observación clave:** algunos proyectos del mismo CapCut tienen `draft_content.json` como **JSON plano legible**, otros están **encriptados con base64-like** (no JSON válido al parsear).

Muestra concreta del PC de Luis (2026-05-18):
- `0507` (mayo 16): **JSON plano** · versión schema 360000 · CapCut 167.0.0
- `0508` (mayo 10): **encriptado** (`cE48NU7jdCDivEIMldFpjJ44zdS2OTsK...`)
- `0509` (mayo 12): **encriptado**
- `0513` (mayo 17): **JSON plano**
- `0516` (mayo 18): **JSON plano**, tiene `.locked`

**Hipótesis:** CapCut introdujo encriptación en alguna versión entre mayo 10-12 y la revirtió/desactivó en versiones posteriores. O hay flag de cuenta que la activa. Necesita validación si retomamos.

### Schema base del JSON plano

```json
{
  "id": "BC413E14-5574-4b03-B794-DADE95BDA126",  // UUID del proyecto
  "version": 360000,                              // Schema version (estable)
  "new_version": "167.0.0",                       // Versión de CapCut
  "name": "",                                     // Nombre visible
  "duration": 1695800000,                         // Microsegundos
  "fps": 30.0,
  "canvas_config": {"width": 1920, "height": 1080},
  "tracks": [...],                                // Pistas (video, audio, texto)
  "materials": {
    "videos": [...],
    "audios": [...],
    "texts": [...],
    "effects": [...],                              // Filtros visuales
    "audio_effects": [...],                        // Voice Enhancement va acá
    "audio_fades": [...],
    "transitions": [...],
    "stickers": [...]
    // + decenas de otras categorías
  },
  "config": {...}
}
```

### Lo que NO pudimos verificar

- Cómo se representa **Voice Enhancement** en `materials.audio_effects` — los proyectos del PC de Luis no tenían el efecto aplicado.
- Schema exacto de **transitions** y **lower-thirds**.
- Si CapCut acepta proyectos generados externos o requiere firma criptográfica (probable que NO requiera dado que el JSON es plano).
- Si la encriptación parcial es bug, feature regional o trigger de cuenta.

## Para retomar este research

**Fase 2 propuesta** (la que pausamos): Luis crea **un proyecto sample** con:
1. Importar 1 MP4 cualquiera
2. Aplicar Voice Enhancement
3. Agregar 1 texto / lower-third
4. Importar 1 música de fondo
5. Guardar

Después yo inspecciono ese `draft_content.json` y mapeo:
- Estructura de `audio_effects[*]` para Voice Enhancement
- Estructura de `texts[*]` y su track
- Cómo se vinculan tracks ↔ materials por IDs

**Fase 3 - Implementación:**
- `scripts/tarrocapcut.py` que toma output de tarroteaser + slug + título
- Genera carpeta con `draft_content.json` + `draft_meta_info.json` mínimos válidos
- Coloca en `C:\Users\Balbr\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\<slug>\`
- Voice Enhancement pre-aplicado al video clip
- Lower-third con título inferido del slug
- (Opcional) intro/outro cargados, música seleccionada

## Alternativa: `pyJianYingDraft` (no validada)

Librería Python open source que genera proyectos para JianyingPro (CapCut chino, mismo motor original). GitHub: `GuanYixuan/pyJianYingDraft`.

**Sin validar:** si funciona con CapCut Global versión 167+. Schema 360000 puede diferir entre forks. Probar antes de adoptar.

## Decisión de archivo

- ✅ Workflow actual mantiene: `tarroteaser.py` genera MP4 → user importa a CapCut → aplica Voice Enhancement manual → publica.
- ⏸️ Retomar este research SI: la cadencia sube a 3+ teasers/semana, o si decidimos volver al ángulo SaaS multi-tenant.

---

*Documentado por Claude · 2026-05-18*
