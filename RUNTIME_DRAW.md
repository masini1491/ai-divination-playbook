# ChatGPT Runtime Draw｜程式抽牌／起卦治理

本章是 ChatGPT／AI 自行執行 stochastic draw / cast 的 canonical runtime authority。

Canonical implementation：

```text
masini1491/divination-casting-randomizer/randomizer.py
```

支援：Tarot、Meihua、Liuyao three-coin raw cast。六爻 deterministic structured facts 由 `LIUYAO.md` 治理。

> **Language-model generation ≠ random draw / cast。** 宣稱 Runtime Draw / Cast 必須有真正 canonical runtime execution result。

## Section Router｜最低必要載入

- **普通代抽／代起卦 + verified cache PASS** → `Fast Path` + 對應 Method Contract + `Execution` + `Fact / Fail-Closed`；STOP。
- **cache FAIL／首次 acquisition** → 再讀 `Acquisition`。
- **多個合法獨立 readings** → `Automatic Batching`。
- **完整 provenance／audit／保存** → 再讀 `Provenance` + `READING_RECORD.md`。
- **補占／重占／copy-ready** → `READING_LIFECYCLE.md`／`CHATGPT_OUTPUT.md`。
- **維護 Randomizer** → 本檔 `Validation`；implementation tests 屬 Randomizer repo。

不要為形式載入 acquisition／audit／maintenance sections。**Fast path 已足夠時就 STOP。**

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

固定位置：

```text
/mnt/data/divination-casting-runtime/randomizer.py
/mnt/data/divination-casting-runtime/verification.json
```

`/mnt/data` 不可寫時唯一 fallback：

```text
<runtime-workspace>/.divination-casting-runtime/randomizer.py
<runtime-workspace>/.divination-casting-runtime/verification.json
```

不 broad filesystem search，不靠 memory 猜第三個位置。

最低 probe：

- script + marker 存在可解析；
- marker SHA-256 與 script 一致；
- source commit 為 exact SHA 或明確 weaker provenance；
- algorithm/schema 與 script 一致；
- 本次方法最低 invariant PASS。

Method invariants：

```text
Tarot  → 78 unique cards
Meihua → A/B + 8×8 mapping
Liuyao → six 6/7/8/9 lines, bottom-to-top, 6/9 changing, 7/8 static
```

PASS → Fast Path。只有以下 trigger 才重新確認 Randomizer source：使用者要求最新版／重新同步、concrete source-update evidence、audit 需要 marker 沒有的 provenance、probe FAIL。

**Playbook HEAD 更新本身不是 Randomizer refresh trigger。Fresh question means fresh RNG, not fresh program acquisition。**

## Acquisition｜只有 cache FAIL 才讀

```text
Python capability
→ GitHub Connect resolve Randomizer ref → exact commit
→ GitHub Connect acquire exact revision randomizer.py
→ bounded smoke
→ write fixed cache + verification marker
→ import
→ fresh execution
```

Marker 最低：

```json
{"verified":true,"cache_locator_version":2,"runtime_source_path":"masini1491/divination-casting-randomizer/randomizer.py","runtime_source_ref":"main","runtime_source_commit":"<SHA or unknown>","runtime_copy_sha256":"<sha256>","algorithm_version":"<version>","schema_version":"<version>","supported_methods":["tarot","plum","liuyao"],"tarot_deck_size":78}
```

GitHub repository acquisition **只走 GitHub Connect**。connector unavailable／blocked 且無 verified cache → `ACCESS BLOCKED`。禁止 public HTML、raw URL、generic Web、Python HTTP、curl/wget/git clone。

GitHub retrieval capability ≠ Python execution ≠ repository write authority。

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

同一 persistent Python interpreter 且 verified module 已 import：

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

## Automatic Batching｜一次執行，多個獨立 Fact

同一 request 有多個**已合法成立且 contract 已固定**的 independent question identities 時，優先最少 execution calls。

- 同方法同 contract → `--repeat N`／direct API `repeat=N`；
- Tarot 張數不同 → `batch --counts ...`／direct API batch；
- mixed methods → 依 method 分組，各自最少 calls；不要濫用 legacy `both`。

Batching Contract：

1. 先固定 child order／contracts，才 execution。
2. `results[0..N-1]` 依 pre-fixed order mapping；抽後不得重排。
3. 每個 child fresh RNG；batch 不使用上一題剩餘牌組。
4. `repeat=N` 代表 N 個合法獨立 readings；不得拿同題 N 抽投票／挑最好。
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

若 canonical source 已取得但 Python 不可用，可改用已部署 Randomizer Web UI 或使用者自行抽／起；若 GitHub source acquisition 本身被阻擋，仍遵守 `ACCESS BLOCKED`。

Runtime 快、batch 方便都不創造補占 authority；同題／新題／補占仍由 `READING_LIFECYCLE.md` 決定。

## Provenance｜需要 audit／保存才讀

Canonical Randomizer version semantics：

```text
algorithm_version: 2
schema_version: 4
ai_schema_version: 1  # compact transport only
```

Runtime timestamp：`generated_at_utc` + `generated_at_taipei` + `Asia/Taipei`；GitHub commit time 不是 draw time。普通 `ai-json` 至少傳 Taipei timestamp；正式保存若需要 UTC，從 full canonical payload 取得，不自行捏造。

共同 provenance：source/tool、algorithm/schema、source ref/commit、actual draw/cast timestamp/timezone。Meihua 另存 A/B；Liuyao 另存 raw six lines + bottom-to-top；deterministic engine provenance 分開保存。

使用者可見預設只顯示必要結果、實際時間與 `Canonical Randomizer v2`，不要 dump audit metadata。

## Validation｜Randomizer 更新後

Common：

- full JSON 與 `ai-json` 都可解析；
- compact projection 與同一次 full payload 的 stochastic facts exact parity；
- `ai-json` 不改 RNG／algorithm version，`ai_schema_version` 獨立；
- direct `generate_payload()` 與 CLI contracts parity；
- UTC/Taipei 同一瞬間、Taipei `+08:00`；
- cache marker/hash/version/invariant reuse；PASS 不重抓 source；
- in-memory reuse 不重用結果；new question fresh RNG；
- `--repeat`／batch result count/order/independent identity 正確；
- GitHub acquisition only through GitHub Connect。

Tarot：78 unique、count boundary、單題無重複、multi-reading independent shuffle、orientation legal。

Meihua：A/B range、moving line 1～6、64 mapping complete。

Liuyao：six bottom-to-top lines、3 coins/line、coin ∈ {2,3}、value ∈ {6,7,8,9}、6/9 changing、7/8 static、theoretical 1/8–3/8–3/8–1/8、Randomizer 不產生納甲 facts。

Implementation tests 屬 Randomizer repo；Playbook 負責 runtime provenance、authority boundary、fast-path governance 與 fail-closed。