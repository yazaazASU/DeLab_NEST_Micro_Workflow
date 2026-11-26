# The 3-Engine Land Evaluation System — Definitions & Behavior

This document defines the architecture of the **3-Engine System** (**Crystals Engine** — Development, **Cells Engine** — Adaptation, **Corals Engine** — Coordination), what is shared across all three, and how each engine evaluates the same piece of land from a distinct architectural and environmental point of view under **NEST**.

> **Canonical Engine Identity:** See [`engine_charter.md`](./engine_charter.md) for the universal overarching cognitive themes of Crystals (**Development**), Corals (**Coordination**), and Cells (**Adaptation**) across land, buildings, skills, and any other object.  
> **Master System Reference:** See [`WORKFLOW.md`](./WORKFLOW.md) for the end-to-end `NEST ↔ 3 Engines` execution contract, [`engines_workflow.md`](./engines_workflow.md) for Stage A (`run_3_engines.py`), and [`nest_workflow.md`](./nest_workflow.md) for Stage B (NEST AI Agent synthesis).

---

## Part 1: What an Engine Is & What Is Shared

### What Is an "Engine"?
An **Engine** is an independent spatial-evaluation lens that inspects the **same 5×5 km GIS plot** (`*_all_layers.geojson` inside `*_boundary.geojson`) on a **50 m × 50 m grid** and turns raw GIS data into:
1. **Nature-First Spatial Force Heatmaps (`0–100`)** for the **6 NEST Nature-First Spatial Forces**:
   - `Hydrology & Waterfront`
   - `Solar & Climate Intensity`
   - `Biodiversity & Ecology`
   - `Heritage & Culture Gravity`
   - `Civic & Service Deficit`
   - `Corridor & Network Connectivity`
   plus `Multi-Force Synergy (2+)`, `Multi-Force Synergy (3+)`, and `Dominant Spatial Force`.
2. **Terrain Classification (`Dry Land` / `Shoreline Edge (≤100 m)` / `Open Water`)** and an unbiased **Nature-First Hidden Potential Score (`0–100`)**.
3. **A Catchment-Driven Nature-First Space Program ($\text{m}^2$)** with Net Assignable Area, Tare (Circulation/Cores/MEP), Total GFA, and a Two-Way Nature Integration architectural cue.

