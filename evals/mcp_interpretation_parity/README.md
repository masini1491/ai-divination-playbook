# MCP vs. direct Repo interpretation parity evaluation

This is a **paired model-output review protocol**, not a new divination engine or a claim that tests ran two LLM paths. All six cases in `cases.json` are synthetic/fixed, with no personal data, live random drawing or private readings. Policy source is the pinned `38898aec...` canonical snapshot; update the fixture source only after separately reviewing the canonical release.

## Recording one real paired run

1. Take a single case (question, contract, facts and rubric). Calculate a SHA-256 of its canonical `json.dumps(case, sort_keys=True, ensure_ascii=False)` representation.
2. In **two separate clean model sessions** with the same model, settings, fixed facts and source revision, instruct one to read the corresponding canonical Playbook owner(s) via GitHub Connect and the other to obtain the same owner(s) through MCP `get_interpretation_policy`. Neither may draw or recast; use supplied fixed facts.
3. Capture the unedited actual response for each route. Record `model_id`, `model_config_id`, `policy_source_commit`, and `fixture_sha256` for both routes.
4. An independent reviewer marks *every* `requirements` item `satisfied=true` iff evidenced in that answer, and every `forbidden` item `satisfied=true` iff the prohibited behavior occurred. Each check must include an `evidence_quote` literally contained in the response; human judgment is required for meaningful assessment.
5. Save `{"schema_version":1,"cases":[{"id":"...","reviewed_by":"...","fixture_sha256":"...","outputs":{"repo":{...},"mcp":{...}}}]}` to an **authorized private evidence location**. Do not commit real conversation records or identifying model responses to the public Playbook.
6. Run `python tools/evaluate_mcp_interpretation_parity.py --cases evals/mcp_interpretation_parity/cases.json --records /private/path/records.json --output /private/path/result.json`.

`PASS` requires all six cases reviewed, two matching pinned execution contexts per case, source-tied quotes, no unmet requirement and no violated prohibition. `FAIL` reports a concrete reviewed violation. `INCONCLUSIVE` means missing/mismatched material evidence; never report it as PASS.

**Limitations:** a check's quote alone does not mechanically prove human semantic judgments are correct; evaluator tests use synthetic controls and do not constitute a completed paired LLM run. Differences in wording are not automatically failures. Actual model-output comparison requires the independently captured responses and a reviewer.
