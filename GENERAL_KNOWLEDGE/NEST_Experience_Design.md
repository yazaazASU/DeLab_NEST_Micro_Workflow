# NEST Experience Design — Crafting Remarkable, Nature-Led Project Journeys

> **Governing Role:** Mandatory Stage B specification for **NEST** ([`WORKFLOW.md`](./WORKFLOW.md), [`nest_workflow.md`](./nest_workflow.md)).  
> **Core Premise:** On a **50–70 feddan (`21.0–29.4 ha`)** site, we are **not** designing a single isolated building—we are designing a **complete project** whose **#1 priority outcome is a remarkable, unforgettable user experience** where **nature is the hero** and architecture is the lens that celebrates it.

---

## 1. What Makes an Experience "Remarkable" (3 Mandatory Pillars)

Every NEST proposal must pass all **3 Pillars** before financial or spatial detailing:

1. **Novel & Unprecedented:**
   - The core experience must feel **genuinely new**—never a generic "eco-resort," "strip mall," "standard museum," or a single-word activity like *"bird watching"* or *"hiking."*
   - Ask: *"What happens here that a visitor cannot experience anywhere else in Egypt or the region?"*
2. **A Visually Stunning Architectural Idea:**
   - The architecture must embody a **bold, unforgettable spatial and tectonic idea**—not generic boxes or decorative facades.
   - How light enters, how roofs span or frame the sky, how walkways skim over water or carve through limestone, and how materials weather with the site must all serve the core experience.
3. **Nature as the Hero:**
   - Nature is **not** a backdrop or landscaping garnish—it is the **main event** the entire project is built to celebrate, reveal, and regenerate.
   - Users come to encounter a living natural phenomenon (lagoon tides, migratory flyways, desert starlight, coastal wind, salt-marsh filtration, wadi flash-floods), and every building exists to heighten that encounter while giving back to the ecosystem.

---

## 2. Architectural & Landscape Ensemble (Not One Building)

A 50–70 feddan project is a **choreographed Architectural & Landscape Ensemble** made up of **Built Elements & Spatial Anchors** across the site's landscape zones—never one monolithic block, and never limited to small park kiosks. Scale and typology are **unrestricted**: a site can combine major anchor architecture (`15,000–50,000+ m²` carved landforms, inhabited bridges, civic forums, research complexes) with specialized supporting built elements, naming every structure by its **actual, site-true architectural typology**:

1. **Anchor Landmarks & Hero Built Elements (Core):**
   - The signature architectural landmarks where the primary nature encounter happens—named by their true typology (e.g., submerged lagoon observatory, wind-tuned acoustic amphitheater, cliff-carved museum, tidal research complex, celestial desert court).
2. **Experience-Curated Dining & Retail (Supporting Uses):**
   - Food, beverage, and retail are **essential** to a full-day or multi-day experience, **but must be curated around the core story**—never generic fast-food courts or strip-mall shops.
   - Examples: salt-marsh tasting kitchens, shaded market arcades, fisherman/artisan cooperatives, field-gear & herbarium outposts, sunset dining halls overlooking the hero landscape.
3. **Eco-Accommodation & Overnight Stays (When Warranted):**
   - Low-impact overnight structures (reed-woven marsh lodges, earth-sheltered desert suites, cliffside retreats) that let guests experience **dawn, dusk, and night** on site—turning a 2-hour visit into a transformative 24-hour stay.

---

## 3. Flexible Project-Specific Guest Journey (`journey[]`, 3–7 Bespoke Moments)

Every project is different—a nocturnal desert stargazing sanctuary, a coastal salt-harvesting festival, and a wetland research promenade should **never** be forced into the same rigid 6 boxes. Instead, every NEST proposal authors its own **`journey[]` (3–7 bespoke moments)** named specifically for that project, drawing from these **creative ingredients** as relevant:
- **Arrival & Threshold**, **Core Nature Encounter**, **Activities & Discovery**, **Dining, Retail & Stay (where relevant)**, and **Atmosphere & Architectural Identity**.

