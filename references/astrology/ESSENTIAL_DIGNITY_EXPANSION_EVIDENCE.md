# Essential Dignity Expansion Evidence｜本質尊貴擴張證據

Status: **REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**

Baseline: `masini1491/ai-divination-playbook@795cff4f4d4425aa8ba674d4d189b7089038b074`

## Scope

Existing coverage already includes domicile/rulership. This dossier extends research coverage to:

```text
triplicity / triangles
exaltation ↔ depression/fall
terms / bounds
face terminology
later practitioner detriment / peregrine / reception framing
```

The goal is not to choose one production dignity table or numeric scoring system.

## Primary source — Ptolemy, *Tetrabiblos*, Book I §§17–23

Reviewed LacusCurtius / University of Chicago web edition of the Robbins translation:

`https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/1B*.html`

Relevant chapter structure:

- §17 Houses of the Several Planets;
- §18 Triangles;
- §19 Exaltations;
- §20 Disposition of Terms;
- §21 Chaldaean method;
- §22 Places and Degrees;
- §23 Faces, Chariots, and the Like.

### Exaltation / depression

The reviewed text explicitly gives paired exaltation/depression assignments, including:

```text
Sun      Aries      ↔ Libra
Saturn   Libra      ↔ Aries
Moon     Taurus     ↔ Scorpio
Jupiter  Cancer     ↔ Capricorn
Mars     Capricorn  ↔ Cancer
Venus    Pisces     ↔ Virgo
Mercury  Virgo      ↔ Pisces
```

This supports a historical Ptolemaic claim about the configuration and its stated seasonal/natural-philosophy rationale. It does not prove astrological efficacy.

### Terms / bounds

Ptolemy explicitly reports more than one term system:

```text
Egyptian
Chaldaean
Ptolemaic / an ancient-manuscript-derived arrangement discussed by Ptolemy
```

Research implication:

`terms/bounds table != method-neutral universal fact`

Any future production calculator must make the selected term system explicit provenance.

### Triplicity / triangles

Ptolemy treats triangles/triplicities as another zodiacal familiarity and discusses their rulers separately from domicile. Research interpretation must therefore keep triplicity support distinct from domicile authority.

### Face terminology warning

Ptolemy §23 uses “proper face” for a planetary relationship that depends on reproducing the aspect relationship of the planet's houses to the luminary houses. This is not safely identical, without further source work, to the later/common practitioner use of `face/decan` as a minor essential dignity attached to ten-degree subdivisions.

Therefore research v1 records:

```text
Ptolemaic proper-face terminology
!= automatically identical to
later decan/face dignity table
```

The later decan/face table remains a separate-source requirement.

## Practitioner/reference implementation — `wvanderen/astrology-skill`

Revision:

`a9339b3c7151313530aa5002572c6612a2cfd59f`

Locator:

`references/traditions/classical/dignities.md`

The module supplies a coherent contemporary classical-practitioner framing:

- domicile → authority/capacity from own terms;
- exaltation → elevated emphasis/honour;
- triplicity → compatible environmental/support resources;
- bound/term → operation under the bound lord;
- face/decan → minor dignity / local coherence;
- detriment → opposite domicile;
- fall → opposite exaltation;
- peregrine → lacking essential dignity;
- reception → welcome/access/negotiated cooperation.

Its source note points back to Ptolemy and Lilly/traditional material. It is therefore valuable as a practitioner/reference layer but remains `REFERENCE_ONLY` for project doctrine.

## Dignity vs accidental strength

A central research contract is retained:

```text
essential dignity by zodiacal relationship
!=
accidental strength by house, angularity, motion, visibility, etc.
```

A planet may be essentially debilitated but accidentally prominent, or dignified but hidden/cadent. Research synthesis must not flatten the two dimensions into one score.

## Table-selection policy boundary

Research v1 does not choose:

- Egyptian vs Ptolemaic vs another bounds table;
- a canonical triplicity-ruler table across every tradition;
- a canonical decan/face table;
- a numeric dignity score;
- whether detriment should be weighted symmetrically with domicile;
- whether every tradition accepts the same dignity ontology.

Such choices belong to explicit future tradition/policy selection.

## Retrieval precondition

Dignity interpretation requires supplied/calculated chart facts and an explicit dignity/tradition policy when a table-dependent minor dignity is being judged. The registry therefore declares:

```json
{"retrieval_preconditions":{"requires_l2_facts":true,"requires_l3_policy":true}}
```

This prevents a language model from inventing a dignity or table choice during retrieval.

## Result

Research v1 can now distinguish:

```text
domicile
triplicity
exaltation/fall
terms/bounds
face terminology
later detriment/peregrine/reception framing
```

while preserving unresolved table/terminology choices instead of silently canonizing one modern synthesis.

Companion registry:

`essential_dignity_expansion_claim_family_registry.json`

Regression:

`test_essential_dignity_expansion_registry.py`
