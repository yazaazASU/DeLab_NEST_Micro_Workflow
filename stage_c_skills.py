#!/usr/bin/env python3
"""
NEST Stage C: On-Demand Project Design Skill Generator (`stage_c_skills.py`)
============================================================================
Generates 9 site-grounded Stage C design skills (3 Crystals + 3 Corals + 3 Cells)
for any selected project(s) in `<run_dir>/stage_b_projects.json`:
  - Writes `<run_dir>/skills/project_<rank>_<slug>/*.json` + `SKILL_INDEX.md`
  - Injects `generated_skills` into `stage_b_projects.json`

Usage:
  python stage_c_skills.py --run-dir outputs_nest_84_617 --sites 1
  python stage_c_skills.py --run-dir outputs_nest_84_617 --all
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (text or "project").lower()).strip("_")[:48]


def _space_names(project: dict) -> list[str]:
    out = []
    for sp in project.get("spaces") or []:
        if isinstance(sp, dict):
            out.append(str(sp.get("name", "")))
        elif isinstance(sp, (list, tuple)) and sp:
            out.append(str(sp[0]))
    return [s for s in out if s]


def generate_skills_for_project(project: dict) -> list[dict]:
    rank = int(project.get("rank", 1))
    title = project.get("title", f"Project #{rank}")
    idiom = project.get("idiom", "landform")
    gfa = project.get("built_gfa", "N/A")
    feddans = project.get("area_feddans", 55.0)
    strat = str(project.get("strategy", "Select"))
    ptrs = project.get("map_pointers") or []
    p0 = ptrs[0] if len(ptrs) >= 1 else {"label": "Primary Site Feature", "distance_m": 0}
    p1 = ptrs[1] if len(ptrs) >= 2 else {"label": "Adjacent Corridor", "distance_m": 150}
    ta = project.get("terrain_analysis") or {}
    relief = float(ta.get("relief_m", 4.0))
    slope = float(ta.get("slope_mean_deg", 1.5))
    t_mode = ta.get("mode", "free_standing")
    zones = project.get("landscape_zones") or []
    pres_zones = [z["name"] for z in zones if "preserve" in str(z.get("intervention", "")).lower()]
    pres_lbl = ", ".join(pres_zones) or "Coastal / Ecological Preserve Buffer"
    sp_names = _space_names(project)
    n2b = project.get("nature_to_bldg", "Prevailing coastal/desert breezes flush shaded courts.")
    b2n = project.get("bldg_to_nature", "Greywater reed beds recharge native planting.")
    mr = project.get("massing_rationale") or {}
    orient = mr.get("orientation", "Aligned to prevailing breeze and low-glare solar axis.")

    lead_crystals = "Primary Lead" if "crystal" in strat.lower() else "Specialist Contributor"
    lead_corals = "Primary Lead" if "coral" in strat.lower() or "merge" in strat.lower() else "Specialist Contributor"
    lead_cells = "Primary Lead" if "cell" in strat.lower() or "merge" in strat.lower() else "Specialist Contributor"

    c1 = {
        "skill_id": "crystal_01_poi_viewshed_axis",
        "title": f"{title}: POI Standoff & Solar Axis",
        "definition": f"Enforces build-around setbacks from {p0.get('label')} ({p0.get('distance_m', 0):.0f} m) and locks massing orientation ({orient}).",
        "parent_engine": "Crystals Engine",
        "role_in_project": lead_crystals,
        "trigger": [
            f"Massing placement or footprint rotation within {feddans} feddans",
            f"Grading or circulation layout near {pres_lbl}",
        ],
        "action": {
            "type": "Warning",
            "message": f"Keep all non-bridge building footprints strictly outside '{pres_lbl}' and maintain primary solar/breeze alignment: {orient}",
        },
        "attributes": {
            "scale": "Cluster",
            "facets": [
                {"capability": "Preserve-buffer setback & viewshed corridor check", "tool": ["QGIS", "Rhino", "Grasshopper"]},
                {"capability": "Solar & prevailing wind axis lock", "tool": ["Ladybug", "Autodesk Forma"]},
            ],
            "axes": {"space": f"{feddans}-feddan site parcel", "time": "Schematic Massing & Site Plan", "depth": "Deep"},
            "density": "Verified",
            "growth": "Linear",
            "field": "Environmental",
            "state": "Stable",
            "memory": {
                "past_experiences": [f"Derived from {p0.get('label')} at {p0.get('distance_m', 0):.0f} m"],
                "usage_history": [],
                "feedback": [],
                "lessons_learned": [f"Orient {idiom} volumes to shade glazing while opening view corridors."],
            },
            "bonds": ["Environmental", "Urban", "Engineering"],
            "resilience": "Resistance",
        },
    }

    c2 = {
        "skill_id": "crystal_02_tectonic_climate_envelope",
        "title": f"{idiom.replace('_', ' ').title()} Climate Envelope",
        "definition": f"Calibrates the {idiom} roof overhangs, thermal mass, and shading envelope for {title} ({t_mode}, {relief:.1f} m relief).",
        "parent_engine": "Crystals Engine",
        "role_in_project": lead_crystals,
        "trigger": [
            "Facade glazing ratio or roof canopy perforation edit",
            "Thermal mass wall thickness or shading louver sizing",
        ],
        "action": {
            "type": "Study",
            "message": f"Run annual solar-radiation and cross-ventilation checks on the {idiom} envelope; keep west-facing glazing deeply recessed behind stone or timber louvers.",
        },
        "attributes": {
            "scale": "Crystal",
            "facets": [
                {"capability": "Incident solar radiation & shading overhang study", "tool": ["Ladybug", "Honeybee", "Grasshopper"]},
                {"capability": "Envelope wall-to-window thermal mass check", "tool": ["Revit", "Grasshopper"]},
            ],
            "axes": {"space": "Building envelope & shaded courts", "time": "Peak summer (Jun–Sep) & diurnal swing", "depth": "Deep"},
            "density": "Verified",
            "growth": "Iterative",
            "field": "Material",
            "state": "Growing",
            "memory": {
                "past_experiences": [f"DEM mode={t_mode}, relief={relief:.1f} m, slope={slope:.1f}°"],
                "usage_history": [],
                "feedback": [],
                "lessons_learned": ["Deep overhangs + high-mass walls outperform glass curtain walls in arid coastal climates."],
            },
            "bonds": ["Material", "Environmental", "Engineering"],
            "resilience": "Adapt",
        },
    }

    c3 = {
        "skill_id": "crystal_03_program_stacking_gfa",
        "title": f"Program Stacking & {gfa} GFA Lock",
        "definition": f"Balances public, research, and service spaces across {gfa} total GFA without exceeding the site's acoustic and thermal zones.",
        "parent_engine": "Crystals Engine",
        "role_in_project": lead_crystals,
        "trigger": [
            "Floor-plate area or interior zone schedule edit",
            "Acoustic separation between public halls and quiet labs/study rooms",
        ],
        "action": {
            "type": "Guidance",
            "message": f"Hold total built area within ±5% of {gfa}; place {', '.join(sp_names[:2]) or 'core public halls'} on cool shaded ground courts and isolate MEP/service cores.",
        },
        "attributes": {
            "scale": "Crystal",
            "facets": [
                {"capability": "Exact ±5% GFA & interior-zone reconciliation", "tool": ["Revit", "Grasshopper"]},
                {"capability": "Day/night zone access & acoustic buffering", "tool": ["Revit", "Autodesk Forma"]},
            ],
            "axes": {"space": "All interior program volumes", "time": "24/7 vs. daytime/evening operating clocks", "depth": "Medium"},
            "density": "Verified",
            "growth": "Linear",
            "field": "Program",
            "state": "Stable",
            "memory": {
                "past_experiences": [f"Program spans {len(sp_names)} primary space groups totaling {gfa}"],
                "usage_history": [],
                "feedback": [],
                "lessons_learned": ["Separate 24/7 technical cores from late-night community study halls."],
            },
            "bonds": ["Program", "Human", "Engineering"],
            "resilience": "Resistance",
        },
    }

    co1 = {
        "skill_id": "coral_01_multi_element_coordination",
        "title": f"Site Seam Coordination ({p0.get('label')} + {p1.get('label')})",
        "definition": f"Connects {p0.get('label')} ({p0.get('distance_m', 0):.0f} m) with {p1.get('label')} ({p1.get('distance_m', 0):.0f} m) through shared shaded circulation.",
        "parent_engine": "Corals Engine",
        "role_in_project": lead_corals,
        "trigger": [
            "Arrival plaza, pedestrian spine, or service-dock routing",
            "Linking public outdoor zones to adjacent roads and trails",
        ],
        "action": {
            "type": "Prompt",
            "message": f"How can arrival from {p1.get('label')} feed the public forum while keeping freight/MEP service hidden from {p0.get('label')}?",
        },
        "attributes": {
            "resources": [
                {"resource": f"{p0.get('label')} ({p0.get('distance_m', 0):.0f} m)", "potential": "Ecological & scenic anchor", "constraints": [f"Protect {pres_lbl}"]},
                {"resource": f"{p1.get('label')} ({p1.get('distance_m', 0):.0f} m)", "potential": "Public & logistics access", "constraints": ["Buffer traffic noise from quiet courts"]},
            ],
            "branches": [
                {"direction": "Shaded pedestrian promenade linking arrival to main courtyard", "maturity": "Maturing", "application": "Continuous pergola spine", "tool": ["Autodesk Forma", "Grasshopper"]},
                {"direction": "Rear earth-bermed service court for deliveries", "maturity": "Specialized", "application": "Acoustic service apron", "tool": ["Revit", "QGIS"]},
            ],
            "symbiosis": [
                {"with": [p0.get("label", "Natural Edge"), p1.get("label", "Access Corridor")], "shared_intention": "Turn a transit edge into a shaded public gateway."}
            ],
            "evaluation": {
                "status": "Under Study",
                "criteria": {"creativity": "Seamless indoor-outdoor threshold", "resource_connection": "Zero conflict between freight and pedestrians", "feasibility": "Uses local stone grading"},
                "studies_needed": ["Pedestrian wind-comfort and shade continuity check"],
            },
            "state": "Maturing",
            "adaptation": "Redirect",
            "archive": {
                "retained_explorations": ["Direct vehicle drop-off at the Preserve edge rejected to keep noise and dust away."],
                "validated_knowledge": [f"GIS pointer provenance: {p0.get('provenance', 'Observed GIS')}"],
                "lessons_learned": ["Place noisy access at the rear edge so public courts open calmly toward nature."],
            },
        },
    }

    co2 = {
        "skill_id": "coral_02_two_way_nature_symbiosis",
        "title": "Two-Way Water & Microclimate Loop",
        "definition": "Coordinates passive cooling inputs from nature with regenerative water/flora outputs from the building.",
        "parent_engine": "Corals Engine",
        "role_in_project": lead_corals,
        "trigger": [
            "Landscape irrigation, greywater reed-bed, or evaporative court design",
            "Cistern sizing and native planting palette selection",
        ],
        "action": {
            "type": "Study",
            "message": f"Balance the two-way loop: ({n2b}) <-> ({b2n}). Verify zero reliance on imported potable water for outdoor landscapes.",
        },
        "attributes": {
            "resources": [
                {"resource": "Site microclimate & greywater stream", "potential": "Closed-loop passive cooling & native irrigation", "constraints": ["Arid evaporation loss; salinity control"]},
            ],
            "branches": [
                {"direction": "Sub-surface reed-bed filtration feeding native drought-adapted flora", "maturity": "Maturing", "application": "Terraced bio-swales", "tool": ["Ladybug", "QGIS"]},
                {"direction": "Covered thermal cisterns pre-cooling ventilation air", "maturity": "Exploratory", "application": "Earth-tube / courtyard mist intake", "tool": ["Honeybee", "Grasshopper"]},
            ],
            "symbiosis": [
                {"with": ["Building Greywater Output", "Restored Native Flora Belt"], "shared_intention": "Every liter used indoors irrigates resilient native shade outdoors."}
            ],
            "evaluation": {
                "status": "Under Study",
                "criteria": {"creativity": "Visible living water-to-garden cycle", "resource_connection": "100% greywater reuse on site", "feasibility": "Low-tech reed beds + gravity flow"},
                "studies_needed": ["Daily greywater yield vs. native plant evapotranspiration balance"],
            },
            "state": "Active",
            "adaptation": "Regenerate",
            "archive": {
                "retained_explorations": ["Decorative open turf lawns rejected due to extreme evaporation."],
                "validated_knowledge": [n2b, b2n],
                "lessons_learned": ["Sub-surface irrigation eliminates midday evaporative waste."],
            },
        },
    }

    co3 = {
        "skill_id": "coral_03_shared_network_archive",
        "title": "Dual-Clock Public & Work Program Sharing",
        "definition": "Coordinates daytime research/craft programs with evening community use so shared halls stay active past sunset.",
        "parent_engine": "Corals Engine",
        "role_in_project": lead_corals,
        "trigger": [
            "Operating schedule or shared-courtyard programming review",
            "Lighting and after-hours security zoning",
        ],
        "action": {
            "type": "Alternative",
            "message": "Pair daytime technical/craft spaces with public viewing corridors and night-lit community courts so no zone sits empty after 17:00.",
        },
        "attributes": {
            "resources": [
                {"resource": f"{len(sp_names)} program zones across {gfa}", "potential": "Shared parking, lobbies, and shaded plazas across day/night shifts", "constraints": ["Secure restricted lab cores after hours"]},
            ],
            "branches": [
                {"direction": "Lockable glazed viewing gallery along research labs", "maturity": "Specialized", "application": "Public perimeter gallery", "tool": ["Revit", "Autodesk Forma"]},
            ],
            "symbiosis": [
                {"with": ["Daytime Research/Craft", "Evening Community Forum"], "shared_intention": "Shared infrastructure cuts idle space and energy peaks."}
            ],
            "evaluation": {
                "status": "Evaluated",
                "criteria": {"creativity": "24-hour civic vitality", "resource_connection": "Shared MEP & chilled-water loop", "feasibility": "Simple card-access inner doors"},
                "studies_needed": ["After-hours glare & dark-sky lighting check near Preserve"],
            },
            "state": "Maturing",
            "adaptation": "Reinterpret",
            "archive": {
                "retained_explorations": ["Isolated single-use gated compound rejected to preserve public access."],
                "validated_knowledge": ["Dual-clock programming increases annual revenue and civic utility."],
                "lessons_learned": ["Glass viewing corridors let visitors experience science without entering sterile labs."],
            },
        },
    }

    ce1 = {
        "skill_id": "cell_01_host_element_adaptation",
        "title": f"Terrain & Edge Adaptation ({title})",
        "definition": f"Adapts the site's {relief:.1f} m terrain relief and natural edge into shaded microclimates and terraced public walks.",
        "parent_engine": "Cells Engine",
        "role_in_project": lead_cells,
        "trigger": [
            "Site grading, retaining walls, or foundation excavation",
            f"Design of outdoor terraces near {pres_lbl}",
        ],
        "action": {
            "type": "Guidance",
            "message": f"Work with the {relief:.1f} m natural relief ({slope:.1f}° mean slope) using stepped dry-stone terraces and shaded courtyards rather than flat cut-and-fill pads.",
        },
        "attributes": {
            "host_element": {
                "element": f"Natural site terrain & edge ({relief:.1f} m relief, {slope:.1f}° slope)",
                "current_condition": "Exposed arid ground subject to solar heat gain and seasonal runoff",
                "category": "Terrain",
            },
            "transformation": {
                "from_state": "Unshaded, wind-scoured terrain margin",
                "to_state": "Terraced stone-and-flora microclimate spine cooling building entries",
                "value_unlocked": "Passive outdoor comfort and natural stormwater retention",
            },
            "adaptation_moves": [
                {"move": "Step terraces parallel to natural contours with dry-stone retaining edges", "reversibility": "Phased", "tools": ["Rhino", "QGIS", "Grasshopper"]},
                {"move": "Place light timber boardwalks over sensitive ecological pockets", "reversibility": "Reversible", "tools": ["Revit", "Autodesk Forma"]},
            ],
            "limits_and_proof": {
                "constraints": [f"Keep heavy foundations clear of {pres_lbl}", "Minimize rock blasting"],
                "site_checks_needed": ["Geotechnical soil/rock bearing test", "Seasonal runoff flow check"],
                "fallback": "If bedrock is unstable, shift heavy loads onto compact pier pads and bridge lightly.",
            },
            "maturity": "Concept",
            "memory": {
                "precedent_lessons": ["Contour-stepped terraces reduce excavation cost and anchor buildings visually."],
                "site_notes": [f"DEM mode classified as '{t_mode}'."],
            },
        },
    }

    ce2 = {
        "skill_id": "cell_02_extreme_climate_mutation",
        "title": "Extreme Sun & Breeze-to-Cooling Adaptation",
        "definition": "Adapts intense solar exposure and prevailing coastal/desert winds into passive architectural cooling and power.",
        "parent_engine": "Cells Engine",
        "role_in_project": lead_cells,
        "trigger": [
            "Roof canopy, courtyard proportion, or natural ventilation modeling",
            "HVAC load reduction and shading strategy review",
        ],
        "action": {
            "type": "Study",
            "message": "Turn harsh solar radiation into canopy shade + flush integrated PV power while funneling prevailing breezes across shaded water/planted courts.",
        },
        "attributes": {
            "host_element": {
                "element": "High solar irradiance & prevailing coastal/desert wind",
                "current_condition": "Thermal stress and glare limiting daytime outdoor use",
                "category": "Climate",
            },
            "transformation": {
                "from_state": "Overheated exposed site requiring heavy mechanical AC",
                "to_state": "Self-shaded courtyard campus powered by flush roof louvers",
                "value_unlocked": "Extended daytime outdoor usability and lower cooling CapEx",
            },
            "adaptation_moves": [
                {"move": "Integrate flush matte-dark PV louvers into timber/steel shade canopies", "reversibility": "Phased", "tools": ["Ladybug", "Honeybee"]},
                {"move": "Proportion courtyards (H:W >= 1:1.5) to trap cool night air and shade walls", "reversibility": "Permanent", "tools": ["Grasshopper", "Ladybug"]},
            ],
            "limits_and_proof": {
                "constraints": ["Avoid tilted shiny blue-black roof racks", "Control windblown sand at intakes"],
                "site_checks_needed": ["Hourly TMY wind-rose & glare simulation", "Sand-trap louver detailing"],
                "fallback": "If summer humidity spikes reduce evaporative cooling, switch courts to pure high-mass shade + ceiling fans.",
            },
            "maturity": "Tested",
            "memory": {
                "precedent_lessons": ["Flush canopy louvers outperform bolted-on racks both thermally and visually."],
                "site_notes": [n2b],
            },
        },
    }

    ce3 = {
        "skill_id": "cell_03_reinterpretation_fallback",
        "title": "Low-Impact Material & Phasing Fallback",
        "definition": "Ensures local earth/stone material sourcing and reversible phasing if supply-chain or ecological constraints block heavy construction.",
        "parent_engine": "Cells Engine",
        "role_in_project": lead_cells,
        "trigger": [
            "Structural system, foundation, or material specification review",
            "Phase 0 pilot staging and budget check",
        ],
        "action": {
            "type": "Alternative",
            "message": "Start with modular, locally dressed stone or compressed-earth bays for Phase 0 so construction stays reversible and local-labor friendly.",
        },
        "attributes": {
            "host_element": {
                "element": "Regional stone, excavated earth & local craft labor",
                "current_condition": "Often bypassed for imported steel/curtain-wall systems",
                "category": "Infrastructure",
            },
            "transformation": {
                "from_state": "High-carbon imported construction",
                "to_state": "Local thermal masonry & demountable timber-shade kit-of-parts",
                "value_unlocked": "Lower embodied carbon, local jobs, and easy future expansion",
            },
            "adaptation_moves": [
                {"move": "Use excavated site rock/earth for retaining berms and Phase 0 test pavilions", "reversibility": "Reversible", "tools": ["Revit", "Grasshopper"]},
            ],
            "limits_and_proof": {
                "constraints": ["Verify local quarry/soil compressive strength", "Keep Phase 0 self-sufficient"],
                "site_checks_needed": ["Local stone/soil compression & salt-efflorescence lab test"],
                "fallback": "If local earth fails strength tests, use lime-stabilized precast stone-aggregate blocks.",
            },
            "maturity": "Concept",
            "memory": {
                "precedent_lessons": ["Phase 0 shade-and-spine pilots build early public momentum at <10% CapEx."],
                "site_notes": [f"Idiom={idiom}, Built GFA={gfa}."],
            },
        },
    }

    return [c1, c2, c3, co1, co2, co3, ce1, ce2, ce3]


def main():
    ap = argparse.ArgumentParser(description="Generate Stage C Design Skills for selected NEST projects")
    ap.add_argument("--run-dir", type=Path, required=True, help="NEST run output directory")
    ap.add_argument("--sites", type=str, default=None, help="Comma-separated site ranks (e.g. 1,3)")
    ap.add_argument("--all", action="store_true", help="Generate skills for all projects in stage_b_projects.json")
    args = ap.parse_args()

    pjson = args.run_dir / "stage_b_projects.json"
    if not pjson.exists():
        raise FileNotFoundError(f"Missing {pjson}")
    projects = json.loads(pjson.read_text(encoding="utf-8"))
    site_filter = {int(s.strip()) for s in args.sites.split(",") if s.strip().isdigit()} if args.sites else None

    skills_root = args.run_dir / "skills"
    skills_root.mkdir(parents=True, exist_ok=True)

    for p in projects:
        rk = int(p.get("rank", 1))
        if not args.all and site_filter and rk not in site_filter:
            continue
        skills = generate_skills_for_project(p)
        p["generated_skills"] = skills
        pdir = skills_root / f"project_{rk}_{_slug(p.get('title', ''))}"
        pdir.mkdir(parents=True, exist_ok=True)
        idx_lines = [f"# Stage C Design Skills — Project #{rk}: {p.get('title')}", "", "| Skill ID | Engine | Role | Action |", "| :--- | :--- | :--- | :--- |"]
        for sk in skills:
            (pdir / f"{sk['skill_id']}.json").write_text(json.dumps(sk, indent=2, ensure_ascii=False), encoding="utf-8")
            idx_lines.append(f"| `{sk['skill_id']}` | {sk['parent_engine']} | {sk['role_in_project']} | `{sk['action']['type']}` |")
        (pdir / "SKILL_INDEX.md").write_text("\n".join(idx_lines) + "\n", encoding="utf-8")
        print(f"[Stage C] Generated {len(skills)} skills for Project #{rk} -> {pdir}")

    pjson.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Stage C] Updated {pjson} with generated_skills.")


if __name__ == "__main__":
    main()
