# Remaining House Axes Evidence｜剩餘四條宮位軸證據

Status: **REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**

Baseline: `masini1491/ai-divination-playbook@795cff4f4d4425aa8ba674d4d189b7089038b074`

## Scope

This dossier completes the research-level twelve-house skeleton by covering the four remaining opposing pairs:

```text
2nd ↔ 8th   personal resources ↔ transferred/shared/other-party resources, loss and inheritance
3rd ↔ 9th   local kin/messages/movement ↔ distant travel/religion/knowledge/guidance
5th ↔ 11th  children/pleasure/generation ↔ friends/benefactors/hopes/support
6th ↔ 12th  illness/labor/service ↔ confinement/hidden adversity/isolation
```

It does not choose a production house system, prove astrological efficacy, or make deterministic life-event claims.

## Source set

### Vettius Valens / Mark Riley translation transcription

Repository: `janegca/latex-valens`

Reviewed revision: `2d4a8b9890cd5cb7714abd52f6bd938272ba8237`

Locator: `book04/12-places.tex`

The reviewed primary passage supplies a compact Hellenistic catalogue for all twelve places. Relevant bounded observations:

- II: life, Gate of Hades, giving/receiving, association;
- III: brothers, travel abroad, authority, friends/relatives, revenue and dependants;
- V: children, friendship, association and benefaction;
- VI: slaves, injuries, hostility, disease and sickness;
- VIII: death, benefits from the deceased, law and sickness;
- IX: friendship, travel, foreigners, God, rulers, astrology/oracles and mystic matters;
- XI: friends, hopes, gifts, children and dependants;
- XII: foreign lands, hostility, dependants, injuries, dangers, tribunals, disease and death.

These are retained as historical Hellenistic claims. They are not rewritten into modern psychological categories.

### Deborah Houlding / Skyscript, *House Rulerships in Practice* (1996)

Reviewed public pages:

- `https://www.skyscript.co.uk/2.html`
- `https://www.skyscript.co.uk/3.html`
- `https://www.skyscript.co.uk/5.html`
- `https://www.skyscript.co.uk/6.html`
- `https://www.skyscript.co.uk/8.html`
- `https://www.skyscript.co.uk/9.html`
- `https://www.skyscript.co.uk/11.html`
- `https://www.skyscript.co.uk/12.html`

Bounded practitioner framing reviewed in this round includes:

- 2nd: resources, earnings, assets and personal movable possessions;
- 8th: death/loss, inheritance, partner or other-party money, debts/taxes/loans;
- 3rd: siblings/kin, neighbours, local environment, short journeys and communications;
- 9th: long journeys, foreign places, religion/philosophy/divination and higher learning;
- 5th: children, pregnancy/procreation, romance, pleasure, arts and gambling/speculation;
- 11th: friends, supporters, benefactors, hopes, wider groups and allies;
- 6th: illness, service/employees, practical labour, small animals and maintenance topics;
- 12th: hidden/restraint, sorrow, confinement, persecution, isolation and secret adversity.

This is contemporary practitioner evidence, not an independent ancient witness and not scientific validation.

### `wvanderen/astrology-skill`

Reviewed revision: `a9339b3c7151313530aa5002572c6612a2cfd59f`

Locators:

```text
references/houses/2nd.md
references/houses/3rd.md
references/houses/5th.md
references/houses/6th.md
references/houses/8th.md
references/houses/9th.md
references/houses/11th.md
references/houses/12th.md
```

The modules add modern/reference language such as values/security, worldview/meaning, creative confidence, community belonging, health-maintenance systems, vulnerability/entanglement, and unconscious/private patterns. Their own source notes identify dependence on older doctrine families, so these remain `REFERENCE_IMPLEMENTATION / REFERENCE_ONLY` and are never counted as independent historical corroboration.

## Tradition boundary

```text
Valens
→ tradition_context_refs = [lineage:hellenistic]
→ historical_context_refs = [context:classical_antiquity]

Houlding
→ tradition_context_refs = []
→ historical_context_refs = [context:modern_contemporary]

wvanderen modules
→ tradition_context_refs = []
→ historical_context_refs = [context:modern_contemporary]
→ REFERENCE_ONLY
```

No modern wording is silently assigned to `school:modern:psychological_astrology` merely because it uses psychological vocabulary.

## Oppositional-axis boundary

The registry treats each house as its own sourced claim and uses axis conflict/context groups only to preserve scope. Opposition does not mean that one house is the negation of the other or that every topic must be interpreted as a binary.

## Medical / death / financial guardrails

The 6th, 8th and 12th contain historically difficult topics. Research retrieval must not turn them into:

- diagnosis or medical advice;
- deterministic death prediction;
- guaranteed debt/investment outcomes;
- claims that isolation, illness or loss is deserved or spiritually required.

These houses may be discussed symbolically and historically, with ordinary high-stakes safety boundaries preserved.

## Birth-time precondition

All house interpretation requires supplied, sufficiently reliable L2 house facts. This registry therefore declares registry-level:

```json
{"retrieval_preconditions":{"requires_l2_facts":true,"requires_l3_policy":false}}
```

Once metadata-driven precondition enforcement is enabled in this completion round, callers no longer need to remember to set `requires_l2_facts=true` manually for this registry. A query with no `l2_fact_refs` must fail closed before claim selection.

## Non-goals

This family does not decide:

- whole-sign vs quadrant house policy;
- cusp/house-system equivalence;
- planetary joys as production doctrine;
- turned-house policy;
- deterministic fertility, illness, death, legal or financial outcomes;
- scientific predictive validity.

Machine-readable companion:

`remaining_house_axes_claim_family_registry.json`

Dedicated regression:

`test_remaining_house_axes_registry.py`
