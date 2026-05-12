from __future__ import annotations

import json

import pytest

from tests.conftest import MockTransport


@pytest.mark.asyncio
async def test_connect_bluesky(client, transport: MockTransport):
    transport.add("POST", "/api/profile_groups/pg-1/initialize_connection", 200, {
        "success": True,
        "profile": {
            "id": "pf_bsky_1",
            "network": "bluesky",
            "name": "Jane",
            "external_username": "jane.bsky.social",
        },
    })

    result = await client.profile_groups.connect_bluesky(
        "pg-1", identifier="jane.bsky.social", app_password="xxxx"
    )
    assert result.success
    assert result.profile.id == "pf_bsky_1"

    body = json.loads(transport.requests[0].content)
    assert body == {
        "platform": "bluesky",
        "identifier": "jane.bsky.social",
        "app_password": "xxxx",
    }


@pytest.mark.asyncio
async def test_connect_telegram(client, transport: MockTransport):
    transport.add("POST", "/api/profile_groups/pg-1/initialize_connection", 200, {
        "success": True,
        "profile": {
            "id": "pf_tg_1",
            "network": "telegram",
            "name": "My Bot",
            "external_username": "my_bot",
        },
        "next_step": "Add bot as admin",
    })

    result = await client.profile_groups.connect_telegram("pg-1", bot_token="123:ABC")
    assert result.success
    assert "admin" in result.next_step

    body = json.loads(transport.requests[0].content)
    assert body == {"platform": "telegram", "bot_token": "123:ABC"}
