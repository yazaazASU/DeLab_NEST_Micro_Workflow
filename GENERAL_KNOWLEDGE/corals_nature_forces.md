# Corals Engine (Coordination) — 6 NEST Nature-First Spatial Forces

> **Machine-Readable Config:** Parsed directly by `run_3_engines.py` (`parse_typology_config`).  
> **Overarching Theme ([`engine_charter.md`](./engine_charter.md)):** **Corals (Coordination — Finding Elements in Site/Nature/Context to Use Better Together or Introduce a Beneficial Relationship)** evaluates the entire plot (land, shoreline, urban-edge, and water) using its signature **`corridor_bridge`** operator (`Group A AND Group B` midpoint/seam gravity) to locate where disconnected natural, civic, cultural, and infrastructural elements can be coordinated into mutually beneficial relationships. Serves as the Stage A spatial seedbed for downstream **Corals Engine Skills** (`Resources`, `Symbiosis`, `Branches`, `Evaluation`, `State`, `Adaptation`, `Archive`).

---

## 4. Nature-First Spatial Force Scoring Tables

### Typology: Hydrology & Waterfront
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cor_hyd_seam | Town-to-waterfront civic & port bridging seam | `source_layer=New data — populated_places` OR `source_layer=Egypt — Buildings` AND `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Nile River` OR `source_layer=نهر النيل` | corridor_bridge | 500 | 0.55 |
| cor_hyd_port | Marine / river port & public ferry interchange | `source_layer=New data — sea_ports` OR `source_layer=Egypt — Transport Points` AND `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Nile River` | corridor_bridge | 550 | 0.30 |
| cor_hyd_link | Regional blue-green waterfront spine | `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Waterways` | decay | 400 | 0.15 |

### Typology: Solar & Climate Intensity
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cor_sol_grid | Solar resource to settlement/transit microgrid bridge | `source_layer=development_investigation_priorities_2030` OR `source_layer=solar resource investigation — relative study priority` AND `source_layer=New data — populated_places` OR `source_layer=Egypt — Transport Points` | corridor_bridge | 600 | 0.50 |
| cor_sol_cold | Arterial solar cold-chain & EV charging spine | `source_layer=الطرق` OR `source_layer=gis_osm_roads_free_1` OR `source_layer=Egypt — Roads (Drive source)` AND `source_layer=New data — sea_ports` OR `source_layer=New data — populated_places` | corridor_bridge | 550 | 0.30 |
| cor_sol_load | Proximity to community energy & cooling demand | `source_layer=Egypt — Buildings` OR `source_layer=New data — populated_places` | decay | 450 | 0.20 |

### Typology: Biodiversity & Ecology
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cor_bio_bridge | Community-to-biodiversity eco-education bridge | `source_layer=New data — populated_places` OR `source_layer=New data — education_facilities` AND `source_layer=gbif_egypt_plants` OR `source_layer=GBIF — Egypt Birds (observations)` OR `source_layer=GBIF — Egypt Species Observations` | corridor_bridge | 700 | 0.55 |
| cor_bio_cor | Green/agricultural to natural habitat corridor | `source_layer=Egypt — Land Use;fclass=farmland,orchard,park,grass` AND `source_layer=gbif_egypt_plants` OR `source_layer=Egypt — Water Areas` | corridor_bridge | 650 | 0.25 |
| cor_bio_trail | Accessible eco-trail & visitor dispersion seam | `source_layer=gis_osm_roads_free_1` OR `source_layer=Egypt — Transport Points` | decay | 450 | 0.20 |

### Typology: Heritage & Culture Gravity
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cor_her_bridge | Settlement-to-UNESCO heritage cultural & craft spine | `source_layer=New data — populated_places` OR `source_layer=Egypt — Buildings` AND `source_layer=New data — egypt_unesco_world_heritage` OR `source_layer=New data — cultural_places` | corridor_bridge | 650 | 0.55 |
| cor_her_trans | Transit/port to heritage visitor dispersion bridge | `source_layer=Egypt — Transport Points` OR `source_layer=New data — sea_ports` OR `source_layer=gis_osm_roads_free_1` AND `source_layer=New data — egypt_unesco_world_heritage` OR `source_layer=New data — cultural_places` | corridor_bridge | 600 | 0.30 |
| cor_her_poi | Cultural POI & community gathering cluster | `source_layer=New data — cultural_places` OR `source_layer=Egypt — Points of Interest (points)` | kde | 500 | 0.15 |

### Typology: Civic & Service Deficit
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cor_civ_seam | Road/transit spine to community catchment civic bridge | `source_layer=gis_osm_roads_free_1` OR `source_layer=الطرق` OR `source_layer=Egypt — Transport Points` AND `source_layer=New data — populated_places` OR `source_layer=Egypt — Buildings` | corridor_bridge | 450 | 0.40 |
| cor_civ_hlth | Regional health service gap bridging | `source_layer=New data — health_facilities` | service_gap | 750 | 0.30 |
| cor_civ_edu | Regional youth & STEM education gap bridging | `source_layer=New data — education_facilities` | service_gap | 750 | 0.30 |

### Typology: Corridor & Network Connectivity
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cor_cor_inter | Road-to-port / intermodal transit transfer bridge | `source_layer=gis_osm_roads_free_1` OR `source_layer=الطرق` OR `source_layer=Egypt — Roads (Drive source)` AND `source_layer=New data — sea_ports` OR `source_layer=Egypt — Transport Points` OR `source_layer=Egypt — Water Areas` | corridor_bridge | 450 | 0.50 |
| cor_cor_town | Settlement-to-arterial logistics & market seam | `source_layer=New data — populated_places` OR `source_layer=Egypt — Buildings` AND `source_layer=gis_osm_roads_free_1` OR `source_layer=الطرق` | corridor_bridge | 400 | 0.30 |
| cor_cor_hub | Multi-modal network convergence density | `source_layer=Egypt — Transport Points` OR `source_layer=New data — sea_ports` OR `source_layer=New data — populated_places` | kde | 550 | 0.20 |

---

## 5. Mixed-Use Compatibility Whitelist
| Typology A | Typology B | Rationale |
| :--- | :--- | :--- |
| Hydrology & Waterfront | Corridor & Network Connectivity | Multi-modal eco-ports & town-to-waterfront promenades |
| Hydrology & Waterfront | Heritage & Culture Gravity | Heritage-to-waterfront cultural & visitor dispersion spines |
| Hydrology & Waterfront | Biodiversity & Ecology | Riparian bioswales & community wetland parks |
| Hydrology & Waterfront | Civic & Service Deficit | Waterfront civic commons & community markets |
| Solar & Climate Intensity | Corridor & Network Connectivity | Solar EV/ferry charging & cold-chain logistics corridors |
| Solar & Climate Intensity | Civic & Service Deficit | Shaded solar-powered community health, STEM & transit hubs |
| Biodiversity & Ecology | Heritage & Culture Gravity | Eco-cultural narrative trails & artisan botanical spines |
| Biodiversity & Ecology | Civic & Service Deficit | Community agro-ecology & youth environmental academies |
| Heritage & Culture Gravity | Civic & Service Deficit | Cultural civic exchanges, craft ateliers & community forums |
| Heritage & Culture Gravity | Corridor & Network Connectivity | Transit-oriented heritage visitor gateways |
| Civic & Service Deficit | Corridor & Network Connectivity | Accessible regional health, STEM & market hubs |
