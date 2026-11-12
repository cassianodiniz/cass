# Change guide page

A **change guide page** is one page the user works from to apply a skill change by hand: every edit, where it goes, what leaves and what enters. The user pastes; you never edit the skill. The user here does not program and reads one edit at a time.

## Steps

1. **Read the current text and name the behaviour.** Read every file the change touches, at its current state. Say, in the user's language, what the skill does today and what it will do after. Done when each claim cites a file and line of the current version.

2. **Write the edit list.** One entry per edit: file, find text, replace text (empty for a deletion), kind (essential, recommended, optional), a before/after description, and a translation of both texts. Follow the edit rules below. Done when every entry has all six fields.

3. **Check what depends on the removed text.** Search scripts, templates, fixtures and the other skills for every name, section and column the edits remove. Done when each search and its result is listed for the user.

4. **Prove the list against the files.** Each find text occurs exactly once in its file. Apply the whole list to a throwaway copy and diff it against the original. Done when the diff shows only the intended lines.

5. **Build the page** with the layout below and publish it.

6. **Recheck on every request.** When the user says they pasted something, or asks what is left, read the files again and recompute every edit's state by comparing the current line with the expected final line. Republish at the same address. Done when every edit is in exactly one state and every difference from the expected text is shown.

7. **Report.** State what was verified (text matches, scripts still run) and what was not (no agent was run with the new text).

## Edit rules

- **Start from the original sentence.** Change only the words that carry the exception. A new sentence is the last resort, and is labelled as new.
- **Undo means the original, word for word**, taken from git, never retyped.
- **Smallest set.** Essential edits are the ones without which the old behaviour remains. Everything else is recommended or optional and is labelled so.
- **One meaning per edit.** If the same rule is written in several files, each file gets its own edit, and each description names its own file and behaviour.

## Description of an edit

Write `Before: … After: …` in the user's language. Name the manual by what it is for and state the behaviour, so the description stands alone. The reader has not read the other edits.

- Weak: "The same photo change, in the other manual that repeats the rule."
- Strong: "Before: the review safeguards manual said the screen photos are taken only if every test passes; on a failure they wait for the next round. After: the photos are taken in the same review, even with a failing test."

## Page layout

Order: grouped by skill file; inside each file, essential first, then recommended, then optional.

Top of the page:
- three steps on how to use it, and what stays as it is;
- three filter rows, label on the left and buttons starting on the same column: **Status** (all, to do, done), **File** (all, one per file, with its pending count), **Kind** (all, essential, recommended, optional). The rows combine. When a filter leaves nothing, say so in one line;
- a counter of the pending edits the user has ticked.

Each pending edit is a card:
- number, line number in the current file, manual name and file path, kind badge, and a state badge when it is an undo or a leftover;
- the before/after description;
- where it goes: the sentence right before the text, on the same line or the line above;
- the diff box: what leaves in red, what enters in green, with the changed words inside the sentence in a stronger tone;
- a collapsed translation of the same diff, keeping commands, file names and step names in the original language;
- two copy buttons: the text to find, and the new text;
- a "done" tick, kept in the user's browser.

Done edits stay on the page as a register, collapsed to their header row; opening one shows the same card, so the user can check or undo it later.

Leave out instructions the layout already makes obvious, such as "replace the red with the green".

## States

Computed from the files on every recheck, never from the tick:

| State | Condition |
| --- | --- |
| To do | the find text is in the file and the final text is not |
| Done | the line equals the expected final line |
| Leftover | part of the old text remains, or a word differs from the expected line; show both |
| Undo | the user decided to keep the original and the file still has the changed text |

A tick the user placed hides the card from "to do" at once; the state itself changes only when the file matches.

## When the request comes from an audit

- Order findings by impact on the user's stated problem. A finding that does not reduce that problem stays out.
- Label each claim: what the skill text says, what was seen in a real run, what is deduced.
- Use evidence from the current version of the skill only. Records from before a rewrite describe another skill.
- A situation that has not happened is a hypothesis; say so, and do not build edits on it.
