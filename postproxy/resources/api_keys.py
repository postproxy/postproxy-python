from __future__ import annotations

from typing import TYPE_CHECKING

from .._types import ApiKey, DeleteResponse, ListResponse

if TYPE_CHECKING:
    from .._client import PostProxy


class ApiKeysResource:
    """Manage profile-group-scoped API keys. Requires an account-wide key."""

    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(self) -> ListResponse[ApiKey]:
        data = await self._client._request("GET", "/api_keys")
        return ListResponse[ApiKey].model_validate(data)

    async def create(
        self,
        name: str,
        profile_group_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> ApiKey:
        """Create a key scoped to one profile group. The returned `token` is
        shown only once."""
        data = await self._client._request(
            "POST",
            "/api_keys",
            json={"name": name, "profile_group_id": profile_group_id},
            idempotency_key=idempotency_key,
        )
        return ApiKey.model_validate(data)

    async def delete(
        self, id: str, *, idempotency_key: str | None = None
    ) -> DeleteResponse:
        data = await self._client._request(
            "DELETE", f"/api_keys/{id}", idempotency_key=idempotency_key
        )
        return DeleteResponse.model_validate(data)
