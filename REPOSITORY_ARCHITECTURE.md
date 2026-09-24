# Repository Architecture｜共通資料與實作分層

Status: **REPO-LEVEL CANONICAL CONTRACT**

本檔是 `ai-divination-playbook` 的 repository topology 與 deterministic-data layering canonical owner。各 method owner、runtime/materialization contract、generator、dataset、schema 與 research evidence 都必須遵守本檔，但本檔不取得各 method 的 calculation、interpretation、routing 或 admission authority。

## 1. Scope / authority

本檔只回答：

- executable logic 應放在哪一層；
- deterministic dataset 應如何定位與證明 provenance；
- ChatGPT runtime/materialization transport 與 durable data 的邊界；
- third-party implementation 何時可 vendored；
- research/evidence 與 stable machine contract 的位置；
- 本 Repo 實際採用哪些 supporting surfaces 與 physical path mapping；
- 大型 repo-local data 如何維持 bounded-read / bounded-loading。

本檔不回答：

- 哪個 divination method 應被選中；
- method calculation / interpretation semantics；
- 某個 provider / resolver / dataset 是否已 production-admitted；
- research 結論本身；
- release / GitHub mutation procedure。

這些仍由各自 canonical owner 處理。

## 2. Repository layer taxonomy

共通層級固定為：

```text
tools/        executable authority / provider / resolver / generator
data/         repo-local deterministic datasets
runtime/      ChatGPT execution / materialization transport artifacts
third_party/  actually vendored upstream implementation
references/   research / external-source dossiers / comparison / historical records
schemas/      stable machine-readable contracts
```

這六層是 **core topology**，不是要求 repository 只能存在這六個目錄。Supporting surface（例如 routing index、evidence、fixture、validation、coordination）的 generic admission / loading / authority semantics 由 activated shared development baseline canonical owners負責；本 Repo 只在 §2.7 記錄實際採用的 physical mapping 與 stricter local delta，不為目錄對稱建立空 surface。


### 2.1 `tools/`

放置 project-owned executable logic，包括但不限於：

- runtime composition；
- provider；
- resolver；
- deterministic engine；
- generator / compiler / verifier；
- CLI / adapter。

`tools/` 內的實作可成為 calculation / provider / generator authority，但 authority 必須由對應 method / admission / architecture owner 明確建立；「檔案在 tools/」本身不自動取得 production authority。

### 2.2 `data/`

`data/` 放置 repo-local deterministic datasets，包括 source-derived tables、generated indexes、calendar tables、mapping tables、shards 與其他可 deterministic 驗證的 machine data。

**Shared invariant：`data/` 不等於 upstream authority source。**

Repo-local data 必須保留其 provenance chain：

```text
upstream authority / admitted source bytes
→ verified project generator / adapter
→ repo-local deterministic derived dataset under data/
→ project-owned provider / resolver
```

因此：

- `data/**` 不得因存在於 main 而反向取代 upstream/source authority；
- derived dataset 必須可追溯 generator identity、source identity / revision、必要 source hashes、schema/version 與 license/attribution；
- method-specific admission 仍決定該 data 是否可被 production 使用。

### 2.3 `runtime/`

`runtime/` 只放 ChatGPT execution / materialization transport artifacts 與 runtime-specific execution support。

典型範例：

```text
runtime/astrology/CHATGPT_DETERMINISTIC_CORE_BUNDLE.json
runtime/ziwei/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
runtime/liuyao/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
runtime/meihua/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
runtime/casting/**
```

Generated bundle / cache / transport artifact 是 **derived transport only**：

- 不取得 calculation authority；
- 不取得 deterministic dataset authority；
- 不取得 interpretation / admission authority；
- 不應為便利而內嵌整份大型 `data/**`，若 current task 可用 query-bounded data retrieval 解決。

核心分層：

```text
upstream / admitted source
→ repo-local deterministic data
→ runtime transport
```

三層不可互相偷換 authority。

### 2.4 `third_party/`

`third_party/` 只用於 **production/runtime 真正需要一起執行的 vendored upstream implementation**。

判斷規則：

```text
A. production runtime 需要 import / execute upstream implementation
→ third_party/<dependency>/ may be appropriate

B. upstream implementation 只用於 build / generation / validation
→ production runtime只讀 project-owned tools/data
→ 不因 build-time dependency 而自動建立 third_party/<dependency>/
```

Vendoring 仍需：

