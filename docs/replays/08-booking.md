# 08-booking

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
          "service_id": "01a0c6f9-39e5-7b0e-a09a-610c1f4cfda8",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-39e7-7e6a-be58-e2960f46dfc8",
            "01a0c6f9-39e7-7fec-b8e7-ac7af2f3d4f0",
            "01a0c6f9-39e7-7fec-b8e7-ac7af2f3d4f1"
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
          "slot_id": "01a0c6f9-39e7-7e6a-be58-e2960f46dfc8"
        },
        "name": "book_slot",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-3a4d-74eb-b716-0a8c4a668939"
          ],
          "ok": true
        }
      }
    ]
  }
]
~~~
