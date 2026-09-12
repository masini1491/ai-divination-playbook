# Astrology Interpretation Source Admission Draft｜占星解讀來源准入草案

Status: **REFERENCE-ONLY / RESEARCH DRAFT / NOT PRODUCTION-ROUTABLE**

Branch baseline: `masini1491/ai-divination-playbook@dd893bd816e77db9858b4672f3f9330ad01d0c60`

This draft extends `INTERPRETATION_ARCHITECTURE_DRAFT.md` with a source-admission and claim-registry contract for L4 interpretation evidence. It does **not** admit any astrology corpus into production, choose a canonical tradition, or establish scientific predictive validity.

## 1. Goal

The research problem is not simply "find astrology meanings." The project needs to keep four independent questions separate:

```text
What is this source?
What claim can it support?
May its expression be stored/reused?
Has the project adopted the claim/policy?
```

A source may be legally reusable but weak as doctrine evidence. A source may be historically or scholarly valuable but unsuitable for verbatim storage. A frequently repeated claim may still be tradition-specific. None of these states automatically creates production authority.

The target pipeline is:

```text
external source
→ source identity / provenance
→ admission assessment
→ claim extraction or normalized paraphrase
→ L4 claim registry
→ conflict grouping
→ L5 synthesis
```

## 2. Inputs from prior research

Prior research already established:

```text
L1/L2 = deterministic facts
L3 = tradition / policy projection
L4 = sourced interpretation claim
L5 = ChatGPT synthesis
```

This draft owns only the evidence-admission layer around L4 and source-backed L3 policy provenance.

Primary architecture precedent remains:

```text
wvanderen/astrology-skill@a9339b3c7151313530aa5002572c6612a2cfd59f
```

Decision remains:

```text
ADAPT architecture / REFERENCE-ONLY source
```

Its MIT license permits broad software/documentation reuse subject to license notice, but that legal permission does not turn its interpretive corpus into this project's canonical doctrine.

## 3. Source identity record

Candidate source registry shape:

```text
InterpretationSource
- source_id
- title
- author_or_org
- source_role
- source_kind
- tradition_tags[]
- publication_or_release_date
- edition
- immutable_revision
- locator
- language
- license_status
- license_identifier
- copyright_status
- storage_mode
- verification_status
- admission_status
- admission_scope[]
- excluded_scope[]
- notes[]
```

### `source_role`

Candidate values:

```text
PRIMARY_TEXT
SCHOLARLY_SECONDARY
PRACTITIONER_REFERENCE
REFERENCE_IMPLEMENTATION
UNVERIFIED_WEB_SOURCE
PROJECT_SYNTHESIS
```

These are evidence-role labels, not truth rankings.

### `source_kind`

Examples:

```text
book
article
critical_edition
translation
academic_paper
encyclopedia
practitioner_manual
repository
website
course_material
project_note
```

## 4. Admission status

Keep source admission separate from source role.

Candidate values:

```text
REJECTED
REFERENCE_ONLY
CLAIM_ELIGIBLE
POLICY_PROVENANCE_ELIGIBLE
CORPUS_STORAGE_ELIGIBLE
PRODUCTION_ADMITTED
```

Meaning:

- `REJECTED`: unsuitable for current research purpose or provenance insufficient.
- `REFERENCE_ONLY`: may inform architecture/research but cannot back project interpretation claims by default.
- `CLAIM_ELIGIBLE`: may support bounded L4 claims within declared scope.
- `POLICY_PROVENANCE_ELIGIBLE`: may support documentation of a named L3 doctrine/policy.
- `CORPUS_STORAGE_ELIGIBLE`: project has sufficient rights/status to store the permitted expression under declared storage mode.
- `PRODUCTION_ADMITTED`: requires an explicit future production decision; never inferred from any earlier state.

A source may hold multiple applicable capabilities, but production admission is never implicit.

## 5. Verification status

Candidate values:

```text
identity_verified
revision_verified
license_verified
publication_verified
locator_verified
partially_verified
unverified
```

Verification should be field-specific where practical. For example, a repository revision and license can be verified while historical authorship claims remain outside the current review.

## 6. Copyright / license boundary

### 6.1 Legal reuse is separate from evidence authority

The project must not collapse:

```text
license permits reuse
```

into:

```text
claim is historically authoritative
claim is scholarly consensus
claim is project canonical
```

