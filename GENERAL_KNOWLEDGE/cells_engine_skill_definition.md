# CELLULAR ENGINE (Cells Engine) — Behavioral Specification & Stage C Skill Schema

> **Overarching Theme ([`engine_charter.md`](./engine_charter.md)):** **Cells Engine — Adaptation** (*Finding elements in site, nature, or context to unlock their full potential by adapting them into something new or better*).  
> **Stage C Skill Contract:** See **Section 12** at the bottom of this document for how the Cellular Engine's internal architecture (`Project DNA`, `Skill Contract`, `Skill Genome`, `Confidence/Novelty`, `Adaptation`, `Division`) serializes into the universal NEST Stage C `skill_name.json` format ([`skill_defintion.md`](./skill_defintion.md)).

Version: 0.5 (proposed architecture — generation-first Skills, Skill Genome, novelty handling, scoring and similarity rubrics, managed escalation, phased MVP) + NEST Stage C Adaptation Skill Schema
Status: Behavioral specification & active Stage C skill schema contract.

## 1. Mission

Transform structured site information (Project DNA) into a network of bounded, cooperating AI Skills that investigate site problems and produce evidence-traceable architectural design requirements and options.

The engine is **cell-inspired**, not a biological simulation. Its operating principles are sensing, state regulation, memory, differentiation, communication, adaptation, and lifecycle management.

**Core loop:** Sense → Diagnose → Generate capabilities → Investigate → Communicate → Evaluate → Adapt or Escalate → Record → Deliver.

This is a feedback-driven loop, not a mandatory linear pipeline. Any new observation or conflict can reopen earlier decisions.

The engine is **domain-general**. Site problems may be environmental, climatic, regulatory, social, infrastructural, heritage-related, or of a kind the engine has never seen. The soil-erosion case in this document is only a worked example. The engine must expect unfamiliar and anomalous problems and handle them explicitly (Rule I), never force them into the nearest familiar category.

## 2. Input Contract: Project DNA

Accept a structured object with:

- `project_id`, `site_id`, `dna_version`, `project_goal`, `building_program`
- `project_lead`: the architect or project lead who approves decisions and answers escalations (Rule H)
- `delegations` (optional): escalation categories the project lead pre-assigns to specialists, e.g. `{hydrology: specialist_a, structure: specialist_b}`
- `review_settings`: `max_items_per_packet`, `review_cycle` (how often a review packet is sent)
- `location_context`, `site_boundary`, `topography`, `soil`, `climate`, `hydrology`, `vegetation`, `access`, `adjacencies`, `regulations`
- `observations`: each with `observation_id`, `value`, `unit`, `source`, `timestamp`, `spatial_extent`, `confidence`, `method`
- `constraints` (each marked `hard` or `soft`), `stakeholder_priorities` (criteria and optional weights), `available_tools`, `budgets`
- `unknowns` and `assumptions`

Do not fabricate missing observations. Unknown data remain explicitly unknown.

Any change to the Project DNA creates a new `dna_version`. Findings, caches, and decisions record the `dna_version` they were based on.

## 3. Internal Data Models

### Scales: Confidence, Severity, and Novelty

Confidence and severity use an internal **score** (0–1) and a displayed **level** (`low` | `medium` | `high`). The score is **computed from a fixed rubric**, not chosen freely, so the same evidence always gives the same score. The level is derived from the score using project-configurable ranges; default ranges:

| Level | Score range |
|---|---|
| `low` | 0.00 – < 0.40 |
| `medium` | 0.40 – < 0.70 |
| `high` | 0.70 – 1.00 |

Every score records its rubric answers as its `basis`. A score whose rubric answers are missing or do not match the cited evidence is rejected by the Quality Controller (Rule F).

**Confidence** — how well a claim is supported. Score = mean of four factors, each rated 0, 0.5, or 1:

| Factor | 0 | 0.5 | 1 |
|---|---|---|---|
| Directness | Indirect, regional, or analogous source | Direct source relevant to the site | Site-specific source |
| Measurement | Assumption or illustrative input | Documented secondary source | Site-measured observation |
| Corroboration | Single source | Partial agreement between sources | Independent sources or methods agree |
| Method validity | Unvalidated method | Standard method, not checked for this context | Method validated for this context |

Hard caps applied after averaging:

- No site-measured observation → score at most 0.69 (cannot be `high`).
- Unresolved contradiction in the cited evidence → score at most 0.39.
- `novel` problem without discriminating evidence (Rule I) → score at most 0.39.

**Severity** — how much the problem threatens the project if left unaddressed. Score = mean of four factors, each rated 0, 0.5, or 1:

| Factor | 0 | 0.5 | 1 |
|---|---|---|---|
| Impact on project goals | Minor | Degrades one goal | Defeats a goal or the program |
| Safety / regulatory | None | Possible non-compliance or minor risk | Life-safety risk or clear non-compliance |
| Reversibility | Easily reversed later | Costly to reverse | Irreversible once built |
| Extent | Local spot | Part of the site | Whole site or beyond the boundary |

Severity is provisional until its supporting evidence reaches at least `medium` confidence. A safety factor of 1 always sets priority to the top of the queue, whatever the average.

**Novelty** — how familiar the problem is to the engine. It has a **level only** (no score), set by three rubric questions, each answered `yes`, `partly`, or `no` with cited gene IDs and observation IDs:

| Question | |
|---|---|
| N1 | Is there an approved mechanism gene that explains the problem? |
| N2 | Do that gene's validity conditions fit this site (climate, scale, context)? |
| N3 | Do all relevant observations agree with what that mechanism predicts? |

| Level | Rule |
|---|---|
| `familiar` | N1, N2, and N3 are all `yes` |
| `novel` | N1 is `no`, or N3 is `no` |
| `partial` | Any other combination |

