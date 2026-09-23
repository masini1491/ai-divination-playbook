# Zi Wei Dou Shu Calculation Engine Research

Authority：`REFERENCE-ONLY / RESEARCH SYNTHESIS`

本檔記錄目前已完成的 matched-profile calculation reconciliation；不是 implementation dependency manifest。

## Capability decomposition

```text
D0  Research routing
D1  Input provenance
D2  Calendar normalization
D3  Time boundary
D4  Core palace geometry
D5  Five-Element Bureau
D6  Major-star placement
D7  Auxiliary stars
D8  Four Transformations
D9  Brightness
D10 Structural topology
D11 Dynamic charts
D12 Tradition / profile
D13 Interpretation claims
D14 Validation / admission
```

第一階段以 D0–D6、D10、D12、D14 為主。D13 的 architecture / source-policy / runtime-facing contracts v0 已完成 research admission；完整 claim corpus 仍未 admission。D7/D9/D11 保持後續研究。

## Normalized architecture

```text
Birth Input
→ Calendar Normalization Boundary
→ Normalized Zi Wei Input
→ Zi Wei Calculation Profile
→ Deterministic Chart Facts
```

若使用者已直接提供合法農曆日期／時辰／閏月 identity，不應為形式強制要求經緯度；只有 civil-time normalization 或 true-solar policy 需要時才要求額外 location/timezone provenance。

## Matched-profile reconciliation v1

### Life / Body Palace

在 `chart_mode=tian_pan`、matched lunar month/hour branch 下，matharts、iztro、Fortel、ziwei-lite、Binger 的基本命身宮規則一致：

```text
寅起正月，順數至生月
命宮逆數生時
身宮順數生時
```

Fortel / ziwei-lite 的 Di/Ren chart modes 可改 Life Palace，因此分類：

`SAME_RULE under matched chart_mode=tian_pan`，其他 mode = `PROFILE_VARIANT`。

### Five-Element Bureau

matharts、iztro、Fortel、ziwei-lite 可對到同一 5×6 bureau mapping。Binger 透過命宮干支納音 element 轉 bureau number，合理預期等價，但其 external NaYin dependency 尚未完成 exhaustive closure。

分類：

- first four：`SAME_RULE`
- Binger：`DEPENDENCY RECONCILIATION PENDING`

### Zi Wei start

matharts / iztro / ziwei-lite 使用等價 quotient/remainder parity formula；Fortel / Binger 以 table 表達。Binger 的 5×30 / 150 entries 已在研究過程與 formula 做 deterministic comparison，結果一致。

分類：`SAME_RULE`。Historical/source reconciliation 已找到傳統生日配置表／歌訣支持 placement outcome；現代 quotient/remainder closed-form 應標成等價 algorithmic reconstruction，不冒充古籍原文公式。

### Fourteen major stars

Tier-A implementations 的 relative placements 高度一致；matharts 的 primary-scan dossier另提供日本國立公文書館 `新鋟希夷陳先生紫微斗数全書１` 的 placement glyph evidence。

分類：`SAME_RULE`，目前是最強的 source-backed deterministic candidate之一。

### 左輔／右弼／文昌／文曲

common placement rule 在多個 engines 一致，matharts primary-scan research 亦提供 rule-specific evidence。

### Four Transformations

不能視為 universal Core Fact，也不能再用單一「《全書》表」代表所有 historical witnesses。

目前至少要分：

```text
QUANSHU-NANYANG
  戊 貪陰弼機
  庚 日武同相
  壬 梁紫府武
  evidence = witness-identified transcription / rule-specific source research

QUANSHU-WENGUANG-EARLY
  庚 日武同陰
  evidence = editorial collation claim
  facsimile = open

QUANJI-COMMON
  戊 貪陰弼機
  庚 日武陰同
  壬 梁紫左武
  evidence = witness-identified transcription support
  facsimile = open

ZHONGZHOU-MODERN
  戊 貪陰陽機
  庚 日武府同
  壬 梁紫府武

PROJECT-DEFAULT-V1
  戊 貪陰弼機
  庚 日武府同
  壬 梁紫左武
  selection_basis = user_perceived_fit_research
```

詳細身份與 evidence level 由 `FOUR_TRANSFORMATION_VARIANT_REGISTRY.md` 擁有。

`PROJECT-DEFAULT-V1` 使用中性 identity `sihua.default_v1`；它不是已證實的古籍單一 lineage。選它作 `ziwei.baseline.tw_v1` 的理由是 user-perceived-fit Tarot design review，不是 engine majority、古籍唯一性或科學效度證明。

### Leap month

Historical witness research 已確認 Nanyang-Hall witness 的 rule 接近「閏月視作次月」；這與目前 project default `split_after_day_15` 不同，因此閏月必須保留 profile identity。

