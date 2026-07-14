from __future__ import annotations

import pytest

import json

from postproxy import (
    AssignedPlacement,
    IceBreaker,
    IceBreakersResponse,
    ListResponse,
    Placement,
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
