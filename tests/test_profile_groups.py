from __future__ import annotations

import json

import pytest

from postproxy import ProfileGroup, DeleteResponse, ConnectionResponse
from tests.conftest import MockTransport


PG_DATA = {"id": "pg-1", "name": "My Group", "profiles_count": 3}


@pytest.mark.asyncio
async def test_list_profile_groups(client, transport: MockTransport):
    transport.add("GET", "/api/profile_groups", 200, {"data": [PG_DATA]})
    groups = await client.profile_groups.list()
    assert len(groups) == 1
    assert isinstance(groups[0], ProfileGroup)
    assert groups[0].name == "My Group"


@pytest.mark.asyncio
async def test_get_profile_group(client, transport: MockTransport):
    transport.add("GET", "/api/profile_groups/pg-1", 200, PG_DATA)
    group = await client.profile_groups.get("pg-1")
    assert group.profiles_count == 3


@pytest.mark.asyncio
async def test_create_profile_group(client, transport: MockTransport):
    transport.add("POST", "/api/profile_groups", 201, PG_DATA)
    group = await client.profile_groups.create("My Group")
    assert group.name == "My Group"
    body = json.loads(transport.requests[0].content)
    assert body == {"profile_group": {"name": "My Group"}}


@pytest.mark.asyncio
async def test_delete_profile_group(client, transport: MockTransport):
    transport.add("DELETE", "/api/profile_groups/pg-1", 200, {"deleted": True})
    result = await client.profile_groups.delete("pg-1")
    assert isinstance(result, DeleteResponse)
    assert result.deleted is True


@pytest.mark.asyncio
async def test_initialize_connection(client, transport: MockTransport):
    transport.add("POST", "/api/profile_groups/pg-1/initialize_connection", 200, {
        "url": "https://app.postproxy.dev/partner_connect/abc",
        "success": True,
    })
    result = await client.profile_groups.initialize_connection(
        "pg-1", "facebook", "https://example.com/callback"
    )
    assert isinstance(result, ConnectionResponse)
    assert result.success is True
    assert "partner_connect" in result.url

    body = json.loads(transport.requests[0].content)
    assert body["platform"] == "facebook"
    assert body["redirect_url"] == "https://example.com/callback"
