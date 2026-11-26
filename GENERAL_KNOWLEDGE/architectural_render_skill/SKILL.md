---
name: architectural-conceptual-render
description: >-
  Generate photorealistic editorial aerial architectural conceptual renders
  (ArchDaily / Dezeen / MIR / Luxigon quality) directly via the image-generator
  subagent from text briefs, sketches, massing screenshots, satellite site crops,
  or moodboards—with strict GIS/site-reality landscape grounding and a
  consolidated multi-prompt fallback when image-generator usage is exhausted.
---

# Architectural Conceptual Render

Produces photorealistic, editorial-grade **aerial architectural conceptual renders** directly through the `image-generator` subagent—showing the whole project, massing strategy, roofscape, authentic site/landscape integration, and overall architectural idea.

> **Project-Files Location:** This skill runs directly out of `GENERAL_KNOWLEDGE/architectural_render_skill/` (mirrored in `.agents/skills/architectural-conceptual-render/` for automatic agent discovery).

**Core Principles:**
- **Engine**: `image-generator` subagent by default. Deliver image files directly—do **not** save standalone prompt `.txt`/`.md` files **unless** `image-generator` runs out of usage/quota (see **Step 4B: Quota/Usage Fallback**).
- **Aesthetic**: Photorealistic architectural editorial only (*ArchDaily / Dezeen / MIR / Luxigon* quality)—restrained composition, authentic materials, natural atmosphere, zero CGI clichés.
- **Site-Reality Honesty (Zero Landscape Hallucinations)**: Every render **must** match the real topography, hydrology, vegetation density, and surrounding urban/rural fabric of the actual GIS site. Never invent lakes, turquoise ponds, waterfalls, cliffs, mountains, or lush European parkland on flat alluvial plains or arid desert sites.
- **Default View**: Elevated aerial architectural perspective that clearly reads the entire project, massing hierarchy, and site parti.
- **Image-to-Render Fidelity**: Balanced conceptual translation—preserve the overall massing idea, real satellite context, footprint logic, and site organization from input visuals while freely refining facade articulation, roof details, and landscape geometry.

---

## Workflow

### Step 1: Inspect Any Visual & GIS Inputs
Before writing a single word of the prompt, inspect all available visual and geographic context:
- **User visuals** (sketches, massing/viewport screenshots, site plans, site photos, moodboards): inspect with `read_file`.
- **GIS / Satellite Site Context** (for NEST / site-based runs): read `*_site_context.md` and, whenever possible, capture/export a clean **satellite image crop** of the exact site boundary + immediate surroundings to pass to `image-generator` as a spatial/landscape anchor.
- **Regional Knowledge Grounding (`EGYPT_KNOWLEDGE/`)**: for Egyptian plots, look up the plot's governorate and nearest special place in `EGYPT_KNOWLEDGE/egypt_index.json` + its regional `.md` atlas to pull authentic local stone/earth hues, native vegetation, prevailing wind/mist cues, and regional lighting—while strictly obeying the Site-Reality Honesty rule above (never invent landforms or water absent from the satellite crop).

### Step 2: Structured Intake Checklist (Required Before Generating)
Lock in 5 items before generating (for autonomous NEST runs, self-answer all 5 from `*_site_context.md`, GIS layers, and the architectural program; for interactive runs, use `ask_question` for any missing items):

1. **Site Reality Lock (Mandatory GIS/Context Grounding)**:
   - **True Topography**: Exact relief (e.g., *strictly flat Nile alluvial plain, 0–2% slope* vs *arid gravel wadi bed* vs *rocky escarpment*).
   - **True Hydrology**: Exact real water edges (e.g., *Nile River along northeast edge only* or *bone-dry ephemeral desert wadi — zero standing or flowing water*).
   - **Cardinal Surrounding Fabric**: What actually borders the site on N/S/E/W (e.g., *dense 3–5 story Upper Egypt brick/concrete urban blocks to the west, flat rectangular farmland to the south/east*).
   - **Explicit Forbidden Landscape Features**: Concrete negative list of features that **must not appear** (e.g., *no hills, no cliffs, no mountains, no interior ponds/lagoons/lakes, no waterfalls, no lush tropical/European lawns*).
2. **Material Palette & Architectural Character**: Primary envelope materials (e.g., board-formed concrete, stacked local Sinai/Assiut limestone, rammed earth, oxidized bronze, warm plaster, low-iron glazing) and overall formal language.
3. **Time of Day / Lighting Mode** *(Default: Overcast / Soft Diffused Daylight)*:
   - `Overcast / Soft Diffused Daylight` *(Default — best for reading pure form and material honesty)*
   - `Golden Hour` *(warm low-angle sunlight, long sculptural shadows)*
   - `Blue Hour / Dusk` *(deep cool twilight sky contrasting with warm glowing interiors)*
   - `Harsh Desert / Mediterranean Sun` *(crisp high-contrast architectural shadows, bright atmospheric haze)*
   - `Rainy / Misty Atmosphere` *(damp reflective paving, soft atmospheric depth)*
