from decimal import Decimal, ROUND_HALF_UP

# Example prices in USD per 1 million tokens
TOKEN_PRICES = {
    "input": Decimal("1.00"),
    "output": Decimal("4.00"),
    "cached": Decimal("0.25"),
    "reasoning": Decimal("4.00")
}


def calculate_token_cost(
    input_tokens: int = 0,
    output_tokens: int = 0,
    cached_tokens: int = 0,
    reasoning_tokens: int = 0
):
    counts = (
        input_tokens,
        output_tokens,
        cached_tokens,
        reasoning_tokens
    )

    if any(type(count) is not int or count < 0 for count in counts):
        raise ValueError("Token counts must be non-negative integers")

    if cached_tokens > input_tokens:
        raise ValueError("Cached tokens cannot exceed input tokens")

    # Cached tokens are part of input tokens
    normal_input_tokens = input_tokens - cached_tokens

    # Reasoning tokens are billed at the output rate
    total_usd = (
        Decimal(normal_input_tokens) * TOKEN_PRICES["input"]
        + Decimal(output_tokens) * TOKEN_PRICES["output"]
        + Decimal(cached_tokens) * TOKEN_PRICES["cached"]
        + Decimal(reasoning_tokens) * TOKEN_PRICES["reasoning"]
    ) / Decimal(1_000_000)

    # Store cost in integer microdollars (1 USD = 1,000,000 microdollars)
    cost_micro_usd = int(
        (total_usd * Decimal(1_000_000)).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )

    return {
        "total_cost_micro_usd": cost_micro_usd,
        "total_cost_usd": str(total_usd)
    }