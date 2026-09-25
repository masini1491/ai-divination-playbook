# Astrology｜占星方法契約

Status: **PRODUCTION V1 / EXPLICIT-REQUEST ONLY**

本檔是 Astrology 的 **root method owner**。它只擁有跨 reading-mode 共通的 activation、fact/evidence boundary、source/safety、mode routing 與 production handoff responsibility；Natal / Transit 專屬 interpretation policy 分別由 `ASTROLOGY_NATAL.md`、`ASTROLOGY_TRANSIT.md` 擁有。Deterministic implementation / admission truth 仍由既有 tools、schemas 與 `ASTROLOGY_*_ADMISSION_V1.json` 擁有。

## 1. Activation / Routing

Astrology 不參與 ordinary auto-routing；只有使用者明確要求「占星／星盤／本命盤／行運」等 production intent 才啟動。

```text
explicit Astrology production
→ ASTROLOGY.md
→ resolve reading_mode
   ├─ natal   → ASTROLOGY_NATAL.md
   └─ transit → ASTROLOGY_TRANSIT.md
→ admitted deterministic facts
→ bounded evidence selection / interpretation handoff
→ CHATGPT_OUTPUT.md
```

Research intent仍走：

```text
RESEARCH_ROUTING.md
→ references/astrology/**
```

### Ordinary production authority boundary

Ordinary Astrology production execution MUST use the current `ai-divination-playbook` repo-local admitted authority first. It MUST NOT routinely load or consult other public Astrology repositories merely to execute an already-admitted natal / transit reading.

External Astrology repositories remain reference/evidence surfaces only and MAY be consulted when the routed task explicitly requires research, comparison, provenance/source verification, licensing review, or development/admission work. A pinned external software/data dependency already represented by this repo's admitted provider/materialization contract does not by itself require re-reading that dependency's repository during an ordinary production reading.

This boundary does not bypass the declared shared `ai-development-playbook` activation contract for repository-maintenance work, and it does not promote `references/astrology/**` into production authority.

若使用者明確指定 Astrology，不得因 provider unavailable 就偷偷改用 Tarot / Meihua / Liuyao。

## 2. Deterministic Fact Boundary

下列內容屬 deterministic facts，不由 language model 自行心算、估算或憑記憶補造：planet / luminary longitude、sign assignment、motion / retrograde state、Ascendant / MC、house cusps / placement、aspect geometry / orb、transit-to-natal exact contact、station / ingress / repeated passage。

禁止：

```text
raw birth data
→ model freehand calculation
→ pretend verified chart
```

允許的 fact來源：

1. admitted deterministic provider output；
2. user-supplied structured chart/export；
3. verified existing Astrology Fact Bundle / Reading Record。

Canonical runtime gate：`tools/astrology_runtime.py`；所有 generated provider bundle都必須通過它。Fact Bundle / runtime schema與 production admission以 `ASTROLOGY_PRODUCTION_ADMISSION_V1.json` + schemas為 machine truth。

ChatGPT local runtime 缺少 approved provider files／`astronomy-engine` 時，local miss 不等於 Astrology deterministic facts unavailable；若 GitHub Connect exact-commit retrieval與 Python execution可用，依 `ASTROLOGY_MATERIALIZATION.md` 先嘗試 verified core materialization。Core materialization只涵蓋 explicit coordinates + IANA timezone 的 natal/transit calculation；`place`／`country` name resolution仍需 admitted `geonamescache` resolver可用或另行 verified resolver transport，不得由模型或 generic web geocoding補造。

## 3. Mode Owners

### Natal

`ASTROLOGY_NATAL.md` 擁有：

- natal input / interpretation routing；
- house / dignity / natal-aspect interpretation policy；
- natal minimum-sufficient synthesis order；
- natal-specific unsupported / uncertainty handling。

Calculation / resolver mechanics不在該檔重複；由 `ASTROLOGY_PROVIDER_ADMISSION_V1.json`、`ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json` 與對應 tools擁有。

### Transit

`ASTROLOGY_TRANSIT.md` 擁有：

