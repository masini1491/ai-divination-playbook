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
    (ROOT / "ASTROLOGY_SWISS_PROVIDER_ADMISSION_V1.json").read_text(
        encoding="utf-8"
    )
)


class AstrologyProviderSelectorTests(unittest.TestCase):
    def test_current_chatgpt_route_falls_back_while_swiss_is_not_admitted(self):
        result = select_natal_provider(
            host_family="chatgpt",
            reading_mode="natal",
            birth_time_certainty="exact",
            runtime_probe={"available": True, "version": "2.10.03"},
            routing_manifest=ROUTING,
            swiss_admission=SWISS,
        )
        self.assertEqual(ASTRONOMY_PROVIDER_ID, result["selected_provider_id"])
        self.assertEqual(SWISS_PROVIDER_ID, result["preferred_provider_id"])
        self.assertTrue(result["fallback_used"])
        self.assertIn("SWISS_PROVIDER_NOT_ADMITTED", result["reason_codes"])
        self.assertIn("SWISS_LICENSE_UNRESOLVED", result["reason_codes"])

    def test_chatgpt_selects_swiss_only_after_all_activation_gates_close(self):
        admitted = copy.deepcopy(SWISS)
        admitted["status"] = "PRODUCTION_ADMITTED"
        admitted["license"]["status"] = "RESOLVED"
        admitted["license"]["selected_mode"] = "SWISS_PROFESSIONAL"
        admitted["implementation"]["status"] = "PRODUCTION_ADMITTED"
        admitted["implementation"]["runtime_owner"] = "tools/astrology_swiss_provider.py"
        result = select_natal_provider(
            host_family="chatgpt",
            reading_mode="natal",
            birth_time_certainty="approximate",
            runtime_probe={"available": True, "version": "2.10.03"},
            routing_manifest=ROUTING,
            swiss_admission=admitted,
        )
        self.assertEqual(SWISS_PROVIDER_ID, result["selected_provider_id"])
        self.assertFalse(result["fallback_used"])
        self.assertEqual("SWISS_PROFESSIONAL", result["license_mode"])

    def test_chatgpt_falls_back_when_swiss_runtime_is_missing(self):
        admitted = copy.deepcopy(SWISS)
        admitted["status"] = "PRODUCTION_ADMITTED"
        admitted["license"]["status"] = "RESOLVED"
        admitted["license"]["selected_mode"] = "SWISS_AGPL"
        admitted["implementation"]["status"] = "PRODUCTION_ADMITTED"
        admitted["implementation"]["runtime_owner"] = "tools/astrology_swiss_provider.py"
        result = select_natal_provider(
            host_family="chatgpt",
            reading_mode="natal",
            birth_time_certainty="exact",
            runtime_probe={"available": False},
            routing_manifest=ROUTING,
            swiss_admission=admitted,
        )
        self.assertEqual(ASTRONOMY_PROVIDER_ID, result["selected_provider_id"])
        self.assertIn("SWISS_RUNTIME_UNAVAILABLE", result["reason_codes"])

    def test_portable_host_keeps_astronomy_default_even_if_swiss_exists(self):
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

    def test_unknown_time_and_transit_remain_portable(self):
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
        self.assertEqual(["UNKNOWN_TIME_PORTABLE_ROUTE"], unknown["reason_codes"])
        self.assertEqual(["TRANSIT_PORTABLE_ROUTE"], transit["reason_codes"])


if __name__ == "__main__":
    unittest.main()
