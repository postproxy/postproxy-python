"""Example of WhatsApp number administration: business profile, groups,
blocked users and conversion events."""

import asyncio
import os

from postproxy import PostProxy

API_KEY = os.environ["POSTPROXY_API_KEY"]
PROFILE_ID = "your-whatsapp-profile-id"
PHONE_NUMBER_ID = "your-phone-number-id"


async def main():
    async with PostProxy(API_KEY) as client:
        wa = client.whatsapp

        # Business profile
        await wa.update_business_profile(
            PROFILE_ID,
            PHONE_NUMBER_ID,
            about="Fresh coffee, fast replies",
            websites=["https://example.com"],
        )

        # Create a group and share its invite link
        group = await wa.create_group(
            PROFILE_ID,
            PHONE_NUMBER_ID,
            "VIP customers",
            description="Early access to new roasts",
            join_approval_mode="approval_required",
        )
        group_id = str(group["id"])
        invite = await wa.create_group_invite_link(PROFILE_ID, PHONE_NUMBER_ID, group_id)
        print("Invite link:", invite)

        # Approve everyone waiting to join
        requests = await wa.group_join_requests(PROFILE_ID, PHONE_NUMBER_ID, group_id)
        print("Join requests:", requests)
        await wa.approve_group_join_requests(
            PROFILE_ID, PHONE_NUMBER_ID, group_id, ["15551234567"]
        )

        # Block a spammer
        await wa.block_users(PROFILE_ID, PHONE_NUMBER_ID, ["15557654321"])

        # Report a purchase back to Meta for a click-to-WhatsApp ad
        await wa.send_conversion_event(
            PROFILE_ID,
            event_name="Purchase",
            event_id="order-1234",
            phone="15551234567",
            currency="USD",
            value=24.5,
        )


if __name__ == "__main__":
    asyncio.run(main())
