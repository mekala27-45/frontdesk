# 03-booking

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
          "service_id": "01a0c6f9-3746-7fb2-835e-1fb863dc703d",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3749-714b-982a-a449e5462037",
            "01a0c6f9-3749-79a4-9818-b633ef7ef761",
            "01a0c6f9-3749-79a4-9818-b633ef7ef762"
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
          "slot_id": "01a0c6f9-3749-714b-982a-a449e5462037"
        },
        "name": "book_slot",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-37ad-7e13-aef5-8fac227b2bf5"
          ],
          "ok": true
        }
      }
    ]
  }
]
~~~
