# Astrology Place Resolver Materialization Feasibility｜A-MAT-2

Status: **DECISION / EVIDENCE REPORT**

Decision: **DO NOT ADMIT MODEL-MEDIATED PLACE-RESOLVER COLD-START TRANSPORT AT THIS TIME**

This report closes the current A-MAT-2 feasibility question for `geonamescache==3.0.2`. It does not revoke the existing production admission of `tools/astrology_place_resolver.py`; it only defines what ChatGPT may claim or attempt when that admitted resolver runtime is absent.

## 1. Authority / baseline

Target Playbook observed during closure:

```text
masini1491/ai-divination-playbook
main@936bc376413f1f16a8690b5cb41c5cb2f022b9d9
```

Resolver authority:

```text
tools/astrology_place_resolver.py
ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json

geonamescache==3.0.2
yaph/geonamescache@df4f6497b321f7981645ab0c5c77d3354c63bd01
software license: MIT
GeoNames dataset: CC-BY-4.0
attribution required
```

Relevant GitHub Actions evidence runs:

- package/runtime byte inspection: run `35953638622`
- resolver-index/shard feasibility: run `35953811283`

Both workflows were temporary branch-only evidence collectors and self-deleted their branches.

## 2. Installed package identity / size evidence

Pinned `geonamescache==3.0.2` wheel download observed by pip:

```text
35.0 MB
```

Installed distribution:

```text
ALL_DIST_FILE_COUNT = 22
ALL_DIST_BYTES      = 187,204,618
```

Minimum files required by the current resolver implementation and admitted population profiles:

| File | Bytes | SHA-256 |
|---|---:|---|
| `geonamescache/__init__.py` | 4,267 | `7f475fe5fdb4e6479fce15b0016318df2b40eb25a30dfabc016af27523a8d6b6` |
| `geonamescache/types.py` | 3,807 | `4ca8a2be0c060a341074ddd6662f973e0f057e9e465ffdad3caa815617c1428a` |
| `data/countries.json` | 91,860 | `41c01b0843461207e71ba7530434738a4e7a7c84efd72aba03f547f450ca1ba4` |
| `data/cities500.json` | 79,527,431 | `1523be8c6f083eeee946e1c27a0916474d0f0de4361a15104fcc70218bc4d55e` |
| `data/cities1000.json` | 60,986,259 | `a6dffc566a3196e0995c7925defdafa548bb8a8fa951d6ab2ea78abedeb0dd60` |
| `data/cities5000.json` | 29,665,391 | `6f65c327a0f7374cb7ee629ed6e5128d6d3a2a4d92ed98fc7629690f5074ed55` |
| `data/cities15000.json` | 16,670,875 | `24e87d89c775305650301618fa434d26e47e1b64ba5e27a5611e0f351908fd11` |

Minimum total:

```text
186,949,890 bytes
178.289 MiB
```

The package license payload was also observed and hashed:

```text
geonamescache-3.0.2.dist-info/licenses/LICENSE
1082 bytes
sha256 f36856c5030b93e11b7b2c0f799e080999e9af3017e9d7607b40ffaf0d66e304
```

## 3. Population-dataset parity check

Dataset record counts:

```text
500   → 234,908
1000  → 170,391
5000  →  69,472
15000 →  34,006
```

A tempting optimization would be to keep only `cities500.json` and derive the higher-threshold datasets by filtering each row's `population`.

That is **not semantically equivalent**.

Observed parity:

```text
1000:
  population-filter-only = 236
  dataset-only           = 23,108
  exact equality         = false

5000:
  population-filter-only = 124
  dataset-only           = 647
  exact equality         = false

15000:
  population-filter-only = 63
  dataset-only           = 45
  exact equality         = false
```

Therefore A-MAT-2 must not silently collapse the four admitted dataset profiles into one population-filtered dataset.

## 4. Derived compact-index experiment

A compact exact-alias index was generated from the admitted `cities500` data for feasibility measurement only.

Observed cardinality:

```text
aliases    = 1,010,394
candidates =   234,908
```

Combined compact payload:

```text
raw        = 47,750,998 bytes
zlib       = 12,828,903 bytes
base64     = 17,105,204 chars
444-char chunks = 38,526
```

Naive hash-shard experiment:

| Shards | Avg compressed bytes | Max compressed bytes | Max 444-char chunks | P95 chunks |
|---:|---:|---:|---:|---:|
| 64 | 629,657.5 | 1,708,546 | 5,131 | 1,868 |
| 128 | 338,150.7 | 1,419,998 | 4,265 | 1,012 |
| 256 | 179,137.2 | 1,269,996 | 3,814 | 540 |
| 512 | 94,358.8 | 1,182,843 | 3,553 | 288 |
| 1024 | 49,635.3 | 1,138,998 | 3,421 | 155 |

This experiment does **not** establish a production shard design. It shows that straightforward model-mediated sharding still has unacceptable worst-case handoff cost and would add a large generated-data surface.

## 5. Decision

Current production behavior remains:

```text
A. admitted geonamescache resolver already executable
   → place / country name resolution allowed under existing admission

B. resolver unavailable, but explicit latitude + longitude + IANA timezone supplied
   → use A-MAT-1 core materialization
   → natal/transit production can continue

C. resolver unavailable and only place / country name supplied
   → ask for explicit coordinates + IANA timezone
   → no generic-web geocoder fallback
   → no language-model coordinate/timezone guess
   → no silent dataset/profile substitution
```

No `ASTROLOGY_PLACE_RESOLVER_BUNDLE` is admitted by this report.

## 6. Why this is a closure, not an unfinished implementation

The current question was whether the existing admitted resolver should be productized using the same model-mediated deterministic bundle pattern as Astrology core / Zi Wei.

Evidence says **no** for the current package/data shape:

- exact wheel/runtime transport is too large for the intended ordinary ChatGPT cold-start path;
- naive compact/sharded transport remains costly at worst case;
- removing higher-threshold datasets would change admitted semantics;
- web geocoding would change source authority and privacy/network behavior.

The safe product boundary already exists because A-MAT-1 separated core astronomy from place resolution.

## 7. Re-open triggers

A-MAT-2 may be reopened if one of these materially changes:

1. ChatGPT gains a host-native byte-preserving artifact bridge for a pinned 35 MB+ resolver artifact without model-token transport.
2. A query-bounded derived resolver index is designed with exact parity, bounded worst-case retrieval, deterministic provenance, attribution, and product validation.
3. The production resolver profile itself is deliberately changed and re-admitted with a smaller authoritative dataset.
4. A different offline resolver/provider is researched and independently admitted.

Until then, `place_resolver_materialization_status = not-admitted-for-cold-start` is the current machine-readable decision.
