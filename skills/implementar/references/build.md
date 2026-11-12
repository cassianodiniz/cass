# Build

**Goal**: Implement ONE slice at a time. Surgical changes. Verify. Commit. Repeat.

This is where code gets written. Every slice follows the same cycle: plan → implement → verify → commit. Verification is built into every slice, not a separate phase.

Deliver what the user asked for, at the quality you would sign. The checks are the floor and the evidence, not the target; the route is yours. No task list. The bar is [core.md](../../spec-plan/references/core.md) rules 2, 3 and 6.

## Build against the source

Before code, read the actual `**Approved**:` authorization in plan.md, or checks.md when there is no plan, and run `validate_checks.py <feature>` for its structural gate. If authorization is missing, present the plan or checks and stop; do not ask again for authorization already given.

When the plan marks a source binding, the source is the reference, not the plan's description of it. Where a check or a criterion disagrees with the source, ask before building that part.

## Complete test battery

The battery is the approved `## Gate Check Commands` table in plan.md (checks.md when there is no plan): every suite and script it lists, each with its command, starting what each row needs running. The independent Verifier runs it, in the review (skill build-review); while building, run only each slice's gate below. A focal Proof command or compilation alone does not establish this battery. Record each run under `## Test runs` in checks.md: suite, command, HEAD, actual output (or an output path), total, passed, failed and each skip with its justification. Separate inherited failures and environment blockers; never invent counts a runner did not report. A listed suite without its required environment or permission remains unverified; it is not non-applicable.

The coordinator reconciles these records on delegated returns; the independent Verifier runs the whole table at the reviewed HEAD ([verify.md](verify.md)) and records its integrity judgement under `## Test integrity` in verification.md. This is not another task list, nor a full-battery rerun just because a return arrived without code changing.

## Gate failure recovery

Run the gate check commands for the slice's checks and its gate level. This is MANDATORY - not "if applicable."

1. Look up the commands for the slice's Proofs and, for the slice's Gate level (quick/full/build), the suites in the `## Gate Check Commands` table, then run them
2. Non-zero exit code: do not commit. Fixing the failure and re-running is part of the slice, not a stop. If the gate is still red after 3 fix attempts, stop and report it. A failure caused by the environment rather than by the code (a service that is down, a timeout while the machine is under load) is re-run once unchanged; if it fails again, stop and report it.
3. Confirm the test count matches expectations (no tests were silently deleted or skipped)
4. For the checks this slice settles, keep Proof selectors aligned with the tests actually run; copy the real passing line for a Run proof. Record check IDs with the existing gate evidence. A changed selector does not authorize changing a claim or weakening a test.

**Tiered gates (from the `## Gate Check Commands` table):**

| Slice includes                   | Gate level | What runs                    |
| -------------------------------- | ---------- | ---------------------------- |
| Unit tests only                  | Quick      | Suites marked quick          |
| E2E or integration tests         | Full       | Suites marked quick and full |
| No tests (config, entities, etc) | Build      | Build + lint only            |

STOP at a red gate blocks review and commit; authorized corrections inside the approved scope follow this recovery before proceeding. A wrong check still requires renegotiation. Record attempts and environment retries with the gate evidence in checks.md; resume does not reset them. These limits do not extend the separate three code fix-to-review iterations or the selected executor's own bound.

## Post-gate review

After the gate check passes:

1. Verify test count: Are there at least as many test cases as before? (prevents silent deletion)
2. Verify no SPEC_DEVIATION: If implementation diverged from the approved plan, add a marker:

```
// SPEC_DEVIATION: [what diverged]
// Reason: [why the deviation was necessary]
```

3. Quick complexity check: "Would senior engineer flag this as overcomplicated?"
   - Yes → Simplify, re-run gate
   - No → Proceed