Every novelty classification is independently reviewed by the Quality Controller (Rule F).

### Problem

```yaml
problem_id: erosion_001
dna_version: 1
observation_refs: [rain_01, slope_01, soil_01]
statement: "Runoff may remove topsoil from the sloped site"
severity:
  level: medium
  score: 0.50
  provisional: true
  basis: {impact: 0.5, safety: 0.5, reversibility: 0.5, extent: 0.5}
confidence:
  level: low
  score: 0.25
  basis: {directness: 0.5, measurement: 0, corroboration: 0, method_validity: 0.5,
          caps_applied: [no_site_measurement]}
novelty:
  level: familiar
  basis: {N1: "yes — gene_runoff_mech_02", N2: "yes — sandy loam, 8% slope within range",
          N3: "yes — rain_01, slope_01 consistent"}
  reviewed_by_quality_controller: true
anomaly_refs: [] # observations flagged as anomalous or unreferenced (Rule A.3)
impacted_goals: [landscape_stability, safe_access]
dependencies: [surface_runoff, vegetation_establishment]
iterations: 0
reopen_count: 0
status: open # open|investigating|blocked|awaiting_review|provisionally_accepted|accepted|deferred
```

### Skill Contract

```yaml
skill_id: soil_erosion
skill_kind: investigative # investigative|exploratory (Rule I)
parent_skill_id: null
generated_for_problems: [erosion_001]
gene_refs: [gene_runoff_mech_02, gene_soil_inputs_01, gene_no_unvalidated_geometry_01] # Rule C
generated_parts: [mitigation_comparison] # parts not covered by genes
related_skills:
  - skill_id: surface_runoff
    relation: linked # merged|linked|independent (see Rule B)
    shared: [terrain, rainfall]
identity: Soil Erosion Investigator
purpose: Assess erosion mechanisms and feasible mitigation options
inputs: [terrain, soil, rainfall, land_cover]
outputs: [risk_hypotheses, design_options, uncertainties]
capabilities: [reason_over_evidence, compare_strategies]
tools_required: []
state: idle # idle|active|blocked|review|complete|retired (see Rule G)
memory_scope: project
memory_refs: []
dependencies: [surface_runoff]
resource_budget: {max_iterations: 4, max_child_skills: 2, max_reopens: 3}
confidence_policy: "Label unverified recommendations as provisional"
termination_condition: "Options delivered with constraints and validation needs"
```

### Gene (Skill Genome)

A gene is a reusable, reviewed building block of a Skill. Genes are domain-general; examples come from any field.

```yaml
gene_id: gene_west_facade_gain_01
gene_type: mechanism # mechanism|input_schema|method|check|lesson
description: "Low-angle afternoon sun on west façades increases cooling load"
domain_tags: [solar, thermal, envelope]
validity_conditions: {latitude_range: [15, 35], climate: [hot_arid, hot_humid], scale: building}
expected_ranges: {} # for input_schema genes: plausible value ranges used in anomaly detection
provenance: [case_2025_014, source_ref_88]
review_status: approved # candidate|approved|retired
origin: standard # standard|novel_case
usage: {uses: 12, successes: 10, failures: 2}
version: 3
```

Other gene examples: an input schema for noise from a linear road source; a method for applying setback regulations to a site boundary; a check "never state a regulation as in force without source and date"; a lesson "a vegetation-only noise barrier was insufficient at short distances".

### Finding / Message

```yaml
message_id: msg_014
message_type: conflict # finding|conflict|request|notification
in_reply_to: msg_011   # null if it starts a thread
sender: surface_runoff
recipient: soil_erosion
problem_id: erosion_001
dna_version: 1
claim: "Concentrated runoff may displace seeds and young plants"
evidence_refs: [rain_01, slope_01]
confidence:
  level: low
  score: 0.25
  basis: {directness: 0.5, measurement: 0, corroboration: 0, method_validity: 0.5}
assumptions: ["Rainfall event is representative"]
requested_action: "Re-evaluate vegetation-only option"
timestamp: 2026-11-22T10:00:00Z
```

Never communicate an unsupported claim as an established fact.

### Decision Record

```yaml
decision_id: dec_007
problem_id: erosion_001
decision_type: option # relationship|division|option|escalation|memory_promotion|novelty_classification
dna_version: 1
option: "Vegetation + contour-aligned runoff management"
alternatives: ["Vegetation only", "Hard surface stabilization"]
criteria: [landscape_stability, maintenance, cost, downstream_effects]
evidence_refs: [msg_011, msg_014]
conflicts: [msg_014]
confidence: {level: low, score: 0.25, basis: "see msg_014"}
status: pending_approval # accepted|rejected|deferred|escalated|pending_approval
approver: project_lead
reason: "Runoff feedback showed vegetation-only option threatens establishment"
supersedes: dec_003
timestamp: 2026-11-22T10:05:00Z
```

### Escalation

```yaml
escalation_id: esc_004
problem_ids: [erosion_001]
root_cause: "No hydrological data or modeling tool"
reason: capability_gap # capability_gap|novel_problem|anomaly|conflict|oscillation|quality_check|iteration_cap|memory_promotion
priority: high # critical|high|normal|low (Rule H)
blocking: true
ask: "Provide site hydrology data, or approve a provisional strategy"
options: ["Commission a hydrological survey", "Accept provisional strategy with monitoring"]
engine_recommendation: "Accept provisional strategy now; commission survey before detailed design"
consequence_if_unanswered: "Drainage-related requirements stay provisional; dependent problems stay blocked"
routed_to: project_lead # or a delegate from project_dna.delegations
status: open # open|answered|withdrawn
```

## 4. Engine Behavior Rules

### Rule A — Sensing

