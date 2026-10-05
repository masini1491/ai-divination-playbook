# Zi Wei Dou Shu / 紫微斗數 Research

## Authority boundary

```text
RESEARCH OWNER / SCOPE-A V1 HAS SEPARATE PRODUCTION BINDING
```

本目錄是紫微斗數的獨立研究線。它不屬於 Astrology production owner，也不修改 Tarot／Meihua／Liuyao／Palmistry 的 maturity 或 routing。

目前 lifecycle：

```text
research-only scaffold
→ deterministic calculation research
→ source / tradition research
→ interpretation architecture research
→ bounded admission review
```

目前 production 狀態：

- Scope-A natal provider：G1 admitted
- Scope-A v1 production binding：G7 admitted (`admissions/ziwei/ZIWEI_PRODUCTION_ADMISSION_V1.json`)
- root production owner：`ZIWEI.md` 已建立
- explicit Zi Wei routing：已 admitted；使用者明確要求紫微時可進 production Scope-A
- Gregorian input adapter：`ziwei.calendar.civil_v2` 已 admitted（explicit IANA civil time；shared `civil-time-zoneinfo-v1` validation）
- optional true-solar input profile：`ziwei.true_solar.noaa_fractional_year_v1` 已 admitted，僅 explicit profile + longitude；civil time仍是default，birthplace→longitude/timezone不猜
- optional brightness profile：`ziwei.brightness.iztro_v1` 已 admitted，僅 explicit add-on
- sparse same-palace pair interpretation：`武曲×天相` 目前只 admission `兄弟宮` / `官祿宮` 2 條 practitioner-bounded claims；exact canonical occupancy match 才啟動，無 14×14 Cartesian expansion
- Body-Palace overlay interpretation：production admission 1 條 `身宮=後天發展 overlay` methodology + `夫妻宮` / `財帛宮` / `官祿宮` / `遷移宮` 4 條 exact overlay claims；deterministic fact 只把 `body_palace.branch` 映射回既有十二宮，不建立第十三宮
- sparse star×palace contextual interpretation：production admission `天相×命宮`、`天梁×官祿宮`、`巨門×兄弟宮` 3 條 practitioner-bounded overrides + `貪狼×夫妻宮`、`破軍×遷移宮`、`武曲×田宅宮`、`天機×田宅宮`、`破軍×夫妻宮`、`廉貞×財帛宮`、`武曲×命宮` 7 條 historical-bounded overrides + `七殺×福德宮` 1 條 historical-condition + practitioner-bounded override；只吃 canonical occupancy，無 14×12 Cartesian expansion，未 admission 組合維持 L5 composition
- star×palace research follow-up：`STAR_PALACE_CONTEXTUAL_RESEARCH_V2.md` 的 `貪狼×夫妻宮` historical bounded candidate 已 separately production-admitted；Nihai 配偶年齡 heuristic 仍為 practitioner-only defer，`紫微×官祿宮` 維持 non-material rejection，`破軍×遷移宮` 維持 borderline/defer
- star×palace research v3：`STAR_PALACE_CONTEXTUAL_RESEARCH_V3.md` research-only admission candidates `破軍×遷移宮`、`武曲×田宅宮`、`天機×田宅宮`、`破軍×夫妻宮` 均已 separately production-admitted；`貪狼×遷移宮` 維持 borderline/defer，`紫微×遷移宮` 維持 redundant rejection