4. **Aerial Camera Angle & Framing** *(Default: Classic Hero Aerial ~40–45°)*:
   - `Classic Hero Aerial (~40–45°)` *(Default — balanced massing height + site footprint readability)*
   - `Low Oblique Aerial (~25–35°)` *(emphasizes facade elevation, silhouette, and horizon while still showing the full complex)*
   - `High Context Aerial (~55–65°)` *(emphasizes masterplan geometry, roofscape, and urban/landscape integration)*
   - `Custom / Other` *(e.g., eye-level or courtyard perspective only if explicitly requested)*
5. **De-Metaphorized Architectural Translation**: Strip poetic project titles of landscape trigger words before prompting (e.g., translate *"Cooling-Hill"* → *"stepped earth-bermed architectural plinth on a dead-flat plain"*; *"Oasis"* → *"shaded courtyard with sparse native date palms and dry stone paving"*; *"Wadi Hydro-Citadel"* → *"dry stepped limestone flash-flood retention terraces in an arid gravel wadi"*).

### Step 3: Compose the Architectural Brief for `image-generator`
Before invoking `image-generator`, read [editorial-prompt-craft.md](./references/editorial-prompt-craft.md) and assemble a tightly engineered editorial brief containing:
1. **Site Reality Lock (Lead with Geography First)**: Exact topography, hydrology, cardinal context, regional flora, and explicit **FORBIDDEN** landscape features.
2. **Visual Satellite / Reference Anchor** *(when available)*: Pass the satellite site crop or massing screenshot path to `image-generator` with explicit instructions to match the real ground edges (riverbank, roads, flat terrain, adjacent urban/agricultural blocks).
3. **De-Metaphorized Massing & Site Parti**: Clear literal description of the whole project footprint, primary/secondary volumes, roofscape, and two-way nature integration mechanisms.
4. **Camera, Lens, Materials, Lighting & Entourage**: Real drone/helicopter photography framing (`16:9`, deep `f/8`–`f/11` focus, never tilt-shift blur), tactile weathered materials, realistic regional vegetation density, subtle scaled entourage, and strict anti-cliché guardrails.

### Step 4A: Generate & Save to Workspace
Invoke the `image-generator` subagent with the complete brief and instruct it to save (or copy/move the output) to:
- Standard runs: `outputs/renders/<project-slug>/<YYYYMMDD_HHMMSS>_<view-slug>.png`
- NEST autonomous runs: `<run_output_dir>/renders/site_<1..5>.jpg`
- Default aspect ratio: `16:9` widescreen.

### Step 4B: Image-Generator Usage / Quota Fallback (Mandatory Consolidated Prompt)
If `image-generator` returns a **usage limit, quota exhaustion, rate-limit, billing, or service unavailability error** (on either the first image or partway through a multi-site batch):
1. **Do NOT retry in a loop** and do **NOT** fail silently or leave the user without prompts.
2. **Immediately compile ONE single, copy-paste-ready master prompt block** that contains **every required image prompt** (all remaining ungenerated images, or all 5 sites if none succeeded), structured cleanly so the user can paste it into any external image-generation service (Midjourney, Flux, Ideogram, Gemini, ChatGPT, etc.):
   - Include a brief header listing the total image count, target filenames (e.g., `renders/site_1.jpg` .. `renders/site_5.jpg`), and required aspect ratio (`16:9 widescreen`).
   - For each image, provide a self-contained, production-ready prompt block containing: **Project Label & Target Filename**, **Site Reality Lock (Topography, Hydrology, Cardinal Context, Forbidden Features)**, **Literal Architectural Massing & Materials**, **Camera & Lighting**, and **Anti-Cliché Negative Constraints**.
3. **Deliver it in two places**:
   - Save the consolidated file to `<run_output_dir>/renders/ALL_IMAGE_PROMPTS_FALLBACK.md` (or `outputs/renders/ALL_IMAGE_PROMPTS_FALLBACK.md`).
   - Present the **entire consolidated prompt in ONE single fenced code block** directly in your response to the user so they can copy it in one click.

### Step 5: Automated Visual Quality Control (1 Auto-Fix Pass Max)
Once `image-generator` returns a saved image path, **always** inspect the generated image with `read_file` and evaluate it against all 6 critical checks in [qc-checklist.md](./references/qc-checklist.md)—including **Check #6: Geographic, Topographic & Hydrological Fidelity** (comparing the render against the real site context / satellite map):
- **Pass**: All 6 critical checks pass → present or embed the render.
- **Major Flaw Detected** (e.g., hallucinated pond/lake/waterfall, invented hills/cliffs on a flat plain, wrong climate vegetation, missing major river/urban edge, miniature tilt-shift blur, clipped massing, oversaturated HDR CGI look, or gibberish text):
  - Perform **at most 1 automatic fix pass** by re-invoking `image-generator` with targeted corrections stating the exact geographic or architectural defect to remove/fix.
  - Re-inspect with `read_file` and save the improved output.
  - *(If the fix pass hits a quota/usage error, invoke Step 4B immediately.)*

### Step 6: Present & Offer Targeted Refinements
Present the final render(s) with clickable `file://` links and a brief 2–3 bullet architectural & site-fidelity summary, then offer concise next-step iteration options (lighting mode, aerial elevation/orbit angle, material palette, or secondary perspective).
