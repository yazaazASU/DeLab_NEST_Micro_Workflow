# 3-Engine Plot Execution Workflow (Stage A Pipeline)

> **Master Architecture:** See [`WORKFLOW.md`](./WORKFLOW.md) for how this Stage A Python pipeline hands off `intermediates/` to the Stage B **NEST** AI Agent ([`nest_workflow.md`](./nest_workflow.md)).

This document records the exact end-to-end workflow executed by **`run_3_engines.py`** (backed by **`heatmap_engine.py`**) whenever the **Crystals**, **Cells**, and **Corals** engines evaluate a 5×5 km GIS plot.

---

## Stage 1: Plot Ingestion, Observed Telemetry Extraction & Config Loading
1. **Plot Files:** Locate `*_boundary.geojson`, `*_all_layers.geojson`, `dataset-inventory.json` (if present), and `*_site_context.md` (auto-generating one from observed GIS telemetry if missing).
2. **Automatic Observed Telemetry Extraction (`extract_observed_telemetry`):**
   - Inspect `development_investigation_priorities_2030`, `Egypt — Population (WorldPop) — governorate_population_2025_2030`, `New data — mped_governorate_investment_plans_fy2526`, `New data — governorate_agricultural_indicators`, `New data — education_facilities`, `New data — health_facilities`, `gbif_egypt_*`, and `dataset-inventory.json`.
   - Extract real **DEM terrain slope** (`surface_slope_median_deg`, `surface_slope_p90_deg`), **TMY weather station telemetry** (`GHI kWh/m²/yr`, `ETo mm/yr`, `CDH base 26°C`, `+2°C warming projection`), **WorldPop governorate population (2025 → 2030)**, **school/health distance gaps**, and **verified MPED FY2025/26 governorate investment budgets & sector breakdowns**.
3. **Shared Knowledge:**
   - Parse **Efficiency Ratios (NSF/GSF)** for the 6 Nature-First Spatial Forces (`73%–78%`) and `Mixed-Use` (`72%`) from [`GENERAL_KNOWLEDGE/building_typologies.md`](./building_typologies.md).
   - Parse **Nature-First Net Space Program Templates** (Section 7) from [`GENERAL_KNOWLEDGE/space_program_knowledge.md`](./space_program_knowledge.md).
