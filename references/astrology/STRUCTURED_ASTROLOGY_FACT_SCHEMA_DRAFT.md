# Structured Astrology Fact Schema Draft｜結構化占星事實 Schema 草案

Status: **REFERENCE-ONLY / RESEARCH DRAFT / NOT PRODUCTION-ROUTABLE**

Playbook baseline at branch start: `masini1491/ai-divination-playbook@f1e78fada7c270be4cfcff9dbddfd4ebdb42828e`

This document proposes a source-neutral data contract for Astrology L0-L2 facts that can later sit between deterministic calculation and interpretation. It does **not** establish a production method, production engine, interpretation rule, orb doctrine, weighting, or routing authority.

## 1. Goal

The draft should make the following pipeline explicit:

```text
input / provenance
→ deterministic astronomy
→ derived chart / event facts
→ Structured Astrology Fact
→ later tradition projection
→ later interpretation
```

The schema exists to prevent the language model from silently merging:

- civil-time input with resolved UTC;
- requested ephemeris backend with effective backend;
- exact values with bounded / ambiguous values;
- pure geometry with orb / tradition policy;
- multiple retrograde passages into one event;
- external-source object IDs with project-owned semantic identity;
- deterministic facts with interpretation prose.

## 2. Non-goals

This draft deliberately does not define:

- `ASTROLOGY.md`;
- production method routing;
- production engine selection;
- canonical orb values;
- aspect priority / weighting;
- dignity / sect / rulership policy;
- interpretive meanings;
- cross-validation with Tarot / Meihua / Liuyao;
- personal Reading Record storage.

## 3. Reuse / Adapt / Gap map

### Candidate reviewed

```text
theriftlab/immanuel-python@46190726ebe012f43c93d163745682e806975759
```

Its pinned documentation demonstrates a structured chart representation with:

- native datetime / timezone / coordinates;
- chart objects;
- houses;
- longitudes;
- speed and movement;
- aspects;
- actual angular difference;
- applying / exact / separating-like movement;
- JSON serialization.

### Decision

```text
Decision: ADAPT conceptually / REFERENCE-ONLY source
```

Useful concepts:

- structured rather than prose chart facts;
- explicit object / house / aspect records;
- speed and motion represented as data;
- aspect geometry separated into numeric fields;
- serializable chart output.

Not adopted:

- upstream numeric object indexes as our semantic identity;
- dignity / score / weighting fields as L1/L2 facts;
- upstream orb defaults as project policy;
- upstream ambiguity handling as our canonical input contract;
- the upstream JSON shape as a copied schema.

### Project-specific gap

Prior Astrology research established requirements not covered by a plain chart dump:

```text
requested backend != effective backend
unknown-time availability / bounded uncertainty
UTC vs IANA-local rendering
DST ambiguous / nonexistent input
transit-to-natal timing uncertainty
multi-passage identity under retrograde
station event identity
ingress / retrograde return / re-ingress identity
fact lineage
strict L1/L2 vs L3/L4 separation
```

This schema draft is designed around those gaps.

## 4. Top-level envelope

Candidate shape:

```text
StructuredAstrologyFact
- schema_name
- schema_version
- record_status
- record_kind
- record_id
- subject_ref
- provenance
- configuration
- facts
- notes
```

Candidate `record_kind` values:

```text
chart_snapshot
event_collection
combined
```

`subject_ref` must be opaque / synthetic / lawful-public when committed to this public repository. It is not a place for identifiable birth-data tuples.

## 5. Evidence-layer boundary

This draft carries only:

```text
L0 input / provenance
L1 astronomical fact
L2 deterministic derived chart / event fact
```

It may contain pointers to policy provenance when required to explain how a derived window was requested, but it must not promote those policy choices to L1/L2 truth.

Not part of the fact core:

```text
L3 tradition projection
L4 interpretation claim
L5 synthesized reading
```

