from typing import Literal

DEFAULT_BASE_URL = "https://api.postproxy.dev"

Platform = Literal[
    "facebook",
    "instagram",
    "tiktok",
    "linkedin",
    "youtube",
    "twitter",
    "threads",
    "pinterest",
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

TikTokPrivacy = Literal[
    "PUBLIC_TO_EVERYONE",
    "MUTUAL_FOLLOW_FRIENDS",
    "FOLLOWER_OF_CREATOR",
    "SELF_ONLY",
]

YouTubePrivacy = Literal["public", "unlisted", "private"]
