#!/usr/bin/env python3
"""
Retroactively enrich all existing runs under Outputs/All_Plots/ with dual-channel
NEST-Portable-RAG-v3 citations (codes/* + ref/*) in a SINGLE batched E5 model load,
update stage_b_projects.json, NEST_Executive_Report.md, and intermediates/agent_site_context.md,
rebuild all nest_dashboard.html files, and verify every dashboard with `node --check`.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from nest_rag_client import (
    batch_dual_search,
    build_stage_a_queries,
    build_stage_b_queries,
    format_stage_a_rag_markdown,
    format_stage_b_rag_markdown,
)
from run_nest_pipeline import verify_dashboard_js


def _replace_or_append_section(md_text: str, heading: str, new_block: str) -> str:
    pattern = re.compile(rf"\n---\n\n{re.escape(heading)}[\s\S]*\Z")
    if pattern.search(md_text):
        return pattern.sub("\n" + new_block, md_text)
    return md_text.rstrip() + "\n\n" + new_block + "\n"


def _update_report_with_rag(rep_path: Path, projects: list[dict]) -> None:
    if not rep_path.exists():
        return
    txt = rep_path.read_text(encoding="utf-8")
    # Remove any prior RAG subsections so reruns are idempotent
    txt = re.sub(
        r"\n### Cited Egyptian Codes & Architectural Precedents \*\(RAG Reference\)\*[\s\S]*?(?=\n---|\n## Site #|\Z)",
        "",
        txt,
    )
    # Insert each project's RAG block right before the next `---` / `## Site #` or EOF
    parts = re.split(r"(?=\n## Site #\d+:)", txt)
    out_parts = [parts[0]]
    by_rank = {int(p["rank"]): p for p in projects}
    for part in parts[1:]:
        m = re.match(r"\n## Site #(\d+):", part)
        if m and int(m.group(1)) in by_rank:
            p = by_rank[int(m.group(1))]
            rag_lines = format_stage_b_rag_markdown(p.get("rag_citations"))
            if rag_lines:
                # Insert before trailing `---` if present
                if "\n---\n" in part:
                    idx = part.rfind("\n---\n")
                    part = part[:idx].rstrip() + "\n" + "\n".join(rag_lines) + "\n" + part[idx:]
                else:
                    part = part.rstrip() + "\n" + "\n".join(rag_lines) + "\n"
        out_parts.append(part)
    rep_path.write_text("".join(out_parts), encoding="utf-8")


def main() -> None:
    all_plots_dir = ROOT / "Outputs" / "All_Plots"
    plot_dirs = sorted(d for d in all_plots_dir.iterdir() if d.is_dir() and (d / "stage_b_projects.json").exists())
    print(f"[Enrich All Plots] Found {len(plot_dirs)} plots in {all_plots_dir}")

    # Collect ALL Stage B project queries + Stage A candidate queries in ONE batch!
    batch_items: list[dict] = []
    plot_projects: dict[str, list[dict]] = {}
    plot_stage_a: dict[str, list[dict]] = {}

    for pdir in plot_dirs:
        pname = pdir.name
        projs = json.loads((pdir / "stage_b_projects.json").read_text(encoding="utf-8"))
        plot_projects[pname] = projs
        for p in projs:
            cq, rq = build_stage_b_queries(p, pname)
            batch_items.append({"key": f"B::{pname}::{p['rank']}", "code_query": cq, "ref_query": rq})

        sa_p = pdir / "intermediates" / "stage_a_summary.json"
        if sa_p.exists():
            sa = json.loads(sa_p.read_text(encoding="utf-8"))
            cands = (sa.get("candidate_pool") or sa.get("top_5_candidates") or [])[:6]
            plot_stage_a[pname] = cands
            for c in cands:
                cq, rq = build_stage_a_queries(c, pname)
                batch_items.append({"key": f"A::{pname}::{c.get('site_rank')}", "code_query": cq, "ref_query": rq})

    print(f"[Enrich All Plots] Running single batched E5 dual-channel search for {len(batch_items)} queries...")
    results = batch_dual_search(batch_items, k_codes=3, k_refs=3)
    if not results:
        raise SystemExit("RAG batch_dual_search returned empty results!")
    by_key = {r["key"]: r for r in results}

    for pdir in plot_dirs:
        pname = pdir.name
        projs = plot_projects[pname]
        for p in projs:
            hit = by_key.get(f"B::{pname}::{p['rank']}")
            if hit:
                p["rag_citations"] = {
                    "codes": hit.get("codes") or [],
                    "precedents": hit.get("precedents") or [],
                }
        (pdir / "stage_b_projects.json").write_text(json.dumps(projs, indent=2, ensure_ascii=False), encoding="utf-8")
        _update_report_with_rag(pdir / "NEST_Executive_Report.md", projs)

        # Update intermediates/agent_site_context.md if present
        ctx_p = pdir / "intermediates" / "agent_site_context.md"
        if pname in plot_stage_a:
            a_hits = []
            for c in plot_stage_a[pname]:
                hit = by_key.get(f"A::{pname}::{c.get('site_rank')}")
                if hit:
                    hit_copy = dict(hit)
                    hit_copy["key"] = f"Site #{c.get('site_rank')} ({c.get('terrain_class')} · {c.get('dominant_engine')})"
                    a_hits.append(hit_copy)
            if a_hits:
                (pdir / "intermediates" / "rag_site_evidence.json").write_text(
                    json.dumps(a_hits, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                if ctx_p.exists():
                    md_block = "\n".join(format_stage_a_rag_markdown(a_hits))
                    new_ctx = _replace_or_append_section(
                        ctx_p.read_text(encoding="utf-8"),
                        "## Cited Egyptian Codes & Architectural Precedents (NEST Portable RAG v3)",
                        md_block,
                    )
                    ctx_p.write_text(new_ctx, encoding="utf-8")

        # Rebuild dashboard and verify JS syntax
        res = subprocess.run(
            [sys.executable, "build_nest_dashboard.py", "--run-dir", str(pdir), "--plot-title", pname],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            raise RuntimeError(f"Dashboard rebuild failed for {pname}: {res.stderr[:500]}")
        verify_dashboard_js(pdir / "nest_dashboard.html")
        print(f"  [OK] {pname}: {len(projs)} projects enriched, report & dashboard rebuilt + JS verified")

    print(f"\n[Enrich All Plots] Successfully enriched and rebuilt all {len(plot_dirs)} plots!")


if __name__ == "__main__":
    main()
