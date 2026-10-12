---
name: spec-plan
description: Use when the user invokes /spec-plan, $spec-plan or @spec-plan to turn an idea or change that is not yet settled into an approved feature plan. Do not use when the work is already decided, nor to implement, nor when the user is only thinking aloud.
license: TLC-derived material under CC-BY-4.0; Matt Pocock-derived material under MIT. See LICENSE and Credits and licenses.
---

# Spec Plan

This skill runs the planning half of the Spec-Driven Development flow below: Specify (with Discuss when it triggers), Design and Tasks, auto-sized by scope. Execute runs in the `/implementar` skill; the Verifier and the final review run in the `/build-review` skill. Never implement the feature here.

**Project vocabulary**
Before planning, follow the project's documentation pointers to its glossary. Use GLOSSARY-MAP.md to locate the relevant glossary when present; otherwise read root GLOSSARY.md. If neither exists, continue.
During clarification, compare domain terms with the glossary and code. Resolve conflicting meanings with the user. Record agreed project-specific terms as short definitions, with synonyms to avoid. Create a glossary only when the first term is resolved, following the project's layout or defaulting to root GLOSSARY.md. Use that vocabulary in the spec, design and tasks.

## How this skill runs the flow

1. **The feature.** The unit of work is one feature: one folder `.specs/features/<feature>/`, one branch, one draft PR and one issue. There are no sub-issues; phases and tasks live in `tasks.md`.
2. **Conversation.** Ask in rounds, as in [investigate.md](references/investigate.md): the whole frontier of open questions in one round, each with your recommended answer. What the conversation settles goes into the documents: decisions into the spec and, when Discuss runs, into `context.md`; assumptions into the spec's Assumptions & Open Questions.
3. **Language.** Write every `.specs/` file in English, in its template's format: the validators check the English section names and a SHALL in every acceptance criterion. Write every message to the user in the user's language, in plain words; put each technical question in lay terms, with your recommendation and why.
4. **One yes per new document.** Every document the flow presents for confirmation or approval gets one yes, asked with [approval-message.md](references/approval-message.md): the spec always; `context.md` when Discuss ran; design and tasks only for Large and Complex. Before the final yes, nothing reaches GitHub, except when pausing (item 7 below): push nothing and create no issue.
5. **Publishing on the final yes.** The final yes is the yes on the last document this feature gets: for Small and Medium, the spec, or `context.md` when Discuss ran; for Large and Complex, the tasks. Its approval message names every action below, so that yes is the explicit go-ahead Critical Rule 5 asks for. In this order:
   1. Create the feature branch from the current main, unless a pause already created it. Commit the feature folder and any change to `.specs/STATE.md`, and push the branch.
   2. Create the feature's issue with [issue-tracker-github.md](references/issue-tracker-github.md). Title: the feature name. Body: only the link to the feature folder on the branch. The issue is a card: it never copies the spec or the progress.
   3. Create the integration branch. Open a draft PR after the commit in step 1 above (a branch with no commits ahead of main can't open one), marked as closing the feature's issue. The integration branch is the feature branch from step 1. If a pause already opened the draft PR, mark that PR as closing the feature's issue instead.
6. **Small scope.** Write the one-liner spec to `spec.md` too, and publish it the same way. Small skips the closure gate (`references/specify.md`, step 4), so it skips `validate_spec.py` too.
7. **Pausing before the final yes.** First create the feature branch if it does not exist yet. Then follow the Pause procedure in [memory.md](references/memory.md); at its step 4, commit the feature folder and `.specs/STATE.md` (do not stash). Ask the user before pushing (Critical Rule 5). With the yes, push and open the draft PR if it is not open yet. The issue still waits for the final yes.
8. **Tasks requested by `/implementar`.** When the `/implementar` skill stops because its step list has more than 5 steps or complex dependencies (Safety valve below), run the Tasks phase in full for that feature: [tasks.md](references/tasks.md), steps 1 to 5 (step 1 reads the design only if it exists), then the tasks yes, then step 6 as in item 9. The approval message for these tasks shows, in its "Feature size" block, that the size changed and why, and names the commit and push of `tasks.md`, so its yes covers that push. This yes is not a final yes: the branch, the issue and the draft PR already exist. Then hand the feature back to `/implementar`.
9. **Then build.** When the feature has `tasks.md`, ask the question of step 6 of [tasks.md](references/tasks.md) right after the tasks yes and before the commit of `tasks.md`, and write the answer into each task's **Tools** field. Right after publishing, start the `/implementar` skill for this feature, without another question.

# Tech Lead's Club - Spec-Driven Development

Plan and implement features with precision. Granular tasks. Clear dependencies. Right tools. Zero ceremony.

```
┌──────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐
│ SPECIFY  │ → │  DESIGN  │ → │  TASKS  │ → │ EXECUTE │
└──────────┘   └──────────┘   └─────────┘   └─────────┘
   required      optional*      optional*     required

* Agent auto-skips when scope doesn't need it
```

## Critical Rules (read before acting)

**Loading this skill's files.** Reference files live under `references/` in this skill's own directory (where this `SKILL.md` resides). Resolve them relative to the skill directory - never the workspace root - and load them through the active skill by name; never assume a fixed install path. When a step tells you to read a reference, **read it completely (to EOF)** before acting - never act on a partial/truncated read.

**Running this skill's scripts.** Every `scripts/*.py` shipped with this skill lives under that same skill directory. Resolve the skill directory first, then invoke `python3 <skill-dir>/scripts/<name>.py ...`. Never run `python3 scripts/...` from the consuming project root - that looks for a project-local `scripts/` tree that is not this skill. Project data under `.specs/` is still read/written relative to the project root (pass `--root` when the cwd is elsewhere). Below, `<skill-dir>` means the directory that contains this `SKILL.md`.

**Execution contract - every task, non-negotiable (holds even if you do not open the reference files):**

1. Tests derive from the spec's acceptance criteria and assert spec-defined outcomes - they never mirror the implementation.
2. The gate must pass (tests pass) before a task is done - the test runner decides, not self-assessment.
3. One atomic commit per task. Mark the task complete in `tasks.md` (and update spec traceability when used) **before** that commit, and include those updates in the same commit. Never batch tasks; never weaken, skip, or delete tests to make them pass.
4. After the LAST task, a fresh **Verifier always runs automatically** (author ≠ verifier) - spec-anchored outcome check + discrimination sensor. It is never optional and never prompted. See the Verifier Sub-Agent in `references/sub-agents.md` of the `/build-review` skill.
5. **Blast radius:** approving a spec or tasks authorizes local implementation and local commits only. `git push`, force-push, deploy, production DB changes, and other remote / externally visible / destructive operations require an explicit go-ahead for that action.

**Deterministic gates run before human review - not from memory.** The structural gates for the spec and tasks are enforced by scripts in this skill's `scripts/` directory, so they cannot silently drift when the model forgets a step:

- Before confirming a spec: `python3 <skill-dir>/scripts/validate_spec.py <spec-path-or-feature>` (closure gate: EARS-shaped ACs, filled assumptions, well-formed requirement IDs, required sections). Small skips it, as it skips the closure gate (`references/specify.md`, step 4).
- Before presenting tasks for approval: `python3 <skill-dir>/scripts/validate_tasks.py <tasks-path-or-feature>` (granularity smell, diagram-vs-`Depends on` parity within a phase, no forward-phase dependency, every task carries `Tests` + `Gate`).
- On each commit: `python3 <skill-dir>/scripts/check_commit.py --message "<msg>"` (Conventional Commits). Optionally wire it as a git `commit-msg` guard (git only, no agent dependency) - see `references/implement.md` in the `/implementar` skill.
- Before declaring a feature done, in the `/build-review` skill: `python3 <skill-dir>/scripts/validate_state.py <feature>` (completion gate: the Verifier's `validation.md` exists, its verdict is filled to PASS, and it cites `file:line` evidence - a missing, FAIL, placeholder, or evidence-free report fails). The closing step of Execute runs this automatically, the same way the lessons layer runs at distillation; it is not a manual step.

A non-zero exit means STOP and fix before proceeding. Skip a script only when no code-execution tool is available; then perform the same checks by reading the artifact.

**Before Execute** (the `/implementar` skill does this step, not this skill): read `references/implement.md` of the `/implementar` skill completely and run `<skill-dir>/scripts/validate_tasks.py`; if a formal `tasks.md` packs into more than one task-budgeted batch (> ~8 tasks), present the sub-agent offer first (see Sub-Agent Delegation in the `/implementar` skill).

## Auto-Sizing: The Core Principle

**The complexity determines the depth, not a fixed pipeline.** Before starting any feature, assess its scope and apply only what's needed:

| Scope       | What                     | Specify                                                 | Design                                          | Tasks                         | Execute                                               |
| ----------- | ------------------------ | ------------------------------------------------------- | ----------------------------------------------- | ----------------------------- | ----------------------------------------------------- |
| **Small**   | ≤3 files, one sentence   | One-liner spec (inline)                                 | Skip                                            | Skip                          | Implement + verify inline                             |
| **Medium**  | Clear feature, <10 tasks | Spec (brief)                                            | Skip - design inline                            | Skip - tasks implicit         | Implement + verify                                    |
| **Large**   | Multi-component feature  | Full spec + requirement IDs                             | Architecture + components                       | Full breakdown + dependencies | Implement + verify per task                           |
| **Complex** | Ambiguity, new domain    | Full spec + [discuss gray areas](references/discuss.md) | [Research](references/design.md) + architecture | Breakdown + phase plan        | Implement + interactive UAT (`/build-review`) |

**Rules:**

- **Specify and Execute are always required** - you always need to know WHAT and DO it
- **Design is skipped** when the change is straightforward (no architectural decisions, no new patterns)
- **Tasks is skipped** when there are ≤3 obvious steps (they become implicit in Execute)
- **Discuss is triggered within Specify** when the agent detects ambiguous gray areas that need user input, or when the feature has any implicit-requirement dimension present (persistence/state, external calls, auth, payments, concurrency, state transitions)
- **Interactive UAT is triggered within Execute** only for user-facing features with complex behavior

**Safety valve:** Even when Tasks is skipped, Execute ALWAYS starts by listing atomic steps inline (see `references/implement.md` in the `/implementar` skill). If that listing reveals >5 steps or complex dependencies, STOP and create a formal `tasks.md` - the Tasks phase was wrongly skipped.

## .specs Structure

```
.specs/
├── STATE.md            # Project memory: Decisions log (AD-NNN) + Handoff snapshot
├── LESSONS.md          # Self-improving lessons playbook (rendered by scripts/lessons.py - do not hand-edit)
├── lessons.json        # Canonical lessons state (machine-owned)
└── features/           # Feature specifications
    └── [feature]/
        ├── spec.md         # Requirements with traceable IDs
        ├── context.md      # User decisions for gray areas (only when discuss is triggered)
        ├── design.md       # Architecture & components (only for Large/Complex)
        ├── tasks.md        # Atomic tasks with verification (only for Large/Complex)
        └── validation.md   # Verifier report: PASS/FAIL, per-AC evidence, sensor result, diff range
```

**Create artifacts lazily.** Write each file only when its phase actually produces content - never scaffold empty `context.md`, `design.md`, or `tasks.md` up front. An empty file signals a phase happened when it did not; absence is the correct state for a skipped phase. The deterministic validators (`scripts/validate_spec.py`, `scripts/validate_tasks.py` and `scripts/check_commit.py` here, `scripts/validate_state.py` in the `/build-review` skill) ship inside each skill's own `scripts/` directory; this skill also ships `lessons.py`.

## Workflow

**New feature:**

1. Specify → (Design) → (Tasks) → Execute (depth auto-sized)

**Resume work:**

1. Read `.specs/STATE.md` (Handoff + Decisions).
2. Reconcile Handoff against git (`branch`, `status --porcelain`, recent commits) and `tasks.md` - evidence wins over a stale snapshot. Full procedure: [memory.md](references/memory.md).
3. Propose the reconciled next step before writing code.

## Context Loading Strategy

**On-demand load (only what the current task needs):**

- `.specs/STATE.md` - Decisions section (read at Design, re-read on resume); Handoff section (read on resume only)
- confirmed lessons - load at Specify and Design via `python3 <skill-dir>/scripts/lessons.py list --status confirmed` ([lessons.md](references/lessons.md)); confirmed only, never candidates
- spec.md (when working on a specific feature)
- context.md (when designing or implementing from user decisions)
- design.md (when implementing from design)
- tasks.md (when executing tasks)

**Never load simultaneously:**

- Multiple feature specs
- Multiple architecture docs

**Target:** <40k tokens total context
**Reserve:** 160k+ tokens for work, reasoning, outputs
**Monitoring:** Display status when >40k (see [context-limits.md](references/context-limits.md))

## Commands

**Feature-level (auto-sized):**
| Trigger Pattern | Reference |
|----------------|-----------|
| Specify feature, define requirements | [specify.md](references/specify.md) |
| Discuss feature, capture context, how should this work | [discuss.md](references/discuss.md) |
| Design feature, architecture | [design.md](references/design.md) |
| Break into tasks, create tasks | [tasks.md](references/tasks.md) |
| Implement task, build, execute | the `/implementar` skill |
| Validate, verify, test, UAT, walk me through it | the `/build-review` skill |

**Memory:**
| Trigger Pattern | Reference |
|----------------|-----------|
| Record decision, this is a project-level decision | [memory.md](references/memory.md) |
| Pause work, end session, I need to stop | [memory.md](references/memory.md) |
| Resume work, continue, pick up where we left off | [memory.md](references/memory.md) |
| Load lessons, what have we learned, apply past lessons | [lessons.md](references/lessons.md) |
| Record lesson, distill lessons (auto-runs after validation) | the `/build-review` skill |

## Knowledge Verification Chain

When researching, designing, or making any technical decision, follow this chain in strict order. Never skip steps.

```
Step 1: Codebase → check existing code, conventions, and patterns already in use
Step 2: Project docs → README, docs/, inline comments, `.specs/STATE.md` (Decisions)
Step 3: Context7 MCP → resolve library ID, then query for current API/patterns
Step 4: Web search → official docs, reputable sources, community patterns
Step 5: Flag as uncertain → "I'm not certain about X - here's my reasoning, but verify"
```

**Rules:**

- Never skip to Step 5 if Steps 1-4 are available
- Step 5 is ALWAYS flagged as uncertain - never presented as fact
- **NEVER assume or fabricate.** If you cannot find an answer, say "I don't know" or "I couldn't find documentation for this". Inventing APIs, patterns, or behaviors causes cascading failures across design → tasks → implementation. Uncertainty is always preferable to fabrication.

## Output Behavior

**Do the work; do not narrate the machinery.** Produce the right artifact for the phase instead of announcing the phase ("I will now run the Specify phase"). The user judges the output, not a play-by-play of the process. This keeps the flow from reading as robotic.

**Match effort to the work.** Lightweight steps (feature-level checks, validation, mechanical tasks) do not need top-tier reasoning; heavy steps (complex design, ambiguous features) do. If the harness lets you pick a model per sub-agent, apply the tier rubric in `references/sub-agents.md` of the `/implementar` and `/build-review` skills; otherwise proceed and simply invest more care on the heavy steps. Mention this once per session at most, and only if it helps; skip it for an experienced user.

**Write generated artifacts in a plain, decided voice.** Specs, ADRs, validation reports, commit messages, and chat summaries follow the writing rules in [coding-principles.md](references/coding-principles.md): lead with the verdict, state decisions definitively, cut filler and mechanical hedging.

## Code Analysis

Use available tools with graceful degradation. See [code-analysis.md](references/code-analysis.md).

## Credits and licenses

This skill adapts **tlc-spec-driven v3.3.0**, authored by **Felipe Rodrigues ([felipfr](https://github.com/felipfr))**, from **Tech Leads Club**, under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). [Original source](https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills/%28development%29/tlc-spec-driven).

It also incorporates material from **Matt Pocock's** skills (grilling, implement-spec and issue-tracker-github) in [mattpocock/skills](https://github.com/mattpocock/skills), under the **MIT License**, Copyright (c) 2026 Matt Pocock.

Changes from the sources: the TLC workflow was split into `spec-plan`, `implementar` and `build-review`; instructions and cross-references were adapted to connect the three skills; Matt Pocock's material was integrated into the corresponding stages. This adapted skill is not an unchanged upstream copy.

See [LICENSE](LICENSE) for attribution and license notices for both sources.
