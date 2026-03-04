from __future__ import annotations

import mimetypes
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, List

from .._types import (
    DeleteResponse,
    PaginatedResponse,
    PlatformParams,
    Post,
    StatsResponse,
    ThreadChildInput,
)
from .._constants import Platform, PostStatus

if TYPE_CHECKING:
    from .._client import PostProxy


class PostsResource:
    def __init__(self, client: PostProxy) -> None:
        self._client = client

    async def list(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        status: PostStatus | None = None,
        platforms: List[Platform] | None = None,
        scheduled_after: datetime | str | None = None,
        profile_group_id: str | None = None,
    ) -> PaginatedResponse[Post]:
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if status is not None:
            params["status"] = status
        if platforms is not None:
            params["platforms"] = platforms
        if scheduled_after is not None:
            params["scheduled_after"] = (
                scheduled_after.isoformat()
                if isinstance(scheduled_after, datetime)
                else scheduled_after
            )

        data = await self._client._request(
            "GET",
            "/posts",
            params=params,
            profile_group_id=profile_group_id,
        )
        return PaginatedResponse[Post].model_validate(data)

    async def get(self, id: str, *, profile_group_id: str | None = None) -> Post:
        data = await self._client._request(
            "GET",
            f"/posts/{id}",
            profile_group_id=profile_group_id,
        )
        return Post.model_validate(data)

    async def create(
        self,
        body: str,
        profiles: List[str],
        *,
        media: List[str] | None = None,
        media_files: List[str | Path] | None = None,
        platforms: PlatformParams | None = None,
        thread: List[ThreadChildInput] | None = None,
        scheduled_at: datetime | str | None = None,
        draft: bool | None = None,
        profile_group_id: str | None = None,
    ) -> Post:
        scheduled_at_str: str | None = None
        if scheduled_at is not None:
            scheduled_at_str = (
                scheduled_at.isoformat()
                if isinstance(scheduled_at, datetime)
                else scheduled_at
            )

        # Check if any thread children have local media files
        has_thread_files = thread is not None and any(
            t.media_files for t in thread
        )

        # When media_files are provided, use multipart form data
        if media_files is not None or has_thread_files:
            form_data: dict[str, Any] = {"post[body]": body}
            if scheduled_at_str is not None:
                form_data["post[scheduled_at]"] = scheduled_at_str
            if draft is not None:
                form_data["post[draft]"] = str(draft).lower()

            files: list[tuple[str, tuple[str | None, Any, str]]] = []
            for p in profiles:
                files.append(("profiles[]", (None, p, "text/plain")))
            if media is not None:
                for url in media:
                    files.append(("media[]", (None, url, "text/plain")))
            if platforms is not None:
                for platform, params in platforms.model_dump(exclude_none=True).items():
                    for key, value in params.items():
                        files.append(
                            (f"platforms[{platform}][{key}]", (None, str(value), "text/plain"))
                        )
            if media_files is not None:
                for file_path in media_files:
                    path = Path(file_path)
                    content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
                    files.append(("media[]", (path.name, open(path, "rb"), content_type)))

            if thread is not None:
                for i, t in enumerate(thread):
                    files.append((f"thread[{i}][body]", (None, t.body, "text/plain")))
                    if t.media is not None:
                        for url in t.media:
                            files.append((f"thread[{i}][media][]", (None, url, "text/plain")))
                    if t.media_files is not None:
                        for file_path in t.media_files:
                            path = Path(file_path)
                            content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
                            files.append((f"thread[{i}][media][]", (path.name, open(path, "rb"), content_type)))

            data = await self._client._request(
                "POST",
                "/posts",
                data=form_data,
                files=files,
                profile_group_id=profile_group_id,
            )
        else:
            # JSON request for URL-based media
            post_payload: dict[str, Any] = {"body": body}
            if scheduled_at_str is not None:
                post_payload["scheduled_at"] = scheduled_at_str
            if draft is not None:
                post_payload["draft"] = draft

            json_body: dict[str, Any] = {
                "post": post_payload,
                "profiles": profiles,
            }

            if platforms is not None:
                json_body["platforms"] = platforms.model_dump(exclude_none=True)
            if media is not None:
                json_body["media"] = media
            if thread is not None:
                json_body["thread"] = [
                    t.model_dump(exclude_none=True, exclude={"media_files"}) for t in thread
                ]

            data = await self._client._request(
                "POST",
                "/posts",
                json=json_body,
                profile_group_id=profile_group_id,
            )
        return Post.model_validate(data)

    async def publish_draft(
        self, id: str, *, profile_group_id: str | None = None
    ) -> Post:
        data = await self._client._request(
            "POST",
            f"/posts/{id}/publish",
            profile_group_id=profile_group_id,
        )
        return Post.model_validate(data)

    async def stats(
        self,
        post_ids: List[str],
        *,
        profiles: List[str] | None = None,
        from_date: datetime | str | None = None,
        to_date: datetime | str | None = None,
    ) -> StatsResponse:
        params: dict[str, Any] = {
            "post_ids": ",".join(post_ids),
        }
        if profiles is not None:
            params["profiles"] = ",".join(profiles)
        if from_date is not None:
            params["from"] = (
                from_date.isoformat()
                if isinstance(from_date, datetime)
                else from_date
            )
        if to_date is not None:
            params["to"] = (
                to_date.isoformat()
                if isinstance(to_date, datetime)
                else to_date
            )

        data = await self._client._request(
            "GET",
            "/posts/stats",
            params=params,
        )
        return StatsResponse.model_validate(data)

    async def delete(
        self, id: str, *, profile_group_id: str | None = None
    ) -> DeleteResponse:
        data = await self._client._request(
            "DELETE",
            f"/posts/{id}",
            profile_group_id=profile_group_id,
        )
        return DeleteResponse.model_validate(data)
