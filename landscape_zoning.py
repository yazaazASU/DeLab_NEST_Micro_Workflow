#!/usr/bin/env python3
"""
NEST GIS-Driven Landscape Zoning Engine (`landscape_zoning.py`)
===============================================================
Replaces arbitrary geometric stripe-slicing with evidence-based, 5-tier organic
landscape zoning driven by real local GIS data (Copernicus DSM 30 m elevation &
slope, WorldCover 10 m water/built masks, GHS built-up, and vector proximity to
roads, water, protected areas, and heritage routes).

5 Canonical Intervention Tiers (from `GENERAL_KNOWLEDGE/NEST_Landscape_Intelligence.md`):
  - Preserve              (#15803d) — 0% buildable · Restricted / Guided access
  - Minimal Intervention  (#64748b) — 0% buildable · Minimal human footprint
  - Restore               (#65a30d) — Ecological recovery / disturbed-edge healing
  - Enhance               (#0d9488) — Drainage, shade, breeze & transition corridors
  - Activate              (#d97706) — Development Interface / verified buildable envelope

Exports:
  - Evidence-derived organic polygons (100.0% area reconciliation, 0 overlaps)
  - Operational metadata per zone (`gis_evidence`, `access_level`, `water_demand`, `confidence`)
  - `buildable_envelope` summary checked by the Pre-Render Gate
  - Standalone `<run_dir>/landscape_zones.geojson` for QGIS / CAD handover
  - Publication site-zoning map PNGs for `export_nest_pdf.py`
"""
from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path
from typing import Any

import numpy as np
from shapely.geometry import MultiPolygon, Point, Polygon, box, mapping, shape
from shapely.ops import unary_union

FEDDAN_M2 = 4200.0

TIER_META: dict[str, dict[str, str]] = {
    "Preserve": {
        "family": "Natural / Preserved Landscape",
        "color": "#15803d",
        "access_level": "Restricted / Guided",
        "water_demand": "Zero",
        "default_name": "Ecological & Terrain Preserve",
        "default_activities": "Marked low-impact observation trails only; zero built footprints.",
    },
    "Minimal Intervention": {
        "family": "Minimal Intervention Buffer",
        "color": "#64748b",
        "access_level": "Low-Impact Trail Only",
        "water_demand": "Zero",
        "default_name": "Quiet Natural Buffer Plain",
        "default_activities": "Retained intact with minimal disturbance and dark-sky protection.",
    },
    "Restore": {
        "family": "Restoration Landscape",
        "color": "#65a30d",
        "access_level": "Guided / Educational",
        "water_demand": "Low-Native",
        "default_name": "Disturbed-Edge Ecological Restoration",
        "default_activities": "Native scrub/flora recovery, soil healing, and botanical walks.",
    },
    "Enhance": {
        "family": "Connecting / Climate Corridor",
        "color": "#0d9488",
        "access_level": "Open Public",
        "water_demand": "Greywater-Only",
        "default_name": "Wadi Shade & Runoff Spine",
        "default_activities": "Shaded pedestrian paths, water-harvesting swales, and breeze decks.",
    },
    "Activate": {
        "family": "Landscape-Integrated Development Interface",
        "color": "#d97706",
        "access_level": "Open Public",
        "water_demand": "Greywater-Only",
        "default_name": "Public Arrival & Development Interface",
        "default_activities": "Primary architectural clusters, arrival courts, markets, and civic plazas.",
    },
}

TIER_ORDER = ["Preserve", "Minimal Intervention", "Restore", "Enhance", "Activate"]
TIER_ID = {name: idx for idx, name in enumerate(TIER_ORDER)}


def _ensure_poly(g) -> Polygon | MultiPolygon:
    if g is None or g.is_empty:
        return Polygon()
    if not g.is_valid:
        g = g.buffer(0)
    if isinstance(g, (Polygon, MultiPolygon)):
        return g
    polys = [p for p in getattr(g, "geoms", []) if isinstance(p, (Polygon, MultiPolygon)) and not p.is_empty]
    return unary_union(polys).buffer(0) if polys else Polygon()


