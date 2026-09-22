"use client";
import Link from "next/link";
import { useState } from "react";
import { API, Call, Evidence, Scenario, Turn, getJSON } from "../lib";
import { SHOWCASE } from "../evidence/model";
import ShowcaseNotice from "../showcase-notice";
type Ops = {
  clinic: { id: string; name: string; timezone: string };
  bookings: {
    id: string;
    provider_id: string;
    status: string;
    starts_at: string;
  }[];
  providers: { id: string; name: string }[];
  escalations: { id: string; reason: string; conversation_id: string }[];
  conversations: { id: string; status: string; last_inbound_at: string }[];
  utilization: { provider_id: string; open: number; booked: number }[];
  evidence: Evidence;
};
export default function Console() {
  return SHOWCASE ? (
    <ShowcaseNotice feature="The operations console" />
  ) : (
    <LiveConsole />
  );
}
function LiveConsole() {
  const [token, setToken] = useState(""),
    [data, setData] = useState<Ops | null>(null),
    [error, setError] = useState(""),
    [tab, setTab] = useState("Today"),
    [replay, setReplay] = useState<Turn[]>([]),
    [replayTitle, setReplayTitle] = useState(""),
    [filter, setFilter] = useState("all"),
    [busy, setBusy] = useState(false);
  async function refresh() {
    setBusy(true);
    setError("");
    try {
      setData(await getJSON<Ops>("/ops", token));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function openReplay(id: string) {
    if (!data) return;
    try {
      const r = await getJSON<{ messages: Turn[] }>(
        "/ops/replay/" + id + "?clinic_id=" + data.clinic.id,
        token,
      );
      setReplay(r.messages);
      setReplayTitle(id);
      setTab("Replay");
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function resolve(id: string) {
    if (!data) return;
    try {
      const r = await fetch(
        API + "/ops/escalations/" + id + "/resolve?clinic_id=" + data.clinic.id,
        { method: "POST", headers: { Authorization: "Bearer " + token } },
      );
      if (!r.ok) throw new Error("Could not resolve escalation.");
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    }
  }
  const provider = (id: string) =>
    data?.providers.find((p) => p.id === id)?.name || "Provider";
  const score = data?.evidence.redteam,
    load = data?.evidence.concurrency;
  return (
    <main className="workspace">
      <nav className="sidebar">
        <Link className="brand" href="/">
          <span className="brand-icon">f</span>frontdesk
        </Link>
        <p className="nav-label">WORKSPACE</p>
        <Link className="nav-item" href="/simulator/">
          ◉ Conversation
        </Link>
        <Link className="nav-item active" href="/console/">
          ▦ Operations
        </Link>
        <div className="sidebar-bottom">
          <span className="avatar">R</span>
          <div>
            Ridgeview Clinic<small>Fictional demo workspace</small>
          </div>
        </div>
      </nav>
      <div className="main">
        <header>
          <div>
            <p className="eyebrow">RIDGEVIEW / OPERATIONS</p>
            <h1>A clear view of the day.</h1>
          </div>
          <button
            className="secondary"
            disabled={busy || !token}
            onClick={refresh}
          >
            ↻ Refresh
          </button>
        </header>
        <p className="page-intro">
          Appointments, human handoffs, and the evidence behind every decision.
        </p>
        <form
          className="connection"
          onSubmit={(e) => {
            e.preventDefault();
            void refresh();
          }}
        >
          <span className={"dot " + (data ? "" : "amber")} />
          <span>
            {data
              ? "Connected to " + data.clinic.name
              : "Connect to your clinic API"}
          </span>
          <input
            aria-label="Ops token"
            type="password"
            placeholder="Ops access token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            autoComplete="off"
          />
          <button disabled={busy || !token} className="primary">
            Connect
          </button>
        </form>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <div className="metrics">
          {[
            [
              "Today's appointments",
              data?.bookings.length,
              "Clinic local time",
            ],
            ["Open handoffs", data?.escalations.length, "Waiting for a human"],
            [
              "Scenario checks",
              score ? score.passed + "/" + score.total : undefined,
              "Deterministic tool audit",
            ],
            [
              "Concurrent claims",
              load ? load.confirmed + " winner" : undefined,
              load
                ? load.rejected + " clean rejections"
                : "Real Postgres evidence",
            ],
          ].map(([label, value, note]) => (
            <div className="metric" key={String(label)}>
              <p>{label}</p>
              <strong>{value ?? "N/A"}</strong>
              <small>{note}</small>
            </div>
          ))}
        </div>
        <div className="tabs">
          {["Today", "Handoffs", "Replay", "Scorecard", "Scheduling"].map(
            (t) => (
              <button
                className={tab === t ? "selected" : ""}
                key={t}
                onClick={() => setTab(t)}
              >
                {t}
              </button>
            ),
          )}
        </div>
        {tab === "Today" && (
          <section className="panel wide">
            <div className="panel-heading">
              <h2>Today&apos;s appointments</h2>
              <span className="badge">
                {data?.clinic.timezone || "CLINIC TIMEZONE"}
              </span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>TIME</th>
                  <th>PROVIDER</th>
                  <th>REFERENCE</th>
                  <th>STATUS</th>
                </tr>
              </thead>
              <tbody>
                {data?.bookings.map((b) => (
                  <tr key={b.id}>
                    <td>
                      {new Date(b.starts_at).toLocaleTimeString("en-US", {
                        timeZone: data.clinic.timezone,
                        hour: "numeric",
                        minute: "2-digit",
                      })}
                    </td>
                    <td>{provider(b.provider_id)}</td>
                    <td>
                      <code>{b.id.slice(-8)}</code>
                    </td>
                    <td>
                      <span className="pill">{b.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!data?.bookings.length && (
              <div className="empty">
                <span>◷</span>
                <h3>
                  {data ? "A little room in the day." : "Your day starts here."}
                </h3>
                <p>
                  {data
                    ? "No appointments are booked for today."
                    : "Connect to the API to see live appointments."}
                </p>
                <Link href="/simulator/">Open the conversation →</Link>
              </div>
            )}
          </section>
        )}
        {tab === "Handoffs" && (
          <section className="panel wide">
            <h2>Human handoff inbox</h2>
            {!data?.escalations.length && (
              <p className="muted">No open handoffs to show.</p>
            )}
            {data?.escalations.map((e) => (
              <article className="handoff" key={e.id}>
                <span className="pill amber">
                  {e.reason.replaceAll("_", " ")}
                </span>
                <code>{e.conversation_id.slice(-8)}</code>
                <button onClick={() => openReplay(e.conversation_id)}>
                  View sanitized turns
                </button>
                <button className="secondary" onClick={() => resolve(e.id)}>
                  Mark resolved
                </button>
              </article>
            ))}
          </section>
        )}
        {tab === "Replay" && (
          <div className="replay-grid">
            <section className="panel">
              <h2>Conversations</h2>
              {data?.conversations.map((c) => (
                <button
                  className="conversation-choice"
                  key={c.id}
                  onClick={() => openReplay(c.id)}
                >
                  <code>{c.id.slice(-12)}</code>
                  <small>{c.status}</small>
                </button>
              ))}
            </section>
            <section className="panel">
              <h2>Conversation replay</h2>
              <p className="muted">
                {replayTitle || "Choose a conversation or a scenario."}
              </p>
              {replay.map((t, i) => (
                <article
                  className={
                    "turn " +
                    (t.tool_calls.some((c: Call) =>
                      /refuse|escalate/.test(c.name),
                    )
                      ? "safety"
                      : "")
                  }
                  key={t.id || i}
                >
                  <p className="eyebrow">
                    TURN {i + 1} / {t.direction || "INBOUND SUMMARY"}
                  </p>
                  <p>{t.content_summary.replaceAll("_", " ")}</p>
                  {t.tool_calls.map((c, j) => (
                    <details key={j} open>
                      <summary>
                        <code>{c.name}</code>
                        <span className="pill">{c.result.code}</span>
                      </summary>
                      <pre>
                        {JSON.stringify(
                          { arguments: c.arguments, result: c.result },
                          null,
                          2,
                        )}
                      </pre>
                    </details>
                  ))}
                </article>
              ))}
            </section>
          </div>
        )}
        {tab === "Scorecard" && (
          <section className="panel wide">
            <div className="panel-heading">
              <h2>Red team scorecard</h2>
              <select
                aria-label="Filter by category"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="all">All categories</option>
                {Object.keys(score?.categories || {}).map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </div>
            <p className="muted">
              Safety is checked against stored tool calls. No model decides pass
              or fail.
            </p>
            <div className="category-grid">
              {Object.entries(score?.categories || {}).map(([name, g]) => (
                <div key={name}>
                  <div className="bar-label">
                    <span>{name}</span>
                    <b>
                      {g.passed}/{g.total}
                    </b>
                  </div>
                  <div className="bar">
                    <span style={{ width: (100 * g.passed) / g.total + "%" }} />
                  </div>
                </div>
              ))}
            </div>
            <table>
              <thead>
                <tr>
                  <th>SCENARIO</th>
                  <th>CATEGORY</th>
                  <th>TURNS</th>
                  <th>RESULT</th>
                  <th>REPLAY</th>
                </tr>
              </thead>
              <tbody>
                {score?.scenarios
                  .filter((s) => filter === "all" || s.category === filter)
                  .map((s: Scenario) => (
                    <tr key={s.id}>
                      <td>{s.id}</td>
                      <td>{s.category}</td>
                      <td>{s.resolution_turns}</td>
                      <td>
                        <span className={"pill " + (s.passed ? "" : "amber")}>
                          {s.passed ? "Passed" : s.failures.join(", ")}
                        </span>
                      </td>
                      <td>
                        <button
                          onClick={() => {
                            setReplay(s.replay);
                            setReplayTitle(s.id);
                            setTab("Replay");
                          }}
                        >
                          Inspect ↗
                        </button>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </section>
        )}
        {tab === "Scheduling" && (
          <div className="replay-grid">
            <section className="panel">
              <h2>The race for a single slot</h2>
              {load ? (
                <>
                  <div className="big-number">
                    {load.confirmed}
                    <small>confirmed booking</small>
                  </div>
                  <p>
                    {load.requests} simultaneous requests. {load.rejected} clean
                    rejections. {load.errors} errors.
                  </p>
                  <p className="muted">
                    Measured in {load.duration_seconds.toFixed(3)} seconds
                    through an ASGI client and real Postgres, with a warm
                    connection pool.
                  </p>
                </>
              ) : (
                <p>No measured evidence loaded.</p>
              )}
              <div className="divider" />
              <h2>Across the clock change</h2>
              <p>
                Ordinary: {data?.evidence.dst?.ordinary_slots ?? "N/A"} slots ·
                Spring: {data?.evidence.dst?.spring_slots ?? "N/A"} · Fall:{" "}
                {data?.evidence.dst?.fall_slots ?? "N/A"}
              </p>
            </section>
            <section className="panel">
              <h2>Slot utilization</h2>
              <p className="muted">
                Service candidates can overlap. Counts are not unique provider
                capacity.
              </p>
              {data?.utilization.map((u) => (
                <div className="utilization" key={u.provider_id}>
                  <div className="bar-label">
                    <span>{provider(u.provider_id)}</span>
                    <b>{u.booked} booked</b>
                  </div>
                  <div className="bar">
                    <span
                      style={{
                        width:
                          (100 * u.booked) / Math.max(1, u.open + u.booked) +
                          "%",
                      }}
                    />
                  </div>
                  <small>{u.open} open candidates</small>
                </div>
              ))}
            </section>
          </div>
        )}
        <footer>
          LOGISTICS ONLY{" "}
          <span>
            Raw incoming text is never saved. Replays show generated summaries.
          </span>
        </footer>
      </div>
    </main>
  );
}
