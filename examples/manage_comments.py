"""Examples of managing comments with the PostProxy SDK."""

import asyncio
import os

from postproxy import PostProxy

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_GROUP_ID = os.environ.get("POSTPROXY_PROFILE_GROUP_ID", "")


async def main():
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        # Assume we have a published post and a profile
        post_id = "your-post-id"
        profile_id = "your-profile-id"

        # List comments on a post
        comments = await client.comments.list(post_id, profile_id)
        print(f"Total comments: {comments.total}")
        for comment in comments.data:
            print(f"  {comment.author_username}: {comment.body}")
            for reply in comment.replies:
                print(f"    {reply.author_username}: {reply.body}")

        # Get a specific comment
        if comments.data:
            comment = await client.comments.get(post_id, comments.data[0].id, profile_id)
            print(f"Comment: {comment.body} (likes: {comment.like_count})")

        # Create a comment on the post
        new_comment = await client.comments.create(
            post_id, profile_id, "Thanks for the feedback everyone!"
        )
        print(f"Created comment: {new_comment.id} (status: {new_comment.status})")

        # Reply to a comment
        reply = await client.comments.create(
            post_id, profile_id, "Glad you liked it!",
            parent_id=new_comment.id,
        )
        print(f"Created reply: {reply.id}")

        # Hide a comment
        await client.comments.hide(post_id, new_comment.id, profile_id)
        print("Comment hidden")

        # Unhide a comment
        await client.comments.unhide(post_id, new_comment.id, profile_id)
        print("Comment unhidden")

        # Like a comment
        await client.comments.like(post_id, new_comment.id, profile_id)
        print("Comment liked")

        # Unlike a comment
        await client.comments.unlike(post_id, new_comment.id, profile_id)
        print("Comment unliked")

        # Delete a comment
        await client.comments.delete(post_id, new_comment.id, profile_id)
        print("Comment deleted")


if __name__ == "__main__":
    asyncio.run(main())
