# 01-booking

Generated logistics summaries only. Raw input is not retained.

~~~json
[
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
          "service_id": "01a0c6f9-35ee-7188-bbe9-cbaebd5f8c5c",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-35f2-73d5-b290-3a2576845f6b",
            "01a0c6f9-35f2-73d5-b290-3a2576845f6c",
            "01a0c6f9-35f2-7f54-9e04-d0f5e853224b"
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
          "slot_id": "01a0c6f9-35f2-73d5-b290-3a2576845f6b"
        },
        "name": "book_slot",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3694-79c3-9d43-48a01c746c9f"
          ],
          "ok": true
        }
      }
    ]
  }
]
~~~
