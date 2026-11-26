# Building Typology Spatial Proxies & Scoring Specification *(Legacy 6-Typology Archive)*

> **Deprecation & Active Config Notice:** Under the **NEST Nature-First Architecture**, `run_3_engines.py` now parses the **6 NEST Nature-First Spatial Forces** from [`crystals_nature_forces.md`](./crystals_nature_forces.md), [`cells_nature_forces.md`](./cells_nature_forces.md), and [`corals_nature_forces.md`](./corals_nature_forces.md). This file is retained as an archival reference for legacy 6-typology single-engine runs (`heatmap_engine.py`).

This companion document translates the qualitative spatial criteria in `building_typologies.md` into **quantitative GIS rules and derived spatial proxies** for the Assiut 5×5 km dataset (`assiut_5x5km_all_layers.geojson`).

> **Machine-Readable Config:** `heatmap_engine.py` parses the Markdown tables below directly. Editing a **Weight**, **Radius / Sigma (m)**, or **Method** here updates the generated heatmaps on the next run.

---

## 1. Global Hard Mask (Developable Land)
Cells intersecting any of the following physical constraints are forced to **0** across all 6 typologies:
- **Water Bodies:** `Egypt — Water Areas`, `نهر النيل`, `Egypt — Waterways` (15 m buffer), `قنوات المصارف — 1`, `قنوات المصارف — 2` (10 m buffer)
- **Road Network:** `الطرق` (12 m buffer), `New data — heigit_EG_planet_roadsurface_lines` (8 m buffer)
- **Existing Buildings:** `Egypt — Buildings`

---

## 2. Derived Spatial Proxies (Missing Direct Layers)
Where a criterion in `building_typologies.md` has no direct GIS layer in `assiut_5x5km_all_layers.geojson`, the following spatial proxies are derived:

| Qualitative Criterion | Missing Direct Layer | Derived Spatial Proxy |
| :--- | :--- | :--- |
| **Sensory calm / low noise contours** | Acoustic dB contours | Inverse proximity to major roads (`الطرق`), railways (`السكك الحديدية`), industrial zones (`fclass=industrial`, `المدن الصناعية`), and power plants |
| **Low through-traffic / local streets** | Traffic volume counts | Proximity to secondary road network (`heigit_EG_planet_roadsurface_lines`) while penalized near `Traffic Points` / `الطرق` arterials |
| **Foot traffic & commuter density** | Pedestrian flow / mobile telemetry | Kernel Density Estimation (KDE) of high-turnover POIs (`kiosk`, `cafe`, `fast_food`, `convenience`, `marketplace`) + `pedestrian_crossing` + `Transport Points` |
| **Surrounding purchasing power / business ecosystem** | Household income / firm registry | KDE of retail, `financial_services`, `commercial` land use, `hotel`/`restaurant`, and `bank`/`atm` POIs |
| **Demographic service gaps** | Fine-grained census / service catchment deficits | `service_gap` = local residential/populated density (`populated_places` + `residential` land use) minus existing facility coverage (`health_facilities` or `education_facilities`) |
| **Clean microclimates** | Air quality / urban heat island sensors | Combined green/blue buffer (`park`, `grass`, `water`, `river`) minus industrial/arterial proximity |
| **Freight & heavy-truck arterial access** | Freight tonnage / truck routes | Proximity to primary highways (`الطرق`) + rail (`السكك الحديدية`) + distance away from dense residential neighborhoods |
| **Flat, low-cost peripheral land & workforce** | Land price parcels & labor census | `urban extension investigation` / `farmland` / `farmyard` / low building density + moderate distance from `populated_places` |
| **Solar irradiance / watershed gradients** | Weather station / high-res DEM | `solar resource investigation` study priority polygons, `الكنتور` contours, and `Waterways` / `نهر النيل` convergence |
| **Natural views & destination appeal** | Viewshed / tourism footfall | Proximity to `نهر النيل` / `Water Areas`, `park`/`stadium`/`pitch`, `cultural_places`, `attraction`, and `viewpoint` |

---

## 3. Scoring Methods Reference
- `decay`: Exponential distance decay $\exp(-d / r)$ where $d$ is distance (m) to nearest matching feature and $r$ is `Radius / Sigma (m)`. (1.0 at feature, 0.37 at $r$).
- `inverse_decay`: $1 - \exp(-d / r)$ — rewards being *far* from nuisance/incompatible features (0.0 at feature, 0.63 at $r$).
- `kde`: Gaussian-like Kernel Density of matching feature centroids/points with bandwidth $\sigma = \text{Radius / Sigma (m)}$, min-max normalized to `[0, 1]`.
- `inside`: 1.0 if cell is inside polygon (with soft 150 m edge falloff), 0.0 far away.
- `service_gap`: $\max(0, \text{norm}(\text{Residential KDE}_{800m}) - \text{Facility Decay}_{r})$ — peaks in populated areas underserved by the target facility type.

