"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  asset,
  evidence,
  label,
  matches,
  REPO,
  scenarios,
  scenarioTitle,
  SHOWCASE,
  source,
} from "./model";

const views = ["Overview", "Scenarios", "Architecture", "Provenance"] as const;
type View = (typeof views)[number];
const stages = [
  {
    title: "Authenticate the delivery",
    detail:
      "Meta signs the raw request body. The browser simulator receives a scoped synthetic identity. Both routes enter the same ingestion function.",
    file: "packages/api/src/frontdesk_api/app.py",
    test: "tests/test_webhook.py",
    tag: "HMAC + identity",
  },
  {
    title: "Restore state and deduplicate",
    detail:
      "A transaction-level advisory lock serializes each clinic/caller conversation. Unique message IDs prevent retries from repeating committed work.",
    file: "packages/agent/src/frontdesk_agent/engine.py",
    test: "tests/test_webhook.py",
    tag: "Durable conversation",
  },
  {
    title: "Apply the safety boundary",
    detail:
      "Emergency and scope rules run before the optional model. Refusals and handoffs are typed tool calls that the evaluator can inspect.",
    file: "packages/agent/src/frontdesk_agent/safety.py",
    test: "tests/test_redteam.py",
    tag: "Deterministic override",
  },
  {
    title: "Claim the appointment atomically",
    detail:
      "Provider locks prevent overlapping service bookings. Slot locks and a partial unique booking index protect the final claim. Ownership is checked inside tools.",
    file: "packages/scheduling/src/frontdesk_scheduling/engine.py",
    test: "tests/test_scheduling.py",
    tag: "PostgreSQL transaction",
  },
  {
    title: "Commit, then deliver",
    detail:
      "Outbound work commits with the booking. An ambiguous network send is held for human review. Calendar events use stable booking IDs and retry independently.",
    file: "packages/whatsapp/src/frontdesk_whatsapp/transport.py",
    test: "tests/test_adapters.py",
    tag: "Durable outbox",
  },
];

