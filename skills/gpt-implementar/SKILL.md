---
name: gpt-implementar
description: "Use when the user invokes /gpt-implementar (old name /gpt-builder), or answers the final yes of /spec-plan with \"sim, codex\", to build a feature already approved in `.specs/features/` with OpenAI Codex writing the code instead of Claude. Not for work whose spec still needs decisions (/spec-plan first), for reviewing a finished feature (/build-review), or for tasks that need Claude-session tools (MCP, secrets, browser)."
---

# gpt-implementar

Read only [Feature contract](../spec-plan/SKILL.md#feature-contract) to choose the approved
contract; this does not start planning. For a legacy feature, follow [LEGACY.md](LEGACY.md).

For Lean, follow `/implementar` with Codex writing the code. Read the shared
[SKILL.md](../spec-plan/references/tlc-spec-lean/SKILL.md) and its Checks/Build references.
The coordinator uses the existing [Codex operator](references/codex-runner.md); only the context
sent to it changes to the native files. If you are already the dispatched Codex worker, follow
that shared context and return its evidence to the coordinator; do not launch another Codex.
The coordinator starts `/build-review` when the feature reaches verification. Keep the user's
language in the conversation.
