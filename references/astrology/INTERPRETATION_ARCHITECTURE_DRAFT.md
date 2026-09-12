# Astrology Interpretation Architecture Draft｜占星解讀架構草案

Status: **REFERENCE-ONLY / RESEARCH DRAFT / NOT PRODUCTION-ROUTABLE**

Branch baseline: `masini1491/ai-divination-playbook@de587a2ae8f68bf61ee0f74d02c1a09168e4e206`

This draft defines a provenance-first boundary between deterministic Astrology facts and later tradition-specific interpretation. It does **not** establish a canonical astrology tradition, canonical meanings, production routing, or prediction authority.

## 1. Goal

The intended pipeline is:

```text
L0 input / provenance
→ L1 astronomical fact
→ L2 deterministic derived chart/event fact
→ L3 tradition/policy projection
→ L4 sourced interpretation claim
→ L5 ChatGPT synthesis
```

The purpose of the split is to prevent four common collapses:

- symbolic meanings being stored as astronomical facts;
- one tradition's policy being presented as universal astrology truth;
- an external corpus sentence being treated as canonical merely because it was retrieved;
- ChatGPT synthesis being presented as if it were a directly sourced claim.

## 2. Bounded reuse review

Primary architecture reference reviewed at immutable revision:

```text
wvanderen/astrology-skill@a9339b3c7151313530aa5002572c6612a2cfd59f
```

Observed useful patterns:

- structured chart data is interpreted after calculation rather than inside the calculator;
- interpretation uses retrieval-first, minimum-relevant modules;
- tradition mode is explicit (`classical`, `modern`, `blended`);
- missing houses, dignities, aspect precision, timing factors, or birth time are not silently invented;
- uncertainty changes weighting and scope;
- synthesis is distinct from factor retrieval;
- ethical/scope guardrails constrain certainty and high-stakes claims.

Decision:

```text
ADAPT architecture / REFERENCE-ONLY source
```

Not adopted:

- the external corpus as project canonical doctrine;
- its weighting hierarchy as production policy;
- its classical/modern/blended semantics as final project taxonomy;
- any specific planet/sign/house/aspect meaning;
- any statement that astrology predicts external outcomes with objective certainty.

## 3. Layer authority

### L1/L2 — deterministic fact layer

Owned by deterministic calculation/provenance contracts.

Examples:

```text
Mercury longitude = 110.0°
Moon longitude bounded to a range
Ascendant unavailable because birth time is unknown
transit exact root at UTC timestamp
aspect signed angular error
station direct→retrograde speed root
```

L1/L2 must not contain interpretive language such as:

```text
restriction
growth
romance
career pressure
psychological transformation
malefic/benefic judgment
```

### L3 — tradition / policy projection

L3 expresses how a named interpretive system chooses to classify, select, or weight L1/L2 facts.

Candidate responsibilities:

```text
tradition identity
policy identity/version
house-topic mapping
rulership scheme
dignity/debility doctrine
sect doctrine
reception doctrine
aspect-orb policy
factor inclusion/exclusion
factor weighting/ranking policy
timing-technique policy
confidence degradation rules
```

L3 is not astronomy. It is a declared interpretive policy over deterministic facts.

Example:

```text
fact: Venus longitude 15° Libra
policy: classical-essential-dignity-v1
projection: Venus classified as domicile under this policy
```

The classification may be deterministic *given the policy*, but the policy itself is tradition-specific and therefore does not become an L1/L2 fact.

### L4 — sourced interpretation claim

L4 is a human-authored or corpus-authored semantic claim tied to:

```text
specific source
specific revision / edition where available
specific tradition / policy context
specific applicable factor(s)
claim scope
uncertainty / caution
```

Examples:

```text
"Under source X's modern interpretation, Saturn-Moon contact is associated with themes of emotional containment or responsibility."

"Under source Y's classical doctrine, a planet in domicile is treated as having greater capacity to act according to its nature."
```

An L4 claim is **not** promoted merely because multiple websites repeat it.

### L5 — ChatGPT synthesis

L5 combines selected L3 projections and L4 claims to answer a user question.

