# PostProxy Python SDK

Async Python client for the [PostProxy API](https://postproxy.dev). Fully typed with Pydantic v2 models and async/await via httpx.

## Installation

```bash
pip install postproxy-sdk
```

Requires Python 3.10+.

## Quick start

```python
import asyncio
from postproxy import PostProxy

async def main():
    async with PostProxy("your-api-key", profile_group_id="pg-abc") as client:
        # List profiles
        profiles = (await client.profiles.list()).data

        # Create a post
        post = await client.posts.create(
            "Hello from PostProxy!",
            profiles=[profiles[0].id],
        )
        print(post.id, post.status)

asyncio.run(main())
```

## Usage

### Client

```python
from postproxy import PostProxy

# Basic
client = PostProxy("your-api-key")

# With a default profile group (applied to all requests)
client = PostProxy("your-api-key", profile_group_id="pg-abc")

# With a custom httpx client
import httpx
client = PostProxy("your-api-key", httpx_client=httpx.AsyncClient(timeout=30))

# As a context manager (auto-closes the HTTP client)
async with PostProxy("your-api-key") as client:
    ...

# Manual cleanup
await client.close()
```

### Posts

```python
# List posts (paginated)
page = await client.posts.list(page=0, per_page=10, status="draft")
print(page.total, page.data)

# Filter by platform and schedule
from datetime import datetime
page = await client.posts.list(
    platforms=["instagram", "tiktok"],
    scheduled_after=datetime(2025, 6, 1),
)

# Get a single post
post = await client.posts.get("post-id")

# Create a post
post = await client.posts.create(
    "Check out our new product!",
    profiles=["profile-id-1", "profile-id-2"],
)

# Create a draft
post = await client.posts.create(
    "Draft content",
    profiles=["profile-id"],
    draft=True,
)

# Create with media URLs
post = await client.posts.create(
    "Photo post",
    profiles=["profile-id"],
    media=["https://example.com/image.jpg"],
)

# Create with local file uploads
post = await client.posts.create(
    "Posted with a local file!",
    profiles=["profile-id"],
    media_files=["./photo.jpg", "./video.mp4"],
)

# Mix media URLs and local files
post = await client.posts.create(
    "Mixed media",
    profiles=["profile-id"],
    media=["https://example.com/image.jpg"],
    media_files=["./local-photo.jpg"],
)

# Create with platform-specific params
from postproxy import PlatformParams, InstagramParams, TikTokParams

post = await client.posts.create(
    "Cross-platform post",
    profiles=["ig-profile", "tt-profile"],
    platforms=PlatformParams(
        instagram=InstagramParams(format="reel", collaborators=["@friend"]),
        tiktok=TikTokParams(format="video", privacy_status="PUBLIC_TO_EVERYONE"),
    ),
)

# Schedule a post
post = await client.posts.create(
    "Scheduled post",
    profiles=["profile-id"],
    scheduled_at="2025-12-25T09:00:00Z",
)

# Publish a draft
post = await client.posts.publish_draft("post-id")

# Update a post (only drafts or scheduled posts)
post = await client.posts.update("post-id", body="Updated content!")

# Update platform params only
from postproxy import PlatformParams, YouTubeParams
post = await client.posts.update(
    "post-id",
    platforms=PlatformParams(youtube=YouTubeParams(privacy_status="unlisted")),
)

# Replace profiles and media
post = await client.posts.update(
    "post-id",
    profiles=["twitter", "threads"],
    media=["https://example.com/new-image.jpg"],
)

# Replace thread children
post = await client.posts.update(
    "post-id",
    thread=[
        ThreadChildInput(body="Updated first reply"),
        ThreadChildInput(body="Updated second reply", media=["https://example.com/img.jpg"]),
    ],
)

# Remove all media
post = await client.posts.update("post-id", media=[])

# Create a thread post
from postproxy import ThreadChildInput

post = await client.posts.create(
    "Thread starts here",
    profiles=["profile-id"],
    thread=[
        ThreadChildInput(body="Second post in the thread"),
        ThreadChildInput(body="Third with media", media=["https://example.com/img.jpg"]),
    ],
)
for child in post.thread:
    print(child.id, child.body)

# Delete a post
result = await client.posts.delete("post-id")
print(result.deleted)  # True

# Delete a post and also remove it from social platforms
result = await client.posts.delete("post-id", delete_on_platform=True)

# Delete from platforms only (keeps DB record). Defaults to all platforms.
r1 = await client.posts.delete_on_platform("post-id")
# Target a single network
r2 = await client.posts.delete_on_platform("post-id", network="twitter")
# Target a specific profile
r3 = await client.posts.delete_on_platform("post-id", profile_id="prof-abc")
# Target a specific post profile (covers entire thread for that profile)
r4 = await client.posts.delete_on_platform("post-id", post_profile_id="pp-abc")
print(r1.deleting)  # [DeletingPlatform(post_profile_id=..., platform=...)]

# Get post stats
result = await client.posts.stats(["post-id-1", "post-id-2"])
for post_id, post_stats in result.data.items():
    for platform in post_stats.platforms:
        for record in platform.records:
            print(record.recorded_at, record.stats)

# Filter stats by platform and date range
from datetime import datetime
result = await client.posts.stats(
    ["post-id"],
    profiles=["instagram", "twitter"],
    from_date="2026-02-01T00:00:00Z",
    to_date="2026-02-24T00:00:00Z",
)
```

### Queues

```python
# List all queues
queues = (await client.queues.list()).data

# Get a queue
queue = await client.queues.get("queue-id")
print(queue.name, queue.timeslots, queue.enabled)

# Get next available slot
next_slot = await client.queues.next_slot("queue-id")
print(next_slot.next_slot)

# Create a queue with timeslots
queue = await client.queues.create(
    "Morning Posts",
    "profile-group-id",
    description="Weekday morning content",
    timezone="America/New_York",
    jitter=10,
    timeslots=[
        {"day": 1, "time": "09:00"},
        {"day": 2, "time": "09:00"},
        {"day": 3, "time": "09:00"},
    ],
)

# Update a queue
queue = await client.queues.update(
    "queue-id",
    jitter=15,
    timeslots=[
        {"day": 6, "time": "10:00"},        # add new timeslot
        {"id": 1, "_destroy": True},         # remove existing timeslot
    ],
)

# Pause/unpause a queue
await client.queues.update("queue-id", enabled=False)

# Delete a queue
result = await client.queues.delete("queue-id")
print(result.deleted)  # True

# Add a post to a queue
post = await client.posts.create(
    "This post will be scheduled by the queue",
    profiles=["profile-id"],
    queue_id="queue-id",
    queue_priority="high",
)
```

### Profiles

```python
# List all profiles
profiles = (await client.profiles.list()).data

# List profiles in a specific group (overrides client default)
profiles = (await client.profiles.list(profile_group_id="pg-other")).data

# Get a single profile
profile = await client.profiles.get("profile-id")
print(profile.name, profile.platform, profile.status)

# Get available placements for a profile
placements = (await client.profiles.placements("profile-id")).data
for p in placements:
    print(p.id, p.name)

# Delete a profile
result = await client.profiles.delete("profile-id")
print(result.success)  # True
```

### Webhooks

```python
# List webhooks
webhooks = (await client.webhooks.list()).data

# Get a webhook
webhook = await client.webhooks.get("wh-id")
print(webhook.url, webhook.events, webhook.enabled)

# Create a webhook
webhook = await client.webhooks.create(
    "https://example.com/webhook",
    events=["post.published", "post.failed"],
    description="My webhook",
)
print(webhook.id, webhook.secret)

# Update a webhook
webhook = await client.webhooks.update(
    "wh-id",
    events=["post.published"],
    enabled=False,
)

# Delete a webhook
result = await client.webhooks.delete("wh-id")

# List deliveries
deliveries = await client.webhooks.deliveries("wh-id", page=0, per_page=10)
for d in deliveries.data:
    print(d.event_type, d.response_status, d.success)
```

#### Signature verification

Verify incoming webhook signatures using HMAC-SHA256:

```python
from postproxy import verify_signature

is_valid = verify_signature(
    payload=request.body,                  # raw request body string
    signature_header=request.headers["X-PostProxy-Signature"],  # "t=...,v1=..."
    secret="whsec_...",                    # webhook secret from create response
)
```

#### Event types and typed payloads

Subscribe to any of these events (or pass `["*"]` for all):

`post.processed`, `post.imported`, `platform_post.published`, `platform_post.failed`, `platform_post.failed_waiting_for_retry`, `platform_post.insights`, `profile.connected`, `profile.disconnected`, `profile.stats`, `media.failed`, `comment.created`.

`parse_event_typed` validates the envelope and returns `(envelope, typed_data)`:

```python
from postproxy import (
    parse_event_typed,
    WebhookParseError,
    ProfileStatsData,
    PlatformPostData,
    CommentCreatedData,
)

try:
    envelope, data = parse_event_typed(request.body)
    if envelope.type == "profile.stats":
        assert isinstance(data, ProfileStatsData)
        print(data.profile_id, data.stats)
    elif envelope.type == "platform_post.published":
        assert isinstance(data, PlatformPostData)
        print("Published:", data.platform_id)
    elif envelope.type == "comment.created":
        assert isinstance(data, CommentCreatedData)
        print(f"{data.author_username}: {data.body}")
except WebhookParseError as e:
    print("Bad webhook body:", e)
```

### Comments

```python
# List comments on a post (paginated)
comments = await client.comments.list("post-id", "profile-id")
for comment in comments.data:
    print(comment.author_username, comment.body)
    for reply in comment.replies:
        print(f"  {reply.author_username}: {reply.body}")

# List with pagination
comments = await client.comments.list("post-id", "profile-id", page=2, per_page=10)

# Get a single comment
comment = await client.comments.get("post-id", "comment-id", "profile-id")

# Create a comment
comment = await client.comments.create("post-id", "profile-id", text="Great post!")

# Reply to a comment
reply = await client.comments.create("post-id", "profile-id", text="Thanks!", parent_id="comment-id")

# Delete a comment
result = await client.comments.delete("post-id", "comment-id", "profile-id")
print(result.accepted)  # True

# Hide / unhide a comment
await client.comments.hide("post-id", "comment-id", "profile-id")
await client.comments.unhide("post-id", "comment-id", "profile-id")

# Like / unlike a comment
await client.comments.like("post-id", "comment-id", "profile-id")
await client.comments.unlike("post-id", "comment-id", "profile-id")
```

### Profile Groups

```python
# List all groups
groups = (await client.profile_groups.list()).data

# Get a single group
group = await client.profile_groups.get("pg-id")
print(group.name, group.profiles_count)

# Create a group
group = await client.profile_groups.create("My New Group")

# Delete a group (must have no profiles)
result = await client.profile_groups.delete("pg-id")
print(result.deleted)  # True

# Initialize an OAuth platform connection
conn = await client.profile_groups.initialize_connection(
    "pg-id",
    platform="instagram",
    redirect_url="https://yourapp.com/callback",
)
print(conn.url)  # Redirect the user to this URL

# BlueSky — app password flow, synchronous
bsky = await client.profile_groups.connect_bluesky(
    "pg-id",
    identifier="yourname.bsky.social",
    app_password="xxxx-xxxx-xxxx-xxxx",
)
print(bsky.profile.id)

# Telegram — bring-your-own-bot. Channels populate asynchronously; poll
# placements until non-empty.
tg = await client.profile_groups.connect_telegram(
    "pg-id",
    bot_token="123456789:ABCdef-GhIJklMnOpQrStUvWxYz",
)
print(tg.profile.id, tg.next_step)

import asyncio
placements = []
while not placements:
    placements = (await client.profiles.placements(tg.profile.id)).data
    if not placements:
        await asyncio.sleep(3)
print("Channels:", [(p.id, p.name) for p in placements])
```

### Profile stats

Fetch the per-profile stats timeseries. `placement_id` is required for `facebook`, `linkedin`, and `telegram` profiles.

```python
# LinkedIn organization
stats = await client.profiles.get_profile_stats(
    "prof_li_001",
    placement_id="108520199",
    from_="2026-04-01T00:00:00Z",
)
for r in stats.data.records:
    print(r.recorded_at, r.stats.get("followerCount"))

# Bluesky — no placements
bsky = await client.profiles.get_profile_stats("prof_bsky_001")
print(bsky.data.records[-1].stats.get("followersCount"))
```

## Error handling

All errors extend `PostProxyError`, which includes the HTTP status code and raw response body:

```python
from postproxy import (
    PostProxyError,
    AuthenticationError,   # 401
    BadRequestError,       # 400
    NotFoundError,         # 404
    ValidationError,       # 422
)

try:
    await client.posts.get("nonexistent")
except NotFoundError as e:
    print(e.status_code)  # 404
    print(e.response)     # {"error": "Not found"}
except PostProxyError as e:
    print(f"API error {e.status_code}: {e}")
```

## Types

All responses are parsed into Pydantic v2 models. All list methods return a response object with a `data` field — access items via `.data`:

```python
profiles = (await client.profiles.list()).data
posts = await client.posts.list()  # also has .total, .page, .per_page
```

Key types:

| Model | Fields |
|---|---|
| `Post` | id, body, status, scheduled_at, created_at, media, thread, platforms, queue_id, queue_priority |
| `Profile` | id, name, status, platform, profile_group_id, expires_at, post_count |
| `ProfileGroup` | id, name, profiles_count |
| `Media` | id, type, url, status |
| `ThreadChild` | id, body, media |
| `ThreadChildInput` | body, media |
| `Webhook` | id, url, events, secret, enabled, description, created_at |
| `WebhookDelivery` | id, event_id, event_type, response_status, attempt_number, success, attempted_at, created_at |
| `PlatformResult` | platform, status, params, error, attempted_at, insights |
| `StatsResponse` | data (dict keyed by post id) |
| `PostStats` | platforms |
| `PlatformStats` | profile_id, platform, records |
| `StatsRecord` | stats (dict), recorded_at |
| `Queue` | id, name, description, timezone, enabled, jitter, profile_group_id, timeslots, posts_count |
| `Timeslot` | id, day, time |
| `NextSlotResponse` | next_slot |
| `ListResponse[T]` | data |
| `Comment` | id, external_id, body, status, author_username, author_avatar_url, author_external_id, parent_external_id, like_count, is_hidden, permalink, platform_data, posted_at, created_at, replies |
| `AcceptedResponse` | accepted |
| `PaginatedResponse[T]` | total, page, per_page, data |

### Platform parameter models

| Model | Platform |
|---|---|
| `FacebookParams` | format (`post`, `story`), first_comment, page_id |
| `InstagramParams` | format (`post`, `reel`, `story`), first_comment, collaborators, cover_url, audio_name, trial_strategy, thumb_offset |
| `TikTokParams` | format (`video`, `image`), privacy_status, photo_cover_index, auto_add_music, made_with_ai, disable_comment, disable_duet, disable_stitch, brand_content_toggle, brand_organic_toggle |
| `LinkedInParams` | format (`post`), organization_id |
| `YouTubeParams` | format (`post`), title, privacy_status, cover_url, made_for_kids, tags, category_id, contains_synthetic_media |
| `PinterestParams` | format (`pin`), title, board_id, destination_link, cover_url, thumb_offset |
| `ThreadsParams` | format (`post`) |
| `TwitterParams` | format (`post`) |
| `BlueskyParams` | format (`post`) |
| `TelegramParams` | format (`post`), chat_id (required), parse_mode (`HTML`, `MarkdownV2`), disable_link_preview, disable_notification |

Wrap them in `PlatformParams` when passing to `posts.create()`. Telegram needs a `chat_id` per post — list available channels with `client.profiles.placements(profile_id)`.

Supported platforms: facebook, instagram, tiktok, linkedin, youtube, twitter, threads, pinterest, bluesky, telegram.

## Development

```bash
pip install -e ".[dev]"
pytest
mypy postproxy/
```

## License

MIT
