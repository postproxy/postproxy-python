from __future__ import annotations

from typing import TYPE_CHECKING, List

from .._types import ListResponse, Placement, Profile, SuccessResponse

if TYPE_CHECKING:
    from .._client import PostProxy


class ProfilesResource:
    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(
        self, *, profile_group_id: str | None = None
    ) -> ListResponse[Profile]:
        data = await self._client._request(
            "GET",
            "/profiles",
            profile_group_id=profile_group_id,
        )
        return ListResponse[Profile].model_validate(data)

    async def get(self, id: str, *, profile_group_id: str | None = None) -> Profile:
        data = await self._client._request(
            "GET",
            f"/profiles/{id}",
            profile_group_id=profile_group_id,
        )
        return Profile.model_validate(data)

    async def placements(
        self, id: str, *, profile_group_id: str | None = None
    ) -> ListResponse[Placement]:
        data = await self._client._request(
            "GET",
            f"/profiles/{id}/placements",
            profile_group_id=profile_group_id,
        )
        return ListResponse[Placement].model_validate(data)

    async def delete(
        self, id: str, *, profile_group_id: str | None = None
    ) -> SuccessResponse:
        data = await self._client._request(
            "DELETE",
            f"/profiles/{id}",
            profile_group_id=profile_group_id,
        )
        return SuccessResponse.model_validate(data)
