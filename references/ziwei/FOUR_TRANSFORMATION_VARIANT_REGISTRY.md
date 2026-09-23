# Four Transformation Variant Registry｜四化版本登錄

Authority：`REFERENCE-ONLY / RESEARCH EVIDENCE`

本檔只登錄 Four Transformations / 四化的 witness、tradition、implementation 與 project-profile variants。它不宣告「哪一表唯一正統」。

Order：

```text
祿 → 權 → 科 → 忌
```

## Registry

### QUANSHU-NANYANG

Current research reading：

```text
戊：貪狼 / 太陰 / 右弼 / 天機
庚：太陽 / 武曲 / 天同 / 天相
壬：天梁 / 紫微 / 天府 / 武曲
```

Evidence：

```text
witness = Nanyang-Hall Quanshu / National Archives of Japan identified copy
level = witness-specific transcription / rule-specific source research
image_verification = not universally claimed for every glyph in this registry
```

Do not normalize this to later Taiwan/common tables.

### QUANSHU-WENGUANG-EARLY

Current bounded evidence：

```text
庚：太陽 / 武曲 / 天同 / 太陰
```

Evidence：

```text
level = EDITORIAL COLLATION CLAIM
reported_source_family = early Wenguang-Hall woodblock witnesses
facsimile_rule_page = IMAGE GAP OPEN
complete_wu_geng_ren_table = NOT CLOSED
```

Do not infer missing stems from another witness.

### QUANSHU-LATE-PRINT

Known late-print / transcription family may show：

```text
庚：太陽 / 武曲 / 太陰 / 天同
```

Use only when the specific late-print witness is identified. Do not silently collapse it into Wenguang or Nanyang.

### QUANJI-COMMON

Current research table：

```text
戊：貪狼 / 太陰 / 右弼 / 天機
庚：太陽 / 武曲 / 太陰 / 天同
壬：天梁 / 紫微 / 左輔 / 武曲
```

Shorthand：

`戊右／庚陰／壬左`

Evidence：

```text
witness family = Xin-kan Xi-yi Chen Xiansheng Ziwei Doushu Quanji
identified physical witness = Toyo Bunko VII-3-157
rule-text level = WITNESS-IDENTIFIED TRANSCRIPTION SUPPORT
facsimile rule page = IMAGE GAP OPEN
modern usage = common Taiwan / common implementation family
```

### ZHONGZHOU-MODERN

Current research table：

```text
戊：貪狼 / 太陰 / 太陽 / 天機
庚：太陽 / 武曲 / 天府 / 天同
壬：天梁 / 紫微 / 天府 / 武曲
```

Shorthand：

`戊陽／庚府／壬府`

Evidence：

```text
authority = named modern tradition / implementation comparator
historical_witness_uniqueness = not claimed
```

### PROJECT-DEFAULT-V1

Canonical research identity：

`sihua.default_v1`

Table：

```text
戊：貪狼 / 太陰 / 右弼 / 天機
庚：太陽 / 武曲 / 天府 / 天同
壬：天梁 / 紫微 / 左輔 / 武曲
```

Shorthand：

`戊右／庚府／壬左`

Selection metadata：

```text
selection_basis = user_perceived_fit_research
tarot_design_review = supportive
scientific_validity = unestablished
historical_uniqueness = false
named_school_identity = none
production_admitted = false
```

This is a project-level component choice. It must never be relabeled as Quanshu, Quanji, Zhongzhou, ancient-standard, or objectively-most-accurate without new evidence.

## Comparison matrix

| Identity | 戊科 | 庚科 | 壬科 | Evidence role |
| --- | --- | --- | --- | --- |
| QUANSHU-NANYANG | 右弼 | 天同 | 天府 | historical witness research |
| QUANSHU-WENGUANG-EARLY | unresolved | 天同 | unresolved | editorial collation only |
| QUANSHU-LATE-PRINT | unresolved | 太陰 | unresolved | specific late-print witness required |
| QUANJI-COMMON | 右弼 | 太陰 | 左輔 | witness-identified transcription + modern common |
| ZHONGZHOU-MODERN | 太陽 | 天府 | 天府 | named modern tradition |
| PROJECT-DEFAULT-V1 | 右弼 | 天府 | 左輔 | project user-perceived-fit candidate |

## Fact provenance requirement

A future Four-Transformation deterministic fact should carry at least：

```text
year_stem
transform_kind
star
sihua_profile_id
profile_revision
source / evidence provenance
engine / revision
```

A bare fact such as：

`庚年化科 = X`

without profile identity is insufficient.

## Update rule

- New website repetition does not create a new variant.
- A new variant requires a concrete witness, named tradition, independent implementation profile, or explicit project decision.
- Do not majority-vote historical witnesses.
- When a facsimile closes an image gap, update only that witness entry and downstream synthesis that materially depends on it.
