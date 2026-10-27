"""Server-side v2 question summary routing regressions.

No real divination done in these tests; fake bridge counts calls.
"""
import unittest
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / 'integrations' / 'chatgpt-mcp'
sys.path.insert(0, str(BASE))
from auto_routing import route_from_summary, classify_summary, execute_auto_route, ROUTER_VERSION


class SpyBridge:
    def __init__(self): self.calls=[]
    def draw_tarot(self, count):
        self.calls.append(('tarot',count)); return {'cards': ['fake']*count}
    def cast_meihua(self):
        self.calls.append(('meihua',)); return {'symbolic': 'fake'}
    def cast_liuyao(self):
        self.calls.append(('liuyao',)); return {'lines':[7]*6}


class ServerClassifierTests(unittest.TestCase):
    def pick(self,text, **kw): return route_from_summary(text, **kw)
    def test_route_version(self): self.assertEqual(ROUTER_VERSION,'auto-routing-v2')
    def test_psychology_one(self): self.assertEqual(self.pick('為什麼偶爾私訊我')['selected_method'],'tarot')
    def test_psychology_two(self): self.assertEqual(self.pick('她目前如何定位我')['selected_method'],'tarot')
    def test_psychology_three(self): self.assertEqual(self.pick('對方現在怎麼想')['selected_method'],'tarot')
    def test_ongoing_relationship(self): self.assertEqual(self.pick('長期關係發展方向會怎麼發展')['selected_method'],'meihua')
    def test_process_timing(self): self.assertEqual(self.pick('接下來三個月合作的節奏與轉折')['selected_method'],'meihua')
    def test_psychology_with_long_term(self): self.assertEqual(self.pick('她長期對我怎麼想')['selected_method'],'tarot')
    def test_process_not_outcome_due_to_time(self): self.assertEqual(self.pick('年底前這段關係會怎麼發展')['selected_method'],'meihua')
    def test_comparison(self): self.assertEqual(self.pick('A方案B方案哪個比較適合')['selected_method'],'tarot')
    def test_concrete_relationship(self):
        p=self.pick('三個月內是否會正式交往')
        self.assertEqual((p['selected_method'],p['status']),('liuyao','ready'))
    def test_concrete_cooperation(self):
        p=self.pick('截至月底雙方是否正式簽約')
        self.assertEqual((p['selected_method'],p['status']),('liuyao','ready'))
    def test_concrete_reply(self):
        p=self.pick('本週五以前她會不會回覆訊息')
        self.assertEqual((p['selected_method'],p['status']),('liuyao','ready'))
    def test_no_deadline(self):
        p=self.pick('這個工程案能否正式結案')
        self.assertEqual((p['selected_method'],p['status']),('liuyao','needs_clarification'))
    def test_yes_no_not_observable(self):
        p=self.pick('三個月內她會不會想我')
        self.assertEqual(p['status'],'needs_clarification')
    def test_override_tarot(self): self.assertEqual(self.pick('下一階段怎麼發展',method_override='tarot')['selected_method'],'tarot')
    def test_override_meihua(self): self.assertEqual(self.pick('她目前如何看我',method_override='meihua')['selected_method'],'meihua')
    def test_override_liuyao_missing_deadline(self): self.assertEqual(self.pick('她目前如何看我',method_override='liuyao')['status'],'needs_clarification')
    def test_unsupported_astrology(self): self.assertEqual(self.pick('對方怎麼想',method_override='astrology')['status'],'unsupported_method')
    def test_existing_cast_no_redraw(self):
        p=self.pick('長期關係發展方向',existing_cast=True)
        spy=SpyBridge()
        self.assertEqual(execute_auto_route(p,lambda:spy)['status'],'existing_cast_preserved')
        self.assertEqual(spy.calls,[])
    def test_question_empty(self): self.assertEqual(self.pick('')['status'],'needs_clarification')
    def test_question_unspecified(self): self.assertEqual(self.pick('幫我占卜看看')['status'],'needs_clarification')
    def test_phone_reject(self): self.assertEqual(self.pick('某人電話 0912345678 邀約動機')['reason_code'],'possible_contact_or_url')
    def test_email_reject(self): self.assertEqual(self.pick('someone@example.com 的想法')['reason_code'],'possible_contact_or_url')
    def test_bad_len(self): self.assertEqual(self.pick('長期發展'*100)['status'],'invalid_input')
    def test_stale_label_not_used(self):
        p=self.pick('長期關係發展方向')
        self.assertEqual(p['routing_source'],'server_question_summary')
        self.assertEqual(p['router_version'],'auto-routing-v2')
    def test_actual_meihua_called_once(self):
        spy=SpyBridge();r=execute_auto_route(self.pick('長期關係發展方向'),lambda:spy)
        self.assertEqual(r['status'],'cast_completed');self.assertEqual(spy.calls,[('meihua',)])
    def test_actual_tarot_called_once(self):
        spy=SpyBridge();r=execute_auto_route(self.pick('為什麼私訊我'),lambda:spy)
        self.assertEqual(r['status'],'cast_completed');self.assertEqual(spy.calls,[('tarot',3)])
    def test_actual_liuyao_called_once(self):
        spy=SpyBridge();r=execute_auto_route(self.pick('兩個月內是否正式交往'),lambda:spy)
        self.assertEqual(r['status'],'cast_completed');self.assertEqual(spy.calls,[('liuyao',)])
    def test_no_cast_on_missing_horizon(self):
        spy=SpyBridge();r=execute_auto_route(self.pick('對方能否正式回覆'),lambda:spy)
        self.assertEqual(r['status'],'needs_clarification');self.assertEqual(spy.calls,[])

if __name__=='__main__':unittest.main(verbosity=2)
