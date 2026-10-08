from __future__ import annotations
import itertools
import unittest
from tools.ziwei_claim_retrieval import FactPacket, _is_availability_only_conditional, select_natal_synthesis_focus
from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_runtime import ZiWeiReadingRequest, run_ziwei

class NatalBrightnessFocusTests(unittest.TestCase):
    def test_meta_vs_value_conditional(self):
        claim={"claim_type":"star_conditional","matched_requires":["star_present:太陽"],
            "conditional_activation":{"mode":"fact_gated","state":"satisfied",
            "availability_requires":["fact_available:dignity"],
            "satisfies_all":[],"satisfies_any":[],"forbids":[]}}
        self.assertTrue(_is_availability_only_conditional(claim))
        self.assertFalse(_is_availability_only_conditional({**claim,"matched_requires":["star_present:太陽","star_in_palace:太陽:官祿宮"]}))
        self.assertFalse(_is_availability_only_conditional({**claim,"conditional_activation":{**claim["conditional_activation"],"satisfies_all":["dignity:太陽:廟"]}}))
        self.assertFalse(_is_availability_only_conditional({**claim,"conditional_activation":{**claim["conditional_activation"],"mode":"context_only"}}))

    def test_concrete_condition_keeps_priority(self):
        packet=FactPacket("synthetic:focus","ziwei.interpretation.tw_v1","natal_baseline",frozenset())
        def claim(cid,sub,condition):
            return {"claim_id":cid,"claim_type":"star_conditional","subject":sub,"subjects":[sub],
                "matched_requires":[f"star_present:{sub}"],"specificity":40,
                "conditional_activation":{"mode":"fact_gated","state":"satisfied",
                "availability_requires":["fact_available:dignity"],
                "satisfies_all":condition,"satisfies_any":[],"forbids":[]}}
        r=select_natal_synthesis_focus(packet,{"selected_claims":[claim("meta","太陽",[]),claim("concrete","太陰",["dignity:太陰:廟"])]},eligible_claim_ids={"meta","concrete"})
        self.assertEqual(["claim:concrete"],r["focus_signal_ids"])
        self.assertEqual(2,r["eligible_claim_count"])
        self.assertEqual(1,r["candidate_signal_count"])

    def test_48_case_ab_stability_and_trace(self):
        for year,month,branch in itertools.product((1981,1984,1987,1990),(1,5,9),("子","卯","午","酉")):
            with self.subTest(year=year,month=month,branch=branch):
                birth=NormalizedNatalInput(year,month,15,branch,"synthetic:ab-evaluation")
                kw={"request_id":f"ab-{year}-{month}-{branch}","birth":birth}
                a=run_ziwei(ZiWeiReadingRequest(**kw))
                b=run_ziwei(ZiWeiReadingRequest(**kw,optional_modules=("brightness_v1",)))
                ai=a["interpretation"];bi=b["interpretation"]
                self.assertEqual("1.1.0",bi["natal_synthesis_v1"]["version"])
                self.assertEqual(ai["natal_synthesis_v1"]["focus_signal_ids"],bi["natal_synthesis_v1"]["focus_signal_ids"])
                self.assertEqual(ai["natal_synthesis_v1"]["focus_claim_ids"],bi["natal_synthesis_v1"]["focus_claim_ids"])
                self.assertEqual(ai["conflicts"],bi["conflicts"])
                self.assertEqual({"ZW-B1-TAIYANG-COND-002","ZW-B2-TAIYIN-COND-002"},set(bi["selected_claim_ids"])-set(ai["selected_claim_ids"]))
                self.assertTrue(set(ai["selected_claim_ids"]).issubset(set(bi["selected_claim_ids"])))
                self.assertEqual(14,len(b["calculation"]["brightness"]["records"]))
                self.assertEqual("not_computed",a["calculation"]["unsupported"]["brightness"])
                self.assertFalse(b["authority"]["brightness_only_doctrine_admitted"])

if __name__=="__main__":
    unittest.main()
