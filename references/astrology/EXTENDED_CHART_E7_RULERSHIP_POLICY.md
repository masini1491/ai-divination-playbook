# Astrology Extended Chart Facts Phase E7｜Rulership Projection Policy

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / DEFAULT SCHOOL NOT SELECTED / NOT PRODUCTION-ADMITTED**

Baseline: `masini1491/ai-divination-playbook@40d4938bb3f265d332608312463b550fb8b8aa13`

> Production supersession note (current reconciliation: `3346b59055a300aa8998884ccc376017483836af`): this file remains historical research authority. Production subsequently admitted both `rulership-traditional-v1` and `rulership-modern-v1` in #149 under explicit-selector-only activation, with no silent default, blending or co-ruler policy.


## 1. Problem

House-ruler output is not a raw astronomical fact. It projects a sign-rulership tradition onto deterministic house-cusp/sign facts.

Therefore:

```text
house / sign fact
+ rulership policy
→ house-ruler projection
```

belongs at L3 policy/derived interpretation, not L1 astronomy.

## 2. Two required policy families

Research must preserve at least these separately versioned schemes.

### `rulership-traditional-v1`

```text
Aries       Mars
Taurus      Venus
Gemini      Mercury
Cancer      Moon
Leo         Sun
Virgo       Mercury
Libra       Venus
Scorpio     Mars
Sagittarius Jupiter
Capricorn   Saturn
Aquarius    Saturn
Pisces      Jupiter
```

### `rulership-modern-v1`

```text
Aries       Mars
Taurus      Venus
Gemini      Mercury
Cancer      Moon
Leo         Sun
Virgo       Mercury
Libra       Venus
Scorpio     Pluto
Sagittarius Jupiter
Capricorn   Saturn
Aquarius    Uranus
Pisces      Neptune
```

These are policy candidates, not a claim that all schools use exactly one of them or that co-rulership variants do not exist.

## 3. Evidence for policy separation

Pinned Astrolog `CruiserOne/Astrolog@5bf172ea231c4b6ea3d7e09ca307571354a41e8a` exposes explicit standard-rulership data structures (`ruler1`, `ruler2`) and configurable rulership handling rather than treating rulership as celestial-position data. This supports the architectural separation between deterministic chart facts and a chosen rulership projection.

Consumer-chart compatibility evidence already shows that some modern consumer systems assign outer-planet rulers to Scorpio/Aquarius/Pisces. That is evidence for a `modern` compatibility policy, not grounds to overwrite the traditional mapping globally.

## 4. House-ruler projection

Given a deterministic house cusp/sign assignment:

```text
house_ruler = selected_rulership_policy[sign_on_house]
```

Required provenance:

```text
house_system_id
house number
sign on house
rulership_policy_id
ruler object id(s)
```

Do not store only a bare ruler name, because the same house/sign can produce different rulers under different policies.

## 5. Co-rulership and alternative schools

A future policy may legitimately return more than one ruler, for example a traditional + modern co-ruler model. If admitted, it must be represented as another explicit policy rather than silently merged into either v1 mapping.

Example namespace only:

```text
rulership-co-ruler-<version>
```

No co-ruler scheme is admitted by E7.

## 6. Compatibility routing

When reproducing a known consumer chart:

```text
if source declares/establishes modern rulership
→ select modern compatibility policy

if source declares traditional rulership
→ select traditional policy

if source is silent
→ do not infer a universal default from the chart label alone
```

## 7. E7 conclusion

```text
rulership as L3 projection          RESOLVED
traditional-v1 mapping              DEFINED
modern-v1 mapping                   DEFINED
policy provenance requirement       RESOLVED
silent blending                     PROHIBITED
co-ruler alternatives               POSSIBLE / NOT ADMITTED
single production default           NOT SELECTED
production admission                NOT GRANTED
```

E7 research is complete without deciding which school becomes the product default.
