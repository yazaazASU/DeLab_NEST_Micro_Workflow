# NEST Space & Program Typology Atlas

> **Purpose:** Expands NEST Stage B & Stage C beyond generic program labels (`Gallery`, `Lab`, `Café`, `MEP`) so every proposed space is **derived from real site conditions**, **anchored to specific human users**, **explained in plain, vivid language**, and **combined into unexpected, high-synergy civic landmarks** rather than a fixed catalog.  
> **Companion Specs:** [`NEST_Architectural_Direction.md`](./NEST_Architectural_Direction.md) · [`NEST_Form_Material_Site_Atlas.md`](./NEST_Form_Material_Site_Atlas.md) · [`NEST_Concept_Statement_Direction.md`](./NEST_Concept_Statement_Direction.md) · [`project_brief_template.md`](./project_brief_template.md)

---

## 1. Site-to-Space Derivation Matrix *(How Site Conditions Generate Programs)*

Every space in `spaces[]` and `massing_rationale.volumes[].interior_zones[]` must trace back to an **observed site trigger** in `stage_a_summary.json` or `observed_plot_telemetry`. Never drop a generic museum, resort, or office block onto a plot without a physical trigger.

| Observed Site Condition / Force | Spatial Trigger | Derived Space Types (Non-Generic) | Concrete Examples |
| :--- | :--- | :--- | :--- |
| **Coastline / Salt-Marsh / Lagoon Edge** | Brackish water, migratory flyways, sea breeze, tidal fluctuation | **Brackish Ecology Lab**, **Tidal Aquaculture Tanks**, **Salt-Marsh Viewing Blind**, **Desalination & Mist Court**, **Coastal Boat/Kayak Slip** | Public viewing corridor looking into native halophyte propagation tanks; elevated timber bird blind at marsh rim |
| **Desert Wadi / Flash-Flood Channel** | Seasonal runoff, incised canyon microclimate, cool night air pooling | **Flood-Harvesting Cistern Hall**, **Arid Seed & Soil Vault**, **Sunken Acoustic Amphitheater**, **Shaded Wadi Field Station** | Subterranean stone cisterns doubling as thermal cooling mass beneath a public reading courtyard |
| **Arterial Highway / Logistics Corridor** | High freight/passenger throughput, regional market access, noise edge | **Solar Cold-Chain Packing Hub**, **Regional Growers' Auction Hall**, **EV Freight & Transit Concourse**, **Roadside Makers' Market** | Acoustic earth-berm shielding a quiet craft & produce market from highway noise while loading directly at the rear |
| **Dense Settlement / Civic Service Deficit** | Underserved youth/family population, heat-island stress, lack of shaded gathering | **24/7 Shaded Study & Makerspace**, **Community Cooling Commons**, **Youth Sports & Martial-Arts Courtyard**, **Neighborhood Clinic & Pharmacy Pod** | Night-lit public courtyard with free Wi-Fi, shaded play, and vocational fabrication labs open until midnight |
| **Heritage / Archaeological / Vernacular Node** | Cultural memory, craft lineage, tourism footfall, fragile fabric | **Living Craft & Loom Workshop**, **Oral-History & Archive Pavilion**, **Conservation & Material-Testing Studio**, **Artisan Courtyard Café** | Visitors watch master potters/weavers work beside climate-controlled textile & stone conservation rooms |
| **High Solar / Wind Intensity Zone** | `> 2,100 kWh/m²` solar or steady prevailing wind corridor | **Solar-Thermal Drying & Food Lab**, **Wind-Scooped Passive Cooling Hall**, **Agri-Voltaic Research Conservatory**, **Grid-Interactive Battery & Microgrid Hub** | Louvered canopy shading an indoor-outdoor botanical market while powering cold storage below |
| **Agricultural / Oasis / Date-Palm Belt** | Irrigation canals, biomass waste, seasonal harvest peaks | **Bio-Material & Palm-Fiber Workshop**, **Botanical Oil & Spice Extraction Lab**, **Farm-to-Table Culinary Training Kitchen**, **Compost & Greywater Wetland** | Turning palm fronds into acoustic ceiling panels on site while teaching local culinary hospitality |

---

## 2. Core & Hybrid Space Typologies *(Users, Rhythms, Specs & Explanations)*

Use this reference to populate `spaces[]` (using the rich object format) and `interior_zones[]`. Every space must specify **who uses it**, **when it is active**, **what physical conditions it needs**, and **what actually happens inside**.

