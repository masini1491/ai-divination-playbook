# ChatGPT Runtime Draw｜程式抽牌／起卦治理

本章是 ChatGPT／AI 在具有實際程式執行能力時，**自行執行塔羅抽牌或梅花起卦**的主要 authority。

本章不實作 RNG，也不複製抽牌程式。Canonical implementation 由：

- `masini1491/tarot-plum-randomizer/randomizer.py`

維護。

核心原則：

> **Language-model generation ≠ random draw。**
>
> 模型能說出牌名，不代表已完成隨機抽牌；宣稱 Runtime Draw 必須有真正的 runtime execution result。

## Section Router｜依 Runtime 任務只讀最低必要段落

本檔可以按 section 漸進式讀取，不要求每次全文載入：

- **普通 ChatGPT 代抽／代起卦** → 第 1～6 節 + 第 11～12 節；依方法只讀 Tarot 或 Meihua contract。
- **需要版本／timestamp／完整 provenance／audit** → 再讀第 7～10 節。
- **判斷同題能否重抽、補占或 copy-ready vs runtime** → 第 13～14 節，並依需要讀 `READING_LIFECYCLE.md`。
- **維護或驗證 canonical Randomizer** → 第 3、7～9、15 節；實際測試仍屬 Randomizer repo responsibility。
- **正式保存 Runtime Draw** → 第 8～11 節 + `READING_RECORD.md`。

若目前 task 已能由 exact section 唯一處理，直接讀該 section；router 用於降低載入成本，不是額外 ceremony。

## 1. 何時可以使用 Runtime Draw

只有同時符合以下條件時，ChatGPT 才可宣告「自行抽牌／起卦」：

1. 使用者明確要求 ChatGPT 自己抽，或上下文已授權由 ChatGPT 代為抽牌／起卦。
2. 本次 execution environment 具有可實際執行 Python 的能力。
3. 能取得並執行 `tarot-plum-randomizer` 的 canonical Python implementation，或已有與該 implementation 明確同步且可驗證的本地副本。
4. 題目、牌位／起卦契約已在結果出現前固定。
5. 執行結果可以被保留為 `DRAW / CAST FACT`，而不是只留下模型重述。

若只是模型「隨機想一組牌」，不得標記為 Runtime Draw。

## 2. Runtime Capability Gate

### 2.1 Deterministic Cache Slot｜先查固定位置，再決定是否抓 GitHub

對普通 Runtime Draw，**第一個 source-related action 必須是 local cache probe，而不是 GitHub fetch。** 不再用「任意 workspace 搜尋」猜先前把程式放在哪裡。

優先使用以下 deterministic cache slot：

```text
/mnt/data/tarot-plum-runtime/randomizer.py
/mnt/data/tarot-plum-runtime/verification.json
```

若 execution environment 沒有可寫的 `/mnt/data`，才依下列唯一 fallback：

```text
<runtime-workspace>/.tarot-plum-runtime/randomizer.py
<runtime-workspace>/.tarot-plum-runtime/verification.json
```

其中 `<runtime-workspace>` 必須是 execution surface 明確提供、可直接觀察的 current workspace；不得靠 conversation memory 猜 path，也不得為找 cache 做廣泛檔案系統掃描。

若上述兩種 locator 都不可建立／不可觀察，視為 **cache unavailable**，直接進入正常 source acquisition；不要另外發明第三個隨機 cache path。

### 2.2 Mandatory Reuse Probe｜固定順序的重用檢查

在任何 GitHub source acquisition、raw download 或 materialize 前，依 deterministic cache slot 檢查：

- `randomizer.py` 是否存在且可 import／execute；
- `verification.json` 是否存在且可解析；
- marker 記錄的 `runtime_copy_sha256` 是否與目前 `randomizer.py` 一致；
- marker 的 `runtime_source_commit` 是否為可驗證 exact commit SHA，或若 unavailable 是否被明確標記為 weaker provenance；
- `algorithm_version`、`schema_version` 是否與目前程式一致；
- Tarot deck 是否仍為 78 張且唯一，或執行等價的最低必要 invariant check。

若以上 PASS：

