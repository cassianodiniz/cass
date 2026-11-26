#!/usr/bin/env python3
"""
selftest.py - mutation testing against this skill's own gates, plus a smoke run of its tooling.

The gates in validate_plan.py, validate_checks.py and validate_verification.py are only
worth their invocation if they FAIL when the artifact is wrong. A validator that exits 0
on everything is decoration, and nothing about running it would reveal that. So the same
discipline the skill demands of a feature applies to the skill: mutate the artifact, run
the gate, and require the mutant to be killed.

Run this after editing any validator, and after editing the templates in references/ -
a template change that drifts from what a validator parses shows up here as a broken
baseline rather than as a silent pass in six months.

Fixtures live in scripts/fixtures/ as a complete, filled-in worked example (a real feature
shape, not placeholders). They double as the reference for what a passing artifact looks like.

Usage:
  python3 <spec-plan>/scripts/selftest.py [-v]

Exit codes: 0 all mutants killed and the baseline is clean, 1 otherwise.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures")
SKILLS = os.path.dirname(os.path.dirname(HERE))
SCRIPT_DIRS = [HERE, os.path.join(SKILLS, "implementar", "scripts"), os.path.join(SKILLS, "build-review", "scripts")]


def script(name):
    """Path of a script in whichever skill ships it."""
    name = name if name.endswith(".py") else name + ".py"
    for d in SCRIPT_DIRS:
        if os.path.isfile(os.path.join(d, name)):
            return os.path.join(d, name)
    return os.path.join(HERE, name)
FEATURE = "billing"


def shipped(script):
    """The plan and implement skills ship part of these scripts; a case for one they lack is skipped."""
    return os.path.isfile(globals()["script"](script))

def two_phases(s):
    return s.replace("T1 → T2 → T3 → T4", "T1 → T2\n```\n\n### Phase 2: Core\n\n```\nT3 → T4", 1)

# (validator, artifact, description, mutation, expected exit, expected message fragment)
CASES = [
    ("validate_tasks", "tasks.md", "a task whose Where names no file",
     lambda s: s.replace("**Where**: `app/billing/status_map.rb`", "**Where**: billing", 1),
     1, "T2: `Where` names no file"),
    ("validate_tasks", "tasks.md", "a task with no Reuses line",
     lambda s: s.replace("**Reuses**: `app/billing/subscription.rb` status constants\n", "", 1),
     1, "T2: missing `Reuses`"),
    ("validate_tasks", "tasks.md", "a Reuses that names no file",
     lambda s: s.replace("**Reuses**: `app/billing/subscription.rb` status constants", "**Reuses**: existing patterns", 1),
     1, "T2: `Reuses` names no file"),
    ("validate_tasks", "tasks.md", "a Done when with no item",
     lambda s: s.replace("- [ ] Every provider status maps once; an unknown one records `billing.status_unmapped`\n"
                         "- [ ] Gate check passes: `bin/rails test test/billing`\n", "", 1),
     1, "T2: `Done when` has no `- [ ]` item"),
    ("validate_tasks", "tasks.md", "a task depends on a task of a later phase",
     lambda s: two_phases(s).replace("**Depends on**: None", "**Depends on**: T3", 1),
     1, "T1 (phase 1) depends on T3 (phase 2)"),
    ("validate_tasks", "tasks.md", "a task with no Gate line",
     lambda s: s.replace("**Tests**: unit\n**Gate**: quick\n", "**Tests**: unit\n", 1),
     1, "missing `Gate` field"),
    ("validate_tasks", "tasks.md", "missing Test Coverage Matrix",
     lambda s: s.replace("## Test Coverage Matrix", "## Coverage", 1),
     1, "missing required section: ## Test Coverage Matrix"),
    ("validate_checks", "checks.md", "no Build line",
     lambda s: s.replace("Build: `bin/rubocop app/billing`\n", "", 1),
     1, "no `Build:` line"),
    ("validate_checks", "checks.md", "drop one member from a size-5 set",
     lambda s: s.replace(" · `trial_will_end` C10 | - |", " | - |", 1),
     1, "declares 5 members but only 4"),
    ("validate_checks", "checks.md", "remove a check's Proof line",
     lambda s: re.sub(r"\nProof: `bin/rails test test/billing/access_test\.rb[^\n]*\n", "\n", s),
     1, "C4 has no `Proof:` line"),
    ("validate_checks", "checks.md", "delete the concurrency sweep line",
     lambda s: s.replace("- concurrency: C7\n", ""),
     1, "dimension 'concurrency' has no line"),
    ("validate_checks", "checks.md", "bare n/a with no reason",
     lambda s: re.sub(r"- data lifecycle: n/a[^\n]*", "- data lifecycle: n/a", s),
     1, "`n/a` with no reason"),
    ("validate_checks", "checks.md", "a run proof with no Run line",
     lambda s: re.sub(r"^Run billing: [^\n]*\n", "", s, flags=re.M),
     1, "no `Run billing: <command>` line defines it"),
    ("validate_checks", "checks.md", "a run proof with no expected line",
     lambda s: s.replace("Proof: run billing | test_failed_charge_suspends = .", "Proof: run billing"),
     1, "names no line after `|`"),
    ("validate_checks", "checks.md", "a run proof with an empty expected line",
     lambda s: s.replace("Proof: run billing | test_failed_charge_suspends = .", "Proof: run billing |"),
     1, "names no line after `|`"),
    ("validate_checks", "checks.md", "a Run line no proof reads (warn)",
     lambda s: s.replace("Build: `bin/rubocop app/billing`\n", "Build: `bin/rubocop app/billing`\nRun e2e: `npx playwright test`\n"),
     0, "`Run e2e` is read by no proof"),
    ("validate_checks", "checks.md", "reference an undefined check",
     lambda s: s.replace("into it C1 ·", "into it C99 ·"),
     1, "C99 is referenced in Coverage"),
    ("validate_checks", "checks.md", "duplicate check id",
     lambda s: s.replace("**C6** - A `Suspended` subscription returns", "**C5** - A `Suspended` subscription returns"),
     1, "duplicate check id C5"),
    ("validate_checks", "checks.md", "non-empty Unproven cell",
     lambda s: s.replace("| C2, table-driven over all 9 | - |", "| C2, table-driven over all 9 | `paused` |"),
     1, "Unproven is '`paused`'"),
    ("validate_checks", "checks.md", "proof with no test selector (warn)",
     lambda s: s.replace('Proof: `bin/rails test test/billing/access_test.rb -n "/suspended_denies_paid_groups/"`',
                         "Proof: `bin/rails test`"),
     0, "names no test selector"),
    ("validate_checks", "checks.md", "vague claim (warn)",
     lambda s: s.replace("denies access to paid access groups", "handles access gracefully"),
     0, "instead of a concrete value"),

    ("validate_plan", "plan.md", "no Gate Check Commands section",
     lambda s: s.replace("## Gate Check Commands", "## Test notes"),
     1, "no `## Gate Check Commands` section"),
    ("validate_plan", "plan.md", "a suite in Gate Check Commands with no command",
     lambda s: s.replace("| Rails tests | `bin/rails test` | nothing |", "| Rails tests | ask later | nothing |"),
     1, "suite 'Rails tests' has no command"),
    ("validate_plan", "plan.md", "Gate Check Commands left as a template placeholder",
     lambda s: s.replace("| Rails tests | `bin/rails test` | nothing |\n| Lint | `bin/rubocop` | nothing |",
                         "| [suite] | [command] | [service] |"),
     1, "has no suite row"),
    ("validate_plan", "plan.md", "missing Shape section",
     lambda s: s.replace("## Shape", "## How it hangs together"),
     1, "missing required section: ## Shape"),
    ("validate_plan", "plan.md", "empty Shape section",
     lambda s: re.sub(r"## Shape\n.*?\n## Surface", "## Shape\n\n## Surface", s, flags=re.S),
     1, "Shape section is empty"),
    ("validate_plan", "plan.md", "a Shape with no Changes underneath",
     lambda s: s.replace("**Changes underneath**", "**What moves**"),
     1, "no `Changes underneath` part"),
    ("validate_plan", "plan.md", "empty Surface section",
     lambda s: re.sub(r"## Surface\n.*?\n## Landing", "## Surface\n\n## Landing", s, flags=re.S),
     1, "Surface section is empty"),
    ("validate_plan", "plan.md", "empty Landing section",
     lambda s: re.sub(r"## Landing\n.*?\n## Criteria", "## Landing\n\n## Criteria", s, flags=re.S),
     1, "Landing section is empty"),
    ("validate_plan", "plan.md", "Landing door with no rejected alternative",
     lambda s: s.replace("| a boolean `is_suspended` - cannot express the next state |", "|  |"),
     1, "no rejected alternative"),
    ("validate_plan", "plan.md", "Landing door with no literal shape",
     lambda s: s.replace("| enum value, not null, existing rows backfilled to `active` |", "|  |"),
     1, "no literal shape"),
    ("validate_plan", "plan.md", "columns and types creep into the stored shape",
     lambda s: s.replace(
         "    Subscription ||--o{ WebhookDelivery : \"reported by\"",
         "    Subscription {\n        string status\n        datetime suspended_at\n    }\n"
         "    Subscription ||--o{ WebhookDelivery : \"reported by\""),
     1, "carries an attribute block"),
    ("validate_plan", "plan.md", "a Surface route with no statuses",
     lambda s: s.replace("| `200`, `401`, `409`, `422` |", "|  |"),
     1, "names no status code"),
    ("validate_plan", "plan.md", "check ids written into Surface before checks exist",
     lambda s: s.replace("anything else gets `401` |", "anything else gets `401` | C7, C8, C9 |"),
     1, "does not exist yet"),
    ("validate_plan", "plan.md", "a restricted Surface route with no status for the callers it refuses",
     lambda s: s.replace("| `200`, `401`, `409`, `422` |", "| `200`, `409`, `422` |"),
     1, "names no code for the rest"),
    ("validate_plan", "plan.md", "a Surface table with no Who column",
     lambda s: s.replace("| Status | Who |\n| --- | --- | --- | --- | --- |", "| Status |\n| --- | --- | --- | --- |")
                .replace(" | the provider, with a valid signature; anything else gets `401` |", " |"),
     1, "no Who column"),
    ("validate_plan", "plan.md", "a Flow hop naming a module that neither exists nor is a door (warn)",
     lambda s: s.replace(
         "3. `Billing::StatusMap` (new) - provider status -> local status",
         "3. `Billing::StatusMapFactory` - provider status -> local status"),
     0, "without marking it as existing or as a"),
    ("validate_checks", "plan.md", "a route reviewed in the plan that no check mentions (warn)",
     lambda s: s.replace("`POST /webhooks/provider`", "`POST /webhooks/provider/v2`"),
     0, "owe a Coverage row, or the route is dead"),

    ("validate_plan", "plan.md", "acceptance criterion with no SHALL",
     lambda s: s.replace("THEN the system SHALL set the subscription status", "THEN we set the subscription status"),
     1, "has no SHALL"),
    ("validate_plan", "plan.md", "a criterion after a rule's indented examples is still read",
     lambda s: s.replace("THEN the system SHALL leave the status unchanged", "THEN we leave the status unchanged"),
     1, "has no SHALL"),
    ("validate_plan", "plan.md", "assumption with no rationale",
     lambda s: s.replace("| the provider already retried 3 times before it reports a failure |", "|  |"),
     1, "empty 'Rationale'"),
    ("validate_plan", "plan.md", "empty Investigation line",
     lambda s: s.replace("| 9 observability | n/a - existing billing log covers it |", "| 9 observability | |", 1),
     1, "Investigation line '9 observability' is empty"),
    ("validate_plan", "plan.md", "Investigation line with a value outside the three",
     lambda s: s.replace("| Glossary | done - GLOSSARY.md, no new term |", "| Glossary | parcial |", 1),
     1, "Investigation line 'Glossary' is empty"),
    ("validate_plan", "plan.md", "no Investigation section",
     lambda s: s.replace("## Investigation" + chr(10), "## Notes on steps" + chr(10), 1),
     1, "missing required section: ## Investigation"),
    ("validate_plan", "plan.md", "missing required section",
     lambda s: s.replace("## Assumptions", "## Open Decisions"),
     1, "missing required section: ## Assumptions"),
    ("validate_plan", "plan.md", "out hop naming a slug in backticks is not an unresolved module",
     lambda s: s.replace(
         "5. out: `200` `{}`, and `AccessPolicy` (exists) reads `status` on the next request - no call from here",
         "5. out: `200` `{}`; `completo` stays"),
     0, "0 warning"),
    ("validate_plan", "plan.md", "a path with no drawing",
     lambda s: re.sub(r"```mermaid\nsequenceDiagram\n.*?```\n", "", s, flags=re.S),
     1, "does not draw it"),
    ("validate_plan", "plan.md", "no data drawing and no `Data: none`",
     lambda s: re.sub(r"```mermaid\nerDiagram\n.*?```\n", "", s, flags=re.S),
     1, "no `erDiagram` of the data"),
    ("validate_plan", "plan.md", "a data drawing with no `New:` line",
     lambda s: s.replace("New: `WebhookDelivery` and its link to `Subscription`. ", ""),
     1, "has no `New:` line"),
    ("validate_plan", "plan.md", "a capture the plan does not show as an image",
     lambda s: with_binding(s).replace("![card form](captures/billing--card-form.png) ", ""),
     1, "is not shown in the plan"),
    ("validate_plan", "plan.md", "a single-module path owes no drawing",
     lambda s: re.sub(r"```mermaid\nsequenceDiagram\n.*?```\n", "single module - `Billing::Subscription`\n", s, flags=re.S),
     0, "0 error"),
    ("validate_plan", "plan.md", "open question left unresolved (warn)",
     lambda s: s.replace("**Open questions:** none - all resolved or logged above.",
                         "**Open questions:** what happens on a chargeback?"),
     0, "do not read as resolved"),

    ("validate_plan", "plan.md", "a plan that shows a screen capture and has no Screen states",
     lambda s: re.sub(r"## Screen states\n.*?(?=## Investigation)", "", with_binding(s), flags=re.S),
     1, "no `## Screen states`"),
    ("validate_plan", "plan.md", "a screen with no Prototype line",
     lambda s: s.replace("**Prototype:** none - the card form's text edited in place\n", ""),
     1, "no `**Prototype:**` line"),
    ("validate_plan", "plan.md", "a Prototype none that names no in-place edit",
     lambda s: s.replace("**Prototype:** none - the card form's text edited in place", "**Prototype:** none - n/a"),
     1, "`**Prototype:**` names"),
    ("validate_plan", "plan.md", "a Prototype path outside prototype/",
     lambda s: s.replace("**Prototype:** none - the card form's text edited in place", "**Prototype:** ../billing.txt"),
     1, "`**Prototype:**` names"),
    ("validate_plan", "plan.md", "a prototype file that does not exist",
     lambda s: s.replace("**Prototype:** none - the card form's text edited in place", "**Prototype:** prototype/billing.html"),
     1, "the prototype `prototype/billing.html` does not exist"),
    ("validate_plan", "plan.md", "a screen with no Pieces line",
     lambda s: re.sub(r"^\*\*Pieces:\*\*[^\n]*\n", "", s, flags=re.M),
     1, "no `**Pieces:**` line"),
    ("validate_plan", "plan.md", "a Pieces line still the template placeholder",
     lambda s: re.sub(r"^\*\*Pieces:\*\*[^\n]*", "**Pieces:** <element> - `<piece> <variant>` (<manual>:<line>)", s, flags=re.M),
     1, "no `**Pieces:**` line"),
    ("validate_plan", "plan.md", "a screen with no state rows",
     lambda s: re.sub(r"^\| (charge failed|never charged) \|[^\n]*\n", "", s, flags=re.M),
     1, "has no state rows"),
    ("validate_plan", "plan.md", "a state row that names no criterion",
     lambda s: s.replace("375 and 1280 | 1 |", "375 and 1280 |  |"),
     1, "names no criterion"),
    ("validate_plan", "plan.md", "a nothing-to-decide row with no reason",
     lambda s: s.replace("nothing to decide - the screen shows no charge state", "nothing to decide"),
     1, "names no criterion"),
    ("validate_plan", "plan.md", "Screen states with no screen heading",
     lambda s: s.replace("### Billing\n\n**Pieces:**", "**Pieces:**"),
     1, "no `### <screen>`"),

    ("validate_verification", "verification.md", "self-verified report (warn)",
     lambda s: s.replace("independent sub-agent (author != verifier)", "self-verified (degraded - no sub-agent)"),
     0, "self-verified"),
    ("validate_verification", "verification.md", "a screen-state row with no photo or test",
     lambda s: re.sub(r"^\| `captures/review-billing-row2\.png`[^\n]*\n", "", s, flags=re.M),
     1, "row 2"),
    ("validate_verification", "verification.md", "a row written as not reached under PASS",
     lambda s: s.replace("| row 2, 375 | none |", "| row 2 | not reached - no seed account |"),
     1, "not reached"),
]

LAST_AC = "7. IF a delivery carries no valid provider signature THEN the system SHALL return `401` and persist nothing\n"
SHOW_AC = "9. WHEN a member opens Billing THEN the system SHALL show `Card declined` above the plans\n"


def write_artifact(path, content):
    """Text artifacts are written as UTF-8; a picture is bytes."""
    if isinstance(content, bytes):
        with open(path, "wb") as f:
            f.write(content)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def read_artifact(path):
    """The artifact's text, or "" when it does not exist."""
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def with_screen(s):
    return s.replace(LAST_AC, LAST_AC + SHOW_AC, 1)


