# Formato RETRONOTA — diseño aprobado

> Diseñado con Luis a partir de las ideas de inspiración de YouTube Studio (varias
> propuestas de tema no calzaban ni en Reseña ni en TarroShort ni en episodio largo con
> ranking — de ahí la necesidad de un formato nuevo). Aprobado 2026-08-17 via preguntas
> de diseño directas (talento, cierre, estructura interna). Implementación pendiente.

## Qué es

Formato nuevo del canal: **reportaje temático**, 15-20 minutos. No gira en torno a UN
juego (como Reseña) ni es un ranking/countdown de N ítems (como episodios largos y
Specials) — cubre un **tema cultural, histórico o técnico** del mundo retro, casi
siempre con ángulo regional chileno/latam (escena arcade chilena, cybercafés y CS 1.6,
piratería de los 90, localizaciones que nunca llegaron a Sudamérica, leyendas urbanas de
arcades). Llena el vacío entre "10 min sobre un juego" y "25 min de ranking con batería".

## Decisiones clave (por qué, no solo qué)

- **Luis + Coco presentan juntos, conversando/investigando en cámara** — a diferencia de
  Reseña (que los separa 1 y 1) y de Specials (que es Luis leyendo con Koko de
  contrapeso). Decisión de Luis: la RetroNota es más un dúo de investigación que un show
  solista o un sketch burocrático.
- **NUNCA cierra con Koko tocando batería.** Misma lógica que Reseña: mantiene el tono
  de reportaje/documental distinto al show de los episodios largos, que sí cierran con
  batería como firma del formato.
- **Estructura en capítulos temáticos, no countdown.** A diferencia de los rankings
  (#10→#1) y los Specials (item por item con documento burocrático), la RetroNota se
  arma como una historia: gancho → origen/contexto → desarrollo → impacto/legado →
  cierre. Sin numeración de posición.
- **Regla nueva y obligatoria: distinguir HECHO VERIFICADO de MITO/LEYENDA en pantalla.**
  Este formato es el de mayor riesgo de sonar "más autorizado de lo que es" — un
  reportaje suena a verdad comprobada por defecto. Cuando el tema toca folclore o
  leyenda urbana (ej. "Chilean Polybius"), cada slide debe llevar una etiqueta visual
  clara (`HECHO VERIFICADO` vs `MITO / LEYENDA URBANA`) para que la audiencia nunca
  confunda especulación con dato duro. Extiende la regla general del canal ("toda
  afirmación histórica debe poder defenderse") al caso específico de contenido de
  folclore, que antes no existía en el catálogo.
- **Tono:** conversacional-investigativo, no académico ni solemne — mismo registro base
  del canal, pero con menos chiste denso que un Special y más profundidad que un
  TarroShort.

## Estructura del deck (5 bloques, sin numero fijo de slides — depende del tema)

1. **Gancho / pregunta** — plantea el misterio o la pregunta que el reportaje va a
   responder (ej. "¿qué pasó con los cybercafés chilenos?").
2. **Origen / contexto** — de dónde viene el tema, antecedentes necesarios para entender
   el resto.
3. **Desarrollo** — el cuerpo del reportaje: casos concretos, ejemplos, evidencia. Puede
   ser el bloque más largo y el único con multiples slides internos.
4. **Impacto / legado** — qué dejó el tema, cómo se conecta con el presente.
5. **Cierre** — reflexión + CTA de suscripción (sin batería).

## Implementación (pendiente, próxima sesión)

- Nuevo generador `scripts/retronota_deck.py` — no reutiliza `special_deck.py` tal cual
  porque no hay "items" numerados, sino bloques de contenido variable (texto largo,
  fotos de archivo, testimonios, datos con fuente citada). Puede reutilizar CSS base
  (paleta, header, nav) de los generadores existentes.
- Necesita un tipo de slide nuevo para el tag `HECHO VERIFICADO` / `MITO / LEYENDA
  URBANA` — no existe hoy en ningún generador del canal.
- Carpeta de salida sugerida: `studio/retronotas/<slug>.html` (mismo patrón de carpeta
  separada que Reseñas).
- Convención de pautas: aplica el trío completo `pauta-retronota-<slug>.md` +
  `discusion-retronota-<slug>.md` + HTML, igual que el resto de formatos largos.

## Candidatos de tema para el episodio piloto

De las ideas de inspiración de YouTube Studio revisadas el 2026-08-17:

- **The Secret Chilean Arcade Scene** (Regional History) — escena arcade chilena de los 90.
- **The Chilean Polybius** (Gaming Folklore) — leyenda urbana de arcades embrujados en
  Santiago. Requiere aplicar la regla de etiquetado MITO/LEYENDA de forma estricta.
- **Chilean Cybercafes and the Counter-Strike 1.6 Phenomenon** (Social Impact).
- **How Chilean piracy culture saved the legacy of 90s PC gaming history** (Regional Curiosities).
- **The Lost Localizations: juegos que nunca llegaron a Sudamérica** (Regional History) —
  coincide con el "SNES NO-LATAM" ya anotado como próximo especial en la pauta de
  Glorias Navales; podría resolverse como RetroNota en vez de Special.

## Pendiente

- Elegir tema del episodio piloto (conversación siguiente con Luis).
- Construir `scripts/retronota_deck.py` una vez elegido el piloto (mockup real primero,
  no solo descrito — mismo método que se uso para cerrar el formato Reseña).
- Definir si la RetroNota tiene playlist propia en YouTube o vive dentro de "Specials"/
  episodios largos.
