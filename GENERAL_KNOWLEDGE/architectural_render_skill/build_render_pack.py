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

    # Use high-res tiles (z=16) and crop/scale smoothly so the site fills ~70% of the 16:9 frame
    z = 16
    tx0, ty0 = latlon_to_tile_xy(max(all_lats), min(all_lons), z)
    tx1, ty1 = latlon_to_tile_xy(min(all_lats), max(all_lons), z)
    poly_tw = max(abs(tx1 - tx0), 0.2)
    poly_th = max(abs(ty1 - ty0), 0.2)

    target_aspect = out_w / float(out_h)
    # Site fills ~70% of height (or width if wide), leaving ~15% context margin around it
    crop_th = max(poly_th / 0.70, (poly_tw / 0.70) / target_aspect)
    crop_tw = crop_th * target_aspect

    cx, cy = latlon_to_tile_xy(c_lat, c_lon, z)
    left_t = cx - crop_tw / 2.0
    top_t = cy - crop_th / 2.0
    right_t = cx + crop_tw / 2.0
    bottom_t = cy + crop_th / 2.0

    min_tx = int(math.floor(left_t))
    max_tx = int(math.floor(right_t))
    min_ty = int(math.floor(top_t))
    max_ty = int(math.floor(bottom_t))

    stitched_w = (max_tx - min_tx + 1) * 256
    stitched_h = (max_ty - min_ty + 1) * 256
    canvas = Image.new("RGB", (stitched_w, stitched_h), (232, 228, 220))

    for tx in range(min_tx, max_tx + 1):
        for ty in range(min_ty, max_ty + 1):
            tile_img = fetch_tile(z, tx, ty)
            canvas.paste(tile_img, ((tx - min_tx) * 256, (ty - min_ty) * 256))

    crop_box = (
        int(round((left_t - min_tx) * 256.0)),
        int(round((top_t - min_ty) * 256.0)),
        int(round((right_t - min_tx) * 256.0)),
        int(round((bottom_t - min_ty) * 256.0)),
    )
    crop = canvas.crop(crop_box).resize((out_w, out_h), Image.Resampling.LANCZOS).convert("RGBA")

    # Overlay subtle translucent fill + crisp dashed boundary outline
    overlay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    stroke_col = (245, 158, 11, 235) if project.get("is_water") else (255, 97, 76, 235)
    fill_col = (245, 158, 11, 46) if project.get("is_water") else (255, 97, 76, 46)

    for ring in rings:
        pts = []
        for lat, lon in ring:
            tx, ty = latlon_to_tile_xy(lat, lon, z)
            px = (tx - left_t) / crop_tw * out_w
            py = (ty - top_t) / crop_th * out_h
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


_IDIOM_SCULPTURAL_FORMS = {
    "courtyard": "sculptural monolithic walls with deep-cut light-slots, folded/parabolic thin-shell oculus roofs, and dramatic cantilevered shade planes",
    "terrace": "bold stepped monolithic strata and carved earthen/stone light-canyons with sharp shadow geometry",
    "cantilever": "razor-thin cantilevered structural trusses, floating solar-blade canopies, and dramatic suspended observation decks",
    "clustered_compound": "faceted crystalline/monolithic volumes arranged in dynamic diagonal clusters with deep-recessed apertures and sculptural shade fins",
    "bridge": "expressive long-span structural diagrid or parabolic arch spanning cleanly across terrain/water edges with minimal ground touch",
}


