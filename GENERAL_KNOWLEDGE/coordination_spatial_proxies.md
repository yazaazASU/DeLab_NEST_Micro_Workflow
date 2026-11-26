# Engine 3: Coordination — Spatial Proxies & Scoring Specification *(Legacy 6-Typology Archive)*

> **Deprecation & Active Config Notice:** Under the **NEST Nature-First Architecture**, `run_3_engines.py` now uses [`corals_nature_forces.md`](./corals_nature_forces.md) to score the **6 NEST Nature-First Spatial Forces** (`Hydrology & Waterfront`, `Solar & Climate Intensity`, `Biodiversity & Ecology`, `Heritage & Culture Gravity`, `Civic & Service Deficit`, `Corridor & Network Connectivity`) across all land, shoreline, and water zones. This file is retained as an archival reference only.

This specification drives **Engine 3 (Coordination)**, evaluating **all non-water land & seam cells** to identify where shared infrastructure, gap-bridging connections, and district-balancing facilities should be coordinated across plots.

---

## 1. Coordination Mask (All Non-Water Land)
- **Included:** All cells inside the Assiut 5×5 km boundary that are not open water (`Egypt — Water Areas`, `نهر النيل`, `Egypt — Waterways`).
- **Excluded (Masked = 0):** Open water bodies only.

---

## 2. Typology Scoring Tables (Coordination Lens)

### Typology: Residential
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| crd_res_ext | Urban extension & housing coordination priority | `source_layer=urban extension investigation — relative study priority` OR `source_layer=housing and supporting services — relative study priority` | decay | 400 | 0.30 |
| crd_res_gaps | Neighborhood street-endpoint stitching | `source_layer=39,403 endpoint gaps — inspect,do not auto-connect` | kde | 350 | 0.22 |
| crd_res_transit | Linking housing to transit nodes | `source_layer=Egypt — Transport Points;fclass=bus_stop,bus_station` | decay | 450 | 0.18 |
| crd_res_svc | Proximity to schools & health anchors | `source_layer=New data — education_facilities` OR `source_layer=New data — health_facilities` | decay | 500 | 0.16 |
| crd_res_calm | Buffering from heavy rail/industry | `source_layer=السكك الحديدية` OR `source_layer=Egypt — Land Use;fclass=industrial` | inverse_decay | 350 | 0.14 |

### Typology: Commercial & Mercantile
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| crd_com_mixed | Cross-district mixed-use seam priority | `source_layer=existing area mixed use — relative study priority` | decay | 400 | 0.28 |
| crd_com_grade | Coincident grade-context & crossing hubs | `source_layer=10,681 coincident grade-context cases` OR `source_layer=Egypt — Traffic Points;fclass=pedestrian_crossing` | kde | 400 | 0.24 |
| crd_com_trans | Intermodal transit convergence | `source_layer=Egypt — Transport Points` OR `source_layer=Area-centre strategic-network snapping diagnostics` | decay | 450 | 0.24 |
| crd_com_pop | Underserved commercial catchment | `source_layer=New data — populated_places` OR `source_layer=Egypt — Points of Interest (points);fclass=marketplace,supermarket` | kde | 550 | 0.24 |

### Typology: Institutional & Civic
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| crd_inst_health_gap | District health service gap | `source_layer=New data — health_facilities` OR `source_layer=health and older person services — relative study priority` | service_gap | 700 | 0.28 |
| crd_inst_edu_gap | District school & youth service gap | `source_layer=New data — education_facilities` OR `source_layer=school and youth services — relative study priority` | service_gap | 650 | 0.26 |
| crd_inst_civic | Civic & cultural network nodes | `source_layer=New data — cultural_places` OR `source_layer=Egypt — Places of Worship (polygons)` | decay | 500 | 0.20 |
| crd_inst_transit | Multi-district transit reach | `source_layer=Egypt — Transport Points` OR `source_layer=الطرق` | decay | 400 | 0.26 |

### Typology: Industrial & Logistics
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| crd_ind_snap | Strategic freight-network snapping & arterials | `source_layer=Area-centre strategic-network snapping diagnostics` OR `source_layer=الطرق` OR `source_layer=السكك الحديدية` | decay | 450 | 0.30 |
| crd_ind_agri | Agricultural-water & supply-chain interface | `source_layer=agricultural water efficiency — relative study priority` OR `source_layer=Egypt — Land Use;fclass=farmland,industrial` | decay | 450 | 0.26 |
| crd_ind_buf | Separation from residential cores | `source_layer=New data — populated_places` OR `source_layer=Egypt — Land Use;fclass=residential` | inverse_decay | 500 | 0.24 |
| crd_ind_power | Grid & power-plant coordination | `source_layer=Egypt — Power Plants (WRI inventory)` OR `source_layer=New data — egypt_power_plants_wri` | decay | 700 | 0.20 |

### Typology: Assembly & Recreational
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| crd_asm_blue | Blue-green corridor stitching (Nile & parks) | `source_layer=نهر النيل` OR `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Land Use;fclass=park,grass` | decay | 400 | 0.28 |
| crd_asm_cult | Cultural & recreational network linking | `source_layer=New data — cultural_places` OR `source_layer=Egypt — Points of Interest (polygons);fclass=stadium,pitch,park` | kde | 500 | 0.26 |
| crd_asm_gap | Pedestrian gap-stitching near destinations | `source_layer=39,403 endpoint gaps — inspect,do not auto-connect` OR `source_layer=Egypt — Traffic Points;fclass=pedestrian_crossing` | kde | 400 | 0.22 |
| crd_asm_trans | Regional crowd transit dispersion | `source_layer=Egypt — Transport Points` OR `source_layer=Egypt — Traffic Areas` | decay | 450 | 0.24 |

### Typology: Transportation & Infrastructure
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| crd_trn_gaps | Road-network endpoint gap resolution | `source_layer=39,403 endpoint gaps — inspect,do not auto-connect` | kde | 350 | 0.28 |
| crd_trn_grade | Grade-context & crossing coordination | `source_layer=10,681 coincident grade-context cases` OR `source_layer=Egypt — Traffic Points;fclass=railway_crossing` | kde | 400 | 0.24 |
| crd_trn_solar | Solar & utility corridor coordination | `source_layer=solar resource investigation — relative study priority` OR `source_layer=Egypt — Power Plants (WRI inventory)` | decay | 500 | 0.24 |
| crd_trn_rail | Rail, arterial & transit spine | `source_layer=السكك الحديدية` OR `source_layer=الطرق` OR `source_layer=Egypt — Transport Points` | decay | 350 | 0.24 |
