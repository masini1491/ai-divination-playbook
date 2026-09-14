# Astrology Extended Chart Facts Phase E5｜Aspect Participant Policy

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / DEFAULT PARTICIPANT SET NOT SELECTED / NOT PRODUCTION-ADMITTED**

Baseline: `masini1491/ai-divination-playbook@40d4938bb3f265d332608312463b550fb8b8aa13`

## 1. Problem

Current Production v1 computes major aspects over its admitted body list. Extended charts introduce angles, nodes, asteroids, lots and special points. Whether those objects are allowed to participate in aspects is a policy choice, not an astronomical fact.

## 2. Required separation

The research architecture is:

```text
all available deterministic facts
→ aspect_participant_policy
→ eligible object set
→ pair geometry
→ aspect-definition/orb policy
→ policy-qualified aspect graph
```

Do not encode participant eligibility inside longitude calculation or object taxonomy.

## 3. Object classes

Candidate participant classes:

```text
planet
lunar_node
angle
asteroid_or_centaur
lunar_apsis
lot
special_point
```

Examples:

```text
planet: Sun ... Pluto
lunar_node: Mean/True North/South Node
angle: ASC, MC, DSC, IC
asteroid_or_centaur: Chiron, Ceres, Pallas, Juno, Vesta
lunar_apsis: Mean/Osculating/Interpolated Black Moon Lilith
lot: Part of Fortune
special_point: Vertex, Equatorial Ascendant
```

## 4. Policy must be named and versioned

Examples of research policy ids, not production defaults:

```text
aspect-participants-core-bodies-v1
aspect-participants-core-plus-angles-v1
aspect-participants-extended-points-v1
```

Each policy must explicitly enumerate eligible object ids or stable classes. A new object becoming calculable must not automatically begin generating aspects.

## 5. Geometry remains policy-neutral

For two eligible longitudes `a` and `b`:

```text
separation = shortest circular separation(a, b)
```

Aspect matching then applies a separately versioned aspect/orb policy. This keeps:

```text
object availability
participant eligibility
aspect type availability
orb width
```

as distinct concerns.

## 6. Current Production compatibility

Production v1 currently admits major aspects only and its aspect generation uses the existing admitted body set; ASC/MC are calculated but do not participate.

E5 does not silently change that behavior.

A future extension can reproduce current behavior with a participant policy equivalent to the existing body list, then separately admit other policies.

## 7. Extended-object safeguard

The following implication is prohibited:

```text
object exists in fact bundle
therefore object participates in aspects
```

The correct implication is:

```text
object exists
AND selected participant policy includes it
THEREFORE pair geometry may be evaluated
```

This is particularly important for Fortune, Vertex, Equatorial Ascendant and Lilith variants, where schools/software differ materially.

## 8. Pattern dependency

E6 pattern topology must consume the **policy-qualified aspect graph**, not raw longitudes. Otherwise a pattern detector would silently invent its own participant and orb policy.

## 9. E5 conclusion

```text
participant-policy architecture     RESOLVED
object class separation             RESOLVED
geometry boundary                   RESOLVED
production-current compatibility    RESOLVED
single extended default set         NOT SELECTED
production admission                NOT GRANTED
```

E5 research is complete. Selecting one extended participant set as a product default is a later policy decision.
