# NEST System Workflow — Cross-Engine Synthesis & Emergent Program Generation

> **Master Architecture:** See [`WORKFLOW.md`](./WORKFLOW.md) for the overall `NEST ↔ 3 Engines` system architecture, autonomous execution model, Rule Precedence, and final output bundle.
>
> **Input / Output Role:** Ingests the 3 engines' outputs ([`engines_workflow.md`](./engines_workflow.md)), applies [`nature_first_design_principles.md`](./nature_first_design_principles.md), [`NEST_Landscape_Intelligence.md`](./NEST_Landscape_Intelligence.md) *(landscape-first)*, [`NEST_Architectural_Direction.md`](./NEST_Architectural_Direction.md), and [`NEST_Concept_Statement_Direction.md`](./NEST_Concept_Statement_Direction.md) *(competition-grade manifesto writing)*, **merges or selects** among the engine lenses, defines a **50–70 feddan (`21.0–29.4 ha`)** whole-site boundary for each of the Final 5 sites, and synthesizes **integrated Site (Landscape + Architecture) mega-national proposals** under the **Regenerative Monumentality** thesis.

---

## Stage 1: Engine Output & Observed Telemetry Ingestion
1. **Ingest Stage A Candidate Pool & 3-Engine Outputs** (from `intermediates/stage_a_summary.json`):
   - **6 NEST Nature-First Spatial Force Heatmaps** (`Hydrology & Waterfront`, `Solar & Climate Intensity`, `Biodiversity & Ecology`, `Heritage & Culture Gravity`, `Civic & Service Deficit`, `Corridor & Network Connectivity`) + `Multi-Force Synergy (2+ / 3+)` across Crystals, Cells, and Corals.
   - **Merit-Ranked Top 12–15 `candidate_pool`** (`≥ 600 m` spacing, zero artificial land/water caps), each tagged with `terrain_class` (`Dry Land` / `Shoreline Edge` / `Open Water`), `force_scores`, `top_drivers_by_engine`, `map_feature_pointers`, `accessibility`, `flags`, and organic boundary polygon.
   - **Auto-Extracted `observed_plot_telemetry`:** Real DEM slope (`surface_slope_median_deg`), TMY climate (`GHI`, `ETo`, `CDH`), WorldPop demographics, school/health gaps, verified MPED governorate investment budgets, national agricultural context, and `dataset-inventory.json` audit counts.
2. **Select the Final 5 Sites from the Top 12–15 Pool:**
   - Review the full `candidate_pool` to select the **5 strongest, most complementary sites** based on Rule Precedence, physical buildability (`Dry Land` / `Shoreline Edge` / justified `Open Water`), ecological value, and economic/architectural synergy—never blindly locked into the first 5 raw indices.
3. **Evidence & Data Provenance Audit:**
   - Ground every economic and architectural claim in Stage A's `observed_plot_telemetry` and `map_feature_pointers` first; where site-specific market data is missing, use transparent MENA/Egypt benchmarks and explicitly label every metric `Observed` vs. `Benchmark`.
4. **Regional & Environmental Knowledge Lookup (`EGYPT_KNOWLEDGE/`):**
   - Read the plot's `lat`/`lon` centroid (and `plot_title`) from `intermediates/stage_a_summary.json`, look up the matching **governorate** and nearest **special place(s)** in [`EGYPT_KNOWLEDGE/egypt_index.json`](../EGYPT_KNOWLEDGE/egypt_index.json) and its regional `.md` atlas, and blend their microclimate, prevailing wind, local geology/materials, living ecology, and cultural craft into Stage B (`experience_arc`, `Nature Hero`, and tectonic materials)—while **strictly honoring GIS/satellite ground truth** (never invent physical site features absent from the plot).

---

## Stage 2: Rule Precedence & Hard-Gate Screening
Evaluate every candidate site and proposal against NEST's strict priority hierarchy:

