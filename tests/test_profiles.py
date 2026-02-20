from __future__ import annotations

import pytest

from postproxy import Profile, Placement, SuccessResponse
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
    profiles = await client.profiles.list()
    assert len(profiles) == 1
    assert isinstance(profiles[0], Profile)
    assert profiles[0].name == "My Page"
    assert profiles[0].platform == "facebook"


@pytest.mark.asyncio
async def test_list_profiles_with_group(client, transport: MockTransport):
    transport.add("GET", "/api/profiles", 200, {"data": []})
    await client.profiles.list(profile_group_id="pg-99")
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
    placements = await client.profiles.placements("prof-1")
    assert len(placements) == 2
    assert isinstance(placements[0], Placement)
    assert placements[1].id == "story"


@pytest.mark.asyncio
async def test_delete_profile(client, transport: MockTransport):
    transport.add("DELETE", "/api/profiles/prof-1", 200, {"success": True})
    result = await client.profiles.delete("prof-1")
    assert isinstance(result, SuccessResponse)
    assert result.success is True
