from __future__ import annotations

import httpx
import pytest

from postproxy import VERSION, PostProxy
from tests.conftest import MockTransport


@pytest.mark.asyncio
async def test_user_agent_header(transport: MockTransport):
    transport.add("GET", "/api/profiles", 200, {"data": []})
    http = httpx.AsyncClient(transport=transport, base_url="https://api.postproxy.dev")
    c = PostProxy("k", httpx_client=http)
    await c.profiles.list()

    ua = transport.requests[0].headers["user-agent"]
    assert ua.startswith(f"postproxy-python/{VERSION}")
    assert "python/" in ua


def test_version_constant():
    assert VERSION == "1.10.0"
