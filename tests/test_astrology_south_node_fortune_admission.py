import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_fortune_is_bounded_and_south_node_stays_fact_only():
    m=json.loads((ROOT/"ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text())
    p=m["natal_semantic_policy"]["derived_fact_interpretation"]
    assert "south-node-fortune-research-v1" in m["admitted_research_registries"]
    assert p["admitted_claim_bindings"]["PartOfFortune"]==[{"registry_record_id":"south-node-fortune-research-v1","claim_id":"claim:valens-fortune-life-prosperity"}]
    assert "SouthNode" in p["fact_only_object_ids"]
    assert "SouthNode" in p["no_admitted_claim_bindings"]
    assert "SouthNode" not in p["admitted_claim_bindings"]
def test_registry_preserves_source_scope_and_no_generic_south_node_claim():
    r=json.loads((ROOT/"references/astrology/south_node_fortune_claim_family_registry.json").read_text())
    ids={c["claim_id"] for c in r["claims"]}
    assert "claim:valens-fortune-life-prosperity" in ids
    l=next(c for c in r["claims"] if c["claim_id"]=="claim:lilly-south-node-fortune-conjunction-diminution")
    assert "conjunction" in l["applies_to"]
    assert any("standalone South Node" in x for x in l["cautions"])
