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
admission_status: POLICY_PROVENANCE_ELIGIBLE
claim_scope: historical doctrine / rulership configuration / Ptolemaic rationale
storage_mode: metadata_plus_locator + normalized_paraphrase
```

Important boundary: the ancient work and the reviewed English translation are separate rights objects. This dossier stores only bibliographic/locator information and project-authored paraphrase; it does not vendor a translation corpus. The reviewed translation's reuse status is not treated as verified merely because the underlying work is ancient.

### S2 — SCHOLARLY_SECONDARY

Luís Campos Ribeiro, "Is astrology universal? Early modern globalization and the disruption of traditional knowledge," *The British Journal for the History of Science*, vol. 58, no. 3 (September 2025), pp. 425–445, DOI `10.1017/S0007087425000159`.

Cambridge identifies the item as a research article, published online 7 March 2025, and marks it open access under CC BY-NC 4.0.

Observed claim scope:

- Ptolemy tied foundational astrological concepts to seasonal reasoning;
- early-modern encounters with tropical and southern latitudes exposed tension in that rationale;
- Cardano, Campanella, and Kircher addressed reversal implications;
- practitioners working in the New World reached different conclusions;
- historical practice therefore contains a substantive doctrine/applicability conflict rather than one uncontested universal rationale.

Admission:

```text
source_role: SCHOLARLY_SECONDARY
admission_status: CLAIM_ELIGIBLE
claim_scope: history of doctrine / conflict / applicability debate
storage_mode: metadata_plus_locator + normalized_paraphrase
```

This source does **not** become authority for whether astrology is true; it supports the documented historical debate and source lineage it analyzes. No journal text corpus is stored.

### S3 — PRACTITIONER_REFERENCE

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
source_role: PRACTITIONER_REFERENCE
admission_status: REFERENCE_ONLY
claim_scope: modern practitioner framing / reference-implementation precedent
storage_mode: metadata_plus_locator + normalized_paraphrase
```

The reviewed repository is MIT licensed at the pinned revision, but legal reuse permission does not grant semantic or production authority. This source is lineage-linked to older doctrine and therefore is not counted as an independent historical witness merely because it repeats compatible material.

## 3. Claim decomposition

This evidence family shows that "domicile" must be decomposed into separate records.

### C1 — historical configuration claim

```text
claim: Ptolemy presents a named scheme assigning planets to zodiacal houses/domiciles
layer: L4 historical_doctrine claim
L3 consequence: a later project policy could cite this as provenance if separately selected
best evidence role: PRIMARY_TEXT
```

The mapping is not an L1/L2 astronomical fact. The source can support provenance for a named L3 policy, but this research round does not adopt that policy for production.

### C2 — rationale claim

```text
claim: Ptolemy explains the domicile arrangement partly through northern seasonal and planetary-order reasoning
layer: L4 historical_doctrine claim
best evidence role: PRIMARY_TEXT
```

Do not rewrite this as "the scientific reason for rulerships".

### C3 — historical-applicability conflict

```text
claim: early-modern authors/practitioners differed over how season-dependent astrological properties should behave in southern latitudes
layer: L4 historical_doctrine / conflict claim
best evidence role: SCHOLARLY_SECONDARY, with primary-text follow-up when needed
```

Primary conflict class for the registry:

```text
historical_development
```

Related dimensions include policy and scope differences, but the contract stores one canonical `conflict_class` per group and keeps the additional dimensions in context/notes rather than inventing a new enum combination.

### C4 — interpretive meaning

```text
claim: in one contemporary classical-practitioner framework, domicile is treated as greater authority/capacity/resources rather than moral goodness
layer: L4 condition_meaning
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
southern-hemisphere adaptation/reversal proposals vs continuity/universality defenses
↕ later practitioner semantic framing
modern condition/capacity interpretation
```

These can coexist in retrieval without being averaged into one synthetic doctrine.

Registry resolution:

```text
resolution_status: coexist
```

This means preserve the documented positions and scopes. It does not resolve which doctrine should be used in production.

## 5. Source-lineage lesson

The practitioner module cites older doctrine families. Therefore it must not be counted as an independent historical witness to Ptolemy merely because it repeats a compatible idea.

Candidate lineage:

```text
Ptolemy primary text
→ later historical transmission / debate
→ modern practitioner paraphrase
```

For consensus counting, derivative or lineage-linked sources must be marked non-independent. The machine-readable example therefore uses the existing contract value `explicit_derivative` for the practitioner source rather than inventing an ad hoc independence label.

## 6. Rights/storage lesson

This family validates the conservative storage rule:

- store source metadata, edition/revision, locator, licence/copyright note, and normalized paraphrase by default;
- do not vendor long modern translations or journal text merely because the underlying ancient doctrine is old;
- licence status and source authority remain separate fields;
- CC BY-NC / MIT / public-domain status may permit different reuse, but no licence itself establishes doctrinal truth;
- when rights are not fully verified, fail closed to metadata/locator/paraphrase rather than inferring public-domain corpus rights.

## 7. Contract-fit findings

The first concrete claim-family test found several useful schema constraints:

1. `source_role` should remain singular in the source record. A source may also serve as a reference-implementation precedent, but that secondary use belongs in notes/scope rather than an array that violates the current candidate shape.
2. Use canonical `admission_status`, not an ad hoc `admission_state`.
3. Use canonical storage-mode values such as `metadata_plus_locator` and `normalized_paraphrase` rather than concatenated new enum names.
4. Use the current `independence_status` vocabulary (`independent_evidence`, `explicit_derivative`, etc.).
5. Use a canonical conflict `resolution_status` (`coexist` here), not a claim-family-specific status.
6. Keep L3 policy selection separate from L4 historical evidence: a primary text may be `POLICY_PROVENANCE_ELIGIBLE` without the project adopting its policy.

## 8. Result

The existing Source Admission architecture survives its first concrete claim-family test after normalizing the example to the current contract vocabulary.

Key result:

```text
configuration != rationale != historical applicability != interpretive meaning
```

Each needs its own claim identity, source role, scope, lineage, and conflict metadata.

The evidence also supports retaining domicile/dignity as tradition/policy/interpretation material rather than moving it into source-neutral L1/L2.

## 9. Non-goals

This dossier does not:

- choose a canonical dignity table for production;
- decide northern-vs-southern-hemisphere doctrine;
- validate astrological efficacy;
- assign numeric strength scores;
- import a large interpretation corpus;
- alter production routing.

**Current state: REFERENCE-ONLY / RESEARCH EVIDENCE / NOT PRODUCTION-ROUTABLE**
