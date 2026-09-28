# Astrology Natal｜本命盤解讀契約

Status: **PRODUCTION V1 MODE OWNER**

本檔是 `ASTROLOGY.md` 下的 Natal mode policy owner；不取代 root method owner，也不擁有 deterministic calculation mechanics。

## 1. Entry / Inputs

```text
ASTROLOGY.md
→ reading_mode = natal
→ admitted natal Astrology Fact Bundle
→ ASTROLOGY_NATAL.md
```

Raw birth data 的 calculation 由 `tools/astrology_provider.py` 執行；若只有 city/locality，可先走 `tools/astrology_place_resolver.py`。Exact provider/resolver scope、DST、latitude、dependency 與 not-admitted boundary以：

- `ASTROLOGY_PROVIDER_ADMISSION_V1.json`
- `ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json`

為 machine truth。不得在本檔或模型中另造 calculation rule。

Unknown birth time 不得以 local noon 等 placeholder 冒充 exact chart。Production provider 可走 machine-admitted 的 invariant-only path：以本地出生日期 + IANA timezone 建立完整 local-date window，只輸出整個 window 都能 deterministic 保持的 tropical planet/luminary sign facts；不輸出 exact longitude degree、Asc/MC、houses 或 natal aspects。若只有 country-level location，只有在 admitted offline resolver 能唯一解析 IANA timezone 時才可使用；多時區國家 fail closed。

## 2. Natal Interpretation Scope

Production v1 在 admitted facts / claims存在時可解讀：

- 12-house topics；
- major essential dignity；
- admitted major-aspect claims；
- explicit-policy house-rulership projections；
- explicit-policy admitted major-aspect pattern topology；
- source-backed methodological / uncertainty claims。

不得因 chart含更多可計算欄位就自動擴充到未 admitted systems。

### 2.1 Semantic Profile Interaction Policy

Ordinary natal interpretation：explicit admitted `semantic_profile` → `explicit_user_choice`；omitted/null → `composable-symbolic-modern-v1` + `project_default`。Project default 必須在 user-facing output 揭露。

此 profile 是 bounded project UX default，不代表唯一／canonical／客觀正確的占星傳統，也不是科學人格模型。它只選擇既有 admitted semantic claims，不新增 admission、補 unsupported factors或改變 explicit-request-only routing。

Profile / selection provenance 由 reading request + orchestrator 正規化；registry / selector不得自行 silent-default。Explicit 未 admission profile → fail closed。

## 3. House Policy

Known-time production採用下列 interaction profile：

```text
使用者明確指定 Whole Sign / Placidus
→ 尊重 explicit choice
→ house_system_selection = explicit_user_choice

使用者未指定、或 house_system = null
→ project UX default = Placidus
→ house_system_selection = project_default
→ user-facing output 必須揭露目前採 Placidus（預設）
→ 同時提醒 Whole Sign 亦可選，切換後部分宮位落點與相關解讀可能改變
```

這是 **project UX default**，不是「Placidus 客觀更準／歷史上更正統／Whole Sign 次等」的 claim。兩套仍同為 admitted calculation configurations；研究證據不因本 interaction profile 而被改寫。

若 default Placidus 因 current production latitude boundary或其他 provider gate 不可用，必須 fail closed並告知可明確改選 Whole Sign；不得 silent fallback成另一宮位制。

Unknown birth time 不套用 house-system default，仍維持 `house_system = null` 且不輸出 houses / angles。

若比較兩套 house system，建立兩個 configuration views；不得混成一張盤或平均結果。Angles / cusps不做 method-neutral equivalence假設。Parent-signification、turned houses、planetary joys不作 project-wide default。

## 4. Essential Dignity Policy

只使用 `ASTROLOGY_PRODUCTION_ADMISSION_V1.json` 當前 admitted 的 dignity categories；本 mode owner不重複保存 exact enum。

Dignity描述 condition / resources / friction，不是道德好壞；不做 numeric scoring。未由 production admission啟用的 dignity layer不得自行補入。

## 5. Natal Aspect Use

Major-aspect geometry / orb屬 deterministic fact，orb machine authority由 runtime / admission contract擁有，本檔不重複數值表。Geometry fact 本身沒有 semantic interpretation authority。

### 5.1 Natal semantic precedence / fallback

Production natal semantics固定使用下列 precedence：

```text
exact admitted emergent claim
→ admitted bounded composition
→ unsupported_factor
```

這是 interpretation evidence precedence，不改寫 deterministic chart facts。Exact claim 只補充其 source-backed material semantic delta；不得把同一 lower-level composition完整重講一次，也不得因 exact claim存在就修改 planet、sign、house、aspect、orb或其他 deterministic fact。

**Planet × Sign**

- current production baseline已 admission `planet-sign-composable-semantics-research-v1` 的 `planet_function` + `sign_style` primitives；
- composition只有在兩個 primitives都由同一實際 planet fact的 typed applicability綁定、且符合 manifest要求的 explicit semantic profile時成立；
- 若另有 exact Planet×Sign pair claim admission，exact claim優先提供其 emergent delta；**沒有 exact pair claim本身不構成 unsupported**，只要 admitted function + style composition完整成立；
- 任一 primitive、profile、fact binding或source admission缺失 → `unsupported_factor`，不得由 model memory補語義。

**Natal Aspect**

- exact pair/aspect claim只有在實際 natal aspect fact、typed `aspect_pair` applicability、admitted registry/claim與 production source policy全部通過時可用；
- current production已 admission的 pair-specific lane只限 manifest實際列入的 registry/claim + source-policy intersection；qualified-only registries仍不是 production authority；
- current major-aspect geometry / orb policy只證明「這個 aspect fact存在」，**目前沒有 project-wide admitted planet-pair relationship semantic + general aspect-operator semantic primitives，因此一般 natal aspect bounded composition仍未 admission**；
- 所以 current fallback是：exact admitted pair/aspect claim命中 → 使用；否則保留 geometry fact並將 semantic layer標成 `unsupported_factor`。不得把 conjunction / opposition / trine / square / sextile 的一般模型印象當成已 admission operator semantic。

