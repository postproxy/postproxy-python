from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING, Any, List

from .._types import (
    Message,
    PaginatedResponse,
)
from .._constants import MessageDirection, MessageStatus

if TYPE_CHECKING:
    from .._client import PostProxy


class MessagesResource:
    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(
        self,
        chat_id: str,
        *,
        page: int | None = None,
        per_page: int | None = None,
        direction: MessageDirection | None = None,
        status: MessageStatus | None = None,
        profile_group_id: str | None = None,
    ) -> PaginatedResponse[Message]:
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if direction is not None:
            params["direction"] = direction
        if status is not None:
            params["status"] = status

        data = await self._client._request(
            "GET",
            f"/chats/{chat_id}/messages",
            params=params,
            profile_group_id=profile_group_id,
        )
        return PaginatedResponse[Message].model_validate(data)

    async def send(
        self,
        chat_id: str,
        *,
        body: str | None = None,
        media: List[str] | None = None,
        media_files: List[str | Path] | None = None,
        tag: str | None = None,
        reply_to_external_id: str | None = None,
        reply_markup: dict[str, Any] | None = None,
        profile_group_id: str | None = None,
    ) -> Message:
        # When media_files are provided, use multipart form data (mirrors PostsResource).
        if media_files is not None:
            form_data: dict[str, Any] = {}
            if body is not None:
                form_data["body"] = body
            if tag is not None:
                form_data["tag"] = tag
            if reply_to_external_id is not None:
                form_data["reply_to_external_id"] = reply_to_external_id

            files: list[tuple[str, tuple[str | None, Any, str]]] = []
            if media is not None:
                for url in media:
                    files.append(("media[]", (None, url, "text/plain")))
            for file_path in media_files:
                path = Path(file_path)
                content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
                files.append(("media[]", (path.name, open(path, "rb"), content_type)))

            data = await self._client._request(
                "POST",
                f"/chats/{chat_id}/messages",
                data=form_data,
                files=files,
                profile_group_id=profile_group_id,
            )
        else:
            json_body: dict[str, Any] = {}
            if body is not None:
                json_body["body"] = body
            if media is not None:
                json_body["media"] = media
            if tag is not None:
                json_body["tag"] = tag
            if reply_to_external_id is not None:
                json_body["reply_to_external_id"] = reply_to_external_id
            if reply_markup is not None:
                json_body["reply_markup"] = reply_markup

            data = await self._client._request(
                "POST",
                f"/chats/{chat_id}/messages",
                json=json_body,
                profile_group_id=profile_group_id,
            )
        return Message.model_validate(data)

    async def get(self, message_id: str, *, profile_group_id: str | None = None) -> Message:
        data = await self._client._request(
            "GET",
            f"/messages/{message_id}",
            profile_group_id=profile_group_id,
        )
        return Message.model_validate(data)

    async def edit(
        self,
        message_id: str,
        *,
        body: str | None = None,
        reply_markup: dict[str, Any] | None = None,
        profile_group_id: str | None = None,
    ) -> Message:
        json_body: dict[str, Any] = {}
        if body is not None:
            json_body["body"] = body
        if reply_markup is not None:
            json_body["reply_markup"] = reply_markup

        data = await self._client._request(
            "PATCH",
            f"/messages/{message_id}",
            json=json_body,
            profile_group_id=profile_group_id,
        )
        return Message.model_validate(data)

    async def react(
        self,
        message_id: str,
        *,
        reaction: str | None = None,
        emoji: str | None = None,
        profile_group_id: str | None = None,
    ) -> Message:
        json_body: dict[str, Any] = {}
        if reaction is not None:
            json_body["reaction"] = reaction
        if emoji is not None:
            json_body["emoji"] = emoji

        data = await self._client._request(
            "POST",
            f"/messages/{message_id}/react",
            json=json_body or None,
            profile_group_id=profile_group_id,
        )
        return Message.model_validate(data)

    async def unreact(self, message_id: str, *, profile_group_id: str | None = None) -> Message:
        data = await self._client._request(
            "DELETE",
            f"/messages/{message_id}/unreact",
            profile_group_id=profile_group_id,
        )
        return Message.model_validate(data)
