from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal
from urllib.parse import quote

from .._types import ListResponse, WhatsAppTemplate

if TYPE_CHECKING:
    from .._client import PostProxy


class WhatsAppTemplatesResource:
    """WhatsApp message templates, which live on the WhatsApp Business account
    (the profile).

    A template is addressed by its PostProxy id, Meta's id, or its name — pass
    `language` with a name that exists in several languages.
    """

    def __init__(self, client: PostProxy) -> None:
        self._client = client

    @staticmethod
    def _path(profile_id: str, id: str | None = None) -> str:
        base = f"/profiles/{profile_id}/templates"
        return base if id is None else f"{base}/{quote(id, safe='')}"

    async def list(
        self,
        profile_id: str,
        *,
        name: str | None = None,
        language: str | None = None,
        status: str | None = None,
        refresh: bool | None = None,
        profile_group_id: str | None = None,
    ) -> ListResponse[WhatsAppTemplate]:
        """List templates. `refresh=True` re-reads them from Meta first."""
        params: Dict[str, Any] = {}
        if name is not None:
            params["name"] = name
        if language is not None:
            params["language"] = language
        if status is not None:
            params["status"] = status
        if refresh is not None:
            params["refresh"] = str(refresh).lower()

        data = await self._client._request(
            "GET",
            self._path(profile_id),
            params=params or None,
            profile_group_id=profile_group_id,
        )
        return ListResponse[WhatsAppTemplate].model_validate(data)

    async def get(
        self,
        profile_id: str,
        id: str,
        *,
        language: str | None = None,
        profile_group_id: str | None = None,
    ) -> WhatsAppTemplate:
        data = await self._client._request(
            "GET",
            self._path(profile_id, id),
            params={"language": language} if language is not None else None,
            profile_group_id=profile_group_id,
        )
        return WhatsAppTemplate.model_validate(data)

    async def create(
        self,
        profile_id: str,
        *,
        name: str,
        category: str,
        language: str,
        parameter_format: Literal["POSITIONAL", "NAMED"] | None = None,
        components: List[Dict[str, Any]] | None = None,
        library_template_name: str | None = None,
        library_template_body_inputs: Dict[str, Any] | None = None,
        library_template_button_inputs: List[Dict[str, Any]] | None = None,
        message_send_ttl_seconds: int | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> WhatsAppTemplate:
        """Submit a template to Meta for review.

        `category` is MARKETING, UTILITY or AUTHENTICATION. `components` are
        Meta's component objects (HEADER, BODY, FOOTER, BUTTONS); pass
        `library_template_name` instead to create from Meta's template library.
        Follow `status` via :meth:`get` or the `message_template.status_updated`
        webhook.
        """
        json_body: Dict[str, Any] = {
            "name": name,
            "category": category,
            "language": language,
        }
        optional = {
            "parameter_format": parameter_format,
            "components": components,
            "library_template_name": library_template_name,
            "library_template_body_inputs": library_template_body_inputs,
            "library_template_button_inputs": library_template_button_inputs,
            "message_send_ttl_seconds": message_send_ttl_seconds,
        }
        json_body.update({k: v for k, v in optional.items() if v is not None})

        data = await self._client._request(
            "POST",
            self._path(profile_id),
            json=json_body,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return WhatsAppTemplate.model_validate(data)

    async def update(
        self,
        profile_id: str,
        id: str,
        *,
        components: List[Dict[str, Any]] | None = None,
        message_send_ttl_seconds: int | None = None,
        language: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> WhatsAppTemplate:
        json_body: Dict[str, Any] = {}
        if components is not None:
            json_body["components"] = components
        if message_send_ttl_seconds is not None:
            json_body["message_send_ttl_seconds"] = message_send_ttl_seconds

        data = await self._client._request(
            "PATCH",
            self._path(profile_id, id),
            params={"language": language} if language is not None else None,
            json=json_body,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )
        return WhatsAppTemplate.model_validate(data)

    async def delete(
        self,
        profile_id: str,
        id: str,
        *,
        language: str | None = None,
        profile_group_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        """Delete a template. By name without `language`, removes every language."""
        return await self._client._request(
            "DELETE",
            self._path(profile_id, id),
            params={"language": language} if language is not None else None,
            profile_group_id=profile_group_id,
            idempotency_key=idempotency_key,
        )

    async def library(
        self,
        profile_id: str,
        *,
        name: str | None = None,
        language: str | None = None,
        profile_group_id: str | None = None,
    ) -> Dict[str, Any]:
        """Browse Meta's ready-made template library."""
        params: Dict[str, Any] = {}
        if name is not None:
            params["name"] = name
        if language is not None:
            params["language"] = language

        return await self._client._request(
            "GET",
            f"{self._path(profile_id)}/library",
            params=params or None,
            profile_group_id=profile_group_id,
        )
