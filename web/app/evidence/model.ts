import raw from "../../public/evidence.json";
import type { Call, Turn } from "../lib";

export type AuditScenario = {
  id: string;
  category: string;
  passed: boolean;
  failures: string[];
  task_correct: boolean;
  safety_correct: boolean;
  no_hallucinated_confirm: boolean;
  resolution_turns: number;
  expected: { name: string; arguments: Record<string, unknown> }[];
  expected_summary: string | null;
  replay: Turn[];
};

export const evidence = raw;
export const scenarios: AuditScenario[] = raw.redteam.scenarios;
export const REPO = "https://github.com/mekala27-45/frontdesk";
export const source = (path: string) => `${REPO}/blob/main/${path}`;
export const asset = (path: string) =>
  `${process.env.NEXT_PUBLIC_BASE_PATH || ""}/${path}`;
export const SHOWCASE = process.env.NEXT_PUBLIC_SHOWCASE === "true";
export const label = (value: string) => value.replaceAll("_", " ");

export function scenarioTitle(scenario: AuditScenario): string {
  const summaries = scenario.replay.map((turn) => turn.content_summary);
  if (scenario.expected.some((call) => call.arguments.category === "emergency"))
    return "Emergency handoff";
  const titles: Record<string, string> = {
    booking: "Choose a time, confirm a booking",
    changes: summaries.includes("cancel")
      ? "Cancel an owned booking"
      : "Change an owned booking",
    ambiguous: "Ask for the missing service",
    injection: "Refuse an instruction override",
    medical: "Keep the conversation in scope",
    privacy: "Refuse another patient's data",
    concurrency: "Concurrent claim, winning caller",
    boundaries: "Check a scheduling boundary",
  };
  return titles[scenario.category] || label(scenario.category);
}

export function matches(
  call: Call,
  expected: AuditScenario["expected"][number],
): boolean {
  return (
    call.name === expected.name &&
    Object.entries(expected.arguments).every(
      ([key, value]) => call.arguments[key] === value,
    )
  );
}
