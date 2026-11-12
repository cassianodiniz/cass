# Verify

A safety net that raises the work, not an audit of it. A script settles what can be settled mechanically; a fresh sub-agent, the Verifier, judges the rest and takes and judges the screen photos. It runs at completion and freshly after each code fix. The initial review is `**Fixes**: 0`; at most three code fix-to-review iterations follow.

## Author is not verifier

**Always-on, never prompted - one per feature completion.** The Verifier runs once - after the last commit of the feature - as an independent quality gate, dispatched automatically by the orchestrator, and again freshly after each code fix. Do NOT ask the user whether to run validation; it is mandatory.

**Author ≠ verifier:** The agent (or worker) that wrote the code and tests is the author. The Verifier is a fresh sub-agent dispatched by the orchestrator after the final commit. It does not inherit the author's context, mental model, or assumptions. This separation is what makes the gate trustworthy. The author's notes in `checks.md`'s `## Handoff` carry that thinking, so the Verifier reads the claims and proofs, not the Handoff.

**What the Verifier receives:**
- `plan.md` for the feature (`## Criteria` = source of truth)
- `checks.md` and `proofs.md`
- The git diff surface for the feature (scoped to the feature branch or commit range)
- The test files in scope
- This file as its operating checklist

**What the Verifier does (full process below):**
1. **Plan-anchored coverage check** - re-derives coverage evidence-or-zero: every criterion traced to `file:line` + assertion expression. For each covered criterion, confirms the test's asserted value matches the **plan-defined expected outcome** (not just that an assertion exists). Where the plan does not define a precise outcome, flags a **spec-precision gap** rather than passing silently.
2. **Discrimination sensor** - injects a small behavior-level fault (flip a condition, change a return value, off-by-one, remove a required side effect) in an **isolated scratch** (temporary `git worktree` or temp file copies - never `git stash`), runs the relevant tests there, confirms they FAIL (kill the mutant), discards the scratch, and verifies the real worktree's `git status --porcelain` matches the pre-sensor baseline. Tiered by risk: lightweight (1-3 mutations) for standard features; expanded (≥5 mutations or full mutation tooling) for P0/critical paths. Surviving mutants become findings.
3. Applies the **payload/conjunction rule**: checks payload fields are asserted on value/state, not just that the call occurred.
4. **Writes the persisted report** to `.specs/features/[feature]/verification.md` - PASS/FAIL, per-criterion evidence (`file:line` + assertion + plan outcome), sensor result (killed/survived per mutation), gate exit results, diff/commit range.
5. **Returns a compact verdict in chat** to the orchestrator.
6. Does **NOT** write, modify, or fix any code or tests - the real working tree is never mutated (sensor mutations and own examples run in scratch state only).

**Failure handling:** The orchestrator puts the ranked gaps into the fix plan (step 8) for the user's yes; the selected executor builds them, then a fresh Verifier is dispatched. This fix→re-verify loop is bounded to a maximum of **3 iterations**. If gaps remain after 3 iterations, escalate to the user.

**Standalone fallback:** When running without sub-agents (a single agent executing the full feature), run this file as an independent fresh-eyes pass in a new session - re-read `plan.md`, `checks.md` and the diff from scratch, apply evidence-or-zero, run the plan-anchored check and discrimination sensor, write the report file with `Verifier: self-verified (degraded - no sub-agent)`, then run the gate below; it flags the degraded review.

**Model tier:** The Verifier is never the cheapest tier; a weak Verifier defeats the author ≠ verifier gate.

## The round

1. The builder runs `python3 <spec-plan>/scripts/check_proofs.py <feature>` at `HEAD`. It runs each `Run` group and each lone proof once, one at a time, finds each check's line in its group's output, runs the build, checks the walk, and writes `proofs.md` with the tail of every run. A red row is the builder's to fix before anything else. A `browser` proof is not judged there: the Verifier photographs it (step 6b).
2. Through local `/build-review`, the builder dispatches the fresh Verifier and fresh Standards and Spec roles. All reviewers read the same code `HEAD`. Dispatch names the feature, files and diff range without telling reviewers what to accept. Each goes on the `**Dispatched:**` line of `checks.md` `## Handoff` before it is sent; a builder resuming after a compaction waits for a dispatched review with no returned report for that code `HEAD` instead of sending another. An older report does not count.
3. The builder fixes findings within the approved scope, records their closing commits, and reruns `check_proofs.py <feature>` before concluding repairs. For a code fix, increment `**Fixes**` and dispatch a new, fresh Verifier on the corrected `HEAD`, with the count and earlier findings/closure commits as facts, not the author's assessment. The new Verifier judges the real corrected tree, takes the photos again and retains the earlier findings and closure records in verification.md. Repeat only up to `**Fixes**: 3`; remaining failures go to the user before any fourth fix. Do not reset the count on resume or replace a fresh review with green proofs. A commit confined to evidence under `.specs/` needs current proofs, not a new code review.

