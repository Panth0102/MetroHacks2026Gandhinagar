"""Sales-proposal copy generation.

Two paths, both returning a validated ProposalContent:
  * AI path  — Anthropic Claude, strict JSON, bounded retries, server-side only.
  * Template — deterministic, evidence-only fallback when AI is disabled or fails.

Business facts come from the context (built elsewhere); this module only turns
them into prose. It never invents demographics, impressions, conversions, or
guaranteed revenue. `_llm_complete` is the single external call site and is
monkeypatched in tests, so the suite never makes a live API call.
"""
from __future__ import annotations

import json

from pydantic import ValidationError

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.proposal import ProposalContent, ProposalContext, ProposalMetric

logger = get_logger("proposal.generation")


class AIGenerationError(RuntimeError):
    pass


_SYSTEM_PROMPT = (
    "You are a commercial real-estate analyst writing a concise, factual one-page "
    "sales proposal for a metro-station commercial space. You must ONLY use facts "
    "present in the provided JSON context. NEVER invent passenger demographics, "
    "unique visitors, advertising impressions, conversion rates, sales uplift, "
    "guaranteed revenue, official statistics, or verified market prices. Describe "
    "passenger figures exactly as 'observed passenger entries' for the stated period. "
    "Always describe the price as an indicative estimate, not a verified or approved rate. "
    "Respond with ONLY a JSON object (no markdown, no prose) matching exactly these keys: "
    "title (string), executive_summary (string), location_highlights (array of strings), "
    "verified_metrics (array of {label, value}), commercial_opportunity (string), "
    "pricing_summary (string), suggested_usage (string), call_to_action (string), "
    "assumptions_and_limitations (array of strings)."
)


def _llm_complete(system: str, user: str) -> str:  # pragma: no cover - patched in tests
    """The one external AI call. Isolated so tests can monkeypatch it."""
    import anthropic

    client = anthropic.Anthropic(
        api_key=settings.anthropic_api_key, timeout=settings.ai_request_timeout
    )
    msg = client.messages.create(
        model=settings.ai_model,
        max_tokens=settings.ai_max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(getattr(b, "text", "") for b in msg.content)


def _extract_json(raw: str) -> dict | None:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1] if "```" in text[3:] else text
        text = text.removeprefix("json").strip("` \n")
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        data = json.loads(text[start : end + 1])
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def generate_with_ai(context: ProposalContext) -> ProposalContent:
    """Call the LLM with a bounded retry on malformed output; raise on failure."""
    user = "Proposal context JSON:\n" + json.dumps(context.model_dump(mode="json"))
    last_err: str = "no response"
    for attempt in range(settings.ai_max_retries + 1):
        raw = _llm_complete(_SYSTEM_PROMPT, user)
        data = _extract_json(raw)
        if data is None:
            last_err = "model did not return valid JSON"
            continue
        try:
            return ProposalContent(**data)
        except ValidationError as exc:
            last_err = f"schema validation failed ({exc.error_count()} errors)"
            logger.warning("AI proposal attempt %s rejected: %s", attempt + 1, last_err)
    raise AIGenerationError(last_err)


