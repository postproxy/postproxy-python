"""Example of editing a post that's already published."""

import asyncio
import os

from postproxy import (
    PinterestParams,
    PlatformParams,
    PlatformPostData,
    PostProxy,
    YouTubeParams,
    parse_event_typed,
)

API_KEY = os.environ["POSTPROXY_API_KEY"]


async def main():
    async with PostProxy(API_KEY) as client:
        # Only the body, the YouTube title and the Pinterest title /
        # destination_link can change once a post is published.
        post = await client.posts.update(
            "published-post-id",
            body="Launch day! (now with the right link)",
            platforms=PlatformParams(
                youtube=YouTubeParams(title="Launch day — full walkthrough"),
                pinterest=PinterestParams(destination_link="https://example.com/launch"),
            ),
        )
        print([f"{p.platform}: {p.permalink}" for p in post.platforms])


def handle_webhook(raw_body: str) -> None:
    """The edit is pushed to each platform in the background. Your webhook
    handler learns how it went."""
    envelope, data = parse_event_typed(raw_body)
    if not isinstance(data, PlatformPostData):
        return
    if envelope.type == "platform_post.edited":
        print("Edited on", data.platform)
    elif envelope.type == "platform_post.edit_failed":
        print("Edit failed on", data.platform, data.error)


if __name__ == "__main__":
    asyncio.run(main())