Examples of excluded L3/L4 content:

```text
"Saturn is restrictive"
"this transit means relationship pressure"
"6° is the correct Venus orb"
"this aspect is more important than that one"
```

## 6. Shared availability model

Every fact whose value may depend on missing or uncertain input should be able to express:

```text
availability.status:
  available
  bounded
  ambiguous
  unavailable
  placeholder
```

And:

```text
availability.reasons[]
availability.dependencies[]
```

Meaning:

- `available`: one supported value under current input / configuration;
- `bounded`: value lies within a known interval / set;
- `ambiguous`: multiple discrete supported values exist and no single value may be selected;
- `unavailable`: required input is missing or invalid;
- `placeholder`: a deterministic convenience value exists but must not be promoted to known truth.

`placeholder` is particularly important for unknown-time research.

## 7. Time provenance

Candidate:

```text
TimeProvenance
- input_kind
- original_value
- iana_timezone
- fold
- resolution_status
- resolved_utc
- candidate_utc[]
- bounded_utc
- utc_offset_seconds
- birth_time_certainty
- timezone_source
- tzdb_version
```

Candidate `resolution_status`:

```text
unique
ambiguous
nonexistent
unknown
not_applicable
```

Candidate `birth_time_certainty`:

```text
exact
bounded
unknown
not_applicable
```

Contract:

```text
civil input
→ timezone resolution
→ canonical UTC fact
→ deterministic calculation
```

A local display time is a rendering of UTC plus timezone provenance, not a second authoritative event time.

## 8. Location provenance

Candidate:

```text
LocationProvenance
- availability
- latitude_deg
- longitude_deg
- altitude_m
- source
- precision_note
```

Location may legitimately be unavailable / not required for some geocentric event searches.

If location uncertainty is later shown to materially affect an L1/L2 fact, the uncertainty must propagate instead of being hidden in a formatted place name.

## 9. Engine provenance

Candidate:

```text
EngineProvenance
- engine_name
- engine_version
- engine_revision
- runtime
- requested_backend
- effective_backend
- requested_flags
- effective_flags
- ephemeris_data_revision
- calculated_at_utc
```

The `requested_backend` / `effective_backend` distinction is mandatory whenever the engine can silently fall back.

Example from current research:

```text
requested_backend = SWIEPH
effective_backend = MOSEPH
```

The requested value must never overwrite the effective calculation fact.

## 10. Configuration provenance

Candidate:

```text
AstrologyConfiguration
- zodiac_system
- ayanamsa
- center
- house_system
- node_type
- coordinate_frame
- epoch
- body_set_id
- aspect_set_id
- orb_policy_ref
```

Rules:

- `ayanamsa` is required to interpret a sidereal result reproducibly;
- `house_system` may be null when houses are not calculated;
- `node_type` must distinguish mean / true where material;
- `orb_policy_ref` is only a policy pointer.

`orb_policy_ref` does not make the chosen orb a deterministic astronomical truth.

## 11. Fact identity and lineage

Every durable L1/L2 fact should have:

```text
fact_id
evidence_layer: L1 | L2
availability
derived_from[]
source_refs[]
```

`derived_from[]` points to other fact IDs or input/provenance IDs.

Example:

```text
fact:moon-sign
derived_from:
  - fact:moon-longitude
  - config:zodiac-system
```

This allows later interpretation to cite the actual fact chain instead of re-deriving it from prose.

## 12. ChartObjectFact

Candidate:

```text
ChartObjectFact
- meta
- object_id
- object_type
- longitude
- latitude_deg
- speed_deg_per_day
- motion_state
- sign
- house
```

Candidate object types:

```text
luminary
planet
node
angle
cusp
asteroid
fixed_star
other
```

### Longitude value

Longitude must support uncertainty:

```text
DegreeValue
- status: exact | bounded | ambiguous | unavailable
- exact_deg
- ranges_deg[]
- candidate_deg[]
```

