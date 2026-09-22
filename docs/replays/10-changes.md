# 10-changes

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
          "service_id": "01a0c6f9-3afc-7d18-9831-330908ba2905",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3aff-7f6f-b1c5-e868e57c07c4",
            "01a0c6f9-3aff-7f6f-b1c5-e868e57c07c5",
            "01a0c6f9-3aff-7fd8-8b32-99e5b6870793"
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
          "slot_id": "01a0c6f9-3aff-7f6f-b1c5-e868e57c07c4"
        },
        "name": "book_slot",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3b52-720c-9a36-73920c0ab995"
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
            "01a0c6f9-3b52-720c-9a36-73920c0ab995"
          ],
          "ok": true
        }
      }
    ]
  },
  {
    "content_summary": "cancel",
    "tool_calls": [
      {
        "arguments": {
          "booking_id": "01a0c6f9-3b52-720c-9a36-73920c0ab995",
          "category": "unrelated",
          "date_from": null,
          "date_to": null,
          "patient_name": "Demo visitor",
          "patient_wa_id": null,
          "provider_id": null,
          "service_id": null,
          "slot_id": null
        },
        "name": "cancel_booking",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3b52-720c-9a36-73920c0ab995"
          ],
          "ok": true
        }
      }
    ]
  }
]
~~~