def build_site_prompt_text(project: dict, region_cfg: dict, hydro: str, fabric: str, sat_filename: str) -> tuple[str, str]:
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

    def _clean_prompt_text(s: str) -> str:
        s = re.sub(r"\bwind chimneys?\b", "passive roof vents", s, flags=re.I)
        s = re.sub(r"\bmuseum\b", "experience hall", s, flags=re.I)
        s = re.sub(r"\bpavilion(s)?\b", r"structure\1", s, flags=re.I)
        return s.strip()

    exp = project.get("experience_arc") or {}
    vd = project.get("visual_direction") or {}
    vols = (project.get("massing_rationale") or {}).get("volumes") or []

    arch_lang = _clean_prompt_text(
        vd.get("architectural_language")
        or exp.get("core_idea")
        or "; ".join(f"{v.get('name', 'Building')}: {v.get('shape_reason') or v.get('use', '')}" for v in vols[:4])
    )
    aerial_comp = _clean_prompt_text(
        vd.get("aerial_composition")
        or "; ".join(f"{v.get('name', 'Building')} ({v.get('role', 'Component')})" for v in vols[:4])
    )
    hero_scene = _clean_prompt_text(
        vd.get("hero_threshold_scene")
        or (f"{vols[0].get('name', title)}: {vols[0].get('shape_reason') or vols[0].get('use', '')}" if vols else concept)
    )
    lighting_mood = _clean_prompt_text(
        vd.get("lighting_mood")
        or exp.get("atmosphere")
        or "Directional late-afternoon coastal light with crisp architectural shadow relief and subtle atmospheric haze."
    )
    materials_pal = _clean_prompt_text(
        vd.get("materials_palette")
        or "Regionally authentic stone, desert-aggregate concrete, weathered timber, and native arid planting."
    )
    camera_cue = _clean_prompt_text(vd.get("camera_cue") or "")
    aerial_cam = (
        f"Camera & framing tailored to architecture: {camera_cue}."
        if camera_cue
        else "Choose an elevated oblique pitch (~35–50°) and rectilinear focal length that best showcases the masterplan geometry and surrounding fabric."
    )
    hero_cam = (
        f"human-threshold low-oblique perspective (~10–25°, {camera_cue})"
        if camera_cue
        else "human-threshold low-oblique perspective (~10–25°, lens chosen to fit the threshold depth)"
    )

    is_inland_dry = ("dry inland" in hydro.lower()) and not bool(project.get("is_water"))
    no_sea_guard = (
        " Strictly NO ocean, sea, beach, or coastal shoreline visible anywhere in foreground or distant horizon."
        if is_inland_dry
        else ""
    )
    idiom = str(project.get("idiom") or "courtyard").lower().strip()
    sculptural_form = _IDIOM_SCULPTURAL_FORMS.get(idiom, _IDIOM_SCULPTURAL_FORMS["courtyard"])
    anti_box_guard = " Strictly NO generic rectangular boxes, NO repetitive standard resort villas, NO flat-roofed strip malls."

    area_ha = project.get("area_m2", 250000) / 10000.0
    feddans = project.get("area_feddans", round(area_ha * 2.3804, 1))
    side_m = int(round(math.sqrt(max(10000.0, float(project.get("area_m2", 250000))))))

    aerial_prompt = f"""1. OPTICAL & COMPOSITION (WHOLE-SITE SCALE AERIAL):
Medium-format architectural aerial photograph (ArchDaily / Dezeen / MIR / D5 craft), 16:9 widescreen, deep f/11 focus across the entire frame. {aerial_cam} Frame the ENTIRE {feddans}-feddan (~{side_m} m x {side_m} m) red dashed polygon of `{sat_filename}` (Top = North) with generous surrounding Egyptian context.

2. LIGHT, SHADOW & ATMOSPHERE:
{lighting_mood} — natural atmospheric depth toward the horizon, crisp shadow reveals beneath roof overhangs and cantilevers.

3. TECTONIC & SCULPTURAL FORM ({title}):
- Architectural Language & Bold Silhouette: {arch_lang}. Expressive {sculptural_form}.
- Site-Wide Dispersal: {aerial_comp} — buildings are placed in the open sandy/scrub clearings across the ~{side_m} m x {side_m} m polygon, separated by restored arid native landscape, shaded paths, and public plazas.
- Materials & Scale: {materials_pal}; keep all buildings realistically scaled against the surrounding 2-story rural brick houses and agricultural plots.

4. GIS SITE REALITY & NEGATIVE GUARDRAILS:
- Strict Polygon & Fabric Preservation: Place ALL new architecture strictly INSIDE the red dashed polygon of `{sat_filename}` on open unbuilt ground; preserve existing rural brick houses/compounds both outside and along the edges of the polygon untouched, and keep arid ground natural (do NOT turn the site into a lush green park or resort lawn).
- Region ({region_cfg['region']}): {region_cfg['topography']}. {hydro} {fabric}
- Native Flora: {region_cfg['flora']}
- Forbidden: {region_cfg['forbidden']}{no_sea_guard}{tower_guard}{anti_box_guard} Strictly NO tilt-shift blur, NO text/watermarks, NO oversized mega-blocks."""

    hero_prompt = f"""1. OPTICAL & COMPOSITION (CLOSE HERO EXPERIENCE — ARRIVAL THRESHOLD):
Editorial architectural visualization (ArchDaily / Dezeen / Rendair / D5 craft), 16:9 widescreen, {hero_cam} framing the **primary architectural arrival threshold** (foreground path/steps, midground structural soffit/colonnade, and calm distant horizon). Do NOT cram multiple workshops or activities into this single frame.

2. LIGHT, SHADOW & ATMOSPHERE:
{lighting_mood} — single consistent time-of-day lighting (never mix sunset and night stars in the same frame), deep shadow reveals, and tactile surface grain.

3. TECTONIC & SCULPTURAL FORM ({title}):
- Hero Space in Focus: {hero_scene}
- Architectural Language & Bold Silhouette: {arch_lang}. Expressive {sculptural_form}. {materials_pal}, crisp structural joints, weathered textures, and a few candid visitors walking through the threshold for scale.

4. SITE REALITY & NEGATIVE GUARDRAILS:
- Anchored in the flat terrain and native flora of `{sat_filename}` ({region_cfg['region']}): {region_cfg['topography']}. {region_cfg['flora']}
- Forbidden: {region_cfg['forbidden']}{no_sea_guard}{tower_guard}{anti_box_guard} Strictly NO tilt-shift blur, NO text/watermarks, NO theme-park multi-activity collage."""

    return aerial_prompt, hero_prompt


