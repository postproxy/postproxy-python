import hashlib
import hmac


def verify_signature(payload: str, signature_header: str, secret: str) -> bool:
    parts = dict(p.split("=", 1) for p in signature_header.split(","))
    timestamp = parts.get("t", "")
    expected = parts.get("v1", "")

    signed_payload = f"{timestamp}.{payload}"
    computed = hmac.new(
        secret.encode(), signed_payload.encode(), hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, expected)
