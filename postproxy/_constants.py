from typing import Literal, get_args

DEFAULT_BASE_URL = "https://api.postproxy.dev"

VERSION = "1.14.0"

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
    "whatsapp",
]

ProfileStatus = Literal["active", "expired", "inactive"]

PostStatus = Literal["pending", "draft", "processing", "processed", "scheduled", "media_processing_failed"]

MediaStatus = Literal["pending", "processed", "failed"]

PlatformPostStatus = Literal["pending", "processing", "published", "failed", "deleted"]

InstagramFormat = Literal["post", "reel", "story"]

FacebookFormat = Literal["post", "story", "reel"]

TikTokFormat = Literal["video", "image"]

LinkedInFormat = Literal["post", "poll"]

YouTubeFormat = Literal["post"]

PinterestFormat = Literal["pin"]

ThreadsFormat = Literal["post"]

TwitterFormat = Literal["post", "poll"]

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

PostSyncTrigger = Literal["connect", "scheduled", "backfill"]

PostSyncStatus = Literal["pending", "running", "completed", "failed"]

InstagramTrialStrategy = Literal["MANUAL", "SS_PERFORMANCE"]

InstagramAudioType = Literal["music", "original_sound"]

# Facebook and Instagram profiles connect through Facebook login; WhatsApp
# through the Cloud API or the WhatsApp Business app.
ConnectionOnboarding = Literal["instagram", "facebook", "api", "business_app"]

DailyStatsAttribution = Literal["received", "publish"]

ProfileInactiveReason = Literal["network_taken"]

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
    "platform_post.edited",
    "platform_post.edit_failed",
    "platform_post.insights",
    "profile.connected",
    "profile.disconnected",
    "profile.stats",
    "profile.placements_synced",
    "placement.orphaned",
    "placement.restored",
    "media.failed",
    "comment.created",
    "comment.failed",
    "comment.failed_waiting_for_retry",
    "comment.delivery_unconfirmed",
    "comment.edited",
    "comment.edit_failed",
    "profile_comment.created",
    "profile_comment.failed",
    "profile_comment.failed_waiting_for_retry",
    "profile_comment.deleted",
    "message.received",
    "message.sent",
    "message.delivered",
    "message.read",
    "message.edited",
    "message.deleted",
    "message.failed_waiting_for_retry",
    "message.failed",
    "reaction.received",
    "referral.received",
    "message_template.status_updated",
    "message_template.category_updated",
    "placement.name_status_updated",
    "placement.quality_updated",
    "whatsapp.automatic_event",
]

WEBHOOK_EVENT_TYPES: tuple[str, ...] = get_args(WebhookEventType)