| Space Family | Primary & Secondary Users | Active Rhythm | Spatial & Environmental Spec | Plain-Language Explanation Pattern |
| :--- | :--- | :--- | :--- | :--- |
| **1. Arrival & Orientation Commons** | First-time visitors, tour groups, local families, transit riders | `07:00–23:00` | `5.5–8.0 m` clear height; cross-ventilated shaded threshold; tactile site model; acoustic absorption (`RT60 ≤ 0.9 s`) | *"A shaded stone hall where visitors step out of the sun, orient themselves around a carved terrain table, and grab tea before entering the galleries or trails."* |
| **2. Living Ecology & Herbarium Gallery** | School groups, eco-tourists, botanists, weekend families | `08:00–21:00` | North/diffused clerestory daylight (`250–400 lux`); mist/evaporative cooling; durable stone floors for sandy shoes | *"Walk-through planted rooms showcasing native coastal and desert plants growing in real soil beds, paired with simple wall stories."* |
| **3. Applied Research & Seed/Soil Lab** | Marine/arid biologists, university fellows, visiting technicians *(plus public viewing corridor)* | `24/7` (labs) / `09:00–18:00` (viewing) | Vibration-isolated slab; controlled `18–22°C` core; glass viewing gallery so the public sees science without entering sterile zones | *"Climate-locked seed vaults and soil benches where researchers test salt-tolerant crops behind glass walls visible to passing students."* |
| **4. Vocational Maker & Bio-Craft Studio** | Local artisans, youth apprentices, industrial designers, micro-entrepreneurs | `08:00–22:00` | `4.5–6.0 m` bay with overhead power/dust extraction; wide roll-up doors to shaded work yard; washable concrete/stone floor | *"An open-bay workshop with looms, kilns, and CNC tables where local makers turn regional stone, clay, and palm fiber into architectural goods."* |
| **5. Community Library & Night Study Hall** | High-school/university students, remote workers, elders, neighborhood residents | `07:00–24:00` | Glare-free north light + warm `2700K` task lamps; quiet acoustic alcoves alongside collaborative tables; zero-ticket free entry | *"A cool, quiet reading and laptop hall open late into the evening, giving local students reliable Wi-Fi, daylight, and shaded garden terraces."* |
| **6. Acoustic Amphitheater & Forum** | Performers, festival crowds, community town-halls, school assemblies | `17:00–23:30` (events) / `24/7` (open seating) | Carved terrain bowl (`1:10` rake); wind-baffled backdrop wall; natural voice projection up to `400–800` seats without heavy PA | *"A sunken stone amphitheater carved into the slope where evening concerts, film screenings, and neighborhood gatherings happen under open sky."* |
| **7. Culinary Lab & Regional Food Court** | Local cooks, farmers, culinary trainees, travelers, families | `07:00–23:00` | Grease-trap/greywater separation; shaded outdoor dining pergola; visible prep counter; direct service yard from cold storage | *"A shared training kitchen and shaded courtyard dining hall serving dishes cooked from nearby farms, fisheries, and solar-dried harvests."* |
| **8. Cold-Chain & Market Logistics Hub** | Smallholder farmers, cooperative truckers, market vendors, inspectors | `04:00–16:00` | Heavy-duty dock apron (`≥ 18 m` turning); insulated solar-powered cold rooms (`2–8°C`); acoustic/visual buffer from public plazas | *"A solar-cooled packing and auction dock tucked behind an earth berm so local growers can chill and ship produce without post-harvest loss."* |
| **9. Micro-Climate Wellness & Bathhouse** | Residents, wellness travelers, athletes, seniors | `06:00–22:00` | Filtered zenithal oculus light; high-humidity lime/tadelakt plaster; thermal plunge pools fed by solar-heated water; acoustic stillness | *"Daylit stone bathing and recovery chambers using warm mineral water, steam, and shaded courtyard pools for quiet physical rest."* |
| **10. Elevated Trailhead & Bird/Sky Blind** | Hikers, birdwatchers, photographers, school nature clubs | `05:30–20:00` | Elevated timber/steel boardwalk (`≥ 1.2 m` above marsh/wadi bed); slatted viewing slits; zero artificial night spill-light | *"A narrow, quiet timber walkway lifted on slender posts above sensitive marsh grass, ending in a shaded viewing room for watching migratory birds."* |
| **11. Circular Water, Solar & MEP Spine** | Facility engineers, vocational energy trainees *(with educational meter wall)* | `24/7` | Sub-grade or berm-screened service spine; greywater reed-bed interface; acoustic enclosures (`≤ 50 dBA` at plaza edge) | *"Hidden cisterns, reed-bed water filters, and battery rooms that cool the building, recycle every drop of greywater, and display live energy savings."* |

---

## 3. Anti-Catalog Program Mixing Rules *(Avoiding Generic Templates)*

When assembling a project's `spaces[]` and `activities[]`:
1. **Pair One "Engine/Work" Space with One "Public/Wonder" Space:** Never build a pure research fortress or a pure tourist mall. Put a **public viewing corridor** beside the **Seed Bank**, a **tasting terrace** beside the **Solar Cold-Chain Hub**, or a **community night-study hall** beside the **Herbarium**.
2. **Design for Dual Time-Clocks (`Day + Night`):** Every Tier 1 or Precinct project must pair daytime uses (labs, markets, clinics, shade galleries) with evening/night uses (open-air forum, night library, lit waterfront dining, stargazing deck) so the site never becomes a dead zone after `17:00`.
3. **Name Spaces by What Happens Inside — Not Generic Labels:**
   - *Avoid:* `Exhibition Hall A`, `Commercial Zone`, `MEP Block`, `Multi-Purpose Room`.
   - *Use:* `Salt-Marsh Propagation & Viewing Hall`, `Growers' Solar Cold-Chain & Spice Market`, `Sunken Wadi Reading Court`, `Cistern Cooling & Reed-Bed Plant`.
4. **No Jargon in User-Facing Space Explanations:** Follow [`NEST_Concept_Statement_Direction.md`](./NEST_Concept_Statement_Direction.md) — explain spaces using concrete nouns and human actions (*"students study until midnight"*, *"fishermen unload morning catch into solar-chilled rooms"*) rather than *"synergistic multifunctional nexus"*.

---

## 4. Rich `spaces[]` & `interior_zones[]` Data Contract

In `stage_b_projects.json`, `spaces[]` supports **both** legacy 3-item tuples (`["Name", "9,200 m²", "08:00–21:00"]`) and the **preferred rich object format**:

```json
{
  "name": "Salt-Marsh Propagation & Viewing Hall",
  "area": "6,800 m²",
  "hours": "08:00–21:00",
  "users": "Botanists, school groups, weekend families",
  "site_trigger": "Adjacent brackish marsh edge & 85% native halophyte deficit",
  "explanation": "Walk-through planted glasshouse beds where visitors see salt-tolerant coastal crops tested beside a public viewing ramp."
}
```