L5 must preserve:

- which facts were actually available;
- which tradition/policy was used;
- which source claims were used;
- unresolved conflicts;
- uncertainty and missing data;
- distinction between source claim and ChatGPT synthesis.

L5 is not a new doctrine owner. A useful synthesis must remain traceable back to L1/L2 facts + L3 policy + L4 source claims.

## 4. Candidate L3 projection record

```text
TraditionProjection
- projection_id
- layer: L3
- fact_refs[]
- tradition_id
- policy_id
- policy_version
- projection_kind
- result
- confidence
- dependencies[]
- source_refs[]
```

Candidate `projection_kind` values:

```text
signification_scope
rulership
dignity
sect
reception
house_topic
aspect_admission
aspect_weight
timing_technique
factor_priority
condition
other
```

Rules:

1. Every L3 record must point to the L1/L2 facts it consumes.
2. Every nontrivial policy result must name its policy identity.
3. A projection must not silently rewrite its source fact.
4. If different traditions disagree, preserve separate projections rather than merging them into one universal value.

## 5. Candidate L4 interpretation claim record

```text
InterpretationClaim
- claim_id
- layer: L4
- claim_type
- statement
- applies_to[]
- tradition_id
- policy_refs[]
- source
- source_locator
- source_revision
- source_status
- confidence
- scope
- cautions[]
- conflicts_with[]
```

Candidate `claim_type` values:

```text
symbolic_meaning
condition_meaning
house_topic_meaning
aspect_meaning
timing_meaning
synthesis_principle
uncertainty_principle
scope_guardrail
other
```

`statement` must be framed as a sourced interpretive assertion, not as an objective astronomical fact.

## 6. Source authority states

Candidate source states:

```text
PRIMARY_TEXT
SCHOLARLY_SECONDARY
PRACTITIONER_REFERENCE
REFERENCE_IMPLEMENTATION
UNVERIFIED_WEB_SOURCE
PROJECT_SYNTHESIS
```

These are evidence-role labels, not truth scores.

A production admission process would still need to define which classes are acceptable for which claim types.

External GitHub repositories reviewed for architecture remain:

```text
REFERENCE-ONLY
```

Their source-state role does not grant production authority.

## 7. Tradition identity must be explicit

Do not store:

```text
"Mars rules Scorpio"
```

without a policy/tradition context when a conflicting system may exist.

Prefer:

```text
tradition_id: western_classical_candidate
policy_id: rulership-traditional-v1
claim/projection: Mars assigned domicile rulership of Scorpio
```

Likewise, outer-planet rulership, whole-sign vs quadrant topic emphasis, minor aspects, lots, asteroids, modern psychological language, and other contested conventions must be explicit rather than silently blended.

## 8. Tropical / sidereal separation

`tropical` and `sidereal` are L1/L2 configuration facts, not merely interpretation style.

However, interpretive claims may depend on the configured zodiac and tradition. Therefore L4 claims should declare configuration assumptions when material.

A claim derived for a tropical placement must not be silently applied to a sidereal placement merely because the sign label differs.

## 9. Houses and house topics

House cusp geometry / house placement = L2.

House-topic meaning = L3/L4.

Example separation:

```text
L2:
  Venus is in house 7 under house_system = Placidus

L3:
  policy maps house 7 to partnership/contract topics

L4:
  source interprets Venus in that topic context in a stated way
```

Unknown birth time continues to fail closed at L2. L3/L4 must not reconstruct a house topic when house placement is unavailable.

## 10. Aspects and orb policy

Aspect geometry can exist at L1/L2 without deciding whether an interpretive tradition accepts the aspect.

```text
L2:
  angular separation / signed error / relative speed

L3:
  aspect set + orb policy + applying/separating weighting

L4:
  sourced meaning for the admitted aspect under the stated tradition
```

Therefore:

- no project-wide orb is implied by geometry;
- unknown orb or precision degrades interpretive confidence;
- a source's orb doctrine is source/policy evidence, not astronomy.

## 11. Dignity, sect, reception, rulership

