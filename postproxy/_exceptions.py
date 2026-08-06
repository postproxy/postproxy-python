from __future__ import annotations

from typing import Any


class PostProxyError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class AuthenticationError(PostProxyError):
    pass


class NotFoundError(PostProxyError):
    pass


class ConflictError(PostProxyError):
    """409.

    Raised for a duplicate submission (``response["duplicate_post_id"]``), a
    backfill that is already running (``response["profile_sync_id"]``), or a
    request whose ``Idempotency-Key`` is still in flight.
    """


class ValidationError(PostProxyError):
    pass


class BadRequestError(PostProxyError):
    pass