Likewise, a high-value scholarly/historical source may have restrictive copyright and therefore support citation/paraphrase without authorizing corpus replication.

### 6.2 Candidate `license_status`

```text
verified_permissive
verified_copyleft
verified_proprietary_or_restricted
public_domain_verified
permission_granted
license_unresolved
not_applicable
```

### 6.3 Candidate `copyright_status`

```text
copyrighted
public_domain
mixed_or_compilation
unknown
not_applicable
```

Do not infer public-domain status solely from apparent age, an upload site's label, or lack of a visible notice.

### 6.4 Storage mode

Candidate values:

```text
metadata_only
metadata_plus_locator
normalized_paraphrase
short_excerpt_with_citation
licensed_module_copy
public_domain_text_copy
project_authored_synthesis
```

Default for newly reviewed interpretation sources should be conservative:

```text
metadata_plus_locator
+
normalized_paraphrase
```

until reuse rights are sufficiently verified.

Large verbatim corpus storage requires a separate affirmative basis such as:

- compatible verified license;
- verified public-domain status;
- explicit permission;
- project-authored original material.

This repository should not become a mirror of copyrighted interpretation prose merely because retrieval is technically possible.

## 7. Claim record

Candidate `InterpretationClaimRegistryEntry`:

```text
claim_id
layer: L4
claim_type
normalized_statement
source_refs[]
source_locator_refs[]
tradition_tags[]
policy_refs[]
applies_to[]
configuration_assumptions[]
scope
confidence_status
support_status
conflict_group_ids[]
cautions[]
storage_origin
```

`normalized_statement` should generally be project-authored paraphrase rather than copied prose.

### Candidate claim types

```text
symbolic_meaning
condition_meaning
house_topic_meaning
aspect_meaning
timing_meaning
synthesis_principle
uncertainty_principle
scope_guardrail
historical_doctrine
methodological_claim
other
```

## 8. Claim support status

Candidate values:

```text
single_source_supported
multi_source_supported
tradition_bounded
qualified
conflicted
historical_only
architecture_only
unsupported
```

Important rules:

- `multi_source_supported` does not mean scientifically validated.
- multiple sources copied from one another do not create independent support.
- a repeated modern convention does not become a universal historical doctrine.
- `architecture_only` sources may justify workflow design but not semantic astrology claims.

## 9. Source independence / lineage

A registry should preserve known dependence when one source appears derived from another.

Candidate fields:

```text
upstream_source_refs[]
derivative_relationship
independence_status
```

Candidate `independence_status`:

```text
independent_evidence
likely_derivative
explicit_derivative
shared_upstream
unknown
```

This prevents fake consensus from source duplication.

## 10. Claim eligibility by source role

Research default matrix:

| Source role | Architecture claim | Historical/doctrine claim | Contemporary practitioner meaning | Project production doctrine |
|---|---:|---:|---:|---:|
| PRIMARY_TEXT | eligible | eligible within edition/translation limits | contextual only | no automatic authority |
| SCHOLARLY_SECONDARY | eligible | eligible | contextual | no automatic authority |
| PRACTITIONER_REFERENCE | eligible | qualified | eligible within named tradition | no automatic authority |
| REFERENCE_IMPLEMENTATION | strong for architecture | weak/qualified unless independently sourced | qualified | no automatic authority |
| UNVERIFIED_WEB_SOURCE | weak | normally ineligible | normally ineligible | ineligible |
| PROJECT_SYNTHESIS | architecture/project policy only | cannot manufacture external history | synthesis only | only if separately admitted |

This matrix is a research default, not production policy.

## 11. Primary text does not mean "objectively correct"

A historical primary source can establish:

```text
"author/source X taught doctrine Y"
```

It cannot by itself establish:

```text
"doctrine Y is scientifically true"
"all astrology traditions agree with Y"
```

Translation choices, edition history, transmission, and historical context can materially change interpretation. Where relevant, preserve edition/translator provenance.

## 12. Scholarly secondary sources

A scholarly secondary source is useful for:

- historical context;
- terminology lineage;
- comparison among traditions;
- edition/translation criticism;
- distinguishing later convention from older doctrine.

Academic status does not automatically validate astrology's predictive claims. The claim being supported must match the source's actual research question.

## 13. Practitioner references

Practitioner sources may be valuable for documenting living interpretive conventions and operational reading practice.

Use them with explicit tradition/school scope. They should not be upgraded to universal historical authority merely because they are detailed or internally coherent.

