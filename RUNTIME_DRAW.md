# ChatGPT Runtime Draw｜程式抽牌／起卦治理

本章是 ChatGPT／AI 自行執行 stochastic draw / cast 的 canonical runtime authority。

Canonical stochastic core 與完整 Runtime adapter：

```text
runtime/casting/core.py        # canonical stochastic core
runtime/casting/randomizer.py  # full API / CLI adapter，直接重用 core.py
```

Free ChatGPT cold-start transport artifact：

```text
runtime/casting/CHATGPT_RUNTIME_CAPSULE.json
```

`CHATGPT_RUNTIME_CAPSULE.json` 只是由 `core.py` 產生的 derived byte-transport cache，不取得 stochastic policy／algorithm authority；解碼後 bytes 必須以 size + SHA-256 驗證等於 canonical `core.py` 才可執行。

支援：Tarot、Meihua、Liuyao three-coin raw cast。六爻 deterministic structured facts 由 `LIUYAO.md` 治理。

> **Language-model generation ≠ random draw / cast。** 宣稱 Runtime Draw / Cast 必須有真正 canonical runtime execution result。

## Section Router｜最低必要載入

- **普通代抽／代起卦 + verified cache PASS** → `Fast Path` + 對應 Method Contract + `Execution` + `Fact / Fail-Closed`；STOP。
- **cache FAIL／首次 acquisition** → 再讀 `Acquisition`。
- **多個合法獨立 readings** → `Automatic Batching`。
- **完整 provenance／audit／保存** → 再讀 `Provenance` + `READING_RECORD.md`。
- **補占／重占／copy-ready** → `READING_LIFECYCLE.md`／`CHATGPT_OUTPUT.md`。
- **維護 Randomizer** → 本檔 `Validation` + `runtime/casting/**` + `tests/casting/**`。

不要為形式載入 acquisition／audit／maintenance sections。**Fast path 已足夠時就 STOP。**

## Stochastic Fact Completeness Gate｜不可跳過

任何 **AI／Runtime 新產生** 的 Tarot／Meihua／Liuyao stochastic result，只有在同一 canonical execution envelope 同時具備 stochastic result、`generated_at_utc`、`generated_at_taipei`、`timezone = Asia/Taipei` 與 runtime/source provenance 時，才成立為 Raw Draw / Cast Fact。

缺任一項 → `STOCHASTIC EXECUTION FACT INVALID` → **立即停止 interpretation / deterministic downstream / record / Vault write**。不得拿聊天室時間、commit time、事後 `now()` 或估計值補成原 execution timestamp；需要正式 reading 時只能重新執行 canonical stochastic API，形成新的 execution identity。

正式 stochastic execution API 只有 `core.execute_stochastic()`；full `randomizer.generate_payload()` 必須 delegate 到它。`core.py` 內 `_..._raw` helper 只是 implementation detail，其 bare return value永遠不是有效 Reading Fact。

## Fast Path｜普通占問預設

```text
Question Contract fixed
→ fixed-slot probe
→ PASS
→ reuse already-loaded module if available; otherwise import cached module
→ one direct generate_payload() call
→ compact_ai_payload()
→ Draw / Cast Fact fixed
→ Interpretation
```

條件：Python 可執行、fixed cache 通過最低 probe、方法已驗證、無 Randomizer-specific refresh trigger。

### User-visible execution time｜固定顯示格式

只要本輪由 AI／Runtime **新產生** stochastic result，對使用者顯示該牌面／A-B／六爻 Raw Cast 時，必須在同一結果區塊、結果內容之前顯示 execution time；不得省略或移到只有 audit 才會看到的位置。

固定顯示格式：

```text
YYYY-MM-DD HH:mm:ss（Asia/Taipei）
```

Tarot 可標示「抽牌時間」，Meihua／Liuyao 可標示「起卦時間」。顯示層不得再附加 `+08:00`；canonical machine provenance 仍保留 `generated_at_utc`、ISO-8601 `generated_at_taipei`（含 `+08:00`）與 `timezone = Asia/Taipei`，不得用 display string 取代 machine timestamp。