def with_binding_bare(s):
    return (s.replace("- provider webhook reference - the 9 statuses",
                      "- design `03` - **binding for the interface** - the 9 statuses")
            .replace("- TLC-412 - ", "- ![card form](captures/billing--card-form.png) - binding - the card form\n- TLC-412 - ", 1))


# The capture sits in the feature folder, where the scaffold always writes it.
CAPTURE = ".specs/features/billing/captures/billing--card-form.png"
DIFFERENCES = (
    "## Differences from the source\n\n| Source shows | Product shows | Confirmed |\n| --- | --- | --- |\n"
    "| Update card | Atualizar cartão | y - AD-002 |\n"
    "| invoice download link | nothing | y - AD-003 |\n\n"
)
STATE = (
    "# Project state\n\n## Decisions\n\n| ID | Decision | Rationale | Status | Date |\n| --- | --- | --- | --- | --- |\n"
    "| AD-002 | Billing copy is Portuguese, not the design's English | asked \"Which language?\", answered Portuguese | active | 2026-10-23 |\n"
    "| AD-003 | Billing ships without the invoice link | asked \"Invoice link now?\", answered TLC-420 | active | 2026-10-23 |\n"
    "| AD-004 | Billing shows a download link | superseded by AD-003 | superseded by AD-003 | 2026-10-22 |\n"
)
SCREEN_AC = f"8. WHEN a member opens Billing THEN the system SHALL show the screen in `{CAPTURE}`\n"
SCREEN_CHECK = (f"\n**C99** - A member opening Billing sees the screen in `{CAPTURE}` (AC 8)\n"
                "Proof: `bin/rails test test/system/billing_test.rb -n \"/billing screen matches capture/\"`\n")


WIDTHS = (375, 768, 1280)
PROTO_AC = ("8. WHEN a member opens Billing THEN the system SHALL show "
            + ", ".join(f"`.specs/features/billing/captures/billing-row1-{w}.png`" for w in WIDTHS) + "\n")