### What Is Shared Across All 3 Engines
| Shared Component | Source / Behavior |
| :--- | :--- |
| **Study Area & Grid** | Any Egyptian 5×5 km GIS plot boundary, **50 m × 50 m** grid (~10,000 cells inside boundary) |
| **6 Nature-First Spatial Forces & Efficiency Ratios** | Defined in [`building_typologies.md`](./building_typologies.md) (`Hydrology & Waterfront 76%`, `Solar & Climate Intensity 78%`, `Biodiversity & Ecology 75%`, `Heritage & Culture Gravity 74%`, `Civic & Service Deficit 73%`, `Corridor & Network Connectivity 75%`, `Multi-Force Synergy 72%`) |
| **Multi-Force Synergy Clique Rule (`2+` & `3+`)** | Uses the compatibility whitelist in each engine's `*_nature_forces.md` (Section 5). Any 2+ or 3+ force combination where every pair is whitelisted is scored by **Mean − Sample Standard Deviation ($\bar{L} - \sigma$)** to reward balanced multi-force convergence and penalize lopsided scores |
| **Scoring Math & Signature Engine Operators** | Multi-Criteria Evaluation (`decay`, `inverse_decay`, `kde`, `service_gap`) plus **3 Engine-Specific Mathematical Operators**: **`ring_decay`** (Crystals — building around/in/at high-gravity POIs with respectful standoff/viewshed rings & direct POI gravity), **`ecotone_gradient`** (Cells — latent-potential element collisions & high-intensity natural/contextual conditions `Group A AND Group B`), and **`corridor_bridge`** (Corals — coordinating two elements in site/nature/context into a beneficial relationship `Group A AND Group B`) |
| **Engine-Specific Hidden Potential (`0–100`)** | Each engine discovers its Top 5 Hidden Potential sites using its own lens formula: **Crystals** = *High-Gravity POI Development Anchor*, **Cells** = *Latent-Potential Adaptation Target*, **Corals** = *Beneficial Relationship & Coordination Seam* |
| **Demographic Demand & Space Templates** | Defined in [`space_program_knowledge.md`](./space_program_knowledge.md) (Section 7 Nature-First Force Templates) + plot-specific `*_site_context.md` (or auto-generated site context) |
| **Terrain & Territorial Affinity** | Every cell is classified as **`Dry Land`**, **`Shoreline Edge (≤100 m)`**, or **`Open Water`**, and weighted by each engine's **Territorial Affinity Multiplier** (Crystals peaks on open dry land & shoreline plinths; Cells peaks on shoreline edges, water interfaces & GBIF habitats; Corals peaks along settlement-to-nature seams, roads & ports) |
| **Auto-Selection Mode** | Proposes `Multi-Force Synergy (3+)` if `≥ 60`, else `Multi-Force Synergy (2+)` if `≥ 60`, else `Dominant Single Force` |
| **Stratified Top 15 Pool, Convergence & Stage C Skill Seeds** | `run_3_engines.py` exports a **Stratified Top 15 `candidate_pool`** (Top 5 per engine, `≥ 450 m` intra-engine spacing), automatically detects **Cross-Engine Convergence (`≤ 350 m`)** for `Select` vs. `Merge`, and pre-packages **`skill_seeds.{crystals, cells, corals}`** per site so **all 3 engines** are ready to generate downstream `skill_name.json` files when a project is selected from the NEST dashboard |
| **Side-by-Side Visualization & Click Drawer** | All 3 engines render synchronously in `intermediates/3engines_base_dashboard.html` and Tab 2 of `nest_dashboard.html` (**NEST 2.2 UI**), including a **`Hidden Potential`** heatmap toggle and an interactive cell-click drawer showing each engine's **Posture Badge**, **Hidden Potential Score**, **Stage C Skill Seed Cue**, **`Forces & GIS Drivers`**, and **`Emergent Program & Concept`** |

---

## Part 2: Engine Definitions & Behavior

### Engine 1: Crystals Engine *(Development — Finding Points of Interest to Build Around, In, or At)*
* **Overarching Theme:** **Development** — Finding points of interest (natural, cultural, infrastructural, or civic) to build around, in, or at.
* **Point of View:** *"Where are the high-gravity points of interest, and how should we build around, in, or at them?"*
* **Config File:** [`GENERAL_KNOWLEDGE/crystals_nature_forces.md`](./crystals_nature_forces.md)
* **Spatial Mask:** Buildable land, adjacent/infill/landmark zones, shoreline edges, and **water zones** (water cells scorable with `water_zone_warning`) — excludes **existing road footprints** and **existing building footprints / dense built cores**.
* **Scoring Behavior:** Evaluates high-gravity POIs across waterfront/hydrology, solar/climate datums, biodiversity overlooks, UNESCO/cultural & civic POIs, underserved civic catchments, and arterial/port gateways using `ring_decay` (*around*), `decay` (*at*), and `kde` (*in*).
* **Space Program Behavior:** Outputs **POI-Anchored Development GFA ($\text{m}^2$)**, Net NSF ($\text{m}^2$), Tare ($\text{m}^2$), and a Two-Way Nature Integration development concept (*Primary Spatial Force, Multi-Force Convergence, Two-Way Nature Exchange*).
* **Outputs:** `intermediates/engine1_development/` (`geotiff/*.tif`, `*_50m_development.geojson`, `top_site_space_program.md`)

---

