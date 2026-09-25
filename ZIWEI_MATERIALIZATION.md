# Zi Wei Deterministic Tool Materialization｜紫微 deterministic runtime 按需載入契約

Status: **TASK-SPECIFIC CANONICAL CONTRACT**

本檔只在 explicit Zi Wei production 已命中 `ZIWEI.md`，但 ChatGPT local runtime 缺少 verified Zi Wei deterministic tools 或 Gregorian input 所需的 exact calendar year shard 時載入。它不取得 routing、interpretation、claim admission 或 research authority。

## 1. Canonical authority

Repo-local production authority：

```text
tools/ziwei_runtime.py
tools/ziwei_calendar_provider.py
tools/ziwei_gregorian_pipeline.py
tools/ziwei_natal_provider.py
schemas/ziwei/ZIWEI_READING_REQUEST_V1.schema.json
schemas/ziwei/ZIWEI_READING_RESULT_V1.schema.json
tools/ziwei_scope_a_pipeline.py
tools/ziwei_brightness_provider.py
tools/ziwei_m0_auxiliary_provider.py
tools/ziwei_brightness_pipeline.py
tools/ziwei_claim_retrieval.py
tools/ziwei_delivery.py
3 base admitted claim registries + optional M0 auxiliary claim registry
data/calendar/ziwei_tw_interval/v1/**
```

Gregorian production data authority由 `ZIWEI_CALENDAR_ADMISSION_V1.json` 綁定到：

```text
dataset: ziwei_tw_interval_1900_2100_candidate_v1
range: 1900-01-01..2100-12-31
aggregate: 4913a39e770afcd21eedc387523c572b8c4fc6469889c28f6ea75613f8984d79
ordinary query: 1 year shard
31 Dec 23:xx year-edge query: 2 year shards including policy tail
```

Pinned `lunar_python==1.4.8` / `6tail/lunar-python@000c8a3d74eed098d6256a28fdd51b869324c559` is **build/parity-only**. Ordinary production materialization does not bundle or import it.

`runtime/ziwei/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json` is CI-generated **derived transport cache** for repo-local runtime/retrieval source only；不得成為第二套 calculation / interpretation authority。

## 2. Local miss is not source unavailability

聊天室沒有 repo checkout、沒有 Zi Wei runtime、或沒有 calendar shard，本身都不等於 Zi Wei deterministic runtime unavailable。若 GitHub Connect exact-commit retrieval 與 Python execution 可用，先完成同 commit runtime bundle + query-bounded calendar data materialization。

### Explicit Minguo-year notation pre-adapter

使用者明確提供民國年份時，先取同 commit `tools/ziwei_year_notation.py`：

```text
explicit 民國 year
→ same-commit tools/ziwei_year_notation.py
→ deterministic CE year = 民國 year + 1911
→ GregorianBirthInput
→ ordinary Zi Wei deterministic materialization path
```

converted Gregorian date仍必須落在 admitted 1900-01-01..2100-12-31。helper retrieval / execution 失敗時不得模型心算代替。

## 3. Preferred cold-start path

```text
explicit Zi Wei request
→ resolve ai-divination-playbook current main to exact commit
→ probe /mnt/data/divination-ziwei-runtime/bundle_verification.json
→ bundle cache MISS / invalid
   → fetch same-commit runtime/ziwei/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
   → validate schema / authority / contract
   → verify every chunk length + SHA-256
   → index-order concat
   → base64 decode + zlib decompress
   → verify archive size + SHA-256
   → slice every source_file by offset / byte_size
   → verify per-file SHA-256 + Git blob identity
   → write exact paths under /mnt/data/divination-ziwei-runtime/
   → write + fresh-read bundle_verification.json
→ Gregorian input only:
   → import materialized tools.ziwei_calendar_provider
   → call required_calendar_shards(GregorianBirthInput(...))
   → fetch each returned data/calendar/ziwei_tw_interval/v1/years/YYYY.json
      from the same exact playbook commit through GitHub Connect
   → preserve connector-returned Git blob SHA
   → byte-preserving materialize under the same cache root
   → recompute local Git blob identity and require exact match
   → record calendar_shards_verification.json
→ normalized lunar input:
   → no Gregorian calendar shard required
→ prepend verified cache root to Python sys.path
→ execute tools/ziwei_runtime.py (run_ziwei / run_ziwei_transport)
→ deterministic Scope-A facts / admitted claims
→ ZIWEI.md bounded synthesis
```

Bundle v2 contains no `lunar_python` runtime files. Successful Gregorian cold-start therefore needs the verified runtime bundle plus 1 ordinary year shard, or at most 2 shards at the 31 Dec 23:xx year edge. No pip/network package installation is required afterward.

不得由模型重寫 shard、手算農曆或以 candidate/research data path繞過 exact-commit acquisition。Shard missing、wrong year、schema/status mismatch或 blob identity mismatch必須 fail closed。

## 4. Verified cache

Default cache：

```text
/mnt/data/divination-ziwei-runtime/
bundle_verification.json
calendar_shards_verification.json   # Gregorian input only
```

Bundle marker必須綁定 repository、playbook commit、bundle contract、archive SHA與 files。Gregorian shard marker必須綁定同 repository / commit、dataset id與每個 materialized shard的 path + Git blob identity。聊天重開不得假設 cache仍存在；identity不符即視為 MISS。

## 5. Fallback / fail closed

Bundle無法取得或驗證時，可退回同 exact commit 的 direct repo-source materialization；Gregorian input仍只取 canonical provider要求的 exact year shard(s)。Fallback改 transport，不改 authority、range或 dataset。

只有 runtime source與所需 shard的 exact-commit acquisition / materialization 都無法成立，或 Python execution unavailable / verified source import execution failure，才分類：

```text
ZI WEI DETERMINISTIC RUNTIME UNAVAILABLE
```

不得 fallback 到模型手算農曆，也不得用 Tarot / Meihua / Liuyao 冒充 Zi Wei reading。

## 6. Build/parity dependency boundary

`lunar_python==1.4.8` 仍由 `requirements-ziwei-calendar.txt` 提供給 dataset build、source-identity verification與 A/B parity regression。它不是 ordinary production runtime dependency，也不應重新塞回 ChatGPT deterministic bundle。

## 7. Authority boundary

```text
GitHub Connect → acquisition authority
runtime bundle → repo-local source transport cache only
query-bounded year shards → admitted Gregorian deterministic data
ZIWEI_CALENDAR_ADMISSION_V1.json → Gregorian range/data admission truth
pinned lunar-python → build/parity reference only
tools/ziwei_runtime.py → canonical typed production composition
Zi Wei providers + production retrieval/delivery tools → deterministic facts + admitted claim binding
ZIWEI.md → interpretation / output governance
```

核心原則：**local miss ≠ Zi Wei unavailable；materialize exact runtime + exact required shard(s)，不要把 build-time calendar implementation重新變成 ordinary runtime dependency。**