PROTO_FILES = {"prototype/billing.html": lambda s: "<html></html>\n",
               **{f"captures/billing-row1-{w}.png": (lambda s: b"") for w in WIDTHS}}
SCREEN_AC_WRAPPED = ("8. WHEN a member opens Billing THEN the system SHALL show the screen in\n"
                     f"    `{CAPTURE}`\n")


def with_prototype(s):
    s = s.replace("**Prototype:** none - the card form's text edited in place", "**Prototype:** prototype/billing.html")
    s = s.replace(LAST_AC, LAST_AC + PROTO_AC, 1)
    lines = "".join(f"- ![billing row 1, {w}](captures/billing-row1-{w}.png) - binding - prototype\n" for w in WIDTHS)
    return s.replace("## Sources\n\n", "## Differences from the source\n\nNone - the product matches the source\n\n"
                     "## Sources\n\n" + lines, 1)


PIECE_FILE = {"../../../app/components/card.rb": lambda s: "class Card; end\n"}


def screen_task(reuses, deps=None):
    """T1 builds the prototype's screen: its Done when cites the photo, its Reuses is given."""
    def edit(s):
        s = s.replace("- [ ] Migration runs and rolls back",
                      "- [ ] Migration runs and rolls back\n"
                      "- [ ] Billing matches `.specs/features/billing/captures/billing-row1-375.png` (Billing row 1)", 1)
        s = s.replace("**Reuses**: `db/migrate/20260301_add_trialing_status.rb` pattern", f"**Reuses**: {reuses}", 1)
        return s
    return edit


def with_screen_check(s):
    return s.replace("\n## Coverage", SCREEN_CHECK + "\n## Coverage", 1)


def with_binding(s):
    return (with_binding_bare(s).replace("## Sources", DIFFERENCES + "## Sources", 1)
            .replace(LAST_AC, LAST_AC + SCREEN_AC, 1))


def with_diff(old, new):
    return lambda s: with_binding(s).replace(old, new)


def png(width, height):
    """The header of a PNG of that size - all the size gate reads."""
    return (b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR"
            + width.to_bytes(4, "big") + height.to_bytes(4, "big") + b"\x08\x02\x00\x00\x00")


RUNNING = "screens/billing.running.png"


def screens_md(verdict, capture=False):
    row = (f"| `captures/billing--card-form.running.png` | `captures/billing--card-form.png` | {verdict} | - |\n"
           if capture else "")
    return lambda s: (
        "# Billing screens\n\n**Verifier**: independent sub-agent (author != verifier)\n\n"
        "| Screen | Compared with | Verdict | Finding |\n| --- | --- | --- | --- |\n"
        f"| `{RUNNING}` | AC 9 | {verdict} | - |\n" + row)


def with_browser_shot(rel):
    return lambda s: s.replace("\n## Coverage", f"\nProof: browser {rel}\n\n## Coverage", 1)


with_browser_proof = with_browser_shot("captures/billing--card-form.running.png")


def with_photo_finding(closed):
    """A photo defect the Verifier found, as a row in verification.md's `## Findings`."""
    return lambda s: s.rstrip("\n") + (
        "\n| the card form sits below the plan list, the capture draws it above | the Verifier's photo of "
        f"Billing next to `{CAPTURE}` | move the card form above the plans | {closed} |\n")


# A binding capture a criterion cites, a browser proof naming its picture, the picture the
# Verifier saved over the builder's, and screens.md judging it.
CAPTURE_BROWSER = {"plan.md": lambda s: with_screen(with_binding(s)), "checks.md": with_browser_proof,
                   "screens.md": screens_md("matches", capture=True),
                   "captures/billing--card-form.running.png": lambda s: "png"}


def with_walk_proof(s):
    return s.replace("\n## Coverage", "\nProof: walk - open Items from the nav\n\n## Coverage", 1)


def with_walked(s):
    return s.replace("## Handoff\n", "## Handoff\n\n- **Walked:** opened Items from the nav, the list showed\n", 1)


def with_refused_sensor(s, label="wrong value", closed='Refused - user: "do not change this"',
                        extra_finding="", faults=None):
    finding = f"| {label} | sensor output | assert value | {closed} |"
    s = re.sub(r"^\| C4 asserts the status changed[^\n]*", finding + extra_finding, s, flags=re.M)
    rows = faults if faults is not None else "| wrong value | approved proof | no |"
    return s + ("\n## Discrimination sensor\n\n| Fault | Verification | Killed? |\n"
                "| --- | --- | --- |\n" + rows + "\n")


def with_second_screen(s):
    return s.replace("## Investigation" + chr(10), "### Profile" + chr(10) + chr(10)
                     + "| State | Account, data and width | Criterion |" + chr(10) + "| --- | --- | --- |" + chr(10)
                     + "| profile empty | member with no profile yet, 375 | 1 |" + chr(10) + chr(10)
                     + "## Investigation" + chr(10), 1)


# The three screen headings of the E1 run (25/11/2026, diet-sharing-dialog): every word of the last
# one sits in another heading, and two carry accents.
E1_SCREENS = ["Compartilhar dieta na ficha", "Padrão e exceção da Área do paciente", "Dieta na Área do paciente"]


def with_e1_screens(s):
    tables = "".join("### " + screen + chr(10) + chr(10) + "| State | Account, data and width | Criterion |" + chr(10)
                     + "| --- | --- | --- |" + chr(10) + "| opened | owner, 375 | 1 |" + chr(10) + chr(10)
                     for screen in E1_SCREENS)
    return s.replace("## Investigation" + chr(10), tables + "## Investigation" + chr(10), 1)


def with_e1_rows(*screens):
    lines = "".join(chr(10) + "| `captures/review-e1-" + str(i) + ".png` | " + screen + " row 1, 375 | none |"
                    for i, screen in enumerate(screens))
    return lambda s: s.replace("| `captures/review-billing-row2.png` | row 2, 375 | none |",
                               "| `captures/review-billing-row2.png` | row 2, 375 | none |" + lines, 1)


