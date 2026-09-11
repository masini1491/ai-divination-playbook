# Palm Observation Schema｜Real-photo Validation Pass

Status: **REFERENCE-ONLY / DRAFT VALIDATION｜僅供參考／草案驗證**

Reviewed target baseline: `masini1491/ai-divination-playbook@91eeb9423febb486aaa558c953bf159b835d0c27`

本檔用公開、可追溯的真實手掌照片對 `OBSERVATION_SCHEMA_DRAFT.md` 做第一輪 field-coverage / fail-closed 檢查。目的不是替照片做手相解讀，而是確認 schema 是否能誠實描述「看得到什麼、看不到什麼、何時不能解讀」。

本輪**不把外部照片複製進 repository**；只保存 source page、license、case purpose 與 observation-level conclusion。

## Validation set

### Case A — single, open, near-frontal palm

Source: Wikimedia Commons — `Right Hand Palm.png`

URL: https://commons.wikimedia.org/wiki/File:Right_Hand_Palm.png

License: CC BY-SA 4.0

Source description: fully opened right palm，能看到 hand shape、skin texture 與 palm lines；原圖 2553 × 4011。

Observed schema behavior:

- 單手 target 無歧義；
- `hand_side=right`、`view=palm` 可可靠建立；
- palm / finger outline 與主要 crease 具足夠可見度，可進 geometry observation；
- 細小 minor creases 的完整 segmentation 仍不應僅憑肉眼宣稱 deterministic；
- 即使背景與曝光看起來乾淨，也沒有 color calibration evidence，因此 `color_reliable` 不應因「看起來正常」自動變成 `true`。

Result: **geometry-sufficient reference case**。

### Case B — two palms in one frame

Source: Wikimedia Commons — `Open Palm of the Left Hand, Fingers.jpg`

URL: https://commons.wikimedia.org/wiki/File:Open_Palm_of_the_Left_Hand,_Fingers.jpg

License: CC BY-SA 4.0

Source description: both palms open，focus on the left；原圖 4032 × 3024。

Schema gap exposed:

原 draft 只有單一：

```text
image.hand_side
image.view
```

這無法表示：

- 一張圖有幾隻手；
- 哪一隻是 analysis target；
- 非 target hand 是否形成 occlusion / landmark interference；
- target selection confidence。

Decision:

```text
single-hand envelope → scene + hands[] + target_hand_id
```

Result: **multi-hand target-selection requirement confirmed**。

### Case C — accessory on a visible hand

Source: Wikimedia Commons — `Palm, fingers.jpg`

URL: https://commons.wikimedia.org/wiki/File:Palm,_fingers.jpg

License: CC BY-SA 4.0

Source description: left palm and fingers clearly visible，fourth finger has a ring；原圖 3840 × 5760。

Schema gap exposed:

單一 `occlusion` 不足以分辨：

- hand / finger 自己互相遮擋；
- 他人手部遮擋；
- ring / watch / bracelet 等 accessory；
- accessory 只影響 finger morphology，還是已影響 palm-line ROI。

Decision: per-hand 增加 `occluders[]` 與 `accessory_occlusion`，並保存 affected region；accessory 本身不取得 palmistry interpretation authority。

Result: **localized-occlusion requirement confirmed**。

### Case D — low-light / metadata-rich mobile photo

Source: Wikimedia Commons — `A Hand.jpg`

URL: https://commons.wikimedia.org/wiki/File:A_Hand.jpg

License: CC BY-SA 4.0

Relevant source metadata includes high ISO、negative brightness value、auto white balance，且 source page 公開了 camera-location metadata。

Schema gaps exposed:

1. `quality.overall` 太粗：一張照片可能仍能做 geometry，但不能可靠做掌色；
2. auto white balance / uncontrolled lighting 不足以支撐傳統掌色 rule；
3. raw EXIF 可能包含 GPS、device / capture metadata，Palmistry schema 不需要保存這些資訊。

Decision:

- quality 拆成 `geometry / line_detail / surface_detail / color` 等 task-specific gates；
- `color_reliable` 預設不因一般照片而成立；
- provenance 只留最低必要 source identity / license；**不保存 raw EXIF、GPS、camera serial 等無關 metadata**。

Result: **task-specific quality + metadata-minimization requirement confirmed**。

### Case E — palm-up but manipulated / occluded scene

Source: Wikimedia Commons — `Massage-hand-4.jpg`

URL: https://commons.wikimedia.org/wiki/File:Massage-hand-4.jpg

License: CC BY-SA 3.0

Source description: a palm faces upward while another person massages it with baby oil。

Schema behavior:

- palm orientation alone不足以代表可用；
- multiple hands introduce target ambiguity / occlusion；
- pressure from another hand may deform palm geometry；
- oil changes glare / apparent color / surface appearance；
- this can be `partial` for coarse anatomy while `insufficient` for color and fine crease interpretation。

Result: **pose / manipulation / surface-state fail-closed requirement confirmed**。

## Cross-case findings

### 1. One global quality flag is insufficient

第一版 `quality.overall` 容易把不同 observation capability 混在一起。

需要分開：

```text
geometry quality
line-detail quality
surface-detail quality
color quality
```

一張圖可以：

```text
geometry = sufficient
line_detail = partial
color = insufficient
```

### 2. Hand identity is scene-local, not person identity

多手圖片需要 `hand-001 / hand-002` 等 scene-local ID，但這些 ID 只用於同一張圖裡的 geometry association。

不得把它用於：

- biometric identity；
- 跨照片 re-identification；
- user identity database。

### 3. Target selection is a gate

如果一張圖有多隻手而使用者沒有指定、模型也無法可靠選定 target：

```text
target_hand_id = null
selection_state = ambiguous
interpretation_allowed = false
```

### 4. Color is a separate modality-quality problem

傳統來源會使用掌色，但一般手機照片的：

- white balance
- exposure
- ambient light
- skin reflection
- oil / moisture
- camera processing

都可能改變 apparent color。

所以 `color_reliable=true` 需要比「照片清楚」更高的 evidence；普通使用者照片預設應是 `unknown` 或 `false`。

### 5. Metadata minimization is required

Palmistry 不需要 GPS / camera serial / exact capture location。即使來源檔公開包含這些資料，也不把它們帶入 observation fact。

最低原則：

```text
source image identity
+ source / license when applicable
+ only task-relevant capture notes
```

## Schema changes justified by this pass

`OBSERVATION_SCHEMA_DRAFT.md` 應增加／調整：

- `scene.hand_count`
- `scene.target_hand_id`
- `hands[]`
- per-hand `selection_confidence`
- per-hand pose / foreshortening
- task-specific quality gates
- `occluders[]`
- `accessory_occlusion`
- manipulation / surface-state notes
- metadata-minimization rule

## What this pass does NOT validate

仍未完成：

- deterministic landmark / ROI normalization；
- pixel-to-normalized-coordinate implementation；
- CV segmentation accuracy；
- branch / island / star / named-pattern detector performance；
- source-specific Bagua / palace projection geometry；
- repeatability across camera devices；
- behavioral regression for production routing。

因此本輪只把 schema 從「純架構推導」提升為「經代表性真實照片 field-coverage 檢查的 draft」，**仍不是 production contract**。