4. **Test Adequacy Review (MANDATORY - hard gate).**

   A slice cannot be committed or marked done until all four checks below pass. Tests must be both **necessary** (every test traces to a requirement) and **sufficient** (every requirement is covered). The scope boundary is the approved plan - do not test beyond it.

   **Check A - Sufficient coverage (per-layer depth).** Build and output this table:

   | Check / plan criterion / listed edge case | `file:line` + assertion expression | Spec-defined outcome | Covered? |
   | ------------------------------------------------- | ---------------------------------- | -------------------- | -------- |
   | [criterion from task or spec] | `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | [expected value from spec] | ✅ Yes / ❌ No / ⚠️ Spec-precision gap |

   **Evidence-or-zero rule:** Each covered cell MUST cite the exact `file:line` where the assertion lives AND reproduce the assertion expression (not just the `describe`/`it` name). A criterion with no located `file:line` evidence counts as **NOT covered**; the slice cannot be marked done. Do not declare a criterion absent without first searching the test files - show the search before concluding it is missing (mirror: evidence or zero, never a guess).

   **Spec-anchored outcome check:** For each covered criterion, derive the expected outcome from `plan.md` (or the slice's checks in `checks.md`) and confirm the test's asserted value matches it - not just that an assertion exists. Where the spec defines a precise outcome (e.g., a specific status code, a specific field value, a specific error message), the test assertion MUST target that exact outcome. Where the spec does not define a precise outcome, mark the cell as **⚠️ Spec-precision gap** and add a note; do NOT silently pass a vague assertion as if it were covered.

   Every check, every plan.md criterion, and every listed edge case that applies to this slice must map to at least one concrete test assertion. Enforce this per-layer depth:

   - Domain / service layer: assertions map 1:1 to spec ACs; every listed edge case has a dedicated test.
   - Route / controller / e2e layer: every route the slice adds or modifies must have a happy-path test, a test for each listed edge case, and a test for each documented error/failure path.

   No criterion left unverified.

   **Check B - Non-shallow litmus.** Reject each of the following shallow patterns:
   - Assertion-free tests or `expect(true)` / `expect(1).toBe(1)` style tautologies
   - "No error thrown" as the only assertion - unless not-throwing IS the specified behavior
   - Asserting only on mock call counts when the actual output/state is what the criterion demands
   - Happy-path only when the slice's checks or plan.md list edge cases

   **Payload/conjunction rule.** For each named field in an emitted event, returned object, or persisted record, apply a separate check:
   1. Open the constructed object at its `file:line` and confirm the field is present in the assertion.
   2. Confirm the assertion targets the field's **value or state**, not just the call that produced it.
   3. A present `emit(...)` / `return ...` / `save(...)` call does NOT prove the field - only an assertion on the result does.
   4. Asserting a method was called (spy/mock) != asserting the resulting state. Both may be needed; neither substitutes for the other.

   Apply this check to every payload-bearing criterion before marking it covered.

   **Stack-agnostic litmus:** An assertion is shallow if it would still pass under a plausible *wrong* implementation. If so, strengthen it before committing.

   **Check C - Necessary (no tests beyond the spec).** Reverse-map every test back to a plan criterion, a listed edge case, or a check. Build this table:

   | `file:line` + assertion expression | Maps to (AC / edge case / Done-when criterion) | Keep? |
   | ---------------------------------- | ---------------------------------------------- | ----- |
   | `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | [requirement ID or criterion text] | ✅ Keep / ❌ Remove |

   Any test that maps to nothing → remove it. A test with no requirement is scope creep - it proves nothing about the feature and expands scope beyond the spec. Do not write speculative "what if" tests, do not test framework or library behavior, and do not duplicate an assertion that is already covered at another layer for the same scenario.

   **Check D - Guideline conformance.** If project quality/testing guidelines were listed under "Guidelines found" in the plan's `## Gate Check Commands`, verify this slice's tests conform to them (naming conventions, file locations, coverage thresholds, etc.). Note the guideline file followed.

   **Bound:** Tests prove the work; they do not expand it. Thoroughness is scoped to the feature + plan. Repo depth is a floor (never less thorough than existing tests for the same layer); the plan is the ceiling. Do not invent requirements or tests that have no plan anchor.

   **Anti-patterns - known verification cheats (treat any of these as an automatic Check failure):**

   | Anti-pattern | Why it fails |
   | ------------ | ------------ |
   | Committing before the gate check passes | Skips the deterministic verifier - the gate is not optional |
   | Asserting call count / spy invocation instead of the resulting state | Proves the method ran, not that it did the right thing |
   | Marking a criterion covered without a `file:line` citation | Violates evidence-or-zero; suspicion of coverage is not coverage |
   | Weakening an assertion (making it less specific) to force a pass | Moves the goalposts instead of fixing the code |
   | Deleting or skipping a test to make the suite pass | Destroys coverage permanently; a failing test is a signal, not noise |
   | "Tested elsewhere" deferral without citing where | Coverage gaps hide behind vague claims; cite the file:line or it doesn't count |
   | Speculative "what if" tests with no spec anchor | Expands scope beyond the ceiling; remove them in Check C |
   | Testing framework or library behavior | Tests a dependency, not the feature; remove them in Check C |

   **On any failure** → rewrite or remove the affected test(s), re-run the gate, then re-run this review.

   *Honest caveat:* This is an inspection-based review (model judgment), complementary to - not a replacement for - the deterministic gate. The gate confirms the test suite runs; the Verifier's discrimination sensor confirms the tests can detect regressions. This review confirms the suite is meaningful and bounded.

   Add the two mapping tables and a one-line adequacy verdict under that slice in checks.md.

## What is fixed and what is yours

Fixed: the checks and the proofs each check names. Changing them is renegotiation with the user.

