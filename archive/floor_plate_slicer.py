#!/usr/bin/env python3
"""
NEST True-Level Floor-Plate & Vertical Core Slicer
==================================================
Converts each mass's `interior_zones` schedule + 2D footprint GeoJSON into
architecturally honest 3D floor-plate geometry:

1. NEVER invents fake vertical floors: only the real levels named in `tier`
   exist (e.g. a 1-story shell or wadi bar has ONLY 1 level; a 2-tier mass has
   ONLY Level 1 and Level 2).
2. Co-located uses on the SAME floor split that floor's actual polygon
   horizontally side-by-side along its principal architectural axis in exact
   proportion to their m² area (with a crisp 0.7 m partition seam).
3. Spanning service/circulation cores (e.g. `L1–L2`, `L1–L3`, `Levels 1–5`)
   become a compact vertical core block piercing through those exact levels
   rather than a fake top floor.
"""
from __future__ import annotations

import math
import re
from shapely.affinity import rotate as shp_rotate, scale as shp_scale
from shapely.geometry import Polygon, MultiPolygon, Point, box, shape, mapping
from shapely.ops import unary_union

from heatmap_engine import LocalProjection


LEVEL_NAMES = {
    0: ("SUB", "Subterranean"),
    1: ("L1", "Ground · L1"),
    2: ("L2", "Upper · L2"),
    3: ("L3", "Level 3"),
    4: ("L4", "Level 4"),
    5: ("L5", "Level 5"),
    6: ("L6", "Level 6"),
}


def parse_zone_tier(tier_str: str, category: str) -> tuple[list[int], bool, str]:
    """Return (levels_list, is_vertical_core, short_badge) for an interior zone."""
    s = (tier_str or "").strip()
    sl = s.lower()

    if "subterranean" in sl or "basement" in sl or "vault" in sl:
        return [0], False, "SUB"

    if "elevated" in sl or "pier" in sl or "deck" in sl:
        return [1], False, "DECK"

    # Range check: e.g. "L1–L2", "L1-L3", "Tier 1–2", "Levels 1–5", "Levels 2–4"
    m_rng = re.search(r"(\d+)\s*[–\-]\s*(\d+)", s)
    if m_rng:
        a, b = int(m_rng.group(1)), int(m_rng.group(2))
        lo, hi = min(a, b), max(a, b)
        lvls = list(range(lo, hi + 1))
        is_core = (category == "service") and (len(lvls) >= 2)
        badge = f"L{lo}–L{hi} Core" if is_core else f"L{lo}–L{hi}"
        return lvls, is_core, badge

    if "mezz" in sl:
        return [2], False, "MEZZ"

    m_single = re.search(r"(?:l|level|tier)\s*(\d+)", sl)
    if m_single:
        lv = int(m_single.group(1))
        return [lv], False, f"L{lv}"

    if "upper" in sl:
        return [2], False, "L2"

    return [1], False, "L1"


def _principal_axis_deg(geom) -> float:
    """Angle (degrees) of the longest edge of the minimum rotated rectangle."""
    mrr = geom.minimum_rotated_rectangle
    if mrr is None or mrr.is_empty or not hasattr(mrr, "exterior"):
        return 0.0
    coords = list(mrr.exterior.coords)
    if len(coords) < 4:
        return 0.0
    dx1, dy1 = coords[1][0] - coords[0][0], coords[1][1] - coords[0][1]
    dx2, dy2 = coords[2][0] - coords[1][0], coords[2][1] - coords[1][1]
    if math.hypot(dx1, dy1) >= math.hypot(dx2, dy2):
        return math.degrees(math.atan2(dy1, dx1))
    return math.degrees(math.atan2(dy2, dx2))