1. Parse the Project DNA and distinguish observations from interpretations.
2. Identify possible hazards, constraints, opportunities, and missing data, in any domain.
3. **Detect anomalies.** Judge each observation against three references, in order:
   1. *Physical and unit plausibility* (e.g., negative rainfall, impossible slope, wrong unit);
   2. *Internal consistency* with other observations in the Project DNA;
   3. *Expected ranges* from approved `input_schema` genes whose validity conditions fit the site.

   Flag an observation as `anomalous` if it fails any reference. If no gene provides an expected range for its domain, flag it as `unreferenced`: it is neither assumed normal nor anomalous, and it counts against familiarity (rubric question N3 cannot be `yes`). Never discard, smooth, or "correct" an anomaly silently. Keep at least two explanations open: a data or measurement error, and a genuine unusual site condition.
4. Create a Problem for each distinct actionable issue, deduplicating overlapping issues. Anomalies that cannot be explained become Problems in their own right.
5. Classify each problem's **novelty** with the rubric (see Scales) and send the classification to the Quality Controller for independent review (Rule F).
6. Build a dependency graph between problems and project goals.
7. Retrieve memory for each problem (Rule C), then rank investigations using severity, urgency, evidence quality, relevance to the building program, and memory priming. The queue is a **priority queue**; priorities are recalculated whenever a finding, conflict, or human decision changes them.

### Rule B — Skill Generation and Similarity Assessment

The engine does not search a pre-built Skill Registry. It **generates** a Skill specification for each problem, then decides how the new Skill relates to the Skills already generated in the same project.

For each problem:

1. **Generate** a draft Skill Contract from the problem: purpose, inputs, mechanism, methods, outputs, spatial extent, budget, and termination condition. Compose it from approved genes whose validity conditions fit this site (Rule C), and generate only the parts no gene covers (`generated_parts`). For a `novel` problem, generate an **exploratory Skill** instead (Rule I).
2. **Validate** the draft with the Skill Contract validator: bounded scope, budget, termination condition, and confidence policy present. Generated parts are validated in full; approved genes are checked for compatibility with each other and with the site. Genes never bypass the capability check or the Quality Controller.
3. **Check capability.** If the required inputs, data, or tools are not available, mark `capability_gap`, set the problem to `blocked`, escalate (Rule H), and narrow the scope. **Generating a Skill never creates missing scientific expertise, data, or simulation tools.**
4. **Assess similarity** with the rubric below, comparing the validated draft with every active Skill. Each answer is recorded with a one-line justification:

   | Dimension | Answers |
   |---|---|
   | S1 Mechanism | `same` / `related` / `different` |
   | S2 Inputs and evidence | `same` / `overlapping` / `disjoint` |
   | S3 Methods and tools | `same` / `overlapping` / `different` |
   | S4 Outputs | `same` / `overlapping` / `different` |
   | S5 Spatial and temporal extent | `same` / `overlapping` / `separate` |

5. **Decide the relationship** from the rubric, and log it in a Decision Record (`decision_type: relationship`):

   | Relationship | Rubric rule | Engine action |
   |---|---|---|
   | `merged` | S1, S3, and S4 are all `same`, and S2 and S5 are not `disjoint`/`separate` | Do not create a second Skill. Extend the existing Skill's `generated_for_problems`. |
   | `linked` | Not merged, and at least one of: S1 `related`, S2 not `disjoint`, S4 `overlapping`, S5 not `separate` | Create the Skill and link it. Linked Skills use the same version of shared evidence, declare shared assumptions, notify each other when a shared constraint changes (Rule D), and are cross-checked for conflicts (Rule E). |
   | `independent` | All of: S1 `different`, S2 `disjoint`, S4 `different`, S5 `separate` | Create the Skill with no link. |

   **When unsure, link rather than merge.** If any answer needed for a `merged` decision is uncertain, the engine chooses `linked`. A wrong merge hides a difference; a wrong link only costs extra messages.

   **Division (cell-inspired split).** The rubric is re-run on a `merged` Skill whenever its investigation progresses. If S1, S3, or S4 is no longer `same` across the problems it serves, the Skill **divides** into two or more daughter Skills:
   - each daughter takes the problems and the specialization that belong to it;
   - daughters inherit the parent's shared evidence, assumptions, findings, memory references, and the genes relevant to their specialization, with provenance;
   - daughters **continue** from the inherited findings and investigate only what diverged; they do not restart;
   - daughters are `linked` to each other on whatever they still share;
   - the parent Skill is retired, and a Decision Record (`decision_type: division`) states which rubric answers changed and why.
6. If the task needs a narrower investigation, generate a bounded **Child Skill** under the parent, subject to `max_child_skills`.

The engine generates investigation Skills only. It never generates, modifies, merges, or divides the Quality Controller (Rule F).

### Rule C — Memory

Retrieve past cases by problem mechanism, site similarity, data quality, and context. Use them to propose hypotheses, not copy solutions. Preserve provenance, validity conditions, and failed approaches. Retrieval happens before prioritization and can change investigation priority (priming).

New lessons are stored first as **candidate memory**. A candidate is promoted to reusable memory only after it passes the Quality Controller and is approved by the project lead (`decision_type: memory_promotion`). Promotion requests are `low` priority escalations and never block investigation (Rule H).

**Skill Genome.** Instead of storing whole Skills as templates, the engine stores reviewed **genes** (see the Gene model): mechanisms, input schemas, methods, checks, and lessons. This is the most efficient form of reuse:

- **Retrieval by mechanism, not by Skill name.** One gene (e.g., climate data input) can serve solar, flooding, and wind Skills alike.
- **Validity conditions.** A gene is used as a building block only when its validity conditions fit the site; otherwise it is offered as a hint at most.
- **Generate only what is missing.** Skill generation composes matching genes and generates only uncovered parts, reducing cost and review effort.
- **Track record.** Each gene records uses, successes, and failures. Genes that fail repeatedly are retired; near-duplicate genes are merged with a Decision Record.
- **Lesson genes** carry failed approaches forward so they are not proposed again without new evidence.
- **Promotion.** New genes start as `candidate` and become `approved` only through the same review and project-lead approval as other memory. Genes from novel cases carry `origin: novel_case` and narrow validity conditions until they are confirmed elsewhere.