4. **Engine-Specific Nature-First Force Configs & Synergy Whitelists:** *(see [`engine_charter.md`](./engine_charter.md) for overarching themes)*
   - **Crystals Engine (Development — POIs to build around/in/at):** [`GENERAL_KNOWLEDGE/crystals_nature_forces.md`](./crystals_nature_forces.md)
   - **Cells Engine (Adaptation — unlocking an element's potential):** [`GENERAL_KNOWLEDGE/cells_nature_forces.md`](./cells_nature_forces.md)
   - **Corals Engine (Coordination — elements working better together):** [`GENERAL_KNOWLEDGE/corals_nature_forces.md`](./corals_nature_forces.md)

---

## Stage 2: Metric Projection, 50 m Grid, Terrain Classification & Masks
1. **Projection & Grid:** Convert WGS84 GIS geometries into local meters (`LocalProjection`) and build a **50 m × 50 m** grid clipped to the plot boundary.
2. **Terrain Classification (`Dry Land` / `Shoreline Edge` / `Open Water`):**
   - Classify every active cell into one of three physical surface classes using polygon containment and distance to the water-land boundary (`Egypt — Water Areas`, `نهر النيل`, `Egypt — Nile River`, `Egypt — Waterways`):
     - **`Dry Land`:** Outside water polygons (`> 100 m` from shoreline).
     - **`Shoreline Edge (≤100 m)`:** Land-water littoral interface within `100 m` of a shoreline.
     - **`Open Water`:** Inside water polygons (`> 50 m` offshore).
3. **Engine-Specific Masks (Cells outside mask are forced to `0`):**
   - **Crystals Engine (Development):** Buildable land, POI-adjacent/infill/landmark zones, shoreline edges, and **water zones** — excludes existing road footprints and existing building footprints / dense built cores.
   - **Cells Engine (Adaptation):** Natural, semi-natural, desert, mountain, coastal, underused contextual edges, shoreline, and **water zones** — excludes dense active urban cores, roads, and immovable major infrastructure.
   - **Corals Engine (Coordination):** All land, shoreline, urban-edge, and **water zones** inside the boundary.
   - **Water Zone Warning Flag (All 3 Engines):** Water bodies are **scorable** (not zeroed out). Any cell intersecting water carries an explicit **`water_zone_warning`** flag that surfaces in `stage_a_summary.json`, reports, and the dashboard.

---

## Stage 3: 6 Nature-First Spatial Force Scoring (Layer 1 Analysis)
For each engine independently, evaluate every cell (`0–100`) across the **6 NEST Nature-First Spatial Forces**:
1. **`Hydrology & Waterfront`**
2. **`Solar & Climate Intensity`**
3. **`Biodiversity & Ecology`**
4. **`Heritage & Culture Gravity`**
5. **`Civic & Service Deficit`**
6. **`Corridor & Network Connectivity`**

For each force:
- Filter GIS features matching each factor's `source_layer` / `fclass` rule (supporting dual-group `Group A AND Group B` collision/bridging filters).
- Compute normalized `[0, 1]` spatial surfaces using standard methods (`decay`, `inverse_decay`, `kde`, `service_gap`) and the **3 Engine-Specific Mathematical Operators**:
  - **`ring_decay` (Crystals Signature):** Peaks at a respectful standoff ring (`r_peak = 0.55 * radius`) to frame monumental views without intruding on protected heritage or water cores.
  - **`ecotone_gradient` (Cells Signature):** $\sqrt{D_A \cdot D_B}$ — Peaks strictly where two dynamic environmental fields collide (`Water × Extreme Solar`, `Water × Biodiversity`, `Heritage × Microclimate`).
  - **`corridor_bridge` (Corals Signature):** Peaks along the bridging midpoint/seam connecting two disconnected systems (`Settlement ↔ Waterfront/Port`, `Road ↔ Health/School Gap`, `Town ↔ UNESCO Heritage`).
- Multiply by each factor's weight and the engine's **Territorial Affinity Multiplier** (`aff_crystals`, `aff_cells`, `aff_corals`), sum to `0–100`, apply the engine mask, identify the **`Dominant Spatial Force`** (`argmax`), and record the **top 3 contributing GIS drivers** per cell.

---

## Stage 4: Multi-Force Synergy Clique Scoring (`2+ Forces` and `3+ Forces`)
1. Enumerate all valid cliques of size `2+` and `3+` where **every pair** of forces appears in the engine's Compatibility Whitelist (Section 5 of `*_nature_forces.md`).
2. Score each clique at each active cell using **Mean − Sample Standard Deviation**:
   $$\text{Score}(C) = \max\left(0,\; \bar{L}(C) - \sigma(C)\right)$$
   This rewards cells where multiple spatial forces converge at balanced, high intensity and penalizes lopsided mixes.
3. Record the best `Multi-Force Synergy (2+)` and `Multi-Force Synergy (3+)` scores and winning force combinations per cell.

---

## Stage 5: Unbiased Nature-First Hidden Potential & Top 15 Candidate Pool
> *Note: Both the legacy urban-anchor formula and the old open-water proximity bonus (`d_wat == 0 → 100`) are **removed** so dry land, shoreline, and water cells compete strictly on merit.*

1. **Unbiased Natural-System Proximity & Multi-Layer Convergence (`nat_prox_score`):**
   - Evaluates proximity (`≤ 2.5 km` nearest-neighbor rule per [`nature_first_design_principles.md`](./nature_first_design_principles.md)) across all natural, ecological (GBIF), hydrological, solar/climatic, and cultural/UNESCO features, plus a multi-domain convergence bonus (`2+` or `3+` converging natural domains within `600 m`).
2. **Real DEM Slope Accessibility Scoring (`nest_access_score`):**
   - Scores the 5 NEST Accessibility & Mobility indicators (`20%` each: Road, Settlement, Transit, Real DEM Slope `%`, and Est. Emergency Travel Time) as `High = 100`, `Moderate = 50`, `Low = 15`. Uses observed DEM median slope from `development_investigation_priorities_2030` whenever present (falling back to `50 — Pending DEM` only if absent).
3. **Engine-Differentiated Hidden Potential & Stratified Top 15 `candidate_pool`:**
   - Computes a distinct **Hidden Potential (`0–100`)** surface and GeoTIFF (`hidden_potential.tif`) for each engine:
     - **Crystals Hidden Potential (`High-Gravity POI Development Anchor`):** Rewards dominant/dual force anchored around, in, or at high-gravity POIs (natural, cultural, infrastructural, or civic) on buildable land & shoreline plinths + viewshed standoff + low building-footprint conflict.
     - **Cells Hidden Potential (`Latent-Potential Adaptation Target`):** Rewards high-intensity, extreme, or colliding site/nature/context elements (`Hydrology × Solar`, `Hydrology × Biodiversity`, `Solar × Biodiversity`, contextual/heritage adaptation edges) whose untapped potential can be adapted into something new/better.
     - **Corals Hidden Potential (`Beneficial Relationship & Coordination Seam`):** Rewards high `3+ Multi-Force Synergy` + multi-element coordination seams where communities, ports, roads, natural systems, or heritage assets can work better together.
   - Identifies the **Top 5 distinct peaks per engine (`15` stratified candidates total, `≥ 450 m` intra-engine spacing)** in `hidden_opportunities.md` and `stage_a_summary.json`.
   - Automatically detects **Cross-Engine Convergence (`≤ 350 m`)**, tagging each candidate with `converging_engines` and `recommended_strategy` (`Select` vs. `Merge`).
   - Pre-packages **`skill_seeds.{crystals, cells, corals}`** per candidate site so **all 3 engines** are ready to generate downstream `skill_name.json` files when a project is selected from the NEST dashboard in Stage C.

---

## Stage 6: Catchment-Driven Nature-First Space Program & Click Drawer Concept
For every active cell (and in the interactive Tab 2 Click Drawer):
1. **Catchment Population:** Estimate local population within the plot's `Catchment Radius` using residential/building KDE × `Urban Density Baseline`.
2. **Synergy Mode Selection (`Auto Synergy`):**
   - Pick `3+ Forces` if `Multi-Force Synergy (3+) ≥ 60`
   - Else pick `2+ Forces` if `Multi-Force Synergy (2+) ≥ 60`
   - Else pick `Dominant Single Force`
3. **Area Sizing ($\text{m}^2$):** Allocate `Net m²` proportionally to the winning spatial forces' scores and `Net m² / resident` benchmarks, then divide by the force's **Efficiency Ratio** (`73%–78%`, or `72%` for Multi-Force Synergy) to compute **Total GFA ($\text{m}^2$)** and **Tare ($\text{m}^2$)** using the templates in [`space_program_knowledge.md`](./space_program_knowledge.md).
4. **Interactive Click Drawer (`Forces & GIS Drivers` + `Emergent Program & Concept`):**
   - Clicking any `50 m × 50 m` cell on any of the 3 maps compares **Crystals**, **Cells**, and **Corals** side-by-side:
     - **Tab A (`Forces & GIS Drivers`):** Horizontal score bars for all 6 Nature-First Spatial Forces, synergy pills (`1st vs 2nd`, `2+ Forces`, `3+ Forces`), and Top GIS Layer Drivers.
     - **Tab B (`Emergent Program & Concept`):** Engine-specific **Nature-First Architectural Concept & Two-Way Nature Cue** + live **Nature-First Space Program Table** (`GFA m²`, `%`, `NSA m²`).

---

## Stage 7: Stage A Exports (`intermediates/`)
1. **Per-Engine Folders (`intermediates/engine1_development/`, `engine2_adaptation/`, `engine3_coordination/`):**
   - `geotiff/*.tif` (9 EPSG:4326 GeoTIFFs per engine: 6 Nature-First Spatial Forces + `BestFit` + `MixedUse_2plus` + `MixedUse_3plus`)
   - `<plot>_50m_<engine>.geojson`
   - `top_site_space_program.md`
2. **Cross-Engine Handoff & Base Dashboard (`intermediates/`):**
   - `hidden_opportunities.md` (Top 5 Nature-First Hidden Opportunities per engine)
   - `stage_a_summary.json` (Structured handoff containing `observed_plot_telemetry`, `candidate_pool` [Top 15 merit-ranked clusters with `terrain_class`, `force_scores`, `top_drivers_by_engine`, `map_feature_pointers`, `accessibility`, `flags`, and `boundary_geojson`], and legacy `nest_top5_sites` alias)
   - `3engines_base_dashboard.html` (3 synchronized side-by-side Leaflet maps with 6 Nature-First Spatial Force toggles, Hidden Gem pins, and the upgraded NEST 2.2 Click Drawer).

---

## Next Step: Stage B NEST Synthesis
All Stage 7 outputs feed directly into the **NEST System Workflow** ([`nest_workflow.md`](./nest_workflow.md)) and [`project_brief_template.md`](./project_brief_template.md), where the Stage B AI Agent audits the Top 15 `candidate_pool` + `observed_plot_telemetry`, selects the **best 5 sites**, deconstructs their converging Nature-First Spatial Forces, and synthesizes competition-grade mega-landmark proposals into `nest_dashboard.html` (NEST 2.2 UI) and `NEST_Executive_Report.md`.
