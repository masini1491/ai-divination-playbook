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
2. 本次 environment 具有可實際執行 Python 的能力，或本 execution session 已存在**可由 runtime 直接觀察、驗證且仍可執行**的 `randomizer.py` copy。
3. 能取得並執行 `tarot-plum-randomizer` canonical Python implementation，或已有與該 implementation 明確同步且具有 observable verification artifact 的 session copy。
4. 題目、牌位／起卦契約已在結果出現前固定。
5. 執行結果可以被保留為 `DRAW / CAST FACT`，而不是只留下模型重述。

只在聊天 context 中「記得之前載入過」不算 Runtime capability evidence；若只是模型「隨機想一組牌」，也不得標記為 Runtime Draw。

## 2. Runtime Capability Gate

ChatGPT 在需要自行抽牌時，只做本次真正需要的最低充分 capability check，順序固定為：

1. **先做 cheap runtime reuse probe**：目前 execution runtime 中是否實際存在已 bootstrap 的 `randomizer.py` 與對應 verification marker，且 marker 可解析、copy integrity／import 可成立；
2. 若 probe 成立，直接重用該 copy，STOP source discovery；
3. 若 probe 不成立，確認 Python 是否可執行；
4. 取得 canonical `randomizer.py`；
5. 把 source **實際寫入／materialize 到 runtime workspace**；
6. 完成 bounded smoke test，並在同一 runtime workspace 建立 observable verification marker；
7. 然後執行本次真正 draw／cast。

重要邊界：

- **讀 Playbook ≠ Runtime Bootstrap。**
- **GitHub connector 讀到 `randomizer.py` ≠ Runtime Bootstrap。**
- 只有 source 已實際進入可執行 runtime、完成 smoke test 並留下可觀察 verification artifact，才可視為 verified session runtime。
- 重新讀 `CHAT_INIT.md`、`RUNTIME_DRAW.md` 或其他最新版 Playbook 文件，本身**不會讓既有 verified runtime copy 失效，也不應觸發重新抓 `randomizer.py`**；先做 cheap reuse probe。

某條 verified runtime path 成立時即可停止 capability discovery，不要為了形式重新讀 GitHub 或重跑完整 smoke test。

若 execution environment 不可觀察或不可執行，不得因模型「通常可以」或 conversation memory 記得舊狀態就假設本次 capability 成立。

## 3. Canonical Runtime Source

Runtime Draw 的 canonical algorithm implementation 是：

```text
masini1491/tarot-plum-randomizer/randomizer.py
```

Playbook 只保存治理規則，不另外維護一份 Python 抽牌程式，避免 Web、Python、Playbook 多份演算法 drift。

### 3.1 Source Acquisition Layering｜取得 canonical script 的優先序

`repository retrieval capability` 與 `Python runtime network capability` 是不同層級；Python sandbox 無法直接連 GitHub，不代表 ChatGPT 無法透過 repository-native connector 取得 canonical source。

只有在 §2 的 cheap runtime reuse probe **未成立**、確實需要重新取得 `randomizer.py` 時，依最低充分順序：

1. 若目前環境有 **connected GitHub tool／connector**，優先取得指定 `main`／ref 的 canonical `randomizer.py` 與可得 source commit evidence。
2. 取得 source 後，必須實際寫入／materialize 到 temporary／ephemeral runtime workspace，再由 Python 執行；只把 source 顯示在模型 context 裡不算 runtime copy。
3. 若 GitHub connector 不可用，再評估 GitHub public/raw/Web access。
4. 若只拿到不完整、截斷或無法確認 canonical target 的 source，視為 acquisition gap，不得執行並宣稱 canonical Runtime Draw。
5. Connector 能讀 repository ≠ Python runtime 能連網 ≠ repository write authority。這三種 capability 不得互相推導。

推薦首次 bootstrap：

```text
GitHub connector / repository-native read
→ canonical randomizer.py + source evidence
→ write/materialize source into runtime workspace
→ bounded Python smoke test
→ create observable verification marker
→ VERIFIED
→ Runtime Draw
```

### 3.2 Fast Execution Path｜Verified Session Runtime Reuse

為降低每次占問重新讀 GitHub、materialize 與 smoke-test 的 latency，正常 execution path 採：

```text
Cheap runtime reuse probe
  ↓ VERIFIED artifacts present + valid
Existing runtime randomizer.py → fresh execution

  ↓ probe failed / artifacts missing / invalid
GitHub connector → canonical randomizer.py → Runtime Bootstrap
  ↓ unavailable
GitHub public/raw/Web → canonical randomizer.py → Runtime Bootstrap
  ↓ unavailable
Web Randomizer / user self-draw
```

規則：

- 同一個仍持續存在的 execution runtime 中，若 verified artifacts 實際可觀察且 probe 通過，可直接重用 `randomizer.py`；**不要求每一題重新下載、重新 materialize 或重跑完整 smoke test**。
- Conversation 還在、模型還記得舊 SHA、或重新讀過 Playbook，均不足以單獨證明 runtime copy 還在。
- Session reuse 只能省 setup，不得省略每個新 question identity 自己的 fresh random draw／cast；不能快取牌面或重用上一題 RNG result。
- 若已知 canonical Randomizer 更新、verification marker／copy 遺失、copy integrity 不符、import／execution failure、runtime 被重建／清空或版本 contract 不符，verification 失效，重新進入 bootstrap。
- Session reuse 是 execution concern，不會產生補占／重抽 permission；方法論 permission 仍由 `READING_LIFECYCLE.md` 決定。

