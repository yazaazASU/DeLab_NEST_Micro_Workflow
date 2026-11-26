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

    journey_items = exp.get("journey") or []
    hero_moments_str = " | ".join(
        _clean_prompt_text(f"{m.get('moment', '')}: {m.get('detail', '')}") for m in journey_items[:2] if isinstance(m, dict)
    )
    area_ha = project.get("area_m2", 250000) / 10000.0
    feddans = project.get("area_feddans", round(area_ha * 2.3804, 1))
    side_m = int(round(math.sqrt(max(10000.0, float(project.get("area_m2", 250000))))))

    aerial_prompt = f"""1. OPTICAL & COMPOSITION (WHOLE-SITE SCALE AERIAL):
Medium-format architectural aerial photograph (ArchDaily / Dezeen / MIR / D5 craft), 16:9 widescreen, deep f/11 focus across the entire frame. {aerial_cam} Frame the ENTIRE {feddans}-feddan (~{side_m} m x {side_m} m) red dashed polygon of `{sat_filename}` (Top = North) with generous surrounding Egyptian context.

2. LIGHT, SHADOW & ATMOSPHERE:
{lighting_mood} — natural atmospheric depth toward the horizon, crisp shadow reveals beneath roof overhangs and cantilevers.

3. TECTONIC & MATERIAL CRAFT ({title}):
- Architectural Language: {arch_lang}
- Site-Wide Dispersal: {aerial_comp} — buildings are widely separated across the full ~{side_m} m x {side_m} m interior by 150–300 m of restored native landscape, shaded trails, and public plazas.
- Materials & Scale: {materials_pal}; keep all buildings realistically scaled against the surrounding 2-story rural brick houses and agricultural plots.

4. GIS SITE REALITY & NEGATIVE GUARDRAILS:
- Strict Polygon Containment: Place ALL new architecture and landscaping strictly INSIDE the red dashed polygon of `{sat_filename}`; leave every rural brick house, road, canal, and field OUTSIDE the polygon untouched.
- Region ({region_cfg['region']}): {region_cfg['topography']}. {hydro} {fabric}
- Native Flora: {region_cfg['flora']}
- Forbidden: {region_cfg['forbidden']}{tower_guard} Strictly NO tilt-shift blur, NO text/watermarks, NO oversized mega-blocks."""

    hero_prompt = f"""1. OPTICAL & COMPOSITION (CLOSE HERO EXPERIENCE):
Editorial architectural visualization (ArchDaily / Dezeen / Rendair / D5 craft), 16:9 widescreen, {hero_cam} with clear foreground (path/steps/planting), midground (hero threshold & soffits), and flat distant horizon.

2. LIGHT, SHADOW & ATMOSPHERE:
{lighting_mood} — rich interplay of directional light, deep shadow reveals, warm interior-to-exterior glow, and sensory mist or water reflections where warranted.

3. TECTONIC & MATERIAL TACTILITY ({title}):
- Hero Space in Focus: {hero_scene}
- Architectural Language & Materials: {arch_lang}. {materials_pal}, crisp structural joints, weathered textures, and candid human figures walking through the space for true scale.
- Sensory Moments Felt Here: {hero_moments_str or _clean_prompt_text(concept)}

4. SITE REALITY & NEGATIVE GUARDRAILS:
- Anchored in the flat terrain and native flora of `{sat_filename}` ({region_cfg['region']}): {region_cfg['topography']}. {region_cfg['flora']}
- Forbidden: {region_cfg['forbidden']}{tower_guard} Strictly NO tilt-shift blur, NO text/watermarks, NO cramped multi-building collage."""

    return aerial_prompt, hero_prompt


