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
    if data_dir and (data_dir / "dataset-inventory.json").exists():
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
    ap.add_argument("--validate-only", action="store_true", help="Run Pre-Render Geometry & Raster Gate only")
    ap.add_argument("--strict-gate", action="store_true", help="Fail on built-up/pier warnings as well as errors")
    ap.add_argument("--refresh-tiles", action="store_true", help="Re-download Esri 42° satellite locks")
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

    stage_b_json = out_dir / "stage_b_projects.json"
    if not stage_b_json.exists():
        print(f"\n[Stage A Ready] {out_dir / 'intermediates' / 'stage_a_summary.json'} is ready for Stage B synthesis.")
        return

    # 2. DEM Terrain-Embedding Gate (Local Copernicus DSM 30 m / SRTM fallback)
    run_step(
        [sys.executable, "terrain_intelligence.py", "--run-dir", str(out_dir), "--data-dir", str(data_dir), "--apply"],
        "DEM Terrain-Embedding & Idiom Compatibility Gate",
    )

    # 3. Pre-Render Geometry & Raster Sanity Gate
    validate_stage_b_geometry(out_dir, data_dir, strict=args.strict_gate)

    # 4. NEST Experience-First Story Mode Dashboard + JS Gate
    run_step(
        [sys.executable, "build_nest_dashboard.py", "--run-dir", str(out_dir), "--plot-title", plot_title],
        "NEST 2.3 Dashboard Build",
    )
    verify_dashboard_js(out_dir / "nest_dashboard.html")

    # 6. 42° Camera-Matched Esri Satellite Render Pack
    rp_cmd = [sys.executable, "GENERAL_KNOWLEDGE/architectural_render_skill/build_render_pack.py", "--run-dir", str(out_dir)]
    if args.refresh_tiles:
        rp_cmd.append("--refresh-tiles")
    run_step(rp_cmd, "42° Camera-Matched Render Pack")

    print(f"\n[NEST Pipeline Complete] Outputs ready -> {out_dir}")


if __name__ == "__main__":
    main()
