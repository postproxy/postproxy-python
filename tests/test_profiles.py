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


def test_profile_new_fields():
    profile = Profile.model_validate({
        **PROFILE_DATA,
        "status": "inactive",
        "username": "acme",
        "inactive_reason": "network_taken",
        "platform_id": "123",
        "avatar_url": "https://img.test/a.png",
        "platform_url": "https://facebook.com/acme",
        "placements_sync_status": "synced",
    })
    assert profile.inactive_reason == "network_taken"
    assert profile.platform_id == "123"


@pytest.mark.asyncio
async def test_daily_stats_with_attribution(client, transport: MockTransport):
    from postproxy import DailyStatsResponse

    transport.add("GET", "/api/profiles/p1/daily_stats", 200, {
        "data": {
            "profile_id": "p1",
            "platform": "facebook",
            "placement_id": "pl1",
            "attribution": "publish",
            "from": "2026-09-01",
            "to": "2026-09-30",
            "records": [{"date": "2026-09-01", "impressions": 10, "platform_stats": None}],
            "metrics": {},
        }
    })
    result = await client.profiles.daily_stats(
        "p1", placement_id="pl1", from_="2026-09-01", to="2026-09-30", attribution="publish"
    )
    assert isinstance(result, DailyStatsResponse)
    assert result.data.from_ == "2026-09-01"
    assert result.data.records[0].impressions == 10
    params = transport.requests[0].url.params
    assert params["attribution"] == "publish"
    assert params["placement_id"] == "pl1"
    assert params["from"] == "2026-09-01"


@pytest.mark.asyncio
async def test_follower_history(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/p1/follower_history", 200, {
        "data": {"profile_id": "p1", "records": [{"date": "2026-09-01", "followers_total": 100}]}
    })
    result = await client.profiles.follower_history("p1", from_="2026-09-01")
    assert result.data.records[0].followers_total == 100
    assert transport.requests[0].url.params["from"] == "2026-09-01"


@pytest.mark.asyncio
async def test_participant_status(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/p1/participants/igsid_1", 200, {
        "is_verified_user": True, "fetched_at": "2026-09-01T00:00:00Z",
    })
    result = await client.profiles.participant_status("p1", "igsid_1")
    assert result.is_verified_user is True


@pytest.mark.asyncio
async def test_resolve_mention(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/p1/resolve_mention", 200, {
        "urn": "urn:li:organization:1", "type": "organization", "name": "Acme", "vanity_name": "acme",
    })
    result = await client.profiles.resolve_mention("p1", "https://www.linkedin.com/company/acme")
    assert result.urn == "urn:li:organization:1"
    assert transport.requests[0].url.params["url"] == "https://www.linkedin.com/company/acme"


@pytest.mark.asyncio
async def test_instagram_available_audio(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/p1/instagram/available_audio", 200, {"data": [{"id": "a1"}]})
    result = await client.profiles.instagram_available_audio(
        "p1", audio_type="music", search_query="summer"
    )
    assert result.data[0]["id"] == "a1"
    params = transport.requests[0].url.params
    assert params["audio_type"] == "music"
    assert params["search_query"] == "summer"


@pytest.mark.asyncio
async def test_facebook_page_read_and_update(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/p1/facebook/page", 200, {"about": "Hi"})
    transport.add("PATCH", "/api/profiles/p1/facebook/update_page", 200, {"about": "New about"})
    page = await client.profiles.facebook_page("p1", "page_1", fields="about,website")
    await client.profiles.update_facebook_page("p1", "page_1", {"about": "New about"})
    assert page["about"] == "Hi"
    read, update = transport.requests
    assert read.url.params["page_id"] == "page_1"
    assert read.url.params["fields"] == "about,website"
    assert json.loads(update.content) == {"about": "New about", "page_id": "page_1"}


@pytest.mark.asyncio
async def test_assign_to_group(client, transport: MockTransport):
    transport.add("PATCH", "/api/profiles/p1/assign_to_group", 200, {**PROFILE_DATA, "id": "p1"})
    profile = await client.profiles.assign_to_group("p1", "pg_2")
    assert profile.id == "p1"
    assert json.loads(transport.requests[0].content) == {"target_profile_group_id": "pg_2"}


@pytest.mark.asyncio
async def test_chat_backfill_and_syncs(client, transport: MockTransport):
    from postproxy import ChatSync

    sync = {
        "id": "cs1",
        "profile_id": "p1",
        "kind": "chats",
        "trigger": "backfill",
        "status": "pending",
        "chats_seen": 0,
        "messages_imported": 0,
        "created_at": "2026-10-01T00:00:00Z",
    }
    transport.add("POST", "/api/profiles/p1/backfill_chats", 202, sync)
    transport.add("GET", "/api/profiles/p1/chat_syncs", 200, {"total": 1, "page": 1, "per_page": 5, "data": [sync]})
    transport.add("GET", "/api/profiles/p1/chat_syncs/cs1", 200, sync)
    started = await client.profiles.backfill_chats("p1", from_="2026-01-01T00:00:00Z")
    listed = await client.profiles.chat_syncs("p1", status="running", per_page=5)
    one = await client.profiles.chat_sync("p1", "cs1")
    assert isinstance(started, ChatSync)
    assert started.chats_seen == 0
    assert listed.data[0].id == "cs1"
    assert one.id == "cs1"
    start, list_, _ = transport.requests
    assert json.loads(start.content) == {"from": "2026-01-01T00:00:00Z"}
    assert list_.url.params["status"] == "running"
    assert list_.url.params["per_page"] == "5"
