# NEST Massing Intelligence — 3D Form-Finding, Volume Decomposition & Rhino (.3dm) Specification

> **System Role:** Governing **Stage B — Step 4C** 3D Massing & Form Derivation specification for **NEST**. Completes the 3-pillar Stage B design triad alongside [`NEST_Landscape_Intelligence.md`](./NEST_Landscape_Intelligence.md) *(Step 4A: 50–70 feddan landscape-first framing)* and [`NEST_Architectural_Direction.md`](./NEST_Architectural_Direction.md) *(Step 4B: Regenerative Monumentality thesis, tectonic idiom & space program)*.
>
> **Execution Engine:** Implemented programmatically via [`rhino_massing_engine.py`](../rhino_massing_engine.py) (`rhino3dm` + `shapely`), producing structured Rhino 8 (`.3dm`) models and dual 16:9 aerial clay locks (`massing_lock.png` + `massing_lock_clean.png`) **before** Render Pack generation.

---

## 1. Purpose & Core Principle

Architectural massing in NEST is **never** an arbitrary geometric box dropped onto a plot, nor a decorative shape disconnected from real square meters.

> **Core Rule (Form Follows Forces & Exact Program):** Every 3D massing volume must emerge deterministically from the site's **landscape contours, climate physics, space program (`m²`), and tectonic idiom**—and must be **mathematically calibrated (`±5%`) to the proposal's Built GFA** inside a clean, editable Rhino 8 (`.3dm`) model before any render prompt is written.

---

## 2. The 5-Driver Form-Finding Sequence (Step 4C)

For every winning site emerging from Steps 4A and 4B, NEST derives the 3D building massing in this strict 5-step sequence:

### Driver 1 — Landscape Envelope, Topography & Viewshed Axis
- **Strict Containment:** Position all built massing strictly inside the designated `Design & Activate` architectural precinct(s) defined in Step 4A (`NEST_Landscape_Intelligence.md`).
- **Zero Encroachment on `Preserve` Zones:** No building footprint may overlap any `Preserve` landscape zone (`0 m²` tolerance). The sole permitted exception is an explicitly tagged, non-invasive elevated pedestrian boardwalk, observation pier, or footbridge (`bridge_or_pile_allowed: true`) on micro-piles.
- **Primary Alignment Axis:** Orient the building's primary spine, courtyard opening, or stepped terraces directly toward the site's dominant natural/heritage datum (coastline, wadi channel, valley viewshed, or UNESCO sightline).

### Driver 2 — Solar, Wind & Microclimate Physics
- **Solar Geometry (Egypt Latitude `22°–31° N`):** Elongate primary bars along the E–W solar axis or orient deep shaded courtyards/arcades to minimize harsh low-angle West sun while harvesting roof/canopy solar irradiance.
- **Prevailing Wind Capture:** Open horseshoe courtyards, breezeways, and terraced step-downs toward prevailing N/NW onshore or valley breezes to maximize passive cross-ventilation and night-flush cooling.
- **Self-Shading & Courtyard Void Ratio:** Carve real hollow interior courtyards (`20%–35%` of outer plinth area) in hyper-arid zones to engineer a `8–12°C` passive microclimate drop.

### Driver 3 — Program-Matched Volume Decomposition & Realistic Floor-to-Floor Heights
Do **not** lump an entire `15,000–40,000 m²` project into a single undifferentiated block. Decompose the project's `spaces[]` table into **2–4 articulated, named 3D architectural volumes/wings/tiers**, each assigned realistic floor-to-floor heights by functional typology:

| Functional Space Typology | Target Floor-to-Floor Height | Typical Floor Count | Spatial Massing Behavior |
| :--- | :---: | :---: | :--- |
| **Museums, Exhibition Halls, Transit Concourses, Forums** | `6.0 – 9.0 m` *(double/triple-height)* | `1 – 2` | Long-span grounded or vaulted primary anchor volume |
| **Research Labs, Civic Academies, Cultural Studios** | `4.2 – 4.8 m` | `2 – 3` | Medium-span terraced or courtyard-carved wing |
| **Eco-Hospitality, Retreats, Residential Suites** | `3.6 – 4.0 m` | `1 – 3` | Shallow-depth (`12–16 m`) daylight/cross-ventilated bars or stepped clusters |
| **Logistics, Solar Cold-Chain, Desalination Utilities** | `6.5 – 8.5 m` *(clear span)* | `1` | Positioned on the arterial service edge (`Design & Activate`) to keep freight off fragile zones |
| **Vertical Observatories, Climate Spires, Sky-Courts** | `4.2 – 5.0 m` | `4 – 7` | Compact footprint (`< 30%` of GFA), rotating/stepped sky-court setbacks *(max 1 per run)* |

