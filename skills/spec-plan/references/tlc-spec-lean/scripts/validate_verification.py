#!/usr/bin/env python3
"""
validate_verification.py - deterministic completion gate for a feature.

A feature is done when check_proofs.py shows every proof green at HEAD and the Verifier's findings
are each closed by a commit. That is prose a long trajectory quietly drops, so this turns it into a
pass/fail run as the closing step. It reads the artifacts, never the target codebase.

What it checks:
  ERROR  - no verification.md, or no proofs.md (run check_proofs.py)
  ERROR  - proofs.md written at another commit than HEAD, or over uncommitted changes
  ERROR  - a check in checks.md with no row in proofs.md, or a row that is not `pass`
  ERROR  - checks.md names `Build:` commands and proofs.md has no Build row, or one that failed
  ERROR  - no `## Checks` table in verification.md, a check with no row in it, or a row with no test
  ERROR  - no `## Findings` section in verification.md, or a finding with no commit in `Closed`
  ERROR  - a `walk` proof and no `**Walked:**` line in the Handoff
  ERROR  - plan.md (or checks.md without a plan) with no actual `**Approved**:` authorization
  ERROR  - verification.md names no reviewed HEAD, code changed since it, or Fixes is not 0..3
  WARN   - the report says self-verified (author == verifier: a degraded gate)

Usage:
  python3 <skill-dir>/scripts/validate_verification.py [feature] [--root DIR] [--strict]

  Pass --root when cwd is not the project that contains .specs/.

Exit codes: 0 ok, 1 the feature is not done, 2 usage error.
"""

import argparse
import os
import re
import subprocess
import sys

from lean_config import _section, plan_approved

PROOF_RE = re.compile(r"^\**\s*Proof\s*\**\s*:\s*(.+)$", re.IGNORECASE)
JUDGED_HEAD_RE = re.compile(r"^\**\s*HEAD\s*\**\s*:\s*\**\s*`?([0-9a-f]{7,40})", re.IGNORECASE)
FIXES_RE = re.compile(r"^\**\s*Fixes\s*\**\s*:\s*(\d+)\s*$", re.IGNORECASE)
MAX_CODE_FIXES = 3
# Local compatibility: F's explicit user refusal, stored in Lean's existing Closed cell.
REFUSED_RE = re.compile(r'^Refused\s*-\s*user:\s*(?:"([^"\r\n]+)"|“([^“”\r\n]+)”)\s*$', re.IGNORECASE)
EMPTY_CELL = {"", "-", "—", "–", "none", "n/a", "na", "nothing"}
SURVIVED_RE = re.compile(r"\b(no|survived|alive|not killed)\b", re.IGNORECASE)
VERDICT_LINE_RE = re.compile(r"^\**verdict\**\s*:", re.IGNORECASE)
WALK_PROOF_RE = re.compile(r"^`?walk\b", re.IGNORECASE)
WALKED_RE = re.compile(r"^\s*[-*]?\s*\**walked\**\s*:", re.IGNORECASE)


def _feature_dirs(root):
    base = os.path.join(root, ".specs", "features")
    if not os.path.isdir(base):
        return base, []
    return base, [d for d in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base, d))]


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_separator(line):
    return bool(re.match(r"^\s*\|?[\s:|-]+\|?\s*$", line)) and "-" in line


def strip_fences(text):
    """Drop fenced blocks: a report that pasted the template must not be read as data."""
    out, in_fence = [], False
    for ln in text.splitlines():
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(ln)
    return out


def find_tables(lines):
    """Return [(header_cells_lowercased, [data_row_cells, ...]), ...] for every table."""
    tables, buf = [], []
    for ln in lines + [""]:
        stripped = ln.strip()
        if stripped.startswith("|"):
            buf.append(stripped)
            continue
        if buf:
            rows = [split_row(r) for r in buf if not is_separator(r)]
            if len(rows) >= 2:
                tables.append(([c.lower() for c in rows[0]], rows[1:]))
            buf = []
    return tables


def column(header, *names):
    for i, cell in enumerate(header):
        for n in names:
            if n in cell:
                return i
    return None


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _plan_lines(fdir):
    path = os.path.join(fdir, "plan.md")
    if not os.path.exists(path):
        return []
    return strip_fences(_read(path))


def _code_changed_since(root, sha):
    """Paths outside `.specs/` changed between `sha` and HEAD; None when git cannot say."""
    try:
        inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root,
                                capture_output=True, text=True)
        if inside.returncode != 0:
            return None
        p = subprocess.run(["git", "diff", "--name-only", sha, "HEAD"], cwd=root, capture_output=True, text=True)
    except OSError:
        return None
    if p.returncode != 0:
        return [f"<{sha} is not a commit here>"]
    return [f for f in p.stdout.split() if not f.startswith(".specs/")]


