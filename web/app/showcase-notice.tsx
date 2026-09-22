import Link from "next/link";
import { source } from "./evidence/model";

export default function ShowcaseNotice({ feature }: { feature: string }) {
  return (
    <main className="showcase-notice">
      <Link className="brand" href="/">
        <span className="brand-icon">f</span>frontdesk
      </Link>
      <p className="eyebrow">PUBLIC PORTFOLIO</p>
      <h1>{feature} runs with the local API.</h1>
      <p>
        This public site lets you explore recorded test evidence without
        credentials. To create bookings or operate the clinic console, run the
        full application locally.
      </p>
      <div className="actions">
        <Link className="primary" href="/evidence/">
          Explore the evidence ↗
        </Link>
        <a className="secondary" href={source("README.md#try-it-locally")}>
          Local setup ↗
        </a>
      </div>
    </main>
  );
}