---

## Process

### 1. Check Completed Checks

Go through checks.md:

- [ ] All checks C1..Cn marked done?
- [ ] Any blocked or partial?

### 2. Plan-Anchored Acceptance Criteria Check

For each acceptance criterion in `plan.md` `## Criteria`, the Verifier re-derives the **plan-defined expected outcome** and confirms the test's actual assertion matches it:

```markdown
### S1: [Story Title]

**Acceptance Criteria**:

| Criterion (WHEN X THEN Y) | Plan-defined outcome | `file:line` + assertion expression | Result |
| ------------------------- | -------------------- | ---------------------------------- | ------ |
| WHEN [X] THEN [Y]         | [precise value/state from plan] | `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | ✅ PASS / ❌ GAP / ⚠️ Spec-precision gap |
```

**Rules:**

- Where the plan defines a precise outcome (specific status code, field value, error message, state), the test assertion MUST target that exact outcome - not just that an assertion exists.
- Where the plan does NOT define a precise outcome, mark as **⚠️ Spec-precision gap** and flag it in the report. Do NOT silently pass a vague assertion.
- Evidence-or-zero: a criterion with no `file:line` citation counts as NOT covered.

**Each check's test.** For every check, open the test its proof selects - the one whose line the `run` proof names, or the one a lone proof's filter picks - and judge whether it would fail if the claim were false: it asserts the value the claim fixes, on the cases the claim names, at the layer the claim sits. Write one `## Checks` row per check. A `no` is a finding: the test passes without holding its criterion. For an approved `walk` proof, judge the recorded visit instead of a test name; a `browser` proof is judged by your photo in step 6b.

### 3. Check Edge Cases

From the plan's IF/THEN criteria (edge cases):

- [ ] [Edge case 1] handled correctly
- [ ] [Edge case 2] handled correctly

**Own examples.** For two rules the plan states with examples, try a value neither the plan nor the checks name - the other side of a boundary, an empty set, a large one. Run each in the same isolated scratch as the sensor (step 5), never in the real tree, as a throwaway test or a request. A rule that breaks on yours is a finding.

### 4. Run Build-Level Gate Check (MANDATORY)

Run every suite in the approved **Gate Check Commands** table in plan.md (or checks.md without a plan) yourself, at the reviewed code HEAD, starting what each row needs running. This is NOT optional; the builder's runs do not replace yours.

1. Run: `[Command for each suite from the Gate Check Commands table in plan.md]`
2. Non-zero exit code = skip the sensor (step 5). Proceed to Code Quality Check; report the red suite as a Finding.
3. Record results:
   - Total test count: [N]
   - Passed: [N]
   - Failed: [list]
   - Skipped: [list - each skip must be justified]

**Test Integrity Check:**

- Compare current test count against the count before this feature was implemented
- If test count DECREASED: investigate why. Tests should only be deleted with explicit justification.
- If assertions were weakened (less specific than before): flag as potential regression

Cross-check the table against the project's test docs, CI and scripts, including scripts the general runner skips. An omitted existing suite is a Finding, even when its files did not change. A suite you could not run is reported as unverified, never invented.

### 5. Discrimination Sensor (MANDATORY - always runs after gate check passes)

The sensor provides the empirical guarantee that the tests can actually detect regressions. It runs in a scratch/throwaway state - the real working tree is never modified.

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
   - Remove a required side effect (delete a method call that the plan requires)
4. **Run the tests** that cover the mutated code (against the scratch). Use the command of that suite from the Gate Check Commands table.
5. **Confirm the mutant is killed** (tests FAIL). Discard the scratch (remove worktree or delete temp copies). An import/environment error or unexercised fault is not a kill.
6. **Verify isolation.** Re-run `git status --porcelain` on the real worktree and confirm it matches the baseline from step 2. If it differs, STOP - restore the real tree before continuing, and treat the sensor run as invalid.
7. **If a mutant survives** (tests still pass after the fault), the tests are not discriminating for that behavior - add a finding to strengthen the assertion.