def _walk_logged(checks_lines, name):
    """A `walk` proof's evidence is the author's `**Walked:**` line; with none, nothing was visited."""
    walks = [ln for ln in checks_lines
             if (m := PROOF_RE.match(ln.strip())) and WALK_PROOF_RE.match(m.group(1).strip())]
    if walks and not any(WALKED_RE.match(ln) for ln in _section(checks_lines, "Handoff")):
        return [
            f"{name}: checks.md has a `walk` proof but its `## Handoff` has no `**Walked:**` line - "
            f"the visit the proof names is not on record"
        ]
    return []


CHECK_ID_RE = re.compile(r"^\**\s*(C\d+)\s*\**\s*[-–—:]")
SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b")


def _git_head(root):
    try:
        p = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True)
    except OSError:
        return None
    return p.stdout.strip() if p.returncode == 0 else None


def _verdict(lines):
    """Return 'pass', 'fail', 'unfilled', or None."""
    candidates = [
        ln for ln in lines
        if re.search(r"^\**verdict\**\s*:", ln.strip(), re.IGNORECASE)
        or re.search(r"^#{1,4}\s*validation\b", ln.strip(), re.IGNORECASE)
    ]
    hay = " ".join(candidates) if candidates else "\n".join(lines)
    has_pass = re.search(r"\bPASS\b", hay, re.IGNORECASE) is not None
    has_fail = re.search(r"\bFAIL\b", hay, re.IGNORECASE) is not None
    if has_pass and has_fail:
        # Both present on the verdict line = unfilled template "[PASS | FAIL]".
        return "unfilled"
    if has_pass:
        return "pass"
    if has_fail:
        return "fail"
    return None


