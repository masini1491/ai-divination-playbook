#!/usr/bin/env python3
"""Canonical stochastic core for Tarot, Meihua, and Liuyao raw casting."""

from __future__ import annotations

from datetime import datetime, timezone
import secrets
from typing import Any
from zoneinfo import ZoneInfo

CORE_VERSION = "2"
ALGORITHM_VERSION = "2"
SCHEMA_VERSION = "4"
SOURCE = "divination-casting-randomizer-python"
SUPPORTED_METHODS = ("tarot", "plum", "liuyao")
TAIPEI_TZ = ZoneInfo("Asia/Taipei")

MAJORS = [
    "愚者", "魔術師", "女祭司", "女皇", "皇帝", "教皇", "戀人", "戰車", "力量", "隱者",
    "命運之輪", "正義", "倒吊人", "死神", "節制", "惡魔", "高塔", "星星", "月亮", "太陽",
    "審判", "世界",
]
RANKS = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "侍者", "騎士", "皇后", "國王"]
SUITS = ["杖", "杯", "劍", "錢"]
DECK = MAJORS + [f"{suit}{rank}" for suit in SUITS for rank in RANKS]
MAJOR_SHORT = {"魔術師": "魔術", "女祭司": "女祭", "命運之輪": "命輪", "倒吊人": "吊人"}
COURT_SHORT = {"侍者": "侍", "騎士": "騎", "皇后": "后", "國王": "王"}

TRIGRAM = {1: "乾", 2: "兌", 3: "離", 4: "震", 5: "巽", 6: "坎", 7: "艮", 0: "坤"}
HEXAGRAM = {
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

LIUYAO_POSITION_NAMES = ("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")
LIUYAO_LINE_META = {
    6: ("yin", True, "老陰"),
    7: ("yang", False, "少陽"),
    8: ("yin", False, "少陰"),
    9: ("yang", True, "老陽"),
}
UINT32_RANGE = 1 << 32


def randbelow(max_value: int) -> int:
    """Uniform integer in [0, max_value) using 32-bit rejection sampling."""
    if max_value <= 0:
        raise ValueError("max_value must be > 0")
    if max_value == 1:
        return 0
    if max_value > UINT32_RANGE:
        return secrets.randbelow(max_value)
    limit = UINT32_RANGE - (UINT32_RANGE % max_value)
    while True:
        value = secrets.randbits(32)
        if value < limit:
            return value % max_value


def fisher_yates(items: list[str]) -> list[str]:
    shuffled = list(items)
    for i in range(len(shuffled) - 1, 0, -1):
        j = randbelow(i + 1)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled


def short_name(name: str) -> str:
    if name in MAJOR_SHORT:
        return MAJOR_SHORT[name]
    for suit in SUITS:
        if name.startswith(suit):
            rank = name[len(suit):]
            return suit + COURT_SHORT.get(rank, rank)
    return name


def _draw_tarot_raw(count: int) -> dict[str, Any]:
    if not 1 <= count <= 24:
        raise ValueError("Tarot count must be between 1 and 24.")
    chosen = fisher_yates(DECK)[:count]
    cards = []
    for index, full_name in enumerate(chosen, start=1):
        orientation = "逆" if randbelow(2) else "正"
        short = short_name(full_name)
        cards.append({
            "index": index,
            "card": short,
            "full_name": full_name,
            "orientation": orientation,
            "shorthand": f"{short}{orientation}",
        })
    return {"count": count, "cards": cards}


def _cast_plum_raw() -> dict[str, Any]:
    a, b = randbelow(1000), randbelow(1000)
    upper, lower = TRIGRAM[a % 8], TRIGRAM[b % 8]
    rem = (a + b) % 6
    moving_line = 6 if rem == 0 else rem
    return {
        "a": f"{a:03d}",
        "b": f"{b:03d}",
        "upper_trigram": upper,
        "lower_trigram": lower,
        "hexagram": HEXAGRAM[upper + lower],
        "moving_line": moving_line,
        "casting_rule": "A%8→上卦；B%8→下卦；(A+B)%6→動爻；餘0分別視為坤／第6爻",
    }


def resolve_liuyao_coin_values(coin_values: list[int] | tuple[int, int, int]) -> dict[str, Any]:
    """Resolve one three-coin toss using canonical yin=2 / yang=3 mapping."""
    if len(coin_values) != 3 or any(v not in {2, 3} for v in coin_values):
        raise ValueError("Liuyao coin values must be exactly three values, each 2 or 3.")
    values = list(coin_values)
    line_value = sum(values)
    yin_yang, changing, line_type = LIUYAO_LINE_META[line_value]
    return {
        "coin_values": values,
        "coin_faces": ["yin" if v == 2 else "yang" for v in values],
        "value": line_value,
        "yin_yang": yin_yang,
        "changing": changing,
        "line_type": line_type,
    }


def _cast_liuyao_raw() -> dict[str, Any]:
    """Cast six lines bottom-to-top with three independent fair coins per line."""
    lines = []
    for position, position_name in enumerate(LIUYAO_POSITION_NAMES, start=1):
        values = [2 if randbelow(2) == 0 else 3 for _ in range(3)]
        line = resolve_liuyao_coin_values(values)
        line.update({"position": position, "position_name": position_name})
        lines.append(line)
    return {
        "cast_method": "three-coins",
        "line_order": "bottom-to-top",
        "coin_mapping": {"yin": 2, "yang": 3},
        "casting_rule": "每爻三枚獨立公平銅錢；陰=2、陽=3；合計6/7/8/9；6=老陰動、7=少陽靜、8=少陰靜、9=老陽動；由初爻至上爻起卦",
        "lines": lines,
    }


def _make_result_raw(method: str, count: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"method": method}
    if method in {"tarot", "both"}:
        if count is None:
            raise ValueError("Tarot count is required.")
        result["tarot"] = _draw_tarot_raw(count)
    if method in {"plum", "both"}:
        result["plum"] = _cast_plum_raw()
    if method == "liuyao":
        result["liuyao"] = _cast_liuyao_raw()
    return result


def execute_stochastic(
    command: str,
    *,
    count: int = 3,
    repeat: int = 1,
    counts: list[int] | None = None,
    method: str = "tarot",
    source_commit: str | None = None,
) -> dict[str, Any]:
    """Only canonical public stochastic API; timestamp and result are atomic."""
    if repeat < 1 or repeat > 100:
        raise ValueError("repeat must be between 1 and 100")
    utc = datetime.now(timezone.utc)
    if command in {"tarot", "plum", "liuyao", "both"}:
        results = [_make_result_raw(command, count) for _ in range(repeat)]
    elif command == "batch":
        if not counts or method not in {"tarot", "both"}:
            raise ValueError("batch requires counts and method tarot or both")
        if any(value < 1 or value > 24 for value in counts):
            raise ValueError("each count must be between 1 and 24")
        results = [_make_result_raw(method, value) for value in counts]
    else:
        raise ValueError(f"unsupported command: {command}")
    taipei = utc.astimezone(TAIPEI_TZ)
    return {
        "source": SOURCE,
        "algorithm_version": ALGORITHM_VERSION,
        "schema_version": SCHEMA_VERSION,
        "supported_methods": list(SUPPORTED_METHODS),
        "runtime_source_commit": source_commit or "unknown",
        "generated_at_utc": utc.isoformat(timespec="seconds"),
        "generated_at_taipei": taipei.isoformat(timespec="seconds"),
        "timezone": "Asia/Taipei",
        "rng": "secrets.randbits(32) + rejection sampling",
        "results": results,
    }
