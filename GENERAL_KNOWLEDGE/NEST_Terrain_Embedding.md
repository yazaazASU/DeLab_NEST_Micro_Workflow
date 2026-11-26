# NEST — Terrain-Embedded Architecture & DEM Applicability Intelligence

## 1. Purpose & Design Philosophy: Earn the Carve, Never Force It
Two architectural families coexist inside NEST's 50–70 feddan masterplanning pipeline:

1. **Terrain-Embedded Landform Architecture (`mode: "embedded"`):** Long, low, contour-aligned linear bars, shelf-cut ledges, stepped wadi retaining walls, sunken circular skylight pits, and walkable roofs that read as a continuation of the geological ground rather than an object placed upon it.
2. **Free-Standing Sculptural Architecture (`mode: "free_standing"`):** Aerodynamic thin shells on reversible pins, climatic solar-vault canopies over flat transit/market concourses, and compact vertical climate spires where lifting off or rising above the ground is the core ecological move.

**Core Rule:** *Never force terrain-embedding onto a flat parcel or onto a tectonic idiom whose ecological logic depends on lightness, clear-span canopy shade, or vertical footprint compression.* Conversely, whenever a site possesses real topographic relief, coherent slope contours, or a coastal/wadi shelf edge—and its architectural idiom benefits from thermal mass and horizon preservation—the building should **dissolve into the terrain**.

---

## 2. Measured DEM Applicability Test (`terrain_intelligence.py`)

For every candidate parcel, NEST fetches and caches a 30 m Digital Elevation Model (`SRTM 30 m` via OpenTopoData with Open-Meteo elevation fallback) in local meters centered at `(0, 0)` (matching `rhino_massing_engine.py`), shifted to `z_ref` = lowest elevation inside the site boundary so all site geometry remains `Z >= 0`.

### 2.1 Four Measured Terrain Signals (Evaluated Inside the Non-Preserve Buildable Envelope)
1. **Mean Slope (`slope_mean_deg`, 0–45 pts):** `45 * min(slope_mean_deg / 9.0, 1.0)`
2. **Buildable Relief (`relief_m`, 95th − 5th percentile elevation, 0–25 pts):** `25 * min(relief_m / 22.0, 1.0)`
3. **Contour Coherence (`coherence` $R \in [0, 1]$, 0–15 pts):** Doubled-angle gradient vector resultant measuring whether slopes face one consistent direction (`R >= 0.55` = clean parallel contours) vs. chaotic micro-undulations: `15 * clip((R - 0.30) / 0.50, 0, 1)`
4. **Coastal / Wadi Shelf Edge (`shelf_edge`, 0 or 15 pts):** `+15 pts` when sea-level/channel cells (`<= 1 m`) sit within `250 m` of raised buildable ground (`>= 4 m`), creating a natural geological ledge.

### 2.2 Dual Gate: Topographic Threshold + Tectonic Idiom Compatibility
Terrain-embedding (`mode = "embedded"`) activates **if and only if ALL three conditions hold**:
1. **Score Gate:** `Total Applicability Score >= 50.0 / 100`
2. **Physical Relief Sanity Gate:** Either `(slope_mean_deg >= 3.5° AND relief_m >= 8.0 m)` **OR** `(shelf_edge == True AND relief_m >= 4.0 m)`
3. **Idiom Compatibility Gate:**
   - **Eligible Idioms** (gain thermal mass, wind shelter, and unbroken horizon):
     - `Carved Landform & Geological Monumentality` (`landform`)
     - `Hydrological & Ecological Sculpture` (`hydrological`)
   - **Protected Free-Standing Idioms** (never forced underground/into bars even on sloped sites—though they still sit accurately on the 3D DEM terrain surface!):
     - `Parametric Shells & Tensile Structures` (`shell` — reversible point-footings, zero excavation)
     - `Climatic Mega-Canopies & Solar Vaults` (`canopy` — tall porous civic concourse beneath floating PV vaults)
     - `Biophilic Vertical & Terraced Megastructures` (`vertical` — compact stacked spire freeing >85% of the ridge)

