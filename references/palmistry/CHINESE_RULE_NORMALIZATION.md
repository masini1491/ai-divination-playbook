# Chinese Palmistry Rule Normalization Matrix｜中國傳統手相規則正規化草案

Status: **REFERENCE-ONLY / DRAFT｜僅供參考／草案**

Reviewed target baseline: `masini1491/ai-divination-playbook@8621f095cf68366cf67cc0e6b7e10b3e076fd0e4`

本檔把已審查的中國傳統手相來源拆成可比較的 rule families。它的目的不是決定哪一本「最准」，也不是把古籍直接變成 production rule，而是避免：

- 同名術語跨來源／跨部位誤合併；
- 近似文本被錯算成多份獨立佐證；
- 中國術語被硬映射成 Western palmistry labels；
- interpretation 反過來污染 image observation。

Primary provenance / comparison set：

1. 《古今圖書集成》藝術典第 640 卷所收《神相全編十》掌部（以下簡稱 `SXQ-640`）；
2. 《太清神鑑》（四庫全書本）卷五（以下簡稱 `TQ-V5`）；
3. 《神相鐵關刀》掌部（以下簡稱 `TGKD`）。

GitHub bounded-search mirror：`look-fate/lookfate-book@5cd1a3c3bd0337ec24f2963684fb96e67cb32301`。Mirror 只協助 retrieval / cross-check，不取代上游古籍 provenance。

## 1. Evidence-lineage guard

### `SXQ-640` × `TQ-V5`

兩者在已審查的「掌上三紋、紋深細／粗淺、縱橫理、貫指、手背紋」段落存在高度近似甚至接近逐句重合的文本。

因此在本 Playbook 的 evidence independence 上：

```text
SXQ-640 + TQ-V5
= two textual witnesses / surfaces
≠ automatically two independent rule origins
```

除非後續完成版本學／文本譜系研究，這一組先標成 `shared-or-dependent rule family`，不能因「兩本都寫到」就提高 prediction confidence。

### `TGKD`

本輪審查到的掌部組織方式明顯不同：更強調八卦掌宮、身／面／掌配合、掌色，以及掌紋在特定宮位的變化。

只能說它在**目前 reviewed passages 中屬 distinct presentation / rule organization**；不得進一步宣稱其歷史文本來源完全獨立。

## 2. Rule-family matrix

| Rule family | `SXQ-640` | `TQ-V5` | `TGKD` | Normalization decision |
|---|---|---|---|---|
| Hand / palm morphology | 有獨立「論手」：手掌長短、厚薄、軟硬、指形、掌心／四畔等 | 有高度相近的「論手」內容 | 有掌與身／面／五行形配合，亦看厚薄、筋節、掌背等 | 只抽取**可見形態 observation**；吉凶／性格留在 source interpretation |
| General line quality | 細深、粗淺、紋理清濁、是否破損 | 與 `SXQ-640` 高度近似 | 強調「深秀」、紋多寡、紋破與宮位狀態 | Raw fact 存 apparent width / contrast / continuity；不得直接存「吉／賤」 |
| Three principal traditional lines | 明確有上／中／下三紋，分別稱天／人／地的象徵角色 | 同一 rule family，文字高度近似 | 本輪 reviewed palm section 未建立同一套三紋 contract | 可建立 source-local labels；**不得預設等同 heart/head/life** |
| Break / continuity | 三紋清楚、無破為一類；好紋若破亦影響判斷 | 高度近似 | 多處使用「紋不破／紋亂／沖」等條件 | Observation 層只記 `continuous / broken / fragmented / uncertain` |
| Direction / density | 縱、橫、直貫指、散出指縫等 | 高度近似 | 直紋／橫紋、沖指、溢掌旁等 | 以幾何方向、密度、endpoint / boundary crossing 表示，不帶傳統結論 |
| Bagua / palm palaces | 《玉掌記》要求先看八卦；另有離卦紋、震卦紋等 source terms | 本輪 palm excerpt 尚不足以建立完整八卦 contract | 明確把巽、離、坤列為重要掌宮，並給 source-specific responsibility；掌心稱明堂 | 八卦／掌宮屬 **tradition projection layer**，不是 raw visual fact |
| Named patterns | 有大量 named patterns，如玉柱、三才、智慧、井、印等；部分高度依賴圖示 | 有部分 named pattern vocabulary | 有字／印／令、井等 pattern，以及宮位組合 | 每個 pattern 必須帶 `source_id + section + anatomical_scope + geometry_basis`；名稱本身不足以 match |
| Palm-back / dorsal features | 有獨立「論手背紋」 | 有高度相近的手背段落 | 會看掌背厚薄、露筋，也提紋溢掌背 | `palm` 與 `dorsal_hand` 必須是不同 anatomical scope |
| Color / surface state | 有掌色與四季／色澤等傳統判讀 | 有掌色描述 | 特別重視掌色，且另有「相掌秘訣」以色澤判讀時運 | 相片色彩高度受 lighting / white balance 影響；未通過 color-quality gate 時不得進 interpretation |
| Finger / nail features | 指形、指節、爪甲另有判讀 | 同類 feature 存在 | 指長短、節、甲、配掌均重要 | 可觀察幾何與 surface state 分開；不要把 finger rule 混成 palm-line rule |
| Special illustrated marks | 《玉掌圖》《相掌善惡》等多處需要圖形才能辨認 | 文字可見若干 pattern，但仍有 shape ambiguity | 部分 pattern 可由文字描述，部分仍依 source convention | 缺圖、圖形未識別或 definition ambiguous → `unresolved`，不得靠名稱腦補 |

