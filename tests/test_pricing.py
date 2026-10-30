import pytest

from app.pricing import calculate_token_cost


def test_zero_tokens():
    result = calculate_token_cost()

    assert result["total_cost_micro_usd"] == 0


def test_input_tokens():
    result = calculate_token_cost(input_tokens=1_000_000)

    assert result["total_cost_micro_usd"] == 1_000_000


def test_output_tokens():
    result = calculate_token_cost(output_tokens=500_000)

    assert result["total_cost_micro_usd"] == 2_000_000


def test_cached_tokens():
    result = calculate_token_cost(
        input_tokens=1_000_000,
        cached_tokens=200_000,
    )

    assert result["total_cost_micro_usd"] == 850_000


def test_reasoning_tokens():
    result = calculate_token_cost(reasoning_tokens=100_000)

    assert result["total_cost_micro_usd"] == 400_000


def test_combined_tokens():
    result = calculate_token_cost(
        input_tokens=1_000_000,
        output_tokens=500_000,
        cached_tokens=200_000,
        reasoning_tokens=100_000,
    )

    assert result["total_cost_micro_usd"] == 3_250_000


def test_negative_tokens_rejected():
    with pytest.raises(ValueError):
        calculate_token_cost(input_tokens=-1)


def test_cached_tokens_exceed_input():
    with pytest.raises(ValueError):
        calculate_token_cost(
            input_tokens=100,
            cached_tokens=200,
        )


def test_fractional_tokens_rejected():
    with pytest.raises(ValueError):
        calculate_token_cost(input_tokens=1.5)