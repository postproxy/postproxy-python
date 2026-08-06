from __future__ import annotations

from postproxy import (
    Post,
    Profile,
    ProfileGroup,
    PaginatedResponse,
    PlatformParams,
    FacebookParams,
    InstagramParams,
    TikTokParams,
    LinkedInParams,
    YouTubeParams,
    PinterestParams,
)


def test_post_model():
    post = Post.model_validate({
        "id": "1",
        "body": "test",
        "status": "draft",
        "created_at": "2025-01-01T00:00:00Z",
        "platforms": [],
    })
    assert post.id == "1"
    assert post.scheduled_at is None


def test_post_with_platforms():
    post = Post.model_validate({
        "id": "1",
        "body": "test",
        "status": "processed",
        "created_at": "2025-01-01T00:00:00Z",
        "platforms": [
            {
                "platform": "instagram",
                "status": "published",
                "params": {"format": "reel"},
                "insights": {"impressions": 1500, "on": "2025-01-02T00:00:00Z"},
            }
        ],
    })
    assert post.platforms[0].insights.impressions == 1500


def test_profile_model():
    profile = Profile.model_validate({
        "id": "p1",
        "name": "Test",
        "status": "active",
        "platform": "tiktok",
        "profile_group_id": "pg1",
        "expires_at": None,
        "post_count": 0,
    })
    assert profile.platform == "tiktok"


def test_profile_group_model():
    pg = ProfileGroup.model_validate({"id": "pg1", "name": "G", "profiles_count": 5})
    assert pg.profiles_count == 5


def test_paginated_response():
    resp = PaginatedResponse[Post].model_validate({
        "total": 100,
        "page": 2,
        "per_page": 10,
        "data": [{
            "id": "1",
            "body": "hi",
            "status": "draft",
            "created_at": "2025-01-01T00:00:00Z",
            "platforms": [],
        }],
    })
    assert resp.total == 100
    assert len(resp.data) == 1


def test_platform_params_serialization():
    params = PlatformParams(
        facebook=FacebookParams(format="story"),
        instagram=InstagramParams(format="reel", collaborators=["user1"]),
        tiktok=TikTokParams(privacy_status="PUBLIC_TO_EVERYONE", made_with_ai=True),
        linkedin=LinkedInParams(organization_id="org-1"),
        youtube=YouTubeParams(title="My Video", privacy_status="unlisted"),
        pinterest=PinterestParams(title="Pin", board_id="board-1"),
    )
    d = params.model_dump(exclude_none=True)
    assert d["facebook"]["format"] == "story"
    assert d["instagram"]["collaborators"] == ["user1"]
    assert d["tiktok"]["privacy_status"] == "PUBLIC_TO_EVERYONE"
    assert d["linkedin"]["organization_id"] == "org-1"
    assert d["youtube"]["privacy_status"] == "unlisted"
    assert d["pinterest"]["board_id"] == "board-1"


def test_platform_params_exclude_none():
    params = PlatformParams(facebook=FacebookParams(format="post"))
    d = params.model_dump(exclude_none=True)
    assert "instagram" not in d
    assert d == {"facebook": {"format": "post"}}


def test_stats_response_model():
    from postproxy import StatsResponse
    resp = StatsResponse.model_validate({
        "data": {
            "post1": {
                "platforms": [
                    {
                        "profile_id": "prof1",
                        "platform": "instagram",
                        "records": [
                            {
                                "stats": {"impressions": 100, "likes": 10},
                                "recorded_at": "2026-02-20T12:00:00Z",
                            }
                        ],
                    }
                ]
            }
        }
    })
    assert "post1" in resp.data
    assert resp.data["post1"].platforms[0].platform == "instagram"
    assert resp.data["post1"].platforms[0].records[0].stats["impressions"] == 100


def test_stats_response_empty():
    from postproxy import StatsResponse
    resp = StatsResponse.model_validate({"data": {}})
    assert resp.data == {}


def test_instagram_params_accept_user_tags():
    from postproxy import InstagramParams, InstagramUserTag

    params = InstagramParams(
        format="post",
        user_tags=[
            InstagramUserTag(username="natgeo", x=0.5, y=0.4),
            InstagramUserTag(username="nasa", x=0.2, y=0.8, media_index=1),
            # Video slides are tagged by username only.
            InstagramUserTag(username="spacex", media_index=2),
        ],
    )

    assert params.user_tags is not None
    assert len(params.user_tags) == 3
    assert params.user_tags[0].x == 0.5
    assert params.user_tags[2].media_index == 2
    dumped = params.model_dump(exclude_none=True)
    assert dumped["user_tags"][2] == {"username": "spacex", "media_index": 2}


def test_post_sync_shape():
    from postproxy import PostSync

    sync = PostSync.model_validate(
        {
            "id": "sync456def",
            "profile_id": "prof123abc",
            "kind": "posts",
            "trigger": "backfill",
            "status": "running",
            "started_at": "2026-08-06T09:15:02.000Z",
            "completed_at": None,
            "posts_seen": 150,
            "posts_imported": 143,
            "backfill_from": "2025-01-01T00:00:00.000Z",
            "oldest_posted_at": "2025-11-04T18:22:00.000Z",
            "error": None,
            "created_at": "2026-08-06T09:15:00.000Z",
        }
    )

    assert sync.trigger == "backfill"
    assert sync.posts_imported < sync.posts_seen
    assert sync.completed_at is None