Typed applicability與 evidence lineage必須保持分離：Planet×Sign使用實際 object/sign fact binding；Natal Aspect使用實際 aspect fact + canonicalized pair/aspect applicability。Research-only pair module不得偷渡。

## 6. Policy-Derived Natal Projections

Rulership 與 aspect-pattern topology 都不是新的 astronomical facts；它們是建立在已 admitted natal facts 上的 deterministic policy projection。

### House rulership

使用者明確要求宮主星／house ruler，且本命盤具有完整 admitted house facts時：

```text
admitted natal bundle
→ require explicit rulership policy
   ├─ rulership-traditional-v1
   └─ rulership-modern-v1
→ tools/astrology_rulership_projection.py
```

不得因一般占星習慣、使用者未指定流派或模型偏好而 silent-default。不得自動混合 traditional / modern，也不得自行加入未 admitted co-ruler policy。Projection 本身沒有 semantic interpretation authority；後續語意仍需 admitted claims / mode-owner規則。

### Aspect-pattern topology

使用者明確要求 T-Square、Grand Trine、Grand Cross、Kite、Mystic Rectangle、Cradle、Grand Sextile 等 production-admitted pattern時：

```text
runtime-admitted natal aspect graph
→ explicit admitted E5 participant / aspect / orb policy
→ explicit E6 pattern policy + projection policy
→ tools/astrology_pattern_topology.py
```

不得從 raw longitudes繞過 E5 qualified aspect graph，也不得因 object存在就讓 angle、South Node、Part of Fortune或其他 extended point自動參與。若缺少 explicit policy selector，保持 unsupported / ask only when materially necessary；不得 silent-default。

Yod、Stellium、Grand Quintile 另走 `tools/astrology_special_pattern_projection.py` 的 explicit special-pattern policy path；必須明確選擇 participant / aspect / orb / pattern / Stellium policy，且不改寫既有 major-pattern topology。這些 projection 只建立 deterministic geometry/topology facts，沒有 semantic interpretation authority。exact consumer/唐綺陽 pattern compatibility仍未驗證，不得宣稱相容。

## 7. Natal Interpretation Order

```text
1. identify user question
2. resolve input only if needed
3. calculate / admit natal facts
4. runtime Fact Gate
5. state provenance / uncertainty
6. select only relevant houses / dignity / aspects
7. preserve source/tradition conflicts
8. minimum-sufficient synthesis
```

不要為了「完整」傾倒整張盤所有 factor；輸出仍受 `CHATGPT_OUTPUT.md` minimum-sufficient與Pre-Send gate約束。

## 8. Natal Unsupported / Uncertainty

- 無 house fact → 不從 Sun sign猜 house；
- planet-in-sign interpretation依 §5.1 precedence：有 separately admitted exact pair claim時只由它補 emergent delta；否則只要 production-admitted planet-function + sign-style claims、實際 fact binding與 explicit semantic profile全部成立，就使用 bounded composition。**缺 exact pair claim本身不是 unsupported 條件**；缺任一 required primitive/profile/applicability/source gate才是 `unsupported_factor`。不得把 composition寫成固定人格診斷；
- North Node sign interpretation 只允許 `north-node-sign-semantics-research-v1` 的 bounded `north_node_function` 與既有 admitted sign-style composition。typed selection 必須以 `north_node_core` / `north_node_sign_style` 綁定實際 `NorthNode` point、實際 sign，並保留 production-admitted **mean North Node** provenance；普通 planet `sign_style` scope 仍不得接受 point。此 admission 不包含 North Node aspect meanings、South Node semantics、generic karma / past-life / soul-evolution doctrine，缺任一 admission 或 provenance gate 時保持 `unsupported_factor`；
- `user_asserted` chart facts要標示未獨立重算；
- birth-time uncertainty materially影響 house/angle時必須揭露；unknown-time invariant-only bundle不得被描述成完整星盤；
- unknown-time 被 provider省略的天體代表該 local-date window 內 sign 無法達到 admission certainty，不得由模型補猜；
- provider不支援的 scope不得由模型補算。

共通 safety / source / recording rule回到 `ASTROLOGY.md`。


## Explicit extended-aspect projections

The natal provider's default aspect graph remains `aspect-participants-core-bodies-v1`. Extended aspect geometry is available only through `tools/astrology_aspect_projection.py` with explicit admitted participant, aspect, and orb policy selectors. No silent default or automatic inclusion is allowed. Angle/Fortune policies require exact birth time. Projection output is deterministic geometry only; semantic interpretation requires separately admitted source-backed claims.


## Explicit extended ephemeris facts

使用者明確要求 Chiron / Ceres / Pallas / Juno / Vesta 且出生時間為 exact / approximate 時，可透過 `extended_objects` selector 啟動 `ASTROLOGY_EXTENDED_EPHEMERIS_ADMISSION_V1.json` 的獨立 provider lane。

此 lane 只 admission deterministic calculation facts：

- longitude / sign / degree；
- speed / motion；
- 已有 admitted houses 時的 known-time house placement。

它**不**因此 admission 該天體的象徵語意、星座語意、宮位語意、相位語意或人格／事件判讀。沒有另外 source-backed semantic claim family 時，interpretation 必須維持 `unsupported_factor`。

Extended objects 不加入 default natal aspect graph；若未來要參與 aspect，仍須另外 explicit participant / aspect / orb policy admission。Unknown birth time 與 transit extended-object path目前都不 admission。