1. **Priority 1 — Financial Feasibility (Hard Gate):**
   - A project must not be financially unfeasible. Proposals that cannot achieve financial feasibility are **hard-rejected**.
2. **Priority 2 — Environmental Harm Flag & Mandatory Nature-Safe Alternative:**
   - If a project achieves financial feasibility *only* by harming or degrading the environment, NEST may report it **only with a bold `Harmful to the Environment` red flag**, and **must automatically propose a nature-safe feasible alternative** if one exists.
3. **Priority 3 — Physical, Access & Regulatory Screening:**
   - **Hard Exclusions:**
     - Physically inaccessible land (only when no feasible land/water/air route exists or terrain slope makes construction/access impossible, e.g., sheer cliffs `> 45°` or unnavigable hazards).
     - Areas occupied by immovable major infrastructure.
     - Existing dense urban fabric (for Crystals & Cells nature-first discovery).
   - **Accessibility Scoring:** Score the 5 Accessibility & Mobility indicators equally (`High = 100`, `Moderate = 50`, `Low = 15`).
   - **Mandatory Advisory Flags (Retain & Warn):**
     - `water_zone_warning` — site intersects water; surface explicit aquatic/marine construction and ecological precautions.
     - `policy_complexity` — multiple authorities, heritage preservation, or temporary/reversible-use permit pathways.
     - `emergency_access_alert` — evaluate emergency reachability against the Accessibility & Mobility thresholds (`≤ 15 min` High, `15–30 min` Moderate, `> 30 min` Low).
4. **Priority 4 — Nature-Linked Value Optimization:**
   - Among feasible options, optimize long-term economic return, diversified revenue streams, and multi-decade resilience where ecological preservation strengthens financial value.

---

## Stage 3: Cross-Engine Merging & Lens Selection
For each surviving candidate site, NEST compares the **Crystals**, **Cells**, and **Corals** scores and GIS drivers to decide whether to **select** a single dominant lens or **merge** multiple lenses:

| Mode | When NEST Uses It | Architectural Posture |
| :--- | :--- | :--- |
| **Select: Crystals (Development)** | Site holds a high-gravity Point of Interest (natural, cultural, infrastructural, or civic) to build around, in, or at with clear siting & economic gravity. | POI-anchored landmark development framing, staging, or inhabiting the focal anchor. |
| **Select: Cells (Adaptation)** | Site holds a natural or contextual/man-made element (landform, cave, extreme climate, seasonal wadi, quarry, ruin, underused edge) whose full potential can be unlocked by adapting it into something new/better. | Element-transformative, adaptive, reversible, or evolving structure that unlocks latent potential. |
| **Select: Corals (Coordination)** | Site contains disconnected natural, civic, cultural, or infrastructural elements that can work better together through a beneficial relationship. | Symbiotic connector, shared utility/mobility hub, or relational catalyst stitching elements together. |
| **Merge (Hybrid 2- or 3-Engine)** | Site shows strong complementary scores across multiple engines (e.g., *Crystals + Cells* developing around a POI while adapting a harsh microclimate/wadi; *Cells + Corals* adapting a quarry/wetland while coordinating it with village livelihoods). | Composite strategy combining the spatial strengths of each contributing engine while respecting the strictest ecological gate among them. |

---

## Stage 4: Whole-Site Framing (50–70 Feddans) → Landscape-First & Integrated Architecture Co-Synthesis
**Core Rule:** The **6 NEST Nature-First Spatial Forces** (*Hydrology & Waterfront, Solar & Climate Intensity, Biodiversity & Ecology, Heritage & Culture Gravity, Civic & Service Deficit, Corridor & Network Connectivity*) and `Multi-Force Synergy (2+ / 3+)` scores are treated strictly as **spatial force signals & capability proxies**, *not* as fixed building templates. Stage B thinks about the **entire 50–70 feddan Site (Landscape + Building as one unified system)**, driven jointly by [`NEST_Landscape_Intelligence.md`](./NEST_Landscape_Intelligence.md) *(which comes before the built environment)* and [`NEST_Architectural_Direction.md`](./NEST_Architectural_Direction.md).

