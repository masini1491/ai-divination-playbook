# Saturn–Moon Aspect Claim-Family Evidence｜土星－月亮相位解讀證據族

Status: **REFERENCE-ONLY / RESEARCH RESULT / NOT PRODUCTION-ROUTABLE**

Branch baseline: `masini1491/ai-divination-playbook@56db58abe6e3e52cb57b7b1e0fd68d31c5f278f0`

This dossier applies the source-admission and claim-registry contracts to one bounded interpretation family: **Moon–Saturn major aspects**. The research goal is not to prove that astrology is predictive. It is to separate what the geometry establishes, what a doctrine/policy admits, what historical sources actually say, what modern practitioner sources add, and what must remain ChatGPT synthesis.

## 1. Research question

Can the project represent Moon–Saturn aspect interpretation without collapsing these layers?

```text
L2 aspect geometry
→ L3 aspect/admission/context policy
→ L4 historical / scholarly / practitioner claims
→ L5 synthesis
```

The answer from this bounded evidence pass is **yes, but only if source role and scope remain explicit**.

## 2. Evidence set

### S1 — PRIMARY_TEXT

**Claudius Ptolemy, _Tetrabiblos_** (F. E. Robbins translation; LacusCurtius web edition)

Reviewed locators:

- Book I §13 — geometric aspect classes;
- Book III §4 — Saturn regarding the Moon in maternal judgment;
- Book III §13 — the Moon and planets configured with her in separation/application as inputs to judgment of the sensory / irrational part of the soul.

Locator roots:

- `https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/1B*.html`
- `https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3A*.html`
- `https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3D*.html`

Admission:

```text
source_role = PRIMARY_TEXT
admission_status = CLAIM_ELIGIBLE + POLICY_PROVENANCE_ELIGIBLE
storage_mode = metadata_plus_locator + normalized_paraphrase
```

Copyright/licensing note: this research pass does not independently establish a reusable-license/public-domain status for the online English translation. No large verbatim storage is adopted here.

### S2 — SCHOLARLY_SECONDARY

**Nicholas Campion, “Astrology in Ancient Greek and Roman Culture,” Oxford Research Encyclopedia of Planetary Science, published 23 May 2019.**

DOI:

`10.1093/acrefore/9780190647926.013.46`

Useful scope:

- classical astrology was not one uniform system;
- Ptolemy is a major but not exclusive classical source;
- the Moon is used by Ptolemy in the analysis of the sensory / irrational soul together with configured planets;
- detailed classical judgments may combine theory and accumulated observational convention;
- modern historians must distinguish source doctrine, philosophical rationale, later transmission, and translation.

Admission:

```text
source_role = SCHOLARLY_SECONDARY
admission_status = CLAIM_ELIGIBLE
storage_mode = metadata_plus_locator + normalized_paraphrase
```

This source supports historical context, not scientific validation of astrology.

### S3 — PRACTITIONER_REFERENCE

**Liz Greene, “Psychological Astrology: The Eternal Triangle,” Skyscript online reproduction, originally derived from _Relationships and How to Survive Them_ / Apollon material.**

Locator:

`https://direct.skyscript.co.uk/lgreene`

Useful bounded evidence:

- Moon–Saturn opposition appears as an example within a psychological-astrology discussion of parental image and later inner-life patterns;
- the framing treats the planetary configuration as part of psychological inheritance rather than as proof that a parent literally behaved in one fixed way;
- the source is modern psychological astrology, not classical doctrine.

Admission:

```text
source_role = PRACTITIONER_REFERENCE
admission_status = CLAIM_ELIGIBLE
storage_mode = metadata_plus_locator + normalized_paraphrase
```

Copyright status: copyrighted practitioner material; no bulk text storage.

### S4 — REFERENCE_IMPLEMENTATION

Immutable repository reference:

`wvanderen/astrology-skill@a9339b3c7151313530aa5002572c6612a2cfd59f`

Reviewed modules:

- `references/aspects/by_planet_pair/moon_conjunction_saturn.md`
- `references/aspects/by_planet_pair/moon_square_saturn.md`
- `references/aspects/by_planet_pair/moon_opposition_saturn.md`

