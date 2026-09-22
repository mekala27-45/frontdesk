# 14-changes

Generated logistics summaries only. Raw input is not retained.

~~~json
[
  {
    "content_summary": "availability",
    "tool_calls": [
      {
        "arguments": {
          "booking_id": null,
          "category": "unrelated",
          "date_from": null,
          "date_to": null,
          "patient_name": "Demo visitor",
          "patient_wa_id": null,
          "provider_id": null,
          "service_id": "01a0c6f9-3e73-7d85-8eec-5bd81fddf3e5",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3e76-7858-a2e8-849ac8029682",
            "01a0c6f9-3e76-7858-a2e8-849ac8029683",
            "01a0c6f9-3e76-7858-a2e8-849ac8029684"
          ],
          "ok": true
        }
      }
    ]
  },
  {
    "content_summary": "confirm_prompt",
    "tool_calls": []
  },
  {
    "content_summary": "confirmation",
    "tool_calls": [
      {
        "arguments": {
          "booking_id": null,
          "category": "unrelated",
          "date_from": null,
          "date_to": null,
          "patient_name": "Demo visitor",
          "patient_wa_id": null,
          "provider_id": null,
          "service_id": null,
          "slot_id": "01a0c6f9-3e76-7858-a2e8-849ac8029682"
        },
        "name": "book_slot",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3ed4-7886-b046-827093da49e2"
          ],
          "ok": true
        }
      }
    ]
  },
  {
    "content_summary": "booking_choice",
    "tool_calls": [
      {
        "arguments": {
          "booking_id": null,
          "category": "unrelated",
          "date_from": null,
          "date_to": null,
          "patient_name": "Demo visitor",
          "patient_wa_id": "15550001111",
          "provider_id": null,
          "service_id": null,
          "slot_id": null
        },
        "name": "get_my_bookings",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3ed4-7886-b046-827093da49e2"
          ],
          "ok": true
        }
      }
    ]
  },
  {
    "content_summary": "service_prompt",
    "tool_calls": []
  },
  {
    "content_summary": "availability",
    "tool_calls": [
      {
        "arguments": {
          "booking_id": null,
          "category": "unrelated",
          "date_from": null,
          "date_to": null,
          "patient_name": "Demo visitor",
          "patient_wa_id": null,
          "provider_id": null,
          "service_id": "01a0c6f9-3e73-7d85-8eec-5bd81fddf3e5",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3e76-7858-a2e8-849ac8029683",
            "01a0c6f9-3e76-7858-a2e8-849ac8029684"
          ],
          "ok": true
        }
      }
    ]
  },
  {
    "content_summary": "confirm_prompt",
    "tool_calls": []
  },
  {
    "content_summary": "confirmation",
    "tool_calls": [
      {
        "arguments": {
          "booking_id": "01a0c6f9-3ed4-7886-b046-827093da49e2",
          "category": "unrelated",
          "date_from": null,
          "date_to": null,
          "patient_name": "Demo visitor",
          "patient_wa_id": null,
          "provider_id": null,
          "service_id": null,
          "slot_id": "01a0c6f9-3e76-7858-a2e8-849ac8029683"
        },
        "name": "reschedule_booking",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3ed4-7886-b046-827093da49e2"
          ],
          "ok": true
        }
      }
    ]
  }
]
~~~
