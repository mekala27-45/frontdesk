# LinkedIn draft, not posted

I sent 50 simultaneous HTTP requests at one appointment slot in a WhatsApp booking agent. One booking was confirmed, 49 requests were cleanly rejected, and there were 0 server errors. The local ASGI-to-Postgres run took 0.166 seconds with a warm connection pool.

The more interesting part was making safety auditable: refusals are named tool calls, and a deterministic scorer checks the database. The scripted suite passed 50 of 50 scenarios, including injection attempts, emergencies, cross-patient requests and concurrent claims.

The browser demo uses the same conversation engine as the signed Meta webhook. Live WhatsApp delivery and public API hosting are still unverified, and the README says so.

Source and measured evidence: https://github.com/mekala27-45/frontdesk
