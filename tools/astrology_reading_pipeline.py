#!/usr/bin/env python3
"""Compose the complete admitted Astrology Production v1 reading path.

Pipeline:
reading request -> deterministic calculation/runtime gates -> interpretation
handoff -> provenance/pre-send output guard.

The pipeline owns composition only. It does not calculate astronomy outside the
existing providers, choose interpretation evidence, author final prose, or store
private Reading Records.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.astrology_interpretation_handoff import InterpretationHandoffError, build_handoff
from tools.astrology_orchestrator import OrchestrationInputError, run_request
from tools.astrology_output_guard import AstrologyOutputGuardError, build_output
from tools.astrology_place_resolver import PlaceResolutionError
from tools.astrology_provider import ProviderInputError
from tools.astrology_transit_provider import TransitProviderInputError

PIPELINE_SCHEMA_NAME = "astrology_reading_pipeline_run"
PIPELINE_SCHEMA_VERSION = "1.0.0"
PIPELINE_ID = "astrology-production-reading-pipeline-v1"
PIPELINE_VERSION = "1.0.0"


class AstrologyReadingPipelineError(ValueError):
    """A stage of the admitted Astrology reading pipeline rejected the request."""


def run_pipeline(
    reading_request: Any,
    interpretation_request: Any,
    output_draft: Any,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    try:
        reading_run = run_request(reading_request)
        handoff = build_handoff(reading_run, interpretation_request, repo_root=repo_root)
        final_output = build_output(handoff, output_draft)
    except (
        OrchestrationInputError,
        PlaceResolutionError,
        ProviderInputError,
        TransitProviderInputError,
        InterpretationHandoffError,
        AstrologyOutputGuardError,
        RuntimeError,
    ) as exc:
        raise AstrologyReadingPipelineError(str(exc)) from exc

    if reading_run.get("status") != "admitted" or reading_run.get("interpretation_allowed") is not True:
        raise AstrologyReadingPipelineError("reading calculation stage did not produce an admitted run")
    if handoff.get("status") != "ready_for_bounded_interpretation" or handoff.get("interpretation_allowed") is not True:
        raise AstrologyReadingPipelineError("interpretation handoff stage was not admitted")
    if final_output.get("status") != "ready_for_user" or final_output.get("output_allowed") is not True:
        raise AstrologyReadingPipelineError("output guard stage was not admitted")

    return {
        "schema_name": PIPELINE_SCHEMA_NAME,
        "schema_version": PIPELINE_SCHEMA_VERSION,
        "status": "ready_for_user",
        "output_allowed": True,
        "pipeline": {
            "pipeline_id": PIPELINE_ID,
            "pipeline_version": PIPELINE_VERSION,
            "authority": "composition_only",
            "semantic_selection_authored": False,
            "final_text_authored": False,
            "reading_record_storage": "external_only",
        },
        "stages": {
            "reading_run": reading_run,
            "interpretation_handoff": handoff,
            "user_facing_output": final_output,
        },
        "rendered_text": final_output["rendered_text"],
    }


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the complete Astrology Production v1 request-to-user-output pipeline."
    )
    parser.add_argument("reading_request", type=Path)
    parser.add_argument("interpretation_request", type=Path)
    parser.add_argument("output_draft", type=Path)
    args = parser.parse_args()
    try:
        result = run_pipeline(
            _load_json(args.reading_request),
            _load_json(args.interpretation_request),
            _load_json(args.output_draft),
        )
    except (OSError, json.JSONDecodeError, AstrologyReadingPipelineError) as exc:
        result = {
            "schema_name": PIPELINE_SCHEMA_NAME,
            "schema_version": PIPELINE_SCHEMA_VERSION,
            "status": "rejected",
            "output_allowed": False,
            "error": str(exc),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
