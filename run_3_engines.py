"""
NEST Stage A: 3-Engine Plot Execution Pipeline (`run_3_engines.py`)
Evaluates any Egyptian 5x5 km GIS plot across Crystals (Development), Cells (Adaptation),
and Corals (Coordination), outputting `intermediates/` for Stage B NEST synthesis.

Usage:
    python run_3_engines.py --data-dir "<plot_dir>" --out-dir "<run_output_dir>" --plot-name "<Plot Name>"
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import unary_union

from heatmap_engine import (
    FORCE_NAMES,
    LocalProjection,
    filter_features,
    load_plot_gis,
    min_dist_to_points,
    parse_efficiency_ratios,
    parse_typology_config,
    score_factor,
    write_geotiff_float32,
    _sample_points_from_geoms,
)


ENGINE_SPECS = [
    ("crystals", "Crystals", "crystals_nature_forces.md", "engine1_development", "High-Gravity POI Anchor (Development Engine)"),
    ("cells", "Cells", "cells_nature_forces.md", "engine2_adaptation", "Ecotone & Contradiction (Metabolic Adaptation Engine)"),
    ("corals", "Corals", "corals_nature_forces.md", "engine3_coordination", "Symbiotic Seam & Spine (Coordination Engine)"),
]


def extract_observed_telemetry(features: Sequence[Dict[str, Any]], meta: Dict[str, Any]) -> Dict[str, Any]:
    """Extract real DEM, TMY, WorldPop, MPED, and dataset audit telemetry when present in GIS layers."""
    telemetry: Dict[str, Any] = {
        "climate_tmy": {"provenance": "Benchmark (Egypt Coastal/Arid Baseline)"},
        "dem_slope": {"surface_slope_median_deg": 0.5, "surface_slope_p90_deg": 2.0, "provenance": "Pending DEM"},
        "demographics": {"provenance": "Benchmark"},
        "governorate_budget": {"provenance": "Benchmark"},
        "agriculture_context": {"provenance": "Benchmark"},
        "dataset_inventory_audit": {},
    }

    slopes: List[float] = []
    ghi_vals: List[float] = []
    eto_vals: List[float] = []
    cdh_vals: List[float] = []

    for feat in features:
        p = feat.get("properties") or {}
        src = str(p.get("source_layer") or "").lower()
        if "development_investigation_priorities" in src or "slope" in src:
            for k in ("slope_med", "slope_median", "surface_slope_median_deg", "slope"):
                if p.get(k) is not None:
                    try:
                        slopes.append(float(p[k]))
                    except (TypeError, ValueError):
                        pass
            for k in ("ghi", "ghi_kwh_m2_yr"):
                if p.get(k) is not None:
                    try:
                        ghi_vals.append(float(p[k]))
                    except (TypeError, ValueError):
                        pass
            for k in ("eto", "eto_mm_yr"):
                if p.get(k) is not None:
                    try:
                        eto_vals.append(float(p[k]))
                    except (TypeError, ValueError):
                        pass
            for k in ("cdh", "cdh_26"):
                if p.get(k) is not None:
                    try:
                        cdh_vals.append(float(p[k]))
                    except (TypeError, ValueError):
                        pass

    if slopes:
        telemetry["dem_slope"] = {
            "surface_slope_median_deg": round(float(np.median(slopes)), 2),
            "surface_slope_p90_deg": round(float(np.percentile(slopes, 90)), 2),
            "provenance": "Observed (DEM)",
        }
    if ghi_vals:
        telemetry["climate_tmy"]["ghi_kwh_m2_yr"] = round(float(np.mean(ghi_vals)), 1)
        telemetry["climate_tmy"]["provenance"] = "Observed (TMY)"
    if eto_vals:
        telemetry["climate_tmy"]["eto_mm_yr"] = round(float(np.mean(eto_vals)), 1)
    if cdh_vals:
        telemetry["climate_tmy"]["cdh_base26"] = round(float(np.mean(cdh_vals)), 1)

    exp = meta.get("export_summary.json") or meta.get("dataset-inventory.json") or {}
    if exp:
        telemetry["dataset_inventory_audit"] = {
            "source_layers": exp.get("source_layers"),
            "exported_layers": exp.get("exported_layers"),
            "exported_vector_features": exp.get("exported_vector_features", len(features)),
        }
    else:
        telemetry["dataset_inventory_audit"] = {"exported_vector_features": len(features)}

    return telemetry


def compute_cliques(whitelist: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, ...]], List[Tuple[str, ...]]]:
    adj: Dict[str, set] = {f: set() for f in FORCE_NAMES}
    for a, b in whitelist:
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)

    c2: List[Tuple[str, ...]] = []
    c3: List[Tuple[str, ...]] = []
    for a, b in itertools.combinations(FORCE_NAMES, 2):
        if b in adj[a]:
            c2.append((a, b))
    for a, b, c in itertools.combinations(FORCE_NAMES, 3):
        if b in adj[a] and c in adj[a] and c in adj[b]:
            c3.append((a, b, c))
    return c2, c3


def score_cliques(force_arrays: Dict[str, np.ndarray], cliques: List[Tuple[str, ...]]) -> Tuple[np.ndarray, List[str]]:
    n = len(next(iter(force_arrays.values())))
    best = np.zeros(n, dtype=np.float64)
    best_lbl = [""] * n
    if not cliques:
        return best, best_lbl
    for cl in cliques:
        mat = np.stack([force_arrays[f] for f in cl], axis=1)  # (N, k)
        mean = np.mean(mat, axis=1)
        std = np.std(mat, axis=1, ddof=1)
        sc = np.maximum(0.0, mean - std)
        mask = sc > best
        if np.any(mask):
            best[mask] = sc[mask]
            lbl = " + ".join(cl)
            for idx in np.where(mask)[0]:
                best_lbl[idx] = lbl
    return best, best_lbl


def _build_organic_site_polygon(cx: float, cy: float, active_xy: np.ndarray, target_area_m2: float = 250000.0) -> Polygon:
    """Create a 50–70 feddan (~250,000 m²) GIS-snapped organic site boundary around (cx, cy)."""
    r = math.sqrt(target_area_m2 / math.pi)
    angles = np.linspace(0, 2 * math.pi, 24, endpoint=False)
    # Slight organic modulation while keeping area near target_area_m2
    pts = []
    for i, a in enumerate(angles):
        mod = 1.0 + 0.08 * math.sin(3 * a + 0.4) + 0.05 * math.cos(2 * a - 0.3)
        pts.append((cx + r * mod * math.cos(a), cy + r * mod * math.sin(a)))
    poly = Polygon(pts)
    return poly


def _select_peaks(scores: np.ndarray, xy: np.ndarray, k: int = 5, min_dist_m: float = 450.0) -> List[int]:
    order = np.argsort(-scores)
    chosen: List[int] = []
    for idx in order:
        if scores[idx] <= 1.0:
            break
        px, py = xy[idx]
        if all(math.hypot(px - xy[c, 0], py - xy[c, 1]) >= min_dist_m for c in chosen):
            chosen.append(int(idx))
            if len(chosen) >= k:
                break
    return chosen


def run_pipeline(data_dir: str, out_dir: str, plot_name: str, gk_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    inter_dir = os.path.join(out_dir, "intermediates")
    os.makedirs(inter_dir, exist_ok=True)

    print(f"[Stage A] Loading GIS plot from {data_dir} ...")
    boundary_ll, features_ll, meta = load_plot_gis(data_dir)
    centroid_ll = boundary_ll.centroid
    proj = LocalProjection(centroid_ll.x, centroid_ll.y)
    boundary_xy = proj.geom_to_xy(boundary_ll)

    features_xy = []
    for feat in features_ll:
        try:
            gxy = proj.geom_to_xy(feat["geometry"])
            if not gxy.is_empty:
                features_xy.append({"geometry": gxy, "properties": feat["properties"]})
        except Exception:
            continue

    telemetry = extract_observed_telemetry(features_ll, meta)
    eff_ratios = parse_efficiency_ratios(os.path.join(gk_dir, "building_typologies.md"))

    # Build 50m x 50m grid inside boundary
    minx, miny, maxx, maxy = boundary_xy.bounds
    cell_size = 50.0
    xs = np.arange(minx + cell_size / 2, maxx, cell_size)
    ys = np.arange(miny + cell_size / 2, maxy, cell_size)
    gx, gy = np.meshgrid(xs, ys)
    all_pts = np.column_stack([gx.ravel(), gy.ravel()])

    # Filter to active cells inside boundary
    active_mask = np.array([boundary_xy.contains(Point(px, py)) for px, py in all_pts], dtype=bool)
    active_idx = np.where(active_mask)[0]
    active_xy = all_pts[active_idx]
    n_act = active_xy.shape[0]
    print(f"[Stage A] Grid: {len(xs)}x{len(ys)} ({len(all_pts)} total, {n_act} active 50m cells)")

    # Terrain classification: Dry Land / Shoreline Edge (<=100m) / Open Water
    water_feats = filter_features(
        features_xy,
        "source_layer=Egypt — Water Areas OR source_layer=نهر النيل OR source_layer=Egypt — Nile River OR source_layer=Egypt — Waterways OR source_layer=River network",
    )
    water_polys = [f["geometry"] for f in water_feats if f["geometry"].geom_type in ("Polygon", "MultiPolygon")]
    water_pts = _sample_points_from_geoms([f["geometry"] for f in water_feats], step_m=60.0)
    d_wat = min_dist_to_points(active_xy, water_pts)

    in_water = np.zeros(n_act, dtype=bool)
    if water_polys:
        water_union = unary_union(water_polys)
        in_water = np.array([water_union.contains(Point(px, py)) for px, py in active_xy], dtype=bool)

    terrain_classes = np.empty(n_act, dtype=object)
    for i in range(n_act):
        if in_water[i] and d_wat[i] > 50.0:
            terrain_classes[i] = "Open Water"
        elif in_water[i] or d_wat[i] <= 100.0:
            terrain_classes[i] = "Shoreline Edge"
        else:
            terrain_classes[i] = "Dry Land"

    # Masks for buildings & roads
    bldg_feats = filter_features(features_xy, "source_layer=Egypt — Buildings OR source_layer=Built surface")
    road_feats = filter_features(features_xy, "source_layer=الطرق OR source_layer=Egypt — Roads OR source_layer=gis_osm_roads")
    bldg_pts = _sample_points_from_geoms([f["geometry"] for f in bldg_feats], step_m=40.0)
    road_pts = _sample_points_from_geoms([f["geometry"] for f in road_feats], step_m=40.0)
    d_bldg = min_dist_to_points(active_xy, bldg_pts)
    d_road = min_dist_to_points(active_xy, road_pts)

    # Natural proximity & accessibility
    nat_feats = filter_features(
        features_xy,
        "source_layer=Egypt — Water Areas OR source_layer=gbif_egypt OR source_layer=GBIF OR source_layer=cultural_places OR source_layer=unesco",
    )
    nat_pts = _sample_points_from_geoms([f["geometry"] for f in nat_feats], step_m=80.0)
    nat_dist_m = min_dist_to_points(active_xy, nat_pts) if nat_pts.shape[0] > 0 else np.full(n_act, 9999.0)
    nat_prox_score = np.clip(100.0 * np.exp(-nat_dist_m / 1200.0), 0.0, 100.0)

    slope_deg = float(telemetry["dem_slope"].get("surface_slope_median_deg", 0.5))
    slope_score = 100.0 if slope_deg <= 5.0 else (50.0 if slope_deg <= 15.0 else 15.0)
    road_score = np.where(d_road <= 250.0, 100.0, np.where(d_road <= 750.0, 50.0, 15.0))
    nest_access_score = 0.20 * road_score + 0.20 * 50.0 + 0.20 * 50.0 + 0.20 * slope_score + 0.20 * 50.0

    # Geographic bounds for GeoTIFF export
    ll_min = proj.to_ll(minx, miny)
    ll_max = proj.to_ll(maxx, maxy)
    px_lon = (ll_max[0] - ll_min[0]) / max(1, len(xs))
    px_lat = (ll_max[1] - ll_min[1]) / max(1, len(ys))

    engine_results: Dict[str, Dict[str, Any]] = {}
    all_candidates: List[Dict[str, Any]] = []

    for eng_key, eng_label, md_file, sub_dir, posture in ENGINE_SPECS:
        print(f"[Stage A] Running {eng_label} Engine ...")
        cfg = parse_typology_config(os.path.join(gk_dir, md_file), eng_label)
        eng_out = os.path.join(inter_dir, sub_dir)
        tif_dir = os.path.join(eng_out, "geotiff")
        os.makedirs(tif_dir, exist_ok=True)

        # Engine mask
        if eng_key in ("crystals", "cells"):
            eng_mask = (d_road > 25.0) & (d_bldg > 25.0)
        else:
            eng_mask = np.ones(n_act, dtype=bool)

        force_scores: Dict[str, np.ndarray] = {}
        top_drivers_per_force: Dict[str, List[Tuple[str, np.ndarray]]] = {}

        for fname in FORCE_NAMES:
            rules = cfg.factors_by_force.get(fname, [])
            acc = np.zeros(n_act, dtype=np.float64)
            w_sum = 0.0
            drivers: List[Tuple[str, np.ndarray]] = []
            for rule in rules:
                arr, cnt = score_factor(active_xy, features_xy, rule)
                contrib = arr * rule.weight * 100.0
                acc += arr * rule.weight
                w_sum += rule.weight
                drivers.append((rule.criterion, contrib))
            if w_sum > 0:
                acc = (acc / w_sum) * 100.0
            acc = np.where(eng_mask, np.clip(acc, 0.0, 100.0), 0.0)
            force_scores[fname] = acc
            top_drivers_per_force[fname] = drivers

            # Export GeoTIFF
            grid2d = np.full((len(ys), len(xs)), -9999.0, dtype=np.float32)
            flat = grid2d.ravel()
            flat[active_idx] = acc.astype(np.float32)
            safe_name = re.sub(r"[^a-zA-Z0-9_]+", "_", fname)
            write_geotiff_float32(os.path.join(tif_dir, f"{safe_name}.tif"), np.flipud(grid2d), ll_min[0], ll_max[1], px_lon, px_lat)

        mat_forces = np.stack([force_scores[f] for f in FORCE_NAMES], axis=1)
        best_fit = np.max(mat_forces, axis=1)
        dom_idx = np.argmax(mat_forces, axis=1)

        c2, c3 = compute_cliques(cfg.whitelist_pairs)
        syn2, syn2_lbl = score_cliques(force_scores, c2)
        syn3, syn3_lbl = score_cliques(force_scores, c3)

        # Engine-differentiated Hidden Potential
        if eng_key == "crystals":
            hidden = np.where(eng_mask, np.clip(0.55 * best_fit + 0.25 * syn2 + 0.20 * nat_prox_score, 0.0, 100.0), 0.0)
        elif eng_key == "cells":
            eco_coll = np.sqrt(force_scores["Hydrology & Waterfront"] * force_scores["Solar & Climate Intensity"])
            hidden = np.where(eng_mask, np.clip(0.45 * best_fit + 0.35 * eco_coll + 0.20 * nat_prox_score, 0.0, 100.0), 0.0)
        else:
            hidden = np.where(eng_mask, np.clip(0.50 * syn3 + 0.30 * best_fit + 0.20 * nest_access_score, 0.0, 100.0), 0.0)

        for label, arr in [("BestFit", best_fit), ("MixedUse_2plus", syn2), ("MixedUse_3plus", syn3), ("hidden_potential", hidden)]:
            grid2d = np.full((len(ys), len(xs)), -9999.0, dtype=np.float32)
            grid2d.ravel()[active_idx] = arr.astype(np.float32)
            write_geotiff_float32(os.path.join(tif_dir, f"{label}.tif"), np.flipud(grid2d), ll_min[0], ll_max[1], px_lon, px_lat)

        # Write 50m GeoJSON
        geo_feats = []
        for i in range(n_act):
            px, py = active_xy[i]
            lon, lat = proj.to_ll(px, py)
            geo_feats.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                    "properties": {
                        "dominant_force": FORCE_NAMES[int(dom_idx[i])],
                        "best_fit": round(float(best_fit[i]), 1),
                        "syn2": round(float(syn2[i]), 1),
                        "syn3": round(float(syn3[i]), 1),
                        "hidden_potential": round(float(hidden[i]), 1),
                        "terrain_class": terrain_classes[i],
                    },
                }
            )
        with open(os.path.join(eng_out, f"plot_50m_{eng_key}.geojson"), "w", encoding="utf-8") as f:
            json.dump({"type": "FeatureCollection", "features": geo_feats}, f)

        peaks = _select_peaks(hidden, active_xy, k=5, min_dist_m=450.0)
        engine_results[eng_key] = {
            "label": eng_label,
            "posture": posture,
            "force_scores": force_scores,
            "best_fit": best_fit,
            "dom_idx": dom_idx,
            "syn2": syn2,
            "syn3": syn3,
            "hidden": hidden,
            "peaks": peaks,
            "top_drivers_per_force": top_drivers_per_force,
        }

        with open(os.path.join(eng_out, "top_site_space_program.md"), "w", encoding="utf-8") as f:
            f.write(f"# {eng_label} Engine — Top Site Space Program ({plot_name})\n\n")
            if peaks:
                pi = peaks[0]
                dom_f = FORCE_NAMES[int(dom_idx[pi])]
                eff = eff_ratios.get(dom_f, 0.74)
                f.write(f"- **Top Cell Dominant Force:** {dom_f}\n")
                f.write(f"- **Hidden Potential Score:** {hidden[pi]:.1f}/100\n")
                f.write(f"- **Efficiency Ratio (NSF/GSF):** {eff*100:.0f}%\n")

    # Build Stratified Top 15 Candidate Pool & detect cross-engine convergence (<=350m)
    rank_counter = 1
    for eng_key, eng_label, _, _, posture in ENGINE_SPECS:
        res = engine_results[eng_key]
        for local_rank, idx in enumerate(res["peaks"], start=1):
            cx, cy = float(active_xy[idx, 0]), float(active_xy[idx, 1])
            lon, lat = proj.to_ll(cx, cy)

            # Check convergence across engines (<=350m or strong score at same cell)
            conv: List[str] = []
            for ek, el, _, _, _ in ENGINE_SPECS:
                if ek == eng_key:
                    conv.append(el)
                elif any(math.hypot(cx - active_xy[p, 0], cy - active_xy[p, 1]) <= 350.0 for p in engine_results[ek]["peaks"]):
                    conv.append(el)
            strategy = f"Merge ({' + '.join(conv)})" if len(conv) > 1 else f"Select: {eng_label}"

            fscores = {fn: round(float(res["force_scores"][fn][idx]), 1) for fn in FORCE_NAMES}
            dom_force = FORCE_NAMES[int(res["dom_idx"][idx])]
            poly_xy = _build_organic_site_polygon(cx, cy, active_xy, target_area_m2=250000.0)
            poly_ll = proj.geom_to_ll(poly_xy)
            b = poly_ll.bounds

            top_drivers = {}
            for ek, _, _, _, _ in ENGINE_SPECS:
                dr_list = []
                for crit, contrib_arr in engine_results[ek]["top_drivers_per_force"][dom_force]:
                    dr_list.append({"driver": crit, "contribution": round(float(contrib_arr[idx]), 1)})
                dr_list.sort(key=lambda x: -x["contribution"])
                top_drivers[ek] = dr_list[:3]

            cand = {
                "site_rank": rank_counter,
                "selection_role": f"{eng_label} #{local_rank} ({terrain_classes[idx]} • {strategy})",
                "dominant_engine": eng_label,
                "engine_posture": posture,
                "converging_engines": conv,
                "recommended_strategy": strategy,
                "terrain_class": terrain_classes[idx],
                "merit_score": round(float(res["hidden"][idx]), 1),
                "cx": cx,
                "cy": cy,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "engine_scores": {
                    ek: round(float(engine_results[ek]["best_fit"][idx]), 1) for ek, _, _, _, _ in ENGINE_SPECS
                },
                "engine_hidden_scores": {
                    ek: round(float(engine_results[ek]["hidden"][idx]), 1) for ek, _, _, _, _ in ENGINE_SPECS
                },
                "force_scores": fscores,
                "nat_dist_m": round(float(nat_dist_m[idx]), 1),
                "nat_prov": "Observed (Direct GIS)" if nat_dist_m[idx] < 2500.0 else "Benchmark",
                "accessibility": {
                    "score": round(float(nest_access_score[idx]), 1),
                    "road_dist_m": round(float(d_road[idx]), 1),
                    "settlement_dist_m": None,
                    "transit_dist_m": None,
                    "est_emergency_min": round(float(max(5.0, d_road[idx] / 25.0 + 10.0)), 1),
                    "slope_provenance": telemetry["dem_slope"]["provenance"],
                },
                "flags": {
                    "water_zone_warning": bool(terrain_classes[idx] in ("Open Water", "Shoreline Edge") and in_water[idx]),
                    "emergency_access_alert": bool(d_road[idx] > 1000.0),
                },
                "baseline_signal": {
                    "dominant_forces": [k for k, _ in sorted(fscores.items(), key=lambda kv: -kv[1])[:2]],
                    "typologies": [dom_force],
                },
                "landmark_capacity": {
                    "target_far": 0.22,
                    "landmark_capacity_gfa_m2": round(250000.0 * 0.22, 1),
                    "recommended_scale_tier": "Tier 1: Flagship National Landmark",
                },
                "gis_evidence": {
                    "top_drivers_by_engine": top_drivers,
                    "map_feature_pointers": [],
                },
                "skill_seeds": {
                    "crystals": {"parent_engine": "Crystals Engine", "role_in_project": "Primary Lead" if eng_key == "crystals" else "Supporting"},
                    "cells": {"parent_engine": "Cells Engine", "role_in_project": "Primary Lead" if eng_key == "cells" else "Supporting"},
                    "corals": {"parent_engine": "Corals Engine", "role_in_project": "Primary Lead" if eng_key == "corals" else "Supporting"},
                },
                "boundary": {
                    "footprint_type": "Contiguous",
                    "cluster_cells": 100,
                    "area_m2": round(float(poly_xy.area), 1),
                    "bbox_ll": [round(b[0], 6), round(b[1], 6), round(b[2], 6), round(b[3], 6)],
                    "geojson": mapping(poly_ll),
                },
            }
            all_candidates.append(cand)
            rank_counter += 1

    all_candidates.sort(key=lambda c: -c["merit_score"])
    for idx_r, c in enumerate(all_candidates, start=1):
        c["site_rank"] = idx_r

    summary = {
        "plot_label": plot_name,
        "spatial_force_layers": FORCE_NAMES,
        "bounds_ll": [[round(ll_min[1], 6), round(ll_min[0], 6)], [round(ll_max[1], 6), round(ll_max[0], 6)]],
        "grid": {"nx": int(len(xs)), "ny": int(len(ys)), "cell_size_m": cell_size},
        "terrain_breakdown_cells": {
            "dry_land": int(np.sum(terrain_classes == "Dry Land")),
            "shoreline_edge": int(np.sum(terrain_classes == "Shoreline Edge")),
            "open_water": int(np.sum(terrain_classes == "Open Water")),
        },
        "observed_plot_telemetry": telemetry,
        "engine_stats": {
            ek: {
                "mean_best_fit": round(float(np.mean(engine_results[ek]["best_fit"])), 2),
                "max_hidden_potential": round(float(np.max(engine_results[ek]["hidden"])), 2),
            }
            for ek, _, _, _, _ in ENGINE_SPECS
        },
        "candidate_pool": all_candidates,
        "top_5_candidates": all_candidates[:5],
    }

    with open(os.path.join(inter_dir, "stage_a_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Write hidden_opportunities.md
    with open(os.path.join(inter_dir, "hidden_opportunities.md"), "w", encoding="utf-8") as f:
        f.write(f"# Stage A Hidden Opportunities — {plot_name}\n\n")
        for c in all_candidates:
            f.write(f"## #{c['site_rank']} — {c['selection_role']}\n")
            f.write(f"- **Merit Score:** {c['merit_score']}/100 | **Terrain:** {c['terrain_class']} | **Coords:** {c['lat']}, {c['lon']}\n")
            f.write(f"- **Engine Scores:** Crystals {c['engine_scores']['crystals']}, Cells {c['engine_scores']['cells']}, Corals {c['engine_scores']['corals']}\n\n")

    # Build rich NEST 2.2 3-Engine Analysis Maps dashboard via dashboard_3engines_view
    import base64
    import io
    from PIL import Image
    from dashboard_3engines_view import build_3engine_dashboard

    typ_colors_rgb = [
        (14, 165, 233),
        (245, 158, 11),
        (16, 185, 129),
        (168, 85, 247),
        (239, 68, 68),
        (59, 130, 246),
    ]

    def _arr_to_b64_png(vals_1d: np.ndarray, rgb: Tuple[int, int, int]) -> str:
        rgba = np.zeros((len(ys), len(xs), 4), dtype=np.uint8)
        grid_v = np.zeros((len(ys), len(xs)), dtype=np.float64)
        grid_v.ravel()[active_idx] = vals_1d
        grid_v = np.flipud(grid_v)
        norm = np.clip(grid_v / 100.0, 0.0, 1.0)
        rgba[..., 0] = rgb[0]
        rgba[..., 1] = rgb[1]
        rgba[..., 2] = rgb[2]
        rgba[..., 3] = np.where(grid_v > 1.0, (40 + norm * 175).astype(np.uint8), 0)
        buf = io.BytesIO()
        Image.fromarray(rgba, "RGBA").save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    def _bestfit_to_b64_png(dom_1d: np.ndarray, bf_1d: np.ndarray) -> str:
        rgba = np.zeros((len(ys), len(xs), 4), dtype=np.uint8)
        g_dom = np.zeros((len(ys), len(xs)), dtype=np.int32)
        g_bf = np.zeros((len(ys), len(xs)), dtype=np.float64)
        g_dom.ravel()[active_idx] = dom_1d
        g_bf.ravel()[active_idx] = bf_1d
        g_dom = np.flipud(g_dom)
        g_bf = np.flipud(g_bf)
        for fi, rgb in enumerate(typ_colors_rgb):
            m = (g_dom == fi) & (g_bf > 1.0)
            rgba[m, 0] = rgb[0]
            rgba[m, 1] = rgb[1]
            rgba[m, 2] = rgb[2]
            rgba[m, 3] = np.clip(45 + (g_bf[m] / 100.0) * 170, 0, 225).astype(np.uint8)
        buf = io.BytesIO()
        Image.fromarray(rgba, "RGBA").save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    terrain_code_map = {"Dry Land": 0, "Shoreline Edge": 1, "Open Water": 2}
    engines_view_data = []
    for eng_key, eng_label, _, _, _ in ENGINE_SPECS:
        res = engine_results[eng_key]
        overlays = {fn: _arr_to_b64_png(res["force_scores"][fn], typ_colors_rgb[fi]) for fi, fn in enumerate(FORCE_NAMES)}
        overlays["Mixed-Use (2+)"] = _arr_to_b64_png(res["syn2"], (255, 97, 76))
        overlays["Mixed-Use (3+)"] = _arr_to_b64_png(res["syn3"], (163, 71, 58))
        overlays["Best-Fit Typology"] = _bestfit_to_b64_png(res["dom_idx"], res["best_fit"])
        overlays["Hidden Potential"] = _arr_to_b64_png(res["hidden"], (217, 119, 6))

        lookup: List[Any] = [None] * (len(xs) * len(ys))
        for local_i, flat_i in enumerate(active_idx):
            di = int(res["dom_idx"][local_i])
            dom_f = FORCE_NAMES[di]
            fvec = [round(float(res["force_scores"][fn][local_i]), 1) for fn in FORCE_NAMES]
            drv = sorted(
                [[crit, round(float(arr[local_i]), 1)] for crit, arr in res["top_drivers_per_force"][dom_f]],
                key=lambda x: -x[1],
            )[:3]
            lookup[int(flat_i)] = [
                di,
                1 if res["best_fit"][local_i] > 0 else 0,
                fvec,
                drv,
                round(float(res["syn2"][local_i]), 1),
                dom_f,
                round(float(res["syn3"][local_i]), 1),
                dom_f,
                2500,
                terrain_code_map.get(terrain_classes[local_i], 0),
                round(float(res["hidden"][local_i]), 1),
            ]
        engines_view_data.append({"title": f"{eng_label} Engine", "overlays": overlays, "lookup": lookup})

    hidden_gems = [
        [
            {
                "rank": c["site_rank"],
                "lat": c["lat"],
                "lon": c["lon"],
                "engine": f"{c['dominant_engine']} Engine",
                "mix": " + ".join(c["baseline_signal"]["dominant_forces"]),
                "hidden_score": c["merit_score"],
            }
            for c in all_candidates
            if c["dominant_engine"].lower() == ek
        ]
        for ek, _, _, _, _ in ENGINE_SPECS
    ]

    ref_bld = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": mapping(proj.geom_to_ll(f["geometry"])), "properties": {}} for f in bldg_feats[:120]]}
    ref_rd = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": mapping(proj.geom_to_ll(f["geometry"])), "properties": {}} for f in road_feats[:150]]}
    ref_wat = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": mapping(proj.geom_to_ll(f["geometry"])), "properties": {}} for f in water_feats[:80]]}
    demand_per_res = {fn: 1.5 for fn in FORCE_NAMES}
    space_templates = {fn: [["Primary Commons", 40], ["Research & Labs", 35], ["Support & Tare", 25]] for fn in FORCE_NAMES}

    combined_overlays = {
        fn: _arr_to_b64_png(np.maximum.reduce([engine_results[ek]["force_scores"][fn] for ek, _, _, _, _ in ENGINE_SPECS]), typ_colors_rgb[fi])
        for fi, fn in enumerate(FORCE_NAMES)
    }
    combined_overlays["Mixed-Use (2+)"] = _arr_to_b64_png(np.maximum.reduce([engine_results[ek]["syn2"] for ek, _, _, _, _ in ENGINE_SPECS]), (255, 97, 76))
    combined_overlays["Mixed-Use (3+)"] = _arr_to_b64_png(np.maximum.reduce([engine_results[ek]["syn3"] for ek, _, _, _, _ in ENGINE_SPECS]), (163, 71, 58))
    comb_bf = np.maximum.reduce([engine_results[ek]["best_fit"] for ek, _, _, _, _ in ENGINE_SPECS])
    comb_hid = np.maximum.reduce([engine_results[ek]["hidden"] for ek, _, _, _, _ in ENGINE_SPECS])
    combined_overlays["Best-Fit Typology"] = _bestfit_to_b64_png(engine_results["crystals"]["dom_idx"], comb_bf)
    combined_overlays["Hidden Potential"] = _arr_to_b64_png(comb_hid, (217, 119, 6))

    dash_html = build_3engine_dashboard(
        bounds=summary["bounds_ll"],
        nx=len(xs),
        ny=len(ys),
        typ_names=FORCE_NAMES,
        typ_colors_rgb=typ_colors_rgb,
        engines_data=engines_view_data,
        ref_buildings=ref_bld,
        ref_roads=ref_rd,
        ref_water=ref_wat,
        space_templates=space_templates,
        eff_ratios={fn: eff_ratios.get(fn, 0.75) for fn in FORCE_NAMES},
        demand_per_res=demand_per_res,
        hidden_gems=hidden_gems,
        combined_overlays=combined_overlays,
        top_sites=all_candidates[:5],
    )
    with open(os.path.join(inter_dir, "3engines_base_dashboard.html"), "w", encoding="utf-8") as f:
        f.write(dash_html)

    print(f"[Stage A] Complete! Outputs written to {inter_dir}")
    return os.path.join(inter_dir, "stage_a_summary.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="NEST Stage A 3-Engine GIS Evaluation")
    parser.add_argument("--data-dir", required=True, help="Path to single GIS plot folder")
    parser.add_argument("--out-dir", required=True, help="Path to run output directory")
    parser.add_argument("--plot-name", required=True, help="Human-readable plot name")
    parser.add_argument("--gk-dir", default=os.path.join(os.path.dirname(__file__), "GENERAL_KNOWLEDGE"), help="Path to GENERAL_KNOWLEDGE")
    args = parser.parse_args()
    run_pipeline(args.data_dir, args.out_dir, args.plot_name, args.gk_dir)


if __name__ == "__main__":
    main()
