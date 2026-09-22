# 41-concurrency

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
          "service_id": "01a0c6f9-4474-78ba-9837-a3320a8b588e",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-4477-7f13-8f62-25ec17a28554",
            "01a0c6f9-4477-7f13-8f62-25ec17a28555",
            "01a0c6f9-4477-7f13-8f62-25ec17a28556"
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
          "slot_id": "01a0c6f9-4477-7f13-8f62-25ec17a28554"
        },
        "name": "book_slot",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-44cd-7461-9034-5db9ba09f94c"
          ],
          "ok": true
        }
      }
    ]
  }
]
~~~
