from __future__ import annotations

import mimetypes
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, List

from .._types import (
    DeleteOnPlatformResponse,
    DeleteResponse,
    MediaInput,
    PaginatedResponse,
    PlatformParams,
    Post,
    StatsResponse,
    ThreadChildInput,
)
from .._constants import Platform, PostStatus

if TYPE_CHECKING:
    from .._client import PostProxy


_Files = List[tuple[str, tuple[str | None, Any, str]]]


def _media_url(item: MediaInput) -> str:
    return item if isinstance(item, str) else item["url"]


def _is_local_cover_file(value: Any) -> bool:
    """`cover_file` is a local path unless it's a base64 data URL, which the
    API takes as a plain string."""
    return isinstance(value, str) and not value.startswith("data:")


def _has_local_cover_file(platforms: PlatformParams | None) -> bool:
    if platforms is None:
        return False
    return any(
        _is_local_cover_file(params.get("cover_file"))
        for params in platforms.model_dump(exclude_none=True).values()
        if isinstance(params, dict)
    )


def _file_part(file_path: str | Path) -> tuple[str, Any, str]:
    path = Path(file_path)
    content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return (path.name, open(path, "rb"), content_type)


def _append_platform_params(files: _Files, platforms: PlatformParams) -> None:
    """Platform params as flat form fields; a local `cover_file` is attached as a file."""
    for platform, params in platforms.model_dump(exclude_none=True).items():
        for key, value in params.items():
            field = f"platforms[{platform}][{key}]"
            if key == "cover_file" and _is_local_cover_file(value):
                files.append((field, _file_part(value)))
            elif isinstance(value, list):
                for item in value:
                    files.append((f"{field}[]", (None, str(item), "text/plain")))
            else:
                files.append((field, (None, str(value), "text/plain")))


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
        media: List[MediaInput] | None = None,
        media_files: List[str | Path] | None = None,
        platforms: PlatformParams | None = None,
        thread: List[ThreadChildInput] | None = None,
        scheduled_at: datetime | str | None = None,
        draft: bool | None = None,
        queue_id: str | None = None,
        queue_priority: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
        skip_duplicate_check: bool | None = None,
    ) -> Post:
        """Create a post.

        A local ``cover_file`` in ``platforms`` (Instagram, TikTok, YouTube,
        Pinterest) is uploaded with the post, switching the request to
        multipart even without ``media_files``. ``skip_duplicate_check=True``
        publishes even if an identical post was just submitted (skips the 409).
        """
        scheduled_at_str: str | None = None
        if scheduled_at is not None:
            scheduled_at_str = (
                scheduled_at.isoformat()
                if isinstance(scheduled_at, datetime)
                else scheduled_at
            )
        headers = {"X-Skip-Duplicate-Check": "true"} if skip_duplicate_check else None

        # Check if any thread children have local media files
        has_thread_files = thread is not None and any(
            t.media_files for t in thread
        )

        # When local files are provided, use multipart form data
        if media_files is not None or has_thread_files or _has_local_cover_file(platforms):
            form_data: dict[str, Any] = {"post[body]": body}
            if scheduled_at_str is not None:
                form_data["post[scheduled_at]"] = scheduled_at_str
            if draft is not None:
                form_data["post[draft]"] = str(draft).lower()
            if queue_id is not None:
                form_data["queue_id"] = queue_id
            if queue_priority is not None:
                form_data["queue_priority"] = queue_priority

            files: list[tuple[str, tuple[str | None, Any, str]]] = []
            for p in profiles:
                files.append(("profiles[]", (None, p, "text/plain")))
            if media is not None:
                for item in media:
                    files.append(("media[]", (None, _media_url(item), "text/plain")))
            if platforms is not None:
                _append_platform_params(files, platforms)
            if media_files is not None:
                for file_path in media_files:
                    files.append(("media[]", _file_part(file_path)))

            if thread is not None:
                for i, t in enumerate(thread):
                    files.append((f"thread[{i}][body]", (None, t.body, "text/plain")))
                    if t.media is not None:
                        for url in t.media:
                            files.append((f"thread[{i}][media][]", (None, url, "text/plain")))
                    if t.media_files is not None:
                        for file_path in t.media_files:
                            files.append((f"thread[{i}][media][]", _file_part(file_path)))

            data = await self._client._request(
                "POST",
                "/posts",
                data=form_data,
                files=files,
                profile_group_id=profile_group_id,
                idempotency_key=idempotency_key,
                headers=headers,
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
            if queue_id is not None:
                json_body["queue_id"] = queue_id
            if queue_priority is not None:
                json_body["queue_priority"] = queue_priority

            data = await self._client._request(
                "POST",
                "/posts",
                json=json_body,
                profile_group_id=profile_group_id,
                idempotency_key=idempotency_key,
                headers=headers,
            )
        return Post.model_validate(data)

    async def update(
        self,
        id: str,
        *,
        body: str | None = None,
        profiles: List[str] | None = None,
        media: List[MediaInput] | None = None,
        media_files: List[str | Path] | None = None,
        platforms: PlatformParams | None = None,
        thread: List[ThreadChildInput] | None = None,
        scheduled_at: datetime | str | None = None,
        draft: bool | None = None,
        queue_id: str | None = None,
        queue_priority: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Post:
        """Update a post.

        On a published post only ``body``, ``platforms.youtube.title``,
        ``platforms.pinterest.title`` and ``platforms.pinterest.destination_link``
        can change; the edit is pushed to the platforms in the background
        (``platform_post.edited`` / ``platform_post.edit_failed`` webhooks).
        A local ``cover_file`` is uploaded as on :meth:`create`.
        """
        scheduled_at_str: str | None = None
        if scheduled_at is not None:
            scheduled_at_str = (
                scheduled_at.isoformat()
                if isinstance(scheduled_at, datetime)
                else scheduled_at
            )

        has_thread_files = thread is not None and any(
            t.media_files for t in thread
        )

        if media_files is not None or has_thread_files or _has_local_cover_file(platforms):
            form_data: dict[str, Any] = {}
            if body is not None:
                form_data["post[body]"] = body
            if scheduled_at_str is not None:
                form_data["post[scheduled_at]"] = scheduled_at_str
            if draft is not None:
                form_data["post[draft]"] = str(draft).lower()
            if queue_id is not None:
                form_data["queue_id"] = queue_id
            if queue_priority is not None:
                form_data["queue_priority"] = queue_priority

            files: list[tuple[str, tuple[str | None, Any, str]]] = []
            if profiles is not None:
                for p in profiles:
                    files.append(("profiles[]", (None, p, "text/plain")))
            if media is not None:
                for item in media:
                    files.append(("media[]", (None, _media_url(item), "text/plain")))
            if platforms is not None:
                _append_platform_params(files, platforms)
            if media_files is not None:
                for file_path in media_files:
                    files.append(("media[]", _file_part(file_path)))

            if thread is not None:
                for i, t in enumerate(thread):
                    files.append((f"thread[{i}][body]", (None, t.body, "text/plain")))
                    if t.media is not None:
                        for url in t.media:
                            files.append((f"thread[{i}][media][]", (None, url, "text/plain")))
                    if t.media_files is not None:
                        for file_path in t.media_files:
                            files.append((f"thread[{i}][media][]", _file_part(file_path)))

            data = await self._client._request(
                "PATCH",
                f"/posts/{id}",
                data=form_data,
                files=files,
                profile_group_id=profile_group_id,
                idempotency_key=idempotency_key,
            )
        else:
            json_body: dict[str, Any] = {}

            post_payload: dict[str, Any] = {}
            if body is not None:
                post_payload["body"] = body
            if scheduled_at_str is not None:
                post_payload["scheduled_at"] = scheduled_at_str
            if draft is not None:
                post_payload["draft"] = draft
            if post_payload:
                json_body["post"] = post_payload

            if profiles is not None:
                json_body["profiles"] = profiles
            if platforms is not None:
                json_body["platforms"] = platforms.model_dump(exclude_none=True)
            if media is not None:
                json_body["media"] = media
            if thread is not None:
                json_body["thread"] = [
                    t.model_dump(exclude_none=True, exclude={"media_files"}) for t in thread
                ]
            if queue_id is not None:
                json_body["queue_id"] = queue_id
            if queue_priority is not None:
                json_body["queue_priority"] = queue_priority

            data = await self._client._request(
                "PATCH",
                f"/posts/{id}",
                json=json_body,
                profile_group_id=profile_group_id,
                idempotency_key=idempotency_key,
            )
        return Post.model_validate(data)

    async def publish_draft(
        self,
        id: str,
        *,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Post:
        data = await self._client._request(
            "POST",
            f"/posts/{id}/publish",
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
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
        self,
        id: str,
        *,
        delete_on_platform: bool | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> DeleteResponse:
        params: dict[str, Any] = {}
        if delete_on_platform is not None:
            params["delete_on_platform"] = str(delete_on_platform).lower()
        data = await self._client._request(
            "DELETE",
            f"/posts/{id}",
            params=params or None,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return DeleteResponse.model_validate(data)

    async def delete_on_platform(
        self,
        id: str,
        *,
        post_profile_id: str | None = None,
        profile_id: str | None = None,
        network: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> DeleteOnPlatformResponse:
        json_body: dict[str, Any] = {}
        if post_profile_id is not None:
            json_body["post_profile_id"] = post_profile_id
        if profile_id is not None:
            json_body["profile_id"] = profile_id
        if network is not None:
            json_body["network"] = network
        data = await self._client._request(
            "POST",
            f"/posts/{id}/delete_on_platform",
            json=json_body or None,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return DeleteOnPlatformResponse.model_validate(data)
