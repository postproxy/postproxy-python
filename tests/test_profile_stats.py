from __future__ import annotations

import pytest

from tests.conftest import MockTransport


@pytest.mark.asyncio
async def test_get_profile_stats_with_placement(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/pf1/stats", 200, {
        "data": {
            "profile_id": "pf1",
            "platform": "linkedin",
            "placement_id": "org_1",
            "records": [
                {"stats": {"followerCount": 100}, "recorded_at": "2026-05-12T00:00:00Z"}
            ],
        }
    })

    result = await client.profiles.get_profile_stats(
        "pf1", placement_id="org_1", from_="2026-04-01T00:00:00Z"
    )

    assert result.data.profile_id == "pf1"
    assert result.data.records[0].stats["followerCount"] == 100

    req = transport.requests[0]
    assert req.method == "GET"
    assert "placement_id=org_1" in str(req.url)
    assert "from=2026-04-01" in str(req.url)


@pytest.mark.asyncio
async def test_get_profile_stats_no_placement(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/bsky1/stats", 200, {
        "data": {
            "profile_id": "bsky1",
            "platform": "bluesky",
            "placement_id": None,
            "records": [],
        }
    })

    result = await client.profiles.get_profile_stats("bsky1")
    assert result.data.placement_id is None
    assert "placement_id" not in str(transport.requests[0].url)