- pinned source/revision；
- license / notice；
- adopted scope；
- byte / file identity 或等價 integrity evidence；
- 不把 vendored copy 升格為 method semantic owner。

### 2.5 `references/`

`references/` 放置以**外部來源與研究 synthesis**為主的 durable material：

- research synthesis；
- external source / upstream dossier；
- source comparison；
- historical research record；
- feasibility / architecture comparison；
- external implementation review。

Run-specific observation、bench/hardware measurement、validation result 或 pre-canonical capture staging 優先歸 `evidence/`（若該 repository 採用此 optional surface），不要讓 `references/` 同時變成 run-result archive。

`references/**` 預設不是 production authority；production scope 必須另由 method owner / admission contract 明確承接。

### 2.6 `schemas/`

`schemas/` 放置跨 implementation 的 stable machine-readable contracts，例如 request/result/fact bundle/manifest/schema。

Schema：

- 定義資料形狀與 machine contract；
- 不自動取得 calculation / semantic authority；
- 若 schema 與 owner policy 衝突，以 canonical owner 為準。


### 2.7 Project-specific supporting-surface mapping

Supporting-surface 的 **generic semantics 不由本檔重定義**。Shared development baseline 被 activation 時：

- retrieval intent / context cohesion / thin routing / control-data plane / Hot-Cold / evidence staging → upstream `AI_CONTEXT.md`；
- coordination persistence / promotion / execution / write authority → upstream `REPOSITORY_EXECUTION.md`；
- fixture / validation / PASS scope / large-artifact acceptance → upstream `DEBUG_VALIDATION.md`；
- source / derived / provenance integrity → upstream `INFORMATION_INTEGRITY.md`；
- external-source research / reference knowledge / licensing → upstream `RESEARCH_ARCHITECTURE.md`。

本 Repo 只保存實際採用的 physical mapping 與 stricter local delta。

#### Method-scoped coordination topology

本 Repo 已採用三個 peer coordination surfaces：

```text
ASTROLOGY_BACKLOG.md
ZIWEI_BACKLOG.md
PALMISTRY_BACKLOG.md
```

共同 local contract：

- 都是 `coordination-only`；
- 都不是 production authority、research-evidence authority 或 method-routing authority；
- Astrology、Zi Wei、Palmistry 具有獨立 retrieval intent，且可由獨立 ChatGPT project conversations 維護，因此不建立 root `BACKLOG.md` aggregate；
- machine discovery 由 `PLAYBOOK_INDEX.json` routing-only entries提供；
- 本節同時是 shared `REPOSITORY_EXECUTION.md` 所要求的 project-specific equivalent path contract：ChatGPT coordination-write allowlist 明確為 `/ASTROLOGY_BACKLOG.md`、`/ZIWEI_BACKLOG.md`、`/PALMISTRY_BACKLOG.md`；`AGENTS.md` 只提供 routing pointer；
- cross-method shared item只指定一個 canonical coordination owner，其餘 backlog只保存 pointer，避免 divergent work state。
- 此 allowlist 只授權 coordination-only persistence；不因而擴張對 `tools/**`、`data/**`、`runtime/**`、`references/**`、`schemas/**`、method owners、admission manifests 或其他 governance surfaces 的寫入權。

#### Other optional surfaces

`indexes/`、`evidence/`、`fixtures/`、`validation/` 等 path 只有在本 Repo 未來真的採用時才建立；是否值得建立與其 generic semantics依 shared baseline canonical owners判斷。本檔不因目錄名稱存在而自行建立第二份 shared policy。

## 4. Source / derived data / transport boundary

任何 deterministic-data feature 必須先分類三層：

```text
source authority
→ derived deterministic data
→ transport / materialization
```

不得因 transport 比較容易取得，就把 transport 當 source。

不得因 derived dataset 已 repo-local，就省略 source provenance。

不得因 source package 可執行，就假設 production 必須 vendor 或 materialize整包 source implementation。

## 5. Repo-local deterministic-data contract

新增或大改 `data/**` 時，至少回答：

1. data 的 upstream/source authority 是什麼；
2. project generator / adapter 是什麼；
3. source exact revision / source hash 如何建立；
4. data schema/version 是什麼；
5. dataset 是 source copy、normalized copy、還是 derived index；
6. license / attribution requirement；
7. rebuild 是否 deterministic；
8. provider / resolver 如何 bounded-read；
9. integrity verification 如何做；
10. production admission owner 是誰。

