# ChatGPT Runtime Draw｜程式抽牌／起卦治理

本章是 ChatGPT／AI 在具有實際可執行能力時，**自行執行塔羅抽牌或梅花起卦**的主要 authority。

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
- **維護或驗證 canonical Randomizer** → 第 3、7～9、15 節；實際 implementation tests 仍屬 Randomizer repo responsibility。
- **正式保存 Runtime Draw** → 第 8～11 節 + `READING_RECORD.md`。

若目前 task 已能由 exact section 唯一處理，直接讀該 section；router 用於降低載入成本，不是額外 ceremony。

## 1. 何時可以使用 Runtime Draw

只有同時符合以下條件時，ChatGPT 才可宣告「自行抽牌／起卦」：

1. 使用者明確要求 ChatGPT 自己抽，或上下文已授權由 ChatGPT 代為抽牌／起卦。
2. 本次 environment 具有可實際執行 Python 的能力，或本 session 已存在先前成功驗證且仍可執行的 `randomizer.py` copy。
3. 能取得並執行 `tarot-plum-randomizer` canonical Python implementation，或已有與該 implementation 明確同步且可驗證的 session copy。
4. 題目、牌位／起卦契約已在結果出現前固定。
5. 執行結果可以被保留為 `DRAW / CAST FACT`，而不是只留下模型重述。

若只是模型「隨機想一組牌」，不得標記為 Runtime Draw。

## 2. Runtime Capability Gate

ChatGPT 在第一次需要自行抽牌時，只做本次真正需要的最低充分 capability check：

1. 本聊天室／本 execution session 是否已有先前成功驗證、來源版本仍可辨識且 temporary runtime 仍存在的 `randomizer.py` copy；
2. 若沒有，Python 是否可執行；
3. canonical `randomizer.py` 是否可取得／載入；
4. 必要標準庫是否可用；
5. 程式能否完成一次 bounded smoke test。

某條已驗證 session path 成立時即可停止 capability discovery，不要為了形式重新讀 GitHub 或重跑完整 smoke test。

若 execution environment 不可觀察或不可執行，不得因模型「通常可以」就假設本次 capability 成立。

## 3. Canonical Runtime Source

Runtime Draw 的 canonical algorithm implementation 是：

```text
masini1491/tarot-plum-randomizer/randomizer.py
```

Playbook 只保存治理規則，不另外維護一份 Python 抽牌程式，避免 Web、Python、Playbook 多份演算法 drift。

### 3.1 Source Acquisition Layering｜取得 canonical script 的優先序

`repository retrieval capability` 與 `Python runtime network capability` 是不同層級；Python sandbox 無法直接連 GitHub，不代表 ChatGPT 無法透過 repository-native connector 取得 canonical source。

當本次需要載入 `randomizer.py` 時，依最低充分順序：

1. 若目前環境有 **connected GitHub tool／connector**，優先取得指定 `main`／ref 的 canonical `randomizer.py` 與可得 source commit evidence。
2. 取得 source 後，可寫入 temporary／ephemeral runtime workspace，再由 Python 執行；temporary copy 只是 execution input，不會變成新的 canonical implementation。
3. 若 GitHub connector 不可用，再評估 GitHub public/raw/Web access。
4. 若已有本地／session copy，只有來源與 canonical version 能被可靠確認時才可使用；未確認 freshness 的 cached copy 不得覆蓋較新的 canonical GitHub evidence。
5. Connector 能讀 repository ≠ Python runtime 能連網 ≠ repository write authority。這三種 capability 不得互相推導。
6. 若只拿到不完整、截斷或無法確認 canonical target 的 source，視為 acquisition gap，不得執行並宣稱 canonical Runtime Draw。

推薦概念流程：

```text
GitHub connector / repository-native read
→ canonical randomizer.py + source evidence
→ temporary runtime copy
→ Python smoke test
→ Runtime Draw
```

### 3.2 Fast Execution Path｜Verified Session Runtime Reuse

為降低每次占問重新讀 GitHub、materialize 與 smoke-test 的 latency，正常 execution path 採：

