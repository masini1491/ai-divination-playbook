# Zi Wei Dou Shu / 紫微斗數 Research

## Authority boundary

```text
REFERENCE-ONLY / RESEARCH-ONLY / NOT PRODUCTION-ROUTABLE
```

本目錄是紫微斗數的獨立研究線。它不屬於 Astrology production owner，也不修改 Tarot／Meihua／Liuyao／Palmistry 的 maturity 或 routing。

目前 lifecycle：

```text
research-only scaffold
→ deterministic calculation research
→ source / tradition research
→ bounded admission review
```

目前**沒有**：

- production `ZIWEI.md`
- production runtime / provider
- ordinary `METHOD_ROUTING.md` entry
- production cross-validation
- unspecified-user auto-routing
- 科學／客觀預測有效性聲明

## Research objective

第一階段研究目標是建立：

1. 可重現的 deterministic chart-fact architecture；
2. 明確的 calculation / tradition profile；
3. 古籍、現代門派與 implementation evidence 的分層；
4. lineage-aware cross-engine validation；
5. 一套可供未來 ChatGPT 使用的 research default candidate。

產品 default 的目前目標不是宣稱「唯一正統」，而是：

> 在未指定流派時，提供一套明確、可追溯、componentized 的 baseline；目前 user-facing selection goal 偏重一般使用者載入 ChatGPT 後的主觀貼合／命中感，同時保留常見流派 alternative。

## Default candidate

目前 research-level default candidate：

```text
profile_id = ziwei.baseline.tw_v1
authority = research-candidate
production_admitted = false

chart_mode = tian_pan
calendar_basis = traditional_lunar
year_boundary = lunar_new_year
life_body = standard_month_hour_rule
five_element_bureau = standard_ming_palace_ganzhi
ziwei_start = standard_bureau_day_rule
major_star_placement = standard_fourteen_major
decadal_direction = yang_male_yin_female_forward_else_reverse
decadal_start_age = five_element_bureau_number

sihua_profile = sihua.default_v1
  戊 = 貪狼化祿 / 太陰化權 / 右弼化科 / 天機化忌
  庚 = 太陽化祿 / 武曲化權 / 天府化科 / 天同化忌
  壬 = 天梁化祿 / 紫微化權 / 左輔化科 / 武曲化忌

leap_month_policy = split_after_day_15
rat_hour_policy = next_day_at_23
clock_mode = civil_time
true_solar_time = disabled
```

### Why this is only a candidate

- 核心命身宮、五行局、紫微起星、十四主星與大限基本方向在多個 implementation 中高度一致，但仍需逐項補 primary-source reconciliation。
- 四化、閏月、晚子時、年界、天／地／人盤、亮度與部分輔雜星存在流派或 boundary 差異。
- `sihua.default_v1` 的「戊右／庚府／壬左」不是目前網路最普及的單一 named-school table；它是本研究線針對 **user-perceived fit** 做 Tarot 比較後保留的 default candidate。
- Tarot selection evidence 只代表本專案的象徵性設計覆核，不證明客觀預測效度，也不取代 source evidence。

## Componentized profile rule

不得把 profile 簡化成只有：

```text
school = zhongzhou
```

至少概念上分離：

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
└─ horoscope_boundary_policy
```

named school / preset 可以組合 components，但 component identity 與 provenance 必須保留。

## Evidence architecture

詳細見：

- [`EVIDENCE_ARCHITECTURE.md`](EVIDENCE_ARCHITECTURE.md)
- [`CALCULATION_ENGINE_RESEARCH.md`](CALCULATION_ENGINE_RESEARCH.md)
- [`SOURCE_REGISTRY.md`](SOURCE_REGISTRY.md)

## Promotion boundary

未來若要進 production，仍需另外完成：

```text
research judgment gap closed
→ production method owner
→ deterministic/runtime authority
→ request/fact schemas
→ provenance/fact gate
→ routing
→ behavioral regression
→ explicit production admission
```

建立本 research dossier 不構成 production admission。
