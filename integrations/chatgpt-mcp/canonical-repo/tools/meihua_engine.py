#!/usr/bin/env python3
"""Deterministic Meihua downstream derivation.

Consumes an already-fixed Meihua Cast Fact and derives mutual hexagram,
changed hexagram, body/use assignment, and five-element relation.
No RNG and no interpretation authority.
"""
from __future__ import annotations

import argparse
import json
from typing import Any

ENGINE_NAME = "ai-divination-playbook/meihua-engine"
ENGINE_VERSION = "1"
LINE_ORDER = "bottom-to-top"

TRIGRAM_BITS = {
    "乾": "111", "兌": "110", "離": "101", "震": "100",
    "巽": "011", "坎": "010", "艮": "001", "坤": "000",
}
BITS_TRIGRAM = {bits: name for name, bits in TRIGRAM_BITS.items()}
TRIGRAM_ELEMENT = {
    "乾": "金", "兌": "金", "離": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土",
}
HEXAGRAM_BY_PAIR = {
    "乾乾":"乾為天","坤坤":"坤為地","坎震":"水雷屯","艮坎":"山水蒙","坎乾":"水天需","乾坎":"天水訟",
    "坤坎":"地水師","坎坤":"水地比","巽乾":"風天小畜","乾兌":"天澤履","坤乾":"地天泰","乾坤":"天地否",
    "乾離":"天火同人","離乾":"火天大有","坤艮":"地山謙","震坤":"雷地豫","兌震":"澤雷隨","艮巽":"山風蠱",
    "坤兌":"地澤臨","巽坤":"風地觀","離震":"火雷噬嗑","艮離":"山火賁","艮坤":"山地剝","坤震":"地雷復",
    "乾震":"天雷無妄","艮乾":"山天大畜","艮震":"山雷頤","兌巽":"澤風大過","坎坎":"坎為水","離離":"離為火",
    "兌艮":"澤山咸","震巽":"雷風恆","乾艮":"天山遯","震乾":"雷天大壯","離坤":"火地晉","坤離":"地火明夷",
    "巽離":"風火家人","離兌":"火澤睽","坎艮":"水山蹇","震坎":"雷水解","艮兌":"山澤損","巽震":"風雷益",
    "兌乾":"澤天夬","乾巽":"天風姤","兌坤":"澤地萃","坤巽":"地風升","兌坎":"澤水困","坎巽":"水風井",
    "兌離":"澤火革","離巽":"火風鼎","震震":"震為雷","艮艮":"艮為山","巽艮":"風山漸","震兌":"雷澤歸妹",
    "震離":"雷火豐","離艮":"火山旅","巽巽":"巽為風","兌兌":"兌為澤","巽坎":"風水渙","坎兌":"水澤節",
    "巽兌":"風澤中孚","震艮":"雷山小過","坎離":"水火既濟","離坎":"火水未濟",
}
SHENG = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
KE = {"木":"土","土":"水","水":"火","火":"金","金":"木"}