- admitted natal baseline → transit interpretation routing；
- exactness / motion / repeated-passage / timing semantics；
- transit minimum-sufficient synthesis order；
- transit-specific unsupported / uncertainty handling。

Transit search mechanics不在該檔重複；由 `ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json` + `tools/astrology_transit_provider.py` 擁有。

若同一問題同時要求 natal baseline + transit，依序讀兩個 mode owner；不得把兩者揉成未標示的混合規則。

## 4. Shared Source / Evidence Policy

Interpretation admission：`ASTROLOGY_PRODUCTION_ADMISSION_V1.json`。

共通原則：

- deterministic geometry / chart fact ≠ semantic meaning；
- exact pair有 admitted claim才可使用 pair-specific meaning；
-只有 general geometry時只解 method/general layer；
- 未 admitted semantic claim → `unsupported_factor`；
- `REFERENCE_ONLY` research module不因可計算出 fact就自動取得 production authority；
- preserve source admission、tradition/historical scope、cautions與 registered conflicts；
- research registry status不得因 production use而被回寫。

Typed selector只做 deterministic evidence selection；不取得 free-text NLU、astrological-meaning、source-admission或 final-prose authority。

## 5. Production Handoff / Output Boundary

Production支援 exact-reference與typed-selector兩條 composition-only path；兩者最後都必須保留：

```text
astrology_reading_run@1.0.0
→ admitted exact facts / claims
→ tools/astrology_interpretation_handoff.py
→ bounded synthesis under ASTROLOGY.md + selected mode owner + CHATGPT_OUTPUT.md
→ tools/astrology_output_guard.py
→ astrology_user_facing_output@1.0.0
```

責任邊界：

- `tools/astrology_orchestrator.py`：request normalization / composition only；
- `tools/astrology_evidence_selector.py`：typed deterministic selection only；
- `tools/astrology_interpretation_handoff.py`：admitted fact/claim provenance packaging only；
- `tools/astrology_output_guard.py`：provenance + Pre-Send draft validation only；
- `tools/astrology_reading_pipeline.py` / `tools/astrology_typed_reading_pipeline.py`：composition only；
- final semantic method authority仍是 `ASTROLOGY.md` + selected mode owner；
- final output contract由 `CHATGPT_OUTPUT.md` 擁有。

現有 schemas / manifests中 `final_method_owner = ASTROLOGY.md` 不因 mode layering而改變。

## 6. Shared Uncertainty / Safety

輸出至少語意區分：

```text
Input-resolution fact
Chart / timing fact
Astrology interpretation
Synthesis
```

若 facts 是 `user_asserted`，必須說明本流程沒有獨立重算。

Astrology不是 medical / legal / financial / safety decision authority；不得把 symbolic timing / interpretation寫成 death、pregnancy、medical diagnosis/outcome、accident、legal outcome、investment result、job loss或 relationship ending等必然結果。

## 7. Unsupported-Factor Rule

```text
unsupported_factor
→ state outside admitted scope
→ identify minimum missing fact/source/provider when useful
→ do not fill from model memory
```

禁止用未 admission research、模型記憶或 provider scope外的自由計算補洞。

## 8. Provenance / Recording

Reading Record若需要保存，至少保留 method/version、reading_mode、question identity、Fact Bundle identity/source、provider/resolver provenance、configuration、used claim refs、unsupported factors、interpretation與 reality updates。

真實 birth/chart資料仍服從 `READING_RECORD.md` storage boundary，不得寫入本公開 Playbook。

## 9. Authority Map

```text
ASTROLOGY.md
→ root production method owner / common invariants / mode routing

ASTROLOGY_NATAL.md
→ natal interpretation-policy owner

ASTROLOGY_TRANSIT.md
→ transit interpretation-policy owner

ASTROLOGY_*_ADMISSION_V1.json + tools/astrology_*.py
→ deterministic implementation / admission truth

CHATGPT_OUTPUT.md
→ final output / Pre-Send owner

references/astrology/**
→ research evidence only unless separately admitted
```

Production v1 admitted reading modes仍只有 `natal` + `transit`；ordinary auto-routing仍為 NO。
