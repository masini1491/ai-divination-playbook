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

Unknown birth time 不得以 local noon 等 placeholder 冒充 exact chart；若缺失 materially 影響 angles / houses，依 provider/runtime contract fail closed或縮小解讀範圍。

## 2. Natal Interpretation Scope

Production v1 在 admitted facts / claims存在時可解讀：

- 12-house topics；
- major essential dignity；
- admitted major-aspect claims；
- source-backed methodological / uncertainty claims。

不得因 chart含更多可計算欄位就自動擴充到未 admitted systems。

## 3. House Policy

```text
explicit house system required
→ Whole Sign or Placidus
→ preserve configuration provenance
→ no cross-system averaging
```

若比較兩套 house system，建立兩個 configuration views；不得混成一張盤。Angles / cusps不做 method-neutral equivalence假設。Parent-signification、turned houses、planetary joys不作 project-wide default。

## 4. Essential Dignity Policy

Production v1 admitted：

```text
domicile
exaltation
detriment
fall
```

Dignity描述 condition / resources / friction，不是道德好壞；不做 numeric scoring。

Triplicity、terms/bounds、face/decan、peregrine/full reception scoring等未由 production admission另行啟用前，不得自行補入。

## 5. Natal Aspect Use

Major-aspect geometry / orb屬 deterministic fact，orb machine authority由 runtime / admission contract擁有，本檔不重複數值表。

Interpretation：

- exact pair有 admitted claim → 可用 pair-specific meaning；
- 只有 general aspect geometry → 只用 general geometry layer；
- 沒有 admitted semantic claim → `unsupported_factor`；
- research-only pair module不得偷渡。

## 6. Natal Interpretation Order

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

## 7. Natal Unsupported / Uncertainty

- 無 house fact → 不從 Sun sign猜 house；
- 無 source-backed planet/sign或pair claim → 不輸出固定人格模板；
- `user_asserted` chart facts要標示未獨立重算；
- birth-time uncertainty materially影響 house/angle時必須揭露；
- provider不支援的 scope不得由模型補算。

共通 safety / source / recording rule回到 `ASTROLOGY.md`。
