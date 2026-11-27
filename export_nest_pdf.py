#!/usr/bin/env python3
"""
NEST Pure-Python Publication PDF Exporter (`export_nest_pdf.py`)
================================================================
Generates a clean, magazine-grade, browser-free PDF dossier directly from
`<run_dir>/stage_b_projects.json` using PyMuPDF (`fitz.Story`) + PIL.

Zero Chrome/Playwright/browser dependency. Runs 100% offline in ~2 seconds.

Usage:
  python export_nest_pdf.py --run-dir "Outputs/NEST-71-606" --plot-title "Red Sea Foothills / Gebel Shayeb El Banat — NEST-71-606"
"""
from __future__ import annotations

import argparse
import html
import io
import json
import re
from pathlib import Path
from typing import Any

import pymupdf as fitz  # PyMuPDF
from PIL import Image

ROOT = Path(__file__).resolve().parent

ENGINE_META: dict[str, dict[str, str]] = {
    "Crystals": {
        "theme": "Development",
        "defn": "Finding points of interest to build around, in, or at.",
        "fg": "#8C3325",
        "bg": "#FFF5F2",
        "bd": "#E8B5A8",
    },
    "Cells": {
        "theme": "Adaptation",
        "defn": "Finding elements in site, nature, or context to unlock their full potential by adapting them into something new or better.",
        "fg": "#1D4ED8",
        "bg": "#F2F7FF",
        "bd": "#B5CCF5",
    },
    "Corals": {
        "theme": "Coordination",
        "defn": "Finding elements in site, nature, or context to use better together or introduce a beneficial relationship.",
        "fg": "#0F766E",
        "bg": "#F0FAF8",
        "bd": "#A5DCD2",
    },
}


def _esc(val: Any) -> str:
    return html.escape(str(val or "").strip())


def _safe_slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", (name or "NEST_Plot").strip()).strip("_")[:60]


def _stage_image(src: Path, archive_dir: Path, key: str, max_w: int = 1200) -> str | None:
    """Copy/downscale an image into an in-memory/temp archive folder for fitz.Story."""
    if not src or not src.is_file():
        return None
    try:
        with Image.open(src) as im:
            im = im.convert("RGB")
            if im.width > max_w:
                h = max(1, int(round(im.height * (max_w / float(im.width)))))
                im = im.resize((max_w, h), Image.Resampling.LANCZOS)
            out_name = f"{key}.jpg"
            im.save(archive_dir / out_name, format="JPEG", quality=86, optimize=True)
            return out_name
    except Exception:
        return None


def _stage_logo(src: Path, archive_dir: Path, key: str, max_px: int = 240) -> str | None:
    if not src or not src.is_file():
        return None
    try:
        with Image.open(src) as im:
            im = im.convert("RGBA")
            im.thumbnail((max_px, max_px), Image.Resampling.LANCZOS)
            out_name = f"{key}.png"
            im.save(archive_dir / out_name, format="PNG", optimize=True)
            return out_name
    except Exception:
        return None


