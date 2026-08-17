"""Examples of managing direct messages (chats & messages) with the PostProxy SDK."""

import asyncio
import os

from postproxy import MessageButton, MessageCard, PostProxy, QuickReply

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_GROUP_ID = os.environ.get("POSTPROXY_PROFILE_GROUP_ID", "")


async def main():
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        profile_id = "your-profile-id"  # a DM-capable profile (facebook/instagram/telegram/bluesky)

        # List existing chats for a profile
        chats = await client.chats.list(profile_id, per_page=20)
        print(f"Total chats: {chats.total}")
        for chat in chats.data:
            print(f"  {chat.participant_username or chat.participant_external_id}: {chat.last_message_at}")

        # Find or create a chat with a participant
        chat = await client.chats.create(
            profile_id,
            "igsid_8675309",
            participant_username="jane_doe",
        )
        print(f"Chat: {chat.id} (platform: {chat.platform})")

        # List messages in the chat
        messages = await client.messages.list(chat.id, direction="inbound")
        for msg in messages.data:
            print(f"  [{msg.direction}] {msg.body}")
            for att in msg.attachments:
                print(f"    attachment: {att.type} -> {att.url}")

        # Send a text message (within the 24h window)
        sent = await client.messages.send(chat.id, body="Yes, we ship worldwide!")
        print(f"Sent message: {sent.id} (status: {sent.status})")

        # Send outside the 24h window with a tag (Facebook/Instagram)
        await client.messages.send(
            chat.id, body="Following up on your order.", tag="HUMAN_AGENT"
        )

        # Send an image by hosted URL
        await client.messages.send(chat.id, media=["https://cdn.example.com/photo.png"])

        # Send an image from a local file (multipart)
        # await client.messages.send(chat.id, media_files=["./photo.png"])

        # Quick replies — tappable chips above the composer, gone once tapped.
        # Facebook & Instagram only; up to 13.
        await client.messages.send(
            chat.id,
            body="What can I help with?",
            quick_replies=[
                QuickReply(title="Track order", payload="TRACK"),
                QuickReply(title="Talk to support", payload="HELP"),
            ],
        )

        # Buttons — attached to the message and stay in the thread. Up to 3, and
        # body is capped at 80 characters when buttons are present (Meta's limit).
        # card adds subtitle / image / tap-through to the same card.
        await client.messages.send(
            chat.id,
            body="Your order shipped",
            buttons=[
                MessageButton(
                    type="web_url", title="Track", url="https://shop.example.com/o/123"
                ),
                MessageButton(type="postback", title="Cancel", payload="CANCEL:123"),
            ],
            card=MessageCard(
                subtitle="Arriving Friday",
                image_url="https://cdn.example.com/shoe.png",
            ),
        )

        # A tap comes back as an inbound message carrying tapped_action.
        inbound = await client.messages.list(chat.id, direction="inbound")
        for msg in inbound.data:
            if msg.tapped_action:
                print(
                    f"  tapped {msg.tapped_action.kind}: {msg.tapped_action.payload}"
                )

        # React / unreact (Facebook & Instagram)
        await client.messages.react(sent.id, reaction="love", emoji="❤️")
        await client.messages.unreact(sent.id)

        # Edit an outbound message (Telegram only)
        # await client.messages.edit(sent.id, body="Updated answer.")

        # Archive / unarchive a chat (Bluesky only)
        # await client.chats.archive(chat.id)
        # await client.chats.unarchive(chat.id)

        # Private reply to a comment (Instagram/Facebook) — returns a Message
        reply = await client.comments.private_reply(
            "your-post-id", "comment-id", profile_id, "Thanks — DM-ing you the details."
        )
        print(f"Private reply queued: {reply.id} (chat: {reply.chat_id})")

        # Ice breakers (Instagram only): FAQ prompts shown when a user opens a chat
        await client.profiles.set_ice_breakers(
            profile_id,
            [
                {"question": "What services do you offer?", "payload": "services"},
                {"question": "What are your hours?", "payload": "hours"},
            ],
        )
        result = await client.profiles.ice_breakers(profile_id)
        print("Ice breakers:", [ib.question for ib in result.ice_breakers])
        # await client.profiles.delete_ice_breakers(profile_id)


if __name__ == "__main__":
    asyncio.run(main())
