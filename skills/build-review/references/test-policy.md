# Test policy

**Goal:** the repo, not this skill, decides which code must be proven at which level and how
deeply - and says so in writing, so the next agent and the next human inherit the decision
instead of re-deriving it.

## The failure this prevents

A proof may settle a behaviour across layers only when all of these are true:

- it executes the real path through the changed decision rather than replacing it with a mock or
  stub;
- its input isolates the claimed behaviour from alternative causes, and its assertion names the
  value, state or side effect the checklist claims;
- a targeted behaviour-level fault makes that assertion fail, rather than failing earlier in
  setup or for an unrelated reason;
- every outcome-changing branch and entry point in a decision added or touched by the diff, a
  changed contract, binding source or checklist claim has a named discriminating proof.

Crossing a layer is neither proof by itself nor a reason by itself to demand another test. When
the conditions above hold, one proof may settle both the boundary contract and the internal
decision. When one fails, require evidence for that specific gap. An explicit, applicable repo
rule may still require proof at a particular level.

## 1. Does the repo already answer this?

Do not judge whether the repo "has testing docs" - it almost always does, and that impression is
what makes this step never fire. Ask the two questions a policy has to answer, for each layer
this change touches:

1. **Which level proves this code?**
2. **How much of its input space must the proof assert to count?**

If the declaration answers both for every touched layer, follow it and skip the rest of this
file. If either is unanswered for code that decides something, identify the behaviour or branch
the current proofs do not settle and derive rows only for that gap.

A statement answers neither question when it only says **where** tests live or how they are
named, **how** to run them, **how a test is built** (which dependencies are real and which are
doubled), or **that** testing matters. Those are all useful and none of them allocate: they
describe the tests, while a policy has to describe the code. Watch for the third one especially,
because it is the one that looks like an allocation rule: keying the level to whether a test
uses real dependencies decides *how* to write a test, and if you read it as deciding *what
deserves* one, every decision table that touches a real dependency gets routed away from its own
layer and is never enumerated.

## 2. Classify by the shape of the code, never by the name of the layer

Layer names lie. A file named like a service can be a pass-through, and a handler that looks like
plumbing can hold the densest decision table in the change. Classify each candidate on a signal
you can point at.

A candidate is a decision added or touched by the diff, or one whose contract the diff changes.
Touching one branch brings every outcome row of that decision into scope, because precedence can
change across rows. Reading through a separate, unrelated pre-existing decision does not bring it
into scope and does not create a new proof obligation.

**Instrumentation** - the body forwards its arguments to one call, or maps one shape onto another
with no conditional deciding the result. Its correctness is its consumer's problem; a test over
it re-asserts the framework underneath.

**Decision** - anything that changes an outcome. A dispatch over a status, event type or code. A
boundary or validation check. A state transition. A payload assembled conditionally. A mapping
table with more than one row. A guard, a precedence rule, an ordering rule.

Count it and write the number down: decision points added or touched, per file. "Dispatches over
six event types, eleven branch points" is contestable. "Looks like business logic" is not.

Then **name the members, not only the count** - `paused`, `updated`, `deleted`, `trial_will_end`,
other. Those names are what `Coverage` joins each proof against, and a set that only ever exists
as a number cannot be joined at all: the member you left out of the sentence is the one that ends
up with no proof and is never missed.

**The proof follows the behaviour at risk, not automatically the file containing the branch.** A
boundary proof discharges an internal decision only when it meets the four conditions above;
otherwise name the branch, entry point or assertion still missing evidence.

## 3. Derive from the code, not from the current suite

The existing tests set style, location and commands - never the bar. A module with no tests at a
level is evidence about its history, not evidence that its logic needs none; deriving the policy
from the suite you found codifies the gap you were asked to look at.

**Judge the house pattern across the whole repo, not the folder you happen to be changing.** That
folder is the smallest and least reliable sample there is, and reading it as the standard is how
a local gap gets promoted to a rule. Search instead for the closest analogue **by code shape** -
the other state machine, the other dispatcher, the other validator - wherever it lives. When you
find one, cite it in the evidence: a proposal that points at a sibling proven at that level is
precedent, and one that does not is taste.

When the existing suite or an existing rule contradicts what you propose, say so in one line.
That contradiction is information for the user, not a reason to lower the proposal.

## 4. Propose

Present it with the checklist - one place, not two. It goes in the artifact as a
`## Test policy` section immediately before `## Checks`, because every proof below depends on the
rows above. Use the repo's own level names, locations and commands; invent none.

```markdown
## Test policy (proposed - the repo does not declare this)

| Code | Required proofs | Coverage expectation |
| --- | --- | --- |
| Decides, and is reached across a boundary | proof(s) meeting the four conditions above; one proof may settle boundary and decision | every required outcome-changing row has a named discriminating assertion; fault injection follows the Verifier's distinct assertion surfaces and limit |
| Decides, not reached across a boundary | one at its own layer | one asserted case per row of the decision table |
| Entry point or adapter that decides nothing | one at the boundary | accepted input, each rejected input, each error path |
| Instrumentation, pass-throughs | none of its own | covered by its consumer's proof |

Evidence:
- <file>: dispatches over <n> cases, <n> branch points -> decides
- <file>: forwards a single call, no conditional -> instrumentation
- <existing declaration> decides <what it decides> and leaves the two questions open
- closest analogue in the repo: <file>, same shape, already proven at this level with <n> cases
- the module has <n> proofs at this level today, which the table deliberately does not match

Cost: <n> additional proofs for <behaviours or branches the current evidence does not settle>,
across <n> files. Without these rows, the named gap can remain wrong while every proof stays green.
```

A floor, never a ceiling, and a target rather than a description of what exists today. State the
cost in the proposal - a row set nobody can price is a governance debate, and a row set with a
number next to it is a five-second decision.

## 5. Ask, then write

**One question, not a menu.** The rows you derived are the default you build under: state them
and keep going. Offering a choice between allocation philosophies hands back the analysis this
step exists to do, and the option that always looks like the conservative one - prove everything
at the boundary, the way the repo already does - is level substitution wearing a hat.

So the only explicit question is the narrow one: **do these rows go into the repo's guidelines?**
Building under them is reversible and needs no permission. Writing them is not: project
guidelines reach every future agent and every human in the repo, a wider blast radius than the
feature you were asked to build, so approved rows go in their own commit, before the build
starts, and never ride along in a feature commit.

Ask it in one line, with both outcomes stated, so silence is not ambiguous. Adapt the names, keep
the shape:

> These rows are the bar I build under - approving the checklist is enough for that. Writing them
> into `<guidelines file>` needs an explicit yes, and it lands as its own commit before the build.
> Without one I build under them and leave the file alone.

Then stop asking. The answer settles it for this feature, and rule 4 keeps the rows fixed from
that point on.

**Fix what misleads, do not just add to it.** If an existing line is being read as an allocation
rule and is not one, leaving it in place means the next run re-derives the same wrong answer and
the Verifier defers to it. Quote the line, say what it actually decides, and propose the edit that
scopes it - as part of the same approval, in the same commit as the new rows.

If the user does not answer, do not write. Carry the proposal inside the checklist as a stated
assumption, build under it, and leave the files alone - a policy nobody agreed to is worse than
no policy, for exactly the reason above.
