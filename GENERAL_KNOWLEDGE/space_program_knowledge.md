# Space Program Knowledge (Plot-Agnostic)

This knowledge base defines universal architectural programming principles and machine-readable **Net Space Program Templates** (with generic activities and operating-hour profiles) for both the **6 NEST Nature-First Spatial Forces** (Section 7 — active Stage A & Stage B default) and legacy urban typologies (Section 6). Plot-specific demographics and climate rhythms live in `<plot>_site_context.md`.

> **How It Connects:** `heatmap_engine.py` and `run_3_engines.py` read **Efficiency Ratios (NSF/GSF)** from [`building_typologies.md`](./building_typologies.md), **Net Space Templates** from Section 7 (and Section 6) below, and **Plot Demographics** from the active `*_site_context.md` file. Gross share for each space is computed as:
> $$\text{Gross Share (\%)} = \text{Force/Typology Weight (\%)} \times \text{Net Share (\%)} \times \text{Efficiency Ratio}$$
> The remaining $(1 - \text{Efficiency Ratio})$ is explicitly allocated to **Circulation, Cores & MEP (Tare)**.

---

## 1. Physical Context & Site Drivers
* **Frontage Hierarchy:** Distinguish primary public street frontages (high visibility, pedestrian/transit arrival, retail, drop-off) from quiet secondary streets (private residential lobbies) and rear service alleys (loading, waste, deliveries).
* **Microclimate & Orientation:** Align living, working, and assembly spaces to capture favorable solar exposure, prevailing breezes, and natural views (waterfronts, parks), while buffering noisy arterials, railways, or industrial edges with service cores or solid massing.

## 2. Users, Occupancy & Time-of-Day Synergy
* **User Groups:** Account for distinct user cohorts—residents, office/civic staff, shoppers, visitors, patients, or commuters—and design for **peak vs. average** occupancy.
* **Time-of-Day Overlap:** In Mixed-Use buildings, pair **daytime anchors** (offices, clinics, retail) with **evening/nighttime anchors** (residential, dining, entertainment) so shared plazas, parking, and transit frontage stay active around the clock.

## 3. Net-to-Gross Efficiency (NSF vs. GSF)
* **Net Assignable Area (NSF):** Usable rooms and functional zones that directly serve the building's program.
* **Non-Assignable / Tare Area:** Horizontal circulation (corridors, lobbies), vertical circulation (stairs, elevators), structural walls, and MEP/utility rooms.
* **Efficiency Ratio ($\text{NSF} / \text{GSF}$):** Defined per typology in `building_typologies.md`. Single-use buildings with simple layouts achieve higher efficiency (e.g., Industrial `88%`, Residential `80%`), while Mixed-Use (`72%`) and public/civic buildings (`70%–72%`) require lower efficiency due to separated lobbies, wider public concourses, and dedicated service cores.

## 4. Adjacency, Privacy & Vertical Stacking
* **Public → Semi-Public → Private Gradient:** Never allow high-turnover public crowds or delivery/loading flows to cross private residential lobbies or sensitive institutional zones.
* **Vertical Stacking Strategy:**
  * **Ground Level:** High-turnover public uses, street-front retail, venue foyers, transit concourses, and isolated rear loading bays.
  * **Podium / Transition Levels:** Offices, co-working, institutional/civic suites, or recreational halls that absorb daytime energy and buffer upper floors.
  * **Upper Levels:** Quiet, daylight- and view-dependent spaces (residential units, lounges, rooftop terraces).
* **Acoustic & Odor Isolation:** Separate noisy assembly halls, restaurants, and loading docks from quiet living and study zones using acoustic buffers or intermediate podium levels.

## 5. Phasing, Flexibility & Viability
* **Revenue vs. Support Balance:** Maintain a clear ratio between core revenue/mission-driving spaces and shared amenities or back-of-house support.
* **Long-Term Adaptability:** Favor modular, open-plan podium zones that can adapt between retail, office, or civic uses as neighborhood demand evolves.

---

## 6. Net Space Program Templates (Machine-Readable)
*Each typology's Net Assignable spaces sum to **100%** of its Net Area (before applying the Efficiency Ratio from `building_typologies.md`).*

### Template: Residential
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Living Units (Family Apartments) | 82 | Upper / Quiet | Daily family living, sleeping, study, home dining | 18:00–08:00 |
| Resident Lobby & Mailroom | 9 | Ground (Separated) | Secure arrival, parcel drop-off, neighbor greeting | 07:00–22:00 |
| Resident Lounge, Terrace & Co-Living | 9 | Upper / Podium Roof | Evening socializing, children's play, shaded roof leisure | 17:00–23:00 |

### Template: Commercial & Mercantile
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Street-Front Retail, Cafés & Showrooms | 55 | Ground / Street Edge | Shopping, casual dining, street-level social gathering | 10:00–23:30 |
| Offices & Co-Working Suites | 34 | Lower–Mid Podium | Desk work, client meetings, coworking, workshops | 08:30–17:30 |
| Public Concourse & Drop-Off | 11 | Ground | Pedestrian flow, transit transfer, shaded seating | 08:00–23:00 |

### Template: Institutional & Civic
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Primary Program (Clinics / Classrooms / Civic Hall) | 65 | Lower–Mid Levels | Outpatient care, classes, youth training, civic services | 08:00–16:00 |
| Public Atrium & Reception | 18 | Ground | Waiting, information desk, community noticeboard | 08:00–18:00 |
| Admin, Staff & Support Suites | 17 | Mid Levels | Administration, records, staff prep & breakrooms | 08:00–16:00 |

