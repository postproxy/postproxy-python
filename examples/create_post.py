"""Examples of creating posts with the PostProxy SDK."""

import asyncio
import os

from postproxy import (
    PostProxy,
    PlatformParams,
    FacebookParams,
    InstagramParams,
    TikTokParams,
    YouTubeParams,
    PinterestParams,
    LinkedInParams,
    ThreadsParams,
    ThreadChildInput,
    TwitterParams,
)

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_GROUP_ID = os.environ.get("POSTPROXY_PROFILE_GROUP_ID")


async def simple_post():
    """Create a simple text post."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        profiles = (await client.profiles.list()).data
        post = await client.posts.create(
            "Hello from PostProxy Python SDK!",
            profiles=[profiles[0].id],
        )
        print(f"Created post {post.id} — status: {post.status}")


async def post_with_media():
    """Create a post with media URLs."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        profiles = (await client.profiles.list()).data
        facebook_profile = next(
            (p for p in profiles if p.platform == "facebook"), None
        )
        if facebook_profile is None:
            raise ValueError("No Facebook profile found")

        placements = (await client.profiles.placements(id=facebook_profile.id)).data

        post = await client.posts.create(
            "Check this out!",
            profiles=[facebook_profile.id],
            draft=True,
            media=[
                "https://example.com/photo.jpg",
            ],
            platforms=PlatformParams(
                facebook=FacebookParams(
                    format="post",
                    page_id=placements[0].id,
                    first_comment="First!",
                ),
            ),
        )
        print(f"Created post {post.id} with media — status: {post.status}")


async def post_with_local_file():
    """Create a post with a local file upload."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        profiles = (await client.profiles.list()).data
        post = await client.posts.create(
            "Posted with a local file!",
            profiles=[profiles[0].id],
            draft=True,
            media_files=["./photo.jpg"],
        )
        print(f"Created post {post.id} with file upload — status: {post.status}")


async def draft_then_publish():
    """Create a draft post, then publish it."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        profiles = (await client.profiles.list()).data

        # Create as draft
        post = await client.posts.create(
            "This starts as a draft",
            profiles=[profiles[0].id],
            draft=True,
        )
        print(f"Created draft {post.id} — status: {post.status}")

        # Publish the draft
        post = await client.posts.publish_draft(post.id)
        print(f"Published {post.id} — status: {post.status}")


async def scheduled_post():
    """Schedule a post for the future."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        profiles = (await client.profiles.list()).data
        post = await client.posts.create(
            "This post is scheduled!",
            profiles=[profiles[0].id],
            scheduled_at="2025-12-25T09:00:00Z",
        )
        print(f"Scheduled post {post.id} for {post.scheduled_at}")


async def cross_platform_post():
    """Create a post with platform-specific parameters."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        profiles = (await client.profiles.list()).data

        profile_ids = [p.id for p in profiles]

        post = await client.posts.create(
            "Cross-platform post with custom settings per network",
            profiles=profile_ids,
            draft=True,
            media=["https://example.com/video.mp4"],
            platforms=PlatformParams(
                facebook=FacebookParams(
                    format="post",
                    first_comment="First!",
                ),
                instagram=InstagramParams(
                    format="reel",
                    collaborators=["@collab_account"],
                ),
                tiktok=TikTokParams(
                    format="video",
                    privacy_status="PUBLIC_TO_EVERYONE",
                    auto_add_music=True,
                ),
                linkedin=LinkedInParams(
                    format="post",
                    organization_id="org-123",
                ),
                youtube=YouTubeParams(
                    format="post",
                    title="My Video Title",
                    privacy_status="public",
                ),
                pinterest=PinterestParams(
                    format="pin",
                    title="Pin Title",
                    board_id="board-abc",
                    destination_link="https://example.com",
                ),
                threads=ThreadsParams(
                    format="post",
                ),
                twitter=TwitterParams(
                    format="post",
                ),
            ),
        )
        print(f"Created cross-platform post {post.id}")
        for p in post.platforms:
            print(f"  {p.platform}: {p.status}")


async def thread_post():
    """Create a thread post with multiple child posts."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        profiles = (await client.profiles.list()).data
        twitter_profile = next(
            (p for p in profiles if p.platform == "twitter"), None
        )
        if twitter_profile is None:
            raise ValueError("No Twitter profile found")

        post = await client.posts.create(
            "Here's a thread about PostProxy 🧵",
            profiles=[twitter_profile.id],
            thread=[
                ThreadChildInput(body="First, connect your social accounts."),
                ThreadChildInput(body="Then, create posts with media!", media=["https://example.com/demo.jpg"]),
                ThreadChildInput(body="Finally, schedule or publish instantly."),
            ],
        )
        print(f"Created thread {post.id} with {len(post.thread)} children")
        for child in post.thread:
            print(f"  - {child.id}: {child.body}")

        # Twitter poll: 2-4 options (max 25 chars each), 5-10080 minutes
        poll_post = await client.posts.create(
            "Which framework?",
            ["twitter"],
            platforms=PlatformParams(
                twitter=TwitterParams(
                    format="poll",
                    poll_options=["Rails", "Django", "Laravel", "Other"],
                    poll_duration_minutes=1440,
                )
            ),
        )
        print(f"Created poll post {poll_post.id}")


if __name__ == "__main__":
    asyncio.run(simple_post())
