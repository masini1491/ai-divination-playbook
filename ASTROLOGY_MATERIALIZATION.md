# Astrology Deterministic Core Materialization｜占星 deterministic runtime 按需載入契約

Status: **TASK-SPECIFIC CANONICAL CONTRACT**

本檔只在 explicit Astrology production 已命中 `ASTROLOGY.md`，且 `ASTROLOGY_PROVIDER_ROUTING_V1.json` / provider selector已因 non-ChatGPT、Swiss host probe FAIL、unknown-time或 transit 落到 portable `astronomy-engine-natal-v1`／transit path後，ChatGPT local runtime仍缺少 verified Astrology core tools或 `astronomy-engine` 時載入。它是 portable fallback 的 materialization owner，不取得 provider-preference、method routing、interpretation、claim admission、place-resolution或 research authority。

## 1. Canonical authority

Portable fallback calculation authority仍是：

```text
tools/astrology_runtime.py
tools/civil_time_normalizer.py
tools/astrology_provider.py
tools/astrology_transit_provider.py
tools/astrology_orchestrator.py
admissions/shared/CIVIL_TIME_NORMALIZER_ADMISSION_V1.json
admissions/astrology/ASTROLOGY_PROVIDER_ADMISSION_V1.json
admissions/astrology/ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json
```

Provider preference／fallback policy另由 `ASTROLOGY_PROVIDER_ROUTING_V1.json` 擁有；本檔只 materialize portable Astronomy fallback，不得安裝、下載或 vendor Swiss/PySwissEph。

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
→ shared civil-time normalizer
→ natal / transit provider
→ Astrology runtime Fact Gate
```

下列不在 core bundle：

```text
tools/astrology_place_resolver.py
geonamescache==3.0.2
GeoNames datasets
```

因此 `place`／`country` name input仍與 core bundle分層：installed admitted resolver可直接使用；resolver runtime/cache缺失時，必須改讀 `ASTROLOGY_PLACE_RESOLVER_MATERIALIZATION.md`。該 owner 的 profile-500 query-bounded transport與 astronomical provider selection無關。不得因 core bundle或 Swiss probe PASS 就宣稱 resolver path已完成；也不得用 generic web geocoding或模型猜座標／timezone補洞。

## 3. Local miss is not source unavailability

聊天室沒有 repo checkout、沒有 `astronomy` package、或 `/mnt/data/divination-astrology-runtime` 不存在，本身都不等於 Astrology deterministic runtime unavailable。

在把 local checkout／package／verified cache MISS 分類為 provider、handoff 或 runtime unavailable 前，先套用 root `CHAT_INIT.md` → `GitHub Connect Minimum Capability Probe｜不得未試即判 unavailable`；ordinary Astrology production 不因這個 probe 本身啟動 shared development baseline。

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
            → exact resolved commit has a successful main-push Astrology core handoff artifact?
               → yes: download exact-commit artifact through GitHub connector
               → materialize connector-backed file payload
               → verify artifact digest when exposed by GitHub
               → verify PLAYBOOK_COMMIT + HANDOFF_MANIFEST.json exact commit/file identities
               → load bundled canonical verifier + core bundle
               → materialize with the same chunk/archive/per-file integrity gates
               → no / expired / unavailable: fetch same-commit runtime/astrology/CHATGPT_DETERMINISTIC_CORE_BUNDLE.json
            → bounded verified opaque transport fallback
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

只有 real cache miss / invalid identity 才判斷 connector→execution handoff。Host提供 direct byte/file-aware handoff時優先使用。Direct bridge unavailable時，若 resolved exact commit存在成功的 `main` push validation handoff artifact，優先使用該 connector-backed file payload；只有 artifact不存在、已過期、下載/identity驗證失敗或 resolved commit沒有對應 main-push artifact時，才進既有 bounded verified opaque bundle fallback。

Main-push handoff artifact只是 **temporary transport convenience**，不是 source authority、不是 production admission、也不取代 Git-tracked core bundle。Artifact名稱必須包含 exact playbook commit；payload至少包含同 commit的 `CHATGPT_DETERMINISTIC_CORE_BUNDLE.json`、canonical bundle verifier、`PLAYBOOK_COMMIT` 與 machine-readable handoff manifest。下載後若 GitHub connector提供 artifact digest，先驗 downloaded artifact bytes與該 digest；再驗 `PLAYBOOK_COMMIT`、manifest repository/commit與各 payload file SHA-256。任一 mismatch直接停止 artifact route，不把錯誤 bytes餵給 verifier。Actions artifact可能依 retention policy過期；availability miss只代表此 fast path不可用，不得升格成 Astrology runtime unavailable。

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

## 6. Extended ephemeris query-bounded materialization

Chiron / Ceres / Pallas / Juno / Vesta 的 production calculation facts 使用獨立 generated-data lane；它不屬於 Astronomy Engine core bundle，也不要求 ordinary runtime 連線 Horizons。

Canonical admission：

```text
provider: astrology-extended-ephemeris-c1-v1
dataset: astrology-extended-ephemeris-c1-f32-v1
data ref: refs/heads/data/astrology-extended-ephemeris-v1
exact data commit: 0052ba1c0a3b65238b4f9ec3a94a1aff47e341ea
dataset SHA-256: 580bb2a8ef463dfc6527ea611f27daad3562cb1fa5698391b3e2baeba64987bf
representation: c1-cheb-d7-w60-f32-c0mod360-v1
```

只有 explicit known-time natal request 的 `extended_objects` selector 才啟動：

```text
exact admitted data commit
→ fetch MANIFEST.json + GENERATED_IDENTITY.json
→ verify dataset / representation / generator-source identities
→ derive one required shard from UTC instant
→ GitHub Connect fetch_file(encoding=base64) for that shard only
→ strip transport whitespace
→ base64 decode exact binary bytes
→ verify byte_size + SHA-256 + Git blob identity
→ materialize under /mnt/data/divination-astrology-runtime/extended_ephemeris/v1/
→ tools/astrology_extended_ephemeris.py
→ Astrology Fact Gate
```

Maximum admitted shard = 30,720 raw bytes / 40,960 compact base64 characters. Missing manifest/identity/shard, wrong digest/blob, unsupported object, out-of-coverage date or generator-source mismatch全部 fail closed。不得 fallback live Horizons、Swiss Ephemeris、模型手算或其他近似軌道。

Generated-data branch 的 `GENERATED_CANDIDATE_ONLY` 不是 production authority；production admission 只由 main 的 `admissions/astrology/ASTROLOGY_EXTENDED_EPHEMERIS_ADMISSION_V1.json` 授權並 pin exact data commit。

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
main-push handoff artifact → temporary exact-commit connector-backed transport only
this contract → core handoff / verification / cache policy only
Astronomy Engine → pinned astronomical calculation dependency
Astrology providers/runtime → deterministic production facts + Fact Gate
place resolver → separate admitted input-resolution authority
ASTROLOGY.md → interpretation / output governance
```

核心原則：**local package miss ≠ Astrology unavailable；core calculation與place resolution分層，只materialize本題真正需要的 deterministic workload。**