Every project stores its full `terrain_analysis` dictionary (`mode`, `typology`, `score`, `score_parts`, `slope_mean_deg`, `relief_m`, `coherence`, `contour_dir_deg`, `shelf_edge`, `verdict`, `reasons`) inside `stage_b_projects.json` and surfaces it transparently in the dashboard.

---

## 3. The Three Terrain-Embedded Typologies

When `mode == "embedded"`, the engine selects one of three site-specific tectonic typologies aligned to `contour_dir_deg`:

| Typology Key | Trigger Condition | Spatial & Architectural DNA | Signature Voids & Landscape Integration |
|---|---|---|---|
| **`coastal_shelf_cut`** | `shelf_edge == True` | Low, crisp coral-limestone / sandstone linear wedges & shelf bars cut parallel to the coastal terrace behind the `Preserve` buffer; walkable gravel/stone roofs flush with the upper desert shelf. | Circular sunken skylight wells (`4–8 m` dia.) punched through the stone roof, shaded colonnade slots facing the sea, and stepped rock-cut tidal/cooling basins along the terrace rim. |
| **`wadi_terrace_bars`** | `coherence >= 0.55` (and no coastal shelf) | 2–4 parallel stepped linear bars terraced down the cross-slope along contours, anchored by dry-stacked stone retaining walls and solar-shaded roof pergolas. | Shaded canyon slots between bars funneling cool down-valley breezes, stepped check-dam micro-catchment terraces, and earth-bermed up-slope backs that blend seamlessly into the hillside. |
| **`ridge_berm_bars`** | `coherence < 0.55` on high-relief headland/ridge | Angular/faceted stone-and-rammed-earth monolith bars tucked just below the ridge crest with sloped earthen berms banking up against windward walls. | Deep carved open-sky stargazing/botanical courts cut inside the mass, canyon entry ramps, and zero skyline protrusion above the natural ridge profile. |

---

## 4. Gains-Preserving Invariants (Zero Regression Contract)

Switching a site to `mode: "embedded"` **must preserve 100% of NEST's analytical and interactive capabilities**:
1. **Exact GFA Lock (`±3%`):** Stepped terrace bars / shelf-cut wedges are auto-calibrated so total modeled GFA matches `built_gfa` within `±3%` (`0.0%` target variance).
2. **Zero Preserve-Zone Encroachment:** All embedded bars, retaining walls, and sunken courts are clipped/placed strictly outside `Preserve` zones (except `bridge_or_pile_allowed: true` elevated boardwalks).
3. **Co-Located Multi-Use `interior_zones` + Ghosted 3D Inspection:** Clicking any embedded bar in the Live 3D WebGL viewer ghosts its stone roof/walls (`opacity: 0.22`) to reveal the color-coded 3D interior program blocks seated at its exact terrain elevation, synced to the left-hand **Inside Mass** tab.
4. **Unified 3D DEM Terrain Surface Everywhere:**
   - **Rhino 8 (`.3dm`):** `00_TERRAIN_DEM` triangulated 3D terrain mesh + `02_BUILDING_MASSING` seated directly into the slope (with retaining aprons extending cleanly down to grade so zero masses float in mid-air).
   - **Matplotlib 3D Clay Locks (`site_<N>_massing_lock.png` & `_clean.png`):** Shaded 3D topographic terrain mesh + contour lines so external renderers see the exact slope, cut-and-fill ledges, and roof-as-ground relationship.
   - **Dashboard Live 3D WebGL (`build_nest_dashboard.py`):** Real displaced `THREE.BufferGeometry` terrain mesh with landscape zone draping and buildings seated at true DEM elevation `sampleTerrain(x, z)`.
   - **Render Pack Prompts (`build_render_pack.py`):** Injects the measured DEM slope, relief, and typology-specific cut-and-fill materiality into the editorial render prompt.