Observed practitioner/implementation framing:

```text
conjunction → fuses Moon needs with Saturnian gravity
square      → friction between need and constraint
opposition  → polarizes need and duty / may externalize the polarity
```

The modules also add modern psychological language around self-sufficiency, guardedness, care, vulnerability, responsibility, and support.

Admission:

```text
source_role = REFERENCE_IMPLEMENTATION
admission_status = REFERENCE_ONLY for project doctrine
claim use = qualified practitioner/implementation evidence only
license_status = verified_permissive (MIT repository root)
storage_mode = metadata_plus_locator + normalized_paraphrase
```

The repository is useful evidence for a retrieval-first interpretation implementation. Its Moon–Saturn meanings are not automatically canonical here.

## 3. Layer boundary findings

### 3.1 L2: aspect geometry only

L2 may establish facts such as:

```text
Moon longitude
Saturn longitude
angular separation
aspect target angle
signed angular error
absolute error
relative speed
applying / separating state when deterministically available
```

L2 must not emit:

```text
emotional deprivation
cold mother
fear of dependency
loyalty
maturity
relationship burden
```

Those are interpretive statements.

### 3.2 L3: admission and context policy

L3 must decide, under an explicit policy:

```text
whether conjunction / square / opposition is admitted
orb threshold
whether applying/separating changes weight
whether sect modifies Saturn
whether natal / transit / synastry use different interpretation rules
whether reception or benefic testimony modifies the reading
```

A source module cannot create an aspect that L2 did not establish or an L3 policy did not admit.

### 3.3 L4: source-bounded meaning

L4 may store claims such as:

```text
Ptolemy uses the Moon plus configured planets when judging the sensory/irrational soul.
Ptolemy gives difficult maternal judgments when Saturn regards the Moon under specified conditions.
A modern psychological practitioner source uses Moon–Saturn opposition in a parental-image / inner-life framework.
The reviewed reference implementation frames Moon–Saturn conjunction, square, and opposition with distinct modern psychological metaphors.
```

Each claim must preserve source role and scope.

## 4. Primary-source boundary

A key result of this pass is negative but important:

**The reviewed Ptolemaic passages do not establish the modern practitioner metaphors**

```text
conjunction = fusion
square = friction
opposition = projection / polarization
```

Ptolemy Book I §13 establishes geometric aspect relationships; Books III §4 and §13 provide examples of Saturn/Moon and Moon/configured-planet judgment. This does not justify relabeling later psychological metaphors as direct Ptolemaic doctrine.

Therefore:

```text
aspect geometry terminology                  → L1/L2 / historical technique
classical Saturn–Moon judgment examples      → L4 historical doctrine
modern fusion/friction/polarity metaphors    → L4 practitioner / modern school
```

## 5. Classical vs modern scope

The evidence supports **scope separation**, not forced consensus.

### Classical / Ptolemaic scope

The reviewed classical material emphasizes:

- planetary nature;
- luminaries;
- configuration;
- sect/familiarity/power;
- bodily, parental, and soul-related judgments in their specific inquiry contexts.

### Modern psychological scope

The modern practitioner material emphasizes:

- inner emotional patterning;
- parental image / psychological inheritance;
- vulnerability and self-protection;
- responsibility and emotional containment;
- developmental integration.

These may coexist in a blended reading only when the synthesis names the school/context. They are not interchangeable source claims.

## 6. Aspect-form distinction

The reviewed reference implementation differentiates three aspect forms:

### Conjunction

Normalized practitioner claim:

> Moon and Saturn are treated as merged into one configuration, emphasizing the coexistence of need/care with limit/duty.

### Square

Normalized practitioner claim:

> Moon and Saturn are treated as a frictional configuration, emphasizing tension between need and constraint that requires adjustment.

### Opposition

Normalized practitioner claim:

> Moon and Saturn are treated as a polarity across an axis, emphasizing contrast between need and duty and possible externalization of one side.

These are **tradition-bounded practitioner claims**, not source-neutral geometry facts.

## 7. Natal / transit / synastry scope

The same planet pair cannot be retrieved without reading-type scope.

### Natal

A practitioner may discuss a long-term pattern or developmental theme.