A gene is never activated on its own as a ready-made Skill.

### Rule D — Communication

A Skill must notify affected Skills when its finding changes a shared constraint or design option. For `linked` Skills, any change to a `shared` element always produces a `notification` message. Messages enter a shared evidence/decision ledger. The engine detects incompatible assumptions, competing objectives, and duplicated work.

### Rule E — Adaptation

When feedback identifies a conflict:

1. Record the conflict and its supporting evidence.
2. Identify which assumptions or design decisions caused it.
3. Reopen only the affected Skills and dependencies, and increment each affected problem's `reopen_count`.
4. Generate a bounded set of revised alternatives.
5. **Compare them against explicit multi-objective criteria:**
   1. Criteria come from `project_goal`, `constraints`, and `stakeholder_priorities`.
   2. **Hard constraints filter first.** An option that violates a `hard` constraint is rejected, unless the project lead explicitly approves the exception.
   3. Remaining options are rated on each criterion. Weights come from `stakeholder_priorities`; if none are given, equal weights are used and recorded as an assumption.
   4. **Veto:** an option rated unacceptable on any single criterion cannot win on its weighted total.
   5. If the top options are within a small, recorded margin, both are presented as alternatives instead of the engine picking one.
6. Accept, reject, defer, or escalate; log why.

If a problem's `reopen_count` reaches `max_reopens`, the engine treats it as oscillation: it stops reopening that problem and escalates (Rule H).

**Evolution** in this engine means the progressive revision of investigation strategies and design alternatives over iterations; it does not claim biological evolution or autonomous acquisition of new scientific capability.

### Rule F — Quality Controller (Homeostasis)

The **Quality Controller** is a fixed engine component, not a generated Skill. Every finding passes through it before it can be provisionally accepted. It:

- blocks unjustified certainty: a confidence score that does not match its rubric answers and caps, or rubric answers that do not match the cited evidence;
- blocks contradictory accepted facts and missing source provenance, and checks that cited evidence actually exists and supports the claim;
- blocks outputs outside a Skill's declared competence (`inputs`, `capabilities`, `tools_required`);
- checks units, dates, spatial scale, `dna_version`, constraints, and confidence;
- **independently reviews every novelty classification** (see below);
- sends unresolved conflicts and failed checks that need judgment to escalation (Rule H).

A finding that fails a check is returned to its Skill with the reason. If the Skill cannot fix it within `max_iterations`, the problem is escalated.

**Novelty review.** The engine that generates Skills tends to see problems as familiar, so its novelty classification is never final on its own. The Quality Controller re-checks the rubric:

- For `familiar`: the cited gene exists and is `approved`; its validity conditions really fit the site; every relevant observation is consistent with it; no observation is `anomalous` or `unreferenced`. If any check fails, it downgrades the problem to `partial` or `novel` and records why.
- For `partial` and `novel`: it confirms the cited gaps are real.
- The engine can never upgrade a problem's novelty level by itself; only a Quality Controller review backed by new evidence can.

### Rule G — Lifecycle

Every Skill (parent, child, or daughter) moves through these states:

| State | Meaning | Exits to |
|---|---|---|
| `idle` | Generated and validated, waiting for its turn in the queue or for a dependency to finish | `active`, `blocked` |
| `active` | Investigating | `review`, `blocked` |
| `blocked` | Missing data, a tool, a dependency, or waiting for a human decision (Rule H) | `idle` when the cause is resolved, `retired` if no longer needed |
| `review` | Output submitted to the Quality Controller or to the project lead | `complete` if accepted, `active` if returned for revision |
| `complete` | Bounded output delivered and accepted (provisionally or fully) | `active` if reopened by a conflict, `retired` |
| `retired` | No longer needed, or replaced by daughters after a division | — |

Problem `status` moves in step: `open` → `investigating` → `provisionally_accepted` → `accepted` (after project-lead approval), or → `blocked` / `awaiting_review` when waiting for data or a human, or → `deferred` by decision.

Retire temporary workers while preserving their decision records, findings, provenance, and reviewed memory.

### Rule H — Human Review and Escalation

**Triggers:** unresolved conflict, `capability_gap`, a `novel` problem or an unexplained anomaly (Rule I), a problem reaching `max_reopens`, a Quality Controller check that needs judgment, the global iteration cap, and memory or gene promotion requests.

**Routing:** every escalation goes to the `project_lead`, or directly to a delegate when its category appears in `project_dna.delegations`. The project lead decides, or delegates to a specialist. A specialist's answer enters the ledger as evidence with its source, not as an unsourced override.

**Managing the load.** The project lead's attention is limited, and unmanaged escalations would turn the safeguard into noise. The engine therefore:

1. **Prioritizes** every escalation:

   | Priority | When |
   |---|---|
   | `critical` | Life-safety risk, or an irreversible design decision is pending |
   | `high` | Blocks other problems or a deliverable for the current design stage |
   | `normal` | Non-blocking: novel problems and anomalies under exploration, conflicts not yet blocking |
   | `low` | Memory and gene promotions, informational notices |

2. **Deduplicates**: escalations with the same root cause are merged into one, listing all affected problems.
3. **Batches**: escalations are sent as a **review packet** each `review_cycle`, sorted by priority and then by how many problems each one blocks, with at most `max_items_per_packet` items. `low` items only fill remaining space. `critical` items are sent immediately without waiting for the cycle.
4. **Makes each item quick to answer**: one clear `ask`, the `options`, the engine's recommendation, and the consequence if unanswered (see the Escalation model).

