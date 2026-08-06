from __future__ import annotations

import pytest

from postproxy import (
    PostProxy,
    PostProxyError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    BadRequestError,
    ConflictError,
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
async def test_409_raises_conflict_error(client, transport: MockTransport):
    transport.add(
        "POST",
        "/api/posts",
        409,
        {"error": "Duplicate post", "duplicate_post_id": "post-1"},
    )
    with pytest.raises(ConflictError) as exc_info:
        await client.posts.create("test", ["p1"])

    assert exc_info.value.status_code == 409
    assert exc_info.value.response["duplicate_post_id"] == "post-1"


@pytest.mark.asyncio
async def test_idempotency_key_header_is_sent(client, transport: MockTransport):
    transport.add("POST", "/api/posts", 200, {"id": "post-1", "body": "hi", "status": "processed", "created_at": "2026-08-06T00:00:00Z"})
    await client.posts.create(
        "hi", ["p1"], idempotency_key="3f8b1c94-6a2d-4f0e-9d31-7c5e2a8b4f10"
    )
    assert (
        transport.requests[0].headers["idempotency-key"]
        == "3f8b1c94-6a2d-4f0e-9d31-7c5e2a8b4f10"
    )


@pytest.mark.asyncio
async def test_idempotency_key_header_omitted_by_default(
    client, transport: MockTransport
):
    transport.add("POST", "/api/posts", 200, {"id": "post-1", "body": "hi", "status": "processed", "created_at": "2026-08-06T00:00:00Z"})
    await client.posts.create("hi", ["p1"])
    assert "idempotency-key" not in transport.requests[0].headers


@pytest.mark.asyncio
async def test_context_manager():
    async with PostProxy("key") as c:
        assert c.api_key == "key"