Yours: order, decomposition, where files go, naming, error shapes, helpers. The repo's conventions answer most of it.

In `plan.md`, `Landing`, `Surface` and the stored shape are additive: a door found mid-build gets a row, and a row the user approved is not rewritten. The path and `Changes underneath` in `Shape` are kept true: take a different path and change the hop in that commit. A fifth module in a feature scoped to two means the boundary was wrong; say so.

## Tests come from the checks

Write each test from the check's claim and its concrete value, not from the implementation. Where the approved proof is a test, work one criterion at a time: write its test, run it and see it fail, implement it and see it pass, then move to the next criterion. Observe the intended missing behavior before production changes; an import or environment error is not that RED. A proof still red after implementation blocks review and commit; follow gate failure recovery above. If a check or an approved `Landing` row turns out wrong or unbuildable, renegotiate with the user. Extra tests are welcome.

When the shape of a module's interface is itself in question (how deep the module is, where the seam belongs, what the interface should expose), read [codebase-design](../../spec-plan/references/skills/codebase-design/SKILL.md) for the vocabulary. It is the shared source of the module, interface, depth, seam, adapter, leverage and locality terms, and it is a reference to consult, not a session to run.

**HARD CONSTRAINTS (test integrity - never violate):**

- Do NOT weaken assertions (making them less specific to pass more easily)
- Do NOT delete or skip test cases
- Do NOT use the test framework's skip/disable/pending mechanism to bypass failing tests

A test changes only with the claim it proves, and leaves with the code it proves, in the same commit. Changing a test to make a suite pass hides the failure it exists to show: a wrong check is a stop-and-ask.

So: when an existing test fails because the approved `plan.md` changed the behavior it checks (a criterion that replaces the old behavior), update that test in the same commit as the code, asserting the new plan-defined outcome with the same strength, and cite that criterion in the commit body. If a test seems wrong for any other reason, STOP and ask the user before modifying it. Never silently change a test.

## A door found mid-build

Decide it yourself, then append the row to `Landing` with its literal shape and the rejected alternative before the code that closes it, in that code's commit. Written afterwards, it becomes a justification. A new door that contradicts nothing approved does not stop the build.

## Commit

Follow the repo's commit convention. Where it has none, use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) and validate each message:

```bash
python3 <implementar>/scripts/check_commit.py --message "feat(billing): suspend on failed charge"
```

When a slice's proofs are green, mark its checks complete in `checks.md`, and commit `.specs/` with the slice when the repo tracks it. No Co-Authored-By, Made-with or other agent trailer unless the repo asks for one.

Each slice gets its own commit immediately after verification. Never batch multiple slices into one commit.

## How to write the code

Surgical: do not improve adjacent code or formatting, and remove only what your change orphaned.

## Scope

Outside the plan's scope, do not touch it: surface a bug, note an improvement. Inside it, nothing is missing: what a control needs to work for real is the work even when no check names it. Pushes and deploys: [core.md](../../spec-plan/references/core.md) rule 8.

## Before you stop (features with a screen)

Green proofs do not show that a person can do what the plan promised, or that the screen looks like what was asked for. Open the running app and do what the plan promises as the user would, screens that share the state you changed included. If you cannot reach the app, hand the steps to the user.

A state a capture draws must match the capture except for what `## Differences from the source` lists; the Verifier photographs and judges it ([verify.md](verify.md), step 6b). A `walk` check is a visit you name in the `**Walked:**` line, which also says how the user reaches each state.

Something broken that a check covers is a red proof you missed: fix it. Something broken that no check covers is a missing obligation: append a check with its proof, say so, then fix it. A difference from a capture is fixed, not turned into a check.

## Then stop

What the user settles while you build goes on the `**Settled mid-build:**` line in the turn they say it, in their words - a compaction drops the chat, not the file. When you stop, append to `## Handoff` in `checks.md`: boundary, what was abandoned, the walk. Report checks closed, commit hashes, proof results and deviations.

Run `python3 <spec-plan>/scripts/check_proofs.py <feature>`; a red row goes back to the build. Then, if you hold the whole feature, enter the local `/build-review`: it dispatches the fresh Verifier ([verify.md](verify.md)), who also takes the screen photos, and fresh Standards/Spec roles. Record each on the `**Dispatched:**` line with the `HEAD` before sending and mark `returned` when back. When all dispatched roles have returned, fix their findings within the approved scope, then rerun `check_proofs.py`. A code fix increments `**Fixes**` in verification.md and requires a new, fresh Verifier at the corrected `HEAD`; preserve earlier findings and closure commits as in [verify.md](verify.md). After three code fix-to-review iterations, remaining failures go to the user instead of another fix. Evidence-only changes do not require a new code review. Close only when every dispatched sub-agent has returned and the gate passes; open the report with its last line.
