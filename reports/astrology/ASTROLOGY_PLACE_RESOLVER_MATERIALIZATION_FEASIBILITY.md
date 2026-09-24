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


## 8. Re-open evidence — query-bounded alias-hash shard POC

Status: **FEASIBILITY PASS / NOT PRODUCTION ADMISSION**

A-MAT-2 re-open trigger 2 was exercised on a research-only branch in PR #172.

Evidence identity:

```text
branch: research/astrology-place-shard-poc
benchmark head: 7871af51467e8183e79e4e054ca157098a6aba15
workflow: Astrology Place Shard POC
run: 36033683587
job: 107748401932
artifact: astrology-place-shard-benchmark
artifact id: 10823938328
artifact digest: sha256:69b0da4440c0fab690e8ee0e0bfef0f76a55fcffc17ff1047c2db4563fc029b9
```

The POC first verified the installed `geonamescache==3.0.2` dataset bytes against the identities already recorded by this report. All four profiles matched exactly:

| Profile | Bytes | SHA-256 identity |
|---:|---:|---|
| 500 | 79,527,431 | PASS |
| 1000 | 60,986,259 | PASS |
| 5000 | 29,665,391 | PASS |
| 15000 | 16,670,875 | PASS |

The benchmark then preserved the current resolver's exact case-insensitive alternate-name semantics, hashed the full normalized alias with SHA-256, and measured 2/3/4 hexadecimal-prefix shard widths. Each profile remained separate; no population-filter substitution was used.

| Profile | Hex chars | Non-empty shards | P95 bytes | P99 bytes | Max bytes | Total serialized bytes |
|---:|---:|---:|---:|---:|---:|---:|
| 500 | 2 | 256 | 474,340 | 482,034 | 482,599 | 117,909,047 |
| 500 | 3 | 4,096 | 33,018 | 35,169 | 42,531 | 120,558,937 |
| 500 | 4 | 65,536 | 2,848 | 3,443 | 16,532 | 127,096,383 |
| 1000 | 2 | 256 | 385,683 | 390,847 | 393,192 | 95,678,047 |
| 1000 | 3 | 4,096 | 27,115 | 28,923 | 35,773 | 98,130,586 |
| 1000 | 4 | 65,536 | 2,383 | 2,865 | 13,081 | 104,717,330 |
| 5000 | 2 | 256 | 228,395 | 233,406 | 234,311 | 56,266,076 |
| 5000 | 3 | 4,096 | 16,447 | 17,532 | 19,681 | 58,251,241 |
| 5000 | 4 | 65,508 | 1,576 | 1,880 | 5,118 | 64,804,259 |
| 15000 | 2 | 256 | 148,211 | 150,161 | 152,803 | 36,007,647 |
| 15000 | 3 | 4,096 | 10,915 | 11,642 | 13,820 | 37,639,163 |
| 15000 | 4 | 65,119 | 1,136 | 1,373 | 2,908 | 44,190,300 |

Fixture parity was PASS for every profile × shard-width combination.

Representative `cities500` query-bounded payloads:

| Query | Country | 2 hex | 3 hex | 4 hex | Exact candidates |
|---|---|---:|---:|---:|---:|
| 樹林區 | TW | 460,943 B | 29,303 B | 1,432 B | 1 |
| Tokyo | JP | 467,588 B | 42,189 B | 1,373 B | 1 |
| Springfield | none | 442,749 B | 29,949 B | 3,669 B | 21 |
| Springfield | US | 442,749 B | 29,949 B | 3,669 B | 20 |

The ambiguity result is intentional: the derived transport preserves the current resolver's fail-closed candidate semantics rather than selecting the largest-population record.

### 8.1 Current design conclusion

The POC materially changes the feasibility evidence but **does not change current production behavior**.

- 2-hex / 256-shard design is still unnecessarily large for query-bounded retrieval.
- 4-hex / 65,536-shard-per-profile design minimizes per-query payload but creates an excessive generated-file surface.
- **3-hex / 4,096-shard-per-profile is the current architecture candidate**: even the largest `cities500` shard was 42,531 bytes and P95 was 33,018 bytes while keeping the theoretical file surface to 16,384 shards across the four admitted profiles.
- Whole generated storage remains larger than the source datasets because candidate payloads are replicated across alias buckets. This is acceptable for the feasibility result but should be considered before freezing the external repository format.
- The benchmark establishes a viable query-bounded transport representation. It does not yet establish external-repository provenance, manifest/hash layout, cache policy, GitHub Connect end-to-end retrieval, product latency, or production admission.

Therefore the original A-MAT-2 decision remains valid for the old **model-mediated whole-package / chunk transport**. Re-open trigger 2 is now satisfied at the feasibility layer, and a separate query-bounded transport admission study may proceed without silently changing current resolver behavior.


## 9. Split alias-index + candidate-store POC

Status: **FEASIBILITY PASS / CURRENT FORMAT CANDIDATE SELECTED / NOT PRODUCTION ADMISSION**

