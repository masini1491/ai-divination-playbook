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

第一階段以 D0–D6、D10、D12、D14 為主；D7/D9/D11/D13 保持後續研究。

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

分類：`SAME_RULE`；primary textual evidence 仍開放。

### Fourteen major stars

Tier-A implementations 的 relative placements 高度一致；matharts 的 primary-scan dossier另提供日本國立公文書館 `新鋟希夷陳先生紫微斗数全書１` 的 placement glyph evidence。

分類：`SAME_RULE`，目前是最強的 source-backed deterministic candidate之一。

### 左輔／右弼／文昌／文曲

common placement rule 在多個 engines 一致，matharts primary-scan research 亦提供 rule-specific evidence。

### Four Transformations

不能視為 universal Core Fact。

目前至少三個 relevant families：

```text
Taiwan/common implementation family
  戊 貪陰右機
  庚 陽武陰同
  壬 梁紫左武

Zhongzhou family
  戊 貪陰陽機
  庚 陽武府同
  壬 梁紫府武

Research default candidate
  戊 貪陰右機
  庚 陽武府同
  壬 梁紫左武
```

第三組在網路／實務可找到採用例，但不是目前最普及的單一 named-school whole-table。故使用中性 identity：

`sihua.default_v1`

而不是強行命名為「全書版」或其他 lineage。

選它作 `ziwei.baseline.tw_v1` 的原因是 user-perceived-fit Tarot research decision，不是 engine majority 或古籍唯一性證明。

### Leap month

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

基本方向與 first start age 在 matharts / iztro / Fortel / Binger 高度一致：

```text
陽男陰女順
陰男陽女逆
first start age = bureau number
```

更細的 transition / childhood / boundary semantics 仍保留 profile。

## Research default candidate v1

```text
ziwei.baseline.tw_v1
├─ chart_mode.tian_pan
├─ calendar.traditional_lunar
├─ year_boundary.lunar_new_year
├─ life_body.standard
├─ bureau.standard
├─ major_stars.standard_14
├─ decadal.standard_direction_start
├─ sihua.default_v1 = 戊右 / 庚府 / 壬左
├─ leap.split_after_15
├─ rat_hour.next_day_23
├─ clock.civil
└─ true_solar.disabled
```

這是一個 **componentized research preset**。任何 component 的未來 evidence 更新，都可個別 revision，不應把整套 preset當成單一不可拆 doctrine。

## Open evidence gaps

優先順序：

1. Life / Body original or early textual evidence；
2. Five-Element Bureau primary / historical evidence；
3. Zi Wei birthday-placement primary evidence；
4. decadal direction / start-age source evidence；
5. Four-Transformation variant/source registry；
6. brightness、minor stars、dynamic charts；
7. interpretation claim source architecture。

在上述 gap 關閉前，不建立 production provider selection 或 canonical production profile。
