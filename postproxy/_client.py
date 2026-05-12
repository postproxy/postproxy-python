from __future__ import annotations

from typing import Any

import httpx

import platform as _py_platform
import sys

from ._constants import DEFAULT_BASE_URL, VERSION
from ._exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PostProxyError,
    ValidationError,
)


_PY_VER = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
_USER_AGENT = f"postproxy-python/{VERSION} (python/{_PY_VER}; {_py_platform.system().lower()})"


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

        self.posts = PostsResource(self)
        self.profiles = ProfilesResource(self)
        self.profile_groups = ProfileGroupsResource(self)
        self.webhooks = WebhooksResource(self)
        self.queues = QueuesResource(self)
        self.comments = CommentsResource(self)

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
    ) -> Any:
        url = f"{self.base_url}/api{path}"

        query: dict[str, Any] = {}
        pgid = profile_group_id or self.profile_group_id
        if pgid is not None:
            query["profile_group_id"] = pgid
        if params:
            query.update(params)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": _USER_AGENT,
        }

        response = await self._client.request(
            method,
            url,
            headers=headers,
            params=query or None,
            json=json,
            data=data,
            files=files,
        )

        if response.status_code == 204:
            return None

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
        if response.status_code == 404:
            raise NotFoundError(message, **error_kwargs)
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