PR #173 compared the current 3-hex inline alias+candidate representation against a split transport:

```text
alias lookup: SHA-256(normalized exact alias) → 3-hex alias shard
alias shard route payload: geoname_id + country_code + population + canonical name
candidate lookup: SHA-256(geoname_id) → candidate shard
candidate record: current admitted PlaceCandidate fields
```

The route payload is intentionally sufficient to preserve country filtering and the current resolver sort order before any full candidate record is fetched. A unique match requires one candidate record; an ambiguous match materializes only the first ten sorted candidates needed by the current error preview.

Evidence identity:

```text
branch: research/astrology-place-shard-split-poc
benchmark head: 742c7899478aa6790daa5f6f809949f13f75150d
workflow: Astrology Place Split Shard POC
run: 36035872538
job: 107755709035
artifact: astrology-place-split-shard-benchmark
artifact id: 10825181328
artifact digest: sha256:d4ec99fd8ab9e008855ff5f81a9bcb06a00695552541cc64a73cf6bacfda8748
```

The exact `geonamescache==3.0.2` dataset identities from A-MAT-2 again matched before the comparison was accepted. All tested split designs preserved fixture parity for 樹林區/TW, Tokyo/JP, Springfield without country, and Springfield/US across all four admitted population profiles.

### 9.1 Storage comparison

Current inline 3-hex total serialized storage across the four profiles:

```text
314,579,927 bytes
```

Split alias-3hex + candidate-3hex total serialized storage:

```text
189,935,792 bytes
```

This is a reduction of approximately **39.6%** while preserving the same source datasets and the tested exact-match semantics.

| Profile | Inline 3-hex total | Split alias-3 + candidate-3 total | Alias P95 | Alias max | Candidate P95 | Candidate max |
|---:|---:|---:|---:|---:|---:|---:|
| 500 | 120,558,937 | 75,168,066 | 15,142 | 18,809 | 5,887 | 7,268 |
| 1000 | 98,130,586 | 60,190,165 | 12,596 | 15,946 | 4,457 | 6,197 |
| 5000 | 58,251,241 | 33,557,450 | 7,700 | 9,287 | 2,103 | 2,884 |
| 15000 | 37,639,163 | 21,020,111 | 5,140 | 6,463 | 1,201 | 1,798 |

The split 3+3 design has a theoretical file surface of 8,192 shards/profile, or 32,768 shard paths across the four admitted profiles.

### 9.2 Query-bounded retrieval comparison

Representative `cities500` split 3+3 payloads:

| Query | Country | Alias shard | Candidate buckets | Candidate bytes | Total lookup bytes | Match count |
|---|---|---:|---:|---:|---:|---:|
| 樹林區 | TW | 13,710 | 1 | 4,784 | 18,494 | 1 |
| Tokyo | JP | 18,411 | 1 | 5,291 | 23,702 | 1 |
| Springfield | none | 13,754 | 10 | 49,315 | 63,069 | 21 |
| Springfield | US | 13,754 | 10 | 49,315 | 63,069 | 20 |

For comparison, the previous inline 3-hex `cities500` fixture shards were 29,303 bytes for 樹林區, 42,189 bytes for Tokyo, and 29,949 bytes for Springfield. The split design improves unique-match payload and total generated storage; ambiguous queries may require multiple candidate-store reads because the current resolver exposes a ten-candidate preview.

### 9.3 Candidate-store width trade-off

Candidate 2-hex keeps the file surface small but makes ambiguous retrieval too expensive: `cities500` Springfield required 701,598 bytes total lookup.

Candidate 4-hex minimizes lookup bytes further — `cities500` 樹林區 14,248 bytes and Springfield 18,283 bytes — but raises the theoretical file surface to 69,632 paths/profile, or 278,528 across four profiles.

**Current format candidate: alias 3-hex + candidate 3-hex.**

It is the best measured balance in this POC between:

- total generated storage;
- bounded unique lookup;
- bounded ambiguity preview;
- generated-file surface;
- exact source/profile preservation;
- current country-filter / ambiguity / preview semantics.

### 9.4 Remaining admission boundary

This POC selects a transport-format candidate but still does **not** admit it for production. Remaining work is now narrower:

1. define the external generated-data repository contract, manifest, schema version, source SHA identities, per-shard integrity and CC-BY attribution;
2. make the generator build the alias index once per profile and derive candidate stores without repeated alias work;
3. prove end-to-end GitHub Connect exact-revision retrieval, integrity verification, cache behavior and connector-side filtering;
4. expand semantic parity beyond the bounded fixtures to a deterministic corpus covering not-found, country filters, Unicode/casefold aliases and high-ambiguity names;
5. benchmark end-to-end cold-start latency and actual model-visible payload;
6. only after those gates pass, consider a separate change to `ASTROLOGY_MATERIALIZATION.md` and production admission.

The original A-MAT-2 prohibition remains applicable to whole-package/model-mediated cold-start transport. The query-bounded external-shard lane now has a selected research format candidate but no production authority yet.
