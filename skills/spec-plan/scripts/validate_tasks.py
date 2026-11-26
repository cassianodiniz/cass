#!/usr/bin/env python3
"""
validate_tasks.py - deterministic pre-approval checks for a feature tasks.md.

Turns the three pre-approval checks (task granularity, diagram-vs-definition
cross-check, test co-location) into a checkable pass/fail run BEFORE tasks are
presented for approval, instead of trusting the model to build the tables by
hand. Pure standard library, zero dependencies. Operates only on the tasks.md
markdown artifact, so it is stack-agnostic and tool-agnostic.

What it checks (heuristic markdown inspection, not a full parser):
  ERROR  - a required section is missing
  ERROR  - a task is missing its `Tests` or `Gate` field
  ERROR  - a task whose `Where` names no file, whose `Reuses` is empty or names no file
           (`none - <why>` is an answer), or whose `Done when` has no `- [ ]` item
  ERROR  - a task depends on a task in a LATER phase (dependencies point back only)
  ERROR  - a dependency edge shown in the diagram has no matching `Depends on`
           (and vice-versa) when both sides are parseable
  WARN   - a task's `Where` names multiple files (granularity smell -> split it)
  WARN   - a task says `Tests: none` (confirm the coverage matrix agrees)
  WARN   - the diagram could not be parsed confidently (cross-check skipped)
  ERROR  - with --execute: plan.md or tasks.md has no `**Approved**: <date> - user: "<their words>"`
  ERROR  - for a screen whose plan names `**Prototype:** prototype/<stem>.html`: no task's Done
           when cites its photos; a piece of its `**Pieces:**` line, with its variant, missing from
           the Reuses of the tasks that build it; or a new or changed piece and no `Depends on`

The checks and the `Build:` line live in checks.md, and validate_checks.py owns them.

Usage:
  python3 <spec-plan>/scripts/validate_tasks.py [target] [--root DIR] [--strict] [--execute]

  Invoke from the skill directory that ships this script (not the project root).
  target    Path to a tasks.md, a feature directory, or a project root.
            Omitted -> auto-detect the single feature under <root>/.specs/features/.
  --root    Project root that contains .specs/ (default: current dir).
  --strict  Treat warnings as errors.

Exit codes: 0 pass, 1 errors found (or warnings under --strict), 2 usage error.
"""

import argparse
import os
import re
import sys

from lean_config import unapproved

REQUIRED_SECTIONS = ["Test Coverage Matrix", "Execution Plan", "Task Breakdown"]
NONE_WHY_RE = re.compile(r"^`?none`?\s*-\s*\S", re.IGNORECASE)
NAMED_RE = re.compile(r"`[^`]*\S[^`]*`")
DONE_ITEM_RE = re.compile(r"^[-*]\s+\[[ xX]\]\s*\S")
TASK_RE = re.compile(r"^#{2,4}\s+(T\d+)\s*:", re.IGNORECASE)
EDGE_RE = re.compile(r"\bT\d+\b")
FILE_HINT_RE = re.compile(r"[\w./-]+\.\w{1,6}\b")


def resolve_tasks(target, root):
    if target:
        if os.path.isfile(target):
            return target
        if os.path.isdir(target):
            cand = os.path.join(target, "tasks.md")
            if os.path.isfile(cand):
                return cand
            return _autodetect(target)
        # Not a path: treat as a feature name under <root>/.specs/features/<name>/
        cand = os.path.join(root, ".specs", "features", target, "tasks.md")
        if os.path.isfile(cand):
            return cand
        return None
    return _autodetect(root)


def _autodetect(root):
    base = os.path.join(root, ".specs", "features")
    if not os.path.isdir(base):
        return None
    features = [d for d in sorted(os.listdir(base)) if os.path.isfile(os.path.join(base, d, "tasks.md"))]
    if len(features) == 1:
        return os.path.join(base, features[0], "tasks.md")
    if len(features) == 0:
        return None
    raise SystemExit(
        "validate_tasks: multiple features found; pass one explicitly:\n  "
        + "\n  ".join(os.path.join(base, f, "tasks.md") for f in features)
    )