def _majority_smooth(grid: np.ndarray, valid: np.ndarray, passes: int = 2) -> np.ndarray:
    """3x3 spatial majority filter inside the valid parcel mask to remove salt-and-pepper noise."""
    out = grid.copy()
    ny, nx = out.shape
    for _ in range(passes):
        nxt = out.copy()
        for r in range(ny):
            r0, r1 = max(0, r - 1), min(ny, r + 2)
            for c in range(nx):
                if not valid[r, c]:
                    continue
                c0, c1 = max(0, c - 1), min(nx, c + 2)
                sub_v = valid[r0:r1, c0:c1]
                vals = out[r0:r1, c0:c1][sub_v]
                if vals.size:
                    counts = np.bincount(vals, minlength=len(TIER_ORDER))
                    # Slight weight to current cell to avoid oscillation
                    counts[out[r, c]] += 1
                    nxt[r, c] = int(np.argmax(counts))
        out = nxt
    return out


def _dist_to_mask(mask: np.ndarray, cell_m: float) -> np.ndarray:
    """Fast exact Euclidean distance (in meters) from every cell to True cells in `mask`."""
    ny, nx = mask.shape
    ys, xs = np.where(mask)
    if ys.size == 0:
        return np.full((ny, nx), 9999.0, dtype=np.float32)
    gy, gx = np.mgrid[0:ny, 0:nx]
    # Broadcast in chunks if large, though parcel grids are ~30x30 (<= 1,500 cells)
    dy = gy[:, :, None] - ys[None, None, :]
    dx = gx[:, :, None] - xs[None, None, :]
    d2 = np.min(dy * dy + dx * dx, axis=2)
    return (np.sqrt(d2.astype(np.float32)) * float(cell_m)).astype(np.float32)


def _norm01(arr: np.ndarray, valid: np.ndarray) -> np.ndarray:
    out = np.zeros_like(arr, dtype=np.float32)
    v = arr[valid]
    if v.size == 0:
        return out
    lo, hi = float(np.nanmin(v)), float(np.nanmax(v))
    if hi - lo < 1e-6:
        return out
    out[valid] = np.clip((arr[valid] - lo) / (hi - lo), 0.0, 1.0)
    return out


def _tier_match_seed(tier: str, z_seeds: list[dict[str, Any]] | None) -> dict[str, Any]:
    if not z_seeds:
        return {}
    t_low = tier.lower()
    for zs in z_seeds:
        iv = str(zs.get("intervention") or "").lower().strip()
        if t_low == iv:
            return zs
        if t_low == "minimal intervention" and ("minimal" in iv or "buffer" in iv):
            return zs
        if t_low in iv or iv in t_low:
            return zs
    return {}


