from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from .._types import (
    DeleteResponse,
    ListResponse,
    NextSlotResponse,
    Queue,
)

if TYPE_CHECKING:
    from .._client import PostProxy


class QueuesResource:
    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(
        self, *, profile_group_id: str | None = None
    ) -> ListResponse[Queue]:
        data = await self._client._request(
            "GET", "/post_queues", profile_group_id=profile_group_id
        )
        return ListResponse[Queue].model_validate(data)

    async def get(self, id: str) -> Queue:
        data = await self._client._request("GET", f"/post_queues/{id}")
        return Queue.model_validate(data)

    async def next_slot(self, id: str) -> NextSlotResponse:
        data = await self._client._request("GET", f"/post_queues/{id}/next_slot")
        return NextSlotResponse.model_validate(data)

    async def create(
        self,
        name: str,
        profile_group_id: str,
        *,
        description: str | None = None,
        timezone: str | None = None,
        jitter: int | None = None,
        timeslots: List[dict[str, Any]] | None = None,
        idempotency_key: str | None = None,
    ) -> Queue:
        post_queue: dict[str, Any] = {"name": name}
        if description is not None:
            post_queue["description"] = description
        if timezone is not None:
            post_queue["timezone"] = timezone
        if jitter is not None:
            post_queue["jitter"] = jitter
        if timeslots is not None:
            post_queue["queue_timeslots_attributes"] = timeslots

        json_body: dict[str, Any] = {
            "profile_group_id": profile_group_id,
            "post_queue": post_queue,
        }

        data = await self._client._request(
            "POST", "/post_queues", json=json_body, idempotency_key=idempotency_key
        )
        return Queue.model_validate(data)

    async def update(
        self,
        id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        timezone: str | None = None,
        enabled: bool | None = None,
        jitter: int | None = None,
        timeslots: List[dict[str, Any]] | None = None,
        idempotency_key: str | None = None,
    ) -> Queue:
        post_queue: dict[str, Any] = {}
        if name is not None:
            post_queue["name"] = name
        if description is not None:
            post_queue["description"] = description
        if timezone is not None:
            post_queue["timezone"] = timezone
        if enabled is not None:
            post_queue["enabled"] = enabled
        if jitter is not None:
            post_queue["jitter"] = jitter
        if timeslots is not None:
            post_queue["queue_timeslots_attributes"] = timeslots

        json_body: dict[str, Any] = {"post_queue": post_queue}

        data = await self._client._request(
            "PATCH", f"/post_queues/{id}", json=json_body, idempotency_key=idempotency_key
        )
        return Queue.model_validate(data)

    async def delete(
        self, id: str, *, idempotency_key: str | None = None
    ) -> DeleteResponse:
        data = await self._client._request(
            "DELETE", f"/post_queues/{id}", idempotency_key=idempotency_key
        )
        return DeleteResponse.model_validate(data)
