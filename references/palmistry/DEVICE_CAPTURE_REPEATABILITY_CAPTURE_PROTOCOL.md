# Device / Capture-condition Repeatability — Capture Protocol

Status: **REFERENCE-ONLY / PRE-EXECUTION CAPTURE PROTOCOL / PRIVATE SOURCE IMAGES / NO PRODUCTION AUTHORITY**

## Purpose

本文件把 `DEVICE_CAPTURE_REPEATABILITY_PLAN.md` 轉成可實際收集第一輪 30-image source set 的操作流程。

第一輪只做：

```text
2 devices × 3 sessions × 5 captures = 30 images
```

先建立 controlled baseline；不要在同一輪故意加入模糊、極端暗光、旋轉、濾鏡或其他 perturbation。

## Before capture

### Choose two devices

任選兩個不同實體拍攝裝置，先只命名：

```text
D1
D2
```

可以是兩支手機、手機 + 平板、手機 + webcam等；不需要在檔名放品牌、帳號或 serial。

若要記 device model，只放在 private/local manifest，不需要進 public repo。

### Choose one anatomical hand

整輪固定同一隻手。

在 private manifest記：

```text
anatomical_side = left | right
side_authority = explicit_bodily_self_report
```

之後即使 detector handedness顯示相反，也不改這個欄位，只記 metadata conflict。

### Prepare folders

建議 private/local source tree：

```text
B2_device_repeatability/
  manifest.json
  D1/
    S1/
    S2/
    S3/
  D2/
    S1/
    S2/
    S3/
```

每個 session folder放 5 張原始 still photo。

這個資料夾不得 commit進 public GitHub repo。

## File naming

每張檔案統一：

```text
D1_S1_01.jpg
D1_S1_02.jpg
...
D2_S3_05.jpg
```

若裝置輸出 HEIC / PNG等，不需要先人工轉 JPG；保留原檔格式，analysis pipeline再處理。

不要用聊天軟體轉傳後的壓縮副本取代 camera source file。

## Session definition

S1 / S2 / S3 必須是三次真正重新建立的拍攝狀態。

每個 session結束後：

1. 把手放下；
2. 移開裝置；
3. 中斷至少數分鐘或稍後再做；
4. 下一 session重新拿裝置、重新 framing、重新放手。

目的不是研究時間長短，而是避免把一次 pose的 burst frames誤當 independent reposition captures。

## Baseline capture posture

每張照片盡量做到：

```text
掌面朝鏡頭
接近正面
手指自然張開
手掌完整
手腕底部可見
食指與小指 MCP region可見
無手錶/手環/物件遮掌心
不刻意拉扯或按壓手掌
```

若戒指只在手指且不遮 palm ROI，可保留，但 manifest應記 visible accessory；若會影響掌面則先移除。

## Lighting / background

第一輪 baseline：

```text
ordinary diffuse indoor light
avoid direct flash if possible
avoid strong specular glare
avoid deep shadow across palm
simple contrasting background
```

不要開 beauty filter、portrait blur、skin smoothing或 AI enhancement；若 camera app無法關閉某處理，記在 private note即可。

## Distance

Nominal target：約 `35 cm`。

不需要精密量測到毫米，但兩 device盡量使用同一距離概念，且整個 palm + wrist base都落在 frame內。

不要用 digital zoom。

## Five captures within one device/session

每張之間都重新做一次小幅 reposition：

```text
拍一張
→ 手放鬆 / 稍微移開
→ 重新擺回近似 baseline pose
→ 再拍下一張
```

不要按住快門 burst五張，也不要從同一 video抽五 frame。

## Device order

Session內 D1 / D2順序不建立 scientific authority。

為降低固定順序 confound，可用：

```text
S1: D1 → D2
S2: D2 → D1
S3: D1 → D2
```

如果操作不方便，也可固定順序，但需在 manifest保存 capture order note。

## Front-camera / selfie caution

第一輪若能選，優先使用 rear camera，因為 front-camera preview / stored-file mirroring較容易因 app而不同。

如果某 device只能或刻意使用 front camera，必須記：

```text
camera_role = front
preview_mirrored = true | false | unknown
stored_file_mirror_state = mirrored | not_mirrored | unknown
```

不知道就寫 `unknown`，不要用 detector handedness猜。

## Task-relevant metadata only

Local manifest只需保存：

```text
file_id
relative_file_path
device_id
session_id
capture_index
camera_role
anatomical_side
side_authority
preview_mirrored
stored_file_mirror_state
capture_condition_block = baseline
notes
```

Analysis pipeline稍後自動補：

```text
source_file_sha256
EXIF orientation present/code
normalized pixel SHA
image dimensions
```

不要人工抄 GPS、serial、完整 EXIF dump。

## Minimal manifest example

```json
{
  "study": "B2-device-repeatability-baseline",
  "anatomical_side": "right",
  "side_authority": "explicit_bodily_self_report",
  "devices": {
    "D1": {"camera_role": "rear"},
    "D2": {"camera_role": "rear"}
  },
  "entries": [
    {
      "file_id": "D1-S1-01",
      "relative_file_path": "D1/S1/D1_S1_01.jpg",
      "device_id": "D1",
      "session_id": "S1",
      "capture_index": 1,
      "camera_role": "rear",
      "preview_mirrored": "not_applicable",
      "stored_file_mirror_state": "unknown",
      "capture_condition_block": "baseline",
      "notes": []
    }
  ]
}
```

Example中的 `right`只是格式示例，不是對實際 participant的預設值。

## Capture acceptance checklist

每張先只人工檢查：

- 手掌沒有被 frame切掉主要區域；
- wrist base、index MCP、little MCP看得到；
- 沒有嚴重 motion blur；
- 沒有強反光遮掉 palm ROI；
- 沒有其他手或物件遮掌心；
- 照片確實是同一隻 explicit anatomical hand；
- 不是 duplicate / burst frame。

若拍壞，當場重拍並只保留最後採用的 5 張；不要先看 detector結果再決定哪張留下，避免 model-informed selection bias。

## Freeze discipline after collection

30 張收齊後，正式 inference前先做：

1. manifest completeness check；
2. source-file SHA256；
3. duplicate-byte scan；
4. task-relevant EXIF orientation extraction；
5. source set manifest hash freeze；
6. 再建立 / 執行正式 detector runner。

不要先挑「看起來 detector比較穩」的照片。

## What not to do in the first baseline round

不要混入：

```text
intentional blur
extreme dim light
flash-vs-no-flash experiment
large oblique pose
wet/oily palm
cropped palm
front/rear camera comparison within same device
filters
JPEG recompression experiment
```

那些可以在 baseline完成後各自另開 controlled extension block。

## Privacy / repository boundary

真實手掌照片、source archive、private device manifest不 commit到 public repo。

Public repo只保存：

- protocol；
- code；
- aggregate research metrics；
- non-identifying provenance；
- hash identities needed for reproducibility。

不建立 biometric template或跨樣本 re-identification database。

## Ready-to-run condition

以下成立後才進 runner implementation：

```text
D1/S1 = 5
D1/S2 = 5
D1/S3 = 5
D2/S1 = 5
D2/S2 = 5
D2/S3 = 5
same explicit anatomical hand across all 30
private manifest present
```

完成拍攝後只需要回報「30張與 manifest已準備好」，再由後續流程做 hash / integrity / runner，不需要人工先分析影像。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
