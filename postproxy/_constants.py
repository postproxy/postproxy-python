from typing import Literal, get_args

DEFAULT_BASE_URL = "https://api.postproxy.dev"

VERSION = "1.10.0"

Platform = Literal[
    "facebook",
    "instagram",
    "tiktok",
    "linkedin",
    "youtube",
    "twitter",
    "threads",
    "pinterest",
    "bluesky",
    "telegram",
    "google_business",
]

ProfileStatus = Literal["active", "expired", "inactive"]

PostStatus = Literal["pending", "draft", "processing", "processed", "scheduled", "media_processing_failed"]

MediaStatus = Literal["pending", "processed", "failed"]

PlatformPostStatus = Literal["pending", "processing", "published", "failed", "deleted"]

InstagramFormat = Literal["post", "reel", "story"]

FacebookFormat = Literal["post", "story", "reel"]

TikTokFormat = Literal["video", "image"]

LinkedInFormat = Literal["post"]

YouTubeFormat = Literal["post"]

PinterestFormat = Literal["pin"]

ThreadsFormat = Literal["post"]

TwitterFormat = Literal["post"]

BlueskyFormat = Literal["post"]

TelegramFormat = Literal["post"]

TikTokPrivacy = Literal[
    "PUBLIC_TO_EVERYONE",
    "MUTUAL_FOLLOW_FRIENDS",
    "FOLLOWER_OF_CREATOR",
    "SELF_ONLY",
]

YouTubePrivacy = Literal["public", "unlisted", "private"]

TelegramParseMode = Literal["HTML", "MarkdownV2"]

MessageDirection = Literal["inbound", "outbound"]

MessageStatus = Literal[
    "pending",
    "published",
    "failed_waiting_for_retry",
    "failed",
    "received",
]

WebhookEventType = Literal[
    "post.processed",
    "post.imported",
    "platform_post.published",
    "platform_post.failed",
    "platform_post.failed_waiting_for_retry",
    "platform_post.insights",
    "profile.connected",
    "profile.disconnected",
    "profile.stats",
    "media.failed",
    "comment.created",
    "profile_comment.created",
    "message.received",
    "message.sent",
    "message.delivered",
    "message.read",
    "message.edited",
    "message.deleted",
    "message.failed_waiting_for_retry",
    "message.failed",
    "reaction.received",
]

WEBHOOK_EVENT_TYPES: tuple[str, ...] = get_args(WebhookEventType)