# Mutants that need more than one artifact edited: the screen rules read plan.md and judge
# another file. (validator, description, {artifact: edit}, expected exit, expected fragment)
MULTI_CASES = [
    *[("validate_verification", description,
       {"verification.md": lambda s, options=options: with_refused_sensor(s, **options)},
       1, "PASS but a mutant survived") for description, options in [
        ("another finding's refusal cannot settle a survivor", {"label": "another fault"}),
        ("a substring finding cannot settle a survivor", {"label": "wrong value extra"}),
        ("case is part of the fault identity", {"label": "Wrong value"}),
        ("Markdown is part of the fault identity", {"label": "`wrong value`"}),
        ("a survivor with a blank quoted refusal stays open", {"closed": 'Refused - user: "   "'}),
        ("a survivor with a bare refusal stays open", {"closed": "Refused"}),
        ("a survivor with an unquoted refusal stays open", {"closed": "Refused - user: do not fix"}),
        ("a survivor with mismatched quotation stays open", {"closed": 'Refused - user: "do not fix”'}),
        ("duplicate Findings cannot settle a survivor",
         {"extra_finding": '\n| wrong value | output | fix | Refused - user: "no" |'}),
        ("a duplicate fixed Finding is still ambiguous",
         {"extra_finding": "\n| wrong value | output | fix | e4f5a6b C1 |"}),
        ("duplicate Faults cannot share a refusal",
         {"faults": "| wrong value | proof1 | no |\n| wrong value | proof2 | no |"}),
        ("a killed duplicate Fault is still ambiguous",
         {"faults": "| wrong value | proof1 | no |\n| wrong value | proof2 | yes |"}),
        ("one refusal cannot settle two different survivors",
         {"faults": "| wrong value | proof1 | no |\n| wrong bound | proof2 | no |"}),
        ("a fix commit does not negate an actual survivor", {"closed": "e4f5a6b C1"}),
    ]],
    ("validate_verification", "two screens numbered from 1, evidence for one only",
     {"plan.md": with_second_screen},
     1, "'Profile' row 1 has no photo or test"),
    ("validate_verification", "two screens numbered from 1, evidence for both (control)",
     {"plan.md": with_second_screen,
      "verification.md": lambda s: s.replace("| `captures/review-billing-row2.png` | row 2, 375 | none |",
          "| `captures/review-billing-row2.png` | row 2, 375 | none |" + chr(10)
          + "| `captures/review-profile-row1.png` | row 1, 375 | none |", 1)},
     0, ""),
    ("validate_verification", "E1 screens: a heading whose words all sit in other headings, evidence for all (control)",
     {"plan.md": with_e1_screens, "verification.md": with_e1_rows(*E1_SCREENS)},
     0, ""),
    ("validate_verification", "E1 screens: no evidence for the heading whose words sit in other headings",
     {"plan.md": with_e1_screens, "verification.md": with_e1_rows(*E1_SCREENS[:2])},
     1, "'Dieta na Área do paciente' row 1 has no photo or test"),
    ("validate_verification", "E1 screens: a row line that also names a longer heading after the row number (control)",
     {"plan.md": with_e1_screens, "verification.md": lambda s: with_e1_rows(*E1_SCREENS)(s).replace(
         "Dieta na Área do paciente row 1, 375 | none |",
         "Dieta na Área do paciente row 1, 375; padrão, exceção e conta da Área do paciente | none |", 1)},
     0, ""),
    ("validate_verification", "a browser proof and no screens.md",
     {"plan.md": with_screen, "checks.md": with_browser_shot(RUNNING), RUNNING: lambda s: "png"},
     1, "no `screens.md`"),
    ("validate_verification", "a screen that diverges in screens.md next to PASS",
     {"plan.md": with_screen, "screens.md": screens_md("diverges - the card form sits below the plan list"),
      "checks.md": with_browser_shot(RUNNING), RUNNING: lambda s: "png"},
     1, "reads 'diverges"),
    ("validate_verification", "a plan citing a capture and no running screenshot",
     {"plan.md": lambda s: with_screen(with_binding(s)), "screens.md": screens_md("matches")},
     1, "no `*.running.png`"),
    ("validate_verification", "a cited capture with no running screenshot beside it",
     {"plan.md": lambda s: with_screen(with_binding(s)), "screens.md": screens_md("matches"),
      "screens/other.running.png": lambda s: "png"},
     1, "has no `billing--card-form.running.png`"),
    ("validate_verification", "a browser proof names a screenshot that is not on disk",
     {"plan.md": with_screen, "screens.md": screens_md("matches"),
      "checks.md": with_browser_shot("screens/missing.running.png"), RUNNING: lambda s: "png"},
     1, "which is not under the feature folder"),
    ("validate_verification", "a browser proof names no screenshot",
     {"plan.md": with_screen, "screens.md": screens_md("matches"),
      "checks.md": lambda s: s.replace("\n## Coverage", "\nProof: browser - click the button\n\n## Coverage", 1),
      RUNNING: lambda s: "png"},
     1, "names no `.running.png`"),
    ("validate_verification", "a browser proof alone makes a screen, and there is no screens.md",
     {"checks.md": with_browser_shot(RUNNING), RUNNING: lambda s: "png"},
     1, "no `screens.md`"),
    ("validate_verification", "a picture taken at another size than its capture",
     {"plan.md": lambda s: with_screen(with_binding(s)), "screens.md": screens_md("matches"),
      "captures/billing--card-form.png": lambda s: png(1024, 839),
      "captures/billing--card-form.running.png": lambda s: png(1440, 1200)},
     1, "take the picture at the capture's size"),
    ("validate_verification", "a .jpg capture with no running picture beside it",
     {"plan.md": lambda s: with_screen(with_binding(s)).replace("billing--card-form.png", "billing--card-form.jpg"),
      "captures/billing--card-form.jpg": lambda s: "jpg", "screens.md": screens_md("matches")},
     1, "has no `billing--card-form.running.png`"),
    ("validate_verification", "a photo defect the Verifier found left open in Findings",
     {**CAPTURE_BROWSER, "verification.md": with_photo_finding("")},
     1, "is not closed"),
    ("validate_verification", "proofs.md with a failing proof",
     {"proofs.md": lambda s: re.sub(r"^(\| C5 \|.*\| )pass \|$", r"\1**no test ran** |", s, flags=re.M)},
     1, "C5 reads"),
    ("validate_verification", "proofs.md with no row for a check",
     {"proofs.md": lambda s: re.sub(r"^\| C12 \|[^\n]*\n", "", s, flags=re.M)},
     1, "has no row for C12"),
    ("validate_verification", "proofs.md where a run group failed",
     {"proofs.md": lambda s: s.replace("| Build |", "| Run billing | `bin/rails test test/billing -v` | **fail** - exit 1 |\n| Build |")},
     1, "Run billing reads"),
    ("validate_verification", "PASS contradicted by a declared surviving mutant",
     {"verification.md": lambda s: s.replace("**Verdict**: FAIL", "**Verdict**: PASS") +
      "\n## Sensor\n\n| Mutation | Killed? |\n| --- | --- |\n| wrong value | no |\n"},
     1, "PASS but a mutant survived"),
    ("validate_verification", "lowercase pass cannot hide a declared survivor",
     {"verification.md": lambda s: s.replace("**Verdict**: PASS", "**Verdict**: pass") +
      "\n## Sensor\n\n| Mutation | Killed? |\n| --- | --- |\n| wrong value | no |\n"},
     1, "PASS but a mutant survived"),
    ("validate_verification", "mixed-case Pass cannot hide a declared survivor",
     {"verification.md": lambda s: s.replace("**Verdict**: PASS", "**Verdict**: Pass") +
      "\n## Sensor\n\n| Mutation | Killed? |\n| --- | --- |\n| wrong value | no |\n"},
     1, "PASS but a mutant survived"),
    ("validate_verification", "an explicit FAIL is not completion",
     {"verification.md": lambda s: s.replace("**Verdict**: PASS", "**Verdict**: FAIL")},
     1, "needs an explicit `**Verdict**: PASS`"),
    ("validate_verification", "a report with no explicit verdict",
     {"verification.md": lambda s: s.replace("**Verdict**: PASS\n", "")},
     1, "needs an explicit `**Verdict**: PASS`"),
    ("validate_verification", "an unfilled verdict template is not completion",
     {"verification.md": lambda s: s.replace("**Verdict**: PASS", "**Verdict**: [PASS | FAIL]")},
     1, "needs an explicit `**Verdict**: PASS`"),
    ("validate_verification", "PASS in the body cannot replace the verdict",
     {"verification.md": lambda s: s.replace("**Verdict**: PASS\n", "") + "\n## Notes\nPrior tests reported PASS.\n"},
     1, "needs an explicit `**Verdict**: PASS`"),
    ("validate_verification", "a report with no reviewed HEAD",
     {"verification.md": lambda s: re.sub(r"^\*\*HEAD\*\*:.*\n", "", s, flags=re.M)},
     1, "names no reviewed `**HEAD**`"),
    ("validate_verification", "a report with no code fix count",
     {"verification.md": lambda s: s.replace("**Fixes**: 0\n", "")},
     1, "needs `**Fixes**: 0..3`"),
    ("validate_verification", "a fourth code fix-to-review is not allowed",
     {"verification.md": lambda s: s.replace("**Fixes**: 0", "**Fixes**: 4")},
     1, "needs `**Fixes**: 0..3`"),
    ("validate_verification", "a report with no Checks table",
     {"verification.md": lambda s: re.sub(r"## Checks\n.*?\n## Findings", "## Findings", s, flags=re.S)},
     1, "no `## Checks` table"),
    ("validate_verification", "a Checks table with no row for a check",
     {"verification.md": lambda s: re.sub(r"^\| C7 \|[^\n]*\n", "", s, flags=re.M)},
     1, "`## Checks` has no row for C7"),
    ("validate_verification", "a Checks row that names no test",
     {"verification.md": lambda s: s.replace("| C9 | `test/webhooks/ingest_test.rb` `test_missing_subscription_id_is_422` |", "| C9 | - |")},
     1, "row C9 names no test"),
    ("validate_verification", "a refusal without the user's words is not closure",
     {"verification.md": lambda s: s.replace("| e4f5a6b C4 |", "| Refused |")},
     1, "is not closed"),
    ("validate_verification", "an empty quoted refusal is not closure",
     {"verification.md": lambda s: s.replace("| e4f5a6b C4 |", '| Refused - user: "   " |')},
     1, "is not closed"),
    ("validate_verification", "a finding with no commit in Closed",
     {"verification.md": lambda s: s.replace("| e4f5a6b C4 |", "|  |")},
     1, "is not closed"),
    ("validate_verification", "a report with no Findings section",
     {"verification.md": lambda s: s.split("## Findings")[0]},
     1, "no `## Findings` section"),
    ("validate_verification", "proofs.md where the build failed",
     {"proofs.md": lambda s: s.replace("| Build | `bin/rubocop app/billing` | pass |", "| Build | `bin/rubocop app/billing` | **fail** - 2 offenses |")},
     1, "Build reads"),
    ("validate_verification", "proofs.md with no Build row while checks.md names a build",
     {"proofs.md": lambda s: s.replace("| Build | `bin/rubocop app/billing` | pass |\n", "")},
     1, "has no Build row"),
    ("validate_verification", "proofs.md written over uncommitted changes",
     {"proofs.md": lambda s: s.replace("**Tree**: clean", "**Tree**: dirty - apps/x.ts")},
     1, "ran on uncommitted changes"),
    ("validate_verification", "a walk proof with no Walked line in the Handoff",
     {"checks.md": with_walk_proof},
     1, "no `**Walked:**` line"),
    ("validate_verification", "a plan with no approval line",
     {"plan.md": lambda s: s.replace('**Approved**: 2026-10-23 - user: "approved, go ahead"\n', "")},
     1, "plan.md has no `**Approved**"),
    ("validate_checks", "checks written from a plan nobody approved",
     {"plan.md": lambda s: s.replace('**Approved**: 2026-10-23 - user: "approved, go ahead"\n', "")},
     1, "plan.md has no `**Approved**"),
    ("validate_checks", "an approval without the user's words",
     {"plan.md": lambda s: s.replace('user: "approved, go ahead"', "the plan is complete")},
     1, "plan.md has no `**Approved**"),
    ("validate_checks", "an approval with no date",
     {"plan.md": lambda s: s.replace("**Approved**: 2026-10-23 -", "**Approved**: yes -")},
     1, "plan.md has no `**Approved**"),
    ("validate_plan", "a binding source with no Differences section",
     {"plan.md": lambda s: with_binding(s).replace(DIFFERENCES, "")},
     1, "no `## Differences from the source` section"),
    ("validate_plan", "a difference the user never confirmed",
     {"plan.md": with_diff("| y - AD-003 |", "| n - the agent decided |")},
     1, "is the user's call"),
    ("validate_plan", "a difference with a blank Confirmed cell",
     {"plan.md": with_diff("| y - AD-002 |", "|  |")},
     1, "is the user's call"),
    ("validate_plan", "a confirmed difference that cites no decision",
     {"plan.md": with_diff("| y - AD-002 |", "| y - existing fields, 2026-10-23 |")},
     1, "cites no decision"),
    ("validate_plan", "a difference citing a decision STATE.md does not hold",
     {"plan.md": with_diff("| y - AD-002 |", "| y - AD-009 |")},
     1, "does not hold as active"),
    ("validate_plan", "a difference citing a superseded decision",
     {"plan.md": with_diff("| y - AD-003 |", "| y - AD-004 |")},
     1, "does not hold as active"),
    ("validate_plan", "a Differences section with no rows and no None",
     {"plan.md": lambda s: re.sub(r"## Differences from the source\n.*?\n## Sources",
                                  "## Differences from the source\n\nsee chat\n\n## Sources",
                                  with_binding(s), flags=re.S)},
     1, "has no rows"),
    ("validate_plan", "a capture a criterion cites that does not exist",
     {"plan.md": with_diff(f"`{CAPTURE}`", "`.specs/features/billing/captures/nope.png`")},
     1, "does not exist"),
    ("validate_plan", "a design-file link where an exported capture belongs",
     {"plan.md": with_diff(f"`{CAPTURE}`", "`https://design.example.com/file/abc?node-id=12-34`")},
     1, "is a link, not a capture"),
    ("validate_plan", "a capture under captures/ that no criterion cites",
     {"plan.md": lambda s: with_binding(s).replace(SCREEN_AC, "")},
     1, "no criterion cites the capture"),
    ("validate_plan", "a print the user sent, left in captures/ as non-binding with their words",
     {"plan.md": lambda s: with_binding(s).replace(
         "- binding - the card form", '- non-binding - user: "only the tone, the layout is ours" - the card form')},
     1, "is not marked binding"),
    ("validate_plan", "a capture in captures/ that Sources never mentions and nothing binds",
     {"captures/billing--card-form.png": lambda s: b""},
     1, "is not marked binding"),
    ("validate_plan", "a prototype with only the 375 photo",
     {"plan.md": with_prototype, "prototype/billing.html": lambda s: "<html></html>\n",
      "captures/billing-row1-375.png": lambda s: b""},
     1, "no `captures/billing-row1-768.png`"),
    ("validate_checks", "a screen criterion whose capture sits on its second line and no check cites it",
     {"plan.md": lambda s: with_binding(s).replace(SCREEN_AC, SCREEN_AC_WRAPPED)},
     1, "no check proving AC 8 does"),
    ("validate_tasks", "a piece of the prototype's screen in no Reuses of the tasks that build it",
     {"plan.md": with_prototype, **PROTO_FILES, **PIECE_FILE,
      "tasks.md": screen_task("`db/migrate/20260301_add_trialing_status.rb` pattern")},
     1, "is in no `Reuses` of the tasks that build that screen"),
    ("validate_tasks", "the right piece file with the wrong variant",
     {"plan.md": with_prototype, **PROTO_FILES, **PIECE_FILE,
      "tasks.md": screen_task("`Card compact` (`app/components/card.rb`)")},
     1, "is in no `Reuses` of the tasks that build that screen"),
    ("validate_tasks", "a prototype no task builds",
     {"plan.md": with_prototype, **PROTO_FILES, **PIECE_FILE,
      "tasks.md": lambda s: s.replace("**Reuses**: `db/migrate/20260301_add_trialing_status.rb` pattern",
                                      "**Reuses**: `Card default` (`app/components/card.rb`)", 1)},
     1, "no task's `Done when` cites `captures/billing-row"),
    ("validate_tasks", "a screen with a new piece whose tasks depend on nothing",
     {"plan.md": lambda s: with_prototype(s).replace(
         "(`app/components/card.rb`)\n", "(`app/components/card.rb`); banner - new piece - billing row 1\n", 1),
      **PROTO_FILES, **PIECE_FILE,
      "tasks.md": screen_task("`Card default` (`app/components/card.rb`)")},
     1, "has a new or changed piece"),
    ("validate_verification", "a cited capture screens.md never judges",
     {"plan.md": lambda s: with_screen(with_binding(s)), "screens.md": screens_md("matches"),
      "captures/billing--card-form.png": lambda s: png(1024, 839),
      "captures/billing--card-form.running.png": lambda s: png(1024, 839),
      RUNNING: lambda s: png(1024, 839)},
     1, "has no row in screens.md"),
    ("validate_checks", "a screen criterion cites a capture and no check cites it",
     {"plan.md": with_binding},
     1, "no check proving AC 8 does"),
]

