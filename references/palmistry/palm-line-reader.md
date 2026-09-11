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
- right-hand mirroring normalization；
- 4-class segmentation（background + 3 major lines）；
- browser / mobile-friendly ONNX deployment；
- line continuity-oriented training objective；
- held-out palm evaluation。

## Authority boundary

本來源只對「如何偵測可見掌紋」提供技術參考；不取得 Palmistry interpretation authority。

作者 README 明確表示 demo fortune reading 是 nonsense，專案重點是 segmentation，而不是證明手相學成立。

## Provenance / dataset limitation

README 說明 pseudo-label training source 包含從 Reddit `r/PalmReading` 蒐集的數千張 palm photos，再經 teacher model + human review 產生 labels；source photos 未隨 repo 發布，並明示有 provenance reasons。

因此：

- 不把其 dataset 視為可直接再散布的 training corpus；
- 不因 code 是 MIT 就推定原始 palm photos 也取得相同 reuse rights；
- 若未來真的 reuse model / dataset pipeline，需另做 data provenance / privacy review。

## Adoption

**REFERENCE-ONLY**

目前只保留 observation-layer 技術參考，不把 model、threshold 或 training pipeline 納入 canonical Palmistry contract。
