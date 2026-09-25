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

    def test_manifest_admits_natal_transit_and_place_resolution(self):
        data = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        natal = data["natal_provider"]
        transit = data["transit_provider"]
        place = data["place_resolver"]
        self.assertEqual("astronomy-engine-natal-v1", natal["provider_id"])
        self.assertEqual("1.3.0", natal["provider_version"])
        self.assertIn("natal_known_time_derived_axes", natal["scope"])
        self.assertEqual(
            ["SouthNode", "Descendant", "ImumCoeli"],
            natal["known_time_derived_axes"]["object_ids"],
        )
        self.assertEqual("not_emitted", natal["known_time_derived_axes"]["unknown_time"])
        self.assertEqual("explicit_projection_policy_only", natal["known_time_derived_axes"]["aspect_participation"])
        self.assertEqual("astronomy-engine-transit-v1", transit["provider_id"])
        self.assertEqual("geonamescache-city-v1", place["resolver_id"])
        self.assertTrue(natal["raw_birth_data_supported"])
        self.assertEqual(400, transit["max_search_days"])
        self.assertFalse(place["network_required"])
        self.assertNotIn("provider_transit_event_search", data["unsupported_scopes"])
        self.assertNotIn("provider_geocoding", data["unsupported_scopes"])

    def test_manifest_admits_natal_and_transit_interpretation_only(self):
        data = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual({"natal", "transit"}, set(data["reading_modes"]))
        self.assertIn("synastry", data["unsupported_scopes"])
        self.assertIn("raw_birth_data_model_calculation", data["unsupported_scopes"])
        self.assertIn("street_or_building_geocoding", data["unsupported_scopes"])
        self.assertIn("unbounded_transit_search", data["unsupported_scopes"])

    def test_natal_provider_admission_manifest_is_pinned_and_bounded(self):
        data = json.loads((ROOT / "ASTROLOGY_PROVIDER_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("astrology_provider_admission", data["schema_name"])
        self.assertEqual("PRODUCTION_ADMITTED", data["status"])
        self.assertEqual("1.3.0", data["provider_version"])
        self.assertEqual(
            [
                "natal",
                "natal_unknown_time_invariant_signs",
                "natal_known_time_derived_axes",
                "natal_known_time_part_of_fortune",
                "natal_known_time_sect",
            ],
            data["scope"],
        )
        self.assertEqual("astronomy-engine", data["dependency"]["package"])
        self.assertEqual("2.1.19", data["dependency"]["version"])
        self.assertEqual("MIT", data["dependency"]["license"])
        self.assertEqual("fail_closed", data["calculation_policy"]["dst_ambiguous_wall_time"])
        self.assertIn("unknown", data["input_contract"]["birth_time_certainty"])
        self.assertEqual(
            "admitted_invariant_sign_only_no_noon_substitution",
            data["calculation_policy"]["unknown_birth_time"],
        )

    def test_transit_provider_admission_manifest_is_pinned_and_bounded(self):
        data = json.loads((ROOT / "ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("astrology_transit_provider_admission", data["schema_name"])
        self.assertEqual("PRODUCTION_ADMITTED", data["status"])
        self.assertIn("transit_to_natal_exact_aspects", data["scope"])
        self.assertIn("stations", data["scope"])
        self.assertIn("tropical_ingresses", data["scope"])
        self.assertEqual("astronomy-engine", data["dependency"]["package"])
        self.assertEqual("2.1.19", data["dependency"]["version"])
        self.assertEqual(400, data["input_contract"]["max_search_days"])
        self.assertEqual("UTC", data["calculation_policy"]["canonical_event_time"])

    def test_place_resolver_admission_manifest_is_offline_and_attributed(self):
        data = json.loads((ROOT / "ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("astrology_place_resolver_admission", data["schema_name"])
        self.assertEqual("PRODUCTION_ADMITTED", data["status"])
        self.assertEqual("geonamescache", data["dependency"]["package"])
        self.assertEqual("3.0.2", data["dependency"]["version"])
        self.assertEqual("MIT", data["dependency"]["software_license"])
        self.assertEqual("CC-BY-4.0", data["dependency"]["dataset_license"])
        self.assertTrue(data["dependency"]["attribution_required"])
        self.assertFalse(data["resolution_policy"]["network_required"])
        self.assertFalse(data["resolution_policy"]["auto_pick_largest_population_when_ambiguous"])
        self.assertIn("country_name_or_code_to_unique_iana_timezone", data["scope"])
        self.assertEqual("fail_closed", data["resolution_policy"]["country_multiple_timezones"])

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

    def test_chat_init_routes_production_astrology_through_root_and_mode_owner(self):
        text = (ROOT / "CHAT_INIT.md").read_text(encoding="utf-8")
        self.assertIn("明確指定 production Astrology", text)
        self.assertIn("先讀 root `ASTROLOGY.md`", text)
        self.assertIn("`ASTROLOGY_NATAL.md` 或 `ASTROLOGY_TRANSIT.md`", text)
        self.assertIn("selected Astrology mode owner", text)
        self.assertIn("raw birth data 不授權模型自行手算", text)

    def test_research_router_keeps_astrology_research_separate(self):
        text = (ROOT / "RESEARCH_ROUTING.md").read_text(encoding="utf-8")
        self.assertIn("Production owner：[`ASTROLOGY.md`](ASTROLOGY.md)", text)
        self.assertIn("Astrology production reading 不屬於這個 gate", text)
        self.assertIn("不因 production v1 已 admission 就回頭改寫成 production source of truth", text)

    def test_machine_index_exposes_complete_astrology_runtime_path(self):
        data = json.loads((ROOT / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        rows = {row["id"]: row for row in data["capabilities"]}
        row = rows["method.astrology"]
        self.assertEqual("ASTROLOGY.md", row["owner"])
        self.assertEqual("explicit-request-only", row["activation"])
        self.assertEqual("tools/astrology_place_resolver.py", row["place_resolver"])
        self.assertEqual("tools/astrology_provider.py", row["natal_provider"])
        self.assertEqual("tools/astrology_transit_provider.py", row["transit_provider"])
        self.assertEqual("tools/astrology_runtime.py", row["runtime"])
        self.assertEqual("ASTROLOGY_NATAL.md", row["natal_owner"])
        self.assertEqual("ASTROLOGY_TRANSIT.md", row["transit_owner"])
        self.assertEqual("ASTROLOGY_NATAL.md", rows["method.astrology.natal"]["owner"])
        self.assertEqual("ASTROLOGY_TRANSIT.md", rows["method.astrology.transit"]["owner"])
        self.assertEqual("tools/astrology_rulership_projection.py", row["rulership_projection"])
        self.assertEqual(
            "schemas/astrology/ASTROLOGY_RULERSHIP_PROJECTION_V1.schema.json",
            row["rulership_projection_schema"],
        )
        self.assertEqual("explicit-selector-only", row["rulership_activation"])
        self.assertEqual("tools/astrology_pattern_topology.py", row["pattern_topology_projection"])
        self.assertEqual(
            "schemas/astrology/ASTROLOGY_PATTERN_TOPOLOGY_PROJECTION_V1.schema.json",
            row["pattern_topology_projection_schema"],
        )
        self.assertEqual("explicit-selector-only", row["pattern_topology_activation"])
        self.assertEqual("tools/astrology_special_pattern_projection.py", row["special_pattern_projection"])
        self.assertEqual(
            "schemas/astrology/ASTROLOGY_SPECIAL_PATTERN_PROJECTION_V1.schema.json",
            row["special_pattern_projection_schema"],
        )
        self.assertEqual("explicit-selector-only", row["special_pattern_activation"])
        self.assertNotIn("explicit_astrology", data["loader"]["bypass_profiles"])

    def test_astrology_root_owner_keeps_common_boundary_and_routes_mode_owners(self):
        text = (ROOT / "ASTROLOGY.md").read_text(encoding="utf-8")
        self.assertIn("model freehand calculation", text)
        self.assertIn("ASTROLOGY_NATAL.md", text)
        self.assertIn("ASTROLOGY_TRANSIT.md", text)
        self.assertIn("final_method_owner = ASTROLOGY.md", text)

    def test_astrology_mode_owners_point_to_machine_truth_without_copying_provider_specs(self):
        natal = (ROOT / "ASTROLOGY_NATAL.md").read_text(encoding="utf-8")
        transit = (ROOT / "ASTROLOGY_TRANSIT.md").read_text(encoding="utf-8")
        self.assertIn("ASTROLOGY_PROVIDER_ADMISSION_V1.json", natal)
        self.assertIn("ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json", natal)
        self.assertIn("ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json", transit)
        self.assertNotIn("astronomy-engine==", natal)
        self.assertNotIn("Whole Sign or Placidus", natal)
        self.assertNotIn("\ndomicile\nexaltation\ndetriment\nfall\n", natal)
        self.assertNotIn("root tolerance =", transit)
        self.assertIn("production orchestrator / admitted natal provider", transit)
        self.assertIn("tools/astrology_rulership_projection.py", natal)
        self.assertIn("rulership-traditional-v1", natal)
        self.assertIn("rulership-modern-v1", natal)
        self.assertIn("不得因一般占星習慣、使用者未指定流派或模型偏好而 silent-default", natal)
        self.assertIn("tools/astrology_pattern_topology.py", natal)
        self.assertIn("runtime-admitted natal aspect graph", natal)
        self.assertIn("Yod、Stellium、Grand Quintile", natal)


    def test_e1_admission_keeps_aspect_and_interpretation_boundaries_closed(self):
        manifest = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        participants = manifest["aspect_policy"]["participant_object_ids"]
        self.assertEqual(
            ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "NorthNode"],
            participants,
        )
        self.assertTrue({"SouthNode", "Descendant", "ImumCoeli"}.isdisjoint(participants))
        self.assertEqual("explicit_projection_policies_only", manifest["aspect_policy"]["extended_points_or_angles"])
        self.assertIsNone(manifest["aspect_policy"]["default_extended_policy"])
        self.assertEqual(
            {
                "aspect-participants-core-plus-angles-v1",
                "aspect-participants-core-plus-south-node-v1",
                "aspect-participants-core-plus-fortune-v1",
            },
            set(manifest["aspect_policy"]["extended_participant_policy_ids"]),
        )
        derived = manifest["natal_semantic_policy"]["derived_fact_interpretation"]
        self.assertEqual("forbidden_unless_explicitly_admitted", derived["claim_binding"])
        self.assertEqual({"Descendant", "ImumCoeli", "PartOfFortune"}, set(derived["admitted_claim_bindings"]))
        self.assertEqual(["SouthNode"], derived["no_admitted_claim_bindings"])


    def test_e4_admission_is_named_fail_closed_and_fact_only(self):
        provider = json.loads((ROOT / "ASTROLOGY_PROVIDER_ADMISSION_V1.json").read_text(encoding="utf-8"))
        production = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))

        sect = provider["calculation_policy"]["sect_policy"]
        self.assertEqual("sect-geometric-solar-altitude-v1", sect["policy_id"])
        self.assertEqual("geocentric-equator-of-date", sect["sun_frame"])
        self.assertEqual("Airless", sect["refraction"])
        self.assertEqual("fail_closed", sect["exact_zero"])
        self.assertEqual("fail_closed", sect["unavailable"])
        self.assertEqual("not_computed", sect["unknown_time"])

        fortune = provider["calculation_policy"]["part_of_fortune"]
        self.assertEqual("PartOfFortune", fortune["object_id"])
        self.assertEqual("fortune-day-night-v1", fortune["derivation_policy"])
        self.assertEqual("sect-geometric-solar-altitude-v1", fortune["sect_policy_id"])
        self.assertEqual("Ascendant + Moon - Sun", fortune["diurnal_formula"])
        self.assertEqual("Ascendant + Sun - Moon", fortune["nocturnal_formula"])
        self.assertEqual("not_emitted", fortune["unknown_time"])
        self.assertEqual("explicit_projection_policy_only", fortune["aspect_participation"])

        admitted = production["natal_provider"]["known_time_part_of_fortune"]
        self.assertEqual("fact_only_until_separately_admitted", admitted["interpretation_semantics"])
        self.assertEqual(
            "provider_derived_calculation_context",
            production["natal_provider"]["known_time_sect"]["authority"],
        )
        self.assertIn(
            "PartOfFortune",
            production["natal_semantic_policy"]["derived_fact_interpretation"]["fact_only_object_ids"],
        )
        self.assertNotIn("PartOfFortune", production["aspect_policy"]["participant_object_ids"])

    def test_e7_rulership_is_dual_policy_and_has_no_silent_default(self):
        manifest = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        policy = manifest["orchestration"]["policy_projections"]["rulership"]
        self.assertEqual("deterministic_policy_projection_only", policy["authority"])
        self.assertEqual("explicit_selector_only", policy["activation"])
        self.assertEqual(
            ["rulership-traditional-v1", "rulership-modern-v1"],
            policy["admitted_policy_ids"],
        )
        self.assertEqual("forbidden", policy["silent_default"])
        self.assertEqual("forbidden", policy["silent_blending"])
        self.assertFalse(policy["semantic_interpretation_authority"])


    def test_e5_names_current_aspect_policy_without_expanding_behavior(self):
        manifest = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        policy = manifest["aspect_policy"]
        self.assertEqual("aspect-participants-core-bodies-v1", policy["participant_policy_id"])
        self.assertEqual("major-aspects-v1", policy["aspect_policy_id"])
        self.assertEqual("major-aspect-orbs-v1", policy["orb_policy_id"])
        self.assertFalse(policy["auto_include_new_objects"])
        self.assertEqual("explicit_selector_only", policy["extended_policy_activation"])
        self.assertTrue({"SouthNode", "Ascendant", "Descendant", "Midheaven", "ImumCoeli", "PartOfFortune"}.isdisjoint(policy["participant_object_ids"]))

    def test_e6_topology_requires_explicit_e5_and_projection_policies(self):
        manifest = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        policy = manifest["orchestration"]["policy_projections"]["pattern_topology"]
        self.assertEqual("explicit_selector_only", policy["activation"])
        self.assertEqual("aspect-participants-core-bodies-v1", policy["required_participant_policy_id"])
        self.assertEqual("major-aspects-v1", policy["required_aspect_policy_id"])
        self.assertEqual("major-aspect-orbs-v1", policy["required_orb_policy_id"])
        self.assertEqual(["aspect-pattern-topology-major-v1"], policy["admitted_pattern_policy_ids"])
        self.assertEqual(
            ["pattern-projection-report-all-valid-v1", "pattern-projection-suppress-strict-subsets-v1"],
            policy["admitted_projection_policy_ids"],
        )
        self.assertEqual("forbidden", policy["silent_default"])
        self.assertFalse(policy["semantic_interpretation_authority"])

    def test_p1_120_special_patterns_are_explicit_and_do_not_mutate_major_topology(self):
        manifest = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        major = manifest["orchestration"]["policy_projections"]["pattern_topology"]
        special = manifest["orchestration"]["policy_projections"]["special_patterns"]
        self.assertEqual("major-aspects-v1", major["required_aspect_policy_id"])
        self.assertEqual(
            ["T-Square", "Grand Trine", "Grand Cross", "Kite", "Mystic Rectangle", "Cradle", "Grand Sextile"],
            major["admitted_pattern_types"],
        )
        self.assertEqual("explicit_selector_only", special["activation"])
        self.assertEqual("pattern-aspects-yod-quintile-v1", special["aspect_policy_id"])
        self.assertEqual("pattern-aspect-orbs-yod-quintile-v1", special["orb_policy_id"])
        self.assertEqual(
            {"conjunction": 8.0, "sextile": 5.0, "quincunx": 3.0, "quintile": 2.0, "biquintile": 2.0},
            special["max_orb_degrees"],
        )
        self.assertEqual(["Yod", "Stellium", "Grand Quintile"], special["admitted_pattern_types"])
        self.assertIsNone(special["default_participant_policy_id"])
        self.assertEqual("forbidden", special["silent_default"])
        self.assertFalse(special["semantic_interpretation_authority"])
        self.assertFalse(special["exact_consumer_compatibility_claimed"])


    def test_derived_interpretation_admission_is_exact_claim_allowlist(self):
        manifest = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        policy = manifest["natal_semantic_policy"]["derived_fact_interpretation"]
        descendant = {
            (row["registry_record_id"], row["claim_id"])
            for row in policy["admitted_claim_bindings"]["Descendant"]
        }
        ic = {
            (row["registry_record_id"], row["claim_id"])
            for row in policy["admitted_claim_bindings"]["ImumCoeli"]
        }
        self.assertEqual(
            {
                ("first-seventh-house-axis-research-v1", "claim:valens-seventh-place-marriage"),
                ("first-seventh-house-axis-research-v1", "claim:lilly-seventh-house-marriage-opponents"),
                ("first-seventh-house-axis-research-v1", "claim:houlding-seventh-house-partnership-opponent"),
            },
            descendant,
        )
        self.assertEqual(
            {
                ("fourth-tenth-house-axis-research-v1", "claim:valens-fourth-place-home-possessions-activity"),
                ("fourth-tenth-house-axis-research-v1", "claim:lilly-fourth-house-land-father-endings"),
                ("fourth-tenth-house-axis-research-v1", "claim:houlding-fourth-house-roots-foundation-property"),
            },
            ic,
        )


if __name__ == "__main__":
    unittest.main()
