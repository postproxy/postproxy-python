from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel

from ._constants import (
    BlueskyFormat,
    FacebookFormat,
    InstagramFormat,
    LinkedInFormat,
    MediaStatus,
    MessageDirection,
    MessageStatus,
    PinterestFormat,
    Platform,
    PlatformPostStatus,
    PostStatus,
    ProfileStatus,
    TelegramFormat,
    TelegramParseMode,
    ThreadsFormat,
    TikTokFormat,
    TikTokPrivacy,
    TwitterFormat,
    WebhookEventType,
    YouTubeFormat,
    YouTubePrivacy,
)

T = TypeVar("T")


# --- Response models ---


class Profile(BaseModel):
    id: str
    name: str
    status: ProfileStatus
    platform: Platform
    profile_group_id: str
    expires_at: datetime | None = None
    post_count: int


class Placement(BaseModel):
    id: str
    name: str


class ProfileGroup(BaseModel):
    id: str
    name: str
    profiles_count: int


class Insights(BaseModel):
    impressions: int | None = None
    on: datetime | None = None


class ErrorDetails(BaseModel):
    platform_error_code: str | None = None
    platform_error_subcode: str | None = None
    platform_error_message: str | None = None
    postproxy_note: str | None = None


class PlatformResult(BaseModel):
    platform: Platform
    status: PlatformPostStatus
    params: dict | None = None
    error: str | None = None
    error_details: ErrorDetails | None = None
    attempted_at: datetime | None = None
    insights: Insights | None = None


class MediaPlatformError(BaseModel):
    platform: Platform
    status: PlatformPostStatus
    error: str | None = None
    error_details: ErrorDetails | None = None


class Media(BaseModel):
    id: str
    status: MediaStatus
    error_message: str | None = None
    content_type: str
    source_url: str | None = None
    url: str | None = None
    platforms: list[MediaPlatformError] | None = None


class ThreadChild(BaseModel):
    id: str
    body: str
    media: list[Media] = []


class Post(BaseModel):
    id: str
    body: str
    status: PostStatus
    scheduled_at: datetime | None = None
    created_at: datetime
    media: list[Media] = []
    platforms: list[PlatformResult] = []
    thread: list[ThreadChild] = []
    queue_id: str | None = None
    queue_priority: str | None = None


class Webhook(BaseModel):
    id: str
    url: str
    events: list[str]
    enabled: bool
    description: str | None = None
    secret: str | None = None
    created_at: datetime
    updated_at: datetime


class WebhookDelivery(BaseModel):
    id: str
    event_id: str
    event_type: str
    response_status: int | None = None
    attempt_number: int
    success: bool
    attempted_at: datetime
    created_at: datetime


class ListResponse(BaseModel, Generic[T]):
    data: list[T]


class PaginatedResponse(ListResponse[T]):
    total: int
    page: int
    per_page: int


class DeleteResponse(BaseModel):
    deleted: bool


class DeletingPlatform(BaseModel):
    post_profile_id: str
    platform: Platform


class DeleteOnPlatformResponse(BaseModel):
    success: bool
    deleting: list[DeletingPlatform] = []


class SuccessResponse(BaseModel):
    success: bool


class AcceptedResponse(BaseModel):
    accepted: bool


class ProfileComment(BaseModel):
    id: str
    external_id: str
    parent_external_id: str | None = None
    placement_id: str
    body: str
    status: str
    author_username: str | None = None
    author_avatar_url: str | None = None
    platform_data: dict | None = None
    posted_at: datetime
    created_at: datetime
    replies: list[ProfileComment] = []


class Attachment(BaseModel):
    id: str
    type: str
    url: str | None = None
    status: MediaStatus
    external_id: str | None = None


class Comment(BaseModel):
    id: str
    external_id: str | None = None
    body: str
    status: str
    author_username: str | None = None
    author_avatar_url: str | None = None
    author_external_id: str | None = None
    metadata: dict | None = None
    parent_external_id: str | None = None
    like_count: int = 0
    is_hidden: bool = False
    permalink: str | None = None
    platform_data: dict | None = None
    attachments: list[Attachment] = []
    posted_at: datetime | None = None
    created_at: datetime
    replies: list[Comment] = []


