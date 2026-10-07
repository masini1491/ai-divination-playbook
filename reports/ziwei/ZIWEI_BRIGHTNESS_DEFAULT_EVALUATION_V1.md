# Zi Wei Brightness Default Evaluation V1

Authority: **EVALUATION EVIDENCE / NOT PRODUCTION ADMISSION / NOT ROUTING AUTHORITY**

## Question

Evaluate whether the already-admitted optional `brightness_v1` profile should become the default for explicit Zi Wei `natal_baseline` production.

This evaluation does **not** change current production activation, optional-module defaults, claim admission, temporal scope, or interpretation doctrine.

## Evaluated revision

```text
repository: masini1491/ai-divination-playbook
revision: 11432b5cdf75c5a077b9a77444214592794ad8eb
workflow: Validate Playbook #37583962344
handoff artifact: ziwei-deterministic-handoff-11432b5cdf75c5a077b9a77444214592794ad8eb
artifact sha256: f151a20ae4d35bc42bfa6abad3f0f63b1a5779972917258ece62bd81cda87ef6
```

The exact-main handoff artifact was hash-verified before materialization. The bundled Zi Wei runtime was materialized through the repository-provided verifier/materializer and retained the exact `playbook_commit` above.

## Bounded A/B sample

The comparison used synthetic normalized-lunar inputs only. No private or user-identifying birth data was used.

Sample grid:

- lunar years: `1981, 1984, 1987, 1990`
- lunar months: `1, 5, 9`
- lunar day: `15`
- hour branches: `子, 卯, 午, 酉`
- total cases: **48**

For every case:

```text
A = canonical natal request with no optional modules
B = same request + optional_modules=(brightness_v1,)
```

M0, M1 and Sihua remained disabled in both arms. The comparison inspected selected claims, conditional evaluations, natal-synthesis candidate/focus signals, omissions and conflicts.

## Results

Across all 48 cases:

- brightness produced **14 major-star brightness records** per case;
- B added exactly **2 selected claims** in every case:
  - `ZW-B1-TAIYANG-COND-002`
  - `ZW-B2-TAIYIN-COND-002`
- no baseline selected claim was removed from the full selected-claim set;
- eligible-claim count increased by **2** in every case;
- candidate-signal count increased by **2** in every case;
- omission count decreased by **2** in every case;
- conflict count was unchanged in all 48 cases.

The important effect appeared in `natal_synthesis_v1` focus selection:

- focus set changed in **47 / 48 cases (97.9%)**;
- `ZW-B1-TAIYANG-COND-002` entered the focus in **47 / 48** cases;
- `ZW-B2-TAIYIN-COND-002` entered the focus in **45 / 48** cases;
- 45 cases displaced exactly **2** baseline focus signals;
- 2 cases displaced **1** baseline focus signal;
- 1 case displaced none;
- mean displaced baseline focus signals = **1.9167** per case;
- no new non-brightness focus signal was introduced by the B arm.

## Interpretation

The two claims unlocked by brightness alone are currently **dignity-availability meta-conditionals**:

- 太陽: brightness materially modifies interpretation strength/direction;
- 太陰: brightness materially modifies interpretation strength/direction.

They do not themselves encode a value-specific semantic direction for the actual current `廟／旺／得／利／平／不／陷` value.

Because these L4 conditional claims become eligible whenever `fact_available:dignity` exists, current synthesis ranking tends to elevate them above lower-ranked but more chart-specific bounded L5 star×palace signals.

Therefore default-enabling `brightness_v1` **increases deterministic fact coverage but does not currently demonstrate increased natal-synthesis specificity**. In this bounded sample it usually replaces more chart-distinctive focus signals with generic modifier-awareness claims.

## Decision

**Outcome B — retrieval / ordering issue.**

Do **not** promote `brightness_v1` to the default natal module on the current synthesis policy.

Current production behavior remains unchanged:

- `brightness_v1` stays separately admitted and explicit/profile-bound;
- `ziwei.brightness.iztro_v1` remains a named implementation profile, not a universal historical brightness authority;
- no brightness-only doctrine or generic `廟吉陷凶` rule is admitted;
- no temporal scope is widened.

## Follow-up gate

If default-on brightness is reconsidered, first adjust `natal_synthesis_v1` selection/ranking so that generic dignity-availability meta-conditionals do not consume scarce focus slots unless they add value-specific, chart-distinctive semantics.

Then rerun the same bounded A/B matrix and require evidence that:

1. brightness-dependent evidence remains traceable and profile-bound;
2. focus distinctiveness does not regress;
3. generic modifier-awareness claims do not systematically displace stronger contextual signals;
4. conflicts and safety boundaries remain unchanged;
5. no new doctrine is created merely from brightness labels.

This is a synthesis/retrieval follow-up. It does **not** justify reopening the 14×12 star×palace matrix.
