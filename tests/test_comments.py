from __future__ import annotations

import json

import pytest

from postproxy import (
    AcceptedResponse,
    BulkComment,
    Comment,
    PaginatedResponse,
)
from tests.conftest import MockTransport


MOCK_REPLY = {
    "id": "cmt_def456",
    "external_id": "17858893269123457",
    "body": "Thanks!",
    "status": "synced",
    "author_username": "author",
    "author_avatar_url": None,
    "author_external_id": "67890",
    "parent_external_id": "17858893269123456",
    "like_count": 1,
    "is_hidden": False,
    "permalink": None,
    "platform_data": None,
    "posted_at": "2026-03-25T10:05:00Z",
    "created_at": "2026-03-25T10:05:00Z",
    "replies": [],
}

MOCK_COMMENT = {
    "id": "cmt_abc123",
    "external_id": "17858893269123456",
    "body": "Great post!",
    "status": "synced",
    "author_username": "someuser",
    "author_avatar_url": None,
    "author_external_id": "12345",
    "parent_external_id": None,
    "like_count": 3,
    "is_hidden": False,
    "permalink": None,
    "platform_data": None,
    "posted_at": "2026-03-25T10:00:00Z",
    "created_at": "2026-03-25T10:01:00Z",
    "replies": [MOCK_REPLY],
}


@pytest.mark.asyncio
async def test_list_comments(client, transport: MockTransport):
    transport.add("GET", "/api/posts/post1/comments", 200, {
        "total": 1,
        "page": 0,
        "per_page": 20,
        "data": [MOCK_COMMENT],
    })
    result = await client.comments.list("post1", "prof1")
    assert isinstance(result, PaginatedResponse)
    assert result.total == 1
    assert len(result.data) == 1
    comment = result.data[0]
    assert isinstance(comment, Comment)
    assert comment.id == "cmt_abc123"
    assert comment.body == "Great post!"
    assert comment.like_count == 3
    assert len(comment.replies) == 1
    assert comment.replies[0].id == "cmt_def456"

    req = transport.requests[0]
    assert "profile_id=prof1" in str(req.url)


@pytest.mark.asyncio
async def test_list_comments_with_pagination(client, transport: MockTransport):
    transport.add("GET", "/api/posts/post1/comments", 200, {
        "total": 42,
        "page": 2,
        "per_page": 10,
        "data": [],
    })
    result = await client.comments.list("post1", "prof1", page=2, per_page=10)
    assert result.total == 42
    assert result.page == 2
    assert result.per_page == 10

    req = transport.requests[0]
    assert "page=2" in str(req.url)
    assert "per_page=10" in str(req.url)


@pytest.mark.asyncio
async def test_comment_attachments_and_metadata(client, transport: MockTransport):
    comment = {
        **MOCK_COMMENT,
        "metadata": {"is_verified_user": True, "follower_count": 482},
        "attachments": [
            {
                "id": "att_xyz321",
                "type": "image",
                "url": "https://storage.postproxy.dev/x",
                "status": "processed",
                "external_id": "529233764205652",
            }
        ],
    }
    transport.add("GET", "/api/posts/post1/comments/cmt_abc123", 200, comment)
    result = await client.comments.get("post1", "cmt_abc123", "prof1")
    assert result.metadata["follower_count"] == 482
    assert len(result.attachments) == 1
    assert result.attachments[0].type == "image"
    assert result.attachments[0].status == "processed"


@pytest.mark.asyncio
async def test_get_comment(client, transport: MockTransport):
    transport.add("GET", "/api/posts/post1/comments/cmt_abc123", 200, MOCK_COMMENT)
    comment = await client.comments.get("post1", "cmt_abc123", "prof1")
    assert isinstance(comment, Comment)
    assert comment.id == "cmt_abc123"
    assert comment.body == "Great post!"
    assert len(comment.replies) == 1

    req = transport.requests[0]
    assert "profile_id=prof1" in str(req.url)


@pytest.mark.asyncio
async def test_create_comment(client, transport: MockTransport):
    created = {
        "id": "cmt_ghi789",
        "external_id": None,
        "body": "Thanks for the feedback everyone!",
        "status": "pending",
        "author_username": None,
        "author_avatar_url": None,
        "author_external_id": None,
        "parent_external_id": None,
        "like_count": 0,
        "is_hidden": False,
        "permalink": None,
        "platform_data": None,
        "posted_at": None,
        "created_at": "2026-03-25T12:00:00Z",
        "replies": [],
    }
    transport.add("POST", "/api/posts/post1/comments", 201, created)
    comment = await client.comments.create("post1", "prof1", "Thanks for the feedback everyone!")
    assert isinstance(comment, Comment)
    assert comment.id == "cmt_ghi789"
    assert comment.status == "pending"

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["text"] == "Thanks for the feedback everyone!"
    assert "parent_id" not in body
    assert "profile_id=prof1" in str(req.url)


@pytest.mark.asyncio
async def test_create_reply(client, transport: MockTransport):
    reply = {
        "id": "cmt_reply1",
        "external_id": None,
        "body": "Glad you liked it!",
        "status": "pending",
        "author_username": None,
        "author_avatar_url": None,
        "author_external_id": None,
        "parent_external_id": None,
        "like_count": 0,
        "is_hidden": False,
        "permalink": None,
        "platform_data": None,
        "posted_at": None,
        "created_at": "2026-03-25T12:00:00Z",
        "replies": [],
    }
    transport.add("POST", "/api/posts/post1/comments", 201, reply)
    comment = await client.comments.create(
        "post1", "prof1", "Glad you liked it!", parent_id="cmt_abc123"
    )
    assert comment.id == "cmt_reply1"

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["text"] == "Glad you liked it!"
    assert body["parent_id"] == "cmt_abc123"


