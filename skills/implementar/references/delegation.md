# Delegation

Use the shared Checks/Build workflow and its artifacts. The coordinator may use the native sub-agents available in its environment; this contract does not prescribe model identity or require delegation for inline work. If the selected mechanism is unavailable, report the concrete blocker; do not silently replace independent review with self-review. The Codex route retains its selected executor, transport and limits in its operator.

## Brief sent to the worker

Include these instructions in the actual dispatch, with absolute paths the worker can open:

- The shared core.md and Checks/Build references, plus this contract; the approved plan.md, or approved Intent in checks.md; the feature's checks.md, current C-IDs and assigned boundary.
- The approved diff base, current code HEAD, project instructions and test/environment/app notes; the project glossary path, or its recorded absence. Recover done/pending from the feature files and Git on resume rather than inventing a new task list.
- The approved `## Gate Check Commands` table (plan.md, or checks.md when there is no plan), with every suite, its command and what it needs running, and the existing `## Test runs` records. Before dispatch, the coordinator starts what those rows need running and confirms it is up.
- For approved repairs: verification.md, separate source reports and their reviewed HEAD, each approved finding's problem, paths, expected proof and actual approval/refusal. Keep check claims fixed; append approved new obligations instead of silently rewriting them.
- The return format below and the stop protocol. Follow the shared TDD and integrity rules; a wrong check is a stop-and-ask, never permission to weaken a test. Do not spawn nested workers.

## Compact return

Append the required Handoff; then return this compact summary, for each check declared settled. Link existing records and actual output instead of creating a parallel report:

- Checks settled: C-IDs, commit hashes and the checks.md status path; for a fix, also its verification.md Findings closure.
- Evidence: per-check links to existing proof/verification records and actual prescribed output; for a test proof, the selected assertion at file:line; for an approved non-test proof, its command/gesture/comparison and observed result. Evidence must apply to the returned code.
- Tests: actual total, passed, failed and skipped counts for each command and scope run, with each skip's reason, before/after comparison and investigated differences. On an approved non-test path, name that proof instead of inventing counts.
- Deviations/blockers: remaining open checks, environment failures, incomplete evidence and any question requiring the coordinator's response.

Do not edit proofs.md manually to fill the summary. A partial return does not close the feature.

## Coordinator reconciliation

The worker's report is not proof.

1. Receive the compact summary and open its check-evidence links.
2. For each check the returned delivery settles, check its commit and actual prescribed proof result; confirm the result applies to the code in that commit. For test proofs, open the cited assertions at their file:line in that commit and compare with the mapped required outcomes. For an approved non-test proof, confirm its command, gesture or comparison and observed result. Include the check IDs, selected assertions or approved non-test evidence and actual output in the existing Handoff reconciliation.
3. Reconcile checks.md and, for a review fix, verification.md Findings closures with those records. Compare counts and scopes with earlier runs; inspect each removed test, weakened assertion, new failure and skip with its justification. A smaller count needs investigation, not automatic rejection; an unchanged count does not establish integrity. Accept only evidence-supported checks and preserve every pending item.
4. If evidence is missing, inconsistent or insufficient, return the affected check to the worker. Follow existing approval rules when a correction requires a user decision.

Use the existing records locally. Receiving a return creates no additional whole-suite rerun; the complete product battery runs in the independent review with skill `build-review`. Honor any project requirement to execute checks outside the worker. This reconciliation does not replace the three independent code roles.

## Stops and decisions

A worker stops and reports when the shared workflow or project requires a user decision, a required capability is absent, or an existing iteration limit is reached. It does not answer for the user. The coordinator presents the question using “Context before asking for a decision” in implementar, records the actual answer in the decision/Findings record, and returns that answer and its scope to the selected worker. Unsettled checks remain open. Do not change executor or extend an iteration bound silently; the Codex operator retains its same-session resume and two-round limit.

