"""Privacy-preserving automatic method routing for AI Divination.

For non-explicit methods, the server classifies a short, de-identified
question summary rather than trusting the ChatGPT tool-selection bias.
Reject obvious contact details; no raw conversation history is required.

Canonical intent rules: ai-divination-playbook/METHOD_ROUTING.md (2026-10-25).
"""
from __future__ import annotations

from typing import Any
import re

ROUTER_VERSION = "auto-routing-v2"
FUNCTION_METHOD = {
    "psychology_comparison": "tarot",
    "process_evolution": "meihua",
    "outcome_completion": "liuyao",
}
TOOLS = {
    "tarot": "draw_tarot",
    "meihua": "cast_meihua",
    "liuyao": "cast_liuyao",
}
REASONS = {
    "tarot": "psychology_or_comparison",
    "meihua": "process_or_evolution",
    "liuyao": "verifiable_outcome_or_completion",
}
EXPLICIT_ONLY_UNAVAILABLE = {"astrology", "ziwei"}


def route_plan(
    judgment_function: str,
    method_override: str = "auto",
    existing_cast: bool = False,
    has_completion_rule: bool = False,
    has_horizon: bool = False,
    tarot_count: int = 3,
) -> dict[str, Any]:
    """Choose exactly one method without drawing; fail closed on missing contract."""
    base: dict[str, Any] = {
        "router_version": ROUTER_VERSION,
        "judgment_function": judgment_function,
        "method_override": method_override,
    }
    if not isinstance(judgment_function, str) or judgment_function not in {*FUNCTION_METHOD, "unclear"}:
        return {**base, "status": "invalid_input", "reason_code": "invalid_judgment_function"}
    if not isinstance(method_override, str) or method_override not in {*TOOLS, "auto", *EXPLICIT_ONLY_UNAVAILABLE}:
        return {**base, "status": "invalid_input", "reason_code": "invalid_method_override"}
    if type(existing_cast) is not bool or type(has_completion_rule) is not bool or type(has_horizon) is not bool:
        return {**base, "status": "invalid_input", "reason_code": "boolean_flags_required"}
    if type(tarot_count) is not int or not (1 <= tarot_count <= 24):
        return {**base, "status": "invalid_input", "reason_code": "invalid_tarot_count"}

    # Existing cards/hexagram facts are immutable. Never reinterpret as new cast.
    if existing_cast:
        return {
            **base, "status": "existing_cast_preserved",
            "reason_code": "do_not_redraw",
            "next_step": "Use the supplied cards/hexagram; fixed Meihua/Liuyao facts go to derive_meihua/derive_liuyao.",
        }
    if method_override in EXPLICIT_ONLY_UNAVAILABLE:
        return {
            **base, "status": "unsupported_method",
            "reason_code": "explicit_only_not_in_this_mcp",
            "next_step": "Do not silently substitute Tarot, Meihua, or Liuyao; report that this private MCP currently supports only those three.",
        }
    if method_override == "auto" and judgment_function == "unclear":
        return {
            **base, "status": "needs_clarification",
            "reason_code": "judgment_function_unclear",
            "question": "你想看人物心態／選項比較、事件如何發展，還是某件事能否在期限內完成？",
        }

    selected = method_override if method_override != "auto" else FUNCTION_METHOD[judgment_function]
    if selected == "liuyao" and (not has_completion_rule or not has_horizon):
        if not has_completion_rule and not has_horizon:
            question = "這件事具體以什麼結果算完成，以及要看至哪個日期或期限？"
        elif not has_completion_rule:
            question = "這件事具體以什麼可驗證的結果算完成？"
        else:
            question = "你希望以哪個日期或期限作為是否完成的判定時間？"
        return {
            **base, "selected_method": selected,
            "status": "needs_clarification",
            "reason_code": "completion_contract_incomplete",
            "question": question,
        }
    return {
        **base,
        "status": "ready",
        "selected_method": selected,
        "selected_tool": TOOLS[selected],
        "selection_reason": "user_method_override" if method_override != "auto" else REASONS[selected],
        "tarot_count": tarot_count if selected == "tarot" else None,
    }


def execute_auto_route(plan: dict[str, Any], bridge_factory) -> dict[str, Any]:
    """Execute exactly one approved draw/cast, or return a no-draw verdict."""
    if plan.get("status") != "ready":
        return plan
    engine = bridge_factory()
    selected = plan["selected_method"]
    if selected == "tarot":
        result = engine.draw_tarot(plan["tarot_count"])
    elif selected == "meihua":
        result = engine.cast_meihua()
    elif selected == "liuyao":
        result = engine.cast_liuyao()
    else:
        raise RuntimeError("Unexpected selected method")
    return {**plan, "status": "cast_completed", "cast_result": result}


