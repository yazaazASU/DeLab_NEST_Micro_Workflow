#!/usr/bin/env python3
"""
NEST Architectural Render Pack Builder
======================================
Generates a self-contained `<run_dir>/renders/render_pack/` folder for any NEST run:
  - site_<N>_satellite_lock.png   (16:9 Esri World Imagery crop + dashed site boundary + N arrow)
  - site_<N>_prompt.md            (GIS-grounded Site Reality Lock + de-metaphorized prompt)
  - ALL_PROMPTS_CONSOLIDATED.md   (Single copy-paste master prompt file for quota fallback / external tools)
  - AGENT_INSTRUCTIONS.md         (Step-by-step instructions for autonomous agents & visual QC)

Usage:
  python GENERAL_KNOWLEDGE/architectural_render_skill/build_render_pack.py --run-dir outputs
  python GENERAL_KNOWLEDGE/architectural_render_skill/build_render_pack.py --run-dir outputs_sinai
"""

import argparse
import io
import json
import math
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ESRI_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"


def latlon_to_tile_xy(lat: float, lon: float, z: int) -> tuple[float, float]:
    n = 2.0 ** z
    x = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return x, y


def extract_json_var(html: str, var_name: str):
    m = re.search(rf"const {re.escape(var_name)}\s*=\s*(\[.*?\]|\{{.*?\}});", html)
    if not m:
        return None
    return json.loads(m.group(1))


def feature_centroid(feat) -> tuple[float, float]:
    coords = feat["geometry"]["coordinates"]
    pts = []

    def walk(c):
        if isinstance(c[0], (int, float)):
            pts.append(c)
        else:
            for item in c:
                walk(item)

    walk(coords)
    lon = sum(p[0] for p in pts) / len(pts)
    lat = sum(p[1] for p in pts) / len(pts)
    return lat, lon


