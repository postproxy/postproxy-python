from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._types import (
    AcceptedResponse,
    PaginatedResponse,
    ProfileComment,
)

if TYPE_CHECKING:
    from .._client import PostProxy


class ProfileCommentsResource:
    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(
        self,
        profile_id: str,
        *,
        placement_id: str | None = None,
        page: int | None = None,
        per_page: int | None = None,
        profile_group_id: str | None = None,
    ) -> PaginatedResponse[ProfileComment]:
        params: dict[str, Any] = {}
        if placement_id is not None:
            params["placement_id"] = placement_id
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        data = await self._client._request(
            "GET",
            f"/profiles/{profile_id}/comments",
            params=params,
            profile_group_id=profile_group_id,
        )
        return PaginatedResponse[ProfileComment].model_validate(data)

    async def get(
        self,
        profile_id: str,
        comment_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> ProfileComment:
        data = await self._client._request(
            "GET",
            f"/profiles/{profile_id}/comments/{comment_id}",
            profile_group_id=profile_group_id,
        )
        return ProfileComment.model_validate(data)

    async def create(
        self,
        profile_id: str,
        parent_id: str,
        text: str,
        *,
        profile_group_id: str | None = None,
    ) -> ProfileComment:
        data = await self._client._request(
            "POST",
            f"/profiles/{profile_id}/comments",
            json={"parent_id": parent_id, "text": text},
            profile_group_id=profile_group_id,
        )
        return ProfileComment.model_validate(data)

    async def delete(
        self,
        profile_id: str,
        comment_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> AcceptedResponse:
        data = await self._client._request(
            "DELETE",
            f"/profiles/{profile_id}/comments/{comment_id}",
            profile_group_id=profile_group_id,
        )
        return AcceptedResponse.model_validate(data)
