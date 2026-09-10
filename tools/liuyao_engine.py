#!/usr/bin/env python3
"""Zero-dependency deterministic Liuyao chart core.

Input is a fixed six-line cast (6/7/8/9, bottom-to-top). This module does not
cast, choose a question category, select a yongshen, or interpret auspiciousness.
It only converts fixed raw lines into reproducible structured chart facts.

Calendar-dependent facts are optional inputs. If ``day_gan`` is supplied, six
spirits are added. Month/day branch and xunkong may be supplied to add factual
flags without making a judgment.
"""
from __future__ import annotations

import argparse
import json
from typing import Any

ENGINE_NAME = "ai-divination-playbook/lightweight-liuyao"
ENGINE_VERSION = "1"
LINE_ORDER = "bottom-to-top"

TRIGRAM_NAME = {
    "111": "乾", "110": "兌", "101": "離", "100": "震",
    "011": "巽", "010": "坎", "001": "艮", "000": "坤",
}
TRIGRAM_BITS = {v: k for k, v in TRIGRAM_NAME.items()}
PALACE_WUXING = {
    "乾": "金", "兌": "金", "離": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土",
}
NAJIA = {
    "乾": ("甲", "子寅辰", "壬", "午申戌"),
    "坎": ("戊", "寅辰午", "戊", "申戌子"),
    "艮": ("丙", "辰午申", "丙", "戌子寅"),
    "震": ("庚", "子寅辰", "庚", "午申戌"),
    "巽": ("辛", "丑亥酉", "辛", "未巳卯"),
    "離": ("己", "卯丑亥", "己", "酉未巳"),
    "坤": ("乙", "未巳卯", "癸", "丑亥酉"),
    "兌": ("丁", "巳卯丑", "丁", "亥酉未"),
}
ZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}
GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"
SIX_SPIRITS = ("青龍", "朱雀", "勾陳", "螣蛇", "白虎", "玄武")
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

GUA64 = {
    "111111":"乾為天","011111":"天風姤","001111":"天山遯","000111":"天地否",
    "000011":"風地觀","000001":"山地剝","000101":"火地晉","111101":"火天大有",
    "110110":"兌為澤","010110":"澤水困","000110":"澤地萃","001110":"澤山咸",
    "001010":"水山蹇","001000":"地山謙","001100":"雷山小過","110100":"雷澤歸妹",
    "101101":"離為火","001101":"火山旅","011101":"火風鼎","010101":"火水未濟",
    "010001":"山水蒙","010011":"風水渙","010111":"天水訟","101111":"天火同人",
    "100100":"震為雷","000100":"雷地豫","010100":"雷水解","011100":"雷風恆",
    "011000":"地風升","011010":"水風井","011110":"澤風大過","100110":"澤雷隨",
    "011011":"巽為風","111011":"風天小畜","101011":"風火家人","100011":"風雷益",
    "100111":"天雷無妄","100101":"火雷噬嗑","100001":"山雷頤","011001":"山風蠱",
    "010010":"坎為水","110010":"水澤節","100010":"水雷屯","101010":"水火既濟",
    "101110":"澤火革","101100":"雷火豐","101000":"地火明夷","010000":"地水師",
    "001001":"艮為山","101001":"山火賁","111001":"山天大畜","110001":"山澤損",
    "110101":"火澤睽","110111":"天澤履","110011":"風澤中孚","001011":"風山漸",
    "000000":"坤為地","100000":"地雷復","110000":"地澤臨","111000":"地天泰",
    "111100":"雷天大壯","111110":"澤天夬","111010":"水天需","000010":"水地比",
}

# (flipped positions from pure palace hexagram, shi position, type)
PALACE_SEQUENCE = (
    (frozenset(), 6, "本宮"),
    (frozenset({0}), 1, "一世"),
    (frozenset({0, 1}), 2, "二世"),
    (frozenset({0, 1, 2}), 3, "三世"),
    (frozenset({0, 1, 2, 3}), 4, "四世"),
    (frozenset({0, 1, 2, 3, 4}), 5, "五世"),
    (frozenset({0, 1, 2, 4}), 4, "遊魂"),
    (frozenset({4}), 3, "歸魂"),
)


