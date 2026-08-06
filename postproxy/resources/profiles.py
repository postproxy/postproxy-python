from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._constants import PostSyncStatus, PostSyncTrigger
from .._types import (
    AssignedPlacement,
    IceBreaker,
    IceBreakersResponse,
    ListResponse,
    PaginatedResponse,
    Placement,
    PostSync,
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

    async def assign_placement_to_group(
        self,
        id: str,
        *,
        placement_id: str,
        target_profile_group_id: str,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> AssignedPlacement:
        data = await self._client._request(
            "PATCH",
            f"/profiles/{id}/assign_placement_to_group",
            json={
                "placement_id": placement_id,
                "target_profile_group_id": target_profile_group_id,
            },
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return AssignedPlacement.model_validate(data)

    async def backfill_posts(
        self,
        id: str,
        *,
        from_: str,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> PostSync:
        """Import older posts from the platform.

        Walks the profile's feed backwards from the newest post until it reaches
        `from_` or the platform stops returning posts. Runs in the background —
        poll :meth:`post_sync` with the returned id for progress. Only one
        backfill runs per profile; starting a second raises
        :class:`ConflictError` carrying the running one's `profile_sync_id`.
        """
        data = await self._client._request(
            "POST",
            f"/profiles/{id}/backfill_posts",
            json={"from": from_},
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return PostSync.model_validate(data)

    async def post_syncs(
        self,
        id: str,
        *,
        trigger: PostSyncTrigger | None = None,
        status: PostSyncStatus | None = None,
        page: int | None = None,
        per_page: int | None = None,
        profile_group_id: str | None = None,
    ) -> PaginatedResponse[PostSync]:
        """List post sync runs, newest first. Runs are kept for 30 days."""
        params: dict[str, Any] = {}
        if trigger is not None:
            params["trigger"] = trigger
        if status is not None:
            params["status"] = status
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        data = await self._client._request(
            "GET",
            f"/profiles/{id}/post_syncs",
            params=params or None,
            profile_group_id=profile_group_id,
        )
        return PaginatedResponse[PostSync].model_validate(data)

    async def post_sync(
        self,
        id: str,
        post_sync_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> PostSync:
        """Fetch a single run.

        Poll this to follow a backfill to completion — the run is finished when
        `status` is `completed` or `failed`.
        """
        data = await self._client._request(
            "GET",
            f"/profiles/{id}/post_syncs/{post_sync_id}",
            profile_group_id=profile_group_id,
        )
        return PostSync.model_validate(data)

    async def ice_breakers(
        self, id: str, *, profile_group_id: str | None = None
    ) -> IceBreakersResponse:
        """List DM ice breakers. Supported for Instagram profiles only."""
        data = await self._client._request(
            "GET",
            f"/profiles/{id}/ice_breakers",
            profile_group_id=profile_group_id,
        )
        return IceBreakersResponse.model_validate(data)

    async def set_ice_breakers(
        self,
        id: str,
        ice_breakers: list[IceBreaker | dict[str, Any]],
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> SuccessResponse:
        items = [
            ib.model_dump() if isinstance(ib, IceBreaker) else ib
            for ib in ice_breakers
        ]
        data = await self._client._request(
            "POST",
            f"/profiles/{id}/ice_breakers",
            json={"ice_breakers": items},
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return SuccessResponse.model_validate(data)

    async def delete_ice_breakers(
        self,
        id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> SuccessResponse:
        data = await self._client._request(
            "DELETE",
            f"/profiles/{id}/ice_breakers",
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return SuccessResponse.model_validate(data)

    async def delete(
        self,
        id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> SuccessResponse:
        data = await self._client._request(
            "DELETE",
            f"/profiles/{id}",
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return SuccessResponse.model_validate(data)