def build_moment_prompts(p: dict, region_cfg: dict, sat_name: str) -> list[tuple[int, str, str]]:
    """Build one Gemini-ready camera & lighting prompt per experience_arc.journey moment."""
    exp = p.get("experience_arc") or {}
    journey = exp.get("journey") or []
    if not journey:
        return []
    ts = p.get("thesis_summary") or {}
    gesture = ts.get("gesture_line", "") or exp.get("core_idea", "")
    atmo = exp.get("atmosphere", "") or "Warm directional sunlight with crisp architectural shadow relief."
    register = p.get("concept_register", "Regional stone & timber")
    out = []
    for idx, m in enumerate(journey, start=1):
        m_title = str(m.get("moment") or m.get("title") or f"Moment {idx}").strip()
        m_detail = str(m.get("detail") or m.get("desc") or "").strip()
        low_t = m_title.lower()
        if any(k in low_t for k in ("night", "midnight", "star", "lantern", "dusk", "twilight", "evening")):
            light_cue = "Blue-hour twilight / warm lantern glow against deep indigo sky, subtle interior illumination spilling onto stone and water."
        elif any(k in low_t for k in ("sunrise", "dawn", "morning", "breakfast")):
            light_cue = "Low golden morning sun casting long cool shadows across textured walls and native planting."
        elif any(k in low_t for k in ("sunset", "golden")):
            light_cue = "Warm amber sunset grazing across limestone, timber louvers, and water reflections."
        else:
            light_cue = "Crisp midday desert sun filtered through deep architectural overhangs, pergolas, and courtyard shade."

        prompt = f"""Continue in the same {p['title']} site chat — keep the exact same architectural massing, roof geometry, and weathered material palette ({register}: {region_cfg.get('materials', 'local stone, rammed earth, desert-aggregate concrete, and weathered timber')}) established in the aerial and hero renders above.

- Camera & Framing: Eye-level human perspective (~5–15° pitch, 28–35 mm rectilinear lens), 16:9 widescreen, candid people in motion for true scale.
- Moment #{idx} ({m_title}): {m_detail}
- Lighting & Atmosphere: {light_cue} Mood: {atmo}
- Site Guardrails ({region_cfg['region']}): {region_cfg['flora']} {region_cfg['forbidden']} Strictly NO tilt-shift blur, NO text/watermarks."""
        out.append((idx, m_title, prompt))
    return out


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
        aerial_prompt, hero_prompt = build_site_prompt_text(p, region_cfg, hydro, fabric, sat_name)
        moment_prompts = build_moment_prompts(p, region_cfg, sat_name)

        chat_group = f"site_{rank}"
        render_jobs.append({
            "job_id": f"site_{rank}_aerial",
            "site_rank": rank,
            "site_title": p["title"],
            "chat_group": chat_group,
            "job_type": "aerial",
            "attach_image": f"renders/render_pack/site_{rank}/{sat_name}",
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
            "output_file": f"renders/site_{rank}_hero.jpg",
            "prompt": hero_prompt,
        })
        for mi, mt, mp in moment_prompts:
            render_jobs.append({
                "job_id": f"site_{rank}_moment_{mi}",
                "site_rank": rank,
                "site_title": p["title"],
                "chat_group": chat_group,
                "job_type": "moment",
                "moment_index": mi,
                "moment_title": mt,
                "attach_image": None,
                "output_file": f"renders/site_{rank}_moment_{mi}.jpg",
                "prompt": mp,
            })

        moment_targets = "\n".join(
            f"- **Target {2 + mi} (Moment #{mi} — {mt}):** `../../site_{rank}_moment_{mi}.jpg` (`16:9` widescreen · attach `./{sat_name}` for regional context)"
            for mi, mt, _ in moment_prompts
        )
        moment_sections = "\n".join(
            f"\n## {2 + mi}. Moment #{mi}: {mt} (`../../site_{rank}_moment_{mi}.jpg`)\n\n```text\n{mp}\n```\n"
            for mi, mt, mp in moment_prompts
        )

        site_md = f"""# Site #{rank} Render Brief — {p['title']}

- **Target 1 (Whole-Site Scale Aerial):** `../../site_{rank}.jpg` (`16:9` widescreen · attach `./{sat_name}`)
- **Target 2 (Close Hero Experience):** `../../site_{rank}_hero.jpg` (`16:9` widescreen · attach `./{sat_name}` for context)
{moment_targets}
- **Coordinates:** `{p['lat']:.5f}, {p['lon']:.5f}` · **Boundary:** `{p.get('footprint_type', 'Contiguous')}` ({p.get('area_m2', 0)/10000:.2f} ha)

## 1. Whole-Site Scale Aerial Prompt (`../../site_{rank}.jpg`)

```text
{aerial_prompt}
```

## 2. Hero Experience Shot Prompt (`../../site_{rank}_hero.jpg`)

```text
{hero_prompt}
```
{moment_sections}"""
        (site_dir / "prompt.md").write_text(site_md, encoding="utf-8")

    (pack_dir / "render_jobs.json").write_text(
        json.dumps(render_jobs, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    agent_instructions = f"""# Render Execution Instructions (Codex / ChatGPT)

This `render_pack/` includes **`render_jobs.json`** ({len(render_jobs)} total jobs across `{len(projects)}` sites) for autonomous execution using your built-in image generation.

## Execution Rules
1. **One Image Thread / Context Per `chat_group` (`site_1`..`site_{len(projects)}`):** Keep all renders for a single site (`aerial`, `hero`, and `moment_1..N`) in one continuous generation context so they share the exact same architecture, massing, and materials.
2. **Iterate `render_jobs.json` in order:**
   - Skip any job whose `output_file` (relative to the plot's run directory, e.g. `renders/site_1.jpg`) already exists on disk.
   - When `attach_image` is set (the `aerial` job of each `chat_group`), pass `site_<N>/satellite_lock.png` as the visual reference alongside `prompt`.
   - For `hero` and `moment` jobs in the same `chat_group`, generate in the **same site context** (carrying over the architecture from `aerial`/`hero`) and save each image to `output_file` (`16:9` widescreen).
3. **Rebuild Dashboard:** After saving images, run:
   `python build_nest_dashboard.py --run-dir "{run_dir}" --plot-title "{run_dir.name}"`
"""
    (pack_dir / "AGENT_INSTRUCTIONS.md").write_text(agent_instructions, encoding="utf-8")
    (run_dir / "renders" / "README.md").write_text(
        f"# Renders Entry Point — {run_dir.name}\n\n"
        f"- **Job Queue:** `render_pack/render_jobs.json` ({len(render_jobs)} jobs)\n"
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


if __name__ == "__main__":
    main()
