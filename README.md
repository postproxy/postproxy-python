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

# Delete a post
result = await client.posts.delete("post-id")
print(result.deleted)  # True

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

# Initialize a social platform connection
conn = await client.profile_groups.initialize_connection(
    "pg-id",
    platform="instagram",
    redirect_url="https://yourapp.com/callback",
)
print(conn.url)  # Redirect the user to this URL
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
| `Post` | id, body, status, scheduled_at, created_at, platforms |
| `Profile` | id, name, status, platform, profile_group_id, expires_at, post_count |
| `ProfileGroup` | id, name, profiles_count |
| `PlatformResult` | platform, status, params, error, attempted_at, insights |
| `StatsResponse` | data (dict keyed by post id) |
| `PostStats` | platforms |
| `PlatformStats` | profile_id, platform, records |
| `StatsRecord` | stats (dict), recorded_at |
| `ListResponse[T]` | data |
| `PaginatedResponse[T]` | total, page, per_page, data |

### Platform parameter models

| Model | Platform |
|---|---|
| `FacebookParams` | format (`post`, `story`), first_comment, page_id |
| `InstagramParams` | format (`post`, `reel`, `story`), first_comment, collaborators, cover_url, audio_name, trial_strategy, thumb_offset |
| `TikTokParams` | format (`video`, `image`), privacy_status, photo_cover_index, auto_add_music, made_with_ai, disable_comment, disable_duet, disable_stitch, brand_content_toggle, brand_organic_toggle |
| `LinkedInParams` | format (`post`), organization_id |
| `YouTubeParams` | format (`post`), title, privacy_status, cover_url |
| `PinterestParams` | format (`pin`), title, board_id, destination_link, cover_url, thumb_offset |
| `ThreadsParams` | format (`post`) |
| `TwitterParams` | format (`post`) |

Wrap them in `PlatformParams` when passing to `posts.create()`.

## Development

```bash
pip install -e ".[dev]"
pytest
mypy postproxy/
```

## License

MIT
