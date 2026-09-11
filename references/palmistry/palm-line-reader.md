# Source Dossier｜samuelwbarber/palm-line-reader

Status: **REFERENCE-ONLY｜僅供參考**

Repository: `samuelwbarber/palm-line-reader`

Reviewed revision: `bc48939f4deee6d8ff842bfde499396dab9c4830`

License: MIT

## What it is

一個輕量 neural-network palm-line segmentation 專案，主要辨識三大主線：

- heart line
- head line
- life line

README 說明其 browser 版本約 5.5M parameters，fp16 ONNX 約 11 MB，搭配 MediaPipe hand landmarker 做 palm crop / normalization。

## Relevant value

可作為未來 `Palm Observation Fact` 的**影像 observation implementation reference**，尤其是：

- RGB palm image → crop / normalize；
- detector-only right-hand mirroring；
- 4-class segmentation（background + 3 major lines）；
- browser / mobile-friendly ONNX deployment；
- line continuity-oriented training objective；
- held-out palm evaluation。

## Shipped model contract

`models/model_meta.json` 與 `web/palmLines.js` 對 shipped student model 的 inference contract 相對完整：

- input：RGB / NCHW / 512×512 / float32；
- pixels 先除以 255，再用 ImageNet mean / std normalize；
- training / browser inference 都使用 plain resize 到 512×512，**沒有 aspect-ratio letterbox**；
- output：4-class logits；
- argmax over class axis 得到 class-index mask；
- 若需要 confidence，需另外對 logits 做 probability handling，argmax 本身不是 confidence；
- metadata 記錄 `val_fg_dice = 0.8098`；這是 aggregate held-out foreground metric，不是單張照片 accuracy guarantee；
- int8 model upstream 明示 thin-line quality 較差。

Browser segmentation module本身**不負責 hand ROI**：caller 必須提供 reasonably square hand/palm crop；module 會直接把任何 source 拉伸至 512×512。

## Preprocessing reconstruction caveat

`pipeline/hand_preprocess.py` 的檔頭明確說明：原始 preprocessing module 曾只存在 `/home/ubuntu` VM，後來未 recover；目前版本是 reconstruction。

該 reconstruction：

- 使用 MediaPipe Hand Landmarker，`num_hands=1`；
- 以 wrist landmark 0 → middle-finger MCP landmark 9 建立 fingers-up rotation；
- 以 landmarks bounding box + fixed 100 px margin crop；
- 可依 MediaPipe handedness label mirror 至固定方向；
- 程式註解明確警告 MediaPipe handedness convention 假設 mirrored / selfie input，因此其 Left / Right label 不應直接視為 anatomical handedness ground truth。

因此本 Playbook 的 evidence boundary：

```text
shipped model I/O / resize / classes = reproducible technical reference
current reconstructed crop / handedness preprocessing = reference only
```

不得把 reconstruction 冒充原 student model training 時的完整 historical preprocessing contract。

## Authority boundary

本來源只對「如何偵測可見掌紋」提供技術參考；不取得 Palmistry interpretation authority。

作者 README 明確表示 demo fortune reading 是 nonsense，專案重點是 segmentation，而不是證明手相學成立。

同樣地：

```text
heart / head / life model class
≠ 天 / 人 / 地紋
```

model class 只能先保存為 Western tool-local classification。

## Provenance / dataset limitation

README 說明 pseudo-label training source 包含從 Reddit `r/PalmReading` 蒐集的數千張 palm photos，再經 teacher model + human review 產生 labels；source photos 未隨 repo 發布，並明示有 provenance reasons。

因此：

- 不把其 dataset 視為可直接再散布的 training corpus；
- 不因 code 是 MIT 就推定原始 palm photos 也取得相同 reuse rights；
- 若未來真的 reuse model / dataset pipeline，需另做 data provenance / privacy review。

## Adoption

**REFERENCE-ONLY**

目前只保留 observation-layer 技術參考，不把 model、threshold、reconstructed crop 或 training pipeline 納入 canonical Palmistry contract。