### Engine 2: Cells Engine *(Adaptation — Unlocking an Element's Full Potential by Adapting It Into Something New/Better)*
* **Overarching Theme:** **Adaptation** — Finding elements in site, nature, or context (both natural and man-made/contextual: landforms, caves, harsh climates, wadis, quarries, ruins, underused edges) to unlock their full potential by adapting them into something new or better.
* **Point of View:** *"Which natural or contextual element holds untapped potential, and how can we adapt or transform it into something new and better?"*
* **Config File:** [`GENERAL_KNOWLEDGE/cells_nature_forces.md`](./cells_nature_forces.md)
* **Spatial Mask:** Natural, semi-natural, ecological-transition, desert/mountain/coastal, underused contextual edges, shoreline, and **water zones** (water cells scorable with `water_zone_warning`) — excludes **dense active urban cores**, **roads**, and immovable major infrastructure.
* **Scoring Behavior:** Prioritizes high-intensity or underutilized site/nature/context elements and dynamic transition interfaces (`ecotone_gradient`, `kde`, extreme-condition `decay`) — hydrological/flood edges, extreme solar/evaporative gradients, GBIF biodiversity hotspots, heritage/contextual transformation edges, and amphibious mobility interfaces.
* **Space Program Behavior:** Outputs **Adaptive Transformation GFA ($\text{m}^2$)** structured for low-impact, passive-cooled, reversible, seasonal, or regenerative interventions that unlock the latent potential of the host element.
* **Outputs:** `intermediates/engine2_adaptation/` (`geotiff/*.tif`, `*_50m_adaptation.geojson`, `top_site_space_program.md`)

---

### Engine 3: Corals Engine *(Coordination — Using Elements Better Together / Introducing Beneficial Relationships)*
* **Overarching Theme:** **Coordination** — Finding elements in site, nature, or context to use better together or introduce a beneficial relationship.
* **Point of View:** *"Which elements in the site, nature, or context can work better together, or what beneficial relationship can be introduced between them?"*
* **Config File:** [`GENERAL_KNOWLEDGE/corals_nature_forces.md`](./corals_nature_forces.md)
* **Spatial Mask:** All **land, shoreline, urban-edge, and water zones** inside the boundary (water cells scorable with `water_zone_warning`).
* **Scoring Behavior:** Prioritizes multi-element seams and pairing zones (`corridor_bridge`: `Group A AND Group B`) — settlement-to-waterfront civic/port seams, solar-to-community microgrid/cold-chain spines, community-to-biodiversity corridors, heritage-to-settlement craft/visitor spines, and regional civic/intermodal bridges.
* **Space Program Behavior:** Outputs **Symbiotic Connector / Coordination GFA ($\text{m}^2$)** sized for shared civic-ecological hubs, multi-modal eco-ports, zero-carbon cold-chain logistics, community STEM/health connectors, and cultural-waterfront spines.
* **Outputs:** `intermediates/engine3_coordination/` (`geotiff/*.tif`, `*_50m_coordination.geojson`, `top_site_space_program.md`)

---

## Part 3: Editing & Re-Running
1. Edit **shared rules** (efficiency ratios, Nature-First space templates, demographic benchmarks) in [`building_typologies.md`](./building_typologies.md) or [`space_program_knowledge.md`](./space_program_knowledge.md).
2. Edit **engine-specific force weights, GIS layer filters, or synergy pairs** in [`crystals_nature_forces.md`](./crystals_nature_forces.md), [`cells_nature_forces.md`](./cells_nature_forces.md), or [`corals_nature_forces.md`](./corals_nature_forces.md). *(Note: Legacy 6-typology files `typology_spatial_proxies.md`, `adaptation_spatial_proxies.md`, and `coordination_spatial_proxies.md` are retained for archival reference only.)*
3. Run:
   ```powershell
   python run_3_engines.py --data-dir "<path_to_plot_folder>" --out-dir "<run_output_dir>" --plot-name "<Plot Name>"
   ```
   to regenerate all GeoTIFFs, GeoJSONs, `hidden_opportunities.md`, `stage_a_summary.json`, and `intermediates/3engines_base_dashboard.html`.
