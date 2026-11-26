#!/usr/bin/env python3
"""
NEST Rhino (.3dm) Massing & Aerial 3D Clay-Lock Engine
======================================================
Massing-First (Geometry-Locked) 3D generator for NEST Stage B & Stage C.

Generates for each NEST proposal:
  1. Structured Rhino 8 (.3dm) model in local meters (origin 0,0,0 at site centroid,
     with WGS84 lat/lon & CRS anchor stored in Document UserStrings):
       - 00_SITE_BOUNDARY            (50-70 feddan outer boundary curve)
       - 01_LANDSCAPE_ZONES::L-01..  (validated planar zone meshes + boundaries + metadata)
       - 02_BUILDING_MASSING::...    (idiom-aware 3D Brep/Extrusion/Mesh volumes scaled to GFA)
       - 03_GIS_CONTEXT::Water/Roads/Context_Buildings
       - 04_MAP_POINTERS             (3D TextDots for GIS drivers)
  2. Crisp 16:9 Aerial 3D Clay/Shaded Massing Lock (`site_<N>_massing_lock.png`)
     designed to be passed alongside `site_<N>_satellite_lock.png` into `image-generator`
     so editorial renders lock 1:1 to the Rhino massing and 50-70 feddan landscape zones.

Modes:
  --mode concept   (Stage B default): Clean conceptual massing for all 5 sites
  --mode detailed  (Stage C upgrade): Adds floor plates, vertical cores & structural canopy ribs

Usage:
  python rhino_massing_engine.py --project-json outputs_aswan/exports/project_1_.../project_data.json
  python rhino_massing_engine.py --run-dir outputs_aswan --gis-layers "10 PLOT TEST/Aswan.../engine-input.geojson"
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import rhino3dm as r3d
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, shape, box
from shapely.ops import triangulate, unary_union

from heatmap_engine import LocalProjection


# ---------------------------------------------------------------------------
# Color & Parsing Helpers
# ---------------------------------------------------------------------------
def hex_to_rgba(hex_str: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = (hex_str or "#625753").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return (120, 110, 105, alpha)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def hex_to_rgb01(hex_str: str) -> tuple[float, float, float]:
    r, g, b, _ = hex_to_rgba(hex_str)
    return (r / 255.0, g / 255.0, b / 255.0)


def parse_m2_number(text: Any) -> float:
    if isinstance(text, (int, float)):
        return float(text)
    if not text:
        return 0.0
    m = re.search(r"([\d,]+(?:\.\d+)?)", str(text))
    if not m:
        return 0.0
    return float(m.group(1).replace(",", ""))


def classify_idiom(idiom_str: str, is_water: bool = False) -> str:
    s = (idiom_str or "").lower()
    if "canop" in s or "vault" in s or "dome" in s or "arcade" in s:
        return "canopy"
    if "vertical" in s or "tower" in s or "biophilic" in s or "sky" in s:
        return "vertical"
    if "hydrolog" in s or "water" in s or "floating" in s or "pier" in s or "tidal" in s or is_water:
        return "hydrological"
    if "shell" in s or "tensile" in s or "parametric" in s or "dune" in s:
        return "shell"
    return "landform"


def polygon_list_from_geom(geom) -> list[Polygon]:
    if geom is None or geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return [g for g in geom.geoms if not g.is_empty and g.area > 1.0]
    return []


def project_geojson_geom(geojson_obj: dict, proj: LocalProjection):
    if not geojson_obj:
        return None
    g = shape(geojson_obj)
    if not g.is_valid:
        g = g.buffer(0)
    return proj.geom_to_meters(g)


# ---------------------------------------------------------------------------
# Rhino Layer & Geometry Primitives
# ---------------------------------------------------------------------------
class RhinoLayerManager:
    def __init__(self, model: r3d.File3dm):
        self.model = model
        self.cache: dict[str, int] = {}

    def ensure(self, path: str, color_rgba: tuple[int, int, int, int] = (180, 180, 180, 255)) -> int:
        if path in self.cache:
            return self.cache[path]
        parts = path.split("::")
        parent_id = None
        acc = []
        idx = 0
        for i, part in enumerate(parts):
            acc.append(part)
            key = "::".join(acc)
            if key in self.cache:
                idx = self.cache[key]
                parent_id = self.model.Layers[idx].Id
                continue
            lay = r3d.Layer()
            lay.Name = part[:64]
            if i == len(parts) - 1:
                lay.Color = color_rgba
            else:
                lay.Color = (90, 90, 95, 255)
            if parent_id is not None:
                lay.ParentLayerId = parent_id
            idx = self.model.Layers.Add(lay)
            self.cache[key] = idx
            parent_id = self.model.Layers[idx].Id
        return idx


def ring_to_polyline_curve(coords: list[tuple[float, float]], z: float = 0.0) -> r3d.PolylineCurve:
    pts = [r3d.Point3d(float(x), float(y), float(z)) for x, y in coords]
    if len(pts) >= 2 and (abs(pts[0].X - pts[-1].X) > 1e-6 or abs(pts[0].Y - pts[-1].Y) > 1e-6):
        pts.append(r3d.Point3d(pts[0].X, pts[0].Y, float(z)))
    return r3d.PolylineCurve(pts)


def polygon_to_rhino_planar_mesh(poly: Polygon, z: float = 0.0) -> r3d.Mesh | None:
    if poly is None or poly.is_empty or poly.area < 1.0:
        return None
    tris = [t for t in triangulate(poly) if t.representative_point().within(poly)]
    if not tris:
        return None
    mesh = r3d.Mesh()
    v_idx = 0
    for tri in tris:
        coords = list(tri.exterior.coords)[:3]
        if len(coords) < 3:
            continue
        for x, y in coords:
            mesh.Vertices.Add(float(x), float(y), float(z))
        mesh.Faces.AddFace(v_idx, v_idx + 1, v_idx + 2)
        v_idx += 3
    if v_idx == 0:
        return None
    mesh.Normals.ComputeNormals()
    return mesh


def add_extruded_poly(
    model: r3d.File3dm,
    poly: Polygon,
    z_base: float,
    height: float,
    layer_idx: int,
    name: str,
    user_strings: dict[str, str] | None = None,
    clay_faces: list | None = None,
    clay_color: tuple[float, float, float] = (0.91, 0.88, 0.84),
):
    if poly is None or poly.is_empty or poly.area < 2.0 or height <= 0.1:
        return
    # Simplify slightly for crisp Rhino geometry
    p_clean = poly.simplify(0.4, preserve_topology=True)
    if p_clean.is_empty or not isinstance(p_clean, Polygon):
        p_clean = poly
    coords = list(p_clean.exterior.coords)
    if len(coords) < 4:
        return
    crv = ring_to_polyline_curve(coords, z=z_base)
    ext = r3d.Extrusion.Create(crv, float(height), True)
    if ext is not None:
        attr = r3d.ObjectAttributes()
        attr.LayerIndex = layer_idx
        attr.Name = name
        if user_strings:
            for k, v in user_strings.items():
                attr.SetUserString(str(k), str(v))
        model.Objects.AddExtrusion(ext, attr)

    if clay_faces is not None:
        _append_extrusion_clay_faces(p_clean, z_base, height, clay_faces, clay_color)


def _append_extrusion_clay_faces(
    poly: Polygon,
    z0: float,
    h: float,
    clay_faces: list,
    base_rgb: tuple[float, float, float],
):
    z1 = z0 + h
    coords = list(poly.exterior.coords)
    # Side walls
    for i in range(len(coords) - 1):
        x0, y0 = coords[i][0], coords[i][1]
        x1, y1 = coords[i + 1][0], coords[i + 1][1]
        if math.hypot(x1 - x0, y1 - y0) < 0.2:
            continue
        quad = [(x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1)]
        clay_faces.append((quad, base_rgb))
    # Roof cap (triangulated for non-convex polygons)
    roof_rgb = tuple(min(1.0, c * 1.05) for c in base_rgb)
    tris = [t for t in triangulate(poly) if t.representative_point().within(poly)]
    for tri in tris:
        tc = list(tri.exterior.coords)[:3]
        if len(tc) == 3:
            clay_faces.append(([(tc[0][0], tc[0][1], z1), (tc[1][0], tc[1][1], z1), (tc[2][0], tc[2][1], z1)], roof_rgb))


def add_arched_shell_mesh(
    model: r3d.File3dm,
    poly: Polygon,
    z_base: float,
    rise: float,
    layer_idx: int,
    name: str,
    clay_faces: list | None = None,
    clay_color: tuple[float, float, float] = (0.86, 0.80, 0.72),
):
    """Create a smooth parametric dome/vault shell mesh spanning the polygon's oriented bounding box."""
    mrr = poly.minimum_rotated_rectangle
    coords = list(mrr.exterior.coords)[:4]
    if len(coords) < 4:
        return
    p0 = np.array(coords[0])
    u_vec = np.array(coords[1]) - p0
    v_vec = np.array(coords[3]) - p0
    nu, nv = 12, 8
    mesh = r3d.Mesh()
    grid_pts = []
    for i in range(nu + 1):
        u = i / nu
        row = []
        for j in range(nv + 1):
            v = j / nv
            xy = p0 + u * u_vec + v * v_vec
            arch = math.sin(math.pi * u) * math.sin(math.pi * v)
            z = z_base + rise * (0.25 + 0.75 * arch)
            mesh.Vertices.Add(float(xy[0]), float(xy[1]), float(z))
            row.append((float(xy[0]), float(xy[1]), float(z)))
        grid_pts.append(row)
    for i in range(nu):
        for j in range(nv):
            a = i * (nv + 1) + j
            b = (i + 1) * (nv + 1) + j
            c = (i + 1) * (nv + 1) + (j + 1)
            d = i * (nv + 1) + (j + 1)
            mesh.Faces.AddFace(a, b, c, d)
            if clay_faces is not None:
                clay_faces.append(([grid_pts[i][j], grid_pts[i + 1][j], grid_pts[i + 1][j + 1], grid_pts[i][j + 1]], clay_color))
    mesh.Normals.ComputeNormals()
    attr = r3d.ObjectAttributes()
    attr.LayerIndex = layer_idx
    attr.Name = name
    model.Objects.AddMesh(mesh, attr)


