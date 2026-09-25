# AST-P1-020 — Mean Black Moon Lilith Local Analytical Parity

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / PARITY PASS / NOT PRODUCTION-ADMITTED**

## 1. Explicit fact identity

This experiment intentionally does not use bare `Lilith`.

```text
fact id         black_moon_lilith_mean_iers2003_v1
definition      IERS Conventions (2003) secular mean lunar apogee
formula         F + Omega - l + 180 degrees
frame           mean ecliptic / mean equinox of date
time argument   TT Julian centuries since J2000.0
normalization   mod 360 degrees
```

Mean, Osculating/True and Interpolated Black Moon Lilith remain different facts.

## 2. Why Swiss is not the same-definition oracle

The existing E3 research already establishes that Swiss `SE_MEAN_APOG` uses an ELP-hybrid mean-apogee treatment. The IERS candidate here is a secular fundamental-argument definition.

Therefore:

```text
ERFA/SOFA fundamental arguments
→ same-definition parity authority

XALEN / Meeus mean-perigee polynomial + 180°
→ independent analytical compatibility path

Swiss SE_MEAN_APOG
→ different-definition compatibility observation
→ not a same-definition pass/fail oracle
```

This distinction prevents an implementation from being bent merely to imitate a different `Mean Lilith` convention.

## 3. Prospective research contract

Before first execution, the temporary probe froze:

```text
candidate T window          -2.0 through +2.0 Julian centuries
approx calendar window      1800-2200
fixtures                    17
fixture spacing             0.25 Julian century

ERFA same-definition max    <= 0.0001 arcsec
XALEN/Meeus compatibility   <= 1.0 arcsec
Swiss                       report only; no gate
```

The 1800-2200 range is a **research validation window**, not a production-admitted date window. Production admission remains a later decision.

Temporary non-merge execution:

```text
PR                 #183
head               52fb14b65ce5adfe9a3c0b119e1426f58819c1ee
workflow run       36088099046
validate job       107924363210
merged             NO
```

No prospective numerical gate was widened after execution.

## 4. Pinned reference paths

| Role | Source | Revision |
|---|---|---|
| same-definition execution authority | `liberfa/erfa` | `1a8044cde5b7763295d472a6443387239127c6c8` |
| architecture cross-check | `TheDaniel166/moira` | `6dcc0fdaf35c16d96b544e03a509f2188603bc68` |
| independent analytical compatibility | `vedika-io/xalen-ephemeris` | `cc6edbec1f748ebdc4950ae6198f575c5ada73fa` |
| Swiss compatibility only | `astrorigin/pyswisseph` | `91ec65631badc7faf4a4b913570c944a4c1b101d` |

Research runtime versions were `pyerfa 2.0.1.5` and `pyswisseph 2.10.03`.

## 5. Measured result

| Path | Frozen gate | Observed max | Result |
|---|---:|---:|---|
| ERFA same definition | 0.0001″ | ~2.05e-10″ | PASS |
| XALEN/Meeus analytical compatibility | 1.0″ | 0.709806″ | PASS |
| Swiss different-definition compatibility | none | 416.343″ | REPORT ONLY |

Swiss compatibility residual across the 17 fixtures ranged from about **79.044″ to 416.343″**. That non-trivial gap is consistent with the definition boundary above; it is not treated as failure of the IERS candidate.

## 6. Research conclusion

```text
black_moon_lilith_mean_iers2003_v1
→ explicit identity
→ same-definition ERFA parity PASS
→ independent Meeus/XALEN compatibility PASS
→ no bare Lilith alias
→ no runtime network dependency
→ research candidate supported for later admission review
```

This does **not** add a production provider, provider capability, public schema field, interpretation claim or output contract.

Any future production admission must separately decide:

- production date window;
- provider/API ownership;
- schema/fact identity;
- interaction with existing Astrology Fact Gate;
- interpretation admission;
- regression and compatibility policy.

## 7. Files

- research implementation: `mean_lilith_iers2003_research.py`
- machine evidence: `astrology_exp2_mean_lilith_iers2003_parity.json`

