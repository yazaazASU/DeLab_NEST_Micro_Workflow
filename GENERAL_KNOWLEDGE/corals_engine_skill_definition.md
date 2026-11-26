# Corals Engine Skill Definition

> **Overarching Theme ([`engine_charter.md`](./engine_charter.md)):** **Corals Engine — Coordination** (*Finding elements in site, nature, or context to use better together or introduce a beneficial relationship*).  
> **Note:** The complete definition of a skill (including output format `skill_name.json`) is in [`skill_defintion.md`](./skill_defintion.md). Supporting design notes, source traceability, and open questions are preserved in [`Coral_engine_design_notes.md`](./Coral_engine_design_notes.md).

**Engine Nature (`Corals Engine`):** Generates relational, symbiosis-driven architectural skills that **coordinate multiple elements in site, nature, or context** so they work better together or form a new beneficial relationship. Unlike **Crystals Engine** skills (structured analytical rules for building around/in/at POIs) and **Cells Engine** skills (adapting a single element into something new/better), **Corals Engine** skills focus strictly on **multi-element coordination & mutualistic loops** — branching coordination possibilities inside a single skill, linking site/context/building elements into shared intentions, and retaining alternative pairings in an archive.

---

## Resources
*Which distinct elements in site, nature, or context are being coordinated together?*
- **Expected Data Type:** `array of objects` (typically **2 or more** elements to pair or link)

Resources are distinct site, natural, civic, or contextual elements that perform better when coordinated into a beneficial relationship rather than treated in isolation.

- **resource** (`text`): The site, natural, or contextual element.
- **potential** (`text`): What this element contributes to a shared, mutually beneficial relationship.
- **constraints** (`array of text`, optional): Known site limits, conflicts, or execution constraints to respect when coordinating.

## Branches
*What directions live inside this skill, how specific have they matured, and which tools support them?*
- **Expected Data Type:** `array of objects`

Branches remain **parts of the original skill** rather than splitting into separate skills. A branch matures from generic intention to specific application (*what*, *where*, *tools*) and can branch again.

- **direction** (`text`): The design possibility being explored.
- **maturity** (`enum (text)` — `Exploratory` | `Maturing` | `Specialized`):
  - **Exploratory**: Open creative possibility.
  - **Maturing**: Defining *what* the experience could be, *where* it could occur, and *which tools* can study it.
  - **Specialized**: Concrete, site-grounded application ready for design use or further branching.
- **application** (`text` or `null`, optional): Specific design application and site location once maturing.
- **tool** (`text` or `array of text`, optional): Candidate or used platform/tool (e.g., `Ladybug`, `Autodesk Forma`, `Grasshopper`, `QGIS`, `Revit`). Naming a tool does not imply it has been run.

## Symbiosis
*Which other skills and site resources connect with this skill to unlock emergent ideas?*
- **Expected Data Type:** `array of objects`

- **with** (`array of text`): Connected skills and/or site resources (e.g., `Site History Narrative`, `Circulation Experience`, `warm microclimate`).
- **shared_intention** (`text`): The emergent design intention or hidden relationship they unlock together.

## Evaluation
*How promising and evidence-backed is this skill's knowledge?*
- **Expected Data Type:** `object`

Keeps creative hypotheses clearly separate from evidence-backed proposals, using qualitative criteria rather than fixed numeric weights.

- **status** (`enum (text)` — `Hypothesized` | `Under Study` | `Evaluated` | `Validated`):
  - **Hypothesized**: Creative possibility not yet tested.
  - **Under Study**: Required studies and candidate tools identified, not yet completed.
  - **Evaluated**: Assessed with available site data or tool runs, with limits noted.
  - **Validated**: Supported by recorded evidence and proven outcomes.
- **criteria** (`object`):
  - **creativity** (`text` or `null`): Creative contribution of the skill's direction(s).
  - **resource_connection** (`text` or `null`): How effectively it uses, reuses, and connects site resources.
  - **feasibility** (`text` or `null`): Known findings, limits, or open questions.
- **studies_needed** (`array of text`, optional): Evidence or investigations still required.

## State
*What is the skill's current condition?*
- **Expected Data Type:** `enum (text)` — `Branching` | `Maturing` | `Active` | `Dormant` | `Reinterpreting`

- **Branching**: Opening new directions and resource hypotheses.
- **Maturing**: Specifying applications, site locations, and tool studies.
- **Active**: Recommended or validated skill actively informing design.
- **Dormant**: Retained in `Archive` (including paused or unsuccessful explorations), ready to revive when new connections appear.
- **Reinterpreting**: Carrying qualities of an unsuitable resource into a new design theory elsewhere.

## Adaptation
*How does the skill respond when site conditions change, a resource presents a problem, or direct use fails?*
- **Expected Data Type:** `enum (text)` — `Redirect` | `Regenerate` | `Reinterpret` | `Hold`