# ---------------------------------------------------------------------------
# Idiom-Aware Parametric Massing Builder
# ---------------------------------------------------------------------------
def build_idiom_massing(
    model: r3d.File3dm,
    layers: RhinoLayerManager,
    poly: Polygon,
    label: str,
    target_gfa: float,
    idiom_key: str,
    mode: str,
    clay_faces: list,
    is_water: bool = False,
):
    area = max(poly.area, 1.0)
    est_floors = max(1, min(8, int(round(target_gfa / area)))) if target_gfa > 0 else 2
    floor_h = 4.2
    total_h = max(6.0, min(34.0, est_floors * floor_h))
    z0 = 2.2 if is_water else 0.0

    safe_name = re.sub(r"[^A-Za-z0-9_\- ]+", "", label).strip()[:42] or "Pavilion"
    lay_idx = layers.ensure(f"02_BUILDING_MASSING::{safe_name}", (215, 198, 180, 255))
    meta = {
        "program": label,
        "footprint_m2": f"{area:.0f}",
        "target_gfa_m2": f"{target_gfa:.0f}",
        "est_floors": str(est_floors),
        "idiom": idiom_key,
    }

    if idiom_key == "canopy":
        # Grounded stone pavilions + sweeping overhanging perforated solar canopy
        pav_h = max(6.5, min(14.0, total_h * 0.72))
        add_extruded_poly(model, poly, z0, pav_h, lay_idx, f"{safe_name}_Volume", meta, clay_faces, (0.91, 0.87, 0.82))
        canopy_poly = poly.buffer(min(14.0, math.sqrt(area) * 0.14), join_style=2)
        canopy_lay = layers.ensure("02_BUILDING_MASSING::Mega_Canopy", (186, 150, 122, 255))
        canopy_z = z0 + pav_h + 3.5
        add_extruded_poly(
            model, canopy_poly, canopy_z, 1.4, canopy_lay, f"{safe_name}_Canopy",
            {"role": "Perforated Solar/Microclimate Canopy", "clearance_m": f"{canopy_z:.1f}"},
            clay_faces, (0.78, 0.65, 0.54),
        )
        # Support columns along perimeter
        col_lay = layers.ensure("02_BUILDING_MASSING::Structure", (130, 120, 112, 255))
        perim = poly.exterior
        n_cols = max(6, min(16, int(perim.length / 26.0)))
        for k in range(n_cols):
            pt = perim.interpolate(k / n_cols, normalized=True)
            col_poly = pt.buffer(0.85, resolution=4)
            add_extruded_poly(model, col_poly, z0, canopy_z - z0, col_lay, f"{safe_name}_Col_{k+1}", None, clay_faces, (0.62, 0.58, 0.55))

    elif idiom_key == "vertical":
        # Stacked terraced podium + mid-rise + sky-court setback + thermal-chimney accent
        h1 = max(5.0, total_h * 0.35)
        add_extruded_poly(model, poly, z0, h1, lay_idx, f"{safe_name}_Podium", meta, clay_faces, (0.90, 0.86, 0.81))
        mid = poly.buffer(-min(8.0, math.sqrt(area) * 0.12))
        for mp in polygon_list_from_geom(mid):
            h2 = max(6.0, total_h * 0.45)
            add_extruded_poly(model, mp, z0 + h1, h2, lay_idx, f"{safe_name}_MidTier", meta, clay_faces, (0.93, 0.90, 0.86))
            top = mp.buffer(-min(6.0, math.sqrt(mp.area) * 0.18))
            for tp in polygon_list_from_geom(top):
                h3 = max(5.0, total_h * 0.35)
                add_extruded_poly(model, tp, z0 + h1 + h2, h3, lay_idx, f"{safe_name}_Crown", meta, clay_faces, (0.85, 0.78, 0.70))

    elif idiom_key == "hydrological":
        # Stepped water-edge deck / micro-pile plinth + tiered sculptural pavilion
        deck_poly = poly.buffer(min(10.0, math.sqrt(area) * 0.12), join_style=2)
        deck_lay = layers.ensure("02_BUILDING_MASSING::Hydrological_Deck", (165, 148, 130, 255))
        add_extruded_poly(model, deck_poly, max(0.4, z0 - 0.8), 1.4, deck_lay, f"{safe_name}_Deck", {"role": "Micro-Pile Waterfront / Wadi Terrace"}, clay_faces, (0.76, 0.71, 0.65))
        h1 = max(5.0, total_h * 0.55)
        add_extruded_poly(model, poly, z0 + 0.6, h1, lay_idx, f"{safe_name}_LowerTier", meta, clay_faces, (0.91, 0.88, 0.84))
        upper = poly.buffer(-min(7.0, math.sqrt(area) * 0.14))
        for up in polygon_list_from_geom(upper):
            add_extruded_poly(model, up, z0 + 0.6 + h1, max(4.2, total_h * 0.45), lay_idx, f"{safe_name}_UpperTier", meta, clay_faces, (0.87, 0.82, 0.76))

    elif idiom_key == "shell":
        # Sculpted plinth + parametric vaulted shell roof
        base_h = max(4.5, total_h * 0.45)
        add_extruded_poly(model, poly, z0, base_h, lay_idx, f"{safe_name}_Plinth", meta, clay_faces, (0.90, 0.87, 0.82))
        shell_lay = layers.ensure("02_BUILDING_MASSING::Parametric_Shell", (205, 184, 160, 255))
        add_arched_shell_mesh(model, poly, z0 + base_h, max(5.5, total_h * 0.65), shell_lay, f"{safe_name}_Shell", clay_faces, (0.85, 0.78, 0.70))

    else:
        # Carved Landform & Geological Monumentality: stepped sandstone/earth-bermed plinths
        plinth = poly.buffer(min(8.0, math.sqrt(area) * 0.10), join_style=2)
        add_extruded_poly(model, plinth, z0, 3.6, lay_idx, f"{safe_name}_LandformPlinth", {"role": "Carved Earth-Bermed Plinth"}, clay_faces, (0.84, 0.77, 0.69))
        h_main = max(5.5, total_h * 0.65)
        add_extruded_poly(model, poly, z0 + 3.6, h_main, lay_idx, f"{safe_name}_Monolith", meta, clay_faces, (0.91, 0.87, 0.81))
        crown = poly.buffer(-min(7.0, math.sqrt(area) * 0.15))
        for cp in polygon_list_from_geom(crown):
            add_extruded_poly(model, cp, z0 + 3.6 + h_main, max(4.0, total_h * 0.30), lay_idx, f"{safe_name}_TerraceCrown", meta, clay_faces, (0.88, 0.83, 0.77))

    # Stage C Detailed Mode upgrades: floor plates + vertical circulation core
    if mode == "detailed":
        slab_lay = layers.ensure("02_BUILDING_MASSING::Floor_Plates", (150, 155, 165, 255))
        core_lay = layers.ensure("02_BUILDING_MASSING::Cores", (163, 71, 58, 255))
        for fl in range(1, est_floors + 1):
            zf = z0 + fl * floor_h
            if zf < z0 + total_h - 0.5:
                add_extruded_poly(model, poly.buffer(-0.4), zf, 0.35, slab_lay, f"{safe_name}_Floor_{fl}", {"level": str(fl)}, None)
        c_pt = poly.representative_point()
        core_r = max(3.0, min(7.0, math.sqrt(area) * 0.08))
        core_box = box(c_pt.x - core_r, c_pt.y - core_r, c_pt.x + core_r, c_pt.y + core_r)
        add_extruded_poly(model, core_box, z0, total_h + 2.5, core_lay, f"{safe_name}_Core", {"role": "Vertical Circulation & MEP Core"}, clay_faces, (0.64, 0.28, 0.23))


