# Free ChatGPT Stochastic Transport Product Scenario

## Purpose

Validate the product-level Free ChatGPT cold-start transport path when repository routing succeeds but model-mediated opaque payload transfer is the remaining risk boundary.

This scenario is evidence for transport reliability only. It does not change stochastic authority, RNG semantics, method interpretation, or the fail-closed integrity gate.

## Preconditions

- Fresh Free ChatGPT session.
- GitHub Connect can read the current `masini1491/ai-divination-playbook` exact commit.
- Local stochastic runtime cache is absent or invalid.
- Python execution is available.
- A direct connector→Python byte-preserving full-runtime object bridge is unavailable.
- `RUNTIME_DRAW.md` cold-start recovery has been discovered.
- Preferred transport is `runtime/casting/capsule-v3/MANIFEST.json`.

## Stimulus

```text
依最新版 ai-divination-playbook 幫我代抽 5 張塔羅；本地 runtime 沒有時請照 Repo 的 cold-start recovery 執行。
```

## Required observed actions

1. Resolve and freeze one exact repository commit.
2. Read v3 `MANIFEST.json` from that exact commit.
3. Verify manifest schema, authority, source path, chunk count, encoded size, decoded size and final SHA metadata.
4. Fetch **one chunk file at a time** in ascending index order.
5. Derive one `verified_payload`: exclude at most one terminal LF from fetched file content; do not broad-trim any other character.
6. Immediately pass that exact `verified_payload` to Python and verify encoded length + SHA-256; retain that same representation in the accumulator.
7. Do not fetch the next chunk until the current chunk passes.
8. If one chunk mismatches, fresh-read only that same chunk path from the same exact commit and retry within the declared limit.
9. Keep already-passed verified payloads in the Python accumulator; do not overwrite them on another chunk retry.
10. After all chunks pass, concatenate **only retained verified payloads** in index order; never switch back to raw fetched file text. Then decode/decompress and verify final decoded size + SHA.
11. Materialize the verified canonical `core.py`, probe `runtime_invariants()`, then call `core.execute_stochastic()`.
12. Produce a valid Raw Draw / Cast Fact before interpretation.

## PASS

- All v3 chunks pass per-chunk verification and final canonical-byte verification, followed by canonical execution; or
- v3 is genuinely unavailable/blocked at the connector capability level and the agent uses the admitted v2 compatibility fallback, which itself completes exact verification and canonical execution.

## FAIL

- Agent loads all opaque chunks at once into model-visible context before transfer.
- Agent treats the first chunk mismatch as overall runtime unavailable without required same-chunk retry.
- Agent mixes chunks from different commits or memory.
- Agent executes before final decoded SHA passes.
- Agent broad-trims chunk text with `strip()`／`rstrip()` instead of excluding at most one terminal LF.
- Agent verifies a normalized chunk but later concatenates raw fetched file content or otherwise switches representation between verification and reassembly.
- Agent rewrites or substitutes stochastic code.
- Agent claims transport success based only on repository-side deterministic round-trip tests.
- Agent asks the user to draw manually while an applicable admitted transport path remains unexhausted.

## Product evidence

A formal product run should record only sanitized transport evidence:

- exact Playbook commit;
- transport contract/version;
- chunk count and chunk size;
- per-index PASS/RETRY/FAIL status;
- retry count;
- final decoded size/SHA PASS;
- runtime invariant PASS;
- canonical execution fact identity.

Do not commit private reading context, screenshots containing personal data, or the actual user question when it is sensitive.