def _check_with_proofs(fdir, name, lines, checks_lines):
    """The report format where check_proofs.py ran the proofs: proofs.md holds the evidence,
    verification.md the Verifier's judgement of each check and its findings, each closed by a commit."""
    errors, warnings = [], []
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(fdir))))
    plines = strip_fences(_read(os.path.join(fdir, "proofs.md")))
    pbody = "\n".join(plines)

    m = re.search(r"\*\*HEAD\*\*\s*:\s*`?([0-9a-f]{4,40})", pbody)
    head = _git_head(root)
    if not m:
        errors.append(f"{name}: proofs.md names no `**HEAD**` - run check_proofs.py again")
    elif head and not (head.startswith(m.group(1)) or m.group(1).startswith(head)):
        errors.append(f"{name}: proofs.md was written at {m.group(1)} and HEAD is {head} - run check_proofs.py again")

    tree = re.search(r"\*\*Tree\*\*\s*:\s*(\S+)", pbody)
    if tree and tree.group(1).lower().startswith("dirty"):
        errors.append(f"{name}: proofs.md ran on uncommitted changes - commit them and run check_proofs.py again")

    ids = {mm.group(1) for mm in (CHECK_ID_RE.match(ln.strip()) for ln in checks_lines) if mm}
    seen = set()
    for header, rows in find_tables(plines):
        result, check = column(header, "result"), column(header, "check")
        if result is not None and check is not None:
            for r in rows:
                if check < len(r):
                    seen.add(r[check])
                if result < len(r) and not r[result].lower().startswith("pass"):
                    errors.append(f"{name}: proofs.md - {r[check]} reads '{r[result][:40]}'")
    for cid in sorted(ids - seen, key=lambda c: int(c[1:])):
        errors.append(f"{name}: proofs.md has no row for {cid} - run check_proofs.py again")
    build = next((ln.strip() for ln in checks_lines if re.match(r"^\**\s*Build\s*\**\s*:", ln.strip(), re.IGNORECASE)), "")
    if build and "none" not in build.lower()[:15] and "Build" not in seen:
        errors.append(f"{name}: checks.md names `Build:` commands and proofs.md has no Build row - run check_proofs.py again")

    judged = {}
    for header, rows in find_tables(_section(lines, "Checks")):
        check, test = column(header, "check"), column(header, "test")
        if check is None or test is None:
            continue
        for r in rows:
            if check < len(r):
                judged[r[check].strip("*` ")] = r[test].strip() if test < len(r) else ""
    if ids and not judged:
        errors.append(f"{name}: verification.md has no `## Checks` table - the Verifier opens the test each check's "
                      f"proof selects and writes whether it holds the criterion")
    elif judged:
        for cid in sorted(ids, key=lambda c: int(c[1:])):
            if cid not in judged:
                errors.append(f"{name}: verification.md `## Checks` has no row for {cid} - judge its test against "
                              f"the criterion")
            elif judged[cid] in ("", "-"):
                errors.append(f"{name}: verification.md `## Checks` row {cid} names no test - write the test the "
                              f"proof selects, file and name")

    findings = _section(lines, "Findings")
    if not findings:
        errors.append(f"{name}: verification.md has no `## Findings` section (write `None - <why>` when empty)")
    finding_rows = {}
    for header, rows in find_tables(findings):
        closed = column(header, "closed")
        finding = header.index("finding") if "finding" in header else None
        for r in rows:
            cell = r[closed].strip() if closed is not None and closed < len(r) else ""
            refusal = REFUSED_RE.fullmatch(cell)
            refused = bool(refusal and any(s and s.strip() for s in refusal.groups()))
            if finding is not None and finding < len(r):
                finding_rows.setdefault(r[finding], []).append(refused)
            # F permits an actual user refusal instead of a fix; the local wrapper keeps
            # that decision in Closed, not F's separate Refused column.
            if re.match(r"^Refused\b", cell, re.IGNORECASE):
                if refused:
                    continue
                closed_by_commit = False
            else:
                closed_by_commit = bool(SHA_RE.search(cell))
            if not closed_by_commit:
                errors.append(f"{name}: finding '{r[0][:50]}' is not closed - write the fixing commit or the "
                              "user's actual quoted refusal in `Closed`")
    # Preserve F's survivor contradiction guard without requiring a sensor table or count.
    if any(VERDICT_LINE_RE.search(ln.strip()) for ln in lines) and _verdict(lines) == "pass":
        sensor_tables = [(h, rows) for h, rows in find_tables(lines)
                         if column(h, "killed") is not None]
        fault_counts = {}
        for header, rows in sensor_tables:
            fault = header.index("fault") if "fault" in header else None
            if fault is not None:
                for r in rows:
                    if fault < len(r):
                        fault_counts[r[fault]] = fault_counts.get(r[fault], 0) + 1
        # The gate reads the report's own tables and refuses a verdict its rows contradict.
        for header, rows in sensor_tables:
            killed = column(header, "killed")
            fault = header.index("fault") if "fault" in header else None
            if killed is not None:
                for r in rows:
                    if killed >= len(r):
                        continue
                    cell = r[killed]
                    if cell.lower() in EMPTY_CELL and cell.lower() != "no":
                        continue
                    if SURVIVED_RE.match(cell) or "survived" in cell.lower():
                        # Only this uniquely identified fault's own quoted refusal can
                        # settle its survivor. Other findings and ambiguous labels cannot.
                        label = r[fault] if fault is not None and fault < len(r) else ""
                        if (label and fault_counts.get(label) == 1
                                and finding_rows.get(label) == [True]):
                            continue
                        errors.append(
                            f"{name}: PASS but a mutant survived ({r[0][:50]}) - the assertion would "
                            f"pass under a plausible wrong implementation"
                        )
    return errors, warnings


def _check_feature(fdir, name):
    errors, warnings = [], []
    if not os.path.exists(os.path.join(fdir, "verification.md")):
        errors.append(
            f"{name}: no verification.md - the feature is not done until a fresh Verifier "
            f"(author != verifier) writes its findings over <feature base>..HEAD"
        )
    if not os.path.exists(os.path.join(fdir, "proofs.md")):
        errors.append(f"{name}: no proofs.md - run check_proofs.py <feature> at HEAD")
    if errors:
        return errors, warnings

    lines = strip_fences(_read(os.path.join(fdir, "verification.md")))
    cpath = os.path.join(fdir, "checks.md")
    checks_lines = strip_fences(_read(cpath)) if os.path.exists(cpath) else []
    errors, warnings = _check_with_proofs(fdir, name, lines, checks_lines)
    verdicts = [
        VERDICT_LINE_RE.sub("", ln.strip()).strip().upper()
        for ln in lines if VERDICT_LINE_RE.search(ln.strip())
    ]
    if verdicts != ["PASS"]:
        errors.append(f"{name}: verification.md needs an explicit `**Verdict**: PASS`")
    # Mechanical proofs at HEAD do not replace judgement on the corrected code.
    fixes = next((int(m.group(1)) for m in (FIXES_RE.match(ln.strip()) for ln in lines) if m), None)
    if fixes is None or fixes > MAX_CODE_FIXES:
        errors.append(f"{name}: verification.md needs `**Fixes**: 0..3` - initial review plus at most three "
                      "code fix-to-review iterations; remaining failures go to the user")
    judged = next((m.group(1) for m in (JUDGED_HEAD_RE.match(ln.strip()) for ln in lines) if m), None)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(fdir))))
    head = _git_head(root)
    unknown = any(re.match(r"^\**\s*HEAD\s*\**\s*:\s*unknown\s*$", ln.strip(), re.IGNORECASE) for ln in lines)
    if not judged and not (head is None and unknown):
        errors.append(f"{name}: verification.md names no reviewed `**HEAD**` - a fresh Verifier records it")
    if head is None:
        warnings.append(f"{name}: no git HEAD - independent review freshness cannot be checked (degraded)")
    elif judged:
        changed = _code_changed_since(root, judged)
        if changed is None or changed:
            errors.append(f"{name}: verification.md needs a fresh independent review at the current code HEAD")
    if "self-verified" in "\n".join(lines).lower():
        warnings.append(f"{name}: verification.md says self-verified - author == verifier, a degraded gate")
    plan = _plan_lines(fdir)
    approval = plan if os.path.isfile(os.path.join(fdir, "plan.md")) else checks_lines
    if not plan_approved(approval):
        document = "plan.md" if os.path.isfile(os.path.join(fdir, "plan.md")) else "checks.md"
        errors.append(f"{name}: {document} has no `**Approved**: <YYYY-MM-DD> - user: \"<their words>\"` line - "
                      "record the user's actual authorization before code")
    errors += _walk_logged(checks_lines, name)
    return errors, warnings


