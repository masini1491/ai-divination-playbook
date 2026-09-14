# Astrology Extended Chart Facts Phase E4｜Fortune, Vertex, Equatorial Ascendant

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / COMPATIBILITY LABELS POLICY-GATED / NOT PRODUCTION-ADMITTED**

Baseline: `masini1491/ai-divination-playbook@40d4938bb3f265d332608312463b550fb8b8aa13`

## 1. Scope

Phase E4 separates three deterministic special-point families:

```text
Part of Fortune
Vertex
Equatorial Ascendant
```

Consumer aliases such as `East Point` are not silently promoted to canonical identity.

## 2. Part of Fortune

Pinned Kerykeion research source `g-battaglia/kerykeion@b18848eb8e1e0a2b09a096dbb9688c8404dfb06b` documents and tests the day/night formulas:

```text
diurnal:   Asc + Moon - Sun
nocturnal: Asc + Sun - Moon
```

Normalize to `[0, 360)` after arithmetic.

Recommended policy id:

```text
fortune-day-night-v1
```

Required provenance:

```text
ASC longitude
Sun longitude
Moon longitude
diurnal/nocturnal classification
sect policy id
formula policy id
normalized result
```

The formula must not be reversed merely to match a consumer output.

### 2.1 Diurnal / nocturnal classification

The same pinned Kerykeion evidence defines a day chart as the Sun above the horizon and a night chart as the Sun below it, and records that its `is_diurnal` classification uses the Sun's **geometric altitude** via Swiss Ephemeris `swe.azalt()`. This makes the classification independent of house system and zodiac mode.

For this research line, freeze the deterministic candidate policy:

```text
sect-geometric-solar-altitude-v1

Sun geometric altitude > 0° → diurnal
Sun geometric altitude < 0° → nocturnal
Sun geometric altitude = 0° → boundary / FAIL CLOSED
calculation unavailable      → FAIL CLOSED
```

The upstream package has a defensive fallback behavior when sect calculation fails; this Playbook does **not** inherit that fallback into the research contract. An unavailable classification must remain unavailable rather than silently becoming diurnal.

This policy is still REFERENCE-ONLY; it does not alter Production v1.

## 3. Vertex

Pinned Swiss source `aloistr/swisseph@91339e55d2351f32548d8a8d5bca6aa93b4f6da7` explicitly returns:

```text
ascmc[0] Ascendant
ascmc[1] MC
ascmc[2] ARMC
ascmc[3] Vertex
ascmc[4] Equatorial Ascendant
```

Therefore Vertex is an independent house/angle calculation output, not an alias for ASC/DSC/MC/IC and not derivable by a simple 180-degree operation from one of those four angles.

Recommended deterministic id:

```text
vertex
```

Its opposite may be represented separately as `anti_vertex` if a future surface needs it; do not infer that such an alias is production-admitted from E4 alone.

## 4. Equatorial Ascendant

The same pinned Swiss source defines `SE_EQUASC = 4` and labels it `equatorial ascendant`.

Recommended deterministic id:

```text
equatorial_ascendant
```

This is distinct from ordinary Ascendant.

## 5. “East Point” compatibility label

Some consumer astrology software uses `East Point` for the Equatorial Ascendant. The private consumer-chart compatibility investigation associated with this research was numerically consistent with that interpretation, but private identifying inputs are intentionally not repository evidence.

Repository-safe rule:

```text
canonical fact identity: equatorial_ascendant
consumer alias: East Point
alias status: COMPATIBILITY_POLICY, not mathematical name
```

A source that says `East Point` should be matched to `equatorial_ascendant` only when its definition or numerical behavior establishes the equivalence.

## 6. Location/time sensitivity

Vertex and Equatorial Ascendant are location/time-derived special points. Their validation must use public/synthetic coordinates and multiple locations rather than personal natal records.

They belong in the angle/special-point fact family, not the ephemeris-body family.

Part of Fortune also requires the chart instant/location indirectly through ASC and through the sect classification.

## 7. House-system independence boundary

These outputs come from a house/angle calculation API, but their identity must not be replaced by convenient house cusps. As established in E1, angle identity and house-cusp identity remain separate even when a particular house system makes them numerically coincide.

The `sect-geometric-solar-altitude-v1` classification is likewise not defined by a house number; it uses geometric horizon altitude explicitly.

## 8. E4 conclusion

```text
Fortune day/night formula          RESOLVED AS fortune-day-night-v1
sect classification candidate      RESOLVED AS sect-geometric-solar-altitude-v1
sect failure behavior              FAIL CLOSED
Vertex identity                    RESOLVED
Equatorial Ascendant identity      RESOLVED
“East Point” canonical math name   NOT USED
“East Point” compatibility alias   POLICY-GATED
production admission               NOT GRANTED
```

E4 research can complete without deciding whether a future product displays the consumer label `East Point`.
