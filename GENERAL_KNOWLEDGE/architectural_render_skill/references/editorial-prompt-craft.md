# Editorial Architectural Render Prompt Craft

Use this reference when composing the brief for the `image-generator` subagent (or the consolidated fallback prompt). Every render must read like an authentic, museum-grade architectural photograph published in *ArchDaily*, *Dezeen*, *El Croquis*, or produced by *MIR* / *Luxigon*—never like generic AI art, oversaturated real-estate CGI, or geographically impossible fantasy terrain.

---

## 0. Site Reality Lock (Mandatory First Section of Every Prompt)

**Always open the brief by locking the real geography before describing the building.** Image generators default to generic "architectural paradise" tropes (turquoise ponds, rolling hills, lush lawns, dramatic cliffs) unless explicitly constrained.

Include all four lines in every prompt:
1. **Topography Lock**: State exact ground relief from GIS / `*_site_context.md` (e.g., *"Strictly flat Nile Valley alluvial plain (0–2% slope), extending level to the horizon"* or *"Flat arid gravel desert plain with low distant limestone mesas"*).
2. **Hydrology Lock**: State exact real water presence and position (e.g., *"Wide Nile River channel strictly along the northeast edge; dry built ground everywhere else"* or *"Bone-dry ephemeral Sinai desert gravel wadi; zero standing water, zero flowing stream"*).
3. **Cardinal Context Lock**: State real surrounding land cover by direction (e.g., *"Dense 3–5 story Upper Egypt red-brick and weathered-concrete urban blocks to the west; flat rectilinear agricultural fields to the south and east"*).
4. **Explicit Forbidden Landscape Features**: Name the exact hallucinations to exclude for that site:
   - *Flat plain site*: **"Strictly NO hills, NO cliffs, NO mountains, NO rocky bluffs, NO undulating parkland."**
   - *Dry / ephemeral wadi or inland site*: **"Strictly NO turquoise ponds, NO artificial lakes, NO flowing perennial rivers, NO waterfalls, NO lush green riverbanks."**
   - *Arid Egyptian / desert site*: **"Strictly NO European manicured lawns, NO dense tropical rainforests, NO pine forests."**

### De-Metaphorizing Trigger Words (Critical)
Never copy poetic project titles or marketing metaphors directly into the visual prompt—image models read them literally and hallucinate landscape features:

| Poetic / Metaphorical Term | Why It Fails | Literal Physical Replacement for Prompt |
|---|---|---|
| *"Cooling-Hill"* / *"Terraced Hill"* | Model invents rocky hills/cliffs on flat farmland | *"Low stepped earth-bermed architectural plinth rising gently from a dead-flat plain"* |
| *"Oasis"* / *"Water Sanctuary"* | Model invents a giant turquoise lagoon or pond | *"Shaded stone-paved desert courtyard with sparse native date palms and dry limestone benches"* |
| *"Wadi Hydro-Citadel"* / *"Flood Harvesting"* | Model invents a gushing alpine river & waterfalls | *"Dry stepped limestone check-dam terraces and subterranean cistern openings spanning a dry arid gravel wadi bed"* |
| *"Urban Cooling Forest"* | Model invents dense temperate woodland | *"Grid of native Upper Egypt acacia, sycamore, and date-palm shade canopies with dappled shadows over dry pale earth and stone paving"* |

---

## 1. Aerial Camera & Lens Grammar

Always frame from a real-world aerial photography perspective (medium-format camera mounted on a professional drone or helicopter), **16:9 widescreen** by default:

- **Classic Hero Aerial (~40–45° pitch)** *(Default)*: Elevated three-quarter aerial perspective showing the entire architectural complex, its full footprint, massing hierarchy, roofscape, and immediate real urban or natural context. Generous breathing room around the site edges so no primary volume is cropped.
- **Low Oblique Aerial (~25–35° pitch)**: Lower drone vantage point that captures the full project silhouette against the true horizon, emphasizing facade articulation, cantilevers, and ground-plane arrival while keeping the entire massing legible.
- **High Context Aerial (~55–65° pitch)**: Steep bird's-eye architectural view emphasizing masterplan organization, courtyard sequence, roof geometry, circulation axes, and exact alignment with the real roads, river edge, or urban grid.

**Mandatory Optical Rules:**
- Crisp, deep depth-of-field across the entire frame (`f/8`–`f/11` equivalent). **Never** use shallow depth-of-field or miniature tilt-shift blur (which makes architecture look like a toy model).
- Natural rectilinear architectural lens (35mm–50mm full-frame equivalent) with controlled perspective and zero fisheye distortion.
- Subtle natural atmospheric perspective in the far distance to convey true architectural scale.

---

## 2. Lighting & Atmosphere Modes

### Overcast / Soft Diffused Daylight *(Default)*
- Even, luminous overcast sky acting as a giant softbox; soft ambient occlusion in recesses, overhangs, and courtyards.
- Restrained, desaturated editorial color grading (neutral cool-gray sky, true-to-life muted material tones).
- Ideal for pure massing legibility and honest material expression.

### Golden Hour
- Low-angle late-afternoon sun raking across facades, casting long crisp sculptural shadows that reveal relief, louvers, and massing depth.
- Warm natural sunlight balanced by cool shadows—restrained and filmic, never neon orange or heavily saturated HDR.