- 直接使用 cached `randomizer.py` 執行本題新的 draw／cast；
- **本次 draw 禁止 GitHub fetch／raw download／重新 materialize canonical source；**
- 不重跑完整 smoke test／完整 invariant suite；
- 每個新的 question identity 仍 fresh execution／fresh shuffle，絕不重用上一題結果。

只有以下情況之一成立，才可以在 cache PASS 後仍重新確認 Randomizer source：

- 使用者明確要求「Randomizer 最新版／重新同步最新版」；
- 有 concrete evidence 顯示 `masini1491/tarot-plum-randomizer` 的 canonical source 已更新；
- 使用者要求完整 provenance，而現有 marker 缺少完成該 audit 所必要、且無法由 local copy 證明的 source identity；
- local verification 本身 FAIL／無法完成。

**Playbook 本身的 HEAD 更新，不等於 Randomizer source 已更新。** 不得只因重新讀了最新版 Playbook 就順手重新下載 `randomizer.py`。

Conversation context 記得「之前載入過」本身不算 runtime evidence；真正的 reuse evidence 是 deterministic cache slot 中仍實際存在且通過驗證的檔案。

### 2.3 First Acquisition｜第一次取得後必須回填固定 cache slot

ChatGPT 在第一次需要自行抽牌，或 deterministic cache probe 不成立時，做最低充分 capability check：

- Python 是否可執行；
- canonical `randomizer.py` 是否可取得；
- 必要標準庫是否可用；
- 程式能否完成一次 bounded smoke test。

首次取得並成功 smoke-test `randomizer.py` 後，只要 runtime 有上述可用 cache slot，**必須**把 canonical copy 與 verification marker 寫入該 slot，供後續 turn 直接 reuse；不要只把檔案留在臨時、不可預期名稱的位置。

Marker 最低包含：

```json
{
  "verified": true,
  "cache_locator_version": 1,
  "runtime_source_path": "masini1491/tarot-plum-randomizer/randomizer.py",
  "runtime_source_ref": "main",
  "runtime_source_commit": "<exact immutable commit SHA or unknown>",
  "runtime_copy_sha256": "<sha256>",
  "algorithm_version": "<version>",
  "schema_version": "<version>",
  "tarot_deck_size": 78
}
```

Marker 只屬 temporary execution state，不是新的 canonical authority，也不是 Reading Record evidence layer。

若 runtime／kernel 被重建，cache slot 不存在，重新取得一次 canonical source 是正常 cold-cache 行為；**不存在的 cache 不得靠聊天記憶假裝仍存在。**

不要為了能力盤點去掃描所有 runtime、compiler、sandbox 套件或任意目錄；只驗證本次真正需要的 Python capability與固定 cache slot。

核心流程：

```text
Runtime Draw requested
→ resolve deterministic cache slot
→ probe randomizer.py + verification.json
   ├─ PASS → GitHub acquisition forbidden for this draw → fresh RNG execution
   └─ FAIL / absent / unavailable → canonical source acquisition
        → resolve moving ref to exact commit
        → acquire exact revision randomizer.py
        → bounded smoke test
        → write fixed cache slot + marker
        → fresh RNG execution
```

核心原則：**Fresh question means fresh RNG, not fresh program acquisition。**

若 execution environment 不可觀察或不可執行，不得因模型「通常能跑 Python」就假設本次可用。

## 3. Canonical Runtime Source

Runtime Draw 的 canonical implementation 是：

```text
masini1491/tarot-plum-randomizer/randomizer.py
```

Playbook 只保存治理規則，不另外維護一份 Python 抽牌程式，避免 Web、Python、Playbook 三份演算法 drift。

### 3.1 Source Acquisition Layering｜取得 canonical script 的優先序

`repository retrieval capability` 與 `Python runtime network capability` 是不同層級；Python sandbox 無法直接連 GitHub，不代表 ChatGPT 無法透過 repository-native connector 取得 canonical source。

**只有 §2 deterministic cache probe FAIL／absent／unavailable，或 §2 明列的 Randomizer-specific refresh trigger 成立時，才允許進入本節。**

#### Moving Ref Resolution Gate｜`main` 只用來選版本

若取得的是浮動 ref（例如 `main`），在把程式寫入 cache 或宣告 snapshot provenance 前，先以最低成本 read-only identity probe 將該 ref resolve 成 **exact immutable commit SHA**。

規則：

