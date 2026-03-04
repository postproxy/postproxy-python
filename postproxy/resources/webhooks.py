from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from .._types import (
    DeleteResponse,
    ListResponse,
    PaginatedResponse,
    Webhook,
    WebhookDelivery,
)

if TYPE_CHECKING:
    from .._client import PostProxy


class WebhooksResource:
    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(self) -> ListResponse[Webhook]:
        data = await self._client._request("GET", "/webhooks")
        return ListResponse[Webhook].model_validate(data)

    async def get(self, id: str) -> Webhook:
        data = await self._client._request("GET", f"/webhooks/{id}")
        return Webhook.model_validate(data)

    async def create(
        self,
        url: str,
        events: List[str],
        *,
        description: str | None = None,
    ) -> Webhook:
        json_body: dict[str, Any] = {"url": url, "events": events}
        if description is not None:
            json_body["description"] = description

        data = await self._client._request("POST", "/webhooks", json=json_body)
        return Webhook.model_validate(data)

    async def update(
        self,
        id: str,
        *,
        url: str | None = None,
        events: List[str] | None = None,
        enabled: bool | None = None,
        description: str | None = None,
    ) -> Webhook:
        json_body: dict[str, Any] = {}
        if url is not None:
            json_body["url"] = url
        if events is not None:
            json_body["events"] = events
        if enabled is not None:
            json_body["enabled"] = enabled
        if description is not None:
            json_body["description"] = description

        data = await self._client._request(
            "PATCH", f"/webhooks/{id}", json=json_body
        )
        return Webhook.model_validate(data)

    async def delete(self, id: str) -> DeleteResponse:
        data = await self._client._request("DELETE", f"/webhooks/{id}")
        return DeleteResponse.model_validate(data)

    async def deliveries(
        self,
        id: str,
        *,
        page: int | None = None,
        per_page: int | None = None,
    ) -> PaginatedResponse[WebhookDelivery]:
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        data = await self._client._request(
            "GET", f"/webhooks/{id}/deliveries", params=params
        )
        return PaginatedResponse[WebhookDelivery].model_validate(data)
