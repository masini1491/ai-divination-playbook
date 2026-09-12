# Palm Line Anatomical Manual Audit — P001 Sensitivity Note

Status: **REFERENCE-ONLY / POST-HOC OBSERVER QUALITY CAVEAT / SENSITIVITY ANALYSIS**

## Trigger

After the frozen blind manual audit result had been generated, hashed, recorded, and substantively inspected, the observer reported that `P001/S1/01.jpg` was too blurry for confident manual tracing and that parts of the three manual traces were drawn by inference/guess rather than clearly visible crease evidence.

This information was reported **after** model-comparison inspection. It therefore must not be used to edit or replace the frozen annotation artifact, and it must not retroactively change the primary 10-image audit.

## Frozen artifacts remain unchanged

- frozen annotation SHA256: `51c4886e20cb9aee2d660fe1ca39f25b927398261478c013090ab5d611858041`
- frozen comparison-result SHA256: `6f95828b70b388028a46ee1879835d432d9dd695bdbbdd1f2656b6ebf3572284`
- tolerance: `8 px`
- selected sources in primary audit: `10`
- no re-annotation is performed
- no model rerun is performed for this sensitivity note

The primary audit remains the full ten-image result.

## Why P001 is a manual-reference quality caveat

`P001/S1/01.jpg` was the weakest case for all three correct-class harmonic-coverage values:

- `heart_line`: `0.37837837837837834`
- `head_line`: `0.6519823788546255`
- `life_line`: `0.5041257751086373`

However, the observer's post-hoc report means those low values cannot be attributed purely to model error. They combine at least two unresolved factors:

1. model/reference disagreement;
2. uncertainty in the manually drawn reference itself because the image was blurry.

Accordingly, P001 should not be described as a clean model-failure example.

## Post-hoc leave-P001-out sensitivity summary

The table below is a descriptive sensitivity calculation only. The leave-P001-out mean is computed from the already frozen 10-image mean and the frozen P001 value:

`mean_9 = (10 * mean_10 - P001) / 9`

| class | primary mean harmonic coverage, n=10 | P001 harmonic coverage | leave-P001-out mean, n=9 | wrong-class exceeds correct |
|---|---:|---:|---:|---:|
| `heart_line` | 0.9036458631 | 0.3783783784 | **0.9620089169** | 0/10 primary; 0/9 leave-P001-out |
| `head_line` | 0.9137675861 | 0.6519823789 | **0.9428548314** | 0/10 primary; 0/9 leave-P001-out |
| `life_line` | 0.7906154111 | 0.5041257751 | **0.8224475929** | 0/10 primary; 0/9 leave-P001-out |

P001 itself had no wrong-class win for any of the three classes, so removing it does not change the qualitative class-specificity result: the correct shipped class still exceeds every wrong class for every retained manual trace.

## Interpretation

The primary ten-image audit and the leave-P001-out sensitivity analysis point in the same direction:

- class-specific spatial agreement is supported in this bounded sample;
- `heart_line` and `head_line` are especially strong among the nine images not affected by this observer-reported P001 blur caveat;
- `life_line` remains weaker than the other two classes but still retains substantial correct-class agreement;
- P001's low coverage should be treated as **reference-quality confounded**, not as pure model failure.

The leave-P001-out result is not a replacement endpoint and is not a new preregistered audit. It is explicitly post-hoc and exists only to test whether the main qualitative conclusion depends on the single observer-reported low-confidence image. It does not.

## Evidence boundary

This note does **not** establish anatomical ground truth, inter-observer reproducibility, cross-dataset generalization, production readiness, a production cutoff, or any palmistry interpretation claim. The palm-line work remains `REFERENCE-ONLY / Cold / NOT PRODUCTION-ROUTABLE`.