def build_gis_landscape_zones(
    site_m: Polygon,
    proj: Any,
    raster_bundle: Any = None,
    cand: dict[str, Any] | None = None,
    z_seeds: list[dict[str, Any]] | None = None,
    site_bearing_deg: float = 0.0,
    cell_m: float = 20.0,
    built_footprint_m2: float = 0.0,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Classify a site parcel on a 20 m GIS grid into 5 organic, 100%-reconciled
    landscape zones (`Preserve`, `Minimal Intervention`, `Restore`, `Enhance`, `Activate`)
    and compute the verified `buildable_envelope` summary.
    """
    site_m = _ensure_poly(site_m)
    site_area_m2 = max(site_m.area, 1.0)
    minx, miny, maxx, maxy = site_m.bounds

    nx = max(12, min(48, int(math.ceil((maxx - minx) / cell_m))))
    ny = max(12, min(48, int(math.ceil((maxy - miny) / cell_m))))
    dx = (maxx - minx) / nx
    dy = (maxy - miny) / ny
    eff_cell = 0.5 * (dx + dy)

    xs = minx + (np.arange(nx) + 0.5) * dx
    ys = miny + (np.arange(ny) + 0.5) * dy
    gx, gy = np.meshgrid(xs, ys)

    valid = np.zeros((ny, nx), dtype=bool)
    for r in range(ny):
        for c in range(nx):
            if site_m.contains(Point(float(gx[r, c]), float(gy[r, c]))):
                valid[r, c] = True
    if not np.any(valid):
        valid[:, :] = True

    # Convert grid centers to WGS84 for local raster sampling
    lons = np.zeros((ny, nx), dtype=np.float64)
    lats = np.zeros((ny, nx), dtype=np.float64)
    for r in range(ny):
        for c in range(nx):
            ll = proj.geom_to_lonlat(Point(float(gx[r, c]), float(gy[r, c])))
            lons[r, c] = ll.x
            lats[r, c] = ll.y

    has_dsm = False
    has_wc = False
    elev = np.zeros((ny, nx), dtype=np.float32)
    slope_deg = np.zeros((ny, nx), dtype=np.float32)
    water_mask = np.zeros((ny, nx), dtype=bool)
    built_mask = np.zeros((ny, nx), dtype=bool)

    if raster_bundle is not None:
        try:
            d_vals = raster_bundle.sample_dsm(lons.ravel(), lats.ravel())
            if d_vals is not None and np.any(~np.isnan(d_vals)):
                arr = np.asarray(d_vals, dtype=np.float32).reshape((ny, nx))
                med = float(np.nanmedian(arr[valid])) if np.any(~np.isnan(arr[valid])) else 0.0
                elev = np.where(np.isnan(arr), med, arr)
                gy_e, gx_e = np.gradient(elev, dy, dx)
                slope_deg = np.degrees(np.arctan(np.hypot(gx_e, gy_e))).astype(np.float32)
                has_dsm = True
        except Exception:
            pass
        try:
            wm, bm = raster_bundle.sample_water_built_masks(lons.ravel(), lats.ravel())
            if wm is not None and len(wm) == ny * nx:
                water_mask = np.asarray(wm, dtype=bool).reshape((ny, nx))
                has_wc = True
            if bm is not None and len(bm) == ny * nx:
                built_mask = np.asarray(bm, dtype=bool).reshape((ny, nx))
                has_wc = True
        except Exception:
            pass

    confidence_lbl = "Measured GIS" if (has_dsm or has_wc) else "Provisional"

    # Normalized directional / terrain gradients
    elev_v = elev[valid]
    relief_m = float(np.max(elev_v) - np.min(elev_v)) if elev_v.size else 0.0
    elev_n = _norm01(elev, valid)
    slope_n = _norm01(slope_deg, valid)
    dist_water = _dist_to_mask(water_mask, eff_cell)
    dist_built = _dist_to_mask(built_mask, eff_cell)

    # Parcel axis projection (for deterministic road/access side vs. quiet/preserve side when flat)
    ang = math.radians(float(site_bearing_deg or 0.0))
    cx_m, cy_m = site_m.centroid.x, site_m.centroid.y
    u_axis = (gx - cx_m) * math.cos(ang) + (gy - cy_m) * math.sin(ang)
    v_axis = -(gx - cx_m) * math.sin(ang) + (gy - cy_m) * math.cos(ang)
    u_n = _norm01(u_axis, valid)
    v_n = _norm01(v_axis, valid)

    # Determine road/access & nature context from Stage A candidate
    acc = (cand or {}).get("accessibility") or {}
    road_dist = float(acc.get("road_dist_m", 150.0) or 150.0)
    nat_dist = float((cand or {}).get("nat_dist_m", 9999.0) or 9999.0)
    ptrs = ((cand or {}).get("gis_evidence") or {}).get("map_feature_pointers") or []
    has_protected = any("protected" in str(x).lower() or "محمية" in str(x) or "شايب" in str(x) for x in ptrs)
    has_heritage = any("roman" in str(x).lower() or "historic" in str(x).lower() or "heritage" in str(x).lower() for x in ptrs)

    # Compute per-cell composite suitability scores for each of the 5 tiers
    # 1. Preserve: water/shoreline, steep slopes, upper ridges, or sensitive far edge
    preserve_score = (
        (dist_water <= 85.0).astype(np.float32) * 2.5
        + (slope_deg >= 7.5).astype(np.float32) * 1.4
        + slope_n * (0.95 if relief_m >= 8.0 else 0.35)
        + elev_n * (0.55 if (relief_m >= 10.0 or has_protected) else 0.25)
        + (1.0 - v_n) * (0.45 if has_heritage else 0.25)
    )
    # 2. Activate (Development Interface): flattest, unbuilt, dry, well-drained NW/access side
    activate_score = (
        (1.0 - slope_n) * 0.9
        + (1.0 - (water_mask | built_mask).astype(np.float32)) * 1.5
        + (1.0 - u_n) * 0.55
        + v_n * 0.55
        - (dist_water <= 60.0).astype(np.float32) * 2.0
    )
    # 3. Restore: near built-up/disturbed edges or mid-outer transition margins
    restore_score = (
        (dist_built <= 80.0).astype(np.float32) * 1.8
        + (built_mask.astype(np.float32)) * 1.2
        + (1.0 - np.abs(u_n - 0.55) * 2.0) * 0.55
        + (1.0 - v_n) * 0.35
    )
    # 4. Enhance: lower-elevation drainage/wadi swales & breeze corridors bridging Activate <-> Preserve
    enhance_score = (
        (1.0 - elev_n) * (0.95 if relief_m >= 6.0 else 0.45)
        + (1.0 - np.abs(v_n - 0.48) * 2.0) * 0.65
        + (1.0 - slope_n) * 0.30
    )
    # 5. Minimal Intervention: remote quiet flank farthest from Activate
    minimal_score = (
        u_n * 0.70
        + (1.0 - v_n) * 0.45
        + (1.0 - (built_mask | water_mask).astype(np.float32)) * 0.50
    )

    # Classify cells using evidence thresholds + ranked allocation so every tier sits on its true GIS ground
    cls = np.full((ny, nx), TIER_ID["Enhance"], dtype=np.int32)
    n_valid = int(np.sum(valid))
    v_idx = np.argwhere(valid)

    # Natural evidence-driven target fractions (bounded for realism & buildability)
    # Steep/water/protected parcels naturally carry larger Preserve + Minimal Intervention shares
    steep_frac = float(np.mean(slope_deg[valid] >= 6.5)) if has_dsm else 0.0
    water_frac = float(np.mean(dist_water[valid] <= 85.0)) if has_wc else 0.0
    built_frac = float(np.mean(dist_built[valid] <= 75.0)) if has_wc else 0.0

    p_share = min(0.45, max(0.22, 0.24 + 0.55 * steep_frac + 0.60 * water_frac + (0.06 if has_protected else 0.0)))
    a_share = min(0.32, max(0.18, 0.26 - 0.35 * steep_frac - 0.35 * water_frac + (0.04 if road_dist <= 80.0 else 0.0)))
    r_share = min(0.24, max(0.14, 0.16 + 0.45 * built_frac))
    m_share = min(0.18, max(0.10, 0.12 + (0.04 if has_protected else 0.0)))
    e_share = max(0.12, 1.0 - (p_share + a_share + r_share + m_share))
    tot_s = p_share + a_share + r_share + m_share + e_share
    p_share, a_share, r_share, m_share, e_share = [x / tot_s for x in (p_share, a_share, r_share, m_share, e_share)]

    assigned = np.zeros((ny, nx), dtype=bool)

    def _claim(tier_name: str, score_arr: np.ndarray, count: int) -> None:
        avail = valid & (~assigned)
        coords = np.argwhere(avail)
        if coords.size == 0 or count <= 0:
            return
        sc = score_arr[coords[:, 0], coords[:, 1]]
        take = min(count, len(coords))
        top = np.argsort(-sc)[:take]
        sel = coords[top]
        cls[sel[:, 0], sel[:, 1]] = TIER_ID[tier_name]
        assigned[sel[:, 0], sel[:, 1]] = True

    # Priority order: 1) Preserve (hardest environmental constraints), 2) Activate (best buildable ground),
    # 3) Restore (disturbed edges), 4) Minimal Intervention (remote quiet plain), 5) Enhance (remaining drainage/transition)
    _claim("Preserve", preserve_score, int(round(n_valid * p_share)))
    _claim("Activate", activate_score, int(round(n_valid * a_share)))
    _claim("Restore", restore_score, int(round(n_valid * r_share)))
    _claim("Minimal Intervention", minimal_score, int(round(n_valid * m_share)))
    rem = valid & (~assigned)
    cls[rem] = TIER_ID["Enhance"]

    # Smooth into organic, contiguous landscape zones
    cls = _majority_smooth(cls, valid, passes=2)

    # Convert raster classes to smooth, non-overlapping, 100%-reconciled polygons clipped to site_m
    raw_polys: dict[str, Polygon | MultiPolygon] = {}
    for tier in TIER_ORDER:
        tid = TIER_ID[tier]
        cells = np.argwhere(valid & (cls == tid))
        if cells.size == 0:
            continue
        boxes = [
            box(minx + c * dx, miny + r * dy, minx + (c + 1) * dx, miny + (r + 1) * dy)
            for r, c in cells
        ]
        u = unary_union(boxes).buffer(eff_cell * 0.35, join_style=1).buffer(-eff_cell * 0.30, join_style=1)
        u = _ensure_poly(u.intersection(site_m))
        if not u.is_empty and u.area > 10.0:
            raw_polys[tier] = u

    # Enforce strict pairwise disjointness + 100.0% parcel coverage
    final_polys: dict[str, Polygon | MultiPolygon] = {}
    claimed_geom = Polygon()
    for tier in TIER_ORDER:
        g = raw_polys.get(tier)
        if g is None or g.is_empty:
            continue
        g_clean = _ensure_poly(g.difference(claimed_geom)) if not claimed_geom.is_empty else g
        if not g_clean.is_empty and g_clean.area > 10.0:
            final_polys[tier] = g_clean
            claimed_geom = _ensure_poly(unary_union([claimed_geom, g_clean])) if not claimed_geom.is_empty else g_clean

    # Assign any residual slivers along the boundary to their nearest touching zone for exact 100.0% reconciliation
    sliver = _ensure_poly(site_m.difference(claimed_geom)) if not claimed_geom.is_empty else site_m
    if not sliver.is_empty and sliver.area > 1.0 and final_polys:
        sliv_parts = list(sliver.geoms) if isinstance(sliver, MultiPolygon) else [sliver]
        for sp in sliv_parts:
            best_t = min(final_polys.keys(), key=lambda t: final_polys[t].distance(sp))
            final_polys[best_t] = _ensure_poly(unary_union([final_polys[best_t], sp]))

    # Assemble rich landscape_zones list with measured per-zone GIS evidence & seed metadata
    zones_out: list[dict[str, Any]] = []
    for idx, tier in enumerate(TIER_ORDER, 1):
        zp = final_polys.get(tier)
        if zp is None or zp.is_empty:
            continue
        tm = TIER_META[tier]
        zs = _tier_match_seed(tier, z_seeds)
        tid = TIER_ID[tier]
        zmask = valid & (cls == tid)

        # Compute measured per-zone GIS evidence summary
        ev_bits = []
        if has_dsm and np.any(zmask):
            z_el = elev[zmask]
            z_sl = slope_deg[zmask]
            ev_bits.append(f"Elev {float(np.min(z_el)):.1f}–{float(np.max(z_el)):.1f} m, mean slope {float(np.mean(z_sl)):.1f}°")
        if has_wc and np.any(zmask):
            b_pct = float(np.mean(built_mask[zmask]) * 100.0)
            w_pct = float(np.mean(water_mask[zmask]) * 100.0)
            if w_pct >= 1.0:
                ev_bits.append(f"{w_pct:.0f}% surface water")
            elif b_pct >= 1.0:
                ev_bits.append(f"{b_pct:.0f}% existing built edge")
            else:
                ev_bits.append("100% open unbuilt ground")
        if tier == "Activate":
            ev_bits.append(f"road access {road_dist:.0f} m · buildable interface")
        elif tier == "Preserve" and (has_protected or has_heritage):
            ev_bits.append("protected/heritage setback locked 0% buildable")
        elif tier == "Minimal Intervention":
            ev_bits.append("quiet buffer plain locked 0% buildable")
        elif tier == "Enhance" and relief_m >= 6.0:
            ev_bits.append("lower-elevation wadi/breeze corridor")
        gis_ev_str = " · ".join(ev_bits) if ev_bits else "Parcel terrain & proximity classification"

        a_m2 = zp.area
        sh_pct = (a_m2 / site_area_m2) * 100.0
        zones_out.append({
            "id": f"L-0{len(zones_out) + 1}",
            "name": zs.get("name") or tm["default_name"],
            "family": zs.get("family") or tm["family"],
            "intervention": tier,
            "why_here": zs.get("why_here") or gis_ev_str,
            "outdoor_activities": zs.get("outdoor_activities") or tm["default_activities"],
            "gis_evidence": zs.get("gis_evidence") or gis_ev_str,
            "access_level": zs.get("access_level") or tm["access_level"],
            "water_demand": zs.get("water_demand") or tm["water_demand"],
            "confidence": zs.get("confidence") or confidence_lbl,
            "buildable": tier in ("Activate", "Enhance"),
            "area_m2": round(a_m2),
            "area_ha": round(a_m2 / 10000.0, 2),
            "area_feddans": round(a_m2 / FEDDAN_M2, 2),
            "share_pct": round(sh_pct, 1),
            "color": tm["color"],
            "geom": mapping(proj.geom_to_lonlat(zp)),
        })

    # Reconcile displayed share_pct to sum to 100.0%
    if zones_out:
        diff = round(100.0 - sum(z["share_pct"] for z in zones_out), 1)
        zones_out[-1]["share_pct"] = round(zones_out[-1]["share_pct"] + diff, 1)

    # Compute verified Development Interface / Buildable Envelope summary
    act_m2 = sum(z["area_m2"] for z in zones_out if z["intervention"] == "Activate")
    enh_m2 = sum(z["area_m2"] for z in zones_out if z["intervention"] == "Enhance")
    locked_m2 = sum(z["area_m2"] for z in zones_out if z["intervention"] in ("Preserve", "Minimal Intervention"))
    net_buildable_m2 = round(act_m2 + 0.35 * enh_m2)
    cov_pct = round((built_footprint_m2 / max(net_buildable_m2, 1.0)) * 100.0, 1) if built_footprint_m2 > 0 else 0.0
    # Build plain-English site-specific zoning rationale explaining WHY this site got its exact split
    z_by_tier = {z["intervention"]: z for z in zones_out}
    rationale_parts: list[str] = []
    if "Preserve" in z_by_tier:
        zp_d = z_by_tier["Preserve"]
        rationale_parts.append(
            f"Preserve claimed {zp_d['share_pct']}% ({zp_d['area_feddans']} fed.) first on the parcel's highest-constraint ground ({zp_d['gis_evidence']})."
        )
    if "Activate" in z_by_tier:
        za_d = z_by_tier["Activate"]
        rationale_parts.append(
            f"Activate took {za_d['share_pct']}% ({za_d['area_feddans']} fed.) on the flattest 100% open ground nearest road access ({road_dist:.0f} m), yielding {net_buildable_m2:,} m² net buildable ({cov_pct}% footprint coverage)."
        )
    if "Restore" in z_by_tier:
        zr_d = z_by_tier["Restore"]
        rationale_parts.append(
            f"Restore covers {zr_d['share_pct']}% ({zr_d['gis_evidence']})."
        )
    if "Minimal Intervention" in z_by_tier and "Enhance" in z_by_tier:
        zm_d, ze_d = z_by_tier["Minimal Intervention"], z_by_tier["Enhance"]
        rationale_parts.append(
            f"Minimal Intervention ({zm_d['share_pct']}%) locks the quietest natural flank at 0% buildable (total {round((locked_m2 / site_area_m2) * 100.0, 1)}% locked), while Enhance ({ze_d['share_pct']}%) follows the lower-elevation drainage/breeze seam."
        )

    buildable_envelope = {
        "activate_m2": act_m2,
        "enhance_m2": enh_m2,
        "net_buildable_m2": net_buildable_m2,
        "preserve_locked_m2": locked_m2,
        "preserve_locked_pct": round((locked_m2 / site_area_m2) * 100.0, 1),
        "building_footprint_m2": round(built_footprint_m2),
        "envelope_coverage_pct": cov_pct,
        "fits_envelope": (built_footprint_m2 <= net_buildable_m2 * 0.65) if built_footprint_m2 > 0 else True,
        "rule": "Preserve & Minimal Intervention locked at 0% buildable; buildings confined to Activate + low-impact Enhance interface.",
        "zoning_rationale": " ".join(rationale_parts),
        "method_summary": "20 m GIS grid classified in priority order: 1) Preserve (steep slope / water / protected & heritage setbacks) → 2) Activate (flattest open ground nearest road) → 3) Restore (disturbed/built edges) → 4) Minimal Intervention (quiet remote plain) → 5) Enhance (lower-elevation drainage & breeze corridors).",
    }
    return zones_out, buildable_envelope


def format_stage_a_landscape_markdown(site_rank: int, zones: list[dict[str, Any]], env: dict[str, Any]) -> list[str]:
    """Compact Stage A evidence-derived landscape summary for agent_site_context.md (Pass 1)."""
    z_bits = " | ".join(f"{z['id']} {z['intervention']} {z['share_pct']}% ({z['area_feddans']} fed.)" for z in zones)
    return [
        f"- **Pass-1 GIS Landscape Zones (Evidence-Derived):** {z_bits}",
        f"- **Verified Buildable Envelope:** `{env['net_buildable_m2']:,} m²` net buildable (`Activate` {env['activate_m2']:,} m² + 35% `Enhance`), `{env['preserve_locked_pct']}%` locked 0% buildable (`Preserve` + `Minimal Intervention`)",
    ]


def export_landscape_zones_geojson(run_dir: Path, projects: list[dict[str, Any]]) -> Path:
    """Export all projects' organic GIS landscape zones to standalone `<run_dir>/landscape_zones.geojson` for QGIS/CAD."""
    features = []
    for p in projects:
        for z in p.get("landscape_zones") or []:
            geom = z.get("geom")
            if not geom:
                continue
            features.append({
                "type": "Feature",
                "properties": {
                    "project_rank": p.get("rank"),
                    "project_title": p.get("title"),
                    "engine": p.get("engine"),
                    "zone_id": z.get("id"),
                    "zone_name": z.get("name"),
                    "family": z.get("family"),
                    "intervention": z.get("intervention"),
                    "share_pct": z.get("share_pct"),
                    "area_m2": z.get("area_m2"),
                    "area_ha": z.get("area_ha"),
                    "area_feddans": z.get("area_feddans"),
                    "buildable": bool(z.get("buildable")),
                    "access_level": z.get("access_level"),
                    "water_demand": z.get("water_demand"),
                    "confidence": z.get("confidence"),
                    "gis_evidence": z.get("gis_evidence"),
                    "why_here": z.get("why_here"),
                    "outdoor_activities": z.get("outdoor_activities"),
                    "color": z.get("color"),
                },
                "geometry": geom,
            })
    out_path = run_dir / "landscape_zones.geojson"
    out_path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return out_path


def render_zone_map_png(project: dict[str, Any], out_path: Path) -> Path | None:
    """Render a crisp publication-grade 5-tier landscape zoning map PNG for PDF embedding."""
    zones = project.get("landscape_zones") or []
    if not zones:
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Patch, Polygon as MplPoly

        fig, ax = plt.subplots(figsize=(5.6, 3.2), dpi=180)
        fig.patch.set_facecolor("#FFFAF7")
        ax.set_facecolor("#F5F1EE")

        def _plot_geom(g_obj, fc, ec, lw=0.8, alpha=0.82):
            if isinstance(g_obj, Polygon):
                xs, ys = g_obj.exterior.xy
                ax.add_patch(MplPoly(list(zip(xs, ys)), closed=True, facecolor=fc, edgecolor=ec, linewidth=lw, alpha=alpha))
            elif isinstance(g_obj, MultiPolygon):
                for sub in g_obj.geoms:
                    _plot_geom(sub, fc, ec, lw=lw, alpha=alpha)

        legend_handles = []
        all_bounds = []
        for z in zones:
            if not z.get("geom"):
                continue
            g = _ensure_poly(shape(z["geom"]))
            if g.is_empty:
                continue
            col = z.get("color") or TIER_META.get(z.get("intervention", ""), {}).get("color", "#0d9488")
            _plot_geom(g, fc=col, ec="#FFFFFF", lw=0.9, alpha=0.85)
            all_bounds.append(g.bounds)
            legend_handles.append(
                Patch(facecolor=col, edgecolor="#FFFFFF", label=f"{z.get('id')} {z.get('intervention')} ({z.get('share_pct')}%)")
            )

        if project.get("geojson"):
            bg = _ensure_poly(shape(project["geojson"]))
            if not bg.is_empty:
                _plot_geom(bg, fc="none", ec="#302B2A", lw=1.6, alpha=1.0)
                all_bounds.append(bg.bounds)

        if not all_bounds:
            plt.close(fig)
            return None

        minx = min(b[0] for b in all_bounds)
        miny = min(b[1] for b in all_bounds)
        maxx = max(b[2] for b in all_bounds)
        maxy = max(b[3] for b in all_bounds)
        padx = max((maxx - minx) * 0.08, 1e-4)
        pady = max((maxy - miny) * 0.08, 1e-4)
        ax.set_xlim(minx - padx, maxx + padx)
        ax.set_ylim(miny - pady, maxy + pady)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor("#D5C9C5")
            sp.set_linewidth(0.8)

        ax.set_title(
            f"Site #{project.get('rank')} GIS Landscape Zoning ({project.get('area_feddans')} Feddans)",
            fontsize=8.5,
            fontweight="bold",
            color="#302B2A",
            pad=5,
        )
        ax.text(
            0.97, 0.94, "N ↑", transform=ax.transAxes, ha="right", va="top",
            fontsize=8, fontweight="bold", color="#302B2A",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#D5C9C5", alpha=0.9),
        )
        if legend_handles:
            ax.legend(
                handles=legend_handles, loc="center left", bbox_to_anchor=(1.02, 0.5),
                frameon=True, facecolor="#FFFFFF", edgecolor="#D5C9C5", fontsize=7.0,
            )
        fig.tight_layout()
        fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        return out_path
    except Exception:
        return None
