# Execute: Validate & Verify

**Goal**: Verify implementation meets spec AND coding principles. This is NOT a separate phase - verification is part of every task's completion within Execute.

**Three levels of verification:**

1. **Per-task verification (always, author self-check):** After implementing each task, verify its "Done when" criteria before committing. This is mandatory and automatic. The implementer runs it.

2. **Feature-level validation (independent Verifier sub-agent, always-on, never prompted):** After all tasks for a feature are done, validation runs automatically - the orchestrator dispatches a **fresh Verifier sub-agent** (see [sub-agents.md](sub-agents.md)). Do NOT ask the user whether to run it; it is the safety net, not an opt-in. User interaction is limited to interactive UAT (for user-facing features) and acting on a FAIL verdict ("fix these gaps now?"). The Verifier:
   - Runs **read-only** over the real implementation and tests - mutations run in a scratch/throwaway state only (see Discrimination Sensor section)
   - Scopes coverage to the feature's **git diff surface** (not the full repository)
   - Re-derives coverage independently using **evidence-or-zero**: each AC cites `file:line` plus its exact assertion when tests are required, or the approved Tests:none row and actual command/observation when none is approved; absent outcome evidence counts as NOT covered
   - Runs the **spec-anchored outcome check** and the **discrimination sensor** (both described below)
   - Writes `.specs/features/[feature]/validation.md` with the full evidence report
   - Returns a compact verdict + ranked gap list to the orchestrator in chat
   - Gaps become **fix tasks** in the fix plan (step 8), for the user's yes, routed back to the `/implementar` skill; re-verification follows with a maximum of **3 fix→re-verify iterations** before escalating to the user

3. **Interactive UAT (for user-facing features only):** The feature has complex user-facing behavior where human judgment matters (UI flows, interaction patterns, visual design). For backend-only or infrastructure work, automated checks are sufficient.

**Trigger for explicit validation:** "Validate", "verify work", "UAT", "test with me", "walk me through it"

---

## Process

### 1. Check Completed Tasks

Go through tasks.md when present; otherwise use the persisted checks.md Execution Plan. On fix rounds also read the approved validation.md Fix Plans and their closure records:

- [ ] All tasks marked done?
- [ ] Any blocked or partial?

### 2. Spec-Anchored Acceptance Criteria Check

For each acceptance criterion in `spec.md`, the Verifier re-derives the **spec-defined expected outcome** and confirms its evidence matches it. Where the approved testing matrix requires tests, inspect the test's assertion. Where it permits Tests: none, cite that approved row and the actual command/observation proving the outcome; do not invent a test or count mere compilation as proof of an unrelated behavior:

```markdown
### P1: [Story Title]

**Acceptance Criteria**:

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion expression | Result |
| ------------------------- | -------------------- | ---------------------------------- | ------ |
| WHEN [X] THEN [Y]         | [precise value/state from spec] | `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | ✅ PASS / ❌ GAP / ⚠️ Spec-precision gap |
```

**Rules:**

- Where the spec defines a precise outcome (specific status code, field value, error message, state), the test assertion MUST target that exact outcome - not just that an assertion exists.
- Where the spec does NOT define a precise outcome, mark as **⚠️ Spec-precision gap** and flag it in the report. Do NOT silently pass a vague assertion.
- Evidence-or-zero: cite `file:line` for the assertion or affected artifact, together with the actual outcome evidence; a Tests:none row also cites the approved matrix entry. No outcome evidence means NOT covered.

Read checks.md alongside the spec, without replacing the all-AC table above. When tasks.md is
absent, use the testing matrix and gate commands in checks.md throughout this file.

For checks whose approved matrix requires tests, apply the following TLC judgement:

**Each check's test.** For every check, open the test its proof selects - the one whose line the
`run` proof names, or the one a lone proof's filter picks - and judge whether it would fail if the
claim were false: it asserts the value the criterion fixes, on the cases the criterion names, at
the layer the Test Coverage Matrix names. Write one `## Checks` row per check. A `no` is a finding:
the test passes without holding its criterion. Look hardest where a wrong decision costs most - a
returned value, a condition, a bound shifted by one, an order, a sign, a filter - and at rules the
diff touched that no check names: a rule in the browser with no test is still a rule.

