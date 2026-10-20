from __future__ import annotations

import json

import pytest

from postproxy import (
    CommentCreatedData,
    MediaFailedData,
    MessageEventData,
    PlatformPostData,
    PlatformPostInsightsData,
    PostImportedData,
    PostProcessedData,
    ProfileCommentCreatedData,
    ProfileEventData,
    ProfileStatsData,
    ReactionEventData,
    WebhookParseError,
    parse_event,
    parse_event_typed,
)


def _message(**overrides):
    base = {
        "id": "msg_1",
        "chat_id": "chat_1",
        "external_id": "mid.1",
        "direction": "inbound",
        "body": "hi",
        "status": "received",
        "created_at": "2026-06-01T00:00:00Z",
    }
    base.update(overrides)
    return base


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


@pytest.mark.parametrize("type_", [
    "message.received",
    "message.sent",
    "message.delivered",
    "message.read",
    "message.edited",
    "message.deleted",
    "message.failed_waiting_for_retry",
    "message.failed",
])
def test_parse_message_event(type_):
    body = envelope(type_, {"message": _message()})
    e, data = parse_event_typed(json.dumps(body))
    assert e.type == type_
    assert isinstance(data, MessageEventData)
    assert data.message.id == "msg_1"


def test_parse_reaction_received():
    body = envelope("reaction.received", {
        "message": _message(reactions=[
            {"sender_external_id": "psid_123", "emoji": "❤️", "reaction": "love", "at": "2026-06-01T15:02:00Z"}
        ]),
        "sender_external_id": "psid_123",
        "action": "react",
        "reaction": "love",
        "emoji": "❤️",
        "occurred_at": "2026-06-01T15:02:00Z",
    })
    _, data = parse_event_typed(json.dumps(body))
    assert isinstance(data, ReactionEventData)
    assert data.action == "react"
    assert data.message.reactions[0].reaction == "love"


def test_parse_profile_comment_created():
    body = envelope("profile_comment.created", {
        "id": "abc123",
        "profile_id": "prof123",
        "platform": "google_business",
        "placement_id": "accounts/1/locations/2",
        "external_id": "accounts/1/locations/2/reviews/A",
        "parent_external_id": None,
        "body": "Great coffee!",
        "status": "synced",
        "author_username": "Jane D.",
        "author_avatar_url": None,
        "platform_data": {"star_rating": 5},
        "posted_at": "2026-05-10T11:55:00Z",
        "created_at": "2026-05-13T18:00:00Z",
    })
    _, data = parse_event_typed(json.dumps(body))
    assert isinstance(data, ProfileCommentCreatedData)
    assert data.platform_data["star_rating"] == 5


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


NEW_EVENT_TYPES = [
    "platform_post.edited",
    "platform_post.edit_failed",
    "profile.placements_synced",
    "placement.orphaned",
    "placement.restored",
    "comment.failed",
    "comment.failed_waiting_for_retry",
    "comment.delivery_unconfirmed",
    "comment.edited",
    "comment.edit_failed",
    "profile_comment.failed",
    "profile_comment.failed_waiting_for_retry",
    "profile_comment.deleted",
    "referral.received",
    "message_template.status_updated",
    "message_template.category_updated",
    "placement.name_status_updated",
    "placement.quality_updated",
    "whatsapp.automatic_event",
]


@pytest.mark.parametrize("type_", NEW_EVENT_TYPES)
def test_parse_new_event_types(type_):
    from postproxy import event_data_model

    e = parse_event(envelope(type_, {"id": "x"}))
    assert e.type == type_
    assert event_data_model(type_) is not None


def test_parse_message_template_status_updated():
    from postproxy import MessageTemplateEventData

    _, data = parse_event_typed(envelope("message_template.status_updated", {
        "id": "tpl_1",
        "external_id": "998877",
        "profile_id": "prof_wa",
        "platform": "whatsapp",
        "name": "order_update",
        "language": "en_US",
        "category": "UTILITY",
        "status": "APPROVED",
        "rejected_reason": None,
        "quality_score": None,
    }))
    assert isinstance(data, MessageTemplateEventData)
    assert data.status == "APPROVED"


def test_parse_platform_post_edit_failed():
    _, data = parse_event_typed(envelope("platform_post.edit_failed", {
        "id": "pp1",
        "post_id": "p1",
        "platform": "youtube",
        "profile_id": "prof1",
        "profile_name": "Channel",
        "status": "published",
        "error": "Title too long",
    }))
    assert isinstance(data, PlatformPostData)
    assert data.error == "Title too long"


def test_parse_placement_quality_updated_keeps_extra_fields():
    from postproxy import PlacementEventData

    _, data = parse_event_typed(envelope("placement.quality_updated", {
        "id": "pn_1",
        "name": "+1 555 123 4567",
        "platform": "whatsapp",
        "profile_group_id": None,
        "profile_id": "prof_wa",
        "profile_name": "Acme",
        "metadata": {},
        "event": "UPGRADE",
        "current_limit": "TIER_10K",
    }))
    assert isinstance(data, PlacementEventData)
    assert data.current_limit == "TIER_10K"


def test_parse_profile_placements_synced():
    from postproxy import PlacementsSyncedData

    _, data = parse_event_typed(envelope("profile.placements_synced", {
        "id": "prof1",
        "name": "Acme",
        "platform": "facebook",
        "profile_group_id": "pg1",
        "status": "active",
        "uid": "u1",
        "platform_id": "123",
        "placements_sync_status": "synced",
        "placements": [{"id": "page_1", "name": "Acme Page", "metadata": {}}],
    }))
    assert isinstance(data, PlacementsSyncedData)
    assert data.placements[0].id == "page_1"


def test_parse_referral_received():
    from postproxy import ReferralEventData

    _, data = parse_event_typed(envelope("referral.received", {
        "chat": {
            "id": "chat_1",
            "profile_id": "prof_wa",
            "platform": "whatsapp",
            "external_placement_id": "pn_1",
            "group": False,
            "participant_external_id": "15551234567",
        },
        "source": "ADS",
        "ctwa_clid": "clid_1",
    }))
    assert isinstance(data, ReferralEventData)
    assert data.chat.external_placement_id == "pn_1"
    assert data.ctwa_clid == "clid_1"
