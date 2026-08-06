from __future__ import annotations

import pytest

import json

from postproxy import (
    AssignedPlacement,
    ConflictError,
    IceBreaker,
    IceBreakersResponse,
    ListResponse,
    PaginatedResponse,
    Placement,
    PostSync,
    Profile,
    SuccessResponse,
)
from tests.conftest import MockTransport


PROFILE_DATA = {
    "id": "prof-1",
    "name": "My Page",
    "status": "active",
    "platform": "facebook",
    "profile_group_id": "pg-1",
    "expires_at": "2025-12-01T00:00:00Z",
    "post_count": 42,
}


@pytest.mark.asyncio
async def test_list_profiles(client, transport: MockTransport):
    transport.add("GET", "/api/profiles", 200, {"data": [PROFILE_DATA]})
    result = await client.profiles.list()
    assert isinstance(result, ListResponse)
    assert len(result.data) == 1
    assert isinstance(result.data[0], Profile)
    assert result.data[0].name == "My Page"
    assert result.data[0].platform == "facebook"


@pytest.mark.asyncio
async def test_list_profiles_with_group(client, transport: MockTransport):
    transport.add("GET", "/api/profiles", 200, {"data": []})
    result = await client.profiles.list(profile_group_id="pg-99")
    assert len(result.data) == 0
    assert "profile_group_id=pg-99" in str(transport.requests[0].url)


@pytest.mark.asyncio
async def test_get_profile(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/prof-1", 200, PROFILE_DATA)
    profile = await client.profiles.get("prof-1")
    assert profile.id == "prof-1"
    assert profile.post_count == 42


@pytest.mark.asyncio
async def test_placements(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/prof-1/placements", 200, {
        "data": [
            {"id": "feed", "name": "Feed"},
            {"id": "story", "name": "Story"},
        ]
    })
    result = await client.profiles.placements("prof-1")
    assert isinstance(result, ListResponse)
    assert len(result.data) == 2
    assert isinstance(result.data[0], Placement)
    assert result.data[1].id == "story"


@pytest.mark.asyncio
async def test_assign_placement_to_group(client, transport: MockTransport):
    transport.add(
        "PATCH",
        "/api/profiles/prof-1/assign_placement_to_group",
        200,
        {"id": "pl-1", "name": "Feed", "metadata": {}, "profile_group_id": "pg-2"},
    )
    result = await client.profiles.assign_placement_to_group(
        "prof-1", placement_id="pl-1", target_profile_group_id="pg-2"
    )
    assert isinstance(result, AssignedPlacement)
    assert result.profile_group_id == "pg-2"
    body = json.loads(transport.requests[0].content)
    assert body == {"placement_id": "pl-1", "target_profile_group_id": "pg-2"}


@pytest.mark.asyncio
async def test_ice_breakers(client, transport: MockTransport):
    transport.add(
        "GET",
        "/api/profiles/prof-1/ice_breakers",
        200,
        {"ice_breakers": [{"question": "What do you do?", "payload": "services"}]},
    )
    result = await client.profiles.ice_breakers("prof-1")
    assert isinstance(result, IceBreakersResponse)
    assert result.ice_breakers[0].question == "What do you do?"


@pytest.mark.asyncio
async def test_set_ice_breakers(client, transport: MockTransport):
    transport.add("POST", "/api/profiles/prof-1/ice_breakers", 200, {"success": True})
    result = await client.profiles.set_ice_breakers(
        "prof-1",
        [IceBreaker(question="What do you do?", payload="services")],
    )
    assert isinstance(result, SuccessResponse)
    assert result.success is True
    body = json.loads(transport.requests[0].content)
    assert body == {
        "ice_breakers": [{"question": "What do you do?", "payload": "services"}]
    }