For approved non-test, browser or walk proofs, judge the actual command/observation, saved comparison
or performed gesture instead of a test name. Preserve the matrix's approved Tests: none path.
Reconcile each Coverage member and each Swept landing against the spec and actual evidence;
a missing case or a negative Holds result also becomes GAP in the existing all-AC table and FAIL.

### 3. Check Edge Cases

From spec.md edge cases:

- [ ] [Edge case 1] handled correctly
- [ ] [Edge case 2] handled correctly

**Own examples.** For two rules the spec states, try a value neither the spec nor the checks name -
the other side of a boundary, an empty set, a large one. Run each at `HEAD` as a throwaway test or a
request. A rule that breaks on yours is a finding.

**Assertions that do not hold the value.** Report the tests whose assertion is looser than the value
the criterion fixes, that prove a rule on two cases out of nine, or that sit at another level than
the Test Coverage Matrix names for that layer.

### 4. Run Build-Level Gate Check (MANDATORY)

Run the Build-level gate check from the **Gate Check Commands** section in tasks.md, or checks.md when Tasks was skipped. This is NOT optional.

1. Run: `[Build gate command from the Gate Check Commands section in tasks.md]`
2. Non-zero exit code = STOP. Do not proceed to Code Quality Check.
3. Record results:
   - Total test count: [N]
   - Passed: [N]
   - Failed: [list]
   - Skipped: [list - each skip must be justified]

**Test Integrity Check:**

- Compare current test count against the count before this feature was implemented
- If test count DECREASED: investigate why. Tests should only be deleted with explicit justification.
- If assertions were weakened (less specific than before): flag as potential regression

### 5. Discrimination Sensor (MANDATORY - always runs after gate check passes)

The sensor checks whether the approved verification can detect a plausible wrong outcome. Where
the matrix requires tests, use those tests. Where it approves Tests:none, use the same prescribed
command, browser comparison or observation against the mutated scratch; do not invent a test suite.
It runs in a scratch/throwaway state - the real working tree is never modified.

**How it works:**