# Negative controls: a gate that fires where it should not is the same bug as one that never
# fires - it just fails loudly instead of silently.
NEGATIVE_CONTROLS = [
    ("validate_tasks", "a dependency on an earlier phase needs no arrow",
     {"tasks.md": two_phases},
     "Depends on"),
    ("validate_tasks", "a Reuses of `none - <why>` is an answer",
     {"tasks.md": lambda s: s.replace("**Reuses**: `app/billing/subscription.rb` status constants",
                                      "**Reuses**: none - first status map in the repo", 1)},
     "Reuses"),
    ("validate_verification", "one exact individually refused survivor is accepted",
     {"verification.md": with_refused_sensor}),
    ("validate_verification", "paired curly quotation is a valid refusal",
     {"verification.md": lambda s: with_refused_sensor(s, closed='Refused - user: “do not change this”')}),
    ("validate_verification", "two separately refused survivors are accepted",
     {"verification.md": lambda s: with_refused_sensor(s,
      extra_finding='\n| wrong bound | output | fix | Refused - user: "leave this bound" |',
      faults="| wrong value | proof1 | no |\n| wrong bound | proof2 | no |")}),
    ("validate_checks", "a run proof needs no test selector - its expected line is one",
     {"checks.md": lambda s: s.replace("test_failed_charge_suspends = .", "test_failed_charge_suspends PASS")},
     "names no test selector"),
    ("validate_checks", "an old checks.md with a Mutations line is still read",
     {"checks.md": lambda s: s.replace("Build: `bin/rubocop", "Mutations: 3\nBuild: `bin/rubocop")}),
    ("validate_verification", "an old checks.md with a Mutations line owes nothing",
     {"checks.md": lambda s: s.replace("Build: `bin/rubocop", "Mutations: 3\nBuild: `bin/rubocop")}),
    ("validate_plan", "a binding source with confirmed differences is accepted",
     {"plan.md": with_binding}),
    ("validate_plan", "a fixed visual defect needs no prototype",
     {"plan.md": lambda s: s.replace("**Prototype:** none - the card form's text edited in place",
                                     "**Prototype:** none - the card form's spacing defect fixed")}),
    ("validate_plan", "the Verifier's review photos in captures/ are not plan captures",
     {"plan.md": with_binding, "captures/review-billing-375.png": lambda s: b"",
      "captures/review-billing-row1.png": lambda s: b""}),
    ("validate_plan", "a binding source that matches with no differences is accepted",
     {"plan.md": lambda s: with_binding(s).replace(
         DIFFERENCES, "## Differences from the source\n\nNone - the product matches the source\n\n")}),
    ("validate_tasks", "the screen's piece, variant and file in the Reuses of the task that builds it",
     {"plan.md": with_prototype, **PROTO_FILES, **PIECE_FILE,
      "tasks.md": screen_task("`Card default` (`app/components/card.rb`)")}),
    ("validate_tasks", "a piece path with parentheses is read",
     {"plan.md": lambda s: with_prototype(s).replace("app/components/card.rb", "app/(staff)/card.rb"),
      **PROTO_FILES, "../../../app/(staff)/card.rb": lambda s: "class Card; end\n",
      "tasks.md": screen_task("`Card default` (`app/(staff)/card.rb`)")}),
    ("validate_plan", "a prototype with its photos at 375, 768 and 1280 is accepted",
     {"plan.md": with_prototype, **PROTO_FILES}),
    ("validate_plan", "a Surface route anyone may call owes no refusal status",
     {"plan.md": lambda s: s.replace(
         "| `200`, `401`, `409`, `422` | the provider, with a valid signature; anything else gets `401` |",
         "| `200`, `409`, `422` | anyone |")}),
    ("validate_checks", "a screen check citing the criterion's capture is accepted",
     {"plan.md": with_binding, "checks.md": with_screen_check}),
    ("validate_verification", "a cited capture, its picture and screens.md that matches are accepted",
     CAPTURE_BROWSER, "screens.md", ".running.png"),
    ("validate_verification", "a plan with a binding source and matching pictures is accepted",
     {"plan.md": with_binding,
      "screens.md": screens_md("matches", capture=True),
      "captures/billing--card-form.running.png": lambda s: "png"}),
    ("validate_verification", "a picture at twice its capture's size is the same layout",
     {"plan.md": lambda s: with_screen(with_binding(s)), "screens.md": screens_md("matches", capture=True),
      "captures/billing--card-form.png": lambda s: png(1024, 839),
      "captures/billing--card-form.running.png": lambda s: png(2048, 1678),
      RUNNING: lambda s: png(1024, 839)}),
    ("validate_verification", "a browser proof whose screenshot exists is accepted",
     {"plan.md": with_screen, "screens.md": screens_md("matches"),
      "checks.md": with_browser_shot(RUNNING), RUNNING: lambda s: "png"}),
    ("validate_verification", "a screen judged in screens.md is accepted",
     {"plan.md": with_screen, "screens.md": screens_md("matches"), RUNNING: lambda s: "png"}),
    ("validate_verification", "a photo defect the Verifier found and closed by a commit is accepted",
     {**CAPTURE_BROWSER, "verification.md": with_photo_finding("e4f5a6b C99")}),
    ("validate_verification", "a screen no capture draws owes no picture and no screens.md",
     {"plan.md": with_screen}),
    ("validate_verification", "the user's explicit quoted refusal closes that finding",
     {"verification.md": lambda s: s.replace("| e4f5a6b C4 |", '| Refused - user: "do not make this change" |')}),
    ("validate_verification", "PASS does not mechanically require a sensor table",
     {"verification.md": lambda s: s.replace("**Verdict**: PASS", "**Verdict**: pass")}),
    ("validate_verification", "PASS with a declared killed mutant is accepted",
     {"verification.md": lambda s: s.replace("**Verdict**: FAIL", "**Verdict**: PASS") +
      "\n## Sensor\n\n| Mutation | Killed? |\n| --- | --- |\n| wrong value | yes |\n"}),
    ("validate_verification", "the third code fix review is accepted",
     {"verification.md": lambda s: s.replace("**Fixes**: 0", "**Fixes**: 3")}),
    ("validate_verification", "proofs.md green and no finding is accepted",
     {"verification.md": lambda s: s.split("## Findings")[0] + "## Findings\n\nNone - every rule probed held\n"}),
    ("validate_checks", "a walk proof needs no test selector and no picture",
     {"checks.md": with_walk_proof}, "names no test selector"),
    ("validate_verification", "a walk proof with its visit in the Walked line is accepted",
     {"checks.md": lambda s: with_walked(with_walk_proof(s))}),
]