```text
Verified session runtime copy
  ↓ unavailable / stale / missing
GitHub connector → canonical randomizer.py → temporary Python runtime
  ↓ unavailable
GitHub public/raw/Web → canonical randomizer.py → temporary Python runtime
  ↓ unavailable
Web Randomizer / user self-draw
```

規則：

- 同一 ChatGPT execution session 中，若 `randomizer.py` 已完成來源確認與 bounded smoke test，且 temporary runtime copy 仍存在，可直接重用；**不要求每一題重新下載、重新 materialize 或重跑 smoke test**。
- Session reuse 只能省 setup，不得省略每個新 question identity 自己的 fresh random draw／cast；不能快取牌面或重用上一題 RNG result。
- 若已知 canonical Randomizer 更新、session copy identity 不明、runtime 被重建／清空、版本不符或上一輪 execution 出現 integrity failure，session verification 失效，重新進入 capability/source acquisition gate。
- Session reuse 是 execution concern，不會產生補占／重抽 permission；方法論 permission 仍由 `READING_LIFECYCLE.md` 決定。

### 3.3 Verified Session Runtime State｜同聊天室重用契約

第一次透過 GitHub／public source 取得並成功驗證 `randomizer.py` 後，Agent 可以在**目前仍可持續的同一 execution session**保留 ephemeral verification state。

最低充分狀態可以概念上保存：

```text
runtime_session_verified: true
runtime_source_path: masini1491/tarot-plum-randomizer/randomizer.py
runtime_source_commit: <known SHA or unknown>
runtime_algorithm_version: <verified version>
runtime_schema_version: <verified version>
runtime_copy_present: true
runtime_smoke_test: passed
```

這些是 ephemeral execution state，不是 Reading Record 的新 evidence layer，也不要求預設顯示給使用者。

重用規則：

1. `runtime_session_verified = true`、copy 仍存在且上一輪 execution 無 integrity error 時，下一題直接執行新的 draw／cast；不要為形式重新讀 GitHub。
2. 不要求每次抽牌前去 GitHub 重新確認 `main` 是否有新 commit；否則 session reuse 失去降低 latency 的意義。
3. 只有在使用者明確要求最新版／完整 audit、已知 Randomizer source 更新、session/runtime reset、copy 遺失、source identity 不可辨識、版本／payload contract 不符，或 execution integrity failure 時重新驗證。
4. 新一題仍必須產生全新的 RNG execution 與新的 Draw/Cast Fact；**reuse code, never reuse result**。
5. Chat session 還在不代表 Python runtime 一定還在。若 runtime state 不可觀察，先做最低成本 existence／import／execution check。
6. Session state 不跨 fresh chat 自動延續，也不因模型 memory 記得某個 SHA 就視為 runtime copy 仍存在。

若 ChatGPT 取得的是 repo 某個 commit 的檔案，應在內部 provenance 中保留該 commit SHA。GitHub commit time 只代表程式版本提交時間，不是抽牌時間。

若未能確認來源版本，可記 `runtime_source_commit: unknown`，但不得捏造 SHA。

## 4. Tarot Runtime Contract

Runtime Tarot 必須維持 Randomizer canonical contract：

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

若同 session 已有已驗證 copy，直接重用，不重新做 GitHub acquisition ceremony。

單題塔羅：

```text
python randomizer.py tarot --count 6 --format json --source-commit <SHA>
```

梅花：

```text
python randomizer.py plum --format json --source-commit <SHA>
```

塔羅＋梅花：

```text
python randomizer.py both --count 6 --format json --source-commit <SHA>
```

多題：

```text
python randomizer.py batch --counts 5,5,6,3 --format json --source-commit <SHA>
```

AI integration 優先使用 JSON，避免把人類排版重新解析成機械欄位。

## 7. Version Semantics｜版本語意

`algorithm_version` 只代表抽牌／起卦演算法契約。只有牌組、RNG／rejection sampling／shuffle、正逆位、梅花 A/B 公式等真正改變結果分布或契約的內容改變時才升版。

