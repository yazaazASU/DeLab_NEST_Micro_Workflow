---
name: architectural-conceptual-render
description: >-
  Build a satellite-locked architectural render pack and hand the user a single-shot
  copy-paste ChatGPT batch prompt to generate photorealistic editorial aerial & hero
  architectural renders (ArchDaily / Dezeen / MIR / Luxigon quality) with strict
  GIS/site-reality landscape grounding. Never auto-invokes image-generator unless
  explicitly requested by the user.
---

# Architectural Conceptual Render

Produces satellite-locked **render packs** and a **single-shot copy-paste ChatGPT batch prompt** by default—so the user can generate photorealistic, editorial-grade **aerial & close hero architectural conceptual renders** directly in ChatGPT while preserving authentic topography, hydrology, massing strategy, roofscape, and surrounding fabric.

> **Project-Files Location:** This skill runs directly out of `GENERAL_KNOWLEDGE/architectural_render_skill/` (mirrored in `.agents/skills/architectural-conceptual-render/` for automatic agent discovery).

**Core Principles:**
- **Default Engine (ChatGPT Handoff — Zero Auto `image-generator` Calls)**: Always generate the render pack first (`renders/render_pack/` via `build_render_pack.py`), then **prompt the user in chat with ONE single-shot copy-paste ChatGPT batch prompt** (`CHATGPT_RENDER_PROMPT.md`) plus the exact list of `site_<N>/satellite_lock.png` files to attach. Do **not** invoke the built-in `image-generator` subagent automatically—only use `image-generator` if the user explicitly asks for in-app generation.
- **Aesthetic**: Photorealistic architectural editorial only (*ArchDaily / Dezeen / MIR / Luxigon* quality)—restrained composition, authentic materials, natural atmosphere, zero CGI clichés.
- **Site-Reality Honesty (Zero Landscape Hallucinations)**: Every render prompt **must** match the real topography, hydrology, vegetation density, and surrounding urban/rural fabric of the actual GIS site. Never invent lakes, turquoise ponds, waterfalls, cliffs, mountains, or lush European parkland on flat alluvial plains or arid desert sites.
- **Default Views**: 2 shots per site — Whole-Site Aerial (`renders/site_<N>.jpg`, ~40–45°) locked to `site_<N>/satellite_lock.png` + Close Hero Experience (`renders/site_<N>_hero.jpg`) carrying over the exact same architecture and materials.

---

## Workflow

### Step 1: Inspect Any Visual & GIS Inputs
Before writing a single word of the prompt, inspect all available visual and geographic context:
- **User visuals** (sketches, massing/viewport screenshots, site plans, site photos, moodboards): inspect with `read_file`.
- **GIS / Satellite Site Context** (for NEST / site-based runs): read `*_site_context.md` and run `build_render_pack.py` to export clean `16:9` **satellite lock crops** (`site_<N>/satellite_lock.png`) for every site.
- **Regional Knowledge Grounding (`EGYPT_KNOWLEDGE/`)**: for Egyptian plots, look up the plot's governorate and nearest special place in `EGYPT_KNOWLEDGE/egypt_index.json` + its regional `.md` atlas to pull authentic local stone/earth hues, native vegetation, prevailing wind/mist cues, and regional lighting—while strictly obeying the Site-Reality Honesty rule above (never invent landforms or water absent from the satellite crop).

### Step 2: Structured Intake Checklist (Required Before Prompting)
Lock in 5 items (for autonomous NEST runs, self-answer all 5 from `*_site_context.md`, GIS layers, and `stage_b_projects.json`; for interactive single-project runs, use `ask_question` for any missing items):

1. **Site Reality Lock (Mandatory GIS/Context Grounding)**:
   - **True Topography**: Exact relief (e.g., *strictly flat Nile alluvial plain, 0–2% slope* vs *arid gravel wadi bed* vs *rocky ridge*).
   - **True Hydrology**: Exact real water edges (e.g., *Nile River along northeast edge only* or *bone-dry seasonal desert wadi — zero standing water*).
   - **Cardinal Surrounding Fabric**: What actually borders the site on N/S/E/W (e.g., *dense 3–5 story brick/concrete urban blocks to the west, flat rectangular farmland to the south/east*).
   - **Explicit Forbidden Landscape Features**: Concrete negative list of features that **must not appear** (e.g., *no hills, no cliffs, no mountains, no interior ponds/lagoons/lakes, no waterfalls, no lush tropical/European lawns*).