def scaffold():
    root = tempfile.mkdtemp(prefix="tlc-selftest-")
    fdir = os.path.join(root, ".specs", "features", FEATURE)
    os.makedirs(fdir)
    for name in ("plan.md", "checks.md", "verification.md", "proofs.md", "tasks.md"):
        if os.path.isfile(os.path.join(FIXTURES, name)):
            shutil.copyfile(os.path.join(FIXTURES, name), os.path.join(fdir, name))
    # The print the user sent is a reference; it binds nothing.
    os.makedirs(os.path.join(fdir, "references"))
    open(os.path.join(fdir, "references", "billing--card-form.png"), "wb").close()
    with open(os.path.join(root, ".specs", "STATE.md"), "w", encoding="utf-8") as f:
        f.write(STATE)
    return root


def run(validator, root):
    # A capture the binding cases cite; the gates check that it exists, never its format.
    fdir = os.path.join(root, ".specs", "features", FEATURE)
    cap = os.path.join(fdir, "captures", "billing--card-form.png")
    if "captures/billing--card-form.png" in read_artifact(os.path.join(fdir, "plan.md")) and not os.path.exists(cap):
        os.makedirs(os.path.dirname(cap), exist_ok=True)
        open(cap, "wb").close()
    p = subprocess.run(
        [sys.executable, script(validator), FEATURE, "--root", root],
        capture_output=True, encoding="utf-8", errors="replace",
    )
    return p.returncode, p.stdout + p.stderr


def run_script(name, *args, cwd=None, env=None, here=HERE):
    """Run a shipped script directly and return (exit code, combined output)."""
    proc = subprocess.run(
        [sys.executable, script(name) if here == HERE else os.path.join(here, name), *args],
        capture_output=True, encoding="utf-8", errors="replace", cwd=cwd,
        env=None if env is None else {**os.environ, **env},
    )
    return proc.returncode, proc.stdout + proc.stderr


# (script, description, argv, expected exit, expected output fragment)
TOOLING = [
    ("check_commit.py", "a conventional message passes",
     ["feat: suspend the subscription on a failed charge"], 0, "OK"),
    ("check_commit.py", "a non-conventional message fails",
     ["Updated stuff."], 1, "does not match"),
    ("check_commit.py", "a capitalized description fails",
     ["feat: Suspend the subscription"], 1, "start lowercase"),
    ("check_commit.py", "an unknown type fails",
     ["wip: suspend the subscription"], 1, "is not one of"),
    ("lessons.py", "normalization regressions pass", ["selftest"], 0, "ok"),
    ("lessons.py", "--root before the subcommand is the documented form",
     ["--root", tempfile.gettempdir(), "list", "--status", "confirmed"], 0, ""),
]


