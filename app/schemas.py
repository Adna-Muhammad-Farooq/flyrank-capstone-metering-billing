from pydantic import BaseModel, Field, model_validator


class UsageRequest(BaseModel):
    tenant_id: int = Field(gt=0)
    usage_type: str
    quantity: int = Field(gt=0)
    idempotency_key: str = Field(min_length=1, max_length=255)

    # Optional AI token details
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cached_tokens: int = Field(default=0, ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_token_usage(self):
        if self.usage_type == "ai_tokens":
            total = (
                self.input_tokens
                + self.output_tokens
                + self.reasoning_tokens
            )

            if total != self.quantity:
                raise ValueError(
                    "For ai_tokens, quantity must equal input + output + reasoning tokens"
                )

            if self.cached_tokens > self.input_tokens:
                raise ValueError(
                    "Cached tokens cannot exceed input tokens"
                )

        elif any((
            self.input_tokens,
            self.output_tokens,
            self.cached_tokens,
            self.reasoning_tokens
        )):
            raise ValueError(
                "Token details are only allowed for ai_tokens usage"
            )

        return self


class UsageResponse(BaseModel):
    message: str
    tenant_id: int
    usage_type: str
    quantity: int
    usage_event_id: int
    cost_micro_usd: int = 0