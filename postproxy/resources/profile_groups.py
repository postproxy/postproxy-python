from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._constants import Platform
from .._types import (
    BlueskyConnectionResponse,
    DeleteResponse,
    ListResponse,
    OAuthConnectionResponse,
    ProfileGroup,
    TelegramConnectionResponse,
)

if TYPE_CHECKING:
    from .._client import PostProxy


class ProfileGroupsResource:
    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(self) -> ListResponse[ProfileGroup]:
        data = await self._client._request("GET", "/profile_groups")
        return ListResponse[ProfileGroup].model_validate(data)

    async def get(self, id: str) -> ProfileGroup:
        data = await self._client._request("GET", f"/profile_groups/{id}")
        return ProfileGroup.model_validate(data)

    async def create(
        self, name: str, *, idempotency_key: str | None = None
    ) -> ProfileGroup:
        data = await self._client._request(
            "POST",
            "/profile_groups",
            json={"profile_group": {"name": name}},
            idempotency_key=idempotency_key,
        )
        return ProfileGroup.model_validate(data)

    async def delete(
        self, id: str, *, idempotency_key: str | None = None
    ) -> DeleteResponse:
        data = await self._client._request(
            "DELETE", f"/profile_groups/{id}", idempotency_key=idempotency_key
        )
        return DeleteResponse.model_validate(data)

    async def initialize_connection(
        self,
        id: str,
        platform: Platform,
        redirect_url: str | None = None,
    ) -> OAuthConnectionResponse:
        """Start an OAuth connection (returns a {url, success} response).

        BlueSky and Telegram do not use OAuth — use `connect_bluesky` and
        `connect_telegram` instead.
        """
        body: dict[str, Any] = {"platform": platform}
        if redirect_url is not None:
            body["redirect_url"] = redirect_url
        data = await self._client._request(
            "POST",
            f"/profile_groups/{id}/initialize_connection",
            json=body,
        )
        return OAuthConnectionResponse.model_validate(data)

    async def connect_bluesky(
        self,
        id: str,
        *,
        identifier: str,
        app_password: str,
    ) -> BlueskyConnectionResponse:
        data = await self._client._request(
            "POST",
            f"/profile_groups/{id}/initialize_connection",
            json={
                "platform": "bluesky",
                "identifier": identifier,
                "app_password": app_password,
            },
        )
        return BlueskyConnectionResponse.model_validate(data)

    async def connect_telegram(
        self,
        id: str,
        *,
        bot_token: str,
    ) -> TelegramConnectionResponse:
        """Submit a Telegram bot token.

        Channels populate asynchronously — after this call returns, poll
        `profiles.placements(profile.id)` until non-empty.
        """
        data = await self._client._request(
            "POST",
            f"/profile_groups/{id}/initialize_connection",
            json={"platform": "telegram", "bot_token": bot_token},
        )
        return TelegramConnectionResponse.model_validate(data)
