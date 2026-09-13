#!/usr/bin/env python3
"""Compose Astrology Production v1 using explicit typed evidence selectors.

Pipeline:
reading request -> admitted reading run -> deterministic typed evidence selection
-> existing interpretation handoff -> existing provenance/pre-send output guard.

This adapter owns composition only. It does not parse free-text questions into typed
selectors, calculate astronomy outside admitted providers, author astrological meaning,
widen source admission, author final prose, or store private Reading Records.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.astrology_evidence_selector import (
    AstrologyEvidenceSelectionError,
    select_evidence,
    selection_to_interpretation_request,
)
from tools.astrology_interpretation_handoff import InterpretationHandoffError, build_handoff
from tools.astrology_orchestrator import OrchestrationInputError, run_request
from tools.astrology_output_guard import AstrologyOutputGuardError, build_output
from tools.astrology_place_resolver import PlaceResolutionError
from tools.astrology_provider import ProviderInputError
from tools.astrology_transit_provider import TransitProviderInputError

PIPELINE_SCHEMA_NAME = "astrology_typed_reading_pipeline_run"
PIPELINE_SCHEMA_VERSION = "1.0.0"
PIPELINE_ID = "astrology-production-typed-reading-pipeline-v1"
PIPELINE_VERSION = "1.0.0"


class AstrologyTypedReadingPipelineError(ValueError):
    """A stage of the typed Astrology pipeline rejected the request."""


def run_typed_pipeline(
    reading_request: Any,
    typed_selection_request: Any,
    output_draft: Any,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    try:
        reading_run = run_request(reading_request)
        evidence_selection = select_evidence(
            reading_run,
            typed_selection_request,
            repo_root=repo_root,
        )
        interpretation_request = selection_to_interpretation_request(evidence_selection)
        handoff = build_handoff(reading_run, interpretation_request, repo_root=repo_root)
        final_output = build_output(handoff, output_draft)
    except (
        OrchestrationInputError,
        PlaceResolutionError,
        ProviderInputError,
        TransitProviderInputError,
        AstrologyEvidenceSelectionError,
        InterpretationHandoffError,
        AstrologyOutputGuardError,
        RuntimeError,
    ) as exc:
        raise AstrologyTypedReadingPipelineError(str(exc)) from exc

    if reading_run.get("status") != "admitted" or reading_run.get("interpretation_allowed") is not True:
        raise AstrologyTypedReadingPipelineError("reading calculation stage did not produce an admitted run")
    if evidence_selection.get("status") != "selected" or evidence_selection.get("selection_allowed") is not True:
        raise AstrologyTypedReadingPipelineError("typed evidence selection stage was not admitted")
    if handoff.get("status") != "ready_for_bounded_interpretation" or handoff.get("interpretation_allowed") is not True:
        raise AstrologyTypedReadingPipelineError("interpretation handoff stage was not admitted")
    if final_output.get("status") != "ready_for_user" or final_output.get("output_allowed") is not True:
        raise AstrologyTypedReadingPipelineError("output guard stage was not admitted")

    return {
        "schema_name": PIPELINE_SCHEMA_NAME,
        "schema_version": PIPELINE_SCHEMA_VERSION,
        "status": "ready_for_user",
        "output_allowed": True,
        "pipeline": {
            "pipeline_id": PIPELINE_ID,
            "pipeline_version": PIPELINE_VERSION,
            "authority": "composition_only",
            "free_text_query_resolution": False,
            "semantic_selection_authored": False,
            "final_text_authored": False,
            "reading_record_storage": "external_only",
        },
        "stages": {
            "reading_run": reading_run,
            "evidence_selection": evidence_selection,
            "interpretation_handoff": handoff,
            "user_facing_output": final_output,
        },
        "rendered_text": final_output["rendered_text"],
    }


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Astrology Production v1 with explicit typed evidence selectors."
    )
    parser.add_argument("reading_request", type=Path)
    parser.add_argument("typed_selection_request", type=Path)
    parser.add_argument("output_draft", type=Path)
    args = parser.parse_args()
    try:
        result = run_typed_pipeline(
            _load_json(args.reading_request),
            _load_json(args.typed_selection_request),
            _load_json(args.output_draft),
        )
    except (OSError, json.JSONDecodeError, AstrologyTypedReadingPipelineError) as exc:
        print(
            json.dumps(
                {
                    "schema_name": PIPELINE_SCHEMA_NAME,
                    "schema_version": PIPELINE_SCHEMA_VERSION,
                    "status": "rejected",
                    "output_allowed": False,
                    "error": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
