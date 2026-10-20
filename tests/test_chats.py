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


@pytest.mark.asyncio
async def test_create_whatsapp_chat_on_placement(client, transport: MockTransport):
    transport.add("POST", "/api/profiles/prof_wa/chats", 201, {**MOCK_CHAT, "platform": "whatsapp"})
    await client.chats.create("prof_wa", "15551234567", placement_id="pn_1")
    assert json.loads(transport.requests[0].content) == {
        "participant_external_id": "15551234567",
        "placement_id": "pn_1",
    }


@pytest.mark.asyncio
async def test_chat_whatsapp_fields(client, transport: MockTransport):
    transport.add("GET", "/api/chats/chat_wa", 200, {
        **MOCK_CHAT,
        "platform": "whatsapp",
        "external_placement_id": "pn_1",
        "group": False,
        "within_messaging_window": True,
    })
    chat = await client.chats.get("chat_wa")
    assert chat.external_placement_id == "pn_1"
    assert chat.group is False
    assert chat.within_messaging_window is True


@pytest.mark.asyncio
async def test_mark_read(client, transport: MockTransport):
    transport.add("POST", "/api/chats/chat_xyz789/mark_read", 200, MOCK_CHAT)
    chat = await client.chats.mark_read("chat_xyz789")
    assert isinstance(chat, Chat)
    assert transport.requests[0].method == "POST"


@pytest.mark.asyncio
async def test_start_and_stop_typing(client, transport: MockTransport):
    transport.add("POST", "/api/chats/chat_xyz789/start_typing", 202, {"accepted": True})
    transport.add("POST", "/api/chats/chat_xyz789/stop_typing", 202, {"accepted": True})
    started = await client.chats.start_typing("chat_xyz789")
    await client.chats.stop_typing("chat_xyz789")
    assert started.accepted is True
    assert transport.requests[0].url.path.endswith("/start_typing")
    assert transport.requests[1].url.path.endswith("/stop_typing")
