from __future__ import annotations

import json

import pytest

from postproxy import AccountPlacement, ApiKey, PaginatedResponse
from tests.conftest import MockTransport


MOCK_PLACEMENT = {
    "id": "pl_1",
    "platform": "facebook",
    "external_id": "1234567890",
    "name": "Acme Page",
    "avatar_url": None,
    "status": "active",
    "active_profile": {"id": "prof_1", "name": "Jane", "connected": True},
    "linked_profiles": [{"id": "prof_2", "name": "John", "connected": True}],
}

MOCK_KEY = {
    "id": "k1",
    "name": "CI",
    "profile_group_id": "pg_1",
    "sandbox": False,
    "created_at": "2026-09-09T00:00:00Z",
}


@pytest.mark.asyncio
async def test_list_placements(client, transport: MockTransport):
    transport.add("GET", "/api/placements", 200, {
        "total": 1, "page": 2, "per_page": 10, "data": [MOCK_PLACEMENT],
    })
    result = await client.placements.list(page=2, per_page=10)
    assert isinstance(result, PaginatedResponse)
    assert isinstance(result.data[0], AccountPlacement)
    assert result.data[0].active_profile.id == "prof_1"
    assert result.data[0].linked_profiles[0].name == "John"

    url = transport.requests[0].url
    assert url.params["page"] == "2"
    assert url.params["per_page"] == "10"


@pytest.mark.asyncio
async def test_set_active_profile(client, transport: MockTransport):
    transport.add("PATCH", "/api/placements/pl_1/set_active_profile", 200, MOCK_PLACEMENT)
    await client.placements.set_active_profile("pl_1", "prof_2", idempotency_key="idem")
    req = transport.requests[0]
    assert json.loads(req.content) == {"profile_id": "prof_2"}
    assert req.headers["idempotency-key"] == "idem"


@pytest.mark.asyncio
async def test_list_api_keys(client, transport: MockTransport):
    transport.add("GET", "/api/api_keys", 200, {"data": [MOCK_KEY]})
    result = await client.api_keys.list()
    assert isinstance(result.data[0], ApiKey)
    assert result.data[0].name == "CI"
    assert result.data[0].token is None


@pytest.mark.asyncio
async def test_create_api_key(client, transport: MockTransport):
    transport.add("POST", "/api/api_keys", 201, {**MOCK_KEY, "token": "secret"})
    key = await client.api_keys.create("CI", "pg_1", idempotency_key="idem")
    assert key.token == "secret"
    req = transport.requests[0]
    assert json.loads(req.content) == {"name": "CI", "profile_group_id": "pg_1"}
    assert req.headers["idempotency-key"] == "idem"


@pytest.mark.asyncio
async def test_delete_api_key(client, transport: MockTransport):
    transport.add("DELETE", "/api/api_keys/k1", 200, {"deleted": True})
    result = await client.api_keys.delete("k1")
    assert result.deleted is True
    assert transport.requests[0].method == "DELETE"
