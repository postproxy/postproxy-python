from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._types import (
    AcceptedResponse,
    Comment,
    Message,
    PaginatedResponse,
)

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
        profile_group_id: str | None = None,
    ) -> PaginatedResponse[Comment]:
        params: dict[str, Any] = {"profile_id": profile_id}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        data = await self._client._request(
            "GET",
            f"/posts/{post_id}/comments",
            params=params,
            profile_group_id=profile_group_id,
        )
        return PaginatedResponse[Comment].model_validate(data)

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
        )
        return Comment.model_validate(data)

    async def delete(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> AcceptedResponse:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "DELETE",
            f"/posts/{post_id}/comments/{comment_id}",
            params=params,
            profile_group_id=profile_group_id,
        )
        return AcceptedResponse.model_validate(data)

    async def hide(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> AcceptedResponse:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/hide",
            params=params,
            profile_group_id=profile_group_id,
        )
        return AcceptedResponse.model_validate(data)

    async def unhide(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> AcceptedResponse:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/unhide",
            params=params,
            profile_group_id=profile_group_id,
        )
        return AcceptedResponse.model_validate(data)

    async def like(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> AcceptedResponse:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/like",
            params=params,
            profile_group_id=profile_group_id,
        )
        return AcceptedResponse.model_validate(data)

    async def unlike(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> AcceptedResponse:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/unlike",
            params=params,
            profile_group_id=profile_group_id,
        )
        return AcceptedResponse.model_validate(data)

    async def private_reply(
        self,
        post_id: str,
        comment_id: str,
        profile_id: str,
        text: str,
        *,
        profile_group_id: str | None = None,
    ) -> Message:
        params: dict[str, Any] = {"profile_id": profile_id}
        data = await self._client._request(
            "POST",
            f"/posts/{post_id}/comments/{comment_id}/private_reply",
            params=params,
            json={"text": text},
            profile_group_id=profile_group_id,
        )
        return Message.model_validate(data)
