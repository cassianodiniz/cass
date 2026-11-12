---
name: spec-plan
description: Use when the user invokes /spec-plan, $spec-plan or @spec-plan to turn an idea or change that is not yet settled into an approved feature plan. Do not use when the work is already decided, nor to implement, nor when the user is only thinking aloud.
license: TLC-derived material under CC-BY-4.0; Matt Pocock-derived material under MIT. See LICENSE and source credits in CREDITS.md.
---

# Spec Plan

## Feature contract

Choose from the user-approved work and git, not from a filename alone. Use the approved `plan.md`; when checks exist, their `Plan:` points to that plan. Without a plan, use the approved checks-only `Intent`. If the artifacts claim different authorities or approval is unclear, ask before proceeding. Never invent or reuse a yes to resolve it.

The shared [core.md](references/core.md) lists each phase's reference and where each script lives, while project artifacts stay under `.specs/`. Return to the invoking role after choosing the contract; reading this section does not start Plan.

## Project vocabulary

Before planning, follow the project's documentation pointers to its glossary. Use GLOSSARY-MAP.md to locate the relevant glossary when present; otherwise read root GLOSSARY.md. If neither exists, continue.

During clarification, compare domain terms with the glossary and code, as [domain-modeling](references/skills/domain-modeling/SKILL.md) describes. Resolve conflicting meanings with the user. Record agreed project-specific terms as short definitions, with synonyms to avoid. Create a glossary only when the first term is resolved, following the project's layout or defaulting to root GLOSSARY.md. Use that vocabulary in plan.md and checks.md.

## Plan

Read the shared [core.md](references/core.md) and follow [Plan](references/plan.md). Use plan.md and checks.md; do not create spec, design or tasks files.

**Conversation.** Ask in rounds, as in [investigate.md](references/investigate.md): the whole frontier of open questions in one round, each with your recommended answer.

**Language.** Write every message to the user in portuguese, in plain words; put each technical question in lay terms, with your recommendation and why.

**The one yes.** Ask for it with [approval-message.md](references/approval-message.md).

**Publishing on the yes.** On the yes, record `**Approved**: <YYYY-MM-DD> - user: "<their words>"` in plan.md (checks.md when there is no plan), using the actual reply, then publish. Its approval message names every action below, so that yes is the explicit go-ahead for them. In this order:
1. Create the feature branch from the current main. Commit the feature folder and any change to `.specs/STATE.md`, and push the branch.
2. Create the feature's issue with [issue-tracker-github.md](references/issue-tracker-github.md). Title: the feature name. Body: only the link to the feature folder on the branch. The issue is a card: it never copies the plan or the progress.
3. Open a draft PR after the commit in step 1 above (a branch with no commits ahead of main can't open one), marked as closing the feature's issue. The PR body is the plan's `## Shape` Mermaid block plus the link to the feature folder on the branch.
4. Tell the user the PR number and the branch name.

**After publishing.** On its real approval and publishing, continue to `/implementar`, or `/gpt-implementar` when the user chose Codex. When the user chose to only publish, stop after publishing and build nothing.