def _slice_polygon_along_axis(geom, weights: list[float], gap_m: float = 0.75) -> list:
    """Slice `geom` (Polygon or MultiPolygon in meters) along its principal axis into
    len(weights) side-by-side polygons whose areas match `weights` proportionally."""
    n = len(weights)
    if n == 0 or geom.is_empty:
        return []
    if n == 1:
        return [geom]

    tot_w = sum(max(w, 1e-3) for w in weights)
    fracs = [max(w, 1e-3) / tot_w for w in weights]

    ang = _principal_axis_deg(geom)
    c = geom.centroid
    rot_g = shp_rotate(geom, -ang, origin=(c.x, c.y))
    minx, miny, maxx, maxy = rot_g.bounds
    pad_y = (maxy - miny) + 50.0
    total_area = max(rot_g.area, 1e-3)

    # Find cumulative cut positions x_cuts[1..n-1] via binary search on exact polygon area
    cuts = [minx - 1.0]
    cum = 0.0
    for k in range(n - 1):
        cum += fracs[k]
        target_a = cum * total_area
        lo, hi = cuts[-1], maxx + 1.0
        for _ in range(28):
            mid = 0.5 * (lo + hi)
            left_piece = rot_g.intersection(box(minx - 5.0, miny - pad_y, mid, maxy + pad_y))
            if left_piece.area < target_a:
                lo = mid
            else:
                hi = mid
        cuts.append(0.5 * (lo + hi))
    cuts.append(maxx + 1.0)

    pieces = []
    half_gap = gap_m * 0.5
    for k in range(n):
        x0 = cuts[k] + (half_gap if k > 0 else 0.0)
        x1 = cuts[k + 1] - (half_gap if k < n - 1 else 0.0)
        if x1 <= x0 + 0.1:
            x0, x1 = cuts[k], cuts[k + 1]
        slab = rot_g.intersection(box(x0, miny - pad_y, x1, maxy + pad_y)).buffer(0)
        if slab.is_empty:
            slab = rot_g.intersection(box(cuts[k], miny - pad_y, cuts[k + 1], maxy + pad_y)).buffer(0)
        pieces.append(shp_rotate(slab, ang, origin=(c.x, c.y)))
    return pieces


def _step_plate_for_level(base_geom, lvl_idx: int, total_pos_levels: int, fp_idiom: str, has_mezz_only: bool):
    """Match upper floor plates to the actual stepped/tapered building envelope so upper
    levels never overhang smaller upper tiers."""
    if lvl_idx <= 1:
        return base_geom
    c = base_geom.centroid
    if has_mezz_only and lvl_idx == 2:
        sc = 0.55
        g = shp_scale(base_geom, xfact=sc, yfact=sc, origin=(c.x, c.y)).intersection(base_geom).buffer(0)
        return g if not g.is_empty else base_geom
    if fp_idiom == "coastal_shelf_cut" and lvl_idx >= 2:
        sc = 0.72
        g = shp_scale(base_geom, xfact=sc, yfact=sc, origin=(c.x, c.y)).intersection(base_geom).buffer(0)
        return g if not g.is_empty else base_geom
    if total_pos_levels >= 4:
        # Biophilic vertical / tapered multi-story spire
        step_k = lvl_idx - 1
        sc = max(0.56, 1.0 - step_k * 0.09)
        rot = step_k * 7.0 if "vertical" in fp_idiom else 0.0
        g = shp_scale(base_geom, xfact=sc, yfact=sc, origin=(c.x, c.y))
        if rot:
            g = shp_rotate(g, rot, origin=(c.x, c.y))
        return g.buffer(0)
    if total_pos_levels >= 2 and lvl_idx >= 2:
        sc = max(0.72, 1.0 - (lvl_idx - 1) * 0.11)
        return shp_scale(base_geom, xfact=sc, yfact=sc, origin=(c.x, c.y)).buffer(0)
    return base_geom


