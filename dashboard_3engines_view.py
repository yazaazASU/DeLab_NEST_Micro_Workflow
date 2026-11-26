"""
NEST 2.2 Visual 3-Engine Analysis Map View
==========================================
Generates the synchronized 3-engine Leaflet comparison dashboard (Crystals, Cells, Corals)
in the unified NEST 2.2 warm light editorial palette with:
  1. Per-Engine visual architectural header strips (Plan+Curve SVG icons + clickable rule pills)
  2. Live contextual Color Legend strip synced to Stages 1 -> 2 -> 3
  3. Live Visual Math Breakdown in the cell-click drawer:
       - Exact exclusion reason for masked cells
       - Terrain class & engine affinity multiplier strip (e.g. Dry Land · ×1.00)
       - Top GIS drivers with spatial operator badges & point contribution bars
       - Visual Synergy Balance dot-plot (Average vs Imbalance Spread Penalty -> Synergy Score)
  4. Upgraded "Visual Math & Engine Guide" modal with 3 tabs:
       - Tab 1: The 3 Engines Compared (Plan + Curve SVGs + Terrain Affinity charts)
       - Tab 2: Interactive Math Lab (live Distance slider for all 6 spatial operators + live Force Balance slider for Mean - StdDev)
       - Tab 3: Stages 1 -> 2 -> 3 Pipeline (visual score assembly & engine-specific Untapped Potential weights)
"""

from __future__ import annotations

import json


