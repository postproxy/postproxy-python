from __future__ import annotations

import json

import pytest

from postproxy import WhatsAppTemplate
from tests.conftest import MockTransport


BASE = "/api/profiles/prof_wa/whatsapp"

MOCK_TEMPLATE = {
    "id": "tpl_1",
    "external_id": "998877",
    "profile_id": "prof_wa",
    "name": "order_update",
    "language": "en_US",
    "category": "UTILITY",
    "status": "APPROVED",
    "parameter_format": "POSITIONAL",
    "components": [{"type": "BODY", "text": "Order {{1}} shipped"}],
    "variable_count": 1,
    "created_at": "2026-09-28T00:00:00Z",
    "updated_at": "2026-09-28T00:00:00Z",
}


# --- Templates ---


@pytest.mark.asyncio
async def test_list_templates(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/prof_wa/templates", 200, {"data": [MOCK_TEMPLATE]})
    result = await client.whatsapp_templates.list("prof_wa", status="APPROVED", refresh=True)
    assert isinstance(result.data[0], WhatsAppTemplate)
    assert result.data[0].name == "order_update"
    params = transport.requests[0].url.params
    assert params["status"] == "APPROVED"
    assert params["refresh"] == "true"


@pytest.mark.asyncio
async def test_get_template_by_name_is_url_encoded(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/prof_wa/templates/order update", 200, MOCK_TEMPLATE)
    await client.whatsapp_templates.get("prof_wa", "order update", language="en_US")
    url = transport.requests[0].url
    assert url.raw_path.decode().startswith("/api/profiles/prof_wa/templates/order%20update")
    assert url.params["language"] == "en_US"


@pytest.mark.asyncio
async def test_create_update_delete_template(client, transport: MockTransport):
    transport.add("POST", "/api/profiles/prof_wa/templates", 201, MOCK_TEMPLATE)
    transport.add("PATCH", "/api/profiles/prof_wa/templates/tpl_1", 200, MOCK_TEMPLATE)
    transport.add("DELETE", "/api/profiles/prof_wa/templates/order_update", 200, {"success": True})
    t = client.whatsapp_templates
    await t.create(
        "prof_wa",
        name="order_update",
        category="UTILITY",
        language="en_US",
        components=[{"type": "BODY", "text": "Order {{1}} shipped"}],
    )
    await t.update("prof_wa", "tpl_1", message_send_ttl_seconds=3600)
    await t.delete("prof_wa", "order_update")
    create, update, delete = transport.requests
    assert json.loads(create.content) == {
        "name": "order_update",
        "category": "UTILITY",
        "language": "en_US",
        "components": [{"type": "BODY", "text": "Order {{1}} shipped"}],
    }
    assert update.method == "PATCH"
    assert json.loads(update.content) == {"message_send_ttl_seconds": 3600}
    assert delete.method == "DELETE"
    assert "language" not in delete.url.params


@pytest.mark.asyncio
async def test_template_library(client, transport: MockTransport):
    transport.add("GET", "/api/profiles/prof_wa/templates/library", 200, {"data": []})
    await client.whatsapp_templates.library("prof_wa", name="delivery")
    assert transport.requests[0].url.params["name"] == "delivery"


# --- Number administration ---


@pytest.mark.asyncio
async def test_reads_pass_phone_number_id_as_query(client, transport: MockTransport):
    transport.add("GET", f"{BASE}/number_info", 200, {"verified_name": "Acme"})
    transport.add("GET", f"{BASE}/blocked_users", 200, {"data": []})
    info = await client.whatsapp.number_info("prof_wa", "pn_1")
    await client.whatsapp.blocked_users("prof_wa", "pn_1", limit=10)
    assert info["verified_name"] == "Acme"
    info_url, blocked_url = [r.url for r in transport.requests]
    assert info_url.params["phone_number_id"] == "pn_1"
    assert blocked_url.params["limit"] == "10"
    assert "after" not in blocked_url.params


@pytest.mark.asyncio
async def test_writes_send_json_bodies(client, transport: MockTransport):
    for method, action in [
        ("POST", "register_phone_number"),
        ("POST", "request_verification_code"),
        ("POST", "verify_phone_number"),
        ("PATCH", "update_business_profile"),
        ("POST", "update_business_profile_photo"),
        ("POST", "request_display_name_change"),
        ("PUT", "set_username"),
        ("POST", "block_users"),
    ]:
        transport.add(method, f"{BASE}/{action}", 200, {"success": True})
    wa = client.whatsapp
    await wa.register_phone_number("prof_wa", "pn_1", "123456")
    await wa.request_verification_code("prof_wa", "pn_1", method="SMS", language="en")
    await wa.verify_phone_number("prof_wa", "pn_1", "000111")
    await wa.update_business_profile("prof_wa", "pn_1", about="Hi", websites=["https://acme.test"])
    await wa.update_business_profile_photo("prof_wa", "pn_1", url="https://img.test/a.png")
    await wa.request_display_name_change("prof_wa", "pn_1", "Acme Co")
    await wa.set_username("prof_wa", "pn_1", "acme", transfer_action="force_transfer")
    await wa.block_users("prof_wa", "pn_1", ["15551234567"])
    reqs = transport.requests
    assert [r.method for r in reqs] == ["POST", "POST", "POST", "PATCH", "POST", "POST", "PUT", "POST"]
    bodies = [json.loads(r.content) for r in reqs]
    assert bodies[0] == {"phone_number_id": "pn_1", "pin": "123456"}
    assert bodies[1] == {"phone_number_id": "pn_1", "method": "SMS", "language": "en"}
    assert bodies[3] == {"phone_number_id": "pn_1", "about": "Hi", "websites": ["https://acme.test"]}
    assert bodies[4] == {"phone_number_id": "pn_1", "url": "https://img.test/a.png"}
    assert bodies[5] == {"phone_number_id": "pn_1", "display_name": "Acme Co"}
    assert bodies[6] == {"phone_number_id": "pn_1", "username": "acme", "transfer_action": "force_transfer"}
    assert bodies[7] == {"phone_number_id": "pn_1", "users": ["15551234567"]}


@pytest.mark.asyncio
async def test_delete_username_uses_query_params(client, transport: MockTransport):
    transport.add("DELETE", f"{BASE}/delete_username", 200, {"success": True})
    await client.whatsapp.delete_username("prof_wa", "pn_1")
    req = transport.requests[0]
    assert req.method == "DELETE"
    assert req.content == b""
    assert req.url.params["phone_number_id"] == "pn_1"


@pytest.mark.asyncio
async def test_groups(client, transport: MockTransport):
    for method, action in [
        ("POST", "create_group"),
        ("GET", "group"),
        ("PATCH", "update_group"),
        ("POST", "add_group_participants"),
        ("POST", "create_group_invite_link"),
        ("POST", "approve_group_join_requests"),
        ("DELETE", "delete_group"),
    ]:
        transport.add(method, f"{BASE}/{action}", 200, {})
    wa = client.whatsapp
    await wa.create_group("prof_wa", "pn_1", "Customers", join_approval_mode="approval_required")
    await wa.group("prof_wa", "pn_1", "g_1")
    await wa.update_group("prof_wa", "pn_1", "g_1", subject="VIPs")
    await wa.add_group_participants("prof_wa", "pn_1", "g_1", ["15551234567"])
    await wa.create_group_invite_link("prof_wa", "pn_1", "g_1")
    await wa.approve_group_join_requests("prof_wa", "pn_1", "g_1", ["15557654321"])
    await wa.delete_group("prof_wa", "pn_1", "g_1")
    reqs = transport.requests
    assert json.loads(reqs[0].content) == {
        "phone_number_id": "pn_1", "subject": "Customers", "join_approval_mode": "approval_required",
    }
    assert reqs[1].url.params["group_id"] == "g_1"
    assert json.loads(reqs[2].content) == {"phone_number_id": "pn_1", "group_id": "g_1", "subject": "VIPs"}
    assert reqs[3].url.path == f"{BASE}/add_group_participants"
    assert json.loads(reqs[3].content) == {
        "phone_number_id": "pn_1", "group_id": "g_1", "phone_numbers": ["15551234567"],
    }
    assert reqs[4].url.path.endswith("/create_group_invite_link")
    assert reqs[5].url.path.endswith("/approve_group_join_requests")
    assert reqs[6].method == "DELETE"
    assert reqs[6].url.params["group_id"] == "g_1"


@pytest.mark.asyncio
async def test_conversion_events_without_phone_number_id(client, transport: MockTransport):
    transport.add("GET", f"{BASE}/dataset", 200, {"id": "ds_1"})
    transport.add("POST", f"{BASE}/send_conversion_event", 200, {"events_received": 1})
    await client.whatsapp.dataset("prof_wa")
    await client.whatsapp.send_conversion_event(
        "prof_wa",
        event_name="Purchase",
        event_id="order-42",
        chat_id="chat_1",
        currency="USD",
        value=19.99,
    )
    dataset, event = transport.requests
    assert "phone_number_id" not in dataset.url.params
    assert json.loads(event.content) == {
        "event_name": "Purchase",
        "event_id": "order-42",
        "chat_id": "chat_1",
        "currency": "USD",
        "value": 19.99,
    }
