# Zi Wei Dou Shu Evidence Architecture

Authority：`REFERENCE-ONLY / RESEARCH-ONLY`

## Layer model

```text
L0 Input / Provenance
L1 Calendar Facts
L2 Deterministic Zi Wei Chart Facts under explicit profile
L3 Tradition / School Projection
L4 Source-backed Interpretation Claims
L5 Bounded Synthesis
```

### L0 — Input / provenance

至少區分：

- 已正規化傳統輸入：農曆年月日、時辰、閏月 identity、必要性別／陰陽 identity；
- civil timestamp input：local timestamp、timezone／locality（只有 normalization 需要時）。

civil timestamp 不應直接餵入 Zi Wei core；先經 calendar/time normalization。

### L1 — Calendar facts

負責：

- solar ↔ lunar normalization
- leap-month identity
- ganzhi / year-stem identity
- hour branch
- day/year boundary policy
- optional true-solar/civil-time normalization

Calendar facts 與 Zi Wei placement rule 必須可分別追溯。

### L2 — Deterministic chart facts

L2 不是「流派無關真理」。其 identity 應至少是：

```text
normalized_input
+ calculation_profile
+ rule_family_profile
+ engine/revision
+ provenance
→ deterministic chart fact
```

Baseline Core Fact Set 在 matched profile 下目前可研究：

- Life Palace / Body Palace
- 12 palace geometry
- Five-Tiger palace stems
- Five-Element Bureau
- Zi Wei / Tian Fu anchors
- fourteen major stars
- 左輔／右弼／文昌／文曲
- opposition / Sanfang-Sizheng topology
- decadal direction
- first decadal start age

### L3 — tradition / school projection

下列不得混入無 profile 的 L2 universal fact：

- Four Transformations
- brightness
- leap-month convention
- late-Rat convention
- subsystem year boundaries
- Heaven / Earth / Human chart mode
- many auxiliary/minor stars
- dynamic month/day/hour charts

### L4 — interpretation claims

Implementation README、code comment 或 LLM memory 不足以成為 interpretation authority。

未來 claim 應能追溯：

```text
source identity
→ claim identity
→ applicable tradition/profile
→ context conditions
→ allowed synthesis scope
```

### L5 — bounded synthesis

L5 可以組合 L2/L3/L4，但不得：

- 把 research candidate 說成 production fact；
- 把 source variant 說成唯一正統；
- 把 Tarot design decision 說成 historical evidence；
- 宣稱科學／客觀預測有效性。

## Profile architecture

至少概念上：

```text
calculation_profile
├─ chart_mode
├─ placement_algorithm
├─ five_element_bureau_profile
├─ sihua_profile
├─ brightness_profile
├─ leap_month_policy
├─ rat_hour_policy
├─ boundary_profile
│  ├─ palace_stem_year
│  ├─ sihua_year
│  ├─ body_master_year
│  └─ flow_year
└─ horoscope_boundary_policy
```

一個 named school 可以是 preset，但不能隱藏 components。

## Default candidate semantics

`ziwei.baseline.tw_v1` 是 research default candidate，不是 universal truth。

目前 selection objective：

> 一般使用者沒有指定流派、把本 Repo 載入 ChatGPT 使用時，優先讓結果具備可理解、可追溯、且主觀上較容易感到貼合的 baseline，同時保留 alternative profile。

其中：

`sihua.default_v1 = 戊右 / 庚府 / 壬左`

其選擇 evidence 分成兩類：

1. **external research**：證明四化確實存在版本差異，且「庚府」有實際 tradition / implementation lineage；不證明本組合客觀最準；
2. **Tarot design-review evidence**：在「一般 ChatGPT 使用者主觀覺得準」的比較題中，該候選相對受到支持。

因此此欄位必須保持：

```text
selection_basis = user_perceived_fit_research
scientific_validity = unestablished
historical_uniqueness = false
production_admitted = false
```

## Validation model

禁止 engine majority voting。

區分：

1. same implementation / different runtime → portability；
2. port / derived implementation / same rule lineage → implementation parity；
3. independent implementation under matched profile → cross-implementation evidence；
4. primary-source reconciliation → rule-specific source support。

理想 validation：

```text
primary-source rule evidence
+ explicit calculation profile
+ independent-engine agreement under same profile
+ edge-case fixtures
+ lineage-aware disagreement record
```

## Required boundary fixtures

至少涵蓋：

```text
ordinary month
leap day 1 / 15 / 16 / final day
× early Rat / ordinary hour / late Rat

Lunar New Year vs Beginning of Spring
Tian / Di / Ren chart mode
default / Zhongzhou placement profile
Four-Transformation variants
civil time vs true solar time when applicable
```

遇到 boundary-sensitive input，future implementation 應可標記 ambiguity，而不是靜默假裝無分歧。

## Admission boundary

Research scaffold 要進 production 時，必須另外建立 deterministic provider/runtime、fact schema、provenance gate、behavioral regression 與 explicit admission。本文不得被 production router直接引用成 method authority。
