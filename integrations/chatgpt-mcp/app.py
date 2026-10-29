"""AI Divination P0 Streamable HTTP application for ASGI / Vercel.

No private reading data is stored; only canonical verified Python calculations.
"""
from contextlib import asynccontextmanager
from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from public_guard import PublicGuard
from auto_routing import route_from_summary, execute_auto_route, ROUTER_VERSION
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from bridge import DivinationBridge, SOURCE_COMMIT
from policy_adapter import policy_identity, get_policy_owner
from response_format import method_policy_output
from batch_cast import execute_batch, MAX_BATCH, RECEIPT_FORMAT

BASE = Path(__file__).resolve().parent
ENGINE = DivinationBridge(BASE / "canonical-repo")
MCP_RUNTIME_VERSION = "1.4.0-private-batch-interleaving"
INTERPRETATION_POLICY_VERSION = "canonical-owner-parity-v1"

mcp = MCPServer(
    "AI Divination Facts",
    version=MCP_RUNTIME_VERSION,
    instructions=(
        "Fact tools only: Tarot, Meihua and Liuyao. Preserve original raw cast "
        "and provenance. Results are symbolic, not certain predictions. "
        "When method is not specified, call auto_divination with a short anonymized question_summary, and let the SERVER choose the method. "
        "Avoid sending user question text, identity, or sensitive data as tool args. "
        "Do not redraw existing facts or invent failed casts. "
        "For existing fixed cards or hexagrams, set existing_cast=true with the known method_override "
        "to obtain pinned interpretation rules without any new draw/cast. "
        "For interpretation, use the full pinned method owner plus CHATGPT_OUTPUT.md from method_policy. "
        "If excerpts are omitted or an applicable conditional owner is truncated, "
        "call get_interpretation_policy to retrieve exact text before making claims. "
        "When the user requests multiple independent readings of any Tarot, Meihua, "
        "or Liuyao methods, including interleaved mixed-method sequences, "
        "prefer batch_divination (up to 12 each call) and preserve all labeled "
        "original receipts BEFORE prose interpretation; "
        "never redraw completed labels if interpretation context is truncated. "
        "Load complete method/output policy only once per distinct method for the batch. "
        "Only facts are calculated by this MCP; natural-language synthesis is done by ChatGPT. "
        "To verify that the web-connected plugin has the updated interpretation rules, "
        "check runtime_status.interpretation_policy_version and the get_interpretation_policy tool. "
        "A source commit alone cannot distinguish old and new interpretation-policy releases."
    ),
)


def _bridge():
    ENGINE.revalidate_source()
    return ENGINE


@mcp.tool()
def runtime_status() -> dict:
    """Verified canonical engine source and supported divination methods."""
    _bridge()
    return {"runtime_source_commit": SOURCE_COMMIT, "verified": True,
            "mcp_runtime_version": MCP_RUNTIME_VERSION,
            "interpretation_policy_version": INTERPRETATION_POLICY_VERSION,
            "batch_cast_capabilities": {"tool": "batch_divination", "receipt_format": RECEIPT_FORMAT,
                                        "max_items": MAX_BATCH,
                                        "mixed_methods": True, "interleaved_calls": True,
                                        "per_invocation_batch_id": True, "storage": "none"},
            "interpretation_policy_capabilities": {
                "complete_method_owner_by_default": True,
                "complete_output_contract_by_default": True,
                "policy_read_tool": "get_interpretation_policy",
                "existing_cast_preserves_facts_and_method_policy": True,
                "enabled_methods": ["tarot", "meihua", "liuyao"],
            },
            "methods": ["tarot", "plum", "liuyao"], "routing": ROUTER_VERSION,
            "routing_authority": "server_question_summary", "advertised_auto_tool": "auto_divination",
            "policy_pack": policy_identity(), "storage": "none"}


