"""Model pricing table and cost math.

Prices are USD per 1M tokens. Source: OpenAI and Cohere public pricing pages,
verified 2026-04-15. Update this file when providers change prices.
"""

from __future__ import annotations

PRICING_PER_1M: dict[str, dict[str, float]] = {
    # OpenAI chat models
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "o3": {"input": 2.00, "output": 8.00},
    "o3-mini": {"input": 1.10, "output": 4.40},
    # OpenAI embeddings (input-only)
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "text-embedding-3-large": {"input": 0.13, "output": 0.0},
}


def price_for(model: str) -> dict[str, float]:
    """Return {'input', 'output'} USD-per-1M for a model, or zeros if unknown."""
    return PRICING_PER_1M.get(model, {"input": 0.0, "output": 0.0})


def cost_for_call(model: str, input_tokens: int, output_tokens: int) -> float:
    """Compute USD cost for one LLM call."""
    price = price_for(model)
    return round(
        (input_tokens / 1_000_000) * price["input"]
        + (output_tokens / 1_000_000) * price["output"],
        6,
    )


def cost_from_usage(usage_metadata: dict) -> dict[str, float | int]:
    """Sum cost across a `get_usage_metadata_callback` result.

    `usage_metadata` maps model name -> {'input_tokens', 'output_tokens', 'total_tokens', ...}.
    Returns overall totals plus per-model breakdown suitable for run extra.
    """
    total_input = 0
    total_output = 0
    total_cost = 0.0
    per_model: dict[str, dict[str, float | int]] = {}

    for model, usage in (usage_metadata or {}).items():
        input_tokens = int(usage.get("input_tokens", 0) or 0)
        output_tokens = int(usage.get("output_tokens", 0) or 0)
        call_cost = cost_for_call(model, input_tokens, output_tokens)
        per_model[model] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": call_cost,
        }
        total_input += input_tokens
        total_output += output_tokens
        total_cost += call_cost

    return {
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_tokens": total_input + total_output,
        "cost_usd": round(total_cost, 6),
        "per_model": per_model,
    }