**While waiting:** only problems that a `blocking` escalation affects, and the problems that depend on them, become `blocked` / `awaiting_review`. Non-blocking escalations (e.g., a novel problem under exploration) never stop work. The rest of the queue continues normally.

**On response:** blocked problems return to the queue with the human decision recorded. **Silence is never approval:** unanswered items stay provisional or blocked, and the engine never upgrades an escalated item from provisional to accepted without the project lead's approval.

### Rule I — Novel and Anomalous Problems

The engine must expect problems that are unusual, unfamiliar, or unlike anything in memory, and handle them deliberately.

1. **Do not force-fit.** If no approved gene or past case explains a problem, the engine must not relabel it as the nearest familiar problem. It records the mismatch and why known mechanisms do not explain it (`decision_type: novelty_classification`), and the Quality Controller reviews that classification (Rule F).
2. **Explore before solving.** Generate an **exploratory Skill** whose purpose is to characterize the problem, not to design a solution. It must produce:
   - at least two competing hypotheses, always including "data or measurement error" when an anomaly is involved;
   - what each hypothesis predicts and what observation would tell them apart;
   - the minimum data, tests, or expertise needed next;
   - which design decisions are affected and which are safe to continue.
3. **Cap confidence.** Findings on a `novel` problem stay at `low` confidence until a hypothesis is supported by discriminating evidence (enforced by the confidence caps in Scales).
4. **Escalate early, without stopping work.** Notify the project lead with a `normal`-priority, non-blocking escalation as soon as a problem is classified `novel` or an anomaly stays unexplained. Exploration continues; only design decisions marked as affected wait. If the novel problem carries a safety factor of 1, the escalation is `critical`.
5. **Design for uncertainty.** Until the problem is understood, prefer robust, reversible, or phased design options (keep options open, add monitoring, avoid irreversible commitments in the affected zone) over committing to a single solution.
6. **Learn carefully.** When the problem is resolved, store what was learned as candidate genes with `origin: novel_case` and narrow validity conditions. A single novel case never becomes a general rule.
7. **Reclassify when understood.** When an exploratory Skill's findings explain the problem, the Quality Controller re-reviews its novelty. If it moves to `partial` or `familiar`, the exploratory Skill is retired and the problem receives an investigative Skill, with a Decision Record.

## 5. Orchestrator Pseudocode

The human review step is asynchronous in practice; it is shown inline for clarity.

```python
problems = sense_and_map(project_dna)                     # Rule A: anomalies + novelty rubric
for p in problems:
    p.novelty = quality_controller.review_novelty(p)      # independent review (Rule F)
    p.context = memory.retrieve(p, project_dna)           # priming before ranking
queue = PriorityQueue(prioritize(problems))
escalations = EscalationQueue(project_dna.review_settings, project_dna.delegations)
iterations = 0

while queue and iterations < MAX_GLOBAL_ITERATIONS:
    task = queue.pop_highest()
    problem = task.problem
    problem.status = "investigating"

    if task.skill is not None:                            # resumed: revision or daughter Skill
        skill = task.skill
    else:
        # --- Generate (Rule B.1 / Rule I) ---
        if problem.novelty.level == "novel":
            draft = generator.create_exploratory_skill(problem)
            escalations.add(problem, reason="novel_problem", blocking=False)
        else:
            genes = genome.match(problem, site=project_dna)    # validity conditions checked
            draft = generator.create_skill(problem, genes=genes)

        # --- Validate and check capability before relating (Rule B.2–3) ---
        if not validator.check(draft) or not draft.has_required_capabilities():
            ledger.record_gap(problem, draft)
            problem.status = "blocked"
            escalations.add(problem, reason="capability_gap", blocking=True)
            iterations += 1
            continue

        # --- Relate with the similarity rubric (Rule B.4–5) ---
        rubric = similarity.assess(draft, active_skills)  # S1–S5 answers + justifications
        ledger.record_decision("relationship", draft, rubric)
        if rubric.relation == "merged":
            skill = rubric.match.extend(problem)
        else:
            skill = draft
            if rubric.relation == "linked":
                skill.link(rubric.match, shared=rubric.shared_elements)
            active_skills.add(skill)                      # state: idle

    # --- Investigate ---
    skill.state = "active"
    findings = skill.investigate(problem, problem.context, resume_from=task.inherited)
    ledger.record(findings)
    problem.iterations += 1

    # --- Division check: re-run rubric on merged Skills ---
    if skill.relation == "merged" and similarity.has_diverged(skill):
        daughters = skill.divide()        # inherit evidence, findings, genes; link daughters
        lifecycle.retire(skill)
        ledger.record_decision("division", skill, daughters)
        active_skills.replace(skill, daughters)
        for d in daughters:               # continue from inherited findings, do not restart
            queue.push(Task(d.problems, skill=d, inherited=d.inherited_findings))
        iterations += 1
        continue

    # --- Quality gate (Rule F) ---
    skill.state = "review"
    verdict = quality_controller.check(findings, ledger, project_dna)
    if verdict.needs_human or (verdict.failed and problem.iterations >= skill.max_iterations):
        problem.status = "awaiting_review"
        escalations.add(problem, reason="quality_check", blocking=True)
        iterations += 1
        continue
    if verdict.failed:
        skill.state = "active"
        queue.push(Task(problem, skill=skill, note=verdict.reason))
        iterations += 1
        continue

    # --- Communicate (Rule D) ---
    for other in skill.linked_skills_affected_by(findings):
        ledger.send(notification(sender=skill, recipient=other, findings=findings))

    # --- Cross-check and adapt (Rule E) ---
    conflicts = evaluate_and_cross_check(findings, ledger, project_dna)
    if conflicts:
        for affected in dependency_graph.affected_problems(conflicts):
            affected.reopen_count += 1
            if affected.reopen_count >= affected.max_reopens:
                affected.status = "awaiting_review"
                escalations.add(affected, reason="oscillation", blocking=True)
            else:
                affected.status = "open"
                queue.push(reopen_with_revised_objectives(affected, conflicts))
    else:
        ledger.mark_provisionally_accepted(findings)
        problem.status = "provisionally_accepted"
        skill.state = "complete"
        genome.record_usage(skill.gene_refs, outcome=verdict)
        if skill.skill_kind == "exploratory" and findings.explains(problem):
            problem.novelty = quality_controller.review_novelty(problem)   # Rule I.7
            if problem.novelty.level != "novel":
                queue.push(Task(problem))                 # now gets an investigative Skill
        lifecycle.retire_if_unneeded(skill)               # keeps records and provenance

    # --- Human review cycle (Rule H) ---
    if escalations.packet_ready():                        # critical items: immediately
        for answer in present_to_reviewers(escalations.next_packet()):
            ledger.record_decision("escalation", answer)
            queue.push_all(answer.unblocked_tasks())

    queue.reprioritize(ledger)
    iterations += 1

if queue:
    escalations.add_all(queue, reason="iteration_cap", blocking=True)
present_to_reviewers(escalations.remaining_packets())

return synthesize_design_brief(ledger, unresolved_gaps=True)
```