@mcp.tool()
def auto_divination(
    question_summary: str,
    method_override: str = "auto",
    existing_cast: bool = False,
    has_completion_rule: bool = False,
    has_horizon: bool = False,
    tarot_count: int = 3,
    include_policy_excerpts: bool = True,
) -> dict:
    """PREFERRED single entry for new readings. Server routes the question.

    First rewrite the user's question locally as a short, anonymized INTENT
    SUMMARY, e.g. `長期關係後續如何發展`, not private names or conversation text.
    Send ONLY that summary. Server determines:
    - motives, feelings, choices, comparisons -> Tarot
    - evolution, longer-term direction, turning points -> Meihua
    - ONE concrete verifiable event with outcome criterion and deadline -> Liuyao
    Default policy includes full canonical method and output owners. Other
    conditional owners may be truncated. To apply omitted sections, call
    get_interpretation_policy with exact owner and sequential offsets.
    When reinterpreting a fixed existing cast, set existing_cast=true and
    method_override to its known method; this returns policy without recasting.
    Set include_policy_excerpts=false for a compact evidence response: identical
    cast_result with policy identity only; fetch full policy before interpreting.
    A time window alone never implies Liuyao. Respect method_override when user
    explicitly requests tarot/meihua/liuyao. Flags has_completion_rule and
    has_horizon supplement the de-identified summary; if missing for Liuyao,
    ask one clarification without casting. Existing casts are NEVER redrawn.
    Stop on unsupported astrology/ziwei; don't silently substitute tools.
    When status=cast_completed, read original cast_result. Otherwise NO CAST.
    The original raw methods remain callable for backward compatibility but
    are not advertised in tools/list to fresh ChatGPT MCP scans.
    """
    plan = route_from_summary(
        question_summary=question_summary, method_override=method_override,
        existing_cast=existing_cast, has_completion_rule=has_completion_rule,
        has_horizon=has_horizon, tarot_count=tarot_count,
    )
    # Resolve and verify applicable pinned policy BEFORE any stochastic cast.
    # Missing/tampered policy must not consume RNG or create a partial reading.
    prepared = method_policy_output(plan, include_policy_excerpts)
    return execute_auto_route(prepared, _bridge)


@mcp.tool()
def batch_divination(items: list[dict]) -> dict:
    """PREFERRED for 2–12 independent readings; all three methods may alternate.

    Each item selects its own method (auto/tarot/meihua/liuyao) and receives
    one independent cast in its supplied order. Separate batch_divination and
    auto_divination calls may be interleaved freely: unique batch_id and
    receipt_id distinguish repeated labels across calls. The caller must
    preserve receipt records before subsequent calls or interpretation.

    Supply [{label, question_summary, method_override?, has_completion_rule?,
    has_horizon?, tarot_count?}]. Every label is unique, anonymized and stable.
    Validates ALL items before drawing; one independent canonical cast per item.
    Returns a compact, labeled original stochastic-fact receipt for EACH item
    including cards, A/B numbers, or six raw lines + coin triples, timestamps,
    provenance and SHA-256 bound to batch identity. Other deterministic chart
    details are deliberately omitted; use derive_meihua/derive_liuyao after
    preserving receipts. No repeated rule excerpts. Preserve every receipt
    immediately before interpreting; receipts are NOT server-persisted.
    A partial failure returns completed receipts; NEVER retry completed labels.
    Get full method/output rules separately once per distinct method.
    """
    return execute_batch(items, _bridge)


@mcp.tool()
def get_interpretation_policy(method: str, owner: str, offset: int = 0,
                              max_chars: int = 12000) -> dict:
    """Read complete exact-commit interpretation rules, with bounded pagination.

    Required core: method's TAROT/MEIHUA/LIUYAO.md and CHATGPT_OUTPUT.md.
    Conditional owners include QUESTION_DESIGN, INPUT_CONTRACT, LIFECYCLE,
    READING_RECORD, CROSS_VALIDATION and other eleven allowlisted documents.
    Read sequential chunks until next_offset is None; do not infer omitted text.
    A method-specific owner can be read only under that same method, preventing
    accidental cross-method interpretations; shared owners remain available.
    """
    _bridge()
    return get_policy_owner(method, owner, offset, max_chars)


@mcp.tool()
def draw_tarot(count: int = 3) -> dict:
    """Draw 1 to 24 Tarot cards using the pinned canonical stochastic engine."""
    return _bridge().draw_tarot(count)


@mcp.tool()
def cast_meihua() -> dict:
    """Cast Meihua A/B using canonical randomness and derive mutual/changed hexagrams."""
    return _bridge().cast_meihua()


@mcp.tool()
def cast_liuyao() -> dict:
    """Cast six three-coin lines and derive canonical Liuyao chart/calendar facts."""
    return _bridge().cast_liuyao()


