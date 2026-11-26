#!/usr/bin/env python3
"""
NEST 2.3 Interactive Story Mode + Live 3D WebGL Studio Dashboard Builder
========================================================================
Canonical default dashboard generator integrating:
  - NEST Visual Identity (warm off-white #F5F5F5, soft rose #FBEFED, coral #FF614C,
    Funnel Display font, official NEST + DeLab logos embedded as base64 data URIs)
  - Top Split Interactive Stage per Project Card:
      * Left: Live Orbitable 3D WebGL Massing (Three.js r128) built directly from
        each site's organic WGS84 polygons, stepped tiers, hollow courtyards,
        colored landscape zones, and 3D outdoor destinations + 3D Raycasting
        (with quick switcher: Live 3D | 3D Clay | Clean Clay | Satellite | Editorial Render)
      * Right: Live Tri-Layer Leaflet Satellite Mini-Map with full 3-way sync
  - 5-Step Interactive Guided Walkthrough (Story Mode) per Project Card:
      1. Site & Concept (4-Axis Signal Radar SVG + GIS Proximity Pins + Hook & Jury Pull-Line)
      2. Massing Move (Sun/Wind Orientation Compass SVG + Interactive Massing GFA Bars)
      3. Nature Engine (Two-Way Functional Nature Flow Loop SVG + Environmental Guardrail)
      4. Landscape & Experience (100% Proportional Zone Bar + Interactive Zone Cards + 3D Destination Chips)
      5. Feasibility & Blueprint (CapEx Split Donut SVG + Revenue Mix Bars + KPIs + Rhino .3dm)
  - Progressive Disclosure: Optional 'Read full brief' drawer with 3-Act Competition Narrative,
    Space Program table, 3-Engine Traceability & Validation Matrix + Auto-Expand for PDF Print
  - Tab 2: Synchronized 3-Engine Analysis Maps (Crystals, Cells, Corals) from Stage A

Usage:
  python build_nest_dashboard.py --run-dir outputs_south_sinai_83_616 --plot-title "South Sinai — Ras Mohamed (NEST-83-616)"
"""

from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path


