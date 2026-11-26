# Stage C: Project Skill Generation Workflow (`Crystals Engine` + `Corals Engine` + `Cells Engine`)

> **Canonical Engine Identity:** See [`engine_charter.md`](./engine_charter.md) for the universal cognitive themes (**Crystals = Development**, **Corals = Coordination**, **Cells = Adaptation**).  
> **Master Architecture:** See [`WORKFLOW.md`](./WORKFLOW.md) for the end-to-end `Stage A → Stage B → Stage C` pipeline, [`skill_defintion.md`](./skill_defintion.md) for the universal skill envelope (`definition`, `parent_engine`, `trigger`, `action`, `attributes`), [`crystal_engine_skill_definition.md`](./crystal_engine_skill_definition.md) for **Crystals Engine** skill attributes, [`corals_engine_skill_definition.md`](./corals_engine_skill_definition.md) for **Corals Engine** skill attributes, and [`cells_engine_skill_definition.md`](./cells_engine_skill_definition.md) (Section 12) for **Cells Engine** skill attributes.
>
> **Active Engine Scope:** All three engines — **`Crystals Engine`**, **`Corals Engine`**, and **`Cells Engine`** — actively generate Stage C skills.

---

## 1. Trigger & Execution Model (Strictly On-Demand — Stage C)

1. **When Stage C Runs:**
   - Stage A (`run_3_engines.py`) and Stage B (`nest_workflow.md`) prepare the 5 Project Cards in `nest_dashboard.html` along with pre-packaged `skill_seeds` in `intermediates/stage_a_summary.json` and `NEST_PROJECTS[i].skill_seeds`.
   - **Stage C runs on demand** when the user selects one of the 5 projects from the NEST dashboard (e.g., *"Generate skills for Project #1"* or clicking **`Generate Project Skills →`** on a project card).
2. **Inputs Consumed by Stage C for the Selected Project (`#rank`):**
   - The selected project's complete Stage B brief (`NEST_PROJECTS[rank - 1]` in `nest_dashboard.html` and Section `#rank` in `NEST_Executive_Report.md`):
     - `title`, `strategy` (`Select` vs. `Merge`), `tier`, `built_gfa`, `area_m2`, `footprint_type`, `footprints[]`
     - `map_pointers[]` (1–5 exact GIS features, distances in `m`, source layers, and provenance)
     - `thesis_summary`, `thesis_detailed`, `idiom`, `precedent`, `engine_trace`
     - `nature_to_bldg` & `bldg_to_nature` (Two-Way Nature Integration)
     - `activities[]` & `spaces[]` (GFA `m²` & operating hours)
     - `hypotheses[]` & `harmful_note` (including rejected or `Harmful to the Environment` alternatives)
   - The project's Stage A `observed_plot_telemetry` (TMY station `GHI`, `ETo`, `CDH`, DEM slope `° / %`, WorldPop, MPED governorate budgets) and `skill_seeds` from `intermediates/stage_a_summary.json`.

---

## 2. Stratified Skill Allocation & Domain Slots (6–9 Skills per Project; 9 Default)

Even if a project was a single-engine `Select` proposal, **all three engines (`Crystals`, `Corals`, `Cells`) contribute specialist skills** in Stage C, stratified by their role in the project's strategy (`Primary Lead` vs. `Specialist Contributor`):
- **Default Complete Set:** **9 skills total** (**3 `Crystals Engine`** + **3 `Corals Engine`** + **3 `Cells Engine`**), or **6–9 dynamically weighted toward the project's Lead Engine(s)** (e.g., `3` from the Primary Lead engine + `2` from each supporting engine = `7` skills, or `3 + 3 + 3 = 9` for multi-engine merges / flagship projects).
- Every skill must be grounded in **exact site numbers, distances, climate metrics, and spatial zones** from Stage A + Stage B—never generic architectural advice.

### A. Crystals Engine Skill Slots *(Development — Building Around, In, or At Points of Interest)*
Follows [`crystal_engine_skill_definition.md`](./crystal_engine_skill_definition.md) (`scale`, `facets`, `axes`, `density`, `growth`, `field`, `state`, `memory`, `bonds`, `resilience`):