---

## 4. Typology Scoring Tables

### Typology: Residential
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| res_neighborhood | Established residential fabric | `source_layer=Egypt — Land Use;fclass=residential` OR `source_layer=New data — populated_places` OR `source_layer=housing and supporting services — relative study priority` | decay | 350 | 0.20 |
| res_walk_amenities | Walkability to daily amenities | `source_layer=Egypt — Points of Interest (points);fclass=convenience,greengrocer,bakery,pharmacy,kiosk` | kde | 400 | 0.20 |
| res_schools_parks | Access to schools & parks | `source_layer=New data — education_facilities` OR `source_layer=Egypt — Points of Interest (polygons);fclass=park,playground,pitch` OR `source_layer=Egypt — Land Use;fclass=park,grass` | decay | 500 | 0.15 |
| res_transit | Local public transit access | `source_layer=Egypt — Transport Points;fclass=bus_stop,bus_station` | decay | 450 | 0.12 |
| res_acoustic_calm | Sensory calm (away from rail/industrial/arterials) | `source_layer=السكك الحديدية` OR `source_layer=الطرق` OR `source_layer=Egypt — Land Use;fclass=industrial` OR `source_layer=المدن الصناعية` | inverse_decay | 300 | 0.18 |
| res_views_breeze | Natural views (Nile, waterfronts, greenery) | `source_layer=نهر النيل` OR `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Land Use;fclass=park,grass` | decay | 400 | 0.15 |

### Typology: Commercial & Mercantile
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| com_foot_traffic | Human flow & foot-traffic density | `source_layer=Egypt — Points of Interest (points);fclass=kiosk,cafe,fast_food,convenience,restaurant,clothes,marketplace,supermarket` | kde | 350 | 0.28 |
| com_arterial_vis | High-visibility arterial & street frontage | `source_layer=الطرق` OR `source_layer=New data — heigit_EG_planet_roadsurface_lines` | decay | 150 | 0.18 |
| com_transit_hubs | Major transit & pedestrian hubs | `source_layer=Egypt — Transport Points` OR `source_layer=Egypt — Traffic Points;fclass=pedestrian_crossing,parking` | decay | 400 | 0.20 |
| com_biz_ecosystem | Financial & business ecosystem | `source_layer=New data — financial_services` OR `source_layer=Egypt — Points of Interest (points);fclass=bank,atm,hotel` OR `source_layer=Egypt — Land Use;fclass=commercial` | kde | 450 | 0.18 |
| com_catchment | Surrounding consumer catchment | `source_layer=New data — populated_places` OR `source_layer=Egypt — Buildings` | kde | 600 | 0.16 |

### Typology: Institutional & Civic
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| inst_health_gap | Underserved population health gap | `source_layer=New data — health_facilities` OR `source_layer=Egypt — Points of Interest (points);fclass=hospital,clinic` | service_gap | 700 | 0.24 |
| inst_edu_gap | Underserved school & youth gap | `source_layer=New data — education_facilities` OR `source_layer=Egypt — Points of Interest (points);fclass=school,college,university` | service_gap | 650 | 0.22 |
| inst_civic_gravity | Cultural, civic & knowledge nodes | `source_layer=New data — cultural_places` OR `source_layer=Egypt — Points of Interest (polygons);fclass=university,college,public_building,hospital` OR `source_layer=Egypt — Places of Worship (polygons)` | decay | 450 | 0.20 |
| inst_multimodal | Multi-modal public & emergency access | `source_layer=Egypt — Transport Points` OR `source_layer=الطرق` | decay | 350 | 0.18 |
| inst_clean_micro | Clean microclimate & quiet buffer | `source_layer=Egypt — Land Use;fclass=park,grass` OR `source_layer=Egypt — Water Areas` | decay | 400 | 0.16 |

### Typology: Industrial & Logistics
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ind_freight_roads | Direct heavy-truck arterial & rail access | `source_layer=الطرق` OR `source_layer=السكك الحديدية` OR `source_layer=Egypt — Transport Points;fclass=railway_station` | decay | 350 | 0.28 |
| ind_buffer_res | Buffered away from dense residential core | `source_layer=Egypt — Land Use;fclass=residential` OR `source_layer=New data — populated_places` | inverse_decay | 500 | 0.26 |
| ind_existing_zone | Existing industrial & utility corridors | `source_layer=Egypt — Land Use;fclass=industrial` OR `source_layer=المدن الصناعية` OR `source_layer=Egypt — Power Plants (WRI inventory)` | decay | 600 | 0.18 |
| ind_periphery_land | Low-cost peripheral / agricultural-edge land | `source_layer=Egypt — Land Use;fclass=farmland,farmyard` OR `source_layer=urban extension investigation — relative study priority` | decay | 350 | 0.16 |
| ind_water_process | Process water & canal proximity | `source_layer=Egypt — Waterways` OR `source_layer=نهر النيل` | decay | 500 | 0.12 |

