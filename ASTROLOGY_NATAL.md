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

## 3. House Policy

```text
explicit admitted house system
→ preserve configuration provenance
→ no cross-system averaging
```

若比較兩套 house system，建立兩個 configuration views；不得混成一張盤。Angles / cusps不做 method-neutral equivalence假設。Parent-signification、turned houses、planetary joys不作 project-wide default。

## 4. Essential Dignity Policy

只使用 `ASTROLOGY_PRODUCTION_ADMISSION_V1.json` 當前 admitted 的 dignity categories；本 mode owner不重複保存 exact enum。

Dignity描述 condition / resources / friction，不是道德好壞；不做 numeric scoring。未由 production admission啟用的 dignity layer不得自行補入。

## 5. Natal Aspect Use

Major-aspect geometry / orb屬 deterministic fact，orb machine authority由 runtime / admission contract擁有，本檔不重複數值表。

Interpretation：

- exact pair有 admitted claim → 可用 pair-specific meaning；
- 只有 general aspect geometry → 只用 general geometry layer；
- 沒有 admitted semantic claim → `unsupported_factor`；
- research-only pair module不得偷渡。

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

目前 Yod、Stellium、Grand Quintile與 exact consumer/唐綺陽 pattern compatibility不在此 production projection scope；依 `ASTROLOGY_PRODUCTION_ADMISSION_V1.json` fail closed。

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
- planet-in-sign interpretation 優先組合 production-admitted 的 planet-function + sign-style claims；該 composable semantics registry 必須由 typed request 明確選擇 production manifest 所列 semantic profile，不得在 tradition / framework 未指定時 silent-default。此 profile 是 project semantic profile，不得冒充 canonical astrology school。不得把兩者合成固定人格診斷。Exact planet/sign pair meaning只有在另有 pair-specific admitted claim時才可使用；無 source-backed claim（包含目前未另行 admission 的 North Node sign semantics）→ `unsupported_factor`；
- `user_asserted` chart facts要標示未獨立重算；
- birth-time uncertainty materially影響 house/angle時必須揭露；unknown-time invariant-only bundle不得被描述成完整星盤；
- unknown-time 被 provider省略的天體代表該 local-date window 內 sign 無法達到 admission certainty，不得由模型補猜；
- provider不支援的 scope不得由模型補算。

共通 safety / source / recording rule回到 `ASTROLOGY.md`。


## Explicit extended-aspect projections

The natal provider's default aspect graph remains `aspect-participants-core-bodies-v1`. Extended aspect geometry is available only through `tools/astrology_aspect_projection.py` with explicit admitted participant, aspect, and orb policy selectors. No silent default or automatic inclusion is allowed. Angle/Fortune policies require exact birth time. Projection output is deterministic geometry only; semantic interpretation requires separately admitted source-backed claims.
