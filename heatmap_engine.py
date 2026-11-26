"""
NEST Stage A Spatial Heatmap Engine (`heatmap_engine.py`)
Zero-external-GIS-dependency implementation using numpy, shapely, sqlite3, and stdlib.
Supports both `*_all_layers.geojson` and `*.gpkg` + `Layer export inventory.csv`.
"""

from __future__ import annotations

import csv
import glob
import json
import math
import os
import re
import sqlite3
import struct
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from shapely import wkb
from shapely.geometry import MultiPolygon, Point, Polygon, shape
from shapely.ops import unary_union


FORCE_NAMES: List[str] = [
    "Hydrology & Waterfront",
    "Solar & Climate Intensity",
    "Biodiversity & Ecology",
    "Heritage & Culture Gravity",
    "Civic & Service Deficit",
    "Corridor & Network Connectivity",
]

DEFAULT_EFF_RATIOS: Dict[str, float] = {
    "Hydrology & Waterfront": 0.76,
    "Solar & Climate Intensity": 0.78,
    "Biodiversity & Ecology": 0.75,
    "Heritage & Culture Gravity": 0.74,
    "Civic & Service Deficit": 0.73,
    "Corridor & Network Connectivity": 0.75,
    "Mixed-Use": 0.72,
}


class LocalProjection:
    """Fast local tangent-plane metric projection centered on plot centroid (lon0, lat0)."""

    def __init__(self, lon0: float, lat0: float) -> None:
        self.lon0 = float(lon0)
        self.lat0 = float(lat0)
        self.kx = 111320.0 * math.cos(math.radians(self.lat0))
        self.ky = 110540.0

    def to_xy(self, lon: float, lat: float) -> Tuple[float, float]:
        return (lon - self.lon0) * self.kx, (lat - self.lat0) * self.ky

    def to_ll(self, x: float, y: float) -> Tuple[float, float]:
        return self.lon0 + x / self.kx, self.lat0 + y / self.ky

    def geom_to_xy(self, geom: Any) -> Any:
        from shapely.ops import transform

        return transform(lambda x, y, z=None: ((x - self.lon0) * self.kx, (y - self.lat0) * self.ky), geom)

    def geom_to_ll(self, geom: Any) -> Any:
        from shapely.ops import transform

        return transform(lambda x, y, z=None: (self.lon0 + x / self.kx, self.lat0 + y / self.ky), geom)

    # Aliases expected by stage_b_builder.py / rhino_massing_engine.py
    def to_meters(self, lon: float, lat: float) -> Tuple[float, float]:
        return self.to_xy(lon, lat)

    def to_wgs84(self, x: float, y: float) -> Tuple[float, float]:
        return self.to_ll(x, y)

    def geom_to_meters(self, geom: Any) -> Any:
        return self.geom_to_xy(geom)

    def geom_to_wgs84(self, geom: Any) -> Any:
        return self.geom_to_ll(geom)

    def geom_to_lonlat(self, geom: Any) -> Any:
        return self.geom_to_ll(geom)

    def to_lonlat(self, x: float, y: float) -> Tuple[float, float]:
        return self.to_ll(x, y)


@dataclass
class FactorRule:
    factor_id: str
    criterion: str
    filter_expr: str
    method: str
    radius_m: float
    weight: float


@dataclass
class EngineConfig:
    engine_name: str
    factors_by_force: Dict[str, List[FactorRule]] = field(default_factory=dict)
    whitelist_pairs: List[Tuple[str, str]] = field(default_factory=list)


def _strip_md_code(s: str) -> str:
    return s.strip().strip("`").strip()


