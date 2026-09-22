import Link from "next/link";
export default function Home() {
  return (
    <main className="landing">
      <div className="brand">
        <span className="brand-icon">f</span> frontdesk
        <span className="version">FICTIONAL CLINIC DEMO</span>
      </div>
      <div className="landing-grid">
        <section>
          <p className="eyebrow">A LITTLE LESS WAITING.</p>
          <h1>
            A front desk
            <br />
            that keeps
            <br />
            <em>its promises.</em>
          </h1>
          <p className="lead">
            Book a time. Change your plans. Reach a person.
            <br />
            Appointment logistics for Ridgeview Family and Wellness Clinic.
          </p>
          <div className="actions">
            <Link className="primary" href="/simulator/">
              Try the conversation <span>↗</span>
            </Link>
            <Link className="secondary" href="/console/">
              Open operations
            </Link>
          </div>
          <p className="fine">
            Fictional people. Fictional clinic. Real scheduling engine.
            <br />
            Please do not enter symptoms or other health information.
          </p>
        </section>
        <aside className="landing-card">
          <div className="status">
            <i /> LOCAL API DEMO
          </div>
          <div className="mini-bubble">Can I book a welcome visit?</div>
          <div className="mini-bubble reply">
            Of course. Choose an available time.
          </div>
          <div className="slot-preview">
            <span>◷</span>
            <div>
              A time that is actually yours
              <small>Provider locks protect overlapping appointments.</small>
            </div>
            <b>✓</b>
          </div>
          <div className="card-line" />
          <p>Every decision leaves a trace.</p>
          <div className="tag-row">
            <span>Persistent state</span>
            <span>Structured refusals</span>
            <span>Tenant isolation</span>
          </div>
        </aside>
      </div>
      <footer>
        RIDGEVIEW FAMILY AND WELLNESS CLINIC{" "}
        <span>Booking logistics only. No medical advice.</span>
      </footer>
    </main>
  );
}
