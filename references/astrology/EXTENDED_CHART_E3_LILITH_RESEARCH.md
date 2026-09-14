# Astrology Extended Chart Facts Phase E3｜Black Moon Lilith Identity

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / DEFAULT NOT SELECTED / NOT PRODUCTION-ADMITTED**

Baseline: `masini1491/ai-divination-playbook@40d4938bb3f265d332608312463b550fb8b8aa13`

## 1. Research question

A consumer chart label such as `Lilith` is not sufficiently precise to be a deterministic fact identity. Phase E3 separates the mathematical objects before any product naming/default policy is chosen.

## 2. Resolved Swiss identities

Pinned Swiss Ephemeris source `aloistr/swisseph@91339e55d2351f32548d8a8d5bca6aa93b4f6da7` exposes distinct apsis objects:

```text
SE_MEAN_APOG → mean lunar apogee
SE_OSCU_APOG → osculating lunar apogee
SE_INTP_APOG → interpolated lunar apogee
```

The reviewed Swiss header assigns separate object ids to mean and osculating apogee. The source/test surface also treats mean, osculating and interpolated apogees as distinct node/apsis calculation objects.

Pinned Immanuel `theriftlab/immanuel-python@eba98099b7724598064113ffa1322e78dc4bccf6` maps:

```text
LILITH              → swe.MEAN_APOG
TRUE_LILITH         → swe.OSCU_APOG
INTERPOLATED_LILITH → swe.INTP_APOG
```

Pinned Kerykeion `g-battaglia/kerykeion@b18848eb8e1e0a2b09a096dbb9688c8404dfb06b` independently exposes separate `Mean_Lilith` and `True_Lilith` points and describes True Lilith as the oscillating Black Moon Lilith.

## 3. Canonical research identities

Recommended deterministic ids:

```text
black_moon_lilith_mean
black_moon_lilith_osculating
black_moon_lilith_interpolated
```

Recommended aliases are metadata only:

```text
Mean Lilith / Mean Black Moon Lilith
True Lilith / Osculating Black Moon Lilith
Interpolated Lilith
```

Do not use bare `lilith` as a mathematical identity.

## 4. Fact-layer rule

```text
L1/L2 fact:
  exact apsis model + longitude/speed + provider provenance

L3 policy:
  which model a product, school, consumer chart, or compatibility mode calls “Lilith”
```

A consumer source that only says `Lilith` without defining its model is `AMBIGUOUS_MODEL`, not evidence for one of the three identities.

## 5. Comparison rule

Comparisons must be model-to-model:

```text
mean ↔ mean
osculating ↔ osculating
interpolated ↔ interpolated
```

A difference between Mean Lilith and True/Osculating Lilith is not numerical error; they are different mathematical objects.

## 6. Production boundary

E3 resolves the identity problem but intentionally does not choose a single unqualified production default.

If a future API supports all variants, no default decision is necessary:

```text
request explicit model
→ return explicit model
```

If a future UI/API insists on one bare `Lilith`, the default model becomes a product-policy decision and must be explicitly admitted/versioned.

## 7. E3 conclusion

```text
Mean Black Moon identity          RESOLVED
Osculating/True identity          RESOLVED
Interpolated identity             RESOLVED
bare consumer “Lilith”            AMBIGUOUS WITHOUT POLICY
model-to-model comparison rule    RESOLVED
single production default         NOT SELECTED
production admission              NOT GRANTED
```

E3 research is complete without selecting a product default.
