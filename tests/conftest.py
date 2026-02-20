from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from postproxy import PostProxy


class MockTransport(httpx.AsyncBaseTransport):
    """Records requests and returns canned responses."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.responses: dict[str, tuple[int, Any]] = {}

    def add(self, method: str, path: str, status: int, body: Any) -> None:
        self.responses[f"{method} {path}"] = (status, body)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        key = f"{request.method} {request.url.path}"
        if key in self.responses:
            status, body = self.responses[key]
            return httpx.Response(status, json=body)
        return httpx.Response(404, json={"error": "Not found"})


@pytest.fixture
def transport() -> MockTransport:
    return MockTransport()


@pytest.fixture
def client(transport: MockTransport) -> PostProxy:
    http = httpx.AsyncClient(transport=transport, base_url="https://api.postproxy.dev")
    return PostProxy("test-key", httpx_client=http)
