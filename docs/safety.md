# Safety decisions

This is booking logistics only. The code does not diagnose, prescribe, assess symptoms, or store raw clinical content.

The deterministic emergency pattern check runs before conversation state handling, the optional planner, and booking tools. It emits a canonical emergency-services redirect and calls escalate_to_human. It also runs when the conversation is already escalated. Non-emergency medical and prescription questions produce refuse_out_of_scope with a named category.

The policy uses finite English patterns. Passing the scripted suite does not prove recognition of all emergencies, paraphrases or adversarial language. Never rely on this demonstration for emergency care.

The US crisis redirect is based on [SAMHSA's crisis lifeline guidance](https://www.samhsa.gov/mental-health/988). The user must not wait for the fictional front desk. Location-specific resources and a clinical safety review are outside scope.

Safety scoring reads stored tool calls. It has independent tests proving a refusal passes, friendly prose without a refusal fails, and missing evidence cannot pass. Optional model scores concern tone and clarity only.

Cross-patient access is enforced in SQL predicates, and foreign clinic/conversation identities raise an explicit denial. A shared demo ops token is not a production authorization system.

