import Link from "next/link";
import { evidence, REPO, SHOWCASE, source } from "./evidence/model";

export default function Home() {
  const race = evidence.concurrency;
  return (
    <main className="portfolio-home">
      <nav className="portfolio-nav" aria-label="Main navigation">
        <Link className="brand" href="/">
          <span className="brand-icon">f</span>frontdesk
        </Link>
        <div>
          <Link href="/evidence/">Evidence explorer</Link>
          <a href={REPO}>GitHub ↗</a>
        </div>
      </nav>
      <section className="portfolio-hero">
        <div>
          <p className="eyebrow">WHATSAPP AUTOMATION / BUILT TO BE INSPECTED</p>
          <h1>
            A booking is
            <br />a <em>promise.</em>
            <br />
            Prove it holds.
          </h1>
          <p className="portfolio-lead">
            A clinic booking agent with durable conversations, atomic
            scheduling, and safety decisions you can audit.
          </p>
          <div className="actions">
            <Link className="primary" href="/evidence/">
              Explore the engineering ↗
            </Link>
            <a className="secondary" href={source("ARCHITECTURE.md")}>
              Read the architecture
            </a>
          </div>
          <p className="fine">
            Fictional clinic. Booking logistics only.
            <br />
            Public explorer uses recorded evidence. No account required.
          </p>
        </div>
        <div className="portfolio-proof">
          <div className="portfolio-proof-heading">
            <span className="evidence-live-dot" /> POSTGRES CONCURRENCY TEST
            <span>MEASURED</span>
          </div>
          <div className="portfolio-proof-stat">
            <strong>{race.requests}</strong>
            <span>
              requests.
              <br />
              The same appointment.
            </span>
          </div>
          <div className="portfolio-claims" aria-hidden="true">
            {Array.from({ length: race.requests }, (_, i) => (
              <span className={i < race.confirmed ? "winner" : ""} key={i}>
                {i < race.confirmed ? "✓" : "·"}
              </span>
            ))}
          </div>
          <div className="portfolio-proof-result">
            <div>
              <strong>{race.confirmed}</strong>
              <small>confirmed</small>
            </div>
            <div>
              <strong>{race.rejected}</strong>
              <small>clean rejections</small>
            </div>
            <div>
              <strong>{race.errors}</strong>
              <small>server errors</small>
            </div>
          </div>
          <div className="portfolio-proof-caption">
            One persisted booking row. Local ASGI client, real PostgreSQL.
            <br />
            Grouped outcomes, not request arrival order.
          </div>
        </div>
      </section>
      <section className="portfolio-strip" aria-label="Measured results">
        <div>
          <b>
            {evidence.redteam.passed}/{evidence.redteam.total}
          </b>
          <span>scripted scenarios pass</span>
        </div>
        <div>
          <b>
            {evidence.tenant.explicitly_refused}/{evidence.tenant.attempts}
          </b>
          <span>tenant boundary checks</span>
        </div>
        <div>
          <b>{evidence.quality.coverage_percent}%</b>
          <span>statement coverage</span>
        </div>
        <Link href="/evidence/">Inspect the evidence →</Link>
      </section>
      <section className="portfolio-capabilities">
        <div>
          <p className="eyebrow">ENGINEERING THAT EARNS TRUST</p>
          <h2>
            The hard parts are
            <br />
            what happens next.
          </h2>
        </div>
        <article>
          <span>01 / CORRECTNESS</span>
          <h3>When two people choose the same time.</h3>
          <p>
            Provider and slot locks, atomic rescheduling, and database
            constraints keep competing requests from creating overlapping
            bookings.
          </p>
        </article>
        <article>
          <span>02 / RELIABILITY</span>
          <h3>When a webhook arrives again.</h3>
          <p>
            Persistent state, message deduplication, and a durable outbox keep
            retries and process restarts from repeating committed work.
          </p>
        </article>
        <article>
          <span>03 / SAFETY</span>
          <h3>When the conversation leaves logistics.</h3>
          <p>
            Structured refusals and emergency handoffs run before the optional
            model. Deterministic checks inspect the resulting tool calls.
          </p>
        </article>
      </section>
      <section className="portfolio-bottom">
        <div>
          <p className="eyebrow">GO ONE LEVEL DEEPER</p>
          <h2>Follow a decision all the way to the database.</h2>
          <p>
            Search the scenario library, step through audit traces, and compare
            expected tools with observed results.
          </p>
        </div>
        <Link className="primary" href="/evidence/">
          Open the explorer ↗
        </Link>
      </section>
      <footer className="evidence-footer">
        <span>Python · FastAPI · PostgreSQL · Next.js</span>
        <a href={source("README.md#try-it-locally")}>
          Run the full application locally ↗
        </a>
        {!SHOWCASE && <Link href="/simulator/">Local simulator ↗</Link>}
      </footer>
    </main>
  );
}
