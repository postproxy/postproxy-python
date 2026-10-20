from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal

if TYPE_CHECKING:
    from .._client import PostProxy


def _compact(values: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in values.items() if v is not None}


class GoogleBusinessResource:
    """Manage a Google Business Profile location's own data — hours,
    attributes, services, menus, action links and photos — separate from
    posting to it.

    `location_id` is the placement id from `profiles.placements(profile_id)`.
    Google's payloads are camelCased and passed through untouched, so you can
    PATCH back exactly what you GET. Updates take a `fields` list naming which
    top-level fields to change (Google's update mask).
    """

    def __init__(self, client: PostProxy) -> None:
        self._client = client

    @staticmethod
    def _path(profile_id: str, action: str) -> str:
        return f"/profiles/{profile_id}/google_business/{action}"

    async def _read(
        self,
        profile_id: str,
        action: str,
        location_id: str,
        query: Dict[str, Any],
        profile_group_id: str | None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"location_id": location_id}
        for key, value in _compact(query).items():
            params[key] = str(value).lower() if isinstance(value, bool) else value
        return await self._client._request(
            "GET",
            self._path(profile_id, action),
            params=params,
            profile_group_id=profile_group_id,
        )

    async def _write(
        self,
        method: str,
        profile_id: str,
        action: str,
        location_id: str,
        body: Dict[str, Any],
        profile_group_id: str | None,
        idempotency_key: str | None,
    ) -> Dict[str, Any]:
        return await self._client._request(
            method,
            self._path(profile_id, action),
            json={"location_id": location_id, **_compact(body)},
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )

    async def _remove(
        self,
        profile_id: str,
        action: str,
        location_id: str,
        query: Dict[str, Any],
        profile_group_id: str | None,
        idempotency_key: str | None,
    ) -> Dict[str, Any]:
        return await self._client._request(
            "DELETE",
            self._path(profile_id, action),
            params={"location_id": location_id, **query},
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )

    # --- Location ---

    async def location(
        self,
        profile_id: str,
        location_id: str,
        *,
        read_mask: str | None = None,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._read(
            profile_id, "location", location_id, {"read_mask": read_mask}, profile_group_id
        )

    async def update_location(
        self,
        profile_id: str,
        location_id: str,
        fields: List[str],
        location: Dict[str, Any],
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """`location` holds the Google fields to change (e.g. `title`,
        `phoneNumbers`, `websiteUri`); `fields` names them."""
        return await self._write(
            "PATCH",
            profile_id,
            "update_location",
            location_id,
            {**location, "fields": fields},
            profile_group_id,
            idempotency_key,
        )

    async def available_location_categories(
        self,
        profile_id: str,
        location_id: str,
        region_code: str,
        *,
        language_code: str | None = None,
        filter: str | None = None,
        view: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._read(
            profile_id,
            "available_location_categories",
            location_id,
            {
                "region_code": region_code,
                "language_code": language_code,
                "filter": filter,
                "view": view,
                "page_size": page_size,
                "page_token": page_token,
            },
            profile_group_id,
        )

    async def update_hours(
        self,
        profile_id: str,
        location_id: str,
        *,
        fields: List[str] | None = None,
        regular_hours: Dict[str, Any] | None = None,
        special_hours: Dict[str, Any] | None = None,
        more_hours: List[Dict[str, Any]] | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """Update opening hours. Each hours argument is Google's camelCase
        object, sent as `regularHours`, `specialHours` and `moreHours`."""
        return await self._write(
            "PATCH",
            profile_id,
            "update_hours",
            location_id,
            {
                "fields": fields,
                "regularHours": regular_hours,
                "specialHours": special_hours,
                "moreHours": more_hours,
            },
            profile_group_id,
            idempotency_key,
        )

    # --- Attributes ---

    async def attributes(
        self,
        profile_id: str,
        location_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._read(profile_id, "attributes", location_id, {}, profile_group_id)

    async def available_attributes(
        self,
        profile_id: str,
        location_id: str,
        *,
        category_name: str | None = None,
        region_code: str | None = None,
        language_code: str | None = None,
        show_all: bool | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._read(
            profile_id,
            "available_attributes",
            location_id,
            {
                "category_name": category_name,
                "region_code": region_code,
                "language_code": language_code,
                "show_all": show_all,
                "page_size": page_size,
                "page_token": page_token,
            },
            profile_group_id,
        )

    async def update_attributes(
        self,
        profile_id: str,
        location_id: str,
        attributes: List[Dict[str, Any]],
        *,
        attribute_mask: List[str] | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._write(
            "PATCH",
            profile_id,
            "update_attributes",
            location_id,
            {"attributes": attributes, "attribute_mask": attribute_mask},
            profile_group_id,
            idempotency_key,
        )

    # --- Services & food menus ---

    async def service_list(
        self,
        profile_id: str,
        location_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._read(profile_id, "service_list", location_id, {}, profile_group_id)

    async def update_service_list(
        self,
        profile_id: str,
        location_id: str,
        service_items: List[Dict[str, Any]],
        *,
        fields: List[str] | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._write(
            "PATCH",
            profile_id,
            "update_service_list",
            location_id,
            {"serviceItems": service_items, "fields": fields},
            profile_group_id,
            idempotency_key,
        )

    async def food_menus(
        self,
        profile_id: str,
        location_id: str,
        *,
        fields: List[str] | None = None,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._read(
            profile_id,
            "food_menus",
            location_id,
            {"fields": ",".join(fields) if fields is not None else None},
            profile_group_id,
        )

    async def update_food_menus(
        self,
        profile_id: str,
        location_id: str,
        menus: List[Dict[str, Any]],
        *,
        fields: List[str] | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._write(
            "PATCH",
            profile_id,
            "update_food_menus",
            location_id,
            {"menus": menus, "fields": fields},
            profile_group_id,
            idempotency_key,
        )

    # --- Place action links (booking, ordering, ...) ---

    async def place_action_links(
        self,
        profile_id: str,
        location_id: str,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._read(
            profile_id,
            "place_action_links",
            location_id,
            {"page_size": page_size, "page_token": page_token},
            profile_group_id,
        )

    async def available_place_action_types(
        self,
        profile_id: str,
        location_id: str,
        *,
        language_code: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._read(
            profile_id,
            "available_place_action_types",
            location_id,
            {
                "language_code": language_code,
                "page_size": page_size,
                "page_token": page_token,
            },
            profile_group_id,
        )

    async def create_place_action_link(
        self,
        profile_id: str,
        location_id: str,
        *,
        uri: str,
        place_action_type: str,
        is_preferred: bool | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """`place_action_type` is e.g. APPOINTMENT, ONLINE_APPOINTMENT,
        DINING_RESERVATION, FOOD_ORDERING, FOOD_DELIVERY, FOOD_TAKEOUT,
        SHOP_ONLINE."""
        return await self._write(
            "POST",
            profile_id,
            "create_place_action_link",
            location_id,
            {
                "uri": uri,
                "place_action_type": place_action_type,
                "is_preferred": is_preferred,
            },
            profile_group_id,
            idempotency_key,
        )

    async def update_place_action_link(
        self,
        profile_id: str,
        location_id: str,
        name: str,
        fields: List[str],
        *,
        uri: str | None = None,
        place_action_type: str | None = None,
        is_preferred: bool | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """`name` is the link's resource name from :meth:`place_action_links`."""
        return await self._write(
            "PATCH",
            profile_id,
            "update_place_action_link",
            location_id,
            {
                "name": name,
                "fields": fields,
                "uri": uri,
                "place_action_type": place_action_type,
                "is_preferred": is_preferred,
            },
            profile_group_id,
            idempotency_key,
        )

    async def delete_place_action_link(
        self,
        profile_id: str,
        location_id: str,
        name: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._remove(
            profile_id,
            "delete_place_action_link",
            location_id,
            {"name": name},
            profile_group_id,
            idempotency_key,
        )

    # --- Media ---

    async def media(
        self,
        profile_id: str,
        location_id: str,
        *,
        page_size: int | None = None,
        page_token: str | None = None,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._read(
            profile_id,
            "media",
            location_id,
            {"page_size": page_size, "page_token": page_token},
            profile_group_id,
        )

    async def create_media(
        self,
        profile_id: str,
        location_id: str,
        media_url: str,
        *,
        category: str | None = None,
        media_format: Literal["PHOTO", "VIDEO"] | None = None,
        description: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """`category` is e.g. COVER, PROFILE, LOGO, EXTERIOR, INTERIOR,
        PRODUCT, ADDITIONAL."""
        return await self._write(
            "POST",
            profile_id,
            "create_media",
            location_id,
            {
                "media_url": media_url,
                "category": category,
                "media_format": media_format,
                "description": description,
            },
            profile_group_id,
            idempotency_key,
        )

    async def delete_media(
        self,
        profile_id: str,
        location_id: str,
        media_name: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """`media_name` is the item's resource name from :meth:`media`."""
        return await self._remove(
            profile_id,
            "delete_media",
            location_id,
            {"media_name": media_name},
            profile_group_id,
            idempotency_key,
        )
