# Zi Wei Interpretation Fixture Validation v0

Authority：`REFERENCE-ONLY / RESEARCH VALIDATION / NOT PRODUCTION-ROUTABLE`

## Objective

Compare `contextual_composition` with a flat star dictionary using synthetic contrast fixtures. This validates architecture behavior, not scientific predictive validity.

## Rubric

```text
R1 uses material chart conditions
R2 contrast conditions change output
R3 source / tradition identity preserved
R4 registered conflicts are not silently averaged
R5 conditional claims are not promoted to certainty
R6 result has stronger chart-specific differentiation than flat lookup
```

## Fixtures

| Fixture | Material facts | Flat-dictionary pressure | Contextual expectation |
| --- | --- | --- | --- |
| F1 | 紫微命宮 + 左右吉助 | generic 帝星/領導 | consume support modifiers + topology |
| F2 | 紫微命宮 + 無左右 + 煞曜 | repeats F1 positive template | materially differ from F1 |
| F3 | 太陽官祿 + 廟旺 | generic 適合當官 | use Career domain + dignity |
| F4 | 太陽官祿 + 陷 | repeats F3 | dignity alters synthesis |
| F5 | 武曲財帛 + 祿馬 | generic 財星=會賺 | acquisition/mobility context |
| F6 | 武曲財帛 + 破軍/凶曜 | generic positive | retention/volatility context |
| F7 | 巨門夫妻 + favorable modifiers | 婚姻必爭吵 | preserve modifiers; no certainty |
| F8 | 天府福德 + malefic context | invents relief compromise | trigger Tianfu conflict gate |
| F9 | 天相官祿 + favorable supports | universal 位高無權 | preserve authority tension |

## Result

```text
flat_dictionary:
  material failures on contrast/conflict cases
  weak source/conflict handling
  weak-to-medium chart differentiation

contextual_composition:
  uses conditions
  preserves source/tradition identity
  preserves conflicts
  supports bounded chart-specific differentiation
```

## Research decision

```text
contextual_composition = SELECTED RESEARCH ARCHITECTURE
flat_dictionary = REJECTED AS PRIMARY INTERPRETATION MODEL
flat_dictionary = possible low-level index/retrieval aid only
```

User-perceived fit should come from real chart differentiation, not stronger certainty, dramatic predictions or Barnum-style filler.

## Combination-claim boundary

These fixtures test whether contextual composition reacts to material conditions. They do not admit dedicated star×palace L4 claims. Under `STAR_PALACE_COMBINATION_RESEARCH_V0.md`, first-layer star and palace evidence may be jointly synthesized at L5 with provenance preserved; any dedicated combination override still requires explicit source/admission evidence.

## Executable-v0 follow-up

`interpretation_retrieval_v0.py` now provides a bounded research-only selector/composer over the admitted 52 first-layer claims. This does not retroactively make every fixture executable: several fixtures assume brightness, auxiliary, malefic or dedicated contextual claims that remain outside the admitted first-layer corpus.

Executable behavioral validation must therefore treat correct omission/fail-closed behavior as a valid outcome where the fixture dependency is unavailable.

## Limitations

Fixtures are synthetic; no production selector/composer exists. A bounded research-only selector/composer exists, but major-star and twelve-palace first-layer registries remain the admitted claim boundary while later contextual claim families are incomplete.