PASS 後：

- 不抓 GitHub、不重新 materialize、不跑 full smoke；
- 同一 persistent Python interpreter 若 canonical cached module 已成功 import 且 cache identity 未變，**直接 reuse module object**，不重啟 CLI/subprocess；
- interpreter/module reuse 不可跨 runtime restart 假設；新 interpreter 只需從 verified fixed cache import；
- 每個新 question identity 仍 fresh RNG；module reuse **不重用結果或 RNG outcome**；
- 多個 compatible independent readings 依 `Automatic Batching` 合併成最少 calls；
- 普通 AI interpretation transport 優先 `compact_ai_payload()`／CLI `--format ai-json`；只有 audit-grade raw metadata 或 compatibility 需要才用 full JSON。

核心：

> **Verify once per runtime state; import once per interpreter; draw fresh per question; batch compatible readings; return only minimum sufficient facts。**

## Cache Probe｜先本地、後 GitHub

完整 Runtime fixed cache：

```text
/mnt/data/divination-casting-runtime/randomizer.py
/mnt/data/divination-casting-runtime/verification.json
```

Free ChatGPT capsule core cache（只在完整 Runtime cache FAIL 後於 `Acquisition` probe）：

```text
/mnt/data/divination-casting-runtime/core.py
/mnt/data/divination-casting-runtime/capsule_verification.json
```

`/mnt/data` 不可寫時唯一 fallback：

```text
<runtime-workspace>/.divination-casting-runtime/<same filenames>
```

不 broad filesystem search，不靠 memory 猜第三個位置。

完整 Runtime 最低 probe：

- `randomizer.py` + `verification.json` 存在可解析；
- marker SHA-256 與 script 一致；
- source repository / path / commit 符合 marker；
- algorithm/schema 與 script 一致；
- 本次方法最低 invariant PASS。

Capsule core 最低 probe：

- `core.py` + `capsule_verification.json` 存在可解析；
- marker `cache_locator_version = 4`；
- marker SHA-256 與 `core.py` 一致；
- source repository / `runtime/casting/core.py` / commit 符合 marker；
- `core_version`／algorithm version／supported methods 與 module 一致；
- 本次方法最低 invariant PASS。

Method invariants：

```text
Tarot  → 78 unique cards
Meihua → A/B + 8×8 mapping
Liuyao → six 6/7/8/9 lines, bottom-to-top, 6/9 changing, 7/8 static
```

完整 Runtime probe PASS → Fast Path。Capsule core probe PASS → `Execution` 的 `D. Verified capsule core`。只有以下 trigger 才重新確認 source：使用者要求最新版／重新同步、concrete source-update evidence、audit 需要 marker 沒有的 provenance、相關 probe FAIL。

**Playbook HEAD 更新本身不是 Randomizer refresh trigger。Fresh question means fresh RNG, not fresh program acquisition。**

## Acquisition｜只有 cache FAIL 才讀

```text
Python capability
→ full Runtime fixed-cache probe FAIL
→ capsule-core cache probe
→ PASS ? execute verified core : continue
→ GitHub Connect resolve ai-divination-playbook ref → exact commit
→ preferred: exact full-runtime handoff when product bridge exists
→ otherwise: verified bounded capsule transport
→ write verified cache + marker
→ bounded smoke
→ import
→ fresh execution
```

### A. Preferred full-runtime byte-preserving bridge

這條路徑由三個彼此獨立的 capability 組成：

```text
GitHub source acquisition
→ connector→Python byte-preserving payload handoff
→ Python materialization / verification / execution
```

若產品能把 GitHub Connect 回傳的完整 payload 直接、可觀察、可驗證地交給 Python，優先使用完整 Runtime：

```text
GitHub Connect fetch exact runtime/casting/randomizer.py as base64
→ pass returned complete base64 payload into Python as data only
→ Python base64.b64decode(...)
→ write decoded bytes to fixed cache randomizer.py
→ SHA-256 / marker / method invariant verification
→ import or CLI execute that fixed-cache file
```

