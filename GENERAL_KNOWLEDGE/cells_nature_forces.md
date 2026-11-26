# Cells Engine (Adaptation) — 6 NEST Nature-First Spatial Forces

> **Machine-Readable Config:** Parsed directly by `run_3_engines.py` (`parse_typology_config`).  
> **Overarching Theme ([`engine_charter.md`](./engine_charter.md)):** **Cells (Adaptation — Finding Elements in Site/Nature/Context to Unlock Their Full Potential by Adapting Them Into Something New/Better)** targets both natural and contextual/man-made elements (landforms, caves, extreme solar/evaporative microclimates, wadis, quarries, ruins, underused edges, and GBIF biodiversity pockets — while avoiding dense active urban cores) using its signature **`ecotone_gradient`** (`Group A AND Group B`) and **`kde`** operators. Serves as the Stage A spatial seedbed for downstream **Cells Engine Skills** (`Host Element`, `Latent Potential`, `Adaptation Pathway`, `Gene Refs`, `Novelty & Confidence`, `Reinterpretation Fallback`).

---

## 4. Nature-First Spatial Force Scoring Tables

### Typology: Hydrology & Waterfront
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cel_hyd_eco | Water-meets-arid-climate hydrological ecotone | `source_layer=Egypt — Water Areas` OR `source_layer=نهر النيل` OR `source_layer=Egypt — Nile River` OR `source_layer=Egypt — Waterways` AND `source_layer=development_investigation_priorities_2030` OR `source_layer=agricultural water efficiency — relative study priority` | ecotone_gradient | 300 | 0.55 |
| cel_hyd_edge | Active littoral shoreline & flood-pulse transition band | `source_layer=Egypt — Water Areas` OR `source_layer=نهر النيل` OR `source_layer=Egypt — Nile River` | ecotone_gradient | 180 | 0.25 |
| cel_hyd_buf | Buffered from impervious urban heat-island stock | `source_layer=Egypt — Buildings` | inverse_decay | 350 | 0.20 |

### Typology: Solar & Climate Intensity
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cel_sol_evap | Extreme solar-water evaporation & thermal collision | `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Nile River` OR `source_layer=نهر النيل` AND `source_layer=development_investigation_priorities_2030` OR `source_layer=solar resource investigation — relative study priority` | ecotone_gradient | 450 | 0.55 |
| cel_sol_ext | High cooling-degree & evapotranspiration exposure | `source_layer=development_investigation_priorities_2030` OR `source_layer=solar resource investigation — relative study priority` | decay | 500 | 0.25 |
| cel_sol_open | Unobstructed wind/thermal boundary layer | `source_layer=Egypt — Buildings` | inverse_decay | 300 | 0.20 |

### Typology: Biodiversity & Ecology
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cel_bio_kde | High-density GBIF flora, avian & species hotspot cluster | `source_layer=gbif_egypt_plants` OR `source_layer=GBIF — Egypt Birds (observations)` OR `source_layer=GBIF — Egypt Species Observations` OR `source_layer=GBIF — Egypt Mammals (observations)` | kde | 550 | 0.50 |
| cel_bio_eco | Aquatic-terrestrial wetland & habitat ecotone | `source_layer=gbif_egypt_plants` OR `source_layer=GBIF — Egypt Birds (observations)` AND `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Nile River` | ecotone_gradient | 450 | 0.30 |
| cel_bio_buf | Acoustic & habitat refuge away from roads | `source_layer=الطرق` OR `source_layer=gis_osm_roads_free_1` | inverse_decay | 400 | 0.20 |

### Typology: Heritage & Culture Gravity
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cel_her_eco | Heritage-meets-shoreline/ecology adaptation interface | `source_layer=New data — egypt_unesco_world_heritage` OR `source_layer=New data — cultural_places` AND `source_layer=Egypt — Water Areas` OR `source_layer=gbif_egypt_plants` | ecotone_gradient | 650 | 0.50 |
| cel_her_ctx | Underused contextual, quarry, ruin or cultural transformation edge | `source_layer=New data — egypt_unesco_world_heritage` OR `source_layer=New data — cultural_places` OR `source_layer=Egypt — Land Use;fclass=quarry,brownfield,scrub,heath` | decay | 750 | 0.30 |
| cel_her_calm | Low-disturbance adaptation buffer away from dense urban cores | `source_layer=Egypt — Buildings` OR `source_layer=الطرق` | inverse_decay | 300 | 0.20 |

### Typology: Civic & Service Deficit
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cel_civ_cool | Microclimate-cooled settlement edge (Town × Water/Green) | `source_layer=New data — populated_places` OR `source_layer=Egypt — Land Use;fclass=residential` AND `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Nile River` | ecotone_gradient | 550 | 0.45 |
| cel_civ_hlth | Climate-stress health service deficit | `source_layer=New data — health_facilities` | service_gap | 900 | 0.30 |
| cel_civ_edu | Adaptive ecological education deficit | `source_layer=New data — education_facilities` | service_gap | 900 | 0.25 |

### Typology: Corridor & Network Connectivity
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| cel_cor_amph | Amphibious land-to-water mobility transition zone | `source_layer=gis_osm_roads_free_1` OR `source_layer=الطرق` OR `source_layer=New data — sea_ports` AND `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Nile River` | ecotone_gradient | 400 | 0.55 |
| cel_cor_blue | Blue-green ecological migration corridor | `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Waterways` OR `source_layer=Egypt — Nile River` | decay | 350 | 0.25 |
| cel_cor_bio | Low-impact trail interface with biodiversity | `source_layer=gbif_egypt_plants` OR `source_layer=GBIF — Egypt Birds (observations)` | decay | 600 | 0.20 |

---

## 5. Mixed-Use Compatibility Whitelist
| Typology A | Typology B | Rationale |
| :--- | :--- | :--- |
| Hydrology & Waterfront | Solar & Climate Intensity | Floating/canopy evaporation-shield PV & thermal water cooling |
| Hydrology & Waterfront | Biodiversity & Ecology | Littoral reed-bed bio-filtration & avian wetland restoration |
| Hydrology & Waterfront | Heritage & Culture Gravity | Climate-buffered heritage shorelines & amphibious terraces |
| Hydrology & Waterfront | Corridor & Network Connectivity | Zero-emission waterborne mobility & watershed corridors |
| Solar & Climate Intensity | Biodiversity & Ecology | Shade-mesh microclimate craters & arid seed-bank biomes |
| Solar & Climate Intensity | Civic & Service Deficit | Passive-cooled desert community clinics & thermal sanctuaries |
| Biodiversity & Ecology | Heritage & Culture Gravity | Living eco-archaeological sanctuaries |
| Civic & Service Deficit | Corridor & Network Connectivity | Climate-resilient regional service & emergency nodes |