| Slot | Filename Slug | Architectural Decision & Knowledge Base | Typical `action.type` & Target Tools |
| :--- | :--- | :--- | :--- |
| **Crystal Skill 1** | `crystal_01_poi_viewshed_axis.json` | **POI Standoff, Viewshed & Solar/Datum Axis Rule:** Enforces exact GIS build-around / build-at standoff distances (`ring_decay` buffer to heritage, waterfront, or civic POIs), skyline caps, and primary solar/view axes. | `Warning` or `Guidance` · `["QGIS", "Grasshopper", "Autodesk Forma", "Revit"]` |
| **Crystal Skill 2** | `crystal_02_tectonic_climate_envelope.json` | **POI-Anchored Tectonic Envelope & Climate Thresholds:** Governs the signature tectonic system (canopy perforation `%`, earth-bermed thermal mass thickness, structural micro-piles/pontoons, glazing ratio) calibrated to observed TMY `GHI`, `ETo`, and `CDH`. | `Study` or `Guidance` · `["Ladybug", "Honeybee", "Grasshopper", "Revit"]` |
| **Crystal Skill 3** | `crystal_03_program_stacking_gfa.json` | **Programmatic Stacking, Adjacency & GFA/Tare Calibration:** Enforces the project's exact `Built GFA (m²)`, Net-to-Gross efficiency ratio, acoustic/thermal zoning across pavilions (`footprints[]`), and public-to-private staging around the POI. | `Guidance` or `Warning` · `["Revit", "Grasshopper"]` |

### B. Corals Engine Skill Slots *(Coordination — Using Elements Better Together / Beneficial Relationships)*
Follows [`corals_engine_skill_definition.md`](./corals_engine_skill_definition.md) (`resources`, `branches`, `symbiosis`, `evaluation`, `state`, `adaptation`, `archive`):

| Slot | Filename Slug | Architectural Decision & Knowledge Base | Typical `action.type` & Target Tools |
| :--- | :--- | :--- | :--- |
| **Coral Skill 1** | `coral_01_multi_element_coordination.json` | **Multi-Element Site & Context Coordination:** Pairs `2+` distinct site, natural, civic, or contextual elements (`map_pointers`) into a mutually beneficial relationship, opening `2–3` maturing/exploratory coordination branches (`direction`, `maturity`, `application`, `tool`). | `Prompt` or `Guidance` · `["Ladybug", "Autodesk Forma", "Grasshopper", "QGIS"]` |
| **Coral Skill 2** | `coral_02_two_way_nature_symbiosis.json` | **Two-Way Nature Symbiosis & Mutualistic Loop:** Coordinates living natural flows (`Nature → Building`) and regenerative architectural outputs (`Building → Nature`) with local community/economic activities (`symbiosis` pairs), specifying required validation studies (`evaluation.studies_needed`). | `Study` or `Prompt` · `["Ladybug", "QGIS", "Grasshopper"]` |
| **Coral Skill 3** | `coral_03_shared_network_archive.json` | **Alternative Coordination Pairings & Rejected-Loop Archive:** Preserves rejected or paused multi-element coordination hypotheses (`H2`, `H3`) inside `archive.retained_explorations` with exact reasons, redirecting beneficial relationships into nature-safe shared networks. | `Alternative` or `Warning` · `["Autodesk Forma", "Revit", "QGIS"]` |

### C. Cells Engine Skill Slots *(Adaptation — Unlocking an Element's Full Potential by Adapting It Into Something New/Better)*
Follows [`cells_engine_skill_definition.md`](./cells_engine_skill_definition.md) Section 12 (`host_element`, `latent_potential`, `adaptation_pathway`, `gene_refs`, `novelty`, `confidence`, `reinterpretation_fallback`, `state`, `evolution_memory`):

| Slot | Filename Slug | Architectural Decision & Knowledge Base | Typical `action.type` & Target Tools |
| :--- | :--- | :--- | :--- |
| **Cell Skill 1** | `cell_01_host_element_adaptation.json` | **Primary Site/Nature/Context Element Adaptation:** Targets a high-potential natural or contextual element (landform, cave, quarry, ruin, seasonal wadi, underused shoreline) and defines reversible/phased adaptation pathways that transform it into something new and better. | `Study` or `Prompt` · `["Ladybug", "Autodesk Forma", "Grasshopper", "Revit"]` |
| **Cell Skill 2** | `cell_02_extreme_climate_mutation.json` | **Climatic / Ecological Constraint-to-Asset Adaptation:** Adapts an environmental extreme (high `GHI`/`ETo`/`CDH`, flash runoff, salinity, wind exposure) into a passive-performing architectural or ecological engine, explicitly flagging unknowns and confidence caps. | `Study` or `Guidance` · `["Ladybug", "Honeybee", "QGIS", "Grasshopper"]` |
| **Cell Skill 3** | `cell_03_reinterpretation_fallback.json` | **Novelty Escalation & Safe Reinterpretation Fallback:** Guards against unverified site assumptions (Rule H/I), defining a low-impact reinterpretation fallback if direct physical adaptation of a sensitive or harmful element is blocked. | `Alternative` or `Warning` · `["Autodesk Forma", "Revit", "QGIS"]` |

