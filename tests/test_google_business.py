from __future__ import annotations

import json

import pytest

from tests.conftest import MockTransport


BASE = "/api/profiles/prof_gbp/google_business"


def _ok(transport: MockTransport, method: str, action: str, body=None) -> None:
    transport.add(method, f"{BASE}/{action}", 200, body if body is not None else {})


@pytest.mark.asyncio
async def test_location_with_read_mask(client, transport: MockTransport):
    _ok(transport, "GET", "location", {"title": "Cafe"})
    result = await client.google_business.location(
        "prof_gbp", "loc_1", read_mask="title,phoneNumbers"
    )
    assert result["title"] == "Cafe"
    params = transport.requests[0].url.params
    assert params["location_id"] == "loc_1"
    assert params["read_mask"] == "title,phoneNumbers"


@pytest.mark.asyncio
async def test_update_location(client, transport: MockTransport):
    _ok(transport, "PATCH", "update_location")
    await client.google_business.update_location(
        "prof_gbp", "loc_1", ["websiteUri"], {"websiteUri": "https://acme.test"}
    )
    assert json.loads(transport.requests[0].content) == {
        "location_id": "loc_1",
        "websiteUri": "https://acme.test",
        "fields": ["websiteUri"],
    }


@pytest.mark.asyncio
async def test_available_location_categories(client, transport: MockTransport):
    _ok(transport, "GET", "available_location_categories", {"categories": []})
    await client.google_business.available_location_categories(
        "prof_gbp", "loc_1", "US", page_size=50
    )
    params = transport.requests[0].url.params
    assert params["region_code"] == "US"
    assert params["page_size"] == "50"
    assert "filter" not in params


@pytest.mark.asyncio
async def test_update_hours_sends_google_shape(client, transport: MockTransport):
    _ok(transport, "PATCH", "update_hours")
    regular_hours = {
        "periods": [
            {"openDay": "MONDAY", "openTime": {"hours": 9}, "closeDay": "MONDAY", "closeTime": {"hours": 17}}
        ]
    }
    await client.google_business.update_hours(
        "prof_gbp", "loc_1", fields=["regularHours"], regular_hours=regular_hours
    )
    assert json.loads(transport.requests[0].content) == {
        "location_id": "loc_1",
        "fields": ["regularHours"],
        "regularHours": regular_hours,
    }


@pytest.mark.asyncio
async def test_update_attributes_services_and_menus(client, transport: MockTransport):
    _ok(transport, "PATCH", "update_attributes")
    _ok(transport, "PATCH", "update_service_list")
    _ok(transport, "PATCH", "update_food_menus")
    gbp = client.google_business
    await gbp.update_attributes(
        "prof_gbp", "loc_1",
        [{"name": "attributes/has_wifi", "values": [True]}],
        attribute_mask=["attributes/has_wifi"],
    )
    await gbp.update_service_list("prof_gbp", "loc_1", [{"freeFormServiceItem": {}}])
    await gbp.update_food_menus("prof_gbp", "loc_1", [{"labels": []}], fields=["menus"])
    attrs, services, menus = [json.loads(r.content) for r in transport.requests]
    assert attrs == {
        "location_id": "loc_1",
        "attributes": [{"name": "attributes/has_wifi", "values": [True]}],
        "attribute_mask": ["attributes/has_wifi"],
    }
    assert services == {"location_id": "loc_1", "serviceItems": [{"freeFormServiceItem": {}}]}
    assert menus == {"location_id": "loc_1", "menus": [{"labels": []}], "fields": ["menus"]}


@pytest.mark.asyncio
async def test_reads(client, transport: MockTransport):
    for action in ("attributes", "available_attributes", "service_list", "food_menus"):
        _ok(transport, "GET", action)
    gbp = client.google_business
    await gbp.attributes("prof_gbp", "loc_1")
    await gbp.available_attributes("prof_gbp", "loc_1", show_all=True)
    await gbp.service_list("prof_gbp", "loc_1")
    await gbp.food_menus("prof_gbp", "loc_1", fields=["menus", "name"])
    urls = [r.url for r in transport.requests]
    assert [u.path for u in urls] == [
        f"{BASE}/attributes",
        f"{BASE}/available_attributes",
        f"{BASE}/service_list",
        f"{BASE}/food_menus",
    ]
    assert urls[1].params["show_all"] == "true"
    assert urls[3].params["fields"] == "menus,name"


@pytest.mark.asyncio
async def test_place_action_links(client, transport: MockTransport):
    _ok(transport, "GET", "place_action_links")
    _ok(transport, "GET", "available_place_action_types")
    _ok(transport, "POST", "create_place_action_link")
    _ok(transport, "PATCH", "update_place_action_link")
    _ok(transport, "DELETE", "delete_place_action_link")
    gbp = client.google_business
    name = "locations/1/placeActionLinks/2"
    await gbp.place_action_links("prof_gbp", "loc_1")
    await gbp.available_place_action_types("prof_gbp", "loc_1", language_code="en")
    await gbp.create_place_action_link(
        "prof_gbp", "loc_1", uri="https://book.test", place_action_type="APPOINTMENT", is_preferred=True
    )
    await gbp.update_place_action_link("prof_gbp", "loc_1", name, ["uri"], uri="https://book2.test")
    await gbp.delete_place_action_link("prof_gbp", "loc_1", name)
    list_, types, create, update, delete = transport.requests
    assert list_.method == "GET"
    assert types.url.params["language_code"] == "en"
    assert json.loads(create.content) == {
        "location_id": "loc_1",
        "uri": "https://book.test",
        "place_action_type": "APPOINTMENT",
        "is_preferred": True,
    }
    assert json.loads(update.content) == {
        "location_id": "loc_1", "name": name, "fields": ["uri"], "uri": "https://book2.test",
    }
    assert delete.method == "DELETE"
    assert delete.url.params["name"] == name
    assert delete.url.params["location_id"] == "loc_1"


@pytest.mark.asyncio
async def test_media(client, transport: MockTransport):
    _ok(transport, "GET", "media")
    _ok(transport, "POST", "create_media")
    _ok(transport, "DELETE", "delete_media")
    gbp = client.google_business
    await gbp.media("prof_gbp", "loc_1", page_size=10)
    await gbp.create_media(
        "prof_gbp", "loc_1", "https://img.test/a.jpg", category="COVER", media_format="PHOTO"
    )
    await gbp.delete_media("prof_gbp", "loc_1", "accounts/1/locations/1/media/9")
    list_, create, delete = transport.requests
    assert list_.url.params["page_size"] == "10"
    assert json.loads(create.content) == {
        "location_id": "loc_1",
        "media_url": "https://img.test/a.jpg",
        "category": "COVER",
        "media_format": "PHOTO",
    }
    assert delete.url.params["media_name"] == "accounts/1/locations/1/media/9"