## 6. Worked Example — Soil Erosion

**Hypothetical Project DNA:** 20 m × 15 m hillside, 8% slope, sandy loam, rainfall event of 30 mm in 2 hours. These are illustrative inputs, not measured site data, so the measurement factor is 0 and every finding in this example is `low` confidence.

1. **Sense:** The engine identifies a plausible risk of runoff-driven soil erosion. It does not claim to have measured erosion rates. Novelty rubric: N1–N3 `yes` → `familiar`; the Quality Controller confirms.
2. **Generate:** Generate and validate `Soil Erosion Skill` from the erosion problem, composed from approved runoff and soil genes.
3. **Memory:** Retrieve prior erosion-control approaches. Initial hypothesis: native grasses could help stabilize soil after establishment.
4. **Differentiate:** The Soil Skill identifies runoff as a dependency, and the engine generates `Surface Runoff Skill`. Similarity rubric: S1 `related`, S2 `overlapping` (terrain, rainfall), S3 `different`, S4 `different`, S5 `same` → `linked`, not merged.
5. **Communicate:** Runoff Skill flags that concentrated flow may displace seeds and young plants.
6. **Adapt:** Revise the option from **vegetation only** to **vegetation + contour-aligned runoff management**, potentially including shallow swales where appropriate.
7. **Evaluate:** Check runoff routing, overflow points, infiltration, soil stability, vegetation water demand, maintenance, and downstream effects. Do not prescribe swale depth or spacing without site-specific hydrological assessment.
8. **Regulate:** The Quality Controller finds no hydrological data or modeling capability. The engine outputs a provisional landscape strategy and adds a `high`-priority escalation (see the Escalation model) — not an engineered final design.
9. **Remember:** Store the relationship between runoff concentration and planting establishment as **candidate memory**, with context and source references. Its promotion request is a `low`-priority escalation.
10. **Deliver:** Design implications for landscape grading, planting, drainage, and protected building access, all marked provisional.

### Feedback example

```text
Soil Skill: "Planting may reduce erosion after establishment."
Runoff Skill: "Concentrated runoff threatens establishment."
Engine: CONFLICT -> reopen erosion option (reopen_count = 1)
Soil + Runoff Skills: "Test contour runoff controls with planting."
Quality Controller: "No hydraulic validation available. Mark provisional."
Engine: ESCALATE (high, blocking drainage decisions) -> next review packet
Engine: OUTPUT conditional concept + verification requirements
```

## 7. Outputs for Architectural Design

Return a machine-readable and human-readable design brief containing:

- `problem_map`: detected problems, priorities, relationships, severity and confidence (level, score, rubric basis), and novelty (level, rubric basis)
- `anomalies_and_novel_problems`: flagged and unreferenced observations, competing hypotheses, discriminating data needed, and interim robust design guidance
- `skill_graph`: generated Skills, parent-child relationships, `merged`/`linked`/`independent` relationships and divisions with their rubric answers, dependencies, final lifecycle states
- `site_design_constraints`: location-specific constraints with provenance
- `design_requirements`: implications for massing, orientation, access, landscape, envelope, and services
- `alternatives`: options, trade-offs, weights used, assumptions, evaluation status
- `unresolved_questions`: missing measurements, required simulations, expert reviews, open escalations by priority
- `decision_history`: what changed and why, including who approved
- `memory_updates`: candidate and approved genes and lessons, clearly separated, with gene usage updates

Every output records the `dna_version` it was based on. Downstream architectural design stages may consume these outputs, but must not treat provisional concepts as validated engineering requirements.

## 8. Efficiency and Stop Conditions

- Merge near-identical Skills instead of running duplicate investigations; link specialized Skills instead of letting them work in isolation.
- Daughter Skills continue from inherited findings instead of restarting.
- Reopen only affected nodes in the dependency graph.
- Cache validated analyses keyed by site, `dna_version`, and method.
- Cap global iterations, and per problem: iterations, reopens, children, tool calls, and time.
- Protect human attention: prioritize, deduplicate, and batch escalations (Rule H).
- Stop when evidence is sufficient for the requested design stage, improvement is negligible, resources are exhausted, or human review is required.
- Never optimize a single Skill's objective while silently violating project-level constraints.

## 9. Minimum Viable Implementation

Build in two phases. **Do not start Phase 2 until Phase 1's acceptance tests pass.**

### Phase 1 — Prove the feedback loop

Goal: show that generated, linked Skills can detect a conflict, revise an option, stay honest about evidence, and escalate.