### Step 4A: 50–70 Feddan Site Delineation & Landscape-First Site Framing (`NEST_Landscape_Intelligence.md`)
1. **Delineate the 50–70 Feddan Site Boundary (`210,042–294,058 m²` / `21.0–29.4 ha`):**
   - Stage A (`run_3_engines.py`) remains unchanged as pure spatial peak clusters. Starting from each selected Stage A peak, Stage B delineates an explicit, GIS-grounded **50–70 feddan (`21.0–29.4 ha`)** outer site boundary polygon respecting roads, water edges, dense urban fabric, and plot borders.
   - **Standard Target with Documented Exception:** `50–70 feddans` is the standard target for **all 5 sites**. A site may go below `50 feddans` **only** with an explicit documented exception when hard physical or plot-edge constraints make a 50-feddan envelope impossible.
2. **Run Landscape Intelligence Before the Built Environment:**
   - Perform the site reading across natural, spatial, and human/cultural structure (`NEST_Landscape_Intelligence.md` Sections 4–8): map opportunities/constraints, determine intervention levels (**Preserve**, **Restore**, **Enhance**, **Design & Activate**, **Minimal Intervention**), and establish the **Landscape Backbone**, major landscape destinations, connectors/thresholds, and ecological/hydrological protection corridors.
   - **No Fixed Landscape-to-Building Ratio:** Relative land allocations between landscape and architecture must emerge strictly from site evidence, ecological sensitivity, and project vision—never from a predetermined percentage.

### Step 4B: Integrated Site + Building Co-Synthesis (`NEST_Architectural_Direction.md` + `NEST_Landscape_Intelligence.md`)
1. **Deconstruct Engine Signals & Document Spatial Traceability (`engine_trace`):**
   - Extract *why* the site scored well across Crystals, Cells, and Corals (exact force scores, winning `2+`/`3+` synergy cliques, and top GIS layer drivers + distances from `stage_a_summary.json`).
   - Record an explicit **`engine_trace`** block for every final project showing each engine's score + top GIS driver contribution, the raw Stage A baseline force signal, and how NEST (`Select` vs. `Merge`) elevated those converging forces into the winning integrated Site + Building proposal.
2. **Apply NEST Discovery Principles & Thinking Models:**
   - Use **first-principles**, **abductive**, **lateral**, and **systems thinking** to:
     - **Search for Unusual Combinations** across geology, climate, ecology, hydrology, and local culture.
     - **Explore Environmental Contradictions** (heat vs. cooling, scarcity vs. seasonal water, fragility vs. activity) as design generators for both landform and architecture.
     - **Challenge Conventional Programs** by proposing distributed, modular, seasonal, phased, or reversible site + building interventions.
     - **Let Potential Emerge** from the site's natural processes and wider ecological/regional network.
