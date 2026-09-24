# Astrology Deterministic Core Materialization｜占星 deterministic runtime 按需載入契約

Status: **TASK-SPECIFIC CANONICAL CONTRACT**

本檔只在 explicit Astrology production 已命中 `ASTROLOGY.md`，但 ChatGPT local runtime 缺少 verified Astrology core tools 或 `astronomy-engine` 時載入。它不取得 method routing、interpretation、claim admission、place-resolution 或 research authority。

## 1. Canonical authority

Repo-local calculation authority仍是：

```text
tools/astrology_runtime.py
tools/astrology_provider.py
tools/astrology_transit_provider.py
tools/astrology_orchestrator.py
ASTROLOGY_PROVIDER_ADMISSION_V1.json
ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json
```

Core astronomical dependency固定為：

```text
astronomy-engine==2.1.19
cosinekitty/astronomy@865d3da7d8112bbc7911238052c6af4aaf877181
MIT
```

`runtime/astrology/CHATGPT_DETERMINISTIC_CORE_BUNDLE.json` 是 CI-generated **derived transport cache only**；不得成為第二套 astronomical calculation、interpretation或admission authority。

## 2. Core / resolver split

A-MAT-1只解決 **core deterministic calculation**：

```text
explicit coordinates
+ explicit IANA timezone
→ natal / transit provider
→ Astrology runtime Fact Gate
```

下列不在 core bundle：

```text
tools/astrology_place_resolver.py
geonamescache==3.0.2
GeoNames datasets
```

因此 `place`／`country` name input仍要求 admitted resolver runtime已存在，或未來另有 verified resolver materialization transport。不得因 core bundle PASS 就宣稱 place resolver也已 materialize；也不得用 generic web geocoding或模型猜座標／timezone補洞。

## 3. Local miss is not source unavailability

聊天室沒有 repo checkout、沒有 `astronomy` package、或 `/mnt/data/divination-astrology-runtime` 不存在，本身都不等於 Astrology deterministic runtime unavailable。

若 GitHub Connect exact-commit retrieval與 Python execution可用，且本題已提供 explicit coordinates + IANA timezone，必須先嘗試 same-commit core bundle materialization。

## 4. Preferred cold-start path

```text
explicit Astrology natal/transit request
→ resolve ai-divination-playbook current ref to exact commit
→ probe /mnt/data/divination-astrology-runtime/core_bundle_verification.json
→ cache MISS / invalid
   → fetch same-commit runtime/astrology/CHATGPT_DETERMINISTIC_CORE_BUNDLE.json
   → validate schema / authority / contract
   → verify every chunk length + SHA-256
   → index-order concat
   → base64 decode + zlib decompress
   → verify archive size + SHA-256
   → slice every source_file by offset / byte_size
   → verify per-file SHA-256 + Git blob identity
   → astronomy dependency files must match pinned `astronomy-engine==2.1.19` PyPI distribution SHA-256 allowlist
   → write exact paths under /mnt/data/divination-astrology-runtime/
   → write + fresh-read core_bundle_verification.json
   → prepend verified cache root to Python sys.path
→ execute tools/astrology_orchestrator.py or admitted provider directly
→ Astrology runtime Fact Gate
→ ASTROLOGY.md + selected mode owner bounded synthesis
```

Successful core materialization does **not require pip/network installation afterward**.

Chunk mismatch只 retry同一 exact commit bundle的失敗 chunk；archive/per-file identity PASS前不得import／execute。不得讀完 upstream source後由模型重寫一份「等價」Astronomy Engine。

## 5. Verified cache

Default cache：

```text
/mnt/data/divination-astrology-runtime/
core_bundle_verification.json
```

marker至少綁定 repository、playbook commit、bundle contract、archive SHA、dependency identity與所有 files。新 session不得只靠記憶假設 cache存在；identity不足或不符即 MISS。

## 6. Place resolver boundary

`tools/astrology_orchestrator.py` 對 explicit coordinates path不得 unconditional import `geonamescache`。只有 `place`／`country` input需要 resolver時才 lazy-load admitted resolver。

若 resolver runtime缺失：

```text
coordinates + timezone request → core path仍可執行
place/country request → resolver-specific unavailable / materialization requirement
```

不得把 resolver dependency miss升格成整個 Astrology core runtime unavailable。

## 7. Fallback / fail closed

Core bundle無法取得或驗證時，可退回同 exact commit repo-source + pinned upstream Astronomy Engine exact-source materialization；仍須 byte-preserving、逐檔 identity verification。

只有 admitted core materialization路徑都無法成立，或 Python execution不可用／verified source import execution failure時，才分類：

```text
ASTROLOGY DETERMINISTIC CORE RUNTIME UNAVAILABLE
```

此時不得由模型手算 planet longitude、houses、angles、aspects或transit events冒充 verified facts，也不得偷偷改用 Tarot / Meihua / Liuyao冒充 Astrology。

## 8. Authority boundary

```text
GitHub Connect → current source acquisition authority
core bundle → derived transport cache only
this contract → core handoff / verification / cache policy only
Astronomy Engine → pinned astronomical calculation dependency
Astrology providers/runtime → deterministic production facts + Fact Gate
place resolver → separate admitted input-resolution authority
ASTROLOGY.md → interpretation / output governance
```

核心原則：**local package miss ≠ Astrology unavailable；core calculation與place resolution分層，只materialize本題真正需要的 deterministic workload。**
