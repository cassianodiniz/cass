---
name: build-review
description: Use when /implementar starts it after the last task of a feature, or when the user invokes /build-review, $build-review or @build-review, to review a finished feature of `.specs/features/` before it goes live. Not for building nor for planning.
license: TLC-derived material under CC-BY-4.0; Matt Pocock-derived material under MIT. See LICENSE and source credits in LEGACY.md.
---

# Build Review

Read only [Feature contract](../spec-plan/SKILL.md#feature-contract) to choose the approved
contract; this does not start planning. For a legacy feature, follow [LEGACY.md](LEGACY.md).

For Lean, read the shared [SKILL.md](../spec-plan/references/tlc-spec-lean/SKILL.md) and
[Verify](../spec-plan/references/tlc-spec-lean/references/verify.md).
Also read [local review safeguards](references/local-review.md) and
[Standards and Spec](references/code-review-lean.md): preserve both fresh Matt contexts beside
the Lean Verifier, the Verifier's photos, applicable UAT, per-item fix decisions and the final yes.
Use their native reports and completion gate; this entry does not fix code. Approved corrections
return to the same selected executor.
Do not require legacy `validation.md` or its gate for a native Lean feature. Keep the user's
language in the conversation.
