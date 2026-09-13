from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AstrologyProductionContractTests(unittest.TestCase):
    def test_admission_manifest_is_bounded_and_not_auto_routed(self):
        data = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("astrology_production_admission", data["schema_name"])
        self.assertEqual("1.0.0", data["schema_version"])
        self.assertEqual("PRODUCTION_ADMITTED", data["status"])
        self.assertEqual("explicit_user_request_only", data["activation"])
        self.assertFalse(data["ordinary_auto_routing"])
        self.assertTrue(data["built_in_ephemeris_provider"])
        self.assertFalse(data["admission_decision"]["scientific_predictive_validity_claimed"])

    def test_manifest_admits_natal_provider_but_not_transit_search_provider(self):
        data = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        provider = data["natal_provider"]
        self.assertEqual("astronomy-engine-natal-v1", provider["provider_id"])
        self.assertTrue(provider["raw_birth_data_supported"])
        self.assertTrue(provider["requires_iana_timezone"])
        self.assertIn("provider_transit_event_search", data["unsupported_scopes"])

    def test_manifest_admits_natal_and_transit_interpretation_only(self):
        data = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual({"natal", "transit"}, set(data["reading_modes"]))
        self.assertIn("synastry", data["unsupported_scopes"])
        self.assertIn("raw_birth_data_model_calculation", data["unsupported_scopes"])

    def test_provider_admission_manifest_is_pinned_and_bounded(self):
        data = json.loads((ROOT / "ASTROLOGY_PROVIDER_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("astrology_provider_admission", data["schema_name"])
        self.assertEqual("PRODUCTION_ADMITTED", data["status"])
        self.assertEqual(["natal"], data["scope"])
        self.assertEqual("astronomy-engine", data["dependency"]["package"])
        self.assertEqual("2.1.19", data["dependency"]["version"])
        self.assertEqual("MIT", data["dependency"]["license"])
        self.assertEqual("fail_closed", data["calculation_policy"]["dst_ambiguous_wall_time"])
        self.assertIn("transit event search".replace(" ", "_"), [x.replace("-", "_").replace(" ", "_") for x in data["not_admitted"]])

    def test_manifest_keeps_reference_only_pair_registry_qualified(self):
        data = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertIn("high-value-planet-aspects-research-v1", data["qualified_only_registries"])
        self.assertEqual(
            "not_admitted_until_claim_sources_are_independently_admitted",
            data["qualified_registry_policy"]["production_pair_specific_meaning"],
        )

    def test_method_router_requires_explicit_astrology_override(self):
        text = (ROOT / "METHOD_ROUTING.md").read_text(encoding="utf-8")
        self.assertIn("Astrology（explicit-request only；不參與 ordinary auto-routing）", text)
        self.assertIn("Astrology 不在這個 ordinary auto-selection tree", text)
        self.assertIn("用占星／用星盤／看本命盤／看行運", text)

    def test_chat_init_routes_production_astrology_to_astrology_owner(self):
        text = (ROOT / "CHAT_INIT.md").read_text(encoding="utf-8")
        self.assertIn("明確指定 production Astrology", text)
        self.assertIn("直接讀 `ASTROLOGY.md`", text)
        self.assertIn("raw birth data 不授權模型自行手算", text)

    def test_research_router_keeps_astrology_research_separate(self):
        text = (ROOT / "RESEARCH_ROUTING.md").read_text(encoding="utf-8")
        self.assertIn("Production owner：[`ASTROLOGY.md`](ASTROLOGY.md)", text)
        self.assertIn("Astrology production reading 不屬於這個 gate", text)
        self.assertIn("不因 production v1 已 admission 就回頭改寫成 production source of truth", text)

    def test_machine_index_exposes_method_astrology(self):
        data = json.loads((ROOT / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        rows = {row["id"]: row for row in data["capabilities"]}
        row = rows["method.astrology"]
        self.assertEqual("ASTROLOGY.md", row["owner"])
        self.assertEqual("explicit-request-only", row["activation"])
        self.assertEqual("tools/astrology_runtime.py", row["runtime"])

    def test_astrology_method_owner_forbids_model_calculation_and_names_provider(self):
        text = (ROOT / "ASTROLOGY.md").read_text(encoding="utf-8")
        self.assertIn("model freehand calculation", text)
        self.assertIn("tools/astrology_provider.py", text)
        self.assertIn("astronomy-engine-natal-v1", text)
        self.assertIn("transit event-search provider 尚未 admission", text)


if __name__ == "__main__":
    unittest.main()