### Template: Industrial & Logistics
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Production / Warehouse / Storage Bays | 70 | Ground (High Bay) | Light manufacturing, cold storage, sorting & packing | 06:00–18:00 |
| Loading Docks & Marshaling Apron | 18 | Ground Perimeter | Truck staging, freight transfer, dispatch | 05:00–15:00 |
| Operations & QC Offices | 12 | Mezzanine / Front | Inventory control, quality lab, logistics dispatch | 07:00–17:00 |

### Template: Assembly & Recreational
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Main Venue / Event Hall / Fitness & Leisure | 61 | Podium / Anchor | Cultural events, indoor sports, youth workshops, screenings | 16:00–23:30 |
| Crowd Foyer, Ticketing & Dispersion Plaza | 21 | Ground | Evening promenade, markets, event arrival/exit | 17:00–00:00 |
| Hospitality, F&B & Visitor Support | 18 | Ground / Podium | Cafés, family seating, refreshments, restrooms | 16:00–00:00 |

### Template: Transportation & Infrastructure
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Transit Concourse / Interchange Bays | 57 | Ground | Bus/microbus boarding, pedestrian transfer, bike hubs | 06:30–22:00 |
| Ticketing, Waiting & Commuter Services | 23 | Ground / Mezzanine | Shaded waiting, kiosks, commuter amenities | 06:30–22:00 |
| Operations, Control & Utility Plant | 20 | Service / Roof | Solar/microgrid inverter room, transit dispatch, MEP | 24/7 |

---

## 7. NEST Nature-First Spatial Force Program Templates (Machine-Readable)

### Template: Hydrology & Waterfront
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Waterfront Promenade, Piers & Shaded Terraces | 48 | Shoreline / Micro-Piles | Evaporative-cooled public boardwalk, electric boat docking | 06:00–22:00 |
| Hydro-Harvesting, Filtration & Limnology Hall | 32 | Lower Plinth / Cistern | Water treatment, reed bio-filtration, aquaculture/hydro labs | 24/7 |
| Aquatic Ecology Gallery & Overlook Forum | 20 | Upper Terrace | Exhibitions, watershed monitoring, community gathering | 08:00–21:00 |

### Template: Solar & Climate Intensity
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Climatic Mega-Canopy & Shaded Civic Canyon | 46 | Ground / Canopy | 10–12°C cooler shaded outdoor commons, markets, events | 07:00–23:00 |
| Earth-Sheltered Thermal Sanctuary & Labs | 34 | Subterranean / Bermed | Passive-cooled research, wellness, or cold-chain storage | 24/7 |
| Agrivoltaic / Solar Microgrid & Energy Hall | 20 | Roof / Array Deck | Clean power generation, battery storage, EV/boat charging | 24/7 |

### Template: Biodiversity & Ecology
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Shade-Mesh Botanical Conservatory & Seed Bank | 45 | Sunken Crater / Dome | Native arid-flora propagation, genetic seed banking, R&D | 07:00–19:00 |
| Habitat Restoration Nursery & Field Station | 33 | Terraced Landscape | Wildlife/avian monitoring, wetland & desert revegetation | 06:00–18:00 |
| Eco-Interpretation Trailhead & Bird-Blind Deck | 22 | Elevated Boardwalk | Low-impact nature observation, eco-education tours | 05:30–20:00 |

### Template: Heritage & Culture Gravity
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Earth-Sheltered Cultural Forum & Exhibition Hall | 46 | Low-Profile Plinth | Heritage interpretation, sun-festival / astronomical events | 08:00–22:00 |
| Living Craft Atelier, Culinary & Community Souq | 32 | Shaded Courtyard | Local artisan workshops, traditional gastronomy, trade | 09:00–23:00 |
| Sanctuary Eco-Lodge & Stargazing Terraces | 22 | Stepped Contour | Low-glare overnight heritage & dark-sky hospitality | 24/7 |

### Template: Civic & Service Deficit
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Community Health, Tele-Medicine & Rehab Wing | 44 | Ground / Bermed | Outpatient diagnostics, desert medicine, emergency care | 07:00–20:00 |
| Regional Youth STEM Academy & Fab-Lab | 36 | Mid Podium / Court | Technical training, digital classrooms, library commons | 07:30–18:00 |
| Shaded Evening Civic Amphitheater & Commons | 20 | Sunken Oasis Court | Community assemblies, evening screenings, youth sports | 17:00–23:00 |

### Template: Corridor & Network Connectivity
| Space / Zone | Net Share (%) | Vertical Stacking Zone | Typical Activities | Peak Hours |
| :--- | :---: | :--- | :--- | :--- |
| Multi-Modal Eco-Port & Solar Transit Concourse | 48 | Waterfront / Quay | Electric ferry & bus interchange, visitor arrival gateway | 05:30–23:00 |
| Zero-Carbon Cold-Chain & Regional Trade Hall | 32 | Arterial Apron | Solar-cooled agri/fisheries logistics, cooperative exchange | 24/7 |
| Shared Mobility Hub & Shaded Transfer Plaza | 20 | Ground Forecourt | E-shuttle charging, pedestrian spine, wayfinding pavilion | 06:00–23:00 |

