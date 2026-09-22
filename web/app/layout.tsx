import type { Metadata } from "next";
import "./style.css";
import "./evidence.css";
export const metadata: Metadata = {
  title: "frontdesk | Booking promises, proven",
  description:
    "Explore a WhatsApp booking agent's PostgreSQL concurrency tests, durable workflows, and auditable safety decisions. Recorded synthetic evidence, no login required.",
};
export default function Layout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