def build_pdf_html(
    run_dir: Path,
    projects: list[dict[str, Any]],
    plot_title: str,
    archive_dir: Path,
) -> tuple[str, str]:
    ui_logos = ROOT / "UI Handover" / "logos"
    nest_logo = _stage_logo(ui_logos / "nest-wordmark-black.png", archive_dir, "logo_nest", 280)
    delab_logo = _stage_logo(ui_logos / "delab-colour.png", archive_dir, "logo_delab", 240)
    eng_gfx_dir = ROOT / "NEST Engine Graphics"
    eng_icons = {
        "Crystals": _stage_logo(eng_gfx_dir / "Crystals.png", archive_dir, "icon_crystals", 96),
        "Cells": _stage_logo(eng_gfx_dir / "Cells.png", archive_dir, "icon_cells", 96),
        "Corals": _stage_logo(eng_gfx_dir / "Corals.png", archive_dir, "icon_corals", 96),
    }

    def _eicon(name: str, h: int = 16) -> str:
        fn = eng_icons.get(name)
        return f'<img src="{fn}" height="{h}" /> ' if fn else ""

    css = """
    body {
      font-family: sans-serif;
      font-size: 9pt;
      line-height: 1.42;
      color: #302B2A;
    }
    h1 { font-size: 18pt; color: #302B2A; margin: 4pt 0 2pt 0; }
    h2 { font-size: 13.5pt; color: #302B2A; margin: 0 0 3pt 0; }
    h3 {
      font-size: 9.5pt;
      text-transform: uppercase;
      letter-spacing: 0.4pt;
      color: #A3473A;
      border-bottom: 1pt solid #E6DAD6;
      padding-bottom: 2pt;
      margin: 10pt 0 5pt 0;
    }
    p { margin: 0 0 5pt 0; }
    .cover-bar {
      border-top: 3pt solid #DDA199;
      border-bottom: 1pt solid #D5C9C5;
      padding: 8pt 0 8pt 0;
      margin-bottom: 10pt;
    }
    .subtitle { font-size: 9.5pt; color: #625753; margin-bottom: 6pt; }
    .muted { color: #625753; font-size: 8.2pt; }
    .pill {
      display: inline-block;
      padding: 2pt 6pt;
      border-radius: 3pt;
      font-size: 7.8pt;
      font-weight: bold;
      border: 0.6pt solid #D5C9C5;
      background-color: #FFFAF7;
      color: #302B2A;
      margin-right: 4pt;
    }
    .kpi-table { width: 100%; border-collapse: collapse; margin: 6pt 0 8pt 0; }
    .kpi-table td {
      border: 0.6pt solid #D5C9C5;
      background-color: #FFFAF7;
      padding: 5pt 7pt;
      vertical-align: top;
    }
    .kpi-k { font-size: 7pt; text-transform: uppercase; color: #625753; font-weight: bold; }
    .kpi-v { font-size: 11pt; font-weight: bold; color: #302B2A; margin-top: 1pt; }
    table.data { width: 100%; border-collapse: collapse; margin: 4pt 0 8pt 0; font-size: 8pt; }
    table.data th {
      background-color: #302B2A;
      color: #FFFAF7;
      text-align: left;
      padding: 4pt 5pt;
      font-weight: bold;
      border: 0.5pt solid #302B2A;
    }
    table.data td {
      padding: 3.5pt 5pt;
      border: 0.5pt solid #DFD5D1;
      vertical-align: top;
    }
    table.data tr.alt td { background-color: #FAF7F5; }
    table.data tr.tare td { background-color: #FFF5E5; color: #775014; }
    .num { text-align: right; white-space: nowrap; }
    .box {
      border: 0.8pt solid #D5C9C5;
      background-color: #FFFAF7;
      padding: 7pt 9pt;
      margin: 6pt 0 8pt 0;
    }
    .hook {
      border-left: 3pt solid #FF614C;
      background-color: #FBEFED;
      padding: 6pt 9pt;
      font-size: 9.5pt;
      font-weight: bold;
      color: #302B2A;
      margin: 6pt 0 8pt 0;
    }
    .page-break { page-break-before: always; }
    .img-plate { width: 100%; margin: 5pt 0 8pt 0; border-collapse: collapse; }
    .img-plate td { padding: 0 3pt 0 0; vertical-align: top; }
    .img-cap { font-size: 7.5pt; color: #625753; margin-top: 2pt; }
    ul { margin: 2pt 0 6pt 14pt; padding: 0; }
    li { margin-bottom: 3pt; }
    """

    # --- COVER & PORTFOLIO OVERVIEW ---
    logo_cells = []
    if nest_logo:
        logo_cells.append(f'<img src="{nest_logo}" height="20" />')
    if delab_logo:
        logo_cells.append(f'<img src="{delab_logo}" height="17" />')
    logo_bar = (
        f'<table style="width:100%;border-collapse:collapse;margin-bottom:4pt"><tr>'
        f'<td style="text-align:left">{" &nbsp;&nbsp; ".join(logo_cells)}</td>'
        f'<td style="text-align:right;font-size:8pt;color:#625753"><b>NEST Micro Workflow · Executive Proposals Dossier</b></td>'
        f'</tr></table>'
    )

    eng_cards = []
    for eng in ("Crystals", "Cells", "Corals"):
        em = ENGINE_META[eng]
        cnt = sum(1 for p in projects if (p.get("engine") or "Crystals") == eng)
        eng_cards.append(
            f'<td style="width:33.3%;border:0.8pt solid {em["bd"]};background-color:{em["bg"]};padding:6pt 7pt;vertical-align:top">'
            f'<div style="font-size:8.5pt;font-weight:bold;color:{em["fg"]}">{_eicon(eng, 16)}{eng} Engine ({em["theme"]}) · {cnt} Project(s)</div>'
            f'<div style="font-size:7.6pt;color:#4A413D;margin-top:2pt">{_esc(em["defn"])}</div>'
            f'</td>'
        )
    eng_strip = f'<table style="width:100%;border-collapse:collapse;margin:6pt 0 10pt 0"><tr>{"".join(eng_cards)}</tr></table>'

    port_rows = []
    for idx, p in enumerate(projects):
        fin = p.get("fin") or {}
        eng = p.get("engine") or "Crystals"
        em = ENGINE_META.get(eng, ENGINE_META["Crystals"])
        vols = (p.get("massing_rationale") or {}).get("volumes") or []
        gfa_num = int(re.sub(r"[^\d]", "", str(p.get("built_gfa", "0"))) or 0)
        far_pct = (gfa_num / max(float(p.get("area_m2", 1)), 1.0)) * 100.0
        cls = ' class="alt"' if idx % 2 == 1 else ""
        port_rows.append(
            f'<tr{cls}>'
            f'<td class="num"><b>#{p.get("rank", idx + 1)}</b></td>'
            f'<td style="color:{em["fg"]};font-weight:bold">{_esc(eng)}<br><span class="muted">{_esc(em["theme"])}</span></td>'
            f'<td><b>{_esc(p.get("title"))}</b><br><span class="muted">{_esc(p.get("subtitle"))}</span></td>'
            f'<td>{_esc(p.get("idiom"))}<br><span class="muted">{_esc(p.get("concept_register"))}</span></td>'
            f'<td class="num">{_esc(p.get("area_feddans"))}</td>'
            f'<td class="num">{_esc(p.get("built_gfa"))}<br><span class="muted">{far_pct:.1f}% FAR · {len(vols)} bldgs</span></td>'
            f'<td class="num">{_esc(fin.get("capex", "—"))}</td>'
            f'<td class="num"><b>{_esc(fin.get("irr", "—"))}</b><br><span class="muted">{_esc(fin.get("payback", "—"))}</span></td>'
            f'</tr>'
        )

    cover_html = "<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>" + "\n".join([
        f'<div class="cover-bar">{logo_bar}<h1>{_esc(plot_title)}</h1>'
        f'<div class="subtitle">Independent 3-Engine Architectural Proposals · Reconciled Space Programs · Cited Egyptian Codes (RAG) · Stage C Design Skills</div></div>',
        eng_strip,
        '<h3>Portfolio Overview</h3>',
        '<table class="data"><thead><tr>'
        '<th>#</th><th>Engine</th><th>Project</th><th>Idiom &amp; Register</th>'
        '<th class="num">Fed.</th><th class="num">Built GFA</th><th class="num">CapEx</th><th class="num">IRR / Payback</th>'
        '</tr></thead><tbody>' + "".join(port_rows) + '</tbody></table>',
    ]) + "</body></html>"
    sections: list[str] = [cover_html]

    # --- PER-PROJECT DOSSIERS ---
    for p in projects:
        rk = p.get("rank", 1)
        eng = p.get("engine") or "Crystals"
        em = ENGINE_META.get(eng, ENGINE_META["Crystals"])
        fin = p.get("fin") or {}
        ts = p.get("thesis_summary") or {}
        er = p.get("engine_reasoning") or {}
        mr = p.get("massing_rationale") or {}
        vols = mr.get("volumes") or []
        zones = p.get("landscape_zones") or []
        rag = p.get("rag_citations") or {}
        skills = p.get("generated_skills") or []
        cs_list = p.get("commercial_screening") or []

        # Visuals: prefer aerial + hero renders if present; else satellite lock
        aerial_src = run_dir / "renders" / f"site_{rk}.jpg"
        hero_src = run_dir / "renders" / f"site_{rk}_hero.jpg"
        sat_src = run_dir / "renders" / "render_pack" / f"site_{rk}" / "satellite_lock.png"
        aerial_img = _stage_image(aerial_src, archive_dir, f"site_{rk}_aerial", max_w=1100)
        hero_img = _stage_image(hero_src, archive_dir, f"site_{rk}_hero", max_w=1100)
        sat_img = _stage_image(sat_src, archive_dir, f"site_{rk}_sat", max_w=1100)

        img_html = ""
        if aerial_img and hero_img:
            img_html = (
                f'<table class="img-plate"><tr>'
                f'<td style="width:50%"><img src="{aerial_img}" width="240" height="135" /><div class="img-cap">Whole-Site Scale Aerial</div></td>'
                f'<td style="width:50%"><img src="{hero_img}" width="240" height="135" /><div class="img-cap">Close Hero Experience</div></td>'
                f'</tr></table>'
            )
        elif aerial_img and sat_img:
            img_html = (
                f'<table class="img-plate"><tr>'
                f'<td style="width:50%"><img src="{aerial_img}" width="240" height="135" /><div class="img-cap">Whole-Site Scale Aerial</div></td>'
                f'<td style="width:50%"><img src="{sat_img}" width="240" height="135" /><div class="img-cap">Esri Satellite Site Lock</div></td>'
                f'</tr></table>'
            )
        elif sat_img:
            img_html = (
                f'<div style="margin:5pt 0 8pt 0">'
                f'<img src="{sat_img}" width="480" height="270" />'
                f'<div class="img-cap">Esri Satellite Site Lock — Red Dashed Boundary (Top = North)</div>'
                f'</div>'
            )

        # Engine reasoning box
        er_html = ""
        if er.get("lead") or er.get("peers"):
            peer_items = []
            for pk, pv in (er.get("peers") or {}).items():
                if not pv:
                    continue
                pn = pk.strip().title()
                pm = ENGINE_META.get(pn, {"fg": "#625753", "theme": ""})
                peer_items.append(
                    f'<div style="font-size:8pt;margin-top:3pt;color:#4A413D">'
                    f'<b style="color:{pm["fg"]}">{_esc(pn)} ({_esc(pm["theme"])}) Peer:</b> {_esc(pv)}</div>'
                )
            er_html = (
                f'<div style="border:0.9pt solid {em["bd"]};background-color:{em["bg"]};padding:7pt 9pt;margin:6pt 0 8pt 0">'
                f'<div style="font-size:8.2pt;font-weight:bold;color:{em["fg"]};text-transform:uppercase">'
                f'{_eicon(eng, 15)}{_esc(eng)} Engine ({_esc(em["theme"])}) · Why I Chose This Site</div>'
                f'<div style="font-size:7.4pt;color:{em["fg"]};margin-bottom:3pt"><i>Engine Definition: {_esc(em["defn"])}</i></div>'
                f'<div style="font-size:8.5pt;color:#231E1C">{_esc(er.get("lead"))}</div>'
                f'{"".join(peer_items)}'
                f'</div>'
            )

        # Space program table (room-by-room)
        sp_rows = []
        for v in vols:
            v_gfa = v.get("area_m2", "")
            v_nsf = v.get("nsf_m2")
            v_tare = v.get("tare_m2")
            eff = f" ({v.get('nsf_gsf_pct')}% NSF/GSF)" if v.get("nsf_gsf_pct") is not None and v_tare else ""
            sp_rows.append(
                f'<tr style="background-color:#F2ECE9"><td colspan="2"><b>{_esc(v.get("name"))}</b> '
                f'<span class="muted">— {_esc(v.get("use"))} · {_esc(v.get("height_floors"))}</span></td>'
                f'<td class="num"><b>{_esc(v_gfa)} GSF{_esc(eff)}</b></td></tr>'
            )
            for z in v.get("interior_zones") or []:
                is_t = bool(re.search(r"tare|circulation|boh|mep|service|core", str(z.get("role", "")), re.I))
                rcls = ' class="tare"' if is_t else ""
                sp_rows.append(
                    f'<tr{rcls}><td>{_esc(z.get("name"))}</td>'
                    f'<td class="muted">{_esc(z.get("role"))}</td>'
                    f'<td class="num">{int(z.get("area_m2") or 0):,} m²</td></tr>'
                )
        sp_html = (
            '<table class="data"><thead><tr><th>Building / Room</th><th>Role</th><th class="num">Area</th></tr></thead>'
            '<tbody>' + "".join(sp_rows) + '</tbody></table>'
            if sp_rows
            else ""
        )

        # Landscape zones table + rendered organic GIS zoning map plate
        from landscape_zoning import render_zone_map_png
        zmap_path = archive_dir / f"site_{rk}_zmap.png"
        zmap_ok = render_zone_map_png(p, zmap_path)
        zmap_html = (
            f'<div style="margin:4pt 0 6pt 0"><img src="{zmap_path.name}" width="460" /></div>'
            if zmap_ok and zmap_path.is_file()
            else ""
        )
        b_env = p.get("buildable_envelope") or {}
        env_html = (
            f'<div class="box" style="font-size:8pt">'
            f'<b>Verified Development Interface (Buildable Envelope):</b> {int(b_env.get("net_buildable_m2", 0)):,} m² net buildable '
            f'vs. {int(b_env.get("building_footprint_m2", 0)):,} m² building footprint ({b_env.get("envelope_coverage_pct", 0)}% coverage) · '
            f'<b>{b_env.get("preserve_locked_pct", 0)}%</b> locked 0% buildable (Preserve + Minimal Intervention).'
            + (f'<div style="margin-top:3pt"><b>Why This Site Is Zoned This Way:</b> {_esc(b_env.get("zoning_rationale"))}</div>' if b_env.get("zoning_rationale") else "")
            + (f'<div class="muted" style="margin-top:2pt"><b>GIS Priority Order:</b> {_esc(b_env.get("method_summary"))}</div>' if b_env.get("method_summary") else "")
            + '</div>'
            if b_env
            else ""
        )
        lz_rows = []
        for idx_z, z in enumerate(zones):
            cls = ' class="alt"' if idx_z % 2 == 1 else ""
            meta_str = " · ".join(
                bit for bit in [
                    f"Access: {z.get('access_level')}" if z.get("access_level") else "",
                    f"Water: {z.get('water_demand')}" if z.get("water_demand") else "",
                    str(z.get("confidence") or ""),
                ]
                if bit
            )
            lz_rows.append(
                f'<tr{cls}><td><b>{_esc(z.get("id"))} {_esc(z.get("name"))}</b><br><span class="muted">{_esc(meta_str)}</span></td>'
                f'<td><b>{_esc(z.get("intervention"))}</b><br><span class="muted">{"0% Buildable" if z.get("buildable") is False else "Interface"}</span></td>'
                f'<td class="num">{_esc(z.get("share_pct"))}%<br><span class="muted">{_esc(z.get("area_feddans"))} fed.</span></td>'
                f'<td>{_esc(z.get("gis_evidence") or z.get("why_here"))}<br><span class="muted">{_esc(z.get("outdoor_activities"))}</span></td></tr>'
            )
        lz_html = (
            zmap_html
            + env_html
            + (
                '<table class="data"><thead><tr><th>Landscape Zone &amp; Controls</th><th>Tier</th><th class="num">Share</th><th>GIS Evidence &amp; Uses</th></tr></thead>'
                '<tbody>' + "".join(lz_rows) + '</tbody></table>'
                if lz_rows
                else ""
            )
        )

        # Commercial screening
        cs_html = ""
        if cs_list:
            cs_items = "".join(
                f'<li><b>{_esc(cs.get("question"))}</b> {_esc(cs.get("answer"))}</li>' for cs in cs_list
            )
            cs_html = f'<h3>Commercial Viability Screening (Unvalidated Hypotheses)</h3><ul>{cs_items}</ul>'

        # RAG citations
        rag_html = ""
        rag_codes = rag.get("codes") or []
        rag_precs = rag.get("precedents") or []
        if rag_codes or rag_precs:
            r_items = []
            for c in rag_codes:
                ocr = " [OCR — verify]" if c.get("extraction") != "text" else ""
                r_items.append(
                    f'<li><b>[Egyptian Code] {_esc(c.get("doc_name"))}</b> (p. {_esc(c.get("page"))}{ocr}): {_esc(c.get("excerpt"))}</li>'
                )
            for r in rag_precs:
                r_items.append(
                    f'<li><b>[Precedent] {_esc(r.get("doc_name"))}</b> (p. {_esc(r.get("page"))}): {_esc(r.get("excerpt"))}</li>'
                )
            rag_html = f'<h3>Cited Egyptian Codes &amp; Architectural Precedents (RAG Reference)</h3><ul>{"".join(r_items)}</ul>'

        # Stage C skills
        skills_html = ""
        if skills:
            sk_rows = []
            for idx_s, sk in enumerate(skills):
                cls = ' class="alt"' if idx_s % 2 == 1 else ""
                sk_rows.append(
                    f'<tr{cls}><td><b>{_esc(sk.get("engine"))}</b><br><span class="muted">{_esc(sk.get("role"))}</span></td>'
                    f'<td><b>{_esc(sk.get("name") or sk.get("skill_id"))}</b></td>'
                    f'<td>{_esc(sk.get("summary") or sk.get("description"))}</td></tr>'
                )
            skills_html = (
                f'<h3>Stage C Generated Design Skills ({len(skills)})</h3>'
                '<table class="data"><thead><tr><th>Engine</th><th>Skill</th><th>Site-Grounded Action</th></tr></thead>'
                '<tbody>' + "".join(sk_rows) + '</tbody></table>'
            )

        sections.append(
            "<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>"
            f'<div style="border-top:2.5pt solid {em["fg"]};padding-top:6pt;margin-bottom:4pt">'
            f'<span class="pill" style="background-color:{em["fg"]};color:#FFFAF7;border-color:{em["fg"]}">{_esc(eng.upper())} ENGINE · {_esc(em["theme"].upper())}</span>'
            f'<span class="pill">PROJECT #{rk}</span>'
            f'<span class="pill">{_esc(p.get("area_feddans"))} FEDDANS</span>'
            f'<span class="pill">{_esc(p.get("built_gfa"))}</span>'
            f'<span class="pill">{_esc(p.get("idiom"))} · {_esc(p.get("concept_register"))}</span>'
            f'</div>'
            f'<h2>Site #{rk}: {_esc(p.get("title"))}</h2>'
            f'<div class="subtitle">{_esc(p.get("subtitle"))} · Coordinates: ({float(p.get("lat", 0)):.5f}, {float(p.get("lon", 0)):.5f})</div>'
            f'{img_html}'
            f'{er_html}'
            f'<div class="hook">{_esc(ts.get("hook"))}</div>'
            f'<p><b>Why Here:</b> {_esc(ts.get("why_here"))}</p>'
            f'<p>{_esc(p.get("thesis_detailed"))}</p>'
            f'<p><b>Orientation &amp; Massing:</b> {_esc(mr.get("orientation"))} {_esc(mr.get("shape_logic"))}</p>'
            f'<h3>Space Program ({_esc(p.get("built_gfa"))} across {len(vols)} Buildings)</h3>'
            f'{sp_html}'
            f'<h3>Two-Way Nature Loop &amp; Landscape ({_esc(p.get("area_feddans"))} Feddans)</h3>'
            f'<div class="box">'
            f'<p><b>Nature → Building:</b> {_esc(p.get("nature_to_bldg"))}</p>'
            f'<p style="margin-bottom:0"><b>Building → Nature:</b> {_esc(p.get("bldg_to_nature"))}</p>'
            f'</div>'
            f'{lz_html}'
            f'<h3>Investment &amp; Feasibility</h3>'
            f'<table class="kpi-table"><tr>'
            f'<td><div class="kpi-k">Total CapEx</div><div class="kpi-v">{_esc(fin.get("capex", "—"))}</div></td>'
            f'<td><div class="kpi-k">Annual Revenue</div><div class="kpi-v">{_esc(fin.get("rev", "—"))}</div></td>'
            f'<td><div class="kpi-k">Projected IRR</div><div class="kpi-v" style="color:#A3473A">{_esc(fin.get("irr", "—"))}</div></td>'
            f'<td><div class="kpi-k">Payback</div><div class="kpi-v">{_esc(fin.get("payback", "—"))}</div></td>'
            f'</tr></table>'
            f'{cs_html}'
            f'{rag_html}'
            f'{skills_html}'
            "</body></html>"
        )

    return sections, css


