from __future__ import annotations

import json

import pytest

from postproxy import Chat, PaginatedResponse
from tests.conftest import MockTransport


MOCK_CHAT = {
    "id": "chat_xyz789",
    "profile_id": "prof_abc123",
    "platform": "instagram",
    "participant_external_id": "igsid_8675309",
    "participant_username": "jane_doe",
    "participant_name": "Jane Doe",
    "participant_avatar_url": "https://storage.postproxy.dev/x.jpg",
    "external_conversation_id": None,
    "last_inbound_at": "2026-05-31T14:02:00.000Z",
    "last_outbound_at": "2026-05-31T15:10:00.000Z",
    "last_message_at": "2026-05-31T15:10:00.000Z",
    "metadata": {"is_verified_user": False, "follower_count": 482},
    "created_at": "2026-04-12T08:00:00.000Z",
}


@pytest.mark.asyncio
async def test_list_chats(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/prof_abc123/chats", 200, {
        "total": 1,
        "page": 0,
        "per_page": 20,
        "data": [MOCK_CHAT],
    })
    result = await client.chats.list("prof_abc123", per_page=20)
    assert isinstance(result, PaginatedResponse)
    assert result.total == 1
    chat = result.data[0]
    assert isinstance(chat, Chat)
    assert chat.id == "chat_xyz789"
    assert chat.participant_username == "jane_doe"
    assert chat.metadata["follower_count"] == 482

    req = transport.requests[0]
    assert "per_page=20" in str(req.url)


@pytest.mark.asyncio
async def test_create_chat(client, transport: MockTransport):
    transport.add("POST", "/api/profiles/prof_abc123/chats", 201, MOCK_CHAT)
    chat = await client.chats.create(
        "prof_abc123", "igsid_8675309", participant_username="jane_doe"
    )
    assert isinstance(chat, Chat)
    assert chat.id == "chat_xyz789"

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["participant_external_id"] == "igsid_8675309"
    assert body["participant_username"] == "jane_doe"


@pytest.mark.asyncio
async def test_get_chat(client, transport: MockTransport):
    transport.add("GET", "/api/chats/chat_xyz789", 200, MOCK_CHAT)
    chat = await client.chats.get("chat_xyz789")
    assert chat.id == "chat_xyz789"


@pytest.mark.asyncio
async def test_archive_chat(client, transport: MockTransport):
    transport.add("POST", "/api/chats/chat_xyz789/archive", 200, {**MOCK_CHAT, "archived": True})
    chat = await client.chats.archive("chat_xyz789")
    assert chat.archived is True


@pytest.mark.asyncio
async def test_unarchive_chat(client, transport: MockTransport):
    transport.add("DELETE", "/api/chats/chat_xyz789/archive", 200, {**MOCK_CHAT, "archived": False})
    chat = await client.chats.unarchive("chat_xyz789")
    assert chat.archived is False