這條 bridge 只搬運 canonical bytes，不授權 Python 自己連 GitHub，也不授權模型重建 source。Python 端允許的 materialization logic 只應處理 base64 decode、filesystem write、hash／marker 驗證與 canonical module import／execution；不得在 bridge 中重寫 RNG、牌組、A/B、coin、mapping、schema 或 provenance core。

### B. Free ChatGPT verified bounded capsule transport

若 GitHub acquisition PASS、Python PASS，但產品沒有完整 connector→Python automatic payload bridge，**不得立刻停止**。先嘗試本 Repo 專為 Free ChatGPT cold start 提供的 chunked bounded capsule。Canonical transport contract 是 `chunked-model-mediated-opaque-handoff-v2`：

```text
GitHub Connect fetch same exact commit runtime/casting/CHATGPT_RUNTIME_CAPSULE.json
→ verify schema_version = 2
→ verify authority = derived-transport-cache-only
→ verify transport_contract = chunked-model-mediated-opaque-handoff-v2
→ verify source_path = runtime/casting/core.py
→ verify payload_encoding = base64+zlib and chunk_encoding = ascii
→ verify chunk_count matches chunks[] and admission bounds
→ for each chunk in index order:
     copy only that opaque chunk payload + encoded_length + encoded_sha256 into Python data
     verify ASCII encoded length
     verify SHA-256 of the chunk text bytes
     mismatch ? fresh same-commit capsule read and retry only that failed chunk, up to chunk_retry_limit : accept chunk
→ after every chunk PASS, concatenate accepted chunks by ascending index
→ verify concatenated encoded length == manifest encoded_size
→ Python base64.b64decode(..., validate=True)
→ Python zlib.decompress(...)
→ verify exact decoded byte count == decoded_size
→ verify SHA-256 == manifest decoded_sha256
→ only then write bytes as fixed-cache core.py
→ write capsule_verification.json (locator v4)
→ import that verified core.py
→ execute canonical `core.execute_stochastic()`; bare raw helpers are not valid reading execution
```

Admission / retry contract：

- `chunk_size <= 512` chars、`chunk_count <= 16`、`encoded_size <= 5000` chars、`decoded_size <= 8192` bytes；任一超界 → FAIL CLOSED；
- `chunk_reassembly` 必須是 `index-ascending-concat`；index 必須唯一且完整覆蓋 `0..chunk_count-1`；
- 每個 chunk 都必須在 Python 端以 `encoded_length` + `encoded_sha256` **個別驗證**，不能只在最後驗整包；
- chunk mismatch 時，若 manifest `chunk_retry_required_on_mismatch = true`，**不得立即整次 fail closed**；必須從同一 resolved exact commit fresh-read capsule，僅重取失敗 chunk，再驗證；
- retry 上限使用 manifest `chunk_retry_limit`，目前 canonical v2 為 `2`；超過上限仍 mismatch 才視為 handoff failure；
- fresh retry 不得改 commit/ref、不得用 memory／舊聊天 payload，也不得重送已 PASS chunks 來覆蓋已驗證資料；
- 全部 chunks PASS 後仍須做 concatenated `encoded_size`、base64/zlib、`decoded_size` 與 final `decoded_sha256`；per-chunk PASS **不取代** final canonical-byte identity verification；
- 若所有 chunk hashes PASS、但 final decoded size/hash FAIL，視為 manifest/reassembly/integrity failure，直接 FAIL CLOSED；不得用模型猜哪裡錯、不得改寫 source。

這裡的 model-mediated step 是**明確 admission 的 bounded opaque transport**，不是 source transcription：