def run_tooling():
    """Exercise the scripts the skill ships beyond the validators.

    A shipped script nothing ever calls is where a crash hides: check_commit.py once raised a
    traceback on the message form of its own argument, and no gate noticed because no gate ran it.
    """
    print("\ntooling - every shipped script must run, not just parse")
    ok = True
    for script, desc, argv, want_code, want_frag in TOOLING:
        if not shipped(script):
            continue
        code, out = run_script(script, *argv)
        if code == want_code and want_frag.lower() in out.lower():
            print(f"  ok      {script}: {desc}")
            continue
        ok = False
        print(f"  BROKEN  {script}: {desc} - expected exit={want_code} and {want_frag!r}, "
              f"got exit={code}")
        print("          " + out.strip().replace("\n", "\n          "))

    # A passing commit names what follows the build of a feature whose verification is still owed.
    root = tempfile.mkdtemp(prefix="commit-")
    try:
        fdir = os.path.join(root, ".specs", "features", FEATURE)
        os.makedirs(fdir)
        write_artifact(os.path.join(fdir, "checks.md"), "# Billing checks\n\n## Checks\n")
        for desc, verified, want in [] if not shipped("check_commit") else [
            ("an unverified feature is told what follows its last commit", False, True),
            ("a verified feature is not", True, False),
        ]:
            if verified:
                write_artifact(os.path.join(fdir, "verification.md"), "# Billing verification\n")
            code, out = run_script("check_commit.py", "feat: suspend the subscription", "--root", root)
            if code == 0 and ("check_proofs.py billing" in out) == want:
                print(f"  ok      check_commit.py: {desc}")
            else:
                ok = False
                print(f"  BROKEN  check_commit.py: {desc} - exit {code}: {out.strip()[:300]}")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # Before building, the Build line runs once: a command red before any change is not the gate.
    # The Build waits for both yeses: a draft or missing tasks.md stops it before any command runs.
    for desc, build, argv, tasks, want_code, want_frag in [] if not shipped("validate_checks") else [
        ("--execute passes a green Build line", "exit 0", ["--execute"], "approved", 0, "0 error"),
        ("--execute fails a Build line red before building", "exit 3", ["--execute"], "approved", 1,
         "Build is red before building: `exit 3` exit 3"),
        ("without --execute the Build line is not run", "exit 3", [], "approved", 0, "0 error"),
        ("--execute does not build tasks the user has not approved", "exit 3", ["--execute"], "draft", 1,
         "tasks.md has no `**Approved**:` line"),
        ("--execute does not build with no tasks.md", "exit 3", ["--execute"], "missing", 1,
         "tasks.md is missing"),
    ]:
        root = scaffold()
        fdir = os.path.join(root, ".specs", "features", FEATURE)
        path = os.path.join(fdir, "checks.md")
        write_artifact(path, read_artifact(path).replace("Build: `bin/rubocop app/billing`", f"Build: `{build}`", 1))
        tasks_path = os.path.join(fdir, "tasks.md")
        if tasks == "approved":
            write_artifact(tasks_path, read_artifact(tasks_path) + '\n**Approved**: 2026-11-24 - user: "sim"\n')
        elif tasks == "missing":
            os.remove(tasks_path)
        code, out = run_script("validate_checks.py", FEATURE, "--root", root, *argv)
        shutil.rmtree(root, ignore_errors=True)
        built = "Build is red" in out
        if code == want_code and want_frag in out and (tasks == "approved" or not built):
            print(f"  ok      validate_checks.py: {desc}")
        else:
            ok = False
            print(f"  BROKEN  validate_checks.py: {desc} - expected exit={want_code} and {want_frag!r}, "
                  f"got exit={code}: {out.strip()[:300]}")

    # The completion gate must not go green on an empty run. This is a control, not a mutant:
    # "no report found" once exited 0, which reads as a pass to anything checking exit codes.
    empty = tempfile.mkdtemp(prefix="empty-root-")
    try:
        for argv, want, desc in [] if not shipped("validate_verification") else [
            (["--root", empty], 2, "gating nothing exits 2, not 0"),
            (["--root", empty, "--allow-empty"], 0, "an explicit empty sweep is allowed"),
            (["missing-feature", "--root", empty], 2, "an unresolvable feature exits 2"),
        ]:
            code, out = run_script("validate_verification.py", *argv)
            if code == want:
                print(f"  ok      validate_verification.py: {desc}")
            else:
                ok = False
                print(f"  BROKEN  validate_verification.py: {desc} - expected exit={want}, "
                      f"got {code}: {out.strip()}")
    finally:
        shutil.rmtree(empty, ignore_errors=True)

    # the lessons store has to survive a real round-trip on disk, not only its unit checks
    if not shipped("lessons"):
        return ok
    root = tempfile.mkdtemp(prefix="lessons-")
    try:
        steps = [
            (["--root", root, "init"], "Initialized"),
            (["--root", root, "add", "--feature", FEATURE, "--signal", "weak_test",
              "--source", "app/billing/x.rb:31", "--text", "assert the dedup path returns the row"],
             "ADDED"),
            (["--root", root, "status"], "1 total"),
            (["status", "--root", root], "1 total"),
        ]
        for argv, frag in steps:
            code, out = run_script("lessons.py", *argv)
            if code != 0 or frag.lower() not in out.lower():
                ok = False
                print(f"  BROKEN  lessons.py: round-trip step {' '.join(argv)!r} - expected {frag!r}, "
                      f"got exit={code}: {out.strip()}")
                break
        else:
            for artifact in ("lessons.json", "LESSONS.md"):
                if not os.path.isfile(os.path.join(root, ".specs", artifact)):
                    ok = False
                    print(f"  BROKEN  lessons.py: round-trip wrote no .specs/{artifact}")
                    break
            else:
                print("  ok      lessons.py: init - add - status round-trip writes both artifacts")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # a store written before the signal was renamed reads as the new signal, and its lesson recurs
    root = tempfile.mkdtemp(prefix="lessons-")
    try:
        text = "assert the dedup path returns the row"
        old = {"schema": 1, "next_id": 2, "lessons": [{
            "id": "L-001", "key": "surviving_mutant::" + text, "text": text, "signal": "surviving_mutant",
            "scope": "", "status": "candidate", "features": ["older"], "recurrence": 1, "harmful": 0,
            "evidence": ["app/billing/x.rb:31"], "created": "2026-10-01", "last_seen": "2099-01-01"}]}
        os.makedirs(os.path.join(root, ".specs"))
        write_artifact(os.path.join(root, ".specs", "lessons.json"), json.dumps(old))
        code, out = run_script("lessons.py", "--root", root, "add", "--feature", FEATURE, "--signal", "weak_test",
                               "--source", "app/billing/x.rb:31", "--text", text)
        stored = read_artifact(os.path.join(root, ".specs", "lessons.json"))
        if code == 0 and "UPDATED L-001" in out and "surviving_mutant" not in stored:
            print("  ok      lessons.py: a surviving_mutant lesson loads as weak_test and recurs")
        else:
            ok = False
            print(f"  BROKEN  lessons.py: surviving_mutant migration - exit={code}: {out.strip()}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return ok


# A test runner nothing has to install: prints each argument after the exit code as a line,
# logs that it ran, and exits with that code. `{esc}` stands for the escape byte of a colour code.
RUNNER = ('import sys\n'
          'open("ran.log", "a").write(" ".join(sys.argv[1:]) + "\\n")\n'
          'for line in sys.argv[2:]:\n'
          '    print(line.replace("{esc}", "\\x1b"))\n'
          'sys.exit(int(sys.argv[1]))\n')


def proofs_md(runs, proofs, build="none - fixture", head=""):
    text = f"# Billing checks\n\n{head}Build: {build}\n"
    text += "".join(f"Run {name}: `{cmd}`\n" for name, cmd in runs.items())
    text += "\n## Checks\n\n"
    return text + "".join(f"**C{i}** - claim {i} (AC {i})\nProof: {p}\n\n" for i, p in enumerate(proofs, 1))


def result_rows(text):
    """{first cell: result cell} of proofs.md's table."""
    rows = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("| ") and len(cells) == 3 and cells[0] not in ("Check", "---"):
            rows[cells[0]] = cells[2]
    return rows


def run_proofs_tooling():
    """check_proofs.py runs the project's own commands, so it is checked with a fake runner: a
    group runs once, each check reads its line from the group's output, and a line that is not
    there is never a pass."""
    from check_proofs import sees
    parser_cases = [
        ("test_error_with_cache (test_example.QueryTests) ... ok", "test_error (test_example.QueryTests) ... ok", False),
        ("✓ src/a.test.ts > returns error with cache 33ms", "✓ src/a.test.ts > returns error", False),
        ("✓ src/a.test.ts > returns error 33ms", "✓ src/a.test.ts > returns error", True),
        ("✓ src/a.test.ts > returns error (33ms) [100%]", "✓ src/a.test.ts > returns error", True),
        ("BillingDunningTest#test_failed_charge_suspends = 0.02 s = .", "test_failed_charge_suspends = .", True),
        ("BillingDunningTest#test_failed_charge_suspends_later = 0.02 s = .", "test_failed_charge_suspends = .", False),
        ("✓ src/a.test.ts > latency is 20ms 8ms", "✓ src/a.test.ts > latency is 10ms 6ms", False),
        ("✓ src/a.test.ts > latency is 20ms 8ms", "✓ src/a.test.ts > latency is 20ms 6ms", True),
        ("✓ src/a.test.ts > latency is 20ms 8ms", "✓ src/a.test.ts > latency is 20ms", True),
        ("✓ src/a.test.ts > latency is 20ms 8ms", "✓ src/a.test.ts > latency is 10ms", False),
        ("✓ src/a.test.ts > latency is 20ms (8ms) [100%]", "✓ src/a.test.ts > latency is 10ms (6ms) [50%]", False),
        ('classifies only the named input errors as safe refusals ... ok (812µs)', 'classifies only the named input errors as safe refusals ... ok', True),
        ('classifies only the named input errors as safe refusals ... ok (4ms)', 'classifies only the named input errors as safe refusals ... ok', True),
        ('classifies only the named input errors as safe refusals ... ok (1s)', 'classifies only the named input errors as safe refusals ... ok', True),
        ('regression: classifies only the named input errors as safe refusals ... ok (4ms)', 'classifies only the named input errors as safe refusals ... ok', False),
        ('regression: classifies only the named input errors as safe refusals ... ok (812µs)', 'classifies only the named input errors as safe refusals ... ok', False),
        ('regression: classifies only the named input errors as safe refusals ... ok (812µs)', 'regression: classifies only the named input errors as safe refusals ... ok', True),
        ('classifies only the named input errors as safe refusals ... FAILED (812µs)', 'classifies only the named input errors as safe refusals ... ok', False),
        ('BillingDunningTest#test_failed_charge_suspends = 0.02 s = .', 'BillingDunningTest#test_failed_charge_suspends = .', True),
        ('BillingDunningTest#test_failed_charge_suspends = 0.02 s = .', 'OtherTest#test_failed_charge_suspends = .', False),
        ('BillingDunningTest#test_failed_charge_suspends = 0.02 s = .', 'test_failed_charge_suspends = .', True),
        ('regression: BillingDunningTest#test_failed_charge_suspends = 0.02 s = .', 'test_failed_charge_suspends = .', False),
        ('BillingDunningTest#test_failed_charge_suspends = 0.02 s = F', 'test_failed_charge_suspends = .', False),
        ('regression: ✓ src/a.test.ts > returns error 33ms', '✓ src/a.test.ts > returns error', False),
        ('✓ src/a.test.ts > budget (20µs)', '✓ src/a.test.ts > budget (10µs)', False),
        ('✓ src/a.test.ts > budget (20µs)', '✓ src/a.test.ts > budget (20µs)', True),
        ('numeric title (20µs) ... ok (812µs)', 'numeric title (10µs) ... ok', False),
        ('numeric title (20µs) ... ok (812µs)', 'numeric title (20µs) ... ok', True),
        ('✓ src/a.test.ts > budget ... ok (20µs) (8ms)', '✓ src/a.test.ts > budget ... ok (10µs) (6ms)', False),
        ('✓ src/a.test.ts > budget ... ok (20µs) (8ms)', '✓ src/a.test.ts > budget ... ok (20µs) (6ms)', True),
        ('✓ src/a.test.ts > budget ... ok (20µs) 8ms', '✓ src/a.test.ts > budget ... ok (10µs) 6ms', False),
        ('✓ src/a.test.ts > budget ... ok (20µs) 8ms', '✓ src/a.test.ts > budget ... ok (20µs) 6ms', True),
        ('✓ src/a.test.ts > budget ... ok (20µs) (0.008s)', '✓ src/a.test.ts > budget ... ok (10µs) (0.006s)', False),
        ('✓ src/a.test.ts > budget ... ok (20µs) (0.008s)', '✓ src/a.test.ts > budget ... ok (20µs) (0.006s)', True),
        ('✓ src/a.test.ts > budget ... ok (20µs) 0.008s', '✓ src/a.test.ts > budget ... ok (10µs) 0.006s', False),
        ('✓ src/a.test.ts > budget ... ok (20µs) 0.008s', '✓ src/a.test.ts > budget ... ok (20µs) 0.006s', True),
    ]
    parser_ok = all(sees(output, selector) == want for output, selector, want in parser_cases)
    print(f"  {'ok' if parser_ok else 'BROKEN'}      check_proofs.py: complete identity with Vitest/Rails metadata")
    root = tempfile.mkdtemp(prefix="proofs-")
    fdir = os.path.join(root, ".specs", "features", FEATURE)
    os.makedirs(fdir)
    write_artifact(os.path.join(root, "runner.py"), RUNNER)
    r = '"' + sys.executable.replace("\\", "/") + '" runner.py'
    unit = {"unit": f'{r} 0 "PASS billing suspends on a failed charge (3 ms)" "PASS billing keeps a paid account"'}
    cases = [
        ("a group runs once and each check reads its line",
         proofs_md(unit, ["run unit | PASS billing suspends on a failed charge", "run unit | PASS billing keeps a paid account"]),
         0, {"C1": "pass", "C2": "pass"}, 1),
        ("a line the group never printed is no test ran",
         proofs_md(unit, ["run unit | PASS renamed test"]), 1, {"C1": "**no test ran**"}, None),
        ("a failed group: its passing line passes, the missing one fails, the group gets a fail row",
         proofs_md({"unit": f'{r} 1 "PASS billing suspends" "FAIL billing keeps a paid account"'},
                   ["run unit | PASS billing suspends", "run unit | PASS billing keeps a paid account"]),
         1, {"C1": "pass", "C2": "**fail**", "Run unit": "**fail** - exit 1"}, None),
        ("a proof naming a group no Run line defines",
         proofs_md(unit, ["run unit | PASS billing suspends on a failed charge", "run e2e | PASS checkout"]),
         1, {"C2": "**no such run**"}, None),
        ("a lone proof is judged by its exit code",
         proofs_md({}, [f"`{r} 0 ok`", f"`{r} 3 boom`"]), 1, {"C1": "pass", "C2": "**fail**"}, None),
        ("a lone proof two checks name runs once",
         proofs_md({}, [f"`{r} 0 ok`", f"`{r} 0 ok`"]), 0, {"C1": "pass", "C2": "pass"}, 1),
        ("a coloured line still matches",
         proofs_md({"unit": f'{r} 0 "{{esc}}[32mPASS{{esc}}[0m billing suspends"'}, ["run unit | PASS billing suspends"]),
         0, {"C1": "pass"}, None),
        ("partial words do not identify a complete test",
         proofs_md(unit, ["run unit | PASS suspends charge", "run unit | charge suspends PASS"]),
         1, {"C1": "**no test ran**", "C2": "**no test ran**"}, None),
        ("a POSIX shell proof runs as written, on Windows through Git Bash",
         proofs_md({}, ["`printf a | tr a b | grep -q b`"]), 0, {"C1": "pass"}, None),
        ("a failing build command is a fail row",
         proofs_md(unit, ["run unit | PASS billing suspends on a failed charge"], build=f'`{r} 2 "error: 2 offenses"`'),
         1, {"C1": "pass", "Build": "**fail** - error: 2 offenses"}, None),
        ("an old checks.md with a Mutations line still runs",
         proofs_md(unit, ["run unit | PASS billing suspends on a failed charge"], head="Mutations: 3\n"), 0, {"C1": "pass"}, None),
        # Run as a shell command, `browser; <runner>` would log a second run.
        ("a browser proof is never run and passes with no picture",
         proofs_md(unit, ["run unit | PASS billing suspends on a failed charge", f"browser; {r} 0 ran"]),
         0, {"C1": "pass", "C2": "pass - photo by the Verifier"}, 1),
    ]
    ok = parser_ok
    try:
        for desc, checks, want_code, want_rows, want_runs in cases:
            write_artifact(os.path.join(fdir, "checks.md"), checks)
            log = os.path.join(root, "ran.log")
            if os.path.exists(log):
                os.remove(log)
            code, out = run_script("check_proofs.py", FEATURE, "--root", root)
            written = read_artifact(os.path.join(fdir, "proofs.md"))
            rows = result_rows(written)
            runs = len(read_artifact(log).splitlines())
            if (code == want_code and all(rows.get(k, "").startswith(v) for k, v in want_rows.items())
                    and (want_runs is None or runs == want_runs) and "## Output" in written):
                print(f"  ok      check_proofs.py: {desc}")
            else:
                ok = False
                print(f"  BROKEN  check_proofs.py: {desc} - expected exit={want_code}, rows {want_rows}"
                      f"{'' if want_runs is None else f', {want_runs} run(s)'}; got exit={code}, {runs} run(s)")
                print("          " + (out + written).strip().replace("\n", "\n          "))
        code, out = run_script("check_proofs.py", FEATURE, "--root", root, "--mutations", "spec.json")
        if code == 2:
            print("  ok      check_proofs.py: --mutations is gone and exits 2")
        else:
            ok = False
            print(f"  BROKEN  check_proofs.py: --mutations - expected exit=2, got {code}: {out.strip()[:200]}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return ok


def run_local_guards():
    """Checks-only authorization and code-review freshness; Python/Git, no project runner."""
    ok = True
    for approved in (False, True):
        root = scaffold()
        try:
            fdir = os.path.join(root, ".specs", "features", FEATURE)
            os.remove(os.path.join(fdir, "plan.md"))
            path = os.path.join(fdir, "checks.md")
            text = re.sub(r"^Plan: .*\n", "", read_artifact(path), flags=re.M)
            if approved:
                text += '\n**Approved**: 2026-11-02 - user: "approved, go ahead"\n'
                write_artifact(path, text)
                code, output = run("validate_checks", root)
                held = code == 1 and "checks.md has no `## Gate Check Commands` section" in output
                print(f"  {'ok' if held else 'BROKEN'}      validate_checks: checks-only with no Gate Check Commands")
                ok = held and ok
                text += ("\n## Gate Check Commands\n\n| Suite | Command | Needs running |\n| --- | --- | --- |\n"
                         "| Rails tests | `bin/rails test` | nothing |\n")
            write_artifact(path, text)
            for validator in ("validate_checks", "validate_verification"):
                code, output = run(validator, root)
                want = 0 if approved else 1
                held = code == want and (approved or "checks.md has no `**Approved**" in output)
                print(f"  {'ok' if held else 'BROKEN'}      {validator}: checks-only approval={approved}")
                ok = held and ok
        finally:
            shutil.rmtree(root, ignore_errors=True)
    if shipped("validate_verification") and shutil.which("git"):
        root = scaffold()
        try:
            fdir = os.path.join(root, ".specs", "features", FEATURE)
            def git(*args):
                p = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "user.email=s@t", "-c", "user.name=selftest", *args],
                                   cwd=root, capture_output=True, text=True)
                if p.returncode:
                    raise RuntimeError(p.stderr)
                return p.stdout.strip()
            git("init", "-q")
            write_artifact(os.path.join(root, "app.ts"), "export const value = 1\n")
            git("add", "-A"); git("commit", "-qm", "feat: before")
            judged = git("rev-parse", "--short", "HEAD")
            report = os.path.join(fdir, "verification.md")
            proofs = os.path.join(fdir, "proofs.md")
            write_artifact(report, read_artifact(report).replace("**HEAD**: e4f5a6b", f"**HEAD**: {judged}"))
            git("add", ".specs"); git("commit", "-qm", "docs: evidence")
            head = git("rev-parse", "--short", "HEAD")
            write_artifact(proofs, re.sub(r"\*\*HEAD\*\*: .*", f"**HEAD**: {head}", read_artifact(proofs)))
            kept, kept_out = run("validate_verification", root)
            write_artifact(os.path.join(root, "app.ts"), "export const value = 2\n")
            git("add", "app.ts"); git("commit", "-qm", "fix: after")
            head = git("rev-parse", "--short", "HEAD")
            write_artifact(proofs, re.sub(r"\*\*HEAD\*\*: .*", f"**HEAD**: {head}", read_artifact(proofs)))
            stale, stale_out = run("validate_verification", root)
            write_artifact(report, read_artifact(report).replace(f"**HEAD**: {judged}", f"**HEAD**: {head}").replace("**Fixes**: 0", "**Fixes**: 1"))
            fresh, fresh_out = run("validate_verification", root)
            held = kept == 0 and stale == 1 and "fresh independent review" in stale_out and fresh == 0
            print(f"  {'ok' if held else 'BROKEN'}      validate_verification: code fix stales review, evidence-only does not, fresh review clears it")
            if not held:
                print(kept_out, stale_out, fresh_out)
            ok = held and ok
        finally:
            shutil.rmtree(root, ignore_errors=True)
    return ok


