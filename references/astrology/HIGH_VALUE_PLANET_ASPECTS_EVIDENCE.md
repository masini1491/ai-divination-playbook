# High-Value Planet/Aspect Families Evidence

Status: **REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**

## Scope

This research-v1 tranche expands beyond Saturn–Moon with five high-value exact pair/aspect exemplars:

```text
Sun square Saturn
Venus square Mars
Mars opposition Saturn
Mercury trine Jupiter
Venus square Saturn
```

The goal is not exhaustive combinatorics. It is to prove that the registry can represent multiple practical aspect families while preserving the difference between general aspect doctrine and pair-specific modern/practitioner interpretation.

## Primary doctrine boundary — Ptolemy

Ptolemy, *Tetrabiblos* Book I §13 describes the familiar major geometries, including opposition, trine, quartile/square and sextile. §§5, 7 and 24 discuss planetary natures and related configuration mechanics.

Research implication:

```text
major aspect geometry / general planetary nature
!=
a complete pair-specific interpretation
```

A primary source for the geometry does not automatically establish modern statements such as “Sun–Saturn square means fear of failure” or “Venus–Mars square means chemistry.” Those require separate source admission.

## Reference implementation — `wvanderen/astrology-skill`

Revision:

`a9339b3c7151313530aa5002572c6612a2cfd59f`

Reviewed exact modules:

- `references/aspects/by_planet_pair/sun_square_saturn.md`
- `references/aspects/by_planet_pair/venus_square_mars.md`
- `references/aspects/by_planet_pair/mars_opposition_saturn.md`
- `references/aspects/by_planet_pair/mercury_trine_jupiter.md`
- `references/aspects/by_planet_pair/venus_square_saturn.md`

These modules provide structured natal, transit and synastry guidance and consistently tell the reader to condition the interpretation by house, sign, dignity, sect, reception and reading type.

Because the modules are a modern synthesis and themselves cite older doctrine families, this round admits them as:

```text
REFERENCE_IMPLEMENTATION
REFERENCE_ONLY
qualified retrieval only
```

They are not counted as five independent historical witnesses.

## Bounded pair meanings retained as qualified reference claims

### Sun square Saturn

Reference framing: friction between visibility/purpose and limit/duty; possible themes of pressure, delayed recognition, seriousness, responsibility and tested confidence.

### Venus square Mars

Reference framing: friction between attraction/pleasure and assertion/urgency; possible chemistry, creative heat, relational conflict or desire requiring pacing and consent.

### Mars opposition Saturn

Reference framing: polarity between action/force and restraint/limit; possible disciplined confrontation, endurance, stalemate or stop-start momentum.

### Mercury trine Jupiter

Reference framing: cooperative detail/breadth; possible fluency in learning, teaching, writing, counsel and connecting facts to larger meaning, with a caution against overconfidence or imprecision.

### Venus square Saturn

Reference framing: friction between pleasure/value/affection and limit/time/duty; possible serious commitment, disciplined craft, caution or difficulty receiving warmth/value.

## Safety / non-determinism

Pair modules are never sufficient to predict concrete outcomes. Research retrieval must preserve:

- no diagnosis;
- no guaranteed relationship outcome;
- no guaranteed career or financial event;
- no deterministic claims about parents or partners;
- no coercive sexual framing;
- no fatalism from malefic aspects.

## Applicability and preconditions

Aspect interpretation requires:

1. supplied/calculated L2 aspect facts;
2. explicit L3 aspect/orb/context policy;
3. reading type distinction (`natal`, `transit`, `synastry`) when relevant.

The companion registry therefore declares both L2 and L3 preconditions. The language model must not invent an aspect, orb or phase merely because a pair is interesting.

## Result

Research v1 now contains a reusable pattern:

```text
primary geometry doctrine
+
qualified pair-specific reference claim
+
explicit reading-type applicability
+
L2/L3 fail-closed boundary
```

This is sufficient for broad research retrieval without pretending the project has exhaustively sourced every planet pair.

Companion registry:

`high_value_planet_aspects_claim_family_registry.json`

Regression:

`test_high_value_planet_aspects_registry.py`
