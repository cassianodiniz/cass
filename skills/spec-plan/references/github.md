# GitHub commands

Copied from Matt Pocock, `skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md` (github.com/mattpocock/skills, commit 32165827): the Conventions and, from Wayfinding operations, the Child ticket and Blocking lines, with "map" read as the plan issue. The `gh label create` line is ours: Matt's file has no command to create a label.

Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Create a label** (ours): `gh label create <name>`

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

- **Child ticket**: an issue linked to the plan issue as a GitHub sub-issue (`gh api` on the sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the plan issue body and put `Part of #<plan>` at the top of the child body.
- **Blocking**: GitHub's **native issue dependencies**, the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). GitHub reports `issue_dependencies_summary.blocked_by` (open blockers only, the live gate). Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body.
