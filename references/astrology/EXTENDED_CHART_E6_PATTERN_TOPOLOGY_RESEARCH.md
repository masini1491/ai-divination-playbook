# Astrology Extended Chart Facts Phase E6｜Pattern Topology

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / ORB PRODUCT POLICY NOT SELECTED / NOT PRODUCTION-ADMITTED**

Baseline: `masini1491/ai-divination-playbook@40d4938bb3f265d332608312463b550fb8b8aa13`

> Production supersession note (current reconciliation: `3346b59055a300aa8998884ccc376017483836af`): this file remains historical research authority. Production subsequently admitted seven major-aspect topology projections in #151 and hardened the E5-qualified graph boundary in #154. Yod, Stellium, Grand Quintile and exact consumer/唐綺陽 compatibility remain outside the admitted scope described here.


## 1. Core conclusion

Aspect patterns are deterministic **after** participant, aspect-type and orb policies are fixed. They are not a new astronomical calculation layer.

Canonical pipeline:

```text
available facts
→ E5 participant policy
→ pair geometry
→ aspect/orb policy
→ qualified aspect graph
→ conjunction-cluster normalization
→ topology detector
→ pattern facts carrying policy provenance
```

## 2. External topology evidence

Pinned Immanuel `theriftlab/immanuel-python@eba98099b7724598064113ffa1322e78dc4bccf6` implements pattern matching over an aspect graph and explicitly clusters conjunct objects so one physical pattern is not multiplied by conjunct points on a vertex.

Its reviewed topology definitions include:

```text
T-Square
Grand Trine
Yod
Grand Cross
Kite
Mystic Rectangle
Cradle
Grand Sextile
Grand Quintile
```

Examples of graph requirements:

```text
T-Square:
  square + opposition + square

Grand Trine:
  trine + trine + trine

Yod:
  sextile base + two quincunxes

Grand Cross:
  four square edges + opposite vertices in opposition
```

This provides architecture evidence, not authority to copy implementation or orbs.

## 3. Pattern policy object

Every deterministic pattern result should preserve at least:

```text
pattern_policy_id
participant_policy_id
aspect_policy_id
orb_policy_id
pattern_type
vertex object ids / conjunction clusters
supporting aspect ids
```

A pattern without policy provenance is not reproducible.

## 4. Candidate topology family

Minimum research family relevant to current consumer-chart compatibility work:

```text
stellium
T-square
grand trine
grand cross
yod
kite
mystic rectangle
cradle
```

Additional patterns can be added under versioned topology definitions; their existence must not alter previously versioned results.

## 5. Stellium is policy-sensitive

Unlike the edge-defined patterns above, `stellium` often varies by:

```text
minimum number of objects
maximum span / conjunction-chain rule
sign boundary handling
eligible object classes
whether Sun/Moon/angles count
```

Therefore E6 resolves the architecture but does not declare one universal stellium definition.

Recommended representation:

```text
stellium-policy-<version>
```

with all thresholds explicit.

## 6. Yod requires an aspect-set expansion

Current Production v1 major aspects do not include quincunx.

Therefore:

```text
Yod topology may be research-defined
BUT
Yod cannot be produced under current major-only aspect policy
```

A future Yod admission requires a separately versioned aspect policy that includes 150-degree quincunx plus an explicit orb.

## 7. Nested-pattern suppression

The reviewed Immanuel implementation suppresses smaller candidate patterns when their vertex set is a strict subset of a larger detected pattern. This is a legitimate projection policy but is not mathematically mandatory.

Recommended separation:

```text
raw topology matches
→ pattern_projection_policy
→ displayed/reportable patterns
```

Thus `detect all valid subpatterns` and `suppress nested subpatterns` can coexist as versioned policies.

## 8. Consumer compatibility boundary

A consumer label such as `T-square`, `Grand Cross`, `中三角`, or `大十字` is insufficient to prove exact compatibility unless the following are known:

```text
participant set
aspect definitions
orbs
conjunction clustering
nested-pattern rule
pattern-specific thresholds
```

The exact 唐綺陽 pattern/orb algorithm remains unverified and must not be reverse-invented from a finite set of labels.

## 9. E6 conclusion

```text
aspect-graph topology architecture   RESOLVED
T-square / trine / cross / yod etc.  RESOLVED AS TOPOLOGY TEMPLATES
conjunction-cluster handling         RESOLVED AS EXPLICIT POLICY SURFACE
nested-pattern handling              RESOLVED AS EXPLICIT POLICY SURFACE
stellium universal definition        NOT CLAIMED
exact consumer/唐綺陽 orb policy      UNRESOLVED
production pattern default           NOT SELECTED
production admission                 NOT GRANTED
```

E6 research is complete at the architecture/topology level. Exact product-compatible orb/default selection is intentionally deferred rather than guessed.
