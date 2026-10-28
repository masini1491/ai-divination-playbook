"""No randomness in test: labeled multi-cast receipts remain recoverable."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]/"integrations"/"chatgpt-mcp"
sys.path.insert(0,str(ROOT))
from batch_cast import execute_batch, validate_batch, _stable_hash
import app as service


STAMP = "2026-10-28T20:20:31+08:00"
class FakeBridge:
    def __init__(self, fail_on=0):
        self.calls=[];self.fail_on=fail_on
    def revalidate_source(self): pass
    def cast_liuyao(self):
        self.calls.append("liuyao")
        if len(self.calls)==self.fail_on:
            raise RuntimeError("fixture outage")
        lines=[]
        for p,v in enumerate([8,7,8,6,8,7],1):
            coins={6:[2,2,2],7:[2,2,3],8:[2,3,3],9:[3,3,3]}[v]
            lines.append({"position":p,"value":v,"coin_values":coins,"changing":v in (6,9)})
        exe={"results":[{"method":"liuyao","liuyao":{"lines":lines,"line_order":"bottom-to-top"}}],
             "source":"divination-casting-randomizer-python",
             "algorithm_version":"2","schema_version":"4","runtime_source_commit":"fixture",
             "generated_at_utc":"2026-10-28T12:20:31+00:00",
             "generated_at_taipei":STAMP,"timezone":"Asia/Taipei","rng":"fixture"}
        return {"execution":exe,"structured_method_fact":{"structured_method_fact":{
            "ben_gua":{"name":"山水蒙"}, "zhi_gua":{"name":"火水未濟"}}}}
    def cast_meihua(self):
        self.calls.append("meihua")
        return {"execution":{"results":[{"method":"plum","plum":{
            "a":"175","b":"196","hexagram":"山雷頤","upper_trigram":"艮",
            "lower_trigram":"震","moving_line":5}}],
            "generated_at_taipei":STAMP},
            "structured_method_fact":{"derived":{"mutual_hexagram":{"name":"坤為地"},
                                                 "changed_hexagram":{"name":"風雷益"}}}}
    def draw_tarot(self,count):
        self.calls.append("tarot")
        return {"results":[{"method":"tarot","tarot":{"cards":[
            {"index":i,"full_name":f"card{i}","orientation":"正"} for i in range(1,count+1)]}}],
            "generated_at_taipei":STAMP}


def three():
    return [{"label":label,"question_summary":f"期限內是否正式見面 {label}",
             "method_override":"liuyao","has_completion_rule":True,"has_horizon":True}
            for label in ("XO","Mosy","CMB")]


class BatchCastTests(unittest.TestCase):
    def test_three_independent_liuyao_receipts_with_all_original_coins(self):
        engine=FakeBridge()
        result=execute_batch(three(),lambda:engine)
        self.assertEqual(result["status"],"batch_completed")
        self.assertEqual([x["label"] for x in result["receipts"]],["XO","Mosy","CMB"])
        self.assertEqual(engine.calls,["liuyao"]*3)
        self.assertNotIn("excerpts",str(result))
        for receipt in result["receipts"]:
            self.assertEqual(receipt["status"],"cast_completed")
            self.assertEqual(receipt["summary"]["raw_lines"],[8,7,8,6,8,7])
            self.assertEqual(len(receipt["summary"]["coin_values"]),6)
            self.assertEqual(receipt["source"]["generated_at_taipei"],STAMP)
            self.assertEqual(receipt["summary"]["primary_hexagram"],"山水蒙")
            self.assertEqual(receipt["summary"]["changed_hexagram"],"火水未濟")
            self.assertEqual(len(receipt["receipt_sha256"]),64)
            self.assertLess(len(json.dumps(result,ensure_ascii=False)),14000)

    def test_preflight_invalid_item_blocks_all_casts(self):
        bad=three();bad[-1].pop("has_horizon")
        engine=FakeBridge()
        with self.assertRaises(ValueError):
            execute_batch(bad,lambda:engine)
        self.assertEqual(engine.calls,[])
        for mutate in (
            lambda a:a[1].update(label="XO"),
            lambda a:a[1].update(label="../../unsafe"),
            lambda a:a[1].update(method_override="astrology"),
            lambda a:a[1].update(existing_cast=False),
            lambda a:a[1].update(question_summary="聯絡 0912345678"),
        ):
            with self.subTest(mutation=str(mutate)):
                wrong=three();mutate(wrong)
                with self.assertRaises(ValueError):validate_batch(wrong)

    def test_partial_failure_keeps_prior_receipt_without_retry(self):
        spy=FakeBridge(fail_on=2)
        result=execute_batch(three(),lambda:spy)
        self.assertEqual(result["status"],"partial_failure")
        self.assertEqual(result["completed_count"],1)
        self.assertEqual([r["label"] for r in result["receipts"]],["XO"])
        self.assertEqual(result["failed_label"],"Mosy")
        self.assertEqual(result["unattempted_labels"],["CMB"])
        self.assertEqual(spy.calls,["liuyao","liuyao"])

    def test_mixed_methods_are_prevalidated_and_ordered(self):
        items=[{"label":"A","question_summary":"兩案哪個較適合","method_override":"tarot","tarot_count":2},
               {"label":"B","question_summary":"長期合作發展","method_override":"meihua"},
               three()[0]]
        spy=FakeBridge()
        response=execute_batch(items,lambda:spy)
        self.assertEqual([r["selected_method"] for r in response["receipts"]],
                         ["tarot","meihua","liuyao"])
        self.assertEqual(spy.calls,["tarot","meihua","liuyao"])
        self.assertEqual(response["receipts"][0]["summary"]["cards"][0]["full_name"],"card1")
        self.assertEqual(response["receipts"][1]["summary"]["a"],"175")

    def test_policy_failure_means_zero_random_draws(self):
        spy=FakeBridge()
        with patch("batch_cast.policy_identity",side_effect=RuntimeError("bad policy")):
            with self.assertRaises(RuntimeError):
                execute_batch(three(),lambda:spy)
        self.assertEqual(spy.calls,[])

if __name__=="__main__":
    unittest.main()
