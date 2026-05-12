from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._types import (
    ListResponse,
    Placement,
    Profile,
    ProfileStatsResponse,
    SuccessResponse,
)

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

    async def get_profile_stats(
        self,
        id: str,
        *,
        placement_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        profile_group_id: str | None = None,
    ) -> ProfileStatsResponse:
        """Fetch the profile stats timeseries.

        `placement_id` is required for facebook, linkedin, and telegram profiles.
        """
        params: dict[str, Any] = {}
        if placement_id is not None:
            params["placement_id"] = placement_id
        if from_ is not None:
            params["from"] = from_
        if to is not None:
            params["to"] = to

        data = await self._client._request(
            "GET",
            f"/profiles/{id}/stats",
            params=params or None,
            profile_group_id=profile_group_id,
        )
        return ProfileStatsResponse.model_validate(data)

    async def delete(
        self, id: str, *, profile_group_id: str | None = None
    ) -> SuccessResponse:
        data = await self._client._request(
            "DELETE",
            f"/profiles/{id}",
            profile_group_id=profile_group_id,
        )
        return SuccessResponse.model_validate(data)
