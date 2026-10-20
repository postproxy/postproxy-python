from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._types import AccountPlacement, PaginatedResponse

if TYPE_CHECKING:
    from .._client import PostProxy


class PlacementsResource:
    """Account-level placements. Account-wide API keys only — placements span
    profile groups."""

    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
    ) -> PaginatedResponse[AccountPlacement]:
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        data = await self._client._request(
            "GET",
            "/placements",
            params=params or None,
        )
        return PaginatedResponse[AccountPlacement].model_validate(data)

    async def set_active_profile(
        self,
        id: str,
        profile_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> AccountPlacement:
        """Choose which connected profile PostProxy posts and reads through when
        the same placement is reachable through several."""
        data = await self._client._request(
            "PATCH",
            f"/placements/{id}/set_active_profile",
            json={"profile_id": profile_id},
            idempotency_key=idempotency_key,
        )
        return AccountPlacement.model_validate(data)
