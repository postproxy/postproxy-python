from __future__ import annotations

from typing import Any

import httpx

import math
import platform as _py_platform
import sys

from ._constants import DEFAULT_BASE_URL, VERSION
from ._exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    PostProxyError,
    RateLimitError,
    ValidationError,
)


_PY_VER = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
_USER_AGENT = f"postproxy-python/{VERSION} (python/{_PY_VER}; {_py_platform.system().lower()})"


def _parse_retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None
    return seconds if math.isfinite(seconds) and seconds > 0 else None


class PostProxy:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        profile_group_id: str | None = None,
        httpx_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.profile_group_id = profile_group_id
        self._owns_client = httpx_client is None
        self._client = httpx_client or httpx.AsyncClient()

        # Lazy imports to avoid circular references
        from .resources.posts import PostsResource
        from .resources.profiles import ProfilesResource
        from .resources.profile_groups import ProfileGroupsResource
        from .resources.webhooks import WebhooksResource
        from .resources.queues import QueuesResource
        from .resources.comments import CommentsResource
        from .resources.profile_comments import ProfileCommentsResource
        from .resources.chats import ChatsResource
        from .resources.messages import MessagesResource
        from .resources.placements import PlacementsResource
        from .resources.api_keys import ApiKeysResource
        from .resources.google_business import GoogleBusinessResource
        from .resources.whatsapp_templates import WhatsAppTemplatesResource
        from .resources.whatsapp import WhatsAppResource

        self.posts = PostsResource(self)
        self.profiles = ProfilesResource(self)
        self.profile_groups = ProfileGroupsResource(self)
        self.webhooks = WebhooksResource(self)
        self.queues = QueuesResource(self)
        self.comments = CommentsResource(self)
        self.profile_comments = ProfileCommentsResource(self)
        self.chats = ChatsResource(self)
        self.messages = MessagesResource(self)
        self.placements = PlacementsResource(self)
        self.api_keys = ApiKeysResource(self)
        self.google_business = GoogleBusinessResource(self)
        self.whatsapp_templates = WhatsAppTemplatesResource(self)
        self.whatsapp = WhatsAppResource(self)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: list[tuple[str, tuple[str | None, Any, str]]] | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
        headers: dict[str, str] | None = None,
        raw: bool = False,
    ) -> Any:
        """Send a request and return the parsed JSON body.

        With ``raw=True`` a successful response is returned as a
        ``(content, content_type)`` tuple instead of being parsed.
        """
        url = f"{self.base_url}/api{path}"

        query: dict[str, Any] = {}
        pgid = profile_group_id or self.profile_group_id
        if pgid is not None:
            query["profile_group_id"] = pgid
        if params:
            query.update(params)

        request_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": _USER_AGENT,
        }
        if idempotency_key is not None:
            request_headers["Idempotency-Key"] = idempotency_key
        if headers:
            request_headers.update(headers)

        response = await self._client.request(
            method,
            url,
            headers=request_headers,
            params=query or None,
            json=json,
            data=data,
            files=files,
        )

        if response.status_code == 204:
            return None

        if raw and response.is_success:
            return response.content, response.headers.get("content-type")

        body: Any
        try:
            body = response.json()
        except Exception:
            body = None

        if response.is_success:
            return body

        message = ""
        if isinstance(body, dict):
            message = body.get("error") or body.get("message") or str(body)
        else:
            message = response.text or f"HTTP {response.status_code}"

        error_kwargs = {"status_code": response.status_code, "response": body}

        if response.status_code == 401:
            raise AuthenticationError(message, **error_kwargs)
        if response.status_code == 403:
            raise ForbiddenError(message, **error_kwargs)
        if response.status_code == 429:
            raise RateLimitError(
                message,
                retry_after=_parse_retry_after(response.headers.get("retry-after")),
                **error_kwargs,
            )
        if response.status_code == 404:
            raise NotFoundError(message, **error_kwargs)
        if response.status_code == 409:
            raise ConflictError(message, **error_kwargs)
        if response.status_code == 422:
            raise ValidationError(message, **error_kwargs)
        if response.status_code == 400:
            raise BadRequestError(message, **error_kwargs)
        raise PostProxyError(message, **error_kwargs)

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> PostProxy:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()
