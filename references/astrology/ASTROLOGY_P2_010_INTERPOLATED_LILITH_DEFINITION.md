# AST-P2-010 — Interpolated Black Moon Lilith Definition Research

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / NO PRODUCTION ADMISSION**

## Question

Does "Interpolated Black Moon Lilith" identify one provider-neutral mathematical object that this Playbook can implement as a generic local analytical fact, or is it a compatibility product whose definition must be named explicitly?

## Existing project boundary

The Playbook already keeps three Lilith identities separate:

```text
Mean Black Moon Lilith
Osculating / True Black Moon Lilith
Interpolated Black Moon Lilith
```

A bare `Lilith` alias is ambiguous. AST-P1-020 and AST-P1-030 established separate research identities for Mean and Osculating/True variants; neither implies an Interpolated definition.

## Swiss Ephemeris evidence

Supplemental review: `aloistr/swisseph@9083a12d59e98034fb2337061481ac8800c16e64`.

Relevant surfaces:

- `swephexp.h`: `SE_INTP_APOG = 21`;
- `sweph.c`: routes the distinct interpolated lunar-apogee product;
- `swemmoon.c`: `swi_intp_apsides(...)` computes the interpolated apsis with a dedicated iterative lunar-model procedure.

The algorithm sets the lunar mean anomaly to an apogee/perigee target, repeatedly evaluates the lunar model around that target, estimates the radial extremum, and refines the anomaly with decreasing step size. This is a specific provider definition; it is not "linear interpolation between Mean and Osculating Lilith".

Swiss remains REFERENCE-ONLY in this project. Its source/license path is dual AGPL / professional-license and no code is copied here.

## Independent implementation evidence

Reviewed `g-battaglia/libephemeris@37ffb0555b7a9f5083b4f1b6dc1a0f10feeb85fa` (AGPL-3.0).

Its current methodology defines a different smooth interpolated lunar-apogee curve:

```text
actual JPL DE440 apogee passages
→ mean apse baseline
→ Delaunay-argument fitted series
→ residual interpolation model
→ named INTP_APOG curve
```

The project explicitly distinguishes this from Mean and instantaneous Osculating apogee, and its comparison documentation records intentional non-zero divergence from Swiss between apsis passages.

This source is architecture / definition-boundary evidence only. Its AGPL code, coefficients, tables and generated model are not copied into this Playbook.

## Result

The evidence does **not** support a universal provider-neutral equation:

```text
"Interpolated Lilith" → one canonical numerical identity
```

Instead it supports:

```text
"Interpolated Lilith"
→ named compatibility / model family
→ explicit definition/provider required
```

At minimum, the following identities must not be silently conflated:

- Swiss `SE_INTP_APOG`;
- an independently defined JPL-anchored smooth apsis curve;
- any future project-owned interpolation/smoothing model.

## Production consequence

None.

This research does **not**:

- admit `black_moon_lilith_interpolated` as a production fact;
- choose Swiss as a production dependency;
- create a project-default interpolation algorithm;
- claim Swiss-exact compatibility for an independent curve;
- admit a bare `Lilith` alias;
- grant semantic interpretation authority.

A future production proposal must first name its compatibility target or mathematical definition, then separately satisfy license, provider/data provenance, date-window, numeric validation, schema/runtime, and interpretation gates.

## Closure decision

AST-P2-010 is complete as compatibility-definition research:

```text
definition family characterized
→ no provider-neutral default
→ explicit named definition/provider required
→ production admission remains NOT_GRANTED
```