def bearing_dir(lat1: float, lon1: float, lat2: float, lon2: float) -> tuple[float, str]:
    dlat = lat2 - lat1
    dlon = (lon2 - lon1) * math.cos(math.radians(lat1))
    dist_m = math.hypot(dlat * 111320.0, dlon * 111320.0)
    ang = (math.degrees(math.atan2(dlon, dlat)) + 360.0) % 360.0
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dist_m, dirs[int((ang + 22.5) // 45.0) % 8]


def extract_polygon_rings(geojson: dict) -> list[list[tuple[float, float]]]:
    gtype = geojson.get("type")
    coords = geojson.get("coordinates", [])
    rings = []
    if gtype == "Polygon":
        if coords:
            rings.append([(pt[1], pt[0]) for pt in coords[0]])
    elif gtype == "MultiPolygon":
        for poly in coords:
            if poly:
                rings.append([(pt[1], pt[0]) for pt in poly[0]])
    return rings


def draw_dashed_polyline(draw: ImageDraw.ImageDraw, pts: list[tuple[float, float]], color, width=3, dash=12, gap=7):
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        seg_len = math.hypot(x1 - x0, y1 - y0)
        if seg_len < 1e-3:
            continue
        dx = (x1 - x0) / seg_len
        dy = (y1 - y0) / seg_len
        pos = 0.0
        while pos < seg_len:
            end = min(pos + dash, seg_len)
            draw.line(
                [(x0 + dx * pos, y0 + dy * pos), (x0 + dx * end, y0 + dy * end)],
                fill=color,
                width=width,
            )
            pos += dash + gap


def fetch_tile(z: int, x: int, y: int) -> Image.Image:
    url = ESRI_URL.format(z=z, x=x, y=y)
    req = urllib.request.Request(url, headers={"User-Agent": "NEST-RenderPack/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return Image.open(io.BytesIO(resp.read())).convert("RGB")


def render_satellite_lock(project: dict, out_path: Path, out_w: int = 1280, out_h: int = 720):
    rings = extract_polygon_rings(project["geojson"])
    all_lats = [lat for ring in rings for lat, _ in ring]
    all_lons = [lon for ring in rings for _, lon in ring]
    c_lat = (min(all_lats) + max(all_lats)) / 2.0
    c_lon = (min(all_lons) + max(all_lons)) / 2.0

    # Choose zoom level so the site + ~500 m surrounding context fits comfortably in 1280x720
    lat_span = max(max(all_lats) - min(all_lats), 0.004)
    lon_span = max(max(all_lons) - min(all_lons), 0.006)
    z = 16
    for cand_z in (16, 15, 14):
        x0, y0 = latlon_to_tile_xy(max(all_lats), min(all_lons), cand_z)
        x1, y1 = latlon_to_tile_xy(min(all_lats), max(all_lons), cand_z)
        px_w = abs(x1 - x0) * 256.0
        px_h = abs(y1 - y0) * 256.0
        if px_w <= out_w * 0.52 and px_h <= out_h * 0.56:
            z = cand_z
            break

    cx, cy = latlon_to_tile_xy(c_lat, c_lon, z)
    half_tx = (out_w / 2.0) / 256.0
    half_ty = (out_h / 2.0) / 256.0

    min_tx = int(math.floor(cx - half_tx))
    max_tx = int(math.floor(cx + half_tx))
    min_ty = int(math.floor(cy - half_ty))
    max_ty = int(math.floor(cy + half_ty))

    stitched_w = (max_tx - min_tx + 1) * 256
    stitched_h = (max_ty - min_ty + 1) * 256
    canvas = Image.new("RGB", (stitched_w, stitched_h), (232, 228, 220))

    for tx in range(min_tx, max_tx + 1):
        for ty in range(min_ty, max_ty + 1):
            tile_img = fetch_tile(z, tx, ty)
            canvas.paste(tile_img, ((tx - min_tx) * 256, (ty - min_ty) * 256))

    # Crop exact 16:9 viewport centered on site centroid
    left = int(round((cx - half_tx - min_tx) * 256.0))
    top = int(round((cy - half_ty - min_ty) * 256.0))
    crop = canvas.crop((left, top, left + out_w, top + out_h)).convert("RGBA")

    # Overlay subtle translucent fill + crisp dashed boundary outline
    overlay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    stroke_col = (245, 158, 11, 235) if project.get("is_water") else (255, 97, 76, 235)
    fill_col = (245, 158, 11, 46) if project.get("is_water") else (255, 97, 76, 46)

    for ring in rings:
        pts = []
        for lat, lon in ring:
            tx, ty = latlon_to_tile_xy(lat, lon, z)
            px = (tx - min_tx) * 256.0 - left
            py = (ty - min_ty) * 256.0 - top
            pts.append((px, py))
        if len(pts) >= 3:
            odraw.polygon(pts, fill=fill_col)
            draw_dashed_polyline(odraw, pts, stroke_col, width=4, dash=14, gap=8)

    # Subtle North badge & label pill in top-left / bottom-left for agent orientation
    font = ImageFont.load_default()
    label = f"SATELLITE SITE LOCK — SITE #{project['rank']} ({project['lat']:.4f}, {project['lon']:.4f}) | TOP = NORTH | Esri World Imagery"
    odraw.rounded_rectangle([(14, 14), (min(out_w - 14, 14 + len(label) * 6 + 24), 40)], radius=6, fill=(48, 43, 42, 205))
    odraw.text((24, 21), label, fill=(255, 250, 247, 255), font=font)

    # Compact North arrow in top-right
    nx, ny = out_w - 42, 42
    odraw.ellipse([(nx - 20, ny - 20), (nx + 20, ny + 20)], fill=(48, 43, 42, 205), outline=(213, 201, 197, 220), width=2)
    odraw.polygon([(nx, ny - 13), (nx - 6, ny + 5), (nx, ny + 1), (nx + 6, ny + 5)], fill=(255, 97, 76, 255))
    odraw.text((nx - 3, ny + 5), "N", fill=(255, 250, 247, 255), font=font)

    final_img = Image.alpha_composite(crop, overlay).convert("RGB")
    final_img.save(out_path, format="PNG", optimize=True)


def infer_region_defaults(run_dir_name: str, title: str, lat: float = 0.0, lon: float = 0.0):
    combined = (run_dir_name + " " + title).lower()
    if "sinai" in combined or lon > 32.6:
        return {
            "region": "Sinai / Red Sea Arid Coast & Mountains (Egypt)",
            "topography": "Arid limestone-and-gravel desert plain with distant desert ridges matching the satellite crop",
            "forbidden": "Strictly NO lush green riverbanks, NO perennial flowing rivers, NO waterfalls, NO European lawns, NO tropical forests, NO artificial turquoise resort lagoons.",
            "flora": "Very sparse arid desert scrub and minimal xeriscaped native acacia/date palms strictly inside shaded courtyards.",
        }
    if "port said" in combined or "manzala" in combined or (lat >= 30.2 and 31.2 < lon <= 32.6):
        return {
            "region": "Nile Delta & Mediterranean Lagoon Littoral (Egypt)",
            "topography": "Dead-flat coastal deltaic plain and shallow brackish lagoon shoreline (0–2% slope)",
            "forbidden": "Strictly NO hills, NO cliffs, NO mountains, NO European lawns, NO artificial turquoise resort pools.",
            "flora": "Native Phragmites reed beds, salt-tolerant marsh scrub, and hardy coastal palms over pale stone and compacted sand.",
        }
    if "alexandria" in combined or "matrouh" in combined or "borg el arab" in combined or (lat >= 30.6 and lon <= 31.2):
        return {
            "region": "Mediterranean North Coast / Alexandria–Matrouh Littoral (Egypt)",
            "topography": "Low coastal limestone ridge and flat sandy-scrub plain sloping gently toward the Mediterranean littoral",
            "forbidden": "Strictly NO tall mountains, NO tropical forests, NO European manicured grass lawns, NO artificial turquoise resort lagoons.",
            "flora": "Salt-tolerant Mediterranean coastal scrub, native fig/olive groves, and date palms over pale quarried limestone paving and dry sand.",
        }
    if lat < 30.6 and lon < 30.5 and lon > 1.0:
        return {
            "region": "Egyptian Western Desert",
            "topography": "Open arid desert plateau and wind-swept sand/limestone plains",
            "forbidden": "Strictly NO lush green lawns, NO artificial lakes, NO tropical forests.",
            "flora": "Minimal desert-adapted acacia, tamarisk, and date palms strictly inside shaded microclimates.",
        }
    return {
        "region": "Nile Valley / Upper Egypt",
        "topography": "Strictly dead-flat Nile Valley alluvial plain (0–2% slope), extending completely level to the flat horizon",
        "forbidden": "Strictly NO natural hills, NO rocky cliffs, NO mountains, NO undulating parkland, NO artificial turquoise ponds or resort lakes, NO waterfalls, NO European manicured lawns, NO tropical forests.",
        "flora": "Sparse, regionally authentic Egyptian date palms, acacia, and sycamore shade trees over dry pale limestone paving and compacted earth (no grass lawns).",
    }


def summarize_cardinal_context(project: dict, wat_pts: list, bld_pts: list) -> tuple[str, str]:
    lat, lon = project["lat"], project["lon"]
    w_near = sorted([bearing_dir(lat, lon, wl, wn) for wl, wn in wat_pts], key=lambda x: x[0])[:3]
    if w_near:
        d0, dir0 = w_near[0]
        if d0 <= 250:
            hydro = f"Real river/canal water channel immediately adjacent along the {dir0} edge (~{round(d0)} m from site centroid); dry built ground everywhere inside the site perimeter unless explicitly engineered."
        elif d0 <= 850:
            hydro = f"Real river/canal water channel visible along the {dir0} side (~{round(d0)} m from site centroid); dry alluvial ground across the interior site."
        else:
            hydro = f"Dry inland alluvial/desert ground; nearest mapped water feature lies ~{round(d0)} m away to the {dir0}. Zero interior lakes or ponds."
    else:
        hydro = "Dry inland ground with zero surface water bodies."

    b_dirs = {}
    for bl, bn in bld_pts:
        d, dr = bearing_dir(lat, lon, bl, bn)
        if d <= 800:
            b_dirs[dr] = b_dirs.get(dr, 0) + 1
    top_b = sorted(b_dirs.items(), key=lambda x: -x[1])[:3]
    if top_b:
        dirs_str = ", ".join(f"{dr} ({cnt} mapped footprints)" for dr, cnt in top_b)
        fabric = f"Dense 3–5 story weathered Egyptian red-brick and concrete urban blocks bordering the {dirs_str}; flat rectilinear agricultural/desert parcels on open sides."
    else:
        fabric = "Flat rectilinear rural agricultural fields / open plain with sparse low-rise weathered red-brick buildings and straight dirt/asphalt access tracks."
    return hydro, fabric


def build_site_prompt_text(project: dict, region_cfg: dict, hydro: str, fabric: str, sat_filename: str) -> str:
    rank = project["rank"]
    title = project["title"]
    concept = project.get("concept", "")
    idiom = project.get("idiom", "")
    nat_to_bldg = project.get("nature_to_bldg", "")
    bldg_to_nat = project.get("bldg_to_nature", "")
    is_tower_project = any(k in (title + " " + concept).lower() for k in ("wind-tower", "wind tower", "thermal-chimney", "thermal chimney", "chimney"))
    tower_guard = "" if is_tower_project else " NO malqaf wind-catchers, NO vertical roof chimneys, NO protruding rooftop towers."

    two_way = ""
    if nat_to_bldg or bldg_to_nat:
        two_way = f"\n- Visible Two-Way Nature Integration: (Nature->Building) {nat_to_bldg} | (Building->Nature) {bldg_to_nat}"

    exp = project.get("experience_arc") or {}
    vols = (project.get("massing_rationale") or {}).get("volumes") or []
    constellation_str = "; ".join(
        f"{v.get('name', 'Pavilion')} ({v.get('role', 'Pavilion')}, {v.get('area_m2', '')}): {v.get('shape_reason') or v.get('use', '')}"
        for v in vols[:5]
    )
    journey_items = exp.get("journey") or []
    journey_str = " | ".join(
        f"{m.get('moment', '')}: {m.get('detail', '')}" for m in journey_items[:5] if isinstance(m, dict)
    )

    return f"""Photorealistic editorial aerial architectural photograph (ArchDaily / Dezeen / MIR / Luxigon quality), 16:9 widescreen, medium-format drone camera, 35mm rectilinear lens, crisp deep depth-of-field (f/11) across the entire frame — strictly NO tilt-shift or miniature toy-model blur.

VISUAL REFERENCE LOCK:
Use the attached `{sat_filename}` as the strict geographic and site-organization foundation. Match its exact flat terrain, real water/river/canal edge position, roads, and neighboring urban/agricultural fabric (Top of satellite image = North).

SITE REALITY LOCK ({region_cfg['region']}):
- Topography: {region_cfg['topography']}.
- Hydrology: {hydro}
- Cardinal Surrounding Context: {fabric}
- Regional Flora: {region_cfg['flora']}
- FORBIDDEN LANDSCAPE FEATURES: {region_cfg['forbidden']}{tower_guard}

EXPERIENCE-LED ARCHITECTURE & DISTRIBUTED CONSTELLATION (DE-METAPHORIZED):
- Project: {title} (Total Built GFA: {project.get('built_gfa', 'N/A')} across a distributed multi-pavilion constellation | Site Area: {project.get('area_m2', 0)/10000:.2f} ha).
- Core Architectural Idea & Atmosphere: {exp.get('core_idea', idiom)} {exp.get('atmosphere', '')}
- Tectonic Idiom: {idiom}
- Distributed Pavilions: {constellation_str or concept}
- Visual Guest Journey Moments: {journey_str or concept}
- Nature Hero & Two-Way Exchange (translate any poetic terms strictly into realistic architectural masonry, stepped earth-bermed plinths, shaded courts, and curated dining/retail/eco-stay pavilions — NEVER natural rocky hills or turquoise ponds): {concept}{two_way}
- Materials: Authentic local stacked Egyptian limestone, board-formed desert-aggregate concrete, rammed earth, oxidized bronze shading louvers, matte dark photovoltaic surfaces where integrated, recessed low-iron glazing, dry pale stone paving.
- Entourage: Sparse tiny candid human scale figures and minimal muted local vehicles on real access roads.

CAMERA & LIGHTING:
Classic Hero Aerial (~40–45° pitch), Golden Hour late-afternoon sunlight casting long crisp shadows with subtle natural dusty horizon haze. Zero HDR oversaturation, zero gibberish text/signage, zero logos, zero floating elements."""


def main():
    parser = argparse.ArgumentParser(description="Build satellite-locked architectural render pack for a NEST run.")
    parser.add_argument("--run-dir", default="outputs", help="Path to NEST run output directory (e.g., outputs or outputs_sinai)")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    dash_html_path = run_dir / "nest_dashboard.html"
    if not dash_html_path.exists():
        raise FileNotFoundError(f"Could not find {dash_html_path}")

    html = dash_html_path.read_text(encoding="utf-8")
    projects = extract_json_var(html, "NEST_PROJECTS")
    ref_wat = extract_json_var(html, "REF_WAT") or {"features": []}
    ref_bld = extract_json_var(html, "REF_BLD") or {"features": []}

    if not projects:
        raise RuntimeError(f"Could not extract NEST_PROJECTS from {dash_html_path}")

    wat_pts = [feature_centroid(f) for f in ref_wat.get("features", [])]
    bld_pts = [feature_centroid(f) for f in ref_bld.get("features", [])]

    pack_dir = run_dir / "renders" / "render_pack"
    pack_dir.mkdir(parents=True, exist_ok=True)

    consolidated_sections = [
        f"# Consolidated Architectural Render Prompts — {run_dir.name}",
        "",
        "> **How to use:** Pair each prompt below with its matching `site_<N>_satellite_lock.png` in this folder. Generate at `16:9` widescreen and save final QC-passed renders to `../site_<N>.jpg`.",
        "",
    ]

    for p in projects:
        rank = p["rank"]
        sat_name = f"site_{rank}_satellite_lock.png"
        sat_path = pack_dir / sat_name
        print(f"Fetching Esri satellite lock for Site #{rank} -> {sat_path.name} ...")
        render_satellite_lock(p, sat_path)

        region_cfg = infer_region_defaults(run_dir.name, p["title"], float(p.get("lat", 0.0)), float(p.get("lon", 0.0)))
        hydro, fabric = summarize_cardinal_context(p, wat_pts, bld_pts)
        prompt_text = build_site_prompt_text(p, region_cfg, hydro, fabric, sat_name)

        site_md = f"""# Site #{rank} Render Brief — {p['title']}

- **Target Output File:** `../site_{rank}.jpg` (`16:9` widescreen)
- **Satellite Visual Lock:** `./{sat_name}` *(pass this image as visual context reference)*
- **Coordinates:** `{p['lat']:.5f}, {p['lon']:.5f}` · **Boundary:** `{p.get('footprint_type', 'Contiguous')}` ({p.get('area_m2', 0)/10000:.2f} ha)

## Prompt (Copy-Paste Ready)

```text
{prompt_text}
```
"""
        (pack_dir / f"site_{rank}_prompt.md").write_text(site_md, encoding="utf-8")

        consolidated_sections.extend([
            "---",
            f"## IMAGE {rank} — Save as: `renders/site_{rank}.jpg` (Attach `./{sat_name}`)",
            f"**Project:** {p['title']}",
            "",
            "```text",
            prompt_text,
            "```",
            "",
        ])

    (pack_dir / "ALL_PROMPTS_CONSOLIDATED.md").write_text("\n".join(consolidated_sections), encoding="utf-8")

    agent_instructions = f"""# Agent Instructions — Generating Satellite-Locked NEST Renders

Follow `GENERAL_KNOWLEDGE/architectural_render_skill/SKILL.md` using the assets in this folder (`{pack_dir.name}/`):

## Step-by-Step Execution
1. **For each site (`1` to `{len(projects)}`):**
   - Inspect `site_<N>_satellite_lock.png` with `read_file` to verify real ground edges (river/canal side, urban blocks, flat terrain).
   - Read `site_<N>_prompt.md`.
   - Invoke `image-generator` passing **`site_<N>_satellite_lock.png` as the visual reference** along with the full prompt from `site_<N>_prompt.md`.
   - Copy the generated image to `../site_<N>.jpg`.
2. **Mandatory 6-Point Visual QC (compare side-by-side with `site_<N>_satellite_lock.png`):**
   - Inspect both `../site_<N>.jpg` and `site_<N>_satellite_lock.png` via `read_file`.
   - Verify all 6 checks from `GENERAL_KNOWLEDGE/architectural_render_skill/references/qc-checklist.md` — especially **Check #6 (Geographic, Topographic & Hydrological Fidelity)**:
     - No invented hills/cliffs/mountains on flat plains.
     - No invented turquoise ponds/lagoons/waterfalls.
     - Real river/canal and neighboring urban fabric appear in the right direction.
   - Perform at most **1 auto-fix pass** if any critical check fails.
3. **Quota / Usage Exhaustion Fallback (`429 RESOURCE_EXHAUSTED`):**
   - If `image-generator` hits a usage/quota limit, **stop retrying immediately**.
   - Deliver the contents of `ALL_PROMPTS_CONSOLIDATED.md` (covering all remaining ungenerated sites) in **one single copy-paste fenced code block** in chat and remind the user to attach each matching `site_<N>_satellite_lock.png` in their external generator.
"""
    (pack_dir / "AGENT_INSTRUCTIONS.md").write_text(agent_instructions, encoding="utf-8")
    print(f"Render pack complete -> {pack_dir}")


if __name__ == "__main__":
    main()
