"""Examples of managing queues with the PostProxy SDK."""

import asyncio
import os

from postproxy import PostProxy

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_GROUP_ID = os.environ.get("POSTPROXY_PROFILE_GROUP_ID", "")


async def main():
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        # Create a queue with weekday morning timeslots
        queue = await client.queues.create(
            "Morning Posts",
            PROFILE_GROUP_ID,
            description="Weekday morning content",
            timezone="America/New_York",
            jitter=10,
            timeslots=[
                {"day": 1, "time": "09:00"},
                {"day": 2, "time": "09:00"},
                {"day": 3, "time": "09:00"},
                {"day": 4, "time": "09:00"},
                {"day": 5, "time": "09:00"},
            ],
        )
        print(f"Created queue: {queue.id} {queue.name}")
        print(f"Timeslots: {len(queue.timeslots)}")

        # List all queues
        queues = (await client.queues.list()).data
        print(f"All queues: {[q.name for q in queues]}")

        # Get next available slot
        next_slot = await client.queues.next_slot(queue.id)
        print(f"Next slot: {next_slot.next_slot}")

        # Add a post to the queue
        profiles = (await client.profiles.list()).data
        post = await client.posts.create(
            "This post will be scheduled by the queue",
            profiles=[profiles[0].id],
            queue_id=queue.id,
            queue_priority="high",
        )
        print(f"Queued post: {post.id} scheduled at: {post.scheduled_at}")

        # Update the queue — add a timeslot and change jitter
        updated = await client.queues.update(
            queue.id,
            jitter=15,
            timeslots=[{"day": 6, "time": "10:00"}],
        )
        print(f"Updated queue timeslots: {len(updated.timeslots)}")

        # Pause the queue
        paused = await client.queues.update(queue.id, enabled=False)
        print(f"Queue paused: {not paused.enabled}")

        # Delete the queue
        deleted = await client.queues.delete(queue.id)
        print(f"Deleted: {deleted.deleted}")


if __name__ == "__main__":
    asyncio.run(main())
