# NEST Stage B Fast-Track Quick-Reference & Parallel Fan-Out Contract

> **Purpose:** Compact Stage B execution card (~2–3 min target via **Hybrid Seed + Parallel 5-Site Fan-Out**) replacing sequential 540 KB raw-GeoJSON authoring while preserving bespoke design, diversity, and `0`-error geometry.  
> **Expander Tool:** [`stage_b_builder.py`](../stage_b_builder.py)  
> **Full Reference Atlases:** [`NEST_Experience_Design.md`](./NEST_Experience_Design.md) · [`NEST_Architectural_Direction.md`](./NEST_Architectural_Direction.md) · [`NEST_Form_Material_Site_Atlas.md`](./NEST_Form_Material_Site_Atlas.md) · [`NEST_Space_Program_Atlas.md`](./NEST_Space_Program_Atlas.md) · [`NEST_Concept_Statement_Direction.md`](./NEST_Concept_Statement_Direction.md)

---

## 1. Two-Phase Stage B Execution (2–3 Min Target)

### Phase 1 — Coordinator Portfolio Lock (~30 s)
1. Read `intermediates/agent_site_context.md` (single-file brief with parcel shape/bearing, DEM relief, 10 m open-land quadrants, nearby named GIS landmarks, and the full Creative & Site-Grounding Contract).
2. Select the **5 Sites** (`candidate_rank`) and lock a **Non-Overlapping Portfolio Matrix** *before* spawning any subagents:
   - Each site gets a unique **`idiom`** (`courtyard`, `terrace`, `cantilever`, `clustered_compound`, `bridge`).
   - Each site gets a unique **`concept_register`** (`Limestone & Wind-Tower`, `Earth & Rammed Mass`, `Timber & Tensile Shade`, `Steel & Solar Canopy`, `Vaulted Brick & Courtyard`).
   - Each site gets a unique **`primary_material`** and **`program_anchor`** (never repeat the same building/program pairing twice, and never use banned RFP clichés like `Hub`, `Precinct`, `Campus`, `Innovation`, `Pavilion`).
   - Target realistic GFA: **`8,000–22,000 m²` total** (`2,500–8,000 m²` per volume for craft, cultural, or eco-hospitality clusters; up to `35,000 m²` only for major civic/mixed-use hubs) across `50–70 feddans`.
   - Each building's `interior_zones` (`{name, role, area_m2}`) must list **6–10 realistic rooms** (`150–800 m²` typical) plus explicit **`Circulation & Tare` / `BOH & MEP`** rows (`15%–30%` of volume GFA); `stage_b_builder.py` exports `space_program.json` & `space_program.csv`.

### Phase 2 — 5 Parallel Subagents → `stage_b_builder.py` → `run_nest_pipeline.py`
- Spawn **5 parallel `self` subagents** (`site_1_seed.json`..`site_5_seed.json` in `intermediates/seeds/`).
- Each subagent writes **only ~3 KB of design & narrative** (zero raw GeoJSON coordinates, zero area/IRR arithmetic).
- Run `python stage_b_builder.py --run-dir <out_dir> --seeds-dir <out_dir>/intermediates/seeds` to generate `stage_b_projects.json` with `100.0%` landscape area reconciliation, `0` Preserve encroachments, and exact `fin` math.
- Write `NEST_Executive_Report.md` comparing the 5 sites, then run `python run_nest_pipeline.py --data-dir <gis_dir> --out-dir <out_dir> --skip-stage-a`.

---

## 2. Compact `site_<N>_seed.json` Schema