def build_mass_floor_layout(fp: dict, vol: dict, proj: LocalProjection, project_idiom: str = "") -> dict:
    """Compute exact WGS84 floor-plate zone slices & vertical core shafts for one mass."""
    iz_list = vol.get("interior_zones") or []
    geom_ll = fp.get("geom")
    if not geom_ll or not iz_list:
        return {"level_count": 0, "is_single_level": True, "levels": [], "cores": [], "zone_badges": []}

    base_m = proj.geom_to_meters(shape(geom_ll)).buffer(0)
    if base_m.is_empty:
        return {"level_count": 0, "is_single_level": True, "levels": [], "cores": [], "zone_badges": []}

    # Slight inset (-0.6 m) so floor plates sit cleanly inside the ghosted exterior wall line
    inset_m = base_m.buffer(-0.6).buffer(0)
    if inset_m.is_empty or inset_m.area < 0.65 * base_m.area:
        inset_m = base_m

    fp_idiom = str(fp.get("idiom") or project_idiom or "").lower()
    is_bridge = bool(fp.get("bridge_or_pile_allowed", False))

    parsed = []
    all_levels_set: set[int] = set()
    has_mezz = False
    for idx, iz in enumerate(iz_list):
        lvls, is_core, badge = parse_zone_tier(iz.get("tier", ""), iz.get("category", ""))
        if badge == "MEZZ":
            has_mezz = True
        parsed.append({"iz_idx": idx, "iz": iz, "levels": lvls, "is_core": is_core, "badge": badge})
        if not is_core:
            all_levels_set.update(lvls)

    if not all_levels_set:
        for item in parsed:
            all_levels_set.update(item["levels"])

    sorted_lvls = sorted(all_levels_set)
    pos_lvls = [lv for lv in sorted_lvls if lv >= 1]
    max_pos_lvl = max(pos_lvls) if pos_lvls else 1

    # 1. Carve compact Vertical Core Shafts (never add a fake extra floor!)
    cores_out = []
    core_union_m = None
    core_items = [it for it in parsed if it["is_core"]]
    if core_items and not is_bridge:
        tot_mass_m2 = max(sum(float(z.get("area_m2") or 0) for z in iz_list), 1.0)
        for ci, cit in enumerate(core_items):
            n_span = max(len(cit["levels"]), 1)
            # Core footprint per floor ~ core_total_m2 / n_span
            target_core_fp = max(28.0, min((float(cit["iz"].get("area_m2") or 200) / n_span), inset_m.area * 0.16))
            rp = inset_m.representative_point()
            side = math.sqrt(target_core_fp)
            c_box = box(rp.x - side * 0.6 + ci * side, rp.y - side * 0.45, rp.x + side * 0.6 + ci * side, rp.y + side * 0.45)
            c_poly = c_box.intersection(inset_m.buffer(-1.2)).buffer(0)
            if c_poly.is_empty or c_poly.area < 10.0:
                c_poly = rp.buffer(math.sqrt(target_core_fp / math.pi), resolution=8).intersection(inset_m).buffer(0)
            if not c_poly.is_empty:
                core_union_m = c_poly if core_union_m is None else unary_union([core_union_m, c_poly]).buffer(0)
                cpt_ll = proj.to_lonlat(c_poly.representative_point().x, c_poly.representative_point().y)
                from_slot = sorted_lvls.index(min(cit["levels"])) if min(cit["levels"]) in sorted_lvls else 0
                to_slot = sorted_lvls.index(max(cit["levels"])) if max(cit["levels"]) in sorted_lvls else (len(sorted_lvls) - 1)
                cores_out.append({
                    "iz_idx": cit["iz_idx"],
                    "badge": cit["badge"],
                    "from_slot": from_slot,
                    "to_slot": to_slot,
                    "pin_lonlat": [round(cpt_ll[0], 6), round(cpt_ll[1], 6)],
                    "geom": mapping(proj.geom_to_lonlat(c_poly)),
                })

    # 2. Slice each REAL floor plate horizontally among the co-located uses on that floor
    levels_out = []
    zone_PrimaryPin_set: set[int] = set()

    for slot_idx, lv in enumerate(sorted_lvls):
        plate_m = inset_m if is_bridge else _step_plate_for_level(inset_m, lv, max_pos_lvl, fp_idiom, has_mezz and max_pos_lvl == 2)
        if core_union_m is not None and not is_bridge:
            diff_m = plate_m.difference(core_union_m.buffer(0.6)).buffer(0)
            if not diff_m.is_empty and diff_m.area > 0.4 * plate_m.area:
                plate_m = diff_m

        # Uses present on this floor
        on_floor = [it for it in parsed if (not it["is_core"]) and (lv in it["levels"])]
        weights = [float(it["iz"].get("area_m2") or 100) / max(len(it["levels"]), 1) for it in on_floor]
        slices_m = _slice_polygon_along_axis(plate_m, weights, gap_m=0.85 if not is_bridge else 0.5)

        short_code, default_lbl = LEVEL_NAMES.get(lv, (f"L{lv}", f"Level {lv}"))
        if is_bridge:
            short_code, default_lbl = "DECK", "Elevated Deck +4.5 m"
        elif has_mezz and lv == 2 and max_pos_lvl == 2:
            short_code, default_lbl = "MEZZ", "Mezzanine · L2"

        z_slices_out = []
        for it, sl_m in zip(on_floor, slices_m):
            if sl_m is None or sl_m.is_empty:
                continue
            rp = sl_m.representative_point()
            rp_ll = proj.to_lonlat(rp.x, rp.y)
            # Place primary numbered pin on the highest/most visible slot of a multi-floor non-core zone so each use gets exactly 1 pin!
            is_primary_pin = (lv == max(it["levels"])) and (it["iz_idx"] not in zone_PrimaryPin_set)
            if is_primary_pin:
                zone_PrimaryPin_set.add(it["iz_idx"])
            z_slices_out.append({
                "iz_idx": it["iz_idx"],
                "is_primary_pin": is_primary_pin,
                "pin_lonlat": [round(rp_ll[0], 6), round(rp_ll[1], 6)],
                "geom": mapping(proj.geom_to_lonlat(sl_m)),
            })

        # Left-edge anchor for the Floor Level Tag ('L1', 'L2', 'SUB')
        b_minx, b_miny, b_maxx, b_maxy = plate_m.bounds
        tag_ll = proj.to_lonlat(b_minx - 6.0, 0.5 * (b_miny + b_maxy))
        levels_out.append({
            "slot": slot_idx,
            "level_num": lv,
            "code": short_code,
            "label": default_lbl,
            "tag_lonlat": [round(tag_ll[0], 6), round(tag_ll[1], 6)],
            "zones": z_slices_out,
        })

    return {
        "level_count": len(levels_out),
        "is_single_level": len(levels_out) <= 1,
        "is_bridge": is_bridge,
        "levels": levels_out,
        "cores": cores_out,
        "zone_badges": [it["badge"] for it in parsed],
    }


def enrich_projects_with_floor_layouts(projects: list[dict]) -> None:
    for p in projects:
        site_ll = shape(p["geojson"])
        c = site_ll.centroid
        proj = LocalProjection(c.x, c.y)
        fps = p.get("footprints") or []
        vols = (p.get("massing_rationale") or {}).get("volumes") or []
        for fi, (fp, vol) in enumerate(zip(fps, vols)):
            vol["floor_layout"] = build_mass_floor_layout(fp, vol, proj, p.get("idiom", ""))


if __name__ == "__main__":
    import json
    from pathlib import Path
    pjson = Path("outputs_south_sinai_83_616/stage_b_projects.json")
    projs = json.loads(pjson.read_text(encoding="utf-8"))
    enrich_projects_with_floor_layouts(projs)
    for p in projs:
        for v in p["massing_rationale"]["volumes"]:
            fl = v.get("floor_layout", {})
            lv_summary = [f"{lv['code']}({len(lv['zones'])} bays)" for lv in fl.get("levels", [])]
            cr_summary = [c["badge"] for c in fl.get("cores", [])]
            print(f"Site #{p['rank']} | {v['name'][:38]:38s} -> {fl['level_count']} real levels {lv_summary} | cores={cr_summary}")