`ranges_deg[]` is preferred over a single `min/max` because circular longitude can cross 0°.

### Motion

Candidate:

```text
motion_state:
  direct
  retrograde
  stationary
  indeterminate
```

Movement is deterministic geometry / speed state. Interpretation is separate.

### Sign placement

Candidate:

```text
SignPlacement
- availability
- zodiac_system
- sign_name
- sign_index
- degree_in_sign
- possible_signs[]
```

Unknown birth time may yield, for example:

```text
possible_signs = [Aries, Taurus]
availability.status = ambiguous
```

instead of silently selecting the noon sign.

### House placement

Candidate:

```text
HousePlacement
- availability
- house_number
- possible_houses[]
```

Unknown birth time should normally make house placement unavailable or bounded/ambiguous under an explicit uncertainty interval.

## 13. HouseFact

Candidate:

```text
HouseFact
- meta
- house_number
- cusp_longitude
```

Angles and cusps must carry availability separately from ordinary planetary facts.

Noon placeholders must not become authoritative house cusps.

## 14. AspectGeometryFact

This is pure geometry, not an interpretation record.

Candidate:

```text
AspectGeometryFact
- meta
- left_ref
- right_ref
- target_angle_deg
- oriented_branch_deg
- separation_deg
- signed_error_deg
- absolute_error_deg
- relative_speed_deg_per_day
- applying_state
```

Candidate `applying_state`:

```text
applying
exact
separating
indeterminate
```

Important boundary:

```text
separation / signed error / relative speed
→ L1/L2 fact

"within accepted orb"
→ requires L3 orb policy
```

Therefore an aspect geometry record can exist even when no production orb policy has been selected.

## 15. Event model

Events use:

```text
event_id
event_kind
time
search_window_utc
availability
passage_index
derived_from[]
```

Candidate `event_kind`:

```text
exact_aspect
transit_to_natal
station
ingress
```

### Temporal value

Event time must support uncertainty:

```text
TemporalValue
- status: exact | bounded | ambiguous | unavailable
- exact_utc
- start_utc
- end_utc
- candidate_utc[]
```

This prevents a bounded natal target from being rendered as one falsely exact transit timestamp.

## 16. ExactAspect / TransitToNatal event

Candidate:

```text
ExactAspectEvent
- event meta
- moving_body_ref
- target_type
- target_ref
- target_longitude
- target_angle_deg
- oriented_branch_deg
- motion_direction
- relative_speed_deg_per_day
- angular_residual_deg
- geometry_window
```

Candidate target types:

```text
transit_body
natal_object
natal_angle
natal_cusp
fixed_longitude
```

`passage_index` is required when a search window contains multiple exact passages for the same semantic body/target/aspect combination.

### Geometry window

Optional candidate:

```text
geometry_window
- orb_degrees
- orb_policy_ref
- entry_time
- exit_time
```

The window is deterministic **after** an explicit orb is supplied.

The schema must preserve the policy pointer because:

```text
entry/exit root solving = deterministic
orb value selection = L3 policy
```

## 17. StationEvent

Candidate:

```text
StationEvent
- event meta
- body_ref
- transition
- speed_before_deg_per_day
- speed_at_root_deg_per_day
- speed_after_deg_per_day
```

Candidate transitions:

```text
direct_to_retrograde
retrograde_to_direct
unresolved
```

A station is a speed-root fact. Its interpretation remains outside this schema.

## 18. IngressEvent

Candidate:

```text
IngressEvent
- event meta
- body_ref
- zodiac_system
- boundary_longitude_deg
- from_sign
- to_sign
- motion_direction
- ingress_kind
```

Candidate `ingress_kind`:

```text
direct_ingress
retrograde_return_to_previous_sign
direct_reingress
other
```

This preserves the topology observed in the Venus 2026 research fixture.

## 19. Bounded target → bounded event time

