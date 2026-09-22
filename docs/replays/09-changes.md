# 09-changes

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
          "service_id": "01a0c6f9-3a62-78c6-bef3-49e00a6d6ef8",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3a65-7e72-a57b-ca62b62c6976",
            "01a0c6f9-3a65-7e72-a57b-ca62b62c6977",
            "01a0c6f9-3a65-7e72-a57b-ca62b62c6978"
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
          "slot_id": "01a0c6f9-3a65-7e72-a57b-ca62b62c6976"
        },
        "name": "book_slot",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3aba-70d3-b67f-d4a212583a6c"
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
            "01a0c6f9-3aba-70d3-b67f-d4a212583a6c"
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
          "booking_id": "01a0c6f9-3aba-70d3-b67f-d4a212583a6c",
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
            "01a0c6f9-3aba-70d3-b67f-d4a212583a6c"
          ],
          "ok": true
        }
      }
    ]
  }
]
~~~
