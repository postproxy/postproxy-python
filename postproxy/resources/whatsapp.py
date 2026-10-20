from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal

from .._types import WhatsAppMedia

if TYPE_CHECKING:
    from .._client import PostProxy

JoinApprovalMode = Literal["approval_required", "auto_approve"]


class WhatsAppResource:
    """WhatsApp number administration: registration, business profile, display
    name, username, blocked users, groups and conversion events.

    `phone_number_id` is the placement id from `profiles.placements(profile_id)`.
    Dataset and conversion calls are account-level and don't take one.
    """

    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def _call(
        self,
        method: str,
        profile_id: str,
        action: str,
        values: Dict[str, Any],
        profile_group_id: str | None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        path = f"/profiles/{profile_id}/whatsapp/{action}"
        compact = {k: v for k, v in values.items() if v is not None}

        if method in ("GET", "DELETE"):
            return await self._client._request(
                method,
                path,
                params=compact or None,
                profile_group_id=profile_group_id,
                idempotency_key=idempotency_key,
            )
        return await self._client._request(
            method,
            path,
            json=compact,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )

    # --- Phone number ---

    async def number_info(
        self, profile_id: str, phone_number_id: str, *, profile_group_id: str | None = None
    ) -> Dict[str, Any]:
        return await self._call(
            "GET", profile_id, "number_info", {"phone_number_id": phone_number_id}, profile_group_id
        )

    async def register_phone_number(
        self,
        profile_id: str,
        phone_number_id: str,
        pin: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """`pin` is the 6-digit two-step verification PIN."""
        return await self._call(
            "POST",
            profile_id,
            "register_phone_number",
            {"phone_number_id": phone_number_id, "pin": pin},
            profile_group_id,
            idempotency_key,
        )

    async def request_verification_code(
        self,
        profile_id: str,
        phone_number_id: str,
        *,
        method: Literal["SMS", "VOICE"] | None = None,
        language: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "POST",
            profile_id,
            "request_verification_code",
            {"phone_number_id": phone_number_id, "method": method, "language": language},
            profile_group_id,
            idempotency_key,
        )

    async def verify_phone_number(
        self,
        profile_id: str,
        phone_number_id: str,
        code: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "POST",
            profile_id,
            "verify_phone_number",
            {"phone_number_id": phone_number_id, "code": code},
            profile_group_id,
            idempotency_key,
        )

    # --- Business profile ---

    async def business_profile(
        self, profile_id: str, phone_number_id: str, *, profile_group_id: str | None = None
    ) -> Dict[str, Any]:
        return await self._call(
            "GET", profile_id, "business_profile", {"phone_number_id": phone_number_id}, profile_group_id
        )

    async def update_business_profile(
        self,
        profile_id: str,
        phone_number_id: str,
        *,
        about: str | None = None,
        address: str | None = None,
        description: str | None = None,
        email: str | None = None,
        websites: List[str] | None = None,
        vertical: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "PATCH",
            profile_id,
            "update_business_profile",
            {
                "phone_number_id": phone_number_id,
                "about": about,
                "address": address,
                "description": description,
                "email": email,
                "websites": websites,
                "vertical": vertical,
            },
            profile_group_id,
            idempotency_key,
        )

    async def update_business_profile_photo(
        self,
        profile_id: str,
        phone_number_id: str,
        *,
        url: str | None = None,
        data: str | None = None,
        content_type: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """Pass a public `url`, or base64 `data` with its `content_type`
        (image/jpeg or image/png)."""
        return await self._call(
            "POST",
            profile_id,
            "update_business_profile_photo",
            {
                "phone_number_id": phone_number_id,
                "url": url,
                "data": data,
                "content_type": content_type,
            },
            profile_group_id,
            idempotency_key,
        )

    # --- Display name ---

    async def display_name(
        self, profile_id: str, phone_number_id: str, *, profile_group_id: str | None = None
    ) -> Dict[str, Any]:
        return await self._call(
            "GET", profile_id, "display_name", {"phone_number_id": phone_number_id}, profile_group_id
        )

    async def request_display_name_change(
        self,
        profile_id: str,
        phone_number_id: str,
        display_name: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """Meta reviews the new name; the outcome arrives as the
        `placement.name_status_updated` webhook."""
        return await self._call(
            "POST",
            profile_id,
            "request_display_name_change",
            {"phone_number_id": phone_number_id, "display_name": display_name},
            profile_group_id,
            idempotency_key,
        )

    # --- Username ---

    async def username(
        self, profile_id: str, phone_number_id: str, *, profile_group_id: str | None = None
    ) -> Dict[str, Any]:
        return await self._call(
            "GET", profile_id, "username", {"phone_number_id": phone_number_id}, profile_group_id
        )

    async def set_username(
        self,
        profile_id: str,
        phone_number_id: str,
        username: str,
        *,
        transfer_action: Literal["none", "force_transfer"] | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "PUT",
            profile_id,
            "set_username",
            {
                "phone_number_id": phone_number_id,
                "username": username,
                "transfer_action": transfer_action,
            },
            profile_group_id,
            idempotency_key,
        )

    async def delete_username(
        self,
        profile_id: str,
        phone_number_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "DELETE",
            profile_id,
            "delete_username",
            {"phone_number_id": phone_number_id},
            profile_group_id,
            idempotency_key,
        )

    async def username_suggestions(
        self, profile_id: str, phone_number_id: str, *, profile_group_id: str | None = None
    ) -> Dict[str, Any]:
        return await self._call(
            "GET",
            profile_id,
            "username_suggestions",
            {"phone_number_id": phone_number_id},
            profile_group_id,
        )

    # --- Blocked users ---

    async def blocked_users(
        self,
        profile_id: str,
        phone_number_id: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "GET",
            profile_id,
            "blocked_users",
            {"phone_number_id": phone_number_id, "limit": limit, "after": after},
            profile_group_id,
        )

    async def blocked_user_status(
        self,
        profile_id: str,
        phone_number_id: str,
        user: str,
        *,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "GET",
            profile_id,
            "blocked_user_status",
            {"phone_number_id": phone_number_id, "user": user},
            profile_group_id,
        )

    async def block_users(
        self,
        profile_id: str,
        phone_number_id: str,
        users: List[str],
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """`users` are phone numbers or WhatsApp ids."""
        return await self._call(
            "POST",
            profile_id,
            "block_users",
            {"phone_number_id": phone_number_id, "users": users},
            profile_group_id,
            idempotency_key,
        )

    async def unblock_users(
        self,
        profile_id: str,
        phone_number_id: str,
        users: List[str],
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "POST",
            profile_id,
            "unblock_users",
            {"phone_number_id": phone_number_id, "users": users},
            profile_group_id,
            idempotency_key,
        )

    # --- Groups ---

    async def groups(
        self,
        profile_id: str,
        phone_number_id: str,
        *,
        limit: int | None = None,
        after: str | None = None,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "GET",
            profile_id,
            "groups",
            {"phone_number_id": phone_number_id, "limit": limit, "after": after},
            profile_group_id,
        )

    async def create_group(
        self,
        profile_id: str,
        phone_number_id: str,
        subject: str,
        *,
        description: str | None = None,
        join_approval_mode: JoinApprovalMode | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "POST",
            profile_id,
            "create_group",
            {
                "phone_number_id": phone_number_id,
                "subject": subject,
                "description": description,
                "join_approval_mode": join_approval_mode,
            },
            profile_group_id,
            idempotency_key,
        )

    async def group(
        self,
        profile_id: str,
        phone_number_id: str,
        group_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "GET",
            profile_id,
            "group",
            {"phone_number_id": phone_number_id, "group_id": group_id},
            profile_group_id,
        )

    async def update_group(
        self,
        profile_id: str,
        phone_number_id: str,
        group_id: str,
        *,
        subject: str | None = None,
        description: str | None = None,
        join_approval_mode: JoinApprovalMode | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "PATCH",
            profile_id,
            "update_group",
            {
                "phone_number_id": phone_number_id,
                "group_id": group_id,
                "subject": subject,
                "description": description,
                "join_approval_mode": join_approval_mode,
            },
            profile_group_id,
            idempotency_key,
        )

    async def delete_group(
        self,
        profile_id: str,
        phone_number_id: str,
        group_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "DELETE",
            profile_id,
            "delete_group",
            {"phone_number_id": phone_number_id, "group_id": group_id},
            profile_group_id,
            idempotency_key,
        )

    async def _group_members(
        self,
        action: str,
        profile_id: str,
        phone_number_id: str,
        group_id: str,
        phone_numbers: List[str],
        profile_group_id: str | None,
        idempotency_key: str | None,
    ) -> Dict[str, Any]:
        return await self._call(
            "POST",
            profile_id,
            action,
            {
                "phone_number_id": phone_number_id,
                "group_id": group_id,
                "phone_numbers": phone_numbers,
            },
            profile_group_id,
            idempotency_key,
        )

    async def add_group_participants(
        self,
        profile_id: str,
        phone_number_id: str,
        group_id: str,
        phone_numbers: List[str],
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._group_members(
            "add_group_participants", profile_id, phone_number_id, group_id,
            phone_numbers, profile_group_id, idempotency_key,
        )

    async def remove_group_participants(
        self,
        profile_id: str,
        phone_number_id: str,
        group_id: str,
        phone_numbers: List[str],
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._group_members(
            "remove_group_participants", profile_id, phone_number_id, group_id,
            phone_numbers, profile_group_id, idempotency_key,
        )

    async def create_group_invite_link(
        self,
        profile_id: str,
        phone_number_id: str,
        group_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "POST",
            profile_id,
            "create_group_invite_link",
            {"phone_number_id": phone_number_id, "group_id": group_id},
            profile_group_id,
            idempotency_key,
        )

    async def group_join_requests(
        self,
        profile_id: str,
        phone_number_id: str,
        group_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "GET",
            profile_id,
            "group_join_requests",
            {"phone_number_id": phone_number_id, "group_id": group_id},
            profile_group_id,
        )

    async def approve_group_join_requests(
        self,
        profile_id: str,
        phone_number_id: str,
        group_id: str,
        phone_numbers: List[str],
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._group_members(
            "approve_group_join_requests", profile_id, phone_number_id, group_id,
            phone_numbers, profile_group_id, idempotency_key,
        )

    async def reject_group_join_requests(
        self,
        profile_id: str,
        phone_number_id: str,
        group_id: str,
        phone_numbers: List[str],
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._group_members(
            "reject_group_join_requests", profile_id, phone_number_id, group_id,
            phone_numbers, profile_group_id, idempotency_key,
        )

    # --- Conversions (account-level) ---

    async def dataset(
        self, profile_id: str, *, profile_group_id: str | None = None
    ) -> Dict[str, Any]:
        return await self._call("GET", profile_id, "dataset", {}, profile_group_id)

    async def create_dataset(
        self,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        return await self._call(
            "POST", profile_id, "create_dataset", {}, profile_group_id, idempotency_key
        )

    async def send_conversion_event(
        self,
        profile_id: str,
        *,
        event_name: str,
        event_id: str,
        chat_id: str | None = None,
        phone: str | None = None,
        dataset_id: str | None = None,
        event_time: int | str | None = None,
        email: str | None = None,
        external_id: str | None = None,
        currency: str | None = None,
        value: float | None = None,
        content_ids: List[str] | None = None,
        test_code: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """Report a conversion (e.g. Purchase, LeadSubmitted) back to Meta for a
        click-to-WhatsApp ad. Identify the person by `chat_id` or `phone`."""
        return await self._call(
            "POST",
            profile_id,
            "send_conversion_event",
            {
                "event_name": event_name,
                "event_id": event_id,
                "chat_id": chat_id,
                "phone": phone,
                "dataset_id": dataset_id,
                "event_time": event_time,
                "email": email,
                "external_id": external_id,
                "currency": currency,
                "value": value,
                "content_ids": content_ids,
                "test_code": test_code,
            },
            profile_group_id,
            idempotency_key,
        )

    # --- Media ---

    async def media(
        self,
        profile_id: str,
        phone_number_id: str,
        media_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> WhatsAppMedia:
        """Download an inbound media file (e.g. from a message attachment's
        `external_id`). Returns the raw bytes and their content type."""
        content, content_type = await self._client._request(
            "GET",
            f"/profiles/{profile_id}/whatsapp/media",
            params={"phone_number_id": phone_number_id, "media_id": media_id},
            profile_group_id=profile_group_id,
            raw=True,
        )
        return WhatsAppMedia(data=content, content_type=content_type)