@pytest.mark.asyncio
async def test_delete_comment(client, transport: MockTransport):
    transport.add("DELETE", "/api/posts/post1/comments/cmt_abc123", 200, {"accepted": True})
    result = await client.comments.delete("post1", "cmt_abc123", "prof1")
    assert isinstance(result, AcceptedResponse)
    assert result.accepted is True


@pytest.mark.asyncio
async def test_hide_comment(client, transport: MockTransport):
    transport.add("POST", "/api/posts/post1/comments/cmt_abc123/hide", 200, {"accepted": True})
    result = await client.comments.hide("post1", "cmt_abc123", "prof1")
    assert isinstance(result, AcceptedResponse)
    assert result.accepted is True


@pytest.mark.asyncio
async def test_unhide_comment(client, transport: MockTransport):
    transport.add("POST", "/api/posts/post1/comments/cmt_abc123/unhide", 200, {"accepted": True})
    result = await client.comments.unhide("post1", "cmt_abc123", "prof1")
    assert isinstance(result, AcceptedResponse)
    assert result.accepted is True


@pytest.mark.asyncio
async def test_like_comment(client, transport: MockTransport):
    transport.add("POST", "/api/posts/post1/comments/cmt_abc123/like", 200, {"accepted": True})
    result = await client.comments.like("post1", "cmt_abc123", "prof1")
    assert isinstance(result, AcceptedResponse)
    assert result.accepted is True


@pytest.mark.asyncio
async def test_unlike_comment(client, transport: MockTransport):
    transport.add("POST", "/api/posts/post1/comments/cmt_abc123/unlike", 200, {"accepted": True})
    result = await client.comments.unlike("post1", "cmt_abc123", "prof1")
    assert isinstance(result, AcceptedResponse)
    assert result.accepted is True


MOCK_BULK_COMMENT = {
    "post_id": "abc123xyz",
    "profile_id": "prof456",
    "platform": "instagram",
    "id": "cmt_abc123",
    "external_id": "17858893269123456",
    "body": "Great post!",
    "status": "synced",
    "author_username": "someuser",
    "author_avatar_url": None,
    "author_external_id": "12345",
    "metadata": None,
    "parent_external_id": None,
    "like_count": 3,
    "is_hidden": False,
    "permalink": None,
    "platform_data": None,
    "attachments": [],
    "posted_at": "2026-03-25T10:00:00Z",
    "created_at": "2026-03-25T10:01:00Z",
}

MOCK_BULK_REPLY = {
    **MOCK_BULK_COMMENT,
    "id": "cmt_def456",
    "external_id": "17858893269123457",
    "body": "Thanks!",
    "parent_external_id": "17858893269123456",
    "like_count": 1,
}


@pytest.mark.asyncio
async def test_list_comments_with_date_filter(client, transport: MockTransport):
    transport.add(
        "GET",
        "/api/posts/post-1/comments",
        200,
        {"total": 1, "page": 0, "per_page": 20, "data": [MOCK_COMMENT]},
    )
    await client.comments.list(
        "post-1", "prof-1", from_="2026-03-25", to="2026-03-26T12:00:00Z"
    )

    params = transport.requests[0].url.params
    assert params["from"] == "2026-03-25"
    assert params["to"] == "2026-03-26T12:00:00Z"


@pytest.mark.asyncio
async def test_list_all_comments(client, transport: MockTransport):
    transport.add(
        "GET",
        "/api/comments",
        200,
        {
            "total": 2,
            "page": 0,
            "per_page": 50,
            "data": [MOCK_BULK_COMMENT, MOCK_BULK_REPLY],
        },
    )
    result = await client.comments.list_all(
        profiles=["instagram", "prof456"],
        post_ids=["abc123xyz", "def456uvw"],
        from_="2026-03-25",
        per_page=50,
    )

    assert isinstance(result, PaginatedResponse)
    assert result.total == 2
    assert isinstance(result.data[0], BulkComment)
    assert result.data[0].post_id == "abc123xyz"
    assert result.data[0].profile_id == "prof456"
    assert result.data[0].platform == "instagram"
    # Flat: the reply is its own entry, linked by parent_external_id.
    assert result.data[1].parent_external_id == "17858893269123456"

    request = transport.requests[0]
    assert request.url.path == "/api/comments"
    params = request.url.params
    assert params["profiles"] == "instagram,prof456"
    assert params["post_ids"] == "abc123xyz,def456uvw"
    assert params["from"] == "2026-03-25"
    assert params["per_page"] == "50"


@pytest.mark.asyncio
async def test_list_all_comments_without_filters(client, transport: MockTransport):
    transport.add(
        "GET",
        "/api/comments",
        200,
        {"total": 0, "page": 0, "per_page": 20, "data": []},
    )
    await client.comments.list_all()

    params = transport.requests[0].url.params
    assert "profiles" not in params
    assert "post_ids" not in params


@pytest.mark.asyncio
async def test_create_comment_sends_idempotency_key(client, transport: MockTransport):
    transport.add("POST", "/api/posts/post-1/comments", 200, MOCK_COMMENT)
    await client.comments.create(
        "post-1", "prof-1", "Nice", idempotency_key="key-42"
    )
    assert transport.requests[0].headers["idempotency-key"] == "key-42"
