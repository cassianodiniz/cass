# Changing an existing skill

An existing skill already shapes behaviour, so a change is judged against what it does today, not against an empty page.

## Steps

1. **Read today's text and today's diff.** Read every file the change touches, and the skill's git diff since the last tested version. Done when each behaviour that changes is listed with its file and line.
2. **Compare each proposed edit with what the skill already says.** An edit that repeats an existing rule is dropped, and the user is told which rule already covers it.
3. **Write the smallest edit.** Start from the original sentence. When the user applies the change by hand, follow [change-guide-page.md](change-guide-page.md).
4. **Test on the ladder below.**
5. **Report** per scenario: passes out of runs for each version, the model used, and what the level you stopped at does not prove.

## The ladder

Every change starts at level 1, the cheapest. Go to level 2 only when level 1 passed and the change depends on what level 1 cannot prove. A fix for a failed scenario is retested at the level where it failed, on the failing scenarios only.

| Level | What runs | Proves | Does not prove |
| --- | --- | --- | --- |
| 1. Reading | The micro-test in SKILL.md: the manual pasted in full, a written situation, one question | The new text is read as intended | What the agent does with tools, under a full context |
| 2. Work in a throwaway repo | The agent follows the skill in a fake repo up to a stopping point named in advance | What it explores, asks and would write | The phases after the stopping point |

## Rules for both levels

- **Two frozen versions.** A is the skill before the change, B after. B runs three times per scenario; A runs once, to show the scenario tells them apart.
- **Answer key first.** Write, per scenario, what counts as pass and as fail before the first run.
- **Neutral question.** Ask what the agent does next; never name the behaviour you hope for.
- **Read every answer in full.** Compare a pasted edit against the whole expected file, not against a fragment: a fragment can sit in the wrong place.

Level 2 adds: one scenario with the problem planted and one control without it, and the check is made on the commands the agent ran, not only on its account.

## When a scenario fails

Find the sentence that produces the wrong reading. Test a candidate fix in a copy (version C) on the failing scenarios only, then show the user the fix with its result.