*Circulation, cores, and MEP Tare (`22%–28%`) are distributed proportionally across their parent volumes (or modeled explicitly as vertical `Cores` in Stage C `--mode detailed`).*

### Driver 4 — Site-Led Open Parametric Geometry (No Repetitive Box Catalog)
- **Seeds, Not a Fixed Menu:** The organic primitives in `rhino_massing_engine.py` (*sweeping crescents, contoured landform rings, sinuous curved vaulted ribbons, clustered teardrop/petal thin shells, tapered rotating elliptical spires*) are **starting geometric seeds**, not a closed menu. Any custom Rhino NURBS, lofted, stepped, or courtyard-carved geometry dictated by the site's GIS contours is encouraged.
- **Zero Boxy Defaults:** Never default to raw axis-aligned rectangles (`box(...)`) unless a historic orthogonal urban grid explicitly demands it.
- **Portfolio Massing Diversity Gate:** Across the 5 sites in any run, **no two sites may share the same primary massing parti or silhouette** (matching `NEST_Architectural_Direction.md`'s anti-repetition rule).

### Driver 5 — Hard GFA & Footprint Calibration (`±5%` Lock)
- Footprint coverage and tier stacking must be calibrated **mathematically** before finalizing the `.3dm` model:
  $$\text{Modeled Rhino GFA} = \sum_{v \in \text{Volumes}} \left(\text{Net Profile Area}_v \times \text{Floors}_v\right)$$
- **Mandatory Tolerance:** Total Modeled Rhino GFA must land within **`±5%`** of the project's `built_gfa` target. If a multi-tier idiom (`landform`, `vertical`, `hydrological`) exceeds `target_gfa`, automatically scale the footprint around its centroid (or adjust tier count) before extruding.

---

## 3. Rhino 8 (`.3dm`) File & Layer Architecture Contract

Every Stage B `.3dm` (`models/site_<N>_massing.3dm`) and Stage C detailed upgrade (`models/site_<N>_massing_detailed.3dm`) must conform to:

* **Units & Geolocation:** `UnitSystem.Meters`, local origin `(0, 0, 0)` at the organic site centroid, with `NEST_ORIGIN_LAT`, `NEST_ORIGIN_LON`, `NEST_CRS=EPSG:4326`, `NEST_SITE_AREA_M2`, `NEST_SITE_AREA_FEDDANS`, `NEST_BUILT_GFA`, `NEST_MODELED_GFA_M2`, and `NEST_TECTONIC_IDIOM` stored in Document UserStrings.
* **Nested Layer Tree (Human-Readable Names — No `L-01` Prefixes):**
  * `00_SITE_BOUNDARY` — GIS-snapped organic 50–70 feddan perimeter curve
  * `01_LANDSCAPE_ZONES::<Real Zone Name>` — Planar triangulated zone meshes + curves + `3D_Landforms`
  * `02_BUILDING_MASSING::<Program Volume Name>` — Closed positive-Z extrusions (with hollow courtyards via `AddInnerProfile`), plus `Mega_Canopy` / `Parametric_Shell` / `Hydrological_Deck` / `Elevated_Bridge` / `Structure` (and `Floor_Plates` + `Cores` in Stage C `--mode detailed`)
  * `03_GIS_CONTEXT::Water_Perennial`, `::Wadi_Ephemeral`, `::Roads`, `::Context_Buildings`
  * `04_MAP_POINTERS` — `TextDot` GIS reference markers (`Visible = False` by default for a clean perspective viewport)

---

## 4. Five Mandatory Pre-Export Validation Gates

Before any `.3dm` model is accepted and passed to `renders/render_pack/`, `rhino_massing_engine.py` enforces all 5 gates automatically:

1. **GFA Lock Gate (`±5%`):** `|Modeled Rhino GFA − Target Built GFA| / Target Built GFA ≤ 5%`.
2. **Zero-Encroachment Gate:** `0 m²` overlap between any non-bridge building footprint and any `Preserve` landscape zone.
3. **Z-Integrity & Hollow Courtyard Gate:** Strictly CCW profile winding (`orient(..., sign=1.0)`) + bounding-box self-check guaranteeing `0` unintended below-ground extrusions (`Min.Z >= -0.25 m`), with real hollow interior courtyards preserved via `AddInnerProfile`.
4. **Height, Viewshed & Structural Plausibility Gate:** Floor-to-floor heights within `3.6–9.0 m`, realistic spans, and compliance with heritage/ridgeline height ceilings.
5. **Massing Rationale Traceability:** Record a concise `massing_rationale` per site documenting *why* its specific form, orientation, height, and footprint emerged from the 5 drivers.
