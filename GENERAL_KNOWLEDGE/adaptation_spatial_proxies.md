# Engine 2: Cells Engine (Adaptation to Natural Systems) — Spatial Proxies & Scoring Specification *(Legacy 6-Typology Archive)*

> **Deprecation & Active Config Notice:** Under the **NEST Nature-First Architecture**, `run_3_engines.py` now uses [`cells_nature_forces.md`](./cells_nature_forces.md) to score the **6 NEST Nature-First Spatial Forces** (`Hydrology & Waterfront`, `Solar & Climate Intensity`, `Biodiversity & Ecology`, `Heritage & Culture Gravity`, `Civic & Service Deficit`, `Corridor & Network Connectivity`). This file is retained as an archival reference only.

This specification drives **Engine 2 (Cells Engine — Adaptation to Natural Systems)** under **NEST's Nature-First Design Principles**. Rather than retrofitting dense urban buildings, Cells evaluates **natural, semi-natural, ecological-transition, and water zones** to identify where architectural interventions can **adapt to, coexist with, and evolve alongside dynamic natural systems** (extreme climates, microclimates, seasonal transformations, hydrological/sediment dynamics, ecological relationships, and environmental recovery).

---

## 1. Adaptation Mask (Natural Systems & Dynamic Landscapes)
- **Included:** Natural and semi-natural land, ecological corridors, desert/wadi/karst/mountain/coastal terrains, agricultural/oasis edges, and **water zones** (`Egypt — Water Areas`, `نهر النيل`, `Egypt — Waterways` — scorable with an explicit `water_zone_warning` flag).
- **Excluded (Masked = 0):** Existing dense urban fabric (`Egypt — Buildings`, dense urban `populated_places`), roads (`الطرق`, `heigit_EG_planet_roadsurface_lines`), and existing major infrastructure where intervention is not possible.

> **Migration Note:** The baseline typology proxy tables below are inherited from the legacy urban-adaptation dataset. As NEST's ecological, microclimate, hydrology, and seasonal-change GIS layers are ingested, replace urban-stock factors (`Egypt — Buildings`, urban study priorities) with natural-system adaptation proxies (microclimate differentials, seasonal water/wadi flow, biodiversity corridors, erosion/regeneration zones, and low-impact circular resource potential).

---

## 2. Typology Scoring Tables (Adaptation Lens)

### Typology: Residential
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| adp_res_housing_pri | Existing housing retrofit priority | `source_layer=housing and supporting services — relative study priority` OR `source_layer=Egypt — Land Use;fclass=residential` | decay | 300 | 0.25 |
| adp_res_bldg_stock | Existing building stock suitable for reuse | `source_layer=Egypt — Buildings` | kde | 300 | 0.20 |
| adp_res_amenities | Walkable neighborhood services | `source_layer=Egypt — Points of Interest (points);fclass=convenience,greengrocer,bakery,pharmacy` | kde | 400 | 0.20 |
| adp_res_calm | Acoustic calm for residential conversion | `source_layer=السكك الحديدية` OR `source_layer=الطرق` OR `source_layer=Egypt — Land Use;fclass=industrial` | inverse_decay | 300 | 0.20 |
| adp_res_green | Proximity to parks & waterfronts | `source_layer=نهر النيل` OR `source_layer=Egypt — Land Use;fclass=park,grass` | decay | 450 | 0.15 |

### Typology: Commercial & Mercantile
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| adp_com_mixed_pri | Existing area mixed-use activation priority | `source_layer=existing area mixed use — relative study priority` OR `source_layer=Egypt — Land Use;fclass=commercial` | decay | 300 | 0.26 |
| adp_com_foot | Ground-floor retail & cafe cluster | `source_layer=Egypt — Points of Interest (points);fclass=kiosk,cafe,fast_food,restaurant,clothes,marketplace` | kde | 350 | 0.26 |
| adp_com_transit | Transit & pedestrian frontage | `source_layer=Egypt — Transport Points` OR `source_layer=Egypt — Traffic Points;fclass=pedestrian_crossing` | decay | 350 | 0.22 |
| adp_com_bldg | Dense existing building frontage | `source_layer=Egypt — Buildings` | kde | 350 | 0.14 |
| adp_com_fin | Financial & commercial anchors | `source_layer=New data — financial_services` OR `source_layer=Egypt — Points of Interest (points);fclass=bank,hotel` | decay | 500 | 0.12 |