# ---------------------------------------------------------------------------
# 16:9 Aerial 3D Clay/Shaded Massing Lock Renderer
# ---------------------------------------------------------------------------
def shade_face(verts: list[tuple[float, float, float]], base_rgb: tuple[float, float, float]) -> tuple[float, float, float, float]:
    v0 = np.array(verts[0], dtype=float)
    v1 = np.array(verts[1], dtype=float)
    v2 = np.array(verts[2], dtype=float)
    n = np.cross(v1 - v0, v2 - v0)
    norm = np.linalg.norm(n)
    if norm < 1e-8:
        n = np.array([0.0, 0.0, 1.0])
    else:
        n = n / norm
    if n[2] < 0 and abs(n[2]) > 0.8:
        n = -n
    # Warm SW sun direction
    sun = np.array([-0.52, -0.58, 0.63])
    sun = sun / np.linalg.norm(sun)
    ndotl = max(0.0, float(np.dot(n, sun)))
    sky = 0.35 + 0.65 * max(0.0, float(n[2]))
    intensity = 0.42 + 0.48 * ndotl + 0.14 * sky
    r = min(1.0, base_rgb[0] * intensity)
    g = min(1.0, base_rgb[1] * intensity)
    b = min(1.0, base_rgb[2] * intensity)
    return (r, g, b, 1.0)