## 14. Reference implementations

A software repository or skill can strongly support claims such as:

```text
this architecture separates calculation from interpretation
this workflow uses retrieval-first modules
this implementation degrades on unknown birth time
```

It is weaker evidence for claims such as:

```text
this symbolic meaning is historically canonical
this weighting rule is universally accepted
```

unless those semantic claims are independently sourced.

## 15. Unverified web sources

Default treatment:

```text
admission_status = REFERENCE_ONLY or REJECTED
storage_mode = metadata_plus_locator
claim support = unsupported / lead only
```

A search result, SEO article, forum post, social post, or unattributed page may be useful for discovering terminology or upstream references, but should not become an L4 authority merely because it is easy to retrieve.

## 16. Conflict registry

Candidate `InterpretationConflictGroup`:

```text
conflict_group_id
conflict_class
claim_refs[]
tradition_contexts[]
configuration_contexts[]
resolution_status
resolution_note
```

Candidate conflict classes:

```text
tradition_difference
policy_difference
historical_development
translation_difference
source_disagreement
scope_difference
configuration_difference
precision_difference
unresolved
```

Candidate `resolution_status`:

```text
coexist
scope_separated
historically_sequenced
one_source_superseded_for_specific_claim
insufficient_evidence
unresolved
```

Do not force substantive doctrine differences into a single averaged claim.

## 17. Retrieval behavior

Recommended retrieval sequence:

```text
user question
→ required claim types
→ available L1/L2 facts
→ explicit L3 tradition/policy context
→ registry query by claim type + applicability
→ eligible source-backed L4 claims
→ conflict-group reconciliation
→ minimum sufficient evidence set
→ L5 synthesis
```

Rules:

1. Prefer exact claim applicability over broad generic text.
2. Prefer verified provenance over source popularity.
3. Prefer independent evidence over duplicate downstream repetition.
4. Retrieve only enough material to answer the current question.
5. A retrieval miss does not authorize model-memory invention.
6. If the only available source is weak or unresolved, downgrade the claim or omit it.

## 18. Quotation and paraphrase discipline

The registry should normally store:

```text
normalized_statement
source locator
source identity / revision / edition
```

rather than long quotations.

Short quotations may be useful when exact wording itself is the evidence, for example a disputed historical formulation, but must remain within applicable copyright/license limits and should be no longer than necessary.

The project should never use a paraphrase to hide that a source is weak, derivative, conflicted, or out of scope.

## 19. Claim freshness / versioning

Interpretation sources are not all timeless.

Repository references should pin immutable revisions where possible. Living websites or editions should record retrieval/publication metadata sufficient to detect later changes.

A source revision changing does not automatically invalidate old claims; it creates a new evidence revision that may need reconciliation.

Candidate fields:

```text
reviewed_at
source_revision
supersedes_source_ref
claim_revision
```

## 20. Scientific-validity boundary

This registry is an evidence architecture for **what a tradition/source says**, not proof that astrology predicts outcomes.

The following are separate claim families and must not be conflated:

```text
astronomical calculation accuracy
historical doctrine provenance
interpretive convention prevalence
clinical/psychological validity
predictive validity
user-facing symbolic usefulness
```

An interpretation source can support the second or third without supporting the fourth or fifth.

## 21. Privacy boundary

Interpretation-source fixtures must remain synthetic, fictional, or lawful-public. A claim registry does not need real user natal data.

Do not embed personal readings as source evidence.

## 22. Machine-readable research example

See:

[`interpretation_source_registry_example.json`](interpretation_source_registry_example.json)

The example demonstrates:

- one verified permissive reference implementation;
- architecture-only vs claim-eligible scope separation;
- normalized paraphrase storage;
- independent admission and copyright fields;
- a synthetic conflict group;
- no production authority.

## 23. Promotion gap

Before a production interpretation corpus could be admitted, at minimum:

```text
source taxonomy review
→ source-admission validator
→ license/copyright review process
→ initial bounded claim registry
→ primary/scholarly/practitioner source comparison
→ conflict regression fixtures
→ retrieval behavior regression
→ citation/output provenance contract
→ explicit tradition taxonomy
→ explicit production admission
```

The next research step should therefore be **bounded source acquisition and comparison**, not bulk corpus ingestion.

**Current state: REFERENCE-ONLY / RESEARCH DRAFT / NOT PRODUCTION-ROUTABLE**
