# Dunning on failed charge - tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `implementar` skill, or `gpt-implementar` when the user chose Codex: **activate it by name and follow its Build flow.**

---

**Plan**: `.specs/features/billing/plan.md`
**Design**: `.specs/features/billing/design.md`
**Checks**: `.specs/features/billing/checks.md`
**Status**: Draft

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and plan - confirm before Execute. Guidelines found: none - strong defaults applied.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Domain (`app/billing`) | unit | All branches; 1:1 to plan criteria | `test/billing/*_test.rb` | `bin/rails test test/billing` |
| Webhook route | integration | Happy + every listed edge + error paths | `test/webhooks/*_test.rb` | `bin/rails test test/webhooks` |
| Migration | none | build gate only | - | build gate only |

---

## Execution Plan

### Phase 1: Foundation

```
T1 → T2 → T3 → T4
```

---

## Task Breakdown

### T1: Add `suspended` to the subscription status

**What**: Migration adding the `suspended` enum value, existing rows backfilled to `active`
**Where**: `db/migrate/20261101_add_suspended_status.rb`
**Depends on**: None
**Reuses**: `db/migrate/20260301_add_trialing_status.rb` pattern
**Requirement**: S1 criterion 1 - C1

**Done when**:

- [ ] Migration runs and rolls back
- [ ] Gate check passes: `bin/rubocop app/billing`

**Tests**: none
**Gate**: build

---

### T2: Map provider statuses

**What**: `Billing::StatusMap` maps each provider status to one local status
**Where**: `app/billing/status_map.rb`
**Depends on**: T1
**Reuses**: `app/billing/subscription.rb` status constants
**Requirement**: S1 criteria 1-2 - C1, C2, C3

**Done when**:

- [ ] Every provider status maps once; an unknown one records `billing.status_unmapped`
- [ ] Gate check passes: `bin/rails test test/billing`

**Tests**: unit
**Gate**: quick

---

### T3: Apply the transition

**What**: `Billing::Subscription` applies the mapped status and rejects `Suspended` to `Trialing`
**Where**: `app/billing/subscription.rb` (modify)
**Depends on**: T2
**Reuses**: `app/billing/subscription.rb` transition guard
**Requirement**: S1 criteria 1, 3, 4 - C4, C5, C6, C11

**Done when**:

- [ ] Transitions match the plan's states
- [ ] Gate check passes: `bin/rails test test/billing`

**Tests**: unit
**Gate**: quick

---

### T4: Ingest the delivery once

**What**: `Webhooks::Ingest` dedups on `provider_delivery_id` and answers with the plan's codes
**Where**: `app/webhooks/ingest.rb` (modify)
**Depends on**: T3
**Reuses**: `Webhooks::Verifier` in `app/webhooks/verifier.rb`
**Requirement**: S2 criteria 5-7 - C7, C8, C9, C10, C12

**Done when**:

- [ ] Replay is `200`, a concurrent duplicate is `409`, a missing id is `422`, an unsigned one is `401`
- [ ] Gate check passes: `bin/rails test test/webhooks`

**Tests**: integration
**Gate**: full