class Reaction(BaseModel):
    sender_external_id: str
    emoji: str | None = None
    reaction: str | None = None
    at: datetime | None = None


class Chat(BaseModel):
    id: str
    profile_id: str
    platform: Platform
    participant_external_id: str
    participant_username: str | None = None
    participant_name: str | None = None
    participant_avatar_url: str | None = None
    external_conversation_id: str | None = None
    last_inbound_at: datetime | None = None
    last_outbound_at: datetime | None = None
    last_message_at: datetime | None = None
    metadata: dict | None = None
    archived: bool | None = None
    created_at: datetime


class Message(BaseModel):
    id: str
    chat_id: str
    external_id: str | None = None
    direction: MessageDirection
    body: str | None = None
    status: MessageStatus
    tag: str | None = None
    external_comment_id: str | None = None
    error_message: str | None = None
    platform_data: dict | None = None
    external_posted_at: datetime | None = None
    external_delivered_at: datetime | None = None
    external_read_at: datetime | None = None
    external_edited_at: datetime | None = None
    reply_to_external_id: str | None = None
    reply_markup: dict | None = None
    external_deleted_at: datetime | None = None
    reactions: list[Reaction] = []
    attachments: list[Attachment] = []
    is_unsupported: bool = False
    created_at: datetime


# --- Connection models ---


class OAuthConnectionResponse(BaseModel):
    url: str
    success: bool


class SyncProfile(BaseModel):
    id: str
    network: Platform
    name: str
    external_username: str | None = None


class BlueskyConnectionResponse(BaseModel):
    success: bool
    profile: SyncProfile


class TelegramConnectionResponse(BaseModel):
    success: bool
    profile: SyncProfile
    next_step: str | None = None


# Backwards-compatible alias — the same response shape as OAuthConnectionResponse.
ConnectionResponse = OAuthConnectionResponse


# --- Stats models ---


class StatsRecord(BaseModel):
    stats: dict[str, Any]
    recorded_at: datetime


class PlatformStats(BaseModel):
    profile_id: str
    platform: Platform
    records: list[StatsRecord] = []


class PostStats(BaseModel):
    platforms: list[PlatformStats] = []


class StatsResponse(BaseModel):
    data: dict[str, PostStats]


class ProfileStats(BaseModel):
    profile_id: str
    platform: Platform
    placement_id: str | None = None
    records: list[StatsRecord] = []


class ProfileStatsResponse(BaseModel):
    data: ProfileStats


# --- Webhook event payloads ---


class PostProcessedPlatform(BaseModel):
    id: str
    platform: Platform
    name: str


class PostProcessedData(BaseModel):
    id: str
    body: str
    status: PostStatus
    scheduled_at: datetime | None = None
    created_at: datetime
    platforms: list[PostProcessedPlatform] = []


class ImportedProfile(BaseModel):
    id: str
    name: str
    platform: Platform


class PostImportedData(BaseModel):
    id: str
    body: str
    source: Literal["imported"] = "imported"
    posted_at: datetime | None = None
    created_at: datetime
    platform: Platform
    profile: ImportedProfile
    platform_post_id: str
    public_id: str | None = None


class PlatformPostData(BaseModel):
    id: str
    post_id: str
    platform: Platform
    profile_id: str
    profile_name: str
    status: PlatformPostStatus
    error: str | None = None
    error_details: ErrorDetails | None = None
    platform_id: str | None = None


class PlatformPostInsightsData(PlatformPostData):
    insights: dict[str, Any] = {}


class ProfileEventData(BaseModel):
    id: str
    name: str
    platform: Platform
    profile_group_id: str
    status: str
    uid: str
    username: str | None = None


class ProfileStatsData(BaseModel):
    profile_id: str
    platform: Platform
    placement_id: str | None = None
    stats: dict[str, Any] = {}
    recorded_at: datetime


class MediaFailedData(BaseModel):
    id: str
    post_id: str
    content_type: str
    status: str
    error_message: str


