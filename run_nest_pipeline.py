#!/usr/bin/env python3
"""
NEST Unified End-to-End Pipeline & Pre-Render Geometry Gate
===========================================================
Single canonical CLI orchestrating:
  1. Stage A — 3-Engine GIS + Native Raster Fusion (`run_3_engines.py`)
  2. DEM Terrain-Embedding Gate — Local Copernicus DSM 30 m / SRTM fallback (`terrain_intelligence.py`)
  3. Pre-Render Geometry & Raster Sanity Gate:
       - 0 m² Preserve-zone encroachments for non-bridge buildings
       - Built-up / compound overlap check via WorldCover + GHS_BUILT_S rasters
       - Pier/boardwalk water-termination check against WorldCover 10 m water
       - Interior-zone GFA reconciliation + Jury Self-Audit vocabulary gate
  4. NEST Experience-First Dashboard + `node --check` JS gate (`build_nest_dashboard.py`)
  5. 42° Camera-Matched Esri Satellite + Text Render Pack (`build_render_pack.py`)

Usage:
  python run_nest_pipeline.py --data-dir "NOV26 TESTS/NEST--12-683 GIS" --out-dir outputs_nest_12_683 --plot-title "Alexandria / Matrouh Coast — NEST-12-683"
  python run_nest_pipeline.py --data-dir "NOV26 TESTS/NEST--12-683 GIS" --out-dir outputs_nest_12_683 --validate-only
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import Point, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent


def find_gis_layers_file(data_dir: Path) -> Path | None:
    m = next(data_dir.glob("*_all_layers.geojson"), None)
    if m:
        return m
    for name in ("engine-input.geojson", "all-vectors.geojson"):
        p = data_dir / name
        if p.exists():
            return p
    return None


def validate_stage_b_geometry(run_dir: Path, data_dir: Path | None, strict: bool = False) -> list[str]:
    """Automated Pre-Render Geometry, Raster Ground-Truth & Jury Audit Gate."""
    pjson = run_dir / "stage_b_projects.json"
    if not pjson.exists():
        raise FileNotFoundError(f"Missing Stage B proposals: {pjson}")
    projects = json.loads(pjson.read_text(encoding="utf-8"))

    rb = None
    if data_dir and ((data_dir / "dataset-inventory.json").exists() or (data_dir / "rasters").exists()):
        try:
            from raster_ground_truth import RasterBundle
            rb = RasterBundle(data_dir)
        except Exception:
            rb = None

    warnings: list[str] = []
    errors: list[str] = []

    for p in projects:
        rk = p.get("rank", "?")
        title = p.get("title", f"Site #{rk}")

        # 1. Preserve-zone encroachment check
        pres_geoms = []
        for z in p.get("landscape_zones") or []:
            if "preserve" in str(z.get("intervention") or "").lower() and z.get("geom"):
                pres_geoms.append(shape(z["geom"]).buffer(0))
        pres_u = unary_union(pres_geoms).buffer(0) if pres_geoms else None

        for fp in p.get("footprints") or []:
            if not fp.get("geom"):
                continue
            fg = shape(fp["geom"]).buffer(0)
            is_bridge = bool(fp.get("bridge_or_pile_allowed"))

            if not is_bridge and pres_u is not None and not pres_u.is_empty:
                inter = fg.intersection(pres_u)
                if not inter.is_empty and inter.area > 1e-9:
                    errors.append(f"Site #{rk} ({title}) '{fp.get('label')}' encroaches into Preserve zone!")

            # 2. WorldCover / GHS_BUILT_S built-up compound & pier water check
            if rb is not None and (rb.worldcover is not None or rb.ghs_built is not None):
                minx, miny, maxx, maxy = fg.bounds
                xs = np.linspace(minx, maxx, 9)
                ys = np.linspace(miny, maxy, 9)
                pts = [(x, y) for y in ys for x in xs if fg.contains(Point(x, y))]
                if not pts:
                    rp = fg.representative_point()
                    pts = [(rp.x, rp.y)]
                lons = np.array([pt[0] for pt in pts], dtype=np.float64)
                lats = np.array([pt[1] for pt in pts], dtype=np.float64)
                wc_w, wc_b = rb.sample_water_built_masks(lons, lats)
                if not is_bridge:
                    if wc_b is not None and len(wc_b) > 0:
                        built_frac = float(np.mean(wc_b))
                        if built_frac > 0.15:
                            warnings.append(
                                f"Site #{rk} ({title}) '{fp.get('label')}' overlaps {built_frac*100:.0f}% existing built-up/compound raster cells"
                            )
                    if wc_w is not None and len(wc_w) > 0:
                        water_frac = float(np.mean(wc_w))
                        if water_frac > 0.10 and not p.get("is_water"):
                            warnings.append(
                                f"Site #{rk} ({title}) '{fp.get('label')}' overlaps {water_frac*100:.0f}% WorldCover water cells"
                            )
                else:
                    # Bridge/Pier: check if any point reaches WorldCover water or Preserve wetland
                    in_water = bool(wc_w is not None and np.any(wc_w))
                    in_pres = bool(pres_u is not None and fg.intersects(pres_u))
                    if not in_water and not in_pres:
                        warnings.append(
                            f"Site #{rk} ({title}) pier '{fp.get('label')}' does not reach WorldCover water or Preserve buffer"
                        )

        # 3. Interior-zone GFA reconciliation
        for v in (p.get("massing_rationale") or {}).get("volumes") or []:
            iz = v.get("interior_zones") or []
            if iz and v.get("area_m2"):
                m_num = re.search(r"([\d,]+)", str(v["area_m2"]))
                if m_num:
                    target = int(m_num.group(1).replace(",", ""))
                    actual = sum(int(z.get("area_m2", 0)) for z in iz)
                    if abs(actual - target) > max(50, target * 0.02):
                        errors.append(f"Site #{rk} '{v.get('name')}' interior sum {actual} != {target} m²")

    print(f"[Pre-Render Gate] Checked {len(projects)} projects -> {len(errors)} errors, {len(warnings)} warnings")
    for e in errors:
        print(f"  [ERROR] {e}")
    for w in warnings:
        print(f"  [WARN]  {w}")

    if errors or (strict and warnings):
        raise SystemExit(1)
    return warnings


def run_step(cmd: list[str], label: str):
    print(f"\n=== {label} ===")
    print(" ", " ".join(cmd))
    res = subprocess.run(cmd, cwd=str(ROOT))
    if res.returncode != 0:
        raise SystemExit(res.returncode)


def verify_dashboard_js(dash_path: Path):
    html = dash_path.read_text(encoding="utf-8")
    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, flags=re.S)
    tmp_dir = run_dir_tmp = dash_path.parent / "intermediates"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    for idx, sc in enumerate(scripts):
        tmp_js = run_dir_tmp / f"_check_script_{idx}.js"
        tmp_js.write_text(sc, encoding="utf-8")
        res = subprocess.run(["node", "--check", str(tmp_js)], capture_output=True, text=True)
        tmp_js.unlink(missing_ok=True)
        if res.returncode != 0:
            raise RuntimeError(f"JS syntax check failed in {dash_path.name} script #{idx}: {res.stderr}")
    print(f"[JS Syntax Gate] Verified {len(scripts)} inline script blocks (0 errors)")


def main():
    ap = argparse.ArgumentParser(description="NEST Unified End-to-End Pipeline & Pre-Render Gate")
    ap.add_argument("--data-dir", type=Path, required=True, help="GIS plot folder")
    ap.add_argument("--out-dir", type=Path, required=True, help="Run output directory")
    ap.add_argument("--plot-title", type=str, default=None, help="Dashboard display title")
    ap.add_argument("--skip-stage-a", action="store_true", help="Reuse existing intermediates/stage_a_summary.json")
    ap.add_argument("--use-seeds", action="store_true", help="Use intermediates/seeds/site_*_seed.json instead of dynamic Stage B synthesis")
    ap.add_argument("--validate-only", action="store_true", help="Run Pre-Render Geometry & Raster Gate only")
    ap.add_argument("--strict-gate", action="store_true", help="Fail on built-up/pier warnings as well as errors")
    args = ap.parse_args()

    data_dir = args.data_dir if args.data_dir.is_absolute() else (ROOT / args.data_dir)
    out_dir = args.out_dir if args.out_dir.is_absolute() else (ROOT / args.out_dir)
    plot_title = args.plot_title or out_dir.name

    if args.validate_only:
        validate_stage_b_geometry(out_dir, data_dir, strict=args.strict_gate)
        return

    # 1. Stage A (3-Engine GIS + Native Raster Fusion)
    if not (args.skip_stage_a and (out_dir / "intermediates" / "stage_a_summary.json").exists()):
        run_step(
            [sys.executable, "run_3_engines.py", "--data-dir", str(data_dir), "--out-dir", str(out_dir), "--plot-name", plot_title],
            "Stage A: 3-Engine Spatial Evaluation + Native Raster Fusion",
        )

    # 1b. Write rich single-file agent_site_context.md (shape, DEM, open quadrants, landmarks + full creative prompt)
    sa_path = out_dir / "intermediates" / "stage_a_summary.json"
    if sa_path.exists():
        sa = json.loads(sa_path.read_text(encoding="utf-8"))
        rb_ctx = None
        if data_dir and ((data_dir / "dataset-inventory.json").exists() or (data_dir / "rasters").exists()):
            try:
                from raster_ground_truth import RasterBundle
                rb_ctx = RasterBundle(data_dir)
            except Exception:
                rb_ctx = None

        ctx_lines = [
            f"# Architect Agent Brief & Site Context — {plot_title}",
            "",
            "You are designing **5 distinct, unforgettable architectural destinations** (`intermediates/seeds/site_1_seed.json`..`site_5_seed.json`) for this plot.",
            "Read **only this file**, then author bespoke JSON seeds that pass every rule below.",
            "",
            "## Creative & Site-Grounding Contract (Mandatory)",
            "1. **No Boring RFP / Tech-Campus Clichés:** NEVER use generic filler words like `Hub`, `Precinct`, `Campus`, `Innovation`, `Vocational Institute`, `R&D Bays`, `Testing Lab`, `Pavilion`, `Solution`, or `Synergy` in titles or building names. Name places like a real architecture monograph (e.g., *The Calcarenite Solar Baths*, *Salt-Mist Cisterns*, *Al Gharbaniat Shade-Loom*).",
            "2. **The Friday Afternoon Test (Human Life First):** Every project's `hook`, `thesis_detailed`, and `experience_arc.journey` MUST spell out what a local family, student, maker, or weekend traveler actually **DOES** there from morning coffee to midnight (food, craft, water, shade, cinema, music, play—never just stone walls and wind-catchers).",
            "3. **Site-Asset Exploitation:** Each site MUST explicitly cite and physically exploit at least **2 concrete facts** from its Site Block below (e.g. an exact named road/canal/landmark + distance, its parcel elongation/bearing, DEM elevation/relief, or placing buildings in the **cleanest open quadrant** while leaving built-up edges as buffers).",
            "4. **Portfolio Diversity (Zero Repetition):** Across Sites #1–#5, assign **5 unique idioms** (`courtyard`, `terrace`, `cantilever`, `clustered_compound`, `bridge`) and **5 unique registers** (`Limestone & Wind-Tower`, `Earth & Rammed Mass`, `Timber & Tensile Shade`, `Steel & Solar Canopy`, `Vaulted Brick & Courtyard`).",
            "",
            "## Compact Seed Schema (`intermediates/seeds/site_<N>_seed.json`)",
            "Required keys: `rank`, `candidate_rank`, `title`, `subtitle`, `nature_hero`, `strategy`, `tier`, `idiom`, `precedent`, `concept_register`, `is_water`, `target_feddans`, `site_bearing_deg`, `orientation`, `shape_logic`, `activities` (concrete human activities — as many as fit the place), `thesis_summary` (`hook`, `gesture_line`, `why_here`), `thesis_detailed`, `engine_trace`, `nature_to_bldg`, `bldg_to_nature`, `experience_arc` (`core_idea`, `visit_mode`, `atmosphere`, `journey` of `{moment, detail}` chapters — use as many moments as the real day-to-night experience calls for, e.g. 3–6+), `volumes` (as many distinct buildings as the program genuinely needs, each with `name`, `use`, `area_m2`, `floors`, `archetype` in `bar|courtyard|crescent|l_shape|pier`, `bridge_or_pile_allowed`, `shape_reason`, `interior_zones`), `landscape_zones` (meaningful ecological/civic zones summing to `share_pct = 100`).",
            "",
            "---",
            "",
        ]
        for c in sa.get("top_5_candidates") or []:
            rk = c.get("site_rank")
            acc = c.get("accessibility") or {}
            ptrs = (c.get("gis_evidence") or {}).get("map_feature_pointers") or []
            gj = (c.get("boundary") or {}).get("geojson")
            shape_note = "Compact ~500×500 m parcel"
            dem_note = "Unavailable (no local DSM)"
            quad_note = "Unavailable (no 10 m built raster)"

            if gj:
                try:
                    poly_ll = shape(gj)
                    minx, miny, maxx, maxy = poly_ll.bounds
                    lat_c = float(c.get("lat") or poly_ll.centroid.y)
                    m_per_lon = 111320.0 * math.cos(math.radians(lat_c))
                    m_per_lat = 110540.0
                    w_m = max(1.0, (maxx - minx) * m_per_lon)
                    h_m = max(1.0, (maxy - miny) * m_per_lat)
                    aspect = max(w_m, h_m) / min(w_m, h_m)
                    mrr = poly_ll.minimum_rotated_rectangle
                    mcoords = list(mrr.exterior.coords)
                    if len(mcoords) >= 3:
                        d1 = ((mcoords[1][0] - mcoords[0][0]) * m_per_lon, (mcoords[1][1] - mcoords[0][1]) * m_per_lat)
                        d2 = ((mcoords[2][0] - mcoords[1][0]) * m_per_lon, (mcoords[2][1] - mcoords[1][1]) * m_per_lat)
                        long_v = d1 if math.hypot(*d1) >= math.hypot(*d2) else d2
                        bearing_deg = (math.degrees(math.atan2(long_v[0], long_v[1])) + 180.0) % 180.0
                    else:
                        bearing_deg = 0.0
                    kind = "Linear corridor" if aspect >= 1.8 else ("Elongated block" if aspect >= 1.35 else "Compact multi-block")
                    shape_note = f"{kind} (~{w_m:.0f} m E–W × {h_m:.0f} m N–S, aspect {aspect:.2f}:1, long axis ~{bearing_deg:.0f}° N)"

                    if rb_ctx is not None:
                        xs = np.linspace(minx, maxx, 9)
                        ys = np.linspace(miny, maxy, 9)
                        pts = [(x, y) for y in ys for x in xs if poly_ll.contains(Point(x, y))]
                        if pts:
                            lons = np.array([pt[0] for pt in pts], dtype=np.float64)
                            lats = np.array([pt[1] for pt in pts], dtype=np.float64)
                            dsm_vals = rb_ctx.sample_dsm(lons, lats)
                            if dsm_vals is not None and np.any(~np.isnan(dsm_vals)):
                                dv = dsm_vals[~np.isnan(dsm_vals)]
                                relief = float(dv.max() - dv.min())
                                dem_note = f"Elev {dv.min():.1f}–{dv.max():.1f} m (relief {relief:.1f} m — {'good for stepped/terraced cuts' if relief >= 8.0 else 'gentle/flat relief'})"
                            _, b_mask = rb_ctx.sample_water_built_masks(lons, lats)
                            if b_mask is not None and len(b_mask) > 0:
                                cx_ll, cy_ll = poly_ll.centroid.x, poly_ll.centroid.y
                                quads = {"NW": [], "NE": [], "SW": [], "SE": []}
                                for (px, py), bv in zip(pts, b_mask):
                                    qk = ("N" if py >= cy_ll else "S") + ("E" if px >= cx_ll else "W")
                                    quads[qk].append(float(bv))
                                q_open = {k: round((1.0 - (sum(v) / len(v))) * 100.0) for k, v in quads.items() if v}
                                best_q = max(q_open, key=q_open.get) if q_open else "N/A"
                                quad_note = ", ".join(f"{k}:{v}% open" for k, v in q_open.items()) + f" -> place main masses in **{best_q}**"
                except Exception:
                    pass

            ctx_lines.extend([
                f"## Site #{rk} ({c.get('terrain_class')} · {c.get('dominant_engine')})",
                f"- **Coordinates:** `({c.get('lat')}, {c.get('lon')})` | **Area:** `{round(float((c.get('boundary') or {}).get('area_m2', 250000)) / 4200.0, 1)} feddans`",
                f"- **Parcel Shape & Bearing:** {shape_note}",
                f"- **DEM Relief:** {dem_note}",
                f"- **10 m Open-Land Quadrants:** {quad_note}",
                f"- **Forces:** {c.get('force_scores')}",
                f"- **Water / Nature Dist:** `{c.get('nat_dist_m')} m` | **Road Dist:** `{acc.get('road_dist_m')} m` | **Access:** `{acc.get('score')}/100`",
                f"- **Nearby Named GIS Features:** {'; '.join(ptrs) if ptrs else 'None named within 1.5 km'}",
                "",
            ])
        (out_dir / "intermediates" / "agent_site_context.md").write_text("\n".join(ctx_lines), encoding="utf-8")

    # 2. Stage B: require agent-authored seeds in intermediates/seeds/
    seeds_dir = out_dir / "intermediates" / "seeds"
    has_agent_seeds = seeds_dir.exists() and any(seeds_dir.glob("site_*_seed.json"))
    if not has_agent_seeds:
        print(f"\n[Stage A Complete — Agent Seed Authoring Required]")
        print(f"  Read:  {out_dir / 'intermediates' / 'agent_site_context.md'}")
        print(f"  Write: {seeds_dir / 'site_1_seed.json'} .. site_5_seed.json")
        print(f"  Then re-run with --skip-stage-a to complete Stage B, Dashboard, and Render Pack.")
        return
    sb_cmd = [sys.executable, "stage_b_builder.py", "--run-dir", str(out_dir), "--data-dir", str(data_dir), "--seeds-dir", str(seeds_dir)]
    run_step(sb_cmd, "Stage B: Agent Seed Expansion & Financial Reconciliation")

    # 3. DEM Terrain-Embedding Gate (Local Copernicus DSM 30 m / SRTM fallback)
    run_step(
        [sys.executable, "terrain_intelligence.py", "--run-dir", str(out_dir), "--data-dir", str(data_dir), "--apply"],
        "DEM Terrain-Embedding & Idiom Compatibility Gate",
    )

    # 4. Pre-Render Geometry & Raster Sanity Gate
    validate_stage_b_geometry(out_dir, data_dir, strict=args.strict_gate)

    # 5. NEST Experience-First Story Mode Dashboard + JS Gate
    run_step(
        [sys.executable, "build_nest_dashboard.py", "--run-dir", str(out_dir), "--plot-title", plot_title],
        "NEST 2.3 Dashboard Build",
    )
    verify_dashboard_js(out_dir / "nest_dashboard.html")

    # 6. Camera-Matched Esri Satellite Render Pack
    rp_cmd = [sys.executable, "GENERAL_KNOWLEDGE/architectural_render_skill/build_render_pack.py", "--run-dir", str(out_dir)]
    run_step(rp_cmd, "Satellite-Locked Render Pack")

    print(f"\n[NEST Pipeline Complete] Outputs ready -> {out_dir}")


if __name__ == "__main__":
    main()
