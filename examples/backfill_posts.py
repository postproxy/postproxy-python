"""Backfill a profile's older posts and follow the sync run to completion."""

import asyncio
import os

from postproxy import ConflictError, PostProxy

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_GROUP_ID = os.environ.get("POSTPROXY_PROFILE_GROUP_ID", "")


async def main():
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        profile_id = "your-profile-id"

        # Start a backfill. It walks the profile's feed backwards from the
        # newest post in batches of 25 and stops at `from_` — or earlier, if the
        # platform stops returning history. Runs in the background.
        try:
            sync = await client.profiles.backfill_posts(
                profile_id, from_="2025-01-01"
            )
        except ConflictError as exc:
            # Only one backfill runs per profile at a time; the running one
            # already covers any window a second request could ask for.
            running_id = exc.response["profile_sync_id"]
            print(f"Backfill already running: {running_id}")
            sync = await client.profiles.post_sync(profile_id, running_id)

        print(f"Backfill {sync.id} — status: {sync.status}")

        # Poll until it finishes.
        while sync.status in ("pending", "running"):
            await asyncio.sleep(5)
            sync = await client.profiles.post_sync(profile_id, sync.id)
            print(
                f"  {sync.status}: {sync.posts_imported} imported of "
                f"{sync.posts_seen} seen, reached back to {sync.oldest_posted_at}"
            )

        if sync.status == "failed":
            print(f"Backfill failed: {sync.error}")
        else:
            print(
                f"Done. Imported {sync.posts_imported} posts, "
                f"oldest {sync.oldest_posted_at}"
            )

        # Every pull is recorded — the sync fired on connect, the recurring
        # poll, and each backfill. Runs are kept for 30 days.
        runs = await client.profiles.post_syncs(profile_id, per_page=10)
        print(f"\nRecent post syncs ({runs.total}):")
        for run in runs.data:
            print(
                f"  {run.created_at} {run.trigger} → {run.status} "
                f"({run.posts_imported}/{run.posts_seen} new)"
            )


if __name__ == "__main__":
    asyncio.run(main())