1. Project DNA parser and evidence store (with `dna_version`)
2. Problem detector (without novelty and anomaly assessment) and dependency graph
3. Skill Generator (investigative only, no genes), similarity rubric, and Skill Contract validator
4. Orchestrator with priority queue, caps, and lifecycle management
5. Shared message/decision ledger
6. Quality Controller (scoring rubric checks), conflict evaluator, and feedback router
7. Simple escalation list for the project lead (no batching yet)
8. Design-brief exporter

Prototype: generate **two Skills** (`Soil Erosion`, `Surface Runoff`) from the worked example. Demonstrate that the rubric classifies them as `linked`, that the feedback loop revises the option, and that missing hydrology is escalated.

Phase 1 acceptance tests: 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 18, 22, 23.

### Phase 2 — Memory, novelty, and scale

1. Skill Genome with validity conditions, expected ranges, track record, and candidate/approved separation
2. Anomaly detection and novelty rubric, with Quality Controller novelty review
3. Exploratory Skills and Rule I
4. Division of merged Skills
5. Managed escalation: priorities, deduplication, review packets, delegations

Prototype addition: one deliberately unfamiliar input (an anomalous observation with no matching gene) to show that the engine explores and escalates instead of force-fitting it, and a burst of escalations to show batching.

Phase 2 acceptance tests: 4, 12, 13, 14, 15, 16, 17, 19, 20, 21.

## 10. Acceptance Tests

| # | Given | Expected result (checkable) |
|---|---|---|
| 1 | A required observation is missing (e.g., rainfall, traffic volume, applicable regulation) | The affected problem has `confidence.level == low`; a `capability_gap` or `unknowns` entry names the missing data; no invented value appears in any finding |
| 2 | Two problems whose rubric gives S1, S3, S4 = `same` | One Skill with both problems in `generated_for_problems`; a `relationship` Decision Record with `merged` and the rubric answers |
| 3 | Two problems sharing inputs but with different mechanisms | Two Skills with `relation: linked` and listed `shared` elements; both use the same `dna_version`; a change to a shared element produces a `notification` message to the other Skill |
| 4 | A merged Skill whose rubric answer for S1, S3, or S4 changes from `same` | Daughter Skills exist and are `linked`; parent `state == retired`; daughters reference the parent's findings and do not re-investigate them; a `division` Decision Record lists the changed answers |
| 5 | A generated Skill whose required data or tools are unavailable | Problem `status == blocked`; `capability_gap` recorded; a blocking escalation exists; the Skill never reaches `active` |
| 6 | Feedback from one Skill conflicts with another Skill's option (e.g., runoff vs. vegetation-only, glare vs. glazing ratio) | A `conflict` message exists; a new `option` Decision Record `supersedes` the old one and states the reason |
| 7 | The tool needed to verify a quantity is unavailable (e.g., hydraulic model, daylight simulation) | No finding states that quantity as verified (e.g., swale dimensions, daylight factor); the option is marked provisional with a verification request |
| 8 | Repeated oscillation between alternatives | Problem stops reopening when `reopen_count == max_reopens`; an escalation with reason `oscillation` exists |
| 9 | A blocking escalation while other problems are unaffected | Only the escalated problem and its dependents are `blocked` / `awaiting_review`; other problems continue to be processed |
| 10 | A finding with `high` confidence but no site-measured observation | Quality Controller rejects it: the measurement cap limits the score to ≤ 0.69 |
| 11 | A completed Child Skill | Child `state == retired`; its approved finding and provenance remain in the ledger |
| 12 | A new lesson from any investigation | Stored as a candidate gene; a `low`-priority escalation requests promotion; not reusable until a `memory_promotion` Decision Record approved by `project_lead` exists |
| 13 | A problem with no matching approved gene or past case | Novelty rubric N1 = `no`; `novelty.level == novel`; an exploratory Skill is generated; no finding relabels it as the nearest familiar problem; a `novelty_classification` Decision Record explains the mismatch |
| 14 | An observation outside its expected range or contradicting other observations | It is listed in `anomaly_refs` as `anomalous`, not discarded or corrected; hypotheses include "data or measurement error" and at least one genuine-condition explanation |
| 15 | Findings on a `novel` problem without discriminating evidence | All such findings have score ≤ 0.39; a non-blocking escalation exists; exploration and unaffected problems continue |
| 16 | An approved gene whose validity conditions do not fit the site | It is not used as a building block (at most a hint); the Skill's `gene_refs` does not include it |
| 17 | A novel problem that becomes explained | The Quality Controller re-reviews novelty; the exploratory Skill is retired; an investigative Skill is generated; new genes are stored with `origin: novel_case` and narrow validity conditions |
| 18 | A similarity assessment where an answer needed for `merged` is uncertain | The relationship is `linked`, not `merged`; the uncertainty is recorded in the rubric justification |
| 19 | The engine classifies a problem as `familiar`, but the cited gene's validity conditions do not fit the site, or an observation is `unreferenced` | The Quality Controller downgrades it to `partial` or `novel` and records why |
| 20 | An observation in a domain where no gene provides an expected range | It is flagged `unreferenced`, not assumed normal; rubric N3 is not `yes` |
| 21 | Many escalations in one review cycle, two with the same root cause | The packet is sorted by priority, holds at most `max_items_per_packet` items, merges the two same-cause escalations into one, and sends `critical` items immediately; `low` items never block investigation |
| 22 | The same evidence rated twice | The confidence rubric gives identical factor answers and the same score; caps are applied and listed |
| 23 | An option that violates a `hard` constraint, and a project with no stakeholder weights | The violating option is rejected before weighted comparison (unless the project lead approved an exception); equal weights are used and recorded as an assumption |

## 11. Non-Goals and Boundaries

The engine does not autonomously guarantee safe designs, perform unavailable engineering simulations, or prove global optimality. Engineering verification, local code compliance, and professional approval remain separate required processes.