- **Redirect**: Shift toward a new opportunity revealed by a site condition or new evidence.
- **Regenerate**: Generate fresh ideas and supporting resource links when a resource presents a problem.
- **Reinterpret**: Preserve sensory, spatial, or narrative qualities as a design theory elsewhere when direct physical use is unsuitable.
- **Hold**: Keep existing knowledge unchanged until missing evidence or user approval is resolved.

## Archive
*What has the skill retained for future revival versus actually validated?*
- **Expected Data Type:** `object`

Retaining an exploration does not validate it; both are kept distinct so earlier ideas can return when new connections appear.

- **retained_explorations** (`array of text`): Past ideas, branches, and unsuccessful attempts kept with their reasons for future revival.
- **validated_knowledge** (`array of text`): Proven insights and reusable composite functions backed by evidence.
- **lessons_learned** (`array of text`): Synthesized insights carried across projects.

---

## Output Format Example (`skill_name.json`)
```json
{
  "definition": "Coordinate the adjacent village settlement edge, the shoreline breeze corridor, and the local craft/fishing waterfront into a mutually beneficial shaded civic-ecological spine.",
  "parent_engine": "Corals Engine",
  "trigger": [
    "site circulation or waterfront promenade layout between settlement and water edge",
    "program placement for public market, craft hub, or shaded civic spine"
  ],
  "action": {
    "type": "Prompt",
    "message": "Rather than treating the village edge, waterfront dock, and wind corridor separately, test 3 coordination branches: a continuous shaded market-to-pier axis capturing river breeze, a shared solar cold-chain + craft pavilion at the seam, or a riparian bioswale filtering village runoff before it reaches the water."
  },
  "attributes": {
    "resources": [
      {
        "resource": "adjacent village settlement edge (240 m)",
        "potential": "Daily pedestrian footfall, local craft workforce, and community stewardship",
        "constraints": ["Avoid severing informal fishing access routes"]
      },
      {
        "resource": "prevailing north-west waterfront breeze & shoreline",
        "potential": "Natural evaporative cooling corridor and waterborne mobility link",
        "constraints": ["Seasonal water-level fluctuation requires stepped/elevated edges"]
      },
      {
        "resource": "high-irradiance solar canopy surface",
        "potential": "Shared microgrid power for village cold-chain storage and evening lighting",
        "constraints": ["Must integrate glare control along pedestrian sightlines"]
      }
    ],
    "branches": [
      {
        "direction": "Align shaded craft stalls along the prevailing breeze seam linking village to pier",
        "maturity": "Maturing",
        "application": "Continuous permeable arcade bridging settlement street grid to floating landing",
        "tool": ["Ladybug", "Autodesk Forma", "QGIS"]
      },
      {
        "direction": "Pair rooftop solar microgrid with shared fishing cold-chain and community clinic backup",
        "maturity": "Exploratory",
        "application": null,
        "tool": ["Grasshopper", "Ladybug"]
      },
      {
        "direction": "Coordinate greywater/stormwater runoff from the civic plaza into a shoreline reed-bed filter",
        "maturity": "Maturing",
        "application": "Terraced bioswale edge along the southern promenade border",
        "tool": ["QGIS", "Grasshopper"]
      }
    ],
    "symbiosis": [
      {
        "with": ["adjacent village settlement edge", "prevailing waterfront breeze"],
        "shared_intention": "Channel cool waterfront air deep into the community market while driving daily footfall to the shoreline"
      },
      {
        "with": ["solar canopy microgrid", "local fishing & craft livelihoods"],
        "shared_intention": "Turn shade infrastructure into shared cold-chain refrigeration and evening civic illumination"
      }
    ],
    "evaluation": {
      "status": "Under Study",
      "criteria": {
        "creativity": "Turns three disconnected local conditions into a single self-reinforcing civic-ecological seam",
        "resource_connection": "Links human livelihoods, wind cooling, solar energy, and water quality in a two-way loop",
        "feasibility": "Shaded arcade and bioswale are low-CapEx; shared microgrid governance requires municipal/cooperative sign-off"
      },
      "studies_needed": [
        "Pedestrian wind-comfort & shade simulation along the village-to-pier axis",
        "Local cooperative load profile for shared cold-chain refrigeration"
      ]
    },
    "state": "Maturing",
    "adaptation": "Redirect",
    "archive": {
      "retained_explorations": [
        "Enclosed air-conditioned tourist bazaar at the pier — paused because it severed village permeability and rejected passive river cooling; retained for retail-area benchmarking."
      ],
      "validated_knowledge": [],
      "lessons_learned": [
        "Pair community economic flows with natural microclimate corridors so ecological performance and local livelihoods reinforce each other."
      ]
    }
  }
}
```
