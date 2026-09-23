# Zi Wei Dou Shu Source Reconciliation v1

Authority：`REFERENCE-ONLY / RESEARCH SYNTHESIS`

Status：

```text
CLOSED WITH EXPLICIT IMAGE GAPS
```

本檔保存第一輪 historical/source reconciliation 的 current conclusion。它回答的是「具體 witness 支持哪些 rule、證據到哪一層」，不是決定哪個流派一定正確，也不是 production admission。

## Evidence levels used here

```text
DIRECT / RULE-SPECIFIC TEXT SUPPORT
  = 可把具體 witness identity 與規則文字對上

WITNESS-IDENTIFIED TRANSCRIPTION SUPPORT
  = 實體／館藏 witness identity 已鎖定，但目前規則文字來自可信轉錄，未直接核原頁

EDITORIAL COLLATION CLAIM
  = 校勘者／出版社報告具體異文，但原頁 facsimile 尚未核

IMAGE GAP OPEN
  = 已知道需要哪一件 witness / 哪一頁類型，但公開可驗證 facsimile 尚未取得
```

館藏存在、版本名稱相同、現代 engine 實作一致，都不能自動升級成 image-verified rule evidence。

## Witness matrix

| Witness / family | Rule area | Current evidence | Current reading / implication |
| --- | --- | --- | --- |
| Nanyang-Hall `新鋟希夷陳先生紫微斗數全書` / National Archives of Japan witness | Life / Body | direct rule-specific text support | 寅起正月；命逆生時、身順生時 |
| same | Five-Element Bureau | direct conceptual text support | 命宮干支 → 納音 → 水二／木三／金四／土五／火六局 |
| same | Zi Wei birthday placement | traditional table/verse support | placement outcome source-backed；modern closed-form 是重建 |
| same | Four Transformations | witness-specific transcription research | 庚、壬等與後來 common tables不同；不得稱 universal Quanshu table |
| same | Leap month | witness-specific text research | 閏月按次月處理的 witness rule；不同於 project split-after-15 |
| same | Decadal | direct direction support | 順逆 source-backed；第一限宮描述與 modern/Quanji common 不同 |
| Toyo Bunko `VII-3-157 新刊希夷陳先生紫微斗數全集` | witness identity | cross-catalog verified | 1冊100張；具體 physical witness 已鎖定 |
| same | Four Transformations | witness-identified transcription support | 戊右／庚陰／壬左 family；原頁 image open |
| same | Decadal start age | witness-identified transcription support | 命宮先起局數歲、每十年一宮；原頁 image open |
| Wenguang-Hall early Quanshu family | Four Transformations | editorial collation claim | reported `庚日武同陰`；原頁 image open |
| Zhongzhou modern lineage | Four Transformations | named modern tradition / implementation evidence | 戊陽／庚府／壬府 |
| Project `sihua.default_v1` | Four Transformations | project design decision | 戊右／庚府／壬左；user-perceived-fit objective |

## Rule reconciliation

### Life / Body

Status：`SUBSTANTIALLY CLOSED`

Historical text and multiple independent implementations agree under matched `chart_mode=tian_pan`:

```text
寅起正月
順數至生月
命宮逆數生時
身宮順數生時
```

Di/Ren chart variants remain profile-bound.

### Five-Element Bureau

Status：`SUBSTANTIALLY CLOSED — CONCEPTUAL SOURCE CHAIN`

Traditional semantics are better represented as:

```text
year stem
→ Five-Tiger palace stem
→ Life Palace ganzhi
→ NaYin element
→ bureau number
```

The compact 5×6 tables used by modern engines are deterministic lookup optimizations, not a separate doctrinal authority.

### Zi Wei birthday placement

Status：`SOURCE-BACKED OUTCOME / ALGORITHMIC RECONSTRUCTION`

Traditional tables/verses support birthday-to-ZiWei placement outcomes. Modern engines encode an equivalent quotient/remainder/parity formula.

Do not state that the modern closed-form formula itself is ancient textual wording.

### Decadal

Status：`PROFILE / WITNESS VARIANT`

Common implementation agreement is not enough to call the whole decadal rule universal.

```text
Nanyang witness:
  direction = source-backed
  first palace = adjacent-palace description

Quanji/common lineage:
  first palace = Life Palace
  first start age = bureau number
  direction = yang-male/yin-female forward, otherwise reverse
```

Project baseline therefore uses an explicit identity:

`decadal.quanji_common_v1`

### Leap month

Status：`PROFILE VARIANT`

Nanyang witness research supports a next-month treatment for leap month. Modern implementations expose other policies, including split-after-15.

Project default:

`leap.split_after_15`

is a deliberate modern/project profile choice, not a claim about the Nanyang witness.

### Four Transformations

Status：`VERSIONED VARIANT REGISTRY REQUIRED`

There is no single source-closed “Quanshu table”. Witness and tradition identity must be carried with the transform fact.

Canonical research registry owner：

[`FOUR_TRANSFORMATION_VARIANT_REGISTRY.md`](FOUR_TRANSFORMATION_VARIANT_REGISTRY.md)

## Explicit image gaps

### QUANJI VII-3-157

Known：

- exact Toyo Bunko call mark；
- physical witness identity cross-catalog verified；
- current transcription tradition for Four Transformations and decadal start age.

Missing：

- direct public facsimile of the relevant Four-Transformation rule page；
- direct public facsimile of the relevant decadal rule page.

Disposition：`IMAGE GAP OPEN`

### WENGUANG EARLY QUANSHU

Known：

- early Wenguang-Hall witness family identified through modern facsimile/editorial collation；
- reported variant `庚日武同陰`.

Missing：

- direct public facsimile of the relevant original rule page；
- direct verification of complete 壬干 wording from the same witness.

Disposition：`IMAGE GAP OPEN`

## Reopen triggers

Reopen only when at least one material premise changes：

- a verifiable facsimile page becomes available；
- a new concrete witness with edition/call-mark identity is introduced；
- a transcription can be tied to a stronger primary witness；
- project default objective changes.

Do not reopen merely because another generic teaching page repeats an already-known table.

## Production boundary

This reconciliation closes a research stage only. It does not create a production method, deterministic provider, runtime authority, scientific validity, or ordinary routing permission.