---

## 3. Strict JSON Schema Contract

### 3A. Crystals Engine Skill JSON (`crystal_*.json`)
```json
{
  "skill_id": "crystal_01_viewshed_solar_axis",
  "title": "Human-Readable Skill Title",
  "definition": "Concise overview of the skill's analytical knowledge base and target architectural decision.",
  "parent_engine": "Crystals Engine",
  "role_in_project": "Primary Lead | Specialist Contributor",
  "trigger": [
    "Specific modeling action or design phase trigger 1",
    "Specific site grading, massing, or envelope trigger 2"
  ],
  "action": {
    "type": "Warning | Prompt | Study | Guidance | Alternative",
    "message": "Direct, quantitative, actionable instruction or warning surfaced to the architect at the moment of the trigger."
  },
  "attributes": {
    "scale": "Atom | Molecule | Crystal | Cluster",
    "facets": [
      {
        "capability": "Specific analytical or geometric check performed",
        "tool": ["QGIS", "Grasshopper", "Revit"]
      }
    ],
    "axes": {
      "space": "Exact spatial zone / parcel / pavilion footprint",
      "time": "Design phase or seasonal/diurnal cycle",
      "depth": "Shallow | Medium | Deep"
    },
    "density": "Verified | Inferred",
    "growth": "Iterative | Linear | Branching",
    "field": "Environmental | Material | Machine | Creative | Urban | Human | Program | Engineering",
    "state": "Growing | Stable | Melting",
    "memory": {
      "past_experiences": ["Stage A/B spatial derivation note"],
      "usage_history": [],
      "feedback": [],
      "lessons_learned": ["Key site-specific rule learned"]
    },
    "bonds": ["Environmental", "Urban", "Engineering"],
    "resilience": "Resistance | Adapt"
  }
}
```

### 3B. Corals Engine Skill JSON (`coral_*.json`)
```json
{
  "skill_id": "coral_01_resource_branching_narrative",
  "title": "Human-Readable Skill Title",
  "definition": "Concise overview of the skill's creative resource-branching knowledge base and target architectural experience.",
  "parent_engine": "Corals Engine",
  "role_in_project": "Primary Lead | Specialist Contributor",
  "trigger": [
    "Specific siting, circulation, or resource-interface trigger 1",
    "Specific program or environmental condition trigger 2"
  ],
  "action": {
    "type": "Warning | Prompt | Study | Guidance | Alternative",
    "message": "Creative prompt, multi-branch design question, or nature-safe alternative surfaced to the architect."
  },
  "attributes": {
    "resources": [
      {
        "resource": "Exact GIS site resource & distance",
        "potential": "Creative or functional opportunity unlocked",
        "constraints": ["Specific ecological, heritage, or technical limit"]
      }
    ],
    "branches": [
      {
        "direction": "Design possibility being explored",
        "maturity": "Exploratory | Maturing | Specialized",
        "application": "Concrete spatial application on site (or null if Exploratory)",
        "tool": ["Ladybug", "Autodesk Forma", "Grasshopper"]
      }
    ],
    "symbiosis": [
      {
        "with": ["Connected Skill or Resource A", "Connected Skill or Resource B"],
        "shared_intention": "Emergent architectural intention unlocked together"
      }
    ],
    "evaluation": {
      "status": "Hypothesized | Under Study | Evaluated | Validated",
      "criteria": {
        "creativity": "Experiential & formal originality",
        "resource_connection": "How effectively site resources are linked & preserved",
        "feasibility": "Known engineering/cost findings & limits"
      },
      "studies_needed": [
        "Specific simulation or field verification required"
      ]
    },
    "state": "Branching | Maturing | Active | Dormant | Reinterpreting",
    "adaptation": "Redirect | Regenerate | Reinterpret | Hold",
    "archive": {
      "retained_explorations": [
        "Rejected or paused exploration kept with its reason for future revival/reinterpretation"
      ],
      "validated_knowledge": [
        "Observed GIS / TMY / MPED fact backing this skill"
      ],
      "lessons_learned": [
        "Synthesized takeaway carried across the project"
      ]
    }
  }
}
```