3. **Multi-Hypothesis Co-Testing, Mandatory Nature Integration & Competition-Grade Landmark Gate:**
   - Inside the Step 4A landscape structure, co-generate **2–3 distinct integrated Site + Building hypotheses** per candidate site—each pairing a coherent landscape zoning concept with a mega-national architectural concept anchored in the 4 priority landmark archetypes and **Tier 1 (`15,000–80,000+ m²`) / Tier 2 (`5,000–15,000 m²`)** national scale benchmarks in [`NEST_Architectural_Direction.md`](./NEST_Architectural_Direction.md). Let landscape and building negotiate land allocations from evidence. Reject modest or under-scaled proposals (`< 5,000 m²` unless part of a `≥ 10 ha` monumental ecological/hydrological landwork).
   - **Mandatory Concept Standard (Integrating Nature, Not Just Inspired By Nature):** Every winning concept must prove **Two-Way Functional Exchange**—explicitly defining both **(1) `Nature → Building`** (how the living natural system actively runs, cools, powers, or supports the architecture) and **(2) `Building → Nature`** (how the architecture actively protects, feeds, or regenerates the ecosystem). Purely cosmetic or biomimetic concepts are **rejected and reworked**.
   - **Physical Surface & Human Access Consistency:** Stage B is free to design any land, shoreline, pile-supported, or floating aquatic structure, **provided it matches the actual surface inside the 50–70 feddan site boundary polygon** (never describe an earth-sheltered or rocky-headland building inside a 100% open-water polygon) **and explicitly states how people physically reach it** (road/path connection on dry land; slender pier/bridge to the real shoreline when offshore `≤ 300 m`; dedicated boat/ferry jetty & shuttle vessels when offshore `> 300 m`).
   - **Unified Rubric + Mandatory Visible Trade-Offs:** Score each integrated Site + Building hypothesis against the **5-Criteria Competition-Grade Architectural Impact Rubric** (*Landscape Redefinition, Iconic Silhouette & Aerial Legibility, Ecological Engine Performance, Civic/Cultural Gravity, Global Press & Jury Worthiness* — **20 pts each**, mandatory **≥ 75/100** pass gate, no criterion `< 12/20`), powered by both specs. **Mandatory Safeguard (per `NEST_Landscape_Intelligence.md` Section 10):** Every hypothesis **must** also display an explicit **Landscape Trade-Offs & Water/Resource Risk** callout alongside its score so serious ecological, hydrological, or maintenance trade-offs are never hidden inside an aggregate number.
   - **Portfolio Tectonic & Climatic Diversity Gate (Anti-Repetition):** Across the Top 5 sites in any run, **no two sites may share the same primary tectonic idiom or passive-cooling motif** (strictly max 1 vertical wind-tower / *malqaf* concept per run, and differentiate formal language by Egyptian region per [`NEST_Architectural_Direction.md`](./NEST_Architectural_Direction.md)).
   - **Competition-Grade Concept Statement & Rhetorical Diversity Gate ([`NEST_Concept_Statement_Direction.md`](./NEST_Concept_Statement_Direction.md)):** Author every project's `title`, `subtitle`, `thesis_summary` (`≤ 28-word` hook + 3 non-redundant beats), and `thesis_detailed` (`150–250 word` 3-Act Competition Narrative ending in a quotable jury pull-line) under the **Invisible Engine, Visible Reality** rule (zero raw engine jargon/scores), enforcing the **Adaptive Archetype-Driven Voice Matrix** (≥ 3 distinct registers across the Top 5) and passing the **6-point Pre-Output Jury Self-Audit** and **Banned Archispeak / AI Cliché Blacklist**.
   - **Stage B Validated Landscape Zoning Output (All 5 Sites):** For every winning site, produce GIS-contoured, organic **Landscape Zone polygons** (using clean human-readable zone names everywhere) strictly contained within the organic 50–70 feddan site boundary (no unintended overlaps/gaps), a reconciled **Landscape Zone Area Schedule** (`m²`, `ha`, `feddans`, `%` of total site area), the **Landscape Backbone**, and the **Architecture–Landscape Interface**. *(Reserve the full 8-map PDF set, GeoPackage, QGIS project, CSV/XLSX schedule, and full 12-section landscape deep-dive for the 1 selected project on demand in Stage C.)*
   - Select the winning emergent integrated Site + Building landmark (or phased catalytic combination) with explicit justification, **Two-Way Nature Integration Mechanism**, **Signature Architectural Gesture**, **Landscape Backbone**, and cited Precedent Lens.

### Step 4C: Experience Architecture & Architectural Ensemble (`NEST_Experience_Design.md`)
- Enforce the **3 Remarkable Experience Pillars** (*Novel & Unprecedented*, *Visually Stunning Architectural Idea*, *Nature as the Hero*) per [`NEST_Experience_Design.md`](./NEST_Experience_Design.md).
- Structure every 50–70 feddan site as an **Architectural & Landscape Ensemble** of **Built Elements & Spatial Anchors** (unrestricted scale: major Anchor Landmarks + Experience-Curated Dining & Retail + Eco-Accommodation when warranted, each named by its site-true typology) rather than one monolithic building.
- Author a **flexible, project-specific Guest Journey** (`experience_arc.journey[]`: 3–7 bespoke moments named for that project, drawing from Arrival, Core Nature Encounter, Activities, Dining/Retail/Stay where relevant, and Atmosphere) and verify `0` encroachments into `Preserve` zones.

