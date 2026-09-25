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
