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
- routing/index/evidence/fixture/validation 等 supporting surface 何時值得建立；
- control-plane / data-plane 如何分離；
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

這六層是 **core topology**，不是要求 repository 只能存在這六個目錄。依實際 retrieval intent，可另外建立下列 **optional supporting surfaces**：

```text
indexes/      routing / lookup metadata only
evidence/     bounded observations / measurements / provenance staging
fixtures/     deterministic test / parity / reproducibility inputs
validation/   validation contracts / result artifacts / campaign evidence
coordination/ or TASKS/BACKLOG
              Hot / Cold work-control surfaces where the repository adopts them
```

Optional surface 不是新的 semantic authority class；建立前必須有獨立 retrieval intent、清楚 responsibility boundary 與 bounded-loading benefit。若現有 owner 已能自然承接，不為目錄對稱或形式完整而新增 surface。


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


### 2.7 Optional supporting surfaces

#### `indexes/`

`indexes/` 只放 machine-readable routing / lookup metadata。

Shared rule：

- index 可保存 stable id / alias / owner / path / section / bucket locator；
- index 不複製被路由內容本體；
- index 不保存 volatile current conclusion、validation result 或歷史 evidence，除非該 index 本身就是對應 canonical owner；
- routing metadata 失效時應 fail closed 或回 canonical router，而不是靠模型猜 path；
- generated index 應可由 canonical owner / manifest deterministic rebuild。

概念上：

```text
index = control plane
canonical owner / data / evidence = data plane
```

若 receiving actor 能直接從 current authoritative source 取得 substantive content，routing/handoff 優先傳 pointer / identity，不把大型 file、diff、log、dataset 複製進 control message 或 index。

#### `evidence/`

`evidence/` 可用於保存 observation、bench/hardware result、source capture summary、provenance record 或 pre-canonical evidence staging。

- evidence ≠ policy / architecture / method authority；
- evidence 不因被 commit 就自動升格為 admitted fact；
- promotion 必須回到對應 canonical owner / admission contract；
- raw sensitive evidence 不得為了之後再清理而先進 public Git。

#### `fixtures/`

`fixtures/` 可保存 deterministic tests、parity、replay、golden input/output 或 reproducibility 所需的 bounded examples。

- fixture 證明的是已覆蓋的 tested scope；
- fixture PASS 不等於全域 production validity；
- public fixture 不得包含可識別個資、secret 或未授權 proprietary data。

#### `validation/`

`validation/` 可保存 validation contract、campaign plan、machine result或 current validation evidence，但必須清楚區分：

```text
validation contract
≠ validation run result
≠ production authority
```

是否採 dedicated `validation/` 由 repository scale / independent retrieval intent 決定；小型專案可以由現有 owner 承接，不要求建立空目錄。

#### coordination surfaces

`TASKS.md`、`BACKLOG.md`、`tasks/**` 或等價 Hot / Cold coordination surface 是 work-control plane，不是 technical truth/data plane。

- queue/admission 可授權 work lifecycle，但不得取代 architecture / protocol / data / evidence authority；
- Cold item 不因持久化而取得 execution authority；
- 已完成的 technical truth 應回 canonical owner / source / history，而不是永久靠 queue 維持 current state。

## 3. Information surface admission / retrieval-intent gate

新增 file / directory / router / index / evidence dossier / data shard family前，先回答：

> **這是否形成可被獨立詢問、引用或 bounded-load，且與既有 owner 有清楚 responsibility boundary 的 retrieval intent？**

只有「內容變多」、「檔案變大」、「來源很多」或「看起來比較整齊」不足以構成新 surface。

優先順序：

1. exact canonical leaf 已知 → direct leaf；
2. 需要 routing → thin index / router；
3. 需要 substantive current content → 從 authoritative data plane direct-read；
4. 只有在不可重取、跨邊界 transport 本身是 requirement、或 bounded cache 有實測收益時，才建立 derived transport/cache；
5. evidence足夠即停止，不為形式掃完整 repository。

Repository topology 必須同時最佳化：

- authority clarity；
- retrieval/search cost；
- context cohesion；
- reconciliation/drift cost；
- deterministic rebuildability。

概念上：

```text
control plane
  routing / owner pointer / task state / bounded decision state

data plane
  canonical file body / dataset / evidence / diff / log / runtime result
```

Control plane 不複製 data plane 本體；data plane 也不因被 routing metadata 指到就取得額外 authority。

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