```json
{
  "rank": 1,
  "candidate_rank": 1,
  "target_feddans": 58.0,
  "site_bearing_deg": 22.0,
  "title": "Short Catchy Place Name (2-4 simple words, e.g. The Salt Mist Garden)",
  "subtitle": "Simple 6-10 word line a kid can picture",
  "nature_hero": "3-5 simple words (e.g. Sea Breeze & Salt Marshes)",
  "tier": "Tier 1: Flagship National Landmark",
  "idiom": "mat_courtyard",
  "concept_register": "Civic & Warm",
  "precedent": "1-2 real precedents + why they apply",
  "thesis_summary": {
    "hook": "<= 28-word competition headline naming what the building is early.",
    "why_here": "1 short line citing GIS trigger.",
    "key_program": "1 short line naming paired uses.",
    "gesture_line": "1 short line describing form + materials + passive engine."
  },
  "thesis_detailed": "150-250 word 3-Act narrative ending in a 10-18 word pull-quote.",
  "engine_trace": {
    "drivers": {"crystals": "...", "cells": "...", "corals": "..."},
    "baseline_proposal": "...",
    "synthesis_note": "2-3 sentences on Select vs Merge."
  },
  "nature_to_bldg": "How nature cools/powers/supports the building.",
  "bldg_to_nature": "How the building recharges/protects the ecosystem.",
  "experience_arc": {
    "core_idea": "1-2 sentences on the novel, visually stunning architectural idea celebrating nature.",
    "arrival": "How guests arrive and transition into the natural hero.",
    "core_encounter": "The signature nature-celebration moment and what happens there.",
    "activities_loop": "Secondary trails, workshops, and built elements across the 50–70 feddans.",
    "dining_retail": "Experience-curated food, beverage, and artisan/nature retail.",
    "stay_overnight": "Eco-accommodation or dusk-to-dawn experience (or day-to-dusk note).",
    "atmosphere": "Materials, light, shadow, acoustics, breeze, and visual character."
  },
  "visual_direction": {
    "architectural_language": "Bold tectonic character across all structures (cantilevers, vaults, shells, terraced strata, or shaded courts).",
    "aerial_composition": "How the dispersed buildings and landscape trails sit inside the 50-70 feddan polygon.",
    "hero_threshold_scene": "The single primary entrance/hero space and human activity for the close human-threshold shot.",
    "lighting_mood": "Specific time of day, sky, shadow contrast, and interior glow (e.g., deep blue twilight with warm lantern glow).",
    "materials_palette": "Authentic regional materials and tactile textures (zero m2 or generic buzzwords).",
    "camera_cue": "Optional architectural camera/vantage cue (e.g., 'low oblique looking across the tidal pool toward the arched soffit')."
  },
  "activities": ["Activity 1", "Activity 2", "Activity 3", "Activity 4"],
  "spaces": [
    {
      "name": "Salt-Marsh Propagation & Viewing Hall",
      "area": "18,000 m²",
      "hours": "08:00–21:00",
      "users": "Botanists, school groups, weekend families",
      "site_trigger": "Adjacent brackish marsh edge",
      "explanation": "Walk-through planted beds where visitors watch coastal crop trials beside a shaded viewing ramp."
    }
  ],
  "landscape_summary": {
    "backbone": "...",
    "arch_interface": "...",
    "tradeoffs_risk": "..."
  },
  "landscape_zones": [
    {"name": "Salt-Marsh Preserve", "family": "Ecological Preserve", "intervention": "Preserve", "share_pct": 30, "why_here": "...", "outdoor_activities": "..."},
    {"name": "Native Dune Belt", "family": "Ecological Restoration", "intervention": "Restore", "share_pct": 24, "why_here": "...", "outdoor_activities": "..."},
    {"name": "Cistern Shade Spine", "family": "Climate & Water", "intervention": "Enhance", "share_pct": 22, "why_here": "...", "outdoor_activities": "..."},
    {"name": "Public Arrival Forum", "family": "Civic Activation", "intervention": "Activate", "share_pct": 24, "why_here": "...", "outdoor_activities": "..."}
  ],
  "volumes": [
    {
      "name": "Woven Limestone Herbarium",
      "use": "Galleries, Seed Lab & Night Study Hall",
      "area_m2": 36000,
      "floors": 2,
      "archetype": "courtyard",
      "shape_reason": "Carved inner courts trap cool sea air while shading glazing.",
      "interior_zones": [
        {"name": "Arrival Commons", "category": "public", "tier": "L1", "area_m2": 10000, "access": "Public", "hours": "07:00–23:00"},
        {"name": "Seed & Soil Lab", "category": "research", "tier": "L1-L2", "area_m2": 16000, "access": "Restricted", "hours": "24/7"},
        {"name": "Night Study & Archive", "category": "cultural", "tier": "L2", "area_m2": 10000, "access": "Public", "hours": "07:00–24:00"}
      ]
    }
  ],
  "orientation": "Why building faces wind/sun/viewshed.",
  "shape_logic": "How 3D form emerges from site + idiom.",
  "financials": {
    "building_capex_usd_per_m2": 1850,
    "landscape_capex_usd_per_m2": 75,
    "annual_rev_m_usd": 19.5,
    "opex_ratio": 0.34,
    "funding_partners": ["TSFE Co-Investment", "Private Operator Concession"]
  }
}
```

---

## 3. Hard Quality Gates (Zero Compromises)
- **Vocabulary Gate:** No `sanctuary`, `citadel`, `oasis` (as building noun), `Pleistocene`, `littoral`, `stewardship`, `micro-pile`.
- **Zero-Overlap 4-Block Contract:** Never repeat verbs, shapes, or cooling claims across `hook`, `why_here`, `gesture_line`, and the `pull-quote`.
- **No Raw Coordinates in Seeds:** Let `stage_b_builder.py` clip and reconcile all polygons and numbers.