## 3. Terminology namespace

任何傳統術語在 draft schema 中都不得以裸字串取得全域 identity。

最低 identity：

```text
tradition
source_id
source_revision_or_edition
section
anatomical_scope
term
```

概念例：

```text
tradition: chinese-xiangshu
source_id: SXQ-640
section: 論掌紋
anatomical_scope: palm-line
term: 三紋
```

而不是：

```text
term: life_line
```

### Same-term collision guard

同一文字可能在不同相書、不同 anatomical scope 代表不同東西。例如 research 中可見 `玉柱` 在其他相術文本也被用於面部／骨相名稱；因此 `玉柱紋` 不能因字面相同就與 `玉柱骨` 合併。

核心規則：

```text
same text label ≠ same semantic identity
```

## 4. Cross-tradition mapping state

中西術語 mapping 先使用以下狀態，而不是 true / false：

- `UNREVIEWED`：尚未比較 source definition；
- `GEOMETRICALLY_SIMILAR`：位置／走向看似相近，但 interpretation lineage 不同；
- `SOURCE-SUPPORTED_EQUIVALENCE`：只有明確 source evidence 支持時才可使用；
- `CONFLICTING`：不同來源 definition 不相容；
- `PROHIBITED_ASSUMPTION`：已知不能只因名稱／大致位置就直接等同。

目前至少：

```text
天紋 ↔ heart line      = PROHIBITED_ASSUMPTION
人紋 ↔ head line       = PROHIBITED_ASSUMPTION
地紋 ↔ life line       = PROHIBITED_ASSUMPTION
玉柱紋 ↔ fate line     = PROHIBITED_ASSUMPTION
```

這不是宣稱兩者一定不同，而是說目前 evidence 不允許 production 一對一 mapping。

## 5. Observation vs interpretation normalization

來源句子常把「看到什麼」和「代表什麼」寫在同一句。進本 Playbook 前必須拆開：

```text
Source statement
→ observable predicate
→ source-local traditional interpretation
```

例如只能把：

```text
line continuity / break
line orientation
line crosses a boundary
line located inside a source-defined region
```

放進 Observation Fact。

下列只能留在 Interpretation：

```text
wealth / rank / marriage / lifespan / temperament / future event
```

即使古籍語氣是斷言，也不會因此升格成 image fact 或現代科學 evidence。

## 6. Image-dependent pattern guard

`SXQ-640` 有大量 named patterns，且部分條目原本配圖；Wikisource 本身亦存在部分圖字／圖形辨識不完整的情況。

因此對 named pattern：

1. 有可讀文字 definition + 足夠幾何描述 → 可建立 candidate mapping；
2. 只有名稱、沒有幾何 definition → 不建 mapping；
3. 主要靠插圖，而圖未取得／未辨認 → `not_observable_from_current_source`；
4. LLM 不得依名稱自行畫出 pattern，再反過來認定照片符合。

## 7. GitHub mirror edition caveat

`look-fate/lookfate-book@5cd1a3c...` 的 `content/相/神相全编/` 在 reviewed tree 中是四個卷檔；而本研究的 primary palm source 是《古今圖書集成》第 640 卷所收「神相全編十」掌部。

本輪 GitHub code search 沒有證明該四卷 mirror 可直接替代 `SXQ-640` 的掌部文本。

所以：

```text
look-fate 神相全编 directory
≠ assumed exact edition mirror of SXQ-640
```

對《太清神鑑》卷五與《神相鐵關刀》，GitHub mirror 可直接搜尋到本輪相關掌部內容；仍只作 retrieval / cross-check，不升格成版本 authority。

## 8. Output of this normalization pass

本輪已能確定未來 Palm Observation Fact 至少要支持：

- physical hand side / view；
- palm vs dorsal-hand anatomical scope；
- palm / finger proportions；
- line geometry；
- continuity / branches / intersections；
- source-neutral normalized coordinates；
- image-quality / observability state；
- tradition-specific region projection；
- source-local term mapping；
- mapping confidence 與 source provenance。

詳細 draft 見 [`OBSERVATION_SCHEMA_DRAFT.md`](OBSERVATION_SCHEMA_DRAFT.md)。

## 9. Adoption state

**REFERENCE-ONLY｜僅供參考**

本檔沒有修改 `PALMISTRY.md`、`METHOD_ROUTING.md`、`PLAYBOOK_INDEX.json` 或任何 production method contract。