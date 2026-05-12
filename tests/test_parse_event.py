from __future__ import annotations

import json

import pytest

from postproxy import (
    CommentCreatedData,
    MediaFailedData,
    PlatformPostData,
    PlatformPostInsightsData,
    PostImportedData,
    PostProcessedData,
    ProfileEventData,
    ProfileStatsData,
    WebhookParseError,
    parse_event,
    parse_event_typed,
)


def envelope(type_: str, data: dict) -> dict:
    return {
        "id": "evt_1",
        "type": type_,
        "created_at": "2026-05-12T00:00:00Z",
        "data": data,
    }


def test_parse_post_processed():
    body = envelope("post.processed", {
        "id": "p1",
        "body": "hi",
        "status": "processed",
        "scheduled_at": None,
        "created_at": "2026-05-12T00:00:00Z",
        "platforms": [{"id": "pf1", "platform": "twitter", "name": "X"}],
    })
    e, data = parse_event_typed(json.dumps(body))
    assert e.type == "post.processed"
    assert isinstance(data, PostProcessedData)
    assert data.platforms[0].platform == "twitter"


def test_parse_post_imported():
    body = envelope("post.imported", {
        "id": "p1",
        "body": "x",
        "source": "imported",
        "posted_at": "2026-05-11T00:00:00Z",
        "created_at": "2026-05-12T00:00:00Z",
        "platform": "instagram",
        "profile": {"id": "pf1", "name": "Acme", "platform": "instagram"},
        "platform_post_id": "ig123",
        "public_id": "DEF",
    })
    _, data = parse_event_typed(json.dumps(body))
    assert isinstance(data, PostImportedData)
    assert data.platform_post_id == "ig123"


@pytest.mark.parametrize("type_", [
    "platform_post.published",
    "platform_post.failed",
    "platform_post.failed_waiting_for_retry",
])
def test_parse_platform_post(type_):
    body = envelope(type_, {
        "id": "pp1",
        "post_id": "p1",
        "platform": "twitter",
        "profile_id": "pf1",
        "profile_name": "X",
        "status": "published" if "published" in type_ else "failed",
        "error": None,
        "error_details": None,
        "platform_id": "tw_999",
    })
    e, data = parse_event_typed(json.dumps(body))
    assert e.type == type_
    assert isinstance(data, PlatformPostData)


def test_parse_platform_post_insights():
    body = envelope("platform_post.insights", {
        "id": "pp1",
        "post_id": "p1",
        "platform": "twitter",
        "profile_id": "pf1",
        "profile_name": "X",
        "status": "published",
        "error": None,
        "error_details": None,
        "platform_id": "tw_999",
        "insights": {"impressions": 100, "likes": 5},
    })
    _, data = parse_event_typed(json.dumps(body))
    assert isinstance(data, PlatformPostInsightsData)
    assert data.insights["impressions"] == 100


@pytest.mark.parametrize("type_", ["profile.connected", "profile.disconnected"])
def test_parse_profile_event(type_):
    body = envelope(type_, {
        "id": "pf1",
        "name": "X",
        "platform": "twitter",
        "profile_group_id": "g1",
        "status": "active" if type_ == "profile.connected" else "disconnected",
        "uid": "u1",
        "username": "handle",
    })
    _, data = parse_event_typed(json.dumps(body))
    assert isinstance(data, ProfileEventData)


def test_parse_profile_stats():
    body = envelope("profile.stats", {
        "profile_id": "pf1",
        "platform": "linkedin",
        "placement_id": "org_1",
        "stats": {"followerCount": 4567},
        "recorded_at": "2026-05-12T00:00:00Z",
    })
    _, data = parse_event_typed(json.dumps(body))
    assert isinstance(data, ProfileStatsData)
    assert data.placement_id == "org_1"
    assert data.stats["followerCount"] == 4567


def test_parse_media_failed():
    body = envelope("media.failed", {
        "id": "m1",
        "post_id": "p1",
        "content_type": "image/jpeg",
        "status": "failed",
        "error_message": "broken",
    })
    _, data = parse_event_typed(json.dumps(body))
    assert isinstance(data, MediaFailedData)


def test_parse_comment_created():
    body = envelope("comment.created", {
        "id": "c1",
        "post_id": "p1",
        "platform_post_id": "pp1",
        "platform": "instagram",
        "external_id": "ig_c",
        "parent_external_id": None,
        "body": "great",
        "status": "published",
        "author_external_id": "u",
        "author_name": "Jane",
        "author_username": "jane",
        "author_avatar_url": None,
        "like_count": 0,
        "reply_count": 0,
        "is_hidden": False,
        "permalink": None,
        "platform_data": None,
        "posted_at": None,
        "created_at": "2026-05-12T00:00:00Z",
    })
    _, data = parse_event_typed(json.dumps(body))
    assert isinstance(data, CommentCreatedData)
    assert data.author_name == "Jane"


def test_unknown_event_type_raises():
    with pytest.raises(WebhookParseError):
        parse_event(json.dumps({"id": "e", "type": "foo.bar", "created_at": "x", "data": {}}))


def test_invalid_json_raises():
    with pytest.raises(WebhookParseError):
        parse_event("not json{")


def test_parse_accepts_dict():
    body = envelope("media.failed", {
        "id": "m1", "post_id": "p1", "content_type": "image/jpeg",
        "status": "failed", "error_message": "broken",
    })
    e = parse_event(body)
    assert e.type == "media.failed"
