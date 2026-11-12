# Credits and licenses


This skill adapts **tlc-spec-driven v3.3.0**, authored by **Felipe Rodrigues ([felipfr](https://github.com/felipfr))**, from **Tech Leads Club**, under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). [Original source](https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills/%28development%29/tlc-spec-driven). `references/specify.md` step 3b adds part of tlc-spec-lean v2.2.0, same source and license.


The Checks/Proof/Coverage integration copies tlc-spec-lean v2.2.0's four proof scripts and checks reference, and the test-selection/judgement passages from tlc-spec-driven v4.1.0 (source commit 5929de5cd34f8cca03f3745265571f07b80c9106), same author and CC BY 4.0 license. Adaptations only connect the installed skills, spec.md/validation.md and User Stories, the single approval, three fix/re-verify rounds, explicit refusals, persisted no-tasks records and approved non-test verification. TLC's own code-freshness helper is also used for the mandatory renewed code review, allowing evidence-only commits but rejecting changed code. Existing gates, sensor, reviewers and photo rules remain.

It also incorporates material from **Matt Pocock's** skills (grilling, implement-spec and issue-tracker-github) in [mattpocock/skills](https://github.com/mattpocock/skills), under the **MIT License**, Copyright (c) 2026 Matt Pocock.

Changes from the sources: the TLC workflow was split into `spec-plan`, `implementar` and `build-review`; instructions and cross-references were adapted to connect the three skills; Matt Pocock's material was integrated into the corresponding stages. This adapted skill is not an unchanged upstream copy.

See [LICENSE](LICENSE) for attribution and license notices for both sources.

Integration correction (2026-11-01): binding-source production, source differences and the screen inventory/viewport instructions are copied from tlc-spec-driven v4.1.0 at commit 5929de5cd34f8cca03f3745265571f07b80c9106. Local adaptations preserve one plan approval, independent mandatory photos at three widths, and a complete fresh review after every fix. The Lean proof selector is corrected to require the complete passing line rather than scattered words; capture/criterion identity is adapted to repeated AC numbering in User Stories and Small flat criteria, including wrapped paths. These corrections are not unchanged upstream copies.

Embedded skills (2026-11-12): `references/skills/` holds codebase-design, improve-codebase-architecture and domain-modeling, adapted from [mattpocock/skills](https://github.com/mattpocock/skills), commit 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d, MIT License, Copyright (c) 2026 Matt Pocock. Adaptations: codebase-design leaves out DESIGN-IT-TWICE.md; improve-codebase-architecture keeps only its Explore step; domain-modeling leaves out its ADR part; the copies point to each other's local folders, to `.specs/STATE.md` for decisions, and to plain words for the user. `implementar/references/build.md` carries one paragraph adapted from tdd in the same commit.
