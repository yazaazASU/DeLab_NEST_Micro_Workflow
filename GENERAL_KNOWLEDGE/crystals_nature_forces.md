# Crystals Engine (Development) — 6 NEST Nature-First Spatial Forces

> **Machine-Readable Config:** Parsed directly by `run_3_engines.py` (`parse_typology_config`).  
> **Overarching Theme ([`engine_charter.md`](./engine_charter.md)):** **Crystals (Development — Finding Points of Interest to Build Around, In, or At)** identifies high-gravity natural, cultural, infrastructural, and civic POIs and scores buildable terrain **around** (`ring_decay` standoff/viewshed ring), **at** (`decay` direct edge/gateway proximity), or **in** (`kde` focal POI clusters), while keeping existing road footprints and dense built cores masked for new footprints. Serves as the Stage A spatial seedbed for downstream **Crystals Engine Skills** (`Scale`, `Facets`, `Axes`, `Density`, `Field`, `Bonds`).

---

## 4. Nature-First Spatial Force Scoring Tables

### Typology: Hydrology & Waterfront
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cry_hyd_ring | Scenic waterfront plinth & viewshed standoff | `source_layer=Egypt — Water Areas` OR `source_layer=نهر النيل` OR `source_layer=Egypt — Nile River` OR `source_layer=Egypt — Waterways` OR `source_layer=HydroRIVERS_v10_af` | ring_decay | 400 | 0.50 |
| cry_hyd_calm | Low-disturbance buffer from heavy urban/road fabric | `source_layer=Egypt — Buildings` OR `source_layer=الطرق` | inverse_decay | 400 | 0.30 |
| cry_hyd_agri | Shoreline fertility & water-efficiency study interface | `source_layer=agricultural water efficiency — relative study priority` OR `source_layer=Egypt — Land Use;fclass=farmland,orchard,meadow` | decay | 600 | 0.20 |

### Typology: Solar & Climate Intensity
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cry_sol_open | Unshaded open monumental canvas away from buildings | `source_layer=Egypt — Buildings` | inverse_decay | 450 | 0.45 |
| cry_sol_prio | High solar irradiance & desert datum zone | `source_layer=solar resource investigation — relative study priority` OR `source_layer=development_investigation_priorities_2030` | decay | 600 | 0.35 |
| cry_sol_breeze | Standoff thermal breeze ring from water edge | `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Nile River` | ring_decay | 500 | 0.20 |

### Typology: Biodiversity & Ecology
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cry_bio_ring | Respectful observation standoff from GBIF habitats | `source_layer=gbif_egypt_plants` OR `source_layer=GBIF — Egypt Birds (observations)` OR `source_layer=GBIF — Egypt Species Observations` OR `source_layer=GBIF — Egypt Mammals (observations)` | ring_decay | 550 | 0.45 |
| cry_bio_quiet | Deep acoustic & ecological quiet canvas | `source_layer=الطرق` OR `source_layer=السكك الحديدية` OR `source_layer=Egypt — Buildings` | inverse_decay | 500 | 0.35 |
| cry_bio_hab | Adjacent natural reserve or open green zone | `source_layer=Egypt — Land Use;fclass=nature_reserve,forest,park,meadow,scrub,heath,grass` | decay | 650 | 0.20 |

### Typology: Heritage & Culture Gravity
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cry_her_axis | Build-around visual-axis standoff from UNESCO/cultural POIs | `source_layer=New data — egypt_unesco_world_heritage` OR `source_layer=New data — cultural_places` | ring_decay | 1100 | 0.50 |
| cry_her_poi | Build-at / build-in gravity near cultural, civic & viewpoint POIs | `source_layer=Egypt — Points of Interest (points)` OR `source_layer=Egypt — Points of Interest (polygons)` OR `source_layer=New data — cultural_places` | decay | 650 | 0.30 |
| cry_her_calm | Clear buildable horizon away from dense building footprints | `source_layer=Egypt — Buildings` | inverse_decay | 350 | 0.20 |

### Typology: Civic & Service Deficit
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cry_civ_ring | Build-around civic expansion ring outside settlement core | `source_layer=New data — populated_places` OR `source_layer=Egypt — Land Use;fclass=residential` | ring_decay | 850 | 0.35 |
| cry_civ_poi | Build-at existing civic & community POI gravity | `source_layer=Egypt — Points of Interest (points)` OR `source_layer=Egypt — Points of Interest (polygons)` | kde | 600 | 0.15 |
| cry_civ_health | Underserved health facility catchment gap | `source_layer=New data — health_facilities` | service_gap | 1000 | 0.25 |
| cry_civ_edu | Underserved school & youth facility gap | `source_layer=New data — education_facilities` | service_gap | 1000 | 0.25 |

### Typology: Corridor & Network Connectivity
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cry_cor_gate | Build-at / build-around primary highway & arterial gateway | `source_layer=الطرق` OR `source_layer=Egypt — Roads (Drive source)` OR `source_layer=gis_osm_roads_free_1` OR `source_layer=New data — heigit_EG_planet_roadsurface_lines` | ring_decay | 350 | 0.45 |
| cry_cor_port | Build-at port, rail & regional transit POI hub | `source_layer=New data — sea_ports` OR `source_layer=Egypt — Transport Points` OR `source_layer=السكك الحديدية` | decay | 700 | 0.35 |
| cry_cor_open | Buildable parcel envelope for landmark staging | `source_layer=Egypt — Buildings` | inverse_decay | 350 | 0.20 |

---

## 5. Mixed-Use Compatibility Whitelist
| Typology A | Typology B | Rationale |
| :--- | :--- | :--- |
| Hydrology & Waterfront | Solar & Climate Intensity | Evaporative cooling + solar canopy plinth synergy |
| Hydrology & Waterfront | Biodiversity & Ecology | Waterfront overlooks & protected littoral sanctuaries |
| Hydrology & Waterfront | Heritage & Culture Gravity | Monumental water-edge cultural gateways & axis alignments |
| Hydrology & Waterfront | Corridor & Network Connectivity | Waterfront arrival gateways & scenic overlooks |
| Solar & Climate Intensity | Biodiversity & Ecology | Shade-canopy arid botanical & seed-bank sanctuaries |
| Solar & Climate Intensity | Heritage & Culture Gravity | Solar-aligned cultural monuments & earth-sheltered museums |
| Solar & Climate Intensity | Civic & Service Deficit | Passive-cooled civic, health & youth campuses |
| Biodiversity & Ecology | Heritage & Culture Gravity | Eco-cultural sanctuaries & dark-sky heritage reserves |
| Heritage & Culture Gravity | Civic & Service Deficit | Sovereign cultural forums, museums & craft academies |
| Heritage & Culture Gravity | Corridor & Network Connectivity | National visitor arrival gateways & cultural landmarks |
| Civic & Service Deficit | Corridor & Network Connectivity | Regional civic campuses & accessible public anchors |
