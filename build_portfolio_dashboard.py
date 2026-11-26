#!/usr/bin/env python3
"""
NEST Multi-Plot Portfolio Dashboard Builder (`build_portfolio_dashboard.py`)
============================================================================
Mandatory when multiple plots are processed: builds a clean portfolio index
(`nest_portfolio_dashboard.html`) linking to every single-plot `nest_dashboard.html`,
with each plot card displaying its satellite image, Governorate name, and summary KPIs.

Usage:
  python build_portfolio_dashboard.py
  python build_portfolio_dashboard.py --runs outputs_nest_84_617 outputs_nest_12_683 --out nest_portfolio_dashboard.html
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
from pathlib import Path


def _infer_governorate(run_dir: Path, projects: list[dict], stage_a: dict) -> str:
    # 1. Check stage_a observed telemetry / plot_label
    plot_lbl = str(stage_a.get("plot_label") or "")
    tel = stage_a.get("observed_plot_telemetry") or {}
    gov_b = tel.get("governorate_budget") or {}
    if isinstance(gov_b, dict) and gov_b.get("governorate"):
        return str(gov_b["governorate"])

    blob = " ".join([
        run_dir.name,
        plot_lbl,
        *(str(p.get("title") or "") for p in projects),
    ]).lower()
    if "sinai" in blob or "sharm" in blob or "84_617" in blob or "83_616" in blob:
        return "South Sinai Governorate"
    if "matrouh" in blob or "alexandria" in blob or "12_683" in blob or "omayed" in blob:
        return "Alexandria / Matrouh Coast"
    if "assiut" in blob or "asyut" in blob:
        return "Assiut Governorate"
    if "red sea" in blob or "hurghada" in blob or "gouna" in blob:
        return "Red Sea Governorate"
    if "aswan" in blob:
        return "Aswan Governorate"
    if "luxor" in blob:
        return "Luxor Governorate"
    # Fallback via lat/lon
    if projects:
        lat = float(projects[0].get("lat") or 0.0)
        lon = float(projects[0].get("lon") or 0.0)
        if 27.5 <= lat <= 29.5 and 33.5 <= lon <= 35.0:
            return "South Sinai Governorate"
        if lat >= 30.5 and lon <= 30.5:
            return "Alexandria / Matrouh Coast"
        if 26.8 <= lat <= 27.6 and 30.5 <= lon <= 31.8:
            return "Assiut Governorate"
    return "Egypt National Portfolio"


def _parse_gfa_num(gfa_str: str) -> int:
    m = re.search(r"([\d,]+)", str(gfa_str or "0"))
    return int(m.group(1).replace(",", "")) if m else 0


def collect_plot_cards(run_dirs: list[Path], out_dir: Path) -> list[dict]:
    cards: list[dict] = []
    for rd in run_dirs:
        dash = rd / "nest_dashboard.html"
        pjson = rd / "stage_b_projects.json"
        if not dash.exists() or not pjson.exists():
            continue
        projects = json.loads(pjson.read_text(encoding="utf-8"))
        sa_path = rd / "intermediates" / "stage_a_summary.json"
        stage_a = json.loads(sa_path.read_text(encoding="utf-8")) if sa_path.exists() else {}

        gov = _infer_governorate(rd, projects, stage_a)
        plot_title = str(stage_a.get("plot_label") or rd.name)
        sat_rel = ""
        for cand_sat in (
            rd / "renders" / "render_pack" / "site_1_satellite_lock.png",
            rd / "renders" / "site_1_satellite_lock.png",
            rd / "renders" / "site_1.jpg",
        ):
            if cand_sat.exists():
                sat_rel = cand_sat.relative_to(out_dir).as_posix() if cand_sat.is_relative_to(out_dir) else str(cand_sat)
                break

        dash_rel = dash.relative_to(out_dir).as_posix() if dash.is_relative_to(out_dir) else str(dash)
        tot_gfa = sum(_parse_gfa_num(p.get("built_gfa", "0")) for p in projects)
        tot_fed = sum(float(p.get("area_feddans") or 0.0) for p in projects)
        cards.append({
            "run_name": rd.name,
            "plot_title": plot_title,
            "governorate": gov,
            "dash_href": dash_rel,
            "sat_src": sat_rel,
            "sites_count": len(projects),
            "total_gfa": f"{tot_gfa:,} m²",
            "total_feddans": f"{tot_fed:.1f} feddans",
            "idioms": ", ".join(dict.fromkeys(str(p.get("idiom", "")) for p in projects if p.get("idiom"))),
        })
    return cards


def build_html(cards: list[dict], title: str) -> str:
    card_html = []
    for c in cards:
        img_tag = (
            f'<img src="{html_lib.escape(c["sat_src"])}" alt="{html_lib.escape(c["plot_title"])} Satellite" />'
            if c["sat_src"]
            else '<div class="no-img">No Satellite Lock Found</div>'
        )
        card_html.append(f"""
        <a class="plot-card" href="{html_lib.escape(c['dash_href'])}">
          <div class="card-media">
            {img_tag}
            <span class="gov-pill">{html_lib.escape(c['governorate'])}</span>
          </div>
          <div class="card-body">
            <div class="plot-kicker">{html_lib.escape(c['run_name'])}</div>
            <h2 class="plot-title">{html_lib.escape(c['plot_title'])}</h2>
            <div class="metrics">
              <span><b>{c['sites_count']}</b> Sites</span>
              <span><b>{html_lib.escape(c['total_feddans'])}</b></span>
              <span><b>{html_lib.escape(c['total_gfa'])}</b> GFA</span>
            </div>
            <div class="idioms">{html_lib.escape(c['idioms'])}</div>
            <div class="cta">Open Single-Plot Dashboard →</div>
          </div>
        </a>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{html_lib.escape(title)}</title>
