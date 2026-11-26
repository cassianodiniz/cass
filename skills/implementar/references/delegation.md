# Delegation

You delegate tasks to specialized agents with isolated context. By precisely crafting their instructions and context, you ensure they stay focused and succeed at their task. They should never inherit your session's context or history — you construct exactly what they need. This also preserves your own context for coordination work.

## The Pattern
Prepare a well-defined task and provide it to the agent:
- **Specific scope**
- **Clear goal**
- **Constraints**
- **Expected output**

Do not include connectors, MCP servers, plugins or skills in the request—provide only the context and references necessary for the task. If a task requires something beyond file access or the terminal, stop and state what is missing rather than attempting to improvise.

## Agent Prompt Structure

Good agent prompts are:
1. **Focused** - One clear problem domain
2. **Self-contained** - All context needed to understand the problem
3. **Specific about output** - What should the agent return?

## Common Mistakes

**❌ Too broad:** "Fix all the tests" - agent gets lost
**✅ Specific:** "Fix agent-tool-abort.test.ts" - focused scope

**❌ No context:** "Fix the race condition" - agent doesn't know where
**✅ Context:** Paste the error messages and test names

Use the shared Checks/Build workflow and its artifacts. The coordinator may use the native sub-agents available in its environment; this contract does not prescribe model identity or require delegation for inline work. If the selected mechanism is unavailable, report the concrete blocker; do not silently replace independent review with self-review. The Codex route retains its selected executor, transport and limits in its operator.

## Brief sent to the worker

Include these instructions in the actual dispatch, with absolute paths the worker can open:

- The shared core.md, coding-principles.md and Checks/Build references, plus this contract; the approved plan.md, or approved Intent in checks.md; the feature's checks.md and current C-IDs; design.md and the approved tasks.md, with the worker's batch: whole phases of about 7 tasks, run in order.
- The approved diff base, current code HEAD, project instructions and test/environment/app notes; the project glossary path, or its recorded absence. Recover done/pending from tasks.md and Git on resume.
- The approved `## Gate Check Commands` table (plan.md, or checks.md when there is no plan), with every suite, its command and what it needs running, and the existing `## Test runs` records. Before dispatch, the coordinator starts what those rows need running and confirms it is up.
- For approved repairs: verification.md, separate source reports and their reviewed HEAD, each approved finding's problem, paths, expected proof and actual approval/refusal. Keep check claims fixed; append approved new obligations instead of silently rewriting them.
- The return format below and the stop protocol. Follow the shared TDD and integrity rules; a wrong check is a stop-and-ask, never permission to weaken a test. Do not spawn nested workers.

## Standing instructions (once per brief, not per item)
Before changing anything, read the plan criteria (with amendments), DESIGN.md,
the glossary, AGENTS.md and PROCESS.md for every screen and file you will touch,
including the ones the item does not mention, and use what you find.
Remove what your change leaves unused.
Return a "Choices without a rule" list: every choice that is the user's and the plan did not settle.
An item with such a choice stays open until the user answers.

## Per item, only what the worker cannot find
- the user's decision, when it is not in the plan yet (settled before dispatch);
- the prototype photo the task builds and the screen's prototype HTML: match the photo, except what `## Differences from the source` lists; the plan wins on text, DESIGN.md on sizes and spacing. Do not send the references: the prototype already follows them. A screenshot of a defect from a review shows what must be gone;
- which source wins, when two disagree;
- the expected proof approved for the item; when it is a test, the code change the test must catch, plus the regression test in the neighbouring states and widths, in the same commit.

## Compact return

Append the required Handoff; then return this compact summary, for each check declared settled. Link existing records and actual output instead of creating a parallel report:

- Tasks done and checks settled: task IDs, C-IDs, commit hashes and the tasks.md and checks.md status paths; for a fix, also its verification.md Findings closure.
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

