# Approval message (Lean)

Use this message for the one yes of the Lean plan, which covers plan.md and its Gate Check Commands.

Write the approval message in the user's language, in plain words, for a reader who does not program: they need to understand how the feature works in order to decide well. Tell the feature once, as a story in steps: each fact appears in one place, the step where it happens. How each step is built lives in the document; the message says what changes for the people involved. Keep it to one screen: at most 150 words, the flowchart not counted. When the steps do not fit, keep the ones that touch money, data, people's work or what keeps running; the rest are in the documents (item 8). It is, in this order:

1. **The ask, and how it works when it is done** — open with "I need your yes for this plan" and name the documents it covers. Say that it is built one slice at a time and reviewed once, at the end. Then one or two sentences describing the finished result from the user's side: what happens, to whom, in what order. Right after them, show the plan's `## Shape` sequence diagram drawn in the chat: render that exact Mermaid text with the available drawing tool (the Mermaid library, not a redrawn picture). If no drawing tool is available, show the Mermaid text and say the drawing appears on GitHub. The flowchart does not count toward the word limit.
2. **How I get there, in N steps** — one numbered step per slice of `## Criteria`, in priority order. Each step is one sentence of about 20 words, in the words the people involved would use, stating what that step does to money, data, people's work or what keeps running, when it does — "Postmark, US$ 15 a month", "the old column is deleted for good", "the 212 members start receiving it". Walk through the decisions of the conversation one by one; a decision that appears in no step is a gap: fix the document before showing the message. When work is delegated to subagents, the step says what they do, what they cannot touch, and what their check does not see.
3. **Where I deviated from what you asked, and why** — one line per deviation, quoting the user's words; then one line per assumption that changes what the user gets, with what to tell me if it is wrong. Or "nothing".
4. **Tests** — one line, from `## Gate Check Commands`: how many suites and scripts run at the end, after each fix and in the review, naming the families, and the scripts the general command skips. Do not ask the user to choose tests.
5. **Cost and time** — one line: an estimate, or "I don't know" and why.
6. **What the feature does not cover, and what is still open** — one line each.
7. **Feature size** — plan, or checks-only for a change under roughly three files with no one-way door, with your reason.
8. **Full text** — the document's path, and "ask 'open step N' and I will explain that step here".
9. **Close** — "Approve?" and what a yes does: name each action: the branch name, the commit and push of the feature folder, the issue in `<owner/repo>`, the draft PR, and who builds next. Offer three answers: "sim" publishes and starts `/implementar` (Claude builds), "sim, codex" publishes and starts `/gpt-implementar` (Codex builds), "só publicar" publishes and builds nothing yet.

The message asks once. Treat the user's yes as approval of every document's content, its Gate Check Commands included, and as permission to publish to the destinations shown.

Iterate until the user approves. Before the yes, push nothing and create no issue.