### Typology: Institutional & Civic
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| adp_inst_health_pri | Health & older-person service priority | `source_layer=health and older person services — relative study priority` OR `source_layer=New data — health_facilities` | decay | 400 | 0.26 |
| adp_inst_school_pri | School & youth service priority | `source_layer=school and youth services — relative study priority` OR `source_layer=New data — education_facilities` | decay | 400 | 0.24 |
| adp_inst_cultural | Cultural & civic building reuse anchors | `source_layer=New data — cultural_places` OR `source_layer=Egypt — Points of Interest (polygons);fclass=public_building,university,college` | decay | 450 | 0.20 |
| adp_inst_access | Public transit accessibility | `source_layer=Egypt — Transport Points` OR `source_layer=الطرق` | decay | 400 | 0.16 |
| adp_inst_gap | Underserved residential retrofit need | `source_layer=New data — health_facilities` OR `source_layer=New data — education_facilities` | service_gap | 650 | 0.14 |

### Typology: Industrial & Logistics
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| adp_ind_zone | Existing industrial & workshop stock | `source_layer=Egypt — Land Use;fclass=industrial` OR `source_layer=المدن الصناعية` OR `source_layer=Egypt — Land Use;fclass=farmyard` | decay | 450 | 0.30 |
| adp_ind_freight | Heavy-arterial & rail retrofit access | `source_layer=الطرق` OR `source_layer=السكك الحديدية` | decay | 350 | 0.28 |
| adp_ind_buf | Buffered from dense residential | `source_layer=Egypt — Land Use;fclass=residential` OR `source_layer=New data — populated_places` | inverse_decay | 450 | 0.24 |
| adp_ind_power | Power & utility proximity | `source_layer=Egypt — Power Plants (WRI inventory)` OR `source_layer=Egypt — Waterways` | decay | 600 | 0.18 |

### Typology: Assembly & Recreational
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| adp_asm_cultural | Cultural heritage & landmark reuse | `source_layer=New data — cultural_places` OR `source_layer=Egypt — Points of Interest (points);fclass=attraction,viewpoint,artwork` | kde | 450 | 0.26 |
| adp_asm_sports | Existing sports & civic venue clusters | `source_layer=Egypt — Points of Interest (polygons);fclass=stadium,pitch,sports_centre,sports_hall,swimming_pool` | decay | 450 | 0.24 |
| adp_asm_water | Waterfront & park adjacency | `source_layer=نهر النيل` OR `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Land Use;fclass=park,grass` | decay | 400 | 0.24 |
| adp_asm_transit | Crowd transit & parking | `source_layer=Egypt — Transport Points` OR `source_layer=Egypt — Traffic Points;fclass=parking` | decay | 450 | 0.14 |
| adp_asm_hosp | Hospitality & dining cluster | `source_layer=Egypt — Points of Interest (points);fclass=cafe,restaurant,hotel` | kde | 400 | 0.12 |

### Typology: Transportation & Infrastructure
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| adp_trn_hubs | Existing rail & bus terminal retrofit | `source_layer=Egypt — Transport Points` OR `source_layer=السكك الحديدية` | decay | 350 | 0.30 |
| adp_trn_traffic | Traffic & grade-crossing pinch points | `source_layer=Egypt — Traffic Points` OR `source_layer=Egypt — Traffic Areas` | kde | 400 | 0.24 |
| adp_trn_solar | Solar rooftop / energy retrofit priority | `source_layer=solar resource investigation — relative study priority` OR `source_layer=Egypt — Power Plants (WRI inventory)` | decay | 500 | 0.24 |
| adp_trn_arterial | Major road corridor integration | `source_layer=الطرق` | decay | 300 | 0.22 |