def _normalize_number(value: str | int, name: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer-like value") from exc
    if number < 0:
        raise ValueError(f"{name} must be >= 0")
    return number


def _trigram_from_number(value: int) -> str:
    return {1:"乾",2:"兌",3:"離",4:"震",5:"巽",6:"坎",7:"艮",0:"坤"}[value % 8]


def _moving_line(a: int, b: int) -> int:
    remainder = (a + b) % 6
    return 6 if remainder == 0 else remainder


def _hexagram(upper: str, lower: str) -> dict[str, str]:
    return {
        "upper_trigram": upper,
        "lower_trigram": lower,
        "name": HEXAGRAM_BY_PAIR[upper + lower],
        "bits": TRIGRAM_BITS[lower] + TRIGRAM_BITS[upper],
        "line_order": LINE_ORDER,
    }


def _body_use_relation(body_element: str, use_element: str) -> str:
    if body_element == use_element:
        return "比和"
    if SHENG[body_element] == use_element:
        return "體生用"
    if SHENG[use_element] == body_element:
        return "用生體"
    if KE[body_element] == use_element:
        return "體剋用"
    if KE[use_element] == body_element:
        return "用剋體"
    raise AssertionError("unreachable five-element relation")


def derive(
    *,
    a: str | int,
    b: str | int,
    upper_trigram: str | None = None,
    lower_trigram: str | None = None,
    hexagram: str | None = None,
    moving_line: int | None = None,
) -> dict[str, Any]:
    """Derive deterministic facts while preserving the supplied Cast Fact identity."""
    a_int = _normalize_number(a, "a")
    b_int = _normalize_number(b, "b")
    expected_upper = _trigram_from_number(a_int)
    expected_lower = _trigram_from_number(b_int)
    expected_moving = _moving_line(a_int, b_int)
    primary = _hexagram(expected_upper, expected_lower)

    assertions = {
        "upper_trigram": (upper_trigram, expected_upper),
        "lower_trigram": (lower_trigram, expected_lower),
        "hexagram": (hexagram, primary["name"]),
        "moving_line": (moving_line, expected_moving),
    }
    for field, (supplied, expected) in assertions.items():
        if supplied is not None and supplied != expected:
            raise ValueError(
                f"cast fact mismatch for {field}: supplied={supplied!r}, expected={expected!r}"
            )

    bits = primary["bits"]

    # Mutual hexagram: lower mutual = lines 2-4; upper mutual = lines 3-5.
    mutual_lower = BITS_TRIGRAM[bits[1:4]]
    mutual_upper = BITS_TRIGRAM[bits[2:5]]
    mutual = _hexagram(mutual_upper, mutual_lower)

    # Changed hexagram: flip only the fixed moving line.
    changed_bits = list(bits)
    changed_bits[expected_moving - 1] = "0" if changed_bits[expected_moving - 1] == "1" else "1"
    changed_text = "".join(changed_bits)
    changed = _hexagram(BITS_TRIGRAM[changed_text[3:]], BITS_TRIGRAM[changed_text[:3]])

    # Body/use: moving trigram = 用; static trigram = 體.
    if expected_moving <= 3:
        use_trigram, body_trigram = expected_lower, expected_upper
    else:
        use_trigram, body_trigram = expected_upper, expected_lower

    body_element = TRIGRAM_ELEMENT[body_trigram]
    use_element = TRIGRAM_ELEMENT[use_trigram]

    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "authority": "deterministic-derived-facts-only",
        "cast_fact": {
            "a": f"{a_int:03d}",
            "b": f"{b_int:03d}",
            "upper_trigram": expected_upper,
            "lower_trigram": expected_lower,
            "hexagram": primary["name"],
            "moving_line": expected_moving,
            "line_order": LINE_ORDER,
        },
        "derived": {
            "mutual_hexagram": mutual,
            "changed_hexagram": changed,
            "body": {"trigram": body_trigram, "element": body_element, "source": "static-trigram"},
            "use": {"trigram": use_trigram, "element": use_element, "source": "moving-trigram"},
            "body_use_relation": _body_use_relation(body_element, use_element),
        },
        "rules": {
            "mutual": "lower=lines2-4; upper=lines3-5",
            "changed": "flip-moving-line-yin-yang-only",
            "body_use": "moving-trigram=use; static-trigram=body",
            "five_elements": "乾兌金;震巽木;坎水;離火;坤艮土",
        },
        "interpretation_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Meihua downstream derivation")
    parser.add_argument("--a", required=True)
    parser.add_argument("--b", required=True)
    parser.add_argument("--upper-trigram")
    parser.add_argument("--lower-trigram")
    parser.add_argument("--hexagram")
    parser.add_argument("--moving-line", type=int)
    args = parser.parse_args()
    try:
        payload = derive(
            a=args.a,
            b=args.b,
            upper_trigram=args.upper_trigram,
            lower_trigram=args.lower_trigram,
            hexagram=args.hexagram,
            moving_line=args.moving_line,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
