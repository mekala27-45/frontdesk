# 02-booking

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
          "service_id": "01a0c6f9-36b8-77a1-ac60-27091e029690",
          "slot_id": null
        },
        "name": "check_availability",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-36bb-78dd-b22a-5f6d45ba8afb",
            "01a0c6f9-36bb-7a7e-b3f5-849d64c4cd9a",
            "01a0c6f9-36bb-7d6d-a40c-365688502659"
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
          "slot_id": "01a0c6f9-36bb-78dd-b22a-5f6d45ba8afb"
        },
        "name": "book_slot",
        "result": {
          "code": "ok",
          "ids": [
            "01a0c6f9-372f-7424-bdcf-2d996f12d3f2"
          ],
          "ok": true
        }
      }
    ]
  }
]
~~~