### 3C. Cells Engine Skill JSON (`cell_*.json`)
```json
{
  "skill_id": "cell_01_host_element_adaptation",
  "title": "Human-Readable Skill Title",
  "definition": "Concise overview of the site/nature/context element being adapted and the latent potential it unlocks.",
  "parent_engine": "Cells Engine",
  "role_in_project": "Primary Lead | Specialist Contributor",
  "trigger": [
    "Specific element-interface, grading, microclimate, or adaptive-reuse trigger 1",
    "Specific program or environmental-condition trigger 2"
  ],
  "action": {
    "type": "Warning | Prompt | Study | Guidance | Alternative",
    "message": "Actionable adaptation pathway, evidence/unknown check, or safe reinterpretation fallback surfaced to the architect."
  },
  "attributes": {
    "host_element": {
      "element": "Exact natural or contextual/man-made element & location/metric",
      "current_state": "Current underused condition or perceived constraint",
      "element_class": "Natural | Climatic | Hydrological | Ecological | Geological | Contextual / Man-Made"
    },
    "latent_potential": "Untapped architectural, ecological, or experiential value unlocked by adapting this element",
    "adaptation_pathway": [
      {
        "mutation": "Concrete transformation into something new/better",
        "reversibility": "Reversible | Phased | Permanent",
        "tool": ["Ladybug", "Grasshopper", "Revit"]
      }
    ],
    "gene_refs": ["gene_mechanism_or_check_id"],
    "novelty": "familiar | partial | novel",
    "confidence": {
      "level": "low | medium | high",
      "score": 0.45,
      "unknowns": ["Explicit missing site measurement or verification needed"]
    },
    "reinterpretation_fallback": "Safe design reinterpretation if direct physical adaptation is blocked",
    "state": "idle | active | blocked | review | complete | retired",
    "evolution_memory": {
      "provisional_assumptions": ["Provisional assumption awaiting site verification"],
      "escalation_needed": "Project-lead or specialist escalation ask (or null)",
      "lessons_learned": ["Candidate gene or takeaway carried forward"]
    }
  }
}
```

---

## 4. Stage C Output Bundle & Dashboard Integration

When Stage C is executed for Project `#<rank>`, it produces two synchronized deliverables:

### 4A. Disk Skill Bundle (`<run_output_dir>/skills/project_<rank>_<slug>/`)
```text
<run_output_dir>/skills/project_<rank>_<slug>/
├── SKILL_INDEX.md                              # Human-readable overview of all generated skills, triggers, actions & tools
├── crystal_01_poi_viewshed_axis.json           # Crystals Skill 1 (POI Standoff, Viewshed & Solar/Datum Axis)
├── crystal_02_tectonic_climate_envelope.json   # Crystals Skill 2 (POI-Anchored Tectonic Envelope & Climate Thresholds)
├── crystal_03_program_stacking_gfa.json        # Crystals Skill 3 (Program Stacking, GFA & Staging)
├── coral_01_multi_element_coordination.json    # Corals Skill 1 (Multi-Element Site & Context Coordination)
├── coral_02_two_way_nature_symbiosis.json      # Corals Skill 2 (Two-Way Nature Symbiosis & Mutualistic Loop)
├── coral_03_shared_network_archive.json        # Corals Skill 3 (Alternative Pairings & Rejected-Loop Archive)
├── cell_01_host_element_adaptation.json        # Cells Skill 1 (Primary Host Element Adaptation)
├── cell_02_extreme_climate_mutation.json       # Cells Skill 2 (Climatic / Ecological Constraint-to-Asset Adaptation)
└── cell_03_reinterpretation_fallback.json      # Cells Skill 3 (Novelty Escalation & Safe Reinterpretation Fallback)
```
*(When dynamically weighted to 6–8 skills, omit the lowest-priority slot(s) from supporting engines while keeping all 3 slots for the Primary Lead engine.)*

