from __future__ import annotations

import json

import pytest

from postproxy import (
    DeleteResponse,
    ListResponse,
    PaginatedResponse,
    Webhook,
    WebhookDelivery,
    verify_signature,
)
from tests.conftest import MockTransport


WEBHOOK_DATA = {
    "id": "wh-1",
    "url": "https://example.com/webhook",
    "events": ["post.published", "post.failed"],
    "enabled": True,
    "description": "Test webhook",
    "secret": "whsec_test123",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

DELIVERY_DATA = {
    "id": "del-1",
    "event_id": "evt-1",
    "event_type": "post.published",
    "response_status": 200,
    "attempt_number": 1,
    "success": True,
    "attempted_at": "2025-01-01T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z",
}


@pytest.mark.asyncio
async def test_list_webhooks(client, transport: MockTransport):
    transport.add("GET", "/api/webhooks", 200, {"data": [WEBHOOK_DATA]})
    result = await client.webhooks.list()
    assert isinstance(result, ListResponse)
    assert len(result.data) == 1
    assert isinstance(result.data[0], Webhook)
    assert result.data[0].id == "wh-1"
    assert result.data[0].url == "https://example.com/webhook"


@pytest.mark.asyncio
async def test_get_webhook(client, transport: MockTransport):
    transport.add("GET", "/api/webhooks/wh-1", 200, WEBHOOK_DATA)
    webhook = await client.webhooks.get("wh-1")
    assert isinstance(webhook, Webhook)
    assert webhook.id == "wh-1"
    assert webhook.events == ["post.published", "post.failed"]
    assert webhook.enabled is True


@pytest.mark.asyncio
async def test_create_webhook(client, transport: MockTransport):
    transport.add("POST", "/api/webhooks", 200, WEBHOOK_DATA)
    webhook = await client.webhooks.create(
        "https://example.com/webhook",
        ["post.published", "post.failed"],
        description="Test webhook",
    )
    assert isinstance(webhook, Webhook)
    assert webhook.id == "wh-1"

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["url"] == "https://example.com/webhook"
    assert body["events"] == ["post.published", "post.failed"]
    assert body["description"] == "Test webhook"


@pytest.mark.asyncio
async def test_update_webhook(client, transport: MockTransport):
    updated = {**WEBHOOK_DATA, "enabled": False}
    transport.add("PATCH", "/api/webhooks/wh-1", 200, updated)
    webhook = await client.webhooks.update("wh-1", enabled=False)
    assert webhook.enabled is False

    req = transport.requests[0]
    body = json.loads(req.content)
    assert body["enabled"] is False


@pytest.mark.asyncio
async def test_delete_webhook(client, transport: MockTransport):
    transport.add("DELETE", "/api/webhooks/wh-1", 200, {"deleted": True})
    result = await client.webhooks.delete("wh-1")
    assert isinstance(result, DeleteResponse)
    assert result.deleted is True


@pytest.mark.asyncio
async def test_webhook_deliveries(client, transport: MockTransport):
    transport.add("GET", "/api/webhooks/wh-1/deliveries", 200, {
        "data": [DELIVERY_DATA],
        "total": 1,
        "page": 1,
        "per_page": 10,
    })
    result = await client.webhooks.deliveries("wh-1", page=1, per_page=10)
    assert isinstance(result, PaginatedResponse)
    assert len(result.data) == 1
    assert isinstance(result.data[0], WebhookDelivery)
    assert result.data[0].id == "del-1"
    assert result.data[0].event_type == "post.published"
    assert result.data[0].success is True

    req = transport.requests[0]
    assert "page=1" in str(req.url)
    assert "per_page=10" in str(req.url)


def test_verify_signature_valid():
    payload = '{"event":"post.published","data":{"id":"post-1"}}'
    secret = "whsec_test123"
    signature = "t=1234567890,v1=c8e99efbb07ac8e3152c02dd8d83e8ddb803ae8fb001d9e1ab42fb0b1f405ef2"
    assert verify_signature(payload, signature, secret) is True


def test_verify_signature_invalid():
    payload = '{"event":"post.published","data":{"id":"post-1"}}'
    secret = "whsec_test123"
    signature = "t=1234567890,v1=invalidsignature"
    assert verify_signature(payload, signature, secret) is False


def test_verify_signature_wrong_secret():
    payload = '{"event":"post.published","data":{"id":"post-1"}}'
    secret = "wrong_secret"
    signature = "t=1234567890,v1=c8e99efbb07ac8e3152c02dd8d83e8ddb803ae8fb001d9e1ab42fb0b1f405ef2"
    assert verify_signature(payload, signature, secret) is False


def test_webhook_model():
    webhook = Webhook.model_validate(WEBHOOK_DATA)
    assert webhook.id == "wh-1"
    assert webhook.secret == "whsec_test123"
    assert webhook.events == ["post.published", "post.failed"]


def test_webhook_delivery_model():
    delivery = WebhookDelivery.model_validate(DELIVERY_DATA)
    assert delivery.id == "del-1"
    assert delivery.event_type == "post.published"
    assert delivery.response_status == 200
    assert delivery.success is True


def test_post_with_media_and_thread():
    from postproxy import Post, Media, ThreadChild
    post = Post.model_validate({
        "id": "post-1",
        "body": "Hello",
        "status": "media_processing_failed",
        "created_at": "2025-01-01T00:00:00Z",
        "platforms": [],
        "media": [
            {
                "id": "m-1",
                "status": "processed",
                "content_type": "image/jpeg",
                "source_url": "https://example.com/img.jpg",
                "url": "https://cdn.example.com/img.jpg",
            }
        ],
        "thread": [
            {"id": "t-1", "body": "Thread reply", "media": []},
        ],
    })
    assert post.status == "media_processing_failed"
    assert len(post.media) == 1
    assert isinstance(post.media[0], Media)
    assert post.media[0].status == "processed"
    assert len(post.thread) == 1
    assert isinstance(post.thread[0], ThreadChild)
    assert post.thread[0].body == "Thread reply"


def test_youtube_params_made_for_kids():
    from postproxy import YouTubeParams
    params = YouTubeParams(title="Test", privacy_status="public", made_for_kids=True)
    d = params.model_dump(exclude_none=True)
    assert d["made_for_kids"] is True
