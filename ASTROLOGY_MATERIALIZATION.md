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

Shared generic semantics仍由已啟動的 AI Development Playbook 擁有：
`CHATGPT_RUNTIME_EXECUTION.md` → `Runtime Asset Reuse Fast Path` / `Artifact Handoff / Materialization Gate`，
以及 `GITHUB_OPERATIONS.md` → `Inbound Verified Transport`。
本檔只把這些 shared rules 綁定到 Astrology 的 core bundle、pinned Astronomy Engine 與 place-resolver split；不另建 shared framework。

## 4. Runtime Reuse / Host Integration Fast Path

```text
explicit Astrology natal/transit request
→ resolve ai-divination-playbook current ref to exact commit
→ probe /mnt/data/divination-astrology-runtime/core_bundle_verification.json
→ cheap identity / integrity / executability verification
   → compatible verified cache
      → REUSE materialized Astrology runtime
   → cache MISS / invalid / materially changed / identity insufficient
      → Host Capability Gate
         → direct byte/file-aware connector→filesystem handoff available
            → direct verified materialization of required same-commit core assets
         → direct handoff unavailable
            → fetch same-commit runtime/astrology/CHATGPT_DETERMINISTIC_CORE_BUNDLE.json
            → bounded verified opaque transport
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

### Cache Identity Probe

Cache directory存在只代表 reuse candidate，不是 verified cache。Reuse前只驗證本次 execution correctness 真正需要的最低充分 identity：repository、materialized source revision、bundle/archive identity、所有 required source-file identities、pinned dependency identity，以及目前 executability。

Current `main` 前進本身 **不等於 cache automatically invalid**。有 freshness trigger 時，先比較 materially relevant owned source identities；若 bounded evidence 證明 materialized bytes / dependency identity仍一致，直接 reuse，並把新的 HEAD只記成 currentness / last-checked evidence。不得把較新的 repository HEAD 回填成既有 local bytes 的 `materialized_source_commit` 或其他 historical provenance。

Identity不足、material source changed、dependency impact unresolved、compare coverage不足或 executability probe失敗時，才把 cache視為 MISS / invalid並進入 Host Capability Gate。

### Host Capability Gate / No Full-Bundle-First Rule

只有 real cache miss / invalid identity 才判斷 connector→execution handoff。Host提供 direct byte/file-aware handoff時優先使用；沒有 direct bridge不代表 runtime unavailable，仍可使用既有 bounded verified opaque bundle fallback。

**不得在 cache reuse probe完成前，或 host handoff necessity尚未成立前，就把 full bundle / chunks 搬進 model-visible context。** Model-visible chunk/base64只證明 acquisition visibility；不等於 filesystem materialization。

Successful core materialization does **not require pip/network installation afterward**。

Chunk mismatch只 retry同一 exact commit bundle的失敗 chunk；archive/per-file identity PASS前不得import／execute。不得讀完 upstream source後由模型重寫一份「等價」Astronomy Engine。

### Layered Host Status

需要回報 host/materialization evidence時沿用 shared vocabulary，不建立 Astrology-specific status taxonomy：

```text
Acquisition: PASS | NOT ESTABLISHED
Payload handoff: VERIFIED | UNAVAILABLE | NOT ESTABLISHED
Materialization: VERIFIED | NOT ESTABLISHED
Integrity: VERIFIED | NOT ESTABLISHED | FAIL
Execution: RUN | NOT RUN | FAILED
```

較前層 PASS 不得推導較後層 PASS；尤其 GitHub Connect acquisition PASS 不等於 filesystem materialization VERIFIED。

## 5. Verified cache

Default cache：

```text
/mnt/data/divination-astrology-runtime/
core_bundle_verification.json
```

marker至少綁定 repository、materialized source revision、bundle contract、archive SHA、dependency identity與所有 files。新 session不得只靠記憶假設 cache存在；但 marker中的 source revision不同於 current HEAD也不自動等於 MISS，必須依上方 Cache Identity Probe 判斷 materially relevant identities 是否仍相容。

## 6. Place resolver boundary

`tools/astrology_orchestrator.py` 對 explicit coordinates path不得 unconditional import `geonamescache`。只有 `place`／`country` input需要 resolver時才 lazy-load admitted resolver。

若 resolver runtime缺失：

```text
coordinates + timezone request → core path仍可執行
place/country request → resolver-specific unavailable / materialization requirement
```

不得把 resolver dependency miss升格成整個 Astrology core runtime unavailable。

### 6.1 A-MAT-2 query-bounded resolver materialization

The original whole-package / model-mediated A-MAT-2 transport remains rejected. A separate query-bounded shard transport is production-admitted for the default profile `500` only.

Canonical identity is owned by `data/astrology/place/v1/MANIFEST.json`. Current admitted corpus:

```text
dataset: astrology-place-geonamescache-v1
profile: 500
data ref: refs/heads/data/astrology-place-v1
exact data commit: d18be87abe762433e43e844f33f4b43f7fad9f3b
aggregate digest: 6e542fd50c4d821d783c74c2f392bea087df68666ba1781970df66d47dc719a0
```

For a place/country request，先檢查 admitted resolver runtime / 已驗證 query result or shard cache 是否仍符合 exact data-commit + profile identity；compatible 時可 reuse。只有 resolver/runtime/cache真正不可用或 identity不足時才進 query-bounded transport：

```text
normalize query = strip then casefold
→ SHA-256(normalized query), first 3 hex
→ GitHub Connect exact-data-commit alias shard
→ exact alias lookup
→ optional ISO alpha-2 country filter
→ if zero routes: fail closed NOT_FOUND
→ if multiple surviving routes: fail closed with first 10 deterministic candidates
→ for one selected geoname id, SHA-256(decimal geoname id), first 3 hex
→ GitHub Connect exact-data-commit candidate shard
→ exact geoname-id lookup
→ return admitted resolver fields
```

Path derivation follows the manifest:

```text
aliases/{first_hex}/{remaining_two_hex}.json
candidates/{first_hex}/{remaining_two_hex}.json
```

Every retrieval MUST use the exact admitted data commit, not the moving data branch. Missing path, malformed schema, profile mismatch, missing alias/id, or identity mismatch fails closed. GitHub Connect does not expose connector-internal cache/network-byte/latency telemetry; do not invent those properties.

This transport preserves the existing resolver semantics; it does not create a second geocoder or semantic authority. Profiles `1000`, `5000`, and `15000` remain supported by the installed `geonamescache` resolver but are **not admitted for shard materialization transport**. If a request explicitly requires one of those profiles and the installed resolver is unavailable, request explicit coordinates + IANA timezone or report the resolver-specific materialization limitation; never silently substitute profile 500.

The corpus is generated from the exact admitted `geonamescache==3.0.2` / GeoNames source identity, remains CC-BY-4.0 attribution-bearing derived deterministic data, and does not become astronomical authority.

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