2. **Material Palette & Architectural Character**: Primary envelope materials (e.g., board-formed concrete, stacked local Egyptian limestone, rammed earth, oxidized bronze, warm plaster, low-iron glazing) and overall formal language.
3. **Time of Day / Lighting Mode** *(Default for NEST Render Pack: Golden Hour late-afternoon sunlight; for standalone interactive runs: Overcast / Soft Diffused Daylight or user choice)*.
4. **Aerial Camera Angle & Framing** *(Default: Classic Hero Aerial ~40–45° + Close Hero Experience)*:
   - `Classic Hero Aerial (~40–45°)` *(Default — balanced massing height + site footprint readability)*
   - `Low Oblique Aerial (~25–35°)`
   - `High Context Aerial (~55–65°)`
5. **De-Metaphorized Architectural Translation**: Strip poetic project titles of landscape trigger words before prompting (e.g., translate *"Cooling-Hill"* → *"stepped earth-bermed plinth on a dead-flat plain"*; *"Oasis"* → *"shaded courtyard with sparse native date palms and dry stone paving"*).

### Step 3: Generate the Self-Contained Render Pack (DEFAULT)
For NEST runs, run:
```bash
python GENERAL_KNOWLEDGE/architectural_render_skill/build_render_pack.py --run-dir <run_output_dir>
```
This builds `<run_output_dir>/renders/render_pack/` (+ `renders/render_pack.zip`) containing:
- `site_<1..K>/satellite_lock.png` (`16:9` Esri World Imagery crop + dashed site boundary + North arrow)
- `site_<1..K>/prompt.md` (individual aerial + hero prompt brief per site)
- `render_jobs.json` (structured 2-shot-per-site job queue)
- **`CHATGPT_RENDER_PROMPT.md`** (**Default deliverable**: single-shot ChatGPT batch prompt + upload checklist)
- `AGENT_INSTRUCTIONS.md`

For standalone (non-NEST) render requests, read [editorial-prompt-craft.md](./references/editorial-prompt-craft.md) and compose the equivalent single-shot ChatGPT prompt directly.

### Step 4: Prompt the User with the Single-Shot ChatGPT Batch Prompt (DEFAULT)
Immediately after generating the render pack, **always** present the ChatGPT handoff directly in your response:
1. List the exact satellite lock images to upload to ChatGPT in one batch (`site_1/satellite_lock.png` .. `site_K/satellite_lock.png`) with clickable `file://` paths to `<run_output_dir>/renders/render_pack/`.
2. Paste the **entire single-shot batch prompt** from `CHATGPT_RENDER_PROMPT.md` inside **ONE single copy-paste fenced code block** so the user can copy it in one click, paste it into ChatGPT alongside the attached satellite locks, and let ChatGPT generate all renders sequentially (`Job 1` → `Job 2K`).
3. Tell the user the exact save paths (`<run_output_dir>/renders/site_<N>.jpg` and `site_<N>_hero.jpg`) and the 1-line dashboard rebuild command (`python build_nest_dashboard.py --run-dir "<run_dir>" --plot-title "<plot_title>"`).

### Step 5: Optional In-App `image-generator` Mode (Explicit User Request Only)
Only if the user **explicitly asks** to run the built-in `image-generator` instead of ChatGPT:
1. Invoke `image-generator` following `render_jobs.json` and save to each job's `output_file`.
2. Inspect each result via `read_file` against all 6 checks in [qc-checklist.md](./references/qc-checklist.md) (max 1 auto-fix pass).
3. If `image-generator` hits any quota/usage limit, stop immediately and return to **Step 4** (deliver `CHATGPT_RENDER_PROMPT.md` in one fenced code block).

### Step 6: Optional Post-ChatGPT Visual QC
If the user saves ChatGPT's renders to `renders/site_<N>.jpg` & `renders/site_<N>_hero.jpg` and asks for verification, inspect each render side-by-side with `site_<N>/satellite_lock.png` using [qc-checklist.md](./references/qc-checklist.md) and flag any geographic or architectural drift with a targeted one-line ChatGPT fix prompt.
