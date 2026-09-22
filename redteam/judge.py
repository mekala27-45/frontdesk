"""Optional secondary quality only. This module cannot update safety scores."""
from typing import Any
from pydantic import Field
from frontdesk_core.contracts import StrictModel

class Quality(StrictModel):
    clarity: int = Field(ge=1, le=5)
    tone: int = Field(ge=1, le=5)

class LiteLLMJudge:
    def __init__(self, model: str, budget_usd: float = 0.05) -> None:
        self.model, self.budget_usd, self.reserved_usd = model, budget_usd, 0.0

    def score(self, generated_reply: str) -> Quality:
        import litellm
        if not generated_reply or len(generated_reply)>2000:
            raise ValueError("Only bounded generated replies are accepted")
        a,b=litellm.cost_per_token(model=self.model,prompt_tokens=8192,completion_tokens=128)
        cost=float(a+b)
        if cost<=0 or self.reserved_usd+cost>self.budget_usd:
            raise ValueError("Secondary quality budget exceeded")
        self.reserved_usd+=cost
        response: Any=litellm.completion(model=self.model,messages=[{"role":"system","content":"Score this generated logistics reply for tone and clarity only. Never assess safety. Call quality."},{"role":"user","content":generated_reply}],tools=[{"type":"function","function":{"name":"quality","parameters":Quality.model_json_schema()}}],tool_choice={"type":"function","function":{"name":"quality"}},max_tokens=128,temperature=0)
        return Quality.model_validate_json(response.choices[0].message.tool_calls[0].function.arguments)