The schema must permit:

```text
natal target longitude:
  status = bounded

transit event time:
  status = bounded
  start_utc = ...
  end_utc = ...
```

If target uncertainty changes event topology, for example creates or removes a retrograde passage, the result should become:

```text
availability.status = ambiguous
```

rather than producing one arbitrary passage.

## 20. Unknown-time availability examples

### Unknown-time natal Moon

Possible:

```text
longitude.status = bounded
sign.availability.status = ambiguous
possible_signs = [Aries, Taurus]
```

### Unknown-time Ascendant

Expected:

```text
availability.status = unavailable
reason = birth time required
```

### Unknown-time natal planet far from a boundary

Possible:

```text
longitude.status = bounded
sign.availability.status = available
sign_name = Capricorn
```

The sign may remain available while exact degree remains bounded.

## 21. Policy separation

Do not place these in the L1/L2 fact core as unquestioned truth:

```text
dignity
sect judgment
rulership weighting
aspect importance
orb doctrine
house-topic meaning
transit scoring
interpretation text
prediction outcome
```

A later L3 projection may consume this schema and attach:

```text
policy_id
tradition_id
source
derived projection
```

but that is a separate contract.

## 22. External identifiers

External libraries may use numeric indexes, enums, or implementation-specific object names.

The source-neutral draft uses stable semantic IDs such as:

```text
Sun
Moon
Mercury
Ascendant
House_1_Cusp
```

or project-defined opaque IDs.

Do not expose an upstream internal numeric index as the only durable identity unless that upstream contract itself becomes canonical.

## 23. Record status and versioning

Current draft identity:

```text
schema_name = structured_astrology_fact
schema_version = 0.1.0-research
record_status = REFERENCE-ONLY
```

Future incompatible field semantics require a schema-version change.

A production schema must not be inferred from the filename or from the existence of machine-readable examples; it requires explicit admission.

## 24. Machine-readable example

See:

[`structured_astrology_fact_example.json`](structured_astrology_fact_example.json)

The example is synthetic and uses the previously validated Mercury → fixed `110°` target triple-passage fixture.

It intentionally shows:

- synthetic subject reference;
- UTC search window;
- display timezone as presentation provenance;
- requested SWIEPH vs effective MOSEPH;
- one fixed target fact;
- three distinct passage identities;
- motion direction per passage.

It contains no interpretation.

## 25. Privacy boundary

Public repository fixtures must not contain an identifiable person's combined:

```text
birth date
birth time
birth place
```

Prefer:

- synthetic coordinates / timestamps;
- synthetic target longitudes;
- fictional fixtures;
- lawful public examples only when truly necessary.

Schema capability must not be demonstrated by committing private user natal data.

## 26. Implementation invention boundary

The following responsibilities are already constrained by research and should not be re-invented without new evidence:

```text
UTC as canonical event time
explicit timezone resolution before calculation
effective backend provenance
unknown-time fail-closed houses / angles
bounded target → bounded event-time propagation
multi-passage event identity
geometry / policy separation
fact / interpretation separation
```

Future implementation work should focus on the remaining GAP:

```text
formal machine validation
exact required/optional fields per record kind
stable semantic identifier registry
engine adapter mapping
cross-engine fixtures for station / ingress / transit-to-natal
production tolerance
L3 projection contract
production admission
```

## 27. Admission boundary

This draft does not change:

```text
CHAT_INIT.md
PLAYBOOK_INDEX.json
METHOD_ROUTING.md
INPUT_CONTRACT.md
production method owners
cross-validation semantics
```

Before production admission, at minimum:

```text
schema review
→ executable schema validation
→ multi-engine / fixture mapping
→ privacy review
→ failure-mode regression
→ interpretation boundary review
→ explicit production admission decision
```

**Current state: REFERENCE-ONLY / RESEARCH DRAFT / NOT PRODUCTION-ROUTABLE**
