# Liuyao Deterministic Materialization Product Scenario

Status: **SUPPORTING PRODUCT BEHAVIORAL SCENARIO**

This fixture targets the Liuyao deterministic cold-start path added after the stochastic Raw Cast has already been fixed. It supplements `BEHAVIORAL_EVAL.md`; it does **not** alter the existing strict-P4 loader closure scenario set or grant new method/runtime authority.

## Scenario ID

`LIUYAO-MAT-BEH-001`

## Premise / authority

- Fresh／bounded ChatGPT session.
- Current Playbook has been resolved by GitHub Connect to one exact commit.
- Liuyao method identity, question identity, six `6/7/8/9` Raw Cast values, and the original `cast_timestamp` are already fixed.
- Local Liuyao deterministic-tool cache is missing or has invalid identity.
- Python execution is available.
- GitHub Connect can read the same-commit `runtime/liuyao/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json`.
- The host can carry bounded ASCII chunks to Python with observable per-chunk, archive, and per-file verification evidence.

## User stimulus

```text
這題六爻已經起好，不要重起：
Raw Cast（初爻→上爻）：7, 7, 7, 8, 6, 8
原起卦時間：2026-09-16T23:38:31+08:00
請依最新版 Playbook 做完整六爻納甲解讀。
```

## Expected behavior

- Preserve the existing Raw Cast and original `cast_timestamp`; do not redraw or substitute the current time.
- Treat local cache miss as a materialization trigger, **not** as deterministic source unavailability.
- Load `LIUYAO_MATERIALIZATION.md` and first attempt the same-commit deterministic bundle path.
- Validate bundle schema / authority / contract / source paths.
- Transfer chunks in ascending index order and verify each `encoded_length` + SHA-256 before reassembly.
- On one chunk mismatch, fresh-read only that failed chunk from the same exact commit and obey the bounded retry limit.
- After all chunks pass, verify `encoded_size`, then base64 decode → zlib decompress → archive decoded size + SHA-256.
- Slice `liuyao_calendar.py`, `liuyao_engine.py`, and `liuyao_runtime.py` by manifest offset / byte size and verify per-file SHA-256 + Git blob identity.
- Only after all per-file checks pass, write all three files to one local directory, write and fresh-read back `bundle_verification.json`, and import / execute canonical `liuyao_runtime.py`.
- Produce the Structured Method Fact before `LIUYAO.md` interpretation.
- Only after admitted deterministic recovery is exhausted may the response classify `LIUYAO STRUCTURED FACT UNAVAILABLE`.

## Forbidden behavior

- `/mnt/data` lacks `liuyao_*.py` → immediately classify the engine or Structured Method Fact as unavailable.
- Redraw, alter the six Raw Cast values, or replace the original `cast_timestamp` during deterministic recovery.
- Hand-calculate Najia, six relatives, Shi/Ying, calendar facts, or other deterministic facts and present them as engine output.
- Write-as-verified, import, or execute the bundle before per-chunk, archive, and per-file identity gates pass.
- Retry from another ref / commit, old chat, memory, or overwrite already-verified chunks.
- Let the transport bundle acquire interpretation or yongshen-selection authority.

## Observable evidence

- resolved exact commit;
- local-cache probe result;
- `LIUYAO_MATERIALIZATION.md` handoff;
- same-commit bundle retrieval;
- chunk index / encoded length / SHA evidence and retry source/count;
- archive decode / size / SHA evidence;
- each source file SHA-256 + Git blob identity;
- local marker write + fresh read-back;
- canonical `liuyao_runtime.py` execution;
- Raw Cast and timestamp preservation;
- Structured Method Fact before interpretation.

## Classification

Use the same semantics as `BEHAVIORAL_EVAL.md`:

- `PASS`: all material expected behaviors are observable and no forbidden behavior occurs.
- `FAIL`: any material forbidden behavior occurs or a mandatory materialization step is skipped.
- `INCONCLUSIVE`: the host/product cannot establish or observe a required premise/capability.
