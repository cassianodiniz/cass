# Independent Review

Read this after the existing Quality Checks, before Deployment, for a new skill or an edit that changes behavior: triggers, instructions, workflow, permissions or expected output. Spelling, formatting and equivalent wording changes are mechanical; mark this check N/A when behavior is unchanged. Keep the existing tests, versions and repetition policy.

## Dispatch in a fresh context

The author freezes the candidate using the existing Versions mechanism and gives one independent reviewer:

- The user's request and accepted decisions, including scope and success criteria.
- The frozen candidate; for an edit, the previous version and diff.
- Relevant source material and version-linked test artifacts needed to check the result.

Use an available subagent or equivalent independent context without the author's conversation history, verdict or proposed answers. Select a context-isolation option actually supported by the host; do not assume a history-inheriting fork is independent. Read supporting files when relevant to the request. If an independent context is unavailable, report review pending rather than substituting the author's self-review.

Give the reviewer this instruction, with the paths and request filled in:

```text
Review the frozen candidate against the user's request and accepted decisions.
Check whether the result meets those requirements, whether the instructions
are coherent, and whether the changes stay within scope. Preserve the existing
structure unless the request requires a change. Read relevant supporting files.
You review and return a report to the author; you do not edit or publish files.

For each finding, cite candidate file:line, the version examined and the
requirement or source that supports it. Explain the consequence and smallest
necessary correction. Distinguish textual contradiction, hypothesis and
reproduced failure. Cite test artifacts for reproduced failures; never claim
that reading proves behavior or that unexecuted tests passed. Note requirements
met, unresolved findings and evidence gaps. Recommendations outside the request
remain optional and do not block it. Return the complete report to the author.
```

The reviewer uses the supplied artifacts for this pass. Behavioral tests are a separate step under the existing testing workflow; review does not silently launch another campaign. This isolates history, not the candidate's identity: do not claim an anonymous A/B comparison.

## Return to the author

Save the complete report with the candidate's version identifier. The author checks each finding against its evidence and the accepted scope; record accepted corrections and reasons for rejecting unsupported findings. Extra scope requires a user decision.

If no supported in-scope correction is needed, continue to the existing delivery with the report and its limits. A review alone does not require repeating successful tests.

For a supported in-scope finding, return to the existing **Write / Adjust** step and make only the necessary correction. Freeze the corrected version and record the before/after. An edited candidate does not inherit the previous review verdict or affected test results.

## Offer affected tests after correction

Show what changed, which results remain reusable under the existing Versions rules, and which tests or regressions are affected. Keep the existing scenarios and repetition policy.

- If the new round is already authorized, run it without asking again.
- If it is not authorized, ask whether the user wants to run those affected tests on the new frozen version.
- If the user defers, deliver the draft as **corrected; validation pending**, naming the pending cases. Actions that need this evidence remain pending.

Save fresh results against the corrected version. Reconfirm the affected review findings before declaring review complete; use independent review again when the correction invalidates its verdict. If tests fail, return to the existing adjustment step within the authorized round. Do not start unbounded new review/test rounds: finish the authorized pass, report unresolved findings and offer the next affected round. Do not substitute review approval for behavioral validation or claim missing evidence as a pass.