---

## Stage 5: Whole-Site Economic Base, Resilience & Pilot Validation
Validate the selected integrated **50–70 feddan Site (Landscape + Building)** program for real-world feasibility:

1. **Whole-Site Economic Value Study:**
   - Investigate potential users/visitors, market demand, competition/alternative destinations, customer willingness to pay, potential economic/funding partners, and market uncertainty across both architectural and landscape destinations.
   - Calculate/model **Total Site CapEx** explicitly split into **(a) Building CapEx** and **(b) Landscape & Site-Infrastructure CapEx**, plus **Expected Site-Wide Revenue** (capturing both architectural and landscape-driven revenue streams), **Profitability**, **Payback Period**, **Internal Rate of Return (IRR)**, and **Return on Investment (ROI)**—exploring unconventional and multiple revenue streams where nature preservation strengthens financial value.
   - Financial outputs are **mandatory**: when direct market data is unavailable for an unprecedented concept, actively search for comparable/proxy/regional data to estimate the numbers, show all supporting evidence and calculations, and explicitly label how much of each figure is directly observed vs. predicted or estimated (with bounded scenario ranges where appropriate).
2. **Phased & Pilot-Scale Strategy:**
   - Define a **Pilot-Scale Test (Phase 0)** to validate ecological/hydrological landscape performance and market demand before major capital commitment.
   - Define **Phased Investment** and **Flexible Future Uses** to accommodate land transformation, seasonal livelihoods, and multi-decade environmental/market shifts.
3. **Local Value Retention:**
   - Specify how economic benefits, infrastructure co-benefits, and economic symbiosis remain within nearby communities and reinvest a portion of returns into ongoing ecological and landscape health.

---

## Stage 6: NEST Final Presentation Bundle
Per [`WORKFLOW.md`](./WORKFLOW.md) (Section 4), a complete NEST run outputs a clean **Human-Facing Presentation Bundle** at the run root (`nest_dashboard.html`, `NEST_Executive_Report.md`, and `renders/site_1.jpg`–`site_5.jpg`), with Stage A GIS artifacts archived inside `intermediates/`:

1. **Self-Contained Text + Satellite Render Pack & ChatGPT Prompt Handoff (`renders/render_pack/` — Mandatory Default, Zero Auto `image-generator` Calls):**
   - Run [`GENERAL_KNOWLEDGE/architectural_render_skill/build_render_pack.py`](./architectural_render_skill/build_render_pack.py) to produce `site_<N>/satellite_lock.png` (Esri World Imagery crop), `site_<N>/prompt.md` (aerial + hero prompts with mandatory GIS Site Reality Lock and anti-repetition guardrails), `render_jobs.json`, **`CHATGPT_RENDER_PROMPT.md`** (single-shot batch prompt for ChatGPT Image Generation), `AGENT_INSTRUCTIONS.md`, and `render_pack.zip`. Do **not** auto-call `image-generator` (only if explicitly requested). Always finish the run by **prompting the user directly in chat** with the upload checklist (`site_1/satellite_lock.png`..`site_<K>/satellite_lock.png`) and the full single-shot ChatGPT prompt in one copy-paste fenced code block; once ChatGPT renders are saved to `renders/site_<N>.jpg` and `renders/site_<N>_hero.jpg`, rebuild the dashboard to display them.