純 timestamp、commit provenance、JSON metadata 不升 `algorithm_version`；這類變化使用獨立 `schema_version`。

目前 canonical Randomizer：

```text
algorithm_version: 1
schema_version: 2
```

## 8. Draw Timestamp｜抽牌時間

Runtime Draw 應保存實際程式執行當下 timestamp：

```text
generated_at_utc: <UTC ISO-8601>
generated_at_taipei: <Asia/Taipei ISO-8601, UTC+08:00>
timezone: Asia/Taipei
```

GitHub commit timestamp 只能當版本 provenance，不能替代 draw timestamp。若 Runtime 無法可信取得時間，標示 unavailable，不要自行補值。

## 9. Internal Provenance｜內部來源紀錄

Runtime Draw 至少在工具輸出或正式紀錄中保存：

```text
cards_source: chatgpt-runtime
runtime_tool: tarot-plum-randomizer-python
runtime_algorithm_version: <algorithm_version>
runtime_schema_version: <schema_version>
runtime_source_commit: <known commit SHA or unknown>
generated_at_utc: <tool output>
generated_at_taipei: <tool output>
timezone: Asia/Taipei
```

梅花另保存：

```text
casting_source: chatgpt-runtime
raw_input: A, B
```

Provenance precision 必須如實保存；未知就保持 `unknown`／`unavailable`。

## 10. 使用者可見的標準 Runtime Draw

預設保持簡潔，不把內部 audit metadata 全部印出來。

```text
### Runtime Draw｜YYYY/MM/DD HH:MM

1. 牌位：**牌面**
2. 牌位：**牌面**
...

Canonical Randomizer v1，使用完整 78 張牌與獨立正逆位隨機。
```

若使用者要求完整稽核／provenance，再展開內部欄位。

## 11. DRAW / CAST FACT 與解讀分離

順序固定：

```text
Question Contract fixed
→ Runtime execution
→ Raw result captured
→ DRAW / CAST FACT fixed
→ Interpretation
```

不得邊解牌邊重抽，也不得看到不喜歡的結果後重新執行同一題。

## 12. Fail-Closed Fallback

若 verified session copy 不可用，降級到 canonical Python acquisition/execution。

若所有 Runtime Draw path 都不可用、canonical source 無法取得、程式執行失敗或結果無法可信解析：

- 不得假裝已執行；
- 不得由語言模型自行產生牌名冒充抽牌；
- 不得偷偷改用另一套未宣告 RNG；
- 應改用 Web `tarot-plum-randomizer`，或請使用者自行抽牌後提供結果。

## 13. Runtime Draw 不改變補占紀律

更快的 session reuse 不代表可以更快重抽。所有同題／新題、承接、條件世界、補占／重占與多人 question identity 仍服從 `READING_LIFECYCLE.md`。

**Execution availability does not create divination authority。**

## 14. Runtime Draw 與 Copy-ready 的關係

若使用者要求「你幫我出題，我自己抽」，提供 copy-ready 題目，不自動執行 Runtime Draw。

若使用者要求「你直接幫我抽」，才進入本章 Runtime Gate。若同時要求設計題目並直接抽牌，先固定題目／牌位契約，再執行。

## 15. 最低驗證

Canonical runtime tool 更新後，建議至少驗證：

- 78 張牌唯一；
- 單題無重複牌；
- count boundary 正確；
- 多題各自形成獨立 draw；
- 梅花 A/B 與動爻範圍正確；
- 64 卦 mapping 完整；
- JSON 可正常解析；
- timestamp／timezone 正確；
- metadata-only 變更不誤升 `algorithm_version`；
- 同 session verified copy reuse 只省 setup，不會重用上一題 Draw/Cast Fact；
- verified session state 失效條件成立時會重新 acquire／verify，而不是盲目使用 stale copy。

測試屬於 Randomizer repo implementation responsibility；本 Playbook 只要求 Runtime Draw 不依賴未驗證、來源不明的臨時抽牌片段。