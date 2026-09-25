# AST-P1-005 query-bounded place shard transport contract

Status: **REFERENCE-ONLY / FORMAT CONTRACT SUPPORTED / PRODUCTION ADMISSION NOT GRANTED**

Temporary PR #189 (`fdf5fa8f3236984c05257d648b0907330a6ce7ae`) ran workflow `36097690832`, validate job `107953321687`, and was closed without merge.

Frozen research gates all passed across the four admitted population profiles:

- exact geonamescache 3.0.2 source identity: PASS;
- two independent split 3+3 builds: identical aggregate digest per profile;
- 13-query deterministic corpus semantic parity: 100% per profile;
- ambiguity preview: at most 10 candidate records;
- repeated same-query cache fetch: 0 bytes;
- maximum corpus query-visible bytes: 65,060 (500), 50,244 (1000), 21,831 (5000), 10,431 (15000), all below the frozen 100,000-byte gate.

Corpus coverage included unique, trim/casefold, Unicode/alternate-name, country-filtered, ambiguous, and not-found cases.

The durable format contract is now frozen under `data/astrology/place/v1/**` with manifest, provenance, attribution, exact source hashes, deterministic generator identity and query-derived path layout. The generated ~190 MB shard corpus is intentionally not committed by this change.

Remaining gates are real same-commit GitHub Connect exact-revision retrieval/integrity behavior, connector-side filtering/cache execution, cold-start latency/product validation, and a separate production admission review. Actions local filesystem timing is not evidence for GitHub Connect latency.

```text
format contract supported
≠ generated corpus committed
≠ GitHub Connect transport admitted
≠ production resolver materialization admitted
```


## GitHub Connect exact-revision probe — PR #208

Status: **BOUNDED CONNECTOR PROOF PASS / CACHE TELEMETRY UNAVAILABLE / NOT PRODUCTION ADMISSION**

A temporary non-merge branch/PR used two tiny research fixtures to test the actual connected GitHub retrieval surface at exact commit `d06a041e83322ccfbff936272a98c90a546dbb32`.

Observed:

- the fixture path was absent at base `3442611b1158dd3bf9dcd113c4b4fec232a0a94e` and retrievable at the exact probe head, establishing ref-sensitive same-repository retrieval;
- alias `fetch_file` returned Git blob `6d7004dd83b61352863b6bf17985ca1b5b87d587`; fetching that blob by SHA returned identical content;
- candidate `fetch_file` returned Git blob `4802945fe3d9d79643408d018b2c693a00a5ec8a`;
- repeated exact-ref retrieval returned the same blob/content identity;
- the client can perform path-bounded alias-first retrieval, apply country/ambiguity filtering locally, and retrieve candidate data only after a route survives; a not-found alias can terminate before candidate retrieval.

Limits:

- the connector does not expose cache-hit/network-byte telemetry, so repeated identical retrieval is **not** evidence of a zero-byte connector cache hit;
- filtering occurs in the ChatGPT orchestration layer after bounded alias retrieval, not inside the GitHub server/connector itself; therefore `connector-side filtering` is not an accurate requirement for this connector surface;
- tiny fixtures do not establish full generated-shard cold-start latency, worst-case payload, or full semantic parity.

PR #208 was closed without merge. Production admission remains unchanged.


## Real generated-shard probe — PR #210

Status: **REAL SHARD GENERATION PASS / REPO-FILE COLD-START LATENCY STILL OPEN / NOT PRODUCTION ADMISSION**

Temporary non-merge PR #210 generated real profile-500 split 3+3 shards from the exact admitted geonamescache 3.0.2 dataset. Workflow run 36139602395 succeeded and exported artifact 10866252034 (66,184-byte ZIP).

The bounded corpus covered 樹林區/TW, Tokyo/JP, Springfield ambiguous, Springfield/US and not-found. Routing preserved expected semantics: 樹林區 → 1668875; Tokyo → 1850147; Springfield ambiguity remained fail-closed with the same ordered route set; not-found returned no candidate buckets.

Observed real profile-500 shard sizes: alias 樹林區 13,700 B, Tokyo 18,401 B, Springfield 13,744 B; candidate shards used by the corpus were 3,714–6,120 B each. Every exported shard has a recorded SHA-256 identity in the artifact.

The first probe run 36139475713 generated the same files but failed only when Actions attempted to push them because workflow permission is contents: read. That permission was intentionally not widened; the succeeding probe used an artifact.

Boundary: artifact transport is not a same-commit repository file path. This probe strengthens real-shard payload/semantic evidence but does not claim GitHub Connect repo-file cold-start latency PASS. Production admission remains unchanged.