def render_clay_massing_lock(
    out_png: Path,
    project: dict,
    site_poly_m,
    zone_polys: list[tuple[str, Polygon, str]],
    clay_faces: list[tuple[list[tuple[float, float, float]], tuple[float, float, float]]],
    context_water: list[Polygon],
    context_roads: list,
    context_bldgs: list[Polygon],
    elev: float = 42.0,
    azim: float = -52.0,
):
    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor="#F5F3EF")
    ax = fig.add_subplot(111, projection="3d", facecolor="#F5F3EF")
    fig.subplots_adjust(left=0.0, right=1.0, top=0.97, bottom=0.07)

    minx, miny, maxx, maxy = site_poly_m.bounds
    span = max(maxx - minx, maxy - miny, 260.0)
    pad = span * 0.28
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0
    half = span / 2.0 + pad

    # 1. Ground plane
    gp = [[(cx - half, cy - half, -0.4), (cx + half, cy - half, -0.4), (cx + half, cy + half, -0.4), (cx - half, cy + half, -0.4)]]
    ax.add_collection3d(Poly3DCollection(gp, facecolors="#ECE7DF", edgecolors="none", zorder=0))

    # 2. Context water
    water_tris = []
    for wp in context_water:
        clipped = wp.intersection(box(cx - half, cy - half, cx + half, cy + half))
        for p in polygon_list_from_geom(clipped):
            for t in triangulate(p):
                if t.representative_point().within(p):
                    tc = list(t.exterior.coords)[:3]
                    water_tris.append([(tc[0][0], tc[0][1], -0.15), (tc[1][0], tc[1][1], -0.15), (tc[2][0], tc[2][1], -0.15)])
    if water_tris:
        ax.add_collection3d(Poly3DCollection(water_tris, facecolors="#9FC3D6", edgecolors="none", alpha=0.82))

    # 3. Landscape zones (L-01..L-0N)
    for zid, zpoly, zcol in zone_polys:
        z_tris = []
        for t in triangulate(zpoly):
            if t.representative_point().within(zpoly):
                tc = list(t.exterior.coords)[:3]
                z_tris.append([(tc[0][0], tc[0][1], 0.05), (tc[1][0], tc[1][1], 0.05), (tc[2][0], tc[2][1], 0.05)])
        if z_tris:
            ax.add_collection3d(Poly3DCollection(z_tris, facecolors=zcol, edgecolors="none", alpha=0.36))
        xc, yc = zpoly.exterior.xy
        ax.plot(xc, yc, zs=0.12, color=zcol, linewidth=1.1, alpha=0.8)

    # 4. Context roads
    clip_b = box(cx - half, cy - half, cx + half, cy + half)
    for rd in context_roads:
        cr = rd.intersection(clip_b)
        lines = [cr] if isinstance(cr, LineString) else (list(cr.geoms) if isinstance(cr, MultiLineString) else [])
        for ln in lines:
            rx, ry = ln.xy
            ax.plot(rx, ry, zs=0.08, color="#B8B0A6", linewidth=1.2, alpha=0.75)

    # 5. Context buildings (low neutral clay)
    ctx_faces = []
    for cb in context_bldgs[:120]:
        _append_extrusion_clay_faces(cb, 0.0, 9.0, ctx_faces, (0.82, 0.80, 0.77))
    if ctx_faces:
        ax.add_collection3d(Poly3DCollection(
            [f[0] for f in ctx_faces],
            facecolors=[shade_face(f[0], f[1]) for f in ctx_faces],
            edgecolors="#B0A89E",
            linewidths=0.15,
            alpha=0.72,
        ))

    # 6. Outer 50-70 feddan Site Boundary (dashed)
    for sp in polygon_list_from_geom(site_poly_m):
        sx, sy = sp.exterior.xy
        ax.plot(sx, sy, zs=0.35, color="#A3473A", linewidth=2.2, linestyle="--")

    # 7. Primary Building Massing (shaded architectural clay)
    if clay_faces:
        ax.add_collection3d(Poly3DCollection(
            [f[0] for f in clay_faces],
            facecolors=[shade_face(f[0], f[1]) for f in clay_faces],
            edgecolors="#6E6259",
            linewidths=0.32,
        ))

    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_zlim(0, max(65.0, half * 0.45))
    ax.set_box_aspect((1.0, 1.0, 0.24))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()

    # Clean NEST title footer + North cue
    area_m2 = float(project.get("area_m2") or site_poly_m.area)
    feddans = float(project.get("area_feddans") or (area_m2 / 4200.833))
    gfa = project.get("built_gfa") or "N/A"
    idiom = project.get("idiom") or "Regenerative Monumentality"
    fig.text(
        0.02, 0.028,
        f"NEST 3D MASSING LOCK  |  Site #{project.get('rank', 1)}: {project.get('title', 'Proposal')}",
        fontsize=11.5, fontweight="bold", color="#302B2A",
    )
    fig.text(
        0.02, 0.008,
        f"Site: {area_m2:,.0f} m² ({feddans:.1f} feddans)  •  Built GFA: {gfa}  •  Idiom: {idiom}  •  Camera: Aerial {elev:.0f}°  •  N ↑",
        fontsize=9.2, color="#625753",
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=100, facecolor="#F5F3EF")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main Project Builder
# ---------------------------------------------------------------------------
def build_rhino_and_clay_for_project(
    project: dict,
    out_3dm: Path,
    out_clay_png: Path,
    gis_features_raw: list[dict] | None = None,
    mode: str = "concept",
    elev: float = 42.0,
) -> dict:
    site_ll = shape(project["geojson"])
    if not site_ll.is_valid:
        site_ll = site_ll.buffer(0)
    c_ll = site_ll.centroid
    proj = LocalProjection(c_ll.x, c_ll.y)
    site_m = proj.geom_to_meters(site_ll)

    model = r3d.File3dm()
    model.Settings.ModelUnitSystem = r3d.UnitSystem.Meters
    area_m2 = float(project.get("area_m2") or site_m.area)
    area_feddans = float(project.get("area_feddans") or (area_m2 / 4200.833))

    # Document UserStrings for GIS/Grasshopper geolocation
    model.Strings["NEST_PROJECT_TITLE"] = str(project.get("title", "NEST Proposal"))
    model.Strings["NEST_RANK"] = str(project.get("rank", 1))
    model.Strings["NEST_ORIGIN_LON"] = f"{c_ll.x:.6f}"
    model.Strings["NEST_ORIGIN_LAT"] = f"{c_ll.y:.6f}"
    model.Strings["NEST_CRS"] = "EPSG:4326"
    model.Strings["NEST_UNITS"] = "Meters (Local Origin 0,0,0 at Site Centroid)"
    model.Strings["NEST_SITE_AREA_M2"] = f"{area_m2:.0f}"
    model.Strings["NEST_SITE_AREA_FEDDANS"] = f"{area_feddans:.2f}"
    model.Strings["NEST_BUILT_GFA"] = str(project.get("built_gfa", ""))
    model.Strings["NEST_TECTONIC_IDIOM"] = str(project.get("idiom", ""))
    model.Strings["NEST_MODE"] = mode

    layers = RhinoLayerManager(model)
    clay_faces: list[tuple[list[tuple[float, float, float]], tuple[float, float, float]]] = []

    # 1. Outer 50-70 Feddan Site Boundary
    b_lay = layers.ensure("00_SITE_BOUNDARY", (163, 71, 58, 255))
    for sp in polygon_list_from_geom(site_m):
        crv = ring_to_polyline_curve(list(sp.exterior.coords), z=0.0)
        attr = r3d.ObjectAttributes()
        attr.LayerIndex = b_lay
        attr.Name = f"Site_{project.get('rank', 1)}_Boundary"
        attr.SetUserString("area_m2", f"{area_m2:.0f}")
        attr.SetUserString("area_feddans", f"{area_feddans:.2f}")
        model.Objects.AddCurve(crv, attr)

    # 2. Landscape Zones (L-01..L-0N)
    zone_polys_for_clay: list[tuple[str, Polygon, str]] = []
    l_zones = project.get("landscape_zones") or []
    if l_zones:
        for z in l_zones:
            zid = str(z.get("id") or "L-01")
            zname = str(z.get("name") or "Landscape Zone")
            zcol = str(z.get("color") or "#4D8B6F")
            zgeom = project_geojson_geom(z.get("geom"), proj)
            z_lay = layers.ensure(f"01_LANDSCAPE_ZONES::{zid}_{re.sub(r'[^A-Za-z0-9]+', '_', zname)[:24]}", hex_to_rgba(zcol))
            for zp in polygon_list_from_geom(zgeom):
                zone_polys_for_clay.append((zid, zp, zcol))
                mesh = polygon_to_rhino_planar_mesh(zp, z=0.02)
                attr = r3d.ObjectAttributes()
                attr.LayerIndex = z_lay
                attr.Name = f"{zid}_{zname}"
                for k in ("id", "name", "family", "intervention", "area_m2", "area_feddans", "share_pct"):
                    if k in z and z[k] is not None:
                        attr.SetUserString(k, str(z[k]))
                if mesh is not None:
                    model.Objects.AddMesh(mesh, attr)
                model.Objects.AddCurve(ring_to_polyline_curve(list(zp.exterior.coords), z=0.05), attr)
    else:
        # Graceful fallback for legacy project JSONs without landscape_zones[]
        z_lay = layers.ensure("01_LANDSCAPE_ZONES::L-01_Site_Landscape_Envelope", (77, 139, 111, 255))
        for sp in polygon_list_from_geom(site_m):
            zone_polys_for_clay.append(("L-01", sp, "#5A8F73"))
            mesh = polygon_to_rhino_planar_mesh(sp, z=0.02)
            attr = r3d.ObjectAttributes()
            attr.LayerIndex = z_lay
            attr.Name = "L-01_Site_Landscape_Envelope"
            attr.SetUserString("status", "Default envelope (pre-landscape-zoning legacy JSON)")
            if mesh is not None:
                model.Objects.AddMesh(mesh, attr)

    # 3. Building Massing (Idiom-Aware Parametric Geometry)
    idiom_key = classify_idiom(project.get("idiom", ""), bool(project.get("is_water", False)))
    footprints = project.get("footprints") or []
    total_built_gfa = parse_m2_number(project.get("built_gfa"))
    fp_items = []
    for fp in footprints:
        fg = project_geojson_geom(fp.get("geom"), proj)
        polys = polygon_list_from_geom(fg)
        if not polys:
            continue
        lbl = str(fp.get("label") or "Building")
        gfa_from_lbl = parse_m2_number(lbl)
        fp_items.append((lbl, polys, gfa_from_lbl))

    total_fp_area = sum(p.area for _, ps, _ in fp_items for p in ps) or 1.0
    for lbl, polys, gfa_hint in fp_items:
        for p in polys:
            if gfa_hint > 200:
                part_gfa = gfa_hint * (p.area / max(sum(x.area for x in polys), 1.0))
            elif total_built_gfa > 0:
                part_gfa = total_built_gfa * (p.area / total_fp_area)
            else:
                part_gfa = p.area * 2.0
            build_idiom_massing(
                model=model,
                layers=layers,
                poly=p,
                label=lbl,
                target_gfa=part_gfa,
                idiom_key=idiom_key,
                mode=mode,
                clay_faces=clay_faces,
                is_water=bool(project.get("is_water", False)),
            )

    # 4. GIS Context (Water, Roads, Context Buildings within 750 m)
    ctx_water: list[Polygon] = []
    ctx_roads: list = []
    ctx_bldgs: list[Polygon] = []
    if gis_features_raw:
        minx, miny, maxx, maxy = site_m.bounds
        clip_m = box(minx - 500, miny - 500, maxx + 500, maxy + 500)
        w_lay = layers.ensure("03_GIS_CONTEXT::Water", (56, 152, 204, 255))
        r_lay = layers.ensure("03_GIS_CONTEXT::Roads", (145, 140, 134, 255))
        cb_lay = layers.ensure("03_GIS_CONTEXT::Context_Buildings", (185, 180, 174, 255))

        for feat in gis_features_raw:
            props = feat.get("properties") or {}
            sl = str(props.get("source_layer") or props.get("layer") or "").lower()
            fc = str(props.get("fclass") or "").lower()
            try:
                gm = project_geojson_geom(feat.get("geometry"), proj)
            except Exception:
                continue
            if gm is None or gm.is_empty or not gm.intersects(clip_m):
                continue
            clipped = gm.intersection(clip_m)

            if any(k in sl or k in fc for k in ("water", "nile", "نهر", "river", "lake")):
                for wp in polygon_list_from_geom(clipped):
                    ctx_water.append(wp)
                    mesh = polygon_to_rhino_planar_mesh(wp, z=-0.1)
                    if mesh is not None:
                        attr = r3d.ObjectAttributes()
                        attr.LayerIndex = w_lay
                        model.Objects.AddMesh(mesh, attr)
            elif any(k in sl or k in fc for k in ("road", "طرق", "highway", "street")):
                lines = [clipped] if isinstance(clipped, LineString) else (list(clipped.geoms) if isinstance(clipped, MultiLineString) else [])
                for ln in lines:
                    ctx_roads.append(ln)
                    pts = [r3d.Point3d(float(x), float(y), 0.05) for x, y in ln.coords]
                    if len(pts) >= 2:
                        attr = r3d.ObjectAttributes()
                        attr.LayerIndex = r_lay
                        model.Objects.AddCurve(r3d.PolylineCurve(pts), attr)
            elif any(k in sl or k in fc for k in ("building", "مبان", "osm_buildings")):
                for bp in polygon_list_from_geom(clipped):
                    if bp.intersects(site_m):
                        continue
                    ctx_bldgs.append(bp)
                    if len(ctx_bldgs) <= 200:
                        add_extruded_poly(model, bp, 0.0, 9.0, cb_lay, "Context_Building", None, None)

    # 5. Map Pointers (3D TextDots)
    pt_lay = layers.ensure("04_MAP_POINTERS", (255, 97, 76, 255))
    for ptr in project.get("map_pointers") or []:
        if "lat" in ptr and "lon" in ptr:
            px, py = proj.to_meters(float(ptr["lon"]), float(ptr["lat"]))
            dot = r3d.TextDot(f"#{ptr.get('id', '')} {ptr.get('label', '')}", r3d.Point3d(px, py, 14.0))
            attr = r3d.ObjectAttributes()
            attr.LayerIndex = pt_lay
            attr.Name = f"Pointer_{ptr.get('id', '')}"
            attr.SetUserString("role", str(ptr.get("role", "")))
            model.Objects.AddTextDot(dot, attr)

    out_3dm.parent.mkdir(parents=True, exist_ok=True)
    ok = model.Write(str(out_3dm), 8)
    if not ok:
        raise RuntimeError(f"Failed to write Rhino .3dm file: {out_3dm}")

    render_clay_massing_lock(
        out_png=out_clay_png,
        project=project,
        site_poly_m=site_m,
        zone_polys=zone_polys_for_clay,
        clay_faces=clay_faces,
        context_water=ctx_water,
        context_roads=ctx_roads,
        context_bldgs=ctx_bldgs,
        elev=elev,
    )

    return {
        "rank": project.get("rank", 1),
        "title": project.get("title", ""),
        "mode": mode,
        "idiom_key": idiom_key,
        "rhino_3dm": str(out_3dm),
        "massing_lock_png": str(out_clay_png),
        "layers_count": len(model.Layers),
        "objects_count": len(model.Objects),
    }


