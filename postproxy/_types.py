from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Literal, TypeVar, Union

from pydantic import BaseModel, Field

from ._constants import (
    BlueskyFormat,
    DailyStatsAttribution,
    FacebookFormat,
    InstagramFormat,
    InstagramTrialStrategy,
    LinkedInFormat,
    MediaStatus,
    MessageDirection,
    MessageStatus,
    PinterestFormat,
    Platform,
    PlatformPostStatus,
    PostStatus,
    PostSyncStatus,
    PostSyncTrigger,
    ProfileInactiveReason,
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
    username: str | None = None
    status: ProfileStatus
    # Why an `inactive` profile was deactivated; `network_taken` means the same
    # account was connected elsewhere.
    inactive_reason: ProfileInactiveReason | None = None
    platform: Platform
    # The account's id on the platform.
    platform_id: str | None = None
    profile_group_id: str
    expires_at: datetime | None = None
    post_count: int
    avatar_url: str | None = None
    platform_url: str | None = None
    placements_sync_status: str | None = None


class Placement(BaseModel):
    id: str
    name: str
    avatar_url: str | None = None
    metadata: dict[str, Any] | None = None


class AccountPlacementProfile(BaseModel):
    id: str
    name: str
    connected: bool


class AccountPlacement(BaseModel):
    """An account-level placement, returned by :meth:`PlacementsResource.list`.

    A placement (a Facebook Page, LinkedIn organization, WhatsApp number, ...)
    can be reachable through several connected profiles; one of them is active.
    """

    id: str
    platform: Platform
    external_id: str
    name: str
    avatar_url: str | None = None
    status: str
    active_profile: AccountPlacementProfile | None = None
    linked_profiles: list[AccountPlacementProfile] = []


class ApiKey(BaseModel):
    id: str
    name: str
    profile_group_id: str | None = None
    sandbox: bool = False
    # Only returned by `api_keys.create()` — store it, it can't be read again.
    token: str | None = None
    created_at: datetime


class AssignedPlacement(BaseModel):
    id: str
    name: str
    metadata: dict[str, Any] | None = None
    profile_group_id: str


class IceBreaker(BaseModel, extra="allow"):
    question: str
    payload: str


class IceBreakersResponse(BaseModel):
    ice_breakers: list[IceBreaker] = []


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


class PlatformAttachment(BaseModel):
    """A file PostProxy generated for one platform, e.g. a TikTok cover."""

    id: str
    type: str
    status: str
    content_type: str | None = None
    url: str | None = None


class PlatformResult(BaseModel):
    platform: Platform
    profile_id: str | None = None
    profile_name: str | None = None
    status: PlatformPostStatus
    permalink: str | None = None
    params: dict | None = None
    error: str | None = None
    error_details: ErrorDetails | None = None
    attempted_at: datetime | None = None
    insights: Insights | None = None
    attachments: list[PlatformAttachment] = []


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
    # Each thread item is delivered separately; this shows whether it went out.
    platforms: list[PlatformResult] = []


class Post(BaseModel):
    id: str
    body: str
    status: PostStatus
    scheduled_at: datetime | None = None
    created_at: datetime
    media: list[Media] = []
    platforms: list[PlatformResult] = []
    thread: list[ThreadChild] = []
    draft: bool | None = None
    source: Literal["postproxy", "imported"] | None = None
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
    external_edited_at: datetime | None = None
    posted_at: datetime | None = None
    created_at: datetime
    replies: list[Comment] = []


class BulkComment(BaseModel):
    """A comment from :meth:`CommentsResource.list_all`.

    Flat: replies are their own entries linked to their parent by
    ``parent_external_id`` rather than nested under ``replies``.
    """

    post_id: str
    profile_id: str
    platform: Platform
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
    external_edited_at: datetime | None = None
    posted_at: datetime | None = None
    created_at: datetime


class PostSync(BaseModel):
    id: str
    profile_id: str
    placement_id: str | None = None
    kind: str
    trigger: PostSyncTrigger
    status: PostSyncStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    posts_seen: int = 0
    # Posts that were new and got created — lower than `posts_seen` whenever
    # the run re-read posts you already have.
    posts_imported: int = 0
    backfill_from: datetime | None = None
    # Publish date of the oldest post the run reached.
    oldest_posted_at: datetime | None = None
    error: str | None = None
    created_at: datetime


class ChatSync(BaseModel):
    """A chat (DM) sync run, started by :meth:`ProfilesResource.backfill_chats` or on connect."""

    id: str
    profile_id: str
    placement_id: str | None = None
    kind: str | None = None
    trigger: PostSyncTrigger | None = None
    status: PostSyncStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    chats_seen: int = 0
    messages_imported: int = 0
    backfill_from: datetime | None = None
    oldest_updated_at: datetime | None = None
    error: str | None = None
    created_at: datetime | None = None


class Reaction(BaseModel):
    sender_external_id: str
    emoji: str | None = None
    reaction: str | None = None
    at: datetime | None = None


class Chat(BaseModel):
    id: str
    profile_id: str
    platform: Platform
    # The page / phone number the chat runs through.
    external_placement_id: str | None = None
    # WhatsApp group chat.
    group: bool = False
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
    # WhatsApp-only: whether the 24-hour customer service window is open. When
    # it's closed only a template can be sent.
    within_messaging_window: bool | None = None
    created_at: datetime


class QuickReply(BaseModel):
    """A tappable chip above the participant's composer, gone once tapped.

    Facebook and Instagram only; up to 13 per send. ``content_type`` is optional
    on send (only ``"text"`` is accepted) and always present on responses.
    """

    content_type: str | None = None
    title: str
    payload: str


class MessageButton(BaseModel):
    """A button attached to the message, delivered as a Meta generic template.

    Facebook and Instagram only; up to 3 per send. ``url`` is required and must
    be https when ``type`` is ``"web_url"``; ``payload`` is required when
    ``type`` is ``"postback"``. ``type`` is a plain string rather than an enum so
    a new Meta button type needs no SDK release.
    """

    type: str
    title: str
    url: str | None = None
    payload: str | None = None


class CardDefaultAction(BaseModel):
    type: str
    url: str


class MessageCard(BaseModel):
    """Extra fields for the generic-template element that carries ``buttons``.

    Requires ``buttons``. ``subtitle`` is capped at 80 characters, and both URLs
    must be https.
    """

    subtitle: str | None = None
    image_url: str | None = None
    default_action: CardDefaultAction | None = None


class MessageElement(BaseModel):
    """One card of a horizontally scrolling carousel.

    Facebook and Instagram only; up to 10 per send. ``title`` (80 characters or
    fewer) plus at least one other field is required; up to 3 ``buttons``.
    """

    title: str
    subtitle: str | None = None
    image_url: str | None = None
    default_action: CardDefaultAction | None = None
    buttons: list[MessageButton] | None = None


class MessageLocation(BaseModel):
    latitude: float
    longitude: float
    name: str | None = None
    address: str | None = None


class TemplateButtonParam(BaseModel, extra="allow"):
    """Parameters for one template button, e.g. the dynamic part of a URL button.

    ``sub_type`` is one of ``url``, ``copy_code``, ``flow``, ``quick_reply`` or
    ``voice_call``; extra keys (``text``, ``coupon_code``, ...) pass through.
    """

    index: int
    sub_type: str


class TemplateHeaderMedia(BaseModel):
    """``link`` or ``id`` for an image / video / document template header."""

    link: str | None = None
    id: str | None = None


class MessageTemplateInput(BaseModel):
    """A WhatsApp template send.

    Address the template by ``id`` (PostProxy or Meta id) or by ``name`` (plus
    ``language`` when it exists in several). ``variables`` are positional:
    header, then body, then dynamic URL buttons.
    """

    id: str | None = None
    name: str | None = None
    language: str | None = None
    variables: list[str] | None = None
    button_params: list[TemplateButtonParam] | None = None
    header_media: TemplateHeaderMedia | None = None
    header_location: MessageLocation | None = None


class MessageTemplateRef(BaseModel):
    id: str
    external_id: str | None = None
    name: str
    language: str
    variables: list[str] | None = None


class TappedAction(BaseModel):
    """Set on inbound messages created by a tap on an element you sent.

    Derived from ``platform_data`` rather than stored, so it also resolves for
    taps ingested before PostProxy exposed this field. ``kind`` is one of
    ``quick_reply``, ``postback``, or ``callback_query`` — the last is Telegram,
    so this is not Meta-only even though the send params are.
    """

    kind: str
    payload: str
    title: str | None = None


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
    error_details: ErrorDetails | None = None
    platform_data: dict | None = None
    external_posted_at: datetime | None = None
    external_delivered_at: datetime | None = None
    external_read_at: datetime | None = None
    external_edited_at: datetime | None = None
    reply_to_external_id: str | None = None
    reply_markup: dict | None = None
    quick_replies: list[QuickReply] | None = None
    buttons: list[MessageButton] | None = None
    card: MessageCard | None = None
    elements: list[MessageElement] | None = None
    tapped_action: TappedAction | None = None
    story_reply: dict | None = None
    # WhatsApp-only payloads.
    interactive: dict | None = None
    location: MessageLocation | None = None
    contacts: list[dict[str, Any]] | None = None
    template: MessageTemplateRef | None = None
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
    # Every metric under its original platform name, e.g. `views` for Instagram
    # or `impression_count` for Twitter/X.
    raw_stats: dict[str, Any] = {}
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


class DailyStatsRecord(BaseModel, extra="allow"):
    """One day of stats. Normalized metrics (e.g. ``impressions``, ``viewers``)
    are top-level extra fields — read them as attributes or via ``model_extra``."""

    date: str
    platform_stats: dict[str, Any] | None = None


class DailyStats(BaseModel):
    profile_id: str
    platform: Platform | None = None
    placement_id: str | None = None
    attribution: DailyStatsAttribution | None = None
    from_: str | None = Field(default=None, alias="from")
    to: str | None = None
    data_timezone: str | None = None
    records: list[DailyStatsRecord] = []
    # Describes each metric in `records`.
    metrics: dict[str, Any] = {}


class DailyStatsResponse(BaseModel):
    data: DailyStats


class FollowerHistoryRecord(BaseModel):
    date: str
    followers_gained: int | None = None
    followers_lost: int | None = None
    followers_change: int | None = None
    followers_total: int | None = None


class FollowerHistory(BaseModel):
    profile_id: str | None = None
    platform: Platform | None = None
    placement_id: str | None = None
    from_: str | None = Field(default=None, alias="from")
    to: str | None = None
    records: list[FollowerHistoryRecord] = []


class FollowerHistoryResponse(BaseModel):
    data: FollowerHistory


class ParticipantStatus(BaseModel, extra="allow"):
    """Instagram only. Cached for a short while server-side."""

    is_verified_user: bool | None = None
    is_user_follow_business: bool | None = None
    is_business_follow_user: bool | None = None
    fetched_at: datetime | None = None


class ResolvedMention(BaseModel):
    """LinkedIn only: a company page turned into a URN you can @-mention."""

    urn: str
    type: Literal["organization"] = "organization"
    name: str
    vanity_name: str


class InstagramAvailableAudioResponse(BaseModel, extra="allow"):
    data: list[dict[str, Any]] = []


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
    platform_id: str | None = None
    username: str | None = None
    # On `profile.disconnected`: whether a user disconnected it or PostProxy did.
    origin: Literal["user", "automated"] | None = None


class PlacementEventData(BaseModel, extra="allow"):
    """A placement in ``placement.*`` and ``profile.placements_synced`` events.

    ``placement.name_status_updated`` adds ``decision``, ``requested_name`` and
    ``rejection_reason``; ``placement.quality_updated`` adds ``event``,
    ``current_limit`` and ``old_limit`` — read them as extra attributes.
    """

    # The placement's id on the platform (page id, phone number id, ...).
    id: str
    name: str | None = None
    platform: Platform | None = None
    profile_group_id: str | None = None
    profile_id: str | None = None
    profile_name: str | None = None
    metadata: dict[str, Any] = {}


class PlacementsSyncedData(ProfileEventData):
    placements_sync_status: str | None = None
    placements: list[PlacementEventData] = []


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
    profile_id: str | None = None
    error: str | None = None
    error_details: ErrorDetails | None = None
    external_edited_at: datetime | None = None
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


class WebhookChatData(BaseModel):
    id: str
    profile_id: str
    platform: Platform
    external_placement_id: str | None = None
    group: bool = False
    participant_external_id: str
    participant_username: str | None = None
    participant_name: str | None = None
    last_inbound_at: datetime | None = None
    last_outbound_at: datetime | None = None
    last_message_at: datetime | None = None


class ReferralEventData(BaseModel):
    chat: WebhookChatData
    ref: str | None = None
    source: str | None = None
    type: str | None = None
    # WhatsApp click-to-WhatsApp ad click id.
    ctwa_clid: str | None = None
    occurred_at: datetime | None = None


class MessageTemplateEventData(BaseModel):
    id: str
    external_id: str | None = None
    profile_id: str
    platform: Literal["whatsapp"] = "whatsapp"
    name: str
    language: str
    category: str
    status: str
    rejected_reason: str | None = None
    quality_score: str | None = None


class WhatsAppAutomaticEventData(BaseModel, extra="allow"):
    profile_id: str
    chat_id: str | None = None
    participant_external_id: str | None = None
    external_message_id: str | None = None
    event_name: str | None = None
    ctwa_clid: str | None = None
    custom_data: dict[str, Any] | None = None


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
    error: str | None = None
    error_details: ErrorDetails | None = None
    permalink: str | None = None
    posted_at: datetime | None = None
    created_at: datetime


class WebhookEvent(BaseModel):
    id: str
    type: WebhookEventType
    created_at: datetime
    data: dict[str, Any]


# --- Platform parameter models ---

# A single string, or one per media item in order.
AltText = Union[str, list[str]]


class FacebookParams(BaseModel):
    format: FacebookFormat | None = None
    title: str | None = None
    first_comment: str | None = None
    page_id: str | None = None
    # Link post: Facebook renders the preview card. Text-only, no media.
    link: str | None = None
    alt_text: AltText | None = None
    # Photo posts only; videos and reels ignore it.
    made_with_ai: bool | None = None
    # ISO 3166-1 alpha-2 codes; viewers elsewhere won't see the post.
    countries: list[str] | None = None


class InstagramUserTag(BaseModel):
    """An Instagram account to tag in a post.

    Images require ``x`` and ``y``. Reels and video slides are tagged by
    username only — Instagram ignores coordinates there.
    """

    username: str
    x: float | None = None
    y: float | None = None
    # Which media item to tag, 0-based. Defaults to 0.
    media_index: int | None = None


class InstagramParams(BaseModel):
    format: InstagramFormat | None = None
    first_comment: str | None = None
    collaborators: list[str] | None = None
    cover_url: str | None = None
    # Local path to a cover image, uploaded with the post; a base64 data URL
    # (`data:image/jpeg;base64,...`) is sent as-is.
    cover_file: str | None = None
    audio_name: str | None = None
    # Music or sound id from `profiles.instagram_available_audio()`. Profiles
    # connected via Facebook login only.
    audio_id: str | None = None
    # 1-100, default 100. Facebook-login profiles only.
    audio_volume: int | None = None
    video_volume: int | None = None
    # Remove the video's own audio track (reel, story).
    strip_audio: bool | None = None
    trial_strategy: InstagramTrialStrategy | None = None
    thumb_offset: int | None = None
    user_tags: list[InstagramUserTag] | None = None
    alt_text: AltText | None = None
    made_with_ai: bool | None = None


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
    # Send to the creator's TikTok inbox as a draft instead of publishing.
    upload_as_draft: bool | None = None
    # Custom video cover. Profiles connected before 2026-09-30 must reconnect.
    cover_url: str | None = None
    # Local path to a cover image, uploaded with the post; a base64 data URL
    # (`data:image/jpeg;base64,...`) is sent as-is.
    cover_file: str | None = None
    # Frame to use as cover, in milliseconds. `cover_url` wins if both are set.
    thumb_offset: int | None = None


class LinkedInParams(BaseModel):
    format: LinkedInFormat | None = None
    organization_id: str | None = None
    # URN of a post to reshare, e.g. "urn:li:share:123".
    reshare_urn: str | None = None
    alt_text: AltText | None = None
    # Organization pages only; up to 25 ISO 3166-1 alpha-2 codes.
    countries: list[str] | None = None
    # Required when format is "poll": question of 140 characters or fewer,
    # 2-4 options (max 30 chars each); duration 1, 3, 7 (default) or 14 days.
    poll_question: str | None = None
    poll_options: list[str] | None = None
    poll_duration_days: Literal[1, 3, 7, 14] | None = None


class YouTubeParams(BaseModel):
    format: YouTubeFormat | None = None
    title: str | None = None
    privacy_status: YouTubePrivacy | None = None
    cover_url: str | None = None
    # Local path to a cover image, uploaded with the post; a base64 data URL
    # (`data:image/jpeg;base64,...`) is sent as-is.
    cover_file: str | None = None
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
    # Local path to a cover image, uploaded with the post; a base64 data URL
    # (`data:image/jpeg;base64,...`) is sent as-is.
    cover_file: str | None = None
    thumb_offset: int | None = None
    alt_text: AltText | None = None


class ThreadsParams(BaseModel):
    format: ThreadsFormat | None = None
    alt_text: AltText | None = None
    # One tag, 50 characters or fewer, without the leading # — no "." or "&".
    topic_tag: str | None = None


class TwitterParams(BaseModel):
    format: TwitterFormat | None = None
    alt_text: AltText | None = None
    # Required when format is "poll": 2-4 options (max 25 chars each),
    # duration 5 to 10080 minutes (7 days).
    poll_options: list[str] | None = None
    poll_duration_minutes: int | None = None


class BlueskyParams(BaseModel):
    format: BlueskyFormat | None = None
    alt_text: AltText | None = None


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


# A media item: a URL string, or `{"url": ...}`.
MediaInput = Union[str, dict[str, str]]


# --- WhatsApp models ---


class WhatsAppTemplate(BaseModel):
    id: str
    external_id: str | None = None
    profile_id: str
    name: str
    language: str
    category: str
    status: str
    parameter_format: Literal["POSITIONAL", "NAMED"] | None = None
    components: list[dict[str, Any]] = []
    message_send_ttl_seconds: int | None = None
    rejected_reason: str | None = None
    quality_score: str | None = None
    variable_count: int = 0
    created_at: datetime
    updated_at: datetime


class WhatsAppMedia(BaseModel):
    """An inbound media file downloaded by :meth:`WhatsAppResource.media`."""

    data: bytes
    content_type: str | None = None