def parse_typology_config(md_path: str, engine_name: str = "") -> EngineConfig:
    """Parse a `*_nature_forces.md` config into force factor tables and compatibility whitelist."""
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cfg = EngineConfig(engine_name=engine_name or os.path.basename(md_path))
    current_force: Optional[str] = None
    in_whitelist = False

    for raw in lines:
        line = raw.strip()
        if line.startswith("### Typology:"):
            current_force = line.split(":", 1)[1].strip()
            cfg.factors_by_force.setdefault(current_force, [])
            in_whitelist = False
            continue
        if line.startswith("## ") and "Compatibility Whitelist" in line:
            in_whitelist = True
            current_force = None
            continue
        if line.startswith("## ") and "Compatibility Whitelist" not in line:
            in_whitelist = False
            current_force = None
            continue

        if not line.startswith("|") or line.startswith("| :---") or line.startswith("|---"):
            continue

        parts = [p.strip() for p in line.strip("|").split("|")]
        if in_whitelist and len(parts) >= 2:
            a, b = parts[0], parts[1]
            if a.lower() in ("typology a", "force a") or not a:
                continue
            cfg.whitelist_pairs.append((a, b))
        elif current_force and len(parts) >= 6:
            fid = parts[0]
            if fid.lower() in ("factor id", "id") or not fid:
                continue
            try:
                radius = float(re.sub(r"[^\d.]", "", parts[4]) or "500")
                weight = float(re.sub(r"[^\d.]", "", parts[5]) or "0.33")
            except ValueError:
                radius, weight = 500.0, 0.33
            cfg.factors_by_force[current_force].append(
                FactorRule(
                    factor_id=fid,
                    criterion=parts[1],
                    filter_expr=_strip_md_code(parts[2]),
                    method=parts[3].strip().lower(),
                    radius_m=radius,
                    weight=weight,
                )
            )
    return cfg


def parse_efficiency_ratios(md_path: str) -> Dict[str, float]:
    ratios = dict(DEFAULT_EFF_RATIOS)
    if not os.path.exists(md_path):
        return ratios
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    current: Optional[str] = None
    for line in text.splitlines():
        m = re.match(r"^##\s+\d+\.\s+(.+)$", line.strip())
        if m:
            current = m.group(1).strip()
            if current.startswith("Mixed-Use"):
                current = "Mixed-Use"
            continue
        if current and "Efficiency Ratio" in line:
            pm = re.search(r"(\d+(?:\.\d+)?)\s*%", line)
            if pm:
                ratios[current] = float(pm.group(1)) / 100.0
    return ratios


def _decode_gpkg_geom(blob: bytes) -> Optional[Any]:
    if not blob or len(blob) < 8 or blob[:2] != b"GP":
        return None
    flags = blob[3]
    envelope_indicator = (flags >> 1) & 0x07
    envelope_sizes = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}
    header_len = 8 + envelope_sizes.get(envelope_indicator, 0)
    if len(blob) <= header_len:
        return None
    try:
        return wkb.loads(blob[header_len:])
    except Exception:
        return None