大型 data tree 建議至少具有：

```text
MANIFEST.json
provenance.json
ATTRIBUTION.md / NOTICE where required
versioned path or explicit format version
```

若單一 manifest 過大，可採 hierarchical manifest / aggregate hash；不要求把每個 shard hash 全塞進一個 root file。

## 6. Large-data / bounded-read rule

Repository physical size 與 ChatGPT loading size 分開治理：

```text
repository size
≠ CHAT_INIT payload
≠ method hot-path payload
≠ one deterministic query payload
```

因此「dataset 很大」本身不是 same-repo 的否決條件。

真正的 runtime gate 應量：

- one-query bytes / file count；
- p95 / worst-case bounded retrieval；
- cold-start model-visible payload；
- connector / runtime materialization cost；
- ambiguity / error-preview path；
- cache / integrity verification cost。

Large dataset 必須避免被 `CHAT_INIT.md`、load pack 或 ordinary method bootstrap 全量載入。

Query-bounded shard / index 設計應優先讓 ordinary request 只讀最低充分 data subset。

## 7. Directory width / sharding

大量 generated files 不應全部 flat 放同一 directory。

可使用 stable hash prefix 分層，例如：

```text
data/<domain>/<dataset>/v1/
  profiles/
    500/
      aliases/
        a/
          bc.json
      candidates/
        4/
          de.json
```

Path layout 必須：

- deterministic；
- derivable from query / record identity；
- documented in manifest；
- 不要求 model 先 enumerate 整個 tree；
- 支援 exact-commit bounded retrieval。

## 8. Generator and rebuild contract

Generator 應：

- project-owned；
- deterministic；
- fail closed on source identity mismatch；
- 不 silent substitute source/profile；
- stable serialize / sort；
- only change blobs whose content actually changes when practical；
- produce machine-verifiable summary / manifest。

Build-time dependency ≠ runtime dependency。

Generator 可以依賴 external/pinned package，但 production consumer若只需要 repo-local `data/**`，不因 generator dependency 而必須在 ordinary ChatGPT runtime安裝該 package。

## 9. Method-specific extension rule

Astrology / Zi Wei / Liuyao / Meihua 等 method 可在本共通分層下定義自己的 data schema、provider、materialization 或 admission，但不得建立平行 repository-layer policy。

若 method-specific需求超出本檔：

```text
shared invariant不變
→ method owner只定義自己的 narrower contract
→ 若真的需要改 shared taxonomy，再修改本檔
```

## 10. Current method implications

### Astrology

若 place resolver 採 repo-local deterministic derived dataset，目標位置應是：

```text
data/astrology/place/v1/**
```

而不是：

```text
runtime/astrology/place-data/**
```

其 authority chain 仍為：

```text
GeoNames / admitted geonamescache source bytes
→ verified project generator
→ data/astrology/place/v1/**
→ project-owned place resolver
```

### Zi Wei

Zi Wei calendar architecture 尚未由本檔決定 A/B：

```text
A. production runtime executes vendored upstream implementation
→ third_party may be appropriate

B. upstream calendar source only generates verified repo-local data
→ data/calendar/**
→ project-owned calendar provider
```

哪一條成立，必須由 Zi Wei calendar requirements / parity / materialization evidence 決定；本檔不預先 admission。

### Liuyao / Meihua

未來若加入大型曆法表、mapping table、lookup index，先依本檔判斷是 executable logic、deterministic data、transport、vendored implementation、research evidence 或 schema，再交由各 method owner admission。

## 11. Validation / migration rule

改動 shared repository architecture 時：

1. fresh-resolve current main；
2. 修改本 canonical owner；
3. `AGENTS.md` 只保留 routing pointer / owner mapping，不複製完整 policy；
4. `PLAYBOOK_INDEX.json` 只提供 machine-readable owner pointer；
5. method owner只同步必要 consumer contract，不複製 shared taxonomy；
6. generated artifacts 不因 architecture 文件更新而自動重建，除非其 generator / path contract真的受影響；
7. deterministic structural regression 必須證明 shared owner / AGENTS pointer / machine index不漂移；
8. 再依受影響 method執行最低充分 regression。

核心原則：**repository layer 是共通架構；method semantics 是各自 authority。Data可以很大，但普通 ChatGPT只讀本題需要的 bounded subset。**
