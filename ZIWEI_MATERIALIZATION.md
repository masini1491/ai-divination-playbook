# Zi Wei Deterministic Tool Materialization｜紫微 deterministic runtime 按需載入契約

Status: **TASK-SPECIFIC CANONICAL CONTRACT**

本檔只在 explicit Zi Wei production 已命中 `ZIWEI.md`，但 ChatGPT local runtime 缺少 verified Zi Wei deterministic tools 或 `lunar_python` runtime 時載入。它不取得 routing、interpretation、claim admission 或 research authority。

## 1. Canonical authority

Repo-local authority 仍是：

```text
tools/ziwei_calendar_provider.py
tools/ziwei_gregorian_pipeline.py
tools/ziwei_natal_provider.py
tools/ziwei_scope_a_pipeline.py
tools/ziwei_brightness_provider.py
tools/ziwei_brightness_pipeline.py
references/ziwei/interpretation_retrieval_v0.py
references/ziwei/validate_uncertainty_safety_delivery_v0.py
3 admitted claim registries
```

Gregorian calendar dependency authority固定為：

```text
lunar_python==1.4.8
6tail/lunar-python@000c8a3d74eed098d6256a28fdd51b869324c559
MIT
```

`runtime/ziwei/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json` 只是 CI-generated **derived transport cache**；不得成為第二套 calculation / interpretation authority。

## 2. Local miss is not source unavailability

聊天室 Python 沒有 `lunar_python`、沒有 repo checkout、或 `/mnt/data` 沒有 Zi Wei files，本身都不等於 Zi Wei deterministic runtime unavailable。若 GitHub Connect exact-commit retrieval 與 Python execution 都可用，必須先嘗試同 commit bundle materialization。

## 3. Preferred cold-start path

```text
explicit Zi Wei request
→ resolve ai-divination-playbook current main to exact commit
→ probe /mnt/data/divination-ziwei-runtime/bundle_verification.json
→ cache MISS / invalid
   → fetch same-commit runtime/ziwei/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
   → validate schema / authority / contract
   → verify every chunk length + SHA-256
   → index-order concat
   → base64 decode + zlib decompress
   → verify archive size + SHA-256
   → slice every source_file by offset / byte_size
   → verify per-file SHA-256 + Git blob identity
   → dependency files must match pinned lunar-python upstream blob allowlist
   → write exact paths under /mnt/data/divination-ziwei-runtime/
   → write + fresh-read bundle_verification.json
   → prepend verified cache root to Python sys.path
→ execute tools/ziwei_gregorian_pipeline.py
→ deterministic Scope-A facts / admitted claims
→ ZIWEI.md bounded synthesis
```

Bundle includes the complete Python runtime files of pinned `lunar_python==1.4.8`, so successful materialization **does not require pip/network installation afterward**.

Chunk mismatch只 retry 同一 exact commit bundle 的失敗 chunk；archive/per-file identity PASS 前不得 import / execute。不得用模型重寫缺少的 dependency source。

## 4. Verified cache

Default cache:

```text
/mnt/data/divination-ziwei-runtime/
bundle_verification.json
```

marker 必須綁定 repository、playbook commit、bundle contract、archive SHA、dependency identity與所有 files。聊天重開不得假設 cache 仍存在；identity 不符即視為 MISS。

## 5. Fallback / fail closed

bundle 無法取得或驗證時，才可退回同 exact commit 的 direct repo-source + pinned upstream dependency source materialization。仍須 byte-preserving、逐檔 identity verification。

只有 bundle 與 direct exact-source 路徑都無法成立，或 Python execution 不可用／verified source import execution failure，才分類：

```text
ZI WEI DETERMINISTIC RUNTIME UNAVAILABLE
```

此時不得由模型手算農曆、命身宮、主星 placement 或 brightness 冒充 verified facts，也不得 fallback 到 Tarot / Meihua / Liuyao 冒充 Zi Wei。

## 6. Authority boundary

```text
GitHub Connect → acquisition authority
bundle → derived transport cache only
this contract → handoff / verification / cache policy only
pinned lunar-python → Gregorian/lunar dependency bytes
Zi Wei providers/pipelines → deterministic production facts + retrieval binding
ZIWEI.md → interpretation / output governance
```

核心原則：**local package miss ≠ Zi Wei unavailable；先 materialize exact verified runtime，再做 Fact Gate。**