1. **Prepare an isolated scratch.** Never mutate the real worktree. Choose one:
   - Preferred: a temporary git worktree (`git worktree add <scratch-path> HEAD`), mutate and run tests there, then `git worktree remove --force <scratch-path>`.
   - Fallback (no git / worktree unavailable): copy only the affected file(s) to a temp directory, mutate the copies, point the test runner at those copies (or restore originals from the copies' backups), then delete the temp directory.
   - **Forbidden:** `git stash` / `git stash pop`. A stash records state *before* the mutation; popping it does not reverse a mutation applied afterward, and on a clean tree `git stash` creates no entry at all - so the fault is left in the real worktree.
2. **Capture a baseline.** Record `git status --porcelain` (or equivalent) of the real worktree *before* any sensor work. It must be unchanged after cleanup.
3. **Inject a behavior-level fault** into the scratch copy of the new code introduced by this feature. Choose a mutation proportional to the code's risk:
   - Flip a boolean condition (`if (x)` → `if (!x)`, `>` → `>=`)
   - Change a return value (return a wrong status code, wrong field, zero instead of a computed value)
   - Off-by-one (shift a loop bound, change a slice index)
   - Remove a required side effect (delete a method call that the spec requires)
4. **Run the approved verification** that covers the mutated outcome against the scratch: the tests and Quick/Full command where required; the prescribed command/gesture/comparison on the Tests:none path.
5. **Confirm the mutant is killed** (the verification detects the wrong outcome). Record actual expected/observed evidence, then discard the scratch (remove worktree or delete temp copies).
6. **Verify isolation.** Re-run `git status --porcelain` on the real worktree and confirm it matches the baseline from step 2. If it differs, STOP - restore the real tree before continuing, and treat the sensor run as invalid.
7. **If a mutant survives**, the approved verification does not discriminate that behavior: add a fix task for its assertion or verification procedure. If no relevant mutation can be exercised or observed, record the concrete blocker and stop before PASS; Tests:none is not a sensor exemption.

**Tiering (proportional, not optional):**

| Context | Sensor depth |
| ------- | ------------ |
| Default (all features) | Lightweight fault-injection: 1-3 targeted behavior-level mutations per feature, focused on the highest-risk new code |
| P0 / critical paths (payment, auth, data integrity) | Full mutation run: use language-appropriate mutation tooling if available (e.g., Stryker, mutmut, cargo-mutants, pitest); otherwise increase the number of manual fault-injection mutations to ≥5 covering all branches |

**Stack-agnostic:** The sensor targets behavior-level semantics (what the code does), not a specific tool. Any language, any framework.

**Report:** Record killed/survived for each mutation attempt. Surviving mutants → create fix tasks before marking the feature done.

### 6. Code Quality Check (MANDATORY)

For each changed file, verify against [coding-principles.md](coding-principles.md):

| Check                                | Pass? |
| ------------------------------------ | ----- |
| No features beyond what was asked    |       |
| No abstractions for single-use code  |       |
| No unnecessary "flexibility" added   |       |
| Only touched files required for task |       |
| Didn't "improve" unrelated code      |       |
| Matches existing patterns/style      |       |
| Would senior engineer approve?       |       |
| Tests map to acceptance criteria and are non-shallow (spot-check one story) | |
| Spec-anchored outcome check: each test's asserted value matches the spec-defined outcome (or gap flagged) | |
| Per-layer Coverage Expectation met: domain logic has 1:1 AC mapping; routes/e2e cover happy + edge + error paths for every route in scope | |
| Every test in scope maps to a spec AC, listed edge case, or Done-when criterion (no unclaimed tests) | |
| Documented project quality/testing guidelines followed (cite guideline file, or "none - strong defaults applied") | |

❌ Any "No"? → Fix before marking complete.

### 6b. Screen Photos (only for a feature with a screen)

Skip this step for backend-only or infrastructure work. The Verifier runs it, not the author, only after the gate check and the sensor (steps 4 and 5) pass, never at the same time: both use the running app. If the tests fail, skip this step and say the photos come in the next round.

1. Start the app locally, already logged in with the project's own test account (from its example or seed files).
2. Take a photo of every screen this feature changed, at 375, 768 and 1280 px wide. Also take each binding capture's comparison picture at its own viewport size and state as below; keep the three local widths even when the reference has another size. Use one app/browser at a time.

The author's picture is the author's claim, and a picture taken in a wider window and resized to the
capture's size passes as a match while the page at that size is a different layout. So open the
running app in a browser window at each capture's size - its pixel size divided by its scale, 1x
unless the file says otherwise - reach the state it draws the way the `**Walked:**` line says, and
save `captures/<capture>.running.png` over the author's. Judge your own picture. With no browser, record the blocker and do not claim the mandatory independent photos passed.
3. Look at every photo before showing it, and note each defect you see.
4. Each defect goes into the fix plan (step 8) and makes the verdict FAIL, like an issue from the Interactive UAT.
5. Show the photos to the user with the review result, every time, even when step 7 does not run.

### 6c. Settle the TLC proofs and finish their judgement

After the existing Build gate, sensor and applicable screen photos pass, write screens.md when
a browser proof needs it, using this same independent Verifier and every current photo width.
Do not freeze rows from an earlier round; refresh the whole affected screen review after a fix.
The source comparison follows this inventory, copied from TLC verify-screens.md:

Judge that one state. A fact that lives in another state is not a gap in this picture. A click that
is not itself in the picture is not a gap when the resulting state is.

Open the capture and its picture together. First write the capture's inventory: one row per thing it
draws - each region, control, label and sentence, chip, state mark, line, legend entry, and the
arrangement of each region. Then mark every row `same` or `differs`, applying what
`## Differences from the source` lists, and for `differs` say what the picture draws instead. The
fix covers what the rows name and nothing else, so the inventory is the whole judgement: a thing no
row names is never checked.

What counts as `differs`:

- **controls** - a control the capture shows missing, or one it does not show
- **arrangement** - not the same regions in the same places, with the same nesting
- **copy** - visible text the capture fixes, wrong; a date that follows the day the picture was taken
  is not wrong
- **drawing** - an element drawn differently: a line, a border, a badge, the shape of a bar, the
  layout of a meter or a form
- **render** - overlapping, cut off, scrolled off the window, unreadable, or a component the rest of
  the app does not use

Exact spacing, shade and type weight are a note on a `same` row. A picture with one `differs` row
`diverges`; otherwise it `matches`.

```markdown
# <Feature> screens
**Round**: <1 initially, then 2/3/4 after each of at most three fix rounds>
**HEAD**: <the commit reviewed>

| Screen | Compared to | Verdict |
| --- | --- | --- |
| captures/<name>.running.png | <the bound capture or approved criterion actually examined> | matches / diverges - <reason> |

### `captures/<name>.running.png`

| Element | Result | Picture draws |
| --- | --- | --- |
| <each region, control, text and arrangement> | same / differs | <actual difference, applying approved departures> |
```

Record the same independent Verifier and current HEAD in screens.md. A divergence becomes a finding
under the existing fix/approval rules. Local photos at other widths are also inspected against their
approved responsive outcomes; they do not replace the binding comparison. Rebuild the whole inventory
of each affected screen on every fix round; the upstream frozen-row/two-round shortcut is not imported.

Record each walk in checks.md Handoff with what was done and observed. Then run, sequentially:

```bash
python3 <skill-dir>/scripts/validate_checks.py <feature>
python3 <skill-dir>/scripts/check_proofs.py <feature>
```

Non-zero means no PASS: route the actual failure under the existing fix/approval rules.
Reconcile every resulting proof with the step-2 judgement at this HEAD before writing the report.
Keep browser comparison judgements independent; a screenshot's existence alone is not a match.
This ordering preserves tests-before-photos and avoids requiring screens.md before its reviewer runs.

### 7. Interactive UAT (if user-facing feature)

For each testable deliverable, present one test at a time, with its photos from step 6b:

```
Test [N]: [Test Name]

Expected: [What should happen - specific and observable]

→ Does this work? Describe what you see.
```

Wait for user response:

| User says                      | Interpret as            |
| ------------------------------ | ----------------------- |
| "yes", "pass", "works", "next" | ✅ Pass                 |
| "skip", "can't test", "n/a"    | ⏭️ Skip                 |
| Anything else                  | ❌ Issue - log verbatim |

**Severity inference (never ask the user for severity):**

| User description contains               | Inferred severity |
| --------------------------------------- | ----------------- |
| crash, error, exception, fails, broken  | Blocker           |
| doesn't work, wrong, missing, can't     | Major             |
| slow, weird, off, minor, small          | Minor             |
| color, font, spacing, alignment, visual | Cosmetic          |
| (unclear)                               | Major (default)   |

### 8. Generate Fix Plans (if issues found)

For each issue found during UAT, in the photos (step 6b), by the Verifier, or in the Standards and Spec reports of [code-review.md](code-review.md):

1. **Diagnose** - Analyze the codebase to find root cause
2. **Create fix task** - Write a task definition with:
   - What: The specific fix
   - Where: File paths
   - Verify: How to prove the fix works
   - Done when: Acceptance criteria for the fix
3. **Present fix plan** - Show all fix tasks to user for approval
4. **Close each fix** - Whoever fixes fills `Closed` with the commit that fixes it, then the check that now proves it; an item the user refused carries `Refused` with the user's words instead. A fix that needs a new criterion appends it to the spec with a new requirement ID and a check - never edits an approved one.

Keep checks.md in sync with approved fixes: cite the existing check, or append a new check for
an approved new criterion without rewriting an approved claim. Preserve each finding's closure or
verbatim Refused decision in the Findings index across reports; the index links to the existing
Fix Plans, it is not a second fix plan. Re-run the fresh Verifier and both gates after each fix.

Fix tasks follow the same format as regular tasks and are executed by the `/implementar` skill.

**Guardrail:** Maximum 3 diagnostic iterations per issue. If root cause isn't found after 3 attempts, flag for human investigation. The same 3-iteration bound applies to the Verifier's fix→re-verify cycle: if gaps persist after 3 rounds, escalate to the user rather than continuing to loop.

### 9. Write Validation Report File + Return Chat Summary (MANDATORY)

After all checks complete, the Verifier MUST:

1. **Write the persisted report** to `.specs/features/[feature]/validation.md` (see template below). This file is the evidence artifact - it survives the session and can be referenced by CI, reviewers, or future agents.
2. **Return a compact summary in chat** to the orchestrator (see Compact Chat Summary section below). The orchestrator surfaces it to the user and routes any ranked gaps to fix tasks.

**Deterministic backing (run it, do not eyeball it).** After writing the report, run `python3 <skill-dir>/scripts/validate_state.py <feature>` and then `python3 <skill-dir>/scripts/validate_verification.py <feature>`. Both must pass; the latter checks TLC proofs and Findings and does not replace the existing gate. Always pass this feature explicitly, never a historical sweep. It confirms the report is real - present, with a `**Verdict**:` line filled to PASS, backed by at least one `file:line` evidence citation, and not contradicted by its own tables (a mutant marked survived, or an acceptance criterion whose Result is neither PASS nor a spec-precision gap) - so a missing, hollow, placeholder, FAIL or self-contradicting report cannot slip through as done. A non-zero exit means the feature is NOT done: repair the report or route the FAIL gaps to fix tasks, then re-run. This is the closing gate of Execute and runs automatically, the same way the lessons layer runs at distillation; it is never a manual step. If no code-execution tool is available, confirm the same by reading `validation.md`.

### 10. Distill Lessons (MANDATORY when validation.md has signal)

This is the closing action of validation - not a separate phase. Immediately after the report is written, turn its grounded failures into reusable, project-local guidance by following [lessons.md](lessons.md). In short: for each surviving mutant, spec-precision gap, failed/uncovered AC, or `// SPEC_DEVIATION`, record one terse general lesson via `python3 <skill-dir>/scripts/lessons.py add` (the script enforces grounding and owns all bookkeeping). A clean PASS with no signal → record nothing. Run the self-check: if there was signal but no lesson was recorded, say so in chat. See [lessons.md](lessons.md) for the exact commands, phrasing rules, scope discipline, and the no-script fallback.

---

## Compact Chat Summary (returned in chat after validation)

The Verifier returns this block to the orchestrator after completing all checks:

```markdown
## Validation: [Feature] - [PASS ✅ | FAIL ❌]

**Spec-anchored check**: [N/N ACs matched spec outcome | M spec-precision gaps flagged]
**Gate**: [X passed, 0 failed]
**Sensor**: [N mutations injected, N killed, N survived]
**Report**: `.specs/features/[feature]/validation.md`

**Ranked gaps** (if FAIL):
1. [Gap description] - [AC or criterion] - [file:line or "no evidence"]
2. ...
```

---

## Validation Report Template (`.specs/features/[feature]/validation.md`)

```markdown
# [Feature] Validation

**Verdict**: [PASS | FAIL]
**Date**: [YYYY-MM-DD]
**Spec**: `.specs/features/[feature]/spec.md`
**Diff range**: [commit range or branch..HEAD]
**Verifier**: independent sub-agent (author ≠ verifier)
**Proofs**: `proofs.md` at <sha>
**HEAD**: <the code commit independently reviewed>

## Checks

| Check | Test | Holds |
| --- | --- | --- |
| C1 | <file and selected test, or approved command/browser/walk evidence> | yes / no - <reason> |

## Findings

| Finding | Evidence | Fix | Closed | Refused |
| --- | --- | --- | --- | --- |
| <issue> | <actual evidence> | <link to its existing Fix Plan> | <closing commit and check> | <user's exact refusal, or -> |

With no findings: replace the table with `None - <what was probed>`.
On later rounds retain earlier findings and their closure/refusal, then append new ones.

---

## Task Completion

| Task | Status     | Notes   |
| ---- | ---------- | ------- |
| T1   | ✅ Done    | -       |
| T2   | ✅ Done    | -       |
| T3   | ⚠️ Partial | [Issue] |

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| WHEN X THEN Y             | [precise value/state from spec] | `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | ✅ PASS |
| WHEN A THEN B             | [expected value]     | `path/to/test.ts:88` - `expect(res.status).toBe(400)` | ✅ PASS |
| WHEN C THEN D             | not precisely defined in spec | - | ⚠️ Spec-precision gap |

**Status**: ✅ All ACs covered / ❌ Gaps present / ⚠️ Spec-precision gaps flagged

---

## Discrimination Sensor

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| 1        | `src/service.ts:42` | Flipped condition `x > 0` → `x >= 0` | ✅ Killed |
| 2        | `src/service.ts:88` | Changed return value `status: 'active'` → `status: 'inactive'` | ✅ Killed |
| 3        | `src/handler.ts:15` | Removed side-effect call to `notify()` | ❌ Survived → fix task created |

**Sensor depth**: [lightweight / P0-full]
**Result**: [N/N killed] - [PASS ✅ | FAIL ❌]

---

## Interactive UAT Results (if performed)

| #   | Test        | Result   | Details                                         |
| --- | ----------- | -------- | ----------------------------------------------- |
| 1   | [Test name] | ✅ Pass  | -                                               |
| 2   | [Test name] | ❌ Issue | [Verbatim user response] - Severity: [inferred] |
| 3   | [Test name] | ⏭️ Skip  | [Reason]                                        |

---

## Code Quality

| Principle        | Status |
| ---------------- | ------ |
| Minimum code     | ✅     |
| Surgical changes | ✅     |
| No scope creep   | ✅     |
| Matches patterns | ✅     |
| Spec-anchored outcome check (asserted values match spec) | ✅ |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ✅ |
| Every test maps to a spec requirement - no unclaimed tests | ✅ |
| Documented guidelines followed: [file(s) or "none - strong defaults applied"] | ✅ |

---

## Edge Cases

- [x] Edge case 1: Handled correctly
- [ ] Edge case 2: NOT handled - needs fix

---

## Gate Check

- **Gate command**: [Build gate command from the Gate Check Commands section in tasks.md]
- **Result**: [X] passed, [Y] failed, [Z] skipped
- **Test count before feature**: [N]
- **Test count after feature**: [M]
- **Delta**: [+(M - N) new tests]
- **Skipped tests**: [list with justification for each]
- **Failures**: [list with details]

---

## Fix Plans (if issues found)

### Fix 1: [Issue description]

- **Root cause**: [What's actually wrong]
- **Fix task**: [Task definition]
- **Priority**: [Blocker/Major/Minor/Cosmetic]
- **Closed**: [the commit that fixes it and the check that now proves it]

---

## Requirement Traceability Update

Update spec.md requirement statuses:

| Requirement | Previous Status | New Status   |
| ----------- | --------------- | ------------ |
| [FEAT]-01   | Implementing    | ✅ Verified  |
| [FEAT]-02   | Implementing    | ❌ Needs Fix |

---

## Summary

**Overall**: ✅ Ready | ⚠️ Issues | ❌ Not Ready

**Spec-anchored check**: [N/N ACs matched spec outcome | M spec-precision gaps]
**Sensor**: [N/N mutations killed]
**Gate**: [X passed]

**What works**: [List]

**Issues found**: [Issue 1: How to fix]

**Next steps**: [Action]
```

---

## Tips

- **Validation is never prompted** - it always runs after the last task; do not ask the user whether to run it
- **Spec-anchored, not just covered** - "there is an assertion" is not enough; the assertion must target the spec-defined outcome
- **Sensor in scratch only** - never mutate the real tree; use a temp worktree or file copies (never `git stash`), run, discard, then confirm porcelain matches the pre-sensor baseline
- **Surviving mutants are fix tasks** - do not mark the feature done if the sensor found weak tests
- **P1 first** - MVP must work before P2/P3
- **WHEN/THEN = Test** - Each criterion is a test case
- **Be specific** - "Doesn't work" isn't helpful
- **Recommend fixes** - Don't just report problems, create fix tasks
- **Quality check is mandatory** - Not optional
- **Infer severity** - Never ask the user "how bad is this?"
- **Max 3 diagnostic iterations** - Prevents infinite investigation loops
- **Update traceability** - Every verified requirement updates spec.md status
- **Always write the report file** - `.specs/features/[feature]/validation.md` is the persisted evidence artifact
- **Distill after writing** - turn grounded failures into lessons via `scripts/lessons.py` ([lessons.md](lessons.md)); clean PASS → no lesson
