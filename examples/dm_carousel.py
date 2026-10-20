"""Example of sending a product carousel in a Facebook / Instagram DM."""

import asyncio
import os

from postproxy import MessageButton, MessageElement, PostProxy

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_ID = "your-instagram-profile-id"


async def main():
    async with PostProxy(API_KEY) as client:
        chats = await client.chats.list(PROFILE_ID, per_page=1)
        chat = chats.data[0]

        # Show the participant we're on it, then send a product carousel
        await client.chats.mark_read(chat.id)
        await client.chats.start_typing(chat.id)

        await client.messages.send(
            chat.id,
            elements=[
                MessageElement(
                    title="Red sneaker",
                    subtitle="$89 — sizes 38-46",
                    image_url="https://cdn.example.com/red.png",
                    buttons=[
                        MessageButton(type="web_url", title="Buy", url="https://shop.example.com/red")
                    ],
                ),
                MessageElement(
                    title="Blue sneaker",
                    subtitle="$92 — back in stock soon",
                    image_url="https://cdn.example.com/blue.png",
                    buttons=[
                        MessageButton(type="postback", title="Notify me", payload="NOTIFY:blue")
                    ],
                ),
            ],
        )

        await client.chats.stop_typing(chat.id)


if __name__ == "__main__":
    asyncio.run(main())
