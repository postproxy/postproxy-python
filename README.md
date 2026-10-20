# Postproxy Python SDK

Async Python client for the [Postproxy API](https://postproxy.dev). Fully typed with Pydantic v2 models and async/await via httpx.

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

#### Idempotency

Every write method (`POST`/`PUT`/`PATCH`/`DELETE`) accepts an `idempotency_key`, sent as
the `Idempotency-Key` header. If the connection drops before you see the response, retry
with the same key and you get the original response back instead of a second post:

```python
import uuid

key = str(uuid.uuid4())
post = await client.posts.create("Hello", ["profile-id"], idempotency_key=key)

# Retrying the same call with the same key replays the original response.
```

Generate a fresh key per logical operation — a UUID is ideal. Keys are scoped to your
account and may be up to 255 characters. The SDK never generates keys or retries for you.

| Situation | Result |
|---|---|
| First request with the key | Runs normally |
| Retry after a success | Original status and body replayed |
| Retry while the first is still running | `ConflictError` (409) — wait and retry |
| Same key, different request body | `ValidationError` (422) |
| Retry after an error response | Runs normally — errors are not replayed |

Only successful (`2xx`) responses are stored, so a request that failed validation or hit a
quota leaves the key free — fix the payload and retry with the same key. Stored responses
are kept for **24 hours**. Requests without a key are unaffected.

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

# Media items can be URL strings or {"url": ...} dicts
post = await client.posts.create(
    "Photos",
    profiles=["profile-id"],
    media=["https://example.com/1.jpg", {"url": "https://example.com/2.jpg"}],
)

# Alt text, AI disclosure, and other per-platform params
from postproxy import FacebookParams, LinkedInParams

await client.posts.create(
    "Launch day",
    profiles=["ig-profile", "li-profile", "fb-profile"],
    media=["https://example.com/1.jpg", "https://example.com/2.jpg"],
    platforms=PlatformParams(
        instagram=InstagramParams(alt_text=["Our team", "The product"], made_with_ai=False),
        linkedin=LinkedInParams(
            alt_text="Our team and the product", countries=["US", "CA"], organization_id="123"
        ),
        facebook=FacebookParams(countries=["US"]),
    ),
)

# Facebook link post (text-only — renders the link preview card)
await client.posts.create(
    "Read the announcement",
    profiles=["fb-profile"],
    platforms=PlatformParams(facebook=FacebookParams(link="https://example.com/blog/launch")),
)

# LinkedIn poll
await client.posts.create(
    "Quick question for you all",
    profiles=["li-profile"],
    platforms=PlatformParams(
        linkedin=LinkedInParams(
            format="poll",
            organization_id="123",
            poll_question="Tabs or spaces?",
            poll_options=["Tabs", "Spaces"],
            poll_duration_days=7,  # 1, 3, 7 or 14
        )
    ),
)

# Threads topic tag, TikTok draft with a custom cover
from postproxy import ThreadsParams

await client.posts.create(
    "New drop",
    profiles=["threads-profile", "tt-profile"],
    media=["https://example.com/clip.mp4"],
    platforms=PlatformParams(
        threads=ThreadsParams(topic_tag="Sneakers"),
        tiktok=TikTokParams(
            format="video", upload_as_draft=True, cover_url="https://example.com/cover.jpg"
        ),
    ),
)

# Custom cover image (Instagram, TikTok, YouTube, Pinterest): a hosted URL…
from postproxy import PinterestParams, YouTubeParams

await client.posts.create(
    "New video",
    profiles=["yt-profile"],
    media=["https://example.com/video.mp4"],
    platforms=PlatformParams(
        youtube=YouTubeParams(title="Launch", cover_url="https://example.com/cover.jpg")
    ),
)
# …or a local file, uploaded with the post (switches the request to multipart)…
await client.posts.create(
    "New video",
    profiles=["tt-profile"],
    media=["https://example.com/video.mp4"],
    platforms=PlatformParams(tiktok=TikTokParams(format="video", cover_file="./cover.jpg")),
)
# …or a base64 data URL, sent as-is
await client.posts.create(
    "New pin",
    profiles=["pin-profile"],
    media=["https://example.com/video.mp4"],
    platforms=PlatformParams(
        pinterest=PinterestParams(board_id="board-id", cover_file="data:image/jpeg;base64,/9j/4AAQ...")
    ),
)

# Instagram reel with licensed music (profiles connected via Facebook login).
# Find an audio_id with client.profiles.instagram_available_audio().
await client.posts.create(
    "Summer vibes",
    profiles=["ig-profile"],
    media=["https://example.com/reel.mp4"],
    platforms=PlatformParams(
        instagram=InstagramParams(
            format="reel", audio_id="1234567890", audio_volume=60, video_volume=30
        )
    ),
)

# Skip the duplicate check (otherwise an identical post submitted moments ago
# raises ConflictError)
await client.posts.create("Same text again", profiles=["profile-id"], skip_duplicate_check=True)

# Schedule a post
post = await client.posts.create(
    "Scheduled post",
    profiles=["profile-id"],
    scheduled_at="2025-12-25T09:00:00Z",
)

# Publish a draft
post = await client.posts.publish_draft("post-id")

# Update a post
post = await client.posts.update("post-id", body="Updated content!")

# Edit a post that's already published. Only the body, the YouTube title and
# the Pinterest title / destination_link can change; anything else is a 422.
# The edit is pushed to the platforms in the background — watch for the
# platform_post.edited / platform_post.edit_failed webhooks.
post = await client.posts.update(
    "published-post-id",
    body="Fixed a typo",
    platforms=PlatformParams(youtube=YouTubeParams(title="Better title")),
)

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
    # Each thread item is delivered on its own; its platforms show whether it went out
    print([(p.platform, p.status) for p in child.platforms])

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

# Move a placement (e.g. a Facebook Page or Telegram channel) to another group
placement = await client.profiles.assign_placement_to_group(
    "profile-id",
    placement_id="placement-external-id",
    target_profile_group_id="pg-other",
)
print(placement.profile_group_id)  # "pg-other"

# Move the whole profile (with its placements) to another group
await client.profiles.assign_to_group("profile-id", "pg-other")

# Daily stats and follower history
daily = await client.profiles.daily_stats(
    "profile-id",
    from_="2026-09-01",
    to="2026-09-30",
    attribution="publish",  # or "received" (default)
)
for day in daily.data.records:
    print(day.date, day.impressions)  # normalized metrics are top-level fields

followers = await client.profiles.follower_history("profile-id", from_="2026-09-01")
for day in followers.data.records:
    print(day.date, day.followers_total)

# Instagram: whether a DM participant is verified / follows you
status = await client.profiles.participant_status("ig-profile-id", "igsid-123")

# LinkedIn: resolve a company page to the URN used to @-mention it
mention = await client.profiles.resolve_mention(
    "li-profile-id", "https://www.linkedin.com/company/acme"
)
print(mention.urn)  # "urn:li:organization:123"

# Instagram (Facebook login): music for reels — pass the id as InstagramParams.audio_id
audio = await client.profiles.instagram_available_audio(
    "ig-profile-id",
    audio_type="music",  # or "original_sound"
    search_query="summer",
)

# Facebook Page about / contact info
page = await client.profiles.facebook_page("fb-profile-id", "page-id")
await client.profiles.update_facebook_page(
    "fb-profile-id",
    "page-id",
    {"about": "Coffee roasters since 2010", "website": "https://example.com"},
)

# Ice breakers (Instagram DMs): FAQ prompts shown when a user opens a chat
result = await client.profiles.ice_breakers("profile-id")
print([ib.question for ib in result.ice_breakers])

await client.profiles.set_ice_breakers(
    "profile-id",
    [
        {"question": "What services do you offer?", "payload": "services"},
        {"question": "What are your hours?", "payload": "hours"},
    ],
)  # 1-4 items

await client.profiles.delete_ice_breakers("profile-id")

# Delete a profile
result = await client.profiles.delete("profile-id")
print(result.success)  # True
```

#### Post syncs & backfill

Postproxy mirrors posts published natively on a platform into your account. Every one of
those pulls is recorded as a **post sync**: the one fired when the profile connects, the
recurring poll, and any backfill you start.

```python
# Start a backfill — walks the feed backwards from the newest post in batches
# of 25 until it reaches `from_` or the platform stops returning posts.
sync = await client.profiles.backfill_posts("profile-id", from_="2025-01-01")
print(sync.id, sync.status)  # "sync456def" "pending"

# Poll it to completion — finished when status is "completed" or "failed"
run = await client.profiles.post_sync("profile-id", sync.id)
print(run.posts_imported, "of", run.posts_seen, "back to", run.oldest_posted_at)

# List recent runs (kept for 30 days), newest first
runs = await client.profiles.post_syncs(
    "profile-id",
    trigger="backfill",   # connect | scheduled | backfill
    status="completed",   # pending | running | completed | failed
    per_page=25,
)
```

| `PostSync` field | Description |
|---|---|
| `id` | Sync identifier |
| `profile_id` | Profile this run belongs to |
| `kind` | Always `posts` today |
| `trigger` | `connect`, `scheduled`, or `backfill` |
| `status` | `pending`, `running`, `completed`, or `failed` |
| `started_at` / `completed_at` | Timestamps, `None` until set |
| `posts_seen` | Posts the platform returned across the run |
| `posts_imported` | Posts that were **new** and got created |
| `backfill_from` | The date floor requested; `None` for `connect`/`scheduled` |
| `oldest_posted_at` | Publish date of the oldest post the run reached |
| `error` | Platform error message when `status` is `failed` |
| `created_at` | Timestamp |

**How far back a backfill reaches depends on the platform's API**, not on Postproxy: where
history is pageable we follow it, otherwise the run ends early with whatever it got and
still reports `status="completed"`.

Only one backfill runs per profile at a time — starting a second raises `ConflictError`
carrying the running one's id:

```python
from postproxy import ConflictError

try:
    await client.profiles.backfill_posts("profile-id", from_="2025-01-01")
except ConflictError as e:
    running_id = e.response["profile_sync_id"]
    # Poll the run that's already going.
```

Posts you already have are skipped, so overlapping backfills are safe. Imported posts
behave exactly like ones the poll picks up (`source="imported"`, `post.imported` webhook),
but a backfill's follow-up work is queued at a lower priority so a deep run can't slow
down publishing.

#### Chat backfill

`backfill_chats()` imports DM history the same way `backfill_posts()` imports posts. Runs
are `ChatSync` records (`chats_seen`, `messages_imported`, `oldest_updated_at`).

```python
run = await client.profiles.backfill_chats("profile-id", from_="2026-01-01")
latest = await client.profiles.chat_sync("profile-id", run.id)
runs = await client.profiles.chat_syncs("profile-id", status="completed")
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

- **Posts:** `post.processed`, `post.imported`, `platform_post.published`, `platform_post.failed`, `platform_post.failed_waiting_for_retry`, `platform_post.edited`, `platform_post.edit_failed`, `platform_post.insights`, `media.failed`
- **Profiles:** `profile.connected`, `profile.disconnected`, `profile.stats`, `profile.placements_synced`, `placement.orphaned`, `placement.restored`
- **Comments:** `comment.created`, `comment.failed`, `comment.failed_waiting_for_retry`, `comment.delivery_unconfirmed`, `comment.edited`, `comment.edit_failed`, `profile_comment.created`, `profile_comment.failed`, `profile_comment.failed_waiting_for_retry`, `profile_comment.deleted`
- **Messages:** `message.received`, `message.sent`, `message.delivered`, `message.read`, `message.edited`, `message.deleted`, `message.failed_waiting_for_retry`, `message.failed`, `reaction.received`, `referral.received`
- **WhatsApp:** `message_template.status_updated`, `message_template.category_updated`, `placement.name_status_updated`, `placement.quality_updated`, `whatsapp.automatic_event`

The direct-message events (`message.*`) carry a `MessageEventData` (`.message` is a full `Message`); `reaction.received` carries a `ReactionEventData`; `referral.received` a `ReferralEventData`; the `profile_comment.*` events a `ProfileCommentCreatedData`; the other `comment.*` events a `CommentCreatedData`; `profile.placements_synced` a `PlacementsSyncedData`; the `placement.*` events a `PlacementEventData` (extra keys such as `current_limit` are kept as attributes); `message_template.*` a `MessageTemplateEventData`; and `whatsapp.automatic_event` a `WhatsAppAutomaticEventData`.

`parse_event_typed` validates the envelope and returns `(envelope, typed_data)`:

```python
from postproxy import (
    parse_event_typed,
    WebhookParseError,
    ProfileStatsData,
    PlatformPostData,
    CommentCreatedData,
    MessageEventData,
    MessageTemplateEventData,
    ReactionEventData,
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
    elif envelope.type == "message.received":
        assert isinstance(data, MessageEventData)
        print(f"DM from {data.message.chat_id}: {data.message.body}")
    elif envelope.type == "reaction.received":
        assert isinstance(data, ReactionEventData)
        print(f"{data.action}: {data.reaction} on {data.message.id}")
    elif envelope.type == "platform_post.edited":
        print("Edit went live on", data.platform)
    elif envelope.type == "message_template.status_updated":
        assert isinstance(data, MessageTemplateEventData)
        print(f"{data.name}: {data.status}")
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

# Filter by when PostProxy received the comment (created_at, not posted_at).
# A bare date means that date's start of day. Applies to top-level comments —
# one in range brings its full replies list with it.
recent = await client.comments.list(
    "post-id", "profile-id", from_="2026-03-25", to="2026-03-26T12:00:00Z"
)

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

# Edit a comment you published (Facebook and YouTube). Runs in the
# background — comment.edited / comment.edit_failed report the outcome.
await client.comments.edit("post-id", "comment-id", "profile-id", "Corrected text")

# Pin / unpin a comment (TikTok)
await client.comments.pin("post-id", "comment-id", "profile-id")
await client.comments.unpin("post-id", "comment-id", "profile-id")

# Synced comments may carry media attachments and author metadata
comment = await client.comments.get("post-id", "comment-id", "profile-id")
for att in comment.attachments:
    print(att.type, att.url, att.status)
if comment.metadata:
    print(comment.metadata.get("follower_count"))
```

#### Comments across posts

`comments.list_all()` returns comments spanning every post in the profile group in one
request — the comments counterpart to `posts.stats()`. Every filter is optional.

**This list is flat.** Unlike the per-post list, replies are not nested: every comment,
top-level or reply, is its own entry linked to its parent by `parent_external_id`, so
`total` counts every comment and paging is exact.

```python
all_comments = await client.comments.list_all(
    profiles=["instagram", "prof-abc"],  # profile IDs or network names, mixed
    post_ids=["post-1", "post-2"],       # omit for every post in scope
    placement_id="page-123",             # one Facebook Page / LinkedIn org
    from_="2026-03-25",
    per_page=50,                         # max 100
)

for c in all_comments.data:
    # Each entry says where it came from, so you can act on it with the
    # post-scoped methods above.
    print(c.platform, c.post_id, c.profile_id, c.body)
    if c.parent_external_id:
        print("  ↳ reply to", c.parent_external_id)

# Reply to one of them
first = all_comments.data[0]
await client.comments.create(first.post_id, first.profile_id, "Thanks!", parent_id=first.id)
```

Unknown or out-of-scope IDs in `post_ids` and `profiles` are ignored rather than erroring.
Results are ordered newest first by receipt time.

### Direct Messages

Read and send 1:1 messages on DM-capable profiles (Facebook Messenger, Instagram, WhatsApp, Telegram, Bluesky). A conversation is a **Chat**; it holds **Messages**. Outbound sends are processed asynchronously (`status` starts as `pending`).

```python
# List chats for a profile (paginated, most recent first)
chats = await client.chats.list("profile-id", per_page=20)
for chat in chats.data:
    print(chat.participant_username, chat.last_message_at)

# Find or create a chat with a participant (idempotent)
chat = await client.chats.create(
    "profile-id", "igsid_8675309", participant_username="jane_doe"
)

# Get a single chat
chat = await client.chats.get(chat.id)

# List messages in a chat (filter by direction/status)
messages = await client.messages.list(chat.id, direction="inbound")
for msg in messages.data:
    print(msg.direction, msg.body, [a.url for a in msg.attachments])

# Send a text message (within the 24h window)
sent = await client.messages.send(chat.id, body="Yes, we ship worldwide!")

# Send outside the 24h window with a tag (Facebook/Instagram)
await client.messages.send(chat.id, body="Following up.", tag="HUMAN_AGENT")

# Send media — by hosted URL or local file
await client.messages.send(chat.id, media=["https://cdn.example.com/photo.png"])
await client.messages.send(chat.id, media_files=["./photo.png"])

# Telegram: reply threading + inline keyboard
await client.messages.send(
    chat.id,
    body="Pick one:",
    reply_markup={"inline_keyboard": [[{"text": "Track order", "callback_data": "track:1"}]]},
)

# Get / edit (Telegram only) a message
msg = await client.messages.get(sent.id)
await client.messages.edit(sent.id, body="Updated answer.")

# React / unreact (Facebook & Instagram)
await client.messages.react(sent.id, reaction="love", emoji="❤️")
await client.messages.unreact(sent.id)

# Archive / unarchive a chat (Bluesky only)
await client.chats.archive(chat.id)
await client.chats.unarchive(chat.id)

# Mark the latest inbound message read (sends the read receipt on WhatsApp)
await client.chats.mark_read(chat.id)

# Typing indicator (Facebook, Instagram, WhatsApp)
await client.chats.start_typing(chat.id)
await client.chats.stop_typing(chat.id)

# Private reply to a comment's author (Instagram/Facebook) — returns a Message
reply = await client.comments.private_reply(
    "post-id", "comment-id", "profile-id", "DM-ing you the details."
)
print(reply.chat_id, reply.status)

# Private replies take the same interactive options as messages.send() —
# quick_replies, buttons, card, and a carousel of elements (text may be empty
# then). One private reply per comment, within 7 days of it.
await client.comments.private_reply(
    "post-id", "comment-id", "profile-id", "",
    elements=[
        {"title": "Red sneaker", "image_url": "https://cdn.example.com/red.png",
         "buttons": [{"type": "web_url", "title": "Shop", "url": "https://shop.example.com/red"}]},
    ],
)
```

#### Quick replies and buttons (Facebook & Instagram)

Meta's two interactive primitives. **Quick replies** are chips above the participant's
composer that disappear once tapped; **buttons** are attached to the message and stay in
the thread. Telegram's equivalent is `reply_markup` above — passing `quick_replies` or
`buttons` on a Telegram or Bluesky chat returns `422`.

Each param accepts typed models or plain dicts, whichever you prefer:

```python
from postproxy import CardDefaultAction, MessageButton, MessageCard, QuickReply

# Quick replies — up to 13. title ≤ 20 chars, payload ≤ 1000.
await client.messages.send(
    chat.id,
    body="What can I help with?",
    quick_replies=[
        QuickReply(title="Track order", payload="TRACK"),
        {"title": "Talk to support", "payload": "HELP"},
    ],
)

# Buttons — up to 3, each either web_url or postback. card is optional and
# requires buttons.
await client.messages.send(
    chat.id,
    body="Your order shipped",
    buttons=[
        MessageButton(type="web_url", title="Track", url="https://shop.example.com/o/123"),
        MessageButton(type="postback", title="Cancel", payload="CANCEL:123"),
    ],
    card=MessageCard(
        subtitle="Arriving Friday",
        image_url="https://cdn.example.com/shoe.png",
        default_action=CardDefaultAction(type="web_url", url="https://shop.example.com/o/123"),
    ),
)
```

Buttons are delivered as a Meta generic template and your `body` becomes the template's
element title — so **`body` is capped at 80 characters when buttons are present**. That is
Meta's limit, not Postproxy's, and a longer body is rejected with a `422` naming the
length. Buttons cannot be combined with media. Instagram is stricter than Messenger: it
delivers quick replies only on a plain-text message, so `quick_replies` with media or with
`buttons` returns `422` on Instagram while both are accepted on Facebook.

Validation happens server-side and names the offending index — `buttons[1].url must be an
https:// URL` — surfacing as the SDK's usual error for a `422`.

> The new params are sent on the JSON path only. To combine quick replies with an
> attachment, pass `media` as a hosted URL rather than uploading via `media_files`.

A tap comes back as an **inbound message** carrying `tapped_action`:

```python
inbound = await client.messages.list(chat.id, direction="inbound")
for msg in inbound.data:
    if msg.tapped_action:
        # kind: "quick_reply" | "postback" | "callback_query"
        print(msg.tapped_action.kind, msg.tapped_action.payload)
```

Subscribe to `message.received` to react to taps as they happen — the same field is on the
webhook payload. `tapped_action` is derived rather than stored, so it also resolves for
taps recorded before Postproxy exposed it, including Instagram ice-breaker taps and
Telegram callback queries (`kind="callback_query"`). A tap also opens the 24h window.

#### Carousels (Facebook & Instagram)

`elements` sends a horizontally scrolling carousel of up to 10 cards. Each card needs a
`title` (≤ 80 chars) plus at least one of `subtitle`, `image_url`, `default_action` or
`buttons` (≤ 3). A carousel can't be combined with `body`, `buttons` or `card`.

```python
from postproxy import MessageButton, MessageElement

await client.messages.send(
    chat.id,
    elements=[
        MessageElement(
            title="Red sneaker",
            subtitle="$89",
            image_url="https://cdn.example.com/red.png",
            buttons=[MessageButton(type="web_url", title="Buy", url="https://shop.example.com/red")],
        ),
        MessageElement(
            title="Blue sneaker",
            subtitle="$92",
            image_url="https://cdn.example.com/blue.png",
            buttons=[MessageButton(type="postback", title="Notify me", payload="NOTIFY:blue")],
        ),
    ],
)
```

#### WhatsApp

WhatsApp chats run through a phone number, so creating one takes the `placement_id` (the
phone number id from `profiles.placements()`). Send exactly one of `body`, `media`,
`template`, `interactive`, `location` or `contacts` per message. Outside the 24-hour
customer service window (`chat.within_messaging_window is False`) only an approved
template gets through.

```python
from postproxy import MessageLocation, MessageTemplateInput, TemplateButtonParam

chat = await client.chats.create("wa-profile-id", "15551234567", placement_id="phone-number-id")

# Template — address it by name (+ language) or id. Variables are positional:
# header, then body, then dynamic URL buttons.
await client.messages.send(
    chat.id,
    template=MessageTemplateInput(
        name="order_update",
        language="en_US",
        variables=["Jane", "#1234"],
        button_params=[TemplateButtonParam(index=0, sub_type="url", text="1234")],
    ),
)

# Location, contacts, and Meta's interactive messages (buttons, lists, ...)
await client.messages.send(
    chat.id,
    location=MessageLocation(latitude=52.52, longitude=13.405, name="Our store", address="Main St 1"),
)
await client.messages.send(
    chat.id,
    contacts=[{"name": {"formatted_name": "Support"}, "phones": [{"phone": "+15550000000"}]}],
)
await client.messages.send(
    chat.id,
    interactive={
        "type": "button",
        "body": {"text": "Did that help?"},
        "action": {"buttons": [{"type": "reply", "reply": {"id": "yes", "title": "Yes"}}]},
    },
)

# Send options
await client.messages.send(chat.id, body="https://example.com", link_preview=True)
await client.messages.send(chat.id, media=["https://example.com/invoice.pdf"], filename="invoice.pdf")
await client.messages.send(chat.id, media=["https://example.com/note.ogg"], voice_note=True)
```

Templates, number registration, the business profile, groups and more are managed through
`client.whatsapp_templates` and `client.whatsapp` — see [WhatsApp management](#whatsapp-management).

#### The `HUMAN_AGENT` tag

`HUMAN_AGENT` is Meta's Human Agent message tag, approved for Postproxy on **both
Facebook and Instagram**. It extends the reply window from 24 hours to **7 days** after the
participant's last inbound message, and allows free-form content (no template).

Postproxy does not enforce the 7-day ceiling — past it, Meta rejects the send and the
message lands in `status="failed"` with the platform error in `error_details`. The tag is
ignored on Telegram, and Bluesky has no messaging window at all.

> ⚠️ **Use it only for a human replying to the participant's own inquiry.** Sending
> promotional content, offers, or automated re-engagement under this tag violates Meta's
> policy and can get that Page or Instagram account's messaging capability suspended —
> you lose the ability to send DMs from it. The penalty is scoped to the offending
> account, not to your other profiles.


### Profile comments (Google Business reviews)

Profile-level comments expose Google Business reviews and replies. Reviews are user-generated — the SDK lets you list/get them and reply to or delete your own replies. Reviews sync twice daily.

```python
# List reviews for a profile (paginated)
reviews = await client.profile_comments.list("profile-id")
for review in reviews.data:
    print(review.author_username, (review.platform_data or {}).get("star_rating"), review.body)
    for reply in review.replies:
        print(f"  reply: {reply.body}")

# Filter by placement (location)
reviews = await client.profile_comments.list(
    "profile-id",
    placement_id="accounts/123/locations/456",
)

# Get a single review
review = await client.profile_comments.get("profile-id", "review-id")

# Reply to a review (parent_id is the review id)
reply = await client.profile_comments.create("profile-id", "review-id", text="Thanks for visiting!")

# Delete your reply
await client.profile_comments.delete("profile-id", "reply-id")
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

# Pick the onboarding flow: Instagram via Facebook login (needed for reel music),
# WhatsApp via the Cloud API ("api") or the WhatsApp Business app ("business_app").
await client.profile_groups.initialize_connection(
    "pg-id", "instagram", "https://yourapp.com/callback", onboarding="facebook"
)
await client.profile_groups.initialize_connection(
    "pg-id", "whatsapp", "https://yourapp.com/callback", onboarding="business_app"
)

# Re-authorize an existing connection
await client.profile_groups.initialize_connection(
    "pg-id", "linkedin", "https://yourapp.com/callback", refresh_connection=True
)

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

### Placements & API keys

Both require an **account-wide** API key.

```python
# Every placement (Facebook Page, LinkedIn org, WhatsApp number, ...) across groups
placements = await client.placements.list(per_page=50)
for p in placements.data:
    print(p.platform, p.name, "via", p.active_profile.name if p.active_profile else None)

# When several connected profiles reach the same placement, pick the one to use
await client.placements.set_active_profile("placement-id", "profile-id")

# Group-scoped API keys
key = await client.api_keys.create("CI pipeline", "pg-id")
print(key.token)  # shown only once
keys = (await client.api_keys.list()).data
await client.api_keys.delete(key.id)
```

### Google Business management

Manage a Google Business Profile location's own data — separate from posting to it.
`location_id` is the placement id from `profiles.placements()`. Google's camelCased
payloads pass through untouched (as plain dicts), so you can PATCH back what you GET;
updates take a `fields` list naming what to change.

```python
gbp = client.google_business

location = await gbp.location("gbp-profile-id", "location-id", read_mask="title,websiteUri")
await gbp.update_location(
    "gbp-profile-id", "location-id", ["websiteUri"], {"websiteUri": "https://example.com"}
)
await gbp.update_hours(
    "gbp-profile-id",
    "location-id",
    fields=["regularHours"],
    regular_hours={
        "periods": [
            {"openDay": "MONDAY", "openTime": {"hours": 9}, "closeDay": "MONDAY", "closeTime": {"hours": 17}}
        ]
    },
)

# Categories and attributes
await gbp.available_location_categories("gbp-profile-id", "location-id", "US", filter="coffee")
attrs = await gbp.attributes("gbp-profile-id", "location-id")
await gbp.available_attributes("gbp-profile-id", "location-id")
await gbp.update_attributes(
    "gbp-profile-id",
    "location-id",
    [{"name": "attributes/has_wi_fi", "values": [True]}],
    attribute_mask=["attributes/has_wi_fi"],
)

# Services and food menus
await gbp.service_list("gbp-profile-id", "location-id")
await gbp.update_service_list("gbp-profile-id", "location-id", [...])  # serviceItems
await gbp.food_menus("gbp-profile-id", "location-id")
await gbp.update_food_menus("gbp-profile-id", "location-id", [...])  # menus

# Place action links (booking, ordering, ...)
await gbp.available_place_action_types("gbp-profile-id", "location-id")
await gbp.create_place_action_link(
    "gbp-profile-id",
    "location-id",
    uri="https://book.example.com",
    place_action_type="APPOINTMENT",
    is_preferred=True,
)
links = await gbp.place_action_links("gbp-profile-id", "location-id")
await gbp.update_place_action_link(
    "gbp-profile-id", "location-id", "locations/1/placeActionLinks/2", ["uri"],
    uri="https://book.example.com/new",
)
await gbp.delete_place_action_link("gbp-profile-id", "location-id", "locations/1/placeActionLinks/2")

# Photos and videos
await gbp.create_media(
    "gbp-profile-id",
    "location-id",
    "https://example.com/storefront.jpg",
    category="EXTERIOR",
    media_format="PHOTO",
)
media = await gbp.media("gbp-profile-id", "location-id")
await gbp.delete_media("gbp-profile-id", "location-id", "accounts/1/locations/1/media/9")
```

### WhatsApp management

`phone_number_id` is the placement id from `profiles.placements()`. Responses are plain
dicts holding Meta's payload.

```python
# Message templates (submitted to Meta for review)
tpl = await client.whatsapp_templates.create(
    "wa-profile-id",
    name="order_update",
    category="UTILITY",
    language="en_US",
    components=[{"type": "BODY", "text": "Hi {{1}}, order {{2}} has shipped."}],
)
templates = (await client.whatsapp_templates.list("wa-profile-id", status="APPROVED")).data
await client.whatsapp_templates.get("wa-profile-id", "order_update", language="en_US")
await client.whatsapp_templates.update("wa-profile-id", tpl.id, message_send_ttl_seconds=3600)
await client.whatsapp_templates.delete("wa-profile-id", "order_update")  # every language
await client.whatsapp_templates.library("wa-profile-id", name="delivery")

wa = client.whatsapp

# Number registration
await wa.number_info("wa-profile-id", "phone-number-id")
await wa.request_verification_code("wa-profile-id", "phone-number-id", method="SMS", language="en")
await wa.verify_phone_number("wa-profile-id", "phone-number-id", "123456")
await wa.register_phone_number("wa-profile-id", "phone-number-id", "000000")  # two-step PIN

# Business profile, display name, username
await wa.update_business_profile(
    "wa-profile-id", "phone-number-id", about="We reply fast", websites=["https://example.com"]
)
await wa.update_business_profile_photo("wa-profile-id", "phone-number-id", url="https://example.com/logo.png")
await wa.request_display_name_change("wa-profile-id", "phone-number-id", "Acme Coffee")
await wa.username_suggestions("wa-profile-id", "phone-number-id")
await wa.set_username("wa-profile-id", "phone-number-id", "acmecoffee")

# Blocked users
await wa.block_users("wa-profile-id", "phone-number-id", ["15551234567"])
await wa.blocked_users("wa-profile-id", "phone-number-id")

# Groups
group = await wa.create_group(
    "wa-profile-id", "phone-number-id", "VIP customers", join_approval_mode="approval_required"
)
await wa.create_group_invite_link("wa-profile-id", "phone-number-id", "group-id")
await wa.group_join_requests("wa-profile-id", "phone-number-id", "group-id")
await wa.approve_group_join_requests("wa-profile-id", "phone-number-id", "group-id", ["15551234567"])

# Conversions for click-to-WhatsApp ads (account-level, no phone number id)
await wa.create_dataset("wa-profile-id")
await wa.send_conversion_event(
    "wa-profile-id",
    event_name="Purchase",
    event_id="order-1234",
    chat_id="chat-id",
    currency="USD",
    value=49.0,
)

# Download inbound media — returns raw bytes
file = await wa.media("wa-profile-id", "phone-number-id", "media-id")
print(file.content_type, len(file.data))
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

Every stats record (post stats and profile stats alike) carries `raw_stats` alongside the
normalized `stats`, exposing each metric under its **original platform name**:

```python
stats = await client.posts.stats(["post-id"])
record = stats.data["post-id"].platforms[0].records[0]

print(record.stats["impressions"])            # normalized
print(record.raw_stats["views"])              # Instagram's own name
print(record.raw_stats["impression_count"])   # Twitter/X's own name
```

LinkedIn post stats now normalize `likes`, `comments`, `shares`, and `clicks` alongside
`impressions` — previously only `impressions` was normalized.

## Error handling

All errors extend `PostProxyError`, which includes the HTTP status code and raw response body:

```python
from postproxy import (
    PostProxyError,
    AuthenticationError,   # 401
    BadRequestError,       # 400
    NotFoundError,         # 404
    ForbiddenError,        # 403
    ConflictError,         # 409
    ValidationError,       # 422
    RateLimitError,        # 429
)

try:
    await client.posts.get("nonexistent")
except NotFoundError as e:
    print(e.status_code)  # 404
    print(e.response)     # {"error": "Not found"}
except RateLimitError as e:
    print("Retry in", e.retry_after, "seconds")  # from Retry-After; None if absent
except PostProxyError as e:
    print(f"API error {e.status_code}: {e}")
```

| Status | Error | Raised for |
|---|---|---|
| 400 | `BadRequestError` | Missing required parameters |
| 401 | `AuthenticationError` | Invalid, missing, or insufficient API key permissions |
| 403 | `ForbiddenError` | Account canceled or past due, or the platform refused the action |
| 404 | `NotFoundError` | Resource does not exist or is not accessible |
| 409 | `ConflictError` | Duplicate submission (`response["duplicate_post_id"]`), a backfill already running (`response["profile_sync_id"]`), or an in-flight `Idempotency-Key` |
| 422 | `ValidationError` | Validation failed |
| 429 | `RateLimitError` | Posting rate limit reached, or the platform is rate-limiting — `retry_after` holds the `Retry-After` seconds |

## Types

All responses are parsed into Pydantic v2 models. All list methods return a response object with a `data` field — access items via `.data`:

```python
profiles = (await client.profiles.list()).data
posts = await client.posts.list()  # also has .total, .page, .per_page
```

Key types:

| Model | Fields |
|---|---|
| `Post` | id, body, status, scheduled_at, created_at, media, thread, platforms, draft, source, queue_id, queue_priority |
| `Profile` | id, name, username, status, inactive_reason, platform, platform_id, profile_group_id, expires_at, post_count, avatar_url, platform_url, placements_sync_status |
| `ProfileGroup` | id, name, profiles_count |
| `Media` | id, type, url, status |
| `ThreadChild` | id, body, media, platforms |
| `ThreadChildInput` | body, media |
| `Webhook` | id, url, events, secret, enabled, description, created_at |
| `WebhookDelivery` | id, event_id, event_type, response_status, attempt_number, success, attempted_at, created_at |
| `PlatformResult` | platform, profile_id, profile_name, status, permalink, params, error, error_details, attempted_at, insights, attachments |
| `StatsResponse` | data (dict keyed by post id) |
| `PostStats` | platforms |
| `PlatformStats` | profile_id, platform, records |
| `StatsRecord` | stats (dict), raw_stats (dict), recorded_at |
| `Queue` | id, name, description, timezone, enabled, jitter, profile_group_id, timeslots, posts_count |
| `Timeslot` | id, day, time |
| `NextSlotResponse` | next_slot |
| `ListResponse[T]` | data |
| `Comment` | id, external_id, body, status, author_username, author_avatar_url, author_external_id, parent_external_id, like_count, is_hidden, permalink, platform_data, external_edited_at, posted_at, created_at, replies |
| `BulkComment` | Every `Comment` field except `replies`, plus post_id, profile_id, platform — returned by `comments.list_all()` |
| `PostSync` | id, profile_id, placement_id, kind, trigger, status, started_at, completed_at, posts_seen, posts_imported, backfill_from, oldest_posted_at, error, created_at |
| `ChatSync` | id, profile_id, placement_id, kind, trigger, status, started_at, completed_at, chats_seen, messages_imported, backfill_from, oldest_updated_at, error, created_at |
| `AccountPlacement` | id, platform, external_id, name, avatar_url, status, active_profile, linked_profiles |
| `ApiKey` | id, name, profile_group_id, sandbox, token (create only), created_at |
| `WhatsAppTemplate` | id, external_id, profile_id, name, language, category, status, parameter_format, components, variable_count, created_at, updated_at |
| `DailyStatsResponse` | data: profile_id, platform, placement_id, attribution, from_, to, data_timezone, records, metrics |
| `FollowerHistoryResponse` | data: profile_id, platform, placement_id, from_, to, records (followers_gained/lost/change/total) |
| `WhatsAppMedia` | data (bytes), content_type |
| `AcceptedResponse` | accepted |
| `PaginatedResponse[T]` | total, page, per_page, data |

### Platform parameter models

| Model | Platform |
|---|---|
| `FacebookParams` | format (`post`, `story`, `reel`), first_comment, page_id, link, alt_text, made_with_ai, countries |
| `InstagramParams` | format (`post`, `reel`, `story`), first_comment, collaborators, cover_url, cover_file, audio_name, audio_id, audio_volume, video_volume, strip_audio, trial_strategy (`MANUAL`, `SS_PERFORMANCE`), thumb_offset, user_tags, alt_text, made_with_ai |
| `InstagramUserTag` | username, x, y, media_index |
| `TikTokParams` | format (`video`, `image`), privacy_status, photo_cover_index, auto_add_music, made_with_ai, disable_comment, disable_duet, disable_stitch, brand_content_toggle, brand_organic_toggle, upload_as_draft, cover_url, cover_file, thumb_offset |
| `LinkedInParams` | format (`post`, `poll`), organization_id, reshare_urn, alt_text, countries, poll_question, poll_options (2-4, max 30 chars), poll_duration_days (1, 3, 7, 14) |
| `YouTubeParams` | format (`post`), title, privacy_status, cover_url, cover_file, made_for_kids, tags, category_id, contains_synthetic_media |
| `PinterestParams` | format (`pin`), title, board_id, destination_link, cover_url, cover_file, thumb_offset, alt_text |
| `ThreadsParams` | format (`post`), alt_text, topic_tag |
| `TwitterParams` | format (`post`, `poll`), alt_text, poll_options (2-4 choices, max 25 chars each; required for `poll`), poll_duration_minutes (5-10080; required for `poll`) |
| `BlueskyParams` | format (`post`), alt_text |
| `TelegramParams` | format (`post`), chat_id (required), parse_mode (`HTML`, `MarkdownV2`), disable_link_preview, disable_notification |

#### Instagram user tags

Tag public Instagram accounts in a post — feed post, reel, or story:

```python
from postproxy import InstagramParams, InstagramUserTag, PlatformParams

await client.posts.create(
    "Shot on location",
    ["ig-profile-id"],
    media=[
        "https://example.com/1.jpg",
        "https://example.com/2.jpg",
        "https://example.com/3.mp4",
    ],
    platforms=PlatformParams(
        instagram=InstagramParams(
            format="post",
            user_tags=[
                InstagramUserTag(username="natgeo", x=0.5, y=0.4),               # slide 0
                InstagramUserTag(username="nasa", x=0.2, y=0.8, media_index=1),  # slide 1
                InstagramUserTag(username="spacex", media_index=2),              # video — username only
            ],
        )
    ),
)
```

- **Images require `x` and `y`** — floats `0.0`–`1.0` measured from the top-left corner.
- **Reels and video slides** are tagged by username only; coordinates are ignored and dropped.
- **Stories** accept coordinates but don't need them.
- `media_index` picks the carousel slide (0-based, defaults to `0`, video slides included).
- A leading `@` on a username is stripped for you.

Coordinates outside `0.0`–`1.0`, a `media_index` past the last media item, or an image tag
missing `x`/`y` are rejected with a `ValidationError` naming the offending entry. Accounts
that are private or have tagging turned off are silently skipped by Instagram at publish
time.

Wrap them in `PlatformParams` when passing to `posts.create()`. Telegram needs a `chat_id` per post — list available channels with `client.profiles.placements(profile_id)`.

Supported platforms: facebook, instagram, tiktok, linkedin, youtube, twitter, threads, pinterest, bluesky, telegram, google_business, whatsapp (DMs only).

`alt_text` takes a single string or a list matching the order of `media`. `cover_file` is a
local path (uploaded with the post) or a base64 `data:` URL (sent as-is).

#### Google Business

Google Business posts use the `google_business` key on `PlatformParams` (passed as a plain dict). The location resource path returned by `client.profiles.placements()` is the `location_id`. Supported formats: `standard`, `event`, `offer`. CTA actions: `LEARN_MORE`, `BOOK`, `ORDER`, `SHOP`, `SIGN_UP`, `CALL`. Media is limited to one image (≤5 MB).

```python
await client.posts.create(
    "Now open weekends!",
    ["gbp-profile-id"],
    media=["https://example.com/store.jpg"],
    platforms={
        "google_business": {
            "format": "standard",
            "location_id": "accounts/123/locations/456",
            "cta_action_type": "LEARN_MORE",
            "cta_url": "https://example.com",
        },
    },
)
```

## Development

```bash
pip install -e ".[dev]"
pytest
mypy postproxy/
```

## License

MIT