### Reference Creative Ingredients (Not Rigid Boxes)

Every NEST proposal **must** author a complete, vivid **6-Beat User Journey** from first arrival to departure:

| Beat | Stage of Visit | What Must Be Defined |
| :--- | :--- | :--- |
| **1. Arrival & Threshold** | First 10 minutes | How guests arrive (car, shuttle, boat, trail), the sensory transition from highway/city into nature, and the first architectural threshold. |
| **2. Core Nature Encounter** | The Hero Moment | The signature, novel encounter with the site's natural hero—what the user sees, touches, hears, and learns, and the stunning architectural space that frames it. |
| **3. Secondary Activities & Trails** | 1–4 hours on site | Built elements, workshops, observation decks, water/land loops, and interactive moments across the 50–70 feddan landscape. |
| **4. Dining & Retail** | Eat, Drink, Shop | Where guests eat, drink, and browse—curated local cuisine, artisan/nature retail, and shaded social courts tied directly to the site's ecology and culture. |
| **5. Stay & Overnight (If Applicable)** | Dusk to Dawn | Eco-accommodation typology, privacy/viewshed siting, and how nightfall transforms the site (dark-sky stargazing, nocturnal wildlife, lantern-lit paths). |
| **6. Atmosphere & Architectural Identity** | Sensory & Visual | The unmistakable mood—materials, daylight/shadow, breeze, acoustics, water reflections, and what the buildings actually look like in the landscape. |

---

## 4. Simple, Vivid Writing (Kid-Friendly Clarity Rule)

The way we describe every project must make it **immediately attractive and easy to picture by a 10-year-old**—no hard words, no academic jargon, and no municipal report language:

1. **Zero Hard Words:** Never use words like *insolation, littoral, tectonic, halophyte, perforated, subterranean, cantilevered, porosity, ephemeral, intermodal, agronomy, desalination*. Instead say *bright sun, sea edge, cool shade, salt plants, stone walls with holes, underground, hanging roof, breezeways, sea water turned into fresh water*.
2. **Short, Catchy Place Names (2–4 Words):** Name it like a real place people want to visit (*The Salt Mist Garden*, *The Sunny Market Roof*, *The Wind Shell House*), not a government tender.
3. **Present-Tense Movie Scene:** Write what a visitor sees, hears, feels, and eats (*"You walk through cool stone tunnels, feel sea mist on your face, and eat grilled fish under reed roofs at sunset"*).
4. **Short `Nature Hero` Tag (3–5 Words):** e.g. `Sea Breeze & Salt Marshes` or `Desert Stars & Red Cliffs`—never a long GIS sentence.

---

## 5. Text-First + Satellite-Lock Architectural Visualization

NEST does **not** require 3D Rhino massing or clay-lock renders. Instead:
1. Stage B defines the **Architectural & Landscape Ensemble** (Built Elements & Spatial Anchors), **6-Beat User Journey**, **Atmosphere**, and **Visual Architectural Idea** in rich, concrete, de-metaphorized language.
2. `build_render_pack.py` pairs **`site_<N>_satellite_lock.png`** (real Esri World Imagery crop) with **`site_<N>_prompt.md`** (the experience-driven architectural brief) to produce editorial `16:9` aerial renders directly from text + satellite ground truth.

---

## 5. Tectonic & Atmospheric Ambition (Light-Touch Render Direction)

- **Bold Sectional Gestures:** Favour cantilevers, sculpted shells, stepped green-roof strata, or glowing twilight enclosures over flat-roofed generic compounds.
- **Unified Tectonic World:** Every pavilion in a constellation (hero space, dining, retail, stay) must share one coherent architectural language.
- **Experience-Matched Lighting & Framing:** Let `experience_arc.atmosphere` drive the time of day (e.g., twilight lantern glow, misty dawn, or crisp sun) and use low-oblique `~25–35°` threshold aerials so human scale and spatial drama are felt.
