"""Examples of retrieving post stats with the PostProxy SDK."""

import asyncio
import os

from postproxy import PostProxy

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_GROUP_ID = os.environ.get("POSTPROXY_PROFILE_GROUP_ID")


async def get_stats_for_posts():
    """Fetch stats for specific posts."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        # Get recent posts
        page = await client.posts.list(per_page=5)

        if not page.data:
            print("No posts found")
            return

        post_ids = [p.id for p in page.data]
        result = await client.posts.stats(post_ids)

        for post_id, post_stats in result.data.items():
            print(f"\nPost {post_id}:")
            for platform in post_stats.platforms:
                print(f"  {platform.platform} ({platform.profile_id}):")
                for record in platform.records:
                    print(f"    {record.recorded_at}: {record.stats}")


async def stats_with_filters():
    """Fetch stats filtered by platform and date range."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        page = await client.posts.list(per_page=5)

        if not page.data:
            print("No posts found")
            return

        post_ids = [p.id for p in page.data]

        # Filter by platform and date range
        result = await client.posts.stats(
            post_ids,
            profiles=["instagram", "twitter"],
            from_date="2026-02-01T00:00:00Z",
            to_date="2026-02-24T00:00:00Z",
        )

        for post_id, post_stats in result.data.items():
            print(f"\nPost {post_id}:")
            for platform in post_stats.platforms:
                latest = platform.records[-1] if platform.records else None
                if latest:
                    print(f"  {platform.platform} latest: {latest.stats}")


async def track_growth():
    """Compare earliest and latest snapshots to see growth."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        page = await client.posts.list(per_page=1)

        if not page.data:
            print("No posts found")
            return

        result = await client.posts.stats([page.data[0].id])

        for post_id, post_stats in result.data.items():
            print(f"\nPost {post_id} growth:")
            for platform in post_stats.platforms:
                if len(platform.records) < 2:
                    print(f"  {platform.platform}: not enough data points")
                    continue

                first = platform.records[0].stats
                last = platform.records[-1].stats
                print(f"  {platform.platform}:")
                for key in last:
                    if key in first:
                        diff = last[key] - first[key]
                        print(f"    {key}: {first[key]} -> {last[key]} (+{diff})")


if __name__ == "__main__":
    asyncio.run(get_stats_for_posts())
