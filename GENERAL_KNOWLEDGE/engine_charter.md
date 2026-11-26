# NEST 3-Engine Identity & Thinking Charter

> **Canonical Source of Truth:** This charter defines the overarching cognitive theme of each of the three NEST engines (**Crystals**, **Corals**, **Cells**). These definitions are **scale-agnostic and universal** — they govern how each engine thinks about a piece of land (Stage A), a site & building concept (Stage B), a building's design skills (Stage C), or **any other architectural, environmental, or spatial object** it is asked to evaluate or generate for.

---

## 1. The Three Overarching Themes

| Engine | Overarching Theme | Core Definition | Guiding Question |
| :--- | :--- | :--- | :--- |
| **Crystals Engine** | **Development** | **Finding points of interest to build around, in, or at.** | *"Where are the high-gravity points of interest (natural, cultural, infrastructural, or civic), and how should we build around, in, or at them?"* |
| **Corals Engine** | **Coordination** | **Finding elements in site, nature, or context to use better together or introduce a beneficial relationship.** | *"Which elements in the site, nature, or surrounding context can work better together, or what beneficial relationship can be introduced between them?"* |
| **Cells Engine** | **Adaptation** | **Finding elements in site, nature, or context to unlock their full potential by adapting them into something new or better.** | *"Which natural or contextual element holds untapped potential, and how can it be adapted or transformed into something new and better?"* |

---

## 2. How Each Engine Thinks Across Scales ("Land, Building, Skills, Whatever")

Each engine applies the exact same mental model no matter what object it is given:

### A. Crystals Engine — **Development** *(Build Around, In, or At Points of Interest)*
- **Mental Model:** Anchoring, framing, staging, and crystallizing built form around high-gravity points of interest (POIs) — whether natural (waterfront, ridge, oasis), cultural (heritage site, landmark, viewpoint), infrastructural (port, transit gateway), or civic (community core, service gap).
- **On a Piece of Land (Stage A):** Identifies the strongest POI anchors and scores buildable zones **around** (standoff viewshed/framing ring via `ring_decay`), **at** (direct gateway/edge proximity via `decay`), or **in** (infill/focal cluster via `kde`), while keeping existing road footprints and dense built cores masked for new footprints.
- **On a Site & Building Concept (Stage B):** Shapes landmark massing, skyline datums, viewing axes, programmatic anchors, and phasing that turn a point of interest into a legible, economically viable destination.
- **On Building Skills (Stage C):** Generates structured analytical & geometric rules (`Scale`, `Facets`, `Axes`, `Density`, `Growth`, `Field`, `State`, `Memory`, `Bonds`, `Resilience`) governing how to develop around, in, or at a POI (standoffs, solar/view axes, envelope thresholds, GFA stacking, staging).
- **On Any Other Object ("Whatever"):** Finds the focal anchor(s) of the problem (a room's view, a facade's sun-face, a district's plaza) and establishes clear structural/geometric rules to build around, in, or at them.

### B. Corals Engine — **Coordination** *(Use Elements Better Together / Introduce Beneficial Relationships)*
- **Mental Model:** Relational weaving, symbiosis, pairing, and network stitching. Corals rarely looks at an element in isolation — it always asks what happens when **Element A + Element B (+ Element C)** are coordinated into a mutually beneficial relationship.
- **On a Piece of Land (Stage A):** Evaluates the entire plot (land, shoreline, urban-edge, and water) using `corridor_bridge` (`Group A AND Group B`) to locate seams, midpoints, and exchange zones where disconnected site, natural, civic, or infrastructural elements can be coordinated together.
- **On a Site & Building Concept (Stage B):** Designs shared connectors, symbiotic loops, multi-modal interfaces, and mutualistic exchanges (e.g., settlement ↔ waterfront, solar microgrid ↔ cold-chain port, heritage ↔ local craft economy, `Nature ↔ Building` flows).
- **On Building Skills (Stage C):** Generates relational, symbiosis-driven skills (`Resources`, `Symbiosis`, `Branches`, `Evaluation`, `State`, `Adaptation`, `Archive`) that coordinate multiple site/context/building elements into beneficial relationships and preserve alternative pairings.
- **On Any Other Object ("Whatever"):** Finds separate components, actors, flows, or systems (thermal exhaust + greenhouse, circulation + exhibition narrative, shade + gathering) and introduces a beneficial relationship so they perform better together than apart.

### C. Cells Engine — **Adaptation** *(Unlock an Element's Full Potential by Adapting It Into Something New/Better)*
- **Mental Model:** Element-level transformation, mutation, reinterpretation, and metabolic evolution. Cells targets **both natural AND contextual/man-made elements** (a landform, cave, harsh solar/heat microclimate, seasonal wadi, quarry, ruin, saline marsh, underused shoreline or edge — while avoiding dense active urban cores) and adapts them into something new and better.
- **On a Piece of Land (Stage A):** Identifies high-intensity, extreme, or underutilized site/nature/context elements and dynamic transition zones (`ecotone_gradient` + `kde` + extreme-condition `decay`) where latent potential can be unlocked through adaptation.
- **On a Site & Building Concept (Stage B):** Turns perceived constraints, environmental extremes, or underused contextual elements into the generative engine of the architecture (e.g., adapting extreme solar/evaporation into passive cooling & water harvesting; adapting a quarry, cave, or ruin into a new cultural/ecological organism; reversible/phased/evolving structures).
- **On Building Skills (Stage C):** Generates element-transformative, evidence-tracked adaptive skills (`Host Element`, `Latent Potential`, `Adaptation Pathway`, `Gene Refs / Skill Genome`, `Novelty & Confidence`, `Reinterpretation Fallback`, `State`, `Evolution Memory`) grounded in the Cellular Engine behavioral specification.
- **On Any Other Object ("Whatever"):** Inspects an existing condition, constraint, or underperforming element and asks: *how can we adapt, mutate, or reinterpret this exact element to unlock its highest potential?*

---

## 3. Clean Boundary Test (Same Site Element, Three Distinct Lenses)

Suppose all three engines inspect the **same site feature** — e.g., an **arid limestone ridge overlooking a seasonal wadi near a historic village**:

- **Crystals (Development):** *"This ridge overlook is a high-gravity Point of Interest. Build a landmark terrace **at** the ridge crest and anchor visitor facilities **around** its viewing axis with strict skyline/solar rules."*
- **Corals (Coordination):** *"The village, the wadi's seasonal water, and the ridge's breeze are currently disconnected. Introduce a **beneficial relationship** connecting village water-harvesting, shaded craft circulation, and wadi ecology so all three strengthen each other."*
- **Cells (Adaptation):** *"The wadi's flash-runoff and the ridge's extreme thermal mass are untapped elements. **Adapt** the limestone cavity and seasonal runoff channel into a living passive-cooled subterranean thermal chamber and seed-bank sanctuary."*

---

## 4. Downstream Reference Map

All NEST pipeline specifications, configs, and scripts derive their engine identity from this charter:
- **System Overview & Workflows:** [`engines_overview.md`](./engines_overview.md), [`WORKFLOW.md`](./WORKFLOW.md), [`engines_workflow.md`](./engines_workflow.md), [`nest_workflow.md`](./nest_workflow.md)
- **Stage A Spatial Configs & Runner:** [`crystals_nature_forces.md`](./crystals_nature_forces.md), [`corals_nature_forces.md`](./corals_nature_forces.md), [`cells_nature_forces.md`](./cells_nature_forces.md), [`run_3_engines.py`](../run_3_engines.py)
- **Stage C Skill Definitions & Workflow:** [`skill_defintion.md`](./skill_defintion.md), [`crystal_engine_skill_definition.md`](./crystal_engine_skill_definition.md), [`corals_engine_skill_definition.md`](./corals_engine_skill_definition.md), [`cells_engine_skill_definition.md`](./cells_engine_skill_definition.md), [`skill_generation_workflow.md`](./skill_generation_workflow.md)
