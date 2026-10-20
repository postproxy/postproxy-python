"""Example of creating and sending WhatsApp message templates."""

import asyncio
import os

from postproxy import MessageLocation, MessageTemplateInput, PostProxy

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_ID = "your-whatsapp-profile-id"


async def main():
    async with PostProxy(API_KEY) as client:
        # Create a template — Meta reviews it before it can be sent
        template = await client.whatsapp_templates.create(
            PROFILE_ID,
            name="order_shipped",
            category="UTILITY",
            language="en_US",
            components=[
                {"type": "BODY", "text": "Hi {{1}}, your order {{2}} has shipped."},
            ],
        )
        print(template.name, template.status)  # "order_shipped" "PENDING"

        # Check approval status (or subscribe to message_template.status_updated)
        approved = await client.whatsapp_templates.list(
            PROFILE_ID, status="APPROVED", refresh=True
        )
        print("Approved:", [t.name for t in approved.data])

        # Send it to a customer. The phone number id is a placement of the profile.
        numbers = (await client.profiles.placements(PROFILE_ID)).data
        chat = await client.chats.create(PROFILE_ID, "15551234567", placement_id=numbers[0].id)

        await client.messages.send(
            chat.id,
            template=MessageTemplateInput(
                name="order_shipped",
                language="en_US",
                variables=["Jane", "#1234"],
            ),
        )

        # Inside the 24h window, free-form messages work too
        fresh = await client.chats.get(chat.id)
        if fresh.within_messaging_window:
            await client.messages.send(
                chat.id,
                location=MessageLocation(latitude=52.52, longitude=13.405, name="Pickup point"),
            )


if __name__ == "__main__":
    asyncio.run(main())
