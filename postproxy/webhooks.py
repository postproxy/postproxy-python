import hashlib
import hmac
import json
from typing import Any

from ._constants import WEBHOOK_EVENT_TYPES
from ._types import (
    CommentCreatedData,
    MediaFailedData,
    PlatformPostData,
    PlatformPostInsightsData,
    PostImportedData,
    PostProcessedData,
    ProfileEventData,
    ProfileStatsData,
    WebhookEvent,
)


def verify_signature(payload: str, signature_header: str, secret: str) -> bool:
    parts = dict(p.split("=", 1) for p in signature_header.split(","))
    timestamp = parts.get("t", "")
    expected = parts.get("v1", "")

    signed_payload = f"{timestamp}.{payload}"
    computed = hmac.new(
        secret.encode(), signed_payload.encode(), hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, expected)


_EVENT_DATA_MODELS: dict[str, type] = {
    "post.processed": PostProcessedData,
    "post.imported": PostImportedData,
    "platform_post.published": PlatformPostData,
    "platform_post.failed": PlatformPostData,
    "platform_post.failed_waiting_for_retry": PlatformPostData,
    "platform_post.insights": PlatformPostInsightsData,
    "profile.connected": ProfileEventData,
    "profile.disconnected": ProfileEventData,
    "profile.stats": ProfileStatsData,
    "media.failed": MediaFailedData,
    "comment.created": CommentCreatedData,
}


class WebhookParseError(ValueError):
    """Raised when a webhook payload can't be parsed."""


def parse_event(body: str | bytes | dict[str, Any]) -> WebhookEvent:
    """Parse a webhook body and validate the envelope.

    Returns a `WebhookEvent` with `data` as a raw dict. To get a typed payload,
    pair with `event_data_model(event.type).model_validate(event.data)` or use
    `parse_event_typed(...)` which returns the envelope + typed data tuple.
    """
    if isinstance(body, (bytes, bytearray)):
        body = body.decode()
    if isinstance(body, str):
        try:
            parsed: Any = json.loads(body)
        except json.JSONDecodeError as e:
            raise WebhookParseError(f"Invalid JSON: {e}") from e
    else:
        parsed = body

    if not isinstance(parsed, dict):
        raise WebhookParseError("Webhook body is not a JSON object")

    event_type = parsed.get("type")
    if event_type not in WEBHOOK_EVENT_TYPES:
        raise WebhookParseError(f"Unknown webhook event type: {event_type!r}")

    return WebhookEvent.model_validate(parsed)


def event_data_model(event_type: str) -> type:
    """Return the typed payload model for a given event type."""
    try:
        return _EVENT_DATA_MODELS[event_type]
    except KeyError:
        raise WebhookParseError(f"Unknown webhook event type: {event_type!r}")


def parse_event_typed(body: str | bytes | dict[str, Any]) -> tuple[WebhookEvent, Any]:
    """Parse a webhook body and return (envelope, typed_data)."""
    envelope = parse_event(body)
    typed = event_data_model(envelope.type).model_validate(envelope.data)
    return envelope, typed