def main(argv=None):
    verbose = "-v" in (argv or sys.argv[1:])
    if not os.path.isdir(FIXTURES):
        print(f"selftest: fixtures directory missing: {FIXTURES}", file=sys.stderr)
        return 1

    base = scaffold()
    print("baseline - a clean artifact set must pass every gate")
    baseline_ok = True
    for validator in [v for v in ("validate_plan", "validate_checks", "validate_verification", "validate_tasks") if shipped(v)]:
        code, out = run(validator, base)
        if code != 0:
            baseline_ok = False
            print(f"  BROKEN  {validator} exit={code}")
            print("          " + out.strip().replace("\n", "\n          "))
        else:
            print(f"  ok      {validator}")
    shutil.rmtree(base)

    print("\ngate mutants - every mutant must be killed")
    killed = survived = 0
    for validator, artifact, desc, mutate, want_code, want_msg in CASES:
        if not shipped(validator):
            continue
        root = scaffold()
        path = os.path.join(root, ".specs", "features", FEATURE, artifact)
        with open(path, encoding="utf-8") as f:
            original = f.read()
        mutated = mutate(original)
        if mutated == original:
            survived += 1
            print(f"  VACUOUS {validator}: {desc} - the mutation did not apply, so the case proves nothing")
            shutil.rmtree(root)
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(mutated)
        code, out = run(validator, root)
        if code == want_code and want_msg in out:
            killed += 1
            if verbose:
                print(f"  killed  {validator}: {desc}")
        else:
            survived += 1
            print(f"  SURVIVED {validator}: {desc}")
            print(f"           expected exit={want_code} and {want_msg!r}, got exit={code}")
            print("           " + out.strip().replace("\n", "\n           "))
        shutil.rmtree(root)

    for validator, desc, edits, want_code, want_msg in MULTI_CASES:
        if not shipped(validator):
            continue
        root = scaffold()
        applied = True
        for artifact, edit in edits.items():
            path = os.path.join(root, ".specs", "features", FEATURE, artifact)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            original = read_artifact(path)
            mutated = edit(original)
            if mutated == original:
                applied = False
            write_artifact(path, mutated)
        if not applied:
            survived += 1
            print(f"  VACUOUS {validator}: {desc} - an edit did not apply, so the case proves nothing")
            shutil.rmtree(root)
            continue
        code, out = run(validator, root)
        if code == want_code and want_msg in out:
            killed += 1
            if verbose:
                print(f"  killed  {validator}: {desc}")
        else:
            survived += 1
            print(f"  SURVIVED {validator}: {desc}")
            print(f"           expected exit={want_code} and {want_msg!r}, got exit={code}")
            print("           " + out.strip().replace("\n", "\n           "))
        shutil.rmtree(root)

    if not verbose and survived == 0:
        print(f"  all {killed} killed (-v to list them)")

    print("\nnegative controls - a gate must not fire where nothing is owed")
    controls_ok = True
    for validator, desc, edits, *absent in NEGATIVE_CONTROLS:
        if not shipped(validator):
            continue
        root = scaffold()
        for artifact, edit in edits.items():
            path = os.path.join(root, ".specs", "features", FEATURE, artifact)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            original = read_artifact(path)
            mutated = edit(original)
            if mutated == original:
                controls_ok = False
                print(f"  VACUOUS {validator}: {desc} - the edit to {artifact} did not apply")
            write_artifact(path, mutated)
        code, out = run(validator, root)
        if code == 0 and not any(a in out for a in absent):
            print(f"  ok      {validator}: {desc}")
        else:
            controls_ok = False
            print(f"  FIRED   {validator}: {desc} - expected exit=0 with no {absent!r}, got {code}")
            print("          " + out.strip().replace("\n", "\n          "))
        shutil.rmtree(root)

    tooling = [run_tooling(), run_local_guards()]
    if shipped("check_proofs"):
        tooling.append(run_proofs_tooling())
    tooling_ok = all(tooling)

    print(f"\nselftest: {killed} killed, {survived} survived, "
          f"controls {'ok' if controls_ok else 'BROKEN'}, "
          f"tooling {'ok' if tooling_ok else 'BROKEN'}, "
          f"baseline {'clean' if baseline_ok else 'BROKEN'}")
    return 0 if (survived == 0 and baseline_ok and controls_ok and tooling_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