- `main`／其他 moving ref 只用來選 current revision；真正的 runtime snapshot identity 是該次 resolved commit SHA。
- Source acquisition 應盡可能直接讀取 resolved commit 上的 `randomizer.py`，避免「先解析 SHA、後又從已移動的 main 讀檔」造成 mixed snapshot。
- Marker 應同時保存原始 ref 與 exact commit；後續 cache freshness 比較以 exact commit 為主。
- 若 exact commit identity 因 connector／API capability 限制無法取得，但檔案內容仍可可靠取得，只有在本次不要求 immutable provenance 時才可繼續，並將 `runtime_source_commit` 明確記為 `unknown`；不得把 `main` 字串或 branch 名稱冒充 commit identity。
- 若使用者要求最新版＋完整 provenance／audit，而 exact revision 無法建立，應 fail closed 在 provenance boundary，不宣稱已建立 immutable canonical snapshot。

依最低充分順序：

1. 若目前環境已有可直接讀取 GitHub repository 的 **connected GitHub tool／connector**，優先用它先 resolve 指定 `main`／ref 為 exact commit SHA，再取得該 exact revision 的 canonical `randomizer.py`。
2. 取得 source 後，將該檔案寫入／materialize 至 §2 的 deterministic cache slot；若該 slot 不可用，才使用 current runtime 明確提供的 temporary execution path。
3. bounded smoke test 成功後，建立／更新 §2 的 `verification.json`；後續普通 draw 直接走 cache probe，不再重新抓 GitHub。
4. 若 GitHub connector 不可用，再評估 GitHub public/raw/Web access；只有在必要時才要求 Python runtime 自己具備外網／DNS／HTTPS 能力。
5. 若已有本地副本但不在 deterministic cache slot，不把「可能是以前下載的」當成已驗證 cache；除非能在不做 broad filesystem search 的前提下由 current runtime 明確定位並驗證，否則按 cold cache 處理。
6. Connector 能讀 repository ≠ Python runtime 能連網 ≠ repository write authority。這三種 capability 不得互相推導。
7. 若任何取得路徑只拿到不完整、截斷或無法確認為 canonical target 的 source，視為 acquisition gap，不能因「看起來像 randomizer」就執行並宣稱 canonical Runtime Draw。

對已通過 cache probe 的既有 runtime copy，不要求每題都重新查 Randomizer `main` 是否有新 commit。Randomizer freshness 只由 §2.2 的明確 trigger 啟動。

若 freshness trigger 成立，推薦先只做 cheap ref identity probe：

```text
cached runtime_source_commit = ABC
current main resolves to ABC
→ cache remains current; do not redownload

cached runtime_source_commit = ABC
current main resolves to DEF
→ acquire DEF/randomizer.py
→ verify
→ replace cache + marker
```

推薦正常流程：

```text
固定 cache slot probe
  ↓ PASS
fresh Runtime Draw

  ↓ FAIL / absent / unavailable
resolve Randomizer ref → exact commit SHA
→ GitHub connector / repository-native read at exact revision
→ canonical randomizer.py + source evidence
→ deterministic cache slot
→ Python bounded smoke test
→ write verification.json
→ Runtime Draw
```

若 ChatGPT 取得的是 repo 某個 commit 的檔案，應在內部 provenance 中保留該 commit SHA。GitHub 的 commit time 只代表**該程式版本提交時間**，不是抽牌時間。

若未能確認來源版本，可記 `runtime_source_commit: unknown`，但不得捏造 SHA，也不得把 moving ref 當成 immutable identity。

## 4. Tarot Runtime Contract

Runtime Tarot 必須維持 Randomizer 的 canonical contract：

- 完整 78 張牌；
- 單題 1～24 張；
- 同一題不重複；
- 每個 question identity 都重新建立完整牌組並重新洗牌；
- 正／逆位固定啟用且每張獨立抽取；
- 多人物／多題平行抽牌時，每題是獨立 draw identity，不共用上一題剩餘牌組。

例如四個人物各抽 5 張，應形成四次獨立 shuffle，而不是一次洗牌後連抽 20 張分組。

## 5. Meihua Runtime Contract

若使用 Runtime Draw 起梅花，維持 canonical 雙數契約：

