# Local review safeguards

These are the local review protections. Read the shared Verify reference completely. This entry never fixes code.

## Tests and independent reviewers

The Verifier, a fresh sub-agent (author ≠ verifier), runs [verify.md](verify.md) steps 1 to 6, then 6b, 9 and 10: it writes `verification.md`, distills the lessons and returns its report. Once all checks are complete, run [code-review.md](../../build-review/references/code-review.md) on the feature branch. The verdict is the Verifier's; the Standards and Spec reports stay separate and only report.

A red suite never stops this dispatch: the Verifier runs the battery itself (verify.md step 4) and reports the red suite as a finding. The red-gate stop in shared Build applies to building, not to this review.

Resolve the shared core's scripts. The builder runs `check_proofs.py <feature>`; the fresh Verifier performs its checks and discrimination sensor. Also run [Standards and Spec](../../build-review/references/code-review.md), in two separate fresh contexts, besides the Verifier. The verdict is the Verifier's; the Standards and Spec reports stay separate and only report. All reports concern the same code HEAD and the same approved feature base.

The fresh Verifier runs the `## Gate Check Commands` table itself at the reviewed HEAD, as shared Verify requires, and records `## Test integrity` in verification.md. A focal proof run, compilation alone or unchanged count cannot stand in for the full product battery. Require a result for every suite in that table. No required check is declared passed when unavailable; distinguish inherited failures and blockers.

Before planning, follow the project's documentation pointers to its glossary. Use GLOSSARY-MAP.md to locate the relevant glossary when present; otherwise read root GLOSSARY.md. If neither exists, continue. Require the Verifier and Spec reviewer to read the relevant glossary and report behavior that conflicts with its approved definitions.

## Screen photos

Skip this step for backend-only or infrastructure work. The independent Verifier runs it, not the author, as step 6b of shared Verify: only after the full product battery and the sensor finish, never at the same time (both use the running app).

1. Start the app locally, already logged in with the project's own test account (from its example or seed files).
2. Take a photo of every screen this feature changed, at 375, 768 and 1280 px wide.
3. When a criterion cites a capture (a model image), also photograph that state at the capture's size and compare it with the capture.
4. Look at every photo before showing it, and note each defect you see.
5. Each defect goes into the Findings index and makes the verdict FAIL, like an issue from the Interactive UAT.
6. Show the photos to the user with the review result, every time, even when Interactive UAT does not run.

After a code fix, the fresh Verifier takes the affected photos again at the corrected HEAD.

- Log in with the project's own test account, from its example or seed files. If there is none, ask the user once and record it in the project.
- If the app does not open, the result is "Não deu para revisar as telas", with the reason, and the PR is not marked ready until the user decides.
- With no browser, record the blocker and do not claim the photos passed.

## Guided test with the user

For a feature with complex user-facing behavior where human judgment matters (UI flows, interaction patterns, visual design), run Interactive UAT with the photos. For backend-only or infrastructure work, automated checks are sufficient.

For each testable deliverable, present one test at a time, with its photos:

```
Test [N]: [Test Name]

Expected: [What should happen - specific and observable]

→ Does this work? Describe what you see.
```

Wait for the user's response. A yes/pass/works/next is pass. A skip/can't test/n/a is recorded as skip, not a fabricated pass. Anything else is an issue: log it verbatim. Write the result under `## Interactive UAT Results` in verification.md. Keep user-facing questions in the user's language.

## One fix plan in the Findings index

For each issue found during UAT, in the photos, by the Verifier, or in the Standards and Spec reports, before proposing its fix:

1. **Diagnose** - Analyze the codebase to find root cause

**Guardrail:** Maximum 3 diagnostic iterations per issue. If root cause isn't found after 3 attempts, flag for human investigation.

Record diagnostic attempts and the root cause/evidence in that item's existing Findings `Evidence` cell; carry its count and any blocker in checks.md `## Handoff` on pause/resume. This diagnostic limit is per issue and remains separate from gate recovery, code fix-to-review and Codex limits.

Every issue from the Verifier, the photos, the guided test and the Standards and Spec reports goes into one fix plan: the existing `## Findings` table of verification.md. Each item names where it came from (Verifier, photos, guided test, Standards or Spec), and items are not reranked across those sources. Keep the two Matt reports separately; this index routes their findings, it does not merge the reports. In the existing `Fix` cell, retain the specific fix, file paths, how to prove it and when it is done. The user approves it item by item, even when the Verifier's verdict is PASS. Record the actual approval alongside that item's fix. An item the user refuses is recorded in `Closed` as `Refused - user: "<their words>"` and no longer counts toward FAIL. Never invent a refusal or substitute a technical priority for a user decision. For a refused sensor survivor, its complete `Fault` cell is copied unchanged into the corresponding `Finding` cell, with a nonempty label unique among both sensor faults and Findings. The gate ignores only surrounding cell whitespace; case, Markdown changes and substring matches do not identify the item. Keep the actual `Killed? = no` and that item's own quoted refusal; another item's refusal cannot settle it.

With the yes, hand the approved fixes to the same selected executor (`/implementar`, or the existing Codex session selected through `/gpt-implementar`). Whoever fixes fills `Closed` with the commit that fixes it and the check that now proves it. Include the source report, affected paths, expected proof and actual approval/refusal in the executor's context. Keep checks.md in sync with approved fixes: cite the existing check, or append a new check for an approved new criterion without rewriting an approved claim.

After each code fix, rerun proofs and this complete local review: a fresh Verifier and fresh Standards and Spec contexts, with prior findings and closing commits as facts, not the author's assessment. Retain the cumulative Fixes count; after three fix-to-review rounds with gaps left, stop and ask the user. The existing Codex two-round limit can stop that executor sooner; it does not grant extra global rounds. Evidence-only .specs changes need current proofs, not a new code review. Never update a reviewer's reviewed HEAD on its behalf.

## Final verdict and release

After the reviewers, photos and applicable guided test return, add their results to verification.md. Any unrefused open issue makes the final `**Verdict**:` FAIL. Before the gate, confirm that all three fresh code roles returned for the current code HEAD, no approved fix remains, and every required photo and applicable UAT result is present. Open the sensor results and reconcile negative Holds with Findings; a script PASS alone does not establish these semantic obligations. Run `python3 <build-review>/scripts/validate_verification.py <feature>` explicitly for this feature. The gate does not mechanically check those Matt reports, photos, UAT or per-item consent; a passing script alone does not replace these checks.

When the review stops before the reviewers run, the verdict is neither PASS nor FAIL: it is "Não deu para revisar", with what was missing and how to get it. A red test is not missing input: the reviewers still run.

On PASS, with no approved fix left, mark an existing draft PR ready for review only with the user's yes. Ask one question: commit verification.md, checks/proofs evidence, the review photos and lessons files, push, and mark the PR ready. That yes covers the applicable actions. If there is no PR, omit the ready action rather than inventing a PR. A prior plan approval or local commit authorization does not authorize push, deploy or other remote actions.

Standards/Spec wording and source attribution are in [code-review.md](../../build-review/references/code-review.md).