---

## 12. NEST Stage C Skill Output Format (`skill_name.json`) — Adaptation Skill Schema

When the **Cells Engine** operates inside NEST Stage C ([`skill_generation_workflow.md`](./skill_generation_workflow.md)), it applies its overarching **Adaptation** lens (*finding a natural or contextual/man-made element in the site, nature, or context and unlocking its full potential by adapting it into something new or better*) and serializes its Skill Contract into the universal `skill_name.json` envelope ([`skill_defintion.md`](./skill_defintion.md)).

### Cells Engine `attributes` Specification

- **`host_element`** (`object`): The specific natural or contextual/man-made element being adapted (e.g., cave, quarry, harsh solar microclimate, seasonal wadi, saline marsh, ruin, underused shoreline edge).
  - `element` (`text`): Exact site/nature/context element and location/metric.
  - `current_state` (`text`): How the element behaves or sits underutilized today (or why conventional design treats it as a constraint).
  - `element_class` (`enum`: `Natural` | `Climatic` | `Hydrological` | `Ecological` | `Geological` | `Contextual / Man-Made`).
- **`latent_potential`** (`text`): The untapped value or new/better architectural, ecological, or experiential function unlocked by adapting this element.
- **`adaptation_pathway`** (`array of objects`): Concrete transformation strategies (grounded in Rule B/E/I), ordered by feasibility and reversibility:
  - `mutation` (`text`): How the element is adapted into something new/better.
  - `reversibility` (`enum`: `Reversible` | `Phased` | `Permanent`).
  - `tool` (`array of text`): Candidate tools/platforms (`Ladybug`, `Honeybee`, `Grasshopper`, `QGIS`, `Revit`, `Autodesk Forma`).
- **`gene_refs`** (`array of text`): Reusable Skill Genome building blocks (mechanisms, checks, lessons) that ground this adaptation.
- **`novelty`** (`enum`: `familiar` | `partial` | `novel`): Novelty rubric level per Section 3 & Rule I.
- **`confidence`** (`object`): Rubric-backed evidence confidence (`level`: `low` | `medium` | `high`, `score`: `0.0–1.0`, `unknowns`: `array of text` — never fabricate missing site observations).
- **`reinterpretation_fallback`** (`text`): How the element's sensory, thermal, or spatial qualities are reinterpreted elsewhere if direct physical adaptation is blocked by safety, heritage, or geotechnical constraints.
- **`state`** (`enum`: `idle` | `active` | `blocked` | `review` | `complete` | `retired`): Lifecycle state per Rule G.
- **`evolution_memory`** (`object`):
  - `provisional_assumptions` (`array of text`): Assumptions awaiting site measurement or project-lead sign-off.
  - `escalation_needed` (`text` or `null`): Non-blocking or blocking escalation trigger per Rule H.
  - `lessons_learned` (`array of text`): Candidate genes / takeaways carried forward.

### Output Format Example (`cell_01_element_adaptation.json`)
```json
{
  "skill_id": "cell_01_cave_microclimate_adaptation",
  "title": "Existing Cave & Warm Microclimate Adaptation",
  "definition": "Unlock the full potential of an existing limestone cave and its warm microclimate pocket by adapting it into a passive thermal sanctuary or narrative chamber rather than sealing or avoiding it.",
  "parent_engine": "Cells Engine",
  "role_in_project": "Primary Lead",
  "trigger": [
    "site grading or excavation within 50 m of existing limestone cave",
    "program placement for wellness, thermal refuge, or exhibition chambers"
  ],
  "action": {
    "type": "Study",
    "message": "Do not seal or bypass the limestone cave. Test adapting its thermal pocket into a low-intervention passive wellness chamber or narrative gallery rim; hold irreversible structural cuts until geotechnical and air-quality logs raise confidence above low."
  },
  "attributes": {
    "host_element": {
      "element": "Existing limestone cave & warm microclimate pocket (north slope)",
      "current_state": "Unoccupied geological void conventionally flagged as an excavation hazard",
      "element_class": "Geological"
    },
    "latent_potential": "Naturally insulated subterranean enclosure capable of anchoring a zero-mechanical-cooling narrative chamber or passive thermal wellness sanctuary",
    "adaptation_pathway": [
      {
        "mutation": "Adapt the north chamber rim with reversible timber/stone walkways into a subterranean narrative gallery",
        "reversibility": "Reversible",
        "tool": ["Ladybug", "Autodesk Forma", "Revit"]
      },
      {
        "mutation": "Harness the warm microclimate pocket as a passive thermal wellness sanctuary once air exchange is verified",
        "reversibility": "Phased",
        "tool": ["Ladybug", "Honeybee", "Grasshopper"]
      }
    ],
    "gene_refs": [
      "gene_earth_thermal_lag_01",
      "gene_no_unvalidated_geotech_01"
    ],
    "novelty": "partial",
    "confidence": {
      "level": "low",
      "score": 0.38,
      "unknowns": [
        "Rock-mass geotechnical stability for public occupancy",
        "Continuous cave temperature, humidity, and radon/CO2 ventilation log"
      ]
    },
    "reinterpretation_fallback": "If geotechnical testing prohibits direct interior occupancy, translate the cave's light aperture, acoustic stillness, and thermal mass into an adjacent earth-bermed sensory pavilion framing views into the preserved void.",
    "state": "active",
    "evolution_memory": {
      "provisional_assumptions": [
        "Subsurface rock cavity remains structurally sound under light pedestrian load"
      ],
      "escalation_needed": "Commission geotechnical stability & air-quality survey before locking direct interior occupancy",
      "lessons_learned": [
        "Treat anomalous site features as primary adaptation targets with a reversible fallback rather than defaulting to clearance."
      ]
    }
  }
}
```