def export_pdf(run_dir: Path, plot_title: str, out_pdf: Path | None = None) -> Path:
    pjson = run_dir / "stage_b_projects.json"
    if not pjson.is_file():
        raise FileNotFoundError(f"Missing {pjson}")
    projects = json.loads(pjson.read_text(encoding="utf-8"))
    pdf_path = out_pdf or (run_dir / f"NEST_Proposals_{_safe_slug(run_dir.name)}.pdf")

    import tempfile

    with tempfile.TemporaryDirectory(prefix="nest_pdf_", ignore_cleanup_errors=True) as td:
        arch_dir = Path(td)
        sections, css_str = build_pdf_html(run_dir, projects, plot_title, arch_dir)
        archive = fitz.Archive(str(arch_dir))

        mediabox = fitz.paper_rect("a4")
        where = fitz.Rect(34, 44, mediabox.width - 34, mediabox.height - 40)

        tmp_pdf = arch_dir / "raw.pdf"
        writer = fitz.DocumentWriter(str(tmp_pdf))
        try:
            for sec_html in sections:
                story = fitz.Story(html=sec_html, user_css=css_str, archive=archive)
                more = 1
                sec_pages = 0
                while more and sec_pages < 12:
                    sec_pages += 1
                    dev = writer.begin_page(mediabox)
                    more, filled = story.place(where)
                    story.draw(dev)
                    writer.end_page()
                    if filled and (filled[2] - filled[0] <= 0.5 or filled[3] - filled[1] <= 0.5):
                        break
        finally:
            writer.close()
            del writer

        # Stamp crisp running header + footer with page numbers
        doc = fitz.open(str(tmp_pdf))
        total_pages = len(doc)
        for i, page in enumerate(doc):
            w, h = page.rect.width, page.rect.height
            # Top hairline + header (skip on cover page 0)
            if i > 0:
                page.draw_line(fitz.Point(34, 28), fitz.Point(w - 34, 28), color=(0.87, 0.63, 0.60), width=1.2)
                page.insert_text(
                    fitz.Point(34, 23),
                    f"NEST Micro Workflow  |  {plot_title}",
                    fontsize=7.5,
                    color=(0.38, 0.34, 0.33),
                )
            # Bottom footer
            page.draw_line(fitz.Point(34, h - 28), fitz.Point(w - 34, h - 28), color=(0.84, 0.79, 0.77), width=0.6)
            page.insert_text(
                fitz.Point(34, h - 16),
                "NEST · DeLab | Nature-First 3-Engine Architectural Dossier",
                fontsize=7.5,
                color=(0.38, 0.34, 0.33),
            )
            pg_lbl = f"Page {i + 1} of {total_pages}"
            page.insert_text(
                fitz.Point(w - 34 - len(pg_lbl) * 4.2, h - 16),
                pg_lbl,
                fontsize=7.5,
                color=(0.38, 0.34, 0.33),
            )
        doc.save(str(pdf_path), garbage=4, deflate=True)
        doc.close()

    print(f"[PDF Export] Built browser-free dossier -> {pdf_path} ({total_pages} pages, {pdf_path.stat().st_size:,} bytes)")
    return pdf_path


def main() -> None:
    ap = argparse.ArgumentParser(description="NEST Pure-Python Browser-Free PDF Exporter")
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--plot-title", type=str, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    title = args.plot_title or args.run_dir.name
    export_pdf(args.run_dir, title, args.out)


if __name__ == "__main__":
    main()
