import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_profile500_transport_identity_is_pinned_and_admitted():
    dataset=json.loads((ROOT/"data/astrology/place/v1/MANIFEST.json").read_text())
    resolver=json.loads((ROOT/"ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json").read_text())
    transport=resolver["materialization_transport"]
    assert dataset["production_admission"]=="PROFILE_500_ONLY"
    assert dataset["deployment"]["exact_data_commit"]=="d18be87abe762433e43e844f33f4b43f7fad9f3b"
    assert transport["status"]=="PRODUCTION_ADMITTED_PROFILE_500_ONLY"
    assert transport["profile"]==500
    assert transport["exact_data_commit"]==dataset["deployment"]["exact_data_commit"]
    assert transport["aggregate_digest"]==dataset["deployment"]["expected_aggregate_digest"]
    assert transport["other_profiles"]=="NOT_ADMITTED_FOR_SHARD_MATERIALIZATION"

def test_materialization_requires_exact_data_commit_and_no_profile_substitution():
    text=(ROOT/"ASTROLOGY_MATERIALIZATION.md").read_text()
    assert "Every retrieval MUST use the exact admitted data commit" in text
    assert "not admitted for shard materialization transport" in text
    assert "never silently substitute profile 500" in text

def test_taiwan_admin_normalization_policy_is_small_versioned_and_transport_safe():
    policy=json.loads((ROOT/"runtime/astrology/TW_ADMIN_LOCALITY_V1.json").read_text())
    assert policy["policy_id"]=="taiwan-admin-locality-v1"
    assert policy["status"]=="PRODUCTION_ADMITTED_INPUT_NORMALIZATION"
    assert policy["country_code"]=="TW"
    assert policy["generated_counts"]=={"county_city_count":22,"hierarchy_pair_count":371}
    assert policy["semantics"]["exact_hierarchy_pair_required"] is True
    assert policy["semantics"]["fuzzy_contains_search"] is False
    assert policy["semantics"]["coordinates_authority"] is False

def test_materialization_normalizes_taiwan_admin_input_before_alias_hashing():
    text=(ROOT/"ASTROLOGY_MATERIALIZATION.md").read_text()
    assert "runtime/astrology/TW_ADMIN_LOCALITY_V1.json" in text
    assert "exact county/city × township/district hierarchy validation" in text
    assert "valid pair: query = validated township/district, effective country = TW" in text
    assert "it never supplies coordinates" in text