def _appears_complete(fdir):
    if os.path.exists(os.path.join(fdir, "verification.md")):
        return True
    checks = os.path.join(fdir, "checks.md")
    if not os.path.exists(checks):
        return False
    body = _read(checks)
    if not re.search(r"^\**\s*C\d+\s*\**\s*[-–—:]", body, re.MULTILINE):
        return False
    if re.search(r"^\s*-\s*\[\s\]", body, re.MULTILINE):
        return False
    return True


def _resolve(root, feature):
    base, dirs = _feature_dirs(root)
    # An explicit argument is answered on its own terms: "that feature is not here" beats
    # "there is no features directory", which is true but not what was asked.
    if feature:
        fdir = feature if os.path.isdir(feature) else os.path.join(base, feature)
        if not os.path.isdir(fdir):
            print(f"validate_verification: feature not found: {feature}", file=sys.stderr)
            raise SystemExit(2)
        return [(fdir, os.path.basename(fdir.rstrip("/")))]
    if not os.path.isdir(base):
        print(f"validate_verification: no {base} directory - nothing to check.")
        return []
    if len(dirs) == 1:
        return [(os.path.join(base, dirs[0]), dirs[0])]
    if not dirs:
        print("validate_verification: no features under .specs/features/ - nothing to check.")
        return []
    picked = [(os.path.join(base, d), d) for d in dirs if _appears_complete(os.path.join(base, d))]
    if not picked:
        print("validate_verification: no completed feature detected (all in progress) - nothing to gate.")
    return picked


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="validate_verification.py",
        description="Completion gate: a done feature needs a real PASS report its own rows do not contradict.",
    )
    p.add_argument("feature", nargs="?", default=None, help="Feature dir or name")
    p.add_argument("--root", default=".", help="Project root containing .specs/ (default: current dir)")
    p.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    p.add_argument("--allow-empty", action="store_true",
                   help="Exit 0 when there is no completed feature to gate (repo-wide sweeps)")
    args = p.parse_args(argv)
    root = os.path.abspath(args.root)

    targets = _resolve(root, args.feature)
    if not targets and not args.allow_empty:
        # Gating nothing is not a pass. This is the completion gate for a feature that was just
        # built, so an empty run means the report could not be found - which reads as green to
        # anything checking only the exit code. Exit 2 says "could not gate", like the other
        # validators do, and leaves 0 to mean a report was read and held up.
        print(
            "validate_verification: gated nothing - this is NOT a pass. Point it at the feature "
            "(validate_verification.py <feature> --root <project>), or pass --allow-empty if you "
            "meant to sweep a repo that has no completed feature yet.",
            file=sys.stderr,
        )
        return 2

    all_errors, all_warnings = [], []
    for fdir, name in targets:
        e, w = _check_feature(fdir, name)
        all_errors += e
        all_warnings += w

    for w in all_warnings:
        print(f"  WARN  {w}")
    for e in all_errors:
        print(f"  ERROR {e}")
    checked = ", ".join(name for _, name in targets) or "(none)"
    fail = all_errors or (all_warnings and args.strict)
    print(f"\nvalidate_verification: {len(all_errors)} error(s), {len(all_warnings)} warning(s) across [{checked}]")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
