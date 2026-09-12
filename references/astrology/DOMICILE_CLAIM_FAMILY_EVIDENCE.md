# Domicile Claim Family Evidence｜守護星／本質尊貴 claim family

Status: **REFERENCE-ONLY / RESEARCH EVIDENCE / NOT PRODUCTION-ROUTABLE**

Branch baseline: `masini1491/ai-divination-playbook@b5c882e5806eaaf47672aefd8b66c0d63695357c`

## 1. Research question

Test the interpretation-source admission contract on one bounded claim family:

```text
essential dignity → domicile / planetary rulership
```

The goal is not to establish astrology as scientifically predictive or to promote a production doctrine. The goal is to test whether primary, scholarly-secondary, and practitioner/reference sources can be represented without collapsing distinct claims into a false consensus.

## 2. Sources reviewed

### S1 — PRIMARY_TEXT

Claudius Ptolemy, *Tetrabiblos*, Book I, §17, "Of the Houses of the Several Planets".

Reviewed public web edition: LacusCurtius / University of Chicago mirror of the Robbins translation.

Observed claim scope:

- planets have zodiacal "houses" alongside other familiarities;
- Cancer and Leo are assigned to Moon and Sun;
- the remaining visible planets receive sign assignments by relation to the luminaries, planetary order, and qualities;
- Ptolemy explicitly gives a northern/seasonal natural-philosophy rationale for the scheme.

Admission:

```text
source_role: PRIMARY_TEXT
admission_state: CLAIM_ELIGIBLE
claim_scope: historical doctrine / rulership configuration / Ptolemaic rationale
storage_mode: metadata + locator + normalized paraphrase
```

Important boundary: the ancient work and any modern translation are separate rights objects. This dossier stores only bibliographic/locator information and paraphrase; it does not vendor a translation corpus.

### S2 — SCHOLARLY_SECONDARY

Luís Campos Ribeiro, "Is astrology universal? Early modern globalization and the disruption of traditional knowledge," *The British Journal for the History of Science*, vol. 58, no. 3 (September 2025), pp. 425–445, DOI `10.1017/S0007087425000159`.

Cambridge lists the article as a research article and displays a CC BY-NC licence indicator.

Observed claim scope:

- Ptolemy tied foundational astrological concepts, including sign rulerships / essential dignities, to seasonal reasoning;
- early-modern encounters with the southern hemisphere exposed a serious tension in that rationale;
- Cardano, Campanella, and Kircher proposed reversing dignities in southern latitudes;
- other practitioners, including Morin and Figueroa, rejected reversal and argued for universality or region-dependent accidental effects instead;
- historical practice therefore contains a substantive doctrine conflict rather than a single uncontested universal rationale.

Admission:

```text
source_role: SCHOLARLY_SECONDARY
admission_state: CLAIM_ELIGIBLE
claim_scope: history of doctrine / conflict / applicability debate
storage_mode: metadata + locator + normalized paraphrase
```

This source does **not** become authority for whether astrology is true; it is authority for the documented historical debate and source lineage it analyzes.

### S3 — PRACTITIONER_REFERENCE / REFERENCE_IMPLEMENTATION

`wvanderen/astrology-skill@a9339b3c7151313530aa5002572c6612a2cfd59f`

Path reviewed:

`references/traditions/classical/dignities.md`

Observed claim scope:

- domicile is interpreted as a condition of authority / capacity to act from the planet's own terms;
- dignity is separated from moral goodness;
- dignity is distinguished from accidental strength;
- the module itself identifies Ptolemy and Lilly/traditional material as doctrine provenance.

Admission:

```text
source_role: PRACTITIONER_REFERENCE + REFERENCE_IMPLEMENTATION
admission_state: REFERENCE_ONLY for project doctrine
claim_scope: modern practitioner framing / retrieval architecture example
storage_mode: metadata + immutable revision + normalized paraphrase
```

Its MIT licence permits reuse subject to licence terms, but legal reuse permission does not grant semantic or production authority.

## 3. Claim decomposition

This evidence family shows that "domicile" must be decomposed into separate records.

### C1 — configuration claim

```text
claim: a named tradition assigns particular planets to particular signs as domiciles/rulers
layer: L3 policy / doctrine projection
best evidence role: PRIMARY_TEXT + later doctrine sources
```

This is not an L1/L2 astronomical fact.

### C2 — rationale claim

```text
claim: Ptolemy explains the domicile arrangement partly through northern seasonal and planetary-order reasoning
layer: L4 historical/doctrinal claim
best evidence role: PRIMARY_TEXT
```

Do not rewrite this as "the scientific reason for rulerships".

### C3 — historical-applicability conflict

```text
claim: early-modern authors disputed whether season-based dignities should reverse in the southern hemisphere
layer: L4 historical conflict claim
best evidence role: SCHOLARLY_SECONDARY, with primary-text follow-up when needed
```

Conflict type:

```text
historical_development + policy_difference + scope_difference
```

### C4 — interpretive meaning

```text
claim: in one contemporary classical-practitioner framework, domicile is treated as greater authority/capacity/resources rather than moral goodness
layer: L4 practitioner interpretation claim
best evidence role: PRACTITIONER_REFERENCE
```

This framing is not established by C1 alone and should not be projected backward onto every historical source.

## 4. Conflict preservation

The research evidence does **not** support a flattened statement such as:

```text
"Astrology universally teaches that the standard domicile table is naturally valid everywhere and always means a planet is strong."
```

A conflict-safe representation is:

```text
Ptolemaic configuration/rationale
↕ historical applicability dispute
southern-hemisphere reversal proposals vs universality defenses
↕ later practitioner semantic framing
modern condition/capacity interpretation
```

These can coexist in retrieval without being averaged into one synthetic doctrine.

## 5. Source-lineage lesson

The practitioner module cites older doctrine families. Therefore it must not be counted as an independent historical witness to Ptolemy merely because it repeats a compatible idea.

Candidate lineage:

```text
Ptolemy primary text
→ later historical transmission / debate
→ modern practitioner paraphrase
```

For consensus counting, derivative or lineage-linked sources must be marked non-independent.

## 6. Rights/storage lesson

This family validates the conservative storage rule:

- store source metadata, edition/revision, locator, licence/public-domain note, and normalized paraphrase by default;
- do not vendor long modern translations or journal text merely because the underlying ancient doctrine is old;
- licence status and source authority remain separate fields;
- CC BY-NC / MIT / public-domain status may permit different reuse, but no licence itself establishes doctrinal truth.

## 7. Result

The existing Source Admission architecture survives its first concrete claim-family test.

Key result:

```text
configuration != rationale != historical applicability != interpretive meaning
```

Each needs its own claim identity, source role, scope, and conflict metadata.

The evidence also supports retaining domicile/dignity as L3/L4 material rather than moving it into source-neutral L2.

## 8. Non-goals

This dossier does not:

- choose a canonical dignity table for production;
- decide northern-vs-southern-hemisphere doctrine;
- validate astrological efficacy;
- assign numeric strength scores;
- import a large interpretation corpus;
- alter production routing.

**Current state: REFERENCE-ONLY / RESEARCH EVIDENCE / NOT PRODUCTION-ROUTABLE**
