from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.astrology_provider_selector import (
    ASTRONOMY_PROVIDER_ID,
    SWISS_PROVIDER_ID,
    select_natal_provider,
)

ROOT = Path(__file__).resolve().parents[1]
ROUTING = json.loads(
    (ROOT / "ASTROLOGY_PROVIDER_ROUTING_V1.json").read_text(encoding="utf-8")
)
SWISS = json.loads(
    (ROOT / "admissions/astrology/ASTROLOGY_SWISS_PROVIDER_ADMISSION_V1.json").read_text(encoding="utf-8")
)


class AstrologyProviderSelectorTests(unittest.TestCase):
    def test_chatgpt_known_time_selects_host_swiss_when_probe_passes(self):
        result = select_natal_provider(
            host_family="chatgpt",
            reading_mode="natal",
            birth_time_certainty="exact",
            runtime_probe={
                "available": True,
                "version": "2.10.03",
                "sun_effective_backend": "MOSEPH",
                "capability_kind": "PYSWISSEPH_API_EXECUTABLE",
            },
            routing_manifest=ROUTING,
            swiss_admission=SWISS,
        )
        self.assertEqual(SWISS_PROVIDER_ID, result["selected_provider_id"])
        self.assertFalse(result["fallback_used"])
        self.assertEqual("host_preinstalled_only", result["runtime_source"])

    def test_chatgpt_falls_back_when_host_swiss_probe_fails(self):
        result = select_natal_provider(
            host_family="chatgpt",
            reading_mode="natal",
            birth_time_certainty="exact",
            runtime_probe={"available": False},
            routing_manifest=ROUTING,
            swiss_admission=SWISS,
        )
        self.assertEqual(ASTRONOMY_PROVIDER_ID, result["selected_provider_id"])
        self.assertIn("SWISS_RUNTIME_UNAVAILABLE", result["reason_codes"])

    def test_non_chatgpt_never_selects_swiss(self):
        result = select_natal_provider(
            host_family="portable",
            reading_mode="natal",
            birth_time_certainty="exact",
            runtime_probe={"available": True, "version": "2.10.03"},
            routing_manifest=ROUTING,
            swiss_admission=SWISS,
        )
        self.assertEqual(ASTRONOMY_PROVIDER_ID, result["selected_provider_id"])
        self.assertEqual(["PORTABLE_HOST_DEFAULT"], result["reason_codes"])

    def test_unknown_time_and_transit_never_select_swiss(self):
        unknown = select_natal_provider(
            host_family="chatgpt",
            reading_mode="natal",
            birth_time_certainty="unknown",
            runtime_probe={"available": True},
            routing_manifest=ROUTING,
            swiss_admission=SWISS,
        )
        transit = select_natal_provider(
            host_family="chatgpt",
            reading_mode="transit",
            birth_time_certainty="exact",
            runtime_probe={"available": True},
            routing_manifest=ROUTING,
            swiss_admission=SWISS,
        )
        self.assertEqual(ASTRONOMY_PROVIDER_ID, unknown["selected_provider_id"])
        self.assertEqual(ASTRONOMY_PROVIDER_ID, transit["selected_provider_id"])

    def test_invalid_host_boundary_fails_safe_to_astronomy(self):
        broken = copy.deepcopy(SWISS)
        broken["dependency_boundary"]["runtime_source"] = "repo_installed"
        result = select_natal_provider(
            host_family="chatgpt",
            reading_mode="natal",
            birth_time_certainty="exact",
            runtime_probe={"available": True},
            routing_manifest=ROUTING,
            swiss_admission=broken,
        )
        self.assertEqual(ASTRONOMY_PROVIDER_ID, result["selected_provider_id"])
        self.assertIn("SWISS_HOST_BOUNDARY_INVALID", result["reason_codes"])


if __name__ == "__main__":
    unittest.main()