**Tiering (proportional, not optional):**

| Context | Sensor depth |
| ------- | ------------ |
| Default (all features) | Lightweight fault-injection: 1-3 targeted behavior-level mutations per feature, focused on the highest-risk new code |
| P0 / critical paths (payment, auth, data integrity) | Full mutation run: use language-appropriate mutation tooling if available (e.g., Stryker, mutmut, cargo-mutants, pitest); otherwise increase the number of manual fault-injection mutations to ≥5 covering all branches |

**Stack-agnostic:** The sensor targets behavior-level semantics (what the code does), not a specific tool. Any language, any framework.

**Report:** Record killed/survived for each mutation attempt under `## Discrimination Sensor`, with the columns of the template below. Surviving mutants → findings before marking the feature done. If the sensor cannot be exercised, report the blocker before PASS.

For a survivor the user explicitly refuses, copy its complete `Fault` cell unchanged into that item's `Finding` cell and record that item's quoted refusal in `Closed`. The label must be nonempty and occur exactly once among sensor `Fault` rows and exactly once among Findings; only surrounding cell whitespace is ignored. Keep `Killed?` as the actual `no`: refusal settles only that one finding, never the sensor as a whole.

### 6. Code Quality Check (MANDATORY)

For each changed file, verify against the shared coding principles:

| Check                                | Pass? |
| ------------------------------------ | ----- |
| No features beyond what was asked    |       |
| No abstractions for single-use code  |       |
| No unnecessary "flexibility" added   |       |
| Only touched files required for the plan |   |
| Didn't "improve" unrelated code      |       |
| Matches existing patterns/style      |       |
| Would senior engineer approve?       |       |
| Tests map to acceptance criteria and are non-shallow (spot-check one story) | |
| Plan-anchored outcome check: each test's asserted value matches the plan-defined outcome (or gap flagged) | |
| Per-layer Coverage Expectation met: domain logic has 1:1 criterion mapping; routes/e2e cover happy + edge + error paths for every route in scope | |
| Every test in scope maps to a plan criterion, listed edge case, or check (no unclaimed tests) | |
| Documented project quality/testing guidelines followed (cite guideline file, or "none - strong defaults applied") | |

❌ Any "No"? → It is a finding; fix before marking complete.

### 6b. Screen Photos (only for a feature with a screen)

Skip this step for backend-only or infrastructure work. The Verifier runs it, not the author, only after the gate check and the sensor (steps 4 and 5) finish, never at the same time: both use the running app.

1. Start the app locally, already logged in with the project's own test account (from its example or seed files). If there is none, ask the user once and record it in the project.
2. Take a photo of every screen this feature changed, at 375, 768 and 1280 px wide. Save them as `captures/review-<screen>-<width>.png`.
3. When a criterion cites a capture (a model image), also reach that state and take its photo in a browser window at the capture's size - its pixel size over its scale - so the page lays out as the capture does; an image resized afterwards does not. Save it as `captures/review-<capture>.png` and compare it with the capture: controls, arrangement, copy, drawing and render. It matches except for what `## Differences from the source` lists.
4. Look at every photo before showing it, and note each defect you see.
5. Each defect goes into the fix plan (step 8) and makes the verdict FAIL, like an issue from the Interactive UAT.
6. Show the photos to the user with the review result, every time, even when step 7 does not run.

If the app does not open, the result is "Não deu para revisar as telas", with the reason, and the PR is not marked ready until the user decides.

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

For each issue found during UAT, in the photos (step 6b), by the Verifier, or in the Standards and Spec reports:

1. **Diagnose** - Analyze the codebase to find root cause
2. **Create fix item** - Write one row in `## Findings` with:
   - What: The specific fix
   - Where: File paths
   - Verify: How to prove the fix works
   - Done when: Acceptance criteria for the fix
3. **Present fix plan** - Show all fix items to user for approval

Fix items are executed by the selected executor (`/implementar`, or the Codex session of `/gpt-implementar`), which fills `Closed`.

