from __future__ import annotations

import pytest

from postproxy import (
    PostProxy,
    PostProxyError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    BadRequestError,
)
from tests.conftest import MockTransport


@pytest.mark.asyncio
async def test_auth_header(client, transport: MockTransport):
    transport.add("GET", "/api/profile_groups", 200, {"data": []})
    await client.profile_groups.list()
    assert transport.requests[0].headers["authorization"] == "Bearer test-key"


@pytest.mark.asyncio
async def test_default_profile_group_id(transport: MockTransport):
    import httpx
    http = httpx.AsyncClient(transport=transport, base_url="https://api.postproxy.dev")
    c = PostProxy("key", profile_group_id="pg-default", httpx_client=http)
    transport.add("GET", "/api/profiles", 200, {"data": []})
    await c.profiles.list()
    assert "profile_group_id=pg-default" in str(transport.requests[0].url)


@pytest.mark.asyncio
async def test_override_profile_group_id(transport: MockTransport):
    import httpx
    http = httpx.AsyncClient(transport=transport, base_url="https://api.postproxy.dev")
    c = PostProxy("key", profile_group_id="pg-default", httpx_client=http)
    transport.add("GET", "/api/profiles", 200, {"data": []})
    await c.profiles.list(profile_group_id="pg-override")
    assert "profile_group_id=pg-override" in str(transport.requests[0].url)


@pytest.mark.asyncio
async def test_401_raises_auth_error(client, transport: MockTransport):
    transport.add("GET", "/api/posts/x", 401, {"error": "Invalid API key"})
    with pytest.raises(AuthenticationError) as exc_info:
        await client.posts.get("x")
    assert exc_info.value.status_code == 401
    assert "Invalid API key" in str(exc_info.value)


@pytest.mark.asyncio
async def test_404_raises_not_found(client, transport: MockTransport):
    transport.add("GET", "/api/posts/missing", 404, {"error": "Not found"})
    with pytest.raises(NotFoundError) as exc_info:
        await client.posts.get("missing")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_422_raises_validation_error(client, transport: MockTransport):
    transport.add("POST", "/api/profile_groups", 422, {"error": "Name can't be blank"})
    with pytest.raises(ValidationError):
        await client.profile_groups.create("")


@pytest.mark.asyncio
async def test_400_raises_bad_request(client, transport: MockTransport):
    transport.add("POST", "/api/posts", 400, {"status": 400, "error": "Bad Request", "message": "Invalid JSON"})
    with pytest.raises(BadRequestError):
        await client.posts.create("test", ["p1"])


@pytest.mark.asyncio
async def test_unknown_error_raises_base(client, transport: MockTransport):
    transport.add("GET", "/api/posts/x", 500, {"error": "Internal server error"})
    with pytest.raises(PostProxyError) as exc_info:
        await client.posts.get("x")
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_context_manager():
    async with PostProxy("key") as c:
        assert c.api_key == "key"
