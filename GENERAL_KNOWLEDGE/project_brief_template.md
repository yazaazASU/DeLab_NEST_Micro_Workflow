# NEST Project Brief & Card Template (Canonical Stage B Contract)

> **Purpose:** Single source of truth defining the exact sections, fields, formatting, and data provenance displayed for every project after **Stage B (NEST AI Agent)** completes.  
> **Target Audience:** Balanced Executive & Technical Reviewers — giving equal weight to **GIS spatial evidence**, **architectural thesis**, and **economic/financial feasibility**.  
> **Scope:** Mandatory contract for every project card (`#1`–`#5`) rendered in `nest_dashboard.html` (Tab 1) and documented in `NEST_Executive_Report.md`.  
> **Removed Legacy Field:** `hidden_score` (`Hidden XX/100`) is **excluded** from the project card and brief header.

---

## 1. Visual Header (Top Media Strip)

Displayed side-by-side at the top of each project card.

### 1A. Whole-Site Editorial Aerial Render & 3D Massing Toggle (50–70 Feddans: Landscape + Building)
| Field | Key (`NEST_PROJECTS`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| Render Image (Geometry-Locked) | `render` | `renders/site_<rank>.jpg` (`16:9` whole-site aerial generated from BOTH `massing_lock.png` + `satellite_lock.png` via `architectural-conceptual-render` skill) | Stage B |
| **3D Massing Clay View Toggle** | `massing_lock` | `renders/render_pack/site_<rank>_massing_lock.png` — inline **`Render \| 3D Massing`** toggle pill in the top-right corner of the visual header so reviewers can verify 1:1 fidelity against the Rhino model | Stage B (`rhino_massing_engine.py`) |
| Rank & Strategy Chip | `rank`, `strategy`, `is_water` | `PROJECT #<rank> • <Select (Engine) / Merge (Engine A + Engine B)>` *(amber highlight if `is_water`)* | Stage A + B |

### 1B. Embedded Interactive Mini-Map (Tri-Layer Satellite + Landscape Zones + Building Footprints + Evidence Pointers)
| Field | Key (`NEST_PROJECTS`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| Outer 50–70 Feddan Site Boundary | `geojson` | Dashed translucent polygon (`#10b981` land / `#f59e0b` water), targeting **50–70 feddans (`21.0–29.4 ha` / `210,042–294,058 m²`)** (documented exception required if `< 50 feddans`) | Stage B (delineated from Stage A peak) |
| **Validated Landscape Zone Polygons (`L-01..L-0N`)** | `landscape_zones[]` (`{ id, name, family, intervention, area_m2, area_ha, area_feddans, share_pct, color, geom }`) | Semi-transparent color-coded landscape zoning polygons strictly contained within the 50–70 feddan boundary (no overlaps/gaps), labeled `L-01..L-0N` with hover tooltips showing zone name, intervention level, and area (`m²` / feddans / `%`) | Stage B (`NEST_Landscape_Intelligence.md`) |
| Inner Building Footprints | `footprints[]` (`{ label, geom }`) | Solid concept-matched massing polygons scaled to Built GFA, with hover tooltip (`label`) | Stage B (`NEST_Architectural_Direction.md`) |
| **Influencing Feature Pointers** | `map_pointers[]` | **3–5 numbered, color-coded callout pins** placed at the exact GIS feature coordinates (`lat, lon`) with **dashed leader lines** to the site center. Each pin displays `<id>. <label> • <distance_m> m • <role>` on hover/callout. | Stage A (`gis_evidence.map_feature_pointers`) + Stage B (`role`) |
| Legend Pill | *(fixed UI)* | `Site Boundary (50–70 fed.)` (dashed) · `Landscape Zones (L-01..L-0N)` (tinted) · `Building Footprint` (solid) · `1–5 Site Drivers` (numbered pins) | Fixed |
| Map Meta Bar | `footprint_type`, `area_m2` | `<Contiguous / Distributed> • <area_m2> m² (<ha> ha / <feddans> feddans)` | Stage B |
| Map Jump Action | `rank` | `3-Engine Map →` button (switches to Tab 2 and centers all 3 maps on `[lat, lon]`) | Fixed |

### 1C. Synced Site Evidence Highlights Strip (Directly Below Visual Header — NEW)
A compact horizontal strip of **3–5 numbered chips** matching the numbered callout pins (`1`–`5`) on the mini-map. Clicking/hovering a chip highlights its pin on the map.

| Field | Key (`map_pointers[i]`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| Pointer Number & Color | `id`, `category` | `1` (`hydrology` / `natural` / `access` / `settlement` / `transit` / `energy`) | Stage A |
| Feature & Distance | `label`, `distance_m` | e.g., `Active Desert Wadi • 0 m`, `Arterial Highway • 22 m`, `Al-Hasana Settlement • 921 m` | Stage A |
| Architectural / Economic Role | `role` | Short 2–4 word explanation of how this feature shaped the proposal (e.g., `Hydro-engine`, `Cold-chain corridor`, `Local workforce`) | Stage B |
| GIS Layer & Provenance | `source_layer`, `provenance` | e.g., `Egypt — Waterways (Observed GIS)` or `Predicted ≤ 2.5 km` | Stage A |

---

## 2. Card Body (Core Project Brief — Always Visible)

### 2A. Card Header & Metadata Badges
| Field | Key (`NEST_PROJECTS`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| Project Title | `title` | Bold headline (e.g., `The Sinai Wadi Hydro-Citadel & National Arid-Water Reserve`) | Stage B |
| Subtitle & Engine Line | `subtitle`, `scores.{crystals,cells,corals}`, `access` | `<Subtitle> • Engine Scores: Crystals <X> \| Cells <Y> \| Corals <Z> • Accessibility: <A>/100` | Stage A + B |
| National Scale Tier Pill | `tier` | `Tier 1: Flagship National Landmark` or `Tier 2: Iconic National Anchor` *(gold pill)* | Stage A + B |
| Advisory Flag Pills | `flags[]` | Zero or more pills: `⚠ water_zone_warning`, `⚠ emergency_access_alert`, `⚠ policy_complexity` | Stage A + B |
| Built GFA Pill | `built_gfa` | `Built GFA: <X,XXX> m²` *(blue pill)* | Stage B |
| Site Area Pill | `area_m2`, `cells` | `Site: <X,XXX> m² / <XX.X> feddans` *(slate pill; `1 feddan = 4,200.833 m²`; Stage B target `50–70 feddans`)* | Stage B |

### 2B. Architectural Thesis & Signature Gesture *(Scannable Summary + Expandable Detailed Brief)*
Replaces long prose walls with a **50%-shorter scannable summary by default** plus an inline **`View detailed brief ▾`** toggle (and a global **`Summary | Detailed`** toggle pill at the top of the dashboard). *(Competition Rubric `/100` remains report-only.)*

> **Mandatory Writing Standard:** All `title`, `subtitle`, `thesis_summary`, and `thesis_detailed` copy **must** comply with [`NEST_Concept_Statement_Direction.md`](./NEST_Concept_Statement_Direction.md) — using the **5-Tier Competition Statement Ladder**, **Invisible Engine, Visible Reality** grounding (zero raw engine jargon/scores), the **Adaptive Archetype-Driven Voice Matrix** (Portfolio Rhetorical Diversity Gate across the Top 5), and a **zero-hit Banned Archispeak / AI Cliché Blacklist** sweep.

**Mandatory Default Summary Format (`thesis_summary`):**
- **1-Sentence Bold Hook (`hook`):** Crisp `≤ 28-word` competition headline sentence capturing the site-driven thesis (must pass the 3-Second Scan & Snøhetta Test).
- **3 Tight Labeled Bullets:**
  1. **Why Here (`why_here`):** Exact GIS spatial trigger / site contradiction (1 short line).
  2. **Key Program (`key_program`):** Core activities united on site (1 short line).
  3. **Architectural Gesture (`gesture_line`):** Physical form, materiality & climatic/ecological engine tying it all together (1 short line).
- **Expandable Full Narrative (`thesis_detailed`):** The complete `150–250 word` **3-Act Competition Narrative** (Act I: Site Provocation → Act II: Architectural & Ecological Instrument → Act III: Human Experience & Quotable Jury Pull-Line) hidden behind `View detailed brief ▾` (or revealed across all 5 cards via the global `Summary | Detailed` switch).

| Field | Key (`NEST_PROJECTS`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| Scannable Summary | `thesis_summary.{hook, why_here, key_program, gesture_line}` | 1-sentence hook + 3 tight bullets (`~50%` shorter than full brief) | Stage B |
| Detailed Brief | `thesis_detailed` | Full 4–5 sentence architectural narrative (shown on toggle) | Stage B |
| Tectonic Idiom | `idiom` | Named idiom from `NEST_Architectural_Direction.md` | Stage B |
| Precedent Lens | `precedent` | 1–2 cited architectural precedents + why they apply | Stage B |

### 2B-2. Interactive 2-Column Panel: 3D Massing & Form Rationale | Surrounding Landscape Zones & Outdoor Activities
Displayed side-by-side on every project card (clicking any mass, landscape zone, or 3D outdoor destination highlights and zooms to that exact polygon on the mini-map):

| Column & Field | Key (`NEST_PROJECTS`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| **Left: Orientation & Climate Axis** | `massing_rationale.orientation` | Why the building faces its exact viewshed/wind/solar axis | Stage B (`NEST_Massing_Intelligence.md`) |
| **Left: Why This Shape** | `massing_rationale.shape_logic` | How the 3D form emerges from site contours & tectonic idiom | Stage B (`NEST_Massing_Intelligence.md`) |
| **Left: Volume-by-Volume Breakdown** | `massing_rationale.volumes[]` (`{ name, use, area_m2, height_floors, shape_reason }`) | Interactive rows synced to mini-map footprints (`0.0%` GFA Lock) + `View in 3D Massing ↑` button | Stage B (`rhino_massing_engine.py`) |
| **Right: Backbone & Arch–Landscape Interface** | `landscape_summary.{backbone, arch_interface, tradeoffs_risk}` | Primary organizing system, interface, and mandatory Trade-Offs & Water/Resource Risk callout | Stage B (`NEST_Landscape_Intelligence.md`) |
| **Right: Zones, Why Here & Outdoor Activities** | `landscape_zones[]` (`{ name, why_here, outdoor_activities, intervention, area_feddans, share_pct, color, geom }`) | Interactive rows (human-readable names — no visible `L-01` codes) reconciling `100.0%` of the 50–70 feddan site | Stage B (`NEST_Landscape_Intelligence.md`) |
| **Right: 3D Outdoor Destinations** | `landscape_elements[]` (`{ type, label, geom }`) | Clickable chips for modeled amphitheaters, shaded pergolas, arrival plazas, cooling basins, oasis groves & belvederes | Stage B (`rhino_massing_engine.py`) |

### 2C. How the 3 Engines & Heatmaps Derived This Project *(NEW — Mandatory Spatial Traceability)*
Bridges Stage A's spatial heatmaps directly to Stage B's final architectural proposal so technical and executive reviewers see **exact causality**:

| Field | Key (`NEST_PROJECTS.engine_trace`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| Per-Engine Heatmap Contributions | `drivers.{crystals,cells,corals}` | Score (`0–100`) + top GIS heatmap driver & point contribution from `stage_a_summary.json` | Stage A |
| Baseline Engine Proposal | `baseline_proposal` | What the raw 3-engine heatmap originally flagged (e.g., `Residential · 1,428 m² local-only proxy`) | Stage A |
| How NEST Synthesized It | `synthesis_note` | 2–3 sentences explaining why NEST chose `Select` vs. `Merge` and how those exact heatmap signals + drivers were deconstructed and elevated into the winning landmark | Stage B |

### 2D. Two-Way Nature Integration *(Mandatory — Integrating Nature, Not Just Inspired By It)*
| Field | Key (`NEST_PROJECTS`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| Nature → Building | `nature_to_bldg` | How living natural systems actively cool, power, supply, or support the building | Stage B |
| Building → Nature | `bldg_to_nature` | How the building actively protects, feeds, recharges, or regenerates the ecosystem | Stage B |

### 2E. Key Activities
| Field | Key (`NEST_PROJECTS`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| Activity Tags | `activities[]` | Array of 4–6 short activity pills (e.g., `Flash-Flood Harvesting`, `Arid Hydrology Museum`, `Solar Cold-Chain`) | Stage B |

### 2F. Space Program & Square Meters Table
Header displays `Space Program & Square Meters (<built_gfa> Total GFA)`.

| Column | Key (`NEST_PROJECTS.spaces[]`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| Space / Zone | `spaces[i][0]` | Named program zone (final row = Structural Cores, MEP & Circulation Tare) | Stage B |
| Area | `spaces[i][1]` | `<X,XXX> m²` (right-aligned) | Stage B |
| Hours | `spaces[i][2]` | Operating schedule (e.g., `24/7`, `07:00–14:00`, `17:30–23:30`) | Stage B |

### 2G. Whole-Site Financial Feasibility KPI Strip *(Priority 1 PASS — Base Case)*
5-tile horizontal KPI strip covering the **entire 50–70 feddan Site (Building + Landscape)**, with explicit CapEx split displayed beneath/inside the CapEx tile:

| KPI Tile | Key (`NEST_PROJECTS.fin`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| Total Site CapEx *(with Building vs. Landscape split)* | `fin.capex`, `fin.capex_bldg`, `fin.capex_landscape` | e.g., `$78.5M` (`Building: $58.0M` · `Landscape & Site-Infra: $20.5M`) | Stage B |
| Site-Wide Revenue | `fin.rev` | e.g., `$19.8M/yr` *(architectural + landscape-driven streams)* | Stage B |
| ROI | `fin.roi` | e.g., `12.6%` *(emerald highlight)* | Stage B |
| IRR | `fin.irr` | e.g., `15.4%` *(sky-blue highlight)* | Stage B |
| Payback | `fin.payback` | e.g., `7.9 yrs` | Stage B |

### 2H. Economic Case & Data Sources Block *(Directly Under KPI Strip — NEW)*
Shows the economic evidence, demand drivers, and funding structure that derived the proposal:

| Sub-Element | Key (`NEST_PROJECTS.econ_evidence`) | Format / Example | Source |
| :--- | :--- | :--- | :--- |
| **1. Revenue Mix Bar / Pills** | `revenue_mix[]` (`{ stream, share_pct, annual_rev }`) | Segmented bar + pills summing to `100%` (e.g., `Water PPP 37% ($7.4M)` · `Cold-Chain 24% ($4.8M)` · `Solar PPA 21% ($4.2M)` · `Museum/Grants 18% ($3.4M)`) | Stage B |
| **2. Target Users & Demand Highlights** | `demand_highlights[]` (`{ highlight, source, basis }`) | 1–2 concise cited facts that derived the concept (e.g., `Central Sinai agricultural freight corridor lacks solar cold-chain within 80 km` — `[Observed GIS + Sinai Dev. Authority]`) | Stage A + B |
| **3. Target Funding Partners** | `funding_partners[]` | Compact pills naming realistic capital partners (e.g., `TSFE`, `EBRD / GCF`, `Ministry of Water Resources PPP`, `Golden License`) | Stage B |
| **4. Inline Source & Provenance Tags** | `sources[]` (`{ label, type, reference }`) | Explicit badges distinguishing `Observed` vs. `Benchmark` + named source (e.g., `Spatial: 80% Observed (GIS)` · `CapEx: Benchmark ($2,450/m², Egypt/MENA PPP)` · `Tariffs: Benchmark (EBRD/MWRI Water PPA)`) | Stage A + B |

### 2I. 3-Engine Proactive Design Skills Action Bar *(Stage C Skill Generation Hook — NEW)*
Displayed on the main visible body of every project card directly above the expandable accordion. Even in a single-engine `Select` project, **all 3 engines** (`Crystals`, `Cells`, `Corals`) prepare specialist `skill_seeds` in Stage A/B and contribute proactive design skills (`skill_name.json`) when the project is selected for Stage C:

| Element | Key (`NEST_PROJECTS.skill_seeds`) | Format / Behavior | Source |
| :--- | :--- | :--- | :--- |
| Skill Readiness Summary | `skill_seeds.{crystals,cells,corals}` | `3-Engine Proactive Design Skills (Stage C Ready): Crystals (Axes & Geometric Facets) · Cells (Environmental Stimuli & Homeostasis) · Corals (Resource Symbiosis & Branches)` | Stage A + B |
| Primary Action Button | `openSkillWorkflowModal(rank)` | Prominent raised coral/emerald button **`Generate Project Skills →`** (or **`View & Export Project Skills (6) →`** once generated) opening the Stage C Project Skills Master-Detail Modal | Stage B + C |
| **Download Rhino (`.3dm`) Model** | `rhino_3dm_path` | **`⬇ Rhino (.3dm)`** button downloading `models/site_<rank>_massing.3dm` (Stage B conceptual model, upgraded to `site_<rank>_massing_detailed.3dm` in Stage C) | Stage B + C (`rhino_massing_engine.py`) |
| Standalone Project Folder Export (`.ZIP`) | `export_zip_path` | **`⬇ Export Project Folder (.ZIP)`** button downloading `exports/project_<rank>_<slug>.zip` (containing `project_<rank>_dashboard.html`, `PROJECT_BRIEF.md`, `project_data.json`, `site_geometry.geojson`, `models/site_<rank>_massing.3dm`, `render/`, and `skills/*.json`) | Stage B + C |
| Standalone 1-Project HTML Link | `export_html_path` | **`1-Project HTML ↗`** button opening `exports/project_<rank>_<slug>/project_<rank>_dashboard.html` in a new tab | Stage B + C |

---

## 3. Expandable Accordion (`Hypotheses, Catalytic Phase 0 Pilot & Full Data Provenance`)

Collapsed by default on the dashboard card; expands to show:

1. **Conditional Environmental Harm Banner (`harmful_note`):**
   - Rendered only if a competing hypothesis triggers Rule Precedence Priority 2:  
     `🔴 HARMFUL TO THE ENVIRONMENT (Rule Precedence): <explanation + how winner serves as mandatory nature-safe alternative>`
2. **Multi-Hypothesis Comparison Table (`hypotheses[]`):**
   - 2–3 rows (`[Hypothesis ID, Integrated Site + Building Concept, Ecology & Landscape Trade-Offs / Water Risk, Financial Feasibility / Verdict]`). Every hypothesis explicitly surfaces its **Landscape Trade-Offs & Water/Resource Risk** so no serious ecological trade-off is hidden inside an aggregate score.
3. **Financial Scenarios (`fin.scenarios`):**
   - Conservative / Base / Upside ranges (CapEx, Revenue, IRR, Payback).
4. **Catalytic Phase 0 Pilot (`fin.pilot`):**
   - Pilot cost, timeline (months), and validation scope before full CapEx commitment.
5. **Full Data Provenance & Natural-System Evidence (`fin.prov`, `nat_prov`):**
   - Detailed `% Observed vs. Estimated` audit and Stage A `nat_prov` (`Observed (Direct GIS)` or `Predicted (Nearest-Neighbor X m <= 2.5 km)`).

---

## 4. Additional Fields Shown Only in `NEST_Executive_Report.md`

Kept in the Executive Report to avoid cluttering the dashboard card:

- **Competition-Grade Impact Score Breakdown:** Total `XX/100` (Pass Gate `≥ 75`) + 5 sub-scores (`/20` each).
- **Exact Bounding Box Coordinates:** `Lon [min, max]`, `Lat [min, max]`.
- **Detailed Accessibility 5-Indicator Breakdown:** `Road (m) [score]`, `Settlement (m) [score]`, `Transit (m) [score]`, `Est. Emergency (min) [score]`, `Slope [Observed DEM median ° / % -> score]` (fallback `50 — Pending DEM` only when DEM telemetry is absent).
- **Expanded Advisory Flag Mitigation Bullets:** Detailed engineering/permitting precautions for `water_zone_warning`, `policy_complexity`, and `emergency_access_alert`.
- **Deconstructed Engine Signal:** Stage A dominant Nature-First Spatial Force (`Hydrology & Waterfront`, `Solar & Climate Intensity`, `Biodiversity & Ecology`, `Heritage & Culture Gravity`, `Civic & Service Deficit`, `Corridor & Network Connectivity`), local-only GFA proxy (`m²`), and top GIS driver that NEST elevated/transformed.
- **Full Financial Table:** Annual EBITDA / Profit (`$M/yr` + margin `%`) and row-by-row Calculation / Benchmark Basis.

---

## 5. Markdown Project Brief Template (Copy-Paste Structure)

```markdown
## NEST Site #<rank> — <Project Title> (`<lat>, <lon>`)

![NEST Project #<rank> Architectural Render](renders/site_<rank>.jpg)

> **Strategy:** `<Select / Merge>` | **Scale Tier:** `<Tier 1 / Tier 2>` | **Built GFA:** `<built_gfa>` | **Site Boundary:** `<area_m2> m² (<feddans> feddans, <Contiguous / Distributed>, <cells> cells)`
> **Scores:** Crystals `<crystals>` · Cells `<cells>` · Corals `<corals>` · Accessibility `<access>/100`
> **Flags:** `<flags or None>`

### Site Evidence Highlights (Map Pointers 1–5)
1. **`<Label>` (`<distance_m> m`)** — `<role>` *(Source: `<source_layer>` · `<provenance>` · `<lat>, <lon>`)*
2. **`<Label>` (`<distance_m> m`)** — `<role>` *(Source: `<source_layer>` · `<provenance>` · `<lat>, <lon>`)*
3. **`<Label>` (`<distance_m> m`)** — `<role>` *(Source: `<source_layer>` · `<provenance>` · `<lat>, <lon>`)*

### Architectural Thesis & Signature Gesture
- **Thesis Hook:** **<thesis_summary.hook>**
- **1. Why This Site:** <thesis_summary.why_here>
- **2. Key Program:** <thesis_summary.key_program>
- **3. Architectural Gesture:** <thesis_summary.gesture_line>
- **Detailed Brief:** <thesis_detailed>
- **Tectonic Idiom:** <idiom>
- **Precedent Lens:** <precedent>
- **Competition Rubric *(Report Only)*:** `<total>/100` (Landscape `<x>/20` · Silhouette `<x>/20` · Ecological Engine `<x>/20` · Civic Gravity `<x>/20` · Global Press `<x>/20`)

### Landscape Intelligence & Zoning Schedule (`L-01..L-0N` — `<area_m2> m²` / `<ha> ha` / `<feddans> feddans`)
- **Landscape Backbone:** <landscape_summary.backbone>
- **Architecture–Landscape Interface:** <landscape_summary.arch_interface>
- **Landscape Trade-Offs & Water/Resource Risk:** <landscape_summary.tradeoffs_risk>
| Zone ID | Zone Name & Family | Intervention | Area (`m²` / `ha` / `feddans`) | % of Site |
| :--- | :--- | :--- | ---: | ---: |
| `L-01` | <zone name & family> | <Preserve / Restore / Enhance / Design & Activate / Minimal> | <m² / ha / feddans> | <%> |
| `L-0N` | <zone name & family> | <intervention> | <m² / ha / feddans> | <%> |

### How the 3-Engine Heatmaps & Proposals Derived This Result
- **Crystals (Development):** `<scores.crystals>/100` — `<engine_trace.drivers.crystals>`
- **Cells (Adaptation):** `<scores.cells>/100` — `<engine_trace.drivers.cells>`
- **Corals (Coordination):** `<scores.corals>/100` — `<engine_trace.drivers.corals>`
- **Stage A Baseline Signal:** `<engine_trace.baseline_proposal>`
- **NEST Stage B Synthesis:** `<engine_trace.synthesis_note>`

### Two-Way Nature Integration
- **Nature → Building:** <nature_to_bldg>
- **Building → Nature:** <bldg_to_nature>

### Key Activities
- <activity 1> · <activity 2> · <activity 3> · <activity 4>

### Space Program (`<built_gfa>` Total GFA)
| Space / Zone | Area | Hours |
| :--- | ---: | ---: |
| <zone 1> | <m²> | <hours> |
| <zone N (Cores / MEP / Tare)> | <m²> | <hours> |

### Whole-Site Financial Feasibility (Priority 1 PASS — Base Case)
| Total Site CapEx | Building CapEx | Landscape & Site-Infra CapEx | Annual Revenue | ROI | IRR | Payback |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `<capex>` | `<capex_bldg>` | `<capex_landscape>` | `<rev>` | `<roi>` | `<irr>` | `<payback>` |

### Economic Case & Data Sources
- **Revenue Mix:** `<Stream A> <X%> (<$M>)` · `<Stream B> <Y%> (<$M>)` · `<Stream C> <Z%> (<$M>)`
- **Target Users & Demand Highlights:**
  - <Cited demand/market highlight #1> *(`[Observed / Benchmark]` — `<Source>`)*
  - <Cited demand/market highlight #2> *(`[Observed / Benchmark]` — `<Source>`)*
- **Target Funding Partners:** `<Partner 1>` · `<Partner 2>` · `<Partner 3>`
- **Source & Provenance Tags:** `<Tag 1>` · `<Tag 2>` · `<Tag 3>`

### Hypotheses, Pilot-Scale Test & Full Data Provenance
- **Harmful to the Environment Alert *(if triggered)*:** `<harmful_note>`
- **Competing Integrated Site + Building Hypotheses:**
  | Hypothesis | Integrated Site + Building Concept | Ecology & Landscape Trade-Offs / Water Risk | Feasibility / Verdict |
  | :--- | :--- | :--- | :--- |
  | **H1** | <concept> | <ecology + explicit trade-offs/water risk> | <verdict> |
  | **H2** | <concept> | <ecology + explicit trade-offs/water risk> | <verdict> |
  | **H3** | <concept> | <ecology + explicit trade-offs/water risk> | <verdict> |
- **Scenarios:** `<Conservative / Base / Upside summary>`
- **Catalytic Phase 0 Pilot:** `<pilot cost, timeline & scope>`
- **Data Provenance:** `<fin.prov>` • **Natural-System Evidence:** `<nat_prov>`
```

---

## 6. Canonical Dashboard Card JSON Schema (`NEST_PROJECTS[i]`)

```json
{
  "rank": 1,
  "render": "renders/site_1.jpg",
  "massing_lock": "renders/render_pack/site_1_massing_lock.png",
  "rhino_3dm_path": "models/site_1_massing.3dm",
  "tier": "Tier 1: Flagship National Landmark",
  "title": "Project Title",
  "subtitle": "Short Positioning Subtitle",
  "strategy": "Merge (Crystals + Cells)",
  "is_water": false,
  "nat_prov": "Observed (Direct GIS)",
  "lat": 29.926614,
  "lon": 33.759068,
  "footprint_type": "Contiguous",
  "area_m2": 252050,
  "area_feddans": 60.0,
  "cells": 101,
  "built_gfa": "26,500 m²",
  "access": 80.0,
  "scores": { "crystals": 76.1, "cells": 71.0, "corals": 48.8 },
  "flags": ["⚠ water_zone_warning", "⚠ policy_complexity"],
  "map_pointers": [
    {
      "id": 1,
      "category": "hydrology",
      "label": "Active Desert Wadi",
      "distance_m": 0,
      "role": "Hydro-engine & aquifer recharge",
      "source_layer": "Egypt — Waterways",
      "provenance": "Observed (Direct GIS)",
      "lat": 29.926614,
      "lon": 33.759068
    },
    {
      "id": 2,
      "category": "access",
      "label": "Primary Arterial Highway",
      "distance_m": 22,
      "role": "Cold-chain & national visitor access",
      "source_layer": "الطرق",
      "provenance": "Observed (Direct GIS)",
      "lat": 29.926780,
      "lon": 33.759210
    },
    {
      "id": 3,
      "category": "settlement",
      "label": "Al-Hasana Settlement",
      "distance_m": 921,
      "role": "Local workforce & civic catchment",
      "source_layer": "New data — populated_places",
      "provenance": "Observed (Direct GIS)",
      "lat": 29.918450,
      "lon": 33.757900
    }
  ],
  "thesis_summary": {
    "hook": "1-sentence bold headline capturing the site-driven architectural thesis.",
    "why_here": "Exact GIS spatial trigger / site contradiction (1 short line).",
    "key_program": "Core activities united on site (1 short line).",
    "gesture_line": "Physical form, materiality & climatic/ecological engine tying it all together (1 short line)."
  },
  "thesis_detailed": "Full 4-5 sentence detailed architectural thesis & signature physical gesture narrative (revealed via View detailed brief toggle)...",
  "engine_trace": {
    "drivers": {
      "crystals": "Hydrology & Waterfront (76.1/100) + Solar & Climate Intensity (72.4/100)",
      "cells": "Solar & Climate Intensity (71.0/100) — extreme evaporation & wadi runoff interface",
      "corals": "Corridor & Network Connectivity (48.8/100) — 22 m to primary arterial highway"
    },
    "baseline_proposal": "Hydrology & Waterfront + Solar & Climate Intensity Synergy (1,428 m² local catchment baseline)",
    "synthesis_note": "2-3 sentences explaining why NEST chose Select vs. Merge and how Stage A's Nature-First Spatial Force heatmaps and GIS drivers were elevated into the winning mega-landmark."
  },
  "idiom": "Tectonic Idiom name",
  "precedent": "Precedent 1 + Precedent 2",
  "nature_to_bldg": "How nature runs/supports the building...",
  "bldg_to_nature": "How the building restores/protects nature...",
  "activities": ["Activity 1", "Activity 2", "Activity 3", "Activity 4"],
  "spaces": [
    ["Primary Zone Name", "8,200 m²", "24/7"],
    ["Cores, MEP & Circulation Tare", "3,300 m²", "24/7"]
  ],
  "landscape_summary": {
    "backbone": "Primary connected hydrological/ecological landscape spine organizing the 50–70 feddan site...",
    "arch_interface": "How building clusters frame, buffer, or depend on the surrounding landscape zones...",
    "tradeoffs_risk": "Explicit ecological, hydrological, water-demand, or maintenance trade-offs (never hidden inside aggregate scores)..."
  },
  "landscape_zones": [
    {
      "id": "L-01",
      "name": "Wadi Hydrological Preservation Corridor",
      "family": "Natural / Preserved Landscape",
      "intervention": "Preserve",
      "area_m2": 92000,
      "area_ha": 9.2,
      "area_feddans": 21.9,
      "share_pct": 36.5,
      "color": "#246247",
      "geom": { "type": "Polygon", "coordinates": [] }
    }
  ],
  "fin": {
    "capex": "$78.5M",
    "capex_bldg": "$58.0M",
    "capex_landscape": "$20.5M",
    "rev": "$19.8M/yr",
    "roi": "12.6%",
    "irr": "15.4%",
    "payback": "7.9 yrs",
    "scenarios": "Conservative: ... | Base: ... | Upside: ...",
    "pilot": "$4.2M (12 months) — ...",
    "prov": "Spatial: 80% Observed, 20% Estimated | Financial: 0% Observed, 100% Estimated (...)"
  },
  "econ_evidence": {
    "revenue_mix": [
      { "stream": "Water Off-Take PPP", "share_pct": 37, "annual_rev": "$7.4M" },
      { "stream": "Solar Cold-Chain", "share_pct": 24, "annual_rev": "$4.8M" },
      { "stream": "Solar PPA", "share_pct": 21, "annual_rev": "$4.2M" },
      { "stream": "Museum & Grants", "share_pct": 18, "annual_rev": "$3.4M" }
    ],
    "demand_highlights": [
      {
        "highlight": "Arterial corridor within 22 m links Sinai farms to mainland markets with zero solar cold-chain capacity nearby",
        "source": "GIS Roads + Sinai Context",
        "basis": "Observed"
      },
      {
        "highlight": "Flash-flood harvesting + solar desalination addresses acute regional arid-water deficit",
        "source": "Egypt Vision 2030 / MWRI",
        "basis": "Benchmark"
      }
    ],
    "funding_partners": ["TSFE", "EBRD / GCF", "MWRI PPP", "Golden License"],
    "sources": [
      { "label": "Spatial Drivers", "type": "Observed", "reference": "Direct GIS (50 m grid)" },
      { "label": "CapEx ($2,450/m²)", "type": "Benchmark", "reference": "Egypt/MENA Civic-Infra PPP" },
      { "label": "Water & Solar Tariffs", "type": "Benchmark", "reference": "EBRD / Egypt PPA Benchmarks" }
    ]
  },
  "harmful_note": null,
  "hypotheses": [
    ["H1 (Winner)", "Concept...", "Nature-Safe / Regenerative", "PASS — SELECTED"],
    ["H2", "Concept...", "🔴 HARMFUL TO THE ENVIRONMENT", "FLAGGED HARMFUL"],
    ["H3", "Concept...", "Nature-Safe", "REJECTED"]
  ],
  "geojson": { "type": "Polygon", "coordinates": [] },
  "footprints": [
    { "label": "Pavilion A — 8,200 m²", "geom": { "type": "Polygon", "coordinates": [] } }
  ]
}
```

---

## 7. Default Visual UI System (`UI Handover/`)

Every Stage B `nest_dashboard.html` **must** use the official **NEST 2.2 Visual Identity** from [`UI Handover/NEST_UI_DESIGN_GUIDE.md`](../UI%20Handover/NEST_UI_DESIGN_GUIDE.md) and [`UI Handover/nest-ui-starter.css`](../UI%20Handover/nest-ui-starter.css) as its **default skin** (replacing the legacy dark-slate `#0f172a` theme):

- **Brand & Engine Character Assets (Mandatory, Unmodified Proportions):**
  - Header left: [`UI Handover/logos/nest-wordmark-black.png`](../UI%20Handover/logos/nest-wordmark-black.png) (`~28 px` height / `130–160 px` wide) + [`UI Handover/logos/delab-colour.png`](../UI%20Handover/logos/delab-colour.png) (`~24 px` height / `40–64 px` wide), embedded as base64 data URIs so dashboards remain self-contained.
  - Top `4 px` dusty-rose (`#DDA199`) brand hairline bar across the header shell.
  - **Official 3-Engine Character Portraits ([`NEST Engine Graphics/`](../NEST%20Engine%20Graphics)):** Embed [`Crystals.png`](../NEST%20Engine%20Graphics/Crystals.png) (purple faceted Crystal, frame 1), [`Cells.png`](../NEST%20Engine%20Graphics/Cells.png) (rose-glass Cell, frame 5), and [`Corals.png`](../NEST%20Engine%20Graphics/Corals.png) (branching Coral, frame 1) as base64 data URIs (`ENGINE_GRAPHICS`) across the **3-Engine Heatmap Trace** boxes (Tab 1), the **Stage C Skill Representation Cards & Modal** (Tab 1), and the **Tab 2 Map Pane Badges & Click Drawer**—preserving original artwork and transparency without recolouring.
- **Typography:**
  - Bundled [`UI Handover/fonts/FunnelDisplay.ttf`](../UI%20Handover/fonts/FunnelDisplay.ttf) (`@font-face`, fallback `"Aptos", "Segoe UI", Arial, sans-serif`) for headings, body text, KPIs, and controls.
- **Core Semantic Palette Tokens:**
  - Canvas: `--nest-paper: #F5F5F5` · Soft Rose Surface: `--nest-soft: #FBEFED` · Card Surface: `linear-gradient(135deg, #ffffff, #fbefed)`
  - Dusty Rose: `--nest-rose: #DDA199` · Coral Primary Action: `--nest-coral: #FF614C` (hover `#FF735F`, raised `3 px` lower shadow `#A3473A`)
  - Ink & Borders: `--nest-ink: #302B2A` · `--nest-muted: #625753` · `--nest-line: #D5C9C5` · Deep Accent Bar (`3 px` left mark before titles): `--nest-edge: #A3473A`
  - Semantic Statuses: Success `#246247 / #EAF5EF`, Warning `#775014 / #FFF5E5`, Error `#A12B3A / #FCEEF0`.
- **Map & Analytical Color Guardrail:**
  - Never recolour satellite basemaps, 3-engine analytical heatmap rasters, or map legends merely to match brand rose/coral. Keep source map colors and attribution intact.

---

## 8. Export All Proposals PDF (`A4 Landscape` Executive Dossier)

Every Stage B `nest_dashboard.html` **must** include a zero-dependency **`⬇ Export Proposals PDF`** coral primary button in the Tab 1 proposals toolbar (adjacent to the `Summary View | Detailed Briefs` switch), powered by `exportProposalsPdf()` and a dedicated `@media print` stylesheet (`@page { size: A4 landscape; margin: 9mm 10mm; }`):

- **Print-Only Cover & Portfolio Spread (Page 1):** Hidden on screen (`display: none`), revealed in print with official NEST + DeLab logos, plot title/subtitle, date, and a 5-project Portfolio Comparison Table (`#`, Title, Engine Strategy, Tectonic Idiom, Built GFA, CapEx, Revenue, IRR, Payback) followed by a clean page break.
- **Full Executive Dossier Auto-Expansion:** Clicking **`⬇ Export Proposals PDF`** temporarily switches to Tab 1, activates **Detailed Briefs** mode, expands all `<details>` accordions (`Hypotheses, Catalytic Phase 0 Pilot & Full Data Provenance`), invokes `window.print()`, and automatically restores the user's exact prior UI state on `afterprint`.
- **Reliable Print Maps & Landscape Spreads:** Each project starts cleanly on a new A4 Landscape page with side-by-side **Editorial Aerial Render (`renders/site_<N>.jpg`)** + **Static Satellite Site Lock (`renders/render_pack/site_<N>_satellite_lock.png`)** (swapping out live Leaflet tiles in `@media print` so maps never clip or render blank) above a 2-column horizontal brief spread. Interactive-only chrome (tabs, jump bar, map controls, Stage C Skill Action Bar, modals) is hidden in print.
- **Stage C Design Skills Spread:** Whenever `generated_skills` are populated on a project, a dedicated print-only A4 Landscape **Stage C Design Skills** spread follows each project's brief, presenting all 6 site-grounded skills (`3 Crystals Engine` purple-accented + `3 Corals Engine` coral-accented) with engine character portraits, triggers, proactive action callouts, core attributes, and platform tool tags.


