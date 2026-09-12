# Palm Line Anatomical Manual Audit — Interpretation

Status: **REFERENCE-ONLY / SINGLE-OBSERVER BLIND MANUAL ANATOMICAL AUDIT / BOUNDED INTERPRETATION**

## Frozen provenance

- annotation SHA256: `51c4886e20cb9aee2d660fe1ca39f25b927398261478c013090ab5d611858041`
- result JSON SHA256: `6f95828b70b388028a46ee1879835d432d9dd695bdbbdd1f2656b6ebf3572284`
- selected sources: `10`
- classes: `heart_line`, `head_line`, `life_line`
- tolerance: `8 px`
- all 30 manual class traces were `observable`
- no model overlay was inspected before the result artifact was frozen

## Aggregate observations

### `heart_line`

- harmonic coverage mean: `0.9036458631`
- median: `0.9735923680`
- p10: `0.7884451253`
- min: `0.3783783784`
- max: `1.0`
- wrong-class exceeds correct count: `0 / 10`
- median model→reference distance: `2.1969 px`
- median reference→model distance: `0.0 px`

### `head_line`

- harmonic coverage mean: `0.9137675861`
- median: `0.9572269111`
- p10: `0.7259899438`
- min: `0.6519823789`
- max: `1.0`
- wrong-class exceeds correct count: `0 / 10`
- median model→reference distance: `2.49845 px`
- median reference→model distance: `0.0 px`

### `life_line`

- harmonic coverage mean: `0.7906154111`
- median: `0.8158573054`
- p10: `0.7242934084`
- min: `0.5041257751`
- max: `0.9010927372`
- wrong-class exceeds correct count: `0 / 10`
- median model→reference distance: `2.49845 px`
- median reference→model distance: `0.0 px`

## Per-image pattern

`P001/S1/01.jpg` is the dominant low-agreement case across all three classes:

- heart: correct harmonic `0.3784`, reference-on-model `0.2333`, median reference→model `27.68 px`
- head: correct harmonic `0.6520`, reference-on-model `0.4837`, median reference→model `9.99 px`
- life: correct harmonic `0.5041`, reference-on-model `0.3491`, median reference→model `18.78 px`

For P001 the model-on-reference coverage remains high (`1.0`, `1.0`, `0.9067`), while reference-on-model coverage is much lower. Under this metric geometry, that pattern is consistent with model regions lying near only part of the manually traced line rather than the model being broadly displaced to another class.

Outside P001, heart/head are generally high-agreement. Life remains weaker and shows some overlap with `head_line` on several images, with the largest recorded best-wrong harmonic values approximately `0.254` (P003), `0.253` (P008), and `0.203` (P005), but the correct life-line class still exceeds the wrong classes on all ten images.

## Bounded interpretation

Within this ten-image, single-observer, 8-px-tolerance audit, the result is **not consistent with a purely generic crease detector that ignores shipped class identity**. The strongest evidence is:

1. correct-class harmonic coverage is high for heart/head and moderate-to-high for life;
2. `wrong_class_exceeds_correct_count = 0` for all three classes;
3. wrong-class harmonic coverage is usually zero or materially below the correct class;
4. the lower-performing life-line class is still class-aligned across all ten selected images.

Accordingly, this bounded audit supports the narrower claim that the shipped three-class model is detecting spatial structures that align with the operator-labeled tool-local `heart_line`, `head_line`, and `life_line` classes on these selected MOHI images.

It does **not** establish anatomical truth in a medical sense, palmistry validity, generalization beyond these images, inter-observer agreement, production suitability, or a production cutoff.

## Important limitations

- only 10 selected MOHI images were manually traced;
- one observer supplied the manual references;
- simplified UI exported only `observable` or `not_observable`; no `uncertain` cases were emitted;
- manual traces are sparse centerline polylines, while model output is a region mask;
- the 8 px tolerance is a frozen research comparison tolerance, not a production acceptance threshold;
- P001 shows a systematic low-coverage failure pattern that requires visual overlay inspection before attributing cause;
- no third-party dataset image should be committed to this repository.

## Next evidence step

Inspect the already-frozen overlays, prioritizing:

1. P001 for all three classes;
2. life-line cases with largest wrong-class overlap (`P003`, `P005`, `P008`);
3. one high-agreement heart/head case as a qualitative control.

Record visual observations separately from interpretation. Do not change annotation traces, tolerance, class labels, or model outputs after seeing overlays.