- 模型只搬運 capsule manifest 中的 opaque chunk payload／length／hash 與 final size／hash metadata，不翻譯、不改寫、不補字元；
- Python 必須在寫入／import 前完成 per-chunk exact verification、deterministic reassembly、decode + decompress + final size + SHA-256 exact verification；
- 任一字元在搬運中遺失／改變 → 該 chunk length/hash 不一致；依上述 bounded retry contract 最小重取，而不是默默接受；
- 不得從 chunk／decoded payload 内容「理解後重寫」另一支 Python；
- manifest 與 retry 都必須由同一 resolved exact commit 的 GitHub Connect retrieval 取得；memory／舊聊天中的 payload 不可代替 current acquisition；
- `CHATGPT_RUNTIME_CAPSULE.json` 是 derived transport cache，canonical stochastic authority 仍是 `core.py`；CI 必須驗證 chunks deterministic reassembly 後可 exact round-trip 回該 core bytes。

這條路徑存在的目的就是處理 Free ChatGPT 已實測的 host 限制：GitHub Connect 可讀、Python 可執行，但沒有 connector payload object 可直接注入 Python，而且 monolithic opaque payload 曾實測出現「decoded size PASS、final SHA-256 FAIL」的搬運失真。**只要 v2 chunks 與 final canonical bytes exact verification PASS，這不再是 `MATERIALIZATION HANDOFF CAPABILITY GAP`；它已建立可驗證的 byte-preserving handoff。**

只有以下情況才標記 `MATERIALIZATION HANDOFF CAPABILITY GAP`：

- direct full-runtime bridge 不可用，且同 commit capsule 無法取得；
- capsule／chunk metadata 不符或超過 admission bounds；
- chunk payload 在 required fresh same-commit retries 後仍無法通過 encoded length/SHA-256；
- chunks 無法完整、唯一、依 index 重組，或 concatenated encoded_size 不符；
- base64／zlib decode、decoded size 或 final SHA-256 驗證失敗；
- Python execution capability 本身不可用。

任何「payload 已交給 Python」claim 都必須有本 session 可觀察的 **per-chunk verification + final decode/hash** evidence；只有看到 final size/hash PASS 才能宣稱 canonical `core.py` 已 materialize。

**不得只因 connector 與 Python 是不同 capability，就直接推論 canonical source 無法 materialize；也不得只因兩端都存在，就反向推論 handoff 一定可用。** Retrieval、handoff、execution 仍是獨立 capability；chunked capsule v2 是一條被逐段與最終驗證後才成立的 handoff implementation。

### Canonical Execution Identity｜取得哪份 source，就執行哪份 implementation

完整 Runtime 路徑真正被 import／CLI 執行的 stochastic implementation 必須是 canonical `randomizer.py`（及其 import 的 canonical core）或 byte-for-byte verified copy。

Capsule 路徑真正被執行的 stochastic implementation必須是 capsule exact 解碼、size/hash 驗證後得到的 canonical `core.py` bytes。`randomizer.py` production adapter 也直接 import 同一份 `core.py`，因此**不存在第二套 stochastic implementation**。

允許：

- 將 connector 取得的完整 Runtime canonical source 原樣 materialize 到 fixed cache，驗證後執行；
- 將 admitted capsule 的 opaque payload exact 解碼回 canonical `core.py`，驗證後執行；
- 寫最薄 caller／wrapper 去 import verified canonical module、呼叫 **唯一正式 stochastic entrypoint `core.execute_stochastic()`**；wrapper 不得直接把 `_draw_tarot_raw()`／`_cast_plum_raw()`／`_cast_liuyao_raw()` 的 bare output 當 Raw Draw / Cast Fact，也不得重寫 RNG、牌組、A/B、coin、mapping 或 method core。

禁止：

- 讀完 canonical source 後另寫 `/tmp/cast.py`、inline Python、shell heredoc 或其他 transcription／reimplementation，自己重做 stochastic core再拿結果當 Runtime Draw / Cast；
- 因「邏輯看起來等價」就以 `secrets`／`random`／手寫 modulo／手寫洗牌／手寫 three-coin 取代 canonical implementation；
- 未通過 capsule exact size/hash verification 就 import／execute；
- 自製程式輸出卻標示 canonical `source`、algorithm/schema version、runtime source commit 等 provenance，讓它看起來像 canonical execution。

