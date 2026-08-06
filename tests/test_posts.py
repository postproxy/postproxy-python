from __future__ import annotations

import json

import pytest

from postproxy import Post, PaginatedResponse, DeleteResponse, DeleteOnPlatformResponse, PlatformParams, FacebookParams, StatsResponse, ThreadChildInput, Media, ThreadChild
from tests.conftest import MockTransport


POST_DATA = {
    "id": "abc123",
    "body": "Hello world",
    "status": "draft",
    "scheduled_at": None,
    "created_at": "2025-01-01T00:00:00Z",
    "platforms": [
        {
            "platform": "facebook",
            "status": "processing",
            "params": {"format": "post"},
            "error": None,
            "attempted_at": None,
            "insights": None,
        }
    ],
}


@pytest.mark.asyncio
async def test_list_posts(client, transport: MockTransport):
    transport.add("GET", "/api/posts", 200, {
        "total": 1,
        "page": 0,
        "per_page": 10,
        "data": [POST_DATA],
    })
    result = await client.posts.list()
    assert isinstance(result, PaginatedResponse)
    assert result.total == 1
    assert len(result.data) == 1
    assert isinstance(result.data[0], Post)
    assert result.data[0].id == "abc123"

    req = transport.requests[0]
    assert req.headers["authorization"] == "Bearer test-key"


@pytest.mark.asyncio
async def test_list_posts_with_filters(client, transport: MockTransport):
    transport.add("GET", "/api/posts", 200, {
        "total": 0, "page": 1, "per_page": 5, "data": [],
    })
    await client.posts.list(page=1, per_page=5, status="draft")
    req = transport.requests[0]
    assert "page=1" in str(req.url)
    assert "per_page=5" in str(req.url)
    assert "status=draft" in str(req.url)


@pytest.mark.asyncio
async def test_get_post(client, transport: MockTransport):
    transport.add("GET", "/api/posts/abc123", 200, POST_DATA)
    post = await client.posts.get("abc123")
    assert isinstance(post, Post)
    assert post.body == "Hello world"
    assert post.platforms[0].platform == "facebook"


@pytest.mark.asyncio
async def test_create_post(client, transport: MockTransport):
    transport.add("POST", "/api/posts", 201, POST_DATA)
    post = await client.posts.create(
        "Hello world",
        ["profile-1"],
        platforms=PlatformParams(facebook=FacebookParams(format="post")),
        draft=True,
    )
    assert isinstance(post, Post)
    assert post.id == "abc123"

    req = transport.requests[0]
    import json
    body = json.loads(req.content)
    assert body["post"]["body"] == "Hello world"
    assert body["post"]["draft"] is True
    assert body["profiles"] == ["profile-1"]
    assert body["platforms"]["facebook"]["format"] == "post"


@pytest.mark.asyncio
async def test_create_twitter_poll_post(client, transport: MockTransport):
    from postproxy import TwitterParams

    transport.add("POST", "/api/posts", 201, POST_DATA)
    await client.posts.create(
        "Which framework?",
        ["profile-1"],
        platforms=PlatformParams(
            twitter=TwitterParams(
                format="poll",
                poll_options=["Rails", "Django", "Laravel"],
                poll_duration_minutes=1440,
            )
        ),
    )
    import json
    body = json.loads(transport.requests[0].content)
    assert body["platforms"]["twitter"] == {
        "format": "poll",
        "poll_options": ["Rails", "Django", "Laravel"],
        "poll_duration_minutes": 1440,
    }


@pytest.mark.asyncio
async def test_create_post_with_media(client, transport: MockTransport):
    transport.add("POST", "/api/posts", 201, POST_DATA)
    await client.posts.create(
        "With media",
        ["profile-1"],
        media=["https://example.com/image.jpg", "https://example.com/video.mp4"],
    )
    import json
    body = json.loads(transport.requests[0].content)
    assert body["media"] == ["https://example.com/image.jpg", "https://example.com/video.mp4"]


@pytest.mark.asyncio
async def test_publish_draft(client, transport: MockTransport):
    published = {**POST_DATA, "status": "processing"}
    transport.add("POST", "/api/posts/abc123/publish", 200, published)
    post = await client.posts.publish_draft("abc123")
    assert post.status == "processing"