def section_present(lines, name):
    return any(re.match(r"^#{1,4}\s+" + re.escape(name) + r"\b", ln.strip()) for ln in lines)


def parse_tasks(lines):
    """Return a dict: task_id -> {'deps': set, 'tests': str|None, 'gate': str|None, 'where': str,
    'reuses': str|None, 'done': int}."""
    tasks = {}
    current = None
    in_done = False
    for ln in lines:
        m = TASK_RE.match(ln.strip())
        if m:
            current = m.group(1).upper()
            tasks[current] = {"deps": set(), "tests": None, "gate": None, "where": "", "reuses": None, "done": 0,
                              "done_text": []}
            in_done = False
            continue
        if current is None:
            continue
        stripped = ln.strip()
        if re.match(r"^#{1,4}\s", stripped):
            current, in_done = None, False
            continue
        if re.match(r"^\*{0,2}Done when\*{0,2}\s*:", stripped, re.IGNORECASE):
            in_done = True
            continue
        if in_done:
            if DONE_ITEM_RE.match(stripped):
                tasks[current]["done"] += 1
                tasks[current]["done_text"].append(stripped)
                continue
            if re.match(r"^\*{0,2}[A-Z][\w ]*\*{0,2}\s*:", stripped):
                in_done = False
        rm = re.match(r"^\*{0,2}Reuses\*{0,2}\s*:\s*(.*)$", stripped, re.IGNORECASE)
        if rm:
            tasks[current]["reuses"] = rm.group(1).strip()
        dm = re.match(r"^\*{0,2}Depends on\*{0,2}\s*:\s*(.*)$", stripped, re.IGNORECASE)
        if dm:
            body = dm.group(1)
            if "none" not in body.lower():
                for e in EDGE_RE.findall(body.upper()):
                    tasks[current]["deps"].add(e)
        wm = re.match(r"^\*{0,2}Where\*{0,2}\s*:\s*(.*)$", stripped, re.IGNORECASE)
        if wm:
            tasks[current]["where"] = wm.group(1)
        tm = re.match(r"^\*{0,2}Tests\*{0,2}\s*:\s*(.*)$", stripped, re.IGNORECASE)
        if tm:
            tasks[current]["tests"] = tm.group(1).strip()
        gm = re.match(r"^\*{0,2}Gate\*{0,2}\s*:\s*(.*)$", stripped, re.IGNORECASE)
        if gm:
            tasks[current]["gate"] = gm.group(1).strip()
    return tasks


def parse_phase_membership(lines, declared):
    """Map task_id -> phase index, read from the diagram under each '### Phase N' header
    of the `## Execution Plan`. Task headers (### Tn:) all sit in the Task Breakdown, after
    the last phase, so they cannot place a task. The first phase whose diagram names a
    declared task owns it."""
    membership = {}
    in_plan = False
    phase_idx = None
    in_fence = False
    for ln in lines:
        stripped = ln.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            if phase_idx is not None:
                for tid in EDGE_RE.findall(stripped.upper()):
                    if tid in declared:
                        membership.setdefault(tid, phase_idx)
            continue
        if re.match(r"^##\s", stripped):
            in_plan = stripped[2:].strip().lower().startswith("execution plan")
            phase_idx = None
            continue
        pm = re.match(r"^#{3,4}\s+Phase\s+(\d+)", stripped, re.IGNORECASE)
        if pm and in_plan:
            phase_idx = int(pm.group(1))
    return membership


def parse_diagram_edges(lines):
    """Best-effort: parse 'Tx -> Ty' / 'Tx → Ty' arrow chains from fenced blocks.
    Returns (edges:set[(src,dst)], parsed:bool)."""
    edges = set()
    in_fence = False
    found_any_arrow = False
    for ln in lines:
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        # normalize arrow glyphs
        norm = ln.replace("→", "->").replace("──", "-").replace("-", "-")
        if "->" not in norm:
            continue
        chain = EDGE_RE.findall(norm.upper())
        # only treat as a chain if arrows connect them left-to-right
        segments = [s for s in re.split(r"->", norm)]
        seq = []
        for seg in segments:
            ids = EDGE_RE.findall(seg.upper())
            seq.append(ids[-1] if ids else None)
        for a, b in zip(seq, seq[1:]):
            if a and b:
                edges.add((a, b))
                found_any_arrow = True
    return edges, found_any_arrow


