from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

from .._types import (
    AcceptedResponse,
    BulkComment,
    Comment,
    Message,
    MessageButton,
    MessageCard,
    MessageElement,
    PaginatedResponse,
    QuickReply,
)
from .messages import _dump

if TYPE_CHECKING:
    from .._client import PostProxy


class CommentsResource:
    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(
        self,
        post_id: str,
        profile_id: str,
        *,
        page: int | None = None,
        per_page: int | None = None,
        from_: str | None = None,
        to: str | None = None,
        profile_group_id: str | None = None,
    ) -> PaginatedResponse[Comment]:
        """List a post's comments.

        `from_` and `to` filter on when PostProxy received the comment
        (`created_at`), not the platform's `posted_at`. They apply to top-level
        comments — one in range brings its full `replies` list with it.
        """
        params: dict[str, Any] = {"profile_id": profile_id}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if from_ is not None:
            params["from"] = from_
        if to is not None:
            params["to"] = to

        data = await self._client._request(
            "GET",
            f"/posts/{post_id}/comments",
            params=params,
            profile_group_id=profile_group_id,
        )
        return PaginatedResponse[Comment].model_validate(data)

    async def list_all(
        self,
        *,
        post_ids: list[str] | None = None,
        profiles: list[str] | None = None,
        placement_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        page: int | None = None,
        per_page: int | None = None,
        profile_group_id: str | None = None,
    ) -> PaginatedResponse[BulkComment]:
        """List comments across every post in the profile group.

        Flat: replies come back as their own entries linked by
        `parent_external_id`, so `total` counts every comment. `profiles` takes
        profile IDs or network names, mixed. `placement_id` narrows to one
        page / organization.
        """
        params: dict[str, Any] = {}
        if post_ids is not None:
            params["post_ids"] = ",".join(post_ids)
        if profiles is not None:
            params["profiles"] = ",".join(profiles)
        if placement_id is not None:
            params["placement_id"] = placement_id
        if from_ is not None:
            params["from"] = from_
        if to is not None:
            params["to"] = to
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        data = await self._client._request(
            "GET",
            "/comments",
            params=params or None,
            profile_group_id=profile_group_id,
        )
        return PaginatedResponse[BulkComment].model_validate(data)

    async def get(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> Comment:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "GET",
            f"/posts/{post_id}/comments/{comment_id}",
            params=params,
            profile_group_id=profile_group_id,
        )
        return Comment.model_validate(data)

    async def create(
        self,
        post_id: str,
        profile_id: str,
        text: str,
        *,
        parent_id: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Comment:
        params: dict[str, Any] = {"profile_id": profile_id}
        json_body: dict[str, Any] = {"text": text}
        if parent_id is not None:
            json_body["parent_id"] = parent_id

        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments",
            params=params,
            json=json_body,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return Comment.model_validate(data)

    async def edit(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        text: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> AcceptedResponse:
        """Edit a comment you published. Facebook and YouTube only.

        Runs in the background — the outcome arrives as the `comment.edited` /
        `comment.edit_failed` webhook.
        """
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "PATCH",
            f"/posts/{post_id}/comments/{comment_id}",
            params=params,
            json={"body": text},
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return AcceptedResponse.model_validate(data)

    async def delete(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> AcceptedResponse:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "DELETE",
            f"/posts/{post_id}/comments/{comment_id}",
            params=params,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return AcceptedResponse.model_validate(data)

    async def hide(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> AcceptedResponse:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/hide",
            params=params,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return AcceptedResponse.model_validate(data)

    async def unhide(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> AcceptedResponse:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/unhide",
            params=params,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return AcceptedResponse.model_validate(data)

    async def like(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> AcceptedResponse:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/like",
            params=params,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return AcceptedResponse.model_validate(data)

    async def unlike(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> AcceptedResponse:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/unlike",
            params=params,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return AcceptedResponse.model_validate(data)

    async def pin(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> AcceptedResponse:
        """Pin a comment. TikTok only."""
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/pin",
            params=params,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return AcceptedResponse.model_validate(data)

    async def unpin(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> AcceptedResponse:
        """Unpin a comment. TikTok only."""
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/unpin",
            params=params,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return AcceptedResponse.model_validate(data)

    async def private_reply(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        text: str,
        *,
        quick_replies: Sequence[QuickReply | dict[str, Any]] | None = None,
        buttons: Sequence[MessageButton | dict[str, Any]] | None = None,
        card: MessageCard | dict[str, Any] | None = None,
        elements: Sequence[MessageElement | dict[str, Any]] | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Message:
        """Send a direct message in reply to a comment's author (Instagram/Facebook).

        Returns a Message (not a Comment). One private reply per comment, within
        7 days of it. `quick_replies`, `buttons`, `card` and `elements` work as
        in `messages.send()`; `text` may be empty when sending `elements`.
        """
        params: dict[str, Any] = {"profile_id": profile_id}
        json_body: dict[str, Any] = {"text": text}
        if quick_replies is not None:
            json_body["quick_replies"] = [_dump(qr) for qr in quick_replies]
        if buttons is not None:
            json_body["buttons"] = [_dump(b) for b in buttons]
        if card is not None:
            json_body["card"] = _dump(card)
        if elements is not None:
            json_body["elements"] = [_dump(e) for e in elements]
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/private_reply",
            params=params,
            json=json_body,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return Message.model_validate(data)