STATS_RESPONSE = {
    "data": {
        "abc123": {
            "platforms": [
                {
                    "profile_id": "prof_abc",
                    "platform": "instagram",
                    "records": [
                        {
                            "stats": {"impressions": 1200, "likes": 85, "comments": 12, "saved": 8},
                            "raw_stats": {"views": 1200, "like_count": 85},
                            "recorded_at": "2026-02-20T12:00:00Z",
                        },
                        {
                            "stats": {"impressions": 1523, "likes": 102, "comments": 15, "saved": 11},
                            "recorded_at": "2026-02-21T04:00:00Z",
                        },
                    ],
                }
            ]
        },
        "def456": {
            "platforms": [
                {
                    "profile_id": "prof_def",
                    "platform": "twitter",
                    "records": [
                        {
                            "stats": {"impressions": 430, "likes": 22, "retweets": 5},
                            "recorded_at": "2026-02-20T12:00:00Z",
                        }
                    ],
                }
            ]
        },
    }
}


@pytest.mark.asyncio
async def test_stats(client, transport: MockTransport):
    transport.add("GET", "/api/posts/stats", 200, STATS_RESPONSE)
    result = await client.posts.stats(["abc123", "def456"])
    assert isinstance(result, StatsResponse)
    assert "abc123" in result.data
    assert "def456" in result.data

    ig = result.data["abc123"].platforms[0]
    assert ig.profile_id == "prof_abc"
    assert ig.platform == "instagram"
    assert len(ig.records) == 2
    assert ig.records[0].stats["impressions"] == 1200
    # raw_stats carries every metric under its original platform name.
    assert ig.records[0].raw_stats["views"] == 1200
    # Absent raw_stats defaults to an empty dict rather than failing validation.
    assert ig.records[1].raw_stats == {}
    assert ig.records[1].stats["likes"] == 102

    tw = result.data["def456"].platforms[0]
    assert tw.platform == "twitter"
    assert tw.records[0].stats["retweets"] == 5

    req = transport.requests[0]
    assert "post_ids=abc123%2Cdef456" in str(req.url) or "post_ids=abc123,def456" in str(req.url)


@pytest.mark.asyncio
async def test_stats_with_filters(client, transport: MockTransport):
    transport.add("GET", "/api/posts/stats", 200, {"data": {}})
    await client.posts.stats(
        ["abc123"],
        profiles=["instagram", "prof_abc"],
        from_date="2026-02-01T00:00:00Z",
        to_date="2026-02-24T00:00:00Z",
    )
    req = transport.requests[0]
    url = str(req.url)
    assert "post_ids=abc123" in url
    assert "profiles=instagram%2Cprof_abc" in url or "profiles=instagram,prof_abc" in url
    assert "from=2026-02-01" in url
    assert "to=2026-02-24" in url


@pytest.mark.asyncio
async def test_stats_with_datetime_objects(client, transport: MockTransport):
    from datetime import datetime, timezone
    transport.add("GET", "/api/posts/stats", 200, {"data": {}})
    await client.posts.stats(
        ["abc123"],
        from_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        to_date=datetime(2026, 2, 24, tzinfo=timezone.utc),
    )
    req = transport.requests[0]
    url = str(req.url)
    assert "from=2026-02-01" in url
    assert "to=2026-02-24" in url


@pytest.mark.asyncio
async def test_create_post_with_thread(client, transport: MockTransport):
    transport.add("POST", "/api/posts", 201, {
        **POST_DATA,
        "thread": [
            {"id": "t-1", "body": "Thread reply 1", "media": []},
            {"id": "t-2", "body": "Thread reply 2", "media": []},
        ],
    })
    post = await client.posts.create(
        "Hello world",
        ["profile-1"],
        thread=[
            ThreadChildInput(body="Thread reply 1"),
            ThreadChildInput(body="Thread reply 2", media=["https://example.com/img.jpg"]),
        ],
    )
    assert isinstance(post, Post)
    assert len(post.thread) == 2
    assert isinstance(post.thread[0], ThreadChild)
    assert post.thread[0].body == "Thread reply 1"

    import json
    body = json.loads(transport.requests[0].content)
    assert len(body["thread"]) == 2
    assert body["thread"][0]["body"] == "Thread reply 1"
    assert body["thread"][1]["media"] == ["https://example.com/img.jpg"]