@mcp.tool()
def derive_meihua(a: str, b: str, upper_trigram: str | None = None,
                  lower_trigram: str | None = None, hexagram: str | None = None,
                  moving_line: int | None = None) -> dict:
    """Derive facts from a fixed supplied Meihua A/B cast; never recast."""
    return _bridge().derive_meihua(a, b, upper_trigram=upper_trigram,
             lower_trigram=lower_trigram, hexagram=hexagram, moving_line=moving_line)


@mcp.tool()
def derive_liuyao(raw_lines: list[int], cast_timestamp: str) -> dict:
    """Derive chart from six fixed bottom-to-top 6/7/8/9 lines and original timestamp."""
    return _bridge().derive_liuyao(raw_lines, cast_timestamp)


def _allowed_hosts() -> list[str]:
    """Exact domain names: Vercel deployment URL plus known stable production aliases."""
    names = [
        "localhost", "127.0.0.1", "ai-divination-mcp-public-candidate.vercel.app",
        "ai-divination-mcp-public-candidate-masini1491-9205.vercel.app",
    ]
    for key in ("VERCEL_URL", "VERCEL_BRANCH_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
        name = os.getenv(key, "").lower().strip()
        if name and name.endswith(".vercel.app") and "/" not in name:
            names.append(name)
    return list(dict.fromkeys(names + [n + ":*" for n in names]))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Mounted MCP ASGI lifespan does not run automatically: run its manager here.
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="AI Divination Public MCP Candidate", lifespan=lifespan)


@app.get("/")
def root():
    return HTMLResponse('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>AI Divination</title><body><h1>AI Divination</h1><p>塔羅、梅花易數與六爻：ChatGPT 占卜引擎的雲端服務。</p><p>此服務提供象徵性解讀的計算工具，不保證預測真實事件，也不是醫療、法律、財務或心理專業建議。</p><p><a href="/privacy">Privacy</a> · <a href="/terms">Terms</a> · <a href="/support">Support</a></p></body></html>')


@app.get("/health")
def health() -> dict:
    _bridge()
    return {"status": "ok", "source_commit": SOURCE_COMMIT}


@app.get("/privacy")
def privacy():
    return HTMLResponse("""<!doctype html><html lang=zh-Hant><meta charset=utf-8><title>AI Divination Privacy</title><h1>Privacy Notice (Draft)</h1><p>The MCP tools accept only casting parameters and fixed cast values. No account login is required. Our application code does not intentionally store individual readings, messages, accounts, or uploaded files. We use Vercel to host the service; normal network/diagnostic logs may include IP addresses, request times and technical metadata. Do not include personal or sensitive information in tool arguments. ChatGPT conversations are governed separately by ChatGPT policies. Contact the maintainer through the Support page.</p></html>""")

@app.get("/terms")
def terms():
    return HTMLResponse("""<!doctype html><html lang=zh-Hant><meta charset=utf-8><title>AI Divination Terms</title><h1>Terms of Use (Draft)</h1><p>AI Divination provides optional symbolic divination computations for entertainment and reflection. Output does not establish facts or guarantee future events. Do not rely on it for professional health, financial, legal, or safety decisions. Do not attempt to abuse, overload, or bypass service protections. Service availability is not guaranteed. This is a public distribution candidate, not an approved ChatGPT Directory listing.</p></html>""")

@app.get("/support")
def support():
    return HTMLResponse("""<!doctype html><html lang=zh-Hant><meta charset=utf-8><title>AI Divination Support</title><h1>Support</h1><p>Report technical defects, privacy questions or feature requests via <a href="https://github.com/masini1491/ai-divination-playbook/issues">GitHub Issues</a>. Do not submit passwords, access tokens, or private sensitive data.</p></html>""")

@app.get("/.well-known/openai-apps-challenge")
def openai_challenge():
    value = os.getenv("DIVINATION_OPENAI_APPS_CHALLENGE", "")
    if not value or len(value) > 2048 or any(x in value for x in "\r\n"):
        return PlainTextResponse("Not found", status_code=404)
    return PlainTextResponse(value, headers={"Cache-Control":"no-store"})

security = TransportSecuritySettings(allowed_hosts=_allowed_hosts(), allowed_origins=[])
app.mount("/", mcp.streamable_http_app(
    transport_security=security, stateless_http=True, json_response=True,
    max_request_body_size=16384,
))

app.add_middleware(PublicGuard)
