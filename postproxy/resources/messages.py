from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Sequence

from pydantic import BaseModel

from .._types import (
    Message,
    MessageButton,
    MessageCard,
    MessageElement,
    MessageLocation,
    MessageTemplateInput,
    PaginatedResponse,
    QuickReply,
)
from .._constants import MessageDirection, MessageStatus

if TYPE_CHECKING:
    from .._client import PostProxy


def _dump(value: Any) -> Any:
    """Accept either a pydantic model or a plain dict for interactive params.

    Models would otherwise reach httpx unserializable. Unset fields are dropped
    so an omitted `content_type` stays omitted rather than being sent as null.
    """
    if isinstance(value, BaseModel):
        return value.model_dump(exclude_none=True)
    return value


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
        quick_replies: Sequence[QuickReply | dict[str, Any]] | None = None,
        buttons: Sequence[MessageButton | dict[str, Any]] | None = None,
        card: MessageCard | dict[str, Any] | None = None,
        elements: Sequence[MessageElement | dict[str, Any]] | None = None,
        template: MessageTemplateInput | dict[str, Any] | None = None,
        interactive: dict[str, Any] | None = None,
        location: MessageLocation | dict[str, Any] | None = None,
        contacts: List[dict[str, Any]] | None = None,
        category: str | None = None,
        link_preview: bool | None = None,
        voice_note: bool | None = None,
        filename: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Message:
        """Send a message to a chat.

        `quick_replies`, `buttons`, and `card` are Facebook and Instagram only —
        they return 422 on Telegram and Bluesky, where `reply_markup` is the
        equivalent. They are sent on the JSON path only, so pass `media` as
        hosted URLs rather than `media_files` when combining with an attachment.

        `elements` is a carousel of up to 10 cards (Facebook and Instagram) and
        can't be combined with `body`, `buttons` or `card`.

        WhatsApp: send exactly one of `body`, `media`, `template`,
        `interactive`, `location` or `contacts`; outside the 24-hour window
        only a `template` gets through. `category="utility"` sends a text
        message under the utility category, `voice_note` delivers an audio
        attachment as a voice note, and `filename` names a document attachment.
        """
        # When media_files are provided, use multipart form data (mirrors PostsResource).
        if media_files is not None:
            form_data: dict[str, Any] = {}
            if body is not None:
                form_data["body"] = body
            if tag is not None:
                form_data["tag"] = tag
            if reply_to_external_id is not None:
                form_data["reply_to_external_id"] = reply_to_external_id
            if voice_note is not None:
                form_data["voice_note"] = str(voice_note).lower()
            if filename is not None:
                form_data["filename"] = filename

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
                idempotency_key=idempotency_key,
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
            if quick_replies is not None:
                json_body["quick_replies"] = [_dump(qr) for qr in quick_replies]
            if buttons is not None:
                json_body["buttons"] = [_dump(b) for b in buttons]
            if card is not None:
                json_body["card"] = _dump(card)
            if elements is not None:
                json_body["elements"] = [_dump(e) for e in elements]
            if template is not None:
                json_body["template"] = _dump(template)
            if interactive is not None:
                json_body["interactive"] = interactive
            if location is not None:
                json_body["location"] = _dump(location)
            if contacts is not None:
                json_body["contacts"] = contacts
            if category is not None:
                json_body["category"] = category
            if link_preview is not None:
                json_body["link_preview"] = link_preview
            if voice_note is not None:
                json_body["voice_note"] = voice_note
            if filename is not None:
                json_body["filename"] = filename

            data = await self._client._request(
                "POST",
                f"/chats/{chat_id}/messages",
                json=json_body,
                profile_group_id=profile_group_id,
                idempotency_key=idempotency_key,
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
        idempotency_key: str | None = None,
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
            idempotency_key=idempotency_key,
        )
        return Message.model_validate(data)

    async def react(
        self,
        message_id: str,
        *,
        reaction: str | None = None,
        emoji: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
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
            idempotency_key=idempotency_key,
        )
        return Message.model_validate(data)

    async def unreact(
        self,
        message_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Message:
        data = await self._client._request(
            "DELETE",
            f"/messages/{message_id}/unreact",
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return Message.model_validate(data)