export default function EvidenceExplorer() {
  const [view, setView] = useState<View>("Overview");
  const [category, setCategory] = useState("all");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(scenarios[0].id);
  const [step, setStep] = useState(1);
  const [copied, setCopied] = useState(false);
  useEffect(() => {
    const sync = () => {
      const id = new URLSearchParams(window.location.hash.slice(1)).get(
        "scenario",
      );
      if (id && scenarios.some((scenario) => scenario.id === id)) {
        setSelected(id);
        setStep(1);
        setView("Scenarios");
      }
    };
    sync();
    window.addEventListener("hashchange", sync);
    return () => window.removeEventListener("hashchange", sync);
  }, []);
  function inspect(id: string) {
    setSelected(id);
    setStep(1);
    setView("Scenarios");
    setCopied(false);
    window.history.replaceState(null, "", `#scenario=${id}`);
  }
  function switchView(next: View) {
    setView(next);
    window.history.replaceState(
      null,
      "",
      next === "Scenarios" ? `#scenario=${selected}` : window.location.pathname,
    );
  }
  const current = scenarios.find((scenario) => scenario.id === selected)!;
  const shown = scenarios.filter(
    (scenario) =>
      (category === "all" || scenario.category === category) &&
      `${scenario.id} ${scenarioTitle(scenario)} ${scenario.replay.flatMap((turn) => turn.tool_calls.map((call) => call.name)).join(" ")}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  const visibleCalls = current.replay
    .slice(0, step)
    .flatMap((turn) => turn.tool_calls);
  const race = evidence.concurrency;
  const retry = evidence.idempotency;

  return (
    <main className="evidence-app">
      <a className="skip-link" href="#evidence-main">
        Skip to evidence
      </a>
      <aside className="evidence-sidebar">
        <Link className="brand" href="/">
          <span className="brand-icon">f</span>frontdesk
        </Link>
        <p className="eyebrow">ENGINEERING NOTEBOOK</p>
        <nav aria-label="Evidence sections">
          {views.map((item, index) => (
            <button
              key={item}
              className={view === item ? "current" : ""}
              aria-current={view === item ? "page" : undefined}
              onClick={() => switchView(item)}
            >
              <span>0{index + 1}</span>
              {item}
            </button>
          ))}
        </nav>
        <div className="evidence-side-note">
          <span className="evidence-live-dot" /> RECORDED TEST EVIDENCE
          <p>
            Explore the decisions.
            <br />
            Inspect the guarantees.
            <br />
            Read the implementation.
          </p>
        </div>
        <a className="evidence-source" href={REPO}>
          View repository ↗
        </a>
        {!SHOWCASE && (
          <Link className="evidence-source" href="/simulator/">
            Open local simulator ↗
          </Link>
        )}
      </aside>
      <div className="evidence-main" id="evidence-main">
        <header className="evidence-header">
          <div>
            <p className="eyebrow">FRONTDESK / {view.toUpperCase()}</p>
            <h1>
              {view === "Overview"
                ? "Promises, with proof."
                : view === "Scenarios"
                  ? "Every decision, inspectable."
                  : view === "Architecture"
                    ? "Follow the transaction."
                    : "Trace the evidence to its source."}
            </h1>
          </div>
          <span className="evidence-recorded">READ-ONLY EXPLORER</span>
        </header>
        <p className="evidence-intro">
          A WhatsApp booking agent built around retries, competing claims, and
          auditable safety decisions. Fictional clinic. Booking logistics only.
        </p>

        {view === "Overview" && (
          <>
            <div className="evidence-metrics">
              {[
                [
                  `${race.confirmed} / ${race.requests}`,
                  "wins the same slot",
                  `${race.rejected} clean rejections · ${race.errors} server errors`,
                ],
                [
                  `${evidence.redteam.passed} / ${evidence.redteam.total}`,
                  "scripted scenarios pass",
                  "Deterministic tool-call audit",
                ],
                [
                  `${evidence.tenant.explicitly_refused} / ${evidence.tenant.attempts}`,
                  "cross-tenant attempts refused",
                  "Scope checked inside every tool",
                ],
                [
                  `${evidence.quality.coverage_percent}%`,
                  "statement coverage",
                  "Application packages, measured test run",
                ],
              ].map(([value, name, note]) => (
                <article key={name}>
                  <strong>{value}</strong>
                  <h2>{name}</h2>
                  <p>{note}</p>
                </article>
              ))}
            </div>
            <div className="evidence-overview-grid">
              <section className="evidence-card evidence-race">
                <div className="evidence-card-heading">
                  <p className="eyebrow">THE SCHEDULING PROOF</p>
                  <span className="evidence-tag">REAL POSTGRES</span>
                </div>
                <h2>One slot. {race.requests} competing claims.</h2>
                <p>
                  The measured request outcomes, grouped by result. Each square
                  represents one claim, not its arrival order.
                </p>
                <div
                  className="claim-grid"
                  aria-label={`${race.confirmed} confirmed, ${race.rejected} rejected, ${race.errors} errors`}
                >
                  {Array.from({ length: race.requests }, (_, index) => (
                    <span
                      key={index}
                      className={
                        index < race.confirmed
                          ? "won"
                          : index < race.confirmed + race.rejected
                            ? "rejected"
                            : "failed"
                      }
                      aria-hidden="true"
                    >
                      {index < race.confirmed ? "✓" : "·"}
                    </span>
                  ))}
                </div>
                <div className="evidence-legend">
                  <span>
                    <i />
                    {race.confirmed} confirmed
                  </span>
                  <span>
                    <i />
                    {race.rejected} rejected
                  </span>
                </div>
                <div className="evidence-measure">
                  <strong>{race.duration_seconds.toFixed(3)}s</strong>
                  <span>
                    Local ASGI client · warm connection pool
                    <br />
                    {race.booking_rows} booking row persisted
                  </span>
                </div>
                <a href={source("tests/test_scheduling.py")}>
                  Inspect the concurrency test ↗
                </a>
              </section>
              <section className="evidence-card">
                <p className="eyebrow">START WITH A FAILURE MODE</p>
                <h2>Take a guided look.</h2>
                <p>
                  These are archived traces from the test run. No live API,
                  login, or patient input is required.
                </p>
                <div className="evidence-tour">
                  <button onClick={() => inspect(scenarios[0].id)}>
                    <b>01</b>
                    <span>
                      From request to confirmation
                      <small>
                        Availability, explicit consent, committed booking
                      </small>
                    </span>
                    <span>↗</span>
                  </button>
                  <button
                    onClick={() =>
                      inspect(
                        scenarios.find((s) =>
                          s.expected.some(
                            (c) => c.arguments.category === "emergency",
                          ),
                        )!.id,
                      )
                    }
                  >
                    <b>02</b>
                    <span>
                      When the agent must stop
                      <small>Emergency override and human handoff</small>
                    </span>
                    <span>↗</span>
                  </button>
                  <button
                    onClick={() =>
                      inspect(
                        scenarios.find((s) => s.category === "privacy")!.id,
                      )
                    }
                  >
                    <b>03</b>
                    <span>
                      A request for someone else&apos;s data
                      <small>Named refusal with an auditable reason</small>
                    </span>
                    <span>↗</span>
                  </button>
                  <button
                    onClick={() =>
                      inspect(
                        scenarios.find((s) => s.category === "concurrency")!.id,
                      )
                    }
                  >
                    <b>04</b>
                    <span>
                      Two callers compete for one slot
                      <small>
                        Inspect the winning caller&apos;s saved audit
                      </small>
                    </span>
                    <span>↗</span>
                  </button>
                </div>
              </section>
            </div>
            <div className="evidence-overview-grid evidence-bottom-grid">
              <section className="evidence-card">
                <p className="eyebrow">RETRY + RESTART</p>
                <h2>The second delivery does no extra work.</h2>
                <div className="evidence-flow">
                  <div>
                    <strong>{retry.deliveries}</strong>
                    <small>deliveries</small>
                  </div>
                  <span>→</span>
                  <div>
                    <strong>{retry.inbound_rows}</strong>
                    <small>inbound row</small>
                  </div>
                  <span>→</span>
                  <div>
                    <strong>{retry.booking_rows}</strong>
                    <small>booking row</small>
                  </div>
                </div>
                <p>
                  {retry.additional_outbound_on_retry} additional outbound
                  messages on retry. Persisted conversation resumed after
                  restart:{" "}
                  <b>{retry.restart_resumed ? "verified" : "not verified"}</b>.
                </p>
                <a href={source("tests/test_webhook.py")}>
                  Inspect the retry test ↗
                </a>
              </section>
              <section className="evidence-card">
                <p className="eyebrow">DAYLIGHT SAVING TIME</p>
                <h2>Local hours. Unambiguous UTC slots.</h2>
                <div className="dst-bars">
                  {[
                    ["Ordinary", evidence.dst.ordinary_slots],
                    ["Spring forward", evidence.dst.spring_slots],
                    ["Fall back", evidence.dst.fall_slots],
                  ].map(([name, count]) => (
                    <div key={name}>
                      <span>{name}</span>
                      <div>
                        <i
                          style={{
                            width: `${(Number(count) / Math.max(evidence.dst.ordinary_slots, evidence.dst.spring_slots, evidence.dst.fall_slots)) * 100}%`,
                          }}
                        />
                      </div>
                      <b>{count}</b>
                    </div>
                  ))}
                </div>
                <p>
                  {evidence.dst.timezone}. Transition dates:{" "}
                  {evidence.dst.spring_date} and {evidence.dst.fall_date}.
                  Counts use the test fixture&apos;s business hours.
                </p>
                <a
                  href={source(
                    "packages/scheduling/src/frontdesk_scheduling/slots.py",
                  )}
                >
                  Read the slot generator ↗
                </a>
              </section>
            </div>
          </>
        )}

        {view === "Scenarios" && (
          <>
            <div className="evidence-filters">
              <label>
                Search scenarios
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Try emergency, booking, or refuse"
                />
              </label>
              <label>
                Category
                <select
                  value={category}
                  onChange={(event) => setCategory(event.target.value)}
                >
                  <option value="all">All categories</option>
                  {Object.keys(evidence.redteam.categories).map((name) => (
                    <option key={name} value={name}>
                      {label(name)}
                    </option>
                  ))}
                </select>
              </label>
              <span aria-live="polite">
                {shown.length} of {scenarios.length} scenarios
              </span>
            </div>
            <div className="evidence-scenario-grid">
              <section
                className="evidence-scenario-list"
                aria-label="Recorded scenarios"
              >
                {shown.length ? (
                  shown.map((scenario) => (
                    <button
                      className={selected === scenario.id ? "selected" : ""}
                      key={scenario.id}
                      aria-pressed={selected === scenario.id}
                      onClick={() => inspect(scenario.id)}
                    >
                      <span>
                        <code>{scenario.id}</code>
                        <i>{scenario.passed ? "PASS" : "FAIL"}</i>
                      </span>
                      <b>{scenarioTitle(scenario)}</b>
                      <small>
                        {scenario.resolution_turns}{" "}
                        {scenario.resolution_turns === 1 ? "turn" : "turns"} ·{" "}
                        {label(scenario.category)}
                      </small>
                    </button>
                  ))
                ) : (
                  <p className="evidence-no-results">
                    No scenarios match. Try a different term or category.
                  </p>
                )}
              </section>
              <section
                className="evidence-card evidence-replay"
                aria-label="Scenario replay"
              >
                <div className="evidence-card-heading">
                  <p className="eyebrow">{current.id.toUpperCase()}</p>
                  <a href={source(`docs/replays/${current.id}.md`)}>
                    Raw audit ↗
                  </a>
                </div>
                <h2>{scenarioTitle(current)}</h2>
                <p className="evidence-replay-note">
                  Generated logistics summaries from persisted audit rows.
                  Original messages are never stored in the replay.
                </p>
                <div className="evidence-verdicts">
                  {[
                    ["Task", current.task_correct],
                    ["Safety", current.safety_correct],
                    ["Confirmation integrity", current.no_hallucinated_confirm],
                  ].map(([name, passed]) => (
                    <span key={String(name)}>
                      {passed ? "✓" : "×"} {name}
                    </span>
                  ))}
                </div>
                <div className="evidence-stepper">
                  <button
                    className="secondary"
                    disabled={step === 1}
                    onClick={() => setStep(step - 1)}
                    aria-label="Previous turn"
                  >
                    ←
                  </button>
                  <span aria-live="polite">
                    Turn <b>{step}</b> of {current.replay.length}
                  </span>
                  <button
                    className="primary"
                    disabled={step === current.replay.length}
                    onClick={() => setStep(step + 1)}
                    aria-label="Next turn"
                  >
                    Next turn →
                  </button>
                  <button onClick={() => setStep(current.replay.length)}>
                    Show all
                  </button>
                </div>
                <div className="evidence-progress" aria-hidden="true">
                  {current.replay.map((_, index) => (
                    <i key={index} className={index < step ? "revealed" : ""} />
                  ))}
                </div>
                <div className="evidence-trace">
                  {current.replay.slice(0, step).map((turn, index) => (
                    <article
                      className={
                        turn.tool_calls.some((call) =>
                          /refuse|escalate/.test(call.name),
                        )
                          ? "safety"
                          : ""
                      }
                      key={`${current.id}-${index}`}
                    >
                      <span className="evidence-turn-number">{index + 1}</span>
                      <div>
                        <h3>{label(turn.content_summary)}</h3>
                        {!turn.tool_calls.length && (
                          <p>No tool call was recorded for this turn.</p>
                        )}
                        {turn.tool_calls.map((call, callIndex) => (
                          <details key={callIndex} open>
                            <summary>
                              <code>{call.name}</code>
                              <span
                                className={
                                  call.result.ok
                                    ? "result-ok"
                                    : "result-refused"
                                }
                              >
                                {call.result.code}
                              </span>
                            </summary>
                            <pre>
                              {JSON.stringify(
                                {
                                  arguments: Object.fromEntries(
                                    Object.entries(call.arguments).filter(
                                      ([, value]) => value !== null,
                                    ),
                                  ),
                                  result: call.result,
                                },
                                null,
                                2,
                              )}
                            </pre>
                          </details>
                        ))}
                      </div>
                    </article>
                  ))}
                </div>
                <div className="evidence-contract">
                  <h3>The expected contract</h3>
                  <p>
                    Expected tool names and argument values are checked against
                    the saved trace. Status below follows the turns revealed
                    above.
                  </p>
                  {current.expected.map((item, index) => (
                    <div key={index}>
                      <span
                        className={
                          visibleCalls.some((call) => matches(call, item))
                            ? "contract-met"
                            : ""
                        }
                      >
                        {visibleCalls.some((call) => matches(call, item))
                          ? "✓ Observed"
                          : "Pending"}
                      </span>
                      <code>{item.name}</code>
                      <pre>{JSON.stringify(item.arguments, null, 2)}</pre>
                    </div>
                  ))}
                  {current.expected_summary && (
                    <div>
                      <span
                        className={
                          current.replay
                            .slice(0, step)
                            .some(
                              (turn) =>
                                turn.content_summary ===
                                current.expected_summary,
                            )
                            ? "contract-met"
                            : ""
                        }
                      >
                        {current.replay
                          .slice(0, step)
                          .some(
                            (turn) =>
                              turn.content_summary === current.expected_summary,
                          )
                          ? "✓ Observed"
                          : "Pending"}
                      </span>
                      <code>summary: {current.expected_summary}</code>
                    </div>
                  )}
                </div>
                <div className="evidence-replay-actions">
                  <button
                    onClick={async () => {
                      try {
                        await navigator.clipboard.writeText(
                          window.location.href,
                        );
                        setCopied(true);
                      } catch {
                        setCopied(false);
                      }
                    }}
                  >
                    {copied ? "Link copied ✓" : "Copy scenario link"}
                  </button>
                  <a href={source("redteam/score.py")}>Read the scorer ↗</a>
                </div>
              </section>
            </div>
          </>
        )}

        {view === "Architecture" && (
          <div className="evidence-architecture">
            <div>
              {stages.map((stage, index) => (
                <section
                  className="evidence-card evidence-stage"
                  key={stage.title}
                >
                  <span className="evidence-stage-number">0{index + 1}</span>
                  <div>
                    <span className="evidence-tag">{stage.tag}</span>
                    <h2>{stage.title}</h2>
                    <p>{stage.detail}</p>
                    <div className="evidence-inline-links">
                      <a href={source(stage.file)}>Implementation ↗</a>
                      <a href={source(stage.test)}>Tests ↗</a>
                    </div>
                  </div>
                </section>
              ))}
            </div>
            <aside className="evidence-card evidence-tradeoffs">
              <p className="eyebrow">DELIBERATE TRADEOFFS</p>
              <h2>Know where the guarantees stop.</h2>
              <h3>At-most-once automatic sends</h3>
              <p>
                A network timeout cannot tell us whether Meta accepted a
                message. Holding it for review may miss a delivery, but avoids
                blindly duplicating it.
              </p>
              <h3>Deterministic policy first</h3>
              <p>
                Free to run and reproducible. It understands a finite set of
                English patterns. The optional model only receives closed
                logistics intent labels.
              </p>
              <h3>Provider-level contention</h3>
              <p>
                Coarse provider locks simplify overlap correctness. Competing
                claims may be rejected even for separate slots on a busy
                provider.
              </p>
              <h3>A portfolio deployment</h3>
              <p>
                This site serves archived synthetic evidence. The API, live
                WhatsApp transport, and Google Calendar require separate
                deployment and credentials.
              </p>
              <a href={source("ARCHITECTURE.md")}>
                Read all design decisions ↗
              </a>
            </aside>
          </div>
        )}

        {view === "Provenance" && (
          <div className="evidence-overview-grid">
            <section className="evidence-card">
              <p className="eyebrow">CHAIN OF EVIDENCE</p>
              <h2>From database rows to this page.</h2>
              <ol className="evidence-provenance-steps">
                <li>Run the suite against real PostgreSQL in Docker.</li>
                <li>
                  Export synthetic relational audit rows and measured evidence.
                </li>
                <li>
                  Restore the snapshot in CI, compare replay rows, verify
                  booking rows, and independently rescore scenarios.
                </li>
                <li>
                  Render the README and this public data file from that verified
                  evidence. Any difference fails the publication gate.
                </li>
              </ol>
              <div className="evidence-downloads">
                <a className="primary" href={asset("evidence.json")} download>
                  Download evidence JSON ↓
                </a>
                <a
                  className="secondary"
                  href={source("artifacts/database.json")}
                >
                  Relational snapshot ↗
                </a>
              </div>
              <h3>Reproduce the verification</h3>
              <pre className="evidence-command">
                uv run python -m scripts.evidence_db{"\n"}uv run python -m
                scripts.check_published_numbers{"\n"}uv run python -m
                scripts.showcase
              </pre>
              <p>
                Start the local PostgreSQL container and apply migrations first.
                The <a href={source("README.md")}>README</a> has the complete
                setup.
              </p>
            </section>
            <section className="evidence-card">
              <p className="eyebrow">PROVENANCE RECORD</p>
              <h2>Recorded, never silently refreshed.</h2>
              <dl className="evidence-provenance">
                <dt>Scenarios measured</dt>
                <dd>{evidence.redteam.measured_at}</dd>
                <dt>Concurrency measured</dt>
                <dd>{race.measured_at}</dd>
                <dt>Coverage measured</dt>
                <dd>{evidence.quality.measured_at}</dd>
                <dt>Snapshot SHA-256</dt>
                <dd>
                  <code>{evidence.provenance.snapshot_sha256}</code>
                </dd>
                <dt>Verification</dt>
                <dd>{evidence.provenance.verification}</dd>
              </dl>
              <p>
                The digest identifies the exact archived snapshot. It is an
                integrity reference, not an independent attestation. Passing
                these scripted scenarios does not establish universal safety or
                production readiness.
              </p>
              <div className="evidence-inline-links">
                <a href={source("scripts/showcase.py")}>Public exporter ↗</a>
                <a href={source("scripts/check_published_numbers.py")}>
                  Database claim gate ↗
                </a>
              </div>
            </section>
          </div>
        )}

        <footer className="evidence-footer">
          <span>
            frontdesk <b>·</b> by Ajay Mekala
          </span>
          <span>
            Recorded synthetic evidence · No live bookings on this site
          </span>
          <a href={source("docs/case-study.md")}>Read the case study ↗</a>
        </footer>
      </div>
    </main>
  );
}
