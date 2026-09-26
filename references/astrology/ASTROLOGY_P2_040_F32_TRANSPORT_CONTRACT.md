# AST-P2-040 — Float32 Query-Bounded Transport Projection Contract

Status: **PROSPECTIVE / FROZEN BEFORE FIRST EXTERNAL VALIDATION / NOT YET ADMITTED**

This sub-review addresses only the GitHub-Connect transport/storage layer after the exact float64 C1 dataset passed the frozen AST-P2-040 production probe.

The frozen projection is:

```text
admitted research representation: c1-cheb-d7-w60 float64
→ for each object/segment: c0 := c0 mod 360°
→ cast all 8 coefficients to IEEE-754 float32 little-endian
→ pack 192 segments per transport shard
→ runtime evaluates one shard / one segment, no blending, no network
```

Why `c0 mod 360°` is allowed: Chebyshev `T0(x)=1`, so subtracting an integer multiple of 360° from c0 subtracts the same constant from the polynomial. Modulo-360 longitude is unchanged, while its derivative is exactly unchanged before float quantization.

Frozen transport envelope:

- 511,840 raw coefficient bytes total;
- 17 transport shards;
- at most 30,720 raw bytes / 40,960 base64 transport characters per shard;
- degree 7 / 60-day segment topology unchanged.

New holdout dates, frozen before first external validation:

- `P2-040-Q01` — `1834-02-11T01:13:00Z`
- `P2-040-Q02` — `1866-12-16T07:37:00Z`
- `P2-040-Q03` — `1899-10-20T13:53:00Z`
- `P2-040-Q04` — `1932-08-24T19:23:00Z`
- `P2-040-Q05` — `1965-06-28T01:13:00Z`
- `P2-040-Q06` — `1998-05-02T07:37:00Z`
- `P2-040-Q07` — `2031-03-06T13:53:00Z`
- `P2-040-Q08` — `2064-01-08T19:23:00Z`
- `P2-040-Q09` — `2096-11-11T01:13:00Z`
- `P2-040-Q10` — `2129-09-16T07:37:00Z`
- `P2-040-Q11` — `2162-07-21T13:53:00Z`
- `P2-040-Q12` — `2195-05-25T19:23:00Z`
- `P2-040-Q13` — `2228-03-29T01:13:00Z`
- `P2-040-Q14` — `2261-01-31T07:37:00Z`
- `P2-040-Q15` — `2293-12-05T13:53:00Z`
- `P2-040-Q16` — `2326-10-09T19:23:00Z`

All five objects are validated at all 16 dates (80 rows) against direct Horizons. Frozen gates remain:

```text
longitude p95 <= 10 arcsec
longitude max <= 30 arcsec
speed max     <= 0.001 deg/day
```

This transport projection does not widen production scope, add meanings/aspects/transits/unknown-time facts, or change source authority.