**Guardrail:** Maximum 3 diagnostic iterations per issue. If root cause isn't found after 3 attempts, flag for human investigation. The same 3-iteration bound applies to the Verifier's fix→re-verify cycle: if gaps persist after 3 rounds, escalate to the user rather than continuing to loop.

### 9. Write Verification Report File + Return Chat Summary (MANDATORY)

After all checks complete, the Verifier MUST:

1. **Write the persisted report** to `.specs/features/[feature]/verification.md` (see template below). This file is the evidence artifact - it survives the session and can be referenced by CI, reviewers, or future agents. **Every ❌ GAP, ⚠️ spec-precision gap, Code Quality "No", unhandled edge case, surviving mutant, photo defect and UAT issue is also a row of `## Findings`** - the gate reads that table.
2. **Return a compact summary in chat** to the orchestrator (see Compact Chat Summary section below). The orchestrator surfaces it to the user and routes any ranked gaps to fix items.

**Deterministic backing (run it, do not eyeball it).** The gate is `python3 <build-review>/scripts/validate_verification.py <feature>` (see The gate below). A non-zero exit means the feature is NOT done: repair the report or route the FAIL gaps to fix items, then re-run. If no code-execution tool is available, confirm the same by reading `verification.md`.

### 10. Distill Lessons (MANDATORY when verification.md has signal)

This is the closing action of validation - not a separate phase. Immediately after the report is written, turn its grounded failures into reusable, project-local guidance by following [memory.md](../../spec-plan/references/memory.md): for each surviving mutant, spec-precision gap, failed/uncovered criterion or other finding, record one terse general lesson via `python3 <spec-plan>/scripts/lessons.py add` (the script enforces grounding and owns all bookkeeping). A clean PASS with no signal → record nothing. If there was signal but no lesson was recorded, say so in chat.

---

## Compact Chat Summary (returned in chat after validation)

The Verifier returns this block to the orchestrator after completing all checks:

```markdown
## Validation: [Feature] - [PASS ✅ | FAIL ❌]

**Plan-anchored check**: [N/N criteria matched plan outcome | M spec-precision gaps flagged]
**Gate**: [X passed, Y failed]
**Sensor**: [N mutations injected, N killed, N survived]
**Photos**: [N photos, N defects | no screen]
**Report**: `.specs/features/[feature]/verification.md`

**Ranked gaps** (if FAIL):
1. [Gap description] - [criterion or check] - [file:line or "no evidence"]
2. ...
```

---

## Verification Report Template (`.specs/features/[feature]/verification.md`)

```markdown
# [Feature] verification

**Verdict**: [PASS | FAIL]
**HEAD**: [sha of the code reviewed; unknown only without git]
**Fixes**: [0 initial, then 1-3]
**Proofs**: `proofs.md` at [sha]
**Date**: [YYYY-MM-DD]
**Plan**: `.specs/features/[feature]/plan.md`
**Diff range**: [commit range or branch..HEAD]
**Verifier**: independent sub-agent (author ≠ verifier)

---

## Checks

| Check | Done | Test | Holds |
| ----- | ---- | ---- | ----- |
| C1    | ✅   | `stock-map.service.test.ts` `counts a Transfer in on its destination` | no - asserts the count, not the sign |
| C2    | ✅   | `transfers.e2e.test.ts` `rejects a transfer to the same location` | yes |

---

## Plan-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Plan-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| WHEN X THEN Y             | [precise value/state from plan] | `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | ✅ PASS |
| WHEN C THEN D             | not precisely defined in plan | - | ⚠️ Spec-precision gap |

**Status**: ✅ All criteria covered / ❌ Gaps present / ⚠️ Spec-precision gaps flagged

---

## Discrimination Sensor

| Fault | File:line | Verification | Killed? |
| ----- | --------- | ------------ | ------- |
| Flipped condition `x > 0` → `x >= 0` | `src/service.ts:42` | `npx vitest run src/service` | yes - 2 tests failed |
| Removed side-effect call to `notify()` | `src/handler.ts:15` | `npx vitest run src/handler` | no - survived → finding |

**Sensor depth**: [lightweight / P0-full]
**Isolation**: porcelain before = after
**Result**: [N/N killed] - [PASS ✅ | FAIL ❌]

---

## Screen Photos (if the feature has a screen)