class CommentCreatedData(BaseModel):
    id: str
    post_id: str
    platform_post_id: str
    platform: Platform
    external_id: str | None = None
    parent_external_id: str | None = None
    body: str
    status: str
    author_external_id: str | None = None
    author_name: str | None = None
    author_username: str | None = None
    author_avatar_url: str | None = None
    like_count: int = 0
    reply_count: int = 0
    is_hidden: bool = False
    permalink: str | None = None
    platform_data: dict | None = None
    posted_at: datetime | None = None
    created_at: datetime


class MessageEventData(BaseModel):
    message: Message


class ReactionEventData(BaseModel):
    message: Message
    sender_external_id: str
    action: Literal["react", "unreact"]
    reaction: str | None = None
    emoji: str | None = None
    occurred_at: datetime | None = None


class ProfileCommentCreatedData(BaseModel):
    id: str
    profile_id: str
    platform: Platform
    placement_id: str | None = None
    external_id: str | None = None
    parent_external_id: str | None = None
    body: str
    status: str
    author_username: str | None = None
    author_avatar_url: str | None = None
    platform_data: dict | None = None
    posted_at: datetime | None = None
    created_at: datetime


class WebhookEvent(BaseModel):
    id: str
    type: WebhookEventType
    created_at: datetime
    data: dict[str, Any]


# --- Platform parameter models ---


class FacebookParams(BaseModel):
    format: FacebookFormat | None = None
    title: str | None = None
    first_comment: str | None = None
    page_id: str | None = None


class InstagramParams(BaseModel):
    format: InstagramFormat | None = None
    first_comment: str | None = None
    collaborators: list[str] | None = None
    cover_url: str | None = None
    audio_name: str | None = None
    trial_strategy: bool | None = None
    thumb_offset: int | None = None


class TikTokParams(BaseModel):
    format: TikTokFormat | None = None
    privacy_status: TikTokPrivacy | None = None
    photo_cover_index: int | None = None
    auto_add_music: bool | None = None
    made_with_ai: bool | None = None
    disable_comment: bool | None = None
    disable_duet: bool | None = None
    disable_stitch: bool | None = None
    brand_content_toggle: bool | None = None
    brand_organic_toggle: bool | None = None


class LinkedInParams(BaseModel):
    format: LinkedInFormat | None = None
    organization_id: str | None = None


class YouTubeParams(BaseModel):
    format: YouTubeFormat | None = None
    title: str | None = None
    privacy_status: YouTubePrivacy | None = None
    cover_url: str | None = None
    made_for_kids: bool | None = None
    tags: list[str] | None = None
    category_id: str | None = None
    contains_synthetic_media: bool | None = None


class PinterestParams(BaseModel):
    format: PinterestFormat | None = None
    title: str | None = None
    board_id: str | None = None
    destination_link: str | None = None
    cover_url: str | None = None
    thumb_offset: int | None = None


class ThreadsParams(BaseModel):
    format: ThreadsFormat | None = None


class TwitterParams(BaseModel):
    format: TwitterFormat | None = None


class BlueskyParams(BaseModel):
    format: BlueskyFormat | None = None


class TelegramParams(BaseModel):
    format: TelegramFormat | None = None
    chat_id: str
    parse_mode: TelegramParseMode | None = None
    disable_link_preview: bool | None = None
    disable_notification: bool | None = None


# --- Queue models ---


class Timeslot(BaseModel):
    id: int
    day: int
    time: str


class Queue(BaseModel):
    id: str
    name: str
    description: str | None = None
    timezone: str
    enabled: bool
    jitter: int
    profile_group_id: str
    timeslots: list[Timeslot] = []
    posts_count: int


class NextSlotResponse(BaseModel):
    next_slot: str


class ThreadChildInput(BaseModel):
    body: str
    media: list[str] | None = None
    media_files: list[str] | None = None


class PlatformParams(BaseModel):
    facebook: FacebookParams | None = None
    instagram: InstagramParams | None = None
    tiktok: TikTokParams | None = None
    linkedin: LinkedInParams | None = None
    youtube: YouTubeParams | None = None
    pinterest: PinterestParams | None = None
    threads: ThreadsParams | None = None
    twitter: TwitterParams | None = None
    bluesky: BlueskyParams | None = None
    telegram: TelegramParams | None = None
    google_business: dict[str, Any] | None = None