PIECE_RE = re.compile(r"(`[^`]+`)\s*\(`([^`]+\.\w{1,6})`\)")   # `<piece> <variant>` (`<file>`)
PROTO_LINE_RE = re.compile(r"^\**\s*Prototype\s*\**\s*:\s*\**\s*`?prototype/([\w.-]+)\.html", re.IGNORECASE)
PIECES_LINE_RE = re.compile(r"^\**\s*Pieces\s*\**\s*:\s*\**\s*(.*)$", re.IGNORECASE)


def screens_with_prototype(plan_path):
    """[(stem, [(`<piece> <variant>`, file)], has a new or changed piece)] for each screen of the
    plan's `## Screen states` whose `**Prototype:**` line names `prototype/<stem>.html`."""
    if not os.path.isfile(plan_path):
        return []
    with open(plan_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    out, in_states, pieces, stem = [], False, "", None

    def close():
        if stem:
            out.append((stem, PIECE_RE.findall(pieces), bool(re.search(r"\b(new|changed) piece\b", pieces))))

    for ln in lines:
        s = ln.strip()
        if re.match(r"^##\s", s):
            close()
            in_states, pieces, stem = s[2:].strip().lower() == "screen states", "", None
        elif in_states and re.match(r"^###\s", s):
            close()
            pieces, stem = "", None
        elif in_states:
            pm, qm = PIECES_LINE_RE.match(s), PROTO_LINE_RE.match(s)
            if pm:
                pieces = pm.group(1)
            if qm:
                stem = qm.group(1)
    close()
    return out


def check_pieces(tasks, tasks_path):
    """Each piece of a prototype's screen, with its variant, is in the Reuses of the tasks that
    build that screen - the tasks whose Done when cites its photos (tasks.md)."""
    errors = []
    fdir = os.path.dirname(os.path.abspath(tasks_path))
    root = os.path.dirname(os.path.dirname(os.path.dirname(fdir)))
    for stem, pieces, new in screens_with_prototype(os.path.join(fdir, "plan.md")):
        own = [t for t in tasks.values() if f"captures/{stem}-row" in " ".join(t["done_text"])]
        if not own:
            errors.append(f"no task's `Done when` cites `captures/{stem}-row<n>-<width>.png` - the task that "
                          "builds the screen names the photos it must match")
            continue
        reuses = "\n".join(t["reuses"] or "" for t in own)
        for label, f in pieces:
            if os.path.isfile(os.path.join(root, f)) and (f not in reuses or label not in reuses):
                errors.append(f"screen `{stem}`: {label} (`{f}`) from the plan's `**Pieces:**` line is in no "
                              "`Reuses` of the tasks that build that screen - copy the piece, variant and file")
        if new and not any(t["deps"] for t in own):
            errors.append(f"screen `{stem}` has a new or changed piece and its tasks depend on no task - name "
                          "the task that builds the shared piece in `Depends on`")
    return errors


def check(tasks_path):
    with open(tasks_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    errors, warnings = [], []

    for name in REQUIRED_SECTIONS:
        if not section_present(lines, name):
            errors.append(f"missing required section: ## {name}")

    tasks = parse_tasks(lines)
    if not tasks:
        warnings.append("no tasks (### T1: ...) parsed - is this file filled in?")
        return errors, warnings

    # Field presence + granularity smell.
    for tid, t in tasks.items():
        if t["tests"] is None:
            errors.append(f"{tid}: missing `Tests` field")
        elif t["tests"].lower().startswith("none"):
            warnings.append(f"{tid}: Tests: none - confirm the Test Coverage Matrix says 'none' for this layer")
        if t["gate"] is None:
            errors.append(f"{tid}: missing `Gate` field")
        files = FILE_HINT_RE.findall(t["where"])
        if not files:
            errors.append(f"{tid}: `Where` names no file - write the path of the file this task creates or changes")
        reuses = t["reuses"] or ""
        if not reuses:
            errors.append(f"{tid}: missing `Reuses` - name the existing file or pattern this task builds on, "
                          "or write `none - <why>`")
        elif not (NONE_WHY_RE.match(reuses) or FILE_HINT_RE.search(reuses) or NAMED_RE.search(reuses)):
            errors.append(f"{tid}: `Reuses` names no file - name the existing file or pattern in backticks, "
                          "or write `none - <why>`")
        if not t["done"]:
            errors.append(f"{tid}: `Done when` has no `- [ ]` item - list what proves this task done")
        if len(set(files)) > 1:
            warnings.append(f"{tid}: `Where` names multiple files {sorted(set(files))} - granularity smell, consider splitting")

    errors += check_pieces(tasks, tasks_path)

    # Forward-phase dependency.
    membership = parse_phase_membership(lines, tasks)
    for tid, t in tasks.items():
        p_here = membership.get(tid)
        if p_here is None:
            continue
        for dep in t["deps"]:
            p_dep = membership.get(dep)
            if p_dep is not None and p_dep > p_here:
                errors.append(f"{tid} (phase {p_here}) depends on {dep} (phase {p_dep}) - dependencies must point backward or within the same phase")

    # Diagram vs definition cross-check (best effort).
    edges, parsed = parse_diagram_edges(lines)
    if not parsed:
        warnings.append("diagram arrows not parsed confidently - diagram/definition cross-check skipped (verify by hand)")
    else:
        def intra_phase(a, b):
            # Parity applies only within a phase. A backward cross-phase dependency
            # is validated by the forward-phase check above and needs no diagram arrow;
            # phase diagrams are drawn per phase, so cross-phase edges are out of scope here.
            pa, pb = membership.get(a), membership.get(b)
            if pa is None or pb is None:
                return True  # unknown phase -> keep best-effort parity
            return pa == pb

        dep_edges = set()
        for tid, t in tasks.items():
            for dep in t["deps"]:
                dep_edges.add((dep, tid))  # arrow points dep -> task
        only_in_diagram = {(a, b) for (a, b) in (edges - dep_edges) if intra_phase(a, b)}
        only_in_defs = {(a, b) for (a, b) in (dep_edges - edges) if intra_phase(a, b)}
        for a, b in sorted(only_in_diagram):
            if a in tasks and b in tasks:
                errors.append(f"diagram shows {a} -> {b} but {b} has no matching `Depends on: {a}`")
        for a, b in sorted(only_in_defs):
            errors.append(f"{b} declares `Depends on: {a}` but the diagram has no {a} -> {b} arrow")

    return errors, warnings


def main(argv=None):
    p = argparse.ArgumentParser(prog="validate_tasks.py", description="Pre-approval checks for a feature tasks.md.")
    p.add_argument("target", nargs="?", default=None)
    p.add_argument("--root", default=".")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--execute", action="store_true",
                   help="Before the first task: also require the plan and the tasks approved in the user's words")
    args = p.parse_args(argv)

    tasks_path = resolve_tasks(args.target, args.root)
    if not tasks_path:
        print("validate_tasks: could not locate a tasks.md. Pass a path or run from the project root.", file=sys.stderr)
        return 2

    errors, warnings = check(tasks_path)
    if args.execute:
        for name in unapproved(os.path.dirname(os.path.abspath(tasks_path))):
            errors.append(
                f"{name} has no `**Approved**: <YYYY-MM-DD> - user: \"<their words>\"` line - Execute starts "
                f"after the user approves; present it and stop, never write the approval yourself")
    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    fail = errors or (warnings and args.strict)
    print(f"\nvalidate_tasks: {len(errors)} error(s), {len(warnings)} warning(s) in {tasks_path}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
