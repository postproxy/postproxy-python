from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from .._constants import (
    DailyStatsAttribution,
    InstagramAudioType,
    PostSyncStatus,
    PostSyncTrigger,
)
from .._types import (
    AssignedPlacement,
    ChatSync,
    DailyStatsResponse,
    FollowerHistoryResponse,
    IceBreaker,
    IceBreakersResponse,
    InstagramAvailableAudioResponse,
    ListResponse,
    PaginatedResponse,
    ParticipantStatus,
    Placement,
    PostSync,
    Profile,
    ProfileStatsResponse,
    ResolvedMention,
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

    async def daily_stats(
        self,
        id: str,
        *,
        placement_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        attribution: DailyStatsAttribution | None = None,
        profile_group_id: str | None = None,
    ) -> DailyStatsResponse:
        """Fetch the per-day stats series.

        `attribution="publish"` attributes post metrics to the day the post was
        published instead of the day they were received.
        """
        params: dict[str, Any] = {}
        if placement_id is not None:
            params["placement_id"] = placement_id
        if from_ is not None:
            params["from"] = from_
        if to is not None:
            params["to"] = to
        if attribution is not None:
            params["attribution"] = attribution

        data = await self._client._request(
            "GET",
            f"/profiles/{id}/daily_stats",
            params=params or None,
            profile_group_id=profile_group_id,
        )
        return DailyStatsResponse.model_validate(data)

    async def follower_history(
        self,
        id: str,
        *,
        placement_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        profile_group_id: str | None = None,
    ) -> FollowerHistoryResponse:
        params: dict[str, Any] = {}
        if placement_id is not None:
            params["placement_id"] = placement_id
        if from_ is not None:
            params["from"] = from_
        if to is not None:
            params["to"] = to

        data = await self._client._request(
            "GET",
            f"/profiles/{id}/follower_history",
            params=params or None,
            profile_group_id=profile_group_id,
        )
        return FollowerHistoryResponse.model_validate(data)

    async def participant_status(
        self,
        id: str,
        user_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> ParticipantStatus:
        """Instagram only: whether a DM participant is verified and follows you."""
        data = await self._client._request(
            "GET",
            f"/profiles/{id}/participants/{quote(user_id, safe='')}",
            profile_group_id=profile_group_id,
        )
        return ParticipantStatus.model_validate(data)

    async def resolve_mention(
        self,
        id: str,
        url: str,
        *,
        profile_group_id: str | None = None,
    ) -> ResolvedMention:
        """LinkedIn only: resolve a company page URL (or vanity name) to the URN
        used to @-mention it in a post."""
        data = await self._client._request(
            "GET",
            f"/profiles/{id}/resolve_mention",
            params={"url": url},
            profile_group_id=profile_group_id,
        )
        return ResolvedMention.model_validate(data)

    async def instagram_available_audio(
        self,
        id: str,
        *,
        audio_type: InstagramAudioType | None = None,
        search_query: str | None = None,
        profile_group_id: str | None = None,
    ) -> InstagramAvailableAudioResponse:
        """Music and original sounds a reel can attach via
        `InstagramParams.audio_id`. Profiles connected via Facebook login only."""
        params: dict[str, Any] = {}
        if audio_type is not None:
            params["audio_type"] = audio_type
        if search_query is not None:
            params["search_query"] = search_query

        data = await self._client._request(
            "GET",
            f"/profiles/{id}/instagram/available_audio",
            params=params or None,
            profile_group_id=profile_group_id,
        )
        return InstagramAvailableAudioResponse.model_validate(data)

    async def facebook_page(
        self,
        id: str,
        page_id: str,
        *,
        fields: str | None = None,
        profile_group_id: str | None = None,
    ) -> dict[str, Any]:
        """Read a Facebook Page's details. `page_id` is the placement id from
        :meth:`placements`."""
        params: dict[str, Any] = {"page_id": page_id}
        if fields is not None:
            params["fields"] = fields

        return await self._client._request(
            "GET",
            f"/profiles/{id}/facebook/page",
            params=params,
            profile_group_id=profile_group_id,
        )

    async def update_facebook_page(
        self,
        id: str,
        page_id: str,
        fields: dict[str, Any],
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Update the Page's about / contact fields, e.g. `about` (255
        characters or fewer), `description`, `website`, `phone`, `emails`."""
        return await self._client._request(
            "PATCH",
            f"/profiles/{id}/facebook/update_page",
            json={**fields, "page_id": page_id},
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )

    async def assign_to_group(
        self,
        id: str,
        target_profile_group_id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Profile:
        """Move the profile (with its placements) to another profile group."""
        data = await self._client._request(
            "PATCH",
            f"/profiles/{id}/assign_to_group",
            json={"target_profile_group_id": target_profile_group_id},
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return Profile.model_validate(data)

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

    async def backfill_chats(
        self,
        id: str,
        *,
        from_: str,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> ChatSync:
        """Import DM history back to `from_`.

        Like :meth:`backfill_posts`, runs in the background and only one runs
        per profile — poll :meth:`chat_sync` with the returned id.
        """
        data = await self._client._request(
            "POST",
            f"/profiles/{id}/backfill_chats",
            json={"from": from_},
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return ChatSync.model_validate(data)

    async def chat_syncs(
        self,
        id: str,
        *,
        trigger: PostSyncTrigger | None = None,
        status: PostSyncStatus | None = None,
        page: int | None = None,
        per_page: int | None = None,
        profile_group_id: str | None = None,
    ) -> PaginatedResponse[ChatSync]:
        """List chat sync runs, newest first."""
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
            f"/profiles/{id}/chat_syncs",
            params=params or None,
            profile_group_id=profile_group_id,
        )
        return PaginatedResponse[ChatSync].model_validate(data)

    async def chat_sync(
        self,
        id: str,
        chat_sync_id: str,
        *,
        profile_group_id: str | None = None,
    ) -> ChatSync:
        data = await self._client._request(
            "GET",
            f"/profiles/{id}/chat_syncs/{chat_sync_id}",
            profile_group_id=profile_group_id,
        )
        return ChatSync.model_validate(data)

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
