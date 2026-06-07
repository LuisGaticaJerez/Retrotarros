# Discusion · NES Top Mundial

Documento de trabajo: el "detras de escena" del armado del ranking. NO es la pauta.

---

## Por que este ranking y como se armo

El "top mundial" del canal es siempre el **ranking de calidad** (la contraparte del top precios). Para NES cruzamos el consenso historico/critico (IGN "Top NES Games", Nintendo Life, Edge, GamesRadar). No es la opinion personal de Luis: es lo que el mundo gamer considera lo mejor del catalogo 8 bits.

A diferencia del top precios (que tiene cifras objetivas), aca hay subjetividad. Por eso el episodio invita explicitamente a debatir en comentarios.

---

## El orden y sus polemicas

| # | Juego | Defensa | Polemica posible |
|---|-------|---------|------------------|
| 1 | Super Mario Bros. 3 | Consenso casi unanime como mejor NES. | Hay quien pone SMB original primero por importancia historica. |
| 2 | Super Mario Bros. | Salvo la industria, define el genero. | Algunos lo bajan por "envejecio" frente a SMB3. |
| 3 | The Legend of Zelda | Fundo la saga, mundo abierto en 1987. | Zelda II queda fuera (con razon). |
| 4 | Metroid | Raiz del metroidvania. | El backtracking sin mapa lo hace duro hoy. |
| 5 | Mega Man 2 | El Mega Man canonico, BSO eterna. | Mega Man 3 tiene defensores fuertes. |
| 6 | Punch-Out!! | Boxeo de patrones perfecto. | "Mike Tyson's" vs "Mr. Dream" (licencia). |
| 7 | Kirby's Adventure | Ultimo gran NES, copiar poderes. | Llego tan tarde que muchos lo asocian a SNES. |
| 8 | Contra | Run-and-gun + codigo Konami. | Super C tambien podria estar. |
| 9 | Ninja Gaiden | Cinematicas + velocidad. | Su dificultad injusta divide. |
| 10 | Castlevania III | Techo tecnico (VRC6). | En USA salio sin el chip (version inferior). |

---

## Decisiones duras (que quedo afuera)

- **Final Fantasy (1987/1990 US)**: fundacional para JRPG, pero fuera del top 10 por alcance masivo menor que los elegidos. Mencionable en vivo.
- **DuckTales**: el mejor licensed game, pero compite en "calidad pura" con pesos pesados. Va como joya en `nes-coleccion`.
- **Tetris (Nintendo)**: importantisimo comercialmente, pero el debate de version (Tengen vs Nintendo) lo complica.
- **Dragon Warrior / Dragon Quest**: historico para el JRPG occidental, pero hoy envejecio mucho.
- **Super Mario Bros. 2 (USA)**: el "raro" de la saga (reskin de Doki Doki Panic), no entra al top.

---

## Dato tecnico para lucirse en vivo

- **Castlevania III JP** usaba el chip **VRC6** dentro del cartucho para canales de audio extra. La version USA NO lo trae (NES yanqui bloqueaba chips de mapper distintos), por eso suena peor. Buen dato para Koko.
- **Kirby's Adventure** es de 1993, cuando la SNES ya llevaba 2-3 años. Que la NES diera ESO al final es flexear hardware.
- **The Legend of Zelda** fue de los primeros cartuchos con **bateria de guardado** en occidente (de ahi el cartucho dorado, era marketing).

---

## Anecdotas para Luis y Koko

- **Luis**: el cartucho dorado de Zelda y por que se veia distinto en la tienda.
- **Koko**: el aterrizaje imposible / la dificultad de Ninja Gaiden y Castlevania.
- **Compartida**: el tema de Dr. Wily de Mega Man 2 como mejor musica del 8 bits.
- **Compartida**: "The Wizard" (la pelicula) y el hype de SMB3 antes de salir.

---

## Decisiones de armado (2026-06-07)

1. Ranking de **consenso critico**, no opinion personal (se dice explicito).
2. Años en **release NTSC/US** (audiencia Latam juega NTSC).
3. **6 first-party** + Konami/Capcom/Tecmo: refleja la realidad de la NES (Nintendo manda, pero las 3rd parties pusieron clasicos).
4. Deck generado con `scripts/top_deck.py` (generador reutilizable nuevo). Sin box art todavia → etiqueta de color por juego (`cart-fallback`).
5. JSON TarroBot con 10 datos #10→#1 + reaccion_short por juego (reacciones con tildes para el TTS).

---

## Riesgos y como mitigarlos

| Riesgo | Mitigacion |
|--------|------------|
| "Tu ranking esta mal" en comentarios | Enmarcar como consenso critico + invitar al debate (engagement). |
| Sin gameplay grabado a tiempo | HTML con placeholder NO SIGNAL + etiqueta de color. |
| Datos tecnicos erroneos (chips, años) | Verificados aca; años en US. Si hay duda en vivo, no afirmar cifra exacta. |

---

**Ultima actualizacion:** 2026-06-07
**Pauta asociada:** `docs/pauta-nes-top-mundial.md`
**HTML:** `studio/nes-top-mundial.html`