<style>
  :root {{ --bg:#f5f1ec; --card:#fffaf7; --ink:#2c2523; --muted:#6b5f5a; --accent:#a3473a; --border:#e5ddd5; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:Inter,system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--ink); padding:32px 24px 64px; }}
  .wrap {{ max-width:1320px; margin:0 auto; }}
  header {{ margin-bottom:28px; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:12px; border-bottom:1px solid var(--border); padding-bottom:18px; }}
  h1 {{ margin:0; font-size:26px; letter-spacing:-0.02em; }}
  .sub {{ color:var(--muted); font-size:13.5px; margin-top:4px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(360px,1fr)); gap:22px; }}
  .plot-card {{ text-decoration:none; color:inherit; background:var(--card); border:1px solid var(--border); border-radius:14px; overflow:hidden; display:flex; flex-direction:column; transition:transform .18s ease, box-shadow .18s ease; box-shadow:0 4px 16px rgba(44,37,35,0.06); }}
  .plot-card:hover {{ transform:translateY(-3px); box-shadow:0 12px 28px rgba(44,37,35,0.12); border-color:var(--accent); }}
  .card-media {{ position:relative; aspect-ratio:16/9; background:#1c1917; overflow:hidden; }}
  .card-media img {{ width:100%; height:100%; object-fit:cover; display:block; }}
  .no-img {{ color:#a8a29e; display:flex; align-items:center; justify-content:center; height:100%; font-size:13px; }}
  .gov-pill {{ position:absolute; top:12px; left:12px; background:rgba(28,25,23,0.84); color:#fff; font-size:11.5px; font-weight:600; padding:5px 10px; border-radius:999px; backdrop-filter:blur(4px); }}
  .card-body {{ padding:16px 18px 18px; display:flex; flex-direction:column; gap:8px; flex:1; }}
  .plot-kicker {{ font-size:11px; text-transform:uppercase; letter-spacing:0.06em; color:var(--muted); font-weight:600; }}
  .plot-title {{ margin:0; font-size:18px; line-height:1.25; }}
  .metrics {{ display:flex; gap:12px; flex-wrap:wrap; font-size:12.5px; color:var(--ink); background:#f5efe9; padding:7px 10px; border-radius:8px; }}
  .idioms {{ font-size:11.5px; color:var(--muted); }}
  .cta {{ margin-top:auto; padding-top:8px; font-size:13px; font-weight:600; color:var(--accent); }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>{html_lib.escape(title)}</h1>
      <div class="sub">{len(cards)} Single-Plot Dashboards · Click any plot card to open its full NEST 2.3 interactive dashboard</div>
    </div>
  </header>
  <div class="grid">
    {"".join(card_html)}
  </div>
</div>
</body>
</html>"""


def main():
    ap = argparse.ArgumentParser(description="Build Multi-Plot Portfolio Dashboard linking all single-plot NEST dashboards")
    ap.add_argument("--runs", nargs="*", type=Path, default=None, help="Run output directories (defaults to all outputs* dirs)")
    ap.add_argument("--out", type=Path, default=Path("nest_portfolio_dashboard.html"), help="Output HTML file")
    ap.add_argument("--title", type=str, default="NEST Multi-Plot Portfolio Dashboard", help="Portfolio title")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent
    out_path = args.out if args.out.is_absolute() else (root / args.out)
    run_dirs = [p if p.is_absolute() else (root / p) for p in args.runs] if args.runs else sorted(
        p for p in root.glob("outputs*") if p.is_dir()
    )

    cards = collect_plot_cards(run_dirs, out_path.parent)
    if not cards:
        raise RuntimeError("No valid plot outputs with nest_dashboard.html + stage_b_projects.json found.")
    out_path.write_text(build_html(cards, args.title), encoding="utf-8")
    print(f"[Portfolio Dashboard] Linked {len(cards)} plot dashboards -> {out_path}")


if __name__ == "__main__":
    main()