### Typology: Assembly & Recreational
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| asm_scenic_water | Waterfronts, parks & scenic landmarks | `source_layer=نهر النيل` OR `source_layer=Egypt — Water Areas` OR `source_layer=Egypt — Land Use;fclass=park,grass` | decay | 400 | 0.26 |
| asm_cultural_dest | Cultural heritage, worship & destination POIs | `source_layer=New data — cultural_places` OR `source_layer=Egypt — Points of Interest (points);fclass=attraction,viewpoint,hotel,artwork` OR `source_layer=Egypt — Places of Worship (points)` | kde | 500 | 0.24 |
| asm_sports_venues | Existing recreational & sports anchors | `source_layer=Egypt — Points of Interest (polygons);fclass=stadium,pitch,sports_centre,sports_hall,swimming_pool,track` | decay | 450 | 0.20 |
| asm_crowd_transit | High-capacity transit & parking dispersion | `source_layer=Egypt — Transport Points` OR `source_layer=Egypt — Traffic Points;fclass=parking,fuel` OR `source_layer=Egypt — Traffic Areas` | decay | 450 | 0.18 |
| asm_night_energy | Vibrant hospitality & gathering energy | `source_layer=Egypt — Points of Interest (points);fclass=cafe,restaurant,fast_food` | kde | 400 | 0.12 |

### Typology: Transportation & Infrastructure
| Factor ID | Criterion | Proxy / GIS Layer Filter | Scoring Method | Radius / Sigma (m) | Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| trn_rail_arterial | Direct anchoring to rail & major arterials | `source_layer=السكك الحديدية` OR `source_layer=الطرق` OR `source_layer=Egypt — Transport Points;fclass=railway_station,bus_station` | decay | 300 | 0.30 |
| trn_pinch_points | Network convergence & crossing pinch points | `source_layer=Egypt — Traffic Points` OR `source_layer=Egypt — Traffic Areas` | kde | 400 | 0.24 |
| trn_energy_grid | Power & utility infrastructure corridors | `source_layer=Egypt — Power Plants (WRI inventory)` OR `source_layer=New data — egypt_power_plants_wri` OR `source_layer=Egypt — Points of Interest (polygons);fclass=water_works` | decay | 700 | 0.18 |
| trn_resource_flow | Solar & watershed/river resource flows | `source_layer=solar resource investigation — relative study priority` OR `source_layer=الكنتور` OR `source_layer=نهر النيل` | decay | 500 | 0.14 |
| trn_sep_res | Separation from sensitive residential cores | `source_layer=Egypt — Land Use;fclass=residential` | inverse_decay | 350 | 0.14 |

---

## 5. Mixed-Use Compatibility Whitelist (2+ Typologies)
Mixed-Use is defined as **any combination of 2 or more** of the 6 primary typologies where **every pair** in the combination appears in the approved whitelist below (forming a clique in the compatibility graph). At each cell, each valid clique $C$ is scored using **Mean minus Sample Standard Deviation** ($\bar{L} - \sigma$), which rewards high compatibility while penalizing imbalanced/weak mixes:
$$\text{MixedUse} = \max_{C \in \text{ValidCliques}} \max\left(0,\; \bar{L}(C) - \sigma(C)\right), \quad \sigma(C) = \sqrt{\frac{\sum_{i \in C}(s_i - \bar{L})^2}{|C| - 1}}$$

| Typology A | Typology B | Urban Rationale |
| :--- | :--- | :--- |
| Residential | Commercial & Mercantile | Classic main-street / retail-podium housing; daytime retail + nighttime residents |
| Residential | Institutional & Civic | Neighborhood housing paired with schools, clinics, libraries, or civic hubs |
| Residential | Assembly & Recreational | Parkfront/waterfront living, hospitality, and community recreation |
| Commercial & Mercantile | Institutional & Civic | Civic plazas, university-district retail, and medical-office hubs |
| Commercial & Mercantile | Assembly & Recreational | Entertainment, dining, cultural venues, and hospitality districts |
| Commercial & Mercantile | Transportation & Infrastructure | Transit-Oriented Development (TOD) and station-concourse retail |
| Institutional & Civic | Assembly & Recreational | Museums, cultural campuses, and civic parks |
| Institutional & Civic | Transportation & Infrastructure | High-accessibility civic, hospital, and university transit nodes |
| Assembly & Recreational | Transportation & Infrastructure | Stadium/arena transit hubs and waterfront terminals |
| Industrial & Logistics | Transportation & Infrastructure | Intermodal freight/logistics hubs and rail-highway distribution parks |
