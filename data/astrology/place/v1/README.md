# Astrology place shard data v1

Status: **FORMAT CONTRACT FROZEN / GENERATED DATA NOT YET COMMITTED / NOT PRODUCTION-ADMITTED**

Authority chain:

```text
GeoNames / geonamescache==3.0.2 exact source bytes
→ tools/generate_astrology_place_shards.py
→ data/astrology/place/v1/**
→ future reviewed query-bounded resolver transport
```

The selected format is split alias-3hex + candidate-3hex. Alias shards contain routing metadata only; candidate shards contain the admitted `PlaceCandidate` fields. Paths are derived directly from SHA-256 prefixes and never require tree enumeration.

This directory intentionally does not yet contain the ~190 MB generated shard corpus. AST-P1-005 still requires same-commit GitHub Connect retrieval/integrity/product validation before production admission can change.

See `MANIFEST.json`, `provenance.json`, and `ATTRIBUTION.md`.
