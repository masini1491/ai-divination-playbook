import json
from pathlib import Path
import re
import sys
import unittest

CASTING_ROOT = Path(__file__).resolve().parents[2] / "runtime" / "casting"
if str(CASTING_ROOT) not in sys.path:
    sys.path.insert(0, str(CASTING_ROOT))

import randomizer

HTML = (CASTING_ROOT / "index.html").read_text(encoding="utf-8")


def _extract_json_object(name: str) -> dict[str, str]:
    match = re.search(rf"const {name}=(\{{[^;]+\}});", HTML)
    if not match:
        raise AssertionError(f"missing JS object: {name}")
    return json.loads(match.group(1))


class CrossRuntimeContractTests(unittest.TestCase):
    def test_web_ui_has_no_browser_stochastic_implementation(self):
        forbidden = (
            "Math.random",
            "crypto.getRandomValues",
            "function rnd(",
            "function shuffle(",
            "function tarot(",
            "function plum(",
            "function liuyao(",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, HTML)

    def test_web_ui_uses_same_origin_controlled_cast_api(self):
        self.assertIn('fetch("/api/cast"', HTML)
        self.assertIn('body:JSON.stringify({method,count,repeat})', HTML)
        self.assertIn('cache:"no-store"', HTML)
        body = re.search(r"body:JSON\.stringify\(([^)]*)\)", HTML)
        self.assertIsNotNone(body)
        self.assertNotIn("question", body.group(1))
        self.assertIn('apiCast("tarot"', HTML)
        self.assertIn('apiCast("plum"', HTML)
        self.assertIn('drawOne("liuyao")', HTML)

    def test_web_tarot_is_projected_from_api_payload(self):
        self.assertIn("function tarotFromPayload(payload)", HTML)
        self.assertIn('orientation==="reversed"', HTML)
        self.assertIn("tarot.cards.map", HTML)

    def test_web_meihua_is_projected_from_api_payload(self):
        self.assertIn("function plumFromPayload(payload)", HTML)
        self.assertIn("plum.upper", HTML)
        self.assertIn("plum.lower", HTML)
        self.assertIn("plum.hexagram", HTML)
        self.assertIn("plum.moving_line", HTML)

    def test_web_liuyao_uses_api_values_and_coin_values(self):
        self.assertIn("function liuyaoFromPayload(payload)", HTML)
        self.assertIn("liuyao.values", HTML)
        self.assertIn("liuyao.coin_values", HTML)
        self.assertIn('6:["老陰","陰",true]', HTML)
        self.assertIn('9:["老陽","陽",true]', HTML)

    def test_web_hexagram_presentation_table_matches_python_contract(self):
        self.assertEqual(_extract_json_object("hex"), randomizer.HEXAGRAM)


if __name__ == "__main__":
    unittest.main()
