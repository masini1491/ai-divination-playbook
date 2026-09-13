# Fourth–Tenth House Axis Evidence｜第四－第十宮軸證據

Status: **REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**

Baseline: `masini1491/ai-divination-playbook@b2e16a9375603fc9aed3c0032503aa178dc6046f`

## 1. Research question

本輪只研究一條 bounded angular axis：

```text
4th house / IC / lower midheaven
↕
10th house / MC / midheaven
```

目的不是建立十二宮大全，而是補齊目前 interpretation coverage 中第二條最重要的 angular axis，並驗證：

```text
historical house catalogue
!= contemporary traditional-practitioner framing
!= modern psychological/reference language
```

所有 claims 仍屬 L3/L4 research evidence；不建立 production Astrology method。

## 2. Why this axis now

前一輪已完成 1st–7th house axis，使本命解讀有第一條：

```text
self / body / native
↔
partner / marriage / direct other
```

4th–10th 軸補上另一條實用核心：

```text
home / land / roots / endings
↔
occupation / rank / authority / public standing
```

這對 natal、career、family/home 類問題都有直接 coverage 價值，同時仍能保持 bounded scope。

## 3. Source set

### 3.1 Vettius Valens / Mark Riley translation transcription

Source identity:

- `janegca/latex-valens`
- reviewed revision: `2d4a8b9890cd5cb7714abd52f6bd938272ba8237`
- locator: `book04/12-places.tex`
- repository license file: GPL-2.0
- translation/presentation rights are tracked separately; no translation corpus is vendored here.

Reviewed primary passage assigns the IV Place a broad catalogue including rank, children, wife, older persons, activity, city, home, possessions, lodgings, alterations and change of place, among other matters. The X Place includes occupation, rank, success, change and innovation in business, among other matters.

Research implication:

- Valens supports a Hellenistic typed claim for both places;
- Valens does **not** justify rewriting the 4th as only family-of-origin psychology;
- Valens does **not** justify reducing the 10th to a single modern notion of personal calling.

### 3.2 William Lilly, *Christian Astrology* (1647)

Reviewed locator:

- Skyscript / Deborah Houlding retyped web edition;
- “Of the Twelve Houses, their Nature and Signification”;
- Fourth House, CA p.53;
- Tenth House, CA p.56.

Fourth-house catalogue includes father, lands, houses, inheritances, cultivation, hidden treasure, and the determination/end of a matter; it names the angle *Imum Coeli*.

Tenth-house catalogue includes rulers/magistrates, honour, preferment, dignity, office, profession/trade, and mother; it names the *Medium Coeli* / Midheaven.

Research implication:

- Lilly is retained as an **early-modern historical context**;
- the current taxonomy has no canonical early-modern doctrinal-lineage selector;
- therefore `context:early_modern` must not be converted into an invented doctrine ID.

### 3.3 Deborah Houlding / Skyscript house rulerships

Reviewed pages:

- `The 4th house`, *House Rulerships in Practice*, 1996;
- `The 10th house`, *House Rulerships in Practice*, 1996.

The 4th-house page frames roots/foundations, parents/ancestry, land/property, home environment and endings as practitioner topics.

The 10th-house page frames profession/employment, employers/authority, honour/reputation, worldly position and public visibility; it explicitly contrasts the lower midheaven as roots with the midheaven as outward manifestation and preserves the traditional mother association.

Research implication:

- this is useful contemporary traditional-practitioner evidence;
- it is not an independent ancient witness;
- it does not establish scientific validity or a universal house ontology.

### 3.4 `wvanderen/astrology-skill`

Reviewed revision:

`a9339b3c7151313530aa5002572c6612a2cfd59f`

Locators:

- `references/houses/4th.md`
- `references/houses/10th.md`

Useful modern/reference language includes:

```text
4th:
belonging / emotional foundations / private memory /
inner architecture inherited from family or place

10th:
ambition / calling / public identity / contribution /
leadership / external standards of success
```

The source notes themselves state that classical material is paraphrased from earlier authors. Therefore these modules remain:

`REFERENCE_IMPLEMENTATION / REFERENCE_ONLY`

and do not become independent historical evidence.

## 4. Tradition / historical separation

The registry intentionally preserves four layers:

```text
Valens
→ lineage:hellenistic
→ context:classical_antiquity

Lilly
→ no invented doctrine context
→ context:early_modern

Houlding
→ no invented doctrine context
→ context:modern_contemporary

wvanderen modern/reference modules
→ no silent psychological-school promotion
→ context:modern_contemporary
→ REFERENCE_ONLY
```

No broad tag such as `classical`, `traditional`, or `modern` is allowed to silently become a typed doctrine selector.

## 5. Parent-signification boundary

This axis exposes a known tradition-sensitive issue:

```text
4th ↔ father / parents / ancestry
10th ↔ mother
```

The reviewed Lilly and Houlding material preserves versions of this assignment, but this research family does **not** promote it to a project-wide parent rule.

Instead the registry records a conflict group:

`conflict:fourth-tenth-parent-signification`

with resolution `coexist`.

Any future policy answering questions such as “which parent belongs to which angle?” requires a separate evidence family and explicit tradition selection.

## 6. Unknown birth-time / L2 precondition

Earlier executable unknown-time research showed that Asc/MC/cusps can sweep the full zodiac across a birth day and that houses can change completely when time is unknown.

Therefore this family carries the same interpretation boundary as 1st–7th:

```text
requires_l2_facts = true

required facts include, as applicable:
fact:ic / fact:house-4
fact:mc / fact:house-10
```

If those facts are unavailable:

```text
retrieval_status = precondition_failed
```

Current limitation remains explicit: registry metadata documents this L3 policy, but the generic retrieval core only enforces it when the caller declares `requires_l2_facts=true`. This family does not silently broaden core behavior.

## 7. Claim-family boundaries

This round does **not** decide:

- a production house system;
- whether IC/MC must equal 4th/10th cusps under every house system;
- a universal father/mother house assignment;
- a single definition of vocation or calling;
- deterministic career outcome from the 10th;
- deterministic family psychology from the 4th;
- scientific predictive validity of astrology.

It also does not infer private facts about any real person.

## 8. Machine-readable companion

Registry:

`fourth_tenth_house_axis_claim_family_registry.json`

Dedicated regression:

`test_fourth_tenth_house_axis_registry.py`

The registry uses `interpretation_claim_registry@0.2.0-research` and the existing typed tradition taxonomy. No new taxonomy contexts are introduced.
