# Zi Wei Deterministic Tool Materialization｜紫微 deterministic runtime 按需載入契約

Status: **TASK-SPECIFIC CANONICAL CONTRACT**

本檔只在 explicit Zi Wei production 已命中 `ZIWEI.md`，但 ChatGPT local runtime 缺少 verified Zi Wei deterministic tools、calendar manifest 或本次 Gregorian input 所需 year shard 時載入。它不取得 routing、interpretation、claim admission 或 research authority。

## 1. Canonical authority

Repo-local authority：

```text
tools/ziwei_runtime.py
tools/ziwei_calendar_provider.py
tools/ziwei_calendar_data_provider.py
data/calendar/ziwei_tw_interval/v1/MANIFEST.json
schemas/ziwei/ZIWEI_READING_REQUEST_V1.schema.json
schemas/ziwei/ZIWEI_READING_RESULT_V1.schema.json
tools/ziwei_natal_provider.py
tools/ziwei_sihua_provider.py
tools/ziwei_claim_retrieval.py
tools/ziwei_delivery.py
ZIWEI_CALENDAR_ADMISSION_V1.json
ZIWEI_SIHUA_ADMISSION_V1.json
```

Production Gregorian calendar runtime 使用 repo-local interval data。Pinned build source：

```text
lunar_python==1.4.8
6tail/lunar-python@000c8a3d74eed098d6256a28fdd51b869324c559
MIT
build/parity dependency only
```

ordinary production runtime **不 import、pip install 或 materialize lunar_python**。

`runtime/ziwei/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json` 仍只是 CI-generated **derived transport cache**；不得成為第二套 calculation / interpretation authority。

## 2. Local cache miss is not source unavailability

**local cache miss ≠ Zi Wei unavailable**。聊天室沒有 repo checkout、沒有 Zi Wei source、沒有 calendar manifest 或缺少本次需要的 year shard，都先走 same-commit verified materialization；不得由模型手算補齊。

### Explicit Minguo-year notation pre-adapter

明確民國紀年仍先取同 exact commit 的 `tools/ziwei_year_notation.py`：

```text
explicit 民國 year
→ same-commit tools/ziwei_year_notation.py
→ deterministic CE year
→ GregorianBirthInput
→ ordinary Zi Wei materialization path
```

converted Gregorian date仍必須落在 admitted 1900-01-01..2100-12-31 range。

## 3. Preferred cold-start path

```text
explicit Zi Wei Gregorian request
→ resolve ai-divination-playbook current main to exact commit
→ verify/reuse matching /mnt/data/divination-ziwei-runtime cache
→ cache MISS / invalid
   → fetch same-commit runtime/ziwei/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
   → verify chunk/archive/per-file identities
   → materialize repo-local runtime + calendar MANIFEST.json
→ derive required shard path(s) from Gregorian input
   ordinary Gregorian request → 1 year shard
   31 December 23:00 cross-year edge → at most 2 year shards
→ fetch only required same-commit data/calendar/ziwei_tw_interval/v1/years/YYYY.json
→ verify each shard path + byte count + SHA-256 against bundled manifest
→ execute tools/ziwei_runtime.py
→ deterministic Scope-A facts / admitted claims
→ ZIWEI.md bounded synthesis
```

Calendar shards are **query-bounded** data acquisitions，不得為方便把完整202-shard dataset塞進 bundle或 active Context。successful materialization **does not require pip/network installation afterward**；GitHub Connect exact-commit shard retrieval本身仍是 acquisition step。

## 4. Verified cache

Default cache：

```text
/mnt/data/divination-ziwei-runtime/
bundle_verification.json
data/calendar/ziwei_tw_interval/v1/MANIFEST.json
data/calendar/ziwei_tw_interval/v1/years/<needed>.json
```

marker必須綁定 repository、playbook commit、bundle contract、archive SHA、calendar dataset identity、build-source provenance與 materialized files。year shard只能在同 commit manifest identity一致時 reuse。

## 5. Fallback / fail closed

Bundle無法取得／驗證，或 required same-commit shard無法取得／通過 manifest identity驗證時，可退回同 exact commit 的 direct repo-source materialization；authority與 hash contract不變。

只有 admitted bundle/direct-source路徑與 query-bounded calendar data都無法成立，或 Python execution不可用／verified source execution failure，才分類：

```text
ZI WEI DETERMINISTIC RUNTIME UNAVAILABLE
```

不得 fallback到模型手算農曆，也不得改用 Tarot / Meihua / Liuyao冒充 Zi Wei。

## 6. Authority boundary

```text
GitHub Connect → acquisition authority
bundle → runtime + calendar-manifest derived transport cache
query-bounded year shard(s) → same-commit deterministic data
ZIWEI_CALENDAR_ADMISSION_V1.json → production calendar admission truth
pinned lunar-python → build/parity source only
tools/ziwei_runtime.py → canonical typed production composition
tools/ziwei_sihua_provider.py → optional profile-bound Four-Transformation calculation facts; no interpretation authority
Zi Wei providers + retrieval/delivery → deterministic facts + admitted claims; `sihua_v1` additionally requires bundled `ziwei_interpretation_claim_registry_sihua_v0.json`
ZIWEI.md → interpretation / output governance
```

核心原則：**transport runtime與calendar data分離；bundle不搬完整dataset，ordinary request只取最低充分1個 shard，跨年晚子時最多2個，全部綁同 exact commit與manifest hash後才執行。**
