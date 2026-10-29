"""Mixed Tarot / Meihua / Liuyao batch and interleaved-call regressions.

No live draws: FakeBridge supplies canned raw facts, including all six coin
triples. Tests cover ten+ distinct labeled receipts and multiple invocations.
"""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]/"integrations"/"chatgpt-mcp"
sys.path.insert(0,str(ROOT))
from batch_cast import (execute_batch, validate_batch, _stable_hash, MAX_BATCH,
                        MAX_SUMMARY_CHARS, RECEIPT_FORMAT)
from auto_routing import route_from_summary, execute_auto_route
import app as service

STAMP="2026-10-28T20:20:31+08:00"
SOURCE={"source":"divination-casting-randomizer-python",
        "algorithm_version":"2", "schema_version":"4",
        "runtime_source_commit":"fixture",
        "generated_at_utc":"2026-10-28T12:20:31+00:00",
        "generated_at_taipei":STAMP, "timezone":"Asia/Taipei",
        "rng":"fixture"}

class FakeBridge:
    def __init__(self, fail_on=0):
        self.calls=[]
        self.fail_on=fail_on
    def revalidate_source(self): pass
    def _failure(self, method):
        self.calls.append(method)
        if len(self.calls)==self.fail_on:
            raise RuntimeError("fixture outage")
    def cast_liuyao(self):
        self._failure("liuyao")
        lines=[]
        for p,v in enumerate([8,7,8,6,8,7],1):
            coins={6:[2,2,2],7:[2,2,3],8:[2,3,3],9:[3,3,3]}[v]
            lines.append({"position":p,"value":v,"coin_values":coins,
                          "changing":v in (6,9)})
        exe={**SOURCE, "results":[{"method":"liuyao","liuyao":{
            "lines":lines,"line_order":"bottom-to-top"}}]}
        return {"execution":exe,"structured_method_fact":{"structured_method_fact":{
            "ben_gua":{"name":"山水蒙"}, "zhi_gua":{"name":"火水未濟"}}}}
    def cast_meihua(self):
        self._failure("meihua")
        return {"execution":{**SOURCE, "results":[{"method":"plum","plum":{
            "a":"175","b":"196","hexagram":"山雷頤","upper_trigram":"艮",
            "lower_trigram":"震","moving_line":5}}]},
            "structured_method_fact":{"derived":{"mutual_hexagram":{"name":"坤為地"},
                                                 "changed_hexagram":{"name":"風雷益"}}}}
    def draw_tarot(self,count):
        self._failure("tarot")
        return {**SOURCE, "results":[{"method":"tarot","tarot":{
            "cards":[{"index":i,"full_name":f"card{i}","orientation":"正"}
                     for i in range(1,count+1)]}}]}


def labeled(method, index):
    item={"label":f"R{index:02d}", "question_summary":"某項匿名事件的測試",
          "method_override":method}
    if method=="liuyao":
        item.update(question_summary="一個月內是否正式見面",
                    has_completion_rule=True,has_horizon=True)
    if method=="meihua":
        item["question_summary"]="某項合作後續發展"
    if method=="tarot":
        item["question_summary"]="比較兩個匿名方案"
        item["tarot_count"]=2
    return item

def mixed_twelve():
    sequence=("tarot","liuyao","meihua","tarot","meihua","liuyao",
              "liuyao","tarot","meihua","liuyao","tarot","meihua")
    return [labeled(method,i) for i,method in enumerate(sequence)]

def three():
    return [{"label":label,"question_summary":"期限內是否正式見面",
             "method_override":"liuyao","has_completion_rule":True,
             "has_horizon":True} for label in ("XO","Mosy","CMB")]