- star×palace coverage architecture V1：168 identities 已 admission；目前 reviewed 154 / resolved 119 / unreviewed 14，dedicated L4 為 11。168/168 resolved 保留為長期 research horizon，不是近期 product KPI / release blocker；matrix continuation 改為 reading-gap-driven，不再 bulk sweep。
- star×palace research v4：`STAR_PALACE_CONTEXTUAL_RESEARCH_V4.md` 已推進至 batch 13；所有 ordinary non-health palace rows 已 14/14 reviewed；只剩 14 個疾厄宮 identities 尚未 reviewed。疾厄宮維持 separate health-safe research path，但不阻擋 natal synthesis v1；research candidate 仍不等於 production claim。
- star×palace targeted recheck v5：`STAR_PALACE_CONTEXTUAL_RESEARCH_V5.md` 依實際 reading specificity gap 只重查 `紫微×官祿宮`、`七殺×福德宮`、`天府×財帛宮`；前後兩格維持 `BOUNDED_L5_COMPOSITION`，`七殺×福德宮` 重新開為 `DEFERRED_EVIDENCE / ADMISSION-CANDIDATE-RECHECK`，尚未取得 production authority。
- star×palace targeted recheck v6：`STAR_PALACE_CONTEXTUAL_RESEARCH_V6.md` 只重查 `太陽×父母宮`、`天梁×父母宮`、`天同×兄弟宮`、`巨門×兄弟宮`；太陽／天同維持 bounded-L5，天梁／巨門重新開為 `DEFERRED_EVIDENCE / ADMISSION-CANDIDATE-RECHECK`；`太陰×子女宮` 仍留給 separate high-risk gate。
- star×palace high-risk targeted recheck v7：`STAR_PALACE_CONTEXTUAL_RESEARCH_V7.md` 單獨重查 `太陰×子女宮`；排除性別／數量／生育／健康存亡／固定成就等高風險斷語後，沒有留下超越現有 `太陰 core + 子女宮 domain + dignity condition` 的 material distinction，因此維持 `HIGH_RISK_BOUNDED / resolved`，coverage metrics 不變。
- star×palace admission-candidate evidence review v8：`STAR_PALACE_CONTEXTUAL_RESEARCH_V8.md` 對 V5/V6 reopened cells 做下一層 evidence gate；`巨門×兄弟宮`、`七殺×福德宮` 當時升為 research `ADMISSION-CANDIDATE`，`天梁×父母宮` 改為 `DEFER-BORDERLINE`。後續 production-admission review 已將前兩格 separately admission 為 dedicated L4；`天梁×父母宮` 仍維持 deferred。
- natal synthesis v1：production-admitted selection-only layer over the default 70 base natal claims；保留 full selected-claim trace，預設聚焦 4–6 個高辨識度且盡量不重複的 evidence-bounded signals，不新增 doctrine，不更改 optional-module defaults。
- optional M1 auxiliary profile：`ziwei.auxiliary.m1.common_v1` admission 天魁／天鉞／祿存／天馬／擎羊／陀羅／火星／鈴星／地空／地劫十星 natal placement + 10 條 bounded modifier-role policy；runtime 必須與 M0 同時啟用，M0+M1 才提供 broader auxiliary completeness；M2/M3與高風險事件斷語仍未 admission
- deterministic ChatGPT materialization：`ZIWEI_MATERIALIZATION.md` + bundle 已建立
- ordinary unspecified auto-routing：仍刻意為 false
- dynamic calculation：`decadal → yearly → monthly → daily → hourly` 五層 calculation-only 已依 V2–V6 分層 production-admitted；
- decadal / 大限 interpretation：V7 只 admission 2 條 bounded methodology claims，用已計算的大限區間／命宮位置建立十年 context，並要求較細事件等待 lower-layer evidence；不 admission natal-claim promotion、generic吉凶或具體事件預測；
- yearly / 流年 interpretation：V8 只 admission 3 條 bounded methodology claims，要求同層三方／對照、compatible 大限 parent 合參與 no-generic-yearly-filler；target-year 四化仍是 calculation context，不自動 admission 流年四化斷語；
- monthly / 流月 interpretation：V9 只 admission 3 條 bounded methodology claims，要求斗君／effective-month 月層 identity、compatible 流年 parent 合參與 no-generic-monthly-filler；monthly Si Hua / flow stars仍未 admission；
- daily / 流日 interpretation：V10 只 admission 3 條 bounded methodology claims，來源為 practitioner/tradition references；要求 explicit lunar-day identity、compatible 流月 parent 合參與 no-generic-daily-filler；day pillar / daily Si Hua / flow stars仍未 admission；
- hourly / 流時 interpretation：V11 只 admission 3 條 profile-bounded methodology claims，要求 explicit hour-branch identity、compatible 流日 parent 合參與 no-generic-hourly-filler；來源亦顯示派法不唯一，故不宣稱唯一傳統；physical hour pillar / 五鼠遁時干 / hourly Si Hua / flow stars仍未 admission；
- broader contextual star×palace / 未另 admission 的 auxiliary / Four-Transformation interpretation：仍未 production-admitted；star×palace 僅上述 11 條、same-palace pairs 僅上述 2 條、Body-Palace overlays 僅上述 5 條 source-explicit claims admitted
- 科學／客觀預測有效性：未聲稱

## Production boundary

Research registries remain historical research owners and keep `production_routable=false`. Scope-A v1 production authority is added separately by root `admissions/ziwei/ZIWEI_PRODUCTION_ADMISSION_V1.json` and `tools/ziwei_scope_a_pipeline.py`; this does not make the research directory itself an ordinary production router.

## Research objective

第一階段研究目標是建立：

1. 可重現的 deterministic chart-fact architecture；
2. 明確的 calculation / tradition profile；
3. 古籍、現代門派與 implementation evidence 的分層；
4. lineage-aware cross-engine validation；
5. 一套可供未來 ChatGPT 使用的 research default candidate；
6. 可追溯、conflict-preserving、fail-closed 的 interpretation architecture。

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
decadal_profile = decadal.quanji_common_v1
  direction = yang_male_yin_female_forward_else_reverse
  first_palace = life_palace
  first_start_age = five_element_bureau_number