### 3.3 Runtime Bootstrap & Observable Verification｜可觀察重用契約

第一次需要透過 Python Runtime Draw、且 cheap reuse probe 未成立時，Agent 應建立真正可被後續 turn 檢查的 Runtime Bootstrap artifacts。

推薦在同一 ephemeral runtime workspace 內保存：

```text
<runtime-workspace>/tarot-randomizer/randomizer.py
<runtime-workspace>/tarot-randomizer/runtime_verified.json
```

實際 path 可依 environment 調整；重點是兩者必須位於**後續 Python execution 可再次觀察的同一 runtime workspace**。

`runtime_verified.json` 最低充分內容建議為：

```json
{
  "runtime_session_verified": true,
  "runtime_source_path": "masini1491/tarot-plum-randomizer/randomizer.py",
  "runtime_source_commit": "<known SHA or unknown>",
  "runtime_algorithm_version": "<verified version>",
  "runtime_schema_version": "<verified version>",
  "runtime_copy_sha256": "<sha256 of materialized randomizer.py>",
  "runtime_smoke_test": "passed"
}
```

這是 ephemeral execution state，不是 Reading Record 的新 evidence layer，也不要求預設顯示給使用者。

#### Bootstrap 成立條件

以下都成立才可寫入 `runtime_session_verified: true`：

1. canonical source 已取得；
2. source 已實際寫入／materialize 成 runtime file；
3. 可由 Python import／execute；
4. bounded smoke test 已通過；
5. marker 已由 runtime 寫出，並保存 materialized copy 的 SHA-256 或等價 integrity evidence。

只有模型在對話中宣告「已驗證」而沒有 runtime artifacts，不算成立。

#### Cheap reuse probe

後續新題在碰 GitHub 前，先以現有 runtime 做最低成本 probe：

```text
randomizer.py exists?
+ runtime_verified.json exists and parses?
+ marker says verified=true?
+ current randomizer.py SHA-256 matches marker?
+ import / minimal execution path works?
↓ yes
REUSE
```

實際新的 draw／cast execution 本身可兼作最後的 execution viability check，不需要每次另跑完整 invariant suite。

#### Reuse / invalidation 規則

1. probe 通過後，下一題直接用既有 copy 執行新的 draw／cast；**reuse code, never reuse result**。
2. 不要求每次抽牌前去 GitHub 重新確認 `main` 是否有新 commit；否則 session reuse 失去降低 latency 的意義。
3. **重新讀最新版 Playbook 本身不構成 Randomizer invalidation。** 除非新讀到的 canonical rule 明確表示 Randomizer contract／source 已變更，否則仍先 probe existing runtime artifacts。
4. 只有在使用者明確要求 Randomizer 最新版／完整 audit、已知 Randomizer source 更新、runtime reset、artifact 遺失、digest mismatch、source identity 不可辨識、版本／payload contract 不符或 execution integrity failure 時重新 bootstrap。
5. Chat conversation 還在不代表 Python runtime 一定還在；artifact probe 失敗就視為 runtime reuse 不成立。
6. Runtime state 不跨 fresh chat 自動延續，也不因模型 memory 記得某個 SHA 就視為 artifacts 仍存在。

簡化為：

```text
首次：source acquisition
→ materialize randomizer.py
→ smoke test
→ write verification marker
→ VERIFIED
→ fresh draw

後續：probe runtime artifacts
→ pass → fresh draw
→ fail → re-acquire + bootstrap
```

若 ChatGPT 取得的是 repo 某個 commit 的檔案，應在 marker／internal provenance 中保留該 commit SHA。GitHub commit time 只代表程式版本提交時間，不是抽牌時間。

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

先按 §2／§3.3 probe existing runtime artifacts。Probe 通過就直接重用既有 `randomizer.py`，不要先讀 GitHub。

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

Runtime verification marker 用來證明 session copy 可重用；它不是單次 Reading Record 的 draw provenance，也不得取代每一次真正 execution 產生的 timestamp／result。

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

若 cheap reuse probe 不通過，降級到 canonical Python acquisition + Runtime Bootstrap。

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

Canonical runtime tool 或 Runtime Bootstrap contract 更新後，建議至少驗證：

- 78 張牌唯一；
- 單題無重複牌；
- count boundary 正確；
- 多題各自形成獨立 draw；
- 梅花 A/B 與動爻範圍正確；
- 64 卦 mapping 完整；
- JSON 可正常解析；
- timestamp／timezone 正確；
- metadata-only 變更不誤升 `algorithm_version`；
- 只讀 Playbook／只 fetch source 不會被誤判成 Runtime Bootstrap；
- bootstrap 後 runtime workspace 同時存在 `randomizer.py` 與 verification marker；
- marker digest 與 materialized copy 一致；
- 同 runtime 的下一題會先做 cheap reuse probe，再直接執行 fresh RNG，不先重抓 GitHub；
- 重新讀最新版 Playbook 本身不會無故 invalidated verified runtime artifacts；
- runtime artifacts 消失／digest mismatch／import failure 時會重新 acquire／bootstrap；
- session reuse 只省 setup，不會重用上一題 Draw/Cast Fact。

測試屬於 Randomizer repo implementation responsibility；本 Playbook 只要求 Runtime Draw 不依賴未驗證、來源不明的臨時抽牌片段。