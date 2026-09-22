# 11-changes

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
          "service_id": "01a0c6f9-3b91-7c82-beaf-1df097f69ca3",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3b94-7df7-84d8-90477592644f",
            "01a0c6f9-3b94-7df7-84d8-904775926450",
            "01a0c6f9-3b94-7df7-84d8-904775926451"
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
          "slot_id": "01a0c6f9-3b94-7df7-84d8-90477592644f"
        },
        "name": "book_slot",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3be9-7d94-a027-27da7a849a7f"
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
            "01a0c6f9-3be9-7d94-a027-27da7a849a7f"
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
          "booking_id": "01a0c6f9-3be9-7d94-a027-27da7a849a7f",
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
            "01a0c6f9-3be9-7d94-a027-27da7a849a7f"
          ],
          "ok": true
        }
      }
    ]
  }
]
~~~
