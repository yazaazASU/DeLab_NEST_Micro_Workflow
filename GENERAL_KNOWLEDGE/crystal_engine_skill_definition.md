# Crystal Engine Skill Definition

> **Overarching Theme ([`engine_charter.md`](./engine_charter.md)):** **Crystals Engine — Development** (*Finding points of interest to build around, in, or at*).  
> **Note:** The complete definition of a skill (including universal envelope `skill_name.json`) is in [`skill_defintion.md`](./skill_defintion.md).
>
> **Engine Nature (`Crystals Engine`):** Generates structured analytical and geometric architectural skills anchored to high-gravity **points of interest (POIs)** — natural, cultural, infrastructural, or civic — governing *how to build around, in, or at* those anchors (standoff/viewshed rings, orientation datums, massing envelopes, programmatic stacking, and staging).

## Scale
*How complex is the skill?*
- **Expected Data Type:** `enum (text)` — `Atom` | `Molecule` | `Crystal` | `Cluster`

- **Atom**: Skill acts on raw data.
- **Molecule**: Skill acts on analyzed data.
- **Crystal**: Fully developed skill.
- **Cluster**: Multiple skills acting as one unit.

## Facets
*What can it do? (Multiple capabilities, each optionally paired with the tool/platform needed to perform it)*
- **Expected Data Type:** `array of objects`

- **capability** (`text`): A specific capability the skill can perform.
- **tool** (`text` or `array of text`, optional): Target platform or tool needed to perform that capability (e.g., `Revit`, `Grasshopper`, `QGIS`, `Python`).

## Axes
*Where and when does it operate?*
- **Expected Data Type:** `object`

- **Space** (`text`): Spatial scope where the skill applies (e.g., parcel, district, building zone).
- **Time** (`text`): Project or temporal phase when it applies (e.g., concept, schematic, seasonal).
- **Depth** (`enum (text)` — `Shallow` | `Medium` | `Deep`): Analytical granularity of the skill.

## Density
*How reliable is its knowledge?*
- **Expected Data Type:** `enum (text)` — `Verified` | `Inferred`

- **Verified**: We have the data.
- **Inferred**: We estimated the data.

## Growth
*How does the skill develop?*
- **Expected Data Type:** `enum (text)` — `Iterative` | `Linear` | `Branching`

- **Iterative**: Improves through repeated cycles.
- **Linear**: Steady step-by-step accumulation.
- **Branching**: Splits into specialized sub-skills.

## Field
*What category does the skill belong to?*
- **Expected Data Type:** `enum (text)` — `Environmental` | `Material` | `Machine` | `Creative` | `Urban` | `Human` | `Program` | `Engineering`

- **Environmental**
- **Material**
- **Machine**
- **Creative**
- **Urban**
- **Human**
- **Program**
- **Engineering**

## State
*What is its current condition?*
- **Expected Data Type:** `enum (text)` — `Growing` | `Stable` | `Melting`

- **Growing**: Skill is improving.
- **Stable**: Skill is not developing.
- **Melting**: Skill is not needed anymore.

## Memory
*What has it learned and retained?*
- **Expected Data Type:** `object` (containing arrays of `text`)

- **Past experiences** (`array of text`)
- **Usage history** (`array of text`)
- **Feedback** (`array of text`)
- **Lessons learned** (`array of text`)

## Bonds
*Which other fields impact and/or work together with this skill?*
- **Expected Data Type:** `array of enum (text)` (from **Field**: `Environmental` | `Material` | `Machine` | `Creative` | `Urban` | `Human` | `Program` | `Engineering`)

- Other **Fields** that impact and/or work together with this skill.

## Resilience
*How does the skill respond to new data / change?*
- **Expected Data Type:** `enum (text)` — `Resistance` | `Adapt`

- **Resistance**: Hold existing knowledge/rules until user approval.
- **Adapt**: Auto-adapt to new data and update knowledge/insights.

## Output Format Example (`skill_name.json`)
```json
{
  "definition": "Enforce standoff viewshed, skyline datum, and solar orientation limits when developing around a high-gravity heritage/waterfront point of interest.",
  "parent_engine": "Crystals Engine",
  "trigger": [
    "new massing placement around heritage or waterfront POI",
    "building height, setback, or primary facade orientation edit"
  ],
  "action": {
    "type": "Guidance",
    "message": "Hold massing within the 220–400 m build-around standoff ring of the heritage POI, cap ridge elevation below the primary sightline datum, and align glazed facades within 15° of north-south before locking the envelope."
  },
  "attributes": {
    "scale": "Crystal",
    "facets": [
      {
        "capability": "Evaluate build-around POI viewshed standoff and solar orientation for new massing",
        "tool": ["QGIS", "Grasshopper", "Revit"]
      }
    ],
    "axes": {
      "space": "POI development ring & parcel envelope",
      "time": "concept",
      "depth": "Medium"
    },
    "density": "Verified",
    "growth": "Iterative",
    "field": "Environmental",
    "state": "Growing",
    "memory": {
      "past_experiences": [],
      "usage_history": [],
      "feedback": [],
      "lessons_learned": []
    },
    "bonds": ["Urban", "Engineering"],
    "resilience": "Adapt"
  }
}
```