def b64_uri(path: Path, mime: str) -> str:
    if not path.exists():
        return ""
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def build_nest_22_dashboard(run_dir: Path, projects: list[dict], plot_title: str, root_dir: Path) -> Path:
    base_dash = run_dir / "intermediates" / "3engines_base_dashboard.html"
    if not base_dash.exists():
        raise FileNotFoundError(f"Missing Stage A base dashboard: {base_dash}")

    base_html = base_dash.read_text(encoding="utf-8")

    # Extract Tab 2 body + script from Stage A 3engines_base_dashboard.html
    body_m = re.search(r"<body>(.*?)</body>", base_html, re.S)
    style_m = re.search(r"<style>(.*?)</style>", base_html, re.S)
    if not body_m or not style_m:
        raise RuntimeError("Could not parse Stage A 3engines_base_dashboard.html")

    tab2_inner = body_m.group(1)
    tab2_css = style_m.group(1)

    # Embed official NEST assets
    ui_dir = root_dir / "UI Handover"
    nest_logo = b64_uri(ui_dir / "logos" / "nest-wordmark-black.png", "image/png") or b64_uri(ui_dir / "logos" / "nest-wordmark-black.svg", "image/svg+xml")
    delab_logo = b64_uri(ui_dir / "logos" / "delab-colour.png", "image/png") or b64_uri(ui_dir / "logos" / "delab-colour.svg", "image/svg+xml")
    font_uri = b64_uri(ui_dir / "fonts" / "FunnelDisplay.ttf", "font/ttf")
    font_face_css = f"{font_face_css}" if font_uri else ""

    # Detect whether optional external editorial renders exist & ensure asset paths
    for p in projects:
        rk = p["rank"]
        p.setdefault("massing_lock", f"renders/render_pack/site_{rk}_massing_lock.png")
        p.setdefault("massing_lock_clean", f"renders/render_pack/site_{rk}_massing_lock_clean.png")
        p.setdefault("satellite_lock", f"renders/render_pack/site_{rk}_satellite_lock.png")
        p.setdefault("rhino_3dm", f"models/site_{rk}_massing.3dm")
        p.setdefault("rhino_3dm_path", f"models/site_{rk}_massing.3dm")
        p.setdefault("render_prompt", f"renders/render_pack/site_{rk}_prompt.md")
        p.setdefault("render_prompt_path", f"renders/render_pack/site_{rk}_prompt.md")
        ext_render = run_dir / "renders" / f"site_{rk}.jpg"
        p["has_editorial_render"] = ext_render.exists()
        if p["has_editorial_render"]:
            p["render"] = f"renders/site_{rk}.jpg"

    nest_css = f"""
{font_face_css}
:root {{
  --nest-paper: #F5F5F5; --nest-soft: #FBEFED; --nest-rose: #DDA199;
  --nest-coral: #FF614C; --nest-coral-hi: #FF735F; --nest-edge: #A3473A;
  --nest-ink: #302B2A; --nest-muted: #625753; --nest-line: #D5C9C5;
  --nest-ok: #246247; --nest-ok-bg: #EAF5EF;
  --nest-warn: #775014; --nest-warn-bg: #FFF5E5;
  --nest-err: #A12B3A; --nest-err-bg: #FCEEF0;
}}
* {{ box-sizing: border-box; }}
html, body {{ height: 100%; margin: 0; font-family: 'Funnel Display', 'Segoe UI', system-ui, sans-serif; background: var(--nest-paper); color: var(--nest-ink); display: flex; flex-direction: column; overflow: hidden; }}
.nest-shell-hdr {{ border-top: 4px solid var(--nest-rose); background: #FFFFFF; border-bottom: 1px solid var(--nest-line); padding: 10px 22px; display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; z-index: 1100; flex: none; }}
.nest-brand {{ display: flex; align-items: center; gap: 14px; }}
.nest-brand img.nest {{ height: 26px; }}
.nest-brand img.delab {{ height: 22px; }}
.nest-plot-lbl {{ font-size: 13px; color: var(--nest-muted); border-left: 1px solid var(--nest-line); padding-left: 12px; font-weight: 600; }}
.nest-main-tabs {{ display: inline-flex; gap: 6px; align-items: center; }}
.mtab-btn {{ padding: 7px 14px; border-radius: 9px; border: 1px solid var(--nest-line); background: #FFFFFF; color: var(--nest-ink); font-family: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer; }}
.mtab-btn:hover {{ background: var(--nest-soft); border-color: var(--nest-edge); }}
.mtab-btn.active {{ background: var(--nest-coral); color: #302B2A; border-color: var(--nest-edge); box-shadow: 0 3px 0 var(--nest-edge); }}
#tab-proposals {{ flex: 1; overflow-y: auto; padding: 18px 22px 54px; background: var(--nest-paper); }}
#tab-maps {{ flex: 1; display: none; flex-direction: column; min-height: 0; overflow: hidden; }}
.prop-toolbar {{ max-width: 1380px; margin: 0 auto 16px; display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 12px; padding: 10px 16px; }}
.jump-bar {{ display: inline-flex; gap: 6px; flex-wrap: wrap; align-items: center; }}
.jbtn {{ padding: 5px 11px; border-radius: 8px; border: 1px solid var(--nest-line); background: var(--nest-soft); color: var(--nest-ink); font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; text-decoration: none; }}
.jbtn:hover {{ border-color: var(--nest-edge); background: #FFFFFF; }}
.tb-actions {{ display: inline-flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
.btn-coral {{ display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; border-radius: 9px; background: var(--nest-coral); color: #302B2A; border: 1px solid var(--nest-edge); box-shadow: 0 3px 0 var(--nest-edge); font-family: inherit; font-size: 12px; font-weight: 800; cursor: pointer; text-decoration: none; }}
.btn-coral:hover {{ background: var(--nest-coral-hi); }}
.btn-outline {{ display: inline-flex; align-items: center; gap: 6px; padding: 7px 12px; border-radius: 9px; background: #FFFFFF; color: var(--nest-ink); border: 1px solid var(--nest-line); font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; text-decoration: none; }}
.btn-outline:hover {{ background: var(--nest-soft); border-color: var(--nest-edge); }}

.cards-stack {{ max-width: 1380px; margin: 0 auto; display: flex; flex-direction: column; gap: 28px; }}
.proj-card {{ background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 18px; overflow: hidden; box-shadow: 0 10px 28px rgba(48,43,42,0.07); }}

/* Top Split Visual Stage (Live 3D WebGL + Live Leaflet Satellite Map) */
.card-visuals {{ display: grid; grid-template-columns: 1.2fr 1fr; border-bottom: 1px solid var(--nest-line); }}
@media (max-width: 980px) {{ .card-visuals {{ grid-template-columns: 1fr; }} }}
.render-wrap {{ position: relative; background: #F3EFEA; height: 420px; overflow: hidden; }}
.webgl-stage {{ width: 100%; height: 100%; cursor: grab; display: block; }}
.webgl-stage:active {{ cursor: grabbing; }}
.render-wrap img.static-media {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: none; z-index: 3; }}
.render-wrap.show-img img.static-media {{ display: block; }}
.render-wrap.show-img .webgl-hud, .render-wrap.show-img .webgl-hint {{ display: none; }}
.rank-chip {{ position: absolute; top: 12px; left: 12px; z-index: 6; background: rgba(48,43,42,0.92); color: #FFFAF7; padding: 5px 12px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 0.02em; }}
.media-toggle-bar {{ position: absolute; top: 12px; right: 12px; z-index: 7; display: inline-flex; gap: 3px; background: rgba(255,250,247,0.96); border: 1px solid var(--nest-line); border-radius: 9px; padding: 3px; box-shadow: 0 4px 12px rgba(48,43,42,0.16); }}
.media-tbtn {{ border: 0; background: transparent; color: var(--nest-ink); font-family: inherit; font-size: 11px; font-weight: 700; padding: 5px 9px; border-radius: 6px; cursor: pointer; }}
.media-tbtn.active {{ background: var(--nest-coral); color: #302B2A; box-shadow: 0 2px 0 var(--nest-edge); }}
.webgl-hint {{ position: absolute; bottom: 10px; right: 12px; z-index: 6; background: rgba(48,43,42,0.78); color: #FFFAF7; padding: 4px 10px; border-radius: 999px; font-size: 10.5px; font-weight: 600; pointer-events: none; }}
.webgl-hud {{ position: absolute; bottom: 10px; left: 12px; z-index: 6; max-width: 68%; background: rgba(255,250,247,0.96); border: 1px solid var(--nest-edge); border-left: 4px solid var(--nest-coral); border-radius: 10px; padding: 7px 11px; font-size: 11.5px; color: var(--nest-ink); box-shadow: 0 6px 16px rgba(48,43,42,0.16); display: none; }}
.webgl-hud.visible {{ display: block; }}
.webgl-hud .hud-k {{ font-size: 9.5px; text-transform: uppercase; font-weight: 800; color: var(--nest-edge); letter-spacing: 0.05em; }}
.webgl-hud .hud-t {{ font-weight: 800; font-size: 12.5px; margin: 1px 0 2px; }}
.webgl-hud .hud-d {{ font-size: 11px; color: var(--nest-muted); line-height: 1.35; }}

.mini-map-wrap {{ position: relative; height: 420px; border-left: 1px solid var(--nest-line); }}
.mini-map {{ width: 100%; height: 100%; }}
.map-legend-pill {{ position: absolute; bottom: 44px; left: 10px; z-index: 800; background: rgba(255,250,247,0.94); border: 1px solid var(--nest-line); border-radius: 9px; padding: 4px 10px; font-size: 10.5px; display: flex; gap: 9px; flex-wrap: wrap; color: var(--nest-ink); font-weight: 600; }}
.map-meta-bar {{ position: absolute; bottom: 8px; left: 10px; right: 10px; z-index: 800; display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; }}
.map-coord-pill {{ background: rgba(48,43,42,0.88); color: #FFFAF7; padding: 4px 10px; border-radius: 8px; font-size: 11px; }}
.jump-map-btn {{ padding: 4px 10px; border-radius: 8px; border: 1px solid var(--nest-edge); background: var(--nest-coral); color: #302B2A; font-family: inherit; font-size: 11px; font-weight: 800; cursor: pointer; }}
.mini-btn {{ padding: 4px 9px; border-radius: 7px; border: 1px solid var(--nest-line); background: #FFFFFF; color: var(--nest-edge); font-family: inherit; font-size: 11px; font-weight: 700; cursor: pointer; }}
.mini-btn:hover {{ background: var(--nest-soft); border-color: var(--nest-edge); }}

/* Compact Card Title Header */
.card-head-bar {{ padding: 16px 24px 14px; background: linear-gradient(180deg, #FFFAF7, #FFFFFF); border-bottom: 1px solid var(--nest-line); display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; }}
.card-head-bar h2 {{ margin: 0 0 3px; font-size: 24px; line-height: 1.15; color: var(--nest-ink); letter-spacing: -0.01em; }}
.card-head-bar .sub {{ font-size: 13px; color: var(--nest-muted); margin-bottom: 8px; }}
.badge-row {{ display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }}
.pill {{ display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; border: 1px solid var(--nest-line); background: #FFFFFF; color: var(--nest-ink); }}
.pill.tier {{ background: var(--nest-warn-bg); color: var(--nest-warn); border-color: #E2BE84; }}
.pill.ok {{ background: var(--nest-ok-bg); color: var(--nest-ok); border-color: #9CCAB1; }}
.pill.warn {{ background: var(--nest-warn-bg); color: var(--nest-warn); border-color: #E2BE84; }}

/* Story Mode Stepper Bar */
.story-nav {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 10px 24px; background: var(--nest-soft); border-bottom: 1px solid var(--nest-line); flex-wrap: wrap; }}
.story-steps {{ display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }}
.step-pill {{ display: inline-flex; align-items: center; gap: 7px; padding: 6px 13px; border-radius: 999px; border: 1px solid var(--nest-line); background: #FFFFFF; color: var(--nest-muted); font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; transition: all 140ms ease; }}
.step-pill:hover {{ border-color: var(--nest-edge); color: var(--nest-ink); }}
.step-pill.active {{ background: var(--nest-coral); color: #302B2A; border-color: var(--nest-edge); box-shadow: 0 2px 0 var(--nest-edge); }}
.step-num {{ width: 19px; height: 19px; border-radius: 50%; background: rgba(48,43,42,0.1); display: inline-flex; align-items: center; justify-content: center; font-size: 10.5px; font-weight: 800; }}
.step-pill.active .step-num {{ background: #302B2A; color: #FFFAF7; }}
.story-arrows {{ display: inline-flex; gap: 6px; align-items: center; }}
.arr-btn {{ padding: 6px 12px; border-radius: 8px; border: 1px solid var(--nest-line); background: #FFFFFF; color: var(--nest-ink); font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; }}
.arr-btn:hover {{ background: #FFFFFF; border-color: var(--nest-edge); color: var(--nest-edge); }}

/* Story Step Panels */
.story-stage {{ padding: 20px 24px 22px; background: #FFFFFF; }}
.story-pane {{ display: none; animation: fadeSlide 220ms ease; }}
.story-pane.active {{ display: block; }}
@keyframes fadeSlide {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}

.story-grid {{ display: grid; grid-template-columns: 1fr 1.15fr; gap: 18px; align-items: stretch; }}
@media (max-width: 900px) {{ .story-grid {{ grid-template-columns: 1fr; }} }}
.diag-card {{ background: #FFFAF7; border: 1px solid var(--nest-line); border-radius: 14px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: center; }}
.diag-lbl {{ font-size: 10.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: var(--nest-edge); margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
.hook-hero {{ font-size: 17px; font-weight: 700; line-height: 1.42; color: var(--nest-ink); margin-bottom: 12px; }}
.pull-banner {{ padding: 10px 14px; border-left: 4px solid var(--nest-coral); background: var(--nest-soft); border-radius: 0 10px 10px 0; font-size: 13.5px; font-weight: 700; font-style: italic; color: var(--nest-edge); margin-bottom: 12px; }}
.micro-chips {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
@media (max-width: 680px) {{ .micro-chips {{ grid-template-columns: 1fr; }} }}
.mchip {{ background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 10px; padding: 9px 11px; font-size: 12px; line-height: 1.4; }}
.mchip .mk {{ font-size: 10px; font-weight: 800; text-transform: uppercase; color: var(--nest-edge); letter-spacing: 0.05em; margin-bottom: 3px; }}

/* Interactive Pin Chips */
.pin-row {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }}
.pin-btn {{ display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 999px; background: #FFFFFF; border: 1px solid var(--nest-line); font-family: inherit; font-size: 11px; font-weight: 700; color: var(--nest-ink); cursor: pointer; }}
.pin-btn:hover {{ border-color: var(--nest-coral); background: var(--nest-soft); }}
.pin-dot {{ width: 16px; height: 16px; border-radius: 50%; background: var(--nest-edge); color: #FFFAF7; font-size: 9.5px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; }}

/* Interactive Massing GFA Bars (Step 2) */
.mass-bar-list {{ display: flex; flex-direction: column; gap: 9px; }}
.mass-bar-item {{ background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 11px; padding: 10px 12px; cursor: pointer; transition: all 140ms ease; }}
.mass-bar-item:hover, .mass-bar-item.active-item {{ border-color: var(--nest-coral); background: var(--nest-soft); transform: translateX(3px); }}
.mb-top {{ display: flex; justify-content: space-between; align-items: baseline; gap: 8px; margin-bottom: 5px; }}
.mb-name {{ font-weight: 800; font-size: 13px; color: var(--nest-ink); }}
.mb-stat {{ font-size: 11.5px; font-weight: 800; color: var(--nest-edge); white-space: nowrap; }}
.mb-track {{ height: 8px; border-radius: 999px; background: #EFE6E3; overflow: hidden; margin-bottom: 5px; }}
.mb-fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--nest-edge), var(--nest-coral)); }}
.mb-desc {{ font-size: 11.5px; color: var(--nest-muted); line-height: 1.35; }}

/* Nature Loop Diagram (Step 3) */
.nature-loop-wrap {{ display: grid; grid-template-columns: 1fr 140px 1fr; gap: 14px; align-items: center; }}
@media (max-width: 860px) {{ .nature-loop-wrap {{ grid-template-columns: 1fr; }} }}
.nat-col {{ display: flex; flex-direction: column; gap: 8px; }}
.nat-node {{ background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 11px; padding: 10px 13px; }}
.nat-node.in {{ border-left: 4px solid #246247; background: #F5FBF8; }}
.nat-node.out {{ border-right: 4px solid var(--nest-coral); background: #FFF8F6; }}
.nat-k {{ font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }}
.nat-node.in .nat-k {{ color: #246247; }}
.nat-node.out .nat-k {{ color: var(--nest-edge); }}
.nat-v {{ font-size: 12.5px; line-height: 1.45; color: var(--nest-ink); }}
.nat-badges {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 7px; }}
.nat-stat-pill {{ display: inline-block; padding: 3px 9px; border-radius: 999px; font-size: 11px; font-weight: 800; background: #FFFFFF; border: 1px solid var(--nest-line); color: var(--nest-ink); }}
.risk-strip {{ margin-top: 12px; padding: 9px 13px; border-radius: 10px; background: var(--nest-warn-bg); border: 1px solid #E2BE84; border-left: 4px solid #B56E18; color: var(--nest-warn); font-size: 12px; line-height: 1.42; }}

/* Landscape Proportional Bar + Zone Cards (Step 4) */
.zstack-bar {{ display: flex; height: 28px; border-radius: 10px; overflow: hidden; border: 1px solid var(--nest-line); margin-bottom: 12px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.08); }}
.zstack-seg {{ display: flex; align-items: center; justify-content: center; color: #FFFFFF; font-size: 11px; font-weight: 800; cursor: pointer; transition: filter 130ms ease; overflow: hidden; white-space: nowrap; padding: 0 4px; }}
.zstack-seg:hover {{ filter: brightness(1.12); }}
.zone-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 12px; }}
@media (max-width: 980px) {{ .zone-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
@media (max-width: 560px) {{ .zone-grid {{ grid-template-columns: 1fr; }} }}
.zone-tile {{ background: #FFFFFF; border: 1px solid var(--nest-line); border-top: 4px solid var(--zc, #246247); border-radius: 11px; padding: 10px 11px; cursor: pointer; transition: all 140ms ease; }}
.zone-tile:hover, .zone-tile.active-item {{ background: var(--nest-soft); border-color: var(--nest-edge); transform: translateY(-2px); }}
.zt-top {{ display: flex; justify-content: space-between; align-items: center; gap: 6px; margin-bottom: 4px; }}
.zt-pct {{ font-size: 16px; font-weight: 800; color: var(--nest-ink); }}
.zt-name {{ font-size: 12px; font-weight: 800; color: var(--nest-ink); margin-bottom: 4px; line-height: 1.25; }}
.zt-act {{ font-size: 11px; color: var(--nest-muted); line-height: 1.35; }}
.el-chip {{ display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; background: #FFFAF7; border: 1px solid var(--nest-line); color: var(--nest-ink); cursor: pointer; margin: 2px 5px 3px 0; }}
.el-chip:hover, .el-chip.active-item {{ border-color: var(--nest-coral); background: var(--nest-soft); color: var(--nest-edge); }}

/* Financials Donut + Bars (Step 5) */
.fin-kpi-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 9px; margin-bottom: 10px; }}
.kpi-tile {{ background: #FFFAF7; border: 1px solid var(--nest-line); border-radius: 11px; padding: 10px 12px; }}
.kpi-tile .k {{ font-size: 10px; text-transform: uppercase; color: var(--nest-muted); font-weight: 800; }}
.kpi-tile .v {{ font-size: 20px; font-weight: 800; color: var(--nest-ink); margin-top: 2px; }}
.kpi-tile .s {{ font-size: 10.5px; color: var(--nest-muted); margin-top: 2px; }}
.rev-bar-row {{ margin-bottom: 8px; }}
.rev-bar-hdr {{ display: flex; justify-content: space-between; font-size: 11.5px; font-weight: 700; margin-bottom: 3px; }}
.rev-track {{ height: 7px; border-radius: 999px; background: #EFE6E3; overflow: hidden; }}
.rev-fill {{ height: 100%; border-radius: 999px; background: var(--nest-coral); }}
.action-bar {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--nest-line); }}

/* Full Brief Progressive Disclosure Drawer */
.full-brief-drawer {{ display: none; padding: 18px 24px 24px; background: #FAF7F5; border-top: 1px dashed var(--nest-line); }}
.proj-card.brief-open .full-brief-drawer, body.show-detailed .full-brief-drawer {{ display: block; }}
.two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }}
@media (max-width: 900px) {{ .two-col {{ grid-template-columns: 1fr; }} }}
.box {{ background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 12px; padding: 13px 15px; font-size: 12.5px; line-height: 1.5; }}
.sec-lbl {{ font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--nest-edge); border-left: 3px solid var(--nest-edge); padding-left: 8px; margin-bottom: 8px; }}
.prog-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
.prog-table th, .prog-table td {{ padding: 6px 8px; border-bottom: 1px solid #ECE2DF; text-align: left; vertical-align: top; }}
.prog-table th {{ font-size: 10px; text-transform: uppercase; color: var(--nest-muted); background: #FFFAF7; }}
.prog-table td.num {{ text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }}
.narrative-body p {{ margin: 0 0 8px; }}
.narrative-body p:last-child {{ margin-bottom: 0; }}
.jury-pull-line {{ display: block; margin-top: 8px; padding-left: 10px; border-left: 3px solid var(--nest-coral); font-weight: 700; font-style: italic; color: var(--nest-edge); }}

/* Print / PDF Auto-Expand */
body.print-all .story-pane {{ display: block !important; margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid var(--nest-line); }}
body.print-all .full-brief-drawer {{ display: block !important; }}
@media print {{
  @page {{ size: A4 landscape; margin: 9mm 10mm; }}
  html, body {{ height: auto; overflow: visible; }}
  .nest-shell-hdr, .prop-toolbar, .media-toggle-bar, .story-nav, .action-bar, .jump-map-btn, .webgl-hint {{ display: none !important; }}
  #tab-proposals {{ overflow: visible; padding: 0; }}
  #tab-maps {{ display: none !important; }}
  .story-pane {{ display: block !important; margin-bottom: 14px; }}
  .full-brief-drawer {{ display: block !important; }}
  .proj-card {{ break-after: page; box-shadow: none; }}
}}
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>NEST — {plot_title}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<style>
{tab2_css}
{nest_css}
</style>
</head>
<body>
<header class="nest-shell-hdr">
  <div class="nest-brand">
    <img class="nest" src="{nest_logo}" alt="NEST" />
    <img class="delab" src="{delab_logo}" alt="DeLab" />
    <span class="nest-plot-lbl">{plot_title} • Interactive Story Mode &amp; Live 3D Studio</span>
  </div>
  <div class="nest-main-tabs">
    <button type="button" id="btn-tab-proposals" class="mtab-btn active" onclick="switchMainTab('proposals')">Project Proposals ({len(projects)} Interactive Cards)</button>
    <button type="button" id="btn-tab-maps" class="mtab-btn" onclick="switchMainTab('maps')">3-Engine Analysis Maps</button>
  </div>
</header>

<section id="tab-proposals">
  <div class="prop-toolbar">
    <div id="jump-bar" class="jump-bar"><span style="font-size:11.5px;font-weight:800;color:#625753;margin-right:4px">JUMP TO SITE:</span></div>
    <div class="tb-actions">
      <button type="button" id="btn-detail-toggle" class="btn-outline" onclick="toggleDetailed()">Story Mode | Full Dossiers</button>
      <a class="btn-outline" href="renders/render_pack/ALL_PROMPTS_CONSOLIDATED.md" target="_blank">Render Pack Prompts ↗</a>
      <button type="button" class="btn-coral" onclick="exportProposalsPdf()">⬇ Export Proposals PDF</button>
    </div>
  </div>
  <div id="cards-stack" class="cards-stack"></div>
</section>

<section id="tab-maps">
{tab2_inner}
</section>

<script>
const NEST_PROJECTS = {json.dumps(projects)};
const miniMaps = [];
const miniMapRegistry = {{}};
const webglRegistry = {{}};
const cardStepState = {{}};

const STORY_LABELS = [
  ['1', 'The Experience'],
  ['2', 'Constellation'],
  ['3', 'Nature & Landscape'],
  ['4', 'Site & GIS'],
  ['5', 'Feasibility']
];

// --- HELPER PARSERS FOR REAL-DATA SVG DIAGRAMS ---
function parseNumber(str, fallback = 0) {{
  if (typeof str === 'number') return str;
  const m = String(str || '').replace(/,/g, '').match(/-?\d+(\.\d+)?/);
  return m ? parseFloat(m[0]) : fallback;
}}

function parseAngleDeg(orientationStr) {{
  const m = String(orientationStr || '').match(/([+-]?\d+(?:\.\d+)?)\s*°/);
  return m ? parseFloat(m[1]) : 0;
}}

function parseHeightMeters(hStr, isBridge) {{
  if (isBridge) return 4.5;
  const m = String(hStr || '').match(/(\d+(?:\.\d+)?)\s*m/);
  return m ? parseFloat(m[1]) : 10.5;
}}

function parseTiers(hStr) {{
  const m = String(hStr || '').match(/(\d+)\s*(?:tier|stepped|floor|stor)/i);
  return m ? Math.min(Math.max(parseInt(m[1], 10), 1), 6) : 2;
}}

function extractPullLine(txt) {{
  if (!txt) return '';
  const paras = txt.split(/\\n\\s*\\n/).map(s => s.trim()).filter(Boolean);
  if (!paras.length) return '';
  const sents = paras[paras.length - 1].split(/(?<=[.!?])\\s+/);
  return sents[sents.length - 1] || '';
}}

function extractStatBadges(txt) {{
  const matches = String(txt || '').match(/(?:\d[\d,\.]*\+?\s*(?:%|°C|kWh\/m²\/yr|m²|m|feddans|saplings|levels))/gi) || [];
  return [...new Set(matches)].slice(0, 3);
}}

function formatDetailedNarrative(txt) {{
  if (!txt) return '';
  const paras = txt.split(/\\n\\s*\\n/).map(s => s.trim()).filter(Boolean);
  return paras.map((par, idx) => {{
    if (idx === paras.length - 1) {{
      const sents = par.split(/(?<=[.!?])\\s+/);
      if (sents.length > 1) {{
        const pull = sents.pop();
        return `<p>${{sents.join(' ')}}</p><span class="jury-pull-line">“${{pull}}”</span>`;
      }}
    }}
    return `<p>${{par}}</p>`;
  }}).join('');
}}

// --- CUSTOM INTERACTIVE SVG ARCHITECTURAL DIAGRAMS ---
function buildSignalRadarSVG(p) {{
  const vals = [
    {{ lbl: 'Crystals', v: p.scores.crystals || 0 }},
    {{ lbl: 'Cells', v: p.scores.cells || 0 }},
    {{ lbl: 'Corals', v: p.scores.corals || 0 }},
    {{ lbl: 'Access', v: p.access || 0 }}
  ];
  const cx = 135, cy = 96, R = 64;
  const angles = [-Math.PI/2, 0, Math.PI/2, Math.PI];
  const pt = (val, i) => {{
    const r = (Math.min(Math.max(val, 0), 100) / 100) * R;
    return [cx + Math.cos(angles[i]) * r, cy + Math.sin(angles[i]) * r];
  }};
  const polyPts = vals.map((d, i) => pt(d.v, i).map(n => n.toFixed(1)).join(',')).join(' ');
  const rings = [0.33, 0.66, 1.0].map(f => {{
    const rpts = angles.map(a => `${{(cx + Math.cos(a)*R*f).toFixed(1)}},${{(cy + Math.sin(a)*R*f).toFixed(1)}}`).join(' ');
    return `<polygon points="${{rpts}}" fill="none" stroke="#E4D8D4" stroke-width="1"/>`;
  }}).join('');
  const axes = angles.map((a, i) => {{
    const x2 = cx + Math.cos(a)*R, y2 = cy + Math.sin(a)*R;
    const lx = cx + Math.cos(a)*(R + 24), ly = cy + Math.sin(a)*(R + 18) + 4;
    return `<line x1="${{cx}}" y1="${{cy}}" x2="${{x2.toFixed(1)}}" y2="${{y2.toFixed(1)}}" stroke="#D5C9C5" stroke-width="1"/>` +
           `<text x="${{lx.toFixed(1)}}" y="${{ly.toFixed(1)}}" text-anchor="middle" font-size="10" font-weight="800" fill="#625753">${{vals[i].lbl}} ${{vals[i].v}}</text>`;
  }}).join('');
  const dots = vals.map((d, i) => {{
    const [x, y] = pt(d.v, i);
    return `<circle cx="${{x.toFixed(1)}}" cy="${{y.toFixed(1)}}" r="4" fill="#FF614C" stroke="#A3473A" stroke-width="1.5"/>`;
  }}).join('');
  return `<svg viewBox="0 0 270 192" style="width:100%;max-height:185px;display:block;margin:0 auto">
    ${{rings}}${{axes}}
    <polygon points="${{polyPts}}" fill="rgba(255,97,76,0.24)" stroke="#FF614C" stroke-width="2.2"/>
    ${{dots}}
  </svg>`;
}}

function buildCompassSVG(p) {{
  const mr = p.massing_rationale || {{}};
  const deg = parseAngleDeg(mr.orientation);
  const cx = 135, cy = 96, R = 64;
  return `<svg viewBox="0 0 270 192" style="width:100%;max-height:185px;display:block;margin:0 auto">
    <defs>
      <marker id="arr-coral-${{p.rank}}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M0,1 L9,5 L0,9 z" fill="#FF614C"/>
      </marker>
      <marker id="arr-wind-${{p.rank}}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M0,1 L9,5 L0,9 z" fill="#246247"/>
      </marker>
    </defs>
    <!-- Sun arc (East -> South -> West) -->
    <path d="M ${{cx+R+14}} ${{cy+4}} A ${{R+14}} ${{R+14}} 0 0 1 ${{cx-R-14}} ${{cy+4}}" fill="none" stroke="#E5A23C" stroke-width="2" stroke-dasharray="4 4"/>
    <circle cx="${{cx+R+14}}" cy="${{cy+4}}" r="4.5" fill="#E5A23C"/>
    <text x="${{cx}}" y="${{cy+R+26}}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#9A6714">Solar Arc (2,300+ kWh/m²/yr)</text>
    <!-- Compass ring -->
    <circle cx="${{cx}}" cy="${{cy}}" r="${{R}}" fill="#FFFFFF" stroke="#D5C9C5" stroke-width="1.5"/>
    <circle cx="${{cx}}" cy="${{cy}}" r="${{R-16}}" fill="none" stroke="#EFE6E3" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="${{cx}}" y="${{cy-R-6}}" text-anchor="middle" font-size="10" font-weight="800" fill="#302B2A">N</text>
    <text x="${{cx+R+10}}" y="${{cy+4}}" text-anchor="start" font-size="9.5" font-weight="700" fill="#625753">E</text>
    <text x="${{cx-R-10}}" y="${{cy+4}}" text-anchor="end" font-size="9.5" font-weight="700" fill="#625753">W</text>
    <!-- Prevailing Wind vector -->
    <line x1="${{cx-44}}" y1="${{cy-44}}" x2="${{cx-14}}" y2="${{cy-14}}" stroke="#246247" stroke-width="2" marker-end="url(#arr-wind-${{p.rank}})"/>
    <text x="${{cx-50}}" y="${{cy-48}}" text-anchor="end" font-size="9" font-weight="800" fill="#246247">Breeze</text>
    <!-- Building Orientation Axis -->
    <g transform="rotate(${{deg}} ${{cx}} ${{cy}})">
      <rect x="${{cx-36}}" y="${{cy-11}}" width="72" height="22" rx="11" fill="rgba(255,97,76,0.22)" stroke="#A3473A" stroke-width="1.8"/>
      <line x1="${{cx-48}}" y1="${{cy}}" x2="${{cx+48}}" y2="${{cy}}" stroke="#FF614C" stroke-width="2.2" marker-end="url(#arr-coral-${{p.rank}})"/>
    </g>
    <circle cx="${{cx}}" cy="${{cy}}" r="3.5" fill="#302B2A"/>
    <text x="${{cx}}" y="15" text-anchor="middle" font-size="10.5" font-weight="800" fill="#A3473A">Axis Rotation: ${{deg > 0 ? '+' : ''}}${{deg}}°</text>
  </svg>`;
}}

function buildNatureCenterSVG() {{
  return `<svg viewBox="0 0 140 130" style="width:100%;max-width:136px;display:block;margin:0 auto">
    <defs>
      <marker id="ar-g" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="#246247"/></marker>
      <marker id="ar-c" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="#FF614C"/></marker>
    </defs>
    <path d="M 22 38 C 46 12, 94 12, 118 38" fill="none" stroke="#246247" stroke-width="2.6" marker-end="url(#ar-g)"/>
    <text x="70" y="16" text-anchor="middle" font-size="8.5" font-weight="800" fill="#246247">PASSIVE INPUTS</text>
    <circle cx="70" cy="65" r="27" fill="#FBEFED" stroke="#A3473A" stroke-width="2"/>
    <text x="70" y="62" text-anchor="middle" font-size="9.5" font-weight="800" fill="#302B2A">SITE +</text>
    <text x="70" y="74" text-anchor="middle" font-size="9.5" font-weight="800" fill="#A3473A">BUILDING</text>
    <path d="M 118 92 C 94 118, 46 118, 22 92" fill="none" stroke="#FF614C" stroke-width="2.6" marker-end="url(#ar-c)"/>
    <text x="70" y="122" text-anchor="middle" font-size="8.5" font-weight="800" fill="#A3473A">ECOLOGICAL RETURN</text>
  </svg>`;
}}

function buildCapexDonutSVG(p) {{
  const bldg = parseNumber((p.fin || {{}}).capex_bldg, 60);
  const land = parseNumber((p.fin || {{}}).capex_landscape, 20);
  const tot = Math.max(bldg + land, 1);
  const bPct = Math.round((bldg / tot) * 100);
  const lPct = 100 - bPct;
  const r = 48, C = 2 * Math.PI * r;
  const bDash = (bldg / tot) * C;
  return `<svg viewBox="0 0 220 140" style="width:100%;max-height:145px;display:block;margin:0 auto">
    <g transform="translate(74, 70)">
      <circle r="${{r}}" fill="none" stroke="#246247" stroke-width="18"/>
      <circle r="${{r}}" fill="none" stroke="#FF614C" stroke-width="18" stroke-dasharray="${{bDash.toFixed(1)}} ${{C.toFixed(1)}}" transform="rotate(-90)"/>
      <text y="-3" text-anchor="middle" font-size="9" font-weight="700" fill="#625753">TOTAL CAPEX</text>
      <text y="13" text-anchor="middle" font-size="14" font-weight="800" fill="#302B2A">${{(p.fin || {{}}).capex || '—'}}</text>
    </g>
    <g transform="translate(140, 44)">
      <rect width="10" height="10" rx="2" fill="#FF614C"/><text x="15" y="9" font-size="10.5" font-weight="800" fill="#302B2A">Building ${{bPct}}%</text>
      <text x="15" y="22" font-size="10" fill="#625753">${{(p.fin || {{}}).capex_bldg || '—'}}</text>
      <rect y="36" width="10" height="10" rx="2" fill="#246247"/><text x="15" y="45" font-size="10.5" font-weight="800" fill="#302B2A">Landscape ${{lPct}}%</text>
      <text x="15" y="58" font-size="10" fill="#625753">${{(p.fin || {{}}).capex_landscape || '—'}}</text>
    </g>
  </svg>`;
}}

// --- LIVE THREE.JS 3D MASSING ENGINE (CLASSIC UMD, ZERO CORS ISSUES ON FILE://) ---
function initWebGL3D(p) {{
  const container = document.getElementById('webgl-stage-' + p.rank);
  const wrap = document.getElementById('render-wrap-' + p.rank);
  if (!container || typeof THREE === 'undefined') {{
    if (wrap) wrap.classList.add('show-img');
    return;
  }}

  const W = container.clientWidth || 540;
  const H = container.clientHeight || 420;
  let renderer;
  try {{
    renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false }});
  }} catch (e) {{
    if (wrap) wrap.classList.add('show-img');
    return;
  }}
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(W, H);
  renderer.setClearColor(0xF3EFEA, 1);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0xF3EFEA, 900, 2600);

  const camera = new THREE.PerspectiveCamera(40, W / H, 1, 5000);

  // Architectural Studio Lighting
  const hemi = new THREE.HemisphereLight(0xFFFDF8, 0xD8CFC7, 0.88);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xFFF3E2, 0.92);
  sun.position.set(260, 420, 190);
  sun.castShadow = true;
  sun.shadow.mapSize.width = 1024;
  sun.shadow.mapSize.height = 1024;
  sun.shadow.camera.near = 20;
  sun.shadow.camera.far = 1400;
  const d = 420;
  sun.shadow.camera.left = -d; sun.shadow.camera.right = d;
  sun.shadow.camera.top = d; sun.shadow.camera.bottom = -d;
  scene.add(sun);
  const rim = new THREE.DirectionalLight(0xDCEAF5, 0.28);
  rim.position.set(-220, 160, -240);
  scene.add(rim);

  // Coordinate projection WGS84 -> local meters (X=East, Z=South so Y=Up matches north-up map)
  const mLat = 111320.0;
  const mLon = 111320.0 * Math.cos(p.lat * Math.PI / 180.0);
  const toXZ = ([lon, lat]) => [(lon - p.lon) * mLon, -(lat - p.lat) * mLat];

  function geomToPolys(geom) {{
    if (!geom) return [];
    if (geom.type === 'Polygon') return [geom.coordinates];
    if (geom.type === 'MultiPolygon') return geom.coordinates;
    return [];
  }}

  function polyToShape(rings) {{
    if (!rings || !rings.length || rings[0].length < 3) return null;
    const shape = new THREE.Shape();
    rings[0].forEach((pt, idx) => {{
      const [x, z] = toXZ(pt);
      // Shape is built in XY then rotated -90 deg around X -> (x, y) becomes (x, 0, -y)
      if (idx === 0) shape.moveTo(x, -z);
      else shape.lineTo(x, -z);
    }});
    shape.closePath();
    for (let h = 1; h < rings.length; h++) {{
      if (rings[h].length < 3) continue;
      const hole = new THREE.Path();
      rings[h].forEach((pt, idx) => {{
        const [x, z] = toXZ(pt);
        if (idx === 0) hole.moveTo(x, -z);
        else hole.lineTo(x, -z);
      }});
      hole.closePath();
      shape.holes.push(hole);
    }}
    return shape;
  }}

  function polyCenterXZ(geom) {{
    const polys = geomToPolys(geom);
    if (!polys.length || !polys[0].length) return [0, 0];
    let sx = 0, sz = 0, n = 0;
    polys[0][0].forEach(pt => {{
      const [x, z] = toXZ(pt);
      sx += x; sz += z; n++;
    }});
    return n ? [sx / n, sz / n] : [0, 0];
  }}

  // Subtle Ground Plinth
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(3600, 3600),
    new THREE.MeshStandardMaterial({{ color: 0xECE5DD, roughness: 0.96, metalness: 0.0 }})
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.35;
  ground.receiveShadow = true;
  scene.add(ground);

  const pickables = [];
  const meshGroups = {{ zones: [], elements: [], footprints: [] }};

  // 1. Organic Parcel Boundary Ribbon
  let siteRadius = 320;
  geomToPolys(p.geojson).forEach(rings => {{
    if (!rings.length) return;
    const pts = [];
    let maxR = 120;
    rings[0].forEach(c => {{
      const [x, z] = toXZ(c);
      pts.push(new THREE.Vector3(x, 0.8, z));
      maxR = Math.max(maxR, Math.hypot(x, z));
    }});
    siteRadius = Math.max(siteRadius, maxR);
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    const line = new THREE.Line(geo, new THREE.LineBasicMaterial({{ color: 0xFF614C, linewidth: 2 }}));
    scene.add(line);
  }});

  // 2. Landscape Zones (Colored Terrain Slabs)
  (p.landscape_zones || []).forEach((z, zi) => {{
    const grp = new THREE.Group();
    const col = new THREE.Color(z.color || '#4D8B6F');
    const center = polyCenterXZ(z.geom);
    geomToPolys(z.geom).forEach(rings => {{
      const sh = polyToShape(rings);
      if (!sh) return;
      const geo = new THREE.ExtrudeGeometry(sh, {{ depth: 0.45, bevelEnabled: false }});
      geo.rotateX(-Math.PI / 2);
      const mat = new THREE.MeshStandardMaterial({{ color: col, roughness: 0.88, metalness: 0.02, transparent: true, opacity: 0.72 }});
      const mesh = new THREE.Mesh(geo, mat);
      mesh.receiveShadow = true;
      mesh.userData = {{ kind: 'zones', idx: zi, baseColor: col.clone(), label: z.name, k: z.intervention + ' · ' + z.area_feddans + ' fed. (' + z.share_pct + '%)', desc: z.outdoor_activities || z.why_here || '', center }};
      grp.add(mesh);
      pickables.push(mesh);
    }});
    scene.add(grp);
    meshGroups.zones.push({{ grp, center }});
  }});

  // 3. 3D Outdoor Destinations (Landscape Elements)
  (p.landscape_elements || []).forEach((el, ei) => {{
    const grp = new THREE.Group();
    const center = polyCenterXZ(el.geom);
    const colHex = el.type === 'basin' ? 0x3C95C4 : (el.type === 'oasis_grove' ? 0x3B7457 : (el.type === 'pergola' ? 0xC49464 : 0xB89F86));
    const elH = el.type === 'basin' ? 0.85 : (el.type === 'oasis_grove' ? 4.2 : (el.type === 'pergola' ? 3.8 : (el.type === 'belvedere' ? 3.0 : 2.2)));
    const col = new THREE.Color(colHex);
    geomToPolys(el.geom).forEach(rings => {{
      const sh = polyToShape(rings);
      if (!sh) return;
      const geo = new THREE.ExtrudeGeometry(sh, {{ depth: elH, bevelEnabled: false }});
      geo.rotateX(-Math.PI / 2);
      const mat = new THREE.MeshStandardMaterial({{ color: col, roughness: el.type === 'basin' ? 0.18 : 0.75, metalness: el.type === 'basin' ? 0.2 : 0.04 }});
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.y = 0.45;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.userData = {{ kind: 'elements', idx: ei, baseColor: col.clone(), label: el.label, k: '3D Outdoor Destination · ' + el.type, desc: 'Modeled exterior architectural destination synced to the masterplan.', center }};
      grp.add(mesh);
      pickables.push(mesh);
    }});
    scene.add(grp);
    meshGroups.elements.push({{ grp, center }});
  }});

  // 4. Sculpted Architectural Massings (Stepped Tiers + Hollow Courtyards + Architectural Edges)
  const mrVols = (p.massing_rationale || {{}}).volumes || [];
  let bldgCx = 0, bldgCz = 0, bldgN = 0;
  (p.footprints || []).forEach((fp, fi) => {{
    const grp = new THREE.Group();
    const vol = mrVols[fi] || {{}};
    const isBridge = !!fp.bridge_or_pile_allowed;
    const totalH = parseHeightMeters(vol.height_floors, isBridge);
    const tiers = isBridge ? 1 : parseTiers(vol.height_floors);
    const baseColor = new THREE.Color(isBridge ? 0xC97D63 : 0xE6DDD3);
    const center = polyCenterXZ(fp.geom);
    if (!isBridge) {{ bldgCx += center[0]; bldgCz += center[1]; bldgN++; }}

    geomToPolys(fp.geom).forEach(rings => {{
      const sh = polyToShape(rings);
      if (!sh) return;
      const tierH = totalH / tiers;
      for (let t = 0; t < tiers; t++) {{
        const geo = new THREE.ExtrudeGeometry(sh, {{ depth: isBridge ? 1.1 : tierH, bevelEnabled: false }});
        geo.rotateX(-Math.PI / 2);
        const sc = 1.0 - t * 0.09;
        // Scale tier softly around its own centroid for genuine stepped architectural massing
        geo.translate(-center[0], 0, -center[1]);
        geo.scale(sc, 1, sc);
        geo.translate(center[0], 0, center[1]);
        const mat = new THREE.MeshStandardMaterial({{ color: baseColor.clone(), roughness: 0.62, metalness: 0.06 }});
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.y = isBridge ? 3.8 : (0.5 + t * tierH);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.userData = {{
          kind: 'footprints', idx: fi, baseColor: baseColor.clone(),
          label: vol.name || fp.label,
          k: (vol.area_m2 || 'Architectural Mass') + (vol.height_floors ? ' · ' + vol.height_floors : ''),
          desc: vol.shape_reason || vol.use || fp.label,
          center
        }};
        // Crisp architectural edge lines
        const edges = new THREE.LineSegments(
          new THREE.EdgesGeometry(geo, 24),
          new THREE.LineBasicMaterial({{ color: 0x574B46, transparent: true, opacity: 0.42 }})
        );
        mesh.add(edges);
        grp.add(mesh);
        pickables.push(mesh);
      }}
    }});
    scene.add(grp);
    meshGroups.footprints.push({{ grp, center }});
  }});

  const bldgCenter = bldgN ? [bldgCx / bldgN, bldgCz / bldgN] : [0, 0];

  // Smooth Spherical Orbit Camera Controller (Zero external OrbitControls dependency!)
  const camState = {{
    azim: 0.68, polar: 0.94, dist: siteRadius * 1.48,
    tx: 0, ty: 6, tz: 0,
    tAzim: 0.68, tPolar: 0.94, tDist: siteRadius * 1.48,
    tTx: 0, tTy: 6, tTz: 0,
    dirty: true
  }};

  function applyCamera() {{
    const sinP = Math.sin(camState.polar);
    camera.position.set(
      camState.tx + camState.dist * sinP * Math.sin(camState.azim),
      camState.ty + camState.dist * Math.cos(camState.polar),
      camState.tz + camState.dist * sinP * Math.cos(camState.azim)
    );
    camera.lookAt(camState.tx, camState.ty, camState.tz);
  }}

  let activeMeshes = [];
  function highlightSelection(kind, idx, showHud = true) {{
    // Reset prior selection
    activeMeshes.forEach(m => m.material.color.copy(m.userData.baseColor));
    activeMeshes = [];
    const entry = (meshGroups[kind] || [])[idx];
    const hud = document.getElementById('webgl-hud-' + p.rank);
    if (!entry) {{
      if (hud) hud.classList.remove('visible');
      return;
    }}
    let meta = null;
    entry.grp.traverse(obj => {{
      if (obj.isMesh && obj.userData && obj.userData.baseColor) {{
        obj.material.color.setHex(0xFF614C);
        activeMeshes.push(obj);
        if (!meta) meta = obj.userData;
      }}
    }});
    camState.tTx = entry.center[0];
    camState.tTz = entry.center[1];
    camState.tDist = kind === 'zones' ? siteRadius * 1.15 : siteRadius * 0.56;
    camState.dirty = true;
    if (showHud && hud && meta) {{
      hud.innerHTML = `<div class="hud-k">${{meta.k}}</div><div class="hud-t">${{meta.label}}</div><div class="hud-d">${{meta.desc}}</div>`;
      hud.classList.add('visible');
    }}
    wakeAnim();
  }}

  function setStepCamera(stepIdx) {{
    // Choreograph 3D camera per Story Mode step
    const presets = [
      {{ azim: 0.65, polar: 0.94, dist: siteRadius * 1.45, tx: 0, tz: 0 }},                  // 1. Site & Concept
      {{ azim: 0.98, polar: 1.06, dist: siteRadius * 0.62, tx: bldgCenter[0], tz: bldgCenter[1] }}, // 2. Massing Move
      {{ azim: -0.58, polar: 1.18, dist: siteRadius * 0.95, tx: bldgCenter[0]*0.5, tz: bldgCenter[1]*0.5 }}, // 3. Nature Engine
      {{ azim: 0.35, polar: 0.56, dist: siteRadius * 1.32, tx: 0, tz: 0 }},                  // 4. Landscape
      {{ azim: 1.42, polar: 0.86, dist: siteRadius * 1.12, tx: bldgCenter[0]*0.4, tz: bldgCenter[1]*0.4 }}  // 5. Feasibility
    ];
    const pr = presets[stepIdx] || presets[0];
    camState.tAzim = pr.azim;
    camState.tPolar = pr.polar;
    camState.tDist = pr.dist;
    camState.tTx = pr.tx;
    camState.tTz = pr.tz;
    camState.dirty = true;
    wakeAnim();
  }}

  // Mouse Drag Orbit + Wheel Zoom + Click Raycasting
  let dragging = false, moved = false, lx = 0, ly = 0;
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();

  renderer.domElement.addEventListener('pointerdown', e => {{
    dragging = true; moved = false; lx = e.clientX; ly = e.clientY;
  }});
  window.addEventListener('pointermove', e => {{
    if (!dragging) return;
    const dx = e.clientX - lx, dy = e.clientY - ly;
    if (Math.hypot(dx, dy) > 3) moved = true;
    lx = e.clientX; ly = e.clientY;
    camState.tAzim -= dx * 0.008;
    camState.tPolar = Math.min(Math.max(camState.tPolar - dy * 0.007, 0.25), 1.42);
    camState.dirty = true;
    wakeAnim();
  }});
  window.addEventListener('pointerup', () => {{ dragging = false; }});

  renderer.domElement.addEventListener('wheel', e => {{
    e.preventDefault();
    camState.tDist = Math.min(Math.max(camState.tDist * (1 + e.deltaY * 0.0009), siteRadius * 0.25), siteRadius * 2.8);
    camState.dirty = true;
    wakeAnim();
  }}, {{ passive: false }});

  renderer.domElement.addEventListener('click', e => {{
    if (moved) return;
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(pickables, false);
    if (hits.length) {{
      // Prefer footprints/elements over broad landscape zones if overlapping
      const best = hits.find(h => h.object.userData.kind === 'footprints') ||
                   hits.find(h => h.object.userData.kind === 'elements') || hits[0];
      const ud = best.object.userData;
      highlightSelection(ud.kind, ud.idx, true);
      syncMapOnly(p.rank, ud.kind, ud.idx);
    }} else {{
      highlightSelection(null, -1, false);
    }}
  }});

  let animId = null;
  function animate() {{
    const k = 0.12;
    camState.azim += (camState.tAzim - camState.azim) * k;
    camState.polar += (camState.tPolar - camState.polar) * k;
    camState.dist += (camState.tDist - camState.dist) * k;
    camState.tx += (camState.tTx - camState.tx) * k;
    camState.tz += (camState.tTz - camState.tz) * k;
    applyCamera();
    renderer.render(scene, camera);

    const diff = Math.abs(camState.tAzim - camState.azim) + Math.abs(camState.tPolar - camState.polar) +
                 Math.abs(camState.tDist - camState.dist) * 0.01 + Math.abs(camState.tTx - camState.tx) * 0.01 +
                 Math.abs(camState.tTz - camState.tz) * 0.01;
    if (diff > 0.002 || dragging) {{
      animId = requestAnimationFrame(animate);
    }} else {{
      animId = null;
    }}
  }}

  function wakeAnim() {{
    if (!animId) animId = requestAnimationFrame(animate);
  }}

  const ro = new ResizeObserver(() => {{
    const nw = container.clientWidth, nh = container.clientHeight;
    if (nw > 20 && nh > 20) {{
      camera.aspect = nw / nh;
      camera.updateProjectionMatrix();
      renderer.setSize(nw, nh);
      wakeAnim();
    }}
  }});
  ro.observe(container);

  applyCamera();
  renderer.render(scene, camera);
  webglRegistry[p.rank] = {{ highlightSelection, setStepCamera, wakeAnim, bldgCenter }};
}}

// --- 3-WAY SYNC & STORY MODE CHOREOGRAPHY ---
function syncMapOnly(rank, kind, idx) {{
  const reg = miniMapRegistry[rank];
  if (!reg) return;
  const lyr = (reg[kind] || [])[idx];
  if (!lyr) return;
  try {{
    reg.map.fitBounds(lyr.getBounds().pad(0.45), {{ maxZoom: 17 }});
    lyr.openTooltip();
  }} catch (e) {{}}
}}

function focus3Way(rank, kind, idx, itemEl) {{
  const card = document.getElementById('site-card-' + rank);
  if (card) {{
    card.querySelectorAll('.active-item').forEach(el => el.classList.remove('active-item'));
    if (itemEl) itemEl.classList.add('active-item');
  }}
  syncMapOnly(rank, kind, idx);
}}

function focusPinOnMap(rank, lat, lon, label) {{
  const reg = miniMapRegistry[rank];
  if (!reg) return;
  reg.map.setView([lat, lon], 16, {{ animate: true }});
}}

function resetMiniMap(rank) {{
  const reg = miniMapRegistry[rank];
  if (reg && reg.boundary) reg.map.fitBounds(reg.boundary.getBounds().pad(0.22));
  if (webglRegistry[rank]) {{
    webglRegistry[rank].highlightSelection(null, -1, false);
    webglRegistry[rank].setStepCamera(cardStepState[rank] || 0);
  }}
}}

function goStoryStep(rank, stepIdx) {{
  const idx = ((stepIdx % 5) + 5) % 5;
  cardStepState[rank] = idx;
  const card = document.getElementById('site-card-' + rank);
  if (!card) return;
  card.querySelectorAll('.step-pill').forEach((b, i) => b.classList.toggle('active', i === idx));
  card.querySelectorAll('.story-pane').forEach((pane, i) => pane.classList.toggle('active', i === idx));

  // Choreograph 3D Camera + Leaflet Map view per Story Step
  if (webglRegistry[rank]) {{
    webglRegistry[rank].highlightSelection(null, -1, false);
    webglRegistry[rank].setStepCamera(idx);
  }}
  const reg = miniMapRegistry[rank];
  if (reg && reg.boundary) {{
    try {{
      if (idx === 1 && reg.footprints && reg.footprints[0]) {{
        const fg = L.featureGroup(reg.footprints.filter(Boolean));
        reg.map.fitBounds(fg.getBounds().pad(0.65), {{ maxZoom: 17 }});
      }} else if (idx === 2 && reg.zones && reg.zones[0]) {{
        reg.map.fitBounds(reg.zones[0].getBounds().pad(0.28), {{ maxZoom: 16 }});
      }} else {{
        reg.map.fitBounds(reg.boundary.getBounds().pad(0.22));
      }}
    }} catch (e) {{}}
  }}
}}

function stepStoryDelta(rank, delta) {{
  goStoryStep(rank, (cardStepState[rank] || 0) + delta);
}}

function swapCardMedia(rank, mode, src, btn) {{
  const wrap = document.getElementById('render-wrap-' + rank);
  const img = document.getElementById('card-img-' + rank);
  if (!wrap) return;
  btn.parentElement.querySelectorAll('.media-tbtn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  if (mode === '3d' && typeof THREE !== 'undefined') {{
    wrap.classList.remove('show-img');
    if (webglRegistry[rank]) webglRegistry[rank].wakeAnim();
  }} else {{
    if (img && src) img.src = src;
    wrap.classList.add('show-img');
  }}
}}

function toggleCardBrief(rank, btn) {{
  const card = document.getElementById('site-card-' + rank);
  if (!card) return;
  const open = card.classList.toggle('brief-open');
  if (btn) btn.textContent = open ? 'Hide full brief ▴' : 'Read full brief ▾';
}}

function toggleDetailed() {{
  document.body.classList.toggle('show-detailed');
  const isAll = document.body.classList.contains('show-detailed');
  document.querySelectorAll('.card-brief-btn').forEach(b => {{
    b.textContent = isAll ? 'Hide full brief ▴' : 'Read full brief ▾';
  }});
}}

function exportProposalsPdf() {{
  document.body.classList.add('print-all');
  window.print();
  setTimeout(() => document.body.classList.remove('print-all'), 300);
}}

function switchMainTab(tab) {{
  document.getElementById('tab-proposals').style.display = tab === 'proposals' ? 'block' : 'none';
  document.getElementById('tab-maps').style.display = tab === 'maps' ? 'flex' : 'none';
  document.getElementById('btn-tab-proposals').classList.toggle('active', tab === 'proposals');
  document.getElementById('btn-tab-maps').classList.toggle('active', tab === 'maps');
  if (tab === 'proposals') {{
    setTimeout(() => miniMaps.forEach(m => m.invalidateSize()), 80);
  }} else {{
    setTimeout(() => {{
      if (typeof maps !== 'undefined') maps.forEach(m => m.invalidateSize());
      window.dispatchEvent(new Event('resize'));
    }}, 80);
  }}
}}

function jumpTo3EngineMap(rank) {{
  const p = NEST_PROJECTS.find(x => x.rank === rank);
  if (!p) return;
  switchMainTab('maps');
  setTimeout(() => {{
    if (typeof maps !== 'undefined') {{
      maps.forEach(m => {{ m.invalidateSize(); m.setView([p.lat, p.lon], 15); }});
    }}
  }}, 120);
}}

// --- RENDER ALL INTERACTIVE STORY MODE PROJECT CARDS ---
function renderProjectCards() {{
  const stack = document.getElementById('cards-stack');
  const jbar = document.getElementById('jump-bar');

  NEST_PROJECTS.forEach(p => {{
    cardStepState[p.rank] = 0;

    const ja = document.createElement('a');
    ja.className = 'jbtn';
    ja.href = '#site-card-' + p.rank;
    ja.textContent = '#' + p.rank + ' ' + p.title;
    jbar.appendChild(ja);

    const card = document.createElement('article');
    card.id = 'site-card-' + p.rank;
    card.className = 'proj-card';

    const rawFlags = Array.isArray(p.flags) ? p.flags : Object.entries(p.flags || {{}}).filter(([,v]) => !!v).map(([k]) => k.replace(/_/g, ' '));
    const flagPills = (rawFlags.length ? rawFlags : ['✓ Standard Compliance']).map(f => `<span class="pill ${{f.includes('✓') ? 'ok' : 'warn'}}">${{f}}</span>`).join('');
    const pullLine = extractPullLine(p.thesis_detailed);
    const pinBtns = (p.map_pointers || []).map(pt =>
      `<button type="button" class="pin-btn" onclick="focusPinOnMap(${{p.rank}}, ${{pt.lat}}, ${{pt.lon}}, '${{pt.label.replace(/'/g, '')}}')" title="Locate on satellite map">` +
      `<span class="pin-dot">${{pt.id}}</span>${{pt.label.split('(')[0].trim()}} · <b>${{pt.distance_m}} m</b></button>`
    ).join('');

    // Step 2: Distributed Constellation grouped by Experience Role
    const mr = p.massing_rationale || {{}};
    const vols = mr.volumes || [];
    const maxGfa = Math.max(...vols.map(v => parseNumber(v.area_m2, 1000)), 1);
    const classifyRole = (v) => {{
      const txt = `${{v.role || ''}} ${{v.name || ''}} ${{v.use || ''}}`.toLowerCase();
      if (txt.includes('stay') || txt.includes('lodge') || txt.includes('accom') || txt.includes('cabin') || txt.includes('suite')) return 'Eco-Accommodation';
      if (txt.includes('din') || txt.includes('food') || txt.includes('cafe') || txt.includes('kitchen') || txt.includes('retail') || txt.includes('market') || txt.includes('shop')) return 'Dining & Retail';
      return 'Hero Experience Pavilions';
    }};
    const roleOrder = ['Hero Experience Pavilions', 'Dining & Retail', 'Eco-Accommodation'];
    const groupedConstellation = roleOrder.map(role => {{
      const items = vols.map((v, vi) => ({{ v, vi }})).filter(({{ v }}) => classifyRole(v) === role);
      if (!items.length) return '';
      const cards = items.map(({{ v, vi }}) => {{
        const gfaVal = parseNumber(v.area_m2, 0);
        const pct = gfaVal > 0 ? Math.max(Math.round((gfaVal / maxGfa) * 100), 18) : 32;
        return `<div class="mass-bar-item" onclick="focus3Way(${{p.rank}}, 'footprints', ${{vi}}, this)" title="Click to highlight & zoom on satellite map">` +
          `<div class="mb-top"><span class="mb-name">${{v.name}}</span><span class="mb-stat">${{v.area_m2 || 'Pavilion'}} · ${{v.hours || 'Day-to-Dusk'}}</span></div>` +
          `<div class="mb-track"><div class="mb-fill" style="width:${{pct}}%"></div></div>` +
          `<div class="mb-desc">${{v.use || v.shape_reason || ''}}</div></div>`;
      }}).join('');
      return `<div style="margin-bottom:10px"><div style="font-size:10.5px;font-weight:800;text-transform:uppercase;color:#A3473A;margin-bottom:4px">${{role}} (${{items.length}})</div>${{cards}}</div>`;
    }}).join('');

    // Step 3: Nature badges
    const inBadges = extractStatBadges(p.nature_to_bldg).map(b => `<span class="nat-stat-pill">⚡ ${{b}}</span>`).join('');
    const outBadges = extractStatBadges(p.bldg_to_nature).map(b => `<span class="nat-stat-pill">🌿 ${{b}}</span>`).join('');

    // Step 4: Landscape Proportional Bar + Zone Cards + Destination Chips
    const zones = p.landscape_zones || [];
    const zBarSegs = zones.map((z, zi) =>
      `<div class="zstack-seg" style="width:${{z.share_pct}}%;background:${{z.color}}" onclick="focus3Way(${{p.rank}}, 'zones', ${{zi}}, null)" title="${{z.name}} (${{z.share_pct}}%)">${{z.share_pct >= 10 ? z.share_pct + '%' : ''}}</div>`
    ).join('');
    const zTiles = zones.map((z, zi) =>
      `<div class="zone-tile" style="--zc:${{z.color}}" onclick="focus3Way(${{p.rank}}, 'zones', ${{zi}}, this)" title="Click to highlight in 3D &amp; map">` +
      `<div class="zt-top"><span class="zt-pct">${{z.share_pct}}%</span><span class="pill" style="border-color:${{z.color}};background:${{z.color}}18;font-size:10px">${{z.intervention}}</span></div>` +
      `<div class="zt-name">${{z.short_name || z.name}} <span style="font-weight:600;color:#625753">(${{z.area_feddans}} fed.)</span></div>` +
      `<div class="zt-act">${{z.outdoor_activities || z.why_here || ''}}</div></div>`
    ).join('');
    const elChips = (p.landscape_elements || []).map((el, ei) =>
      `<button type="button" class="el-chip" onclick="focus3Way(${{p.rank}}, 'elements', ${{ei}}, this)">● ${{el.label}}</button>`
    ).join('');

    // Step 5: Revenue Bars + Partner Pills
    const revBars = ((p.econ_evidence || {{}}).revenue_mix || []).map(r =>
      `<div class="rev-bar-row"><div class="rev-bar-hdr"><span>${{r.stream}}</span><span>${{r.share_pct}}% (${{r.annual_rev}})</span></div>` +
      `<div class="rev-track"><div class="rev-fill" style="width:${{r.share_pct}}%"></div></div></div>`
    ).join('');
    const partnerPills = ((p.econ_evidence || {{}}).funding_partners || []).map(fp => `<span class="pill ok">${{fp}}</span>`).join('');

    // Full Brief Drawer tables
    const spaceRows = (p.spaces || []).map(item => {{
      const [sp, sqm, hrs] = Array.isArray(item) ? item : [item.name || item.space || '', item.area || item.area_m2 || '', item.hours || ''];
      return `<tr><td>${{sp}}</td><td class="num">${{sqm}}</td><td class="num">${{hrs}}</td></tr>`;
    }}).join('');
    const hypRows = (p.hypotheses || []).map(item => {{
      const [h, c, e, v] = Array.isArray(item) ? item : [item.name || item.hypothesis || '', item.concept || '', item.evaluation || '', item.verdict || ''];
      return `<tr><td><b>${{h}}</b></td><td>${{c}}</td><td>${{e}}</td><td>${{v}}</td></tr>`;
    }}).join('');
    const stepButtons = STORY_LABELS.map(([num, lbl], si) =>
      `<button type="button" class="step-pill ${{si === 0 ? 'active' : ''}}" onclick="goStoryStep(${{p.rank}}, ${{si}})"><span class="step-num">${{num}}</span>${{lbl}}</button>`
    ).join('');

    const exp = p.experience_arc || {{}};
    const hasStay = !!(exp.visit_mode ? exp.visit_mode.toLowerCase().includes('stay') || exp.visit_mode.toLowerCase().includes('night') : (exp.stay_overnight && !exp.stay_overnight.toLowerCase().includes('day-only')));
    const visitMode = exp.visit_mode || (hasStay ? 'Day-to-Night · Eco-Stay' : 'Full-Day Experience');
    const natureHero = p.nature_hero || ((p.thesis_summary && p.thesis_summary.why_here) ? p.thesis_summary.why_here.split('.')[0].slice(0, 42) : 'Sun, Wind & Coast');
    const rawJourney = Array.isArray(exp.journey) && exp.journey.length
      ? exp.journey.map((m, mi) => [`${{mi + 1}} · ${{m.moment || m.title || 'Moment'}}`, m.detail || m.desc || ''])
      : [
          ['1 · Arrival', exp.arrival],
          ['2 · Core Encounter', exp.core_encounter],
          ['3 · Activities & Trails', exp.activities_loop],
          ['4 · Dining & Retail', exp.dining_retail],
          ['5 · Stay & Overnight', exp.stay_overnight],
          ['6 · Atmosphere', exp.atmosphere],
        ].filter(([, v]) => !!v);
    const expBeats = rawJourney.map(([k, v]) => `<div class="mchip"><div class="mk">${{k}}</div>${{v}}</div>`).join('');

    const skillsList = (p.generated_skills || []).map(sk =>
      `<div class="mchip" style="min-width:190px;flex:1"><div class="mk">${{sk.engine || 'Engine'}} · ${{sk.role || ''}}</div><b>${{sk.name || sk.skill_id || 'Skill'}}</b><br><span style="color:#625753">${{sk.summary || sk.description || ''}}</span></div>`
    ).join('');
    const skillsBox = skillsList
      ? `<div class="box" style="margin-top:10px"><div class="sec-lbl">Stage C Generated Design Skills (${{p.generated_skills.length}})</div><div class="micro-chips" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:8px">${{skillsList}}</div></div>`
      : '';

    card.innerHTML = `
      <div class="card-visuals">
        <div id="render-wrap-${{p.rank}}" class="render-wrap">
          <img id="card-img-${{p.rank}}" class="static-media" style="display:block" src="${{p.has_editorial_render ? p.render : p.satellite_lock}}" alt="Site #${{p.rank}}" />
          <div class="rank-chip">PROJECT #${{p.rank}} • ${{p.area_feddans}} FEDDANS • ${{p.built_gfa}}</div>
          <div class="media-toggle-bar">
            ${{p.has_editorial_render ? `<button type="button" class="media-tbtn active" onclick="swapCardMedia(${{p.rank}}, 'img', '${{p.render}}', this)">Editorial Render</button>` : ''}}
            <button type="button" class="media-tbtn ${{p.has_editorial_render ? '' : 'active'}}" onclick="swapCardMedia(${{p.rank}}, 'img', '${{p.satellite_lock}}', this)">Satellite</button>
          </div>
        </div>
        <div class="mini-map-wrap">
          <div id="mini-map-${{p.rank}}" class="mini-map"></div>
          <div class="map-legend-pill">
            <span><b style="color:#FF614C">---</b> ${{p.area_feddans}} Feddan Boundary</span>
            <span><b style="color:#3B6E52">■</b> Landscape Zones</span>
            <span><b style="color:#302B2A">■</b> Distributed Pavilions</span>
          </div>
          <div class="map-meta-bar">
            <span class="map-coord-pill"><b>${{p.footprint_type}}</b> • ${{p.area_m2.toLocaleString()}} m² • ${{p.lat.toFixed(4)}}, ${{p.lon.toFixed(4)}}</span>
            <span style="display:inline-flex;gap:5px">
              <button type="button" class="mini-btn" onclick="resetMiniMap(${{p.rank}})">Reset View</button>
              <button type="button" class="jump-map-btn" onclick="jumpTo3EngineMap(${{p.rank}})">3-Engine Map →</button>
            </span>
          </div>
        </div>
      </div>

      <div class="card-head-bar">
        <div>
          <h2>${{p.title}}</h2>
          <div class="sub">${{p.subtitle}}</div>
          <div class="badge-row">
            <span class="pill tier">${{visitMode}}</span>
            <span class="pill ok">Nature Hero: ${{natureHero}}</span>
            <span class="pill">${{p.area_feddans}} Feddans · ${{vols.length || 1}} Pavilions</span>
            <span class="pill" style="opacity:0.75">${{p.built_gfa}} · ${{p.idiom}}</span>
            ${{flagPills}}
          </div>
        </div>
        <button type="button" class="btn-outline card-brief-btn" onclick="toggleCardBrief(${{p.rank}}, this)">Read full brief ▾</button>
      </div>

      <div class="story-nav">
        <div class="story-steps">${{stepButtons}}</div>
        <div class="story-arrows">
          <button type="button" class="arr-btn" onclick="stepStoryDelta(${{p.rank}}, -1)">← Prev</button>
          <button type="button" class="arr-btn" onclick="stepStoryDelta(${{p.rank}}, 1)">Next →</button>
        </div>
      </div>

      <div class="story-stage">
        <!-- STEP 1: THE EXPERIENCE (DEFAULT OPENING VIEW) -->
        <div class="story-pane active">
          <div class="story-grid">
            <div style="display:flex;flex-direction:column;justify-content:center">
              <div class="hook-hero">${{p.thesis_summary.hook}}</div>
              ${{pullLine ? `<div class="pull-banner">“${{pullLine}}”</div>` : ''}}
              <div class="micro-chips" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:8px">
                <div class="mchip"><div class="mk">1 · Nature as Hero</div>${{natureHero}}</div>
                <div class="mchip"><div class="mk">2 · Why It’s New</div>${{exp.core_encounter || p.thesis_summary.key_program || ''}}</div>
                <div class="mchip"><div class="mk">3 · Architectural Idea</div>${{exp.core_idea || p.thesis_summary.gesture_line || ''}}</div>
              </div>
            </div>
            <div class="diag-card">
              <div class="diag-lbl"><span>Project-Specific Guest Journey (${{rawJourney.length}} Moments)</span><span>${{exp.atmosphere ? 'Atmosphere & Flow' : 'End-to-End'}}</span></div>
              <div class="micro-chips" style="grid-template-columns:repeat(2,minmax(0,1fr));gap:6px">${{expBeats}}</div>
              ${{exp.atmosphere ? `<div style="font-size:11.5px;color:#625753;margin-top:8px"><b>Atmosphere:</b> ${{exp.atmosphere}}</div>` : ''}}
            </div>
          </div>
        </div>

        <!-- STEP 2: DISTRIBUTED CONSTELLATION -->
        <div class="story-pane">
          <div class="diag-lbl"><span>2 · Distributed Project Constellation (${{p.built_gfa}} across ${{vols.length || 1}} Pavilions)</span><span>Click any pavilion to locate on satellite map</span></div>
          <div class="mass-bar-list">${{groupedConstellation}}</div>
        </div>

        <!-- STEP 3: NATURE & LANDSCAPE -->
        <div class="story-pane">
          <div class="diag-lbl"><span>3 · Two-Way Nature Loop &amp; Whole-Site Landscape (${{p.area_feddans}} Feddans)</span><span>Click any zone to zoom on map</span></div>
          <div class="nature-loop-wrap" style="margin-bottom:10px">
            <div class="nat-col">
              <div class="nat-node in">
                <div class="nat-k">Nature → Building (Passive Inputs)</div>
                <div class="nat-v">${{p.nature_to_bldg}}</div>
                ${{inBadges ? `<div class="nat-badges">${{inBadges}}</div>` : ''}}
              </div>
            </div>
            <div>${{buildNatureCenterSVG()}}</div>
            <div class="nat-col">
              <div class="nat-node out">
                <div class="nat-k">Building → Nature (Ecological Return)</div>
                <div class="nat-v">${{p.bldg_to_nature}}</div>
                ${{outBadges ? `<div class="nat-badges">${{outBadges}}</div>` : ''}}
              </div>
            </div>
          </div>
          <div class="zstack-bar">${{zBarSegs}}</div>
          <div class="zone-grid">${{zTiles}}</div>
          ${{elChips ? `<div style="margin-top:8px"><div style="font-size:10.5px;font-weight:800;text-transform:uppercase;color:#625753;margin-bottom:5px">Outdoor Destinations Around Pavilions:</div>${{elChips}}</div>` : ''}}
          <div class="risk-strip" style="margin-top:8px"><b>⚠ Environmental &amp; Resource Guardrail:</b> ${{p.landscape_summary.tradeoffs_risk}}</div>
        </div>

        <!-- STEP 4: SITE & GIS SIGNAL -->
        <div class="story-pane">
          <div class="story-grid">
            <div class="diag-card">
              <div class="diag-lbl"><span>4 · Site Signal Radar &amp; Real GIS Drivers</span><span>Click pins to locate</span></div>
              ${{buildSignalRadarSVG(p)}}
              <div class="pin-row">${{pinBtns}}</div>
            </div>
            <div class="diag-card">
              <div class="diag-lbl"><span>Why This Site &amp; Landscape Strategy</span><span>${{p.area_feddans}} Feddans</span></div>
              <div class="micro-chips">
                <div class="mchip"><div class="mk">Why Here</div>${{p.thesis_summary.why_here}}</div>
                <div class="mchip"><div class="mk">Landscape Backbone</div>${{p.landscape_summary.backbone || ''}}</div>
                <div class="mchip"><div class="mk">Architecture–Landscape Interface</div>${{p.landscape_summary.arch_interface || ''}}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- STEP 5: FEASIBILITY & BLUEPRINT -->
        <div class="story-pane">
          <div class="story-grid">
            <div class="diag-card">
              <div class="diag-lbl"><span>5 · Whole-Site CapEx Split &amp; Revenue Mix</span><span>Building + Landscape</span></div>
              ${{buildCapexDonutSVG(p)}}
              <div style="margin-top:8px">${{revBars}}</div>
            </div>
            <div style="display:flex;flex-direction:column;justify-content:space-between">
              <div>
                <div class="fin-kpi-grid">
                  <div class="kpi-tile"><div class="k">Annual Revenue</div><div class="v">${{p.fin.rev}}</div><div class="s">Architecture + Landscape streams</div></div>
                  <div class="kpi-tile"><div class="k">Projected IRR</div><div class="v" style="color:#A3473A">${{p.fin.irr}}</div><div class="s">20-yr concession · ROI ${{p.fin.roi}}</div></div>
                  <div class="kpi-tile"><div class="k">Payback Period</div><div class="v">${{p.fin.payback}}</div><div class="s">Pilot: ${{p.fin.pilot.split('—')[0]}}</div></div>
                  <div class="kpi-tile"><div class="k">Built GFA / Site</div><div class="v">${{p.built_gfa}}</div><div class="s">${{p.area_feddans}} feddans · 0% variance</div></div>
                </div>
                <div style="display:flex;gap:6px;flex-wrap:wrap">${{partnerPills}}</div>
              </div>
              <div class="action-bar">
                <a class="btn-coral" href="${{p.render_prompt_path}}" target="_blank">Render Pack Prompt ↗</a>
                <a class="btn-outline" href="${{p.satellite_lock}}" target="_blank">Satellite Lock (.png) ↗</a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- OPTIONAL PROGRESSIVE DISCLOSURE FULL BRIEF DRAWER -->
      <div class="full-brief-drawer">
        <div class="two-col">
          <div class="box">
            <div class="sec-lbl">Full 3-Act Competition Narrative${{p.concept_register ? ` · ${{p.concept_register}}` : ''}}</div>
            <div class="narrative-body">${{formatDetailedNarrative(p.thesis_detailed)}}</div>
            <div style="margin-top:9px;font-size:11.5px;color:#625753"><b>Precedent Lens:</b> ${{p.precedent}}</div>
          </div>
          <div class="box">
            <div class="sec-lbl">Space Program (${{p.built_gfa}}) &amp; Engine Traceability</div>
            <table class="prog-table" style="margin-bottom:10px">
              <thead><tr><th>Space / Zone</th><th style="text-align:right">Area</th><th style="text-align:right">Hours</th></tr></thead>
              <tbody>${{spaceRows}}</tbody>
            </table>
            <div style="font-size:11.5px;color:#625753"><b>Engine Synthesis:</b> ${{p.engine_trace.synthesis_note}}</div>
          </div>
        </div>
        <div class="box">
          <div class="sec-lbl">Hypotheses Comparison, Phase 0 Pilot &amp; Provenance</div>
          <table class="prog-table" style="margin-bottom:8px">
            <thead><tr><th>ID</th><th>Integrated Site + Building Concept</th><th>Ecology &amp; Trade-Offs</th><th>Verdict</th></tr></thead>
            <tbody>${{hypRows}}</tbody>
          </table>
          <div style="font-size:11.5px"><b>Scenarios:</b> ${{p.fin.scenarios}} · <b>Phase 0 Pilot:</b> ${{p.fin.pilot}}</div>
        </div>
        ${{skillsBox}}
      </div>
    `;

    stack.appendChild(card);

    // Initialize Live 3D WebGL Stage
    initWebGL3D(p);

    // Initialize Tri-Layer Leaflet Mini-Map with center/zoom set FIRST + 3-way click sync
    try {{
      const mm = L.map('mini-map-' + p.rank, {{ center: [p.lat, p.lon], zoom: 14, zoomControl: true, attributionControl: false, scrollWheelZoom: true }});
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{ maxZoom: 19 }}).addTo(mm);
      const zLayers = [], elLayers = [], fpLayers = [];
      (p.landscape_zones || []).forEach((z, zi) => {{
        try {{
          const zl = L.geoJSON(z.geom, {{ style: {{ color: z.color, weight: 1.5, fillColor: z.color, fillOpacity: 0.36 }} }})
            .bindTooltip(`<b>${{z.name}}</b><br>${{z.intervention}} · ${{z.area_feddans}} fed. (${{z.share_pct}}%)`, {{ sticky: true }})
            .on('click', () => {{ if (webglRegistry[p.rank]) webglRegistry[p.rank].highlightSelection('zones', zi, true); }})
            .addTo(mm);
          zLayers.push(zl);
        }} catch (ez) {{ zLayers.push(null); }}
      }});
      (p.landscape_landforms || []).forEach(lf => {{
        try {{
          L.geoJSON(lf.geom, {{ style: {{ color: '#8C756F', weight: 1.4, fillColor: '#C9B79C', fillOpacity: 0.85 }} }})
            .bindTooltip(lf.label, {{ sticky: true }}).addTo(mm);
        }} catch (elf) {{}}
      }});
      (p.landscape_elements || []).forEach((el, ei) => {{
        try {{
          const elCol = el.type === 'basin' ? '#3898CC' : (el.type === 'oasis_grove' ? '#4D8B6F' : '#B58D63');
          const ell = L.geoJSON(el.geom, {{ style: {{ color: '#302B2A', weight: 1.2, fillColor: elCol, fillOpacity: 0.76 }} }})
            .bindTooltip(`<b>${{el.label}}</b> (${{el.type}})`, {{ sticky: true }})
            .on('click', () => {{ if (webglRegistry[p.rank]) webglRegistry[p.rank].highlightSelection('elements', ei, true); }})
            .addTo(mm);
          elLayers.push(ell);
        }} catch (eel) {{ elLayers.push(null); }}
      }});
      (p.footprints || []).forEach((fp, fi) => {{
        try {{
          const isBr = !!fp.bridge_or_pile_allowed;
          const fl = L.geoJSON(fp.geom, {{ style: {{ color: isBr ? '#FF614C' : '#302B2A', weight: 2.0, fillColor: isBr ? '#FF614C' : '#FFF4EE', fillOpacity: 0.92 }} }})
            .bindTooltip(`<b>${{fp.label}}</b>`, {{ sticky: true }})
            .on('click', () => {{ if (webglRegistry[p.rank]) webglRegistry[p.rank].highlightSelection('footprints', fi, true); }})
            .addTo(mm);
          fpLayers.push(fl);
        }} catch (efp) {{ fpLayers.push(null); }}
      }});
      const bLayer = L.geoJSON(p.geojson, {{ style: {{ color: '#FF614C', weight: 2.6, dashArray: '7 5', fillOpacity: 0 }} }}).addTo(mm);
      (p.map_pointers || []).forEach(pt => {{
        if (pt.lat != null && pt.lon != null) {{
          L.circleMarker([pt.lat, pt.lon], {{ radius: 6, color: '#A3473A', weight: 2, fillColor: '#FF614C', fillOpacity: 0.95 }})
            .bindTooltip(`<b>#${{pt.id}} ${{pt.label}}</b> (${{pt.distance_m}} m)<br>${{pt.role}}`).addTo(mm);
        }}
      }});
      mm.fitBounds(bLayer.getBounds().pad(0.22));
      miniMaps.push(mm);
      miniMapRegistry[p.rank] = {{ map: mm, boundary: bLayer, zones: zLayers, elements: elLayers, footprints: fpLayers }};
    }} catch (err) {{
      console.error('Mini-map init error for Site #' + p.rank, err);
    }}
  }});

  // Overlay the 50-70 feddan organic boundaries on Tab 2's 3 synchronized maps
  if (typeof maps !== 'undefined') {{
    NEST_PROJECTS.forEach(p => {{
      maps.forEach(m => {{
        L.geoJSON(p.geojson, {{ style: {{ color: '#FF614C', weight: 2.4, dashArray: '6 5', fillColor: '#FF614C', fillOpacity: 0.14 }} }})
          .bindTooltip(`<b>#${{p.rank}} ${{p.title}}</b> (${{p.area_feddans}} feddans)`).addTo(m);
      }});
    }});
  }}
}}

renderProjectCards();
</script>
</body>
</html>
"""

    out_path = run_dir / "nest_dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Build NEST 2.3 Interactive Story Mode + Live 3D Studio Dashboard")
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--projects-json", type=Path, default=None)
    ap.add_argument("--plot-title", type=str, default=None)
    args = ap.parse_args()

    pjson = args.projects_json or (args.run_dir / "stage_b_projects.json")
    projects = json.loads(pjson.read_text(encoding="utf-8"))
    plot_title = args.plot_title or args.run_dir.name
    out = build_nest_22_dashboard(args.run_dir, projects, plot_title, Path(__file__).resolve().parent)
    print(f"Built NEST 2.3 Story Mode + Live 3D dashboard -> {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
