from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .._types import (
    Chat,
    PaginatedResponse,
)

if TYPE_CHECKING:
    from .._client import PostProxy


class ChatsResource:
    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(
        self,
        profile_id: str,
        *,
        page: int | None = None,
        per_page: int | None = None,
        before: datetime | str | None = None,
        after: datetime | str | None = None,
        profile_group_id: str | None = None,
    ) -> PaginatedResponse[Chat]:
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if before is not None:
            params["before"] = before.isoformat() if isinstance(before, datetime) else before
        if after is not None:
            params["after"] = after.isoformat() if isinstance(after, datetime) else after

        data = await self._client._request(
            "GET",
            f"/profiles/{profile_id}/chats",
            params=params,
            profile_group_id=profile_group_id,
        )
        return PaginatedResponse[Chat].model_validate(data)

    async def create(
        self,
        profile_id: str,
        participant_external_id: str,
        *,
        participant_username: str | None = None,
        participant_name: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Chat:
        json_body: dict[str, Any] = {"participant_external_id": participant_external_id}
        if participant_username is not None:
            json_body["participant_username"] = participant_username
        if participant_name is not None:
            json_body["participant_name"] = participant_name

        data = await self._client._request(
            "POST",
            f"/profiles/{profile_id}/chats",
            json=json_body,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return Chat.model_validate(data)

    async def get(self, chat_id: str, *, profile_group_id: str | None = None) -> Chat:
        data = await self._client._request(
            "GET",
            f"/chats/{chat_id}",
            profile_group_id=profile_group_id,
        )
        return Chat.model_validate(data)

    async def archive(
        self,
        chat_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Chat:
        data = await self._client._request(
            "POST",
            f"/chats/{chat_id}/archive",
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return Chat.model_validate(data)

    async def unarchive(
        self,
        chat_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Chat:
        data = await self._client._request(
            "DELETE",
            f"/chats/{chat_id}/archive",
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return Chat.model_validate(data)