class BatchCastTests(unittest.TestCase):
    def test_three_independent_liuyao_receipts_with_original_coin_values(self):
        engine=FakeBridge()
        result=execute_batch(three(),lambda:engine)
        self.assertEqual(result["status"],"batch_completed")
        self.assertEqual([x["label"] for x in result["receipts"]],["XO","Mosy","CMB"])
        self.assertEqual(engine.calls,["liuyao"]*3)
        self.assertEqual(result["receipt_format"],RECEIPT_FORMAT)
        self.assertNotIn("excerpts",str(result))
        for receipt in result["receipts"]:
            self.assertEqual(receipt["status"],"cast_completed")
            self.assertEqual(receipt["summary"]["raw_lines"],[8,7,8,6,8,7])
            self.assertEqual(len(receipt["raw_cast"]["lines"]),6)
            for line in receipt["raw_cast"]["lines"]:
                self.assertEqual(sum(line["coin_values"]),line["value"])
            self.assertEqual(receipt["summary"]["cast_timestamp"],STAMP)
            self.assertEqual(receipt["summary"]["primary_hexagram"],"山水蒙")
            self.assertEqual(receipt["summary"]["changed_hexagram"],"火水未濟")
            self.assertEqual(len(receipt["receipt_sha256"]),64)
            unhashed={k:v for k,v in receipt.items() if k!="receipt_sha256"}
            self.assertEqual(receipt["receipt_sha256"],_stable_hash(unhashed))
            self.assertEqual(receipt["batch_id"],result["batch_id"])
        self.assertLess(len(json.dumps(result,ensure_ascii=False)),14000)

    def test_twelve_mixed_interleaved_methods_keep_sequence_and_receipt_identity(self):
        spy=FakeBridge()
        items=mixed_twelve()
        out=execute_batch(items,lambda:spy)
        self.assertEqual(out["status"],"batch_completed")
        self.assertEqual(out["completed_count"],12)
        self.assertEqual(out["total_count"],12)
        self.assertEqual([x["label"] for x in out["receipts"]],[x["label"] for x in items])
        methods=[x["method_override"] for x in items]
        self.assertEqual([x["selected_method"] for x in out["receipts"]],methods)
        self.assertEqual(spy.calls,methods)
        self.assertEqual(len({x["receipt_id"] for x in out["receipts"]}),12)
        self.assertEqual(len({x["receipt_sha256"] for x in out["receipts"]}),12)
        self.assertTrue(all(x["index"]==i for i,x in enumerate(out["receipts"])))
        self.assertLess(len(json.dumps(out,ensure_ascii=False)),32000)

    def test_twelve_liuyao_receipts_do_not_exceed_bounded_response(self):
        spy=FakeBridge()
        items=[labeled("liuyao",i) for i in range(MAX_BATCH)]
        out=execute_batch(items,lambda:spy)
        self.assertEqual(out["completed_count"],12)
        self.assertLess(len(json.dumps(out,ensure_ascii=False)),32000)
        self.assertEqual([x["selected_method"] for x in out["receipts"]],["liuyao"]*12)

    def test_twelve_tarot_and_meihua_are_also_supported(self):
        for method in ("tarot","meihua"):
            with self.subTest(method=method):
                spy=FakeBridge()
                out=execute_batch([labeled(method,i) for i in range(12)],lambda:spy)
                self.assertEqual(out["completed_count"],12)
                self.assertEqual(spy.calls,[method]*12)

    def test_batch_single_batch_interleave_remains_stateless(self):
        spy=FakeBridge()
        first=execute_batch([labeled("tarot",0),labeled("liuyao",1)],lambda:spy)
        middle=execute_auto_route(route_from_summary(
            "某項合作後續發展",method_override="meihua"),lambda:spy)
        second=execute_batch([labeled("liuyao",0),labeled("meihua",1)],lambda:spy)
        self.assertEqual([x["selected_method"] for x in first["receipts"]],["tarot","liuyao"])
        self.assertEqual(middle["status"],"cast_completed")
        self.assertEqual([x["selected_method"] for x in second["receipts"]],["liuyao","meihua"])
        self.assertEqual(spy.calls,["tarot","liuyao","meihua","liuyao","meihua"])
        self.assertNotEqual(first["batch_id"],second["batch_id"])
        self.assertTrue({x["receipt_id"] for x in first["receipts"]}.isdisjoint(
            {x["receipt_id"] for x in second["receipts"]}))
        self.assertEqual(first["receipts"][0]["summary"]["cards"][0]["full_name"],"card1")
        self.assertEqual(second["receipts"][0]["summary"]["raw_lines"],[8,7,8,6,8,7])

    def test_preflight_invalid_item_blocks_all_casts(self):
        for mutate in (
            lambda a:(a[5].pop("has_horizon"), a[5].update(question_summary="是否正式見面")),
            lambda a:a.append(labeled("tarot",12)),
            lambda a:a[1].update(label=a[0]["label"]),
            lambda a:a[1].update(label="../../unsafe"),
            lambda a:a[1].update(method_override="astrology"),
            lambda a:a[1].update(existing_cast=False),
            lambda a:a[1].update(question_summary="聯絡 0912345678"),
            lambda a:a[1].update(question_summary="關係發展"*(MAX_SUMMARY_CHARS)),
        ):
            with self.subTest(mutation=str(mutate)):
                bad=mixed_twelve()
                mutate(bad)
                spy=FakeBridge()
                with self.assertRaises(ValueError):
                    execute_batch(bad,lambda:spy)
                self.assertEqual(spy.calls,[])

    def test_partial_failure_keeps_prior_receipts_without_retry(self):
        spy=FakeBridge(fail_on=6)
        out=execute_batch(mixed_twelve(),lambda:spy)
        self.assertEqual(out["status"],"partial_failure")
        self.assertEqual(out["completed_count"],5)
        self.assertEqual([r["label"] for r in out["receipts"]],
                         [f"R{i:02d}" for i in range(5)])
        self.assertEqual(out["failed_label"],"R05")
        self.assertEqual(out["unattempted_labels"],
                         [f"R{i:02d}" for i in range(6,12)])
        self.assertEqual(len(spy.calls),6)
        self.assertTrue(all(r["batch_id"]==out["batch_id"] for r in out["receipts"]))

    def test_actual_pinned_bridge_twelve_mixed_without_randomness(self):
        # Run the REAL source-verified canonical engines, not a FakeBridge.
        # A constant randbelow fixture prevents consuming actual randomness.
        # Therefore the test is reproducible and is NOT a user divination.
        with patch.object(service.ENGINE.core, 'randbelow', side_effect=lambda limit: 0):
            result = execute_batch(mixed_twelve(), service._bridge)
        self.assertEqual(result['status'], 'batch_completed')
        self.assertEqual(result['completed_count'], 12)
        from bridge import SOURCE_COMMIT
        for item in result['receipts']:
            with self.subTest(label=item['label'], method=item['selected_method']):
                self.assertEqual(item['source']['runtime_source_commit'], SOURCE_COMMIT)
                self.assertEqual(item['source']['source'],
                                 'divination-casting-randomizer-python')
                self.assertEqual(item['source']['algorithm_version'], '2')
                self.assertEqual(item['source']['schema_version'], '4')
                self.assertEqual(item['source']['timezone'], 'Asia/Taipei')
                if item['selected_method'] == 'tarot':
                    self.assertEqual(item['raw_cast']['count'], 2)
                    self.assertEqual(len(item['raw_cast']['cards']), 2)
                    self.assertTrue(all(x['orientation']=='正'
                                        for x in item['raw_cast']['cards']))
                elif item['selected_method'] == 'meihua':
                    cast = item['raw_cast']
                    derived = service.ENGINE.derive_meihua(
                        cast['a'], cast['b'],
                        upper_trigram=cast['upper_trigram'],
                        lower_trigram=cast['lower_trigram'],
                        hexagram=cast['hexagram'],
                        moving_line=cast['moving_line'])
                    self.assertEqual(derived['structured_method_fact']['cast_fact']['hexagram'],
                                     item['summary']['primary_hexagram'])
                    self.assertEqual(derived['structured_method_fact']['derived']
                                     ['changed_hexagram']['name'],
                                     item['summary']['changed_hexagram'])
                else:
                    cast = item['raw_cast']
                    self.assertEqual(cast['line_order'], 'bottom-to-top')
                    self.assertEqual([x['value'] for x in cast['lines']],
                                     item['summary']['raw_lines'])
                    deterministic = service.ENGINE.derive_liuyao(
                        item['summary']['raw_lines'],
                        item['summary']['cast_timestamp'])
                    fact = deterministic['structured_method_fact']['structured_method_fact']
                    self.assertEqual(fact['ben_gua']['name'],
                                     item['summary']['primary_hexagram'])
                    self.assertEqual(fact['zhi_gua']['name'],
                                     item['summary']['changed_hexagram'])
                    self.assertTrue(all(sum(x['coin_values'])==x['value']
                                        for x in cast['lines']))
        self.assertLess(len(json.dumps(result, ensure_ascii=False).encode('utf-8')),
                        40000)

    def test_policy_failure_means_zero_random_draws(self):
        spy=FakeBridge()
        with patch("batch_cast.policy_identity",side_effect=RuntimeError("bad policy")):
            with self.assertRaises(RuntimeError):
                execute_batch(mixed_twelve(),lambda:spy)
        self.assertEqual(spy.calls,[])

if __name__=="__main__":
    unittest.main()