@pytest.mark.asyncio
async def test_get_post_with_media_and_thread(client, transport: MockTransport):
    transport.add("GET", "/api/posts/abc123", 200, {
        **POST_DATA,
        "status": "media_processing_failed",
        "media": [
            {"id": "m-1", "status": "processed", "content_type": "image/jpeg", "url": "https://cdn.example.com/img.jpg"},
        ],
        "thread": [
            {"id": "t-1", "body": "Reply", "media": [{"id": "m-2", "status": "pending", "content_type": "video/mp4"}]},
        ],
    })
    post = await client.posts.get("abc123")
    assert post.status == "media_processing_failed"
    assert len(post.media) == 1
    assert isinstance(post.media[0], Media)
    assert post.media[0].status == "processed"
    assert len(post.thread) == 1
    assert post.thread[0].media[0].status == "pending"


@pytest.mark.asyncio
async def test_create_thread_with_media_files(client, transport: MockTransport, tmp_path):
    transport.add("POST", "/api/posts", 201, {
        **POST_DATA,
        "thread": [
            {"id": "t-1", "body": "Thread reply 1", "media": []},
            {
                "id": "t-2",
                "body": "Thread reply 2",
                "media": [{"id": "m-1", "status": "pending", "content_type": "image/png"}],
            },
        ],
    })

    # Create a temp file to upload
    img = tmp_path / "photo.png"
    img.write_bytes(b"\x89PNG fake image data")

    post = await client.posts.create(
        "Thread with files",
        ["profile-1"],
        thread=[
            ThreadChildInput(body="Thread reply 1"),
            ThreadChildInput(body="Thread reply 2", media_files=[str(img)]),
        ],
    )
    assert len(post.thread) == 2

    req = transport.requests[0]
    # Should be multipart, not JSON
    assert "multipart/form-data" in req.headers["content-type"]
    await req.aread()
    body = req.content.decode("utf-8", errors="replace")
    assert "Thread reply 1" in body
    assert "Thread reply 2" in body
    assert "photo.png" in body


@pytest.mark.asyncio
async def test_delete_post(client, transport: MockTransport):
    transport.add("DELETE", "/api/posts/abc123", 200, {"deleted": True})
    result = await client.posts.delete("abc123")
    assert isinstance(result, DeleteResponse)
    assert result.deleted is True


@pytest.mark.asyncio
async def test_delete_post_with_delete_on_platform(client, transport: MockTransport):
    transport.add("DELETE", "/api/posts/abc123", 200, {"deleted": True})
    result = await client.posts.delete("abc123", delete_on_platform=True)
    assert result.deleted is True
    req = transport.requests[0]
    assert "delete_on_platform=true" in str(req.url)


@pytest.mark.asyncio
async def test_delete_on_platform_all(client, transport: MockTransport):
    transport.add(
        "POST",
        "/api/posts/abc123/delete_on_platform",
        200,
        {
            "success": True,
            "deleting": [{"post_profile_id": "pp-1", "platform": "twitter"}],
        },
    )
    result = await client.posts.delete_on_platform("abc123")
    assert isinstance(result, DeleteOnPlatformResponse)
    assert result.success is True
    assert len(result.deleting) == 1
    assert result.deleting[0].platform == "twitter"
    assert result.deleting[0].post_profile_id == "pp-1"


@pytest.mark.asyncio
async def test_delete_on_platform_by_network(client, transport: MockTransport):
    transport.add(
        "POST", "/api/posts/abc123/delete_on_platform", 200,
        {"success": True, "deleting": []},
    )
    await client.posts.delete_on_platform("abc123", network="twitter")
    req = transport.requests[0]
    body = json.loads(req.content)
    assert body == {"network": "twitter"}


@pytest.mark.asyncio
async def test_delete_on_platform_by_profile_id(client, transport: MockTransport):
    transport.add(
        "POST", "/api/posts/abc123/delete_on_platform", 200,
        {"success": True, "deleting": []},
    )
    await client.posts.delete_on_platform("abc123", profile_id="prof-1")
    req = transport.requests[0]
    body = json.loads(req.content)
    assert body == {"profile_id": "prof-1"}


@pytest.mark.asyncio
async def test_delete_on_platform_by_post_profile_id(client, transport: MockTransport):
    transport.add(
        "POST", "/api/posts/abc123/delete_on_platform", 200,
        {"success": True, "deleting": []},
    )
    await client.posts.delete_on_platform("abc123", post_profile_id="pp-1")
    req = transport.requests[0]
    body = json.loads(req.content)
    assert body == {"post_profile_id": "pp-1"}
