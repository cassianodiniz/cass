---
name: implementar
description: Use when the user invokes /implementar, $implementar or @implementar, or when /spec-plan starts it after the final yes, or when /build-review hands back approved fix tasks, to build a feature already approved in `.specs/features/`. Not for deciding what to build.
license: TLC-derived material under CC-BY-4.0; Matt Pocock-derived material under MIT. See LICENSE and source credits in CREDITS.md.
---

# Implementar

Read only [Feature contract](../spec-plan/SKILL.md#feature-contract) to choose the approved contract; this does not start planning.

Read the shared [core.md](../spec-plan/references/core.md), then [Checks](../spec-plan/references/checks.md) and [Build](references/build.md). Continue the approved feature with their artifacts and rules.

Before writing code, follow “Project vocabulary” in [Spec Plan](../spec-plan/SKILL.md). Use its definitions in check and test descriptions, and include its path in any delegated-worker brief. If absent, record that absence instead of inventing a path.

**One slice at a time.** Never in parallel. After each slice's commit, go on to the next slice without asking. One atomic commit per slice. Mark its checks complete in `checks.md` **before** that commit, and include those updates in the same commit. Never batch slices; never weaken, skip, or delete tests to make them pass.

**Delegation.** When delegating construction or approved repairs, read [Delegation](references/delegation.md) completely before dispatch and apply its brief, return, reconciliation and stop contract. This applies to native workers and the Codex adapter; it does not impose delegation, tasks, phases or batches.

**Verification.** When the feature is ready for verification, start `/build-review`; it dispatches the independent roles required by the shared core. Do not finish at the last commit.

Keep the user's language in the conversation.

## Context before asking for a decision

Before asking the user, present:

1. **Context**: What behavior the feature must provide, what failed, and the evidence supporting the diagnosis.
2. **Proposed change**: What you recommend changing, why it follows the approved requirement, and the practical impact on the user.
3. **Decision**: Your recommendation, the consequence of each choice, and the exact scope of the requested approval. Use plain language for someone who does not program. When using a question panel, include this context in the question itself. Ask about the current correction and any authorization for future changes separately.
