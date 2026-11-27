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


def b64_png_thumb(path: Path, max_px: int = 96) -> str:
    if not path.exists():
        return ""
    try:
        import io
        from PIL import Image
        with Image.open(path) as im:
            im = im.convert("RGBA")
            im.thumbnail((max_px, max_px), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="PNG", optimize=True)
            return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return b64_uri(path, "image/png")


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
    eng_gfx_dir = root_dir / "NEST Engine Graphics"
    engine_icons = {
        "Crystals": b64_png_thumb(eng_gfx_dir / "Crystals.png", 96),
        "Cells": b64_png_thumb(eng_gfx_dir / "Cells.png", 96),
        "Corals": b64_png_thumb(eng_gfx_dir / "Corals.png", 96),
    }
    font_uri = b64_uri(ui_dir / "fonts" / "FunnelDisplay.ttf", "font/ttf")
    font_face_css = f"{font_face_css}" if font_uri else ""

    pdf_slug = re.sub(r"[^A-Za-z0-9_-]+", "_", (run_dir.name or "NEST_Plot").strip()).strip("_")[:60]
    prebuilt_pdf_name = f"NEST_Proposals_{pdf_slug}.pdf"
    has_prebuilt_pdf = (run_dir / prebuilt_pdf_name).is_file()

    # Load full Stage C skill JSON files for Tab 3 (Stage C Skills Dashboard)
    all_stage_c_skills: list[dict] = []
    skills_root = run_dir / "skills"
    proj_by_rank = {int(p.get("rank", idx + 1)): p for idx, p in enumerate(projects)}
    if skills_root.is_dir():
        for pdir in sorted(skills_root.glob("project_*")):
            if not pdir.is_dir():
                continue
            m_rk = re.match(r"project_(\d+)", pdir.name)
            p_rk = int(m_rk.group(1)) if m_rk else 0
            p_obj = proj_by_rank.get(p_rk, {})
            for jf in sorted(pdir.glob("*.json")):
                try:
                    sk_raw = json.loads(jf.read_text(encoding="utf-8"))
                except Exception:
                    continue
                eng_raw = str(sk_raw.get("parent_engine") or sk_raw.get("engine") or "Crystals")
                ekey = "Cells" if "cell" in eng_raw.lower() else ("Corals" if "coral" in eng_raw.lower() else "Crystals")
                attrs = sk_raw.get("attributes") or {}
                tools_set: list[str] = []
                for grp_key, t_key in (("facets", "tool"), ("adaptation_moves", "tools"), ("branches", "tool")):
                    for item in attrs.get(grp_key) or []:
                        t_vals = item.get(t_key) or item.get("tools") or item.get("tool") or []
                        if isinstance(t_vals, str):
                            t_vals = [t_vals]
                        for tv in t_vals:
                            if tv and tv not in tools_set:
                                tools_set.append(str(tv))
                act = sk_raw.get("action") or {}
                all_stage_c_skills.append({
                    "uid": f"p{p_rk}_{sk_raw.get('skill_id') or jf.stem}",
                    "filename": jf.name,
                    "project_rank": p_rk,
                    "project_title": p_obj.get("title") or f"Project #{p_rk}",
                    "engine_key": ekey,
                    "action_type": str(act.get("type") or "Guidance"),
                    "tools": tools_set,
                    "raw": sk_raw,
                })

    # Detect whether optional external editorial renders exist & ensure asset paths
    for p in projects:
        rk = p["rank"]
        p.setdefault("satellite_lock", f"renders/render_pack/site_{rk}/satellite_lock.png")
        p.setdefault("rhino_3dm", f"models/site_{rk}_massing.3dm")
        p.setdefault("rhino_3dm_path", f"models/site_{rk}_massing.3dm")
        p.setdefault("render_prompt", f"renders/render_pack/site_{rk}/prompt.md")
        p.setdefault("render_prompt_path", f"renders/render_pack/site_{rk}/prompt.md")
        ext_render = run_dir / "renders" / f"site_{rk}.jpg"
        hero_render = run_dir / "renders" / f"site_{rk}_hero.jpg"
        p["has_editorial_render"] = ext_render.exists()
        p["has_hero_render"] = hero_render.exists()
        p["hero_render"] = f"renders/site_{rk}_hero.jpg" if hero_render.exists() else ""
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
#tab-proposals {{ flex: 1; overflow-y: auto; padding: 0 0 48px; background: var(--nest-paper); }}
#tab-maps {{ flex: 1; display: none; flex-direction: column; min-height: 0; overflow: hidden; }}
.prop-toolbar {{ max-width: none; width: 100%; margin: 0 0 18px; display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; background: #FFFFFF; border-bottom: 1px solid var(--nest-line); border-radius: 0; padding: 10px 20px; }}
.jump-bar {{ display: inline-flex; gap: 6px; flex-wrap: wrap; align-items: center; }}
.jbtn {{ padding: 5px 11px; border-radius: 8px; border: 1px solid var(--nest-line); background: var(--nest-soft); color: var(--nest-ink); font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; text-decoration: none; }}
.jbtn:hover {{ border-color: var(--nest-edge); background: #FFFFFF; }}
.tb-actions {{ display: inline-flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
.btn-coral {{ display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; border-radius: 9px; background: var(--nest-coral); color: #302B2A; border: 1px solid var(--nest-edge); box-shadow: 0 3px 0 var(--nest-edge); font-family: inherit; font-size: 12px; font-weight: 800; cursor: pointer; text-decoration: none; }}
.btn-coral:hover {{ background: var(--nest-coral-hi); }}
.btn-outline {{ display: inline-flex; align-items: center; gap: 6px; padding: 7px 12px; border-radius: 9px; background: #FFFFFF; color: var(--nest-ink); border: 1px solid var(--nest-line); font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; text-decoration: none; }}
.btn-outline:hover {{ background: var(--nest-soft); border-color: var(--nest-edge); }}

.cards-stack {{ max-width: none; width: 100%; margin: 0; display: flex; flex-direction: column; gap: 24px; }}
.proj-card {{ background: #FFFFFF; border-top: 1px solid var(--nest-line); border-bottom: 1px solid var(--nest-line); border-left: 0; border-right: 0; border-radius: 0; overflow: hidden; box-shadow: 0 8px 22px rgba(48,43,42,0.06); }}
.proj-card-shell {{ display: grid; grid-template-columns: 70% 30%; align-items: stretch; width: 100%; }}
.proj-card-main {{ min-width: 0; display: flex; flex-direction: column; }}
.proj-card-rail {{ min-width: 0; border-left: 1px solid var(--nest-line); background: #F7F3F0; padding: 14px 16px 18px; display: flex; flex-direction: column; gap: 12px; }}
.eng-rail-hdr {{ display: flex; align-items: center; justify-content: space-between; gap: 6px; padding-bottom: 8px; border-bottom: 1px solid var(--nest-line); font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: var(--nest-edge); }}
.eng-rail-card {{ flex: 0 0 auto; display: flex; flex-direction: column; gap: 8px; border-radius: 12px; padding: 12px 13px; border: 1px solid var(--nest-line); background: #FFFFFF; box-shadow: 0 2px 8px rgba(48,43,42,0.04); }}
.eng-rail-top {{ display: flex; align-items: center; justify-content: space-between; gap: 6px; }}
.eng-rail-title {{ display: inline-flex; align-items: center; gap: 7px; font-size: 11.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.03em; }}
.eng-rail-role {{ font-size: 9.5px; font-weight: 800; padding: 2px 7px; border-radius: 999px; letter-spacing: 0.04em; text-transform: uppercase; }}
.eng-rail-defn {{ font-size: 10.5px; line-height: 1.35; font-style: italic; opacity: 0.9; padding-bottom: 6px; border-bottom: 1px dashed rgba(48,43,42,0.14); }}
.eng-rail-words {{ font-size: 12px; line-height: 1.48; color: #231E1C; }}
.eng-rail-map {{ width: 100%; border-radius: 9px; overflow: hidden; border: 1px solid rgba(48,43,42,0.15); background: #EFE9E3; cursor: pointer; transition: border-color 140ms ease, box-shadow 140ms ease; }}
.eng-rail-map:hover {{ border-color: var(--nest-coral); box-shadow: 0 4px 12px rgba(48,43,42,0.14); }}
.eng-rail-map svg {{ display: block; width: 100%; height: auto; }}
.eng-rail-drivers {{ display: flex; flex-wrap: wrap; gap: 5px; padding-top: 2px; }}
.eng-drv-pill {{ display: inline-flex; align-items: center; gap: 4px; font-size: 10.2px; font-weight: 700; line-height: 1.25; color: #3D3532; background: rgba(255,255,255,0.92); border: 1px solid rgba(48,43,42,0.14); border-radius: 999px; padding: 3px 8px; }}
@media (max-width: 1100px) {{
  .proj-card-shell {{ grid-template-columns: 1fr; }}
  .proj-card-rail {{ border-left: 0; border-top: 1px solid var(--nest-line); }}
}}

/* Top Split Visual Stage (Render / Aerial + Live Tri-Layer Leaflet Satellite Map) */
.card-visuals {{ display: grid; grid-template-columns: 1.25fr 1fr; border-bottom: 1px solid var(--nest-line); }}
@media (max-width: 960px) {{ .card-visuals {{ grid-template-columns: 1fr; }} }}
.render-wrap {{ position: relative; background: #F3EFEA; height: 440px; overflow: hidden; }}
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

.mini-map-wrap {{ position: relative; height: 440px; border-left: 1px solid var(--nest-line); }}
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
.exp-story-hdr {{ background: #FFFAF7; border: 1px solid var(--nest-line); border-radius: 14px; padding: 14px 16px; margin-bottom: 14px; }}
.exp-strip {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--nest-line); }}
@media (max-width: 780px) {{ .exp-strip {{ grid-template-columns: 1fr; }} }}
.exp-cue {{ font-size: 12px; line-height: 1.42; color: var(--nest-ink); }}
.exp-cue .mk {{ font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--nest-edge); margin-bottom: 3px; }}
.journey-board {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
.jcard {{ background: #FFFFFF; border: 1px solid var(--nest-line); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; }}
.jcard-media {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block; background: var(--nest-soft); }}
.jcard-slot {{ width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, #FBEFED 0%, #F5F5F5 100%); border-bottom: 1px dashed var(--nest-line); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; padding: 10px; text-align: center; color: var(--nest-muted); font-size: 11px; }}
.jcard-slot b {{ color: var(--nest-edge); font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.05em; }}
.jcard-body {{ padding: 10px 12px; flex: 1; }}

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

/* Tab 3: Stage C Skills Dashboard */
#tab-skills {{ display: none; flex: 1 1 auto; overflow-y: auto; padding: 18px 24px 44px; background: var(--nest-paper); }}
.skills-wrap {{ max-width: 1440px; margin: 0 auto; }}
.skills-toolbar {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap; background: #FFFAF7; border: 1px solid var(--nest-line); border-radius: 14px; padding: 12px 14px; margin-bottom: 14px; }}
.skills-filters {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
.sk-sel {{ font-family: inherit; font-size: 12px; font-weight: 700; color: var(--nest-ink); background: #fff; border: 1px solid var(--nest-line); border-radius: 9px; padding: 6px 10px; cursor: pointer; }}
.skills-lanes {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; align-items: start; }}
@media (max-width: 1080px) {{ .skills-lanes {{ grid-template-columns: 1fr; }} }}
.sk-lane {{ border-radius: 14px; border: 1px solid var(--nest-line); padding: 12px; }}
.sk-lane-hdr {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 6px; }}
.sk-lane-def {{ font-size: 11px; color: var(--nest-muted); line-height: 1.4; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid rgba(0,0,0,0.07); }}
.sk-card {{ background: #fff; border: 1px solid var(--nest-line); border-radius: 11px; padding: 10px 12px; margin-bottom: 9px; cursor: pointer; transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease; }}
.sk-card:hover {{ transform: translateY(-1px); box-shadow: 0 6px 16px rgba(48,43,42,.08); border-color: var(--nest-coral); }}
.sk-card-top {{ display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 4px; flex-wrap: wrap; }}
.sk-card-title {{ font-size: 13px; font-weight: 800; color: var(--nest-ink); line-height: 1.3; margin-bottom: 4px; }}
.sk-card-def {{ font-size: 11.5px; color: var(--nest-muted); line-height: 1.42; margin-bottom: 7px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
.sk-tools-row {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.sk-tool {{ font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 6px; background: #F5F2F0; color: #4A413D; border: 1px solid #E2D9D5; }}
.sk-drawer-backdrop {{ display: none; position: fixed; inset: 0; background: rgba(48,43,42,.38); z-index: 2000; justify-content: flex-end; }}
.sk-drawer-backdrop.open {{ display: flex; }}
.sk-drawer {{ width: min(620px, 94vw); height: 100%; background: #FFFAF7; border-left: 1px solid var(--nest-line); box-shadow: -12px 0 36px rgba(48,43,42,.18); display: flex; flex-direction: column; overflow: hidden; }}
.sk-drawer-hdr {{ padding: 14px 18px; border-bottom: 1px solid var(--nest-line); background: #fff; display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }}
.sk-drawer-body {{ padding: 16px 18px 28px; overflow-y: auto; flex: 1 1 auto; }}
.sk-sec {{ background: #fff; border: 1px solid var(--nest-line); border-radius: 11px; padding: 10px 12px; margin-bottom: 10px; }}
.sk-sec-lbl {{ font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: .45px; color: var(--nest-edge); margin-bottom: 6px; }}
.sk-kv {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 6px; }}
.sk-kv-item {{ background: #FAF7F5; border: 1px solid #EAE1DD; border-radius: 8px; padding: 6px 8px; font-size: 11.5px; }}
.sk-kv-item b {{ display: block; font-size: 9.5px; text-transform: uppercase; color: var(--nest-muted); margin-bottom: 2px; }}

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
    <button type="button" id="btn-tab-skills" class="mtab-btn" onclick="switchMainTab('skills')">Stage C Skills ({len(all_stage_c_skills)})</button>
  </div>
</header>

<section id="tab-proposals">
  <div class="prop-toolbar">
    <div id="jump-bar" class="jump-bar">
      <span style="font-size:11.5px;font-weight:800;color:#625753;margin-right:4px">ENGINE:</span>
      <button type="button" class="jbtn eng-fbtn active" onclick="filterByEngine('All', this)">All</button>
      <button type="button" class="jbtn eng-fbtn" onclick="filterByEngine('Crystals', this)">Crystals</button>
      <button type="button" class="jbtn eng-fbtn" onclick="filterByEngine('Cells', this)">Cells</button>
      <button type="button" class="jbtn eng-fbtn" onclick="filterByEngine('Corals', this)">Corals</button>
      <span style="font-size:11.5px;font-weight:800;color:#625753;margin:0 4px 0 8px">SITE:</span>
    </div>
    <div class="tb-actions">
      <button type="button" id="btn-detail-toggle" class="btn-outline" onclick="toggleDetailed()">Story Mode | Full Dossiers</button>
      <a class="btn-outline" href="renders/render_pack/AGENT_INSTRUCTIONS.md" target="_blank">Render Pack Guide ↗</a>
      <button type="button" class="btn-coral" onclick="exportProposalsPdf()">⬇ Export Proposals PDF</button>
    </div>
  </div>
  <div id="cards-stack" class="cards-stack"></div>
</section>

<section id="tab-maps">
<div id="tab2-engine-reasoning" style="max-width:1420px;margin:0 auto 14px;padding:12px 14px;background:#FFFAF7;border:1px solid var(--nest-line);border-radius:14px"></div>
{tab2_inner}
</section>

<section id="tab-skills">
  <div class="skills-wrap">
    <div class="skills-toolbar">
      <div class="skills-filters">
        <span style="font-size:11.5px;font-weight:800;color:#625753;text-transform:uppercase;letter-spacing:.35px">Filter Skills:</span>
        <select id="sk-filter-project" class="sk-sel" onchange="renderSkillsTab()">
          <option value="All">All Projects</option>
        </select>
        <select id="sk-filter-engine" class="sk-sel" onchange="renderSkillsTab()">
          <option value="All">All Engines</option>
          <option value="Crystals">Crystals (Development)</option>
          <option value="Cells">Cells (Adaptation)</option>
          <option value="Corals">Corals (Coordination)</option>
        </select>
        <select id="sk-filter-tool" class="sk-sel" onchange="renderSkillsTab()">
          <option value="All">All Channels / Tools</option>
          <option value="__agnostic__">Tool-Agnostic (Design Principle)</option>
        </select>
        <select id="sk-filter-action" class="sk-sel" onchange="renderSkillsTab()">
          <option value="All">All Action Types</option>
        </select>
        <span id="sk-count-badge" class="pill" style="font-size:11px">0 skills</span>
      </div>
      <div style="display:flex;gap:8px;align-items:center">
        <button type="button" class="btn-outline" onclick="resetSkillFilters()">Reset</button>
        <button type="button" class="btn-coral" onclick="exportFilteredSkillsPack()">⬇ Export Filtered Skills (.json)</button>
      </div>
    </div>
    <div id="skills-lanes" class="skills-lanes"></div>
  </div>
</section>

<div id="sk-drawer-backdrop" class="sk-drawer-backdrop" onclick="if(event.target===this) closeSkillInspector()">
  <div class="sk-drawer" role="dialog" aria-modal="true">
    <div id="sk-drawer-hdr" class="sk-drawer-hdr"></div>
    <div id="sk-drawer-body" class="sk-drawer-body"></div>
  </div>
</div>

<script>
const NEST_PROJECTS = {json.dumps(projects)};
const NEST_STAGE_C_SKILLS = {json.dumps(all_stage_c_skills)};
const miniMaps = [];
const miniMapRegistry = {{}};
const webglRegistry = {{}};
const cardStepState = {{}};

const STORY_LABELS = [
  ['1', 'The Experience'],
  ['2', 'Nature & Landscape'],
  ['3', 'Site & GIS'],
  ['4', 'Feasibility']
];

const ENGINE_ICONS = {json.dumps(engine_icons)};

function engineIconSVG(engineName, size = 18, color = 'currentColor') {{
  const k = String(engineName || '').toLowerCase();
  const key = k.includes('cell') ? 'Cells' : (k.includes('coral') ? 'Corals' : 'Crystals');
  const uri = ENGINE_ICONS[key];
  if (uri) {{
    const px = Math.max(size + 4, 18);
    return `<img src="${{uri}}" width="${{px}}" height="${{px}}" alt="${{key}}" style="display:inline-block;vertical-align:middle;object-fit:contain;flex:none" />`;
  }}
  const st = `display:inline-block;vertical-align:-2.5px;flex:none`;
  if (key === 'Cells') {{
    return `<svg width="${{size}}" height="${{size}}" viewBox="0 0 24 24" fill="none" stroke="${{color}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="${{st}}" aria-hidden="true"><path d="M12 2.8c4.6 0 8.7 2.8 9.2 7.4.5 4.9-2.8 10.2-8.2 10.8-5.3.6-9.8-3.4-10.1-8.5C2.6 7.2 6.8 2.8 12 2.8Z"/><circle cx="12.2" cy="11.8" r="3.2" fill="${{color}}" fill-opacity="0.22"/><circle cx="16.4" cy="7.6" r="1.2" fill="${{color}}" stroke="none"/><circle cx="8.1" cy="15.7" r="1.1" fill="${{color}}" stroke="none"/></svg>`;
  }}
  if (key === 'Corals') {{
    return `<svg width="${{size}}" height="${{size}}" viewBox="0 0 24 24" fill="none" stroke="${{color}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="${{st}}" aria-hidden="true"><path d="M12 21v-7"/><path d="M12 14c-3.2 0-5.5-2.2-5.5-5.5V6"/><path d="M12 14c3.2 0 5.5-2.2 5.5-5.5V6"/><path d="M12 14V7.5"/><circle cx="6.5" cy="5" r="2" fill="${{color}}" fill-opacity="0.25"/><circle cx="12" cy="5.5" r="2" fill="${{color}}" fill-opacity="0.25"/><circle cx="17.5" cy="5" r="2" fill="${{color}}" fill-opacity="0.25"/><path d="M8.5 21h7"/></svg>`;
  }}
  return `<svg width="${{size}}" height="${{size}}" viewBox="0 0 24 24" fill="none" stroke="${{color}}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="${{st}}" aria-hidden="true"><polygon points="12 2 19.5 8.5 16.5 21 7.5 21 4.5 8.5 12 2" fill="${{color}}" fill-opacity="0.16"/><polyline points="12 2 12 21"/><polyline points="4.5 8.5 12 11.5 19.5 8.5"/></svg>`;
}}

function buildEngineElementMapSVG(p, engName, ec, words, driverTxt, isLead = false) {{
  const W = 340, H = isLead ? 168 : 138;
  const lat0 = Number(p.lat || 0), lon0 = Number(p.lon || 0);
  const cosLat = Math.cos(lat0 * Math.PI / 180) || 1;
  const mPerLon = 111320 * cosLat, mPerLat = 110540;
  const toXY = (lon, lat) => [((lon - lon0) * mPerLon), ((lat - lat0) * mPerLat)];

  const rings = [];
  const gj = p.geojson || null;
  if (gj && gj.type === 'Polygon' && gj.coordinates && gj.coordinates[0]) rings.push(gj.coordinates[0]);
  else if (gj && gj.type === 'MultiPolygon' && gj.coordinates) gj.coordinates.forEach(poly => {{ if (poly[0]) rings.push(poly[0]); }});
  let maxExt = 380;
  rings.forEach(r => r.forEach(pt => {{
    const [mx, my] = toXY(pt[0], pt[1]);
    maxExt = Math.max(maxExt, Math.abs(mx) * 1.45, Math.abs(my) * 1.9);
  }}));
  const halfH = maxExt * 0.72;
  const halfW = halfH * (W / H);
  const proj = (lon, lat) => {{
    const [mx, my] = toXY(lon, lat);
    return [W / 2 + (mx / halfW) * (W / 2), H / 2 - (my / halfH) * (H / 2)];
  }};
  const polyPath = (geom) => {{
    if (!geom || !geom.coordinates) return '';
    const rlist = geom.type === 'Polygon' ? [geom.coordinates[0]] : (geom.type === 'MultiPolygon' ? geom.coordinates.map(c => c[0]) : []);
    return rlist.filter(Boolean).map(r => 'M' + r.map(pt => proj(pt[0], pt[1]).map(v => v.toFixed(1)).join(',')).join('L') + 'Z').join(' ');
  }};
  const geomCenter = (geom) => {{
    if (!geom || !geom.coordinates) return [W / 2, H / 2];
    const pts = [];
    const walk = (c) => {{ if (typeof c[0] === 'number') pts.push(proj(c[0], c[1])); else c.forEach(walk); }};
    walk(geom.coordinates);
    if (!pts.length) return [W / 2, H / 2];
    return [pts.reduce((s, a) => s + a[0], 0) / pts.length, pts.reduce((s, a) => s + a[1], 0) / pts.length];
  }};

  let roadPaths = '';
  try {{
    const rdFeats = (typeof REF_RD !== 'undefined' && REF_RD && REF_RD.features) ? REF_RD.features : [];
    const lines = [];
    rdFeats.forEach(f => {{
      const g = f.geometry;
      if (!g || !g.coordinates) return;
      const segs = g.type === 'LineString' ? [g.coordinates] : (g.type === 'MultiLineString' ? g.coordinates : []);
      segs.forEach(seg => {{
        const ppts = seg.map(pt => proj(pt[0], pt[1]));
        if (ppts.some(([x, y]) => x >= -20 && x <= W + 20 && y >= -20 && y <= H + 20)) {{
          lines.push('M' + ppts.map(([x, y]) => `${{x.toFixed(1)}},${{y.toFixed(1)}}`).join('L'));
        }}
      }});
    }});
    if (lines.length) roadPaths = `<path d="${{lines.slice(0, 28).join(' ')}}" fill="none" stroke="#B5A69E" stroke-width="1.35" stroke-linecap="round"/>`;
  }} catch (e) {{}}

  const sitePath = polyPath(gj);
  const zones = p.landscape_zones || [];
  const fps = p.footprints || [];

  const rawPtrs = (p.map_pointers || []).map(pt => typeof pt === 'string' ? pt : `${{pt.label || ''}} (${{Math.round(pt.distance_m || 0)}} m)`);
  const cleanLabel = (s) => {{
    let t = String(s || '').replace(/^[^:]+:\s*/, '').trim();
    t = t.replace(/\[ANALYSED:\s*/i, '').replace(/\]/g, '').trim();
    t = t.replace(/^unclassified\b/i, 'Access Track').replace(/^track_grade\d\b/i, 'Desert Track').replace(/^path\b/i, 'Site Trail');
    return t.length > 30 ? t.slice(0, 28) + '…' : t;
  }};
  const findPtr = (re) => rawPtrs.find(s => re.test(s));

  const esc = (s) => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const pinTag = (x, y, text, fillCol, anchor = 'middle') => {{
    const tx = Math.max(46, Math.min(W - 46, x));
    const ty = Math.max(17, Math.min(H - 12, y));
    const lbl = esc(text);
    const pw = Math.min(182, Math.max(54, lbl.length * 4.8 + 14));
    const rx = anchor === 'start' ? Math.min(W - pw - 4, tx + 5) : (anchor === 'end' ? Math.max(4, tx - pw - 5) : Math.max(4, Math.min(W - pw - 4, tx - pw / 2)));
    return `<g><circle cx="${{x.toFixed(1)}}" cy="${{y.toFixed(1)}}" r="4" fill="${{fillCol}}" stroke="#FFFFFF" stroke-width="1.5"/>` +
      `<rect x="${{rx.toFixed(1)}}" y="${{(ty - 15).toFixed(1)}}" width="${{pw.toFixed(1)}}" height="15" rx="4" fill="rgba(255,250,247,0.96)" stroke="${{fillCol}}" stroke-width="1"/>` +
      `<text x="${{(rx + pw / 2).toFixed(1)}}" y="${{(ty - 4.8).toFixed(1)}}" text-anchor="middle" font-size="8.2" font-weight="800" fill="${{fillCol}}">${{lbl}}</text></g>`;
  }};

  let overlayHtml = '';
  const eKey = engName.toLowerCase();

  if (eKey === 'crystals') {{
    const fpPaths = fps.map(fp => `<path d="${{polyPath(fp.geom)}}" fill="#8C3325" fill-opacity="0.78" stroke="#FFFFFF" stroke-width="0.7"/>`).join('');
    const poiStr = findPtr(/roman|antinoopolis|deir abu shaar|desert breath|safari|garage|cultural|heritage|point of interest/i) || findPtr(/main roads|طريق/i) || rawPtrs[2] || rawPtrs[0] || 'Anchor POI';
    const roadStr = findPtr(/main roads|طريق|road network/i) || 'Access Track';
    const fpC = fps[0] ? geomCenter(fps[0].geom) : [W * 0.44, H * 0.42];
    const poiPos = [W * 0.72, H * 0.78];
    const rdPos = [W * 0.25, H * 0.22];
    overlayHtml =
      `<circle cx="${{fpC[0].toFixed(1)}}" cy="${{fpC[1].toFixed(1)}}" r="42" fill="none" stroke="#8C3325" stroke-width="1.15" stroke-dasharray="3.5,2.5" opacity="0.7"/>` +
      fpPaths +
      `<line x1="${{fpC[0].toFixed(1)}}" y1="${{fpC[1].toFixed(1)}}" x2="${{poiPos[0].toFixed(1)}}" y2="${{poiPos[1].toFixed(1)}}" stroke="#8C3325" stroke-width="1.4" stroke-dasharray="3,2"/>` +
      pinTag(fpC[0], fpC[1] - 4, 'Build Anchor', '#8C3325') +
      pinTag(poiPos[0], poiPos[1], cleanLabel(poiStr), '#D94432') +
      pinTag(rdPos[0], rdPos[1], cleanLabel(roadStr), '#524844');
  }} else if (eKey === 'cells') {{
    let topoHtml = '';
    const tg = p.terrain_grid;
    if (tg && Array.isArray(tg.z) && tg.z.length) {{
      const zs = tg.z.flat().filter(v => typeof v === 'number' && !isNaN(v));
      const zMin = Math.min(...zs), zMax = Math.max(...zs), zSpan = Math.max(0.5, zMax - zMin);
      const ny = tg.z.length, nx = tg.z[0].length;
      for (let iy = 0; iy < ny; iy++) {{
        for (let ix = 0; ix < nx; ix++) {{
          const zv = tg.z[iy][ix];
          if (typeof zv !== 'number' || isNaN(zv)) continue;
          const t = (zv - zMin) / zSpan;
          const cx = W * 0.24 + (ix / Math.max(1, nx - 1)) * (W * 0.52);
          const cy = H * 0.20 + (iy / Math.max(1, ny - 1)) * (H * 0.60);
          topoHtml += `<circle cx="${{cx.toFixed(1)}}" cy="${{cy.toFixed(1)}}" r="${{(1.8 + t * 2.6).toFixed(1)}}" fill="#1D4ED8" fill-opacity="${{(0.14 + t * 0.44).toFixed(2)}}"/>`;
        }}
      }}
    }}
    // Pull relief strictly from THIS site's driverTxt or terrain_analysis (never from peer cross-site mentions)
    const drvRel = String(driverTxt || '').match(/(\d+(?:\.\d+)?)\s*m\s*(?:DEM|relief|slope|escarpment|grade)/i);
    const reliefM = drvRel
      ? `${{drvRel[1]}} m Relief`
      : ((p.terrain_analysis && p.terrain_analysis.relief_m != null) ? `${{Number(p.terrain_analysis.relief_m).toFixed(1)}} m Relief` : 'Terrain Slope');
    const adaptMatch = String(driverTxt || p.nature_to_bldg || '').match(/(solar|wind|cistern|star bowl|escarpment|reedbed|tensile|vault)/i);
    const adaptLbl = adaptMatch ? `Adapt: ${{adaptMatch[1]}}` : 'Climate Adaptation';
    const fpPaths = fps.map(fp => `<path d="${{polyPath(fp.geom)}}" fill="#1D4ED8" fill-opacity="0.34" stroke="#1D4ED8" stroke-width="0.9"/>`).join('');
    overlayHtml =
      topoHtml + fpPaths +
      `<path d="M40,28 L92,56" stroke="#1D4ED8" stroke-width="1.8" stroke-dasharray="3.5,2"/>` +
      `<polygon points="94,57 85,57 89,50" fill="#1D4ED8"/>` +
      pinTag(66, 25, 'NNW Breeze / Solar', '#1D4ED8') +
      pinTag(W * 0.68, H * 0.38, reliefM, '#1D4ED8') +
      pinTag(W * 0.50, H * 0.82, adaptLbl, '#1E40AF');
  }} else {{
    const zPaths = zones.map(z => `<path d="${{polyPath(z.geom)}}" fill="${{z.color || '#0F766E'}}" fill-opacity="0.32" stroke="${{z.color || '#0F766E'}}" stroke-width="1"/>`).join('');
    const z0 = zones[0] ? geomCenter(zones[0].geom) : [W * 0.28, H * 0.34];
    const zLast = zones[zones.length - 1] ? geomCenter(zones[zones.length - 1].geom) : [W * 0.72, H * 0.68];
    const midPt = [(z0[0] + zLast[0]) / 2, Math.min(z0[1], zLast[1]) - 22];
    const el1 = findPtr(/farm|bird|motacilla|preserve|شايب/i) || (zones[0] ? zones[0].name : 'Ecology');
    const el2 = findPtr(/main roads|طريق|roman|deir abu shaar|highway/i) || (zones[zones.length - 1] ? zones[zones.length - 1].name : 'Civic Seam');
    overlayHtml =
      zPaths +
      `<path d="M${{z0[0].toFixed(1)}},${{z0[1].toFixed(1)}} Q${{midPt[0].toFixed(1)}},${{midPt[1].toFixed(1)}} ${{zLast[0].toFixed(1)}},${{zLast[1].toFixed(1)}}" fill="none" stroke="#0F766E" stroke-width="2.2" stroke-dasharray="4.5,2.5"/>` +
      pinTag(z0[0], z0[1], cleanLabel(el1), '#0F766E') +
      pinTag(zLast[0], zLast[1], cleanLabel(el2), '#0D9488') +
      pinTag(W / 2, H * 0.85, 'Symbiotic Loop', '#115E59');
  }}

  const satBg = p.satellite_lock
    ? `<image href="${{p.satellite_lock}}" x="0" y="0" width="${{W}}" height="${{H}}" preserveAspectRatio="xMidYMid slice" opacity="0.26"/>`
    : '';
  return `<div class="eng-rail-map" onclick="jumpTo3EngineMap(${{p.rank}})" title="Click to inspect ${{engName}} elements on the 3-Engine Map">` +
    `<svg viewBox="0 0 ${{W}} ${{H}}" xmlns="http://www.w3.org/2000/svg">` +
      `<rect width="${{W}}" height="${{H}}" fill="#F2ECE6"/>` +
      satBg +
      `<rect width="${{W}}" height="${{H}}" fill="rgba(247,243,238,0.42)"/>` +
      roadPaths +
      (sitePath ? `<path d="${{sitePath}}" fill="${{ec.bg}}" fill-opacity="0.48" stroke="${{ec.fg}}" stroke-width="1.6" stroke-dasharray="4.5,2.5"/>` : '') +
      overlayHtml +
      `<g transform="translate(${{W - 18}}, 15)"><circle r="8.5" fill="rgba(48,43,42,0.86)"/><text y="3" text-anchor="middle" font-size="8" font-weight="800" fill="#FFFAF7">N</text></g>` +
    `</svg></div>`;
}}

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
  const drv = (p.engine_trace && p.engine_trace.drivers) || {{}};
  const ptr0 = (p.map_pointers || []).map(pt => typeof pt === 'string' ? pt : `${{pt.label || ''}} (${{Math.round(pt.distance_m || 0)}} m)`).slice(0, 3).join('; ');
  const vals = [
    {{ lbl: 'Crystals', key: 'crystals', v: p.scores.crystals || 0, why: drv.crystals || `Development score from nearby POIs & corridors (${{ptr0 || 'site landmarks'}}).` }},
    {{ lbl: 'Cells', key: 'cells', v: p.scores.cells || 0, why: drv.cells || `Adaptation score from terrain relief, solar intensity & natural edge gradients.` }},
    {{ lbl: 'Corals', key: 'corals', v: p.scores.corals || 0, why: drv.corals || `Coordination score from bridging adjacent land uses, corridors & ecology.` }},
    {{ lbl: 'Access', key: 'Corridor & Network Connectivity', v: p.access || 0, why: `Regional road & arrival accessibility score (${{p.access || 0}}/100) based on distance to mapped roads & highways.` }}
  ];
  const escAttr = (s) => String(s || '').replace(/"/g, '&quot;');
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
    const d = vals[i];
    return `<line x1="${{cx}}" y1="${{cy}}" x2="${{x2.toFixed(1)}}" y2="${{y2.toFixed(1)}}" stroke="#D5C9C5" stroke-width="1"/>` +
           `<text class="score-explain" data-score-key="${{d.key}}" data-score-val="${{d.v}}" data-score-why="${{escAttr(d.why)}}" x="${{lx.toFixed(1)}}" y="${{ly.toFixed(1)}}" text-anchor="middle" font-size="10" font-weight="800" fill="#625753" style="cursor:help">${{d.lbl}} ${{d.v}}</text>`;
  }}).join('');
  const dots = vals.map((d, i) => {{
    const [x, y] = pt(d.v, i);
    return `<circle class="score-explain" data-score-key="${{d.key}}" data-score-val="${{d.v}}" data-score-why="${{escAttr(d.why)}}" cx="${{x.toFixed(1)}}" cy="${{y.toFixed(1)}}" r="5" fill="#FF614C" stroke="#A3473A" stroke-width="1.5" style="cursor:help"/>`;
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
  const nSteps = STORY_LABELS.length;
  const idx = ((stepIdx % nSteps) + nSteps) % nSteps;
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
  const prebuilt = {json.dumps(prebuilt_pdf_name if has_prebuilt_pdf else "")};
  if (prebuilt) {{
    const a = document.createElement('a');
    a.href = prebuilt;
    a.target = '_blank';
    a.download = prebuilt;
    document.body.appendChild(a);
    a.click();
    a.remove();
    return;
  }}
  document.body.classList.add('print-all');
  window.print();
  setTimeout(() => document.body.classList.remove('print-all'), 300);
}}

function switchMainTab(tab) {{
  document.getElementById('tab-proposals').style.display = tab === 'proposals' ? 'block' : 'none';
  document.getElementById('tab-maps').style.display = tab === 'maps' ? 'flex' : 'none';
  const skTab = document.getElementById('tab-skills');
  if (skTab) skTab.style.display = tab === 'skills' ? 'block' : 'none';
  document.getElementById('btn-tab-proposals').classList.toggle('active', tab === 'proposals');
  document.getElementById('btn-tab-maps').classList.toggle('active', tab === 'maps');
  const skBtn = document.getElementById('btn-tab-skills');
  if (skBtn) skBtn.classList.toggle('active', tab === 'skills');
  if (tab === 'proposals') {{
    setTimeout(() => miniMaps.forEach(m => m.invalidateSize()), 80);
  }} else if (tab === 'maps') {{
    setTimeout(() => {{
      if (typeof maps !== 'undefined') maps.forEach(m => m.invalidateSize());
      window.dispatchEvent(new Event('resize'));
    }}, 80);
  }} else if (tab === 'skills') {{
    renderSkillsTab();
  }}
}}

function jumpToProjectSkills(rank) {{
  const sel = document.getElementById('sk-filter-project');
  if (sel) sel.value = String(rank);
  const engSel = document.getElementById('sk-filter-engine');
  if (engSel) engSel.value = 'All';
  switchMainTab('skills');
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
    card.dataset.engine = p.engine || 'Crystals';
    const engBadge = `${{p.engine || 'Crystals'}} Engine`;
    const resPills = (p.resources_utilized || []).map(r => `<span class="pill ok" style="font-size:10.5px">${{r}}</span>`).join('');

    const rawFlags = Array.isArray(p.flags) ? p.flags : Object.entries(p.flags || {{}}).filter(([,v]) => !!v).map(([k]) => k.replace(/_/g, ' '));
    const flagPills = (rawFlags.length ? rawFlags : ['✓ Standard Compliance']).map(f => `<span class="pill ${{f.includes('✓') ? 'ok' : 'warn'}}">${{f}}</span>`).join('');
    const pullLine = extractPullLine(p.thesis_detailed);
    const pinBtns = (p.map_pointers || []).map((pt, pi) => {{
      if (typeof pt === 'string') {{
        return `<span class="pin-btn"><span class="pin-dot">${{pi + 1}}</span>${{pt}}</span>`;
      }}
      if (pt && typeof pt === 'object' && pt.label) {{
        return `<button type="button" class="pin-btn" onclick="focusPinOnMap(${{p.rank}}, ${{pt.lat}}, ${{pt.lon}}, '${{String(pt.label).replace(/'/g, '')}}')" title="Locate on satellite map">` +
          `<span class="pin-dot">${{pt.id || (pi + 1)}}</span>${{String(pt.label).split('(')[0].trim()}} · <b>${{pt.distance_m ?? ''}} m</b></button>`;
      }}
      return '';
    }}).join('');

    // Step 2: Distributed Constellation grouped by Experience Role
    const mr = p.massing_rationale || {{}};
    const vols = mr.volumes || [];
    const maxGfa = Math.max(...vols.map(v => parseNumber(v.area_m2, 1000)), 1);
    const classifyRole = (v) => {{
      const txt = `${{v.role || ''}} ${{v.name || ''}} ${{v.use || ''}}`.toLowerCase();
      if (txt.includes('stay') || txt.includes('lodge') || txt.includes('accom') || txt.includes('cabin') || txt.includes('suite')) return 'Eco-Accommodation';
      if (txt.includes('din') || txt.includes('food') || txt.includes('cafe') || txt.includes('kitchen') || txt.includes('retail') || txt.includes('market') || txt.includes('shop')) return 'Dining & Retail';
      return 'Core Experience Architecture';
    }};
    const roleOrder = ['Core Experience Architecture', 'Dining & Retail', 'Eco-Accommodation'];
    const groupedConstellation = roleOrder.map(role => {{
      const items = vols.map((v, vi) => ({{ v, vi }})).filter(({{ v }}) => classifyRole(v) === role);
      if (!items.length) return '';
      const cards = items.map(({{ v, vi }}) => {{
        const gfaVal = parseNumber(v.area_m2, 0);
        const pct = gfaVal > 0 ? Math.max(Math.round((gfaVal / maxGfa) * 100), 18) : 32;
        const nsfVal = v.nsf_m2 != null ? `${{Number(v.nsf_m2).toLocaleString()}} m² NSF` : '';
        const tareVal = v.tare_m2 ? `${{Number(v.tare_m2).toLocaleString()}} m² Tare` : '';
        const effStr = (v.nsf_gsf_pct != null && v.tare_m2) ? ` · ${{v.nsf_gsf_pct}}% NSF/GSF` : '';
        const spRows = (v.interior_zones || []).map(z => {{
          const isT = /tare|circulation|boh|mep|service|core/i.test(z.role || '');
          return `<div style="display:flex;justify-content:space-between;gap:8px;padding:3px 6px;border-radius:6px;background:${{isT ? '#FFF5E5' : '#FAF7F5'}};font-size:11px">` +
            `<span>${{z.name}} <span style="color:#7a6f6a">(${{z.role || 'Program'}})</span></span>` +
            `<b style="white-space:nowrap">${{Number(z.area_m2 || 0).toLocaleString()}} m²</b></div>`;
        }}).join('');
        return `<div class="mass-bar-item" onclick="focus3Way(${{p.rank}}, 'footprints', ${{vi}}, this)" title="Project Component">` +
          `<div class="mb-top"><span class="mb-name">${{v.name}}</span><span class="mb-stat">${{v.area_m2 || 'Component'}} GSF${{effStr}} · ${{v.height_floors || 'Day-to-Dusk'}}</span></div>` +
          `<div class="mb-track"><div class="mb-fill" style="width:${{pct}}%"></div></div>` +
          `<div class="mb-desc">${{v.use || v.shape_reason || ''}}</div>` +
          (nsfVal ? `<div style="font-size:10.5px;color:#625753;margin-top:4px"><b>Net vs Tare:</b> ${{nsfVal}}${{tareVal ? ' · ' + tareVal : ''}}</div>` : '') +
          (spRows ? `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:4px;margin-top:6px">${{spRows}}</div>` : '') +
          `</div>`;
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
    const zTiles = zones.map((z, zi) => {{
      const accBadge = z.access_level ? `<span class="pill" style="font-size:9.5px;padding:1px 6px">Access: ${{z.access_level}}</span>` : '';
      const watBadge = z.water_demand ? `<span class="pill" style="font-size:9.5px;padding:1px 6px">Water: ${{z.water_demand}}</span>` : '';
      const confBadge = z.confidence ? `<span class="pill" style="font-size:9.5px;padding:1px 6px;background:${{z.confidence === 'Measured GIS' ? '#EAF5EF' : '#FFF5E5'}};color:${{z.confidence === 'Measured GIS' ? '#246247' : '#775014'}}">${{z.confidence}}</span>` : '';
      const bldBadge = z.buildable === false ? `<span class="pill" style="font-size:9.5px;padding:1px 6px;background:#FCEEF0;color:#A12B3A">0% Buildable</span>` : (z.intervention === 'Activate' ? `<span class="pill ok" style="font-size:9.5px;padding:1px 6px">Buildable Interface</span>` : '');
      const evLine = z.gis_evidence ? `<div style="font-size:10.5px;color:#625753;margin-top:4px;border-top:1px dashed #E5DDD9;padding-top:3px"><b>GIS Evidence:</b> ${{z.gis_evidence}}</div>` : '';
      return `<div class="zone-tile" style="--zc:${{z.color}}" onclick="focus3Way(${{p.rank}}, 'zones', ${{zi}}, this)" title="Click to highlight on map">` +
        `<div class="zt-top"><span class="zt-pct">${{z.id || ''}} · ${{z.share_pct}}%</span><span class="pill" style="border-color:${{z.color}};background:${{z.color}}18;color:${{z.color}};font-size:10px;font-weight:800">${{z.intervention}}</span></div>` +
        `<div class="zt-name">${{z.short_name || z.name}} <span style="font-weight:600;color:#625753">(${{z.area_feddans}} fed. · ${{Number(z.area_m2 || 0).toLocaleString()}} m²)</span></div>` +
        `<div class="zt-act">${{z.outdoor_activities || z.why_here || ''}}</div>` +
        `<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:5px">${{bldBadge}}${{accBadge}}${{watBadge}}${{confBadge}}</div>` +
        evLine +
        `</div>`;
    }}).join('');
    const bEnv = p.buildable_envelope || null;
    const buildableEnvBar = bEnv ? `
      <div style="margin:8px 0;padding:9px 12px;border-radius:10px;background:${{bEnv.fits_envelope ? '#EAF5EF' : '#FFF5E5'}};border:1px solid ${{bEnv.fits_envelope ? '#B7DFC7' : '#E7C88B'}};font-size:11.5px">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
          <div><b style="color:${{bEnv.fits_envelope ? '#246247' : '#775014'}}">${{bEnv.fits_envelope ? '✓' : '⚠'}} Verified Development Interface (Buildable Envelope):</b> <b>${{Number(bEnv.net_buildable_m2 || 0).toLocaleString()}} m²</b> net buildable vs. <b>${{Number(bEnv.building_footprint_m2 || 0).toLocaleString()}} m²</b> building footprint (<b>${{bEnv.envelope_coverage_pct}}%</b> coverage)</div>
          <div style="font-size:10.5px;color:#4A413D"><b>${{bEnv.preserve_locked_pct}}%</b> locked 0% buildable (Preserve + Minimal Intervention) · <a href="landscape_zones.geojson" target="_blank" style="color:#A3473A;font-weight:700">landscape_zones.geojson ↗</a></div>
        </div>
        ${{bEnv.zoning_rationale ? `<div style="margin-top:6px;padding-top:6px;border-top:1px dashed ${{bEnv.fits_envelope ? '#B7DFC7' : '#E7C88B'}};color:#231E1C;line-height:1.45"><b style="color:#302B2A">Why This Site Is Zoned This Way:</b> ${{bEnv.zoning_rationale}}</div>` : ''}}
        ${{bEnv.method_summary ? `<div style="margin-top:4px;font-size:10.5px;color:#625753"><b>GIS Priority Order:</b> ${{bEnv.method_summary}}</div>` : ''}}
      </div>` : '';
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
    const actPills = (p.activities || []).map(a =>
      `<span class="pill ok" style="font-size:11px;padding:4px 9px">${{a}}</span>`
    ).join('');
    const settingTxt = natureHero;
    const tectonicTxt = (p.thesis_summary && p.thesis_summary.gesture_line) || exp.core_idea || '';
    const atmoTxt = exp.atmosphere || 'Warm directional light, deep courtyard shade, and tactile local stone.';

    const engColors = {{
      Crystals: {{ bg: '#FFF5F2', bd: '#E8B5A8', fg: '#8C3325', theme: 'Development', defn: 'Finding points of interest to build around, in, or at.' }},
      Cells: {{ bg: '#F2F7FF', bd: '#B5CCF5', fg: '#1D4ED8', theme: 'Adaptation', defn: 'Finding elements in site, nature, or context to unlock their full potential by adapting them into something new or better.' }},
      Corals: {{ bg: '#F0FAF8', bd: '#A5DCD2', fg: '#0F766E', theme: 'Coordination', defn: 'Finding elements in site, nature, or context to use better together or introduce a beneficial relationship.' }}
    }};
    const er = p.engine_reasoning || {{}};
    const etDrivers = (p.engine_trace && p.engine_trace.drivers) || {{}};
    const leadEng = p.engine || 'Crystals';
    const allEnginesOrder = [leadEng, ...['Crystals', 'Cells', 'Corals'].filter(e => e !== leadEng)];
    const peersLower = Object.fromEntries(Object.entries(er.peers || {{}}).map(([k, v]) => [k.toLowerCase(), v]));
    const driversLower = Object.fromEntries(Object.entries(etDrivers).map(([k, v]) => [k.toLowerCase(), v]));
    const engineRailCards = allEnginesOrder.map(engName => {{
      const ec = engColors[engName] || engColors.Crystals;
      const isLead = engName === leadEng;
      const eKey = engName.toLowerCase();
      const words = isLead
        ? (er.lead || (p.thesis_summary && p.thesis_summary.why_here) || '')
        : (peersLower[eKey] || `From my ${{ec.theme}} lens, this site supports ${{driversLower[eKey] || 'complementary site forces'}}.`);
      const driverTxt = driversLower[eKey] || '';
      const roleBg = isLead ? ec.fg : '#FFFFFF';
      const roleFg = isLead ? '#FFFAF7' : ec.fg;
      const roleLbl = isLead ? 'Lead' : 'Peer';
      const drvParts = String(driverTxt || '').split(/\s*\+\s*/).map(s => s.trim()).filter(Boolean);
      const matchForceKey = (txt) => {{
        const low = txt.toLowerCase();
        if (low.includes('corridor') || low.includes('connectivity') || low.includes('highway') || low.includes('road')) return 'Corridor & Network Connectivity';
        if (low.includes('solar') || low.includes('climate')) return 'Solar & Climate Intensity';
        if (low.includes('hydrology') || low.includes('water') || low.includes('wadi') || low.includes('cistern')) return 'Hydrology & Waterfront';
        if (low.includes('biodiversity') || low.includes('ecology') || low.includes('bird') || low.includes('farm') || low.includes('protected')) return 'Biodiversity & Ecology';
        if (low.includes('heritage') || low.includes('roman') || low.includes('desert breath') || low.includes('safari')) return 'Heritage & Culture Gravity';
        if (low.includes('civic') || low.includes('service')) return 'Civic & Service Deficit';
        return engName.toLowerCase();
      }};
      const drvPills = drvParts.map(dp => {{
        const fk = matchForceKey(dp);
        const numM = dp.match(/\((\d+(?:\.\d+)?)\)/);
        const valAttr = numM ? ` data-score-val="${{numM[1]}}"` : '';
        const whyAttr = ` data-score-why="${{dp.replace(/"/g, '&quot;')}} — primary GIS signal cited by ${{engName}} Engine for Site #${{p.rank}}."`;
        return `<span class="eng-drv-pill score-explain" tabindex="0" data-score-key="${{fk}}"${{valAttr}}${{whyAttr}} style="border-color:${{ec.bd}};cursor:help"><span style="color:${{ec.fg}}">●</span>${{dp}}</span>`;
      }}).join('');
      return `<div class="eng-rail-card" style="background:${{isLead ? ec.bg : '#FFFFFF'}};border-color:${{ec.bd}};${{isLead ? `border-left:4px solid ${{ec.fg}};` : ''}}">` +
        `<div class="eng-rail-top">` +
          `<span class="eng-rail-title" style="color:${{ec.fg}}">${{engineIconSVG(engName, 17, ec.fg)}}<span>${{engName}} · ${{ec.theme}}</span></span>` +
          `<span class="eng-rail-role" style="background:${{roleBg}};color:${{roleFg}};border:1px solid ${{ec.bd}}">${{roleLbl}}</span>` +
        `</div>` +
        `<div class="eng-rail-defn" style="color:${{ec.fg}}">${{ec.defn}}</div>` +
        `<div class="eng-rail-words">${{words}}</div>` +
        buildEngineElementMapSVG(p, engName, ec, words, driverTxt, isLead) +
        (drvPills ? `<div class="eng-rail-drivers">${{drvPills}}</div>` : '') +
      `</div>`;
    }}).join('');
    const engineRailHtml = `
      <aside class="proj-card-rail" aria-label="3-Engine First-Person Words">
        <div class="eng-rail-hdr"><span>3 Engines · Site Voice</span><span style="font-weight:700;color:#625753">First-Person</span></div>
        ${{engineRailCards}}
      </aside>`;

    const skillsList = (p.generated_skills || []).map(sk => {{
      const sEng = sk.engine || 'Crystals';
      const sCol = (engColors[sEng.replace(/\s*Engine/i, '')] || engColors.Crystals).fg;
      return `<div class="mchip" style="min-width:190px;flex:1"><div class="mk" style="display:flex;align-items:center;gap:4px;color:${{sCol}}">${{engineIconSVG(sEng, 13, sCol)}}<span>${{sEng}} · ${{sk.role || ''}}</span></div><b>${{sk.name || sk.skill_id || 'Skill'}}</b><br><span style="color:#625753">${{sk.summary || sk.description || ''}}</span></div>`;
    }}).join('');
    const skillsBox = skillsList
      ? `<div class="box" style="margin-top:10px"><div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:6px"><div class="sec-lbl" style="margin:0">Stage C Generated Design Skills (${{p.generated_skills.length}})</div><button type="button" class="btn-outline" style="font-size:11px;padding:3px 9px" onclick="jumpToProjectSkills(${{p.rank}})">Inspect in Stage C Skills Tab →</button></div><div class="micro-chips" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:8px">${{skillsList}}</div></div>`
      : '';

    card.innerHTML = `
      <div class="proj-card-shell">
      <div class="proj-card-main">
      <div class="card-visuals">
        <div id="render-wrap-${{p.rank}}" class="render-wrap">
          <img id="card-img-${{p.rank}}" class="static-media" style="display:block" src="${{p.has_editorial_render ? p.render : p.satellite_lock}}" alt="Site #${{p.rank}}" />
          <div class="rank-chip" style="display:inline-flex;align-items:center;gap:5px">${{engineIconSVG(leadEng, 13, '#FFFAF7')}}<span>${{engBadge.toUpperCase()}} • PROJECT #${{p.rank}} • ${{p.area_feddans}} FEDDANS • ${{p.built_gfa}}</span></div>
          <div class="media-toggle-bar">
            ${{p.has_editorial_render ? `<button type="button" class="media-tbtn active" onclick="swapCardMedia(${{p.rank}}, 'img', '${{p.render}}', this)">Whole-Site Aerial</button>` : ''}}
            ${{p.has_hero_render ? `<button type="button" class="media-tbtn" onclick="swapCardMedia(${{p.rank}}, 'img', '${{p.hero_render}}', this)">Hero Experience</button>` : ''}}
            <button type="button" class="media-tbtn ${{p.has_editorial_render ? '' : 'active'}}" onclick="swapCardMedia(${{p.rank}}, 'img', '${{p.satellite_lock}}', this)">Satellite</button>
          </div>
        </div>
        <div class="mini-map-wrap">
          <div id="mini-map-${{p.rank}}" class="mini-map"></div>
          <div class="map-legend-pill"><span><b style="color:#15803d">■</b> Preserve</span><span><b style="color:#64748b">■</b> Minimal</span><span><b style="color:#65a30d">■</b> Restore</span><span><b style="color:#0d9488">■</b> Enhance</span><span><b style="color:#d97706">■</b> Activate</span></div>
          <div class="map-meta-bar">
            <span class="map-coord-pill">${{Number(p.lat).toFixed(4)}}, ${{Number(p.lon).toFixed(4)}} · ${{p.area_feddans}} fed.</span>
            <button type="button" class="jump-map-btn" onclick="jumpTo3EngineMap(${{p.rank}})">3-Engine Map →</button>
          </div>
        </div>
      </div>

      <div class="card-head-bar">
        <div>
          <h2>${{p.title}}</h2>
          <div class="sub">${{p.subtitle}}</div>
          <div class="badge-row">
            <span class="pill" style="display:inline-flex;align-items:center;gap:5px;background:#302B2A;color:#FFFAF7;border-color:#302B2A">${{engineIconSVG(leadEng, 13, '#FFFAF7')}}${{engBadge}}</span>
            <span class="pill tier">${{visitMode}}</span>
            <span class="pill ok">Nature Hero: ${{natureHero}}</span>
            <span class="pill">${{p.area_feddans}} Feddans · ${{vols.length || 1}} Components</span>
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
          <div class="exp-story-hdr">
            <div class="hook-hero" style="margin-bottom:0">${{p.thesis_summary.hook}}</div>
            <div class="exp-strip">
              <div class="exp-cue"><div class="mk">Setting</div>${{settingTxt}}</div>
              <div class="exp-cue"><div class="mk">Architectural Move</div>${{tectonicTxt}}</div>
              <div class="exp-cue"><div class="mk">Atmosphere</div>${{atmoTxt}}</div>
            </div>
          </div>
          <div class="diag-lbl"><span>Space Program (${{p.built_gfa}} across ${{vols.length || 1}} Components)</span><span>${{visitMode}}</span></div>
          <div class="mass-bar-list">${{groupedConstellation}}</div>
        </div>

        <!-- STEP 2: NATURE & LANDSCAPE -->
        <div class="story-pane">
          <div class="diag-lbl"><span>2 · Two-Way Nature Loop &amp; Whole-Site Landscape (${{p.area_feddans}} Feddans)</span><span>Click any zone to zoom on map</span></div>
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
          ${{buildableEnvBar}}
          <div class="zone-grid">${{zTiles}}</div>
          ${{elChips ? `<div style="margin-top:8px"><div style="font-size:10.5px;font-weight:800;text-transform:uppercase;color:#625753;margin-bottom:5px">Outdoor Destinations:</div>${{elChips}}</div>` : ''}}
          <div class="risk-strip" style="margin-top:8px"><b>⚠ Environmental &amp; Resource Guardrail:</b> ${{p.landscape_summary.tradeoffs_risk}}</div>
        </div>

        <!-- STEP 3: SITE & GIS SIGNAL -->
        <div class="story-pane">
          <div class="story-grid">
            <div class="diag-card">
              <div class="diag-lbl"><span>3 · Site Signal Radar &amp; Real GIS Drivers</span><span>Click pins to locate</span></div>
              ${{buildSignalRadarSVG(p)}}
              <div class="pin-row">${{pinBtns}}</div>
            </div>
            <div class="diag-card">
              <div class="diag-lbl"><span>Why This Site &amp; Landscape Strategy</span><span>${{p.area_feddans}} Feddans</span></div>
              <div class="micro-chips">
                <div class="mchip"><div class="mk">Why Here</div>${{p.thesis_summary.why_here}}</div>
                <div class="mchip"><div class="mk">Site Resources Utilized</div>${{resPills || 'All active plot forces'}}${{p.resource_coverage_rationale ? `<div style="margin-top:4px;color:#625753;font-size:11px">${{p.resource_coverage_rationale}}</div>` : ''}}</div>
                <div class="mchip"><div class="mk">Landscape Backbone</div>${{p.landscape_summary.backbone || ''}}</div>
                <div class="mchip"><div class="mk">Architecture–Landscape Interface</div>${{p.landscape_summary.arch_interface || ''}}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- STEP 4: FEASIBILITY & BLUEPRINT -->
        <div class="story-pane">
          <div class="story-grid">
            <div class="diag-card">
              <div class="diag-lbl"><span>4 · Whole-Site CapEx Split &amp; Revenue Mix</span><span>Building + Landscape</span></div>
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
              ${{(p.commercial_screening && p.commercial_screening.length) ? `<div style="margin-top:10px;padding:9px 11px;background:#FFFAF7;border:1px solid var(--nest-line);border-radius:10px"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px"><span class="mk" style="color:var(--nest-edge)">Commercial Viability Screening</span><span style="font-size:10px;color:#775014;background:#FFF5E5;padding:2px 7px;border-radius:999px;font-weight:700">Unvalidated Hypotheses</span></div><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:5px">${{p.commercial_screening.map((cs, csi) => `<div style="font-size:11px;line-height:1.35;background:#fff;border:1px solid var(--nest-line);border-radius:7px;padding:5px 7px"><b>${{csi + 1}}. ${{cs.question}}</b><br><span style="color:#625753">${{cs.answer}}</span></div>`).join('')}}</div></div>` : ''}}
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
            <div style="font-size:11.5px;color:#625753"><b>Engine Reasoning:</b> ${{(p.engine_reasoning && p.engine_reasoning.lead) || (p.engine_trace && p.engine_trace.synthesis_note) || ''}}</div>
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
        ${{((p.rag_citations && ((p.rag_citations.codes && p.rag_citations.codes.length) || (p.rag_citations.precedents && p.rag_citations.precedents.length))) ? `<div class="box" style="margin-top:10px"><div class="sec-lbl" style="display:flex;justify-content:space-between;align-items:center"><span>Egyptian Codes &amp; Architectural Precedents (Cited RAG)</span><span style="font-size:10px;color:#5c534e;font-weight:600">NEST Portable RAG v3 · Reference Only</span></div><div class="two-col" style="margin-top:6px"><div><div style="font-size:11px;font-weight:700;color:#8c3b2b;margin-bottom:5px;text-transform:uppercase;letter-spacing:.4px">Egyptian Codes &amp; Regulations</div>${{(p.rag_citations.codes || []).map(c => `<div style="font-size:11px;line-height:1.4;background:#FFFAF7;border:1px solid var(--nest-line);border-radius:8px;padding:7px 9px;margin-bottom:6px"><div style="display:flex;justify-content:space-between;gap:6px;margin-bottom:3px"><b style="color:#2b2320">${{c.doc_name || c.file}}</b><span style="white-space:nowrap;font-size:10px;background:#F3E7E1;color:#7a3324;padding:1px 6px;border-radius:999px;font-weight:700">p. ${{c.page}}${{c.extraction && c.extraction !== 'text' ? ' · OCR' : ''}}</span></div><div style="color:#5c524e">${{c.excerpt}}</div></div>`).join('')}}</div><div><div style="font-size:11px;font-weight:700;color:#1f6f5b;margin-bottom:5px;text-transform:uppercase;letter-spacing:.4px">Architectural &amp; Climate Precedents</div>${{(p.rag_citations.precedents || []).map(r => `<div style="font-size:11px;line-height:1.4;background:#F7FCFA;border:1px solid var(--nest-line);border-radius:8px;padding:7px 9px;margin-bottom:6px"><div style="display:flex;justify-content:space-between;gap:6px;margin-bottom:3px"><b style="color:#2b2320">${{r.doc_name || r.file}}</b><span style="white-space:nowrap;font-size:10px;background:#E2F3EC;color:#195948;padding:1px 6px;border-radius:999px;font-weight:700">p. ${{r.page}}</span></div><div style="color:#5c524e">${{r.excerpt}}</div></div>`).join('')}}</div></div></div>` : '')}}
        ${{skillsBox}}
      </div>
      </div>
      ${{engineRailHtml}}
      </div>
    `;

    stack.appendChild(card);

    // Initialize Live 3D WebGL Stage
    initWebGL3D(p);

    // Initialize Tri-Layer Leaflet Mini-Map when container exists
    const mmEl = document.getElementById('mini-map-' + p.rank);
    if (mmEl) try {{
      const mm = L.map(mmEl, {{ center: [p.lat, p.lon], zoom: 14, zoomControl: true, attributionControl: false, scrollWheelZoom: true }});
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

window.filterByEngine = function(eng, btn) {{
  document.querySelectorAll('.eng-fbtn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  document.querySelectorAll('.proj-card').forEach(card => {{
    card.style.display = (eng === 'All' || card.dataset.engine === eng) ? '' : 'none';
  }});
}};

window.renderTab2EngineReasoning = function() {{
  const box = document.getElementById('tab2-engine-reasoning');
  if (!box) return;
  const engMeta = [
    {{ key: 'Crystals', sub: 'Development — Finding points of interest to build around, in, or at.', bg: '#FFF5F2', bd: '#E8B5A8', fg: '#8C3325' }},
    {{ key: 'Cells', sub: 'Adaptation — Unlocking an element’s full potential by adapting it into something new or better.', bg: '#F2F7FF', bd: '#B5CCF5', fg: '#1D4ED8' }},
    {{ key: 'Corals', sub: 'Coordination — Using elements better together or introducing a beneficial relationship.', bg: '#F0FAF8', bd: '#A5DCD2', fg: '#0F766E' }},
  ];
  const anyReason = NEST_PROJECTS.some(p => p.engine_reasoning && p.engine_reasoning.lead);
  if (!anyReason) {{
    box.innerHTML = `<div style="font-size:12px;color:#625753"><b>3-Engine First-Person Reasoning:</b> Author <code>engine_reasoning</code> in Stage B seeds to display each engine's site-selection narrative here.</div>`;
    return;
  }}
  const cols = engMeta.map(em => {{
    const led = NEST_PROJECTS.filter(p => (p.engine || 'Crystals') === em.key);
    const items = led.length ? led.map(p => {{
      const leadTxt = (p.engine_reasoning && p.engine_reasoning.lead) || (p.thesis_summary && p.thesis_summary.why_here) || '';
      return `<div style="background:#fff;border:1px solid ${{em.bd}};border-radius:8px;padding:7px 9px;margin-bottom:6px;font-size:11.5px;line-height:1.42"><div style="font-weight:800;color:${{em.fg}};margin-bottom:2px">Site #${{p.rank}} · ${{p.title}}</div><div style="color:#2b2320">${{leadTxt}}</div></div>`;
    }}).join('') : `<div style="font-size:11.5px;color:#7a6f6a">No projects led by ${{em.key}} on this plot.</div>`;
    return `<div style="background:${{em.bg}};border:1px solid ${{em.bd}};border-radius:11px;padding:9px 11px"><div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.4px;color:${{em.fg}}">${{engineIconSVG(em.key, 16, em.fg)}}<span>${{em.key}} Engine</span></div><div style="font-size:10.5px;color:#625753;margin-bottom:7px;margin-top:2px">${{em.sub}}</div>${{items}}</div>`;
  }}).join('');
  box.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span style="font-size:12px;font-weight:800;color:#231E1C;text-transform:uppercase;letter-spacing:.4px">How Each Engine Read This Plot (First-Person Reasoning)</span><span style="font-size:10.5px;color:#625753">Agent-Authored Stage B Engine Trace</span></div><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px">${{cols}}</div>`;
}};

(function upgradeAnalysisLayerTooltips() {{
  const EXTRA = {{
    'Corridor & Network Connectivity': {{ title: 'Corridor & Network Connectivity', scale: '0 – 100', desc: 'Measures how well a site connects to regional highways, paved roads, tracks, ports, ferries, and transit corridors. High scores = strong arrival access & movement seams; low scores = remote/off-grid.', formula: '<b>What drives the score:</b> Proximity to highways, paved roads, ports/stations, and multi-road intersections × Engine Terrain Affinity.', bands: '<b>Bands:</b> 75–100 Direct Highway/Corridor · 45–74 Secondary Road · &lt;45 Remote' }},
    'Hydrology & Waterfront': {{ title: 'Hydrology & Waterfront', scale: '0 – 100', desc: 'Measures proximity and edge interface with seas, rivers, canals, lakes, wetlands, and seasonal wadi drainage channels.', formula: '<b>What drives the score:</b> Distance to mapped shorelines, water bodies, and hydrological runoff corridors × Engine Terrain Affinity.', bands: '<b>Bands:</b> 75–100 Direct Water/Wadi Edge · 45–74 Near Drainage · &lt;45 Dry Inland' }},
    'Solar & Climate Intensity': {{ title: 'Solar & Climate Intensity', scale: '0 – 100', desc: 'Measures solar radiation potential, open sky exposure, diurnal thermal swing, and passive cooling/wind-harvesting opportunity.', formula: '<b>What drives the score:</b> Open unshaded canvas, topographic exposure/relief, and climatic intensity × Engine Terrain Affinity.', bands: '<b>Bands:</b> 75–100 Peak Solar/Passive Potential · 45–74 Strong · &lt;45 Sheltered' }},
    'Biodiversity & Ecology': {{ title: 'Biodiversity & Ecology', scale: '0 – 100', desc: 'Measures ecological richness from protected areas, GBIF wildlife & migratory bird sightings, green corridors, and sensitive habitats.', formula: '<b>What drives the score:</b> Proximity to protected zones, species/flyway records, and natural vegetation × Engine Terrain Affinity.', bands: '<b>Bands:</b> 75–100 High Ecological Value · 45–74 Buffer/Transition · &lt;45 Low Signal' }},
    'Heritage & Culture Gravity': {{ title: 'Heritage & Culture Gravity', scale: '0 – 100', desc: 'Measures cultural pull and sightline proximity to archaeological sites, ancient Roman/caravan routes, land art, and historic landmarks.', formula: '<b>What drives the score:</b> Ring-standoff & proximity to mapped heritage/cultural POIs × Engine Terrain Affinity.', bands: '<b>Bands:</b> 75–100 Prime Landmark Ring · 45–74 Cultural Corridor · &lt;45 No Nearby Heritage' }},
    'Civic & Service Deficit': {{ title: 'Civic & Service Deficit', scale: '0 – 100', desc: 'Measures where nearby communities or travelers lack schools, clinics, markets, shade, or public civic amenities.', formula: '<b>What drives the score:</b> Local population/visitor catchment minus existing civic facilities within service radius × Engine Affinity.', bands: '<b>Bands:</b> 75–100 High Unmet Civic Need · 45–74 Moderate Gap · &lt;45 Well-Served' }},
    'Hidden Potential': {{ title: 'Untapped Potential (Stage 3)', scale: '0 – 100', desc: 'Reveals overlooked, under-built pockets where strong spatial forces converge without dense existing urban clutter.', formula: '<b>Math:</b> Dominant/Synergy forces + Under-built Canvas + Natural Evidence.', bands: '<b>Bands:</b> 75–100 Prime Shortlist Site · 50–74 Promising · &lt;50 Saturated/Low' }},
    'Best-Fit Typology': {{ title: 'Dominant Spatial Force (Stage 2)', scale: 'Categorical', desc: 'Colors each 50×50 m cell by whichever of the 6 spatial forces scored highest under that engine’s rules.', formula: '<b>Math:</b> <code>argmax</code> across the 6 engine-weighted force layers.', bands: '<b>Use:</b> See which single force leads in each zone of the plot.' }},
    'Mixed-Use (2+)': {{ title: 'Balanced Pair Synergy (2+)', scale: '0 – 100', desc: 'Highlights cells where 2+ compatible forces are both high AND balanced — penalizing lopsided pairs.', formula: '<b>Formula:</b> <code>max(0, Average − Spread)</code> across compatible pairs.', bands: '<b>Trigger:</b> ≥60 auto-activates 2+ mixed-use program.' }},
    'Mixed-Use (3+)': {{ title: 'Balanced Trio Synergy (3+)', scale: '0 – 100', desc: 'Pinpoints rare convergence zones where 3+ compatible forces align at similar strength.', formula: '<b>Formula:</b> <code>max(0, Average − Spread)</code> across compatible trios.', bands: '<b>Trigger:</b> ≥60 auto-activates 3+ flagship program.' }},
  }};
  if (typeof SCORE_EXPLAINERS !== 'undefined') Object.assign(SCORE_EXPLAINERS, EXTRA);

  // Attach rich hover tooltips to all Stage 1/2/3 layer chips (removing native title so custom tooltip shines)
  document.querySelectorAll('.layer-chip[data-layer]').forEach(btn => {{
    btn.classList.add('score-explain');
    btn.setAttribute('data-score-key', btn.getAttribute('data-layer'));
    btn.removeAttribute('title');
  }});

  // Upgrade tooltip rendering to show dynamic "Why this score" whenever present
  const tip = document.getElementById('nest-score-tip');
  if (tip) {{
    document.addEventListener('mouseover', e => {{
      const el = e.target.closest('.score-explain');
      if (!el) return;
      const key = el.getAttribute('data-score-key') || el.getAttribute('data-layer');
      const val = el.getAttribute('data-score-val');
      let why = el.getAttribute('data-score-why');
      if (!why && el.closest('.bar-row')) {{
        const row = el.closest('.bar-row');
        const num = (row.textContent.match(/(\d+)\s*$/) || [])[1];
        if (num) {{
          const sc = Number(num);
          const band = sc >= 75 ? 'Peak signal' : (sc >= 50 ? 'Strong signal' : (sc >= 25 ? 'Moderate signal' : 'Low / distant signal'));
          const cardHdr = (row.closest('.eng-card')?.querySelector('h4')?.textContent || 'this engine').trim();
          why = `${{band}} (${{sc}}/100) under ${{cardHdr}}; ${{sc >= 50 ? 'strong mapped GIS proximity/density for this layer at the clicked 50 m cell.' : 'weaker or more distant GIS features for this layer here.'}}`;
        }}
      }}
      const info = (typeof SCORE_EXPLAINERS !== 'undefined' && SCORE_EXPLAINERS[key]) || EXTRA[key];
      if (!info) return;
      const scaleTxt = (val !== null && val !== '') ? `${{val}} / 100` : info.scale;
      const whyBlock = why ? `<div style="margin:5px 0;padding:5px 7px;border-radius:6px;background:#FFF5F2;border-left:3px solid #FF614C;color:#231E1C;font-size:11px;line-height:1.38"><b>Why this score:</b> ${{why}}</div>` : '';
      tip.innerHTML = `<div class="tip-hdr"><span class="tip-title">${{info.title}}</span><span class="tip-scale">${{scaleTxt}}</span></div><div class="tip-desc">${{info.desc}}</div>${{whyBlock}}<div class="tip-formula">${{info.formula}}</div><div class="tip-bands">${{info.bands}}</div>`;
      tip.classList.add('visible');
    }}, true);
  }}
}})();

// --- TAB 3: STAGE C SKILLS DASHBOARD & INTERACTIVE INSPECTOR ---
let _skillsInitDone = false;
let _lastFilteredSkills = [];

function _escHtml(s) {{
  return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function _triggerJsonDownload(filename, obj) {{
  const blob = new Blob([JSON.stringify(obj, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}}

function initSkillsFilters() {{
  if (_skillsInitDone) return;
  _skillsInitDone = true;
  const pSel = document.getElementById('sk-filter-project');
  const tSel = document.getElementById('sk-filter-tool');
  const aSel = document.getElementById('sk-filter-action');
  if (!pSel || !tSel || !aSel) return;

  NEST_PROJECTS.forEach(p => {{
    const opt = document.createElement('option');
    opt.value = String(p.rank);
    opt.textContent = `Site #${{p.rank}} · ${{p.title}}`;
    pSel.appendChild(opt);
  }});

  const tools = [...new Set(NEST_STAGE_C_SKILLS.flatMap(s => s.tools || []))].sort();
  tools.forEach(t => {{
    const opt = document.createElement('option');
    opt.value = t;
    opt.textContent = t;
    tSel.appendChild(opt);
  }});

  const acts = [...new Set(NEST_STAGE_C_SKILLS.map(s => s.action_type || 'Guidance'))].sort();
  acts.forEach(a => {{
    const opt = document.createElement('option');
    opt.value = a;
    opt.textContent = a;
    aSel.appendChild(opt);
  }});
}}

function resetSkillFilters() {{
  ['sk-filter-project', 'sk-filter-engine', 'sk-filter-tool', 'sk-filter-action'].forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.value = 'All';
  }});
  renderSkillsTab();
}}

function getFilteredSkills() {{
  const pf = (document.getElementById('sk-filter-project') || {{ value: 'All' }}).value;
  const ef = (document.getElementById('sk-filter-engine') || {{ value: 'All' }}).value;
  const tf = (document.getElementById('sk-filter-tool') || {{ value: 'All' }}).value;
  const af = (document.getElementById('sk-filter-action') || {{ value: 'All' }}).value;
  return NEST_STAGE_C_SKILLS.filter(s => {{
    if (pf !== 'All' && String(s.project_rank) !== pf) return false;
    if (ef !== 'All' && s.engine_key !== ef) return false;
    if (tf === '__agnostic__') {{
      if ((s.tools || []).length > 0) return false;
    }} else if (tf !== 'All' && !(s.tools || []).includes(tf)) {{
      return false;
    }}
    if (af !== 'All' && (s.action_type || '') !== af) return false;
    return true;
  }});
}}

function renderSkillsTab() {{
  initSkillsFilters();
  const container = document.getElementById('skills-lanes');
  const badge = document.getElementById('sk-count-badge');
  if (!container) return;

  const filtered = getFilteredSkills();
  _lastFilteredSkills = filtered;
  if (badge) badge.textContent = `${{filtered.length}} of ${{NEST_STAGE_C_SKILLS.length}} skills`;

  if (!NEST_STAGE_C_SKILLS.length) {{
    container.innerHTML = `<div class="box" style="grid-column:1/-1"><b>No Stage C skills generated yet.</b> Run <code>python stage_c_skills.py --run-dir &lt;run_dir&gt; --all</code> and rebuild the dashboard.</div>`;
    return;
  }}

  const lanes = [
    {{ key: 'Crystals', theme: 'Development', defn: 'Finding points of interest to build around, in, or at.', bg: '#FFF5F2', bd: '#E8B5A8', fg: '#8C3325' }},
    {{ key: 'Cells', theme: 'Adaptation', defn: 'Finding elements in site, nature, or context to unlock their full potential by adapting them into something new or better.', bg: '#F2F7FF', bd: '#B5CCF5', fg: '#1D4ED8' }},
    {{ key: 'Corals', theme: 'Coordination', defn: 'Finding elements in site, nature, or context to use better together or introduce a beneficial relationship.', bg: '#F0FAF8', bd: '#A5DCD2', fg: '#0F766E' }},
  ];

  container.innerHTML = lanes.map(ln => {{
    const items = filtered.filter(s => s.engine_key === ln.key);
    const cardsHtml = items.length ? items.map(s => {{
      const raw = s.raw || {{}};
      const actType = s.action_type || 'Guidance';
      const actBg = actType === 'Warning' ? '#FCEEF0' : (actType === 'Study' ? '#FFF5E5' : '#EAF5EF');
      const actFg = actType === 'Warning' ? '#A12B3A' : (actType === 'Study' ? '#775014' : '#246247');
      const toolChips = (s.tools || []).length
        ? (s.tools || []).map(t => `<span class="sk-tool">${{_escHtml(t)}}</span>`).join('')
        : `<span class="sk-tool" style="background:#EAF5EF;color:#246247;border-color:#24624733">Design Principle (Tool-Agnostic)</span>`;
      return `<div class="sk-card" onclick="openSkillInspector('${{_escHtml(s.uid)}}')">` +
        `<div class="sk-card-top">` +
          `<span class="pill" style="font-size:10px;padding:2px 6px">Site #${{s.project_rank}}</span>` +
          `<span class="pill" style="font-size:10px;padding:2px 6px;background:${{actBg}};color:${{actFg}};border-color:${{actFg}}44">${{_escHtml(actType)}}</span>` +
        `</div>` +
        `<div class="sk-card-title">${{_escHtml(raw.title || raw.skill_id)}}</div>` +
        `<div class="sk-card-def">${{_escHtml(raw.definition || '')}}</div>` +
        `<div class="sk-tools-row">${{toolChips}}</div>` +
      `</div>`;
    }}).join('') : `<div style="font-size:11.5px;color:#7a6f6a;padding:8px 4px">No matching ${{ln.key}} skills.</div>`;

    return `<div class="sk-lane" style="background:${{ln.bg}};border-color:${{ln.bd}}">` +
      `<div class="sk-lane-hdr">` +
        `<span style="display:inline-flex;align-items:center;gap:7px;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.4px;color:${{ln.fg}}">${{engineIconSVG(ln.key, 18, ln.fg)}}<span>${{ln.key}} (${{ln.theme}})</span></span>` +
        `<span class="pill" style="background:#fff;border-color:${{ln.bd}};color:${{ln.fg}};font-size:10.5px">${{items.length}}</span>` +
      `</div>` +
      `<div class="sk-lane-def">${{_escHtml(ln.defn)}}</div>` +
      `${{cardsHtml}}` +
    `</div>`;
  }}).join('');
}}

function openSkillInspector(uid) {{
  const s = NEST_STAGE_C_SKILLS.find(x => x.uid === uid);
  if (!s) return;
  const raw = s.raw || {{}};
  const attrs = raw.attributes || {{}};
  const act = raw.action || {{}};
  const engColors = {{
    Crystals: {{ fg: '#8C3325', bg: '#FFF5F2', bd: '#E8B5A8', theme: 'Development' }},
    Cells: {{ fg: '#1D4ED8', bg: '#F2F7FF', bd: '#B5CCF5', theme: 'Adaptation' }},
    Corals: {{ fg: '#0F766E', bg: '#F0FAF8', bd: '#A5DCD2', theme: 'Coordination' }},
  }};
  const ec = engColors[s.engine_key] || engColors.Crystals;

  const hdr = document.getElementById('sk-drawer-hdr');
  const body = document.getElementById('sk-drawer-body');
  if (!hdr || !body) return;

  hdr.innerHTML = `<div>` +
    `<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;flex-wrap:wrap">` +
      `<span class="pill" style="display:inline-flex;align-items:center;gap:5px;background:${{ec.bg}};border-color:${{ec.bd}};color:${{ec.fg}};font-size:10.5px">${{engineIconSVG(s.engine_key, 15, ec.fg)}}${{s.engine_key}} (${{ec.theme}})</span>` +
      `<span class="pill" style="font-size:10.5px">Site #${{s.project_rank}} · ${{_escHtml(s.project_title)}}</span>` +
      `<span class="pill" style="font-size:10.5px">${{_escHtml(raw.role_in_project || '')}}</span>` +
    `</div>` +
    `<div style="font-size:15px;font-weight:800;color:var(--nest-ink)">${{_escHtml(raw.title || raw.skill_id)}}</div>` +
    `<div style="font-size:11px;color:var(--nest-muted);margin-top:2px"><code>${{_escHtml(raw.skill_id || s.filename)}}</code></div>` +
  `</div>` +
  `<div style="display:flex;gap:6px;flex:none">` +
    `<button type="button" class="btn-coral" style="font-size:11px;padding:6px 10px" onclick="downloadSingleSkill('${{_escHtml(s.uid)}}')">⬇ Download .json</button>` +
    `<button type="button" class="btn-outline" style="font-size:12px;padding:6px 10px" onclick="closeSkillInspector()">✕</button>` +
  `</div>`;

  const triggersHtml = (raw.trigger || []).map(t => `<li style="margin-bottom:3px">${{_escHtml(t)}}</li>`).join('');
  let anatomyHtml = '';

  if (s.engine_key === 'Crystals') {{
    const ax = attrs.axes || {{}};
    const facetsHtml = (attrs.facets || []).map(f =>
      `<div style="padding:6px 8px;background:#FAF7F5;border:1px solid #EAE1DD;border-radius:8px;margin-bottom:5px;font-size:11.5px"><b>${{_escHtml(f.capability)}}</b><div class="sk-tools-row" style="margin-top:4px">${{(f.tool || []).map(t => `<span class="sk-tool">${{_escHtml(t)}}</span>`).join('')}}</div></div>`
    ).join('');
    const mem = attrs.memory || {{}};
    anatomyHtml = `
      <div class="sk-sec"><div class="sk-sec-lbl">Crystals Geometry &amp; Governance</div>
        <div class="sk-kv">
          <div class="sk-kv-item"><b>Scale</b>${{_escHtml(attrs.scale)}}</div>
          <div class="sk-kv-item"><b>Field</b>${{_escHtml(attrs.field)}}</div>
          <div class="sk-kv-item"><b>State / Density</b>${{_escHtml(attrs.state)}} · ${{_escHtml(attrs.density)}}</div>
          <div class="sk-kv-item"><b>Growth / Resilience</b>${{_escHtml(attrs.growth)}} · ${{_escHtml(attrs.resilience)}}</div>
          <div class="sk-kv-item"><b>Space Axis</b>${{_escHtml(ax.space)}}</div>
          <div class="sk-kv-item"><b>Time / Depth</b>${{_escHtml(ax.time)}} (${{_escHtml(ax.depth)}})</div>
        </div>
      </div>
      <div class="sk-sec"><div class="sk-sec-lbl">Facets &amp; CAD/BIM Tools</div>${{facetsHtml}}</div>
      <div class="sk-sec"><div class="sk-sec-lbl">Bonds &amp; Memory</div>
        <div style="margin-bottom:6px">${{(attrs.bonds || []).map(b => `<span class="pill" style="font-size:10.5px;margin-right:4px">${{_escHtml(b)}}</span>`).join('')}}</div>
        <div style="font-size:11.5px;color:#4A413D"><b>Derived From:</b> ${{(mem.past_experiences || []).map(_escHtml).join(' · ')}}<br><b>Lessons:</b> ${{(mem.lessons_learned || []).map(_escHtml).join(' · ')}}</div>
      </div>`;
  }} else if (s.engine_key === 'Cells') {{
    const he = attrs.host_element || {{}};
    const tr = attrs.transformation || {{}};
    const lim = attrs.limits_and_proof || {{}};
    const movesHtml = (attrs.adaptation_moves || []).map(m =>
      `<div style="padding:6px 8px;background:#FAF7F5;border:1px solid #EAE1DD;border-radius:8px;margin-bottom:5px;font-size:11.5px"><b>${{_escHtml(m.move)}}</b> <span class="pill" style="font-size:10px;padding:1px 6px">${{_escHtml(m.reversibility)}}</span><div class="sk-tools-row" style="margin-top:4px">${{(m.tools || []).map(t => `<span class="sk-tool">${{_escHtml(t)}}</span>`).join('')}}</div></div>`
    ).join('');
    anatomyHtml = `
      <div class="sk-sec"><div class="sk-sec-lbl">Host Element &amp; Transformation (From → To)</div>
        <div class="sk-kv" style="margin-bottom:6px">
          <div class="sk-kv-item"><b>Host Element (${{_escHtml(he.category)}})</b>${{_escHtml(he.element)}}</div>
          <div class="sk-kv-item"><b>Current Condition</b>${{_escHtml(he.current_condition)}}</div>
        </div>
        <div style="padding:8px 10px;background:#F2F7FF;border:1px solid #B5CCF5;border-radius:9px;font-size:11.5px">
          <div><b>From:</b> ${{_escHtml(tr.from_state)}}</div>
          <div style="margin-top:3px"><b>To:</b> ${{_escHtml(tr.to_state)}}</div>
          <div style="margin-top:3px;color:#1D4ED8"><b>Value Unlocked:</b> ${{_escHtml(tr.value_unlocked)}}</div>
        </div>
      </div>
      <div class="sk-sec"><div class="sk-sec-lbl">Adaptation Moves &amp; Tools</div>${{movesHtml}}</div>
      <div class="sk-sec"><div class="sk-sec-lbl">Limits, Site Checks &amp; Fallback (${{_escHtml(attrs.maturity || 'Concept')}})</div>
        <div style="font-size:11.5px;color:#4A413D;line-height:1.45">
          <b>Constraints:</b> ${{(lim.constraints || []).map(_escHtml).join(' · ')}}<br>
          <b>Site Checks Needed:</b> ${{(lim.site_checks_needed || []).map(_escHtml).join(' · ')}}<br>
          <b>Fallback:</b> ${{_escHtml(lim.fallback)}}
        </div>
      </div>`;
  }} else {{
    const resHtml = (attrs.resources || []).map(r =>
      `<div style="padding:6px 8px;background:#FAF7F5;border:1px solid #EAE1DD;border-radius:8px;margin-bottom:5px;font-size:11.5px"><b>${{_escHtml(r.resource)}}</b> — ${{_escHtml(r.potential)}}<div style="font-size:10.5px;color:#625753;margin-top:2px">Constraints: ${{(r.constraints || []).map(_escHtml).join('; ')}}</div></div>`
    ).join('');
    const brHtml = (attrs.branches || []).map(b =>
      `<div style="padding:6px 8px;background:#FAF7F5;border:1px solid #EAE1DD;border-radius:8px;margin-bottom:5px;font-size:11.5px"><b>${{_escHtml(b.direction)}}</b> <span class="pill" style="font-size:10px;padding:1px 6px">${{_escHtml(b.maturity)}}</span><div style="font-size:11px;color:#4A413D;margin-top:2px">${{_escHtml(b.application)}}</div><div class="sk-tools-row" style="margin-top:4px">${{(b.tool || []).map(t => `<span class="sk-tool">${{_escHtml(t)}}</span>`).join('')}}</div></div>`
    ).join('');
    const symHtml = (attrs.symbiosis || []).map(sy =>
      `<div style="padding:7px 9px;background:#F0FAF8;border:1px solid #A5DCD2;border-radius:9px;font-size:11.5px;margin-bottom:5px"><b>${{(sy.with || []).map(_escHtml).join(' ↔ ')}}</b><br>${{_escHtml(sy.shared_intention)}}</div>`
    ).join('');
    const ev = attrs.evaluation || {{}};
    const ar = attrs.archive || {{}};
    anatomyHtml = `
      <div class="sk-sec"><div class="sk-sec-lbl">Symbiosis &amp; Coordinated Resources</div>${{symHtml}}${{resHtml}}</div>
      <div class="sk-sec"><div class="sk-sec-lbl">Coordination Branches &amp; Tools</div>${{brHtml}}</div>
      <div class="sk-sec"><div class="sk-sec-lbl">Evaluation (${{_escHtml(ev.status)}}) &amp; Archive</div>
        <div style="font-size:11.5px;color:#4A413D;line-height:1.45">
          <b>Studies Needed:</b> ${{(ev.studies_needed || []).map(_escHtml).join(' · ')}}<br>
          <b>Lessons Learned:</b> ${{(ar.lessons_learned || []).map(_escHtml).join(' · ')}}
        </div>
      </div>`;
  }}

  body.innerHTML = `
    <div class="sk-sec"><div class="sk-sec-lbl">Definition</div><div style="font-size:12.5px;line-height:1.5;color:var(--nest-ink)">${{_escHtml(raw.definition)}}</div></div>
    <div class="sk-sec"><div class="sk-sec-lbl">Triggers &amp; Action (${{_escHtml(act.type || 'Guidance')}})</div>
      <ul style="margin:0 0 8px 16px;padding:0;font-size:11.5px;color:#4A413D">${{triggersHtml}}</ul>
      <div style="padding:8px 10px;background:${{ec.bg}};border:1px solid ${{ec.bd}};border-radius:8px;font-size:12px;color:#231E1C"><b>${{_escHtml(act.type || 'Action')}}:</b> ${{_escHtml(act.message)}}</div>
    </div>
    ${{anatomyHtml}}`;

  document.getElementById('sk-drawer-backdrop').classList.add('open');
}}

function closeSkillInspector() {{
  const bd = document.getElementById('sk-drawer-backdrop');
  if (bd) bd.classList.remove('open');
}}

function downloadSingleSkill(uid) {{
  const s = NEST_STAGE_C_SKILLS.find(x => x.uid === uid);
  if (!s) return;
  _triggerJsonDownload(s.filename || `${{uid}}.json`, s.raw || s);
}}

function exportFilteredSkillsPack() {{
  const list = _lastFilteredSkills.length ? _lastFilteredSkills : getFilteredSkills();
  const payload = {{
    plot: {json.dumps(plot_title)},
    count: list.length,
    skills: list.map(s => ({{ project_rank: s.project_rank, project_title: s.project_title, ...s.raw }}))
  }};
  _triggerJsonDownload('nest_stage_c_skills_pack.json', payload);
}}

renderProjectCards();
renderTab2EngineReasoning();
renderSkillsTab();
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
