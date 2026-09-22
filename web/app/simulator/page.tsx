"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { API, Reply, Call } from "../lib";
type Bubble = { side: "in" | "out"; text?: string; reply?: Reply };
export default function Simulator() {
  const [identity, setIdentity] = useState<{
      wa_id: string;
      token: string;
    } | null>(null),
    [bubbles, setBubbles] = useState<Bubble[]>([]),
    [draft, setDraft] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [calls, setCalls] = useState<Call[]>([]);
  const chatBody = useRef<HTMLDivElement>(null);
  useEffect(() => {
    chatBody.current?.scrollTo({ top: chatBody.current.scrollHeight, behavior: "smooth" });
  }, [bubbles, busy]);
  async function send(value: string, label?: string) {
    if (busy || !value.trim()) return;
    setBusy(true);
    setError("");
    setDraft("");
    setBubbles((b) => [...b, { side: "in", text: label || value }]);
    try {
      let session = identity;
      if (!session) {
        const r = await fetch(API + "/internal/simulator/session", {
          method: "POST",
        });
        if (!r.ok) throw new Error("Session unavailable");
        session = (await r.json()) as { wa_id: string; token: string };
        setIdentity(session);
      }
      const interactive =
        value.startsWith("slot:") ||
        value.startsWith("service:") ||
        value.startsWith("booking:") ||
        Boolean(label);
      const message = {
        from: session.wa_id,
        id: "demo." + crypto.randomUUID(),
        timestamp: String(Math.floor(Date.now() / 1000)),
        type: interactive ? "interactive" : "text",
        ...(interactive
          ? {
              interactive: {
                type: "button_reply",
                button_reply: { id: value, title: label || "Choice" },
              },
            }
          : { text: { body: value } }),
      };
      const payload = {
        object: "whatsapp_business_account",
        entry: [
          {
            id: "demo-account",
            changes: [
              {
                field: "messages",
                value: {
                  messaging_product: "whatsapp",
                  metadata: { phone_number_id: "demo-phone" },
                  messages: [message],
                },
              },
            ],
          },
        ],
      };
      const response = await fetch(API + "/internal/simulator", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + session.token,
        },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error("Request failed");
      const result = (await response.json()) as {
        results: { reply: Reply; calls: Call[] }[];
      };
      for (const item of result.results) {
        if (item.reply)
          setBubbles((b) => [...b, { side: "out", reply: item.reply }]);
        setCalls((c) => [...c, ...item.calls]);
      }
    } catch {
      setError(
        "Cannot reach the demo API. Start the local API or check its configured URL.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="workspace">
      <nav className="sidebar">
        <Link className="brand" href="/">
          <span className="brand-icon">f</span>frontdesk
        </Link>
        <p className="nav-label">WORKSPACE</p>
        <Link className="nav-item active" href="/simulator/">
          ◉ Conversation
        </Link>
        <Link className="nav-item" href="/console/">
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
            <p className="eyebrow">THE PATIENT EXPERIENCE</p>
            <h1>Meet your front desk.</h1>
          </div>
          <span className="badge">DEV TRANSPORT</span>
        </header>
        <p className="page-intro">
          A real conversation flow, from first hello to a confirmed appointment.
        </p>
        <div className="sim-grid">
          <section className="phone">
            <div className="chat-head">
              <span className="avatar">R</span>
              <div>
                Ridgeview front desk
                <small>
                  <i /> Appointment assistant
                </small>
              </div>
              <span>•••</span>
            </div>
            <div className="chat-body" aria-live="polite" ref={chatBody}>
              <span className="date-chip">TODAY</span>
              <div className="privacy-note">
                Fictional clinic. Logistics only. Do not enter health
                information.
              </div>
              {bubbles.length === 0 && (
                <div className="bubble out">
                  Welcome to Ridgeview. I can help you book, change, or cancel
                  an appointment.
                  <div className="quick-options">
                    {[
                      "Book an appointment",
                      "My bookings",
                      "Talk to a person",
                    ].map((x) => (
                      <button key={x} disabled={busy} onClick={() => send(x)}>
                        {x} ↗
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {bubbles.map((b, index) => (
                <div key={index} className={"bubble " + b.side}>
                  {b.text ||
                    b.reply?.text?.body ||
                    b.reply?.interactive?.body.text ||
                    (b.reply?.template
                      ? "Approved sample template: " + b.reply.template.name
                      : "")}
                  {b.reply?.interactive?.action.sections?.map((section) => (
                    <div className="quick-options" key={section.title}>
                      {section.rows.map((row) => (
                        <button
                          disabled={busy}
                          key={row.id}
                          onClick={() => send(row.id, row.title)}
                        >
                          <strong>{row.title}</strong>
                          <small>{row.description}</small>
                          <span>›</span>
                        </button>
                      ))}
                    </div>
                  ))}
                  {b.reply?.interactive?.action.buttons?.map((button) => (
                    <button
                      className="reply-button"
                      disabled={busy}
                      key={button.reply.id}
                      onClick={() => send(button.reply.id, button.reply.title)}
                    >
                      {button.reply.title}
                    </button>
                  ))}
                </div>
              ))}
              {busy && (
                <div className="bubble out muted">Finding the next step...</div>
              )}
            </div>
            {error && (
              <p role="alert" className="error">
                {error}
              </p>
            )}
            <form
              className="composer"
              onSubmit={(e) => {
                e.preventDefault();
                void send(draft);
              }}
            >
              <input
                aria-label="Message"
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Type a logistics request..."
                maxLength={2000}
              />
              <button
                aria-label="Send message"
                disabled={busy || !draft.trim()}
              >
                ↑
              </button>
            </form>
          </section>
          <aside>
            <div className="panel">
              <span className="panel-icon">⌘</span>
              <h2>Same engine. Different doorway.</h2>
              <p>
                Every tap creates the same webhook shape as WhatsApp. After
                authentication, both routes use the same conversation engine and
                database.
              </p>
              <div className="divider" />
              <p className="eyebrow">TRY A PATH</p>
              {[
                "Book a welcome visit",
                "Reschedule my appointment",
                "Talk to a person",
              ].map((x, i) => (
                <button
                  className="try-path"
                  disabled={busy}
                  key={x}
                  onClick={() => send(x)}
                >
                  <span>0{i + 1}</span>
                  {x}
                  <b>↗</b>
                </button>
              ))}
            </div>
            <div className="panel audit">
              <p className="eyebrow">LIVE TOOL TRACE</p>
              {!calls.length ? (
                <p className="muted">
                  Tool calls appear as the conversation progresses.
                </p>
              ) : (
                calls.slice(-5).map((c, i) => (
                  <div key={i} className="trace">
                    <span className={c.result.ok ? "dot" : "dot amber"} />
                    <code>{c.name}</code>
                    <small>{c.result.code}</small>
                  </div>
                ))
              )}
            </div>
            <p className="fine">
              Live WhatsApp delivery and a real-device recording have not been
              verified. This demo uses DevTransport. No clinical input is
              retained.
            </p>
          </aside>
        </div>
      </div>
    </main>
  );
}