2. **Interactive 2-Tab Dashboard (`nest_dashboard.html`)** — *Must strictly conform to [`project_brief_template.md`](./project_brief_template.md) and default to the **NEST 2.2 UI Design System** ([`UI Handover/NEST_UI_DESIGN_GUIDE.md`](../UI%20Handover/NEST_UI_DESIGN_GUIDE.md): warm off-white `#F5F5F5`, soft rose `#FBEFED`, coral `#FF614C` raised primary buttons, `Funnel Display` font, and official NEST + DeLab logos)*:
   - **Tab 1 (Default) — `Project Proposals (5 Cards)`:** Displays the best 5 Project Cards (omitting `hidden_score`) with a `#1`–`#5` Project Jump Bar and global **`Summary View | Detailed Briefs`** toggle, each featuring its whole-site editorial aerial render, an embedded mini interactive satellite map with a **Tri-Layer Hierarchy** (outer dashed translucent **50–70 Feddan Site Boundary** + color-coded validated **Landscape Zone Polygons `L-01..L-0N`** with hover tooltips + inner solid **Concept-Matched Architectural Massing Polygons** scaled to real `m²` + **3–5 numbered GIS feature pointer pins** with dashed leader lines synced to a clickable **Site Evidence Highlights** strip below the map, zoom controls, legend, and `3-Engine Map →` button), a scannable **Site & Architectural Thesis + Signature Gesture** block (`thesis_summary`: 1-sentence hook + `Why Here` / `Key Program` / `Architectural Gesture` bullets, expandable `thesis_detailed` narrative, `Tier 1`/`Tier 2`, Tectonic Idiom, Precedent Lens — *omit competition scores from dashboard*), a **Landscape Intelligence & Zoning Schedule (`L-01..L-0N`)** block (Landscape Backbone, Architecture–Landscape Interface, reconciled `m² / ha / feddans / %` table, and explicit **Landscape Trade-Offs & Water/Resource Risk** callout), a **How the 3-Engine Heatmaps & Proposals Derived This Result (`engine_trace`)** box, a dedicated **`Two-Way Nature Integration`** box (`Nature → Building` & `Building → Nature`), activities, a spaces & `m²` table, advisory flags, headline site-wide financial KPIs (**Building CapEx + Landscape/Site-Infra CapEx**, Revenue, ROI, IRR, Payback), a compact **Economic Case & Data Sources** block (Revenue Mix bar/pills, cited Target Users & Demand Highlights, Target Funding Partners pills, and inline `Observed` vs. `Benchmark` source tags), and an expandable `Hypotheses, Catalytic Phase 0 Pilot & Full Data Provenance` accordion.
   - **Tab 2 — `3-Engine Analysis Maps`:** Synchronized 3-engine spatial heatmaps (**Crystals**, **Cells**, **Corals**) for the **6 Nature-First Spatial Forces** + `Multi-Force Synergy (2+ / 3+)` overlaid with the NEST Top-5 50–70 feddan site boundary polygons and an interactive **Cell-Click Inspection Drawer** (`Forces & GIS Drivers` + `Emergent Program & Concept`).
3. **Executive NEST Report (`NEST_Executive_Report.md`)** — *Must follow the Markdown brief structure in [`project_brief_template.md`](./project_brief_template.md)*:
   - Spotlights the **Top 5 NEST Project Proposals** with embedded whole-site renders, identifiable 50–70 feddan site boundaries, numbered Site Evidence Highlights (Map Pointers 1–5), merged **Site & Architectural Thesis + Gesture**, **Landscape Intelligence & Zoning Schedule (`L-01..L-0N`)**, **Two-Way Nature Integration** (`Nature → Building` & `Building → Nature`), activities, spaces & `m²`, 2–3 competing integrated Site + Building hypotheses per site (with `/100` rubric scoring + mandatory Landscape Trade-Offs & Water/Resource Risk callout), mandatory nature-safe alternatives when `Harmful to the Environment` is triggered, compact financial tables (**Building CapEx** vs. **Landscape & Site-Infra CapEx**) + **Economic Case & Data Sources** (aligned with Egypt Vision 2030 / TSFE / PPP benchmarks), and mandatory Data Provenance badges.
