from __future__ import annotations

from typing import TYPE_CHECKING

from .._constants import Platform
from .._types import ConnectionResponse, DeleteResponse, ListResponse, ProfileGroup

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

    async def create(self, name: str) -> ProfileGroup:
        data = await self._client._request(
            "POST",
            "/profile_groups",
            json={"profile_group": {"name": name}},
        )
        return ProfileGroup.model_validate(data)

    async def delete(self, id: str) -> DeleteResponse:
        data = await self._client._request("DELETE", f"/profile_groups/{id}")
        return DeleteResponse.model_validate(data)

    async def initialize_connection(
        self, id: str, platform: Platform, redirect_url: str
    ) -> ConnectionResponse:
        data = await self._client._request(
            "POST",
            f"/profile_groups/{id}/initialize_connection",
            json={"platform": platform, "redirect_url": redirect_url},
        )
        return ConnectionResponse.model_validate(data)