若所有 admitted canonical materialization／capsule 路徑都無法可信執行，本次 runtime 必須 fail closed 或走本章明確允許的 runtime fallback；**不得用模型重寫 implementation 來補洞。**

完整 Runtime marker 最低（既有 locator v3）：

```json
{"verified":true,"cache_locator_version":3,"runtime_source_repository":"masini1491/ai-divination-playbook","runtime_source_path":"runtime/casting/randomizer.py","runtime_source_ref":"main","runtime_source_commit":"<SHA or unknown>","runtime_copy_sha256":"<sha256>","algorithm_version":"<version>","schema_version":"<version>","supported_methods":["tarot","plum","liuyao"],"tarot_deck_size":78}
```

Capsule core marker 最低（locator v4）：

```json
{"verified":true,"cache_locator_version":4,"runtime_source_repository":"masini1491/ai-divination-playbook","runtime_source_path":"runtime/casting/core.py","capsule_path":"runtime/casting/CHATGPT_RUNTIME_CAPSULE.json","runtime_source_ref":"main","runtime_source_commit":"<SHA>","runtime_copy_sha256":"<decoded_sha256>","core_version":"1","algorithm_version":"2","supported_methods":["tarot","plum","liuyao"],"tarot_deck_size":78}
```

`cache_locator_version = 3` 是 full-runtime repository/path authority locator；`cache_locator_version = 4` 是 verified capsule-core locator。兩者都不是 Randomizer algorithm/schema revision。

GitHub repository acquisition **只走 GitHub Connect**。connector unavailable／blocked 且無 verified cache → `ACCESS BLOCKED`。禁止 public HTML、raw URL、generic Web、Python HTTP、curl/wget/git clone。

GitHub retrieval capability ≠ connector→Python byte-preserving handoff capability ≠ Python execution ≠ repository write authority。

## Method Contracts

### Tarot

- 78 張；單題 1～24；同題不重複；
- 每個 question identity fresh full-deck shuffle；
- 每張 orientation 獨立；
- 多人物／多題各自獨立 draw identity。

### Meihua

- A/B 各 `000～999`；
- `A % 8` 上卦、`B % 8` 下卦、`(A+B) % 6` 動爻；餘 0 → 坤／第 6 爻；
- A/B 與 canonical derived 本卦／上下卦／動爻共同形成 Cast Fact。

### Liuyao Raw Cast

```text
3 fair binary coins per line
陰=2, 陽=3
6=老陰動, 7=少陽靜, 8=少陰靜, 9=老陽動
初爻 → 上爻 (bottom-to-top)
```

Raw Cast Fact 至少保留 six values；需要 audit／engine 時保留 coin values。Raw Cast ≠ 完整納甲盤；本卦／之卦／納甲／六親／世應／六神／伏神等依 `LIUYAO.md` 由 deterministic engine 建立。engine failure 不重起。

## Execution｜優先順序

### A. In-memory direct API｜最快

同一 persistent Python interpreter 且 verified full Runtime module 已 import：

```python
payload = randomizer.generate_payload("tarot", count=5, repeat=4, source_commit=SHA)
result = randomizer.compact_ai_payload(payload)
```

Meihua／Liuyao：

```python
randomizer.generate_payload("plum", repeat=4, source_commit=SHA)
randomizer.generate_payload("liuyao", repeat=4, source_commit=SHA)
```

這是 performance optimization，不是 correctness requirement。若 interpreter 不持久，直接從 verified cache import 後呼叫即可。

### B. CLI AI transport｜預設 subprocess fallback

```text
python /mnt/data/divination-casting-runtime/randomizer.py tarot --count 5 --repeat 4 --format ai-json --source-commit <SHA>
python /mnt/data/divination-casting-runtime/randomizer.py plum --repeat 4 --format ai-json --source-commit <SHA>
python /mnt/data/divination-casting-runtime/randomizer.py liuyao --method coins --repeat 4 --format ai-json --source-commit <SHA>
python /mnt/data/divination-casting-runtime/randomizer.py batch --counts 5,3,6,5 --method tarot --format ai-json --source-commit <SHA>
```