### Blue Hour / Dusk
- Deep twilight cobalt/slate sky just after sunset with subtle horizon gradient.
- Soft warm interior architectural lighting (`2700K–3000K`) glowing gently through glazing, courtyards, and recessed soffits—never blown-out white or harsh neon.

### Harsh Desert / Mediterranean Sun
- High-clarity arid sky, intense directional sunlight, sharp dark shadow geometry under deep overhangs, brise-soleil, and colonnades.
- Subtle dusty warm atmospheric haze on the distant horizon; pale calcareous earth and xeriscaped native planting.

### Rainy / Misty Atmosphere
- Fine mist or low coastal cloud softening the distant background; damp stone/concrete paving with subtle specular reflections.
- Moody Nordic/Japanese editorial sensibility with muted greens, dark wet surfaces, and quiet warm interior accents.

---

## 3. Material Honesty & Architectural Detailing

Describe materials with real tectonic behavior rather than buzzwords:
- **Concrete**: Board-formed or cast-in-place architectural concrete with subtle formwork tie-holes, slight tonal variation, and clean drip edges.
- **Stone / Earth**: Honed travertine, stacked local limestone, or layered rammed earth with realistic coursing and weathering.
- **Timber**: Weathered cedar, charred sugi ban, or natural oak slats showing subtle grain variation.
- **Metal**: Matte anodized aluminum, patinated zinc, blackened steel, or muted bronze mullions with slender realistic profiles.
- **Glazing**: Low-iron architectural glass with realistic subtle sky/context reflection and faint interior spatial depth (slabs, columns, warm ceilings visible behind glass—never flat solid black or mirror-chrome boxes).
- **Roofscape**: Intentional architectural roofs—gravel ballast, planted arid green roofs, recessed mechanical screens, skylights, or sculpted solar canopies—never messy random rooftop clutter.

---

## 4. Balanced Conceptual Translation (Image-to-Render & Satellite Anchoring)

When a **satellite site crop**, sketch, clay massing screenshot, Revit/Rhino/SketchUp viewport, or site plan is provided:
- **Preserve**: Real site topography, true water/river edges, existing roads, neighboring urban/agricultural fabric, building footprint logic, relative height hierarchy, and site orientation.
- **Elevate & Refine**: Translate rough or placeholder surfaces into resolved architectural facades (coherent structural grid, glazing rhythm, shading devices, parapets, roof detailing) and integrate realistic grading, paving, and regionally accurate native landscape.
- **Explicit Instruction to Include in Brief**:
  > "Use the provided reference image as the strict geographic and site-organization foundation. Preserve the real terrain flatness/relief, true water edges, road alignments, and neighboring urban/agricultural fabric exactly as shown, while translating the architectural intervention into a cohesive photorealistic editorial aerial photograph."

---

## 5. Entourage & Context Realism

- **Scale Figures**: Sparse, candid, properly scaled human figures walking or gathering naturally—never crowded stock-photo groups or stiffly posed figures.
- **Vehicles**: Minimal, understated, muted-color modern vehicles only where roads/parking logically exist—never bright red sports cars or floating cars.
- **Vegetation**: Regionally accurate, organically varied native trees and shrubs at realistic desert/Nile density with dappled shadows—never repetitive copy-pasted bright-green spheres or ungrounded parkland lawns.
- **Surrounding Context**: Authentic, believable neighboring fabric (e.g., weathered Egyptian brick/plaster housing, flat agricultural parcels, pale desert gravel) that anchors the project in its real place.

---

## 6. Mega-National Landmark & Competition Hero Cues *(NEST Default)*

When rendering mega national landmarks governed by `GENERAL_KNOWLEDGE/mega_landmark_architectural_direction.md`, elevate the brief to an international competition-winning hero image (*MIR / Luxigon / ArchDaily* flagship caliber) **without ever violating the Site Reality Lock**:
- **Lead with the Single Boldest Architectural Gesture:** Describe the unmistakable built *parti* (e.g., sweeping perforated solar-canopy vault, sculpted limestone thermal-chimney towers, carved desert monolith) grounded directly in the site's *true* terrain.
- **Convey Territorial Scale Honestly:** Pair authentic local geography (only features that actually exist on that plot) with tiny human scale figures and real neighboring context so monumental scale reads effortlessly.
- **Tectonic & Climatic Honesty:** Show how the monumental form *is* the ecological engine—deep cast shadows under vast overhangs, thermal chimneys, dry flood-retention terraces, and authentic regional Egyptian stone/earth/metal textures rather than unshaded glass boxes.
- **Hero Angle Choice:** Use **Classic Hero Aerial (~40–45°)** for full footprint + roofscape legibility, or **Low Oblique Aerial (~25–35°)** when a dramatic silhouette against the real horizon is the defining hook.

---

## 7. Anti-Cliché Guardrails (What to Explicitly Avoid)

Always steer the generator away from:
- Invented water bodies (ponds, lagoons, waterfalls, canals) or invented relief (hills, cliffs, mountains) not present on the real GIS site.
- Oversaturated HDR sunsets, purple/magenta skies, lens flares, or glowing bloom halos.
- Miniature tilt-shift blur or diorama/toy-model appearance.
- Gibberish text, fake signage, watermarks, logos, or floating UI labels.
- Impossible structural cantilevers, melted mullions, warped perspective lines, or floating stairs/columns.
- Generic glossy "futuristic sci-fi" blobs unless explicitly requested by the user.
