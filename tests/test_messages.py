from __future__ import annotations

import json

import pytest

from postproxy import Message, PaginatedResponse
from tests.conftest import MockTransport


MOCK_INBOUND = {
    "id": "msg_111",
    "chat_id": "chat_xyz789",
    "external_id": "mid.abc123",
    "direction": "inbound",
    "body": "Hey, do you ship internationally?",
    "status": "received",
    "tag": None,
    "error_message": None,
    "platform_data": None,
    "external_posted_at": "2026-05-31T14:02:00.000Z",
    "external_delivered_at": None,
    "external_read_at": None,
    "external_edited_at": None,
    "reactions": [
        {"sender_external_id": "psid_123", "emoji": "❤️", "reaction": "love", "at": "2026-05-31T14:04:00.000Z"}
    ],
    "attachments": [],
    "is_unsupported": False,
    "created_at": "2026-05-31T14:02:01.000Z",
}

MOCK_OUTBOUND = {
    "id": "msg_222",
    "chat_id": "chat_xyz789",
    "external_id": None,
    "direction": "outbound",
    "body": "Yes, we ship worldwide!",
    "status": "pending",
    "tag": None,
    "error_message": None,
    "platform_data": None,
    "external_posted_at": None,
    "attachments": [],
    "reactions": [],
    "is_unsupported": False,
    "created_at": "2026-05-31T15:30:05.000Z",
}


@pytest.mark.asyncio
async def test_list_messages(client, transport: MockTransport):
    transport.add("GET", "/api/chats/chat_xyz789/messages", 200, {
        "total": 1,
        "page": 0,
        "per_page": 20,
        "data": [MOCK_INBOUND],
    })
    result = await client.messages.list("chat_xyz789", direction="inbound")
    assert isinstance(result, PaginatedResponse)
    msg = result.data[0]
    assert isinstance(msg, Message)
    assert msg.direction == "inbound"
    assert msg.reactions[0].reaction == "love"

    req = transport.requests[0]
    assert "direction=inbound" in str(req.url)


@pytest.mark.asyncio
async def test_send_text_message(client, transport: MockTransport):
    transport.add("POST", "/api/chats/chat_xyz789/messages", 202, MOCK_OUTBOUND)
    msg = await client.messages.send("chat_xyz789", body="Yes, we ship worldwide!")
    assert msg.id == "msg_222"
    assert msg.status == "pending"

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["body"] == "Yes, we ship worldwide!"


@pytest.mark.asyncio
async def test_send_message_with_tag(client, transport: MockTransport):
    transport.add("POST", "/api/chats/chat_xyz789/messages", 202, MOCK_OUTBOUND)
    await client.messages.send("chat_xyz789", body="Following up.", tag="HUMAN_AGENT")
    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["tag"] == "HUMAN_AGENT"


@pytest.mark.asyncio
async def test_send_media_message(client, transport: MockTransport):
    transport.add("POST", "/api/chats/chat_xyz789/messages", 202, MOCK_OUTBOUND)
    await client.messages.send("chat_xyz789", media=["https://cdn.example.com/photo.png"])
    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["media"] == ["https://cdn.example.com/photo.png"]


@pytest.mark.asyncio
async def test_get_message(client, transport: MockTransport):
    transport.add("GET", "/api/messages/msg_111", 200, MOCK_INBOUND)
    msg = await client.messages.get("msg_111")
    assert msg.id == "msg_111"


@pytest.mark.asyncio
async def test_edit_message(client, transport: MockTransport):
    transport.add("PATCH", "/api/messages/msg_222", 200, {**MOCK_OUTBOUND, "body": "Updated"})
    msg = await client.messages.edit("msg_222", body="Updated")
    assert msg.body == "Updated"

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["body"] == "Updated"


@pytest.mark.asyncio
async def test_react_message(client, transport: MockTransport):
    transport.add("POST", "/api/messages/msg_111/react", 200, MOCK_INBOUND)
    msg = await client.messages.react("msg_111", reaction="love", emoji="❤️")
    assert msg.id == "msg_111"

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["reaction"] == "love"


@pytest.mark.asyncio
async def test_unreact_message(client, transport: MockTransport):
    transport.add("DELETE", "/api/messages/msg_111/unreact", 200, MOCK_INBOUND)
    msg = await client.messages.unreact("msg_111")
    assert msg.id == "msg_111"


@pytest.mark.asyncio
async def test_private_reply(client, transport: MockTransport):
    transport.add("POST", "/api/posts/post1/comments/cmt_abc123/private_reply", 202, {
        **MOCK_OUTBOUND,
        "external_comment_id": "17858893269123456",
    })
    msg = await client.comments.private_reply("post1", "cmt_abc123", "prof1", "DM-ing you the details.")
    assert isinstance(msg, Message)
    assert msg.external_comment_id == "17858893269123456"

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["text"] == "DM-ing you the details."
    assert "profile_id=prof1" in str(req.url)
