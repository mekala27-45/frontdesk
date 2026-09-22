# 06-booking

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
          "service_id": "01a0c6f9-38df-7ba8-9e09-47350527f763",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-38e2-7fc5-bd47-5c0583de9cb0",
            "01a0c6f9-38e2-7fc5-bd47-5c0583de9cb1",
            "01a0c6f9-38e2-7fc5-bd47-5c0583de9cb2"
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
          "slot_id": "01a0c6f9-38e2-7fc5-bd47-5c0583de9cb0"
        },
        "name": "book_slot",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-394d-798c-9b51-7a1f77f9a7b4"
          ],
          "ok": true
        }
      }
    ]
  }
]
~~~