# A deliberately small, transparent intent classifier. This is NOT an LLM,
# not a factual mind-reading model, and doesn't infer user-specific history.
# Matching ordering implements METHOD_ROUTING.md's primary judgment function.
_HORIZON = re.compile(r'(?:截至|之前|以前|之內|以內|到|在).{0,18}(?:月底|年底|本週|下週|本月|下月|[0-9一二兩三四五六七八九十]+(?:天|日|週|個月|月|年))|(?:[0-9一二兩三四五六七八九十]+(?:天|日|週|個月|月|年)(?:內|之內|以內|前))|(?:週[一二三四五六日天]|星期[一二三四五六日天]).{0,3}(?:前|以前)')
_OUTCOME_QUERY = re.compile(r'是否|會不會|能否|能不能|可否|可不可以|會否|能成功嗎|能達成嗎')
_VERIFIABLE_ACTION = re.compile(r'正式交往|開始交往|成為情侶|結婚|簽約|簽訂|錄取|通過|完成|結案|交付|成立|批准|核准|回覆|回复|傳訊息|發訊息|聯絡|赴約|見面|成行|談成|付款|成交|成功|達成|獲選|入選|發佈|發布|停班停課')
_PROCESS = re.compile(r'發展|走向|演變|變化|轉折|後續|接下來|往後|長期關係|關係進展|如何發展|怎麼發展|怎麼演變|階段|節奏|趨勢|過程|下一步|未來方向|長期發展')
_PSYCHOLOGY = re.compile(r'為何|為什麼|怎麼想|如何看|怎麼看|定位|心態|動機|感受|感覺|想法|態度|印象|看法|喜歡|在意|感情觀|相處品質|猶豫|比較|哪一個|哪個|選哪|選擇|適合|優缺點|是否喜歡')
_PII = re.compile(r'(?:https?://|www\.|@|\+?\d[\d\s()\-]{7,}\d)', re.I)
_UNSCOPED = re.compile(r'^(?:占卜|幫我占卜|幫我占|看一下|幫我看看|占卜看看)[。？?！! ]*$')


def classify_summary(question_summary: str) -> dict[str, Any]:
    """Primary-function classification; never cast here.

    Input must be an anonymized functional summary, not the raw private chat.
    """
    if not isinstance(question_summary, str) or len(question_summary) > 240:
        return {'status': 'invalid_input', 'reason_code': 'invalid_summary_length'}
    summary = re.sub(r'\s+', '', question_summary.strip())
    if _PII.search(summary):
        return {'status': 'invalid_input', 'reason_code': 'possible_contact_or_url',
                'next_step': 'Remove identifying/contact information and provide only a short anonymous intent summary.'}
    if not summary or _UNSCOPED.fullmatch(summary):
        return {'status': 'needs_clarification', 'reason_code': 'question_identity_missing',
                'question': '你主要想占卜什麼問題？'}
    has_time = bool(_HORIZON.search(summary))
    has_outcome = bool(_OUTCOME_QUERY.search(summary) and _VERIFIABLE_ACTION.search(summary))
    psycho = bool(_PSYCHOLOGY.search(summary))
    evolution = bool(_PROCESS.search(summary))
    if has_outcome:
        method = 'outcome_completion'
    elif evolution and not (psycho and re.search(r'怎麼想|如何看|怎麼看|心態|感受|定位', summary)):
        method = 'process_evolution'
    elif psycho:
        method = 'psychology_comparison'
    elif evolution:
        method = 'process_evolution'
    else:
        return {'status': 'needs_clarification', 'reason_code': 'judgment_function_unclear',
                'question': '你想看對方心態、事情怎麼發展，還是某件事是否會完成？'}
    return {'status': 'classified', 'judgment_function': method,
            'has_completion_rule': has_outcome, 'has_horizon': has_time}


def route_from_summary(
    question_summary: str,
    method_override: str = 'auto',
    existing_cast: bool = False,
    has_completion_rule: bool = False,
    has_horizon: bool = False,
    tarot_count: int = 3,
) -> dict[str, Any]:
    """Canonical server-side route from anonymized intent summary.

    ChatGPT can supply context flags, but can never override a more concrete
    completion condition/horizon found within the summary. Explicit method
    override is resolved by existing route_plan logic.
    """
    if method_override not in {*TOOLS, 'auto', *EXPLICIT_ONLY_UNAVAILABLE}:
        return route_plan('unclear', method_override=method_override, existing_cast=existing_cast,
                          has_completion_rule=has_completion_rule, has_horizon=has_horizon, tarot_count=tarot_count)
    if type(existing_cast) is not bool or type(has_completion_rule) is not bool or type(has_horizon) is not bool:
        return {'router_version': ROUTER_VERSION, 'status': 'invalid_input', 'reason_code': 'boolean_flags_required'}
    if existing_cast:
        return route_plan('unclear', method_override=method_override, existing_cast=True,
                          has_completion_rule=has_completion_rule, has_horizon=has_horizon, tarot_count=tarot_count)
    if method_override != 'auto' and not question_summary:
        plan = route_plan('unclear', method_override=method_override,
                          has_completion_rule=has_completion_rule, has_horizon=has_horizon, tarot_count=tarot_count)
        return {**plan, 'routing_source': 'explicit_method_override'}
    info = classify_summary(question_summary)
    if info.get('status') == 'invalid_input':
        return {'router_version': ROUTER_VERSION, **info}
    if info.get('status') == 'needs_clarification' and method_override == 'auto':
        return {'router_version': ROUTER_VERSION, **info}
    if info.get('status') == 'needs_clarification':
        judgment = 'unclear'
    else:
        judgment = info['judgment_function']
    plan = route_plan(judgment, method_override=method_override, existing_cast=False,
                      has_completion_rule=has_completion_rule or info.get('has_completion_rule', False),
                      has_horizon=has_horizon or info.get('has_horizon', False),
                      tarot_count=tarot_count)
    return {**plan, 'routing_source': 'server_question_summary' if method_override=='auto' else 'explicit_method_override'}