def _palace_table() -> dict[str, tuple[str, str, int]]:
    out: dict[str, tuple[str, str, int]] = {}
    for palace, tri_bits in TRIGRAM_BITS.items():
        base = tri_bits + tri_bits
        for flips, shi, gua_type in PALACE_SEQUENCE:
            bits = "".join(str(1 - int(c)) if i in flips else c for i, c in enumerate(base))
            out[bits] = (palace, gua_type, shi)
    return out


PALACE_TABLE = _palace_table()


def parse_raw_lines(raw: str | list[int] | tuple[int, ...]) -> list[int]:
    if isinstance(raw, str):
        text = raw.replace(",", "").replace(" ", "").strip()
        values = [int(ch) for ch in text] if text else []
    else:
        values = [int(v) for v in raw]
    if len(values) != 6 or any(v not in {6, 7, 8, 9} for v in values):
        raise ValueError("raw lines must be exactly six values in {6,7,8,9}, bottom-to-top")
    return values


def raw_to_bits(lines: list[int]) -> str:
    return "".join("1" if v in {7, 9} else "0" for v in lines)


def changed_bits(bits: str, moving_positions: list[int]) -> str:
    moving = set(moving_positions)
    return "".join(str(1 - int(c)) if i + 1 in moving else c for i, c in enumerate(bits))


def six_relative(line_wx: str, palace_wx: str) -> str:
    if line_wx == palace_wx:
        return "兄弟"
    if SHENG[line_wx] == palace_wx:
        return "父母"
    if SHENG[palace_wx] == line_wx:
        return "子孫"
    if KE[line_wx] == palace_wx:
        return "官鬼"
    return "妻財"


def six_spirit_start(day_gan: str) -> int:
    if day_gan not in GAN:
        raise ValueError("day_gan must be one of 甲乙丙丁戊己庚辛壬癸")
    return {"甲":0,"乙":0,"丙":1,"丁":1,"戊":2,"己":3,"庚":4,"辛":4,"壬":5,"癸":5}[day_gan]


def _ying_position(shi: int) -> int:
    return shi + 3 if shi <= 3 else shi - 3


def _flags(zhi: str, month_branch: str | None, day_branch: str | None,
           xunkong: tuple[str, str] | None) -> dict[str, bool] | None:
    if month_branch is None and day_branch is None and xunkong is None:
        return None
    zi = ZHI.index(zhi)
    return {
        "旬空": bool(xunkong and zhi in xunkong),
        "月破": bool(month_branch and zi == (ZHI.index(month_branch) + 6) % 12),
        "日沖": bool(day_branch and zi == (ZHI.index(day_branch) + 6) % 12),
    }


def chart(bits: str, *, day_gan: str | None = None, month_branch: str | None = None,
          day_branch: str | None = None, xunkong: tuple[str, str] | None = None) -> dict[str, Any]:
    if len(bits) != 6 or any(c not in "01" for c in bits):
        raise ValueError("bits must be six binary digits, bottom-to-top")
    lower, upper = bits[:3], bits[3:]
    palace, gua_type, shi = PALACE_TABLE[bits]
    palace_wx = PALACE_WUXING[palace]
    in_gan, in_zhi, _, _ = NAJIA[TRIGRAM_NAME[lower]]
    _, _, out_gan, out_zhi = NAJIA[TRIGRAM_NAME[upper]]
    gans = [in_gan] * 3 + [out_gan] * 3
    zhis = list(in_zhi) + list(out_zhi)
    ying = _ying_position(shi)
    spirit_start = six_spirit_start(day_gan) if day_gan else None
    lines = []
    for i, (gan, zhi) in enumerate(zip(gans, zhis), start=1):
        wx = ZHI_WUXING[zhi]
        lines.append({
            "position": i,
            "yin_yang": "yang" if bits[i-1] == "1" else "yin",
            "najia": f"{gan}{zhi}",
            "gan": gan,
            "zhi": zhi,
            "five_element": wx,
            "six_relative": six_relative(wx, palace_wx),
            "shi_ying": "世" if i == shi else ("應" if i == ying else None),
            "six_spirit": SIX_SPIRITS[(spirit_start + i - 1) % 6] if spirit_start is not None else None,
            "flags": _flags(zhi, month_branch, day_branch, xunkong),
        })
    return {
        "bits": bits,
        "name": GUA64[bits],
        "lower_trigram": TRIGRAM_NAME[lower],
        "upper_trigram": TRIGRAM_NAME[upper],
        "palace": palace,
        "palace_element": palace_wx,
        "palace_type": gua_type,
        "shi_position": shi,
        "ying_position": ying,
        "lines": lines,
    }