def main():
    parser = argparse.ArgumentParser(description="Build satellite-locked architectural render pack for a NEST run.")
    parser.add_argument("--run-dir", default="outputs", help="Path to NEST run output directory (e.g., outputs or outputs_sinai)")
    parser.add_argument("--refresh-tiles", action="store_true", help="Re-download Esri satellite_lock.png even if already cached")
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
    for pattern in ("*massing_lock*.png", "site_*_satellite_lock.png", "site_*_prompt.md", "ALL_PROMPTS_CONSOLIDATED.md"):
        for stale in pack_dir.glob(pattern):
            stale.unlink()

    render_jobs: list[dict] = []

    for p in projects:
        rank = p["rank"]
        site_dir = pack_dir / f"site_{rank}"
        site_dir.mkdir(parents=True, exist_ok=True)
        sat_name = "satellite_lock.png"
        sat_path = site_dir / sat_name
        if args.refresh_tiles or not sat_path.exists():
            print(f"Fetching Esri satellite lock for Site #{rank} -> site_{rank}/{sat_path.name} ...")
            render_satellite_lock(p, sat_path)

        region_cfg = infer_region_defaults(run_dir.name, p["title"], float(p.get("lat", 0.0)), float(p.get("lon", 0.0)))
        hydro, fabric = summarize_cardinal_context(p, wat_pts, bld_pts)
        refs_dir = site_dir / "refs"
        if refs_dir.exists():
            import shutil
            shutil.rmtree(refs_dir, ignore_errors=True)
        aerial_prompt, hero_prompt = build_site_prompt_text(p, region_cfg, hydro, fabric, sat_name)

        chat_group = f"site_{rank}"
        sat_rel = f"renders/render_pack/site_{rank}/{sat_name}"
        render_jobs.append({
            "job_id": f"site_{rank}_aerial",
            "site_rank": rank,
            "site_title": p["title"],
            "chat_group": chat_group,
            "job_type": "aerial",
            "attach_image": sat_rel,
            "attach_images": [sat_rel],
            "output_file": f"renders/site_{rank}.jpg",
            "prompt": aerial_prompt,
        })
        render_jobs.append({
            "job_id": f"site_{rank}_hero",
            "site_rank": rank,
            "site_title": p["title"],
            "chat_group": chat_group,
            "job_type": "hero",
            "attach_image": None,
            "attach_images": [],
            "output_file": f"renders/site_{rank}_hero.jpg",
            "prompt": hero_prompt,
        })

        site_md = f"""# Site #{rank} Render Brief — {p['title']}

- **Target 1 (Whole-Site Scale Aerial):** `../../site_{rank}.jpg` (`16:9` widescreen · attach `./{sat_name}`)
- **Target 2 (Close Hero Experience):** `../../site_{rank}_hero.jpg` (`16:9` widescreen · attach `./{sat_name}` for context)
- **Coordinates:** `{p['lat']:.5f}, {p['lon']:.5f}` · **Boundary:** `{p.get('footprint_type', 'Contiguous')}` ({p.get('area_m2', 0)/10000:.2f} ha)

## 1. Whole-Site Scale Aerial Prompt (`../../site_{rank}.jpg`)

```text
{aerial_prompt}
```

## 2. Hero Experience Shot Prompt (`../../site_{rank}_hero.jpg`)

```text
{hero_prompt}
```
"""
        (site_dir / "prompt.md").write_text(site_md, encoding="utf-8")

    (pack_dir / "render_jobs.json").write_text(
        json.dumps(render_jobs, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Build the DEFAULT Single-Shot ChatGPT Batch Render Prompt (2 renders per site: aerial + hero)
    sat_files_plain = ", ".join(f"site_{p['rank']}/satellite_lock.png" for p in projects)
    sat_files_md = ", ".join(f"`site_{p['rank']}/satellite_lock.png`" for p in projects)
    chatgpt_lines = [
        "You are an award-winning architectural visualization photographer (ArchDaily / Dezeen / MIR / Luxigon quality).",
        f"I have attached {len(projects)} satellite site-reference images (one per site): {sat_files_plain}.",
        f"Generate ALL {len(render_jobs)} photorealistic 16:9 widescreen editorial architectural renders sequentially, ONE IMAGE AT A TIME from Job 1 through Job {len(render_jobs)} ({len(projects)} sites x 2 shots: Whole-Site Aerial + Close Hero Experience), without skipping any shot or merging two sites.",
        "",
        "GLOBAL RULES FOR ALL IMAGES:",
        "- Keep each site's two shots (Aerial + Hero) visually consistent in architecture, massing, materials, and climate—treat the Hero shot as a close-up inside/beside the exact building you just rendered in the Aerial shot.",
        "- Strictly lock each site's Aerial shot to its matching attached `site_<N>/satellite_lock.png`: match the exact red dashed boundary scale, topography, water/coast/river edge, roads, and neighboring urban/agricultural fabric (Top of satellite image = North).",
        "- Never invent hills, cliffs, mountains, turquoise ponds, lagoons, waterfalls, or European lawns where the satellite image shows flat terrain or arid desert.",
        "- Shoot every image with realistic photographic depth, natural light, zero tilt-shift miniature blur, zero HDR oversaturation, and zero text/labels/logos.",
        "- Label each generated image clearly with its Job number and target filename so I can save them directly.",
        "",
    ]
    for idx, job in enumerate(render_jobs, start=1):
        ref_note = f"Reference: {job['attach_image']}" if job.get("attach_image") else f"Reference: carry over exact architecture from site_{job['site_rank']}_aerial"
        chatgpt_lines.extend([
            f"=== JOB {idx} of {len(render_jobs)} | Site #{job['site_rank']} ({job['job_type'].upper()}) | {ref_note} | Save as: {job['output_file']} ===",
            f"Project: {job['site_title']}",
            job["prompt"],
            "",
        ])

    chatgpt_prompt_body = "\n".join(chatgpt_lines).strip()
    chatgpt_md = f"""# ChatGPT Single-Shot Render Prompt — {run_dir.name}

> **Default NEST Render Workflow (2 Renders Per Site — {len(render_jobs)} Total Shots):**
> 1. Open ChatGPT (with Image Generation enabled) and **attach all {len(projects)} satellite lock images** from this folder in one message:
>    {sat_files_md}
> 2. **Copy-paste the entire prompt block below** into the same ChatGPT message and send.
> 3. Save the generated `16:9` renders to `{run_dir.name}/renders/` using each job's `Save as:` filename (`site_<N>.jpg` and `site_<N>_hero.jpg`), then rebuild the dashboard:
>    ```bash
>    python build_nest_dashboard.py --run-dir "{run_dir}" --plot-title "{run_dir.name}"
>    ```

```text
{chatgpt_prompt_body}
```
"""
    (pack_dir / "CHATGPT_RENDER_PROMPT.md").write_text(chatgpt_md, encoding="utf-8")

    agent_instructions = f"""# Render Execution Instructions — Default Render Pack + ChatGPT Handoff

This `render_pack/` includes **`CHATGPT_RENDER_PROMPT.md`** (default single-shot ChatGPT batch prompt) and **`render_jobs.json`** ({len(render_jobs)} total jobs across `{len(projects)}` sites: 1 aerial + 1 hero per site).

## Default Workflow (Zero Auto `image-generator` Calls)
1. **Do NOT invoke built-in `image-generator` automatically** (only use it if the user explicitly asks for in-app generation).
2. **Immediately prompt the user in chat with the ChatGPT Handoff:**
   - Read `CHATGPT_RENDER_PROMPT.md` in this folder.
   - Give the user the exact list of satellite lock images to upload in one batch: {sat_files_md} (located in `{pack_dir}`).
   - Paste the **entire single-shot ChatGPT prompt** in **one copy-paste fenced code block** directly in your final response.
   - Remind the user to save ChatGPT's returned `16:9` images to `{run_dir.name}/renders/site_<N>.jpg` (aerial) and `{run_dir.name}/renders/site_<N>_hero.jpg` (hero).
3. **Rebuild Dashboard After Saving Renders:**
   `python build_nest_dashboard.py --run-dir "{run_dir}" --plot-title "{run_dir.name}"`
"""
    (pack_dir / "AGENT_INSTRUCTIONS.md").write_text(agent_instructions, encoding="utf-8")
    (run_dir / "renders" / "README.md").write_text(
        f"# Renders Entry Point — {run_dir.name}\n\n"
        f"- **Default ChatGPT Prompt (Single-Shot Batch):** `render_pack/CHATGPT_RENDER_PROMPT.md`\n"
        f"- **Job Queue:** `render_pack/render_jobs.json` ({len(render_jobs)} jobs: aerial + hero per site)\n"
        f"- **Instructions:** `render_pack/AGENT_INSTRUCTIONS.md`\n"
        f"- **When Done, Rebuild Dashboard:**\n"
        f"  ```bash\n"
        f"  python build_nest_dashboard.py --run-dir \"{run_dir}\" --plot-title \"{run_dir.name}\"\n"
        f"  ```\n",
        encoding="utf-8",
    )

    import zipfile
    zip_path = run_dir / "renders" / "render_pack.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fp in sorted(pack_dir.rglob("*")):
            if fp.is_file():
                zf.write(fp, fp.relative_to(pack_dir).as_posix())
    print(f"Render pack complete -> {pack_dir} (+ {zip_path.name})")
    print(f"ChatGPT single-shot prompt ready -> {pack_dir / 'CHATGPT_RENDER_PROMPT.md'}")


if __name__ == "__main__":
    main()
