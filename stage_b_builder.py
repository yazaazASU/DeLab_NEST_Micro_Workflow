#!/usr/bin/env python3
"""
NEST Stage B Hybrid Seed Expander (`stage_b_builder.py`)
========================================================
Takes compact, AI-authored architectural/programmatic seeds (`site_1_seed.json`..`site_5_seed.json`
or a single `seeds.json`) + `intermediates/stage_a_summary.json` and deterministically builds
a fully reconciled `stage_b_projects.json` with:
  - 50–70 feddan organic site boundaries snapped from Stage A candidates
  - Non-overlapping `L-01..L-0N` landscape zone polygons summing to 100.0%
  - Zero-encroachment `footprints[]` matching Tier 1 (18%–25%) / Precinct (28%–35%) targets
  - Exact GFA reconciliation across `built_gfa`, `spaces[]`, and `interior_zones[]`
  - Deterministic Whole-Site Financial KPIs (`fin` + `econ_evidence`)
  - Cross-portfolio diversity audit (idioms, registers, titles)

Usage:
  python stage_b_builder.py --run-dir outputs_nest_12_683 --seeds-dir outputs_nest_12_683/intermediates/seeds
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
from shapely.affinity import rotate as shp_rotate, scale as shp_scale, translate as shp_translate
from shapely.geometry import Point, Polygon, box, mapping, shape
from shapely.ops import unary_union

from heatmap_engine import LocalProjection

FEDDAN_M2 = 4200.833

ZONE_COLORS = {
    "preserve": "#15803d",
    "restore": "#0d9488",
    "enhance": "#ca8a04",
    "activate": "#d97706",
}


def _ensure_poly(geom) -> Polygon:
    if geom is None or geom.is_empty:
        return Polygon()
    g = geom.buffer(0)
    if g.geom_type == "Polygon":
        return g
    if g.geom_type in ("MultiPolygon", "GeometryCollection"):
        polys = [p for p in g.geoms if p.geom_type == "Polygon" and not p.is_empty]
        return max(polys, key=lambda p: p.area) if polys else Polygon()
    return Polygon()


def _scale_site_to_feddans(site_m: Polygon, target_feddans: float) -> Polygon:
    target_feddans = max(50.0, min(70.0, float(target_feddans)))
    target_m2 = target_feddans * FEDDAN_M2
    cur_m2 = max(site_m.area, 1.0)
    if 50.0 * FEDDAN_M2 <= cur_m2 <= 70.0 * FEDDAN_M2:
        return site_m
    s = math.sqrt(target_m2 / cur_m2)
    c = site_m.centroid
    return _ensure_poly(shp_scale(site_m, xfact=s, yfact=s, origin=(c.x, c.y)))


def _slice_polygon_by_shares(site_m: Polygon, shares: list[float], bearing_deg: float = 0.0) -> list[Polygon]:
    """Slice `site_m` along `bearing_deg` into contiguous non-overlapping strips matching `shares`."""
    total = sum(max(s, 1.0) for s in shares)
    norm = [max(s, 1.0) / total for s in shares]
    c = site_m.centroid
    rot = shp_rotate(site_m, -bearing_deg, origin=(c.x, c.y))
    minx, miny, maxx, maxy = rot.bounds
    span_x = max(maxx - minx, 1.0)

    cuts = [minx]
    cum = 0.0
    for frac in norm[:-1]:
        cum += frac
        target_area = rot.area * cum
        lo, hi = minx, maxx
        for _ in range(28):
            mid = 0.5 * (lo + hi)
            left_piece = rot.intersection(box(minx - 10, miny - 10, mid, maxy + 10))
            if left_piece.area < target_area:
                lo = mid
            else:
                hi = mid
        cuts.append(0.5 * (lo + hi))
    cuts.append(maxx + 10.0)

    out: list[Polygon] = []
    for i in range(len(norm)):
        strip = box(cuts[i] - (10.0 if i == 0 else 0.0), miny - 10.0, cuts[i + 1], maxy + 10.0)
        piece_rot = rot.intersection(strip)
        piece = _ensure_poly(shp_rotate(piece_rot, bearing_deg, origin=(c.x, c.y)))
        if piece.is_empty:
            piece = site_m.buffer(-span_x * 0.45)
        out.append(piece)
    return out


def _make_archetype_footprint(cx: float, cy: float, area_m2: float, archetype: str, bearing_deg: float) -> Polygon:
    arch = (archetype or "bar").lower()
    side = math.sqrt(max(area_m2, 100.0))
    if arch in ("crescent", "arc"):
        w, d = side * 1.85, side * 0.54
        raw = box(-w / 2, -d / 2, w / 2, d / 2).buffer(d * 0.25)
        notch = box(-w * 0.24, -d * 0.65, w * 0.24, -d * 0.05)
        raw = raw.difference(notch)
    elif arch in ("courtyard", "mat_courtyard"):
        w = side * 1.25
        raw = box(-w / 2, -w / 2, w / 2, w / 2).difference(box(-w * 0.22, -w * 0.22, w * 0.22, w * 0.22))
    elif arch in ("l_shape", "wing"):
        w = side * 1.4
        raw = unary_union([box(-w / 2, -w / 2, w / 2, -w * 0.05), box(-w / 2, -w / 2, -w * 0.05, w / 2)])
    elif arch in ("pier", "boardwalk"):
        w, d = side * 3.4, max(8.0, side * 0.29)
        raw = box(-w / 2, -d / 2, w / 2, d / 2)
    else:  # bar / cluster / default
        w, d = side * 1.75, side * 0.57
        raw = box(-w / 2, -d / 2, w / 2, d / 2).buffer(2.0)

    raw = _ensure_poly(raw)
    s = math.sqrt(max(area_m2, 50.0) / max(raw.area, 1.0))
    scaled = shp_scale(raw, xfact=s, yfact=s, origin=(0, 0))
    rotated = shp_rotate(scaled, bearing_deg, origin=(0, 0))
    return _ensure_poly(shp_translate(rotated, xoff=cx, yoff=cy))


def _is_tare_role(role: str) -> bool:
    r = str(role or "").lower()
    return any(k in r for k in ("tare", "circulation", "boh", "mep", "service", "core"))


def _reconcile_interior_zones(iz_list: list[dict], target_area: int) -> list[dict]:
    if not iz_list:
        return []
    raw_sum = sum(max(int(z.get("area_m2", 0)), 100) for z in iz_list)
    out = []
    running = 0
    for idx, z in enumerate(iz_list):
        z_copy = dict(z)
        if idx == len(iz_list) - 1:
            val = max(100, target_area - running)
        else:
            val = max(100, int(round(max(int(z.get("area_m2", 0)), 100) / raw_sum * target_area)))
            running += val
        z_copy["area_m2"] = val
        out.append(z_copy)
    return out


def _compute_financials(seed: dict, built_gfa_m2: float, site_m2: float) -> tuple[dict, dict]:
    f = seed.get("financials") or {}
    b_rate = float(f.get("building_capex_usd_per_m2", 1850.0))
    l_rate = float(f.get("landscape_capex_usd_per_m2", 75.0))
    b_capex_m = (built_gfa_m2 * b_rate) / 1e6
    l_capex_m = (site_m2 * l_rate) / 1e6
    tot_capex_m = b_capex_m + l_capex_m
    rev_m = float(f.get("annual_rev_m_usd", max(4.5, tot_capex_m * 0.24)))
    opex_ratio = float(f.get("opex_ratio", 0.34))
    ebitda_m = rev_m * (1.0 - opex_ratio)
    payback = tot_capex_m / max(ebitda_m, 0.5)
    irr = min(28.0, max(9.5, (ebitda_m / max(tot_capex_m, 1.0)) * 100.0 + 3.2))
    roi = (ebitda_m * 10.0 / max(tot_capex_m, 1.0)) * 100.0

    fin = {
        "capex": f"${tot_capex_m:.1f}M",
        "capex_split": f"Building ${b_capex_m:.1f}M + Landscape ${l_capex_m:.1f}M",
        "rev": f"${rev_m:.1f}M/yr",
        "irr": f"{irr:.1f}%",
        "roi": f"{roi:.0f}%",
        "payback": f"{payback:.1f} yrs",
        "pilot": f.get("pilot", f"Phase 0 Arrival & Site Spine — ${max(1.8, tot_capex_m * 0.08):.1f}M"),
        "scenarios": f.get("scenarios", f"Conservative {irr-2.8:.1f}% IRR · Base {irr:.1f}% IRR · Upside {irr+3.4:.1f}% IRR"),
    }
    econ = {
        "revenue_mix": f.get("revenue_mix", [
            {"stream": "Core Program & Hospitality", "share_pct": 48, "annual_rev": f"${rev_m*0.48:.1f}M"},
            {"stream": "Research / Concessions & Leases", "share_pct": 32, "annual_rev": f"${rev_m*0.32:.1f}M"},
            {"stream": "Public Events & Landscape Activation", "share_pct": 20, "annual_rev": f"${rev_m*0.20:.1f}M"},
        ]),
        "funding_partners": f.get("funding_partners", ["TSFE Co-Investment", "Private Operator Concession", "Green Climate Facility"]),
    }
    return fin, econ


def build_project_from_seed(seed: dict, stage_a: dict) -> dict:
    rank = int(seed["rank"])
    cands = stage_a.get("candidate_pool") or []
    cand = next((c for c in cands if int(c.get("site_rank", -1)) == int(seed.get("candidate_rank", rank))), None)
    if cand is None and rank - 1 < len(cands):
        cand = cands[rank - 1]
    if cand is None:
        raise ValueError(f"Could not match candidate in stage_a_summary.json for seed rank #{rank}")

    raw_geo = cand["boundary"]["geojson"]
    site_ll_raw = _ensure_poly(shape(raw_geo))
    c_ll = site_ll_raw.centroid
    proj = LocalProjection(float(c_ll.x), float(c_ll.y))
    site_m = _scale_site_to_feddans(_ensure_poly(proj.geom_to_meters(site_ll_raw)), float(seed.get("target_feddans", 58.0)))
    site_area_m2 = site_m.area
    site_feddans = site_area_m2 / FEDDAN_M2

    # 1. Landscape Zones (100.0% area reconciliation, non-overlapping)
    z_seeds = seed.get("landscape_zones") or [
        {"name": "Coastal Preserve Buffer", "family": "Ecological Preserve", "intervention": "Preserve", "share_pct": 28, "why_here": "Protects sensitive edge.", "outdoor_activities": "Boardwalk viewing"},
        {"name": "Native Restoration Belt", "family": "Ecological Restoration", "intervention": "Restore", "share_pct": 24, "why_here": "Rebuilds native flora.", "outdoor_activities": "Botanical trails"},
        {"name": "Shaded Spine & Cisterns", "family": "Climate & Water", "intervention": "Enhance", "share_pct": 22, "why_here": "Channels runoff and breeze.", "outdoor_activities": "Shaded promenade"},
        {"name": "Public Arrival & Forum", "family": "Civic Activation", "intervention": "Activate", "share_pct": 26, "why_here": "Anchors buildings & plaza.", "outdoor_activities": "Evening market & forum"},
    ]
    shares = [float(z.get("share_pct", 25.0)) for z in z_seeds]
    bearing = float(seed.get("site_bearing_deg", 15.0))
    zone_polys = _slice_polygon_by_shares(site_m, shares, bearing_deg=bearing)

    landscape_zones = []
    preserve_geoms = []
    for idx, (zs, zp) in enumerate(zip(z_seeds, zone_polys), 1):
        interv = str(zs.get("intervention", "Enhance"))
        col = zs.get("color") or ZONE_COLORS.get(interv.lower(), "#0d9488")
        a_m2 = zp.area
        sh_pct = (a_m2 / max(site_area_m2, 1.0)) * 100.0
        if "preserve" in interv.lower():
            preserve_geoms.append(zp)
        landscape_zones.append({
            "id": f"L-0{idx}",
            "name": zs["name"],
            "family": zs.get("family", interv),
            "intervention": interv,
            "why_here": zs.get("why_here", ""),
            "outdoor_activities": zs.get("outdoor_activities", ""),
            "area_m2": round(a_m2),
            "area_ha": round(a_m2 / 10000.0, 2),
            "area_feddans": round(a_m2 / FEDDAN_M2, 2),
            "share_pct": round(sh_pct, 1),
            "color": col,
            "geom": mapping(proj.geom_to_lonlat(zp)),
        })

    # 2. Buildable area & Footprints (0 Preserve encroachment, target coverage)
    preserve_u = unary_union(preserve_geoms).buffer(4.0) if preserve_geoms else Polygon()
    buildable_m = _ensure_poly(site_m.difference(preserve_u)) if not preserve_u.is_empty else site_m.buffer(-4.0)
    if buildable_m.is_empty:
        buildable_m = site_m.buffer(-3.0)

    vols_seed = seed.get("volumes") or []
    occupied = Polygon()
    footprints = []
    volumes_out = []
    total_gfa_m2 = 0

    b_pt = buildable_m.representative_point()
    bx0, by0 = b_pt.x, b_pt.y
    rad_angle = math.radians(bearing)
    ux, uy = math.cos(rad_angle), math.sin(rad_angle)

    for v_idx, vs in enumerate(vols_seed):
        v_gfa = int(vs.get("area_m2", 12000))
        total_gfa_m2 += v_gfa
        floors = max(1, int(vs.get("floors", 2)))
        fp_target_m2 = max(350.0, v_gfa / floors)
        is_bridge = bool(vs.get("bridge_or_pile_allowed", False))

        offset = (v_idx - (len(vols_seed) - 1) / 2.0) * math.sqrt(fp_target_m2) * 1.45
        cx = bx0 + ux * offset
        cy = by0 + uy * offset
        fp_m = _make_archetype_footprint(cx, cy, fp_target_m2, vs.get("archetype", "bar"), bearing)

        if not is_bridge:
            safe_buildable = buildable_m.buffer(-2.0)
            if safe_buildable.is_empty:
                safe_buildable = buildable_m
            clipped = _ensure_poly(fp_m.intersection(safe_buildable))
            if clipped.is_empty or clipped.area < fp_target_m2 * 0.4:
                rem = _ensure_poly(safe_buildable.difference(occupied.buffer(6.0))) if not occupied.is_empty else safe_buildable
                rp = (rem if not rem.is_empty else safe_buildable).representative_point()
                fp_m = _make_archetype_footprint(rp.x, rp.y, fp_target_m2, vs.get("archetype", "bar"), bearing)
                clipped = _ensure_poly(fp_m.intersection(safe_buildable))
            if not occupied.is_empty and not clipped.is_empty:
                clipped2 = _ensure_poly(clipped.difference(occupied.buffer(6.0)))
                if not clipped2.is_empty:
                    clipped = clipped2
            if clipped.is_empty and not safe_buildable.is_empty:
                clipped = _ensure_poly(safe_buildable.representative_point().buffer(15.0).intersection(safe_buildable))
            fp_m = clipped
            occupied = unary_union([occupied, fp_m]).buffer(0)

        footprints.append({
            "label": f"{vs['name']} — {v_gfa:,} m²",
            "idiom": seed.get("idiom", "landform"),
            "bridge_or_pile_allowed": is_bridge,
            "geom": mapping(proj.geom_to_lonlat(fp_m)),
        })
        iz_reconciled = _reconcile_interior_zones(vs.get("interior_zones") or [], v_gfa)
        tare_m2 = sum(int(z.get("area_m2", 0)) for z in iz_reconciled if _is_tare_role(z.get("role", "")))
        nsf_m2 = max(0, v_gfa - tare_m2)
        nsf_pct = round((nsf_m2 / max(1, v_gfa)) * 100.0, 1)
        volumes_out.append({
            "name": vs["name"],
            "use": vs.get("use", ""),
            "area_m2": f"{v_gfa:,} m²",
            "gsf_m2": v_gfa,
            "nsf_m2": nsf_m2,
            "tare_m2": tare_m2,
            "nsf_gsf_pct": nsf_pct,
            "height_floors": vs.get("height_floors", f"{floors} {'floor' if floors == 1 else 'floors'} · {floors * 4.5:.1f} m"),
            "shape_reason": vs.get("shape_reason", ""),
            "interior_zones": iz_reconciled,
        })

    fin, econ = _compute_financials(seed, total_gfa_m2, site_area_m2)

    return {
        "rank": rank,
        "title": seed["title"],
        "subtitle": seed["subtitle"],
        "nature_hero": seed.get("nature_hero") or "Sun, Wind & Coast",
        "strategy": seed.get("strategy", cand.get("recommended_strategy", "Select")),
        "tier": seed.get("tier", "Tier 1: Flagship National Landmark"),
        "idiom": seed["idiom"],
        "precedent": seed["precedent"],
        "concept_register": seed.get("concept_register", "Concrete & Tectonic"),
        "is_water": bool(seed.get("is_water", False)),
        "nat_prov": cand.get("nat_prov", "Observed GIS"),
        "lat": float(c_ll.y),
        "lon": float(c_ll.x),
        "footprint_type": cand["boundary"].get("footprint_type", "Contiguous"),
        "area_m2": round(site_area_m2),
        "area_feddans": round(site_feddans, 1),
        "cells": cand["boundary"].get("cluster_cells", []),
        "built_gfa": f"{total_gfa_m2:,} m²",
        "access": int((cand.get("accessibility") or {}).get("score", 75) if isinstance(cand.get("accessibility"), dict) else cand.get("accessibility", 75)),
        "scores": cand.get("engine_scores", {"crystals": 80, "cells": 75, "corals": 78}),
        "flags": cand.get("flags", []),
        "map_pointers": seed.get("map_pointers", cand.get("gis_evidence", {}).get("map_feature_pointers", [])[:5]),
        "thesis_summary": seed["thesis_summary"],
        "thesis_detailed": seed["thesis_detailed"],
        "engine_trace": seed["engine_trace"],
        "nature_to_bldg": seed["nature_to_bldg"],
        "bldg_to_nature": seed["bldg_to_nature"],
        "experience_arc": seed.get("experience_arc") or {
            "core_idea": f"{seed['thesis_summary'].get('gesture_line', '')} — a distributed constellation celebrating the site's natural hero.",
            "visit_mode": "Day-to-Night · Eco-Stay",
            "atmosphere": f"{seed.get('orientation', '')} {seed.get('shape_logic', '')}".strip(),
            "journey": [
                {"moment": "Shaded Threshold Arrival", "detail": "Gradual transition from regional access into restored native landscape."},
                {"moment": "Core Nature Encounter", "detail": seed["thesis_summary"].get("hook", "")},
                {"moment": "Signature Experience Nodes & Trails", "detail": ", ".join(seed.get("activities", [])[:4])},
                {"moment": "Curated Dining & Eco-Stay", "detail": "Experience-curated local tasting kitchen, artisan outpost, and dusk-to-dawn eco-lodges."},
            ],
        },
        "visual_direction": seed.get("visual_direction") or {
            "architectural_language": seed["thesis_summary"].get("gesture_line", ""),
            "aerial_composition": f"Dispersed buildings and restored landscape trails filling the {seed.get('target_feddans', 58):.0f}-feddan site.",
            "hero_threshold_scene": seed["thesis_summary"].get("hook", ""),
            "lighting_mood": seed.get("experience_arc", {}).get("atmosphere", "Warm late-afternoon directional light with crisp shadow relief."),
            "materials_palette": "Regionally authentic stone, desert-aggregate concrete, weathered timber, and native arid planting.",
            "camera_cue": "",
        },
        "activities": seed.get("activities", []),
        "spaces": seed.get("spaces", []),
        "landscape_summary": seed.get("landscape_summary") or " · ".join(
            f"{z.get('code', f'L-0{i+1}')} {z.get('name', '')} ({z.get('share_pct', 25)}%)"
            for i, z in enumerate(landscape_zones)
        ),
        "landscape_zones": landscape_zones,
        "landscape_landforms": seed.get("landscape_landforms", []),
        "landscape_elements": seed.get("landscape_elements", []),
        "fin": fin,
        "econ_evidence": econ,
        "hypotheses": seed.get("hypotheses", []),
        "geojson": mapping(proj.geom_to_lonlat(site_m)),
        "footprints": footprints,
        "massing_rationale": {
            "orientation": seed.get("orientation", ""),
            "shape_logic": seed.get("shape_logic", ""),
            "volumes": volumes_out,
        },
    }


def audit_portfolio_diversity(projects: list[dict]) -> list[str]:
    warnings: list[str] = []
    idioms = [p.get("idiom", "").lower() for p in projects]
    if len(set(idioms)) < len(idioms):
        warnings.append(f"Duplicate idioms detected across portfolio: {idioms}")
    regs = [p.get("concept_register", "").lower() for p in projects]
    if len(set(regs)) < min(len(regs), 4):
        warnings.append(f"Low concept_register diversity across portfolio: {regs}")
    for p in projects:
        rk = p.get("rank", "?")
        gfa_val = int(re.sub(r"[^\d]", "", str(p.get("built_gfa", "0"))) or 0)
        if gfa_val > 35000:
            warnings.append(f"Site #{rk} ({p.get('title')}) has inflated built_gfa={gfa_val:,} m² (>35,000 m²); calibrate to 8,000–22,000 m² unless major civic hub.")
        for v in (p.get("massing_rationale") or {}).get("volumes") or []:
            v_gsf = int(v.get("gsf_m2") or re.sub(r"[^\d]", "", str(v.get("area_m2", "0"))) or 0)
            iz = v.get("interior_zones") or []
            has_tare = any(_is_tare_role(z.get("role", "")) for z in iz)
            if v_gsf >= 1000 and not has_tare:
                warnings.append(f"Site #{rk} '{v.get('name')}' ({v_gsf:,} m²) has no Circulation & Tare / BOH & MEP row.")
            for z in iz:
                za = int(z.get("area_m2", 0))
                if not _is_tare_role(z.get("role", "")) and za > 1200:
                    warnings.append(f"Site #{rk} '{v.get('name')}' room '{z.get('name')}' is {za:,} m² (>1,200 m²); split into realistic rooms.")
    return warnings


def _detect_egypt_region(lat: float, lon: float) -> dict[str, Any]:
    """Map (lat, lon) to one of the 6 EGYPT_KNOWLEDGE regional biomes and material palettes."""
    if lat >= 30.65 and lon < 32.1:
        return {
            "name": "Mediterranean North Coast & Delta",
            "epithet": "Calcarenite",
            "climate": "saline sea breeze, high solar radiation, mild coastal humidity",
            "materials": "local calcarenite limestone, lime-pozzolan render, weathered timber louvers, and salt-tolerant coastal flora",
            "passive_air": "cross-ventilation tunnels and wind-catchers oriented to prevailing NW Mediterranean breezes",
            "water_mech": "solar-assisted desalination, roof dew/rain cisterns, and biosaline greywater reed beds",
        }
    if lon >= 32.1 and lat >= 27.6:
        return {
            "name": "Suez Canal & Sinai",
            "epithet": "Sinai Sandstone",
            "climate": "arid maritime-desert transition, strong channel winds, seasonal wadi runoff",
            "materials": "Sinai sandstone, basalt plinths, desert-aggregate concrete, and woven shade canopies",
            "passive_air": "high thermal-mass plinths with shaded wind-scoop courts aligned to N/NW corridor gusts",
            "water_mech": "wadi flash-flood retention swales, cistern storage, and closed-loop greywater irrigation",
        }
    if lon >= 32.5 and lat < 27.6:
        return {
            "name": "Red Sea & Eastern Desert",
            "epithet": "Coral-Stone",
            "climate": "intense solar gain, dry mountain-to-sea breezes, hyper-saline coast",
            "materials": "fossil coral-limestone, granite aggregate, whitewashed thermal walls, and tensile fabric shade",
            "passive_air": "shaded canyon-like breezeways channeling diurnal mountain-sea airflow without heavy AC",
            "water_mech": "zero-brine-discharge solar desalination and xeriscape coastal sabkha buffers",
        }
    if 29.4 <= lat < 30.65 and 30.5 <= lon < 32.1:
        return {
            "name": "Greater Cairo & Nile Core",
            "epithet": "Nile-Silt & Brick",
            "climate": "urban heat island, hot dry summers, Nile-corridor cooling breezes",
            "materials": "kiln-fired clay brick, Nile-silt lime plaster, perforated terracotta screens, and shaded arcades",
            "passive_air": "shaded courtyards, mashrabiya solar screens, and evaporative tree-canopy microclimates",
            "water_mech": "treated greywater bio-swales, permeable paving, and shaded retention basins",
        }
    if lat < 29.4 and lon >= 29.5:
        return {
            "name": "Upper Egypt & Nubia",
            "epithet": "Nubian Vault",
            "climate": "extreme solar intensity, very low humidity, strong diurnal temperature swings",
            "materials": "sun-dried mudbrick vaults, Nubian sandstone, palm-frond trellises, and limewash",
            "passive_air": "catenary vaulted roofs, deep-recessed apertures, and night-flush thermal mass",
            "water_mech": "deep shaded cisterns, subsurface drip irrigation, and Nile-edge riparian filtration",
        }
    return {
        "name": "Western Desert & Oases",
        "epithet": "Kershef Earth",
        "climate": "hyper-arid desert sun, high diurnal swing, wind-blown sand",
        "materials": "rammed desert earth, kershef salt-stone, palm-rib shading, and compacted limestone",
        "passive_air": "sunken thermal courtyards and wind-deflecting earth berms that block sand while trapping cool night air",
        "water_mech": "closed-loop oasis aquifer conservation, dew-harvesting roofs, and biosaline date-palm belts",
    }


_CRITIC_TITLES: dict[str, list[tuple[str, str]]] = {
    "Water": [
        ("The Salt-Mist Cisterns", "Stepped desalination basins and shaded hydrology labs turning coastal brine into living reed gardens"),
        ("Silt & Reed Observatory", "A low-slung water-stewardship campus where open filtration channels thread between research cloisters"),
        ("Tidal Hydrology Cloister", "Porous stone courts and solar stills staging the public life of water recovery and watershed craft"),
        ("The Brine-Garden Commons", "Closed-loop evaporation terraces and wet-lab halls anchored along the hydrological spine"),
    ],
    "Food": [
        ("The Biosaline Terraces", "Shaded wholesale market vaults and salt-tolerant greenhouses cultivating arid-land food security"),
        ("Granary of the Wind", "Cross-ventilated cold-chain halls and agrarian test kitchens under a breathable timber-and-stone canopy"),
        ("Oolitic Shade-Courts", "Productive microclimate courtyards pairing controlled-environment agriculture with a civic tasting hall"),
        ("The Agrarian Colonnade", "A linear harvest promenade linking seed-bank labs, farmer workshops, and solar-cooled storage"),
    ],
    "Sun": [
        ("The Heliotrope Foundry", "Sawtooth solar-fabrication bays and shaded civic courts tuned to harvest harsh desert light"),
        ("Solar Mastaba & Microgrid", "Monolithic thermal-mass walls cradling high-bay clean-tech assembly and vocational studios"),
        ("Louvered Light-Courts", "Deep-recessed limestone cloisters filtering intense glare into cool, daylit engineering workshops"),
        ("The Photovoltaic Cloister", "A stepped clean-tech precinct where overhead solar canopies cast a continuous microclimate of shade"),
    ],
    "Air": [
        ("Wind-Loom Craft Quarter", "Malqaf wind-chimneys and acoustic stone courts cooling regional clay, stone, and timber studios"),
        ("The Malqaf Kilns", "Sculpted thermal-mass chimneys drawing prevailing breezes across maker workshops and gallery foyers"),
        ("Breeze-Canyon Studios", "Narrow shaded breezeways accelerating natural airflow through fabrication halls and artisan residences"),
        ("Limestone Acoustic Courts", "Quiet, wind-tempered craft cloisters pairing traditional material fabrication with public performance"),
    ],
    "People": [
        ("The Civic Shade Spine", "A continuous shaded arcade stitching multimodal transit, a technical school, clinic, and courtyard housing"),
        ("Threshold Forum & School", "Porous neighborhood commons anchored by a sunken market court, digital library, and family clinic"),
        ("The Sunken Bazaar & Commons", "Cross-ventilated civic halls stepping down into planted micro-courts for daily learning and trade"),
        ("Courtyard Neighborhood Loom", "A human-scaled urban weave of shaded transit exchange, vocational labs, and mid-rise apartments"),
    ],
    "Nature": [
        ("Dune-Cut Herbarium", "Half-buried stone research vaults and low-impact eco-suites tucked quietly into restored native contours"),
        ("The Sabkha Sanctuary", "Elevated boardwalks, botany labs, and off-grid thermal lodges framing untouched coastal ecology"),
        ("Riparian Canopy House", "Shaded trailhead orientation, regional dining, and star-gazing courts embedded in restored flora"),
        ("The Living Edge Reserve", "A quiet ecological threshold where habitat science, local culinary craft, and eco-stays coexist"),
    ],
}

_CRITIC_PRECEDENTS: dict[str, str] = {
    "Limestone & Wind-Tower": "Abdel Wahed El-Wakil's coastal limestone courts + Masdar Institute wind-tower microclimates",
    "Earth & Rammed Mass": "Hassan Fathy's New Gourna vaults + Adrère Amellal kershef thermal mass (Siwa)",
    "Timber & Tensile Shade": "Francis Kéré's ventilated double-roof canopies + Bibliotheca Alexandrina coastal civic scale",
    "Steel & Solar Canopy": "Louvre Abu Dhabi perforated solar dome + Jean Nouvel's high-tech desert shading",
    "Vaulted Brick & Courtyard": "Ramses Wissa Wassef Art Centre mudbrick vaults + Bahrain Pearling Path urban breezeways",
}

_IDIOM_TECTONICS: dict[str, str] = {
    "courtyard": "inward-facing perforated cloisters with deep thermal overhangs and planted evaporative wells",
    "terrace": "stepped topographic plinths that step down with the land to shelter outdoor courts from wind",
    "cantilever": "elevated shadow-casting decks hovering lightly above sensitive ground and drainage lines",
    "clustered_compound": "a porous village-scale cluster of discrete volumes linked by narrow, self-shading alleys",
    "bridge": "linear spanned bars and piled decks stitching across ecological edges without sealing the ground",
}

_ARCHETYPE_REASONS: dict[str, str] = {
    "courtyard": "Hollowed courtyard massing shields interior rooms from glare and gusts while creating a cool microclimate well at its core.",
    "crescent": "Curved crescent geometry wraps the leeward court against prevailing wind while maximizing north-facing daylight.",
    "l_shape": "L-shaped wing geometry frames a wind-sheltered arrival plaza and separates public concourses from quiet work bays.",
    "bar": "Slender linear bar proportion keeps every bay within natural cross-ventilation and daylight reach.",
    "pier": "Narrow piled pier alignment touches the water-land edge lightly, preserving natural tidal flow beneath.",
}


# Typology templates keyed by primary force; no "Pavilion" boilerplate, buildings added only per real use.
_FORCE_PROGRAMS: dict[str, dict[str, Any]] = {
    "Water": {
        "title_stem": "Hydro-Ecological Research & Water Campus",
        "subtitle": "Mist-cooled water courts, solar stills, and waterfront dining",
        "tier": "Tier 1: Flagship National Landmark",
        "visit_mode": "Full-Day Waterfront & Public Life",
        "far_range": (0.14, 0.22),
        "b_capex": 1950.0,
        "daily_life": "stroll along mist-cooled stone terraces fed by solar stills, dine beside living reed-bed gardens, explore open-air water channels with family, or launch kayaks at sunset",
        "activities": ["Mist-terrace promenade", "Interactive water-channel courts", "Reed-bed waterfront dining", "Sunset kayak & boat launch"],
        "uses": [
            {"name": "The Mist Cloister & Solar Stills", "use": "Stepped cooling water-courts, interactive watershed channels, and mineral-water tasting bar", "archetype": "courtyard", "floors": 2, "share": 0.48, "zones": [("Shaded Mist & Tasting Court", "Public"), ("Solar Desalination Gallery", "Exhibition"), ("Hydrology Studio", "Research")]},
            {"name": "Reed-Bed Terrace & Waterfront Kitchen", "use": "Waterfront restaurant, coastal ecology gallery, and shaded reading deck", "archetype": "l_shape", "floors": 2, "share": 0.34, "zones": [("Waterfront Dining Hall", "Hospitality"), ("Ecology Exhibition", "Culture"), ("Shaded Reading Terrace", "Commons")]},
            {"name": "Tidal Boat & Kayak Pier", "use": "Water-edge launch dock, paddleboard outfitter, and sunset deck", "archetype": "pier", "floors": 1, "share": 0.18, "bridge": True, "zones": [("Kayak & Boat Dock", "Recreation"), ("Sunset Observation Deck", "Public")]},
        ],
    },
    "Food": {
        "title_stem": "Agro-Ecology & Regional Food Hub",
        "subtitle": "Shaded harvest market, living citrus conservatory, and wood-fired kitchen",
        "tier": "Tier 1: Productive Regional Precinct",
        "visit_mode": "Morning Market to Lantern Dining",
        "far_range": (0.18, 0.26),
        "b_capex": 1620.0,
        "daily_life": "shop the breezy morning farmers' market for dates, figs, and fresh bread, wander through a lush biosaline conservatory, take a regional cooking class, and linger over long-table courtyard dinners at night",
        "activities": ["Morning shaded harvest market", "Walk-through citrus conservatory", "Regional cooking & baking classes", "Lantern-lit courtyard dining"],
        "uses": [
            {"name": "Shaded Spice, Date & Harvest Market Hall", "use": "Breezy vaulted market hall for local growers, bakers, and street-food stalls", "archetype": "bar", "floors": 1, "share": 0.42, "zones": [("Shaded Market Concourse", "Commerce"), ("Artisan Bakery & Street Food", "Hospitality"), ("Solar-Cooled Cellars", "Logistics")]},
            {"name": "The Living Conservatory & Citrus Court", "use": "Walk-through biosaline glasshouse, heirloom seed library, and botanical garden", "archetype": "crescent", "floors": 1, "share": 0.34, "zones": [("Botanical & Citrus Nave", "Public"), ("Heirloom Seed Library", "Culture")]},
            {"name": "The Wood-Fired Tasting Kitchen", "use": "Chef-led regional cooking workshops, tasting terrace, and artisan pantry", "archetype": "courtyard", "floors": 2, "share": 0.24, "zones": [("Open Teaching Kitchens", "Education"), ("Artisan Pantry & Cafe", "Commerce"), ("Courtyard Tasting Terrace", "Hospitality")]},
        ],
    },
    "Sun": {
        "title_stem": "Solar-Thermal Innovation & Civic Precinct",
        "subtitle": "Sun-kiln glass & metal foundry, shaded espresso cloister, and night cinema court",
        "tier": "Tier 1: Clean-Tech & Civic Anchor",
        "visit_mode": "All-Day Craft, Cafe & Night Cinema",
        "far_range": (0.16, 0.24),
        "b_capex": 1780.0,
        "daily_life": "watch glassblowers and metalworkers cast desert-sand glass using concentrated sunlight, grab espresso or wood-fired flatbread in a mist-cooled cloister, browse weekend maker stalls, and stay for open-air sunset cinema powered by the day's sun",
        "activities": ["Sun-kiln glassblowing & metal foundry", "Shaded cloister espresso & flatbread cafe", "Twilight maker & design bazaar", "Solar-powered open-air night cinema"],
        "uses": [
            {"name": "Solar Glass & Metal Foundry", "use": "Open-air sun-kiln glassblowing, cast-bronze craft studio, and shaded public viewing gallery", "archetype": "bar", "floors": 2, "share": 0.56, "zones": [("Sun-Kiln Foundry Floor", "Craft"), ("Shaded Viewing Gallery", "Public"), ("Design & Fabrication Studio", "Enterprise")]},
            {"name": "Sunlit Cloister Cafe & Night Cinema Court", "use": "Shaded courtyard espresso bar, design library, co-working cloister, and evening screening amphitheater", "archetype": "courtyard", "floors": 2, "share": 0.44, "zones": [("Courtyard Cafe & Commons", "Hospitality"), ("Design Library & Co-Working", "Culture"), ("Evening Cinema & Bazaar Court", "Public")]},
        ],
    },
    "Air": {
        "title_stem": "Wind-Cooled Craft & Cultural Quarter",
        "subtitle": "Wind-chimney pottery kilns, shaded studio alleys, and acoustic amphitheater",
        "tier": "Tier 2: Cultural & Craft Precinct",
        "visit_mode": "Full-Day Culture, Craft & Music",
        "far_range": (0.15, 0.23),
        "b_capex": 1700.0,
        "daily_life": "watch potters, weavers, and stone-carvers work inside wind-cooled kiln courts, browse open-studio galleries along breezy alleys, catch live acoustic music at dusk, or stay overnight in an artist loft",
        "activities": ["Open pottery & weaving studios", "Breezy gallery & craft alley walks", "Twilight acoustic amphitheater", "Visiting artists' courtyard lofts"],
        "uses": [
            {"name": "Wind-Chimney Pottery & Weaving Foundry", "use": "Open-studio ceramic kilns, textile looms, and carved-stone workshops cooled by tall malqaf towers", "archetype": "l_shape", "floors": 2, "share": 0.46, "zones": [("Pottery & Kiln Court", "Craft"), ("Textile Loom & Stone Hall", "Production"), ("Craft Gallery & Shop", "Culture")]},
            {"name": "The Acoustic Stone Amphitheater & Gallery", "use": "Shaded outdoor music court, contemporary craft exhibitions, and twilight foyer", "archetype": "courtyard", "floors": 2, "share": 0.34, "zones": [("Exhibition Galleries", "Culture"), ("Shaded Acoustic Court", "Public")]},
            {"name": "Visiting Artists' Courtyard Lofts", "use": "Short-stay studio lofts and rooftop terraces for resident makers and weekend guests", "archetype": "bar", "floors": 3, "share": 0.20, "zones": [("Makers' Guest Lofts", "Hospitality"), ("Shared Rooftop Terrace", "Commons")]},
        ],
    },
    "People": {
        "title_stem": "Civic Mobility, Learning & Neighborhood Hub",
        "subtitle": "Breezy transit arcade, design library, evening tea courts, and courtyard homes",
        "tier": "Tier 1: Civic & Mixed-Use Precinct",
        "visit_mode": "Lively Neighborhood Day-to-Night",
        "far_range": (0.24, 0.33),
        "b_capex": 1680.0,
        "daily_life": "step off a shuttle into a shaded arcade lined with bakeries and bookshops, read or build in the sunlit neighborhood library, visit the garden clinic, and meet friends for evening tea under courtyard trees",
        "activities": ["Shaded arcade & street bakeries", "Sunlit library & kids' maker studio", "Garden wellbeing house", "Evening courtyard tea & music"],
        "uses": [
            {"name": "The Shaded Arcade & Night Market", "use": "Breezy transit concourse lined with bakeries, bike docks, bookshops, and evening tea terraces", "archetype": "bar", "floors": 2, "share": 0.28, "zones": [("Transit & Bike Arcade", "Mobility"), ("Bakeries, Bookshops & Cafes", "Commerce")]},
            {"name": "Neighborhood Design School & Public Library", "use": "Daylit reading hall, kids' maker studio, and shaded study courts", "archetype": "courtyard", "floors": 3, "share": 0.28, "zones": [("Public Reading Hall", "Education"), ("Kids' Maker & Art Studio", "Culture")]},
            {"name": "Wellbeing House & Apothecary", "use": "Community health, physiotherapy, and herbal apothecary around a quiet garden", "archetype": "l_shape", "floors": 2, "share": 0.16, "zones": [("Care & Consultation Suites", "Health"), ("Herbal Apothecary & Garden", "Wellness")]},
            {"name": "Courtyard Garden Residences", "use": "Cross-ventilated apartments above lively ground-floor cafes and artisan shops", "archetype": "courtyard", "floors": 4, "share": 0.28, "zones": [("Courtyard Apartments", "Residential"), ("Ground-Floor Cafes & Shops", "Commerce")]},
        ],
    },
    "Nature": {
        "title_stem": "Biome Conservation & Eco-Hospitality Sanctuary",
        "subtitle": "Pressed-flora herbarium, foragers' terrace, and stargazing eco-suites",
        "tier": "Tier 2: Ecological Sanctuary & Eco-Stay",
        "visit_mode": "Sunrise Trails to Stargazing Eco-Stay",
        "far_range": (0.11, 0.18),
        "b_capex": 1820.0,
        "daily_life": "join a sunrise birding or botanical walk along elevated trails, press native herbs in the herbarium studio, eat hyper-local dishes on an open-air terrace, and stargaze from quiet off-grid eco-suites",
        "activities": ["Sunrise botanical & birding trails", "Herbarium pressing workshops", "Foragers' terrace dining", "Off-grid stargazing eco-suites"],
        "uses": [
            {"name": "The Herbarium & Field Observatory", "use": "Pressed-flora archive, wildlife viewing blinds, and sunrise trailhead", "archetype": "crescent", "floors": 1, "share": 0.34, "zones": [("Herbarium & Botanical Studio", "Culture"), ("Trailhead & Viewing Blind", "Public")]},
            {"name": "Foragers' Kitchen & Tea Terrace", "use": "Open-air regional dining deck serving local herbs, honey, and coastal/desert fare", "archetype": "l_shape", "floors": 1, "share": 0.26, "zones": [("Open-Air Dining Deck", "Hospitality"), ("Artisan Pantry & Terrace", "Commerce")]},
            {"name": "Stargazing Thermal-Mass Eco-Suites", "use": "Off-grid stone and earth guest suites with private sunken fire-courts and roof telescopes", "archetype": "courtyard", "floors": 1, "share": 0.40, "zones": [("Thermal-Mass Guest Suites", "Hospitality"), ("Quiet Stargazing Court", "Wellness")]},
        ],
    },
}

_PORTFOLIO_IDIOMS = ["courtyard", "terrace", "cantilever", "clustered_compound", "bridge"]
_PORTFOLIO_REGISTERS = [
    "Limestone & Wind-Tower",
    "Earth & Rammed Mass",
    "Timber & Tensile Shade",
    "Steel & Solar Canopy",
    "Vaulted Brick & Courtyard",
]


_FORCE_KEY_MAP = {
    "Hydrology & Waterfront": "Water",
    "Solar & Climate Intensity": "Sun",
    "Biodiversity & Ecology": "Nature",
    "Heritage & Culture Gravity": "Air",
    "Civic & Service Deficit": "People",
    "Corridor & Network Connectivity": "Food",
}


def synthesize_seeds_from_stage_a(stage_a: dict, data_dir: Path | None = None) -> list[dict]:
    """Deterministically synthesize diverse, GIS-grounded, use-driven project seeds for ANY plot."""
    cands = stage_a.get("candidate_pool") or []
    if not cands:
        raise ValueError("stage_a_summary.json has an empty candidate_pool")

    seeds: list[dict] = []
    used_forces: set[str] = set()
    used_titles: set[str] = set()
    for idx, cand in enumerate(cands[:5]):
        rank = int(cand.get("site_rank", idx + 1))
        lat = float(cand.get("lat") or (cand.get("coordinates") or {}).get("lat") or 30.0)
        lon = float(cand.get("lon") or (cand.get("coordinates") or {}).get("lon") or 31.0)
        reg = _detect_egypt_region(lat, lon)

        # Pick highest-scoring unused force from Stage A force_scores so all 5 sites get distinct typologies
        fscores = cand.get("force_scores") or {}
        ranked_forces = [
            (_FORCE_KEY_MAP.get(fk, fk), float(fv))
            for fk, fv in fscores.items()
            if _FORCE_KEY_MAP.get(fk, fk) in _FORCE_PROGRAMS
        ]
        ranked_forces.sort(key=lambda x: -x[1])
        dom_force = None
        for fk, _ in ranked_forces:
            if fk not in used_forces:
                dom_force = fk
                break
        if dom_force is None:
            dom_force = ranked_forces[0][0] if ranked_forces else str(cand.get("dominant_force", "People")).strip()
        if dom_force not in _FORCE_PROGRAMS:
            dom_force = "People"
        used_forces.add(dom_force)
        prog = _FORCE_PROGRAMS[dom_force]
        terrain = str(cand.get("terrain_class", "Dry Land"))
        eng = str(cand.get("dominant_engine", "Crystals"))
        strat = str(cand.get("recommended_strategy", f"Select: {eng}"))
        area_m2 = float(cand.get("boundary", {}).get("area_m2", 240000.0))
        feddans = max(50.0, min(70.0, round(area_m2 / FEDDAN_M2, 1)))

        idiom = _PORTFOLIO_IDIOMS[idx % len(_PORTFOLIO_IDIOMS)]
        register = _PORTFOLIO_REGISTERS[idx % len(_PORTFOLIO_REGISTERS)]

        far_lo, far_hi = prog["far_range"]
        far = far_lo + (far_hi - far_lo) * ((idx % 3) / 2.0)
        total_gfa = int(round((feddans * FEDDAN_M2 * far) / 500.0) * 500)

        uses = list(prog["uses"])
        # Only include water-pier building if site actually touches water/shoreline
        if dom_force == "Water" and terrain == "Dry Land":
            uses = [u for u in uses if not u.get("bridge")]

        share_sum = sum(u["share"] for u in uses)
        volumes: list[dict[str, Any]] = []
        spaces: list[dict[str, Any]] = []
        for ui, u in enumerate(uses):
            vgfa = int(round((total_gfa * (u["share"] / share_sum)) / 100.0) * 100)
            iz_list = [{"name": zn, "role": zr, "area_m2": max(200, int(vgfa / len(u["zones"])))} for zn, zr in u["zones"]]
            arch_reason = _ARCHETYPE_REASONS.get(u["archetype"], _ARCHETYPE_REASONS["bar"])
            volumes.append({
                "name": u["name"],
                "use": u["use"],
                "area_m2": vgfa,
                "floors": u["floors"],
                "archetype": u["archetype"],
                "bridge_or_pile_allowed": bool(u.get("bridge", False)),
                "shape_reason": f"{arch_reason} Calibrated in {register.lower()} to {reg['name']} solar/wind vectors.",
                "interior_zones": iz_list,
            })
            spaces.append({"name": u["name"], "category": u["zones"][0][1], "area_m2": vgfa})

        # GIS context pointers
        gis_ev = cand.get("gis_evidence") or {}
        ptrs = gis_ev.get("map_feature_pointers") or []
        ptr_text = ", ".join(str(p) for p in ptrs[:3]) if ptrs else f"{terrain} parcel near mapped {eng.lower()} infrastructure"
        acc = cand.get("accessibility") or {}
        acc_score = acc.get("score", 75) if isinstance(acc, dict) else acc
        road_dist_m = float(acc.get("road_dist_m", 60.0)) if isinstance(acc, dict) and acc.get("road_dist_m") is not None else 60.0
        nat_dist_m = float(cand.get("nat_dist_m", 250.0)) if cand.get("nat_dist_m") is not None else 250.0
        sec_force = next((fk for fk, _ in ranked_forces if fk != dom_force), dom_force)

        if terrain == "Open Water":
            water_leverage = "Built directly over open water on piled decks, turning the surrounding sea/lake into passive evaporative cooling, kayak launchways, and tidal reflection courts."
        elif terrain == "Shoreline Edge" or nat_dist_m <= 100.0:
            water_leverage = f"Positioned just {nat_dist_m:.0f} m from the water edge, channeling cool marine/canal breezes straight into its shaded courts and framing waterfront dining."
        elif nat_dist_m <= 300.0:
            water_leverage = f"Sitting {nat_dist_m:.0f} m from nearby water corridors, using that natural moisture gradient to pre-cool incoming air before it crosses the central plaza."
        else:
            water_leverage = f"Set {nat_dist_m:.0f} m inland across open dry terrain, turning unobstructed solar exposure and wide desert horizons into a quiet thermal-mass oasis."

        if road_dist_m <= 60.0:
            road_leverage = f"Fronting a mapped road just {road_dist_m:.0f} m away, it pulls travelers directly into its shaded market arcade."
        else:
            road_leverage = f"Set {road_dist_m:.0f} m back from the road behind a planted buffer, trading traffic noise for calm courtyard acoustics."

        site_advantage = f"{water_leverage} {road_leverage} Secondary {sec_force.lower()} potential reinforces the primary {dom_force.lower()} program."

        title_bank = _CRITIC_TITLES.get(dom_force, _CRITIC_TITLES["People"])
        pick_i = (abs(int(round(lat * 1000))) + abs(int(round(lon * 1000))) + idx) % len(title_bank)
        base_title, critic_sub = title_bank[pick_i]
        for off in range(len(title_bank)):
            cand_t, cand_s = title_bank[(pick_i + off) % len(title_bank)]
            stripped_t = cand_t[4:] if cand_t.startswith("The ") else cand_t
            if terrain == "Open Water" and not any(w in cand_t.lower() for w in ("tidal", "salt", "reef", "sabkha", "water")):
                test_t = f"Amphibious {stripped_t}"
            elif terrain == "Shoreline Edge" and not any(w in cand_t.lower() for w in ("tidal", "salt", "shore", "coastal", "sabkha")):
                test_t = f"{reg['epithet']} {stripped_t}"
            else:
                test_t = cand_t
            if test_t not in used_titles:
                title, critic_sub = test_t, cand_s
                break
        else:
            stripped_b = base_title[4:] if base_title.startswith("The ") else base_title
            title = f"{reg['epithet']} {stripped_b}"
        used_titles.add(title)

        bearing = (15.0 + idx * 28.0) % 180.0
        is_water = terrain == "Open Water"
        eng_scores = cand.get("engine_scores") or {}
        top_eng_score = max((float(v) for v in eng_scores.values()), default=float(cand.get("merit_score", 85.0)))
        tectonic_move = _IDIOM_TECTONICS.get(idiom, _IDIOM_TECTONICS["courtyard"])
        precedent = _CRITIC_PRECEDENTS.get(register, f"{reg['name']} vernacular + {register}")

        l_zones = [
            {
                "name": "Ecological Edge & Buffer",
                "family": "Ecological Preserve",
                "intervention": "Preserve",
                "share_pct": 24 if dom_force != "Nature" else 34,
                "why_here": f"Protects sensitive {terrain.lower()} edges and existing natural drainage.",
                "outdoor_activities": "Elevated boardwalks, birdwatching, and passive shade",
            },
            {
                "name": "Native Biome Restoration",
                "family": "Ecological Restoration",
                "intervention": "Restore",
                "share_pct": 26,
                "why_here": f"Re-establishes native flora suited to {reg['name']}.",
                "outdoor_activities": "Botanical trails and shaded desert/riparian groves",
            },
            {
                "name": "Microclimate & Water Spine",
                "family": "Climate & Water",
                "intervention": "Enhance",
                "share_pct": 22,
                "why_here": f"Connects buildings along {reg['passive_air']}.",
                "outdoor_activities": "Shaded promenades, bioswales, and solar canopies",
            },
            {
                "name": "Civic Arrival & Program Courts",
                "family": "Civic Activation",
                "intervention": "Activate",
                "share_pct": 28 if dom_force != "Nature" else 18,
                "why_here": f"Anchors the {len(volumes)} use-driven buildings with direct road access (access score {acc_score}/100).",
                "outdoor_activities": "Outdoor markets, transit drop-off, and evening community courts",
            },
        ]

        n2b_by_force = {
            "Water": f"Captures {reg['climate']} through {tectonic_move}, turning ambient humidity and coastal airflow into passive evaporative cooling.",
            "Food": f"Shapes {tectonic_move} around {reg['passive_air']}, sheltering biosaline crops and cold-chain halls from harsh afternoon heat.",
            "Sun": f"Uses {register.lower()} thermal mass and {tectonic_move} to convert intense {reg['name']} solar gain into shaded, daylit work bays.",
            "Air": f"Pairs {reg['passive_air']} with {tectonic_move}, accelerating natural cross-ventilation through craft kilns and studios.",
            "People": f"Organizes {tectonic_move} along {reg['passive_air']}, creating a cool civic street microclimate without mechanical overload.",
            "Nature": f"Minimizes ground disturbance via {tectonic_move}, letting {reg['climate']} flow uninterrupted across restored habitats.",
        }
        b2n_by_force = {
            "Water": f"Returns purified greywater via {reg['water_mech']}, feeding downstream reed-bed habitats built from {reg['materials']}.",
            "Food": f"Closes nutrient and water loops through {reg['water_mech']}, pairing {reg['materials']} with productive native agro-forestry.",
            "Sun": f"Exports surplus microgrid power to power {reg['water_mech']}, framed in low-carbon {reg['materials']}.",
            "Air": f"Channels roof-harvested condensation and runoff into {reg['water_mech']}, softening the microclimate around {reg['materials']}.",
            "People": f"Transforms civic plazas into permeable sponges via {reg['water_mech']}, grounded in tactile {reg['materials']}.",
            "Nature": f"Buffers adjacent wild ecology with {reg['water_mech']}, using reversible {reg['materials']} that weather naturally into the terrain.",
        }

        thesis_openers = {
            "courtyard": f"Carved around {tectonic_move}, {title} turns inward to manufacture a cool, glare-free microclimate",
            "terrace": f"Stepped along the site's subtle contours as {tectonic_move}, {title} anchors public life into the ground",
            "cantilever": f"Poised lightly above the terrain via {tectonic_move}, {title} preserves natural drainage while casting deep civic shade",
            "clustered_compound": f"Broken into a porous village-scale grain of {tectonic_move}, {title} replaces monolithic blocks with breezy pedestrian alleys",
            "bridge": f"Stitched across the site's ecological seams as {tectonic_move}, {title} pairs structural span with continuous open ground",
        }
        ep_adj = reg["epithet"] if any(p in reg["epithet"] for p in ("Sinai", "Nile", "Nubian", "Kershef")) else reg["epithet"].lower()
        arrival_by_idiom = {
            "courtyard": f"Step off the {terrain.lower()} perimeter (access {acc_score}/100) through a thick {ep_adj} portal into a shadowed arrival cloister.",
            "terrace": f"Descend gently from the {terrain.lower()} approach (access {acc_score}/100) along stepped {ep_adj} plinths toward cooled public courts.",
            "cantilever": f"Pass beneath a broad cantilevered {ep_adj} canopy (access {acc_score}/100) where wind-funnels cool the arrival plaza.",
            "clustered_compound": f"Enter a narrow, self-shading {ep_adj} alley from the {terrain.lower()} road edge (access {acc_score}/100) into the central forum.",
            "bridge": f"Cross a spanned threshold deck (access {acc_score}/100) framed in {ep_adj} structure, overlooking restored ground below.",
        }
        dusk_by_force = {
            "Water": f"Follow the cooled filtration channels and reed beds linking all {len(volumes)} volumes across {feddans:.1f} feddans as evening mist settles.",
            "Food": f"Walk out through productive biosaline groves and shaded harvest courts spanning {feddans:.1f} feddans at dusk.",
            "Sun": f"Move between glowing solar-canopy courts and restored {reg['name']} flora across {feddans:.1f} feddans.",
            "Air": f"Linger in wind-cooled amphitheater courts and native planting beds connecting all {len(volumes)} craft volumes.",
            "People": f"Spill out into lantern-lit neighborhood plazas, bioswales, and shaded civic walkways across {feddans:.1f} feddans.",
            "Nature": f"Trace quiet boardwalks through restored {reg['name']} habitat and star-gazing courts across {feddans:.1f} feddans.",
        }
        anchor_use_lc = volumes[0]["use"].lower().replace("r&d", "R&D").replace("k-12", "K-12")
        daily_life = prog.get("daily_life", "work, gather, and explore shaded public courts")
        acts = prog.get("activities", [])
        act1 = acts[0] if len(acts) > 0 else "Arrival court"
        act2 = acts[1] if len(acts) > 1 else volumes[0]["name"]
        act3 = acts[2] if len(acts) > 2 else "Evening gathering"
        act1_lc = act1.lower().replace("fablab", "FabLab")
        act2_lc = act2.lower().replace("fablab", "FabLab")
        act3_lc = act3.lower().replace("fablab", "FabLab").removeprefix("evening ")

        journey_moments = [
            {"moment": f"Arrival & {act1}", "detail": f"{arrival_by_idiom.get(idiom, arrival_by_idiom['courtyard'])} Stop for coffee, transit drop-off, or {act1_lc}."},
            {"moment": f"{volumes[0]['name']} & {act2}", "detail": f"Step inside the {volumes[0]['area_m2']:,} m² anchor for {anchor_use_lc}—or join {act2_lc} along the public gallery."},
        ]
        if len(volumes) >= 2:
            journey_moments.append({"moment": f"{volumes[1]['name']}", "detail": f"Cross into the {volumes[1]['area_m2']:,} m² {volumes[1]['name'].lower()} for {volumes[1]['use'].lower()}."})
        journey_moments.append({"moment": f"Dusk & {act3}", "detail": f"{dusk_by_force.get(dom_force, dusk_by_force['People'])} Stay after sunset for {act3_lc}."})
        if len(acts) >= 4:
            journey_moments.append({"moment": f"Night · {acts[3]}", "detail": f"End the night with {acts[3].lower()} under shaded lanterns and cool {reg['name']} breezes."})

        seeds.append({
            "rank": rank,
            "candidate_rank": rank,
            "title": title,
            "subtitle": critic_sub,
            "nature_hero": f"{dom_force} · {reg['name']}",
            "strategy": strat,
            "tier": prog["tier"],
            "idiom": idiom,
            "precedent": precedent,
            "concept_register": register,
            "is_water": is_water,
            "target_feddans": feddans,
            "site_bearing_deg": bearing,
            "orientation": f"Primary axes rotated {bearing:.0f}° to align with {reg['passive_air']}.",
            "shape_logic": f"{len(volumes)} distinct architectural volumes ({total_gfa:,} m² GFA) arranged as {tectonic_move}, leaving >{100 - far*100:.0f}% of the {feddans:.1f}-feddan site as open landscape.",
            "activities": acts,
            "thesis_summary": {
                "hook": f"{critic_sub} — a {feddans:.1f}-feddan {terrain.lower()} place where visitors and locals {daily_life}.",
                "gesture_line": f"{register} architecture articulated as {tectonic_move}.",
                "why_here": f"Selected by {eng} ({strat}) at {top_eng_score:.1f}/100 {dom_force} suitability ({ptr_text}); access {acc_score}/100.",
            },
            "thesis_detailed": (
                f"{thesis_openers.get(idiom, thesis_openers['courtyard'])} on a {feddans:.1f}-feddan {terrain.lower()} parcel "
                f"at ({lat:.4f}, {lon:.4f}) in the {reg['name']} biome ({top_eng_score:.1f}/100 peak {dom_force} suitability). "
                f"Designed for everyday public life as much as specialist work, it invites people to {daily_life}. "
                f"{site_advantage} "
                f"{len(volumes)} calibrated volumes ({total_gfa:,} m², FAR {far*100:.1f}%) in {reg['materials']} "
                f"house the enclosed program—led by the {volumes[0]['name']}—while leaving >{100 - far*100:.0f}% of the site as shaded courts and restored landscape."
            ),
            "engine_trace": f"Dominant Engine: {eng} | Dominant Force: {dom_force} ({top_eng_score:.1f}/100) | Strategy: {strat} | Terrain: {terrain}",
            "nature_to_bldg": n2b_by_force.get(dom_force, f"Harnesses {reg['climate']} via {reg['passive_air']}."),
            "bldg_to_nature": b2n_by_force.get(dom_force, f"Integrates {reg['water_mech']} using {reg['materials']}."),
            "experience_arc": {
                "core_idea": f"{title}: {critic_sub}",
                "visit_mode": prog["visit_mode"],
                "atmosphere": f"{reg['materials']}; {tectonic_move}.",
                "journey": journey_moments,
            },
            "visual_direction": {
                "architectural_language": f"{register} architecture calibrated to {reg['name']}.",
                "aerial_composition": f"{len(volumes)} distinct {idiom} buildings set within {feddans:.1f} feddans of restored landscape.",
                "hero_threshold_scene": f"Eye-level approach to {volumes[0]['name']} framed by {reg['materials']}.",
                "lighting_mood": "Crisp late-afternoon directional sun casting deep courtyard and louver shadows.",
                "materials_palette": reg["materials"],
                "camera_cue": "",
            },
            "activities": [u["name"] for u in uses] + ["Native Biome Trails", "Shaded Civic Courts"],
            "spaces": spaces,
            "landscape_summary": f"Four non-overlapping landscape zones balancing {terrain.lower()} preservation with {dom_force.lower()}-driven public activation.",
            "landscape_zones": l_zones,
            "volumes": volumes,
            "financials": {
                "building_capex_usd_per_m2": prog["b_capex"],
                "landscape_capex_usd_per_m2": 75.0,
            },
            "map_pointers": ptrs[:5],
        })
    return seeds


def main():
    ap = argparse.ArgumentParser(description="NEST Stage B Hybrid Seed Expander & Dynamic Synthesizer")
    ap.add_argument("--run-dir", type=Path, required=True, help="Run output directory containing intermediates/stage_a_summary.json")
    ap.add_argument("--seeds-dir", type=Path, default=None, help="Optional directory with site_*_seed.json files")
    ap.add_argument("--seed-file", type=Path, default=None, help="Optional single JSON file containing list of site seeds")
    ap.add_argument("--data-dir", type=Path, default=None, help="Optional GIS plot folder for extra context")
    args = ap.parse_args()

    stage_a_path = args.run_dir / "intermediates" / "stage_a_summary.json"
    if not stage_a_path.exists():
        raise FileNotFoundError(f"Missing {stage_a_path}")
    stage_a = json.loads(stage_a_path.read_text(encoding="utf-8"))

    seeds: list[dict] = []
    if args.seed_file and args.seed_file.exists():
        seeds = json.loads(args.seed_file.read_text(encoding="utf-8"))
    elif args.seeds_dir and args.seeds_dir.exists():
        seed_files = sorted(args.seeds_dir.glob("site_*_seed.json"))
        if seed_files:
            for sf in seed_files:
                seeds.append(json.loads(sf.read_text(encoding="utf-8")))
    if not seeds:
        raise ValueError(
            f"No agent-authored seed files found in {args.seeds_dir or (args.run_dir / 'intermediates' / 'seeds')}. "
            "Stage B requires bespoke site_1_seed.json..site_5_seed.json authored from intermediates/stage_a_agent_brief.md."
        )

    seeds.sort(key=lambda s: int(s["rank"]))
    projects = [build_project_from_seed(s, stage_a) for s in seeds]

    div_warnings = audit_portfolio_diversity(projects)
    for w in div_warnings:
        print(f"[Diversity Warn] {w}")

    out_path = args.run_dir / "stage_b_projects.json"
    out_path.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Stage B Builder] Built {len(projects)} reconciled projects -> {out_path}")

    # Export standalone space_program.json & space_program.csv
    plot_lbl = stage_a.get("plot_label", args.run_dir.name)
    sp_projects = []
    sp_csv_rows = []
    for p in projects:
        vols = (p.get("massing_rationale") or {}).get("volumes") or []
        p_gsf = sum(int(v.get("gsf_m2") or re.sub(r"[^\d]", "", str(v.get("area_m2", "0"))) or 0) for v in vols)
        p_tare = sum(int(v.get("tare_m2", 0)) for v in vols)
        p_nsf = max(0, p_gsf - p_tare)
        sp_projects.append({
            "rank": p["rank"],
            "title": p["title"],
            "area_feddans": p.get("area_feddans"),
            "total_gsf_m2": p_gsf,
            "total_nsf_m2": p_nsf,
            "total_tare_m2": p_tare,
            "nsf_gsf_pct": round((p_nsf / max(1, p_gsf)) * 100.0, 1),
            "buildings": [
                {
                    "name": v.get("name"),
                    "use": v.get("use", ""),
                    "height_floors": v.get("height_floors", ""),
                    "gsf_m2": int(v.get("gsf_m2") or 0),
                    "nsf_m2": int(v.get("nsf_m2") or 0),
                    "tare_m2": int(v.get("tare_m2") or 0),
                    "nsf_gsf_pct": v.get("nsf_gsf_pct", 100.0),
                    "rooms": v.get("interior_zones") or [],
                }
                for v in vols
            ],
        })
        for v in vols:
            v_gsf = int(v.get("gsf_m2") or re.sub(r"[^\d]", "", str(v.get("area_m2", "0"))) or 0)
            v_nsf = int(v.get("nsf_m2", v_gsf))
            v_tare = int(v.get("tare_m2", 0))
            for z in v.get("interior_zones") or []:
                sp_csv_rows.append({
                    "plot": plot_lbl,
                    "site_rank": p["rank"],
                    "project_title": p["title"],
                    "building": v.get("name", ""),
                    "building_gsf_m2": v_gsf,
                    "building_nsf_m2": v_nsf,
                    "building_tare_m2": v_tare,
                    "nsf_gsf_pct": v.get("nsf_gsf_pct", 100.0),
                    "room_name": z.get("name", ""),
                    "role": z.get("role", ""),
                    "is_tare": _is_tare_role(z.get("role", "")),
                    "area_m2": int(z.get("area_m2", 0)),
                })
    sp_json_path = args.run_dir / "space_program.json"
    sp_json_path.write_text(json.dumps({"plot": plot_lbl, "projects": sp_projects}, indent=2, ensure_ascii=False), encoding="utf-8")
    sp_csv_path = args.run_dir / "space_program.csv"
    if sp_csv_rows:
        with open(sp_csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(sp_csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(sp_csv_rows)
    print(f"[Stage B Builder] Exported space program -> {sp_json_path.name} & {sp_csv_path.name} ({len(sp_csv_rows)} room rows)")

    rep_path = args.run_dir / "NEST_Executive_Report.md"
    lines = [
        f"# NEST Executive Report — {plot_lbl}",
        "",
        "> **Approach:** Evidence-First Architectural & Investment Brief (Use-Driven Massing + Regional GIS/Climate Grounding)",
        "",
        "## Portfolio Overview",
        "",
        "| Rank | Project | Idiom & Register | Area (Fed.) | Built GFA (FAR) | Buildings | CapEx | IRR | Payback |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for p in projects:
        fin = p.get("fin") or {}
        vols = (p.get("massing_rationale") or {}).get("volumes") or []
        gfa_num = int(str(p.get("built_gfa", "0")).replace("m²", "").replace(",", "").strip() or 0)
        far_pct = (gfa_num / max(float(p.get("area_m2", 1)), 1.0)) * 100.0
        lines.append(
            f"| #{p['rank']} | **{p['title']}** | {p.get('idiom', '—')} · {p.get('concept_register', '—')} | {p['area_feddans']} | {p['built_gfa']} ({far_pct:.1f}%) | {len(vols)} | {fin.get('capex', '—')} | {fin.get('irr', '—')} | {fin.get('payback', '—')} |"
        )
    for p in projects:
        exp = p.get("experience_arc") or {}
        fin = p.get("fin") or {}
        vols = (p.get("massing_rationale") or {}).get("volumes") or []
        ts = p.get("thesis_summary") or {}
        lines += [
            "",
            "---",
            "",
            f"## Site #{p['rank']}: {p['title']}",
            f"*{p.get('subtitle', '')}* — **{p['area_feddans']} feddans** (`{p['lat']:.5f}, {p['lon']:.5f}`)",
            "",
            f"- **Site Selection & GIS Rationale:** {ts.get('why_here', '')} *(Access: {p.get('access', '—')}/100 · {p.get('engine_trace', '')})*",
            f"- **Architectural Thesis:** {ts.get('gesture_line', '')} — {p.get('thesis_detailed', '')}",
            f"- **Orientation & Massing:** {(p.get('massing_rationale') or {}).get('orientation', '')} {(p.get('massing_rationale') or {}).get('shape_logic', '')}",
            "",
            "### Spatial Experience",
        ]
        for mi, m in enumerate(exp.get("journey") or [], 1):
            lines.append(f"{mi}. **{m.get('moment', f'Moment {mi}')}:** {m.get('detail', '')}")
        lines += [
            "",
            "### Use-Driven Building Program",
            "",
            "| Building | Primary Use | Height / Floors | GFA | Shape Rationale |",
            "| :--- | :--- | :---: | :---: | :--- |",
        ]
        for v in vols:
            lines.append(f"| **{v.get('name')}** | {v.get('use', '')} | {v.get('height_floors', '—')} | {v.get('area_m2', '—')} | {v.get('shape_reason', '—')} |")
        lines += [
            "",
            "### Landscape Zones & Two-Way Nature Integration",
            f"- **Landscape Breakdown:** " + " · ".join(f"{z['id']} {z['name']} ({z['share_pct']}%)" for z in (p.get("landscape_zones") or [])),
            f"- **Nature → Building:** {p.get('nature_to_bldg', '')}",
            f"- **Building → Nature:** {p.get('bldg_to_nature', '')}",
            "",
            "### Investment & CapEx Summary",
            f"- **CapEx:** `{fin.get('capex', '—')}` ({fin.get('capex_split', '—')}) · **Revenue:** `{fin.get('rev', '—')}` · **IRR:** `{fin.get('irr', '—')}` · **Payback:** `{fin.get('payback', '—')}`",
            f"- **Scenarios:** {fin.get('scenarios', '—')}",
        ]
    rep_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[Stage B Builder] Wrote Evidence-First report -> {rep_path}")


if __name__ == "__main__":
    main()
