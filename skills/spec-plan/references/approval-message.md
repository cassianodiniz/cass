# Approval message

Use this message every time the flow presents a document for the user's yes: the spec, `context.md`, the design or the tasks.

Write the approval message in the user's language, in plain words, for a reader who does not program: they need to understand how the feature works in order to decide well. Tell the feature once, as a story in steps: each fact appears in one place, the step where it happens. How each step is built lives in the document; the message says what changes for the people involved. Aim for 300 to 500 words. It is, in this order:

1. **The ask, and how it works when it is done** — open with "I need your yes for this <spec | context | design | tasks>". Say that the whole feature becomes one PR: the entire spec implemented on a single integration branch; it is built one task at a time and reviewed once, at the end. Then three or four sentences describing the finished result from the user's side: what happens, to whom, in what order.
2. **How I get there, in N steps** — one numbered step per phase of `tasks.md` when it exists; before that, one per user story, in priority order. Each step is one sentence of about 20 words, in the words the people involved would use, stating what that step does to money, data, people's work or what keeps running, when it does — "Postmark, US$ 15 a month", "the old column is deleted for good", "the 212 members start receiving it". Walk through the decisions of the conversation one by one; a decision that appears in no step is a gap: fix the document before showing the message. When work is delegated to subagents, the step says what they do, what they cannot touch, and what their check does not see.
3. **Where I deviated from what you asked, and why** — one line per deviation, quoting the user's words; then one line per assumption that changes what the user gets, with what to tell me if it is wrong. Or "nothing".
4. **Cost and time** — one line: an estimate, or "I don't know" and why.
5. **What the feature does not cover, and what is still open** — one line each.
6. **Feature size** — the scope (Small, Medium, Large or Complex) from the Auto-Sizing table, with your reason, and which documents still need approval. For tasks requested by `/implementar` in the middle of a build, say the size changed from <old> to <new> and why. For the tasks yes, add the result of the checks in step 5 of [tasks.md](tasks.md), in plain words.
7. **Full text** — the document's path, and "ask 'open step N' and I will explain that step here".
8. **Close** — "Approve?" and what a yes does. Before the final yes: "a yes saves <document> and moves to <next document>; nothing leaves your machine". On the final yes, name each action: the branch name, the commit and push of the feature folder, the issue in `<owner/repo>`, the draft PR, and who builds next: "sim" starts `/implementar` (Claude builds), "sim, codex" starts `/gpt-implementar` (Codex builds). For tasks requested by `/implementar` in the middle of a build, name the commit and push of `tasks.md` and that the build then continues.

The message asks once. Treat the user's yes as approval of the document's content and, on the final yes, as permission to publish to the destinations shown.

Iterate until the user approves. Before the final yes, push nothing and create no issue, except when pausing.
