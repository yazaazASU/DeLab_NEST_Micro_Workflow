#!/usr/bin/env python3
"""
NEST Native Raster Ground-Truth Reader (Zero External GIS Dependencies)
======================================================================
Reads native-resolution GeoTIFF cutouts exported in `<data_dir>/rasters/` via
`dataset-inventory.json` (ESA WorldCover 2021, Copernicus DSM 30 m, GHS_BUILT_S 100 m)
using pure Python (`struct` + `zlib` + `numpy` + `PIL`), with zero `rasterio`/`gdal` needed.

Provides:
  1. `WorldCoverSampler`: exact 10 m water (class 80) & built-up (class 50) masks.
  2. `GhsBuiltSampler`: 100 m built-up surface density (m²/cell, Mollweide EPSG:54009 or 4326).
  3. `LocalDsmSampler`: offline 30 m Copernicus DSM elevations on any `(lon, lat)` array.
"""
from __future__ import annotations

import json
import math
import struct
import zlib
from pathlib import Path

import numpy as np
from PIL import Image


def _read_tag_values(buf: bytes, endian: str, ttype: int, count: int, val_bytes: bytes):
    fmt_map = {1: ("B", 1), 2: ("c", 1), 3: ("H", 2), 4: ("I", 4), 12: ("d", 8)}
    if ttype not in fmt_map:
        return None
    ch, sz = fmt_map[ttype]
    total = count * sz
    if total <= 4:
        raw = val_bytes[:total]
    else:
        off = struct.unpack(endian + "I", val_bytes)[0]
        raw = buf[off:off + total]
    return struct.unpack(endian + ch * count, raw)


