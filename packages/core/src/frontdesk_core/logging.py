from typing import Any
import re
import structlog

def redact(_: Any, __: str, event: dict[str, Any]) -> dict[str, Any]:
    # Free text is never accepted by the logging interface.
    safe = {key: value for key, value in event.items() if key in {"event", "status", "id", "phone", "kind"}}
    return {key: re.sub(r"\d{7,15}", lambda m: "***" + m[0][-4:], str(value)) for key, value in safe.items()}

structlog.configure(processors=[redact, structlog.processors.JSONRenderer()])
log = structlog.get_logger()

