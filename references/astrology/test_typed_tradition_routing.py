#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

from typed_tradition_routing import (
    canonical_tradition_refs_for_claim,
    filter_claims_by_typed_tradition,
    resolve_tradition_request,
    validate_taxonomy,
)


class TypedTraditionRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.taxonomy = json.loads((here / "tradition_taxonomy_example.json").read_text(encoding="utf-8"))

    def test_taxonomy_fixture_valid(self):
        self.assertEqual(validate_taxonomy(self.taxonomy), [])

    def test_named_psychological_school_resolves(self):
        result = resolve_tradition_request(
            {"requested_labels": ["psychological_astrology"]}, self.taxonomy
        )
        self.assertTrue(result["executable"])
        self.assertEqual(result["tradition_resolution_status"], "inferred_from_named_school")
        self.assertEqual(
            result["requested_tradition_contexts"],
            ["school:modern:psychological_astrology"],
        )
        self.assertEqual(result["requested_synthesis_mode"], "synthesis:single_tradition")

    def test_ptolemaic_lineage_resolves(self):
        result = resolve_tradition_request(
            {"requested_labels": ["ptolemaic"]}, self.taxonomy
        )
        self.assertTrue(result["executable"])
        self.assertEqual(
            result["requested_tradition_contexts"],
            ["lineage:hellenistic:ptolemaic"],
        )

    def test_broad_classical_fails_ambiguous(self):
        result = resolve_tradition_request(
            {"requested_labels": ["classical"]}, self.taxonomy
        )
        self.assertFalse(result["executable"])
        self.assertEqual(result["tradition_resolution_status"], "ambiguous")

    def test_broad_modern_fails_as_doctrine_selector(self):
        result = resolve_tradition_request(
            {"requested_labels": ["modern"]}, self.taxonomy
        )
        self.assertFalse(result["executable"])
        self.assertEqual(result["tradition_resolution_status"], "ambiguous")

    def test_unspecified_has_no_silent_default(self):
        result = resolve_tradition_request({"requested_labels": []}, self.taxonomy)
        self.assertFalse(result["executable"])
        self.assertEqual(result["tradition_resolution_status"], "unspecified")
        self.assertEqual(result["reason"], "no_silent_default_tradition")

    def test_non_doctrine_context_cannot_select_tradition(self):
        result = resolve_tradition_request(
            {"requested_labels": ["history_of_astrology"]}, self.taxonomy
        )
        self.assertFalse(result["executable"])
        self.assertEqual(result["tradition_resolution_status"], "unsupported")

    def test_multi_tradition_defaults_parallel_comparison(self):
        result = resolve_tradition_request(
            {"requested_labels": ["ptolemaic", "psychological_astrology"]},
            self.taxonomy,
        )
        self.assertTrue(result["executable"])
        self.assertEqual(result["requested_synthesis_mode"], "synthesis:parallel_comparison")

    def test_explicit_blend_requires_explicit_request_marker(self):
        result = resolve_tradition_request(
            {
                "requested_labels": ["ptolemaic", "psychological_astrology"],
                "requested_synthesis_mode": "synthesis:explicit_blend",
            },
            self.taxonomy,
        )
        self.assertFalse(result["executable"])
        self.assertEqual(result["reason"], "explicit_blend_requires_explicit_request")

    def test_explicit_blend_allowed_when_explicit(self):
        result = resolve_tradition_request(
            {
                "requested_labels": ["ptolemaic", "psychological_astrology"],
                "requested_synthesis_mode": "synthesis:explicit_blend",
                "explicit_blend_requested": True,
            },
            self.taxonomy,
        )
        self.assertTrue(result["executable"])
        self.assertEqual(result["requested_synthesis_mode"], "synthesis:explicit_blend")

    def test_legacy_claim_tags_map_to_typed_context(self):
        claim = {"tradition_tags": ["modern", "psychological_astrology"]}
        self.assertEqual(
            canonical_tradition_refs_for_claim(claim, self.taxonomy),
            {"school:modern:psychological_astrology"},
        )

    def test_ambiguous_legacy_tags_do_not_become_typed_doctrine(self):
        claim = {"tradition_tags": ["classical", "modern"]}
        self.assertEqual(canonical_tradition_refs_for_claim(claim, self.taxonomy), set())

    def test_typed_claim_refs_take_precedence(self):
        claim = {
            "tradition_context_refs": ["lineage:hellenistic:ptolemaic"],
            "tradition_tags": ["modern", "psychological_astrology"],
        }
        self.assertEqual(
            canonical_tradition_refs_for_claim(claim, self.taxonomy),
            {"lineage:hellenistic:ptolemaic"},
        )

    def test_filter_does_not_cross_substitute_on_miss(self):
        claims = [
            {"claim_id": "p", "tradition_tags": ["ptolemaic", "classical"]},
            {"claim_id": "m", "tradition_tags": ["modern", "psychological_astrology"]},
        ]
        selected = filter_claims_by_typed_tradition(
            claims,
            ["school:nonexistent"],
            self.taxonomy,
        )
        self.assertEqual(selected, [])

    def test_filter_selects_only_requested_school(self):
        claims = [
            {"claim_id": "p", "tradition_tags": ["ptolemaic", "classical"]},
            {"claim_id": "m", "tradition_tags": ["modern", "psychological_astrology"]},
        ]
        selected = filter_claims_by_typed_tradition(
            claims,
            ["school:modern:psychological_astrology"],
            self.taxonomy,
        )
        self.assertEqual([claim["claim_id"] for claim in selected], ["m"])


if __name__ == "__main__":
    unittest.main()