def read_geotiff_band0(tif_path: Path) -> dict:
    """Decode band 0 (and alpha if 2-band) plus ModelTiepoint, ModelPixelScale, and GeoKeys."""
    buf = tif_path.read_bytes()
    endian = "<" if buf[:2] == b"II" else ">"
    ifd_off = struct.unpack(endian + "I", buf[4:8])[0]
    n_tags = struct.unpack(endian + "H", buf[ifd_off:ifd_off + 2])[0]
    tags = {}
    for i in range(n_tags):
        entry = buf[ifd_off + 2 + i * 12:ifd_off + 14 + i * 12]
        tag, ttype, count = struct.unpack(endian + "HHI", entry[:8])
        val = _read_tag_values(buf, endian, ttype, count, entry[8:12])
        tags[tag] = val

    w = int(tags[256][0])
    h = int(tags[257][0])
    bps = tags.get(258, (8,))
    comp = int(tags.get(259, (1,))[0])
    spp = int(tags.get(277, (1,))[0])
    sfmt = tags.get(339, (1,) * spp)
    predictor = int(tags.get(317, (1,))[0])
    tie = tags.get(33922, (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    scale = tags.get(33550, (1.0, 1.0, 0.0))
    geokeys = tags.get(34735, ())

    # Map sample format + bit depth to numpy dtype
    b0_bits = int(bps[0])
    b0_fmt = int(sfmt[0]) if len(sfmt) > 0 else 1
    if b0_fmt == 3 and b0_bits == 32:
        dt = np.dtype(endian + "f4")
    elif b0_fmt == 3 and b0_bits == 64:
        dt = np.dtype(endian + "f8")
    elif b0_fmt == 2 and b0_bits == 16:
        dt = np.dtype(endian + "i2")
    elif b0_bits == 16:
        dt = np.dtype(endian + "u2")
    else:
        dt = np.dtype(endian + "u1")

    # Fast path for single-band/PA uint8 via Pillow when readable
    band0 = np.zeros((h, w), dtype=dt)
    alpha = np.full((h, w), 255, dtype=np.uint8)

    if 324 in tags and 325 in tags:
        tw = int(tags[322][0])
        th = int(tags[323][0])
        offs = tags[324]
        cnts = tags[325]
        nx_t = math.ceil(w / tw)
        for tidx, (toff, tcnt) in enumerate(zip(offs, cnts)):
            raw = buf[toff:toff + tcnt]
            if comp == 8:
                raw = zlib.decompress(raw)
            elif comp != 1:
                raise RuntimeError(f"Unsupported TIFF compression {comp} in {tif_path.name}")
            arr = np.frombuffer(raw, dtype=dt).reshape((th, tw, spp))
            if predictor == 2:
                arr = np.cumsum(arr, axis=1, dtype=dt)
            ty, tx = divmod(tidx, nx_t)
            y0, x0 = ty * th, tx * tw
            y1, x1 = min(y0 + th, h), min(x0 + tw, w)
            band0[y0:y1, x0:x1] = arr[:y1 - y0, :x1 - x0, 0]
            if spp >= 2:
                alpha[y0:y1, x0:x1] = arr[:y1 - y0, :x1 - x0, -1].astype(np.uint8)
    elif 273 in tags and 279 in tags:
        rps = int(tags.get(278, (h,))[0])
        offs = tags[273]
        cnts = tags[279]
        for sidx, (soff, scnt) in enumerate(zip(offs, cnts)):
            raw = buf[soff:soff + scnt]
            if comp == 8:
                raw = zlib.decompress(raw)
            y0 = sidx * rps
            y1 = min(y0 + rps, h)
            arr = np.frombuffer(raw, dtype=dt).reshape((y1 - y0, w, spp))
            if predictor == 2:
                arr = np.cumsum(arr, axis=1, dtype=dt)
            band0[y0:y1, :] = arr[:, :, 0]
            if spp >= 2:
                alpha[y0:y1, :] = arr[:, :, -1].astype(np.uint8)
    else:
        im = Image.open(tif_path)
        arr = np.asarray(im)
        if arr.ndim == 3:
            band0 = arr[:, :, 0]
            alpha = arr[:, :, -1]
        else:
            band0 = arr

    is_mollweide = False
    if geokeys and len(geokeys) >= 4:
        # Check ProjectedCSTypeGeoKey (3072) or string
        for idx in range(4, len(geokeys) - 3, 4):
            if geokeys[idx] == 3072 and geokeys[idx + 3] == 54009:
                is_mollweide = True

    return {
        "band0": band0,
        "alpha": alpha,
        "w": w,
        "h": h,
        "tie_x": float(tie[3]),
        "tie_y": float(tie[4]),
        "scale_x": float(scale[0]),
        "scale_y": float(scale[1]),
        "is_mollweide": is_mollweide,
    }


def _lonlat_to_mollweide(lon_deg: np.ndarray, lat_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """WGS84 (lon, lat) -> World Mollweide (ESRI:54009) meters."""
    R = 6371007.181
    lam = np.radians(lon_deg)
    phi = np.radians(lat_deg)
    theta = phi.copy()
    target = math.pi * np.sin(phi)
    for _ in range(8):
        denom = 2.0 + 2.0 * np.cos(2.0 * theta)
        dth = -(2.0 * theta + np.sin(2.0 * theta) - target) / np.where(np.abs(denom) < 1e-12, 1e-12, denom)
        theta = theta + dth
    x = R * (2.0 * math.sqrt(2.0) / math.pi) * lam * np.cos(theta)
    y = R * math.sqrt(2.0) * np.sin(theta)
    return x, y


class RasterBundle:
    """Optional native raster ground-truth bundle loaded from `<data_dir>/dataset-inventory.json`."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.worldcover = None
        self.ghs_built = None
        self.dsm = None
        inv_path = self.data_dir / "dataset-inventory.json"
        if not inv_path.exists():
            return
        try:
            inv = json.loads(inv_path.read_text(encoding="utf-8"))
        except Exception:
            return
        items = inv if isinstance(inv, list) else inv.get("datasets", inv.get("layers", []))
        for item in items:
            if item.get("type") != "raster" or item.get("status") != "exported":
                continue
            rel = item.get("file") or ""
            fpath = self.data_dir / rel
            if not fpath.exists():
                continue
            nm = str(item.get("name") or "").lower()
            try:
                if "worldcover" in nm and self.worldcover is None:
                    self.worldcover = read_geotiff_band0(fpath)
                elif "ghs_built_s_e2025" in nm and self.ghs_built is None:
                    d = read_geotiff_band0(fpath)
                    d["is_mollweide"] = True
                    self.ghs_built = d
                elif "copernicus dsm 30 m" in nm and self.dsm is None:
                    self.dsm = read_geotiff_band0(fpath)
            except Exception as e:
                print(f"  [RasterGroundTruth] Skipping {fpath.name}: {e}")

    def _sample_nearest(self, r: dict, lon: np.ndarray, lat: np.ndarray):
        if r.get("is_mollweide"):
            px_coord, py_coord = _lonlat_to_mollweide(lon, lat)
        else:
            px_coord, py_coord = lon, lat
        ix = np.floor((px_coord - r["tie_x"]) / r["scale_x"]).astype(np.int32)
        iy = np.floor((r["tie_y"] - py_coord) / r["scale_y"]).astype(np.int32)
        valid = (ix >= 0) & (ix < r["w"]) & (iy >= 0) & (iy < r["h"])
        ixc = np.clip(ix, 0, r["w"] - 1)
        iyc = np.clip(iy, 0, r["h"] - 1)
        vals = r["band0"][iyc, ixc]
        alp = r["alpha"][iyc, ixc] > 0
        return vals, valid & alp

    def sample_water_built_masks(self, lon: np.ndarray, lat: np.ndarray) -> tuple[np.ndarray | None, np.ndarray | None]:
        """Return (is_water_wc, is_built_wc_or_ghs) aligned to input lon/lat arrays, or None if unavailable."""
        is_water = None
        is_built = None
        if self.worldcover is not None:
            wc_val, wc_ok = self._sample_nearest(self.worldcover, lon, lat)
            is_water = wc_ok & (wc_val == 80)
            is_built = wc_ok & (wc_val == 50)
        if self.ghs_built is not None:
            ghs_val, ghs_ok = self._sample_nearest(self.ghs_built, lon, lat)
            ghs_built = ghs_ok & (ghs_val != 65535) & (ghs_val >= 350)
            is_built = ghs_built if is_built is None else (is_built | ghs_built)
        return is_water, is_built

    def sample_dsm(self, lon: np.ndarray, lat: np.ndarray) -> np.ndarray | None:
        if self.dsm is None:
            return None
        vals, ok = self._sample_nearest(self.dsm, lon, lat)
        arr = vals.astype(np.float64)
        arr[~ok] = np.nan
        return arr


if __name__ == "__main__":
    import sys
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("NOV26 TESTS/NEST--12-683 GIS")
    rb = RasterBundle(d)
    print("Loaded:", {k: (v["w"], v["h"], v["is_mollweide"]) if v else None for k, v in [("worldcover", rb.worldcover), ("ghs_built", rb.ghs_built), ("dsm", rb.dsm)]})
    # Test Site 3 highway/compound coordinate (30.8974, 29.4088) vs sea (30.899, 29.408)
    lons = np.array([29.4088, 29.4080, 29.3854, 29.4005])
    lats = np.array([30.8974, 30.8992, 30.8588, 30.8644])
    w_m, b_m = rb.sample_water_built_masks(lons, lats)
    dsm_m = rb.sample_dsm(lons, lats)
    print("Water:", w_m, "| Built:", b_m, "| DSM:", dsm_m)
