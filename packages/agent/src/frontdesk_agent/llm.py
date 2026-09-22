"""Optional closed-vocabulary planner; raw messages never leave the process."""
import json
import threading
from typing import Any, Literal
from frontdesk_core.contracts import StrictModel

Intent = Literal["book", "reschedule", "cancel", "my bookings", "human"]

class Plan(StrictModel):
    intent: Intent

class BudgetExceeded(ValueError):
    pass

class LiteLLMPolicy:
    def __init__(self, model: str, budget_usd: float = 0.05) -> None:
        self.model, self.budget_usd, self.reserved_usd = model, budget_usd, 0.0
        self.lock = threading.Lock()

    def plan(self, cues: list[Intent]) -> Plan:
        import litellm
        if not cues:
            raise ValueError("No safe intent cues")
        messages = [{"role":"system","content":"Choose one logistics intent from the supplied closed vocabulary. Call choose_intent."},{"role":"user","content":json.dumps(cues)}]
        # Reserve a conservative priced token bound before every request. Unknown
        # model prices fail closed. The optional run is bounded to this instance.
        prompt_cost, output_cost = litellm.cost_per_token(model=self.model, prompt_tokens=4096, completion_tokens=128)
        reservation = float(prompt_cost + output_cost)
        if reservation <= 0:
            raise ValueError("Model must have known positive pricing")
        with self.lock:
            if self.reserved_usd + reservation > self.budget_usd:
                raise BudgetExceeded("Optional model budget exhausted")
            self.reserved_usd += reservation
        response: Any = litellm.completion(model=self.model, messages=messages, tools=[{"type":"function","function":{"name":"choose_intent","description":"Select one allowed logistics intent","parameters":Plan.model_json_schema()}}], tool_choice={"type":"function","function":{"name":"choose_intent"}}, max_tokens=128, temperature=0)
        plan = Plan.model_validate_json(response.choices[0].message.tool_calls[0].function.arguments)
        if plan.intent not in cues:
            raise ValueError("Planner selected an ungrounded intent")
        return plan

