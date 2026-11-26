# NEST + 3 Engines

**NEST** is an autonomous, Experience-First spatial evaluation and architectural synthesis system for Egyptian 5×5 km GIS plots. It coordinates **3 spatial lenses**—**Crystals** (Development), **Cells** (Adaptation), and **Corals** (Coordination)—across 6 Nature-First Spatial Forces to synthesize distributed, nature-celebrating project constellations (`50–70 feddans`).

## Repository Structure

- `run_nest_pipeline.py` — End-to-end orchestrator (`Stage A → Terrain Gate → Pre-Render Gate → Dashboard → Render Pack`).
- `run_3_engines.py` & `heatmap_engine.py` — Stage A GIS ingestion (`.gpkg` / `.geojson`), 50 m × 50 m spatial force scoring, synergy cliques, and `stage_a_summary.json` export.
- `dashboard_3engines_view.py` — Synchronized 4-panel **3-Engine Analysis Maps** view (*Crystals, Cells, Corals, Combined Result*) with floating legends and cell-click inspection drawer.
- `terrain_intelligence.py` & `raster_ground_truth.py` — DEM relief & native raster ground-truth checks.
- `stage_b_builder.py` — Expands compact Stage B seeds (`experience_arc.journey[]`, distributed constellations, landscape zones) into reconciled `stage_b_projects.json`.
- `build_nest_dashboard.py` — Generates the interactive **NEST Story Mode** dashboard (`nest_dashboard.html`).
- `stage_c_skills.py` — Generates site-grounded Stage C JSON design skills (`skills/`).
- `build_portfolio_dashboard.py` — Aggregates multiple plot runs into a portfolio view.
- `GENERAL_KNOWLEDGE/` — Governing specs (`WORKFLOW.md`, `nest_workflow.md`, `NEST_Experience_Design.md`, `STAGE_B_QUICKREF.md`, `*_nature_forces.md`, `architectural_render_skill/`).
- `UI Handover/` — Brand design tokens and official NEST + DeLab logos.
- `archive/` — Legacy/archived 3D Rhino massing & floor-plate slicing scripts (`rhino_massing_engine.py`, `floor_plate_slicer.py`).

## Quickstart (Running on a GIS Plot Folder)

1. **Install Python dependencies** (Python 3.10+):
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Stage A on a GIS plot folder** (containing `boundary.geojson` + `.gpkg` or `*_all_layers.geojson`):
   ```bash
   python run_nest_pipeline.py --data-dir "<path_to_plot_folder>" --out-dir "Outputs/My_Plot" --plot-title "My Plot"
   ```

3. **Expand Stage B seeds & build the Experience-First dashboard + render pack:**
   ```bash
   python stage_b_builder.py --run-dir "Outputs/My_Plot" --seeds-dir "Outputs/My_Plot/intermediates/seeds"
   python run_nest_pipeline.py --data-dir "<path_to_plot_folder>" --out-dir "Outputs/My_Plot" --plot-title "My Plot" --skip-stage-a
   ```

4. **Generate Stage C design skills (optional):**
   ```bash
   python stage_c_skills.py --run-dir "Outputs/My_Plot" --all
   ```