已知至少存在：

- same month
- next month
- split after day 15
- 其他 solar-term / tradition variants

iztro 的 leap fix 與 late-Rat index 存在 coupling；Fortel 較直接；ziwei-lite 將 leap 與 Rat-hour policy 分開建模。

分類：`CALENDAR_BOUNDARY_VARIANT`。

### Rat hour

現代實作同時存在 23:00 next-day 與 current-day-until-midnight 等策略。ziwei-lite 顯式 profile；iztro 可配置；matharts core 將此責任放在外部 normalization。

分類：`CALENDAR_BOUNDARY_VARIANT`。

### Year boundary

一個 global `year_boundary` 不足。

iztro 已分 `yearDivide` / `horoscopeDivide`；ziwei-lite 再細分 palace-stem、sihua、body-master、flow-limit boundaries。

分類：`PROFILE_VARIANT`；future schema 應 per-subsystem。

### Decadal

Implementation convergence 與 historical witness agreement 必須分開。

多個現代 engines 常見：

```text
first palace = Life Palace
first start age = bureau number
陽男陰女順
陰男陽女逆
```

但 source reconciliation 已顯示：Nanyang-Hall《全書》witness 的大限文字直接支持順逆方向，且描述第一限宮位從命宮相鄰宮（父母／兄弟）起；Quanji lineage 的流傳轉錄則支持「命宮先起局數歲、每十年一宮」。因此：

- `decadal direction`：source-backed，但仍需記錄 witness/profile；
- `first palace`：`DOCUMENTED PROFILE / WITNESS VARIANT`；
- `first start age = bureau number`：`STRONG QUANJI WITNESS-IDENTIFIED TRANSCRIPTION SUPPORT`，原頁 image 尚 open。

Project default 改用明確 profile identity：

`decadal.quanji_common_v1 = Life Palace start + bureau-number start age + standard direction`。

## Research default candidate v1

```text
ziwei.baseline.tw_v1
├─ chart_mode.tian_pan
├─ calendar.traditional_lunar
├─ year_boundary.lunar_new_year
├─ life_body.standard
├─ bureau.standard
├─ major_stars.standard_14
├─ decadal.quanji_common_v1
├─ sihua.default_v1 = 戊右 / 庚府 / 壬左
├─ leap.split_after_15
├─ rat_hour.next_day_23
├─ clock.civil
└─ true_solar.disabled
```

這是一個 **componentized research preset**。任何 component 的未來 evidence 更新，都可個別 revision，不應把整套 preset當成單一不可拆 doctrine。

## Source Reconciliation v1 status

```text
Life / Body                          SUBSTANTIALLY CLOSED
Five-Element Bureau                 SUBSTANTIALLY CLOSED (conceptual source chain)
Zi Wei birthday placement outcome   SOURCE-BACKED
modern closed-form formula          ALGORITHMIC RECONSTRUCTION
Fourteen major / selected assistants STRONG SOURCE SUPPORT
Decadal direction                   SOURCE-BACKED
Decadal first palace                DOCUMENTED VARIANT
Decadal bureau-number start age     STRONG QUANJI TRANSCRIPTION SUPPORT / IMAGE OPEN
Four Transformations                VERSIONED WITNESS / TRADITION VARIANT REGISTRY
Leap month                          DOCUMENTED PROFILE VARIANT
Quanji rule-page facsimile          IMAGE GAP OPEN
Wenguang rule-page facsimile        IMAGE GAP OPEN
```

因此 Source Reconciliation v1 可標記 `CLOSED WITH EXPLICIT IMAGE GAPS`。未來只有取得 material 新 facsimile／witness evidence 時才 reopen 對應 item；不以一般網頁數量重跑同一研究。

## Interpretation architecture handoff

Interpretation research v0 已完成：

```text
14-star / 12-palace claim prototypes     architecture evidence only
contextual composition                   selected research architecture
flat dictionary                          rejected as primary model
source conflict preservation             selected
ziwei.interpretation.tw_v1               research candidate
fact/retrieval/synthesis contracts v0     research-admitted
synthetic fixture validation v0           pass
```

Canonical owners：

- `INTERPRETATION_ARCHITECTURE_V0.md`
- `INTERPRETATION_RUNTIME_CONTRACTS_V0.md`
- `INTERPRETATION_FIXTURE_VALIDATION_V0.md`
- `INTERPRETATION_ADMISSION_REVIEW_V0.md`

## Remaining research gaps

1. brightness、minor stars、dynamic charts；
2. machine-readable full claim registry and source-normalized claim admission；
3. 上述兩個明確 image gaps（只有取得可驗證 facsimile 時才重開）。

Interpretation Architecture v0 的完成不建立 production provider、production runtime、ordinary routing 或 canonical production profile。