def hidden_spirits(primary: dict[str, Any], *, day_gan: str | None = None) -> list[dict[str, Any]]:
    present = {line["six_relative"] for line in primary["lines"]}
    missing = [name for name in ("兄弟","父母","子孫","妻財","官鬼") if name not in present]
    if not missing:
        return []
    pure_bits = TRIGRAM_BITS[primary["palace"]] * 2
    pure = chart(pure_bits, day_gan=day_gan)
    out = []
    for relation in missing:
        for line in pure["lines"]:
            if line["six_relative"] == relation:
                out.append({
                    "six_relative": relation,
                    "position": line["position"],
                    "najia": line["najia"],
                    "five_element": line["five_element"],
                })
                break
    return out


def build_structured_fact(raw_lines: str | list[int] | tuple[int, ...], *,
                          day_gan: str | None = None,
                          month_branch: str | None = None,
                          day_branch: str | None = None,
                          xunkong: tuple[str, str] | None = None) -> dict[str, Any]:
    lines = parse_raw_lines(raw_lines)
    if month_branch is not None and month_branch not in ZHI:
        raise ValueError("month_branch must be a Chinese Earthly Branch")
    if day_branch is not None and day_branch not in ZHI:
        raise ValueError("day_branch must be a Chinese Earthly Branch")
    if xunkong is not None and (len(xunkong) != 2 or any(x not in ZHI for x in xunkong)):
        raise ValueError("xunkong must contain exactly two Chinese Earthly Branches")
    bits = raw_to_bits(lines)
    moving = [i for i, v in enumerate(lines, start=1) if v in {6, 9}]
    bian_bits = changed_bits(bits, moving)
    primary = chart(bits, day_gan=day_gan, month_branch=month_branch,
                    day_branch=day_branch, xunkong=xunkong)
    changed = chart(bian_bits, day_gan=day_gan, month_branch=month_branch,
                    day_branch=day_branch, xunkong=xunkong) if moving else None
    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "line_order": LINE_ORDER,
        "raw_lines": lines,
        "moving_positions": moving,
        "ben_gua": primary,
        "zhi_gua": changed,
        "fu_shen": hidden_spirits(primary, day_gan=day_gan),
        "calendar_context": {
            "day_gan": day_gan,
            "month_branch": month_branch,
            "day_branch": day_branch,
            "xunkong": list(xunkong) if xunkong else None,
            "status": "provided" if any(v is not None for v in (day_gan, month_branch, day_branch, xunkong)) else "unavailable",
        },
        "interpretation_authority": False,
        "yongshen_selection_authority": False,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Zero-dependency deterministic Liuyao chart core")
    p.add_argument("--lines", required=True, help="six 6/7/8/9 values, bottom-to-top")
    p.add_argument("--day-gan")
    p.add_argument("--month-branch")
    p.add_argument("--day-branch")
    p.add_argument("--xunkong", help="two branches, e.g. 申酉")
    return p


def main() -> int:
    args = build_parser().parse_args()
    xunkong = tuple(args.xunkong) if args.xunkong else None
    try:
        payload = build_structured_fact(
            args.lines,
            day_gan=args.day_gan,
            month_branch=args.month_branch,
            day_branch=args.day_branch,
            xunkong=xunkong,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
