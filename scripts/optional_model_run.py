"""Explicit paid opt-in, never used by the free demo or safety gate."""
import argparse
import json
import os
from frontdesk_agent.llm import LiteLLMPolicy
from redteam.judge import LiteLLMJudge

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--budget-usd", type=float, default=0.05)
    args=parser.parse_args()
    if not any(os.getenv(k) for k in ["OPENAI_API_KEY","ANTHROPIC_API_KEY","GEMINI_API_KEY"]):
        raise SystemExit("No model key: offline policy remains the default; no call made.")
    planner=LiteLLMPolicy(args.model,args.budget_usd/2)
    judge=LiteLLMJudge(args.model,args.budget_usd/2)
    plan=planner.plan(["book"])
    quality=judge.score("Please choose an available appointment time.")
    print(json.dumps({"optional_plan":plan.model_dump(),"secondary_quality":quality.model_dump(),"reserved_usd":planner.reserved_usd+judge.reserved_usd}))

