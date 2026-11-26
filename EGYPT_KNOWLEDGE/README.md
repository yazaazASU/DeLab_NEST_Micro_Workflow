# EGYPT_KNOWLEDGE — Regional Environment, History & Render Atlas

> **Purpose:** A standalone, NEST-ready geographic knowledge base covering all **27 Egyptian governorates** and Egypt's signature **special places** (oases, national protectorates, wetlands, mountain sanctuaries, and heritage corridors).  
> **Goal:** Give Stage B experience design (`NEST_Experience_Design.md`) and architectural rendering (`build_render_pack.py`) deep, site-true grounding in **local microclimate, geology, living ecology, history, craft, and sensory atmosphere**—written in vivid, plain-English prose.

---

## How the Atlas Is Organized (6 Macro-Regions, 27 Governorates)

| File | Macro-Region | Governorates Covered | Signature Special Places |
| :--- | :--- | :--- | :--- |
| [`01_greater_cairo_nile_core.md`](./01_greater_cairo_nile_core.md) | Greater Cairo & Urban Nile Core | Cairo, Giza, Qalyubia | Wadi Degla, Maadi Petrified Forest, Giza Plateau, Saqqara & Dahshur, Historic Cairo, Nile Islands |
| [`02_alexandria_north_coast_delta.md`](./02_alexandria_north_coast_delta.md) | Alexandria, North Coast & Nile Delta | Alexandria, Matrouh, Beheira, Kafr El-Sheikh, Damietta, Dakahlia, Gharbia, Monufia, Sharqia | Ras El-Hekma, El Alamein, Wadi El-Natrun, Rosetta (Rashid), Lake Burullus, Lake Manzala, Tanis |
| [`03_suez_canal_and_sinai.md`](./03_suez_canal_and_sinai.md) | Suez Canal & Sinai Peninsula | Port Said, Ismailia, Suez, North Sinai, South Sinai | Timsah & Bitter Lakes, Lake Bardawil & Zaranik, Saint Catherine & Mount Sinai, Ras Mohammed, Nabq, Dahab, Nuweiba & Taba |
| [`04_red_sea_and_eastern_desert.md`](./04_red_sea_and_eastern_desert.md) | Red Sea & Eastern Desert | Red Sea | Galala Plateau, Hurghada & Giftun, El Gouna, Safaga, El-Quseir, Marsa Alam, Wadi El-Gemal, Gebel Elba |
| [`05_western_desert_and_oases.md`](./05_western_desert_and_oases.md) | Western Desert & Oases | New Valley (El Wadi El Gedid), Fayoum, Beni Suef, Minya | Siwa Oasis, Bahariya & Black Desert, Farafra & White Desert, Dakhla, Kharga, Gilf Kebir, Lake Qarun, Wadi El-Rayan, Wadi El-Hitan, Tuna El-Gebel |
| [`06_upper_egypt_and_nubia.md`](./06_upper_egypt_and_nubia.md) | Upper Egypt & Nubia | Assiut, Sohag, Qena, Luxor, Aswan | Abydos, Dendera, Luxor East & West Banks, Gebel El-Silsila, First Cataract & Elephantine Island, Abu Simbel & Lake Nasser, Wadi Allaqi |
| [`egypt_index.json`](./egypt_index.json) | Machine-Readable Lookup | All 27 Governorates + Special Places | Fast JSON mapping of climate, prevailing wind, local materials, nature hero, and render lighting cues |

---

## Using This in NEST Workflows

1. **Before Stage B Seed Authoring:** Look up the plot's governorate and nearest special place in `egypt_index.json` and read its regional file. Pull **one living natural hero**, **one authentic local material/craft**, and **two sensory render cues** (light, wind, color, sound) into `experience_arc`.
2. **During Render Pack Generation (`build_render_pack.py`):** Use the **Render & Experience Cues** section to lock sky color, sun angle, haze/mist, local stone/earth hues, and native plants—never generic palms or generic glass boxes.
3. **Writing Style:** Every entry follows a **6-part plain-English template**:
   - *Environment & Microclimate*
   - *Geology & Local Materials*
   - *Ecology & Living Hero*
   - *History & Cultural Craft*
   - *Notable Facts & Hidden Stories*
   - *Render & Experience Cues*