def load_projects_from_run_dir(run_dir: Path) -> list[dict]:
    sb = run_dir / "stage_b_projects.json"
    if sb.exists():
        return json.loads(sb.read_text(encoding="utf-8"))
    exports_dir = run_dir / "exports"
    projects = []
    if exports_dir.exists():
        for pj in sorted(exports_dir.glob("*/project_data.json")):
            projects.append(json.loads(pj.read_text(encoding="utf-8")))
    if not projects:
        dash = run_dir / "nest_dashboard.html"
        if dash.exists():
            html = dash.read_text(encoding="utf-8")
            m = re.search(r"const NEST_PROJECTS\s*=\s*(\[.*?\]);", html, re.S)
            if m:
                projects = json.loads(m.group(1))
    projects.sort(key=lambda x: x.get("rank", 99))
    return projects


def main():
    ap = argparse.ArgumentParser(description="NEST Rhino (.3dm) Massing & 16:9 Aerial Clay-Lock Generator")
    ap.add_argument("--project-json", type=Path, help="Single project_data.json file")
    ap.add_argument("--run-dir", type=Path, help="NEST run output directory (processes all 5 sites)")
    ap.add_argument("--gis-layers", type=Path, help="Optional *_all_layers.geojson / engine-input.geojson for 3D GIS context")
    ap.add_argument("--data-dir", type=Path, help="Optional GIS plot folder")
    ap.add_argument("--out-dir", type=Path, help="Override output directory for single project mode")
    ap.add_argument("--mode", choices=["concept", "detailed"], default="concept", help="Stage B concept vs Stage C detailed")
    ap.add_argument("--elev", type=float, default=42.0, help="Aerial camera elevation pitch in degrees (default 42)")
    args = ap.parse_args()

    gis_raw = None
    if args.gis_layers and args.gis_layers.exists():
        gis_raw = json.loads(args.gis_layers.read_text(encoding="utf-8")).get("features", [])

    if args.project_json:
        proj = json.loads(args.project_json.read_text(encoding="utf-8"))
        rank = proj.get("rank", 1)
        base = args.out_dir or args.project_json.parent
        out_3dm = base / "models" / f"site_{rank}_massing{'_detailed' if args.mode == 'detailed' else ''}.3dm"
        out_png = base / "render" / f"site_{rank}_massing_lock.png"
        res = build_rhino_and_clay_for_project(proj, out_3dm, out_png, gis_features_raw=gis_raw, mode=args.mode, elev=args.elev)
        print(json.dumps(res, indent=2))
        return

    if args.run_dir:
        projects = load_projects_from_run_dir(args.run_dir)
        results = []
        for proj in projects:
            rank = proj.get("rank", 1)
            out_3dm = args.run_dir / "models" / f"site_{rank}_massing{'_detailed' if args.mode == 'detailed' else ''}.3dm"
            out_png = args.run_dir / "renders" / "render_pack" / f"site_{rank}_massing_lock.png"
            res = build_rhino_and_clay_for_project(proj, out_3dm, out_png, gis_features_raw=gis_raw, mode=args.mode, elev=args.elev)
            clean_png = out_png.with_name(out_png.stem + "_clean.png")
            if out_png.exists() and not clean_png.exists():
                import shutil
                shutil.copy2(out_png, clean_png)
            results.append(res)
            print(f"  [Site #{rank}] {res['idiom_key']} -> {out_3dm.name} ({res['objects_count']} objs, {res['layers_count']} layers) + {out_png.name}")
        return

    ap.error("Provide either --project-json or --run-dir")


if __name__ == "__main__":
    main()