- A、B 各為 `000～999`；
- `A % 8` → 上卦；
- `B % 8` → 下卦；
- `(A+B) % 6` → 動爻；
- 八卦餘 0 → 坤；
- 動爻餘 0 → 第 6 爻。

Runtime result 中的 A／B、本卦、上下卦與動爻視為該次 canonical casting input。解讀端不得在看到卦象後重新取數、改用時間起卦或替換 A／B。

## 6. Preferred Invocation

有 Python runtime 時，建議直接執行 Randomizer CLI。若 cache probe 已通過，直接從 deterministic cache slot 執行；不要先重新抓 GitHub。

例如 `/mnt/data` cache slot 可用時：

單題塔羅：

```text
python /mnt/data/tarot-plum-runtime/randomizer.py tarot --count 6 --format json --source-commit <SHA>
```

梅花：

```text
python /mnt/data/tarot-plum-runtime/randomizer.py plum --format json --source-commit <SHA>
```

塔羅＋梅花：

```text
python /mnt/data/tarot-plum-runtime/randomizer.py both --count 6 --format json --source-commit <SHA>
```

多題：

```text
python /mnt/data/tarot-plum-runtime/randomizer.py batch --counts 5,5,6,3 --format json --source-commit <SHA>
```

若使用 workspace fallback slot，將上方 script path 換成 `<runtime-workspace>/.tarot-plum-runtime/randomizer.py`。

AI integration 優先使用 JSON，避免把人類排版重新解析成機械欄位。

## 7. Version Semantics｜版本語意

`algorithm_version` 只代表**抽牌／起卦演算法契約**。只有下列內容真的改變時才升版：

- 牌組或抽牌範圍；
- RNG／rejection sampling／shuffle 邏輯；
- 正逆位產生方式；
- 梅花 A/B 與取卦公式；
- 其他會改變實際抽取分布或結果契約的核心方法。

若只是新增 timestamp、commit provenance、JSON 欄位或其他輸出 metadata，不應升 `algorithm_version`；這類變化使用獨立的 `schema_version`。

目前 canonical Randomizer：

```text
algorithm_version: 1
schema_version: 2
```

因此使用者可見仍可寫：

```text
Canonical Randomizer v1
```

不需要因 provenance schema 更新而顯示 v2。

## 8. Draw Timestamp｜抽牌時間

Runtime Draw 應保存實際程式執行當下的 timestamp：

```text
generated_at_utc: <UTC ISO-8601>
generated_at_taipei: <Asia/Taipei ISO-8601, UTC+08:00>
timezone: Asia/Taipei
```

規則：

- `generated_at_utc` 由 runtime 在執行當下取得 UTC。
- `generated_at_taipei` 由同一 timestamp 轉成 `Asia/Taipei`。
- GitHub commit timestamp 只能當版本 provenance，不能替代 draw timestamp。
- 若 Runtime 無法可信取得時間，標示 unavailable，不要自行補一個看似合理的時間。

這些欄位主要用於內部／JSON provenance。使用者可見回覆不需要預設顯示 UTC、GitHub commit time 或 SHA。

## 9. Internal Provenance｜內部來源紀錄

Runtime Draw 至少在工具輸出或正式紀錄中保存：

```text
cards_source: chatgpt-runtime
runtime_tool: tarot-plum-randomizer-python
runtime_algorithm_version: <algorithm_version>
runtime_schema_version: <schema_version>
runtime_source_ref: <main / tag / other declared ref>
runtime_source_commit: <exact commit SHA or unknown>
generated_at_utc: <tool output>
generated_at_taipei: <tool output>
timezone: Asia/Taipei
```

梅花則另外保存：

```text
casting_source: chatgpt-runtime
raw_input: A, B
```

`chatgpt-runtime` 表示「ChatGPT 實際執行 canonical runtime tool」，不是「ChatGPT 自己用語言生成結果」。

Provenance precision 必須如實保存：若只確認 source path／ref、未確認 commit，就保留 `unknown`；若 runtime timestamp unavailable，就標 unavailable。單一 provenance 欄位已知，不代表其他欄位也已驗證。

Local verification marker 只是 reuse optimization evidence；不得拿 marker 的時間或內容替代每一次真正 Runtime Draw 產生的 result／timestamp。

## 10. 使用者可見的標準 Runtime Draw

預設保持簡潔，不把內部 audit metadata 全部印出來。

推薦格式：