### Transit

A practitioner may discuss temporary activation, but timing claims require L2 event facts. `transiting Saturn → natal Moon` and `transiting Moon → natal Saturn` differ greatly in duration and must not be treated as one event class.

### Synastry

A practitioner may discuss relational roles, but the chart does not establish another person's private feelings or motives as fact.

Therefore every Moon–Saturn claim should declare applicability such as:

```text
natal
transit_saturn_to_natal_moon
transit_moon_to_natal_saturn
synastry
```

## 8. Psychological / clinical boundary

This family is especially prone to overreach.

The registry must not convert practitioner language such as:

```text
nervous system
attachment
emotional deprivation
cold mother
abandonment
trauma
```

into clinical facts or biographical certainties.

Safe evidence form:

```text
"Source X interprets this configuration through themes of emotional containment / parental image / vulnerability."
```

Unsafe form:

```text
"This person had a cold mother."
"This aspect proves attachment trauma."
"This person has a nervous-system disorder."
```

The latter require external evidence and, for clinical claims, appropriate professional assessment; astrology is not evidence for diagnosis.

## 9. Source-lineage finding

The three `wvanderen/astrology-skill` modules explicitly cite classical sources at the family level and then add project-authored modern psychological framing.

Therefore their classical passages and modern passages have different lineage states:

```text
classical mechanism notes
→ derivative of stated historical source family

modern psychological synthesis
→ practitioner/reference-implementation synthesis
```

Three aspect files from one repository are not three independent authorities.

## 10. Conflict groups

### C1 — historical vs modern semantic scope

```text
conflict_class = historical_development + scope_difference
resolution_status = scope_separated
```

Classical doctrine and modern psychological astrology answer different interpretive questions.

### C2 — aspect geometry vs aspect metaphor

```text
conflict_class = scope_difference
resolution_status = scope_separated
```

Geometry establishes angle relation; "fusion/friction/polarity" is later interpretive framing.

### C3 — parent-image symbolism vs literal biography

```text
conflict_class = scope_difference
resolution_status = scope_separated
```

A symbolic parent-image claim does not establish a literal parental history.

## 11. Claim-support conclusions

Supported at research level:

```text
Ptolemy defines major aspect geometry.                         historical_doctrine
Ptolemy uses Moon + configured planets in soul judgment.      historical_doctrine
Ptolemy includes Saturn–Moon configurations in specific       historical_doctrine
maternal/body-related judgments.
Campion documents diversity and philosophical context of      scholarly_context
classical astrology and Ptolemy's Moon/soul framework.
Greene uses Moon–Saturn in modern psychological/parental       practitioner_meaning
imagery.
The pinned reference implementation differentiates Moon–      practitioner_meaning
Saturn conjunction/square/opposition with modern metaphors.
```

Not established:

```text
scientific predictive validity
clinical validity
universal Moon–Saturn meaning across traditions
literal childhood history
another person's private motives
project-canonical orb
project-canonical sect weighting
project-canonical aspect interpretation
```

## 12. Retrieval implication

A future query for Moon–Saturn should resolve in this order:

```text
1. confirm L2 geometry / event fact
2. select explicit L3 aspect + orb + context policy
3. select reading type
4. select tradition/school
5. retrieve only applicable L4 claims
6. preserve classical/modern scope differences
7. synthesize with uncertainty
```

A retrieval miss must not authorize free-association from model memory.

## 13. Machine-readable registry

See:

[`saturn_moon_aspect_claim_family_registry.json`](saturn_moon_aspect_claim_family_registry.json)

It records source roles, lineage, claims, applicability, conflict groups, and non-admitted claims without real natal data.

## 14. Promotion gap

This dossier does not choose a production interpretation policy.

Remaining gaps include:

```text
explicit aspect-policy taxonomy
orb-policy evidence comparison
sect-policy evidence comparison
primary-source pass beyond Ptolemy
independent modern-practitioner comparison
claim-registry validator
retrieval regression fixtures
citation/output provenance contract
production admission
```

**Current state: REFERENCE-ONLY / RESEARCH RESULT / NOT PRODUCTION-ROUTABLE**
