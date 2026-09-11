# Multi-hand Fixture Screen｜多手掌 Fixture 篩選

Status: **REFERENCE-ONLY / BOUNDED SCREEN COMPLETE｜僅供參考／有界篩選完成**

Purpose: find a public/free-licensed image for which the pinned MediaPipe Hand Landmarker baseline actually returns **two or more hand candidates**, so the scene-local candidate-association branch in `mediapipe_repeatability_runner.py` can be exercised with real detector output.

This screen does **not** change detector thresholds to manufacture a passing fixture. It uses the same research baseline as the Case A/B work:

```text
MediaPipe 1.0.1
Hand Landmarker float16/1
model SHA256 fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
num_hands = 4
min_hand_detection_confidence = 0.5
min_hand_presence_confidence = 0.5
min_tracking_confidence = 0.5
max working dimension = 1600 px
```

Images were downloaded only into ephemeral GitHub Actions runners. Repository history keeps source page/license/checksum and detector outputs, not the photographs or raw EXIF.

## Screened fixtures

| Fixture | Visual scene | License | Source SHA256 | Baseline candidates | Detector note |
|---|---|---|---|---:|---|
| `Mehndi hands.jpg` | two palms | CC BY-SA 2.0 | `77efb99086af38ba14946a33435e605ba0428cc9ac0d6e30c598c3e8f8cfb467` | 0 | no hand candidate returned |
| `25.12.2018 Vierfingerfurche, beidseitig.JPG` | bilateral palms | CC BY-SA 4.0 | `ea27870698d8615d98c13b5130bc9d80a78129f25e02f15524ea05e414d04da2` | 1 | `Left`, handedness score ≈0.9059 |
| `Givinghandsandredpushpin.jpg` | two open palms | CC BY 2.0 | `98e7790867bdaaad490c58f18773cd0f026c918b5229e9d8117242ac34d55dcc` | 1 | `Left`, handedness score ≈0.8284 |
| `Three open palms placed together each decorated with beautiful henna.jpg` | three open palms | CC BY-SA 4.0 | `a8889762f9f7ace64b225765b820c16e23cae930905f8f6fed2f765cc84fbbba` | 0 | no hand candidate returned |

The first attempt used Wikimedia `Special:Redirect/file/...` and hit HTTP 429. That transport failure was corrected by using direct Commons file URLs / Commons API resolution; it is not counted as detector evidence.

Relevant successful screening runs:

```text
34613331865  — Mehndi hands + bilateral palmar crease
34613479425  — Givinghandsandredpushpin
34613728619  — three open palms / henna
```

## Privacy boundary

One screened source exposes camera-location metadata on its public source page. This research intentionally does **not** collect, reproduce, store, or use those location values. Only the source identity, license, checksum, image dimensions needed for reproducibility, and detector outputs are retained.

## Finding

The bounded screen produced candidate counts:

```text
0 / 1 / 1 / 0
```

Therefore:

```text
visually multiple hands
!=
pinned detector returns multiple candidates
```

The existing scene-local matching algorithm remains executable research code, but the branch that compares best-vs-second-best candidate distance has still not been exercised by real baseline output.

## Evidence interpretation

This negative result is useful for the future quality gate:

1. A scene description such as “two palms visible” cannot be used as evidence that multiple detector candidates exist.
2. Target-selection logic must consume actual detector candidate sets, not infer them from human-visible hand count.
3. A fixture must be admitted by measured baseline candidate count before it is used to claim multi-candidate association validation.
4. Lowering detector confidence thresholds solely to force a fixture across the `>=2` boundary would change the experiment and is not justified by current evidence.
5. Failure to obtain multiple candidates is itself a valid `not_observable / unresolved` research outcome; it is not a reason to invent target identity.

## Stop decision

The screen stops here under the bounded-discovery / evidence-gap rule. Four public fixtures with 2–3 visually apparent hands were enough to establish that casual Commons-image discovery is not a reliable way to obtain a deterministic multi-candidate fixture for this pinned detector.

The next research node should **not** be an open-ended image search. Prefer one of these evidence-controlled paths:

```text
A. a purpose-built/public fixture set already known to produce >=2 MediaPipe candidates;
B. a small consented capture specifically constructed for two fully visible, separated hands;
C. an upstream MediaPipe test/example fixture with reproducible multi-hand output, if licensing/provenance are suitable.
```

Any future fixture must keep the detector/runtime/model identity fixed and record the actual baseline candidate count before transform testing begins.

## Adoption decision

No production threshold, router, `PALMISTRY.md`, or production method set changes are authorized by this screen.

Palmistry remains:

**REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**
