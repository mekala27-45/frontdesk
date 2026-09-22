# WhatsApp integration

GET /webhooks/whatsapp echoes hub.challenge only for the matching verify token and subscribe mode. POST checks X-Hub-Signature-256 over the raw bytes before JSON parsing. Invalid signatures return a rejection, including a body changed after signing.

Inbound text and list/button replies feed the same conversation function. Status-only notifications are acknowledged without starting a conversation. The message identifier deduplicates retries in Postgres.

Outbound requests use httpx directly against the configured Graph API version. Text and interactive messages require an open customer service window. Outside the window, only a template is selected. Interactive lists and reply buttons are validated against platform size limits. Unknown/ambiguous send outcomes are retained for operator review.

DevTransport records the generated payload in the outbox and emits only a metadata log. This intentionally avoids logging full destinations or request bodies. It does not make live network calls.

The tests use **synthetic contract fixtures**, not recordings from a Meta developer app. Live WhatsApp delivery and a real-device recording were not performed. The default hello_world sample demonstrates only the template path. Configure an approved utility template before using useful appointment reminders.

To enable a real test account, set META_TOKEN, META_PHONE_ID, APP_SECRET and VERIFY_TOKEN, seed a clinic with that phone identity, set the public callback URL, and add the intended test recipient in the Meta dashboard. Recheck Graph version and account restrictions in Meta's current documentation before enabling delivery.

References: [Meta webhook verification](https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/webhooks/start/), [Meta message guide](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages), [Google event IDs](https://developers.google.com/workspace/calendar/api/guides/create-events).