```text
### Runtime Draw｜YYYY/MM/DD HH:MM

1. 牌位：**牌面**
2. 牌位：**牌面**
...

Canonical Randomizer v1，使用完整 78 張牌與獨立正逆位隨機。
```

其中：

- 標題時間取自 `generated_at_taipei`，顯示到分鐘即可；
- 不預設顯示 UTC；
- 不預設顯示 GitHub commit time；
- 不預設顯示 commit SHA；
- 若使用者要求完整稽核／provenance，再展開內部欄位。

若是梅花，可在結尾改成對應說明，例如：

```text
Canonical Randomizer v1，採雙數 A/B 起卦契約。
```

若塔羅＋梅花同時使用，可同時簡述兩套 canonical contract。

## 11. DRAW / CAST FACT 與解讀分離

Runtime tool 的原始結果先固定，再開始解讀。

順序：

```text
Question Contract fixed
→ Runtime execution
→ Raw result captured
→ DRAW / CAST FACT fixed
→ Interpretation
```

不得邊解牌邊要求程式重抽，也不得看到不喜歡的結果後重新執行同一題。

若使用者要求保存紀錄，應優先保留實際 tool output 或等價結構化資料，而不是只保存最後的自然語言解讀。

## 12. Fail-Closed Fallback

如果 Runtime Draw 在本次環境不可用、canonical script 無法取得、程式執行失敗或結果無法可信解析：

- 不得假裝已執行；
- 不得由語言模型自行產生牌名來冒充抽牌；
- 不得偷偷改用另一套未宣告 RNG；
- 應改用 Web `tarot-plum-randomizer`，或請使用者自行抽牌後提供結果。

若 runtime 部分成功，例如 Tarot 成功、梅花失敗，應分開標示，不能把整組宣稱為完整 Runtime Draw。

## 13. Runtime Draw 不改變補占紀律

能快速執行 Python，不代表可以快速重抽。

所有：

- 同題／新題判斷；
- 承接前占；
- 條件世界；
- 補占／重占；
- 多人物 question identity；

仍必須服從 `READING_LIFECYCLE.md`。

**Execution availability does not create divination authority。** 有能力執行，只代表技術上可以抽，不代表方法論上已允許重抽。

## 14. Runtime Draw 與 Copy-ready 的關係

若使用者要求「你幫我出題，我自己抽」，依 `CHATGPT_OUTPUT.md` 提供 copy-ready 題目，不自動執行 Runtime Draw。

若使用者要求「你直接幫我抽」，才進入本章 Runtime Gate。

若使用者同時要求：

> 幫我設計題目並直接抽牌

應先完成題目／牌位契約，再執行；不能先抽牌再倒推題目。

## 15. 最低驗證

Canonical runtime tool 更新後，建議至少驗證：

- 78 張牌唯一；
- 單題無重複牌；
- count boundary 正確；
- 多題各自形成獨立 draw；
- 梅花 A/B 與動爻範圍正確；
- 64 卦 mapping 完整；
- JSON 可被正常解析；
- `generated_at_utc` 與 `generated_at_taipei` 代表同一瞬間；
- 台灣時間 offset 為 `+08:00`；
- metadata-only 變更不會誤升 `algorithm_version`；
- deterministic cache locator 能穩定解析到固定 `randomizer.py` + `verification.json`；
- reuse probe 能用 marker + SHA-256 + exact source commit + version + 最低 invariant 驗證現有 copy；
- moving ref 能先 resolve 成 exact commit，且 acquisition 不混用不同 revision；
- cache freshness trigger 先比較 exact commit；相同就不 redownload，不同才更新 cache；
- cache probe PASS 後不重新抓 GitHub／raw download／materialize／完整 smoke test；
- Playbook 自身更新不會被誤當成 Randomizer freshness trigger；
- cache probe PASS 後仍為每個新 question identity fresh execution／fresh shuffle；
- cache probe FAIL／absent／unavailable 時才回到 canonical source acquisition，而不是強行使用 stale／不明 copy；
- acquisition 成功後會把 canonical copy + exact source identity + marker 回填 deterministic cache slot。

測試屬於 Randomizer repo 的 implementation responsibility；本 Playbook 只要求 Runtime Draw 不應依賴未驗證、來源不明的臨時抽牌片段。