### C. Full JSON｜只在需要時

`--format json` 保留完整 canonical output，適用 audit、debug、完整 provenance、compatibility。普通 ChatGPT interpretation 不應為形式支付 full JSON token cost。

`ai-json` 是**transport projection**，不是新 RNG algorithm：

- algorithm version 不因此改變；
- full canonical schema 仍存在；
- `ai_schema_version` 獨立標示 compact projection；
- Tarot 保留 full card name + orientation；
- Meihua 保留 A/B、上下卦、本卦、動爻；
- Liuyao 保留 line values + coin values + line order；
- 保留 source、algorithm/schema、source commit、Taipei timestamp/timezone；
- 省略可由 canonical contract 推回或普通 interpretation 不需要的重複 descriptive fields。

### D. Verified capsule core｜Free ChatGPT cold-start path

當 capsule-core marker v4 PASS，或本次 acquisition 剛完成 exact capsule verification，可直接 import verified `core.py`：

```python
# Tarot
result = core.make_result("tarot", 5)

# Meihua
result = core.make_result("plum")

# Liuyao
result = core.make_result("liuyao")
```

這些回傳值就是 canonical stochastic Raw Draw / Cast Fact。`runtime_source_commit`、capsule/core SHA、執行時間等 provenance 由 caller 依實際 tool evidence另外保存；不得由 core 內不存在的欄位捏造。多個已合法固定的 independent readings 可用最薄 caller 對 `core.make_result(...)` 做 bounded loop；不得在 caller 重寫 stochastic core。

## Automatic Batching｜一次執行，多個獨立 Fact

同一 request 有多個**已合法成立且 contract 已固定**的 independent question identities 時，優先最少 execution calls。

- full Runtime：同方法同 contract → `--repeat N`／direct API `repeat=N`；Tarot 張數不同 → `batch --counts ...`／direct API batch；
- verified capsule core：允許在同一 Python invocation 依 pre-fixed child order bounded loop 呼叫 `core.make_result(...)`；每個 call 仍 fresh RNG；
- mixed methods → 依 method 分組，各自最少 calls；不要濫用 legacy `both`。

Batching Contract：

1. 先固定 child order／contracts，才 execution。
2. `results[0..N-1]` 依 pre-fixed order mapping；抽後不得重排。
3. 每個 child fresh RNG；batch 不使用上一題剩餘牌組。
4. `repeat=N` 或 bounded core loop 代表 N 個合法獨立 readings；不得拿同題 N 抽投票／挑最好。
5. execution envelope 可共享 timestamp，但 question／Draw-Cast Fact／Reading Record／Reality Update identities 分離。
6. compatible batch 可用時，無理由逐題啟動 Python 屬不必要 overhead。
7. output count/order/mapping 無法可信確認 → fail closed；不盲目重跑整批。

> **Batch execution ≠ merged reading。**

## Fact / Fail-Closed

每個 child 都遵守：

```text
Contract fixed
→ Runtime execution
→ Raw result captured
→ Draw / Cast Fact fixed
→ Structured Method Fact if required
→ Interpretation
```

不得邊解讀邊重抽。Runtime／source／parse failure 不得由模型生成替代結果或偷換 RNG。

若 batch 部分 child 已可信固定、其他 child failure，不得重跑整批覆蓋已固定 facts；保留可信 child，對 unresolved child 最小修復或 fail closed。

若 direct connector→Python full-runtime handoff unavailable，**先嘗試本章 admitted verified capsule path**。只有 capsule 也無法取得／搬運／exact 驗證／執行，或 Python 不可用時，才可改用仍在線的 deployed Randomizer Web UI 或使用者自行抽／起；這是 runtime fallback，不改變 GitHub repository authority。若 GitHub source acquisition 本身被阻擋，仍遵守 `ACCESS BLOCKED`。

Runtime 快、batch 方便都不創造補占 authority；同題／新題／補占仍由 `READING_LIFECYCLE.md` 決定。

## Provenance｜需要 audit／保存才讀