@pytest.mark.asyncio
async def test_delete_ice_breakers(client, transport: MockTransport):
    transport.add(
        "DELETE", "/api/profiles/prof-1/ice_breakers", 200, {"success": True}
    )
    result = await client.profiles.delete_ice_breakers("prof-1")
    assert result.success is True
    assert transport.requests[0].method == "DELETE"


@pytest.mark.asyncio
async def test_delete_profile(client, transport: MockTransport):
    transport.add("DELETE", "/api/profiles/prof-1", 200, {"success": True})
    result = await client.profiles.delete("prof-1")
    assert isinstance(result, SuccessResponse)
    assert result.success is True


POST_SYNC_DATA = {
    "id": "sync456def",
    "profile_id": "prof-1",
    "kind": "posts",
    "trigger": "backfill",
    "status": "running",
    "started_at": "2026-08-06T09:15:02.000Z",
    "completed_at": None,
    "posts_seen": 150,
    "posts_imported": 143,
    "backfill_from": "2025-01-01T00:00:00.000Z",
    "oldest_posted_at": "2025-11-04T18:22:00.000Z",
    "error": None,
    "created_at": "2026-08-06T09:15:00.000Z",
}


@pytest.mark.asyncio
async def test_backfill_posts(client, transport: MockTransport):
    transport.add(
        "POST",
        "/api/profiles/prof-1/backfill_posts",
        202,
        {**POST_SYNC_DATA, "status": "pending"},
    )
    sync = await client.profiles.backfill_posts("prof-1", from_="2025-01-01")

    assert isinstance(sync, PostSync)
    assert sync.id == "sync456def"
    assert sync.trigger == "backfill"
    assert sync.status == "pending"

    request = transport.requests[0]
    assert request.method == "POST"
    assert json.loads(request.content) == {"from": "2025-01-01"}


@pytest.mark.asyncio
async def test_backfill_posts_sends_idempotency_key(client, transport: MockTransport):
    transport.add("POST", "/api/profiles/prof-1/backfill_posts", 202, POST_SYNC_DATA)
    await client.profiles.backfill_posts(
        "prof-1", from_="2025-01-01", idempotency_key="key-1"
    )
    assert transport.requests[0].headers["idempotency-key"] == "key-1"


@pytest.mark.asyncio
async def test_backfill_posts_conflict(client, transport: MockTransport):
    transport.add(
        "POST",
        "/api/profiles/prof-1/backfill_posts",
        409,
        {
            "error": "A posts backfill is already running for this profile",
            "profile_sync_id": "sync456def",
        },
    )
    with pytest.raises(ConflictError) as exc:
        await client.profiles.backfill_posts("prof-1", from_="2025-01-01")

    assert exc.value.status_code == 409
    assert exc.value.response["profile_sync_id"] == "sync456def"


@pytest.mark.asyncio
async def test_list_post_syncs(client, transport: MockTransport):
    transport.add(
        "GET",
        "/api/profiles/prof-1/post_syncs",
        200,
        {"total": 1, "page": 0, "per_page": 25, "data": [POST_SYNC_DATA]},
    )
    result = await client.profiles.post_syncs(
        "prof-1", trigger="backfill", status="running", per_page=25
    )

    assert isinstance(result, PaginatedResponse)
    assert result.total == 1
    assert result.data[0].posts_imported == 143
    assert result.data[0].oldest_posted_at is not None

    url = transport.requests[0].url
    assert url.params["trigger"] == "backfill"
    assert url.params["status"] == "running"
    assert url.params["per_page"] == "25"


@pytest.mark.asyncio
async def test_get_post_sync(client, transport: MockTransport):
    transport.add(
        "GET",
        "/api/profiles/prof-1/post_syncs/sync456def",
        200,
        {**POST_SYNC_DATA, "status": "completed"},
    )
    sync = await client.profiles.post_sync("prof-1", "sync456def")

    assert sync.status == "completed"
    assert transport.requests[0].url.path == "/api/profiles/prof-1/post_syncs/sync456def"