def build_3engine_dashboard(
    bounds,
    nx,
    ny,
    typ_names,
    typ_colors_rgb,
    engines_data,
    ref_buildings,
    ref_roads,
    ref_water,
    space_templates,
    eff_ratios,
    demand_per_res,
    hidden_gems,
    combined_overlays=None,
    top_sites=None,
) -> str:
    center_lat = (bounds[0][0] + bounds[1][0]) / 2
    center_lon = (bounds[0][1] + bounds[1][1]) / 2
    typ_hex = [f"rgb({r},{g},{b})" for r, g, b in typ_colors_rgb]
    all_layers = ["Best-Fit Typology", "Hidden Potential", *typ_names, "Mixed-Use (2+)", "Mixed-Use (3+)"]

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>NEST 2.2 — 3-Engine Spatial Analysis Maps</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  :root {
    --nest-paper: #F5F5F5;
    --nest-surface: #FFFAF7;
    --nest-soft: #FBEFED;
    --nest-rose: #DDA199;
    --nest-coral: #FF614C;
    --nest-coral-hi: #FF735F;
    --nest-edge: #A3473A;
    --nest-ink: #302B2A;
    --nest-muted: #625753;
    --nest-line: #D5C9C5;
    --nest-ok: #246247;
    --nest-ok-bg: #EAF5EF;
    --nest-warn: #775014;
    --nest-warn-bg: #FFF5E5;
    --nest-err: #A12B3A;
    --nest-err-bg: #FCEEF0;
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; margin: 0; font-family: 'Funnel Display', 'Segoe UI', system-ui, -apple-system, sans-serif; background: var(--nest-paper); color: var(--nest-ink); display: flex; flex-direction: column; overflow: hidden; }

  /* Topbar */
  .topbar { display: flex; flex-direction: column; gap: 7px; padding: 9px 18px; background: var(--nest-surface); color: var(--nest-ink); border-bottom: 1px solid var(--nest-line); z-index: 1001; flex: none; }
  .topbar-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap; }
  .topbar-row--story { padding-top: 7px; border-top: 1px solid #ECE2DF; gap: 10px; }
  .tb-block { display: inline-flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .tb-lbl { font-size: 10.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: var(--nest-muted); margin-right: 2px; white-space: nowrap; }
  .stage-arrow { color: var(--nest-muted); font-size: 13px; font-weight: 700; user-select: none; }
  .trace-btn { padding: 4px 10px; border: 1px solid var(--nest-line); border-radius: 7px; background: #FFFFFF; color: var(--nest-ink); font: inherit; font-size: 12px; font-weight: 700; cursor: pointer; white-space: nowrap; }
  .trace-btn:hover { background: var(--nest-soft); border-color: var(--nest-edge); }
  .trace-btn.active { border-color: var(--nest-edge); background: var(--nest-ink); color: var(--nest-surface); }
  .stage-flow { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .stage-group { display: inline-flex; align-items: center; gap: 4px; padding: 3px 6px; background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 10px; flex-wrap: wrap; }
  .stage-group.active { border-color: var(--nest-edge); background: #FFF5F2; }
  .stage-tag { display: inline-flex; align-items: center; gap: 4px; font-size: 10.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; color: var(--nest-muted); padding-right: 3px; white-space: nowrap; }
  .stage-group.active .stage-tag { color: var(--nest-edge); }
  .stage-num { display: inline-flex; align-items: center; justify-content: center; width: 16px; height: 16px; border-radius: 50%; background: rgba(48,43,42,0.10); font-size: 10px; font-weight: 800; flex: none; }
  .stage-group.active .stage-num { background: var(--nest-edge); color: #FFFFFF; }
  .layer-chip { display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; border: 1px solid transparent; border-radius: 7px; background: transparent; color: var(--nest-ink); font: inherit; font-size: 11.5px; font-weight: 700; cursor: pointer; white-space: nowrap; transition: background 120ms ease, border-color 120ms ease; }
  .layer-chip:hover { background: var(--nest-soft); border-color: #E2BEB8; }
  .layer-chip.active { background: var(--nest-coral); border-color: var(--nest-edge); color: var(--nest-ink); box-shadow: 0 1.5px 0 var(--nest-edge); }
  .layer-chip--hero { background: #FFFFFF; border: 1px solid var(--nest-line); padding: 5px 12px; border-radius: 9px; font-size: 12px; font-weight: 800; }
  .chip-dot { width: 7px; height: 7px; border-radius: 50%; flex: none; border: 1px solid rgba(48,43,42,0.22); }
  .story-explainer { display: flex; align-items: center; gap: 9px; font-size: 12.5px; line-height: 1.38; color: var(--nest-ink); flex: 1 1 380px; min-width: 0; }
  .story-explainer::before { content: ""; width: 3px; height: 18px; background: var(--nest-edge); border-radius: 2px; flex: none; }
  .story-explainer strong { color: var(--nest-edge); }
  .map-utils { display: inline-flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12px; color: var(--nest-muted); }
  .overlays-menu { position: relative; }
  .overlays-menu summary { list-style: none; display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border: 1px solid var(--nest-line); border-radius: 7px; background: #FFFFFF; color: var(--nest-ink); font-size: 12px; font-weight: 700; cursor: pointer; user-select: none; }
  .overlays-menu summary::-webkit-details-marker { display: none; }
  .overlays-popover { position: absolute; right: 0; top: calc(100% + 6px); z-index: 1400; min-width: 210px; padding: 10px 12px; background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 10px; box-shadow: 0 12px 28px rgba(48,43,42,0.16); display: flex; flex-direction: column; gap: 8px; }
  .overlays-popover label { display: flex; align-items: center; gap: 8px; font-size: 12.5px; font-weight: 600; color: var(--nest-ink); cursor: pointer; }
  .overlays-popover input[type="checkbox"] { width: 14px; height: 14px; margin: 0; accent-color: var(--nest-edge); cursor: pointer; }
  .opacity-ctrl { display: inline-flex; align-items: center; gap: 6px; font-weight: 700; }
  .opacity-ctrl input[type="range"] { width: 76px; accent-color: var(--nest-edge); cursor: pointer; }
  .fit-btn { padding: 4px 11px; border: 1px solid var(--nest-line); border-radius: 7px; background: #FFFFFF; color: var(--nest-ink); font: inherit; font-size: 12px; font-weight: 700; cursor: pointer; }
  .fit-btn:hover { background: var(--nest-soft); border-color: var(--nest-edge); }
  .guide-cta-btn { padding: 5px 12px; border: 1px solid var(--nest-edge); border-radius: 8px; background: var(--nest-soft); color: var(--nest-edge); font: inherit; font-size: 12px; font-weight: 800; cursor: pointer; display: inline-flex; align-items: center; gap: 5px; box-shadow: 0 2px 0 rgba(163,71,58,0.22); }
  .guide-cta-btn:hover { background: var(--nest-coral); color: var(--nest-ink); }

  /* 4-Column Synchronized Map Grid + Floating On-Map Legends */
  .maps-row { flex: 1; display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; padding: 8px 10px 6px; background: var(--nest-paper); min-height: 0; }
  @media (max-width: 1200px) { .maps-row { grid-template-columns: repeat(2, 1fr); } }
  .map-pane { display: flex; flex-direction: column; min-height: 0; background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 14px rgba(48,43,42,0.06); }
  .eng-hdr { display: flex; align-items: center; gap: 9px; padding: 7px 10px; background: linear-gradient(135deg, #FFFFFF, var(--nest-surface)); border-bottom: 1px solid var(--nest-line); flex: none; }
  .eng-hdr-svg { width: 38px; height: 38px; flex: none; border-radius: 8px; background: var(--nest-soft); border: 1px solid #EAD7D3; display: block; }
  .eng-hdr-meta { min-width: 0; flex: 1; }
  .eng-hdr-top { display: flex; align-items: baseline; justify-content: space-between; gap: 6px; }
  .eng-hdr-title { font-size: 12.5px; font-weight: 800; color: var(--nest-ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .eng-hdr-role { font-size: 9.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; color: var(--nest-edge); white-space: nowrap; }
  .eng-hdr-desc { font-size: 10.5px; color: var(--nest-muted); line-height: 1.28; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .eng-hdr-pills { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 4px; }
  .rule-pill { display: inline-flex; align-items: center; gap: 3px; padding: 1.5px 6.5px; border-radius: 999px; font-size: 10px; font-weight: 700; border: 1px solid var(--nest-line); background: #FFFFFF; color: var(--nest-ink); cursor: pointer; font-family: inherit; }
  .rule-pill:hover { background: var(--nest-soft); border-color: var(--nest-edge); color: var(--nest-edge); }
  .rule-pill--op { background: var(--nest-soft); border-color: #E2BEB8; color: var(--nest-edge); }
  .map-canvas-wrap { position: relative; flex: 1; min-height: 0; background: #0f172a; }
  .map-div { width: 100%; height: 100%; }
  .map-legend { position: absolute; left: 8px; bottom: 8px; z-index: 900; max-width: calc(100% - 16px); padding: 6px 8px; background: rgba(255, 250, 247, 0.94); backdrop-filter: blur(4px); border: 1px solid var(--nest-line); border-radius: 8px; box-shadow: 0 4px 12px rgba(48,43,42,0.18); font-size: 10px; color: var(--nest-ink); pointer-events: none; display: flex; flex-direction: column; gap: 4px; }
  .map-legend-title { font-weight: 800; color: var(--nest-edge); font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.04em; }
  .map-legend-ramp { width: 132px; height: 7px; border-radius: 999px; border: 1px solid rgba(48,43,42,0.2); }
  .map-legend-ticks { display: flex; justify-content: space-between; width: 132px; font-size: 9px; font-weight: 700; color: var(--nest-muted); }
  .map-legend-keys { display: flex; flex-wrap: wrap; gap: 6px; padding-top: 3px; border-top: 1px solid #EAE0DC; font-size: 9.5px; font-weight: 700; }
  .map-legend-key { display: inline-flex; align-items: center; gap: 4px; }
  .key-site { width: 11px; height: 8px; border: 1.8px dashed #FF614C; background: rgba(255,97,76,0.18); border-radius: 2px; display: inline-block; }
  .key-form { width: 11px; height: 8px; background: #302B2A; border: 1.5px solid #FFFAF7; border-radius: 2px; display: inline-block; }
  .key-pin { width: 8px; height: 8px; background: #FF614C; border: 1.5px solid #FFFAF7; border-radius: 50%; display: inline-block; }

  /* Contextual Live Color Legend Bar */
  .legend-bar { flex: none; display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 6px 16px; background: var(--nest-surface); border-top: 1px solid var(--nest-line); font-size: 11.5px; color: var(--nest-ink); flex-wrap: wrap; }
  .legend-left { display: inline-flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .legend-title { font-weight: 800; color: var(--nest-edge); font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; }
  .legend-ramp-wrap { display: inline-flex; align-items: center; gap: 7px; }
  .legend-ramp { width: 170px; height: 10px; border-radius: 999px; border: 1px solid rgba(48,43,42,0.18); }
  .legend-ticks { display: inline-flex; gap: 8px; font-size: 10.5px; color: var(--nest-muted); font-weight: 700; }
  .legend-swatches { display: inline-flex; align-items: center; gap: 9px; flex-wrap: wrap; }
  .legend-swatch { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 700; color: var(--nest-ink); }
  .legend-dot { width: 10px; height: 10px; border-radius: 3px; flex: none; border: 1px solid rgba(48,43,42,0.2); }
  .legend-hint { font-size: 11px; color: var(--nest-muted); font-weight: 600; }

  /* Unified NEST 2.2 Cell Inspector Drawer */
  .drawer { height: 420px; background: var(--nest-paper); border-top: 2px solid var(--nest-coral); display: none; flex-direction: column; z-index: 1002; flex: none; box-shadow: 0 -10px 28px rgba(48,43,42,0.12); }
  .drawer-hdr { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 7px 16px; background: var(--nest-surface); border-bottom: 1px solid var(--nest-line); font-size: 12px; flex-wrap: wrap; }
  .drawer-title { color: var(--nest-ink); font-size: 12.5px; }
  .drawer-ctrl { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .d-btn { padding: 4px 9px; border: 1px solid var(--nest-line); border-radius: 7px; background: #FFFFFF; color: var(--nest-ink); font: inherit; font-size: 11px; font-weight: 700; cursor: pointer; }
  .d-btn:hover { background: var(--nest-soft); border-color: var(--nest-edge); }
  .d-btn.active { background: var(--nest-coral); border-color: var(--nest-edge); color: var(--nest-ink); box-shadow: 0 2px 0 var(--nest-edge); }
  .d-sep { color: var(--nest-line); font-weight: 700; }
  .close-btn { background: var(--nest-ink); border: 1px solid var(--nest-ink); color: var(--nest-surface); border-radius: 7px; padding: 4px 10px; cursor: pointer; font: inherit; font-size: 11px; font-weight: 700; }
  .close-btn:hover { background: var(--nest-edge); border-color: var(--nest-edge); }
  .drawer-grid { flex: 1; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; padding: 10px 14px; overflow-y: auto; }
  .eng-card { background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 11px; padding: 10px 12px; font-size: 11.5px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
  .eng-card-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding-bottom: 6px; border-bottom: 1px solid #EFE5E2; }
  .eng-card-head h4 { margin: 0; font-size: 13px; color: var(--nest-ink); font-weight: 800; }
  .score-pills { display: inline-flex; gap: 5px; flex-wrap: wrap; }
  .sc-pill { padding: 2px 8px; border-radius: 999px; font-size: 10.5px; font-weight: 800; border: 1px solid var(--nest-line); background: var(--nest-surface); color: var(--nest-ink); }
  .sc-pill--peak { background: var(--nest-soft); border-color: var(--nest-edge); color: var(--nest-edge); }
  .sc-pill--ok { background: var(--nest-ok-bg); border-color: #9CCAB1; color: var(--nest-ok); }
  .sc-pill--warn { background: var(--nest-warn-bg); border-color: #E2BE84; color: var(--nest-warn); }
  .sc-pill--err { background: var(--nest-err-bg); border-color: #DF9CA5; color: var(--nest-err); }

  /* Visual Score Equation Strip inside Drawer */
  .eq-box { background: var(--nest-surface); border: 1px solid #EADAD5; border-radius: 9px; padding: 8px 10px; display: flex; flex-direction: column; gap: 6px; }
  .eq-top { display: flex; align-items: center; justify-content: space-between; gap: 6px; flex-wrap: wrap; font-size: 10.5px; }
  .eq-lbl { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--nest-edge); }
  .aff-strip { display: flex; align-items: center; gap: 7px; font-size: 10.5px; color: var(--nest-ink); background: #FFFFFF; border: 1px solid #ECE2DF; border-radius: 7px; padding: 4px 8px; }
  .aff-bar-bg { width: 52px; height: 6px; background: #EAE0DC; border-radius: 999px; overflow: hidden; flex: none; }
  .aff-bar-fill { height: 100%; border-radius: 999px; }
  .drv-item { display: flex; flex-direction: column; gap: 3px; padding: 4px 0; border-bottom: 1px dashed #EDE3DF; }
  .drv-item:last-child { border-bottom: 0; padding-bottom: 0; }
  .drv-top { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; font-size: 11px; }
  .drv-name { flex: 1; min-width: 0; color: var(--nest-ink); font-weight: 600; line-height: 1.3; }
  .drv-pts { font-weight: 800; color: var(--nest-edge); white-space: nowrap; font-variant-numeric: tabular-nums; }
  .drv-sub { display: flex; align-items: center; gap: 7px; }
  .drv-bar-bg { flex: 1; height: 5px; background: #EAE0DC; border-radius: 999px; overflow: hidden; }
  .drv-bar-fill { height: 100%; border-radius: 999px; background: var(--nest-coral); }
  .drv-tag { font-size: 9.5px; font-weight: 700; color: var(--nest-muted); background: #FFFFFF; border: 1px solid #E5D9D5; padding: 0.5px 5.5px; border-radius: 999px; white-space: nowrap; }

  /* Synergy Balance Visual Dot-Plot */
  .syn-box { background: #FFFFFF; border: 1px solid #ECE2DF; border-radius: 9px; padding: 7px 9px; display: flex; flex-direction: column; gap: 5px; }
  .syn-row { display: flex; flex-direction: column; gap: 3px; }
  .syn-row-hdr { display: flex; justify-content: space-between; align-items: baseline; gap: 6px; font-size: 10.5px; }
  .syn-svg { width: 100%; height: 26px; display: block; }

  /* Force Bars & Program Table */
  .bar-row { display: flex; align-items: center; gap: 6px; margin: 2px 0; font-size: 10.5px; color: var(--nest-ink); }
  .bar-bg { flex: 1; height: 7px; background: #EDE5E2; border-radius: 999px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 999px; }
  .alloc-bar { display: flex; height: 9px; border-radius: 999px; overflow: hidden; margin: 4px 0; border: 1px solid rgba(48,43,42,0.12); }
  .sp-table { width: 100%; border-collapse: collapse; font-size: 10.5px; margin-top: 2px; }
  .sp-table th, .sp-table td { padding: 4px 5px; border-bottom: 1px solid #EFE5E2; text-align: left; vertical-align: top; color: var(--nest-ink); }
  .sp-table th { color: var(--nest-muted); font-weight: 800; font-size: 9.5px; text-transform: uppercase; background: var(--nest-surface); }
  .concept-box { padding: 7px 9px; background: var(--nest-soft); border-left: 3px solid var(--nest-coral); border-radius: 0 7px 7px 0; font-size: 10.5px; line-height: 1.42; color: var(--nest-ink); }
  .masked-box { padding: 12px; background: var(--nest-surface); border: 1px dashed var(--nest-rose); border-radius: 9px; color: var(--nest-muted); font-size: 11.5px; line-height: 1.48; }

  /* Hover Tooltips */
  .score-explain { display: inline-flex; align-items: baseline; gap: 2px; border-bottom: 1.5px dotted var(--nest-edge); cursor: help; border-radius: 3px; padding: 0 2px; }
  .score-explain:hover, .score-explain:focus-visible { background: var(--nest-soft); }
  #nest-score-tip { position: fixed; z-index: 3200; width: min(360px, calc(100vw - 24px)); padding: 12px 14px; background: var(--nest-surface); color: var(--nest-ink); border: 1px solid var(--nest-line); border-left: 4px solid var(--nest-coral); border-radius: 12px; box-shadow: 0 14px 36px rgba(48,43,42,0.22); pointer-events: none; opacity: 0; transform: translateY(4px); transition: opacity 140ms ease, transform 140ms ease; font-size: 12px; line-height: 1.46; }
  #nest-score-tip.visible { opacity: 1; transform: translateY(0); }
  #nest-score-tip .tip-hdr { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; margin-bottom: 5px; }
  #nest-score-tip .tip-title { font-weight: 800; font-size: 13px; color: var(--nest-ink); }
  #nest-score-tip .tip-scale { font-size: 10.5px; font-weight: 800; color: var(--nest-edge); background: var(--nest-soft); border: 1px solid var(--nest-line); padding: 1px 7px; border-radius: 999px; white-space: nowrap; }
  #nest-score-tip .tip-desc { color: var(--nest-ink); margin-bottom: 6px; }
  #nest-score-tip .tip-formula { background: #FFFFFF; border: 1px solid #ECE2DF; border-radius: 7px; padding: 6px 8px; font-size: 11px; color: var(--nest-muted); margin-bottom: 5px; }
  #nest-score-tip .tip-formula b, #nest-score-tip .tip-bands b { color: var(--nest-ink); }
  #nest-score-tip .tip-bands { font-size: 10.5px; color: var(--nest-muted); }

  /* Visual Math & Engine Guide Modal */
  .glossary-backdrop { position: fixed; inset: 0; z-index: 3100; background: rgba(48,43,42,0.58); display: none; align-items: center; justify-content: center; padding: 18px; }
  .glossary-backdrop.open { display: flex; }
  .glossary-dialog { width: min(1060px, 100%); max-height: calc(100vh - 36px); background: var(--nest-surface); border: 1px solid var(--nest-line); border-radius: 18px; box-shadow: 0 24px 60px rgba(24,18,17,0.34); display: flex; flex-direction: column; overflow: hidden; }
  .glossary-hdr { display: flex; justify-content: space-between; align-items: center; gap: 14px; padding: 13px 20px; background: var(--nest-soft); border-bottom: 1px solid var(--nest-line); flex-wrap: wrap; }
  .glossary-hdr h3 { margin: 0; font-size: 16.5px; color: var(--nest-ink); display: flex; align-items: center; gap: 10px; font-weight: 800; }
  .glossary-hdr h3::before { content: ""; width: 4px; height: 20px; background: var(--nest-coral); border-radius: 2px; }
  .guide-tabs { display: inline-flex; gap: 6px; flex-wrap: wrap; }
  .gtab-btn { padding: 6px 13px; border-radius: 8px; border: 1px solid var(--nest-line); background: #FFFFFF; color: var(--nest-ink); font: inherit; font-size: 12px; font-weight: 700; cursor: pointer; }
  .gtab-btn:hover { background: var(--nest-surface); border-color: var(--nest-edge); }
  .gtab-btn.active { background: var(--nest-coral); border-color: var(--nest-edge); color: var(--nest-ink); box-shadow: 0 2px 0 var(--nest-edge); }
  .glossary-body { padding: 18px 20px; overflow-y: auto; background: var(--nest-paper); flex: 1; }
  .guide-pane { display: none; }
  .guide-pane.active { display: block; }
  .eng-compare-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
  @media (max-width: 860px) { .eng-compare-grid { grid-template-columns: 1fr; } }
  .gloss-card { background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 13px; padding: 14px 15px; display: flex; flex-direction: column; gap: 9px; }
  .gloss-title { font-size: 14px; font-weight: 800; color: var(--nest-ink); display: flex; justify-content: space-between; align-items: center; gap: 6px; }
  .gloss-tag { font-size: 10px; font-weight: 800; color: var(--nest-edge); background: var(--nest-soft); border: 1px solid #E5C5BE; padding: 2px 8px; border-radius: 999px; white-space: nowrap; }
  .gloss-txt { font-size: 12px; line-height: 1.48; color: var(--nest-ink); margin: 0; }
  .gloss-why { font-size: 11px; line-height: 1.42; color: var(--nest-muted); background: var(--nest-surface); border-left: 3px solid var(--nest-rose); padding: 6px 9px; border-radius: 0 7px 7px 0; }
  .diag-svg { width: 100%; height: auto; display: block; background: var(--nest-surface); border: 1px solid #ECE2DF; border-radius: 10px; }
  .aff-mini-grid { display: flex; flex-direction: column; gap: 4px; font-size: 11px; }
  .aff-mini-row { display: grid; grid-template-columns: 92px 1fr 38px; align-items: center; gap: 6px; }

  /* Interactive Math Lab inside Modal */
  .lab-grid { display: grid; grid-template-columns: 1.25fr 1fr; gap: 16px; }
  @media (max-width: 860px) { .lab-grid { grid-template-columns: 1fr; } }
  .op-pills { display: flex; gap: 5px; flex-wrap: wrap; }
  .op-btn { padding: 5px 10px; border-radius: 8px; border: 1px solid var(--nest-line); background: var(--nest-surface); color: var(--nest-ink); font: inherit; font-size: 11px; font-weight: 700; cursor: pointer; }
  .op-btn:hover { border-color: var(--nest-edge); }
  .op-btn.active { background: var(--nest-ink); border-color: var(--nest-ink); color: var(--nest-surface); }
  .slider-row { display: flex; align-items: center; gap: 10px; font-size: 12px; font-weight: 700; color: var(--nest-ink); background: var(--nest-surface); border: 1px solid #ECE2DF; border-radius: 9px; padding: 8px 11px; }
  .slider-row input[type="range"] { flex: 1; accent-color: var(--nest-coral); cursor: pointer; }
  .formula-chip { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 11px; background: var(--nest-soft); border: 1px solid #E5C5BE; color: var(--nest-edge); padding: 4px 8px; border-radius: 7px; display: inline-block; }
  .preset-row { display: flex; gap: 6px; flex-wrap: wrap; }
  .preset-btn { padding: 4px 9px; border-radius: 7px; border: 1px solid var(--nest-line); background: #FFFFFF; color: var(--nest-ink); font: inherit; font-size: 11px; font-weight: 700; cursor: pointer; }
  .preset-btn:hover { background: var(--nest-soft); border-color: var(--nest-edge); }

  /* Stages Pipeline Tab */
  .pipe-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 14px; }
  @media (max-width: 860px) { .pipe-grid { grid-template-columns: 1fr; } }
  .weight-stack { display: flex; height: 22px; border-radius: 7px; overflow: hidden; border: 1px solid rgba(48,43,42,0.15); font-size: 10px; font-weight: 800; color: #FFFFFF; }
  .weight-seg { display: flex; align-items: center; justify-content: center; white-space: nowrap; overflow: hidden; padding: 0 4px; }
  .weight-leg { display: flex; gap: 8px; flex-wrap: wrap; font-size: 10.5px; color: var(--nest-muted); margin-top: 4px; }
  .weight-leg span { display: inline-flex; align-items: center; gap: 4px; }
  .weight-leg i { width: 9px; height: 9px; border-radius: 2px; display: inline-block; }
</style>
</head>
<body>
<div class="topbar">
  <div class="topbar-row">
    <div id="proposal-tracer" class="tb-block" role="group" aria-label="Trace a final NEST proposal">
      <span class="tb-lbl">Trace Proposal</span>
    </div>
    <div class="stage-flow" role="group" aria-label="NEST map view switcher">
      <button type="button" id="chip-hidden" class="layer-chip layer-chip--hero" data-layer="Hidden Potential" onclick="setLayerByStage(3, 'Hidden Potential')">★ Untapped Potential</button>
      <div id="stage-group-1" class="stage-group">
        <span class="stage-tag">Inspect Force</span>
        <div id="stage1-chips" style="display:inline-flex;gap:3px;flex-wrap:wrap"></div>
      </div>
    </div>
  </div>
  <div class="topbar-row topbar-row--story">
    <div id="layer-explainer" class="story-explainer">
      <span><strong>Stage 3 · Untapped Potential:</strong> Reveals under-built pockets where strong site forces converge — dashed outlines mark NEST's 5 shortlisted sites.</span>
    </div>
    <div class="map-utils">
      <details class="overlays-menu">
        <summary>Map Layers ▾</summary>
        <div class="overlays-popover" role="group" aria-label="Map reference overlays">
          <label><input type="checkbox" id="chk-gems" checked /> Top 5 Peak Sites per Engine</label>
          <label><input type="checkbox" id="chk-bld" checked /> Existing Buildings</label>
          <label><input type="checkbox" id="chk-rd" checked /> Roads</label>
          <label><input type="checkbox" id="chk-wat" checked /> Water &amp; Shorelines</label>
        </div>
      </details>
      <label class="opacity-ctrl" for="heatmap-opacity">
        <span>Opacity</span>
        <input id="heatmap-opacity" type="range" min="15" max="100" value="85" />
        <span id="heatmap-opacity-val" style="min-width:30px;color:var(--nest-ink)">85%</span>
      </label>
      <button type="button" class="fit-btn" onclick="resetTraceAndFit()">Fit Plot</button>
      <button type="button" class="guide-cta-btn" onclick="openScoringGuide('engines')">◈ Visual Math &amp; Engine Guide</button>
    </div>
  </div>
</div>

<div class="maps-row">
  <!-- Engine 1: Crystals -->
  <div class="map-pane">
    <div class="eng-hdr">
      <svg class="eng-hdr-svg" viewBox="0 0 40 40" aria-hidden="true">
        <circle cx="20" cy="20" r="14" fill="none" stroke="#FF614C" stroke-width="5.5" opacity="0.28"/>
        <circle cx="20" cy="20" r="14" fill="none" stroke="#A3473A" stroke-width="1.6" stroke-dasharray="2.5 2"/>
        <circle cx="20" cy="20" r="5" fill="#302B2A"/>
        <circle cx="20" cy="20" r="2" fill="#FFFAF7"/>
      </svg>
      <div class="eng-hdr-meta">
        <div class="eng-hdr-top">
          <span class="eng-hdr-title">1. Crystals · Development</span>
          <span class="eng-hdr-role">Build Around / At Landmarks</span>
        </div>
        <div class="eng-hdr-desc">Finds unbuilt plots framing landmarks, water &amp; civic anchors — around, in, or at them.</div>
        <div class="eng-hdr-pills">
          <button type="button" class="rule-pill rule-pill--op" onclick="openScoringGuide('lab','ring_decay')">◎ Framing Ring</button>
          <button type="button" class="rule-pill" onclick="openScoringGuide('engines')">Land &amp; Shore ×1.0</button>
          <button type="button" class="rule-pill" onclick="openScoringGuide('engines')">Unbuilt Plots</button>
        </div>
      </div>
    </div>
    <div class="map-canvas-wrap"><div id="map0" class="map-div"></div><div id="map-legend-0" class="map-legend"></div></div>
  </div>

  <!-- Engine 2: Cells -->
  <div class="map-pane">
    <div class="eng-hdr">
      <svg class="eng-hdr-svg" viewBox="0 0 40 40" aria-hidden="true">
        <circle cx="14" cy="20" r="12" fill="#0EA5E9" opacity="0.26"/>
        <circle cx="26" cy="20" r="12" fill="#F59E0B" opacity="0.28"/>
        <path d="M20 9.5 C23.5 14 23.5 26 20 30.5 C16.5 26 16.5 14 20 9.5 Z" fill="#FF614C" opacity="0.82"/>
        <line x1="20" y1="7" x2="20" y2="33" stroke="#A3473A" stroke-width="1.4" stroke-dasharray="2 2"/>
      </svg>
      <div class="eng-hdr-meta">
        <div class="eng-hdr-top">
          <span class="eng-hdr-title">2. Cells · Adaptation</span>
          <span class="eng-hdr-role">Adapt Existing Elements</span>
        </div>
        <div class="eng-hdr-desc">Targets shorelines, habitats, quarries, ruins &amp; climate extremes to unlock latent potential.</div>
        <div class="eng-hdr-pills">
          <button type="button" class="rule-pill rule-pill--op" onclick="openScoringGuide('lab','ecotone_gradient')">◐ Edge &amp; Hotspot</button>
          <button type="button" class="rule-pill" onclick="openScoringGuide('engines')">Host Element ×1.0</button>
          <button type="button" class="rule-pill" onclick="openScoringGuide('engines')">Outside Urban Core</button>
        </div>
      </div>
    </div>
    <div class="map-canvas-wrap"><div id="map1" class="map-div"></div><div id="map-legend-1" class="map-legend"></div></div>
  </div>

  <!-- Engine 3: Corals -->
  <div class="map-pane">
    <div class="eng-hdr">
      <svg class="eng-hdr-svg" viewBox="0 0 40 40" aria-hidden="true">
        <line x1="9" y1="20" x2="31" y2="20" stroke="#A3473A" stroke-width="2" stroke-dasharray="3 2"/>
        <ellipse cx="20" cy="20" rx="7" ry="11" fill="#FF614C" opacity="0.32"/>
        <circle cx="9" cy="20" r="4.5" fill="#302B2A"/>
        <circle cx="31" cy="20" r="4.5" fill="#246247"/>
        <circle cx="20" cy="20" r="3.2" fill="#FF614C" stroke="#A3473A" stroke-width="1.4"/>
      </svg>
      <div class="eng-hdr-meta">
        <div class="eng-hdr-top">
          <span class="eng-hdr-title">3. Corals · Coordination</span>
          <span class="eng-hdr-role">Connect &amp; Coordinate</span>
        </div>
        <div class="eng-hdr-desc">Finds midpoint seams &amp; corridors that stitch separated settlements, transit &amp; nature together.</div>
        <div class="eng-hdr-pills">
          <button type="button" class="rule-pill rule-pill--op" onclick="openScoringGuide('lab','corridor_bridge')">⇄ Midpoint Seam</button>
          <button type="button" class="rule-pill" onclick="openScoringGuide('engines')">Network &amp; Nature ×1.0</button>
          <button type="button" class="rule-pill" onclick="openScoringGuide('engines')">All Terrain</button>
        </div>
      </div>
    </div>
    <div class="map-canvas-wrap"><div id="map2" class="map-div"></div><div id="map-legend-2" class="map-legend"></div></div>
  </div>

  <!-- 4th Panel: Combined Result (Sites + Building Forms) -->
  <div class="map-pane">
    <div class="eng-hdr">
      <svg class="eng-hdr-svg" viewBox="0 0 40 40" aria-hidden="true">
        <circle cx="15" cy="17" r="9" fill="#0EA5E9" opacity="0.22"/>
        <circle cx="25" cy="17" r="9" fill="#F59E0B" opacity="0.22"/>
        <circle cx="20" cy="25" r="9" fill="#10B981" opacity="0.22"/>
        <rect x="14" y="14" width="12" height="12" rx="2.5" fill="#302B2A" stroke="#FFFAF7" stroke-width="1.5"/>
      </svg>
      <div class="eng-hdr-meta">
        <div class="eng-hdr-top">
          <span class="eng-hdr-title">4. Combined Result</span>
          <span class="eng-hdr-role">Sites &amp; Building Forms</span>
        </div>
        <div class="eng-hdr-desc">Peak score across all 3 engines with resulting building sites and architectural footprints.</div>
        <div class="eng-hdr-pills">
          <button type="button" class="rule-pill rule-pill--op" onclick="openScoringGuide('pipeline')">★ Max of 3 Engines</button>
          <button type="button" class="rule-pill" onclick="resetTraceAndFit()">Sites + Forms</button>
        </div>
      </div>
    </div>
    <div class="map-canvas-wrap"><div id="map3" class="map-div"></div><div id="map-legend-3" class="map-legend"></div></div>
  </div>
</div>

<div id="legend-bar" class="legend-bar">
  <div id="legend-content" class="legend-left"></div>
  <span class="legend-hint">Click any 50×50 m cell on any map to see its live score equation across all 3 engines</span>
</div>

<div id="drawer" class="drawer">
  <div class="drawer-hdr">
    <span id="drawer-title" class="drawer-title"><b>Selected Cell</b> — Click any cell on any map to compare all 3 engines</span>
    <div class="drawer-ctrl">
      <button class="d-btn active" id="tab-sc" onclick="setDrawerTab('scores')">Score Breakdown</button>
      <button class="d-btn" id="tab-sp" onclick="setDrawerTab('program')">Emergent Program &amp; Concept</button>
      <span class="d-sep">|</span>
      <button class="d-btn active" data-m="auto" onclick="setDrawerMode('auto', this)">Auto Balance</button>
      <button class="d-btn" data-m="single" onclick="setDrawerMode('single', this)">Single</button>
      <button class="d-btn" data-m="2+" onclick="setDrawerMode('2+', this)">2+ Pair</button>
      <button class="d-btn" data-m="3+" onclick="setDrawerMode('3+', this)">3+ Trio</button>
      <span class="d-sep">|</span>
      <span style="font-size:11px;font-weight:700;color:var(--nest-muted)">Catchment Pop:</span>
      <input id="d-pop" type="number" min="500" step="500" style="width:74px;padding:3px 6px;border-radius:6px;border:1px solid var(--nest-line);background:#FFFFFF;color:var(--nest-ink);font-size:11px;font-weight:700" oninput="updatePop(this.value)" />
      <button class="close-btn" onclick="document.getElementById('drawer').style.display='none'">Close ✕</button>
    </div>
  </div>
  <div id="drawer-grid" class="drawer-grid"></div>
</div>

<script>
const BOUNDS = __BOUNDS__;
const NX = __NX__, NY = __NY__;
const TYP_NAMES = __TYP_NAMES__;
const TYP_COLORS = __TYP_COLORS__;
const ALL_LAYERS = __ALL_LAYERS__;
const ENGINES = __ENGINES__;
const SPACE_TEMPLATES = __SPACE_TEMPLATES__;
const EFF_RATIOS = __EFF_RATIOS__;
const DEMAND_PER_RES = __DEMAND_PER_RES__;
const REF_BLD = __REF_BLD__;
const REF_RD = __REF_RD__;
const REF_WAT = __REF_WAT__;
const HIDDEN_GEMS = __HIDDEN_GEMS__;
const COMBINED_OVERLAYS = __COMBINED_OVERLAYS__;
const TOP_SITES = __TOP_SITES__;

const TERRAIN_LABELS = ['Dry Land', 'Shoreline Edge', 'Open Water'];
const OP_META = {
  ring_decay:       { icon: '◎', label: 'Ring Standoff',   tip: 'Peaks in a standoff ring around a landmark or asset (too close crowds it; too far loses sightlines).' },
  ecotone_gradient: { icon: '◐', label: 'Edge Collision',  tip: 'Peaks where two different environmental or site fields meet along a transition edge.' },
  corridor_bridge:  { icon: '⇄', label: 'Bridge Seam',     tip: 'Peaks at the balanced midpoint connecting Element A and Element B into one network.' },
  kde:              { icon: '◉', label: 'Cluster Density', tip: 'Smooth bell-curve density field turning scattered GIS points into catchments.' },
  decay:            { icon: '↘', label: 'Proximity Decay', tip: 'Scores 1.0 right beside a feature and fades smoothly with walking/access distance.' },
  inverse_decay:    { icon: '↗', label: 'Buffer Away',     tip: 'Scores higher as you move away from a constraint or disturbance.' },
  service_gap:      { icon: '⊘', label: 'Service Deficit', tip: 'High local population density minus low existing service coverage.' },
};

const maps = [0, 1, 2, 3].map(i => {
  const m = L.map('map' + i, { center: [__CENTER_LAT__, __CENTER_LON__], zoom: 13, zoomControl: i === 0 });
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    attribution: '&copy; Esri, OSM', maxZoom: 19
  }).addTo(m);
  return m;
});

// Sync pan & zoom across all 4 maps
let syncing = false;
maps.forEach((m, idx) => {
  m.on('moveend zoomend', () => {
    if (syncing) return;
    syncing = true;
    const c = m.getCenter(), z = m.getZoom();
    maps.forEach((other, j) => { if (j !== idx) other.setView(c, z, { animate: false }); });
    syncing = false;
  });
});

// Reference overlays on the 3 engine maps (0, 1, 2) — Map 4 (Combined Result) stays clean with only Heatmap + Result Sites & Building Forms
const refGroups = maps.slice(0, 3).map(m => ({
  bld: L.geoJSON(REF_BLD, { style: { color: '#94a3b8', weight: 0.7, fillOpacity: 0.35 } }).addTo(m),
  rd:  L.geoJSON(REF_RD,  { style: { color: '#cbd5e1', weight: 1.1, opacity: 0.65 } }).addTo(m),
  wat: L.geoJSON(REF_WAT, { style: { color: '#38bdf8', weight: 1.4, fillOpacity: 0.4 } }).addTo(m),
}));

document.getElementById('chk-bld').onchange = e => refGroups.forEach((g, i) => e.target.checked ? g.bld.addTo(maps[i]) : maps[i].removeLayer(g.bld));
document.getElementById('chk-rd').onchange  = e => refGroups.forEach((g, i) => e.target.checked ? g.rd.addTo(maps[i])  : maps[i].removeLayer(g.rd));
document.getElementById('chk-wat').onchange = e => refGroups.forEach((g, i) => e.target.checked ? g.wat.addTo(maps[i]) : maps[i].removeLayer(g.wat));

const gemLayers = maps.slice(0, 3).map((m, eIdx) => {
  const grp = L.layerGroup();
  (HIDDEN_GEMS[eIdx] || []).forEach(g => {
    const mk = L.circleMarker([g.lat, g.lon], {
      radius: 8, color: '#FFFAF7', weight: 2.5, fillColor: '#FF614C', fillOpacity: 0.95
    });
    mk.bindTooltip(`#${g.rank} Peak Site (${g.engine}): ${g.mix}`, { direction: 'top' });
    mk.on('click', () => inspectCell(L.latLng(g.lat, g.lon)));
    mk.addTo(grp);
  });
  return grp.addTo(m);
});
document.getElementById('chk-gems').onchange = e => gemLayers.forEach((grp, i) => e.target.checked ? grp.addTo(maps[i]) : maps[i].removeLayer(grp));

// Map 4 (Combined Result): Default to showing the 5 Result Sites + Building Forms (Stage A TOP_SITES fallback until Stage B NEST_PROJECTS loads)
const combinedResultLayer = L.layerGroup().addTo(maps[3]);
function renderCombinedStageASites() {
  if (typeof NEST_PROJECTS !== 'undefined' && Array.isArray(NEST_PROJECTS) && NEST_PROJECTS.length) return;
  combinedResultLayer.clearLayers();
  (TOP_SITES || []).forEach(s => {
    if (s.geojson) {
      const sp = L.geoJSON(s.geojson, {
        style: { color: '#FF614C', weight: 2.4, dashArray: '6 5', fillColor: '#FF614C', fillOpacity: 0.16 }
      }).bindTooltip(`<b>#${s.rank} ${s.engine} Site</b> (${s.area_feddans} feddans · ${s.score}/100)`).addTo(combinedResultLayer);
      sp.on('click', () => inspectCell(L.latLng(s.lat, s.lon)));
    }
    // Schematic building form footprint inside the site core (~110m x 70m courtyard mass)
    const dLat = 0.00050, dLon = 0.00068;
    const formPoly = L.polygon([
      [s.lat - dLat, s.lon - dLon],
      [s.lat - dLat, s.lon + dLon],
      [s.lat + dLat, s.lon + dLon],
      [s.lat + dLat, s.lon - dLon]
    ], {
      color: '#FFFAF7', weight: 1.8, fillColor: '#302B2A', fillOpacity: 0.90
    }).bindTooltip(`<b>#${s.rank} Building Zone (${s.strategy})</b>`).addTo(combinedResultLayer);
    formPoly.on('click', () => inspectCell(L.latLng(s.lat, s.lon)));
  });
}
renderCombinedStageASites();

let activeOverlays = [null, null, null, null];
let currentOpacity = 0.85;
let activeTraceRank = null;

const LAYER_EXPLANATIONS = {
  'Hidden Potential': '<strong>Stage 3 · Untapped Potential:</strong> Reveals under-built pockets where strong site forces converge — dashed outlines mark NEST\\'s 5 shortlisted sites.',
  'Best-Fit Typology': '<strong>Stage 2 · Dominant Force:</strong> Colours each 50×50 m cell by its single strongest spatial force under each engine\\'s rules.',
  'Mixed-Use (2+)': '<strong>Stage 2 · Balanced Pair (2+):</strong> Highlights cells where 2+ compatible forces are both strong and balanced (<code>Avg − Spread</code>).',
  'Mixed-Use (3+)': '<strong>Stage 2 · Balanced Trio (3+):</strong> Pinpoints rare convergence zones where 3+ compatible forces align equally — prime flagship sites.',
  'Hydrology & Waterfront': '<strong>Stage 1 · Hydrology &amp; Waterfront:</strong> Proximity, standoff, and edge interface with rivers, lakes, shorelines, and drainage.',
  'Solar & Climate Intensity': '<strong>Stage 1 · Solar &amp; Climate Intensity:</strong> Solar exposure, thermal intensity, and passive microclimate opportunity.',
  'Biodiversity & Ecology': '<strong>Stage 1 · Biodiversity &amp; Ecology:</strong> Mapped species/bird flyways (GBIF), wetlands, green patches, and ecological corridors.',
  'Heritage & Culture Gravity': '<strong>Stage 1 · Heritage &amp; Culture Gravity:</strong> Sightline buffers and cultural pull of archaeological and historic landmarks.',
  'Civic & Service Deficit': '<strong>Stage 1 · Civic &amp; Service Deficit:</strong> Underserved gaps where local population lacks nearby schools, clinics, or civic anchors.',
  'Corridor & Network Connectivity': '<strong>Stage 1 · Corridor &amp; Network Connectivity:</strong> Seams linking roads, ports, ferries, and regional transit access.',
};

const LAYER_RAMPS = {
  'Hidden Potential': { label: 'Untapped Potential (0–100)', css: 'linear-gradient(90deg, #000004, #420A68, #932667, #DD513A, #FCA50A, #FCFFA4)' },
  'Mixed-Use (2+)':   { label: 'Balanced Pair Synergy (0–100)', css: 'linear-gradient(90deg, #000004, #3B0F70, #8C2981, #DE4968, #FE9F6D, #FCFDBF)' },
  'Mixed-Use (3+)':   { label: 'Balanced Trio Synergy (0–100)', css: 'linear-gradient(90deg, #0D0887, #6A00A8, #B12A90, #E16462, #FCA636, #F0F921)' },
  'Hydrology & Waterfront':          { label: 'Hydrology Signal (0–100)', css: 'linear-gradient(90deg, #FFFFD9, #C7E9B4, #41B6C4, #225EA8, #081D58)' },
  'Solar & Climate Intensity':       { label: 'Solar & Climate Signal (0–100)', css: 'linear-gradient(90deg, #FFFFCC, #FED976, #FD8D3C, #E31A1C, #800026)' },
  'Biodiversity & Ecology':          { label: 'Biodiversity Signal (0–100)', css: 'linear-gradient(90deg, #FFFFE5, #ADDD8E, #41AB5D, #006837, #004529)' },
  'Heritage & Culture Gravity':      { label: 'Heritage Gravity (0–100)', css: 'linear-gradient(90deg, #F7F4F9, #DF65B0, #CE1256, #980043, #67001F)' },
  'Civic & Service Deficit':         { label: 'Civic Deficit (0–100)', css: 'linear-gradient(90deg, #FFF5EB, #FDAE6B, #F16913, #D94801, #7F2704)' },
  'Corridor & Network Connectivity': { label: 'Corridor Connectivity (0–100)', css: 'linear-gradient(90deg, #440154, #3B528B, #21918C, #5EC962, #FDE725)' },
};

function updateLegend(layerName) {
  const box = document.getElementById('legend-content');
  const ramp = LAYER_RAMPS[layerName] || { label: layerName + ' (0–100)', css: 'linear-gradient(90deg, #1E1B4B, #A3473A, #FF614C, #FDE047)' };
  if (box) {
    if (layerName === 'Best-Fit Typology') {
      const swatches = TYP_NAMES.map((n, i) =>
        `<span class="legend-swatch"><span class="legend-dot" style="background:${TYP_COLORS[i]}"></span>${n.split('&')[0].trim()}</span>`
      ).join('');
      box.innerHTML = `<span class="legend-title">Dominant Force:</span><div class="legend-swatches">${swatches}</div>`;
    } else {
      box.innerHTML = `
        <span class="legend-title">${ramp.label}</span>
        <div class="legend-ramp-wrap">
          <span class="legend-ticks">0 Low</span>
          <div class="legend-ramp" style="background:${ramp.css}"></div>
          <span class="legend-ticks">50 Strong · 100 Peak</span>
        </div>
      `;
    }
  }
  const hasProjects = (typeof NEST_PROJECTS !== 'undefined' && Array.isArray(NEST_PROJECTS) && NEST_PROJECTS.length > 0);
  [0, 1, 2, 3].forEach(i => {
    const ml = document.getElementById('map-legend-' + i);
    if (!ml) return;
    const keysHtml = i === 3
      ? `<div class="map-legend-keys">
           <span class="map-legend-key"><span class="key-site"></span>Result Site</span>
           <span class="map-legend-key"><span class="key-form"></span>Building Form</span>
         </div>`
      : '';
    ml.innerHTML = `
      <span class="map-legend-title">${ramp.label}</span>
      <div class="map-legend-ramp" style="background:${ramp.css}"></div>
      <div class="map-legend-ticks"><span>0 Low</span><span>50</span><span>100 Peak</span></div>
      ${keysHtml}
    `;
  });
}

function updateExplainer(htmlStr) {
  const el = document.getElementById('layer-explainer');
  if (el) el.innerHTML = '<span>' + htmlStr + '</span>';
}

let currentStageNum = 3;
let currentLayerName = 'Hidden Potential';

function setLayerByStage(stageNum, layerName) {
  if (!ENGINES[0].overlays[layerName]) return;
  currentStageNum = stageNum;
  currentLayerName = layerName;
  maps.forEach((m, i) => {
    if (activeOverlays[i]) m.removeLayer(activeOverlays[i]);
    const url = (i === 3)
      ? ((COMBINED_OVERLAYS && COMBINED_OVERLAYS[layerName]) || ENGINES[0].overlays[layerName])
      : ENGINES[i].overlays[layerName];
    if (url) activeOverlays[i] = L.imageOverlay(url, BOUNDS, { opacity: currentOpacity, interactive: false }).addTo(m);
  });
  [1, 2, 3].forEach(n => {
    const grp = document.getElementById('stage-group-' + n);
    if (grp) grp.classList.toggle('active', n === stageNum);
  });
  document.querySelectorAll('.layer-chip').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.layer === layerName);
  });
  updateLegend(layerName);
  if (!activeTraceRank) {
    updateExplainer(LAYER_EXPLANATIONS[layerName] || ('<strong>' + layerName + ':</strong> Spatial score surface across all 3 engines.'));
  }
}

function fitAllMaps() {
  maps.forEach(m => m.fitBounds(BOUNDS, { padding: [14, 14] }));
}

function resetTraceAndFit() {
  activeTraceRank = null;
  document.querySelectorAll('.trace-btn').forEach(b => b.classList.toggle('active', b.dataset.rank === 'all'));
  const drawer = document.getElementById('drawer');
  if (drawer) drawer.style.display = 'none';
  fitAllMaps();
  updateExplainer(LAYER_EXPLANATIONS[currentLayerName] || '');
}

function traceProposalOnMaps(rank) {
  if (typeof NEST_PROJECTS === 'undefined') return;
  const p = NEST_PROJECTS.find(x => x.rank === rank);
  if (!p) return;
  activeTraceRank = rank;
  document.querySelectorAll('.trace-btn').forEach(b => b.classList.toggle('active', b.dataset.rank === String(rank)));
  maps.forEach(m => {
    m.invalidateSize();
    m.setView([p.lat, p.lon], 15);
  });
  if (typeof inspectCell === 'function') inspectCell(L.latLng(p.lat, p.lon));
  updateExplainer(`<strong>Tracing Project #${p.rank} (${p.strategy}):</strong> ${p.title} — zoomed to its boundary across all 3 engines; inspect its live math breakdown below.`);
}

const opSlider = document.getElementById('heatmap-opacity');
if (opSlider) {
  opSlider.oninput = e => {
    const pct = parseInt(e.target.value, 10);
    currentOpacity = pct / 100;
    document.getElementById('heatmap-opacity-val').textContent = pct + '%';
    activeOverlays.forEach(ov => { if (ov) ov.setOpacity(currentOpacity); });
  };
}

const SHORT_FORCE_LABELS = {
  'Hydrology & Waterfront': 'Waterfront',
  'Solar & Climate Intensity': 'Solar',
  'Biodiversity & Ecology': 'Ecology',
  'Heritage & Culture Gravity': 'Heritage',
  'Civic & Service Deficit': 'Civic',
  'Corridor & Network Connectivity': 'Corridors'
};
const stage1Chips = document.getElementById('stage1-chips');
ALL_LAYERS.forEach(name => {
  if (name === 'Hidden Potential' || name === 'Best-Fit Typology' || name === 'Mixed-Use (2+)' || name === 'Mixed-Use (3+)') return;
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'layer-chip';
  btn.dataset.layer = name;
  const tIdx = TYP_NAMES.indexOf(name);
  const dot = tIdx >= 0 ? `<span class="chip-dot" style="background:${TYP_COLORS[tIdx]}"></span>` : '';
  btn.innerHTML = dot + (SHORT_FORCE_LABELS[name] || name);
  btn.title = name;
  btn.onclick = () => setLayerByStage(1, name);
  stage1Chips.appendChild(btn);
});

if (ALL_LAYERS.includes('Hidden Potential')) {
  setLayerByStage(3, 'Hidden Potential');
} else {
  const hero = document.getElementById('chip-hidden');
  if (hero) hero.style.display = 'none';
  setLayerByStage(1, TYP_NAMES[0]);
}

function initProposalTracer() {
  const tracer = document.getElementById('proposal-tracer');
  if (!tracer || tracer.dataset.ready === '1') return;
  if (typeof NEST_PROJECTS === 'undefined' || !Array.isArray(NEST_PROJECTS) || !NEST_PROJECTS.length) {
    tracer.style.display = 'none';
    return;
  }
  tracer.style.display = 'inline-flex';
  tracer.dataset.ready = '1';
  const allBtn = document.createElement('button');
  allBtn.type = 'button';
  allBtn.className = 'trace-btn active';
  allBtn.dataset.rank = 'all';
  allBtn.textContent = 'All 5';
  allBtn.onclick = resetTraceAndFit;
  tracer.appendChild(allBtn);
  NEST_PROJECTS.forEach(p => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'trace-btn';
    btn.dataset.rank = String(p.rank);
    btn.title = `#${p.rank}: ${p.title} (${p.strategy})`;
    btn.textContent = '#' + p.rank;
    btn.onclick = () => traceProposalOnMaps(p.rank);
    tracer.appendChild(btn);
  });
}
window.addEventListener('DOMContentLoaded', initProposalTracer);
window.addEventListener('load', initProposalTracer);

// Synchronized click across all 3 maps + Visual Math Inspector
let markers = [null, null, null];
let lastRow = null, lastCol = null;
let drawerTab = 'scores';
let drawerMode = 'auto';
let customPop = null;

function setDrawerTab(t) {
  drawerTab = t;
  document.getElementById('tab-sp').classList.toggle('active', t === 'program');
  document.getElementById('tab-sc').classList.toggle('active', t === 'scores');
  renderDrawer();
}

function setDrawerMode(m, btn) {
  drawerMode = m;
  document.querySelectorAll('[data-m]').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderDrawer();
}

function updatePop(v) {
  customPop = Math.max(500, parseInt(v || 15000, 10));
  renderDrawer();
}

function buildSynergyDotSvg(lbl, synScore, scores) {
  const parts = lbl.split(' + ').map(t => t.trim());
  const vals = parts.map(t => {
    const idx = TYP_NAMES.indexOf(t);
    return { name: t, idx, v: idx >= 0 ? scores[idx] : 0 };
  });
  const mean = vals.reduce((a, b) => a + b.v, 0) / Math.max(vals.length, 1);
  const xOf = v => 8 + (Math.max(0, Math.min(100, v)) / 100) * 244;
  const xMean = xOf(mean);
  const xSyn = xOf(synScore);
  const penaltyW = Math.max(0, xMean - xSyn);
  const dots = vals.map(d =>
    `<circle cx="${xOf(d.v).toFixed(1)}" cy="13" r="4.5" fill="${TYP_COLORS[d.idx] || '#302B2A'}" stroke="#FFFFFF" stroke-width="1.3"><title>${d.name}: ${d.v}</title></circle>`
  ).join('');
  return `
    <svg class="syn-svg" viewBox="0 0 260 26" aria-label="Synergy balance chart">
      <line x1="8" y1="13" x2="252" y2="13" stroke="#E5DAD6" stroke-width="4" stroke-linecap="round"/>
      <line x1="8" y1="13" x2="${xSyn.toFixed(1)}" y2="13" stroke="#FF614C" stroke-width="4" stroke-linecap="round"/>
      ${penaltyW > 2 ? `<rect x="${xSyn.toFixed(1)}" y="8" width="${penaltyW.toFixed(1)}" height="10" rx="2" fill="rgba(163,71,58,0.16)" stroke="#A3473A" stroke-width="0.9" stroke-dasharray="2 1.5"/>` : ''}
      <line x1="${xMean.toFixed(1)}" y1="4" x2="${xMean.toFixed(1)}" y2="22" stroke="#625753" stroke-width="1.4" stroke-dasharray="2 1.5"/>
      ${dots}
    </svg>
  `;
}

function buildConceptHtml(eIdx, activeTyps, topF) {
  const joined = activeTyps.join(' ').toLowerCase();
  const d0 = (topF[0] ? topF[0][0] : '').toLowerCase();
  let gesture = 'Anchors a climate-responsive, site-emergent landmark shaped directly by the cell\\'s dominant natural and regional forces.';
  if (joined.includes('hydrology') || d0.includes('water') || d0.includes('shoreline')) {
    gesture = 'Extends elevated micro-pile terraces and shaded boardwalks toward the water edge while harvesting evaporative breezes and protecting littoral habitats.';
  } else if (joined.includes('solar') || d0.includes('solar') || d0.includes('thermal')) {
    gesture = 'Spans a perforated solar-photovoltaic mega-canopy over earth-sheltered stone courts to drop ambient heat by 10–12°C while generating 100% clean power.';
  } else if (joined.includes('biodiversity') || d0.includes('gbif') || d0.includes('ecological')) {
    gesture = 'Carves earth-bermed botanical crater rings and elevated bird-blind walkways that propagate native flora and shield wildlife corridors from disturbance.';
  } else if (joined.includes('heritage') || d0.includes('unesco') || d0.includes('cultural')) {
    gesture = 'Keeps massing low and earth-sheltered in local stone to honor historic viewsheds while framing cultural forums, artisan souqs, and celestial alignments.';
  } else if (joined.includes('civic') || d0.includes('health') || d0.includes('school')) {
    gesture = 'Creates a shaded, passively ventilated civic oasis pairing regional tele-health and youth STEM classrooms with an evening community amphitheater.';
  } else if (joined.includes('corridor') || d0.includes('port') || d0.includes('road')) {
    gesture = 'Stitches fragmented transport and waterfront endpoints beneath a continuous solar-canopy concourse for electric ferries, shuttles, and cold-chain trade.';
  }

  let twoWay = '<b>Nature → Bldg:</b> Passive microclimate cooling &amp; solar harvesting · <b>Bldg → Nature:</b> Zero-discharge bio-filtration &amp; habitat restoration.';
  if (joined.includes('hydrology') && joined.includes('solar')) {
    twoWay = '<b>Nature → Bldg:</b> Water thermal mass &amp; solar irradiance run cooling/power · <b>Bldg → Nature:</b> Canopy shade cuts evaporation &amp; reed beds filter runoff.';
  } else if (joined.includes('biodiversity')) {
    twoWay = '<b>Nature → Bldg:</b> Earth thermal mass &amp; native micro-misting cut HVAC 65% · <b>Bldg → Nature:</b> Propagates native seed stock &amp; protects migratory flyways.';
  }

  const lensName = eIdx === 0 ? 'Crystals Lens (Development · Around/At POIs)' : (eIdx === 1 ? 'Cells Lens (Adaptation · Edge Transformation)' : 'Corals Lens (Coordination · Multi-Element Bridge)');
  return `
    <div class="concept-box">
      <div style="font-weight:800;color:var(--nest-edge);margin-bottom:3px">${lensName}</div>
      <div style="margin-bottom:3px"><b>Spatial Gesture:</b> ${gesture}</div>
      <div>${twoWay}</div>
    </div>
  `;
}

function renderDrawer() {
  if (lastRow === null || lastCol === null) return;
  const grid = document.getElementById('drawer-grid');
  grid.innerHTML = '';

  ENGINES.forEach((eng, eIdx) => {
    const cell = eng.lookup[lastRow * NX + lastCol];
    const card = document.createElement('div');
    card.className = 'eng-card';
    if (!cell || cell[0] === 0) {
      const reason = (cell && cell[1]) ? cell[1] : 'Spatial Mask';
      const whyTxt = eIdx === 0
        ? 'Crystals excludes road corridors and existing building footprints, while keeping open urban infill plots buildable.'
        : (eIdx === 1
            ? 'Cells excludes roads and dense active urban cores to focus adaptation on shorelines, habitats, and contextual host elements.'
            : 'Outside the active 5×5 km plot boundary.');
      card.innerHTML = `
        <div class="eng-card-head">
          <h4>${eng.title}</h4>
          <span class="sc-pill sc-pill--err">Excluded: ${reason}</span>
        </div>
        <div class="masked-box"><b>Why this cell is masked (0/100):</b><br>${whyTxt}</div>
      `;
      grid.appendChild(card);
      return;
    }

    const [_, bestIdx, scores, topF, mix2, mix2Lbl, mix3, mix3Lbl, defaultPop, isWater, hiddenSc, affMult, terrainCode, builtPct] = cell;
    const pop = customPop || defaultPop;
    if (eIdx === 0 && !customPop) document.getElementById('d-pop').value = defaultPop;
    const terrainLbl = TERRAIN_LABELS[terrainCode] || (isWater ? 'Open Water' : 'Dry Land');
    const affVal = (typeof affMult === 'number') ? affMult : 1.0;
    const affColor = affVal >= 0.9 ? 'var(--nest-ok)' : (affVal >= 0.65 ? 'var(--nest-warn)' : 'var(--nest-err)');
    const affPillCls = affVal >= 0.9 ? 'sc-pill--ok' : (affVal >= 0.65 ? 'sc-pill--warn' : 'sc-pill--err');
    const waterWarn = isWater ? `<div style="background:var(--nest-warn-bg);border:1px solid #E2BE84;color:var(--nest-warn);padding:5px 8px;border-radius:7px;font-size:10.5px"><b>⚠ Water Zone:</b> Requires non-invasive micro-piles/pontoons &amp; zero-discharge safeguards.</div>` : '';

    if (drawerTab === 'scores') {
      const RULE_HINT = {
        ring_decay: 'ring',
        ecotone_gradient: 'edge',
        corridor_bridge: 'seam',
        kde: 'cluster',
        decay: 'nearby',
        inverse_decay: 'buffer',
        service_gap: 'gap'
      };
      const maxPts = Math.max(10, ...(topF || []).map(d => Number(d[1]) || 0));
      const drvRows = (topF || []).map(d => {
        const crit = d[0], pts = d[1], meth = d[2] || 'decay', rad = d[3];
        const hint = RULE_HINT[meth] || 'rule';
        const tagTxt = rad ? `${rad} m ${hint}` : hint;
        const pct = Math.min(100, Math.round(((Number(pts) || 0) / maxPts) * 100));
        return `
          <div class="drv-item">
            <div class="drv-top">
              <span class="drv-name">${crit}</span>
              <span class="drv-pts score-explain" tabindex="0" data-score-key="driver_pts">+${pts} pts</span>
            </div>
            <div class="drv-sub">
              <div class="drv-bar-bg"><div class="drv-bar-fill" style="width:${pct}%"></div></div>
              <span class="drv-tag score-explain" tabindex="0" data-score-key="op_${meth}">${tagTxt}</span>
            </div>
          </div>
        `;
      }).join('');

      const bars = TYP_NAMES.map((n, idx) => ({ n, idx, sc: scores[idx] }))
        .sort((a, b) => b.sc - a.sc)
        .map(x => `<div class="bar-row"><span style="width:146px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:${x.idx === bestIdx ? '800' : '600'}" title="${x.n}">${x.n}</span><div class="bar-bg"><div class="bar-fill" style="width:${x.sc}%;background:${TYP_COLORS[x.idx]}"></div></div><span class="score-explain" tabindex="0" data-score-key="${x.n}" style="min-width:28px;justify-content:flex-end;font-weight:800">${x.sc}</span></div>`).join('');

      const hVal = hiddenSc !== undefined ? hiddenSc : scores[bestIdx];
      const verdictTxt = hVal >= 70 ? 'Peak Spot' : (hVal >= 45 ? 'Moderate' : 'Low');
      const verdictCls = hVal >= 70 ? 'sc-pill--ok' : (hVal >= 45 ? 'sc-pill--warn' : 'sc-pill--err');

      card.innerHTML = `
        <div class="eng-card-head">
          <h4>${eng.title}</h4>
          <div class="score-pills">
            <span class="sc-pill ${verdictCls} score-explain" tabindex="0" data-score-key="hidden">${verdictTxt} · ${hVal}/100</span>
            <span class="sc-pill ${affPillCls} score-explain" tabindex="0" data-score-key="affinity">${terrainLbl} · ×${affVal.toFixed(2)}</span>
          </div>
        </div>
        ${waterWarn}
        <div class="eq-box">
          <div class="eq-top">
            <span class="eq-lbl">Top Reasons (${TYP_NAMES[bestIdx].split('&')[0].trim()})</span>
            ${typeof builtPct === 'number' ? `<span style="font-size:10px;color:var(--nest-muted)">Built: <b>${builtPct}%</b></span>` : ''}
          </div>
          ${drvRows}
        </div>
        <div>
          <div class="eq-lbl" style="margin-bottom:4px">All 6 Forces (0–100)</div>
          ${bars}
        </div>
      `;
      grid.appendChild(card);
      return;
    }

    // Program & Concept Tab
    let activeMode = drawerMode;
    if (drawerMode === 'auto') activeMode = mix3 >= 60 ? '3+' : (mix2 >= 60 ? '2+' : 'single');
    let activeTyps = activeMode === '3+' ? mix3Lbl.split(' + ') : (activeMode === '2+' ? mix2Lbl.split(' + ') : [TYP_NAMES[bestIdx]]);
    const eff = activeTyps.length >= 2 ? (EFF_RATIOS['Mixed-Use'] || 0.74) : (EFF_RATIOS[activeTyps[0]] || 0.75);
    const totSc = activeTyps.reduce((a, t) => a + scores[TYP_NAMES.indexOf(t)], 0) || 1;
    const shares = activeTyps.map(t => {
      const w = scores[TYP_NAMES.indexOf(t)] / totSc;
      const netSqm = pop * (DEMAND_PER_RES[t] || 0.14) * w;
      return { name: t, idx: TYP_NAMES.indexOf(t), pct: Math.round(w * 1000) / 10, netSqm };
    });
    const totNet = shares.reduce((a, s) => a + s.netSqm, 0);
    const totGfa = totNet / eff;
    const tareSqm = totGfa - totNet;

    const allocBar = shares.map(s => `<div style="width:${s.pct}%;background:${TYP_COLORS[s.idx]}" title="${s.name}: ${s.pct}%"></div>`).join('');
    let rowsHtml = '';
    shares.forEach(s => {
      const tpl = SPACE_TEMPLATES[s.name] || [[`${s.name} Primary Zone`, 100, 'Site-Emergent', 'Force-driven program zone', '24/7']];
      tpl.forEach(([sp, pct, stack, act, hrs]) => {
        const sqm = Math.round(s.netSqm * (pct / 100));
        rowsHtml += `<tr><td><b>${sp}</b> <span style="font-size:9.5px;color:var(--nest-edge);font-weight:700">(${s.name.split(' ')[0]})</span><div style="font-size:9.5px;color:var(--nest-muted)">${act || ''} ${hrs ? '• ' + hrs : ''}</div></td><td style="text-align:right;white-space:nowrap"><b>${sqm.toLocaleString()} m²</b></td></tr>`;
      });
    });
    rowsHtml += `<tr><td><b>Structural Cores &amp; Circulation Tare (${(100 - eff*100).toFixed(0)}%)</b></td><td style="text-align:right;white-space:nowrap"><b>${Math.round(tareSqm).toLocaleString()} m²</b></td></tr>`;

    const landmarkEstGfa = Math.max(Math.round(totGfa), 18000);
    card.innerHTML = `
      <div class="eng-card-head">
        <h4>${eng.title}</h4>
        <span class="sc-pill">${Math.round(totGfa).toLocaleString()} m² Local · ~${landmarkEstGfa.toLocaleString()} m² Landmark</span>
      </div>
      ${waterWarn}
      <div style="font-size:11px;color:var(--nest-muted)">
        <b>Active Mix (${activeMode === 'single' ? 'Single' : 'Balanced ' + activeMode}):</b> ${activeTyps.join(' + ')} · Eff ${(eff*100).toFixed(0)}%
      </div>
      <div class="alloc-bar">${allocBar}</div>
      <table class="sp-table">
        <thead><tr><th>Emergent Program Zone &amp; Activities</th><th style="text-align:right">Indicative Area</th></tr></thead>
        <tbody>${rowsHtml}</tbody>
      </table>
      ${buildConceptHtml(eIdx, activeTyps, topF)}
    `;
    grid.appendChild(card);
  });
}

function inspectCell(latlng) {
  const lat = latlng.lat, lon = latlng.lng;
  const minLat = BOUNDS[0][0], minLon = BOUNDS[0][1], maxLat = BOUNDS[1][0], maxLon = BOUNDS[1][1];
  if (lat < minLat || lat > maxLat || lon < minLon || lon > maxLon) return;
  const col = Math.floor(((lon - minLon) / (maxLon - minLon)) * NX);
  const row = Math.floor(((maxLat - lat) / (maxLat - minLat)) * NY);
  if (row < 0 || row >= NY || col < 0 || col >= NX) return;

  lastRow = row; lastCol = col; customPop = null;
  markers.forEach((mk, i) => {
    if (mk) maps[i].removeLayer(mk);
    markers[i] = L.circleMarker(latlng, { radius: 6, color: '#FF614C', weight: 2.5, fillColor: '#FFFAF7', fillOpacity: 0.95 }).addTo(maps[i]);
  });

  document.getElementById('drawer-title').innerHTML = `<b>Selected 50×50 m Cell (${lat.toFixed(5)}, ${lon.toFixed(5)})</b> — Live 3-Engine Visual Math &amp; Spatial Drivers`;
  document.getElementById('drawer').style.display = 'flex';
  renderDrawer();
}

maps.forEach(m => m.on('click', e => inspectCell(e.latlng)));

// Hover Tooltips
const SCORE_EXPLAINERS = {
  crystals:  { title: 'Crystals · Development Score', scale: '0 – 100', desc: 'Measures how well this cell frames high-gravity landmarks or POIs at a respectful standoff ring.', formula: '<b>Math:</b> Weighted sum of Ring-Standoff, Proximity, and Density drivers × Terrain Affinity.', bands: '<b>Bands:</b> 70–100 Peak POI Ring · 45–69 Strong · &lt;45 Secondary' },
  cells:     { title: 'Cells · Adaptation Score', scale: '0 – 100', desc: 'Measures edge collisions where opposing natural/site fields meet and can be adapted into passive assets.', formula: '<b>Math:</b> Weighted sum of Edge-Collision &amp; Gradient drivers × Shoreline/Habitat Affinity.', bands: '<b>Bands:</b> 70–100 Peak Edge · 45–69 Strong · &lt;45 Interior' },
  corals:    { title: 'Corals · Coordination Score', scale: '0 – 100', desc: 'Measures how strongly this cell bridges separated settlements, corridors, services, and nature.', formula: '<b>Math:</b> Weighted sum of Bridge-Seam &amp; Service-Deficit drivers × Corridor Affinity.', bands: '<b>Bands:</b> 70–100 Peak Seam · 45–69 Strong · &lt;45 Isolated' },
  hidden:    { title: 'Untapped Potential Score', scale: '0 – 100', desc: 'Combines strong spatial forces with low existing urban saturation so overlooked sites rise to the top.', formula: '<b>Math:</b> Engine-specific blend of Dominant/Synergy scores + Under-built Canvas + Natural Evidence.', bands: '<b>Bands:</b> 75–100 Prime Opportunity · 50–74 Promising · &lt;50 Saturated/Low' },
  synergy_2: { title: 'Balanced Pair (2+) Synergy', scale: '0 – 100', desc: 'Rewards cells where 2+ compatible forces are both high AND balanced — penalizes lopsided pairs.', formula: '<b>Formula:</b> <code>max(0, Average − Spread)</code> where Spread is Sample StdDev.', bands: '<b>Trigger:</b> ≥60 auto-activates 2+ mixed-use program.' },
  synergy_3: { title: 'Balanced Trio (3+) Synergy', scale: '0 – 100', desc: 'Pinpoints rare flagship peaks where 3+ compatible forces align at similar strength.', formula: '<b>Formula:</b> <code>max(0, Average − Spread)</code> across valid 3+ force trios.', bands: '<b>Trigger:</b> ≥60 auto-activates 3+ flagship program.' },
  affinity:  { title: 'Engine Terrain Multiplier', scale: '×0.35 – ×1.00', desc: 'Scales raw GIS signals according to the terrain each engine prefers (Dry Land vs Shoreline vs Corridors).', formula: '<b>Effect:</b> <code>Final Force = Raw GIS Weighted Sum × Terrain Multiplier</code>.', bands: '<b>Reading:</b> ×1.00 Full Strength · ×0.68–0.85 Moderate · ≤×0.42 Penalized' },
  driver_pts:{ title: 'GIS Driver Point Contribution', scale: '+pts toward 100', desc: 'Exact points this GIS rule adds to the cell\\'s 0–100 Dominant Force score after engine terrain weighting.', formula: '<b>Math:</b> <code>Operator(0–1) × (Rule Weight / Total Weight) × 100 × Affinity</code>.', bands: '<b>Reading:</b> Larger +pts = stronger physical pull from that GIS layer.' },
};
Object.keys(OP_META).forEach(k => {
  SCORE_EXPLAINERS['op_' + k] = {
    title: OP_META[k].icon + ' ' + OP_META[k].label + ' Operator',
    scale: '0.0 → 1.0',
    desc: OP_META[k].tip,
    formula: '<b>Interactive Lab:</b> Click <b>Visual Math &amp; Engine Guide → Interactive Math Lab</b> to test this curve live.',
    bands: '<b>Output:</b> Smooth 0.0–1.0 spatial score before rule weight &amp; terrain affinity.'
  };
});

(function initScoreTooltips() {
  const tip = document.getElementById('nest-score-tip');
  if (!tip) return;
  let activeEl = null;
  function showTip(el) {
    const key = el.getAttribute('data-score-key');
    const info = SCORE_EXPLAINERS[key] || { title: key || 'Spatial Force Score', scale: '0 – 100', desc: 'Normalized 50×50 m spatial force score weighted by this engine\\'s rules and terrain affinity.', formula: '<b>Math:</b> Weighted sum of GIS spatial operators × Engine Terrain Multiplier.', bands: '<b>Bands:</b> 70–100 Peak · 45–69 Strong · &lt;45 Secondary' };
    tip.innerHTML = `<div class="tip-hdr"><span class="tip-title">${info.title}</span><span class="tip-scale">${info.scale}</span></div><div class="tip-desc">${info.desc}</div><div class="tip-formula">${info.formula}</div><div class="tip-bands">${info.bands}</div>`;
    tip.classList.add('visible');
    const r = el.getBoundingClientRect();
    const tw = tip.offsetWidth || 340, th = tip.offsetHeight || 140;
    let left = Math.max(12, Math.min(window.innerWidth - tw - 12, r.left + r.width / 2 - tw / 2));
    let top = r.top - th - 10;
    if (top < 12) top = r.bottom + 10;
    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
  }
  document.addEventListener('mouseover', e => { const t = e.target.closest('.score-explain'); if (t) { activeEl = t; showTip(t); } });
  document.addEventListener('mouseout', e => { const t = e.target.closest('.score-explain'); if (t && (!e.relatedTarget || !t.contains(e.relatedTarget))) { activeEl = null; tip.classList.remove('visible'); } });
  document.addEventListener('focusin', e => { const t = e.target.closest('.score-explain'); if (t) { activeEl = t; showTip(t); } });
  document.addEventListener('focusout', () => { if (activeEl) { activeEl = null; tip.classList.remove('visible'); } });
})();

// Visual Math & Engine Guide Modal + Interactive Math Lab
let activeLabOp = 'ring_decay';

function switchGuideTab(tabName) {
  document.querySelectorAll('.gtab-btn').forEach(b => b.classList.toggle('active', b.dataset.gtab === tabName));
  document.querySelectorAll('.guide-pane').forEach(p => p.classList.toggle('active', p.id === 'gpane-' + tabName));
  if (tabName === 'lab') { renderOpLab(); renderSynLab(); }
}

function openScoringGuide(tabName, opKey) {
  const el = document.getElementById('scoring-guide-backdrop');
  if (!el) return;
  el.classList.add('open');
  el.setAttribute('aria-hidden', 'false');
  if (opKey) { activeLabOp = opKey; }
  switchGuideTab(tabName || 'engines');
}

function closeScoringGuide() {
  const el = document.getElementById('scoring-guide-backdrop');
  if (el) { el.classList.remove('open'); el.setAttribute('aria-hidden', 'true'); }
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeScoringGuide(); });

const LAB_OPS = {
  ring_decay: {
    name: '◎ Ring Standoff (Crystals)',
    formula: 'score = exp(−0.5 · ((d − 0.55·R) / (0.45·R))²)  [R = 600 m]',
    meaning: 'Peaks in a respectful standoff ring around a landmark or shoreline (here ~330 m). Too close crowds the asset; too far loses visual dialogue.',
    evalScore: d => Math.exp(-0.5 * Math.pow((d - 330) / 270, 2)),
  },
  ecotone_gradient: {
    name: '◐ Edge Collision (Cells)',
    formula: 'score = √(exp(−dA/R) · exp(−dB/R))  [R = 500 m]',
    meaning: 'Peaks where two different site fields collide (e.g., water edge at 0 m and desert/habitat at 600 m). Maximum tension = highest adaptation value.',
    evalScore: d => {
      const fa = Math.exp(-d / 450);
      const fb = Math.exp(-Math.abs(600 - d) / 450);
      const peak = Math.sqrt(Math.exp(-300 / 450) * Math.exp(-300 / 450));
      return Math.min(1, Math.sqrt(fa * fb) / peak);
    },
  },
  corridor_bridge: {
    name: '⇄ Bridge Seam (Corals)',
    formula: 'score = exp(−(dA+dB)/(1.6·R)) · (0.35 + 0.65·Balance)',
    meaning: 'Peaks at the balanced midpoint connecting Element A (0 m) and Element B (700 m). Favors cells that can stitch both sides equally.',
    evalScore: d => {
      const da = d, db = Math.abs(700 - d);
      const span = Math.exp(-(da + db) / 960);
      const bal = 1 - Math.abs(da - db) / (da + db + 25);
      const raw = span * (0.35 + 0.65 * bal);
      const peak = Math.exp(-700 / 960) * 1.0;
      return Math.min(1, raw / peak);
    },
  },
  decay: {
    name: '↘ Proximity Decay',
    formula: 'score = exp(−d / R)  [R = 400 m]',
    meaning: 'Scores 100 right next to a feature (road, shore, transit stop) and decays smoothly with walking distance — no harsh arbitrary cutoff.',
    evalScore: d => Math.exp(-d / 400),
  },
  kde: {
    name: '◉ Cluster Density (KDE)',
    formula: 'score = Σ exp(−dᵢ² / (2σ²)) normalized 0–1  [σ = 260 m]',
    meaning: 'Places a smooth bell curve over every GIS point (buildings, bird sightings, hubs) and sums overlapping bells to find true density clusters.',
    evalScore: d => {
      const centers = [140, 220, 310, 680];
      const raw = centers.reduce((acc, c) => acc + Math.exp(-Math.pow(d - c, 2) / (2 * 130 * 130)), 0);
      return Math.min(1, raw / 2.28);
    },
  },
  service_gap: {
    name: '⊘ Service Deficit',
    formula: 'score = max(0, Population_KDE − exp(−d_service / R))',
    meaning: 'Finds populated neighborhoods that are far from existing clinics or schools (service at 0 m, populated cluster around 550 m).',
    evalScore: d => {
      const pop = Math.exp(-Math.pow(d - 560, 2) / (2 * 220 * 220));
      const srv = Math.exp(-d / 320);
      return Math.max(0, Math.min(1, (pop - srv) / 0.82));
    },
  },
};

function selectLabOp(key) {
  activeLabOp = key;
  renderOpLab();
}

function renderOpLab() {
  const op = LAB_OPS[activeLabOp] || LAB_OPS.ring_decay;
  document.querySelectorAll('.op-btn').forEach(b => b.classList.toggle('active', b.dataset.op === activeLabOp));
  const d = parseInt((document.getElementById('lab-dist') || { value: 330 }).value, 10);
  const sc = Math.round(op.evalScore(d) * 100);
  const dLbl = document.getElementById('lab-dist-val');
  if (dLbl) dLbl.textContent = d + ' m';
  const scLbl = document.getElementById('lab-score-val');
  if (scLbl) scLbl.textContent = sc + ' / 100';
  const fEl = document.getElementById('lab-formula');
  if (fEl) fEl.textContent = op.formula;
  const mEl = document.getElementById('lab-meaning');
  if (mEl) mEl.textContent = op.meaning;

  const svg = document.getElementById('lab-op-svg');
  if (!svg) return;

  // Build curve polyline (x: 34..426 for d: 0..1000, y: 175..105 for score 0..1)
  const xOf = dist => 34 + (dist / 1000) * 392;
  const yOf = s => 176 - s * 72;
  let pts = [], area = [`34,176`];
  for (let dist = 0; dist <= 1000; dist += 20) {
    const x = xOf(dist).toFixed(1), y = yOf(op.evalScore(dist)).toFixed(1);
    pts.push(`${x},${y}`);
    area.push(`${x},${y}`);
  }
  area.push(`426,176`);
  const cx = xOf(d), cy = yOf(op.evalScore(d));

  // Plan-view illustration in top half (y: 8..84)
  let planHtml = '';
  if (activeLabOp === 'ring_decay') {
    planHtml = `
      <circle cx="34" cy="46" r="129" fill="none" stroke="#FF614C" stroke-width="32" opacity="0.22"/>
      <circle cx="34" cy="46" r="129" fill="none" stroke="#A3473A" stroke-width="1.3" stroke-dasharray="4 3"/>
      <circle cx="34" cy="46" r="8" fill="#302B2A"/><text x="48" y="34" font-size="9.5" font-weight="800" fill="#302B2A">Landmark / POI (0 m)</text>
      <text x="163" y="24" text-anchor="middle" font-size="9.5" font-weight="800" fill="#A3473A">Sweet-Spot Ring (~330 m)</text>
    `;
  } else if (activeLabOp === 'ecotone_gradient') {
    planHtml = `
      <rect x="34" y="12" width="130" height="68" rx="6" fill="#0EA5E9" opacity="0.18"/>
      <rect x="148" y="12" width="160" height="68" rx="6" fill="#F59E0B" opacity="0.18"/>
      <rect x="128" y="12" width="52" height="68" fill="#FF614C" opacity="0.25"/>
      <text x="44" y="27" font-size="9.5" font-weight="800" fill="#0369A1">Field A (Water)</text>
      <text x="298" y="27" text-anchor="end" font-size="9.5" font-weight="800" fill="#B45309">Field B (Habitat/Solar)</text>
      <text x="154" y="72" text-anchor="middle" font-size="9.5" font-weight="800" fill="#A3473A">Edge Collision Peak</text>
    `;
  } else if (activeLabOp === 'corridor_bridge') {
    planHtml = `
      <line x1="34" y1="46" x2="308" y2="46" stroke="#A3473A" stroke-width="2" stroke-dasharray="4 3"/>
      <ellipse cx="171" cy="46" rx="48" ry="26" fill="#FF614C" opacity="0.24"/>
      <circle cx="34" cy="46" r="8" fill="#302B2A"/><text x="46" y="30" font-size="9.5" font-weight="800" fill="#302B2A">Node A (0 m)</text>
      <circle cx="308" cy="46" r="8" fill="#246247"/><text x="308" y="30" text-anchor="middle" font-size="9.5" font-weight="800" fill="#246247">Node B (700 m)</text>
      <text x="171" y="77" text-anchor="middle" font-size="9.5" font-weight="800" fill="#A3473A">Balanced Bridge Midpoint</text>
    `;
  } else if (activeLabOp === 'kde') {
    planHtml = `
      <ellipse cx="122" cy="46" rx="76" ry="28" fill="#FF614C" opacity="0.22"/>
      <ellipse cx="301" cy="46" rx="34" ry="20" fill="#FF614C" opacity="0.14"/>
      <circle cx="89" cy="46" r="4" fill="#302B2A"/><circle cx="120" cy="40" r="4" fill="#302B2A"/><circle cx="155" cy="50" r="4" fill="#302B2A"/>
      <circle cx="301" cy="46" r="4" fill="#302B2A"/>
      <text x="122" y="24" text-anchor="middle" font-size="9.5" font-weight="800" fill="#A3473A">Dense Point Cluster (High KDE)</text>
      <text x="301" y="24" text-anchor="middle" font-size="9" font-weight="700" fill="#625753">Isolated Point</text>
    `;
  } else if (activeLabOp === 'service_gap') {
    planHtml = `
      <circle cx="34" cy="46" r="65" fill="#246247" opacity="0.15"/>
      <ellipse cx="254" cy="46" rx="72" ry="28" fill="#FF614C" opacity="0.24"/>
      <circle cx="34" cy="46" r="7" fill="#246247"/><text x="46" y="30" font-size="9.5" font-weight="800" fill="#246247">Existing Clinic/School (0 m)</text>
      <text x="254" y="26" text-anchor="middle" font-size="9.5" font-weight="800" fill="#A3473A">Underserved Population Gap</text>
    `;
  } else {
    planHtml = `
      <rect x="34" y="14" width="392" height="64" rx="6" fill="url(#decayGrad)"/>
      <circle cx="34" cy="46" r="8" fill="#302B2A"/><text x="48" y="32" font-size="9.5" font-weight="800" fill="#302B2A">Target Feature (0 m)</text>
      <text x="310" y="32" font-size="9.5" font-weight="700" fill="#625753">Smooth distance fade →</text>
    `;
  }

  svg.innerHTML = `
    <defs>
      <linearGradient id="decayGrad" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#FF614C" stop-opacity="0.34"/>
        <stop offset="50%" stop-color="#FF614C" stop-opacity="0.10"/>
        <stop offset="100%" stop-color="#FF614C" stop-opacity="0.0"/>
      </linearGradient>
      <clipPath id="planClip"><rect x="34" y="10" width="392" height="72" rx="6"/></clipPath>
    </defs>
    <rect x="34" y="10" width="392" height="72" rx="6" fill="#FFFFFF" stroke="#E5DAD6"/>
    <g clip-path="url(#planClip)">${planHtml}</g>
    <line x1="${cx.toFixed(1)}" y1="10" x2="${cx.toFixed(1)}" y2="176" stroke="#302B2A" stroke-width="1.3" stroke-dasharray="3 2.5"/>
    <circle cx="${cx.toFixed(1)}" cy="46" r="6" fill="#FF614C" stroke="#302B2A" stroke-width="2"/>
    <text x="10" y="50" font-size="9" font-weight="800" fill="#625753">PLAN</text>

    <!-- Cross-section curve -->
    <line x1="34" y1="176" x2="426" y2="176" stroke="#C7B9B4" stroke-width="1.2"/>
    <line x1="34" y1="104" x2="34" y2="176" stroke="#C7B9B4" stroke-width="1.2"/>
    <text x="29" y="108" text-anchor="end" font-size="9" font-weight="700" fill="#625753">100</text>
    <text x="29" y="143" text-anchor="end" font-size="9" font-weight="700" fill="#625753">50</text>
    <text x="29" y="178" text-anchor="end" font-size="9" font-weight="700" fill="#625753">0</text>
    <polygon points="${area.join(' ')}" fill="rgba(255,97,76,0.18)"/>
    <polyline points="${pts.join(' ')}" fill="none" stroke="#A3473A" stroke-width="2.4"/>
    <circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="5.5" fill="#FF614C" stroke="#FFFFFF" stroke-width="2"/>
    <text x="${Math.min(395, Math.max(58, cx)).toFixed(1)}" y="${Math.max(100, cy - 9).toFixed(1)}" text-anchor="middle" font-size="10.5" font-weight="800" fill="#A3473A">${sc}/100</text>
    <text x="34" y="191" font-size="9" font-weight="700" fill="#625753">0 m</text>
    <text x="230" y="191" text-anchor="middle" font-size="9" font-weight="700" fill="#625753">500 m</text>
    <text x="426" y="191" text-anchor="end" font-size="9" font-weight="700" fill="#625753">1,000 m</text>
  `;
}

function setSynPreset(a, b) {
  const elA = document.getElementById('syn-a'), elB = document.getElementById('syn-b');
  if (elA) elA.value = a;
  if (elB) elB.value = b;
  renderSynLab();
}

function renderSynLab() {
  const a = parseInt((document.getElementById('syn-a') || { value: 80 }).value, 10);
  const b = parseInt((document.getElementById('syn-b') || { value: 80 }).value, 10);
  const mean = (a + b) / 2;
  const sd = Math.sqrt(((a - mean) ** 2 + (b - mean) ** 2) / 1); // sample std dev (ddof=1)
  const syn = Math.max(0, mean - sd);

  document.getElementById('syn-a-val').textContent = a;
  document.getElementById('syn-b-val').textContent = b;
  document.getElementById('syn-mean-val').textContent = mean.toFixed(1);
  document.getElementById('syn-sd-val').textContent = '−' + sd.toFixed(1);
  document.getElementById('syn-out-val').textContent = syn.toFixed(1) + ' / 100';

  const svg = document.getElementById('lab-syn-svg');
  if (!svg) return;
  const xOf = v => 20 + (Math.max(0, Math.min(100, v)) / 100) * 320;
  const xA = xOf(a), xB = xOf(b), xM = xOf(mean), xS = xOf(syn);
  const penW = Math.max(0, xM - xS);
  svg.innerHTML = `
    <line x1="20" y1="54" x2="340" y2="54" stroke="#E5DAD6" stroke-width="8" stroke-linecap="round"/>
    <line x1="20" y1="54" x2="${xS.toFixed(1)}" y2="54" stroke="#FF614C" stroke-width="8" stroke-linecap="round"/>
    ${penW > 2 ? `<rect x="${xS.toFixed(1)}" y="40" width="${penW.toFixed(1)}" height="28" rx="4" fill="rgba(163,71,58,0.16)" stroke="#A3473A" stroke-width="1.2" stroke-dasharray="3 2"/>` : ''}
    ${penW > 28 ? `<text x="${(xS + penW/2).toFixed(1)}" y="34" text-anchor="middle" font-size="9.5" font-weight="800" fill="#A3473A">Spread −${sd.toFixed(0)}</text>` : ''}
    <line x1="${xM.toFixed(1)}" y1="22" x2="${xM.toFixed(1)}" y2="78" stroke="#625753" stroke-width="1.6" stroke-dasharray="3 2"/>
    <text x="${xM.toFixed(1)}" y="16" text-anchor="middle" font-size="9.5" font-weight="800" fill="#625753">Avg ${mean.toFixed(0)}</text>
    <circle cx="${xA.toFixed(1)}" cy="54" r="7" fill="#0EA5E9" stroke="#FFFFFF" stroke-width="2"/>
    <text x="${xA.toFixed(1)}" y="86" text-anchor="middle" font-size="9.5" font-weight="800" fill="#0369A1">A (${a})</text>
    <circle cx="${xB.toFixed(1)}" cy="54" r="7" fill="#F59E0B" stroke="#FFFFFF" stroke-width="2"/>
    <text x="${xB.toFixed(1)}" y="99" text-anchor="middle" font-size="9.5" font-weight="800" fill="#B45309">B (${b})</text>
    <text x="20" y="72" font-size="9" fill="#625753">0</text>
    <text x="340" y="72" text-anchor="end" font-size="9" fill="#625753">100</text>
  `;
}
</script>

<div id="nest-score-tip" role="tooltip" aria-hidden="true"></div>

<div id="scoring-guide-backdrop" class="glossary-backdrop" role="dialog" aria-modal="true" aria-labelledby="glossary-heading" aria-hidden="true" onclick="if(event.target===this)closeScoringGuide()">
  <div class="glossary-dialog">
    <div class="glossary-hdr">
      <h3 id="glossary-heading">Visual Math &amp; 3-Engine Analysis Guide</h3>
      <div class="guide-tabs" role="tablist">
        <button type="button" class="gtab-btn active" data-gtab="engines" onclick="switchGuideTab('engines')">1. The 3 Engines</button>
        <button type="button" class="gtab-btn" data-gtab="lab" onclick="switchGuideTab('lab')">2. Interactive Math Lab</button>
        <button type="button" class="gtab-btn" data-gtab="pipeline" onclick="switchGuideTab('pipeline')">3. Stages 1 → 2 → 3</button>
      </div>
      <button type="button" class="fit-btn" onclick="closeScoringGuide()">Close ✕</button>
    </div>

    <div class="glossary-body">
      <!-- TAB 1: THE 3 ENGINES COMPARED -->
      <div id="gpane-engines" class="guide-pane active">
        <div class="eng-compare-grid">
          <!-- Crystals Card -->
          <div class="gloss-card">
            <div class="gloss-title"><span>1. Crystals · Development</span><span class="gloss-tag">Build Around / At Landmarks</span></div>
            <svg class="diag-svg" viewBox="0 0 280 140" aria-label="Crystals Framing Ring Plan and Curve">
              <circle cx="72" cy="68" r="44" fill="none" stroke="#FF614C" stroke-width="18" opacity="0.24"/>
              <circle cx="72" cy="68" r="44" fill="none" stroke="#A3473A" stroke-width="1.4" stroke-dasharray="3 2.5"/>
              <circle cx="72" cy="68" r="10" fill="#302B2A"/>
              <text x="72" y="128" text-anchor="middle" font-size="9.5" font-weight="800" fill="#302B2A">PLAN: Framing Ring</text>
              <line x1="150" y1="112" x2="266" y2="112" stroke="#C7B9B4" stroke-width="1.2"/>
              <path d="M 150 108 Q 175 102, 198 34 Q 220 100, 266 110" fill="rgba(255,97,76,0.18)" stroke="#A3473A" stroke-width="2.2"/>
              <circle cx="198" cy="34" r="4" fill="#FF614C"/>
              <text x="198" y="25" text-anchor="middle" font-size="9" font-weight="800" fill="#A3473A">Sweet Spot</text>
              <text x="208" y="128" text-anchor="middle" font-size="9.5" font-weight="800" fill="#625753">CURVE: Framing Ring</text>
            </svg>
            <p class="gloss-txt">Hunts for high-gravity landmarks, shorelines, and civic anchors to build <b>around, in, or at</b> — using a framing ring so new buildings showcase the asset without crowding it.</p>
            <div class="aff-mini-grid">
              <div style="font-size:10px;font-weight:800;color:var(--nest-edge);text-transform:uppercase">Terrain Affinity Multiplier</div>
              <div class="aff-mini-row"><span>Land &amp; Shore</span><div class="bar-bg"><div class="bar-fill" style="width:100%;background:#246247"></div></div><b>×1.00</b></div>
              <div class="aff-mini-row"><span>Shallow Water</span><div class="bar-bg"><div class="bar-fill" style="width:70%;background:#B56E18"></div></div><b>×0.70</b></div>
              <div class="aff-mini-row"><span>Deep Water</span><div class="bar-bg"><div class="bar-fill" style="width:35%;background:#A12B3A"></div></div><b>×0.35</b></div>
            </div>
            <div class="gloss-why"><b>Mask Rule:</b> Excludes road corridors &amp; existing building footprints, while keeping open urban infill plots buildable.</div>
          </div>

          <!-- Cells Card -->
          <div class="gloss-card">
            <div class="gloss-title"><span>2. Cells · Adaptation</span><span class="gloss-tag">Adapt Existing Elements</span></div>
            <svg class="diag-svg" viewBox="0 0 280 140" aria-label="Cells Edge &amp; Hotspot Plan and Curve">
              <circle cx="52" cy="68" r="38" fill="#0EA5E9" opacity="0.22"/>
              <circle cx="96" cy="68" r="38" fill="#F59E0B" opacity="0.22"/>
              <path d="M74 36 C86 52 86 84 74 100 C62 84 62 52 74 36 Z" fill="#FF614C" opacity="0.72"/>
              <text x="74" y="128" text-anchor="middle" font-size="9.5" font-weight="800" fill="#302B2A">PLAN: Edge &amp; Hotspot</text>
              <line x1="150" y1="112" x2="266" y2="112" stroke="#C7B9B4" stroke-width="1.2"/>
              <path d="M 150 38 Q 190 78, 266 110" fill="none" stroke="#0EA5E9" stroke-width="1.5" stroke-dasharray="3 2"/>
              <path d="M 150 110 Q 226 78, 266 38" fill="none" stroke="#F59E0B" stroke-width="1.5" stroke-dasharray="3 2"/>
              <path d="M 150 110 Q 208 26, 266 110" fill="rgba(255,97,76,0.18)" stroke="#A3473A" stroke-width="2.2"/>
              <circle cx="208" cy="48" r="4" fill="#FF614C"/>
              <text x="208" y="34" text-anchor="middle" font-size="9" font-weight="800" fill="#A3473A">Collision Peak</text>
              <text x="208" y="128" text-anchor="middle" font-size="9.5" font-weight="800" fill="#625753">CURVE: √(Field A × B)</text>
            </svg>
            <p class="gloss-txt">Targets natural or contextual host elements (shorelines, habitats, quarries, ruins, isolated structures, solar extremes) to <b>adapt</b> them into something new and better.</p>
            <div class="aff-mini-grid">
              <div style="font-size:10px;font-weight:800;color:var(--nest-edge);text-transform:uppercase">Terrain Affinity Multiplier</div>
              <div class="aff-mini-row"><span>Host Element</span><div class="bar-bg"><div class="bar-fill" style="width:100%;background:#246247"></div></div><b>×1.00</b></div>
              <div class="aff-mini-row"><span>Open Water</span><div class="bar-bg"><div class="bar-fill" style="width:85%;background:#246247"></div></div><b>×0.85</b></div>
              <div class="aff-mini-row"><span>Plain Dry Land</span><div class="bar-bg"><div class="bar-fill" style="width:75%;background:#B56E18"></div></div><b>×0.75</b></div>
            </div>
            <div class="gloss-why"><b>Mask Rule:</b> Excludes roads &amp; dense urban cores, keeping shorelines, ecological hotspots, and adaptable contextual sites open.</div>
          </div>

          <!-- Corals Card -->
          <div class="gloss-card">
            <div class="gloss-title"><span>3. Corals · Coordination</span><span class="gloss-tag">Connect &amp; Coordinate</span></div>
            <svg class="diag-svg" viewBox="0 0 280 140" aria-label="Corals Midpoint Seam Plan and Curve">
              <line x1="28" y1="68" x2="120" y2="68" stroke="#A3473A" stroke-width="2" stroke-dasharray="4 2.5"/>
              <ellipse cx="74" cy="68" rx="22" ry="34" fill="#FF614C" opacity="0.28"/>
              <circle cx="28" cy="68" r="9" fill="#302B2A"/>
              <circle cx="120" cy="68" r="9" fill="#246247"/>
              <circle cx="74" cy="68" r="5" fill="#FF614C" stroke="#A3473A" stroke-width="1.5"/>
              <text x="74" y="128" text-anchor="middle" font-size="9.5" font-weight="800" fill="#302B2A">PLAN: Midpoint Seam</text>
              <line x1="150" y1="112" x2="266" y2="112" stroke="#C7B9B4" stroke-width="1.2"/>
              <path d="M 150 94 Q 208 24, 266 94" fill="rgba(255,97,76,0.18)" stroke="#A3473A" stroke-width="2.2"/>
              <circle cx="208" cy="42" r="4" fill="#FF614C"/>
              <text x="208" y="30" text-anchor="middle" font-size="9" font-weight="800" fill="#A3473A">Midpoint Bridge</text>
              <text x="208" y="128" text-anchor="middle" font-size="9.5" font-weight="800" fill="#625753">CURVE: Span × Balance</text>
            </svg>
            <p class="gloss-txt">Locates missing-link seams between separated settlements, roads, transit hubs, and natural systems so elements <b>work better together</b> in a beneficial loop.</p>
            <div class="aff-mini-grid">
              <div style="font-size:10px;font-weight:800;color:var(--nest-edge);text-transform:uppercase">Terrain Affinity Multiplier</div>
              <div class="aff-mini-row"><span>Network / Nature</span><div class="bar-bg"><div class="bar-fill" style="width:100%;background:#246247"></div></div><b>×1.00</b></div>
              <div class="aff-mini-row"><span>750–1,500 m</span><div class="bar-bg"><div class="bar-fill" style="width:85%;background:#246247"></div></div><b>×0.85</b></div>
              <div class="aff-mini-row"><span>Isolated &gt;1.5 km</span><div class="bar-bg"><div class="bar-fill" style="width:65%;background:#B56E18"></div></div><b>×0.65</b></div>
            </div>
            <div class="gloss-why"><b>Mask Rule:</b> Evaluates <b>all land and water</b> inside the plot boundary so civic/infrastructure bridges can span urban seams directly.</div>
          </div>
        </div>
      </div>

      <!-- TAB 2: INTERACTIVE MATH LAB -->
      <div id="gpane-lab" class="guide-pane">
        <div class="lab-grid">
          <!-- Sandbox 1: Spatial Operators -->
          <div class="gloss-card">
            <div class="gloss-title"><span>Spatial Operator Sandbox</span><span class="gloss-tag">Drag Distance Live</span></div>
            <div class="op-pills">
              <button type="button" class="op-btn active" data-op="ring_decay" onclick="selectLabOp('ring_decay')">◎ Ring Standoff</button>
              <button type="button" class="op-btn" data-op="ecotone_gradient" onclick="selectLabOp('ecotone_gradient')">◐ Edge Collision</button>
              <button type="button" class="op-btn" data-op="corridor_bridge" onclick="selectLabOp('corridor_bridge')">⇄ Bridge Seam</button>
              <button type="button" class="op-btn" data-op="decay" onclick="selectLabOp('decay')">↘ Proximity</button>
              <button type="button" class="op-btn" data-op="kde" onclick="selectLabOp('kde')">◉ Cluster (KDE)</button>
              <button type="button" class="op-btn" data-op="service_gap" onclick="selectLabOp('service_gap')">⊘ Service Gap</button>
            </div>
            <svg id="lab-op-svg" class="diag-svg" viewBox="0 0 460 198"></svg>
            <div class="slider-row">
              <span>Cell Distance: <b id="lab-dist-val" style="color:var(--nest-edge)">330 m</b></span>
              <input id="lab-dist" type="range" min="0" max="1000" step="10" value="330" oninput="renderOpLab()" />
              <span>Score: <b id="lab-score-val" style="color:var(--nest-edge);min-width:58px;display:inline-block;text-align:right">100 / 100</b></span>
            </div>
            <div id="lab-formula" class="formula-chip"></div>
            <p id="lab-meaning" class="gloss-txt"></p>
          </div>

          <!-- Sandbox 2: Force Synergy Balance -->
          <div class="gloss-card">
            <div class="gloss-title"><span>Force Balance Sandbox (Synergy)</span><span class="gloss-tag">Avg − Spread</span></div>
            <p class="gloss-txt">Why does NEST use <code>max(0, Average − Spread)</code> instead of a plain average? Drag the two forces below to see how <b>balance</b> beats a lopsided pair.</p>
            <div class="preset-row">
              <button type="button" class="preset-btn" onclick="setSynPreset(80, 80)">Balanced (80 &amp; 80 → 80)</button>
              <button type="button" class="preset-btn" onclick="setSynPreset(95, 40)">Lopsided (95 &amp; 40 → 29)</button>
              <button type="button" class="preset-btn" onclick="setSynPreset(72, 66)">Strong Pair (72 &amp; 66 → 65)</button>
            </div>
            <svg id="lab-syn-svg" class="diag-svg" viewBox="0 0 360 112"></svg>
            <div class="slider-row">
              <span style="min-width:84px;color:#0369A1">Force A: <b id="syn-a-val">80</b></span>
              <input id="syn-a" type="range" min="0" max="100" value="80" oninput="renderSynLab()" />
            </div>
            <div class="slider-row">
              <span style="min-width:84px;color:#B45309">Force B: <b id="syn-b-val">80</b></span>
              <input id="syn-b" type="range" min="0" max="100" value="80" oninput="renderSynLab()" />
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center">
              <div style="background:var(--nest-surface);border:1px solid #ECE2DF;border-radius:8px;padding:6px">
                <div style="font-size:9.5px;font-weight:800;color:var(--nest-muted);text-transform:uppercase">Average</div>
                <div id="syn-mean-val" style="font-size:16px;font-weight:800;color:var(--nest-ink)">80.0</div>
              </div>
              <div style="background:var(--nest-surface);border:1px solid #ECE2DF;border-radius:8px;padding:6px">
                <div style="font-size:9.5px;font-weight:800;color:var(--nest-muted);text-transform:uppercase">Spread Penalty</div>
                <div id="syn-sd-val" style="font-size:16px;font-weight:800;color:var(--nest-err)">−0.0</div>
              </div>
              <div style="background:var(--nest-soft);border:1px solid #E5C5BE;border-radius:8px;padding:6px">
                <div style="font-size:9.5px;font-weight:800;color:var(--nest-edge);text-transform:uppercase">Synergy Score</div>
                <div id="syn-out-val" style="font-size:16px;font-weight:800;color:var(--nest-edge)">80.0 / 100</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 3: STAGES 1 -> 2 -> 3 PIPELINE -->
      <div id="gpane-pipeline" class="guide-pane">
        <div class="pipe-grid">
          <div class="gloss-card">
            <div class="gloss-title"><span>Stage 1 · Single Forces</span><span class="gloss-tag">6 GIS Surfaces</span></div>
            <p class="gloss-txt">Every 50×50 m cell is evaluated across 6 spatial forces (Hydrology, Solar, Biodiversity, Heritage, Civic Deficit, Corridors). Each GIS rule runs its operator (0→1), multiplies by its rule weight, and scales by the engine's <b>Terrain Affinity Multiplier</b>.</p>
            <div class="formula-chip">Force = Σ(Op × Weight) × 100 × Affinity</div>
          </div>
          <div class="gloss-card">
            <div class="gloss-title"><span>Stage 2 · Force Balance</span><span class="gloss-tag">Dominant / 2+ / 3+</span></div>
            <p class="gloss-txt">Compares all 6 forces at each cell to find either the single <b>Dominant Force</b>, or the highest-scoring compatible <b>Balanced Pair (2+)</b> and <b>Balanced Trio (3+)</b> using <code>Avg − Spread</code>.</p>
            <div class="formula-chip">Synergy = max(0, Mean − StdDev)</div>
          </div>
          <div class="gloss-card">
            <div class="gloss-title"><span>Stage 3 · Untapped Potential</span><span class="gloss-tag">Site Selection</span></div>
            <p class="gloss-txt">Filters for cells with natural-system evidence within 2.5 km, then applies each engine's custom discovery recipe below so Crystals, Cells, and Corals surface genuinely different top 5 sites.</p>
            <div class="formula-chip">Top 5 per Engine (≥450 m spacing)</div>
          </div>
        </div>

        <div class="gloss-card">
          <div class="gloss-title"><span>Exact Stage 3 Recipe per Engine (100% Weight Breakdown)</span><span class="gloss-tag">Why the 3 Maps Differ</span></div>
          <div style="display:flex;flex-direction:column;gap:12px">
            <div>
              <div style="font-size:11.5px;font-weight:800;margin-bottom:4px">1. Crystals · Untapped POI Canvas</div>
              <div class="weight-stack">
                <div class="weight-seg" style="width:38%;background:#A3473A">38% Dominant</div>
                <div class="weight-seg" style="width:22%;background:#FF614C">22% 2+ Synergy</div>
                <div class="weight-seg" style="width:22%;background:#246247">22% Unbuilt Land</div>
                <div class="weight-seg" style="width:18%;background:#625753">18% Dry/Shore</div>
              </div>
            </div>
            <div>
              <div style="font-size:11.5px;font-weight:800;margin-bottom:4px">2. Cells · Environmental Edge Collision</div>
              <div class="weight-stack">
                <div class="weight-seg" style="width:42%;background:#0284C7">42% Force Collision</div>
                <div class="weight-seg" style="width:28%;background:#FF614C">28% 2+ Synergy</div>
                <div class="weight-seg" style="width:18%;background:#246247">18% Ecotone Edge</div>
                <div class="weight-seg" style="width:12%;background:#B56E18">12% Nature Prox</div>
              </div>
            </div>
            <div>
              <div style="font-size:11.5px;font-weight:800;margin-bottom:4px">3. Corals · Missing-Link Bridge Catalyst</div>
              <div class="weight-stack">
                <div class="weight-seg" style="width:42%;background:#7C3AED">42% 3+ Trio Synergy</div>
                <div class="weight-seg" style="width:30%;background:#FF614C">30% Bridge/Civic Peak</div>
                <div class="weight-seg" style="width:16%;background:#246247">16% Accessibility</div>
                <div class="weight-seg" style="width:12%;background:#B56E18">12% Nature Prox</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</body>
</html>
"""

    replacements = {
        "__BOUNDS__": json.dumps(bounds),
        "__NX__": str(nx),
        "__NY__": str(ny),
        "__TYP_NAMES__": json.dumps(typ_names),
        "__TYP_COLORS__": json.dumps(typ_hex),
        "__ALL_LAYERS__": json.dumps(all_layers),
        "__ENGINES__": json.dumps(engines_data),
        "__SPACE_TEMPLATES__": json.dumps(space_templates),
        "__EFF_RATIOS__": json.dumps(eff_ratios),
        "__DEMAND_PER_RES__": json.dumps(demand_per_res),
        "__REF_BLD__": json.dumps(ref_buildings),
        "__REF_RD__": json.dumps(ref_roads),
        "__REF_WAT__": json.dumps(ref_water),
        "__HIDDEN_GEMS__": json.dumps(hidden_gems),
        "__COMBINED_OVERLAYS__": json.dumps(combined_overlays or {}),
        "__TOP_SITES__": json.dumps(top_sites or []),
        "__CENTER_LAT__": str(center_lat),
        "__CENTER_LON__": str(center_lon),
    }
    for k, v in replacements.items():
        html = html.replace(k, v)
    return html