sihua_profile = sihua.default_v1
  戊 = 貪狼化祿 / 太陰化權 / 右弼化科 / 天機化忌
  庚 = 太陽化祿 / 武曲化權 / 天府化科 / 天同化忌
  壬 = 天梁化祿 / 紫微化權 / 左輔化科 / 武曲化忌

leap_month_policy = split_after_day_15
rat_hour_policy = next_day_at_23
clock_mode = civil_time
true_solar_time = disabled_by_default
optional_true_solar_profile = ziwei.true_solar.noaa_fractional_year_v1 (explicit longitude only)

interpretation_profile = ziwei.interpretation.tw_v1
  architecture = contextual_composition
  historical_semantic_baseline = nanyang_quanshu
  modern_claim_adoption = explicit_only
  conflict_policy = preserve_no_implicit_average
  production_admitted = false
```

### Why this is only a candidate

- 命身宮、五行局、紫微生日定位結果、十四主星與部分輔星已取得不同程度的 historical/source support；但大限第一宮／起歲、四化、閏月等已確認存在 witness/profile 差異，不能再以 implementation convergence 代替 historical agreement。
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
- [`SOURCE_RECONCILIATION_V1.md`](SOURCE_RECONCILIATION_V1.md)
- [`FOUR_TRANSFORMATION_VARIANT_REGISTRY.md`](FOUR_TRANSFORMATION_VARIANT_REGISTRY.md)
- [`INTERPRETATION_ARCHITECTURE_V0.md`](INTERPRETATION_ARCHITECTURE_V0.md)
- [`INTERPRETATION_RUNTIME_CONTRACTS_V0.md`](INTERPRETATION_RUNTIME_CONTRACTS_V0.md)
- [`INTERPRETATION_FIXTURE_VALIDATION_V0.md`](INTERPRETATION_FIXTURE_VALIDATION_V0.md)
- [`INTERPRETATION_ADMISSION_REVIEW_V0.md`](INTERPRETATION_ADMISSION_REVIEW_V0.md)
- [`INTERPRETATION_CLAIM_REGISTRY_SCHEMA_V0.md`](INTERPRETATION_CLAIM_REGISTRY_SCHEMA_V0.md)
- [`INTERPRETATION_CLAIM_BATCH1_ADMISSION.md`](INTERPRETATION_CLAIM_BATCH1_ADMISSION.md)
- [`ziwei_interpretation_claim_registry_batch1.json`](ziwei_interpretation_claim_registry_batch1.json)
- [`INTERPRETATION_CLAIM_BATCH2_ADMISSION.md`](INTERPRETATION_CLAIM_BATCH2_ADMISSION.md)
- [`ziwei_interpretation_claim_registry_batch2.json`](ziwei_interpretation_claim_registry_batch2.json)
- [`INTERPRETATION_CLAIM_PALACES_V0_ADMISSION.md`](INTERPRETATION_CLAIM_PALACES_V0_ADMISSION.md)
- [`ziwei_interpretation_claim_registry_palaces_v0.json`](ziwei_interpretation_claim_registry_palaces_v0.json)
- [`STAR_PALACE_COMBINATION_RESEARCH_V0.md`](STAR_PALACE_COMBINATION_RESEARCH_V0.md)
- [`BRIGHTNESS_INTERPRETATION_RESEARCH_V0.md`](BRIGHTNESS_INTERPRETATION_RESEARCH_V0.md)
- [`FOUR_TRANSFORMATION_INTERPRETATION_RESEARCH_V0.md`](FOUR_TRANSFORMATION_INTERPRETATION_RESEARCH_V0.md)
- [`MINOR_STAR_ADMISSION_TAXONOMY_V0.md`](MINOR_STAR_ADMISSION_TAXONOMY_V0.md)
- [`TEMPORAL_CONTEXT_INTERPRETATION_RESEARCH_V0.md`](TEMPORAL_CONTEXT_INTERPRETATION_RESEARCH_V0.md)
- [`EXECUTABLE_RETRIEVAL_COMPOSITION_V0.md`](EXECUTABLE_RETRIEVAL_COMPOSITION_V0.md)
- [`interpretation_retrieval_v0.py`](interpretation_retrieval_v0.py) — research compatibility shim; canonical executable owner is `../../tools/ziwei_claim_retrieval.py`
- [`PRODUCTION_READINESS_GAP_ANALYSIS_V0.md`](PRODUCTION_READINESS_GAP_ANALYSIS_V0.md)
- [`PRODUCTION_SCOPE_A_NATAL_FIRST_V0.md`](PRODUCTION_SCOPE_A_NATAL_FIRST_V0.md)
- [`PRODUCTION_SCHEMA_CANDIDATES_V0.md`](PRODUCTION_SCHEMA_CANDIDATES_V0.md)
- [`UNCERTAINTY_SAFETY_DELIVERY_CONTRACT_V0.md`](UNCERTAINTY_SAFETY_DELIVERY_CONTRACT_V0.md)
- [`ziwei_executable_behavioral_fixtures_v0.json`](ziwei_executable_behavioral_fixtures_v0.json)

## Current coordination backlog

Current open maintenance / architecture / admission work is tracked in [`../../ZIWEI_BACKLOG.md`](../../ZIWEI_BACKLOG.md).

That file is coordination-only. It does not supersede this research owner, `ZIWEI.md`, admission manifests or production tools.

## Research continuation contract

目前 first-layer research closure：

```text
14 major stars / 28 claims
12 palaces / 24 claims
combined = 52 first-layer claims
```

在目前 `Project AI mode: ChatGPT-Only` 下，以下清單保存曾由 ChatGPT 直接承接的 **research / evidence / schema / admission continuation stages**；目前均已 closure：

1. `star×palace` combination-family research — **CLOSED — RESEARCH**；
2. brightness interpretation-family research — **CLOSED — RESEARCH**；
3. Four-Transformation interpretation-family research — **CLOSED — RESEARCH**；
4. bounded minor-star admission taxonomy — **CLOSED — RESEARCH**；
5. temporal-context interpretation research — **CLOSED — RESEARCH**。

這份清單目前已全部完成 research closure。它只保存 **eligible continuation candidates 與 actor suitability**，不是自動啟動的 roadmap、Hot backlog 或 production commitment。只有使用者明確要求繼續 Zi Wei research line，或 current canonical trigger 另行 admission 該 scope 時，才開始其中一項；每個新 Stage 仍須依 current work 重新判斷最低充分 actor，不得因前一 Stage 曾使用其他 actor 而慣性 handoff。

上述 ChatGPT-side research 可做 source reconciliation、claim normalization、conflict preservation、schema/admission design 與 bounded fixture/evidence work。Executable retrieval/composition 已另行取得 **RESEARCH-ONLY V0** admission；不得由此推導為 production authority。

Production-readiness blocker inventory 由 `PRODUCTION_READINESS_GAP_ANALYSIS_V0.md` 擁有；minimum product scope 由 `PRODUCTION_SCOPE_A_NATAL_FIRST_V0.md` 固定為 **Scope A — bounded natal first layer only**；`PRODUCTION_NATAL_PROVIDER_ADMISSION_V0.md` + `tools/ziwei_natal_provider.py` 已完成 **G1 Scope-A natal calculation admission**。G2 schema candidates、G5 executable behavioral validation、G6 uncertainty/safety delivery contract 已完成 **RESEARCH-CLOSED**；52 claims 已滿足 Scope-A interpretation coverage。這些 closure 與 scope decision 都不授予 production authority。

仍需分開 gate 的後續包括：

- executable claim retrieval / composition — **ADMITTED — RESEARCH-ONLY V0**；
- deterministic production runtime / provider；
- production `ZIWEI.md`；
- `METHOD_ROUTING.md` integration / unspecified-user auto-routing；
- production cross-validation / production-bound behavioral validation；
- production renderer/API binding；
- explicit production admission。

建議 continuation ordering（僅供 research planning，不構成自動 admission）：

```text
star×palace
→ brightness
→ Four-Transformation interpretation
→ bounded minor-star taxonomy
→ temporal context
→ executable retrieval/composition  # ADMITTED — RESEARCH-ONLY V0
```

## Promotion boundary

未來若要進 production，仍需另外完成：

```text
research judgment gap closed
→ production method owner
→ deterministic/runtime authority
→ bind versioned request/fact/frame schema candidates
→ provenance/fact gate
→ production-bound behavioral validation
→ uncertainty/safety renderer binding
→ explicit production admission
→ routing
```

目前已 admission 14 顆主星 / 28 條與十二宮 / 24 條 source-normalized machine-readable research claims，完成 `major-star + palace` 第一層共 52 條 coverage；**Scope A 已選定並以這 52 條作為完整必要 interpretation corpus**。star×palace composition policy、brightness interpretation responsibility 與 Four-Transformation interpretation responsibility 已 research-closed；project-wide brightness table、auxiliary-star claim corpus、dynamic claim corpus 均不屬 Scope-A blocker；bounded executable retrieval/composition v0 已 research-only admission。

建立本 research dossier 不構成 production admission。
