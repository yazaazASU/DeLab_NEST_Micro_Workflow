# NEST + 3 Engines

**NEST** is an autonomous, Experience-First spatial evaluation and architectural synthesis system for Egyptian 5×5 km GIS plots. It coordinates **3 spatial lenses**—**Crystals** (Development), **Cells** (Adaptation), and **Corals** (Coordination)—across 6 Nature-First Spatial Forces to synthesize distributed, nature-celebrating project constellations (`50–70 feddans`).

---

## Prerequisites & Input Plot Format

- **Runtime:** Python 3.10+ (`pip install -r requirements.txt`) and **Node.js** (`node --check` validates generated dashboard JS).
- **Input GIS Plot Folder:** Expects `<PLOT>.gpkg`, `boundary.geojson`, `Layer export inventory.csv`, and `rasters/L###_*.tif` (10 m ESA WorldCover, 10 m GHSL Built, Copernicus DEM).

---

## 3-Phase Agent Workflow

### Phase 1 — Spatial Evaluation & Site Context (Stage A)
Run the pipeline on a GIS plot folder. Stage A fuses 10 m built-up rasters and OSM/GIS layers, carves non-overlapping street- and terrain-snapped sites, and pauses cleanly after writing `intermediates/agent_site_context.md`:

```bash
python run_nest_pipeline.py --data-dir "<PLOT_DIR>" --out-dir "Outputs/<PLOT_NAME>" --plot-title "<PLOT_NAME>"
```

### Phase 2 — Agent Seed Authoring & Full Build (Stage B → Dashboard → Render Pack)
1. Read `Outputs/<PLOT_NAME>/intermediates/agent_site_context.md` (and relevant regional briefs in [`EGYPT_KNOWLEDGE/`](EGYPT_KNOWLEDGE/)).
2. Author 5 bespoke, site-specific architectural seeds in `Outputs/<PLOT_NAME>/intermediates/seeds/site_1_seed.json`..`site_5_seed.json` (see schema in [`GENERAL_KNOWLEDGE/STAGE_B_QUICKREF.md`](GENERAL_KNOWLEDGE/STAGE_B_QUICKREF.md)).
3. Re-run with `--skip-stage-a` to execute **Stage B → DEM Gate → Pre-Render Gate → `nest_dashboard.html` → `renders/render_pack/`**:

```bash
python run_nest_pipeline.py --data-dir "<PLOT_DIR>" --out-dir "Outputs/<PLOT_NAME>" --plot-title "<PLOT_NAME>" --skip-stage-a
```

### Phase 3 — Visual Render Pack & Moment Storyboard
Follow `Outputs/<PLOT_NAME>/renders/README.md` and `renders/render_pack/render_jobs.json` (`aerial`, `hero`, and `moment_1..N` jobs grouped by `chat_group`), then rebuild the dashboard so saved renders appear in `nest_dashboard.html`:

```bash
python build_nest_dashboard.py --run-dir "Outputs/<PLOT_NAME>" --plot-title "<PLOT_NAME>"
```

---

## Repository Structure

- `run_nest_pipeline.py` — End-to-end orchestrator (`Stage A → Agent Seed Gate → Stage B → DEM Gate → Pre-Render Gate → Dashboard → Render Pack`).
- `run_3_engines.py` & `heatmap_engine.py` — Stage A `.gpkg` + 10 m raster built-up fusion, 50 m × 50 m force scoring, and `stage_a_summary.json`.
- `dashboard_3engines_view.py` — Synchronized 4-panel **3-Engine Analysis Maps** view (*Crystals, Cells, Corals, Combined Result*).
- `terrain_intelligence.py` & `raster_ground_truth.py` — Copernicus DEM relief gate & 10 m WorldCover/GHSL raster ground-truth reader.
- `stage_b_builder.py` — Expands agent-authored Stage B seeds into reconciled `stage_b_projects.json` and `NEST_Executive_Report.md`.
- `build_nest_dashboard.py` — Generates the interactive **NEST Story Mode** dashboard (`nest_dashboard.html`) with the **Guest Journey Storyboard**.
- `GENERAL_KNOWLEDGE/` — Governing specs ([`WORKFLOW.md`](GENERAL_KNOWLEDGE/WORKFLOW.md), [`nest_workflow.md`](GENERAL_KNOWLEDGE/nest_workflow.md), [`NEST_Experience_Design.md`](GENERAL_KNOWLEDGE/NEST_Experience_Design.md), [`STAGE_B_QUICKREF.md`](GENERAL_KNOWLEDGE/STAGE_B_QUICKREF.md), [`architectural_render_skill/`](GENERAL_KNOWLEDGE/architectural_render_skill/SKILL.md)).
- `EGYPT_KNOWLEDGE/` — Regional architectural, climate, and material briefs across Egypt.
- `UI Handover/` — Brand design tokens, fonts, and official NEST + DeLab logos.