### 4B. Live Dashboard Update (`<run_output_dir>/nest_dashboard.html`)
1. Inject the array of generated skill JSON objects into `NEST_PROJECTS[rank - 1].generated_skills`.
2. Update the project card's Skill Action Bar badge to **`✓ <N> Stage C Design Skills Generated (Crystals · Corals · Cells)`** and button text to **`View & Export Project Skills (<N>) →`**.
3. Clicking the button opens the **Stage C Project Skills Master-Detail Modal** (using the official engine character graphics from [`NEST Engine Graphics/`](../NEST%20Engine%20Graphics) — `Crystals.png` [Purple Crystal], `Cells.png` [Rose-Glass Cell], `Corals.png` [Branching Coral]):
   - **Top Toolbar:** Engine filter tabs (`All Skills (<N>)` | `Crystals Engine` | `Corals Engine` | `Cells Engine`) with character icons and a **`⬇ Download All Skills (.JSON)`** bundle button.
   - **Left Master Column (Minimalist Pill Cards):** A clean vertical list of the **Minimalist Pill Cards**, each showing only the **Official Engine Character Portrait + Engine Badge**, **`action.type` pill** (`Warning`, `Guidance`, `Prompt`, `Study`, `Alternative`), **Skill Title**, **Platform Tool Tags** (`Revit`, `Grasshopper`, `Ladybug`, `Autodesk Forma`, `QGIS`), and a 1-click **`⬇ .json`** download button.
   - **Right Detail Column (3 Sub-Tabs):** Clicking any Minimalist Pill Card on the left displays its details on the right organized into **3 focused Sub-Tabs** (so only one clean chunk is visible at a time):
     - **Sub-Tab 1 (`1. Trigger & Action`):** Skill Definition box, numbered **`WHEN IT WAKES UP (Triggers)`** cards, and a highlighted **`WHAT IT PROACTIVELY DELIVERS (Action)`** callout box.
     - **Sub-Tab 2 (`2. Engine Attributes`):**
       - **For `Crystals Engine` (Purple `#9333ea` accent — Development):** 4-tile metric grid (`Scale | Data Density | Primary Field | Resilience`), `Axes & Cross-Field Bonds` box (`Space · Time · Depth`), `Executable Facets & Platform Tools` cards, and `Crystal Memory & Lessons Learned`.
       - **For `Corals Engine` (Warm Coral `#FF614C` / `#A3473A` accent — Coordination):** 4-tile metric grid (`Coral State | Adaptation | Evaluation | Project Role`), `Coordinated Site Elements & Constraints` cards, `Coordination Branches & Maturation` cards (`Exploratory` / `Maturing` / `Specialized` + tool pills), `Symbiosis With` box, and `Coral Archive (Retained Explorations vs. Validated Evidence)`.
       - **For `Cells Engine` (Rose-Glass `#BE185D` / `#EC4899` accent — Adaptation):** 4-tile metric grid (`Element Class | Novelty | Confidence | Lifecycle State`), `Host Element & Latent Potential` box, `Adaptation Pathways & Reversibility` cards (`Reversible` / `Phased` / `Permanent` + tool pills), `Skill Genome (Gene Refs) & Reinterpretation Fallback` box, and `Evolution Memory & Escalations`.
### 4C. Standalone Single-Project Export Package (`<run_output_dir>/exports/project_<rank>_<slug>/` + `.zip`)
Every project card (`#1`–`#5`) in `nest_dashboard.html` includes a **`⬇ Export Project Folder (.ZIP)`** download button and a **`1-Project HTML ↗`** button backed by `<run_output_dir>/exports/project_<rank>_<slug>/` (and `project_<rank>_<slug>.zip`), containing:
1. **`project_<rank>_dashboard.html`:** A 100% self-contained **Single-Project NEST 2.2 HTML Dashboard** displaying the project's render, interactive Leaflet satellite mini-map with numbered GIS feature pointers, scannable & detailed architectural thesis, 3-engine force trace (with embedded `Crystals.png`, `Cells.png`, `Corals.png` character portraits), two-way nature integration, space program, financial KPIs, economic evidence, and an **inline full-width Master-Detail Tabbed Skill Representation Cards section** at the bottom of the page.
2. **`PROJECT_BRIEF.md`:** Clean Markdown project brief with embedded skill index table.
3. **`project_data.json` & `site_geometry.geojson`:** Complete structured project JSON plus a GIS/CAD-ready GeoJSON FeatureCollection containing the `site_boundary`, `building_footprint` massing polygons, and `gis_feature_pointer` points.
4. **`render/`:** `site_<rank>.jpg`, `site_<rank>_satellite_lock.png`, and `site_<rank>_prompt.md`.
5. **`skills/`:** All 6 generated `<skill_id>.json` files + `SKILL_INDEX.md` (or `skill_seeds.json` if Stage C has not yet been run on that project).
