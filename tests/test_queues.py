from __future__ import annotations

import json

import pytest

from postproxy import (
    DeleteResponse,
    ListResponse,
    NextSlotResponse,
    Queue,
)
from tests.conftest import MockTransport


MOCK_QUEUE = {
    "id": "q1abc",
    "name": "Morning Posts",
    "description": "Daily morning content",
    "timezone": "America/New_York",
    "enabled": True,
    "jitter": 10,
    "profile_group_id": "pg123",
    "timeslots": [
        {"id": 1, "day": 1, "time": "09:00"},
        {"id": 2, "day": 3, "time": "09:00"},
        {"id": 3, "day": 5, "time": "14:00"},
    ],
    "posts_count": 5,
}


@pytest.mark.asyncio
async def test_list_queues(client, transport: MockTransport):
    transport.add("GET", "/api/post_queues", 200, {"data": [MOCK_QUEUE]})
    result = await client.queues.list()
    assert isinstance(result, ListResponse)
    assert len(result.data) == 1
    assert isinstance(result.data[0], Queue)
    assert result.data[0].id == "q1abc"
    assert len(result.data[0].timeslots) == 3


@pytest.mark.asyncio
async def test_list_queues_with_profile_group(client, transport: MockTransport):
    transport.add("GET", "/api/post_queues", 200, {"data": []})
    await client.queues.list(profile_group_id="pg-other")
    req = transport.requests[0]
    assert "profile_group_id=pg-other" in str(req.url)


@pytest.mark.asyncio
async def test_get_queue(client, transport: MockTransport):
    transport.add("GET", "/api/post_queues/q1abc", 200, MOCK_QUEUE)
    queue = await client.queues.get("q1abc")
    assert isinstance(queue, Queue)
    assert queue.id == "q1abc"
    assert queue.name == "Morning Posts"
    assert queue.enabled is True
    assert queue.jitter == 10
    assert len(queue.timeslots) == 3


@pytest.mark.asyncio
async def test_next_slot(client, transport: MockTransport):
    transport.add("GET", "/api/post_queues/q1abc/next_slot", 200, {
        "next_slot": "2026-03-11T14:00:00Z",
    })
    result = await client.queues.next_slot("q1abc")
    assert isinstance(result, NextSlotResponse)
    assert result.next_slot == "2026-03-11T14:00:00Z"


@pytest.mark.asyncio
async def test_create_queue(client, transport: MockTransport):
    transport.add("POST", "/api/post_queues", 200, MOCK_QUEUE)
    queue = await client.queues.create(
        "Morning Posts",
        "pg123",
        description="Daily morning content",
        timezone="America/New_York",
        jitter=10,
        timeslots=[
            {"day": 1, "time": "09:00"},
            {"day": 3, "time": "09:00"},
        ],
    )
    assert isinstance(queue, Queue)
    assert queue.id == "q1abc"

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["profile_group_id"] == "pg123"
    assert body["post_queue"]["name"] == "Morning Posts"
    assert body["post_queue"]["timezone"] == "America/New_York"
    assert body["post_queue"]["jitter"] == 10
    assert body["post_queue"]["queue_timeslots_attributes"] == [
        {"day": 1, "time": "09:00"},
        {"day": 3, "time": "09:00"},
    ]


@pytest.mark.asyncio
async def test_update_queue(client, transport: MockTransport):
    transport.add("PATCH", "/api/post_queues/q1abc", 200, {**MOCK_QUEUE, "enabled": False})
    queue = await client.queues.update("q1abc", enabled=False)
    assert queue.enabled is False

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["post_queue"]["enabled"] is False


@pytest.mark.asyncio
async def test_update_queue_with_timeslots(client, transport: MockTransport):
    transport.add("PATCH", "/api/post_queues/q1abc", 200, MOCK_QUEUE)
    await client.queues.update("q1abc", timeslots=[
        {"day": 2, "time": "10:00"},
        {"id": 1, "_destroy": True},
    ])

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["post_queue"]["queue_timeslots_attributes"] == [
        {"day": 2, "time": "10:00"},
        {"id": 1, "_destroy": True},
    ]


@pytest.mark.asyncio
async def test_delete_queue(client, transport: MockTransport):
    transport.add("DELETE", "/api/post_queues/q1abc", 200, {"deleted": True})
    result = await client.queues.delete("q1abc")
    assert isinstance(result, DeleteResponse)
    assert result.deleted is True
