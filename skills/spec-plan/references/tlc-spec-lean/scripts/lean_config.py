"""
lean_config.py - what a feature's artifacts say the Verifier owes, read the same way by every gate.

Two facts decide it: whether the feature has a screen (the screen comparison), and whether plan.md's
`## Sources` marks a source binding (the binding-source comparison). The shape of a `Run` group and
of a proof that reads one lives here too. validate_checks.py, validate_verification.py and
check_proofs.py act on these, so they live in one place - two copies of the same rule drift until
one gate demands what the other does not.

Every function takes lines already stripped of fenced blocks.
"""

import re

RUN_RE = re.compile(r"^\**\s*Run\s+([\w-]+)\s*\**\s*:\s*(.+)$", re.IGNORECASE)
RUN_PROOF_RE = re.compile(r"^run\s+([\w-]+)\s*\|\s*(.*)$", re.IGNORECASE)
BINDING_RE = re.compile(r"(?<![-\w])binding\b", re.IGNORECASE)
NOT_BINDING_RE = re.compile(r"\b(non|not)[- ]binding\b", re.IGNORECASE)
CAPTURE_RE = re.compile(r"`([^`\s]+\.(?:png|jpe?g|webp|gif))`", re.IGNORECASE)
SCREEN_CRITERION_RE = re.compile(r"\bSHALL\s+(?:NOT\s+)?(?:show|display|render|hide)\b", re.IGNORECASE)
PROOF_RE = re.compile(r"^\**\s*Proof\s*\**\s*:\s*`?browser\b", re.IGNORECASE)
CRITERION_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
APPROVED_RE = re.compile(
    r"^\**\s*Approved\s*\**\s*:\s*\**\s*\d{4}-\d{2}-\d{2}\b.*\buser\s*:\s*[\"“][^\"”]*\S[^\"”]*[\"”]",
    re.IGNORECASE)


def plan_approved(plan_lines):
    """True when plan.md carries `**Approved**: <date> - user: "<their words>"`. The approval is the
    user's, so it carries their words; the chat that held it does not survive a compaction."""
    return any(APPROVED_RE.match(s.strip()) for s in plan_lines)


def read_runs(lines):
    """{name: command} for every `Run <name>: <command>` line."""
    runs = {}
    for ln in lines:
        m = RUN_RE.match(ln.strip())
        if m:
            runs[m.group(1)] = m.group(2).strip().strip("`").strip()
    return runs


def _section(lines, name):
    """The lines under a `#`/`##` heading named `name`, up to the next `#`/`##` heading."""
    out, inside = [], False
    for ln in lines:
        s = ln.strip()
        if re.match(r"^#{1,2}\s+\S", s):
            inside = re.match(r"^#{1,2}\s+" + re.escape(name) + r"\b", s, re.IGNORECASE) is not None
            continue
        if inside:
            out.append(s)
    return out


def plan_criteria(plan_lines):
    """The text of every numbered criterion under `## Criteria`."""
    out = []
    for s in _section(plan_lines, "Criteria"):
        m = CRITERION_RE.match(s)
        if m:
            out.append(m.group(1))
    return out


def plan_has_screen(plan_lines, checks_lines=()):
    """True when the feature puts a screen in front of a user.

    A criterion that cites a capture or says the system SHALL show, display, render or hide
    something is a screen criterion; so is a `browser` proof in checks.md.
    """
    for text in plan_criteria(plan_lines):
        if CAPTURE_RE.search(text) or SCREEN_CRITERION_RE.search(text):
            return True
    return any(PROOF_RE.match(s.strip()) for s in checks_lines)


def plan_marks_binding(plan_lines):
    """True when plan.md's `## Sources` marks a source binding (the binding-source comparison runs)."""
    return any(BINDING_RE.search(s) and not NOT_BINDING_RE.search(s) for s in _section(plan_lines, "Sources"))


GATE_SECTION = "Gate Check Commands"
_PLACEHOLDER_CELL = re.compile(r"^\s*(?:\[.*\]|<.*>|-|)\s*$")


def gate_commands_errors(doc_lines, doc_name):
    """Errors when `## Gate Check Commands` is missing or holds no runnable suite row.

    The section lists the complete test battery the planning discovered: one row per suite,
    `| Suite | Command | Needs running |`. A command cell is a backticked command or
    `none - <why>`; a placeholder is not an answer.
    """
    body = _section(doc_lines, GATE_SECTION)
    if not any(re.match(r"^#{1,2}\s+" + re.escape(GATE_SECTION) + r"\b", s.strip(), re.IGNORECASE)
               for s in doc_lines):
        return [f"{doc_name} has no `## {GATE_SECTION}` section - the planning lists every test suite "
                "and its command for the user to confirm before build"]
    rows = [s for s in body if s.startswith("|")]
    data = [r for r in rows if not (re.match(r"^\s*\|?[\s:|-]+\|?\s*$", r) and "-" in r)][1:]
    good = 0
    errors = []
    for r in data:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        if len(cells) < 2 or _PLACEHOLDER_CELL.match(cells[0]):
            continue
        cmd = cells[1]
        if re.search(r"`[^`]*\S[^`]*`", cmd) or re.match(r"^none\s*-\s*\S", cmd, re.IGNORECASE):
            good += 1
        else:
            errors.append(f"{doc_name} `## {GATE_SECTION}`: suite '{cells[0][:40]}' has no command "
                          "(a backticked command, or `none - <why>`)")
    if not good and not errors:
        errors.append(f"{doc_name} `## {GATE_SECTION}` has no suite row - list every existing suite with its command")
    return errors