These are important boundary cases because they can be calculated deterministically *after a doctrine is selected*.

Candidate classification:

```text
astronomical placements             → L1/L2
selected doctrine/rule table         → L3 policy
calculated dignity/sect/reception    → L3 projection
meaning of that condition            → L4 claim
user-facing synthesis                → L5
```

This avoids putting doctrine-specific classifications into the source-neutral fact core.

## 12. Timing

Exact transit/station/ingress geometry and timestamps remain L1/L2.

Claims such as:

```text
"activation window"
"peak pressure"
"opportunity"
"relationship turning point"
```

are L3/L4/L5 depending on whether they arise from policy, source interpretation, or synthesis.

Timing interpretation must not invent:

- station dates;
- retrograde passes;
- perfection dates;
- house/angle contacts;
- exactness;
- application/separation;

when those facts are absent or unavailable.

## 13. Unknown birth-time propagation

The interpretation layer must consume the availability states produced by Structured Astrology Fact rather than replacing them.

Examples:

```text
Moon sign ambiguous
→ L4 claims tied to one Moon sign cannot be selected as definitive

Ascendant unavailable
→ no Ascendant-specific interpretation claim
→ no chart-ruler projection derived from Ascendant

houses unavailable
→ no house-topic synthesis
```

A narrower interpretation from stable facts remains permitted.

## 14. Retrieval contract

Candidate retrieval sequence:

```text
user question
→ required fact types
→ available L1/L2 facts
→ selected explicit tradition/policy
→ matching L3 projections
→ minimum relevant L4 claims
→ conflict/uncertainty reconciliation
→ L5 synthesis
```

Rules:

- retrieve the minimum relevant sources;
- exact/focused claim modules are preferred over broad generic summaries when provenance quality is comparable;
- retrieval miss does not authorize free-association;
- a missing exact source may justify a broader claim only if its broader scope is made explicit;
- unsupported interpretation should be omitted or marked as unsupported, not filled from model memory.

## 15. Conflict model

Different interpretive sources may disagree without either being a data error.

Candidate conflict classes:

```text
tradition_difference
policy_difference
source_disagreement
scope_difference
configuration_difference
precision_difference
historical_vs_modern_difference
unresolved
```

When sources conflict:

1. compare applicable tradition/configuration;
2. compare source authority/status;
3. preserve both claims when the conflict is substantive;
4. do not average incompatible doctrines into a fictitious consensus;
5. L5 may explain the difference, but may not erase provenance.

## 16. Confidence model

Interpretive confidence is not astronomical accuracy.

Candidate confidence inputs:

```text
fact availability
fact precision
policy explicitness
source quality/status
claim specificity
source agreement/conflict
question fit
```

Candidate output labels:

```text
supported
qualified
provisional
conflicted
unsupported
```

No numeric `0-100` confidence or outcome probability is admitted by this draft.

## 17. High-stakes / certainty boundary

The architecture treats astrology as symbolic/interpretive evidence, not deterministic proof.

L4/L5 must not claim certainty about:

- another person's private motives;
- pregnancy, death, illness, accidents;
- legal outcomes;
- investment outcomes;
- guaranteed relationship outcomes;
- guaranteed external events.

This is a scope boundary on interpretation, not an assertion that an astrology corpus has scientific predictive validation.

## 18. Machine-readable research example

See:

[`interpretation_claim_example.json`](interpretation_claim_example.json)

The example is synthetic and demonstrates:

- L2 fact references;
- explicit L3 tradition/policy projection;
- L4 sourced-claim envelope;
- conflict-safe provenance;
- no real personal birth data;
- no production authority.

## 19. Promotion gap

Before this architecture could become production-routable, at minimum the project would still need:

```text
tradition taxonomy decision
source-admission criteria
claim-source registry
license/copyright review for interpretation corpus
policy versioning
retrieval behavior regression
conflict handling regression
high-stakes/scope regression
L3/L4 machine validation
production owner + routing admission
```

No item above is implied complete by this draft.

**Current state: REFERENCE-ONLY / RESEARCH DRAFT / NOT PRODUCTION-ROUTABLE**
