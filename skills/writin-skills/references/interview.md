# Interview Before Writing

What to settle with the user before the first baseline scenario. A skill written from a guessed need tests the wrong thing; these answers become the test material.

## Start from what's already there

If the conversation already contains the workflow ("turn this into a skill"), extract first: the tools used, the order of steps, the corrections the user made, the input and output formats. Then ask only about the gaps, and have the user confirm what you extracted.

## What to find out

Ask one area at a time, conversationally — never a dump of every question at once. When the user is vague, propose a concrete version they can react to ("Would something like X work?"); refining a proposal is easier than describing a need from scratch.

1. **The job.** What should the skill make consistent? Get a concrete example of how it's done today, step by step.
2. **What goes wrong without it.** Forgotten steps, inconsistent output, re-explaining every time, wrong results. This is what the baseline must show failing.
3. **Who uses it and where.** Just the user, a team, other people's machines? Which tools or MCP servers are involved, and are they always available?
4. **2-3 real use cases**, each written as:
   ```
   Use case: [name]
   Trigger: what the user says or does
   Steps: the sequence of actions
   Tools: built-in or MCP
   Result: what success looks like, concretely
   ```
5. **When it should and should NOT trigger.** Phrases the user would really say, and nearby requests that belong to something else (a neighbor skill, a one-off answer).
6. **What a good result looks like.** Concrete enough to check, and how many back-and-forths it should take.

## Where the answers go

| Answer | Becomes |
|---|---|
| What goes wrong without it + use cases | Baseline (RED) scenarios |
| Should / should-not trigger phrases | The description's "Use when" and "Do NOT use for" (see [description.md](description.md)) |
| What a good result looks like | GREEN pass condition |
| Tools and their availability | Failure scenarios and the skill's failure handling (see [skill-format.md](skill-format.md)) |

## When not to build a skill

If a plain instruction (a CLAUDE.md line, a project rule) or a one-off prompt solves it, say so. Not everything needs to be a skill.

## When you can't ask

If the user isn't available to answer, write the open questions down, state the assumptions you'd make, and stop before writing the skill if any answer would change its design.