def build_template_content(context: ProposalContext) -> ProposalContent:
    """Deterministic, fact-only proposal. Used when AI is unavailable or fails."""
    st = context.station
    sp = context.space
    ff = context.footfall
    pr = context.pricing
    ui = context.user_input

    category = ui.get("tenant_category") or "a suitable commercial tenant"
    business = ui.get("business_name")
    audience = ui.get("business_name") and ui.get("target_audience")

    space_type = str(sp.get("space_type", "space")).replace("_", " ")
    currency = pr.get("currency", "INR")
    price = pr.get("indicative_monthly_price")
    available = pr.get("available")

    metrics: list[ProposalMetric] = []
    if ff.get("avg_daily_entries") is not None:
        metrics.append(
            ProposalMetric(
                label="Observed avg daily entries",
                value=f"{round(ff['avg_daily_entries']):,}",
            )
        )
    if ff.get("peak_hour") is not None:
        metrics.append(ProposalMetric(label="Peak hour", value=f"{ff['peak_hour']:02d}:00"))
    if sp.get("area_sqm"):
        metrics.append(ProposalMetric(label="Area", value=f"{sp['area_sqm']} m²"))
    if sp.get("visibility_score"):
        metrics.append(ProposalMetric(label="Visibility", value=f"{sp['visibility_score']}/10"))
    if available and price is not None:
        metrics.append(
            ProposalMetric(label="Indicative monthly price", value=f"{currency} {price}")
        )
    metrics.append(
        ProposalMetric(label="Observations", value=f"{ff.get('observation_count', 0):,} records")
    )

    period = (
        f"{ff['start_date']} to {ff['end_date']}"
        if ff.get("start_date") and ff.get("end_date")
        else "the observed period"
    )

    highlights = [f"Located at {st['name']} ({st['code']}) metro station"]
    if st.get("line"):
        highlights.append(f"On the {st['line']} corridor")
    if sp.get("floor_description"):
        highlights.append(f"Placement: {sp['floor_description']}")
    if ff.get("peak_hour") is not None:
        highlights.append(f"Peak passenger activity around {ff['peak_hour']:02d}:00")

    summary = (
        f"{space_type.capitalize()} space {sp['space_code']} at {st['name']} is available for "
        f"{category}. Over {period}, the station recorded "
        f"{round(ff['avg_daily_entries']):,} observed passenger entries per day on average."
        if ff.get("avg_daily_entries") is not None
        else (
            f"{space_type.capitalize()} space {sp['space_code']} at {st['name']} is available for "
            f"{category}. Footfall data is limited for this station."
        )
    )

    opportunity = (
        f"The space suits {category}"
        + (f" (e.g. {business})" if business else "")
        + f". Steady commuter flow at {st['name']} offers consistent visibility for an on-site "
        f"{space_type}."
        + (f" Target audience noted: {ui['target_audience']}." if audience else "")
    )

    if available and price is not None:
        pricing_summary = (
            f"Indicative monthly asking price is {currency} {price} "
            f"(model {pr.get('model_version')}, data quality: {pr.get('data_quality')}). "
            "This is a model-generated estimate for discussion, not a verified market rate "
            "or an approved price."
        )
    else:
        pricing_summary = (
            "An indicative price is not available because required inputs are missing. "
            "Pricing will be confirmed on request."
        )

    usage = ui.get("campaign_objective") or (
        f"Operate a {space_type} serving commuters during peak and off-peak bands."
    )

    cta = (
        "To proceed, contact the metro commercial team to arrange a site viewing and confirm "
        "pricing and availability."
    )

    limitations = list(pr.get("limitations") or [])
    limitations.append(
        "Footfall figures are observed station entries, not unique visitors or advertising "
        "impressions."
    )
    limitations.append("Figures are from synthetic demonstration data and are not official statistics.")

    title = (
        f"{business} — {st['name']} {space_type} proposal"
        if business
        else f"{st['name']} {space_type} opportunity ({sp['space_code']})"
    )

    return ProposalContent(
        title=title[:200],
        executive_summary=summary,
        location_highlights=highlights,
        verified_metrics=metrics,
        commercial_opportunity=opportunity,
        pricing_summary=pricing_summary,
        suggested_usage=usage,
        call_to_action=cta,
        assumptions_and_limitations=limitations,
    )


def generate(context: ProposalContext, *, use_ai: bool) -> tuple[ProposalContent, str, str | None]:
    """Return (content, generation_source, ai_model). Falls back to the template
    on AI failure, and never mislabels a template as AI-generated."""
    if use_ai:
        try:
            content = generate_with_ai(context)
            return content, "ai", settings.ai_model
        except Exception as exc:  # noqa: BLE001 - provider/formatting errors vary; fall back safely
            logger.warning("AI generation failed, using template fallback: %s", type(exc).__name__)
    return build_template_content(context), "template", None