| Photo | Width / compared with | Defects |
| ----- | --------------------- | ------- |
| `captures/review-billing-375.png` | 375 | none |
| `captures/review-billing--card-form.png` | `captures/billing--card-form.png` | expiry and CVC on a second row |

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
| Plan-anchored outcome check (asserted values match plan) | ✅ |
| Per-layer Coverage Expectation met (domain 1:1 criteria; routes happy+edge+error) | ✅ |
| Every test maps to a plan requirement - no unclaimed tests | ✅ |
| Documented guidelines followed: [file(s) or "none - strong defaults applied"] | ✅ |

---

## Edge Cases

- [x] Edge case 1: Handled correctly
- [ ] Edge case 2: NOT handled - needs fix

**Own examples**: [value tried] - [result]; [value tried] - [result]

---

## Test integrity

- **Gate commands**: [each suite from the Gate Check Commands table]
- **Result**: [X] passed, [Y] failed, [Z] skipped
- **Test count before feature**: [N]
- **Test count after feature**: [M]
- **Delta**: [+(M - N) new tests]
- **Skipped tests**: [list with justification for each]
- **Failures**: [list with details]

---

## Findings

| Finding | Evidence | Fix | Closed |
| ------- | -------- | --- | ------ |
| Removed side-effect call to `notify()` | survived the sensor - no test asserts the notification | What / Where / Verify / Done when - source: Verifier - severity: Major | |
| Expiry and CVC on a second row | `captures/review-billing--card-form.png` against `captures/billing--card-form.png` | ... - source: photos - severity: Cosmetic | |

---

## Summary

**Overall**: ✅ Ready | ⚠️ Issues | ❌ Not Ready

**Plan-anchored check**: [N/N criteria matched plan outcome | M spec-precision gaps]
**Sensor**: [N/N mutations killed]
**Gate**: [X passed]

**What works**: [List]

**Issues found**: [Issue 1: How to fix]

**Next steps**: [Action]
```

Every check gets a `## Checks` row with the test named; the gate refuses a missing row or an empty `Test`. With nothing to report, write `None - <one line on what was probed>` under `## Findings` and `**Verdict**: PASS`. The executor fills `Closed` with the commit that fixes each one and the check that now proves it. An item the user explicitly refuses instead uses `Closed`: `Refused - user: "<actual words>"`; never invent that reply or present refusal as a fix. The gate refuses an empty `Closed` or a refusal without quoted words. A code fix still requires a fresh review: do not update the reviewed HEAD on behalf of the Verifier. Keep `**Fixes**` cumulative (0 initial, then 1-3), earlier findings and their closure commits.

## The gate

```bash
python3 <build-review>/scripts/validate_verification.py <feature>
```

It reads `proofs.md` at `HEAD` (every check and run has a passing row), the `## Checks` table (a row with a test for every check), the actual `**Approved**:` line in plan.md (or checks.md without a plan), every finding closed, the sensor table (no unrefused survivor next to PASS), and verification.md's `**Verdict**`, reviewed code `**HEAD**` and `**Fixes**` (0-3). A code change after that review fails; an evidence-only `.specs/` commit does not. Without git, freshness is explicitly degraded and warned, as in SKILL.md. `0` means the feature is done. The gate does not read the photos, UAT or the Standards and Spec reports: their issues count only as `## Findings` rows.

---

## Tips

- **Validation is never prompted** - it always runs after the last commit; do not ask the user whether to run it
- **Plan-anchored, not just covered** - "there is an assertion" is not enough; the assertion must target the plan-defined outcome
- **Sensor in scratch only** - never mutate the real tree; use a temp worktree or file copies (never `git stash`), run, discard, then confirm porcelain matches the pre-sensor baseline
- **Surviving mutants are findings** - do not mark the feature done if the sensor found weak tests
- **S1 first** - MVP must work before the rest
- **WHEN/THEN = Test** - Each criterion is a test case
- **Be specific** - "Doesn't work" isn't helpful
- **Recommend fixes** - Don't just report problems, write fix items
- **Quality check is mandatory** - Not optional
- **Infer severity** - Never ask the user "how bad is this?"
- **Max 3 diagnostic iterations** - Prevents infinite investigation loops
- **Always write the report file** - `.specs/features/[feature]/verification.md` is the persisted evidence artifact
- **Distill after writing** - turn grounded failures into lessons via `scripts/lessons.py` ([memory.md](../../spec-plan/references/memory.md)); clean PASS → no lesson