Canonical Randomizer version semantics：

```text
source: divination-casting-randomizer-python
algorithm_version: 2
schema_version: 4
ai_schema_version: 1  # compact transport only
core_version: 1      # stochastic core transport identity, not algorithm version
```

`source` 是 logical runtime identity；repository consolidation 或 wrapper/core split 不改 logical identity 或 algorithm/schema versions。

Runtime timestamp：**timestamp capture 是 canonical stochastic runtime responsibility，不是 caller responsibility。** Full Runtime 與 capsule core 都必須透過 `core.execute_stochastic()` 原子產生 stochastic result + `generated_at_utc` + `generated_at_taipei` + `Asia/Taipei`；GitHub commit time 不是 draw time。任何只有牌面／A-B／6-7-8-9、卻缺 execution timestamp 的新 stochastic output，都是 `STOCHASTIC EXECUTION FACT INVALID`，不得進 interpretation、deterministic downstream、Reading Record 或 Vault，也不得事後補時間冒充同一次 execution。

共同 provenance：source/tool、algorithm、source repository/path/ref/commit（能取得時）、actual draw/cast timestamp/timezone。full Runtime execution 的 source path 是 `runtime/casting/randomizer.py`；capsule core execution 的 canonical source path 是 `runtime/casting/core.py`，並可另記 capsule path／decoded SHA。歷史 legacy-repo commit provenance 保持有效，不重寫。Meihua 另存 A/B；Liuyao 另存 raw six lines + bottom-to-top；deterministic engine provenance 分開保存。

使用者可見預設只顯示必要結果、實際時間與 `Canonical Randomizer v2`，不要 dump audit metadata。

## Validation｜Randomizer 更新後

Common：

- `randomizer.py` stochastic functions 必須直接重用 `core.py`，不可保留第二套 RNG／牌組／A/B／coin implementation；
- full JSON 與 `ai-json` 都可解析；
- compact projection 與同一次 full payload 的 stochastic facts exact parity；
- `ai-json` 不改 RNG／algorithm version，`ai_schema_version` 獨立；
- direct `generate_payload()` 與 CLI contracts parity；
- UTC/Taipei 同一瞬間、Taipei `+08:00`；
- full-runtime cache marker/hash/version/invariant reuse；PASS 不重抓 source；
- capsule artifact 必須以 chunked v2 deterministic index-order reassembly 後 `base64+zlib` exact round-trip 回 current `core.py` bytes；每個 chunk encoded length/SHA-256、concatenated encoded_size、decoded size + final SHA-256 全部 exact match；
- capsule `chunk_size <= 512`、`chunk_count <= 16`、`encoded_size <= 5000` chars、decoded core ≤ 8192 bytes；超過即需重新檢討 transport admission；
- chunk mismatch 必須只 fresh-read 同 commit 的失敗 chunk 並依 manifest retry limit bounded retry；不得立即整次 fail closed，也不得覆蓋已 PASS chunks；
- capsule core marker v4 PASS 後可直接 reuse core，不重新抓 GitHub；new question 仍 fresh RNG；
- in-memory reuse 不重用結果；new question fresh RNG；
- `--repeat`／batch／bounded core loop result count/order/independent identity 正確；
- GitHub acquisition only through GitHub Connect；
- direct connector→Python handoff capability gate 能區分 PASS 與 gap；direct bridge unavailable 時 verified chunked capsule transport 可建立 bounded byte-preserving handoff，且不讓 Python 自己 retrieval GitHub；
- capsule per-chunk retry exhausted、reassembly、decode/final hash failure 必須 fail closed，不得 fallback 到模型重寫 stochastic core；
- `PLAYBOOK_INDEX.json` 與 method owners 的 full Runtime pointer 仍指向 `runtime/casting/randomizer.py`；
- `runtime/casting/MIGRATION_SOURCE.json` 永久保存 pinned legacy import provenance；current production files 可在 canonical repo 依正式 contract/version governance 演進，不再要求 byte-for-byte 等於 legacy snapshot。