def _load_gpkg_layers(gpkg_path: str, inventory_csv: Optional[str]) -> List[Dict[str, Any]]:
    table_to_name: Dict[str, str] = {}
    if inventory_csv and os.path.exists(inventory_csv):
        with open(inventory_csv, "r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                out = (row.get("output") or "").strip()
                name = (row.get("name") or "").strip()
                if "layername=" in out and name:
                    tbl = out.split("layername=", 1)[1].strip()
                    table_to_name[tbl] = name

    features: List[Dict[str, Any]] = []
    conn = sqlite3.connect(gpkg_path)
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM gpkg_contents WHERE data_type='features'")
    tables = [r[0] for r in cur.fetchall()]

    for tbl in tables:
        if tbl == "plot_boundary":
            continue
        cur.execute("SELECT column_name FROM gpkg_geometry_columns WHERE table_name=?", (tbl,))
        gcol_row = cur.fetchone()
        gcol = gcol_row[0] if gcol_row else "geom"

        cur.execute(f'PRAGMA table_info("{tbl}")')
        cols = [c[1] for c in cur.fetchall()]
        if gcol not in cols:
            continue

        attr_cols = [c for c in cols if c != gcol]
        col_sql = ", ".join([f'"{c}"' for c in [gcol] + attr_cols])
        try:
            cur.execute(f'SELECT {col_sql} FROM "{tbl}"')
        except Exception:
            continue

        human_name = table_to_name.get(tbl, tbl)
        for row in cur.fetchall():
            geom = _decode_gpkg_geom(row[0])
            if geom is None or geom.is_empty:
                continue
            props: Dict[str, Any] = {"source_layer": human_name, "_table": tbl}
            for idx, cname in enumerate(attr_cols, start=1):
                props[cname] = row[idx]
            features.append({"geometry": geom, "properties": props})

    conn.close()
    return features


def load_plot_gis(data_dir: str) -> Tuple[Any, List[Dict[str, Any]], Dict[str, Any]]:
    """Load plot boundary geometry, all vector features, and optional dataset inventory/summary."""
    b_files = sorted(glob.glob(os.path.join(data_dir, "*boundary*.geojson")))
    if not b_files:
        raise FileNotFoundError(f"No boundary.geojson found in {data_dir}")

    with open(b_files[0], "r", encoding="utf-8") as f:
        b_data = json.load(f)
    b_geoms = [shape(feat["geometry"]) for feat in b_data.get("features", []) if feat.get("geometry")]
    if not b_geoms:
        raise ValueError(f"Empty boundary in {b_files[0]}")
    boundary_ll = unary_union(b_geoms)

    features: List[Dict[str, Any]] = []
    all_layers = sorted(glob.glob(os.path.join(data_dir, "*_all_layers.geojson")))
    if all_layers:
        with open(all_layers[0], "r", encoding="utf-8") as f:
            raw = json.load(f)
        for feat in raw.get("features", []):
            if feat.get("geometry"):
                features.append(
                    {
                        "geometry": shape(feat["geometry"]),
                        "properties": feat.get("properties") or {},
                    }
                )
    else:
        gpkgs = sorted(glob.glob(os.path.join(data_dir, "*.gpkg")))
        if not gpkgs:
            raise FileNotFoundError(f"No *_all_layers.geojson or *.gpkg found in {data_dir}")
        inv_csv = os.path.join(data_dir, "Layer export inventory.csv")
        features = _load_gpkg_layers(gpkgs[0], inv_csv if os.path.exists(inv_csv) else None)

    meta: Dict[str, Any] = {}
    for mf in ("export_summary.json", "dataset-inventory.json"):
        mp = os.path.join(data_dir, mf)
        if os.path.exists(mp):
            with open(mp, "r", encoding="utf-8") as f:
                meta[mf] = json.load(f)

    return boundary_ll, features, meta


def _match_clause(props: Dict[str, Any], clause: str) -> bool:
    """Match a single `source_layer=X;fclass=a,b` clause against feature properties."""
    src = str(props.get("source_layer") or props.get("_table") or "").lower()
    fclass = str(props.get("fclass") or props.get("type") or props.get("amenity") or "").lower()
    subparts = [s.strip() for s in clause.split(";") if s.strip()]
    for sp in subparts:
        if "=" not in sp:
            continue
        k, v = sp.split("=", 1)
        k = k.strip().lower()
        v_norm = v.strip().lower()
        if k == "source_layer":
            # Normalize dashes/underscores for resilient matching between GPKG inventory and MD
            src_clean = re.sub(r"[\s_\-—]+", " ", src)
            v_clean = re.sub(r"[\s_\-—]+", " ", v_norm)
            if v_clean not in src_clean and v_norm not in src:
                return False
        elif k == "fclass":
            allowed = {x.strip() for x in v_norm.split(",") if x.strip()}
            if fclass and fclass not in allowed:
                return False
    return True


def filter_features(features: Sequence[Dict[str, Any]], group_expr: str) -> List[Dict[str, Any]]:
    clauses = [c.strip() for c in re.split(r"\s+OR\s+", group_expr, flags=re.I) if c.strip()]
    out: List[Dict[str, Any]] = []
    for feat in features:
        props = feat["properties"]
        if any(_match_clause(props, cl) for cl in clauses):
            out.append(feat)
    return out


def _sample_points_from_geoms(geoms: Sequence[Any], step_m: float = 75.0, max_pts: int = 2500) -> np.ndarray:
    pts: List[Tuple[float, float]] = []
    for g in geoms:
        if g is None or g.is_empty:
            continue
        gtype = g.geom_type
        if gtype == "Point":
            pts.append((g.x, g.y))
        elif gtype == "MultiPoint":
            for p in g.geoms:
                pts.append((p.x, p.y))
        elif gtype in ("LineString", "LinearRing"):
            L = max(g.length, 1.0)
            n = max(2, min(40, int(L / step_m) + 1))
            for i in range(n):
                p = g.interpolate(i / max(1, n - 1), normalized=True)
                pts.append((p.x, p.y))
        elif gtype == "MultiLineString":
            for line in g.geoms:
                L = max(line.length, 1.0)
                n = max(2, min(25, int(L / step_m) + 1))
                for i in range(n):
                    p = line.interpolate(i / max(1, n - 1), normalized=True)
                    pts.append((p.x, p.y))
        elif gtype in ("Polygon", "MultiPolygon"):
            polys = [g] if gtype == "Polygon" else list(g.geoms)
            for poly in polys:
                c = poly.representative_point()
                pts.append((c.x, c.y))
                ext = poly.exterior
                L = max(ext.length, 1.0)
                n = max(4, min(36, int(L / step_m) + 1))
                for i in range(n):
                    p = ext.interpolate(i / max(1, n - 1), normalized=True)
                    pts.append((p.x, p.y))
        if len(pts) >= max_pts:
            break
    if not pts:
        return np.empty((0, 2), dtype=np.float64)
    return np.asarray(pts[:max_pts], dtype=np.float64)


def min_dist_to_points(grid_xy: np.ndarray, pts_xy: np.ndarray, chunk: int = 2048) -> np.ndarray:
    """Compute Euclidean distance from each grid cell (M, 2) to nearest point in pts_xy (N, 2)."""
    m = grid_xy.shape[0]
    if pts_xy.shape[0] == 0:
        return np.full(m, 1e6, dtype=np.float64)
    out = np.full(m, 1e6, dtype=np.float64)
    for i in range(0, m, chunk):
        g = grid_xy[i : i + chunk]
        # (chunk, 1, 2) - (1, N, 2)
        d2 = np.sum((g[:, None, :] - pts_xy[None, :, :]) ** 2, axis=2)
        out[i : i + chunk] = np.sqrt(np.min(d2, axis=1))
    return out


def kde_surface(grid_xy: np.ndarray, pts_xy: np.ndarray, sigma_m: float, chunk: int = 1024) -> np.ndarray:
    m = grid_xy.shape[0]
    if pts_xy.shape[0] == 0:
        return np.zeros(m, dtype=np.float64)
    inv_2s2 = 1.0 / (2.0 * max(sigma_m, 25.0) ** 2)
    out = np.zeros(m, dtype=np.float64)
    for i in range(0, m, chunk):
        g = grid_xy[i : i + chunk]
        d2 = np.sum((g[:, None, :] - pts_xy[None, :, :]) ** 2, axis=2)
        out[i : i + chunk] = np.sum(np.exp(-d2 * inv_2s2), axis=1)
    mx = float(np.max(out))
    return out / mx if mx > 1e-9 else out


def score_factor(
    grid_xy: np.ndarray,
    features_xy: Sequence[Dict[str, Any]],
    rule: FactorRule,
) -> Tuple[np.ndarray, int]:
    """Evaluate a single FactorRule on grid_xy, returning normalized [0, 1] array and matched count."""
    m = grid_xy.shape[0]
    method = rule.method
    r = max(rule.radius_m, 50.0)

    if " AND " in rule.filter_expr and method in ("ecotone_gradient", "corridor_bridge"):
        g_a_expr, g_b_expr = re.split(r"\s+AND\s+", rule.filter_expr, maxsplit=1, flags=re.I)
        feats_a = filter_features(features_xy, g_a_expr)
        feats_b = filter_features(features_xy, g_b_expr)
        pts_a = _sample_points_from_geoms([f["geometry"] for f in feats_a])
        pts_b = _sample_points_from_geoms([f["geometry"] for f in feats_b])
        if pts_a.shape[0] == 0 or pts_b.shape[0] == 0:
            return np.zeros(m, dtype=np.float64), 0
        da = np.exp(-min_dist_to_points(grid_xy, pts_a) / r)
        db = np.exp(-min_dist_to_points(grid_xy, pts_b) / r)
        return np.sqrt(da * db), len(feats_a) + len(feats_b)

    feats = filter_features(features_xy, rule.filter_expr)
    pts = _sample_points_from_geoms([f["geometry"] for f in feats])
    if pts.shape[0] == 0:
        if method == "inverse_decay":
            return np.ones(m, dtype=np.float64), 0
        if method == "service_gap":
            return np.full(m, 0.75, dtype=np.float64), 0
        return np.zeros(m, dtype=np.float64), 0

    if method == "kde":
        return kde_surface(grid_xy, pts, r), len(feats)

    d = min_dist_to_points(grid_xy, pts)
    if method == "decay":
        return np.exp(-d / r), len(feats)
    if method == "inverse_decay":
        return 1.0 - np.exp(-d / r), len(feats)
    if method == "service_gap":
        return 1.0 - np.exp(-d / r), len(feats)
    if method == "ring_decay":
        r_peak = 0.55 * r
        sigma = 0.45 * r
        return np.exp(-((d - r_peak) ** 2) / (2.0 * sigma * sigma)), len(feats)
    if method in ("ecotone_gradient", "corridor_bridge"):
        return np.exp(-d / r), len(feats)
    return np.exp(-d / r), len(feats)


def write_geotiff_float32(path: str, arr2d: np.ndarray, lon_min: float, lat_max: float, px_lon: float, px_lat: float) -> None:
    """Write a minimal uncompressed Float32 GeoTIFF (EPSG:4326) with zero external dependencies."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    h, w = arr2d.shape
    data = np.asarray(arr2d, dtype="<f4").tobytes()

    # Standard TIFF + GeoTIFF tags (ModelPixelScaleTag=33550, ModelTiepointTag=33922, GeoKeyDirectoryTag=34735)
    pixel_scale = struct.pack("<3d", px_lon, px_lat, 0.0)
    tiepoint = struct.pack("<6d", 0.0, 0.0, 0.0, lon_min, lat_max, 0.0)
    geokeys = struct.pack("<16H", 1, 1, 0, 3, 1024, 0, 1, 2, 1025, 0, 1, 1, 2048, 0, 1, 4326)

    ifd_count = 13
    ifd_offset = 8
    after_ifd = ifd_offset + 2 + ifd_count * 12 + 4

    off_bps = after_ifd
    off_scale = off_bps + 0  # single SHORT fits inline
    off_tie = off_scale + len(pixel_scale)
    off_geo = off_tie + len(tiepoint)
    off_data = off_geo + len(geokeys)

    def tag(t: int, typ: int, cnt: int, val: int) -> bytes:
        return struct.pack("<HHII", t, typ, cnt, val)

    entries = [
        tag(256, 4, 1, w),               # ImageWidth
        tag(257, 4, 1, h),               # ImageLength
        tag(258, 3, 1, 32),              # BitsPerSample
        tag(259, 3, 1, 1),               # Compression = None
        tag(262, 3, 1, 1),               # Photometric = MinIsBlack
        tag(273, 4, 1, off_data),        # StripOffsets
        tag(277, 3, 1, 1),               # SamplesPerPixel
        tag(278, 4, 1, h),               # RowsPerStrip
        tag(279, 4, 1, len(data)),       # StripByteCounts
        tag(339, 3, 1, 3),               # SampleFormat = IEEEFP
        tag(33550, 12, 3, off_scale),    # ModelPixelScaleTag
        tag(33922, 12, 6, off_tie),      # ModelTiepointTag
        tag(34735, 3, 16, off_geo),      # GeoKeyDirectoryTag
    ]

    with open(path, "wb") as f:
        f.write(b"II" + struct.pack("<HI", 42, ifd_offset))
        f.write(struct.pack("<H", ifd_count))
        for e in entries:
            f.write(e)
        f.write(struct.pack("<I", 0))
        f.write(pixel_scale)
        f.write(tiepoint)
        f.write(geokeys)
        f.write(data)
